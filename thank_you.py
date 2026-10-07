"""Shared destination after form.run accepts an inquiry."""
def thank_you_content():
    return '''<section class="thank-you"><div class="wrap">
<nav class="breadcrumbs" aria-label="パンくず"><a href="/">HOME</a><span>/</span><a href="/inquiry/">お問い合わせ</a><span>/</span><span>送信完了</span></nav>
<div class="thank-you-layout">
<div class="thank-you-message">
<div class="thank-you-status"><span class="thank-you-check" aria-hidden="true"><svg width="30" height="30" viewBox="0 0 32 32" fill="none"><path d="m8 16 5 5 11-11" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg></span><span>MESSAGE RECEIVED</span></div>
<p class="eyebrow">THANK YOU FOR CONTACTING US</p>
<h1>お問い合わせ、<br>ありがとうございます。</h1>
<p class="thank-you-lead">お問い合わせを受け付けました。<br>内容を確認のうえ、担当者よりご連絡いたします。</p>
<p class="thank-you-note">ご相談・ご依頼の内容によっては、回答までにお時間をいただく場合がございます。あらかじめご了承ください。</p>
<a class="button" href="/">トップページへ戻る <span aria-hidden="true">↗</span></a>
</div>
<aside class="thank-you-next" aria-labelledby="next-title">
<div class="eyebrow">WHAT’S NEXT</div><h2 id="next-title">このあとのご案内</h2>
<ol class="thank-you-steps"><li><span class="thank-you-step-number">01</span><div><h3>内容を確認します</h3><p>お送りいただいたご相談・ご依頼を、担当者が確認します。</p></div></li><li><span class="thank-you-step-number">02</span><div><h3>担当者からご連絡します</h3><p>ご入力のメールアドレス、またはお電話へご連絡いたします。</p></div></li></ol>
<div class="thank-you-help"><h3>連絡が届かない場合</h3><p>迷惑メールフォルダーや受信設定をご確認ください。お急ぎの場合は、お電話でもお問い合わせいただけます。</p><div class="thank-you-phone"><span>東京</span><a href="tel:0362627485">03-6262-7485</a><span>名古屋</span><a href="tel:0526849800">052-684-9800</a></div></div>
</aside></div>
<div class="thank-you-explore"><div><span class="eyebrow">EXPLORE WELLENETZ</span><h2>ベレネッツを、もう少し知る。</h2></div><div class="thank-you-links"><a href="/case_study/"><span><small>CASE STUDIES</small>支援事例を見る</span><span aria-hidden="true">↗</span></a><a href="/column/"><span><small>INSIGHTS</small>コラムを読む</span><span aria-hidden="true">↗</span></a></div></div>
</div></section>'''
