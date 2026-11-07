"""Finite, resumable local production job. No publication or background monitoring service."""
import os,sys,subprocess,json,time
from pathlib import Path
from wom13_produce import ROOT,read,save,sha
P=Path(__file__).resolve().parent
def step(name,script,args,env,deps,outputs):
 state=ROOT/'records/pipeline_steps'/f'{name}.json';state.parent.mkdir(exist_ok=True)
 cfg={str(p):sha(p) for p in [P/script,*deps]};old=read(state) if state.exists() else {}
 if old.get('inputs')==cfg and all(p.exists() and old.get('outputs',{}).get(str(p))==sha(p) for p in outputs):
  print('RESUME CHECKPOINT',name,flush=True);return
 print('START',name,flush=True);subprocess.run([sys.executable,str(P/script),*args],env=env,check=True)
 save(state,dict(inputs=cfg,outputs={str(p):sha(p) for p in outputs}));print('COMPLETE',name,flush=True)
def main():
 state=ROOT/'records/pipeline_state.json';save(state,dict(status='running',pid=os.getpid(),publication=False))
 try:
  for lang in ([] if '--4k-only' in sys.argv else ['en','ja']):
   r=ROOT/lang;env=dict(os.environ,WOM13_ROOT=str(r),WOM13_LANG=lang,WOM13_SCALE='1');master=r/'_work/picture_master.mp4';video=r/f'deliverables/EP013_NightWatch_{lang}_v01_1080p30.mp4';review=r/f'deliverables/EP013_NightWatch_{lang}_v01_subtitled_review_1080p30.mp4';audio=r/f'deliverables/EP013_audio_{lang}.m4a'
   subprocess.run([sys.executable,str(P/'wom13_picture.py')],env=env,check=True)
   step(lang+'_package','wom13_render.py',['package'],env,[master,audio],[video])
   step(lang+'_reviews','wom13_render.py',['reviews'],env,[video,video.with_suffix('.srt')],[review])
   subprocess.run([sys.executable,str(P/'wom13_render.py'),'precision'],env=env,check=True)
   step(lang+'_verify','wom13_render.py',['verify'],env,[video,review],[r/'records/qc_v01.json'])
   step(lang+'_continuous','wom13_qc.py',['continuous'],env,[video,r/'records/render_shots.json'],[r/'records/continuous_qc.json'])
   step(lang+'_layout','wom13_qc.py',['layout'],env,[r/'records/frame_layout.json',r/'records/art_scales.json'],[r/'records/layout_qc.json'])
   step(lang+'_motion','wom13_motion.py',[],env,[master,r/'records/render_shots.json'],[r/'records/final_video_motion.json'])
   assert read(r/'records/final_video_motion.json')['passed'],lang+' motion QA failed'
   save(state,dict(status='running',pid=os.getpid(),completed=lang+'_1080p',publication=False))
  r=ROOT/'en';env=dict(os.environ,WOM13_ROOT=str(r),WOM13_LANG='en',WOM13_SCALE='2');master=r/'_work/picture_master_4k.mp4';video=r/'deliverables/EP013_NightWatch_en_v01_2160p30.mp4'
  subprocess.run([sys.executable,str(P/'wom13_picture.py')],env=env,check=True)
  step('en_4k_package','wom13_render.py',['package4k'],env,[master,r/'deliverables/EP013_audio_en.m4a'],[video,r/'records/4k_audio_integrity.json'])
  subprocess.run([sys.executable,str(P/'wom13_render.py'),'precision'],env=env,check=True)
  step('en_4k_continuous','wom13_qc.py',['continuous'],env,[video,r/'records/render_shots_4k.json'],[r/'records/continuous_qc_4k.json'])
  step('en_4k_layout','wom13_qc.py',['layout'],env,[r/'records/frame_layout_4k.json',r/'records/art_scales_4k.json'],[r/'records/layout_qc_4k.json'])
  save(state,dict(status='technical_checks_complete',pid=os.getpid(),publication=False,remaining='Visual inspection, archive, private Draft Release with REST verification'))
 except BaseException as e:
  save(state,dict(status='failed',pid=os.getpid(),error=str(e),publication=False));raise
if __name__=='__main__':main()
