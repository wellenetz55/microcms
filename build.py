from pathlib import Path
from html import escape as E
import json,re,urllib.parse,hashlib,sys,shutil
from navigation import desktop_navigation, mobile_navigation
from contact_form import contact_form
from thank_you import thank_you_content
ROOT=Path(__file__).resolve().parent;SRC=ROOT/'src'
PRODUCTION='--production' in sys.argv
if '--home-only' in sys.argv:raise SystemExit('SEO requires a complete build. Run python3 build.py without --home-only.')
DIST=ROOT/('dist-production' if PRODUCTION else 'dist')
if PRODUCTION:
 shutil.copytree(ROOT/'dist/assets',DIST/'assets',dirs_exist_ok=True)
ASSET_VERSION=hashlib.sha256((DIST/'assets/site.css').read_bytes()+(DIST/'assets/site.js').read_bytes()).hexdigest()[:12]
# Versioned filenames prevent old proxy/browser CSS from being reused after a partial upload.
for extension in ('css','js'):
 shutil.copy2(DIST/f'assets/site.{extension}',DIST/f'assets/site.{ASSET_VERSION}.{extension}')
sources=json.loads((SRC/'source-pages.json').read_text());cases=json.loads((SRC/'cases.json').read_text());inventory=[]
nav=[('/services/','事業内容'),('/overview/what_we_do/','私たちの強み'),('/case_study/','事例紹介'),('/overview/','会社情報'),('/news/','ニュース')]
def a(u,t,cl=''):return f'<a href="{E(u)}" class="{cl}">{t}</a>'
def button(u,t,cl=''):return a(u,t,'button '+cl)
def eyebrow(t):return f'<div class="eyebrow">{t}</div>'
def section(content,cl='',id=''):return f'<section class="section {cl}"'+(f' id="{id}"' if id else '')+f'><div class="wrap">{content}</div></section>'
def sh(en,jp,more=''):return f'<div class="section-head"><div>{eyebrow(en)}<h2>{jp}</h2></div>{more}</div>'
def card(u,en,title,desc,link_label='詳しく見る'):return a(u,f'{eyebrow(en)}<h3>{title}</h3><p>{desc}</p><span class="text-link">{link_label}</span>','card')
def cards(items):return '<div class="grid3">'+''.join(card(*i) for i in items)+'</div>'
def casecard(c):return a('/case_study/'+c['id']+'/',f'<div class="case-image"><img loading="lazy" src="/assets/{c["id"]}.jpg" alt="{E(c["category"])}の事例イメージ" width="380" height="380"><span class="case-no">CASE {c["id"][2:]}</span></div><span class="tag">{E(c["category"])}</span><h3>{E(c["title"])}</h3><span class="text-link">事例を読む</span>','case-card')
def footer(cta=True):
 groups=[('サービス',[('/branding/','ブランディング'),('/marketing/','マーケティング'),('/creative/','クリエイティブ制作'),('/wellenetz-menu/','課題から探す'),('/branding/approrach/','取り組み方')]),('Wellenetz',[('/overview/what_we_do/','私たちの強み'),('/overview/','会社概要'),('/overview/message/','代表メッセージ'),('/overview/history/','沿革'),('/overview/access/','アクセス')]),('知る・相談する',[('/case_study/','事例紹介'),('/news/','ニュース'),('/column/','コラム'),('/resources/','無料コンテンツ'),('/brandingseminar_free/','無料セミナー'),('/inquiry/','お問い合わせ')])]
 return ('<section class="contact-band"><div class="wrap"><div>'+eyebrow('LET’S FIND YOUR VALUE')+'<h2>その価値を、次の成長へ。</h2><p>まだ言葉になっていない課題も、まずはお聞かせください。</p></div>'+button('/inquiry/','無料相談・お問い合わせ','light')+'</div></section>' if cta else '')+'<footer class="site-footer"><div class="wrap"><div class="footer-top"><div><a class="footer-logo" href="/" aria-label="Wellenetz ホーム"><img src="/assets/wellenetz-logo-white.png" width="158" height="64" alt="Wellenetz ベレネッツ" loading="lazy"></a><div class="office"><strong>TOKYO OFFICE</strong><br>東京都中央区銀座1-15-4<br>ヒューリック銀座一丁目昭和通りビル7F<br><a href="tel:0362627485">03-6262-7485</a></div><div class="office"><strong>NAGOYA OFFICE</strong><br>名古屋市中区錦3-11-25 アーク栄錦ビル6F<br><a href="tel:0526849800">052-684-9800</a></div></div><div class="footer-links">'+''.join('<div><strong>'+t+'</strong>'+''.join(a(u,n) for u,n in ls)+'</div>' for t,ls in groups)+'</div></div><div class="footer-bottom"><div class="footer-legal">'+''.join(a(u,t) for u,t in [('/privacy-policy/','プライバシーポリシー'),('/handle_personal_data/','個人情報の取扱い'),('/cookie-policy/','Cookieポリシー'),('/specified_commercial_transactions/','特定商取引法に関する表示'),('/sitemap/','サイトマップ')])+'</div><span>© Wellenetz Inc.</span>'+a('#top','ページ上部へ','to-top')+'</div></div></footer>'
