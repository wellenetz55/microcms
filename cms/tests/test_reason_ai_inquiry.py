"""Protect the diagnosis inquiry context without changing other contact routes."""
import sys
import unittest
from pathlib import Path
from html.parser import HTMLParser
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from contact_form import contact_form, FORMS

class FormParser(HTMLParser):
    def __init__(self, html):
        super().__init__(); self.nodes=[]; self.feed(html)
    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

class ReasonAIInquiryTests(unittest.TestCase):
    def test_diagnosis_context_is_submitted_without_javascript(self):
        html=contact_form('reason-ai'); nodes=FormParser(html).nodes
        inputs={a['name']:a for t,a in nodes if t in ('input','textarea') and 'name' in a}
        self.assertEqual(inputs['お問い合わせ種別']['value'],'選ばれる理由AI｜無料適合診断（45分）')
        self.assertEqual(inputs['お問い合わせ元ページ']['value'],'https://www.wellenetz.co.jp/branding/reason-ai/')
        self.assertIn('readonly',inputs['件名']); self.assertNotIn('disabled',inputs['件名'])
        self.assertIn('【選ばれる理由AI】無料適合診断（45分・Zoom面談）のご相談',html)
        self.assertEqual(next(a['action'] for t,a in nodes if t=='form'),FORMS['general'][1])
    def test_existing_forms_keep_their_own_identity_and_endpoint(self):
        for kind in ('general','interview_requests','instructor_requests','jv'):
            html=contact_form(kind)
            self.assertNotIn('contact-subject',html)
            self.assertNotIn('お問い合わせ元ページ',html)
            self.assertIn('value="'+FORMS[kind][0]+'"',html)
            self.assertIn('action="'+FORMS[kind][1]+'"',html)
