"""SEO output for the static site; uses only the Python standard library."""
from pathlib import Path
from html import escape, unescape
from html.parser import HTMLParser
import json,re,urllib.parse,xml.etree.ElementTree as ET
import mimetypes

class Breadcrumbs(HTMLParser):
    def __init__(self):
        super().__init__();self.inside=False;self.current=None;self.items=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=='nav' and attrs.get('aria-label')=='パンくず':self.inside=True
        if self.inside and tag in ('a','span'):
            self.current={'name':'','path':attrs.get('href')}
    def handle_data(self,data):
        if self.current is not None:self.current['name']+=data
    def handle_endtag(self,tag):
        if self.inside and tag in ('a','span') and self.current is not None:
            self.current['name']=self.current['name'].strip()
            if self.current['name'] not in ('','/','›','>'):self.items.append(self.current)
            self.current=None
        if tag=='nav':self.inside=False

def absolute(base,path):
    return base+urllib.parse.quote(urllib.parse.unquote(path),safe='/')

def tracking(config):
    gtm=config['gtm_id']
    if not re.fullmatch(r'GTM-[A-Z0-9]+',gtm):raise ValueError('Invalid GTM ID')
    # Standard GTM initialization with a production-origin guard for JS-enabled previews.
    script='''<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){if(location.origin!==ORIGIN)return;
w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});
var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';
j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;
f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer',CONTAINER);</script>
<!-- End Google Tag Manager -->'''.replace('ORIGIN',json.dumps(config['site_url'])).replace('CONTAINER',json.dumps(gtm))
    noscript=f'<!-- Google Tag Manager (noscript) --><noscript><iframe title="Google Tag Manager" src="https://www.googletagmanager.com/ns.html?id={gtm}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript><!-- End Google Tag Manager (noscript) -->'
    return script,noscript

