import sys,tempfile,json,time,unittest,hashlib,unicodedata
from pathlib import Path
from unittest.mock import patch
from bgm.bgmkit import storage_cleanup as c
class CleanupSafety(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.d=Path(self.tmp.name)
  self.a=self.d/'source';self.b=self.d/'keep';self.other=self.d/'unlisted';self.a.write_bytes(b'original');self.b.write_bytes(b'original');self.other.write_bytes(b'preserve')
  self.row={'source':str(self.a),'keep':str(self.b),'group':'test','bytes':8}
  self.plan={'candidates':[self.row]};self.checked=self.d/'verified.json';self.output=self.d/'run.jsonl'
  self.save()
 def save(self,age=0):
  self.checked.write_text(json.dumps({'plan_sha256':'testhash','verified_at':time.time()-age,'results':[dict(self.row,status='ready',source_stamp=c.stamp(str(self.a)),keep_stamp=c.stamp(str(self.b)))]}))
 def run_exec(self,opened=()):
  with patch.object(c,'opened_paths',return_value=set(opened)),patch.object(c,'df',return_value='fixture'):
   c.execute(self.plan,'testhash',self.checked,self.output)
 def test_exact_only_and_keeper(self):
  self.run_exec();self.assertFalse(self.a.exists());self.assertEqual(self.b.read_bytes(),b'original');self.assertEqual(self.other.read_bytes(),b'preserve')
 def test_changed_source_held(self):
  self.a.write_bytes(b'changed');self.run_exec();self.assertTrue(self.a.exists())
 def test_changed_keeper_held(self):
  self.b.write_bytes(b'changed');self.run_exec();self.assertTrue(self.a.exists())
 def test_open_source_held(self):
  renamed=self.d/'か\u3099.wav';self.a.rename(renamed);self.a=renamed;self.row['source']=str(renamed);self.save()
  self.run_exec([unicodedata.normalize('NFC',str(self.a))]);self.assertTrue(self.a.exists())
 def test_stale_preflight_aborts(self):
  self.save(age=3601)
  with self.assertRaises(ValueError):self.run_exec()
  self.assertTrue(self.a.exists())
 def test_symlink_rejected(self):
  link=self.d/'link';link.symlink_to(self.b)
  with self.assertRaises(ValueError):c.stamp(str(link))
 def test_manifest_hash_mismatch(self):
  p=self.d/'plan.json';p.write_text('{}')
  with self.assertRaises(ValueError):c.load_plan(p,'wrong')
if __name__=='__main__':unittest.main()