def page(path,title,body,en='',lead='',group='',hero=True,cta=True):
 head=f'<header class="site-header"><a href="/" class="logo" aria-label="Wellenetz ホーム"><img src="/assets/site-logo.png" alt="Wellenetz ベレネッツ" width="360" height="66"></a><nav class="desktop-nav" aria-label="メインナビゲーション">{desktop_navigation(path)}{button("/inquiry/","無料相談・お問い合わせ","orange")}</nav><button class="menu-toggle" aria-label="メニューを開く" aria-expanded="false" aria-controls="mobile-nav"><span></span><span></span></button></header><nav id="mobile-nav" class="mobile-nav" aria-label="モバイルナビゲーション">{mobile_navigation(path)}</nav>'
 ph=''
 if hero:ph='<div class="wrap"><nav class="breadcrumbs" aria-label="パンくず">'+a('/','HOME')+'<span>/</span>'+(a('/services/','事業内容')+'<span>/</span>' if group=='services' else '')+f'<span>{E(re.sub("<[^>]+>","",title))}</span></nav></div><section class="page-hero"><div class="wrap">'+eyebrow(en)+f'<h1>{title}</h1>'+(f'<p class="lead">{lead}</p>' if lead else '')+'</div></section>'
 html='<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="robots" content="noindex,nofollow"><title>'+E(re.sub('<[^>]+>','',title))+' | Wellenetz 株式会社ベレネッツ</title><meta name="description" content="'+E(re.sub('<[^>]+>','',lead or '伝わると惹き寄せるを創る。企業ブランディング・マーケティング・クリエイティブ制作を東京と名古屋から支援するベレネッツ。'))+'"><link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 32 32%27%3E%3Crect width=%2732%27 height=%2732%27 fill=%27%23142d3a%27/%3E%3Cpath d=%27M5 9l5 14 6-10 6 10 5-14%27 fill=%27none%27 stroke=%27%23ff986a%27 stroke-width=%273%27/%3E%3C/svg%3E"><link rel="stylesheet" href="/assets/site.'+ASSET_VERSION+'.css"><script src="/assets/site.'+ASSET_VERSION+'.js" defer></script></head><body id="top"><a class="skip" href="#main">本文へスキップ</a>'+head+'<main id="main">'+ph+body+'</main>'+footer(cta)+'</body></html>'
 file=DIST/path.strip('/')/'index.html' if path!='/' else DIST/'index.html';file.parent.mkdir(parents=True,exist_ok=True);file.write_text(html);inventory.append({'path':path,'title':title,'group':group or en})
services=[('/branding/','01 / BRANDING','ブランディング','隠れた価値を見つけ、「選ばれる理由」をつくる。'),('/marketing/','02 / MARKETING','マーケティング','価値が届く接点を設計し、顧客を惹き寄せる。'),('/creative/','03 / CREATIVE','クリエイティブ制作','戦略を、伝わるデザインと行動につながる体験へ。')]
news=[p for p in sources if '/news/' in p['url'] and p['url'].rstrip('/')!='https://www.wellenetz.co.jp/news']
columns=[p for p in sources if '/column/' in p['url'] and p['url'].rstrip('/')!='https://www.wellenetz.co.jp/column']
def sourcepath(p):return urllib.parse.unquote(urllib.parse.urlparse(p['url']).path)
def date(p):
 if p.get('_cms'):
  from datetime import datetime, timezone, timedelta
  return datetime.fromisoformat(p['_cms']['date']).astimezone(timezone(timedelta(hours=9))).strftime('%Y.%m.%d')
 # Legacy publication dates verified against the original news/column listings.
 # Never infer publication dates from dates mentioned in the article body.
 dates={'chimeido_up':'2026.07.30','btob_branding_step':'2026.07.10','printcenter':'2026.01.09','shoten':'2026.07.31','osaji':'2026.07.28',
        'newcolumn09232025':'2025.09.23','企業ブランディング基礎に「失敗しない！企業ブ':'2025.07.09',
        '動画「ai活用に躊躇している会社のための利用ガイ':'2024.10.03','for_financial':'2024.08.30'}
 return dates.get(sourcepath(p).rstrip('/').split('/')[-1],'')

def article_sort(p):
 from datetime import datetime, timezone, timedelta
 if p.get('_cms'):return datetime.fromisoformat(p['_cms']['date']).timestamp()
 value=date(p)
 return datetime.strptime(value,'%Y.%m.%d').replace(tzinfo=timezone(timedelta(hours=9))).timestamp() if value else 0
news.sort(key=article_sort,reverse=True);columns.sort(key=article_sort,reverse=True)
def article_time(p):
 value=date(p)
 return f'<time datetime="{value.replace(".","-")}">{value}</time>' if value else '<span class="date-unknown">公開日未登録</span>'
def newsrows(ps,label=None):
 return '<div class="news-list">'+''.join(a(sourcepath(p),article_time(p)+f'<span class="tag">{label or ("COLUMN" if sourcepath(p).startswith("/column/") else "NEWS")}</span><h3>{E(p["title"])}</h3>','news-row') for p in ps)+'</div>' 
