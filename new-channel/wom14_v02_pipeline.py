"""Resume serial, low-memory v02 normal masters and exact-pixel proofs."""
import subprocess,sys
from wom14_v02 import ROOT,save
p=sys.executable
for lang,scale in [('en',1),('ja',1),('en',2)]:
 for script,task in [('wom14_v02.py','render'),('wom14_v02_assemble.py','assemble'),('wom14_v02_assemble.py','verify')]:
  save(ROOT/'records/pipeline_v02.json',dict(status='running',language=lang,scale=scale,task=task))
  subprocess.run([p,'new-channel/'+script,task,lang,str(scale)],check=True)
save(ROOT/'records/pipeline_v02.json',dict(status='normal_masters_and_pixel_proofs_complete',remaining='subtitled reviews, final visual QA, draft sharing'))
