"""Attach diagnosis attribution and render the unlisted advertising landing page."""
import re
import shutil

from seo import tracking
import json


def build_reason_ai_ads(root, dist, production):
    source = root / 'src' / 'reason-ai-ads'
    ad = dist / 'ads/reason-ai/diagnosis/index.html'
    ad.parent.mkdir(parents=True, exist_ok=True)
    original = (root / 'src/reason-ai-lp.html').read_text()
    style, header = (source / 'hero.html').read_text().split('<!-- hero -->')
    html, count = re.subn(r'<header class="hero">.*?</header>', lambda _: header, original, flags=re.S)
    if count != 1:
        raise ValueError('Expected one current Reason AI hero')
    customer_dir = dist / 'ads/reason-ai/longest-customer'
    shutil.copytree(source / 'longest-customer', customer_dir, dirs_exist_ok=True)
    customer = customer_dir / 'index.html'
    if production:
        tags, fallback = tracking(json.loads((root / 'src/site-config.json').read_text()))
        customer.write_text(customer.read_text().replace('</head>', tags + '</head>').replace('<body>', '<body>' + fallback))
        html = html.replace('</head>', tags + '</head>').replace('<body id="top">', '<body id="top">' + fallback)
    ad.write_text(html.replace('</head>', style + '</head>'))
    shutil.copyfile(source / 'attribution.js', dist / 'assets/reason-ai-attribution-v1.js')
    script = '<script defer src="/assets/reason-ai-attribution-v1.js"></script>'
    for page in (ad, customer, *(dist / route / 'index.html' for route in ('branding/reason-ai', 'inquiry/reason-ai', 'inquiry/thanks'))):
        page.write_text(page.read_text().replace('</head>', script + '</head>', 1))