# Numbered MP4 filenames define the homepage background sequence.
hero_clips=sorted((p for p in (DIST/'assets/videos').glob('*') if p.is_file() and p.suffix.lower()=='.mp4'),key=lambda p:p.name.lower())
hero_video_sources=['/assets/videos/'+urllib.parse.quote(p.name) for p in hero_clips]
hero_media=('<div class="hero-videos" aria-hidden="true" data-hero-videos="'+E(json.dumps(hero_video_sources))+'"></div><button class="hero-video-toggle" type="button" hidden aria-label="背景動画を一時停止">動画を一時停止</button>') if hero_clips else ''
hero='<section class="hero"><img class="hero-photo" src="/assets/hero.jpg" alt="ブランドの価値を言葉にするワークショップ" width="1800" height="1013" fetchpriority="high">'+hero_media+'<div class="wrap hero-content">'+eyebrow('BRANDING × MARKETING × CREATIVE')+'<h1><span>いい会社を、</span><span><em>選ばれる会社</em>に。</span></h1><p>商品も、技術も、変えません。<br>変えるのは、顧客からの「見え方」です。<br>ベレネッツは、まだ伝わっていない価値を見つけます。</p><div class="actions">'+button('/overview/what_we_do/','ベレネッツができること','light')+button('/wellenetz-menu/','自社の課題から探す','outline')+'</div><div class="hero-bottom"><span>WELLENETZ INC. — TOKYO / NAGOYA</span></div></div></section>'
def track_record():return '<div class="wrap intro-strip" id="track-record"><div class="intro-note"><span class="record-label">OUR TRACK RECORD</span>価値の発見から、実行まで。<br>企業の成長に、一貫して伴走。</div><div class="record-metric"><div class="stat"><span class="stat-value">25</span><small>年以上</small></div><p>ブランディング支援の経験。<br>業績向上につながるブランディング。</p></div><div class="record-metric"><div class="stat"><span class="stat-value">750</span><small>社超</small></div><p>企業の「選ばれる理由」に向き合う。<br>BtoB企業向けが7割。</p></div></div>'
home=hero+track_record()
from client_logos import client_logos
home+=section(sh('OUR CLIENTS','ベレネッツの顧客（一部）')+client_logos(),'clients-section',id='clients')
home+=section('<div class="split"><div>'+eyebrow('OUR PERSPECTIVE')+'<h2>営業・広告・値下げに頼らず、価値で選ばれる。</h2>'+a('/overview/what_we_do/','私たちの強みを知る','text-link')+'</div><div><p>技術も、実績も、想いもある。<br>それなのに、なぜか顧客に伝わらない。</p><p>私たちは、商品やサービスを変えません。社内では当たり前になっている「隠れた価値」を発見し、独自のT.R.U.S.T.理論でブランドの脚本に。広告で押すのではなく、顧客のほうから選びに来る状態をつくります。</p></div></div>')
home+=section(sh('OUR SERVICES','伝わる。惹き寄せる。動き出す。',a('/services/','すべての事業を見る','text-link'))+'<div class="services">'+''.join(a(u,f'<span class="num">0{i+1}</span><div><span class="en">{en.split(" / ")[1]}</span><h3>{t}</h3></div><p>{d}</p><span class="end">サービスを知る</span>','service-row') for i,(u,en,t,d) in enumerate(services))+'</div>','soft')
home+=section(sh('SELECTED CASES','価値が変えた、企業のストーリー。',a('/case_study/','24の事例を見る','text-link'))+'<div class="grid3">'+''.join(casecard(c) for c in cases[:3])+'</div>')
home+=section('<div class="split"><div>'+eyebrow('OUR METHOD')+'<h2>感覚だけに頼らない。<br>再現性高いブランディング。</h2><p>企業の価値を、顧客にとっての価値へ。<br>ベレネッツ独自のブランディングメソッド<br>T.R.U.S.T.が、その接点を見つけます。</p>'+button('/branding/','T.R.U.S.T.理論を知る','light')+'</div><div class="method-panel"><p class="method-owner">ベレネッツ独自のブランディングメソッド</p><div class="big-en">T.R.U.S.T.</div><div class="method-band">'+''.join(f'<div class="method-letter"><strong>{c}</strong><span>{t}</span></div>' for c,t in [('T','透明性'),('R','衝撃性'),('U','独自性'),('S','必然性'),('T','物語性')])+'</div><p style="margin-top:30px">すべてを揃えるのではなく、貴社に合う要素を見極め、組み合わせます。</p></div></div>','dark',id='method')
updates=sorted(news+columns,key=article_sort,reverse=True)
home+=section(sh('NEWS & INSIGHTS','ベレネッツからのお知らせ。','<div class="actions">'+a('/news/','ニュース一覧','text-link')+a('/column/','コラム一覧','text-link')+'</div>')+newsrows(updates[:6]),id='updates')
home+=section('<div class="split"><div>'+eyebrow('ABOUT WELLENETZ')+'<h2>東京と名古屋から、<br>企業の可能性をひらく。</h2><p>ブランドの脚本づくりから、上演まで。<br>企業ブランディングとマーケティングの専門会社です。</p></div><div>'+cards([('/overview/','COMPANY','会社情報','私たちの概要・拠点について。'),('/overview/message/','MESSAGE','代表メッセージ','ブランディングに込める想い。')])+'</div></div>','soft')
page('/','伝わる、その先へ。',home,hero=False)
# Reusable page components and full page inventory.
def source_for(path):return next((p for p in sources if sourcepath(p)==path),None)
def localize(u):
 if u.startswith('https://www.wellenetz.co.jp/'):
  p=urllib.parse.unquote(urllib.parse.urlparse(u).path)
  if p in {sourcepath(s) for s in sources} or p.startswith('/case_study/') or p=='/':return p
 return u

def article(p):
 if p.get('_cms'):
  data=p['_cms']
  cover=('<img class="cms-cover" src="'+E(data['cover'])+'" alt="'+E(p['title'])+'">') if data.get('cover') else ''
  return '<article class="prose cms-article"><p class="cms-date"><time datetime="'+E(data['date'])+'">'+date(p)+'</time></p>'+cover+data['body']+'</article>'
 chunks=[];toc=[];n=0;seen=set()
 for b in p['blocks']:
  t=b['text'].strip();tag=b['tag']
  if tag=='h1' or t in seen or t in ['TOP','会社概要','ベレネッツができること','代表挨拶','沿革','アクセス','取り組み方','目的別パッケージ'] or t.startswith('TOP >') or not t:continue
  if len(t)<3:continue
  seen.add(t)
  if tag in ['h2','h3','h4']:
   n+=1;toc.append((f'#section-{n}',t));chunks.append(f'<h2 id="section-{n}">{E(t)}</h2>')
  else:
   text=E(t)
   for label,u in b.get('links',[]):
    if label.strip() and E(label) in text:text=text.replace(E(label),a(localize(u),E(label)),1)
   chunks.append(f'<p>{text}</p>')
 aside='<aside class="article-aside"><strong>このページの内容</strong>'+''.join(a(u,E(t[:34])) for u,t in toc[:10])+'</aside>'
 return '<div class="article-layout">'+aside+'<article class="prose">'+('<p class="cms-date">'+article_time(p)+'</p>' if date(p) else '')+''.join(chunks)+f'<p class="source-link">掲載情報：{a(p["url"],"Wellenetz公式サイト")}</p></article></div>'
