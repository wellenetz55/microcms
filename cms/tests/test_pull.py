"""Also runs unchanged on the Xserver Python 3.6 interpreter in private temp files."""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pull
import publish
import package_release


class PullTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / 'public'
        self.root.mkdir()
        (self.root / 'manual.pdf').write_text('keep')
        (self.root / '.htaccess').write_text('keep')
        self.state = self.base / 'state'
        self.release = self.base / 'release'
        self.files = {'index.html': 'home', 'sitemap.xml': 'sitemap', 'robots.txt': 'robots', '404.html': 'not found', 'news/new/index.html': 'article'}
        self.config = {'public_root': str(self.root), 'state_dir': str(self.state), 'enabled': False}
        self.tag = 'cms-production-123-1'
        self.archive = self.base / pull.ASSET_NAME
        self.make_archive()

    def tearDown(self):
        self.tmp.cleanup()

    def make_archive(self, routes=None):
        self.manifest = {'version': 1, 'fixture': False, 'files': {}, 'cms_routes': ['/news/new/'] if routes is None else routes, 'legacy_overrides': []}
        for name, content in self.files.items():
            path = self.release / 'site' / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            self.manifest['files'][name] = hashlib.sha256(path.read_bytes()).hexdigest()
        (self.release / 'manifest.json').write_text(json.dumps(self.manifest))
        package_release.package(self.release, self.archive)
        sha = hashlib.sha256(self.archive.read_bytes()).hexdigest()
        self.metadata = {'id': 123, 'tag_name': self.tag, 'draft': False, 'prerelease': False, 'assets': [{'name': pull.ASSET_NAME, 'state': 'uploaded', 'size': self.archive.stat().st_size, 'digest': 'sha256:' + sha, 'browser_download_url': 'https://github.com/' + pull.REPOSITORY + '/releases/download/' + self.tag + '/' + pull.ASSET_NAME}]}

    def fetch(self, url, destination, limit):
        if url == pull.API + '/releases/latest':
            destination.write_text(json.dumps(self.metadata))
        else:
            shutil.copyfile(str(self.archive), str(destination))
        return destination.stat().st_size, hashlib.sha256(destination.read_bytes()).hexdigest()

    def test_dry_run_leaves_public_files_unchanged(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        pull.run(self.config, fetch=self.fetch)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})
        self.assertFalse((self.state / 'applied.json').exists())

    def test_apply_unpublish_and_preserve_unmanaged_files(self):
        self.config['enabled'] = True
        pull.run(self.config, apply=True, fetch=self.fetch)
        self.assertEqual((self.root / 'index.html').read_text(), 'home')
        del self.files['news/new/index.html']
        self.make_archive(routes=[])
        self.metadata['id'] = 124
        pull.run(self.config, apply=True, fetch=self.fetch)
        self.assertFalse((self.root / 'news/new/index.html').exists())
        self.assertEqual((self.root / '.htaccess').read_text(), 'keep')
        self.assertEqual((self.root / 'manual.pdf').read_text(), 'keep')
        pull.run(self.config, apply=True, fetch=lambda *args: self.fetch(*args))

    def test_disabled_apply_is_rejected(self):
        with self.assertRaises(ValueError):
            pull.run(self.config, apply=True, fetch=self.fetch)
        self.assertFalse((self.root / 'index.html').exists())

    def test_tampered_download_fails_before_public_writes(self):
        self.archive.write_bytes(b'tampered')
        with self.assertRaises(ValueError):
            pull.run(self.config, fetch=self.fetch)
        self.assertFalse((self.root / 'index.html').exists())

    def test_untrusted_release_asset_and_digest_rejected(self):
        for change in ({'draft': True}, {'prerelease': True}, {'tag_name': 'other'}):
            altered = dict(self.metadata)
            altered.update(change)
            with self.assertRaises(ValueError):
                pull.select_asset(altered)
        self.metadata['assets'][0]['digest'] = None
        with self.assertRaises(ValueError):
            pull.select_asset(self.metadata)

    def test_no_release_is_safe(self):
        def unavailable(*args):
            raise urllib.error.HTTPError(pull.API, 404, 'Not found', {}, None)
        pull.run(self.config, fetch=unavailable)
        self.assertFalse((self.root / 'index.html').exists())

    def test_archive_traversal_extra_and_symlink_rejected(self):
        with zipfile.ZipFile(str(self.archive), 'a') as archive:
            archive.writestr('../escape', 'bad')
        with self.assertRaises(ValueError):
            pull.unpack(self.archive, self.base / 'unpacked')
        for name in ('../escape.html', '/evil.html', '.htaccess', 'shell.php', 'assets/../evil.js', 'assets//evil.js'):
            altered = dict(self.manifest)
            altered['files'] = dict(self.manifest['files'])
            altered['files'][name] = '0' * 64
            with self.assertRaises(ValueError):
                pull.validate_manifest(altered)
        self.make_archive()
        with zipfile.ZipFile(str(self.archive)) as archive:
            entries = [(i.filename, archive.read(i)) for i in archive.infolist()]
        with zipfile.ZipFile(str(self.archive), 'w') as archive:
            for name, data in entries:
                info = zipfile.ZipInfo(name)
                info.external_attr = (0o120777 if name == 'site/index.html' else 0o100644) << 16
                archive.writestr(info, data)
        with self.assertRaises(ValueError):
            pull.unpack(self.archive, self.base / 'symlink')

    def test_https_redirect_targets_are_restricted(self):
        for url in ('http://github.com/a', 'https://evil.test/a', 'https://github.com.evil.test/a', 'https://user@github.com/a', 'https://github.com:444/a'):
            with self.assertRaises(ValueError):
                pull.check_url(url)
        self.assertEqual(pull.check_url('https://release-assets.githubusercontent.com/a'), 'https://release-assets.githubusercontent.com/a')

    def test_failure_rolls_back_and_does_not_mark_applied(self):
        (self.root / 'index.html').write_text('old')
        self.config['enabled'] = True
        original = publish.atomic_copy
        failed = [False]
        def broken(source, destination):
            if source.name == 'index.html' and 'release/site' in str(source) and not failed[0]:
                failed[0] = True
                raise OSError('simulated disk failure')
            return original(source, destination)
        with patch.object(publish, 'atomic_copy', broken):
            with self.assertRaises(OSError):
                pull.run(self.config, apply=True, fetch=self.fetch)
        self.assertEqual((self.root / 'index.html').read_text(), 'old')
        self.assertFalse((self.state / 'applied.json').exists())
        self.assertFalse((self.state / 'publisher/pending.json').exists())

    def test_older_release_and_changed_applied_release_rejected(self):
        self.config['enabled'] = True
        pull.run(self.config, apply=True, fetch=self.fetch)
        self.metadata['id'] = 122
        with self.assertRaises(ValueError):
            pull.run(self.config, apply=True, fetch=self.fetch)
        self.metadata['id'] = 123
        self.metadata['assets'][0]['digest'] = 'sha256:' + 'a' * 64
        with self.assertRaises(ValueError):
            pull.run(self.config, apply=True, fetch=self.fetch)


if __name__ == '__main__':
    unittest.main(verbosity=2)