def finalize_seo(root,dist,inventory,production=False):
    config=json.loads((root/'src/site-config.json').read_text())
    records=json.loads((root/'src/seo-pages.json').read_text())
    base=config['site_url'].rstrip('/')
    if not re.fullmatch(r'https://[A-Za-z0-9.-]+',base):raise ValueError('site_url must be an HTTPS origin')
    config['site_url']=base
    if production and config['ga4_mode']!='gtm':raise ValueError('Confirm analytics configuration before production build')
    org_id=base+'/#organization';website_id=base+'/#website'
    indexed=[];report=[]
    for item in inventory:
        path=item['path'];file=dist/path.strip('/')/'index.html'
        html=file.read_text()
        if path not in records:raise ValueError(f'Add page-specific metadata in src/seo-pages.json: {path}')
        record=records[path];title=record['title'];description=record['description'];url=absolute(base,path)
        image_path=record['image'];image=absolute(base,image_path)
        if not (dist/image_path.lstrip('/')).is_file():raise ValueError(f'Missing social image: {image_path}')
        if not title or not description:raise ValueError(f'Empty metadata for {path}')
        indexable=path!='/404/' and not record.get('noindex',False)
        if indexable:indexed.append(url)
        robots='index,follow,max-image-preview:large' if production and indexable else 'noindex,nofollow'
        meta=f'<title>{escape(title)}</title><meta name="description" content="{escape(description)}"><meta name="robots" content="{robots}">'
        if indexable:meta+=f'<link rel="canonical" href="{escape(url)}">'
        properties={'og:locale':'ja_JP','og:site_name':config['site_name'],'og:type':'article' if record['type']=='Article' else 'website','og:title':title,'og:description':description,'og:url':url,'og:image':image,'og:image:secure_url':image,'og:image:alt':record.get('image_alt') or ('ベレネッツの支援事例イメージ' if image_path!='/assets/hero.jpg' else 'ベレネッツのブランディング支援イメージ'),'og:image:type':mimetypes.guess_type(image_path)[0] or 'image/jpeg'}
        for key,value in properties.items():meta+=f'<meta property="{key}" content="{escape(value)}">'
        for key,value in {'twitter:card':'summary_large_image','twitter:title':title,'twitter:description':description,'twitter:image':image,'twitter:image:alt':properties['og:image:alt']}.items():meta+=f'<meta name="{key}" content="{escape(value)}">'
        org={'@type':'Organization','@id':org_id,'name':'株式会社ベレネッツ','alternateName':'Wellenetz Inc.','url':base+'/','logo':{'@type':'ImageObject','url':base+'/assets/site-logo.png'},'address':[{'@type':'PostalAddress','addressCountry':'JP','postalCode':'104-0061','addressRegion':'東京都','addressLocality':'中央区','streetAddress':'銀座1-15-4 ヒューリック銀座一丁目昭和通りビル7F'},{'@type':'PostalAddress','addressCountry':'JP','postalCode':'460-0003','addressRegion':'愛知県','addressLocality':'名古屋市中区','streetAddress':'錦3-11-25 アーク栄錦ビル6F'}]}
        website={'@type':'WebSite','@id':website_id,'url':base+'/','name':config['site_name'],'inLanguage':'ja','publisher':{'@id':org_id}}
        webpage={'@type':record['type'] if record['type']!='Article' else 'WebPage','@id':url+'#webpage','url':url,'name':title,'description':description,'inLanguage':'ja','isPartOf':{'@id':website_id},'publisher':{'@id':org_id},'primaryImageOfPage':{'@type':'ImageObject','url':image}}
        graph=[org,website,webpage]
        crumbs=Breadcrumbs();crumbs.feed(html)
        if indexable and len(crumbs.items)>1:
            breadcrumb={'@type':'BreadcrumbList','@id':url+'#breadcrumb','itemListElement':[{'@type':'ListItem','position':i+1,'name':crumb['name'],'item':absolute(base,crumb['path'] or path)} for i,crumb in enumerate(crumbs.items)]}
            graph.append(breadcrumb);webpage['breadcrumb']={'@id':breadcrumb['@id']}
        if record['type']=='Article':
            article={'@type':'Article','@id':url+'#article','headline':unescape(re.sub('<[^>]+>','',item['title'])),'description':description,'image':[image],'inLanguage':'ja','mainEntityOfPage':{'@id':webpage['@id']},'publisher':{'@id':org_id}}
            if record.get('publishedAt'):article['datePublished']=record['publishedAt']
            if record.get('updatedAt'):article['dateModified']=record['updatedAt']
            graph.append(article);webpage['mainEntity']={'@id':article['@id']}
        if record.get('service'):
            service={'@type':'Service','@id':url+'#service','name':title.split(' | ')[0],'description':description,'url':url,'provider':{'@id':org_id},'mainEntityOfPage':{'@id':webpage['@id']}}
            graph.append(service);webpage['mainEntity']={'@id':service['@id']}
        if indexable:meta+='<script type="application/ld+json">'+json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+'</script>'
        html=re.sub(r'<title>.*?</title>','',html,count=1,flags=re.S)
        html=re.sub(r'<meta name="(?:description|robots)"[^>]*>','',html)
        html=html.replace('</head>',meta+'</head>',1)
        if production:
            gtm_head,gtm_body=tracking(config)
            html=html.replace('<head>','<head>'+gtm_head,1).replace('<body id="top">','<body id="top">'+gtm_body,1)
        file.write_text(html)
        report.append({'path':path,'title':title,'description':description,'canonical':url if indexable else None,'schema':[node['@type'] for node in graph] if indexable else [],'robots':robots,'gtm':production})
    (dist/'404.html').write_text((dist/'404/index.html').read_text())
    # No fabricated lastmod values: add only if editorial update dates are maintained.
    ns='http://www.sitemaps.org/schemas/sitemap/0.9';ET.register_namespace('',ns)
    sitemap=ET.Element('{'+ns+'}urlset')
    for url in sorted(indexed):ET.SubElement(ET.SubElement(sitemap,'{'+ns+'}url'),'{'+ns+'}loc').text=url
    ET.indent(sitemap)
    ET.ElementTree(sitemap).write(dist/'sitemap.xml',encoding='utf-8',xml_declaration=True)
    robots=f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n' if production else 'User-agent: *\nDisallow: /\n'
    (dist/'robots.txt').write_text(robots)
    (root/('seo-report-production.json' if production else 'seo-report-preview.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
