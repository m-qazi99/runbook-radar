import unittest,sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from engine import run
from common import read_csv
class EngineTests(unittest.TestCase):
 def sample(self):return json.loads((R/'examples/sample.json').read_text())
 def test_empty_csv_rejected(self):
  with self.assertRaises(ValueError):read_csv('')
 def test_duplicate_headers_rejected(self):
  with self.assertRaises(ValueError):read_csv('a,a\n1,2')
 def test_ragged_csv_rejected(self):
  with self.assertRaises(ValueError):read_csv('a,b\n1')
 def test_quoted_csv_and_bom(self):
  h,r=read_csv('\ufeffid,note\n1,"hello, world"');self.assertEqual(r[0]['note'],'hello, world')
 def test_retrieves_relevant_evidence(self):
  r=run(self.sample());self.assertIn('Storage access denied',r['table']['rows'][0][0]);self.assertIn('role assignments',r['table']['rows'][0][2])
 def test_no_match_abstains(self):
  p=self.sample();p['query']='zzzxxyy';r=run(p);self.assertEqual(r['metrics'][2]['value'],0)
 def test_stop_words_only_rejected(self):
  p=self.sample();p['query']='the and or'
  with self.assertRaises(ValueError):run(p)
 def test_empty_document_rejected(self):
  with self.assertRaises(ValueError):run({'documents':'# Heading','query':'test'})
 def test_untitled_document_searchable(self):
  r=run({'documents':'Restart the database after backup.','query':'database'});self.assertIn('Untitled runbook',r['table']['rows'][0][0])
 def test_source_is_verbatim(self):
  r=run({'documents':'# Test\nAlpha beta gamma.','query':'alpha'});self.assertEqual(r['table']['rows'][0][2],'Alpha beta gamma.')

if __name__=='__main__':unittest.main()
