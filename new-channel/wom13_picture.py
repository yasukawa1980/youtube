"""EP013 independent logical shots -> independent decoders -> single AVC encoder."""
import sys,subprocess,json,os,math
from pathlib import Path
from PIL import Image
from wom13_produce import ROOT,OP,END,read,save,sha,ff,probe
from wom13_scenes import *
LANG=os.environ.get('WOM13_LANG','en');SUFFIX='_4k' if S==2 else ''
R=ROOT/('_work/render'+SUFFIX);R.mkdir(parents=True,exist_ok=True)
def phrase(p,en,ja,segments,subs,events):
 target=en if LANG=='en' else ja;clean=lambda t:re.sub(r'\s+','',t.lower());c=next(c for c in segments[p]['cues'] if clean(target) in clean(c['text']));offset=clean(c['text']).index(clean(target))
 for page in [q for q in subs if q['sentence_id']==c['id']]:
  n=len(clean(page['text']))
  if offset<n:
   f=round(30*(page['start']+offset/n*(page['end']-page['start'])));events.append(dict(segment=p,word=target,cue=c['id'],subtitle=page['text'],frame=f,time=f/30,method='native sentence/subtitle page plus character-offset interpolation'));return f
  offset-=n
 raise ValueError(target)
def camera(k,count):
 a=ARTMEAS[k];px=a['pasted_box'];x,y,x1,y1=[round(v*S) for v in px];w,h=x1-x,y1-y;t=f'on/{max(1,count-1)}';amount=.025;direction='zoom_in'
 if k=='V01_full_1':amount=.10
 if k=='V01_full_2':amount=.10;direction='zoom_out'
 if k=='V06':amount=.025;direction='right'
 if k in ['V01_D2','V01_D3','V01_D4']:amount=.020
 if k=='V01_D5':amount=.020;direction='down'
 if k=='V01_D6':amount=.035
 if k=='V01_D7':amount=.008
 if k=='V02_L':amount=.004
 z=f'(1+{amount}*{t})';xx=f'(W-W/{z})*.5';yy=f'(H-H/{z})*.5'
 if direction=='zoom_out':z=f'(1+{amount}*(1-{t}))';xx=f'(W-W/{z})*.54';yy=f'(H-H/{z})*.58'
 if k=='V01_full_1':xx=f'(W-W/{z})*.54';yy=f'(H-H/{z})*.58'
 if direction in ['down','right']:
  z=f'(1+{amount})';xx=f'(W-W/{z})*'+(t if direction=='right' else '.5');yy=f'(H-H/{z})*'+(t if direction=='down' else '.5')
 p=f"perspective=x0='{xx}':y0='{yy}':x1='{xx}+W/{z}':y1='{yy}':x2='{xx}':y2='{yy}+H/{z}':x3='{xx}+W/{z}':y3='{yy}+H/{z}':sense=source:eval=frame:interpolation=cubic"
 a.update(max_zoom=1+amount,motion=direction,minimum_native_crop_width=a['art_size'][0]/(1+amount),max_native_scale=a['native_output_scale']*(1+amount))
 assert a['minimum_native_crop_width']>=3840 and a['max_native_scale']<=1,(k,a)
 l,top,r,b=a['crop_native_px'];cw,ch=r-l,b-top
 def bounds(u):
  zz=1+amount*(1-u if direction=='zoom_out' else 1 if direction in ['down','right'] else u);ax=u if direction=='right' else .54 if 'full' in k else .5;ay=u if direction=='down' else .58 if 'full' in k else .5
  left=l+(cw-cw/zz)*ax;up=top+(ch-ch/zz)*ay;return [left,up,left+cw/zz,up+ch/zz]
 a['motion_start_native_box']=bounds(0);a['motion_end_native_box']=bounds(1)
 return f'[0:v]fps=30,format=yuv444p,split[base][art];[art]crop={w}:{h}:{x}:{y}:exact=1,{p}[moving];[base][moving]overlay={x}:{y}:format=yuv444'+(',format=yuv444p[pre];[pre][1:v]overlay=format=yuv444,format=yuv420p[v]' if 'full' in k else ',format=yuv420p[v]')
