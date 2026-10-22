"""EP002 picture-only v02. v01 media, SRTs, timing and brand cuts are immutable."""
import argparse,copy,json,math,os,shutil,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageOps
os.environ['WOM02_ROOT']=os.environ.get('WOM02_V02_ROOT','/Users/ryo/Desktop/新チャンネル/EP002_Halloween/確認版_v02_20261022')
from wom02_produce import ROOT,REPO,MEDIA,read,save,sha,ff,probe
from wom01_quiet_origins import stream_hash
PREV=ROOT.parent/'確認版_v01_20261022';FPS=30
NEW={'H03':['R04','D_texts'],'H04':['R05','R06'],'H05':['D_story_record','R04_close'],'H02':['D_trail_pan','D_trail_pan']}

def prepare():
 for d in ['records','deliverables','assets','review','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 for name in ['content.json','content_en.json','master_timeline.json','source_assets.json','subtitle_cues_en.json','subtitle_cues_ja.json','narration_timeline_en.json','narration_timeline_ja.json','chapters.json','reading_replacements.json','pronunciation_locations.json','audio_qc.json','runtime.json']:
  src=PREV/'records'/name;dst=ROOT/'records'/name
  if dst.exists():assert sha(src)==sha(dst)
  else:shutil.copy2(src,dst)
 preserved=[]
 for p in (PREV/'deliverables').iterdir():
  if p.suffix in ['.srt','.m4a','.jpg','.txt'] and p.name!='SHA256SUMS_shared.txt':
   dst=ROOT/'deliverables'/p.name.replace('_v01_','_v02_');shutil.copy2(p,dst);assert sha(p)==sha(dst);preserved.append({'source':str(p),'copy':str(dst),'sha256':sha(p)})
 old=read(PREV/'records/ai_images.json');registry=REPO/'new-channel/episodes/EP002_Halloween/records/ai_images_v02.json'
 new=[a for a in read(registry if registry.exists() else Path('/tmp/wom02_v02_ai_prompts.json')) if a['id'] in ['R04','R05','R06']]
 for a in new:
  src=Path(a.get('local_path',a['source_path']));dst=MEDIA/(a['id']+'_reconstruction_v02.png')
  if dst.exists():assert sha(src)==sha(dst)
  else:shutil.copy2(src,dst)
  a.update({'local_path':str(dst),'sha256':sha(dst),'generated_date':'2026-10-22'})
 save(ROOT/'records/ai_images.json',old+new)
 save(ROOT/'records/preservation.json',{'files':preserved,'master_sha256':sha(PREV/'records/master_timeline.json'),'previous_root':str(PREV)})
 print('PREPARED',ROOT,flush=True)

def visuals():
 import wom02_visuals as v
 def header(im,label='',source=''):
  ImageDraw.Draw(im).rectangle((0,0,1920,109),fill=v.BG);v.text(im,(92,18),'QUIET ORIGINS  /  EP002',28,v.GOLD)
  if label:
   width=ImageDraw.Draw(im).textlength(label,font=v.font(27,label));v.text(im,(1820-width,21),label,27,v.GOLD)
  if source:v.text(im,(92,72),source,23,v.MUTED)
 v.header=header
 v.SOURCES['A07']='Library of Congress • Dorothea Lange • 1938 • California, USA｜米国カリフォルニア • LC-USF34-018556-D'
 def panel(im,art,box):
  x,y,w,h=box;z=min(w/art.width,h/art.height,1.5);out=art.resize((round(art.width*z),round(art.height*z)),Image.Resampling.LANCZOS);pos=(x+(w-out.width)//2,y+(h-out.height)//2);im.paste(out,pos);v.BOXES.append([*pos,pos[0]+out.width,pos[1]+out.height]);return z
 v.panel=panel
 old=read(PREV/'records/visual_manifest.json')['shots'];counts={};records=[]
 for shot in old:
  sid=shot['segment_id'];index=counts.get(sid,0);counts[sid]=index+1;key=NEW.get(sid,[s['key'] for s in old if s['segment_id']==sid])[index]
  base=key.replace('_detail','').replace('_close','');detail=key.endswith('_detail');v.TEXT=[];v.BOXES=[];extra={}
  if key=='D_trail_pan':
   # One continuous fractional-coordinate pan across four cards, split at the original two shot boundaries.
   im=Image.new('RGB',(3840,590),v.BG);d=ImageDraw.Draw(im)
   for i,(a,year,label) in enumerate(zip(['A03','A06','A01','A02'],['1430–1440','1786','1819','1900–1910'],['The Met','Wellcome','Library of Congress','NYPL'])):
    x=i*960;panel(im,v.images[a],(x+120,10,720,430))
    for yy,t,size in [(455,year,34),(515,label,28)]:
     f=v.font(size,t);w=d.textlength(t,font=f);xy=(x+480-w/2,yy);d.text(xy,t,font=f,fill=v.GOLD if yy==455 else v.MUTED);v.TEXT.append({'text':t,'bbox':list(d.textbbox(xy,t,font=f))})
   extra={'wide_pan':True,'strip_canvas':[3840,590],'pan_phase':index,'source':'The Met / Wellcome Collection / Library of Congress / NYPL','label':''}
  elif base in v.images:
   art=v.images[base]
   if key=='R04_close':art=art.crop((round(art.width*.16),round(art.height*.06),round(art.width*.85),round(art.height*.80)))
   im=v.background(art)
   if detail:
    panel(im,art,(80,110,860,820));crop=v.CROPS[base];piece=art.crop(tuple(round(a*(art.width if i%2==0 else art.height)) for i,a in enumerate(crop)));panel(im,piece,(980,110,860,820))
   else:panel(im,art,(80,110,1760,820))
   header(im,'AI RECONSTRUCTION｜AIによる再現' if base.startswith('R') else v.LABEL[base],v.SOURCES.get(base,''))
   extra={'base_asset':base,'source':v.SOURCES.get(base,''),'label':'AI RECONSTRUCTION｜AIによる再現' if base.startswith('R') else v.LABEL[base]}
  else:
   im,rec=v.compose(key);extra={k:rec[k] for k in ['base_asset','source','label']};extra['diagram']=True
   if key=='credits':
    v.TEXT=[t for t in v.TEXT if t['text']!='AI-generated • R01–R03'];ImageDraw.Draw(im).rectangle((460,495,1510,554),fill=v.BG);v.text(im,(470,504),'AI-generated • R01–R06',28,v.IVORY)
  p=ROOT/f'assets/{sid}_{index+1:02}_{key}.png';im.save(p)
  text=copy.deepcopy(v.TEXT);boxes=copy.deepcopy(v.BOXES)
  if key=='D_trail_pan':
   # Strip y is translated by 110 in the final frame; horizontal positions are camera-relative.
   for t in text:t['bbox'][1]+=110;t['bbox'][3]+=110
  assert max(t['bbox'][3] for t in text)<=700
  if base in v.images:assert all(t['bbox'][3]<100 for t in text)
  records.append({**shot,**extra,'key':key,'base_asset':extra.get('base_asset'),'file':str(p.relative_to(ROOT)),'sha256':sha(p),'texts':text,'art_boxes':boxes,'camera_band':[110,930] if base in v.images else [110,700]})
 save(ROOT/'records/visual_manifest.json',{'shots':records,'foreground_max_box':[80,110,1840,930],'detail_max_boxes':[[80,110,940,930],[980,110,1840,930]],'maximum_image_scale':1.5,'source_line_below_y':100})
 print('VISUALS',len(records),flush=True)

def camera(count,band=(110,930),wide=None):
 z=f'(1+0.03*on/{max(1,count-1)})';x=f'(W-W/{z})/2';y=f'(H-H/{z})/2'
 if wide is not None:
  # Source is a 3840px strip; the viewport moves 1920px across the full H02 interval.
  phase,offset,total=wide;x=f'(1920*(on+{offset})/{max(1,total-1)})';y='0'
  pr=f"perspective=x0='{x}':y0=0:x1='{x}+1920':y1=0:x2='{x}':y2=H:x3='{x}+1920':y3=H:sense=source:eval=frame:interpolation=cubic,scale=1920:590,format=yuv420p"
  return pr
 top,bottom=band;h=bottom-top
 p=f"perspective=x0='{x}':y0='{y}':x1='W-{x}':y1='{y}':x2='{x}':y2='H-{y}':x3='W-{x}':y3='H-{y}':sense=source:eval=frame:interpolation=cubic"
 return f'[0:v]split=2[base][art];[art]crop=1920:{h}:0:{top},format=yuv444p,{p}[moving];[base][moving]overlay=0:{top}:format=yuv444,format=yuv420p[v]'

def pictures(limit=0):
 old=read(PREV/'records/render_shots.json');new=iter(read(ROOT/'records/visual_manifest.json')['shots']);parts=[];records=[];done=0
 h02=[s for s in old if s['segment_id']=='H02'];htotal=sum(s['frames'] for s in h02);hoff=0
 for i,s in enumerate(old):
  if s['segment_id']=='BRAND':
   src=PREV/s['encoded_file'];dst=ROOT/s['encoded_file'];dst.parent.mkdir(parents=True,exist_ok=True)
   if not dst.exists():shutil.copy2(src,dst)
   assert sha(src)==sha(dst);parts.append(dst);records.append(s);continue
  a=next(new);count=s['frames'];out=ROOT/f'_work/render/{s["segment_id"]}_{i+1:02}_subpixel.mp4';stamp=out.with_suffix('.json')
  wide=(a['pan_phase'],hoff,htotal) if a.get('wide_pan') else None;filt=camera(count,a['camera_band'],wide)
  cfg={'image_sha256':sha(ROOT/a['file']),'frames':count,'filter':filt,'crf':18}
  if not(out.exists() and stamp.exists() and read(stamp)==cfg):
   if wide:
    # Animate the strip and lay it onto a fixed branded 1920x1080 base.
    bg=ROOT/'assets/trail_base.png'
    if not bg.exists():
     import wom02_visuals as v
     im=Image.new('RGB',(1920,1080),v.BG);ImageDraw.Draw(im).text((92,18),'QUIET ORIGINS  /  EP002',font=v.font(28),fill=v.GOLD);im.save(bg)
    fc=f'[1:v]format=yuv444p,{filt}[strip];[0:v][strip]overlay=0:110,format=yuv420p[v]'
    args=['-loop',1,'-framerate',30,'-i',bg,'-loop',1,'-framerate',30,'-i',ROOT/a['file'],'-filter_complex_threads',2,'-filter_complex',fc,'-map','[v]']
   else:args=['-loop',1,'-framerate',30,'-i',ROOT/a['file'],'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]']
   ff([*args,'-frames:v',count,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out]);save(stamp,cfg)
  parts.append(out);records.append({**a,'start':s['start'],'end':s['end'],'frames':count,'encoded_file':str(out.relative_to(ROOT))});done+=1
  if wide:hoff+=count
  print('PICTURE',s['segment_id'],a['key'],count,flush=True)
  if limit and done>=limit:return
 save(ROOT/'records/render_shots.json',records)
 listing=ROOT/'_work/concat.txt';listing.write_text(''.join(f"file '{p}'\nduration {s['frames']/30:.9f}\n" for p,s in zip(parts,records)))
 raw=ROOT/'_work/picture_concat.mp4';ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw]);ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movflags','+faststart',ROOT/'_work/picture_master.mp4'])
 assert [(s['start'],s['end'],s['frames']) for s in records]==[(s['start'],s['end'],s['frames']) for s in old]
 print('PICTURES COMPLETE',flush=True)

def package():
 for l in ['en','ja']:
  out=ROOT/f'deliverables/EP002_Halloween_{l}_v02_1080p30.mp4';ff(['-i',ROOT/'_work/picture_master.mp4','-i',PREV/f'deliverables/EP002_Halloween_{l}_v01_1080p30.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-movflags','+faststart',out]);print('PACKAGED',l,flush=True)

def review():
 import wom02_render as r
 # Existing review renderer, with versioned names and untouched audio.
 import imageio_ffmpeg
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP002_Halloween_{l}_v02_1080p30.mp4';out=ROOT/f'deliverables/EP002_Halloween_{l}_v02_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(src),'-vf',f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'",'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True);print('REVIEW',l,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','visuals','pictures','package','review']);p.add_argument('--limit',type=int,default=0);a=p.parse_args()
 if a.stage=='pictures':pictures(a.limit)
 else:globals()[a.stage]()
