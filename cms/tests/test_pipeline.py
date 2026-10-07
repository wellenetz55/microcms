import hashlib
import json
import os
import re
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pipeline
import publish

class PipelineTests(unittest.TestCase):
    def test_pagination_and_read_only_header(self):
        calls=[]
        def fetch(url,headers):
            calls.append((url,headers)); offset=0 if len(calls)==1 else 100
            return json.dumps({'contents':[{'id':str(i)} for i in range(offset,101 if offset else 100)],'offset':offset,'totalCount':101}).encode()
        self.assertEqual(len(pipeline.fetch_articles('example','secret','news',fetch)),101)
        self.assertIn('offset=100',calls[1][0]); self.assertNotIn('draftKey',calls[0][0])
        self.assertEqual(calls[0][1],{'X-MICROCMS-API-KEY':'secret'})
    def test_incomplete_api_stops(self):
        with self.assertRaises(ValueError): pipeline.fetch_articles('example','key','news',lambda *a: b'{"contents":[],"totalCount":5,"offset":0}')
    def test_html_and_image_localization(self):
        with tempfile.TemporaryDirectory() as tmp:
            images=pipeline.ImageStore(Path(tmp),lambda *a:b'\x89PNG\r\n\x1a\nfixture')
            body=pipeline.Body(images)
            body.feed('<script>alert(1)</script><h1>題名</h1><p onclick="bad()">本文<img src="https://images.microcms-assets.io/a.png" onerror="bad()"></p><iframe>unsafe</iframe><a href="javascript:alert(1)">link</a>')
            result=''.join(body.parts)
            for banned in ('script','alert','onclick','onerror','unsafe','javascript:'): self.assertNotIn(banned,result)
            self.assertIn('<h2>題名</h2>',result);self.assertIn('/assets/cms/',result)
            self.assertEqual(len(list(Path(tmp).glob('*.png'))),1)
            with self.assertRaises(ValueError): images.save('http://127.0.0.1/secret')
    def test_draft_and_legacy_collision(self):
        data={'news':[{'id':'old','title':'title','body':'<p>body</p>','publishedAt':'2026-10-07T00:00:00Z'}],'column':[]}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError): pipeline.transform(data,Path(tmp),{'/news/old/'},set())
            rows,seo,routes=pipeline.transform(data,Path(tmp),{'/news/old/'},{'/news/old/'})
            self.assertEqual(routes,['/news/old/']);self.assertIn('publishedAt',seo[routes[0]])
            del data['news'][0]['publishedAt']
            with self.assertRaises(ValueError): pipeline.transform(data,Path(tmp),set(),set())

    def test_full_production_build_with_mock_api(self):
        collections=json.loads((pipeline.ROOT/'cms/fixture.json').read_text())
        collections['column'][0]['publishedAt']='2026-10-07T16:30:00Z'
        def fetch(url,headers=None):
            if url=='https://images.microcms-assets.io/demo/cover.jpg': return (pipeline.ROOT/'dist/assets/hero.jpg').read_bytes()
            endpoint='news' if '/news?' in url else 'column'
            items=collections[endpoint]
            return json.dumps({'contents':items,'offset':0,'totalCount':len(items)}).encode()
        with tempfile.TemporaryDirectory() as tmp, patch.dict('os.environ',{'MICROCMS_SERVICE_DOMAIN':'test-service','MICROCMS_API_KEY':'TEST_SECRET_NEVER_PUBLISH'}):
            output=Path(tmp)/'release'; pipeline.build(output,fetch=fetch)
            manifest=json.loads((output/'manifest.json').read_text())
            self.assertFalse(manifest['fixture']);self.assertEqual(len(manifest['cms_routes']),2)
            site=output/'site'
            for route in manifest['cms_routes']:
                html=(site/route.strip('/')/'index.html').read_text()
                self.assertIn('index,follow,max-image-preview:large',html)
                self.assertIn('datePublished',html);self.assertIn('dateModified',html)
                self.assertNotIn('TEST_SECRET_NEVER_PUBLISH',html)
                self.assertNotIn('images.microcms-assets.io',html)
                self.assertIn('https://www.wellenetz.co.jp'+route,(site/'sitemap.xml').read_text())
            self.assertIn('cms-demo-news',(site/'index.html').read_text())
            self.assertIn('cms-demo-column',(site/'column/index.html').read_text())
            home=(site/'index.html').read_text()
            updates=re.search(r'<section[^>]+id="updates".*?</section>',home,re.S).group()
            self.assertLess(updates.index('/column/cms-demo-column/'),updates.index('/news/cms-demo-news/'))
            self.assertIn('2026.10.08',updates)
            self.assertIn('>COLUMN</span>',updates)
            self.assertIn('>NEWS</span>',updates)
            dates=re.findall(r'<time datetime="([^"]+)">',updates)
            self.assertEqual(len(dates),6)
            self.assertEqual(dates,sorted(dates,reverse=True))
            news=(site/'news/index.html').read_text()
            self.assertIn('2025.09.23',news)
            self.assertIn('2025.07.09',news)
            self.assertNotIn('<time></time>',news)
            self.assertNotIn('公開日未登録',news)
            failed=Path(tmp)/'failed'
            with self.assertRaises(RuntimeError): pipeline.build(failed,fetch=lambda *a: (_ for _ in ()).throw(RuntimeError('network failure')))
            self.assertFalse(failed.exists())
            self.assertTrue((site/'index.html').exists())
            destination=Path(tmp)/'public';destination.mkdir()
            publish.publish(output,destination,Path(tmp)/'state')
            self.assertEqual((destination/'column/cms-demo-column/index.html').read_bytes(),(site/'column/cms-demo-column/index.html').read_bytes())

class PublishTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.base=Path(self.tmp.name)
        self.root=self.base/'public';self.root.mkdir();self.state=self.base/'private';self.release=self.base/'release'
        self.files={'index.html':'home','sitemap.xml':'sitemap','robots.txt':'robots','404.html':'404','news/new/index.html':'article','assets/cms/test.png':'image'}
    def tearDown(self): self.tmp.cleanup()
    def test_public_directories_under_private_umask(self):
        self.release_files()
        old = os.umask(0o077)
        try:
            publish.publish(self.release,self.root,self.state)
        finally:
            os.umask(old)
        for rel in ('news','news/new','assets','assets/cms'):
            self.assertEqual((self.root/rel).stat().st_mode & 0o777,0o755)
        self.assertEqual((self.root/'news/new/index.html').stat().st_mode & 0o777,0o644)
        self.assertEqual(self.state.stat().st_mode & 0o777,0o700)
        for backup in (self.state/'backups').iterdir():
            self.assertEqual(backup.stat().st_mode & 0o777,0o700)
    def release_files(self,fixture=False,routes=None):
        site=self.release/'site';site.mkdir(parents=True,exist_ok=True)
        hashes={}
        for rel,text in self.files.items():
            file=site/rel;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text);hashes[rel]=hashlib.sha256(file.read_bytes()).hexdigest()
        (self.release/'manifest.json').write_text(json.dumps({'version':1,'fixture':fixture,'files':hashes,'cms_routes':['/news/new/'] if routes is None else routes,'legacy_overrides':[]}))
    def test_unpublish_preserves_unmanaged_files(self):
        (self.root/'.htaccess').write_text('keep');(self.root/'manual.pdf').write_text('keep')
        self.release_files();publish.publish(self.release,self.root,self.state)
        del self.files['news/new/index.html'];self.release_files(routes=[])
        publish.publish(self.release,self.root,self.state)
        self.assertFalse((self.root/'news/new/index.html').exists())
        self.assertFalse((self.root/'news/new').exists())
        self.assertEqual((self.root/'.htaccess').read_text(),'keep'); self.assertTrue((self.root/'manual.pdf').exists())
    def test_failure_restores_previous_files(self):
        self.release_files();publish.publish(self.release,self.root,self.state)
        self.files.update({'index.html':'changed','news/new/index.html':'changed'})
        self.release_files();original=publish.atomic_copy; failed=False
        def broken(src,dest):
            nonlocal failed
            if src==self.release/'site/index.html' and not failed:
                failed=True;raise OSError('simulated disk error')
            return original(src,dest)
        with patch.object(publish,'atomic_copy',broken):
            with self.assertRaises(OSError):publish.publish(self.release,self.root,self.state)
        self.assertEqual((self.root/'news/new/index.html').read_text(),'article')
        self.assertEqual((self.root/'index.html').read_text(),'home')
        self.assertFalse((self.state/'pending.json').exists())
    def test_fixture_and_tampering_are_rejected_before_writes(self):
        self.release_files(fixture=True)
        with self.assertRaises(ValueError):publish.publish(self.release,self.root,self.state)
        self.release_files();(self.release/'site/index.html').write_text('tampered')
        with self.assertRaises(ValueError):publish.publish(self.release,self.root,self.state)
        self.assertFalse((self.root/'index.html').exists())
    def test_dry_run_and_path_protection(self):
        self.release_files();publish.publish(self.release,self.root,self.state,dry_run=True)
        self.assertFalse((self.root/'index.html').exists())
        for path in ('../private/key','/etc/passwd','.htaccess'):
            with self.assertRaises(ValueError):publish.safe_path(self.root,path)
        (self.root/'assets').symlink_to(self.base,target_is_directory=True)
        with self.assertRaises(ValueError):publish.safe_path(self.root,'assets/key')

if __name__=='__main__':unittest.main()
