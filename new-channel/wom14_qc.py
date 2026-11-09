"""Continuous decode, per-shot evidence and measured EP014 layout checks."""
import os,re,math,json,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageColor
import numpy as np
from wom14_produce import ROOT,REPO,read,save,sha,probe
LANG=os.environ.get('WOM14_LANG','en');S=int(os.environ.get('WOM14_SCALE','1'));SUFFIX='_4k' if S==2 else '';SIZE='2160' if S==2 else '1080'
def continuous():
 shots=read(ROOT/f'records/render_shots{SUFFIX}.json');m=read(ROOT/'records/master_timeline.json');n=round(m['duration_seconds']*30);src=ROOT/f'deliverables/EP014_Oni_{LANG}_v01_{SIZE}p30.mp4'
 assert sum(s['frames'] for s in shots)==n
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
  if s['key'].startswith('D_check') or s['key'] in ['O03-23','O04-272','O06-38','O08-31','O11-12','R10-27','R11-30','R12-1447']:
   for i,e in enumerate(s['stages']):
    if e['kind'] in ['source_zoom','stamp']:continue
    f=e['start_frame']+(e['frames']-1)//2
    with Image.open(paths[f]) as im:im.save(ROOT/f'review/stage_{LANG}{SUFFIX}_{s["key"]}_{i}.jpg',quality=93)
 assert abs(m['brand_intervals']['endcard'][0]-(m['duration_seconds']-10))<1e-7
 save(ROOT/f'records/continuous_qc{SUFFIX}.json',dict(passed=True,video_sha256=sha(src),decoded_frames=n,decoded_format=[1920*S,1080*S,'yuv420p'],decode_warnings=0,exact_30fps_pts=True,profile=v['profile'],selected_frames=frames,no_seeking=True,checks=checks,endcard_exact_last_10_seconds=True))
 print('CONTINUOUS',LANG,S,n,len(frames),flush=True)
def layout():
 from wom14_scenes import CLAIMS,STAMPS,BOXES,SAFE
 rows=read(ROOT/f'records/frame_layout{SUFFIX}.json');sc=read(ROOT/f'records/art_scales{SUFFIX}.json');shots=read(ROOT/f'records/render_shots{SUFFIX}.json')
 def lum(col):
  x=np.array(ImageColor.getrgb(col))/255;x=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4);return float(x@np.array([.2126,.7152,.0722]))
 checks=[]
 for r in rows:
  if not r['card'].startswith('D_'):continue
  a,b=lum(r['foreground']),lum(r['background']);ratio=(max(a,b)+.05)/(min(a,b)+.05);assert ratio>=4.5,(r,ratio)
  if r['major']:assert r['ink_height'] >= (52 if r['card'].startswith('D_check') else 60)
  if 'padding' in r:assert r['padding']>=7,r
  checks.append(dict(r,contrast=ratio))
 usage={s['key']:sum(x['key']==s['key'] for x in shots) for s in shots};assert all(x==1 for x in usage.values())
 assert all(max(a['native_scale'],a.get('max_native_scale',0))<=1.000001 for a in sc)
 request=(REPO/'new-channel/wom14_制作依頼_20261109.md').read_text()
 for pair in CLAIMS+STAMPS:
  assert '｜'.join(pair) in request,pair
 for a in sc:
  if a['key']=='R11-30':assert a['crop_fraction'][0]>=SAFE['R11-30'][0] and a['crop_fraction'][2]<=SAFE['R11-30'][2] and a['crop_fraction'][1]>=SAFE['R11-30'][1]
  if a['key']=='O11-12':assert a['crop_fraction']==list(SAFE['O11-12'])
 assert len(BOXES['O06-38'][0])==1 and BOXES['O06-38'][0][0][0]<.62 and BOXES['O06-38'][0][0][2]>.68
 card_bottom=max(r['box'][3] for r in checks);assert card_bottom<=880
 save(ROOT/f'records/layout_qc{SUFFIX}.json',dict(passed=True,contrast_min=min(r['contrast'] for r in checks),padding_min=min(r['padding'] for r in checks if 'padding' in r),checklist_major_height=52,text_card_major_height_min=60,content_bottom=card_bottom,subtitle_zone_top=925,minimum_reserved_gap=925-card_bottom,usage=usage,source_excerpt_boxes=BOXES,safe_limits=SAFE,sekien_polygon_mask=[[.035,.17],[.395,.17],[.395,.385],[.30,.435],[.035,.435]],max_native_scale=max(max(a['native_scale'],a.get('max_native_scale',0)) for a in sc),rows=checks))
 print('LAYOUT',LANG,S,flush=True)
def motion():
 shots=read(ROOT/'records/render_shots.json');sc=read(ROOT/'records/art_scales.json');master=ROOT/'_work/picture_master.mp4';out=[]
 for s in shots:
  if not s.get('moving'):continue
  a=next(a for a in reversed(sc) if a['key']==s['key']);x0,y0,x1,y1=a['output_box'];ww=int((x1-x0)*.7)//2*2;hh=int((y1-y0)*.6)//2*2;x=round((x0+x1-ww)/2);y=round((y0+y1-hh)/2)
  cmd=['ffmpeg','-nostdin','-v','error','-threads','1','-ss',str(s['start']),'-i',str(master),'-frames:v',str(s['frames']),'-vf',f'format=gray,crop={ww}:{hh}:{x}:{y}:exact=1','-filter_threads','1','-pix_fmt','gray','-fps_mode','passthrough','-f','rawvideo','-'];pr=subprocess.Popen(cmd,stdout=subprocess.PIPE);prev=None;diff=[]
  for _ in range(s['frames']):
   b=pr.stdout.read(ww*hh);assert len(b)==ww*hh;cur=np.frombuffer(b,np.uint8).astype(np.int16)
   if prev is not None:diff.append(float(np.abs(cur-prev).mean()))
   prev=cur
  assert pr.wait()==0;median=float(np.median(diff));p95=float(np.percentile(diff,95));ratio=p95/median if median else (1 if not p95 else None)
  out.append(dict(shot=s['key'],roi=[x,y,ww,hh],adjacent_pairs=len(diff),median=median,p95=p95,ratio=ratio,passed=ratio is not None and ratio<=2.5));print('MOTION',s['key'],ratio,flush=True)
 save(ROOT/'records/final_video_motion.json',dict(passed=all(x['passed'] for x in out),checks=out,method='All adjacent final-master frames within moving art ROIs. Intentional source zooms, stamps, staged cards and brand transitions are separate designed events.'))
 assert all(x['passed'] for x in out),out
if __name__=='__main__':globals()[sys.argv[1]]()
