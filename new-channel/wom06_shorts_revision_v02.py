"""Build the 2026-10-27 hook comparison; preserve v01 and reuse S2 exactly."""
import os,json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD=Path('/Users/ryo/Desktop/新チャンネル/ショート/EP006_確認版_v01_20261027')
ROOT=OLD.with_name('EP006_冒頭比較_v02_20261027')
os.environ['QO_EP006_ROOT']=str(ROOT)
os.environ['QO_EP006_REQUEST']=str(HERE/'wom_ショート冒頭修正_EP006_v02_20261027.md')
os.environ['QO_EP006_CONFIG']=str(HERE/'wom06_shorts_v02_config.json')
import wom06_shorts as nar
import wom06_shorts_render as render
import wom06_shorts_qc as qc

def prepare():
 for folder in ['audio','records','review','deliverables','_work']:(ROOT/folder).mkdir(parents=True,exist_ok=True)
 before={p.name:nar.sha(p) for p in (OLD/'deliverables').glob('*.mp4')}
 nar.save(ROOT/'records/originals_preserved.json',{'source':str(OLD),'sha256':before})
 for p in (OLD/'audio').glob('S2*'):shutil.copy2(p,ROOT/'audio'/p.name)
 shutil.copy2(OLD/'records/S2_phoneme_timings.json',ROOT/'records/S2_phoneme_timings.json')
 stamp=ROOT/'audio/S2_native.json';cfg=json.loads(stamp.read_text());cfg['request_sha256']=nar.sha(nar.REQUEST);nar.save(stamp,cfg)
 nar.narration()
 render.captions()
 render.audio()
 # Preserve exact original S2 mix and narration stems as the unchanged reference.
 for p in (OLD/'audio').glob('S2*'):
  if p.suffix!='.json':shutil.copy2(p,ROOT/'audio'/p.name)
 aq=render.read(ROOT/'records/audio_qc.json');oldaq=render.read(OLD/'records/audio_qc.json')
 for i,r in enumerate(aq['reports']):
  if r['id']=='S2':
   q=next(a for a in oldaq['reports'] if a['id']=='S2');q['final_file']=str(ROOT/'audio/S2_final.m4a');aq['reports'][i]=q
 render.save(ROOT/'records/audio_qc.json',aq)
 render.visuals()

def build():
 render.render()
 target=ROOT/'deliverables/QO_short_EP006_S2_v02.mp4'
 shutil.copy2(OLD/'deliverables/QO_short_EP006_S2_v01.mp4',target)
 assert nar.sha(target)==nar.sha(OLD/'deliverables/QO_short_EP006_S2_v01.mp4')
 method=render.read(ROOT/'records/encoding_method.json')
 for s in method['shorts']:
  if s['id']=='S2':s.update(video_sha256=nar.sha(target),reference_reused_byte_identical=True,original_path=str(OLD/'deliverables/QO_short_EP006_S2_v01.mp4'))
 render.save(ROOT/'records/encoding_method.json',method)

def verify():
 qc.verify();qc.glyphs();qc.motion();qc.frames()
 baseline=render.read(ROOT/'records/originals_preserved.json')
 assert baseline['sha256']=={p.name:nar.sha(p) for p in (OLD/'deliverables').glob('*.mp4')}
 baseline['verified_after']=True;render.save(ROOT/'records/originals_preserved.json',baseline)

if __name__=='__main__':globals()[sys.argv[1]]()
