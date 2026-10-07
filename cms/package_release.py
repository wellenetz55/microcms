"""Package only verified static files for the server-side HTTPS puller."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

from pull import validate_manifest


def package(release, output):
    release, output = Path(release), Path(output)
    manifest = json.loads((release / 'manifest.json').read_text())
    validate_manifest(manifest)
    for name, expected in manifest['files'].items():
        path = release / 'site' / name
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('Invalid release file: ' + name)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(str(output), 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json', json.dumps(manifest, ensure_ascii=False))
        for name in sorted(manifest['files']):
            archive.write(str(release / 'site' / name), 'site/' + name)
    print('Packaged verified production files: ' + str(output))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--release', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    package(args.release, args.output)
