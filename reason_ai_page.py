"""Register the dedicated Reason AI landing page; layout lives in src/reason-ai-lp.html."""

def build_reason_ai_page(page, section, sh, eyebrow, button, a):
    page('/branding/reason-ai/', '選ばれる理由AI', '', en='REASON AI',
         group='services', hero=False, cta=False)


def render_consultation_page(source):
    import re

    page = (source / "reason-ai-lp.html").read_text()
    style, header = (source / "reason-ai-consultation-hero.html").read_text().split("<!-- hero -->")
    page, count = re.subn(r'<header class="hero">.*?</header>', lambda _: header.strip(), page, flags=re.S)
    if count != 1:
        raise ValueError("Expected one Reason AI service page hero")
    return page.replace("</head>", style + "</head>", 1)