def run():
 master=read(ROOT/'records/master_timeline.json');seg={x['id']:x for x in master['segments']};subs=read(ROOT/f'records/subtitle_cues_{LANG}.json')['cues'];events=[];shots=[]
 def st(p):return 0 if p=='P01' else round(seg[p]['start']*30)
 def ed(p):return round(seg[p]['end']*30)
 def at(p,en,ja):return phrase(p,en,ja,seg,subs,events)
 tick1797=at('P09','seventeen ninety-seven','1797年')
 def yr(p,f):
  if p in ['P03','P04','P05']:return '1642'
  return {'P06':'—','P07':'1678','P08':'1715','P09':'1797' if f>=tick1797 else '—','P10':'1946–47','P11':'today'}.get(p)
 def shot(p,k,start,end,changes=[]):
  assert end>start,(k,start,end);points=sorted(set([start,end]+[f for f,s in changes if start<f<end]+([tick1797] if start<tick1797<end else [])));entries=[]
  for i,(a,b) in enumerate(zip(points,points[1:])):
   stage=next((s for f,s in reversed(changes) if f<=a),0);im=scene(k,stage,yr(p,a));path=R/f'{k}_{i:02}.png';im.save(path,compress_level=2)
   entries.append(dict(start_frame=a,frames=b-a,file=str(path.relative_to(ROOT)),stage=stage,year=yr(p,a)))
  shots.append(dict(key=k,segment_id=p,start=start/30,end=end/30,frames=end-start,file=entries[0]['file'],stages=entries))
 def cut(p,keys,cuts):
  pts=[st(p)]+cuts+[ed(p)]
  for k,a,b in zip(keys,pts,pts[1:]):shot(p,k,a,b)
 def brand(k,path):
  a,b=master['brand_intervals'][k];shots.append(dict(key=k,segment_id='BRAND',start=a,end=b,frames=round((b-a)*30),encoded_file=str(path)))
 shot('P01','V01_full_1',0,ed('P01'))
 intro=[(round(st('P02')+(ed('P02')-st('P02')-30)*i/6),i) for i in range(6)]+[(ed('P02')-30+i,6+i) for i in range(30)]
 shot('P02','D_timeline_intro',st('P02'),ed('P02'),intro);brand('opening',OP)
 cut('P03',['V05','V06'],[at('P03','Paintings like this','こうした絵は')])
 cut('P04',['V01_D1','V01_D2','V01_D3','V01_D4'],[at('P04','Around them','そのまわりでは'),at('P04','raise a flag','旗を掲げ'),at('P04','beat a drum','太鼓を打って')])
 cut('P05',['V01_D5'],[])
 shot('P06','D_album',st('P06'),ed('P06'),[(at('P06','march','行進させる'),1)])
 shot('P07','D_1678',st('P07'),ed('P07'),[(at('P07','And he added','そして、もっと光を'),1)])
 a=at('P08','Around that time','そのころ');b=at('P08','We know what they looked like','彼らの姿が分かるのは');flash=at('P08','two men and a child disappeared','男性2人と子ども1人の姿が消えました')
 shot('P08','V07',st('P08'),a);shot('P08','D_cut',a,b,[(flash,1),(min(b-1,flash+60),0)]);shot('P08','V02_L',b,ed('P08'))
 cut('P09',['V08','D_1797'],[at('P09','According to the museum','美術館によると')])
 cut('P10',['V01_D6'],[]);cut('P11',['V01_D7'],[]);shot('P12','V01_full_2',st('P12'),ed('P13'));cut('P14',['credits'],[]);brand('endcard',END)
 assert sum(s['frames'] for s in shots)==round(master['duration_seconds']*30)
 assert all(round(a['end']*30)==round(b['start']*30) for a,b in zip(shots,shots[1:]))
 for k in ['V01_full_1','V01_full_2']:
  overlay=Image.new('RGBA',(W,H),(0,0,0,0));sidebar(overlay,k);overlay.save(R/(k+'_overlay.png'))
 for s in shots:
  k=s['key']
  if s['segment_id']=='BRAND':continue
  out=R/(k+'.mp4');entries=s['stages'];lst=R/(k+'.ffconcat');lines=['ffconcat version 1.0']
  for e in entries:lines += ["file '"+str(ROOT/e['file'])+"'",'option framerate 30',f"duration {e['frames']/30:.9f}"]
  lines += ["file '"+str(ROOT/entries[-1]['file'])+"'",'option framerate 30'];lst.write_text('\n'.join(lines)+'\n')
  moving=k in ARTMEAS and k!='D_cut';f=camera(k,s['frames']) if moving else '[0:v]fps=30,format=yuv420p[v]';args=['-f','concat','-safe',0,'-i',lst]
  if 'full' in k:args+=['-i',R/(k+'_overlay.png')]
  cfg=dict(stages=[(sha(ROOT/e['file']),e['frames']) for e in entries],filter=f,scale=S,overlay=sha(R/(k+'_overlay.png')) if 'full' in k else None);stamp=out.with_suffix('.json')
  if 'design' not in sys.argv:
   if not(out.exists() and stamp.exists() and read(stamp)==json.loads(json.dumps(cfg))):
    ff([*args,'-filter_complex_threads',2,'-filter_complex',f,'-map','[v]','-an','-frames:v',s['frames'],'-c:v','libx264','-preset','veryfast','-threads',3,'-crf',15,'-profile:v','high','-pix_fmt','yuv420p','-video_track_timescale',15360,out]);save(stamp,cfg)
   assert int(next(x for x in probe(out)['streams'] if x['codec_type']=='video')['nb_frames'])==s['frames']
  s['encoded_file']=str(out.relative_to(ROOT));s['moving']=moving;print('SHOT',LANG,S,k,s['frames'],flush=True)
 save(ROOT/f'records/render_shots{SUFFIX}.json',shots);save(ROOT/f'records/art_scales{SUFFIX}.json',ARTMEAS);save(ROOT/f'records/frame_layout{SUFFIX}.json',METR);save(ROOT/f'records/rail_switches{SUFFIX}.json',dict(events=events,rail_by_stage=[dict(key=s['key'],stages=[dict(frame=e['start_frame'],year=e['year']) for e in s.get('stages',[])]) for s in shots]))
 if 'design' in sys.argv:return
 out=ROOT/f'_work/picture_master{SUFFIX}.mp4';cmd=['ffmpeg','-y','-nostdin','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-g','60','-bf','2','-video_track_timescale','15360','-movie_timescale','48000','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-movflags','+faststart',str(out)]
 with (ROOT/f'records/encode{SUFFIX}.log').open('w') as log:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for s in shots:
    args=['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(ROOT/s['encoded_file']),'-map','0:v:0','-an']
    if s['segment_id']=='BRAND' and S==2:args+=['-vf',f'scale={W}:{H}:flags=lanczos']
    subprocess.run([*args,'-frames:v',str(s['frames']),'-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
   enc.stdin.close();assert enc.wait()==0
  except BaseException:enc.kill();enc.wait();raise
 save(ROOT/f'records/encoding_method{SUFFIX}.json',dict(method='independent shot decoders, including opening/endcard, through one raw yuv420p pipe into one AVC encoder',command=cmd,scale=S,painting_images='native verified source pixels resized directly to output plates',common_brand_4k='1080p source scaled with Lanczos' if S==2 else None))
 print('PICTURE MASTER',LANG,W,H,flush=True)
if __name__=='__main__':run()
