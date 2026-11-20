"""Build the dedicated corporate-branding lead magnet without changing existing pages."""
import json
import re
import shutil

def build_branding_guide(root, dist, production):
    source = root / 'src' / 'branding-guide'
    target = dist / 'branding' / 'practical-guide'
    (target / 'thanks').mkdir(parents=True, exist_ok=True)
    for name in ('guide.pdf', 'cover-hd.webp', 'wellenetz-logo-tagline.png', 'steps.jpg', 'checklist.jpg', 'lead-flow.js'):
        shutil.copy2(source / name, target / name)
    for name, output in (('index.html', target / 'index.html'), ('thanks.html', target / 'thanks' / 'index.html')):
        text = (source / name).read_text()
        if not production:
            text = re.sub(r'<script>\(function\(w,d,s,l,i\).*?</script>', '', text)
        output.write_text(text)
    if production:
        shutil.copy2(source / 'lead-config.js', target / 'lead-config.js')
    else:
        config = {'mode': 'preview', 'formAction': '', 'thanksPath': '/branding/practical-guide/thanks/', 'downloadPath': '/branding/practical-guide/guide.pdf', 'trackingEnabled': False}
        (target / 'lead-config.js').write_text('window.BRANDING_LEAD_CONFIG = ' + json.dumps(config) + ';')

    ad_source = root / 'src' / 'ads-branding-guide'
    ad_target = dist / 'ads' / 'branding-guide'
    assets = ad_target / 'assets'
    assets.mkdir(parents=True, exist_ok=True)
    for name in ('cover-hd.webp', 'wellenetz-logo-tagline.png'):
        shutil.copy2(source / name, assets / name)
    shutil.copy2(ad_source / 'checklist-original.png', assets / 'checklist-original.png')
    shutil.copy2(ad_source / 'lead-flow.js', ad_target / 'lead-flow.js')
    ad_html = (ad_source / 'index.html').read_text()
    if production:
        shutil.copy2(ad_source / 'lead-config.js', ad_target / 'lead-config.js')
    else:
        ad_html = re.sub(r'<script>\(function\(w,d,s,l,i\).*?</script>', '', ad_html, flags=re.S)
        shutil.copy2(target / 'lead-config.js', ad_target / 'lead-config.js')
    (ad_target / 'index.html').write_text(ad_html)
