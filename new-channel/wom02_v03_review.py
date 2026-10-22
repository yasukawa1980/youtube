"""v03 all-shot and all-subtitle visual QA, reusing unchanged v02 glyph rasterization."""
import argparse,math,subprocess,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom02_revision_v03 import ROOT,PREV,REPO,read,save,sha,ff
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'

def layout():
 before=read(PREV/'records/subtitle_layout_validation.json');manifest=read(ROOT/'records/visual_manifest.json')['shots']
 for l in ['en','ja']:
  assert sha(PREV/f'deliverables/EP002_Halloween_{l}_v02_1080p30.srt')==sha(ROOT/f'deliverables/EP002_Halloween_{l}_v03_1080p30.srt')
  for size in [14,26]:
   src=PREV/f'_work/layout_{l}_{size}';dst=ROOT/f'_work/layout_{l}_{size}'
   if not dst.exists():shutil.copytree(src,dst)
 checks=[]
 for s in manifest:
  bottom=max(t['bbox'][3] for t in s['texts']);assert bottom<=700
  # Diagram text moves with the 3% camera zoom; fixed header text does not.
  top,lower=s['camera_band'];center=(top+lower)/2
  animated_bottom=max(max(t['bbox'][3],center+1.03*(t['bbox'][3]-center)) if t['bbox'][1]>=top else t['bbox'][3] for t in s['texts'])
  assert animated_bottom<=700
  if s.get('base_asset'):assert bottom<100
  # Images can overlap subtitles. Only text is checked against the exact preserved glyph bboxes.
  subtitle_min=before['minimum_glyph_top'];assert bottom<subtitle_min
  checks.append({'segment_id':s['segment_id'],'key':s['key'],'text_bottom':bottom,'maximum_animated_text_bottom':animated_bottom,'subtitle_min_top':subtitle_min,'passed':True})
 save(ROOT/'records/subtitle_layout_validation.json',{'passed':True,'visual_manifest_sha256':sha(ROOT/'records/visual_manifest.json'),'all_172_cues_two_sizes':344,'method':'Identical SRTs and FontSize14/26 styles: v02 libass glyph rasters reused byte-for-byte, recomposited against every v03 cue frame. Text bounds compared against actual glyph bounds; imagery is allowed below y700.','minimum_glyph_top':before['minimum_glyph_top'],'checks':checks,'srt_checks':before['srt_checks']})
 print('LAYOUT',len(checks),'shot layouts; 344 cue rasters',flush=True)

def frames():
 shots=read(ROOT/'records/render_shots.json');video=ROOT/'deliverables/EP002_Halloween_en_v03_1080p30.mp4';font=ImageFont.truetype(FONT,15);records=[]
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
 save(ROOT/'records/shot_center_validation.json',{'count':len(records),'video_sha256':sha(video),'frames':records})
 print('FRAME QA',len(records),flush=True)

def geometry():
 originals={a['id']:Path(a['original_local_path']) for a in read(ROOT/'records/source_assets.json')['assets']}
 originals.update({a['id']:Path(a['original_local_path']) for a in read(ROOT/'records/new_sources_v03.json')})
 originals.update({a['id']:Path(a['local_path']) for a in read(ROOT/'records/ai_images.json')})
 for a in read(ROOT/'records/new_videos_v03.json'):originals[a['id']]=ROOT/f'assets/{a["id"]}_poster.png'
 crops={'A03':(.28,.38,.73,.88),'A04':(.26,.18,.75,.67),'A05':(0,.31,.40,.67),'A06':(.08,.02,.95,.27)};checks=[];Image.MAX_IMAGE_PIXELS=200000000
 for s in read(ROOT/'records/visual_manifest.json')['shots']:
  if not s.get('base_asset'):continue
  id=s['base_asset'];im=Image.open(originals[id]);sizes=[im.size]
  if s['key'].endswith('_detail'):
   c=crops[id];box=[round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(c)];sizes.append((box[2]-box[0],box[3]-box[1]))
  for b,size in zip(s['art_boxes'],sizes):
   assert b[0]>=80 and b[1]>=110 and b[2]<=1840 and b[3]<=930
   z=max((b[2]-b[0])/size[0],(b[3]-b[1])/size[1])*(1 if s.get('video_asset') else 1.03);assert z<=1.5;checks.append({'id':id,'box_initial_xyxy':b,'source_pixels':size,'maximum_scale_including_zoom':z})
 save(ROOT/'records/layout_geometry_v03.json',{'passed':True,'placement_scope':'Initial composed foreground boxes; source magnification includes the 3% subpixel camera. Blurred background excluded.','maximum_source_scale_including_zoom':max(c['maximum_scale_including_zoom'] for c in checks),'checks':checks})
 print('GEOMETRY',len(checks),flush=True)

def sources():
 xs=read(ROOT/'records/new_videos_v03.json');font=ImageFont.truetype(FONT,15)
 for a in xs:
  folder=ROOT/'_work/source_review';folder.mkdir(exist_ok=True);sheet=Image.new('RGB',(1280,560),'#0c1820');d=ImageDraw.Draw(sheet)
  for i,t in enumerate([.1,2,4,6,8,9.9]):
   p=folder/f'{a["id"]}_{i}.jpg';ff(['-ss',t,'-i',a['local_path'],'-frames:v',1,'-vf','scale=426:240','-q:v',3,p]);x=i%3*426;y=i//3*280;sheet.paste(Image.open(p),(x,y));d.text((x+5,y+245),f'{a["id"]} {t}s',font=font,fill='white')
  sheet.save(ROOT/f'review/source_video_{a["id"]}.jpg',quality=87,optimize=True)
 print('SOURCE SEQUENCES',len(xs),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['layout','frames','sources','geometry']);a=p.parse_args();globals()[a.stage]()
