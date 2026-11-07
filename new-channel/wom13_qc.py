"""Continuous decode, per-shot evidence and measured EP013 layout checks."""
import os,re,math,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageColor
import numpy as np
from wom13_produce import ROOT,REPO,read,save,sha,probe
LANG=os.environ.get('WOM13_LANG','en');S=int(os.environ.get('WOM13_SCALE','1'));SUFFIX='_4k' if S==2 else '';SIZE='2160' if S==2 else '1080'
def continuous():
 shots=read(ROOT/f'records/render_shots{SUFFIX}.json');m=read(ROOT/'records/master_timeline.json');n=round(m['duration_seconds']*30);src=ROOT/f'deliverables/EP013_NightWatch_{LANG}_v01_{SIZE}p30.mp4'
 assert len(shots)==22 and sum(s['frames'] for s in shots)==n
 selected=set([0,30,60,90]);triples=[]
 for s in shots:
  start=round(s['start']*30);tr=[start,start+(s['frames']-1)//2,start+s['frames']-1];triples.append(tr);selected.update(tr)
  selected.update(e['start_frame']+(e['frames']-1)//2 for e in s.get('stages',[]))
 frames=sorted(selected);folder=ROOT/f'_work/continuous{SUFFIX}';folder.mkdir(exist_ok=True)
 def balanced(values):
  if len(values)==1:return f'eq(n\\,{values[0]})'
  mid=len(values)//2;return '('+balanced(values[:mid])+'+'+balanced(values[mid:])+')'
 expr=balanced(frames) # Keep libavutil expression-parser recursion bounded for >100 selected frames.
 cmd=['ffmpeg','-y','-nostdin','-v','level+info','-xerror','-threads','2','-i',str(src),'-an','-filter_threads','2','-vf','showinfo=checksum=0,select='+expr+',scale=1280:720','-fps_mode','passthrough','-threads:v','2',str(folder/'%03d.png')]
 p=subprocess.run(cmd,capture_output=True,text=True)
 if p.returncode:
  (ROOT/f'records/continuous_error{SUFFIX}.log').write_text(p.stderr);raise RuntimeError(p.stderr[-4000:])
 assert not re.search(r'\[(?:warning|error|fatal)\]',p.stderr),p.stderr[-3000:]
 rows=re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+).*?\bfmt:(\w+).*?\bs:(\d+x\d+)',p.stderr)
 assert len(rows)==n and {r[2:] for r in rows}=={('yuv420p',f'{1920*S}x{1080*S}')}
 assert all(int(row[0])==i and int(row[1])==i*512 for i,row in enumerate(rows))
 v=next(x for x in probe(src)['streams'] if x['codec_type']=='video');assert v['profile']=='High' and v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==n
 paths={f:folder/f'{i+1:03d}.png' for i,f in enumerate(frames)};checks=[];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
 for i,(s,tr) in enumerate(zip(shots,triples)):
  trip=Image.new('RGB',(1280,276),'#14110f');dr=ImageDraw.Draw(trip)
  for j,f in enumerate(tr):
   with Image.open(paths[f]) as im:trip.paste(im.resize((426,240),Image.Resampling.LANCZOS),(426*j,0))
   dr.text((426*j+8,245),f'{["FIRST","MIDDLE","LAST"][j]}  frame {f}',fill='white',font=font)
  dest=ROOT/f'review/continuous_{LANG}{SUFFIX}_shot_{i+1:02d}.jpg';trip.save(dest,quality=88,optimize=True)
  center=ROOT/f'review/center_{LANG}{SUFFIX}_{i+1:02d}.jpg'
  with Image.open(paths[tr[1]]) as im:im.save(center,quality=91,optimize=True)
  checks.append(dict(key=s['key'],frames=tr,triptych=str(dest.relative_to(ROOT)),center=str(center.relative_to(ROOT))))
 for i in range(math.ceil(len(shots)/4)):
  sheet=Image.new('RGB',(1280,1240),'#14110f');dr=ImageDraw.Draw(sheet)
  for j,c in enumerate(checks[i*4:i*4+4]):
   dr.text((10,j*310+5),f'{LANG}{SUFFIX} {i*4+j+1:02} {c["key"]}',font=font,fill='#d8b575')
   with Image.open(ROOT/c['triptych']) as im:sheet.paste(im,(0,j*310+30))
  sheet.save(ROOT/f'review/continuous_{LANG}{SUFFIX}_sheet_{i+1:02}.jpg',quality=86,optimize=True)
 for i,f in enumerate([0,30,60,90]):
  with Image.open(paths[f]) as im:im.save(ROOT/f'review/opening_{LANG}{SUFFIX}_{i:02}.jpg',quality=91)
 for s in shots:
  if s['key'] in ['D_album','D_1678','D_cut','D_1797']:
   for i,e in enumerate(s['stages']):
    f=e['start_frame']+(e['frames']-1)//2
    with Image.open(paths[f]) as im:im.save(ROOT/f'review/stage_{LANG}{SUFFIX}_{s["key"]}_{i}.jpg',quality=93)
 assert abs(m['brand_intervals']['endcard'][0]-(m['duration_seconds']-10))<1e-7
 save(ROOT/f'records/continuous_qc{SUFFIX}.json',dict(passed=True,video_sha256=sha(src),decoded_frames=n,decoded_format=[1920*S,1080*S,'yuv420p'],decode_warnings=0,exact_30fps_pts=True,profile=v['profile'],selected_frames=frames,no_seeking=True,checks=checks,endcard_exact_last_10_seconds=True))
 print('CONTINUOUS',LANG,S,n,len(frames),flush=True)
def layout():
 rows=read(ROOT/f'records/frame_layout{SUFFIX}.json');sc=read(ROOT/f'records/art_scales{SUFFIX}.json');shots=read(ROOT/f'records/render_shots{SUFFIX}.json')
 def lum(col):
  x=np.array(ImageColor.getrgb(col))/255;x=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4);return float(x@np.array([.2126,.7152,.0722]))
 checks=[]
 for r in rows:
  if r['card'] not in ['D_album','D_1678','D_1797']:continue
  bg='#412f25' if r['box'][1]>=915 else '#f8f1dc' if r.get('plate_padding') is not None or r['box'][1]>=147 else '#e9ddc4';a,b=lum(r['foreground']),lum(bg);ratio=(max(a,b)+.05)/(min(a,b)+.05)
  checks.append(dict(r,background=bg,contrast=ratio));assert ratio>=4.5,(r,ratio)
  if r['major']:assert r['ink_height']>=60
  if 'plate_padding' in r:assert r['plate_padding']>=35,r
 used={s['key']:sum(x['key']==s['key'] for x in shots) for s in shots};assert all(v==1 for v in used.values())
 assert sum(k.startswith('V01_full') for k in used)==2 and all(used[f'V01_D{i}']==1 for i in range(1,8))
 assert all(a['minimum_native_crop_width']>=3840 and a['max_native_scale']<=1 for a in sc.values() if 'max_zoom' in a)
 request=(REPO/'new-channel/wom13_制作依頼_20261106.md').read_text()
 from wom13_scenes import ALBUM,HOOG
 for phrase in ALBUM+[p for s in HOOG for p in s]:assert phrase in request,phrase
 for s in shots:
  for e in s.get('stages',[]):
   if s['segment_id']=='P06':assert e['year']=='—'
 save(ROOT/f'records/layout_qc{SUFFIX}.json',dict(passed=True,quotation_text_exact=True,major_ink_min=min(r['ink_height'] for r in checks if r['major']),smallest_body_ink=min(r['ink_height'] for r in checks if 'plate_padding' in r),smallest_label_ink=min(r['ink_height'] for r in checks),contrast_min=min(r['contrast'] for r in checks),plate_padding_min=min(r['plate_padding'] for r in checks if 'plate_padding' in r),minimum_native_crop_width=min(a['minimum_native_crop_width'] for a in sc.values() if 'max_zoom' in a),usage=used,rows=checks))
 print('LAYOUT',LANG,S,'passed',flush=True)
if __name__=='__main__':globals()[sys.argv[1]]()
