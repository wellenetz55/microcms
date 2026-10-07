"""Validate generated metadata, sitemap, graph references and environment separation.
Run with Python + beautifulsoup4; site generation itself has no external dependencies.
"""
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse,unquote
import json,xml.etree.ElementTree as ET

root=Path(__file__).resolve().parent
inventory=json.loads((root/'page-inventory.json').read_text())
records=json.loads((root/'src/seo-pages.json').read_text())
base=json.loads((root/'src/site-config.json').read_text())['site_url']
for mode in ('dist','dist-production'):
    production=mode=='dist-production';dist=root/mode
    expected=set();titles=set();descriptions=set();counts={};breadcrumb_count=0
    for entry in inventory:
        path=entry['path'];html=(dist/path.strip('/')/'index.html').read_text()
        soup=BeautifulSoup(html,'html.parser');indexable=path!='/404/' and not records[path].get('noindex',False)
        title=soup.title.get_text();description=soup.select('meta[name=description]')
        assert len(description)==1 and description[0]['content'],path
        assert title not in titles and description[0]['content'] not in descriptions,path
        titles.add(title);descriptions.add(description[0]['content'])
        robots=soup.select_one('meta[name=robots]')['content']
        assert ('noindex' not in robots)==(production and indexable),path
        for field in ('og:title','og:description','og:type','og:url','og:image','og:locale','og:site_name'):
            assert len(soup.select(f'meta[property="{field}"]'))==1,(path,field)
        assert soup.select_one('meta[property="og:title"]')['content']==title
        assert soup.select_one('meta[property="og:description"]')['content']==description[0]['content']
        image=soup.select_one('meta[property="og:image"]')['content']
        assert image.startswith(base+'/') and (dist/unquote(urlparse(image).path).lstrip('/')).is_file()
        assert soup.select_one('meta[name="twitter:card"]')['content']=='summary_large_image'
        canonical=soup.select('link[rel=canonical]');schemas=soup.select('script[type="application/ld+json"]')
        if indexable:
            assert len(canonical)==1 and len(schemas)==1,path
            url=canonical[0]['href'];expected.add(url)
            assert url.startswith(base+'/') and unquote(urlparse(url).path)==path,path
            graph=json.loads(schemas[0].string)['@graph'];ids={node['@id'] for node in graph}
            for node in graph:
                counts[node['@type']]=counts.get(node['@type'],0)+1
                if node['@type']=='BreadcrumbList':
                    breadcrumb_count+=1
                    assert [i['position'] for i in node['itemListElement']]==list(range(1,len(node['itemListElement'])+1))
                    assert len(node['itemListElement'])>=2
                for key in ('isPartOf','publisher','provider','mainEntity','mainEntityOfPage','breadcrumb'):
                    if key in node:assert node[key]['@id'] in ids,(path,key)
        else:assert not canonical and not schemas
        gtm_scripts=[s for s in soup.find_all('script') if 'gtm.js?id=' in (s.string or '')]
        gtm_frames=soup.select('noscript iframe[src*="googletagmanager.com"]')
        assert len(gtm_scripts)==int(production) and len(gtm_frames)==int(production),path
        if production:
            assert soup.head.find('script')==gtm_scripts[0]
            assert soup.body.find(recursive=False).name=='noscript'
            assert 'GTM-KTW89Q' in gtm_scripts[0].string
        assert not soup.select('script[src*="gtag/js"]'),path
        assert len(soup.select('h1'))==1,path
    ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    urls=[x.text for x in ET.parse(dist/'sitemap.xml').findall('s:url/s:loc',ns)]
    assert len(urls)==len(set(urls))==96 and set(urls)==expected
    robots=(dist/'robots.txt').read_text()
    assert ('Disallow: /' not in robots)==production
    assert ('Sitemap: '+base+'/sitemap.xml' in robots)==production
    assert (dist/'404.html').read_bytes()==(dist/'404/index.html').read_bytes()
    print(json.dumps({'mode':mode,'pages':len(inventory),'unique_titles':len(titles),'unique_descriptions':len(descriptions),'sitemap_urls':len(urls),'schema_types':counts,'passed':True},ensure_ascii=False))
