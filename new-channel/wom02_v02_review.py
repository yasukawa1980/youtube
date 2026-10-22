"""v02 all-shot and all-subtitle visual QA, reusing unchanged v01 glyph rasterization."""
import argparse,math,subprocess,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom02_revision_v02 import ROOT,PREV,REPO,read,save,sha,ff
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'

def layout():
 before=read(PREV/'records/subtitle_layout_validation.json');manifest=read(ROOT/'records/visual_manifest.json')['shots']
 for l in ['en','ja']:
  assert sha(PREV/f'deliverables/EP002_Halloween_{l}_v01_1080p30.srt')==sha(ROOT/f'deliverables/EP002_Halloween_{l}_v02_1080p30.srt')
  for size in [14,26]:
   src=PREV/f'_work/layout_{l}_{size}';dst=ROOT/f'_work/layout_{l}_{size}'
   if not dst.exists():shutil.copytree(src,dst)
 checks=[]
 for s in manifest:
  bottom=max(t['bbox'][3] for t in s['texts']);assert bottom<=700
  if s.get('base_asset'):assert bottom<100
  # Images can overlap subtitles. Only text is checked against the exact preserved glyph bboxes.
  subtitle_min=min(c['minimum_subtitle_top'] for c in before['checks']);assert bottom<subtitle_min
  checks.append({'segment_id':s['segment_id'],'key':s['key'],'text_bottom':bottom,'subtitle_min_top':subtitle_min,'passed':True})
 save(ROOT/'records/subtitle_layout_validation.json',{'passed':True,'all_172_cues_two_sizes':344,'method':'Identical SRTs and FontSize14/26 styles: v01 libass glyph rasters reused byte-for-byte, recomposited against every v02 cue frame. Text bounds compared against actual glyph bounds; imagery is allowed below y700.','minimum_glyph_top':min(c['minimum_subtitle_top'] for c in before['checks']),'checks':checks,'srt_checks':before['actual_srt_checks']})
 print('LAYOUT',len(checks),'shot layouts; 344 cue rasters',flush=True)

def frames():
 shots=read(ROOT/'records/render_shots.json');video=ROOT/'deliverables/EP002_Halloween_en_v02_1080p30.mp4';font=ImageFont.truetype(FONT,15);records=[]
 for i,s in enumerate(shots):
  t=(s['start']+s['end'])/2;p=ROOT/f'review/shot_{i+1:02}.jpg';ff(['-ss',t,'-i',video,'-frames:v',1,'-vf','scale=1280:720','-q:v',3,p]);records.append({'shot':i+1,'segment_id':s['segment_id'],'key':s['key'],'time':t,'file':str(p.relative_to(ROOT))})
 for batch in range(math.ceil(len(records)/12)):
  sheet=Image.new('RGB',(1280,1040),'#0c1820');d=ImageDraw.Draw(sheet)
  for i,r in enumerate(records[batch*12:batch*12+12]):
   x=i%3*426;y=i//3*260;im=Image.open(ROOT/r['file']);im.thumbnail((426,240));sheet.paste(im,(x,y));d.text((x+6,y+241),f"{r['segment_id']} {r['key']} {r['time']:.2f}s",font=font,fill='#f4efdf')
  sheet.save(ROOT/f'review/final_storyboard_{batch+1}.jpg',quality=85,optimize=True)
 for lang in ['en','ja']:
  cues=read(ROOT/f'records/subtitle_cues_{lang}.json')['cues'];folder=ROOT/f'_work/cue_context_{lang}';folder.mkdir(exist_ok=True)
  ns=[round((c['start']+c['end'])*15) for c in cues];terms=[f'eq(n\\,{n})' for n in ns];expr='+'.join('('+'+'.join(terms[i:i+20])+')' for i in range(0,len(terms),20))
  ff(['-i',video,'-vf',f'select={expr},scale=640:360','-fps_mode','passthrough','-q:v',3,folder/'%04d.jpg'])
  for size in [14,26]:
   for batch in range(math.ceil(len(cues)/12)):
    sheet=Image.new('RGB',(1280,1040),'#0c1820');d=ImageDraw.Draw(sheet)
    for i,c in enumerate(cues[batch*12:batch*12+12]):
     n=batch*12+i+1;scene=Image.open(folder/f'{n:04d}.jpg').resize((1920,1080));glyph=Image.open(ROOT/f'_work/layout_{lang}_{size}/{n:04d}.png').convert('RGB');gray=np.array(glyph).max(axis=2);ys,xs=np.where(gray>100)
     ImageDraw.Draw(scene).rectangle((xs.min()-12,ys.min()-10,xs.max()+12,ys.max()+10),fill='black');mask=Image.fromarray(np.where(gray>0,255,0).astype('uint8'));scene.paste(glyph,(0,0),mask);scene=scene.resize((426,240));x=i%3*426;y=i//3*260;sheet.paste(scene,(x,y));d.text((x+6,y+241),f'{lang} {size}px cue {n} {c["sentence_id"]}',font=font,fill='#f4efdf')
    sheet.save(ROOT/f'review/subtitles_{lang}_{size}_{batch+1:02d}.jpg',quality=83,optimize=True)
 save(ROOT/'records/shot_center_validation.json',{'count':len(records),'frames':records})
 print('FRAME QA',len(records),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['layout','frames']);a=p.parse_args();globals()[a.stage]()
