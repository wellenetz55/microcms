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
    def test_general_forms_post_one_selected_category_to_one_receiver(self):
        categories = dict(general='総合相談',interview_requests='メディア',instructor_requests='講師依頼',jv='協業提携')
        for kind, category in categories.items():
            nodes=FormParser(contact_form(kind)).nodes
            fields=[a for tag,a in nodes if a.get('name')=='お問い合わせ種別']
            self.assertEqual([a['value'] for a in fields],list(categories.values()))
            self.assertTrue(all(a.get('type')=='radio' and 'required' in a for a in fields))
            self.assertEqual([a['value'] for a in fields if 'checked' in a],[category])
            self.assertEqual(next(a['action'] for tag,a in nodes if tag=='form'), FORMS['general'][1])
