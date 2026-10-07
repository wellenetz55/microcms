"""Server-side managed-file publishing. State and recovery backups stay outside web root."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import uuid


def safe_path(root, rel):
    part = PurePosixPath(rel)
    if part.is_absolute() or not part.parts or any(x in ('.','..') or x.startswith('.') for x in part.parts) or '\\' in rel:
        raise ValueError('Unsafe manifest path')
    dest = root.joinpath(*part.parts)
    for p in [dest, *dest.parents]:
        if p == root.parent: break
        if p.is_symlink(): raise ValueError('Symlinks are not allowed in managed paths: '+str(p))
    if root.resolve() not in dest.resolve().parents: raise ValueError('Path escapes destination')
    return dest


def atomic_copy(source, dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.cms-', dir=dest.parent)
    try:
        with os.fdopen(fd,'wb') as stream, source.open('rb') as incoming: shutil.copyfileobj(incoming,stream)
        os.chmod(name,0o644)
        os.replace(name,dest)
    finally:
        if os.path.exists(name): os.unlink(name)


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def public_parent(root, dest):
    """Create web directories readable by Apache even with the puller's umask 077."""
    parent = root
    for part in dest.parent.relative_to(root).parts:
        parent = parent / part
        if not parent.exists():
            parent.mkdir()
            parent.chmod(0o755)


def restore(root, state):
    journal = json.loads((state/'pending.json').read_text())
    if journal.get('root') != str(root.resolve()): raise ValueError('Recovery destination does not match original publish')
    backup = state/'backups'/journal['id']
    for rel, existed in journal['changes'].items():
        dest = safe_path(root,rel)
        if existed:
            public_parent(root,dest)
            atomic_copy(safe_path(backup/'files',rel),dest)
        elif dest.exists(): dest.unlink()
    if (backup/'manifest.json').exists(): atomic_copy(backup/'manifest.json',state/'manifest.json')
    elif (state/'manifest.json').exists(): (state/'manifest.json').unlink()
    (state/'pending.json').unlink()


def publish(release, root, state, dry_run=False, rollback=False):
    root, state, release = root.absolute(), state.absolute(), release.absolute()
    if root.is_symlink() or state.is_symlink() or root.resolve() in state.resolve().parents or root.resolve() == state.resolve():
        raise ValueError('State must be outside web root, without symlinks')
    if not root.is_dir(): raise ValueError('Destination directory must already exist')
    state.mkdir(parents=True,exist_ok=True)
    with (state/'publish.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if rollback:
            if not (state/'pending.json').exists(): raise ValueError('No interrupted publish to recover')
            restore(root,state); return
        if (state/'pending.json').exists(): raise ValueError('Interrupted publish detected. Run --rollback before continuing')
        manifest = json.loads((release/'manifest.json').read_text())
        if manifest.get('version') != 1 or manifest.get('fixture') is not False: raise ValueError('Only validated production releases can be deployed')
        files = manifest['files']
        if not {'index.html','sitemap.xml','robots.txt','404.html'}.issubset(files): raise ValueError('Incomplete site release')
        for rel, sha in files.items():
            src = safe_path(release/'site',rel); dest = safe_path(root,rel)
            if not src.is_file() or digest(src) != sha: raise ValueError('Release checksum mismatch: '+rel)
            if dest.exists() and not dest.is_file(): raise ValueError('Destination is not a file: '+rel)
        previous = json.loads((state/'manifest.json').read_text()) if (state/'manifest.json').exists() else {'cms_routes':[]}
        old_routes = set(previous['cms_routes']) | set(manifest['legacy_overrides'])
        remove = []
        for route in old_routes - set(manifest['cms_routes']):
            if not re.fullmatch(r'/(news|column)/[A-Za-z0-9_-]+/',route): raise ValueError('Unsafe deletion route')
            rel = route.strip('/')+'/index.html'
            if rel in files: raise ValueError('Conflicting delete/write route')
            if safe_path(root,rel).exists(): remove.append(rel)
        changed = [rel for rel,sha in files.items() if not safe_path(root,rel).exists() or digest(safe_path(root,rel)) != sha]
        print('Publish plan: %d changed files, %d removed CMS pages' % (len(changed),len(remove)))
        if dry_run: return
        ident = uuid.uuid4().hex; backup = state/'backups'/ident; backup.mkdir(parents=True)
        changes = {}
        for rel in changed + remove:
            dest = safe_path(root,rel); changes[rel] = dest.exists()
            if dest.exists(): atomic_copy(dest,safe_path(backup/'files',rel))
        if (state/'manifest.json').exists(): atomic_copy(state/'manifest.json',backup/'manifest.json')
        journal = {'id':ident,'root':str(root.resolve()),'changes':changes}
        (backup/'journal.json').write_text(json.dumps(journal))
        atomic_copy(backup/'journal.json',state/'pending.json')
        try:
            # Assets first, then details, then lists/home/sitemap. Each file is replaced atomically.
            def order(rel):
                if rel.startswith('assets/'): return 0
                if rel in ('index.html','news/index.html','column/index.html','sitemap/index.html','sitemap.xml'): return 2
                return 1
            for rel in sorted(changed,key=order):
                dest = safe_path(root,rel)
                public_parent(root,dest)
                atomic_copy(release/'site'/rel,dest)
            for rel in remove:
                dest = safe_path(root,rel); dest.unlink()
                if not any(dest.parent.iterdir()): dest.parent.rmdir()
            atomic_copy(release/'manifest.json',state/'manifest.json')
            (state/'pending.json').unlink()
        except Exception:
            restore(root,state)
            raise
        print('Published. Recovery backup: '+str(backup))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--release',type=Path,required=True)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--state',type=Path,required=True)
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--rollback',action='store_true')
    args = parser.parse_args()
    publish(args.release,args.root,args.state,args.dry_run,args.rollback)
