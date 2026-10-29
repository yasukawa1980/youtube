"""第8話の既存ローカル入力から確認版を作る。生成・購入・投稿は行わない。"""
import subprocess,sys,os,json,time
from pathlib import Path
HERE=Path(__file__).resolve().parent

def main():
 steps=[('wom08_produce.py','timeline'),('wom08_produce.py','audio'),('wom08_render.py','pictures'),('wom08_render.py','package'),('wom08_render.py','reviews'),('wom08_render.py','precision'),('wom08_render.py','verify'),('wom08_motion.py',),('wom08_final_motion.py',),('wom08_continuous_qc.py',),('wom08_validate.py',),('wom08_episode_qc.py',),('wom08_thumbnails.py',),('wom08_delivery.py',)]
 if '--visual-only' in sys.argv:steps=steps[2:]
 for args in steps:
  started=time.monotonic();print('BUILD START',*args,flush=True)
  subprocess.run([sys.executable,str(HERE/args[0]),*args[1:]],check=True)
  print('BUILD OK',*args,round(time.monotonic()-started,2),'s',flush=True)
if __name__=='__main__':main()
