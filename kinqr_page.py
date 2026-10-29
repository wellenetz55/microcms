"""Visual explanation of KinQR, based on the supplied ten-page proposal."""
from html import escape


def kinqr_content(hero, section, sh, eyebrow, button, steps, tiles, related):
    def picture(name, alt, width, height, caption='', eager=False):
        src = '/assets/kinqr-' + name
        return (f'<figure class="kq-figure"><a href="{src}" target="_blank" rel="noopener" '
                f'aria-label="{escape(alt)}（画像を拡大・別タブ）">'
                f'<img src="{src}" alt="{escape(alt)}" width="{width}" height="{height}" '
                + ('fetchpriority="high"' if eager else 'loading="lazy"')
                + ' decoding="async"></a>'
                + (f'<figcaption>{caption} <span>画像を拡大 ↗</span></figcaption>' if caption else '')
                + '</figure>')

    visual = '''<div class="kq-switch-demo" data-qr-demo>
      <div class="kq-demo-top"><span>同じQRの、2つの役割</span><small>ボタンで切り替え</small></div>
      <div class="mk-qr-switch" role="group" aria-label="情報の切り替えイメージ">
        <button type="button" data-qr-mode="normal" aria-pressed="true">平時の案内を見る</button>
        <button type="button" data-qr-mode="emergency" aria-pressed="false">緊急時の案内を見る</button>
      </div>
      <div class="kq-map-state" data-qr-panel="normal">
        <img src="/assets/kinqr-normal-map.png" alt="街の各所にあるQRコードが、普段は施設案内などの情報の入り口になるイメージ" width="1200" height="675" fetchpriority="high">
        <div><strong>日常の「知りたい」に。</strong><p>施設案内・アクセス・多言語情報などを届けます。</p></div>
      </div>
      <div class="kq-map-state" data-qr-panel="emergency" hidden>
        <img src="/assets/kinqr-emergency-map.png" alt="設置した同じQRコードの案内先を、緊急時の避難情報へ切り替えるイメージ" width="1200" height="675">
        <div><strong>緊急時の「どこへ」に。</strong><p>避難情報や避難先への案内に切り替わります。</p></div>
      </div>
      <p class="mk-qr-status" aria-live="polite" data-qr-status>平時の情報提供を表示しています。</p>
    </div>'''
    content = hero('/marketing/kinqr/', '03', 'DIGITAL SERVICE', '緊急時情報管理サービス「緊QR」',
        'いつものQRが、<br><em>避難情報の入り口に。</em>',
        '平時は施設や街の情報を。緊急時は避難情報を。<br>貼り替えずに案内先を変えられる、可変QRコードの仕組みです。', visual, 'mk-kinqr')

    content += section('''<div class="mk-section-intro"><div>''' + eyebrow('ONE QR, TWO ROLES') + '''
      <h2>貼り替えるのはQRではなく、<br>その先にある情報。</h2></div>
      <p>緊QRは、可変QRコード管理基盤「DynQ」を活用した緊急時情報管理サービスです。あらかじめ設置した緊QRの案内先を切り替えることで、日常の情報提供と、緊急時の避難案内をひとつの接点でつなぎます。</p></div>
      <div class="kq-role-flow"><article><span>01 / 平時</span><h3>施設や街を案内</h3><p>施設案内・アクセス・多言語情報など。普段から使う情報の入り口に。</p></article>
      <div class="kq-same-code"><span aria-hidden="true">⇄</span><strong>QRはそのまま</strong><small>案内先を切り替え</small></div>
      <article><span>02 / 緊急時</span><h3>避難情報へ案内</h3><p>災害・避難情報、緊急のお知らせなど。その時に必要な情報へ。</p></article></div>
      <p class="kq-note">※図の色の変化は切り替えのイメージです。通常の印刷QR自体が変色するものではありません。</p>''', id='overview')

    content += section('''<div class="mk-section-intro"><div>''' + eyebrow('FOR VISITORS') + '''
      <h2>読む。その先に、<br>避難先までの道案内。</h2></div><p>利用者は、身近に設置された緊QRをスマートフォンで読み取ります。緊急時には避難情報へアクセスし、避難先までの経路を確認できます。</p></div>
      <div class="kq-navigation-demo"><article><div class="kq-step-title"><b>1</b><h3>設置された緊QRを読む</h3></div>'''
      + picture('scan.jpg', 'スマートフォンで緊QRを読み取るイメージ', 560, 880)
      + '''</article><div class="kq-next" aria-hidden="true">→</div><article><div class="kq-step-title"><b>2</b><h3>避難先への経路を確認</h3></div>'''
      + picture('navigation.jpg', 'スマートフォンに表示される地図と経路案内の例', 430, 870)
      + '''</article></div><p class="kq-note">提案書掲載の利用イメージです。画面内の地図・経路は表示例です。専用アプリのインストールは不要です。</p>''', 'kq-pale', id='how-to-use')

    content += section('''<div class="kq-control-layout"><div>''' + eyebrow('FOR OPERATORS') + '''
      <h2>情報の切り替えは、<br>管理画面から。</h2><p>通常時・緊急時に届ける情報をあらかじめ設定。Webベースの管理画面で、QRコードや案内先を管理します。</p>
      <div class="kq-control-note"><strong>手動で、ワンクリック切り替え</strong><p>通常モードと緊急モードを、管理者の操作で切り替えられます。</p></div>
      <div class="kq-control-note"><span class="kq-chip">導入条件に応じて対応</span><strong>地震警報に連動した自動切り替え</strong><p>地震警報を受けて、あらかじめ設定した緊急時の情報へ自動的に切り替える仕組みです。</p><small>※自動切り替えは、案件の規模・条件に応じて配置します。導入時に適用条件を確認します。</small></div></div>'''
      + picture('management.jpg', 'DynQのWeb管理画面。QRコード管理とダッシュボードの表示例', 1850, 900, 'QRコード管理・ダッシュボードの画面例。')
      + '</div>', id='management')

    content += section('''<div class="mk-section-intro"><div>''' + eyebrow('VISIBLE IN EVERYDAY PLACES') + '''
      <h2>見つけやすい場所に。<br>変化も、わかりやすく。</h2></div><div><span class="kq-chip">設置オプション例</span><p>壁面から突き出すサイドサインなら、通路からも見つけやすい接点に。提案書では、平時と緊急時で表示が変わる設置イメージを紹介しています。</p></div></div>
      <div class="kq-sign-grid"><article><div class="kq-sign-label">平時 <small>いつもの情報の入り口</small></div>'''
      + picture('sign-normal.jpg', '壁面に設置された白いサイドサインの平時イメージ', 724, 630, '平時の設置イメージ。')
      + '''</article><article><div class="kq-sign-label emergency">緊急時 <small>表示の変化で知らせる</small></div>'''
      + picture('sign-emergency.jpg', '緊急時に赤く表示されたサイドサインのイメージ', 726, 630, '緊急時の設置イメージ。')
      + '''</article></div><p class="kq-note">※サイドサインは設置オプションです。設置方法・表示仕様は導入条件に応じてご相談ください。</p>''', 'kq-pale', id='signage')

    content += section('''<div class="kq-detail-grid"><div>''' + eyebrow('DESIGNED TO BE READ') + '''
      <h2>QRの読み取りやすさにも、<br>工夫があります。</h2><p>DynQは、少ないドット数で生成する「省ドットQRコード」を採用。複雑になりがちなQRコードの密度を抑え、読み取りミスの軽減を図ります。</p>'''
      + picture('qr-comparison.jpg', '一般的な可変QRコードとDynQの省ドットQRコードの比較。DynQはURLの長さが変わっても同じ密度', 1310, 710, '提案書掲載のQRコード比較。')
      + '''</div><div class="kq-options">''' + eyebrow('OPTIONS') + '''<h2>用途に合わせて、<br>運用を広げる。</h2>
      <article><h3>イベント時の情報発信にも</h3><p>オプションでイベントQRとして活用可能。日常と緊急時に加え、イベント時の案内にも使えます。</p></article>
      <article><h3>利用者とスタッフで、案内先を分ける</h3><p>DualQR機能なら、利用者には一般情報、スタッフには管理履歴など、読み取る人に応じて情報を分けられます。</p></article>
      <article><h3>解約後は、固定QRとして残す選択も</h3><p>所定の設定により、固定QRとして機能し続ける運用が可能です。継続条件や設定内容はご相談ください。</p></article></div></div>''')

    content += section(sh('WHERE TO USE', 'いつもの場所を、情報の接点に。') + tiles([
        ('自治体・公共施設', '庁舎、文化施設、スポーツ施設、街頭案内など。日常の施設案内と緊急時の情報提供をひとつに。'),
        ('オフィス・複合施設', 'エントランスや共用部など。館内案内を届ける接点から、緊急時の情報へつなぎます。'),
        ('観光・レジャー施設', '観光案内や多言語情報を届ける場所に。土地に不慣れな来訪者にも、情報の入り口を用意します。')]), 'soft')
    content += section(sh('START SMALL', '小さく試し、確かめて、広げる。', '<p>設置して終わりではなく、<br>実際の環境で確認しながら導入します。</p>') + steps([
        ('ご相談・ヒアリング', '導入目的、対象施設、設置場所、現在の情報提供方法を確認します。', ''),
        ('導入計画・設置設計', '設置場所、平時・緊急時の案内先、情報切り替えの方法を設計します。', ''),
        ('実証・導入テスト', '一部の施設やエリアで、読み取り・情報切り替え・経路案内を確認します。', ''),
        ('本導入・運用', '検証結果を踏まえて展開。定期確認や訓練を通じて、運用を続けます。', '')]))
    content += section('<div class="kq-consult"><div>' + eyebrow('SERVICE & SUPPORT') + '''
      <h2>「どこに設置できるか」から、<br>一緒に考えます。</h2><p>提案・見積、現場調査、設置計画、QR媒体の制作・設置、運用支援まで。ベレネッツが窓口となり、技術開発側と連携して導入を支援します。</p></div>'''
      + button('/inquiry/general/', '緊QRの導入について相談する', 'light') + '</div>', 'dark')
    return content + related('/marketing/kinqr/')
