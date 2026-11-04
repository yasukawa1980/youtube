"""Render v02, then overlap independent 4K encoding and completed-video QA."""
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
def run(stage):
 print('V02 STAGE',stage,flush=True)
 subprocess.run([sys.executable,str(HERE/'wom11_v02.py'),stage],check=True)
def main():
 for stage in ['pictures','package','revision']:run(stage)
 fourk=subprocess.Popen([sys.executable,str(HERE/'wom11_v02.py'),'4k'])
 for stage in ['reviews','precision']:run(stage)
 verify=subprocess.Popen([sys.executable,str(HERE/'wom11_v02.py'),'verify'])
 for stage in ['continuous','motion','pixel','revision']:run(stage)
 assert verify.wait()==0
 assert fourk.wait()==0
 print('V02 TECHNICAL FINISH COMPLETE; inspect final images before sharing',flush=True)
if __name__=='__main__':main()
