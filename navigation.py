"""Shared desktop disclosures and mobile navigation hierarchy."""
from html import escape as E
NAV = [
 ('/services/', '事業内容', 'OUR SERVICES', [
  ('/branding/', 'ブランディング', [('/branding/forbidden/','禁断のブランディング'),('/branding/jitan/','時短ブランディング'),('/branding/reason-ai/','選ばれる理由AI')]),
  ('/marketing/', 'マーケティング', [('/marketing/support/','マーケティング支援'),('/marketing/small-short-term-insurance/','事業開発｜少額短期保険事業参入支援'),('/marketing/kinqr/','デジタルサービス｜緊QR')]),
  ('/creative/', 'クリエイティブ制作', []),
 ], [('/wellenetz-menu/','課題からサービスを探す'),('/branding/approrach/','プロジェクトの進め方')]),
 ('/overview/what_we_do/', '私たちの強み', 'WHY WELLENETZ', [
  ('/overview/what_we_do/','私たちの強み',[]),
  ('/branding/#trust','独自メソッド T.R.U.S.T.',[]),
  ('/overview/proposal/','提案の仕方',[]),
  ('/overview/unique_branding/','解決できる経営課題',[]),
 ], []),
 ('/case_study/', '事例紹介', 'CASE STUDIES', [
  ('/case_study/','すべての事例',[]),
  ('/case_study/','業種から探す',[('/case_category/manufacturing/','製造'),('/case_category/food_manufacturing/','食品製造'),('/case_category/it_btoc/','IT企業（BtoC）'),('/case_category/financial_services/','金融サービス'),('/case_category/medical_device/','医療機器製造'),('/case_study/','すべての業種を見る')]),
 ], []),
 ('/overview/', '会社情報', 'COMPANY', [
  ('/overview/','会社概要',[]),('/overview/message/','代表メッセージ',[]),('/overview/history/','沿革',[]),('/overview/access/','拠点・アクセス',[]),
 ], []),
 ('/news/', 'ニュース', 'NEWS & INSIGHTS', [
  ('/news/','ニュース・お知らせ',[]),('/column/','コラム',[]),('/resources/','無料コンテンツ',[]),('/brandingseminar_free/','無料ブランディングセミナー',[]),
 ], []),
]

def link(url, label, path, cls=''):
    return f'<a href="{E(url)}" class="{cls}"'+(' aria-current="page"' if url == path else '')+'>'+E(label)+'</a>'

def groups_html(groups, path):
    return ''.join('<div class="nav-group">'+link(url,title,path,'nav-group-title')+('<ul class="nav-third">'+''.join('<li>'+link(u,t,path)+'</li>' for u,t in children)+'</ul>' if children else '')+'</div>' for url,title,children in groups)

def desktop_navigation(path):
    out='<ul class="nav-root">'
    for i,(url,title,en,groups,extras) in enumerate(NAV):
        out+=f'<li class="nav-item" data-nav-item><div class="nav-top">'+link(url,title,path,'nav-top-link')+f'<button class="nav-disclosure" type="button" aria-label="{title}の下層メニュー" aria-expanded="false" aria-controls="nav-panel-{i}"><span aria-hidden="true">⌄</span></button></div>'
        out+=f'<div class="nav-panel" id="nav-panel-{i}" hidden><div class="nav-panel-inner"><div class="nav-panel-intro"><span>{en}</span><p>{title}</p>'+link(url,title+'一覧へ',path,'nav-overview')+'</div><div class="nav-panel-content"><div class="nav-groups">'+groups_html(groups,path)+'</div>'
        if extras:out+='<div class="nav-extras">'+''.join(link(u,t,path) for u,t in extras)+'</div>'
        out+='</div></div></div></li>'
    return out+'</ul>'

def mobile_navigation(path):
    out=''
    for url,title,en,groups,extras in NAV:
        out+='<details class="mobile-branch"><summary>'+title+'</summary><div class="mobile-branch-content">'+link(url,title+'一覧へ',path,'mobile-overview')+groups_html(groups,path)
        out+=''.join(link(u,t,path,'mobile-extra') for u,t in extras)+'</div></details>'
    return out+link('/inquiry/','無料相談・お問い合わせ',path)
