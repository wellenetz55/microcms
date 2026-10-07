"""Purpose-specific contact forms: native POST to form.run, with a local confirmation step.
No personal data is saved in browser storage.
"""
from html import escape

FORMS = {
    'general': ('総合お問い合わせ', 'https://form.run/api/v1/r/bf36dj8z2ka0zi2z50kewndp', 'サービスに関するご相談やご質問をお聞かせください。', '現在の課題、ご相談したいこと、ご希望などをお聞かせください。'),
    'interview_requests': ('メディアのお問い合わせ', 'https://form.run/api/v1/r/z6gfj31qd67mbw7v6ft0800f', '取材・掲載など、メディアに関するお問い合わせをお聞かせください。', '媒体名、取材・掲載の概要、ご希望の日程などをお聞かせください。'),
    'instructor_requests': ('講師ご依頼', 'https://form.run/api/v1/r/fnc0lumimw3kjrehhrx7f6gl', '講演・研修などの講師ご依頼についてお聞かせください。', '講演・研修のテーマ、対象者、ご希望の日程・会場・開催形式などをお聞かせください。'),
    'jv': ('協業・提携のご相談', 'https://form.run/api/v1/r/aammn3htrqo22ftn86a834hl', '協業・提携のご提案やご相談をお聞かせください。', '貴社の事業内容、ご提案・ご相談の概要、期待する連携などをお聞かせください。'),
}

def contact_form(kind):
    title, action, introduction, placeholder = FORMS[kind]
    fields = [
        ('company', '会社名', 'text', True, 'organization'),
        ('name', 'お名前', 'text', True, 'name'),
        ('email', 'メールアドレス', 'email', True, 'email'),
        ('phone', '電話番号', 'tel', False, 'tel'),
    ]
    parts = [f'''<div class="contact-form"><p class="form-note">{escape(introduction)}内容をご確認いただいた後、form.runを通じてベレネッツへ送信します。</p>
<form id="contact-inquiry-form" class="formrun" action="{escape(action, quote=True)}" method="post" accept-charset="UTF-8">
<input type="hidden" name="お問い合わせ種別" value="{escape(title, quote=True)}">
<div id="contact-fields">''']
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
