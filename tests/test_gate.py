import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gate import Gate,Denied,FORBIDDEN
class GateTest(unittest.TestCase):
 def setUp(self):
  self.dir=tempfile.TemporaryDirectory();self.addCleanup(self.dir.cleanup);self.db=Path(self.dir.name)/'state.db';self.g=Gate(self.db)
 def test_allowed_draft_survives_restart(self):
  rid,s=self.g.request('DRAFT',{'text':'draft, not sent'},'owner');self.assertEqual(s,'READY_LOCAL')
  g2=Gate(self.db);ret=g2.execute_local(rid);self.assertTrue(ret['simulation']);self.assertFalse(ret['external_effects'])
  self.assertIn('SIMULATED_ONLY',[x['event'] for x in g2.history()])
 def test_human_review(self):
  rid,s=self.g.request('PUBLISH_PREVIEW',{'content':'hello'},'owner');self.assertEqual(s,'REVIEW_REQUIRED')
  with self.assertRaises(Denied):self.g.execute_local(rid)
  with self.assertRaises(Denied):self.g.approve(rid,'','I_EXPLICITLY_APPROVE_THIS_SIMULATION')
  with self.assertRaises(Denied):self.g.approve(rid,'reviewer','yes')
  self.g.approve(rid,'reviewer','I_EXPLICITLY_APPROVE_THIS_SIMULATION')
  self.assertFalse(self.g.execute_local(rid)['external_effects'])
 def test_all_prohibited_actions_have_no_codepath(self):
  for kind in FORBIDDEN:
   rid,status=self.g.request(kind,{'amount':100},'owner');self.assertEqual(status,'BLOCKED')
   with self.assertRaises(Denied):self.g.execute_local(rid)
   with self.assertRaises(Denied):self.g.approve(rid,'reviewer','I_EXPLICITLY_APPROVE_THIS_SIMULATION')
 def test_unknown_action_fails_closed(self):
  with self.assertRaises(ValueError):self.g.request('SNEAKY_SYSTEM_WRITE',{},'owner')
if __name__=='__main__':unittest.main()
