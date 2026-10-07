"""Display the provided logo sheet using CSS windows, without altering the asset."""
from html import escape
from pathlib import Path
import json
MARKETS = json.loads((Path(__file__).resolve().parent/"src/client-markets.json").read_text())
MARKET_LABELS = {"prime":"プライム", "standard":"スタンダード", "growth":"グロース"}
MARKET_ASSETS = {"prime":"jpx-prime.jpg", "standard":"jpx-standard.png", "growth":"jpx-growth.png"}
CLIENTS = [
    ('ASKUL', 42,25,148,44),
    ('公正取引委員会',234,27,237,46),
    ('ibis',532,25,126,50),
    ('ショクブン',710,18,168,58),
    ('チューリッヒ保険',955,15,124,101),
    ('雪印メグミルク',56,101,221,67),
    ('ENERES',303,81,167,64),
    ('大阪府歯科医師会',493,90,211,42),
    ('SUNSTAR',757,90,178,37),
    ('LIXIL',399,150,143,51),
    ('FUJI',603,148,168,53),
    ('MARUHA NICHIRO',807,142,272,47),
    ('BOAT RACE 浜名湖',44,189,260,56),
    ('朝日インテック株式会社',784,207,264,40),
    ('ろうきん',249,269,94,123),
    ('おいしい庄内空港',358,218,92,128),
    ('newgin',491,233,154,77),
    ('Cygames',674,262,167,56),
    ('和牛',970,281,92,95),
    ('名古屋証券取引所',420,342,208,62),
    ('LVN',651,344,148,48),
]

def client_logos():
    items = []
    for name,x,y,w,h in CLIENTS:
        # Keep the original proportions, cap both the horizontal and vertical footprint.
        width = min(160, 64*w/h)
        style = f'width:{width:.3f}px;aspect-ratio:{w}/{h}'
        if name == '名古屋証券取引所':
            style += ';clip-path:polygon(0 8%,30% 8%,30% 0,100% 0,100% 100%,0 100%)'
        image_style = f'width:{1096/w*100:.5f}%;left:{-x/w*100:.5f}%;top:{-y/h*100:.5f}%'
        market = MARKETS['clients'].get(name)
        badge = '<span class="client-market-slot" aria-hidden="true"></span>'
        caption = ''
        if market:
            key = market['market']
            label = MARKET_LABELS[key]
            caption = escape(market.get('caption',''))
            accessible = escape(f"{market['legal_name']}：東証{label}上場（証券コード{market['stock_code']}）")
            badge = f'<span class="client-market" role="img" aria-label="{accessible}"><span class="client-market-image client-market-image--{key}"><img src="/assets/{MARKET_ASSETS[key]}" alt="" aria-hidden="true" loading="lazy" decoding="async"></span><span class="client-market-label"><span>東証</span><strong>{label}</strong></span></span>'
        logo = f'<span class="client-logo-window" style="{style}" role="img" aria-label="{escape(name)}"><img src="/assets/client-logos-sheet.png" alt="" aria-hidden="true" loading="lazy" decoding="async" width="1096" height="409" style="{image_style}"></span>'
        if name == '雪印メグミルク':
            logo = '<img class="client-logo-standalone" src="/assets/client-meg-snow.svg" alt="雪印メグミルク" width="240" height="56.826" loading="lazy" decoding="async">'
        items.append(f'<li class="client-logo"><div class="client-logo-main">{logo}</div><span class="client-current-name">{caption}</span>{badge}</li>')
    return '<ul class="client-logo-grid" aria-label="ベレネッツの顧客ロゴ（一部）">'+''.join(items)+'</ul><p class="client-market-note">市場区分は東証上場企業について表示しています（2026年10月5日確認）。ロゴはお取引時の表記を含みます。</p>'
