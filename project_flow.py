"""One expert-led project flow, transcribed from the supplied project diagram."""
STEPS = [
    ('Step 0–1', '1ヶ月目・中旬まで', 'Kickoff・現状分析', [
        ('Kickoff', ['プロジェクト・前提条件の確認', '現状の共有（保有データ等）']),
        ('現状分析', ['マーケティングフレームを活用し、事業内容・採用状況・業界環境・競合を分析']),
        ('将来ビジョンの深掘り', ['共通認識の形成']),
    ]),
    ('Step 2', '2ヶ月目・中旬まで', 'コンセプト設計', [
        ('「だれに、なにを」を明確に', ['ベレネッツ独自のブランディングセッション']),
        ('ターゲット整理・コンセプト設計', ['自社が本当に取るべき人を言語化', 'その人が自社を選ぶ理由を構造化']),
        ('キーパーソンヒアリング', ['経営層・現場管理職などへのヒアリング']),
    ]),
    ('Step 3', '2ヶ月目・末まで', '戦略策定', [
        ('「どのように」を設計', ['ベレネッツ独自のブランディングセッション']),
        ('コミュニケーション・体験設計', ['ブランドポジションの定義（機能軸・情緒軸・文脈軸）', 'ブランドの約束の策定', '変革ストーリーの言語化']),
        ('実行戦略の策定', ['ブランディングの実行に向けた戦略を整理']),
    ]),
    ('Step 4', '4ヶ月目・末まで', '浸透策（戦術）／<br>クリエイティブ制作', [
        ('戦術レベルの浸透策を策定', ['サイトリニューアルのための指南書']),
        ('クリエイティブ制作', ['必要に応じて制作を実施（オプション）']),
        ('実行を支える設計', ['KPI設計', 'インナーブランディング企画']),
    ]),
    ('Step 5', '5ヶ月目〜', '運用開始・PDCA会議', [
        ('施策・採用活動の開始', ['策定した戦略・浸透策を実行へ']),
        ('PDCA会議の定例化', ['効果検証', '改善策の検討・実施']),
        ('インナーブランディング', ['社内への浸透プロジェクトを始動']),
    ]),
]


def build_project_flow(page, section, sh, eyebrow, button):
    overview = '<ol class="project-flow">'
    for i,(step,month,title,groups) in enumerate(STEPS):
        overview += f'<li class="project-stage"><div class="project-stage-label">{step}</div><h3><span>{title}</span></h3><p class="project-month">{month}</p><div class="project-tasks">'
        for heading,items in groups:
            overview += '<div><h4>'+heading+'</h4><ul>'+''.join('<li>'+text+'</li>' for text in items)+'</ul></div>'
        overview += '</div></li>'
    overview += '</ol>'
    introduction = section('<div class="split"><div>'+eyebrow('FROM DISCOVERY TO ACTION')+'<h2>価値を見つけ言葉化し、<br>実行と改善までつなぐ。</h2></div><div><p>現状分析からコンセプト設計、戦略策定、浸透策・制作、運用へ。ベレネッツは、一貫したプロジェクトフローでブランディングを進めます。</p><p>独自のブランディングセッションで価値を言語化し、定例会議を通じて貴社と認識を合わせながら、各種設計と実施を支援します。</p></div></div>')
    flow = section(sh('PROJECT FLOW','プロジェクトの進め方。','<p>開始月を「1ヶ月目」とした進行イメージです。<br>実際の日程・実施範囲はプロジェクトに応じて調整します。</p>')+overview,'project-flow-section',id='project-flow')
    points = section(sh('OUR APPROACH','進行を支える、3つのポイント。')+'<div class="project-points"><article>'+eyebrow('01 / RESEARCH')+'<h3>調査を、価値の発見へ。</h3><p>独自のT.R.U.S.T.サーチを活用。調査に時間をかけすぎず、企業の価値と課題を捉えます。</p></article><article>'+eyebrow('02 / SESSION')+'<h3>短期間で、言葉にする。</h3><p>ベレネッツ独自のブランディングセッションで、ターゲット・コンセプト・戦略の言語化を先導します。</p></article><article>'+eyebrow('03 / IMPLEMENTATION')+'<h3>定例会議で、実行を支える。</h3><p>定例会議を設定し、貴社とともに各種設計・施策を実施。運用後も効果を検証し、改善につなげます。</p></article></div>')
    page('/branding/approrach/','発見から、実行・改善まで。<br>一つにつながるブランディング。',introduction+flow+points,en='PROJECT FLOW',lead='Kickoff・現状分析から、コンセプト設計、戦略策定、浸透策・制作、運用・PDCAへ。',group='services')
