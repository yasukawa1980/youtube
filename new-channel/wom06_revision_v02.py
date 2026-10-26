"""EP006 v02: only requested visual intervals change; originals and narration remain intact."""
import argparse,copy,csv,json,os,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageOps
import numpy as np
import wom06_produce as p
import wom06_visuals as v
from wom06_render import camera
OLD=p.ROOT
ROOT=OLD.parent/'確認版_v02_20261027'
CHANGED=[(556,838),(838,1209),(4107,4563),(5166,5616),(5616,6144),(6144,6350)]

def prepare():
 for d in ['records','assets','review','deliverables','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 for name in ['content.json','content_en.json','master_timeline.json','source_assets.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_cues_en.json','subtitle_cues_ja.json','subtitle_validation.json','subtitle_layout_validation.json','audio_subtitle_checks.json','reading_replacements.json','reading_audit.json','pronunciation_locations.json','ai_videos.json','kling_generation.json']:
  shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
 for f in (OLD/'deliverables').iterdir():
  if f.suffix in ['.srt','.m4a','.wav']:
   name=f.name.replace('_v01_','_v02_');dest=ROOT/'deliverables'/name
   if dest.exists():assert p.sha(dest)==p.sha(f)
   else:shutil.copy2(f,dest)
 v.originals['museo_Inv27_001']=ImageOps.exif_transpose(Image.open(v.assets['museo_Inv27_001']['path'])).convert('RGB')
 v.CROPS['museo_Inv27_001']=(.075,.004,.999,.984)
 v.CROPS['met_437153']=(.12,.10,.95,.33)
 for key in ['museo_Inv27_001','met_437153']:v.images[key]=v.crop(v.originals[key],v.CROPS[key])
 v.SOURCES['museo_Inv27_001']='C. & G. Zangaki • 1870 • Archivio Museo Egizio, Inv27_001'
 # Exact image pixel rectangles; ink baselines were inspected before choosing margins.
 details={'jebb1904_15':[60,1400,1015,1524]}
 hesiod_quad=[75,1250,75,1300,1292,1290,1292,1240] # UL, LL, LR, UR: follow the sloping baseline.
 hesiod_detail=v.originals['hesiod_159'].transform((1217,50),Image.Transform.QUAD,hesiod_quad,Image.Resampling.BICUBIC)
 for key,rect in details.items():
  w,h=v.originals[key].size;v.DETAILS[key]=tuple(a/(w if i%2==0 else h) for i,a in enumerate(rect))
 shots=[];old=p.read(OLD/'records/render_shots.json')
 for s in old:
  s=copy.deepcopy(s);s['file']=str(OLD/s['file']) if 'file' in s else None;s['encoded_file']=str(OLD/s['encoded_file']);s['changed_v02']=False
  if s['segment_id']=='P09' and s['key']=='met_247343':continue
  key=s['key'];newkey={'met_286141':'museo_Inv27_001','D_pair(met_544186,met_256761)':'D_pair(met_544186,met_329999)'}.get(key,key)
  changed=key in ['met_286141','D_pair(met_544186,met_256761)','hesiod_159','jebb1904_15','met_437153','met_329999']
  if changed:
   if key=='met_329999':newkey='met_247343';s['end']=187.2;s['frames']=450
   if newkey.startswith('D_pair'):
    v.TEXT=[];v.BOXES=[];im=Image.new('RGB',(1920,1080),v.BG)
    source='Senwosret III • The Met, 17.9.2  /  Bronze sphinx • The Met, 2021.40.14';label='SCHEMATIC｜模式図'
    v.header(im,label,source)
    for k,x in [('met_544186',130),('met_329999',1040)]:v.panel(im,v.images[k],(x,140,750,420))
    for x,t in [(505,'EGYPT｜エジプト'),(1415,'GREECE｜ギリシャ')]:v.text(im,(x,615),t,40,v.GOLD,True)
    rec={'base_asset':None,'base_assets':['met_544186','met_329999'],'source':source,'label':label,'texts':v.TEXT.copy(),'art_boxes':v.BOXES.copy(),'camera_band':[110,700]}
   elif newkey=='hesiod_159':
    v.TEXT=[];v.BOXES=[];im=v.background(v.images[newkey]);v.panel(im,v.images[newkey],(80,110,860,820));v.panel(im,hesiod_detail,(980,110,860,820));v.header(im,'PRINTED BOOK｜刊本',v.SOURCES[newkey])
    rec={'base_asset':newkey,'source':v.SOURCES[newkey],'label':'PRINTED BOOK｜刊本','texts':v.TEXT.copy(),'art_boxes':v.BOXES.copy(),'camera_band':[110,930],'detail_crop_quad_pixels':hesiod_quad,'detail_transform':'Bicubic deskew of the single printed line; no painting or character alteration.'}
    hesiod_detail.save(ROOT/'review/hesiod_159_exact_detail.png')
   else:im,rec=v.compose(newkey)
   dst=ROOT/f'assets/{s["segment_id"]}_{newkey}.png';im.save(dst)
   s.update(rec);s.update(key=newkey,file=str(dst),sha256=p.sha(dst),changed_v02=True,old_key=key,encoded_file=str(ROOT/f'_work/render/{s["segment_id"]}_{newkey}.mp4'))
   if newkey in details:
    s['detail_crop_pixels']=details[newkey];v.originals[newkey].crop(details[newkey]).save(ROOT/f'review/{newkey}_exact_detail.png')
   if newkey=='met_247343':s['camera_direction']='face_to_wing'
  shots.append(s)
 assert len(shots)==24 and sum(s['frames'] for s in shots)==10955
 assert [(round(s['start']*30),round(s['end']*30)) for s in shots if s['changed_v02']]==CHANGED
 p.save(ROOT/'records/render_shots.json',shots)
 used=[]
 for s in shots:used.extend(s.get('base_assets',[]) or ([s.get('base_asset')] if s.get('base_asset') in v.assets else []))
 assert len(used)==len(set(used))==18
 p.save(ROOT/'records/visual_manifest.json',{'shots':[s for s in shots if s['segment_id']!='BRAND'],'unique_originals':used,'canvas':[1920,1080]})
 p.save(ROOT/'records/revision_plan.json',{'request':'wom06_修正依頼_v02_20261026.md','previous_root':str(OLD),'root':str(ROOT),'changed_frame_intervals_half_open':CHANGED,'changed_frames':sum(b-a for a,b in CHANGED),'unchanged_frames':10955-sum(b-a for a,b in CHANGED),'script_audio_subtitles_unchanged':True,'optional_met_255796':'Not used: motif too small/low contrast; P09 uses met_247343 for all 450 frames.','end_credits':'Institution-level credits already remain accurate; no artist or accession list was present in v01 screen. No screen change needed.','human_pronunciation_approved':'本人が試聴して大丈夫と回答済み（修正依頼書）'})
 print('PREPARED V02: 6 intervals / 2293 frames; 18 unique originals',flush=True)

def render():
 shots=p.read(ROOT/'records/render_shots.json')
 for s in shots:
  if not s['changed_v02']:continue
  n=s['frames'];key=s['key'];out=Path(s['encoded_file']);static=key.startswith('D_')
  filt='[0:v]format=yuv420p[v]' if static else camera(n,s['camera_band'],direction=s.get('camera_direction'))
  if s['segment_id']=='P09':
   # This object's face is to the left of its wing: move the source window right.
   filt=filt.replace('0.72-0.44*','0.28+0.44*')
  cfg={'image_sha256':p.sha(s['file']),'frames':n,'filter':filt,'quality':'lossless' if static else 'crf18'};stamp=out.with_suffix('.json')
  if not(out.exists() and stamp.exists() and p.read(stamp)==cfg):
   quality=['-qp',0,'-profile:v','high444'] if static else ['-crf',18,'-profile:v','high']
   p.ff(['-loop',1,'-framerate',30,'-i',s['file'],'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',n,'-an','-c:v','libx264','-threads',2,'-preset','veryfast',*quality,'-pix_fmt','yuv420p','-video_track_timescale',15360,out]);p.save(stamp,cfg)
  s['render_config']=cfg;print('RENDERED',s['segment_id'],key,n,flush=True)
 p.save(ROOT/'records/render_shots.json',shots)
 oldcmd=p.read(OLD/'records/encoding_method.json')['command'];cmd=oldcmd[:-1]+[str(ROOT/'_work/picture_master.mp4')]
 assert cmd[cmd.index('-i')+1]=='pipe:0'
 with (ROOT/'records/encode.log').open('w') as log:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for s in shots:
    src=Path(s['encoded_file']);assert not src.is_relative_to(OLD/'deliverables'),'Finished v01 MP4 must never be an input'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
   enc.stdin.close();assert enc.wait()==0
  except BaseException:enc.kill();enc.wait();raise
 p.save(ROOT/'records/encoding_method.json',{'command':cmd,'method':'Each original/individual shot independently decoded to raw yuv420p and fed sequentially into one encoder. No finished v01 MP4 used as source.','shot_sources':[{'key':s['key'],'path':s['encoded_file'],'sha256':p.sha(s['encoded_file'])} for s in shots]})
 print('V02 PICTURE MASTER COMPLETE',flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['prepare','render']);a=ap.parse_args();globals()[a.stage]()
