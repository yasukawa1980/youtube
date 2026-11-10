"""Changed-shot evidence, source-native limits and final-camera continuity."""
import os,sys,subprocess,json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
from wom14_v02 import ROOT,BASE,MODIFIED,TEXT,SCALES,CELL_NATIVE,SPAN,read,save,sha,ff,path_video,v,text_camera

def samples(lang,scale):
 suffix='_4k' if scale==2 else '';shots=read(BASE/lang/f'records/render_shots{suffix}.json');folder=ROOT/lang/'review';changes=[]
 for s in shots:
  k=s['key']
  if k not in MODIFIED:continue
  frames=[round(s['end']*30)-1]
  if k in TEXT:frames=[e['start_frame']+min(10,e['frames']-1) for e in s['stages'] if e['kind']=='source_focus']+[round(s['end']*30)-1]
  for n,f in enumerate(sorted(set(frames))):
   pair=Image.new('RGB',(1280,385),'#201b17');d=ImageDraw.Draw(pair)
   for i,(base,label) in enumerate([(BASE,'v01'),(ROOT,'v02')]):
    p=folder/f'compare_{lang}{suffix}_{k}_{n}_{label}.jpg';ff(['-threads',1,'-ss',f/30,'-i',path_video(base,lang,scale),'-frames:v',1,'-vf','scale=1280:720','-filter_threads',1,'-q:v',2,'-update',1,p]);im=Image.open(p);pair.paste(im.resize((640,360)),(i*640,25));d.text((i*640+5,5),f'{k} {label} frame {f}',fill='white')
   p=folder/f'compare_{lang}{suffix}_{k}_{n}_pair.jpg';pair.save(p,quality=90);changes.append(dict(shot=k,frame=f,file=p.name))
 save(ROOT/lang/f'records/comparisons_v02{suffix}.json',changes)
 print('COMPARISONS',lang,scale,flush=True)

def motion(lang,scale):
 s=next(x for x in read(BASE/lang/'records/render_shots.json') if x['key']=='O02-A');src=path_video(ROOT,lang,scale)
 # Exclude the intentional two-second overview hold; evaluate every subsequent camera step.
 start=s['start']+2;count=s['frames']-60;x,y,w,h=[q*scale for q in [250,130,1420,775]]
 cmd=['ffmpeg','-nostdin','-v','error','-threads','1','-ss',str(start),'-i',str(src),'-frames:v',str(count),'-vf',f'format=gray,crop={w}:{h}:{x}:{y}:exact=1','-filter_threads','1','-pix_fmt','gray','-fps_mode','passthrough','-f','rawvideo','-'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE);previous=None;diff=[]
 for _ in range(count):
  raw=p.stdout.read(w*h);assert len(raw)==w*h;a=np.frombuffer(raw,np.uint8).astype(np.int16)
  if previous is not None:diff.append(float(np.abs(a-previous).mean()))
  previous=a
 assert p.wait()==0;median=float(np.median(diff));p95=float(np.percentile(diff,95));ratio=p95/median
 d=dict(passed=ratio<=2.5,shot='O02-A',scale=scale,roi=[x,y,w,h],pairs=len(diff),median=median,p95=p95,ratio=ratio,excluded='first two seconds are an intentional full-work hold',source=sha(src));save(ROOT/lang/f'records/motion_v02{"_4k" if scale==2 else ""}.json',d);print('MOTION',lang,scale,ratio,flush=True);assert d['passed'],d

def geometry():
 records=[]
 for lang,scale in [('en',1),('ja',1),('en',2)]:
  suffix='_4k' if scale==2 else '';shots=read(BASE/lang/f'records/render_shots{suffix}.json')
  for s in shots:
   if s['key'] not in MODIFIED:continue
   k=s['key'];events=[e['start_frame'] for e in s['stages'] if e['kind']=='source_focus'];row=dict(language=lang,scale=scale,shot=k,highlight_frames_unchanged=events,start_frame=round(s['start']*30),frames=s['frames'],art_bottom=905*scale,subtitle_top=932*scale,minimum_subtitle_gap=27*scale,minimum_note_gap=(14 if k in v.NOTES else 9)*scale)
   if k in TEXT:
    row.update(native_scale=min(1,SCALES[k]*scale),source_character_cell_height=CELL_NATIVE[k],output_character_cell_height=CELL_NATIVE[k]*min(1,SCALES[k]*scale),character_size_basis='Full character cell/pitch; irregular brush-stroke ink height differs by glyph',source_columns_not_reordered=True,source_x_span=SPAN[k],camera=[])
    for j in range(s['frames']):
     z,f,cy,sc,stage=text_camera(k,s,round(s['start']*30)+j,scale)
     if j%30==0 or round(s['start']*30)+j in events:row['camera'].append(dict(frame=round(s['start']*30)+j,center_y_fraction=cy,native_scale=sc,highlight=stage))
   elif k=='O02-A':row.update(native_scale_max=1.0,oni_native_bounds_fraction=[.267,.758,.59,.848],oni_native_height=.09*v.ASSETS[k]['original_dimensions'][1],oni_max_screen_height_fraction=.09*v.ASSETS[k]['original_dimensions'][1]/(1080*scale),exception='本人は原寸1.0倍優先を承認。40%は原寸では達成不能。')
   else:row.update(source_crop_fraction=[.405,.245,.665,.435],native_scale_max=1.0,black_background_and_ruler_excluded=True)
   records.append(row)
 save(ROOT/'records/visual_geometry_v02.json',records)
if __name__=='__main__':
 if sys.argv[1]=='geometry':geometry()
 else:globals()[sys.argv[1]](sys.argv[2],int(sys.argv[3]))