def branch_nav(items,path):return '<nav class="wrap subnav" aria-label="関連ページ">'+''.join(f'<a href="{u}"'+(' aria-current="page"' if path==u else '')+f'>{t}</a>' for u,t in items)+'</nav>'
service_nav=[('/services/','すべての事業'),('/branding/','ブランディング'),('/marketing/','マーケティング'),('/creative/','クリエイティブ制作'),('/branding/approrach/','取り組み方')]
company_nav=[('/overview/','会社概要'),('/overview/what_we_do/','私たちの強み'),('/overview/message/','代表メッセージ'),('/overview/history/','沿革'),('/overview/access/','アクセス')]
from branding_pages import PROGRAMS, program_cards, build_branding_pages
programs=PROGRAMS
page('/services/','価値を見つけ、<br>成長につなげる。',section(sh('THREE CORE SERVICES','3つの力で、事業を前へ。')+cards(services))+section(sh('BRANDING PROGRAMS','課題に合わせた、3つの支援。')+program_cards(),'soft')+section(sh('YOUR CHALLENGE','解決したい課題から探す。')+cards([('/wellenetz-menu/','CHALLENGE','経営課題別アプローチ','認知・価格競争・集客・採用。貴社の悩みから支援を探せます。'),('/branding/approrach/','PROJECT FLOW','プロジェクトの進め方','現状分析からコンセプト設計、戦略策定、実行・改善まで。'),('/overview/proposal/','FIRST STEP','ご提案までの流れ','現状をお聞きし、課題の整理からご提案します。')])),en='OUR SERVICES',lead='ブランディング、マーケティング、クリエイティブ。戦略から実行まで、一つのチームで。')
trust=[('T','Transparency','透明性','見えなかった価値やプロセスを、見える形に。'),('R','Remarkability','衝撃性','顧客の認識に、新しい発見を生み出す。'),('U','Uniqueness','独自性','他社では代えられない、選ぶ理由を明らかに。'),('S','Significance','必然性','顧客にとって、なぜ必要なのかを伝える。'),('T','Tale','物語性','価値の背景を、人の心に届くストーリーへ。')]
trusthtml='<div class="services">'+''.join(f'<div class="service-row"><span class="num" style="font-size:36px">{c}</span><div><span class="en">{en}</span><h3>{jp}</h3></div><p>{d}</p></div>' for c,en,jp,d in trust)+'</div>'
build_branding_pages(page, section, sh, eyebrow, button, a, branch_nav(service_nav,'/branding/'), trusthtml)
for path,en,title,intro,body,external in [('/branding/forbidden/','FORBIDDEN BRANDING','禁断のブランディング®','貴社に眠る価値を発見し、ブランドを再構築する。',[('隠れている価値を、発見する。','技術、実績、現場の工夫。社内では当たり前になっていることの中に、顧客にとって大切な価値が隠れているかもしれません。T.R.U.S.T.理論を用い、企業・製品・サービスを捉え直します。'),('認知から、行動までを設計。','発見した価値をブランドのコンセプトへ。ターゲット層に認知され、行動につながる戦略の構築・実行まで支援します。')],'https://corporate-branding.jp/forbidden_branding/'),('/branding/jitan/','JITAN BRANDING','時短ブランディング®','顧客の思い込みを変え、価値が伝わる状態へ。',[('顧客の思い込み・誤認識に向き合う。','企業・商品・サービス自体は変えずに、顧客が持つ思い込みや誤認識に働きかけます。本来の価値が伝わることを妨げている認識を特定し、顧客からの見え方を変えていきます。'),('必要な変化に、集中する。','ブランド全体の再構築ではなく、認識を変える戦略に焦点を当てることで、取り組みのプロセスを短縮。顧客との関係を強める接点をつくります。')],'https://corporate-branding.jp/jitan_branding/')]:
 page(path,title,section('<div class="split"><div class="statement">'+intro+'</div><div class="prose">'+''.join('<h2>'+h+'</h2><p>'+t+'</p>' for h,t in body)+button(external,'公式サービスサイトを見る')+'</div></div>')+section(sh('RELATED PROGRAMS','関連する支援。')+program_cards([p for p in programs if p[0] != path]),'soft'),en=en,lead=intro,group='services')
