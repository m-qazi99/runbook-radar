import unittest, sys, json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(R/'src'))
from engine import run

class StudioTests(unittest.TestCase):
 def sample(self):return json.loads((R/'examples/studio.json').read_text())
 def execute(self,**changes):
  p=self.sample();p.update(changes);return run(p)['lab']
 def test_json_serializable(self):json.dumps(run(self.sample()),allow_nan=False)
 def test_storage_question_returns_source(self):
  l=self.execute();self.assertEqual(l['matches'][0]['title'],'Storage access denied')
 def test_no_match_abstains(self):self.assertEqual(self.execute(query='xylophone quantum zephyr')['matches'],[])
 def test_terms_sum_to_score(self):
  for r in self.execute()['matches']:self.assertAlmostEqual(sum(t['score'] for t in r['terms']),r['score'],delta=.001)
 def test_tfidf_scores_are_cosines(self):
  for r in self.execute(algorithm='tfidf')['matches']:self.assertTrue(0<=r['score']<=1.00001)
 def test_overlap_changes_chunk_count(self):
  a=self.execute(chunk_size=30,overlap=0);b=self.execute(chunk_size=30,overlap=20);self.assertGreater(len(b['chunks']),len(a['chunks']))
 def test_windows_have_valid_end(self):
  for c in self.execute()['chunks']:self.assertLessEqual(c['start'],c['end'])
 def test_evaluation_mrr_matches_ranks(self):
  l=self.execute();expected=sum(1/x['ranks']['bm25'] if x['ranks']['bm25'] else 0 for x in l['evaluation'])/len(l['evaluation']);self.assertAlmostEqual(l['scores']['bm25']['mrr'],expected,places=3)
 def test_unknown_expected_title_rejected(self):
  with self.assertRaises(ValueError):self.execute(evaluation='[{"query":"storage","expected":"imaginary"}]')
 def test_overlap_must_be_less_than_size(self):
  with self.assertRaises(ValueError):self.execute(chunk_size=30,overlap=30)
 def test_empty_question_rejected(self):
  with self.assertRaises(ValueError):self.execute(query='the and a')
