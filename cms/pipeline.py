"""Fetch published microCMS articles and images, then build an isolated static release."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from html import escape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlencode
from urllib.request import Request, build_opener, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[1]
IMAGE_HOST = 'images.microcms-assets.io'

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Unexpected HTTP redirect; publication stopped')

def request(url, headers=None, limit=25 * 1024 * 1024):
    for attempt in range(3):
        try:
            with build_opener(NoRedirect).open(Request(url, headers=headers or {}), timeout=45) as response:
                data = response.read(limit + 1)
                if len(data) > limit:
                    raise ValueError('Response exceeds size limit')
                return data
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError('microCMS request failed (HTTP %s)' % exc.code) from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError('microCMS network request failed') from None
        time.sleep(2 ** attempt)

def fetch_articles(service, key, endpoint, fetch=request):
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]*', service):
        raise ValueError('Invalid MICROCMS_SERVICE_DOMAIN (subdomain only)')
    result, total, offset = [], None, 0
    while True:
        query = urlencode({'limit': 100, 'offset': offset, 'orders': 'id'})
        url = 'https://%s.microcms.io/api/v1/%s?%s' % (service, endpoint, query)
        data = json.loads(fetch(url, {'X-MICROCMS-API-KEY': key}))
        count = data.get('totalCount')
        batch = data.get('contents')
        if type(count) is not int or not isinstance(batch, list) or count < 0 or count > 10000:
            raise ValueError('Invalid API response')
        if total is not None and count != total:
            raise ValueError('Content changed during pagination; run again')
        total = count
        if data.get('offset') != offset or len(batch) > 100:
            raise ValueError('Invalid API pagination')
        result.extend(batch)
        offset += len(batch)
        if offset == total:
            break
        if not batch or offset > total:
            raise ValueError('Incomplete API response')
    ids = [item['id'] for item in result]
    if len(set(ids)) != len(ids):
        raise ValueError('Repeated article ID; run again')
    return result

class ImageStore:
    def __init__(self, assets, fetch=request):
        self.assets, self.fetch, self.urls = assets, fetch, {}
    def save(self, url):
        if url in self.urls:
            return self.urls[url]
        parts = urlsplit(url)
        if parts.scheme != 'https' or parts.hostname != IMAGE_HOST or parts.username or parts.password or parts.port or parts.fragment:
            raise ValueError('Upload article images to microCMS (HTTPS image assets only)')
        data = self.fetch(url)
        if data.startswith(b'\x89PNG\r\n\x1a\n'): ext = 'png'
        elif data.startswith(b'\xff\xd8\xff'): ext = 'jpg'
        elif data.startswith((b'GIF87a', b'GIF89a')): ext = 'gif'
        elif data.startswith(b'RIFF') and data[8:12] == b'WEBP': ext = 'webp'
        else: raise ValueError('Use PNG, JPEG, GIF or WebP images; unsupported image format')
        name = hashlib.sha256(data).hexdigest() + '.' + ext
        self.assets.mkdir(parents=True, exist_ok=True)
        (self.assets / name).write_bytes(data)
        self.urls[url] = '/assets/cms/' + name
        return self.urls[url]

class Body(HTMLParser):
    TAGS = set('p h2 h3 h4 h5 h6 ul ol li strong b em i u s br hr blockquote pre code a img figure figcaption table thead tbody tfoot tr th td'.split())
    BLOCKED = {'script', 'style', 'iframe', 'object', 'embed', 'svg', 'math', 'form', 'template'}
    VOID = {'br', 'hr', 'img'}
    def __init__(self, images):
        super().__init__(convert_charrefs=True)
        self.images, self.parts, self.text, self.blocked = images, [], [], []
    def handle_starttag(self, tag, attrs):
        if self.blocked:
            if tag not in {'br','hr','img','input','meta','link','embed','source','wbr'}: self.blocked.append(tag)
            return
        if tag in self.BLOCKED:
            if tag != 'embed': self.blocked.append(tag)
            return
        if tag == 'h1': tag = 'h2'
        if tag not in self.TAGS: return
        attrs = dict(attrs); safe = {}
        if tag == 'img':
            if not attrs.get('src'): raise ValueError('Article image has no source')
            safe = {'src': self.images.save(attrs['src']), 'alt': attrs.get('alt', ''), 'loading': 'lazy', 'decoding': 'async'}
            for field in ('width', 'height'):
                if re.fullmatch(r'[1-9][0-9]{0,4}', attrs.get(field, '')): safe[field] = attrs[field]
        if tag == 'a':
            href = attrs.get('href', '').strip()
            if any(ord(c) < 32 for c in href): href = ''
            parsed = urlsplit(href)
            if parsed.scheme in ('https','http','mailto','tel') or (href.startswith(('/', '#')) and not href.startswith('//')):
                safe['href'] = href
        if tag in ('td','th'):
            for field in ('colspan','rowspan'):
                if re.fullmatch(r'[1-9][0-9]?', attrs.get(field,'')): safe[field] = attrs[field]
        if re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', attrs.get('id', '')): safe['id'] = 'cms-' + attrs['id']
        if tag == 'a' and safe.get('href','').startswith('#'): safe['href'] = '#cms-' + safe['href'][1:]
        self.parts.append('<' + tag + ''.join(' %s="%s"' % (k,escape(v,quote=True)) for k,v in safe.items()) + '>')
    def handle_endtag(self, tag):
        if self.blocked:
            if tag in self.blocked:
                self.blocked = self.blocked[:len(self.blocked)-1-self.blocked[::-1].index(tag)]
            return
        if tag == 'h1': tag = 'h2'
        if tag in self.TAGS and tag not in self.VOID: self.parts.append('</'+tag+'>')
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID: self.handle_endtag(tag)
    def handle_data(self, data):
        if not self.blocked:
            self.parts.append(escape(data)); self.text.append(data)


def iso(value):
    if not isinstance(value,str): raise ValueError('Published date is required')
    dt = datetime.fromisoformat(value.replace('Z','+00:00'))
    if dt.tzinfo is None: raise ValueError('Date must include timezone')
    return dt.isoformat()

def transform(collections, assets, legacy_routes, overrides, fetch=request):
    rows, seo, routes = [], {}, set()
    images = ImageStore(assets, fetch)
    for endpoint in ('news','column'):
        for item in collections[endpoint]:
            # No draftKey, status=all, or webhook payload is ever used to obtain content.
            published = iso(item.get('publishedAt'))
            slug = item['id']
            if not isinstance(slug,str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}',slug):
                raise ValueError('Use alphanumeric, hyphen or underscore content IDs')
            route = '/%s/%s/' % (endpoint, slug)
            if route in routes: raise ValueError('Duplicate route: '+route)
            if route in legacy_routes and route not in overrides:
                raise ValueError('Existing article collision: add route to cms/config.json legacy_overrides after migration: '+route)
            routes.add(route)
            title = item.get('title','').strip()
            body = item.get('body','')
            if not title or not isinstance(body,str) or not body.strip(): raise ValueError('title/body are required: '+route)
            parsed = Body(images); parsed.feed(body); parsed.close()
            description = item.get('description','').strip() or ' '.join(parsed.text).strip()[:150]
            if not description: raise ValueError('Article text or description is required: '+route)
            cover = images.save(item['cover']['url']) if item.get('cover') else '/assets/hero.jpg'
            rows.append({'url':'https://www.wellenetz.co.jp'+route,'title':title,'blocks':[],
                         '_cms':{'body':''.join(parsed.parts),'date':published,'cover':cover if item.get('cover') else None}})
            seo[route] = {'title':title+' | ベレネッツ','description':description,'image':cover,'image_alt':title,
                          'type':'Article','publishedAt':published,'updatedAt':iso(item.get('revisedAt') or item.get('updatedAt') or published)}
    return rows, seo, sorted(routes)

def validate_site(site, inventory):
    for row in inventory:
        text = (site / row['path'].strip('/') / 'index.html').read_text()
        if text.count('<h1') != 1: raise ValueError('Unexpected h1 count: '+row['path'])
        if re.search(r'<img[^>]+(?:https?:)?//images\.microcms-assets\.io',text): raise ValueError('Remote CMS image remains')
        if '<link rel="canonical"' not in text and row['path'] not in ('/404/','/inquiry/thanks/'):
            raise ValueError('Missing canonical: '+row['path'])
        for src in re.findall(r'<img[^>]+src="([^"]+)"',text):
            if src.startswith('/') and not (site / src.lstrip('/')).is_file(): raise ValueError('Missing image: '+src)


def build(output, fixture=False, fetch=request):
    output = output.resolve()
    if output.exists(): raise ValueError('Output already exists. Use a new output directory: '+str(output))
    config = json.loads((ROOT/'cms/config.json').read_text())
    overrides = set(config['legacy_overrides'])
    if any(not re.fullmatch(r'/(news|column)/[A-Za-z0-9_-]+/',r) for r in overrides): raise ValueError('Invalid legacy_overrides route')
    if fixture:
        collections = json.loads((ROOT/'cms/fixture.json').read_text())
        original_fetch = fetch
        def fetch(url, headers=None):
            if url == 'https://images.microcms-assets.io/demo/cover.jpg': return (ROOT/'dist/assets/hero.jpg').read_bytes()
            return original_fetch(url, headers)
    else:
        service, key = os.environ.get('MICROCMS_SERVICE_DOMAIN') or config['service_domain'], os.environ.get('MICROCMS_API_KEY','')
        if not key: raise ValueError('Set MICROCMS_API_KEY in environment / GitHub Secrets')
        collections = {name:fetch_articles(service,key,name,fetch) for name in ('news','column')}
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='wellenetz-cms-',dir=output.parent) as tmp:
        tmp = Path(tmp); project = tmp/'project'; project.mkdir()
        for path in ROOT.glob('*.py'): shutil.copy2(path, project/path.name)
        shutil.copytree(ROOT/'src', project/'src')
        shutil.copytree(ROOT/'dist/assets', project/'dist/assets',ignore=shutil.ignore_patterns('.DS_Store'))
        old = json.loads((project/'src/source-pages.json').read_text())
        legacy_routes = {urlsplit(p['url']).path for p in old}
        rows, metadata, routes = transform(collections,project/'dist/assets/cms',legacy_routes,overrides,fetch)
        merged = [p for p in old if urlsplit(p['url']).path not in overrides] + rows
        (project/'src/source-pages.json').write_text(json.dumps(merged,ensure_ascii=False))
        records = json.loads((project/'src/seo-pages.json').read_text()); records.update(metadata)
        (project/'src/seo-pages.json').write_text(json.dumps(records,ensure_ascii=False))
        command = [sys.executable, str(project/'build.py')]
        if not fixture: command.append('--production')
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
        site = project/('dist' if fixture else 'dist-production')
        inventory = json.loads((project/'page-inventory.json').read_text())
        validate_site(site, inventory)
        release = tmp/'release'; release.mkdir(); shutil.move(str(site), release/'site')
        files = {p.relative_to(release/'site').as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in (release/'site').rglob('*') if p.is_file()}
        manifest = {'version':1,'fixture':fixture,'files':files,'cms_routes':routes,'legacy_overrides':sorted(overrides)}
        (release/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
        (release/'page-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
        shutil.move(str(release), output)
    print('CMS build complete: %d articles, %d pages → %s' % (len(rows),len(inventory),output))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fixture', action='store_true', help='Offline sample, noindex, cannot deploy')
    args = parser.parse_args()
    try: build(args.output,args.fixture)
    except (ValueError, RuntimeError, KeyError) as exc: raise SystemExit(str(exc))
