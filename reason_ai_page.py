"""Register the dedicated Reason AI landing page; layout lives in src/reason-ai-lp.html."""

def build_reason_ai_page(page, section, sh, eyebrow, button, a):
    page('/branding/reason-ai/', '選ばれる理由AI', '', en='REASON AI',
         group='services', hero=False, cta=False)
