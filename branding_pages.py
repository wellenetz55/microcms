"""Branding offerings based on the user-provided customer briefing PDF."""
PROGRAMS = [
    ('/branding/forbidden/', 'DISCOVER YOUR VALUE', '禁断のブランディング®', '社内では当たり前になっている強みから、顧客を惹き寄せる「隠れた価値」を発見します。'),
    ('/branding/jitan/', 'CHANGE PERCEPTION', '時短ブランディング®', '企業・商品・サービス自体は変えず、顧客の思い込みや誤認識を変えて、本来の価値を届けます。'),
    ('/branding/reason-ai/', 'YOUR DEDICATED AI', '選ばれる理由AI', '25年・750社のメソッドを、貴社専用のAIに。対話を通じて、自社の「選ばれる理由」を言語化します。'),
]


def program_cards(items=PROGRAMS):
    focuses = ['隠れた価値を、見つける。', '顧客の認識を、変える。', '自社の言葉で、明らかにする。']
    labels = ['価値の発見', '認識の変化', 'AIとの対話']
    result = '<div class="branding-programs">'
    for u, en, title, desc in items:
        i = next(n for n, p in enumerate(PROGRAMS) if p[0] == u)
        heading = '<img src="/assets/reason-ai-logo.png" alt="選ばれる理由AI" width="1261" height="291" loading="lazy">' if i == 2 else title
        result += f'<a href="{u}" class="branding-program branding-program-{i+1}"><div class="branding-program-top"><span class="branding-number">0{i+1}</span><span class="branding-tag">{labels[i]}</span></div><div class="branding-program-name"><span class="branding-en">{en}</span><h3>{heading}</h3></div><p class="branding-focus">{focuses[i]}</p><p class="branding-description">{desc}</p><span class="branding-program-link">サービスを詳しく見る <span aria-hidden="true">↗</span></span></a>'
    return result + '</div>'


def build_branding_pages(page, section, sh, eyebrow, button, a, branch, trusthtml):
    introduction = section('<div class="split"><div>'+eyebrow('OUR BELIEF')+'<h2>「伝わる」と<br>「惹き寄せる」を創る。</h2></div><div><p>いい商品なのに伝わらない。競合との違いを理解してもらえない。ベレネッツは、その課題を顧客の認識から捉え直します。</p><p>企業・製品・サービスに眠る価値を見つけ、顧客が理解し、共感する「ブランドの脚本」をつくる。ロゴやイメージの変更にとどまらず、自ら選びたくなる理由を届けることが、私たちのブランディングです。</p></div></div>')
    offerings = section(sh('THREE BRANDING SERVICES','課題に合わせた、3つの支援。','<p>価値を発見する。認識を変える。自社で言語化する。<br>貴社の課題と体制に合わせたアプローチを。</p>')+program_cards(),'branding-offerings',id='programs')
    paths = section(sh('BRANDING SUPPORT','ベレネッツの支援を、<br>貴社の力に。')+'<div class="branding-paths"><article><span class="branding-route">A / WITH WELLENETZ</span><h3>専門家と、一緒につくる。</h3><p>現状分析からコンセプト設計、戦略策定、浸透策・制作、運用・PDCAまで。一つのプロジェクトフローに沿って、ベレネッツが貴社とともに進めます。</p>'+a('/branding/approrach/','専門家とのプロジェクトフローを見る','text-link')+'</article><article><span class="branding-route">B / WITH YOUR AI</span><h3>専用AIで、自社で言語化する。</h3><p>「選ばれる理由AI」との対話で、貴社自身が価値を言葉にしていきます。節目ごとにベレネッツがシステム上の履歴を直接確認し、進捗をサポートします。</p>'+a('/branding/reason-ai/','選ばれる理由AIを見る','text-link')+'</article></div><p class="branding-common">共通する土台は、25年・750社の支援から体系化したメソッド。</p>','soft')
    method = section(sh('OUR ORIGINAL METHOD','T.R.U.S.T.という、5つの視点。','<p>貴社に適した要素を見極め、組み合わせる。<br>実践から体系化した独自のブランド評価指標です。</p>')+trusthtml,id='trust')
    page('/branding/','隠れた価値を、<br>選ばれる理由へ。',branch+introduction+offerings+paths+method,en='BRANDING',lead='価値を見つけ、認識を変え、自社の言葉にする。ベレネッツの3つのブランディング支援。',group='services')

    from reason_ai_page import build_reason_ai_page
    build_reason_ai_page(page, section, sh, eyebrow, button, a)