marketingitems=[('/marketing/support/','01 / MARKETING SUPPORT','マーケティング支援','WEB・コンテンツ・動画・SNSをつなぎ、顧客が自ら知りたくなる接点を設計。','詳細'),('/marketing/small-short-term-insurance/','02 / BUSINESS DEVELOPMENT','事業開発','既存の顧客基盤や強みを起点に、事業コンセプトとブランドを設計。','少額短期保険事業参入支援'),('/marketing/kinqr/','03 / DIGITAL SERVICE','デジタルサービス','企業や自治体の課題を解決する、新しいデジタルの仕組みを提供。','緊QR')]
from marketing_pages import build_marketing_pages
build_marketing_pages(page, section, sh, eyebrow, button, a, cases, casecard)
page('/creative/','伝わる戦略を、<br>動き出す体験に。',branch_nav(service_nav,'/creative/')+section('<div class="split"><div>'+eyebrow('CREATIVE')+'<h2>目標から逆算する、<br>クリエイティブ。</h2></div><div><p>ブランドの本質的な価値を、デザインと言葉に。一貫した表現で、顧客の理解と次の行動を支えます。</p><p>WEBサイト、動画、営業資料、ロゴ、各種デザイン。ブランディングとマーケティングを理解した社内チームが、戦略から制作までつなぎます。</p></div></div>')+section(sh('WHAT WE CREATE','価値を届ける、さまざまな接点。')+'<div class="grid2">'+''.join('<div class="card">'+eyebrow(en)+'<h3>'+t+'</h3><p>'+d+'</p></div>' for en,t,d in [('WEB / DIGITAL','WEBサイト・LP','企業サイト、オウンドメディア、ランディングページ。利用者の目的に合わせて設計します。'),('MOVIE / CONTENT','動画・コンテンツ','文章だけでは伝えきれない価値やストーリーを、映像とコンテンツで伝えます。'),('VISUAL IDENTITY','ロゴ・ブランドデザイン','ロゴ、色、文字、イメージを通じて、ブランドの個性を一貫した形にします。'),('BRAND MANAGEMENT','ガイドライン・運用支援','表現の基準を明文化し、社内外でブランドの一貫性を保つ運用を支援します。')])+'</div>','soft')+section(sh('DESIGN SERVICES','ロゴ制作の専門サービス。')+'<div class="grid2">'+card('https://logo.jp/','ONLINE','logo.jp','オンラインでのロゴ制作サービス。')+card('https://logomark.jp/','CONSULTATION','logomark.jp','打ち合わせを通じて進めるロゴ制作サービス。')+'</div>'),en='CREATIVE',lead='ブランドの理解を土台に、目標達成のためのデザインを制作します。',group='services')
page('/overview/what_we_do/','貴社に強みはある。<br>伝わっていないだけ。',branch_nav(company_nav,'/overview/what_we_do/')+section('<div class="split"><div class="statement">「うちの強みは何か」<br>社内で答えが、<br>揃いますか。</div><div><p>技術力、実績、社風、現場の対応力。社内で「当たり前」になっているものほど言葉にされず、競合と同じ説明になってしまいます。</p><p>私たちはその「隠れた価値」を発掘し、顧客が選ぶ理由へと言葉にします。感覚ではなく理論にもとづくため、社内の説明や合意形成にも使えます。25年以上の経験知と生成AIを組み合わせ、実行まで支援します。</p></div></div>')+section(sh('FROM STORY TO ACTION','脚本づくりから、上演まで。')+cards(services),'soft')+track_record()+section(sh('WHY WELLENETZ','ベレネッツが選ばれる、3つの理由。')+'<div class="flow"><div><span class="num">01</span><h3>感覚ではなく、理論で進める</h3><p>T.R.U.S.T.理論にもとづくので、判断の根拠を社内で説明できる。</p></div><div><span class="num">02</span><h3>つくって終わりにしない</h3><p>ブランドの脚本から、WEB構築・運用までを社内でつなぐ。</p></div><div><span class="num">03</span><h3>型に当てはめない</h3><p>5つの要素すべてではなく、貴社に合うものを見極めて組み合わせる。</p></div></div><div class="actions">'+button('/overview/proposal/','ご提案までの流れ')+'</div>'),en='WHY WELLENETZ',lead='商品も技術も変えずに、顧客からの見え方を変える。それがベレネッツの仕事です。')
page('/overview/proposal/','まず、貴社を知ることから。',section('<div class="split"><div>'+eyebrow('OUR PROPOSAL')+'<h2>ご提案まで、無料です。</h2></div><div><p>決まった営業資料をお見せするのではなく、貴社の現状を分析したうえで、ご提案をつくります。課題やご希望の進め方を、まずはお聞かせください。</p><p>ご提案をご覧いただいてから、実施するかをご判断いただけます。</p></div></div><div class="flow"><div><span class="num">01 / HEARING</span><h3>初回面談</h3><p>対面またはオンラインで、事業・課題・目標をヒアリング。</p></div><div><span class="num">02 / PROPOSAL</span><h3>分析と初期提案</h3><p>現状を整理し、進め方・概算見積・スケジュールをご提示。</p></div><div><span class="num">03 / DECISION</span><h3>ご検討・ご判断</h3><p>内容に納得いただいてから、プロジェクトを開始します。</p></div></div>')+section('<div class="split"><div>'+eyebrow('PROJECT FLOW')+'<h2>ご提案の、その先へ。</h2></div><div><p>プロジェクト開始後は、現状分析、コンセプト設計、戦略策定、浸透策・制作、運用・PDCAへ。一貫したフローで実行と改善までつなぎます。</p><div class="actions">'+button('/branding/approrach/#project-flow','プロジェクトフローを見る')+'</div></div></div>','soft'),en='PROPOSAL',lead='貴社の課題を整理し、オーダーメイドのご提案へ。')
from project_flow import build_project_flow
build_project_flow(page, section, sh, eyebrow, button)
issues=[('知名度で競合に負けてしまう','広く名前を知られることより、必要とする顧客に「選ばれる理由」が伝わることを目指します。','/branding/forbidden/'),('価格競争から抜け出したい','顧客が得られる価値を言語化し、価格以外の判断基準をつくります。','/branding/'),('自社の特徴や強みが伝わらない','企業側の言葉を顧客の言葉へ。価値の理解を妨げる思い込みを整理します。','/branding/jitan/'),('新規事業の打ち出し方が決まらない','強み・顧客基盤・業界知識と、顧客の課題を結びつけて事業の軸を考えます。','/marketing/'),('WEBサイトからの問い合わせが増えない','メッセージ、情報の順番、相談までの流れを一体で見直します。','/creative/'),('広告の反応が悪い','広告だけに依存せず、検索・コンテンツ・SNSを通じた情報資産を育てます。','/marketing/support/'),('SNSが発信だけで終わっている','潜在ニーズに気づくきっかけとなるコンテンツを設計します。','/branding/sns_branding/'),('採用の応募が集まらない','働く環境と成長機会を捉え直し、企業の魅力を必要な人に届けます。','/branding/recruitment_branding/'),('社内の一体感が生まれない','ブランドの想いと社員の行動をつなぐ言葉とストーリーを整理します。','/branding/'),('投資家に事業の良さが伝わらない','技術の説明から、市場にどんな変化を生む事業なのかが伝わる構成へ。','/branding/branding_for_venture_Investment/'),('営業やプレゼンで興味を持たれない','顧客の課題と導入後の変化を、理解しやすい言葉やデザインで伝えます。','/creative/'),('顧客がまだ課題に気づいていない','意思決定者の潜在的な悩みを言語化し、気づきと解決への接点をつくります。','/branding/attracting_branding/')]
page('/wellenetz-menu/','その課題は、<br>「伝わり方」で変えられる。',section('<div class="split"><div>'+eyebrow('FIND YOUR APPROACH')+'<h2>気になる課題を<br>選んでください。</h2><p>一つに絞れなくても大丈夫です。<br>課題同士のつながりから、一緒に整理します。</p></div><div class="issue-list">'+''.join(f'<details><summary>{t}</summary><p>{d}</p>'+a(u,'関連するサービスを見る','text-link')+'</details>' for t,d,u in issues)+'</div></div>'),en='YOUR CHALLENGE',lead='認知、差別化、集客、採用。いま貴社が解決したいことから、適したアプローチへ。')
# Cases: all 24 published case summaries, detailed pages and industry archives.
categorymap={c['categorySlug']:c['category'] for c in cases}
def caselist(selected='all'):
 shown=[c for c in cases if selected=='all' or c['categorySlug']==selected]
 html='<input class="search-field" type="search" aria-label="事例をキーワードで検索" placeholder="業種やキーワードで検索" data-search>'
 html+='<div class="filters" aria-label="業種で絞り込み">'+''.join(f'<button class="filter" data-filter="{slug}" aria-pressed="{str(slug=="all").lower()}">{t}</button>' for slug,t in ([('all','すべて')]+list(categorymap.items()) if selected=='all' else [('all',categorymap[selected])]))+'</div>'
 html+=f'<p class="results-count" data-count aria-live="polite">{len(shown)}件の事例</p><div class="grid3">'+''.join(f'<div data-category="{c["categorySlug"]}">{casecard(c)}</div>' for c in shown)+'</div><p class="no-result" data-empty hidden>該当する事例がありません。別のキーワードでお試しください。</p>'
 return html
