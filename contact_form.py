"""Purpose-specific contact forms: native POST to form.run, with a local confirmation step.
No personal data is saved in browser storage.
"""
from html import escape

FORMS = {
    'reason-ai': ('選ばれる理由AI｜無料適合診断（45分）', 'https://form.run/api/v1/r/bf36dj8z2ka0zi2z50kewndp', '選ばれる理由AIの無料適合診断（45分・Zoom面談）についての専用窓口です。', '現在の課題や、無料適合診断で相談したいことをお聞かせください。'),
    'general': ('総合お問い合わせ', 'https://form.run/api/v1/r/bf36dj8z2ka0zi2z50kewndp', 'お問い合わせの種類を1つ選び、ご相談内容をご入力ください。', '現在の課題、ご相談したいこと、ご希望などをお聞かせください。'),
}

GENERAL_TYPES = {
    'general': '総合相談',
    'interview_requests': 'メディア',
    'instructor_requests': '講師依頼',
    'jv': '協業提携',
}

def category_picker(selected):
    choices = []
    for key, text in GENERAL_TYPES.items():
        checked = ' checked' if key == selected else ''
        choices.append(f'<label class="inquiry-choice"><input type="radio" name="お問い合わせ種別" value="{text}" required{checked}><span>{text}</span></label>')
    return '<fieldset id="inquiry-category"><legend>お問い合わせの種類<span class="required">必須</span></legend><div class="inquiry-choices">' + ''.join(choices) + '</div></fieldset>'

def contact_form(kind):
    title, action, introduction, placeholder = FORMS['general' if kind in GENERAL_TYPES else kind]
    fields = [
        ('company', '会社名', 'text', True, 'organization'),
        ('name', 'お名前', 'text', True, 'name'),
        ('email', 'メールアドレス', 'email', True, 'email'),
        ('phone', '電話番号', 'tel', False, 'tel'),
    ]
    hidden_type = '' if kind in GENERAL_TYPES else f'<input type="hidden" name="お問い合わせ種別" value="{escape(title, quote=True)}">'
    parts = [f'''<div class="contact-form"><p class="form-note">{escape(introduction)}内容をご確認いただいた後、form.runを通じてベレネッツへ送信します。</p>
<form id="contact-inquiry-form" class="formrun" action="{escape(action, quote=True)}" method="post" accept-charset="UTF-8">
{hidden_type}
<div id="contact-fields">''']
    if kind == 'reason-ai':
        parts.append('''<input type="hidden" name="お問い合わせ元ページ" value="https://www.wellenetz.co.jp/branding/reason-ai/">
<div class="field"><label for="contact-subject">お問い合わせ件名</label><textarea id="contact-subject" name="件名" rows="2" readonly aria-describedby="subject-hint">【選ばれる理由AI】無料適合診断（45分・Zoom面談）のご相談</textarea><p class="field-hint" id="subject-hint">この件名でお送りします。サービス名をあらためて入力する必要はありません。</p></div>''')
    else:
        parts.append(category_picker(kind))
    for key, label, kind, required, autocomplete in fields:
        attrs = ' required' if required else ''
        badge = '<span class="required">必須</span>' if required else '<span class="field-optional">任意</span>'
        note = '<p class="field-hint" id="company-hint">個人の方は「個人」とご入力ください。</p>' if key == 'company' else ''
        described = ' aria-describedby="company-hint"' if key == 'company' else ''
        parts.append(f'<div class="field"><label for="contact-{key}">{label}{badge}</label><input id="contact-{key}" name="{label}" type="{kind}" autocomplete="{autocomplete}" maxlength="150"{attrs}{described}>{note}</div>')
    parts.append(f'''<div class="field"><label for="contact-message">ご相談内容<span class="required">必須</span></label><textarea id="contact-message" name="お問い合わせ内容" required maxlength="5000" placeholder="{escape(placeholder, quote=True)}"></textarea></div>
<div class="contact-consent"><p><a href="/handle_personal_data/" target="_blank" rel="noopener">個人情報の取扱いについて（別タブで開きます）</a></p><label><input id="contact-consent" type="checkbox" name="個人情報の取扱いへの同意" value="同意する" required><span>個人情報の取扱いに関する内容に同意する<span class="required">必須</span></span></label></div>
</div>
<div class="_formrun_gotcha" aria-hidden="true"><label for="_formrun_gotcha">If you are a human, ignore this field</label><input type="text" name="_formrun_gotcha" id="_formrun_gotcha" tabindex="-1" autocomplete="off"></div>
<section id="contact-review" class="form-status" hidden aria-labelledby="contact-review-title"><h2 id="contact-review-title" tabindex="-1">送信内容の確認</h2><p>まだ送信されていません。内容をご確認のうえ「この内容で送信する」を押してください。</p><dl id="contact-review-values" class="contact-review-values"></dl></section>
<noscript><p class="form-note">JavaScriptが無効のため確認画面は表示されません。入力内容をご確認のうえ、送信ボタンを押してください。</p></noscript>
<div class="form-actions"><button class="button outline" type="button" id="contact-edit" hidden>入力内容を修正する</button><button class="button" type="submit" id="contact-submit">この内容で送信する</button></div>
<p id="contact-submit-status" role="status" aria-live="polite"></p>
<p class="field-hint">送信後は完了画面へ移動します。</p>
</form></div>''')
    return ''.join(parts)
