"""Private Cron entry point. Python 3.6+ stdlib; HTTPS out, no inbound SSH.

Trust boundary: a fixed public GitHub repository's Releases API over verified
TLS, plus its SHA-256 asset digest. This is not an independent code signature.
Downloaded archives contain static site files only, never executable updater code.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import ssl
import stat
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

import publish

REPOSITORY = 'wellenetz55/microcms'
API = 'https://api.github.com/repos/' + REPOSITORY
ASSET_NAME = 'wellenetz-site.zip'
MAX_DOWNLOAD = 250 * 1024 * 1024
MAX_EXPANDED = 750 * 1024 * 1024
STATIC_SUFFIXES = {'.html', '.css', '.js', '.json', '.xml', '.txt', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif', '.ico', '.mp4', '.woff', '.woff2', '.pdf'}


def check_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('Only verified GitHub HTTPS endpoints are allowed')
    if parsed.hostname not in {'api.github.com', 'github.com', 'release-assets.githubusercontent.com'}:
        raise ValueError('Unexpected download host')
    return url


class GitHubRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        check_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url, destination, limit):
    check_url(url)
    opener = urllib.request.build_opener(GitHubRedirect(), urllib.request.HTTPSHandler(context=ssl.create_default_context()))
    request = urllib.request.Request(url, headers={'User-Agent': 'Wellenetz-CMS-Pull/1', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    size = 0
    digest = hashlib.sha256()
    with opener.open(request, timeout=60) as response, destination.open('wb') as stream:
        check_url(response.geturl())
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > limit:
                raise ValueError('Download exceeds size limit')
            stream.write(chunk)
            digest.update(chunk)
    return size, digest.hexdigest()


def validate_manifest(manifest):
    if manifest.get('version') != 1 or manifest.get('fixture') is not False:
        raise ValueError('Only production manifests may be applied')
    files = manifest.get('files')
    if not isinstance(files, dict) or not 4 <= len(files) <= 20000:
        raise ValueError('Invalid manifest file count')
    if not {'index.html', 'sitemap.xml', 'robots.txt', '404.html'}.issubset(files):
        raise ValueError('Incomplete production site')
    for name, digest in files.items():
        path = PurePosixPath(name)
        if (not name or len(name) > 500 or path.is_absolute() or str(path) != name
                or '\\' in name or any(ord(c) < 32 for c in name)
                or any(p.startswith('.') for p in path.parts)
                or path.suffix.lower() not in STATIC_SUFFIXES
                or not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest)):
            raise ValueError('Unsafe static manifest path or digest: ' + name)
    for field in ('cms_routes', 'legacy_overrides'):
        routes = manifest.get(field)
        if not isinstance(routes, list) or any(not isinstance(route, str) or not re.fullmatch(r'/(news|column)/[A-Za-z0-9_-]+/', route) for route in routes):
            raise ValueError('Invalid article routes')
    if any(route.strip('/') + '/index.html' not in files for route in manifest['cms_routes']):
        raise ValueError('Missing published article')


def unpack(archive_path, destination):
    with zipfile.ZipFile(str(archive_path)) as archive:
        members = archive.infolist()
        names = [item.filename for item in members]
        if len(names) != len(set(names)) or len(names) > 20001 or sum(item.file_size for item in members) > MAX_EXPANDED:
            raise ValueError('Duplicate or oversized archive')
        if 'manifest.json' not in names or archive.getinfo('manifest.json').file_size > 8 * 1024 * 1024:
            raise ValueError('Missing or oversized manifest')
        manifest = json.loads(archive.read('manifest.json').decode('utf-8'))
        validate_manifest(manifest)
        expected = {'manifest.json'} | {'site/' + name for name in manifest['files']}
        if set(names) != expected:
            raise ValueError('Archive contains unexpected or missing files')
        for item in members:
            mode = item.external_attr >> 16
            if item.is_dir() or stat.S_ISLNK(mode) or item.flag_bits & 1:
                raise ValueError('Archive may contain only unencrypted regular files')
            if stat.S_IFMT(mode) not in (0, stat.S_IFREG):
                raise ValueError('Special archive entries are forbidden')
            target = destination / item.filename
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)
            if item.filename != 'manifest.json' and publish.digest(target) != manifest['files'][item.filename[5:]]:
                raise ValueError('Static file checksum mismatch')
        return manifest


def select_asset(release):
    if release.get('draft') is not False or release.get('prerelease') is not False or not re.fullmatch(r'cms-production-\d+-\d+', release.get('tag_name', '')):
        raise ValueError('Unexpected GitHub release')
    ident = release.get('id')
    if not isinstance(ident, int) or ident <= 0:
        raise ValueError('Invalid release ID')
    assets = [asset for asset in release.get('assets', []) if asset.get('name') == ASSET_NAME]
    if len(assets) != 1:
        raise ValueError('Release must contain exactly one site archive')
    asset = assets[0]
    expected_url = 'https://github.com/' + REPOSITORY + '/releases/download/' + release['tag_name'] + '/' + ASSET_NAME
    if asset.get('browser_download_url') != expected_url or asset.get('state') != 'uploaded':
        raise ValueError('Unexpected asset source or incomplete upload')
    if not re.fullmatch(r'sha256:[a-f0-9]{64}', asset.get('digest') or ''):
        raise ValueError('GitHub SHA-256 asset digest is required')
    if not isinstance(asset.get('size'), int) or not 0 < asset['size'] <= MAX_DOWNLOAD:
        raise ValueError('Invalid asset size')
    return asset


def run(config, apply=False, fetch=download):
    root, state = Path(config['public_root']), Path(config['state_dir'])
    if not root.is_absolute() or not state.is_absolute() or not root.is_dir():
        raise ValueError('Absolute public_root and private state_dir are required')
    if state.is_symlink() or root.is_symlink() or root.resolve() == state.resolve() or root.resolve() in state.resolve().parents:
        raise ValueError('State directory must be private and outside public_root')
    if apply and config.get('enabled') is not True:
        raise ValueError('Production apply is disabled in local configuration')
    state.mkdir(parents=True, exist_ok=True)
    with (state / 'pull.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Another CMS update is running; skipped')
            return
        if (state / 'publisher' / 'pending.json').exists():
            raise ValueError('Interrupted publish requires recovery before retry')
        with tempfile.TemporaryDirectory(prefix='fetch-', dir=str(state)) as folder:
            work = Path(folder)
            try:
                fetch(API + '/releases/latest', work / 'latest.json', 2 * 1024 * 1024)
            except urllib.error.HTTPError as exc:
                if exc.code == 404:
                    print('No production release yet; public files unchanged')
                    return
                raise
            release = json.loads((work / 'latest.json').read_text())
            asset = select_asset(release)
            marker = state / 'applied.json'
            if marker.exists():
                previous = json.loads(marker.read_text())
                if release['id'] < previous['release_id']:
                    raise ValueError('Older release rejected')
                if release['id'] == previous['release_id']:
                    if asset['digest'] != previous['digest']:
                        raise ValueError('Previously applied release was changed')
                    print('Already applied; public files unchanged')
                    return
            size, sha = fetch(asset['browser_download_url'], work / ASSET_NAME, MAX_DOWNLOAD)
            if size != asset['size'] or 'sha256:' + sha != asset['digest']:
                raise ValueError('GitHub asset size or SHA-256 mismatch')
            output = work / 'release'
            unpack(work / ASSET_NAME, output)
            publish.publish(output, root, state / 'publisher', dry_run=not apply)
            if apply:
                staged_marker = work / 'applied.json'
                staged_marker.write_text(json.dumps({'release_id': release['id'], 'digest': asset['digest'], 'tag': release['tag_name']}))
                os.replace(str(staged_marker), str(marker))
                print('Applied ' + release['tag_name'])
            else:
                print('DRY RUN passed; public files unchanged: ' + release['tag_name'])


if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        run(json.loads(args.config.read_text()), args.apply)
    except Exception as exc:
        # Avoid exposing signed redirect URLs or headers in Cron logs.
        print('CMS pull failed (%s); inspect private settings; no unverified release applied' % type(exc).__name__, file=sys.stderr)
        sys.exit(1)