page('/case_study/','価値の発見が、<br>企業の次をつくる。',section(caselist()),en='CASE STUDIES',lead='さまざまな業種でのブランディング支援をご紹介。より具体的な実例は、ご相談・セミナー時にお伝えしています。')
for c in cases:
 page('/case_study/'+c['id']+'/',c['title'],section('<div class="case-detail"><img src="/assets/'+c['id']+'.jpg" alt="'+c['category']+'の事例イメージ" width="380" height="380"><div>'+eyebrow('CASE '+c['id'][2:]+' / '+c['category'])+'<h2>取り組みの背景とアプローチ</h2><div class="prose">'+''.join('<p>'+E(t)+'</p>' for t in c['text'].split('\n') if t)+'</div><div class="actions">'+button('/inquiry/','自社の課題を相談する')+'</div><p class="source-link" style="font-size:13px;margin-top:24px">'+a('https://www.wellenetz.co.jp/case_study/','公式サイト掲載事例をもとに構成')+'</p></div></div>')+section(sh('MORE CASES','ほかの事例も読む。',a('/case_study/','すべての事例','text-link'))+'<div class="grid3">'+''.join(casecard(x) for x in cases if x!=c)[:0]+'</div>' if False else sh('MORE CASES','ほかの事例も読む。',a('/case_study/','すべての事例','text-link'))+'<div class="grid3">'+''.join(casecard(x) for x in [x for x in cases if x!=c][:3])+'</div>','soft'),en='CASE '+c['id'][2:],lead=c['category']+'のブランディング事例')
