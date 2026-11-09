"""Finite resumable EP014 production through measured technical QA. No publication."""
import os,sys,subprocess
from pathlib import Path
from wom14_produce import ROOT,read,save,sha
P=Path(__file__).resolve().parent

def step(name,script,args,env,deps,outputs):
 state=ROOT/'records/pipeline_steps'/f'{name}.json';state.parent.mkdir(exist_ok=True)
 cfg={str(p):sha(p) for p in [P/script,*deps]};old=read(state) if state.exists() else {}
 if old.get('inputs')==cfg and all(p.exists() and old.get('outputs',{}).get(str(p))==sha(p) for p in outputs):print('CHECKPOINT',name,flush=True);return
 print('START',name,flush=True);subprocess.run([sys.executable,str(P/script),*args],env=env,check=True)
 save(state,dict(inputs=cfg,outputs={str(p):sha(p) for p in outputs}));print('COMPLETE',name,flush=True)
def main():
 state=ROOT/'records/pipeline_state.json';save(state,dict(status='running',pid=os.getpid(),publication=False))
 try:
  for lang in ([] if '--4k-only' in sys.argv else ['en','ja']):
   r=ROOT/lang;env=dict(os.environ,WOM14_ROOT=str(r),WOM14_LANG=lang,WOM14_SCALE='1');video=r/f'deliverables/EP014_Oni_{lang}_v01_1080p30.mp4';review=r/f'deliverables/EP014_Oni_{lang}_v01_subtitled_review_1080p30.mp4';audio=r/f'deliverables/EP014_audio_{lang}.m4a'
   step(lang+'_audio','wom14_music.py',[],env,[r/'records/master_timeline.json',r/f'audio/{lang}/narration.wav'],[audio,r/f'deliverables/EP014_audio_{lang}.wav'])
   step(lang+'_subtitles','wom14_subcheck.py',[],env,[r/f'records/subtitle_cues_{lang}.json'],[r/'records/subtitle_layout_validation.json'])
   subprocess.run([sys.executable,str(P/'wom14_picture.py'),'design'],env=env,check=True)
   subprocess.run([sys.executable,str(P/'wom14_qc.py'),'layout'],env=env,check=True)
   subprocess.run([sys.executable,str(P/'wom14_picture.py')],env=env,check=True)
   step(lang+'_package','wom14_render.py',['package'],env,[r/'_work/picture_master.mp4',audio],[video])
   step(lang+'_review','wom14_render.py',['reviews'],env,[video,video.with_suffix('.srt')],[review])
   subprocess.run([sys.executable,str(P/'wom14_render.py'),'precision'],env=env,check=True)
   step(lang+'_continuous','wom14_qc.py',['continuous'],env,[video,r/'records/render_shots.json'],[r/'records/continuous_qc.json'])
   step(lang+'_verify','wom14_render.py',['verify'],env,[video,review],[r/'records/qc_v01.json'])
   step(lang+'_motion','wom14_qc.py',['motion'],env,[r/'_work/picture_master.mp4',r/'records/render_shots.json'],[r/'records/final_video_motion.json'])
   save(state,dict(status='running',completed=lang+'_1080p',pid=os.getpid(),publication=False))
  r=ROOT/'en';env=dict(os.environ,WOM14_ROOT=str(r),WOM14_LANG='en',WOM14_SCALE='2');video=r/'deliverables/EP014_Oni_en_v01_2160p30.mp4'
  subprocess.run([sys.executable,str(P/'wom14_picture.py'),'design'],env=env,check=True)
  subprocess.run([sys.executable,str(P/'wom14_qc.py'),'layout'],env=env,check=True)
  subprocess.run([sys.executable,str(P/'wom14_picture.py')],env=env,check=True)
  step('en_4k_package','wom14_render.py',['package4k'],env,[r/'_work/picture_master_4k.mp4',r/'deliverables/EP014_audio_en.m4a'],[video,r/'records/4k_audio_integrity.json'])
  subprocess.run([sys.executable,str(P/'wom14_render.py'),'precision'],env=env,check=True)
  step('en_4k_continuous','wom14_qc.py',['continuous'],env,[video,r/'records/render_shots_4k.json'],[r/'records/continuous_qc_4k.json'])
  save(state,dict(status='technical_checks_complete',pid=os.getpid(),publication=False,remaining='visual inspection, package, private Draft Release and REST re-download verification'))
 except BaseException as e:save(state,dict(status='failed',pid=os.getpid(),error=str(e),publication=False));raise
if __name__=='__main__':main()
