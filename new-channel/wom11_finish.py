"""Resume final EP011 processing after pictures are complete. Never publishes or posts."""
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent

def run(script,*args):
 print('STAGE',script,*args,flush=True);subprocess.run([sys.executable,str(HERE/script),*args],check=True)

def main():
 # Cache stamps cause only changed shots to be rendered; the final master always uses one encoder.
 run('wom11_pictures.py')
 run('wom11_render.py','package')
 run('wom11_render.py','reviews')
 run('wom11_render.py','precision')
 run('wom11_render.py','verify')
 run('wom11_continuous_qc.py')
 run('wom11_final_motion.py')
 run('wom11_pixel_qc.py')
 run('wom11_episode_qc.py')
 run('wom11_4k.py','v01','en')
 # Visual inspection of extracted final frames must occur before packing and sharing.
 print('TECHNICAL FINISH COMPLETE; VISUAL REVIEW REQUIRED BEFORE SHARE',flush=True)
if __name__=='__main__':main()