for slug,title in categorymap.items():page('/case_category/'+slug+'/',title+'の事例',section(caselist(slug))+'<div class="wrap" style="padding-bottom:55px">'+a('/case_study/','全業種の事例を見る','text-link')+'</div>',en='CASE STUDIES',lead='業種ごとに、価値の発見と伝え方のアプローチをご紹介します。')
# Company and access.
facts=[('会社名','株式会社ベレネッツ / Wellenetz Inc.'),('代表取締役','平松 誠一'),('設立','1983年6月1日'),('資本金','4,500万円'),('事業内容','ブランディング事業<br>マーケティング事業<br>クリエイティブ制作事業'),('東京 OFFICE','〒104-0061 東京都中央区銀座1-15-4<br>ヒューリック銀座一丁目昭和通りビル7F<br>TEL：03-6262-7485 / FAX：03-6262-7486'),('名古屋 OFFICE','〒460-0003 名古屋市中区錦3-11-25<br>アーク栄錦ビル6F<br>TEL：052-684-9800 / FAX：052-684-9797')]
page('/overview/','価値を信じ、<br>可能性をひらく。',branch_nav(company_nav,'/overview/')+section('<div class="split"><div>'+eyebrow('COMPANY PROFILE')+'<h2>会社概要</h2><p>株式会社ベレネッツ<br>Wellenetz Inc.</p></div><table class="fact-table"><tbody>'+''.join('<tr><th scope="row">'+k+'</th><td>'+v+'</td></tr>' for k,v in facts)+'</tbody></table></div>')+section(sh('ABOUT US','ベレネッツを知る。')+cards([('/overview/message/','MESSAGE','代表メッセージ','顧客に価値が伝わるブランディングとは。'),('/overview/history/','HISTORY','沿革','オンラインデザインから、ブランド支援へ。'),('/overview/access/','ACCESS','拠点・アクセス','東京・銀座と、名古屋・錦から。')]),'soft'),en='COMPANY',lead='東京・名古屋を拠点に、企業ブランディングとマーケティングを支援します。')
page('/overview/access/','お会いできることを、<br>楽しみにしています。',branch_nav(company_nav,'/overview/access/')+section('<div class="grid2">'+''.join('<article class="card">'+eyebrow(en)+'<h2 style="font-size:32px;margin:20px 0">'+jp+'</h2><p>'+address+'</p><p>'+a('tel:'+tel.replace('-',''),tel)+'</p><div class="actions">'+button('https://www.google.com/maps/search/?api=1&query='+urllib.parse.quote(query),'Google マップで見る','outline')+'</div></article>' for en,jp,address,tel,query in [('TOKYO OFFICE','東京オフィス','〒104-0061 東京都中央区銀座1-15-4<br>ヒューリック銀座一丁目昭和通りビル7F','03-6262-7485','東京都中央区銀座1-15-4'),('NAGOYA OFFICE','名古屋オフィス','〒460-0003 名古屋市中区錦3-11-25<br>アーク栄錦ビル6F','052-684-9800','名古屋市中区錦3-11-25')])+'</div>'),en='ACCESS',lead='ご来訪の際は、事前にお問い合わせください。オンラインでのご相談にも対応しています。')
page('/overview/history/','変化の先に、<br>新しい選ばれ方を。',branch_nav(company_nav,'/overview/history/')+section('<div class="split"><div>'+eyebrow('OUR JOURNEY')+'<h2>ベレネッツの歩み</h2></div><div>'+''.join(f'<div class="timeline-item"><strong>{year}</strong><div><h3>{title}</h3><p>{desc}</p></div></div>' for year,title,desc in [('1983','会社設立','6月1日、会社設立。'),('1996','独立への一歩','代表・平松誠一がNTTドコモを退社。広告宣伝・マーケティングの経験から、新たなアプローチを模索。'),('1999','デザインを、オンラインで','デザインアウトソーシングやオンラインでのロゴ制作サービスを開始。'),('2000s','ブランディングへ進化','2000年代中期より、顧客を自然に惹き寄せるブランディング事業を本格化。'),('2023','価値の発見を、さらに深く','禁断のブランディングへアップグレード。時短ブランディングとともに、企業の「伝わる力」を支援。')])+'</div></div>'),en='HISTORY',lead='顧客を惹き寄せる仕組みを問い続け、事業を進化させてきました。')
# Each inquiry category posts to its own form.run endpoint.
contacttypes=[('general','総合お問い合わせ','サービス・ブランディングに関するご相談'),('interview_requests','メディアのお問い合わせ','取材・広報に関するご連絡'),('instructor_requests','講師ご依頼','企業ブランディングなどの講演・研修'),('jv','協業・提携のご相談','JV・パートナーシップに関するご連絡')]
page('/inquiry/','まだ言葉にならない課題も、<br>お聞かせください。',section(sh('CONTACT','お問い合わせ内容をお選びください。')+'<div class="grid2 inquiry-options">'+''.join(card('/inquiry/'+id+'/',f'0{i+1} / CONTACT',t,d) for i,(id,t,d) in enumerate(contacttypes))+'</div>')+section('<div class="split"><div>'+eyebrow('BY PHONE')+'<h2>お電話でのご相談</h2></div><div><p>東京 '+a('tel:0362627485','03-6262-7485')+'<br>名古屋 '+a('tel:0526849800','052-684-9800')+'</p></div></div>','soft'),en='CONTACT',lead='まずはご相談内容を整理するところから。初期のご提案まで無料で対応しています。')
for id,t,d in contacttypes:
 page('/inquiry/'+id+'/',t,section(contact_form(id)),en='CONTACT / '+id.replace('_',' ').upper(),lead=d)
