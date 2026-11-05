"""Run the derived outputs only after an intact picture master and mix exist."""
import concurrent.futures,sys,subprocess,time
from wom12_produce import ROOT,read,probe
from pathlib import Path
P=Path(__file__).parent

def stage(script,*args):
 name=script+'_'+('_'.join(args) or 'main');print('START',name,flush=True)
 with (ROOT/'_work'/f'{name}.log').open('w') as log:
  r=subprocess.run([sys.executable,str(P/(script+'.py')),*args],stdout=log,stderr=subprocess.STDOUT);r.check_returncode()
 print('DONE',name,flush=True)
if __name__=='__main__':
 state=ROOT/'records/encoding_method.json';deadline=time.monotonic()+1500
 while not state.exists():
  if time.monotonic()>deadline:raise TimeoutError('Picture master not finished')
  time.sleep(4)
 assert int(probe(ROOT/'_work/picture_master.mp4')['streams'][0]['nb_frames'])==12555
 stage('wom12_render','package')
 # Separate output directories. Cap concurrency to preserve memory on the production Mac.
 def qa1080():
  stage('wom12_render','reviews');stage('wom12_render','precision');stage('wom12_render','verify');stage('wom12_continuous_qc');stage('wom12_layout');stage('wom12_motion')
 with concurrent.futures.ThreadPoolExecutor(2) as tp:
  tasks=[tp.submit(qa1080),tp.submit(stage,'wom12_4k','v01','en')]
  for f in tasks:f.result()