# News and columns have real article detail routes.
page('/news/','ニュース・お知らせ',section(newsrows(news,'NEWS'))+'<div class="wrap" style="padding-bottom:60px">'+a('https://www.wellenetz.co.jp/news/','過去のニュースを公式サイトで読む','text-link')+'</div>',en='NEWS',lead='ベレネッツの活動や、新しいコンテンツの公開情報をお届けします。')
page('/column/','視点が変わると、<br>事業が変わる。',section(newsrows(columns,'COLUMN'))+'<div class="wrap" style="padding-bottom:60px">'+a('https://www.wellenetz.co.jp/column/','過去のコラムを公式サイトで読む','text-link')+'</div>',en='INSIGHTS / COLUMN',lead='ブランディングとマーケティングの現場から、企業の可能性を考えるコラム。')
page('/resources/','ブランドを考える、<br>最初の一歩に。',section(sh('KNOWLEDGE & RESOURCES','学ぶ・読む・相談する。')+cards([('https://corporate-branding.jp/useful_contents/','RESOURCES','無料コンテンツ','企業ブランディングを学ぶ資料・コンテンツを、公式サービスサイトで公開しています。'),('/brandingseminar_free/','ONLINE SEMINAR','無料ブランディングセミナー','ブランディングの考え方や、具体的な実例を学ぶ。'),('/column/','INSIGHTS','コラム','企業や市場を捉え直す、ブランディングの視点。')]))+section(sh('SELF CHECK','自社の現状を整理したい方へ。')+'<div class="grid2">'+card('https://www.wellenetz.co.jp/forms/branding-diagnosis-app.html','BRANDING DIAGNOSIS','BtoBブランディング必要度診断','公式サイトの診断で、自社の状況を振り返る。')+card('/wellenetz-menu/','YOUR CHALLENGE','課題別アプローチ','解決したい課題から、適したサービスを見つける。')+'</div>','soft'),en='FREE RESOURCES',lead='無料コンテンツ、セミナー、コラム。貴社の状況に合う入り口をお選びください。')
# Source-led branches retain factual detail and legal wording.
custom={i['path'] for i in inventory}
titles={'/branding/sns_branding/':('SNSブランディング','SOCIAL BRANDING','潜在ニーズを呼び覚まし、顧客の「知りたい」を育てる。'),'/branding/attracting_branding/':('BtoB集客ブランディング','BtoB BRANDING','意思決定者の潜在的な課題を、解決策との出会いにつなげる。'),'/branding/recruitment_branding/':('採用ブランディング','RECRUITMENT BRANDING','企業の隠れた魅力と、まだ出会えていない人材をつなぐ。'),'/branding/branding_for_venture_Investment/':('出資獲得のためのブランディング','STARTUP BRANDING','技術の価値を、投資家に届く事業の言葉へ。'),'/marketing/support/':('マーケティング支援','MARKETING SUPPORT','顧客が自ら興味を持ち、調べ、相談したくなる仕組みをつくる。'),'/marketing/small-short-term-insurance/':('少額短期保険事業参入支援','BUSINESS DEVELOPMENT','既存の強みから、選ばれる保険事業のコンセプトをつくる。'),'/marketing/kinqr/':('緊急時情報管理サービス「緊QR」','DIGITAL SERVICE','平時も、緊急時も。同じQRコードから必要な情報へ。'),'/overview/unique_branding/':('ブランディングが向き合う経営課題','BUSINESS IMPACT','選ばれる理由を明確にし、事業の課題を解決するために。'),'/overview/message/':('ブランディングは、顧客の認識をつくること。','MESSAGE','代表取締役 平松 誠一からのメッセージ。'),'/brandingseminar_free/':('無料ブランディングセミナー','ONLINE SEMINAR','企業ブランディングの考え方を、具体的な事例から。')}
for p in sources:
 path=sourcepath(p)
 if path in custom or 'error' in p:continue
 title,en,lead=titles.get(path,(E(p['title']) if p.get('_cms') else p['title'],'COLUMN' if '/column/' in path else 'NEWS' if '/news/' in path else 'POLICY',''))
 contents=article(p)
 if path=='/overview/message/':contents='<div class="split" style="margin-bottom:60px"><img class="portrait" src="/assets/author_hiramatsu.png" alt="代表取締役 平松誠一"><div>'+eyebrow('REPRESENTATIVE DIRECTOR')+'<h2 style="font-size:38px;margin:20px 0">平松 誠一</h2><p>Seiichi Hiramatsu</p><p>NTTドコモ出身。広告宣伝・マーケティングの経験を経て、企業の価値が伝わるブランディングを支援。</p></div></div>'+contents
 if path=='/brandingseminar_free/':contents='<div class="actions" style="margin:0 0 40px">'+button(p['url'],'開催情報・お申し込みは公式サイトへ','orange')+'</div>'+contents
 related=''
 if path.startswith(('/branding/','/marketing/')):related=section(sh('EXPLORE MORE','関連するサービス。')+cards(services),'soft')
 page(path,title,section(contents)+related,en=en,lead=lead,group='services' if path.startswith(('/branding/','/marketing/')) else '')
# Readable full inventory, exact old paths retained for the principal branches.
links='<div class="grid3">'
for group,prefix in [('事業・サービス',['/services/','/branding/','/marketing/','/creative/','/wellenetz-menu/']),('会社情報',['/overview/']),('事例・ニュース・ご相談',['/case_study/','/news/','/column/','/inquiry/','/resources/','/brandingseminar_free/'])]:
 links+='<div><h2 style="font-size:24px;margin-bottom:20px">'+group+'</h2>'+''.join('<p style="margin:0 0 14px;font-size:14px">'+a(p['path'],re.sub('<[^>]+>','',p['title']))+'</p>' for p in inventory if any(p['path'].startswith(x) for x in prefix) and '/case_study/ex' not in p['path'])+'</div>'
links+='</div>'
page('/sitemap/','サイトマップ',section(links),en='SITE MAP',lead='Wellenetzの事業・事例・企業情報をご案内します。')
# Completion page is intentionally absent from public navigation and sitemap.
page('/inquiry/thanks/','お問い合わせありがとうございます',thank_you_content(),en='THANK YOU',hero=False,cta=False)
page('/404/','ページが見つかりません',section('<div class="error-page"><h2>404</h2><p>URLをご確認いただくか、トップページからお探しください。</p><div class="actions">'+button('/','トップページへ')+button('/sitemap/','サイトマップ','outline')+'</div></div>'),en='NOT FOUND')
(DIST/'404.html').write_text((DIST/'404/index.html').read_text())
(ROOT/'page-inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2))
from seo import finalize_seo
finalize_seo(ROOT,DIST,inventory,PRODUCTION)
print(f'Built {len(inventory)} pages.')
