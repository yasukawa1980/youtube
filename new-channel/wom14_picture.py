"""Finite per-shot rendering; individual decoders feed one continuous AVC encoder.
Resumes each shot only when its exact plate hashes, frame counts and filter match.
"""
import sys,os,re,subprocess,json
from pathlib import Path
from PIL import Image
from wom14_produce import ROOT,OP,END,read,save,sha,ff,probe
import wom14_scenes as v
S=v.S;W=v.W;H=v.H;LANG=os.getenv('WOM14_LANG','en');SUFFIX='_4k' if S==2 else ''
R=ROOT/('_work/render'+SUFFIX);R.mkdir(parents=True,exist_ok=True)
def phrase(p,en,ja,seg,subs,events):
 target=en if LANG=='en' else ja;clean=lambda x:re.sub(r'\s+','',x.lower());c=next((c for c in seg[p]['cues'] if clean(target) in clean(c['text'])),None)
 assert c is not None,(p,target)
 offset=clean(c['text']).index(clean(target))
 for page in [q for q in subs if q['sentence_id']==c['id']]:
  n=len(clean(page['text']))
  if offset<n:
   f=round(30*(page['start']+offset/n*(page['end']-page['start'])));events.append(dict(segment=p,phrase=target,sentence_id=c['id'],subtitle=page['text'],frame=f,time=f/30,method='native sentence / subtitle page, character-offset interpolation'));return f
  offset-=n
 raise ValueError(target)
def design():
 m=read(ROOT/'records/master_timeline.json');seg={s['id']:s for s in m['segments']};subs=read(ROOT/f'records/subtitle_cues_{LANG}.json')['cues'];events=[];shots=[]
 st=lambda p:0 if p=='P01' else round(seg[p]['start']*30);ed=lambda p:round(seg[p]['end']*30)
 at=lambda p,e,j:phrase(p,e,j,seg,subs,events)
 def shot(p,k,a,b,changes=None,zoom_at=None,highlight2=None):
  assert b>a,(p,k,a,b)
  entries=[]
  def append(f,im,kind,detail):
   path=R/f'{k}_{len(entries):03}.png';im.save(path,compress_level=2);entries.append(dict(start_frame=f,file=str(path.relative_to(ROOT)),kind=kind,detail=detail))
  if k.startswith('D_') or k=='credits':
   changes=changes or [(a,0)]
   if changes[0][0]>a:changes=[(a,0)]+changes
   for f,stage in changes:
    if not a<=f<b:continue
    if k in ['D_check_1','D_check_2','D_check_3','D_check_4'] and stage==1:
     for j in range(min(8,b-f)):
      # 8 frames = .267s: nearest CFR representation of the requested .25s.
      append(f+j,v.card(k,1,1.10-.10*j/7),'stamp',dict(stage=1,animation_frame=j))
    else:append(f,v.card(k,stage),'card',dict(stage=stage))
  elif k in v.BOXES:
   safe=v.SAFE.get(k,(0,0,1,1));focus=v.FOCUS[k];z=min(b-2,max(a+60,zoom_at or a+60))
   append(a,v.art_scene(k,safe),'source_overview',dict(crop=safe))
   # Smooth, finite source-coordinate zoom. Every plate uses native pixels directly.
   dur=min(18,b-z-1)
   if k=='O11-12':dur=0
   for j in range(1,dur+1):
    u=j/dur;u=u*u*(3-2*u);crop=tuple(s+(t-s)*u for s,t in zip(safe,focus));append(z+j-1,v.art_scene(k,crop),'source_zoom',dict(crop=crop))
   f=z+dur;append(f,v.art_scene(k,focus,0),'source_focus',dict(crop=focus,highlight=0))
   if highlight2:
    q=max(f+1,min(b-1,highlight2));crop=(.13,.82,.65,.90) if k=='O04-272' else focus
    append(q,v.art_scene(k,crop,1),'source_focus',dict(crop=crop,highlight=1))
  else:
   crop=v.FOCUS.get(k,(0,0,1,1)) if k in ['O01-A','O01-C','O10-A','O14-B','O02-D'] else (0,0,1,1)
   append(a,v.art_scene(k,crop),'art',dict(crop=crop))
  entries=sorted(entries,key=lambda x:x['start_frame']);assert len(set(e['start_frame'] for e in entries))==len(entries),(k,entries)
  for e,nxt in zip(entries,entries[1:]+[{'start_frame':b}]):e['frames']=nxt['start_frame']-e['start_frame'];assert e['frames']>0
  shots.append(dict(key=k,segment_id=p,start=a/30,end=b/30,frames=b-a,stages=entries,file=entries[0]['file']))
 def cut(p,keys,cuts):
  pts=[st(p)]+cuts+[ed(p)]
  for k,a,b in zip(keys,pts,pts[1:]):shot(p,k,a,b)
 def brand(k,path):
  a,b=m['brand_intervals'][k];shots.append(dict(key=k,segment_id='BRAND',start=a,end=b,frames=round((b-a)*30),encoded_file=str(path),stages=[]))
 a=at('P01','Red or blue skin','赤や青の肌');b=at('P01','That is how oni appear today','いまの鬼は');shot('P01','O01-A',0,a)
 shot('P01','D_features',a,b,[(a,1),(at('P01','horns on its head','頭には角'),2),(at('P01','a loincloth','虎の皮の腰巻き'),3),(at('P01','an iron club','手には金棒'),4)])
 shot('P01','O02-A',b,ed('P01'))
 shot('P02','D_check_list',st('P02'),ed('P02'),[(st('P02'),0)]+[(at('P02',e,j),i+1) for i,(e,j) in enumerate([('That oni always','鬼は昔から'),('That the word oni','「おに」という'),('That the horns','角と虎の皮は'),('And that oni','鬼は追い払われる')])]);brand('opening',OP)
 cut('P03',['D_kanji_oni'],[])
 a=at('P04','Then, after the crown prince','そして、皇太子');b=at('P04','When W. G. Aston','1896年');shot('P04','O05-A',st('P04'),a);shot('P04','O03-23',a,b)
 shot('P04','O04-272',b,ed('P04'),highlight2=at('P04','added a note','注に'))
 a=at('P05','The parents hid','父と母は');shot('P05','O06-38',st('P05'),a,zoom_at=at('P05','A one-eyed oni','そこへ一つ目'));shot('P05','O15-A',a,ed('P05'))
 shot('P06','D_check_1',st('P06'),ed('P06'),[(st('P06'),0),(at('P06','Neither record','どちらの記録も'),1)])
 shot('P07','O08-31',st('P07'),ed('P07'),zoom_at=at('P07','Some say','ある説では'),highlight2=at('P07','The entry ends','この項は'))
 a=at('P08','In the Tales of Ise','10世紀ごろ');shot('P08','D_check_2',st('P08'),a,[(st('P08'),0),(at('P08','It is an early guess','確かめられた語源'),1)]);shot('P08','O09-A',a,ed('P08'))
 cut('P09',['O10-A','O14-B'],[at('P09','Over the following centuries','それからの何百年')])
 a=at('P10','People call the northeast','世の人は');shot('P10','O11-12',st('P10'),a,highlight2=max(st('P10')+80,a-45));shot('P10','D_compass',a,ed('P10'))
 shot('P11','D_check_3',st('P11'),ed('P11'),[(st('P11'),0),(at('P11','Whether the picture','資料は'),1)])
 a=at('P12','In a later court manual','およそ900年前');b=at('P12','Beans came later','豆は');c=at('P12','In fourteen forty-seven','1447年')
 shot('P12','R10-27',st('P12'),a);shot('P12','R11-30',a,b,highlight2=at('P12','shoot arrows at the','殿上人が'));shot('P12','O02-B',b,c);shot('P12','R12-1447',c,ed('P12'),highlight2=at('P12','and called it','これがこの国'))
 a=at('P13','And by the fifteenth','そして15世紀');shot('P13','O02-D',st('P13'),a);shot('P13','D_check_4',a,ed('P13'),[(a,1)])
 a=at('P14','The oldest records show','最も古い記録が');assert a-st('P14')>=45;shot('P14','D_check_all',st('P14'),a);shot('P14','O01-C',a,ed('P14'))
 cut('P15',['O16-A'],[]);cut('P16',['credits'],[]);brand('endcard',END)
 assert sum(s['frames'] for s in shots)==round(m['duration_seconds']*30)
 assert all(round(a['end']*30)==round(b['start']*30) for a,b in zip(shots,shots[1:]))
 return m,events,shots

def camera(s):
 k=s['key'];a=next(a for a in reversed(v.ARTMEAS) if a['key']==k);x,y,x1,y1=[round(q*S) for q in a['output_box']];w=x1-x;h=y1-y;t=f'on/{max(1,s["frames"]-1)}';amount=.10 if k=='O01-A' else .025
 if k=='O05-A':
  # Translate native-scale art smoothly inside a paper margin; no zoom or recrop.
  pad=20*S;x-=pad;w+=2*pad
  drift=f'({8*S}-{16*S}*{t})'
  p=f"perspective=x0='{drift}':y0=0:x1='W+{drift}':y1=0:x2='{drift}':y2=H:x3='W+{drift}':y3=H:sense=source:eval=frame:interpolation=cubic"
  a['max_native_scale']=a['native_scale'];a['motion']='horizontal_pan_without_zoom';a['zoom_factor']=1
  return f'[0:v]fps=30,format=yuv444p,split[base][art];[art]crop={w}:{h}:{x}:{y}:exact=1,{p}[moving];[base][moving]overlay={x}:{y}:format=yuv444,format=yuv420p[v]',True
 if a['native_scale']*(1+amount)>1:amount=max(0,1/a['native_scale']-1)
 if amount<.001:return '[0:v]fps=30,format=yuv420p[v]',False
 z=f'(1+{amount}*'+(f'(1-{t})' if k=='O01-A' else t)+')';xx=f'(W-W/{z})/2';yy=f'(H-H/{z})/2'
 p=f"perspective=x0='{xx}':y0='{yy}':x1='{xx}+W/{z}':y1='{yy}':x2='{xx}':y2='{yy}+H/{z}':x3='{xx}+W/{z}':y3='{yy}+H/{z}':sense=source:eval=frame:interpolation=cubic"
 a['max_native_scale']=a['native_scale']*(1+amount);a['motion']='zoom_out' if k=='O01-A' else 'zoom_in';a['zoom_factor']=1+amount
 return f'[0:v]fps=30,format=yuv444p,split[base][art];[art]crop={w}:{h}:{x}:{y}:exact=1,{p}[moving];[base][moving]overlay={x}:{y}:format=yuv444,format=yuv420p[v]',True

def run():
 config=dict(timeline=sha(ROOT/'records/master_timeline.json'),picture=sha(Path(__file__)),scenes=sha(Path(__file__).with_name('wom14_scenes.py')),scale=S,language=LANG)
 state=R/'design_state.json';cached=read(state) if state.exists() else {}
 if cached.get('config')==config and all((ROOT/e['file']).exists() for s in cached['shots'] for e in s['stages']):
  m=cached['master'];events=cached['events'];shots=cached['shots'];v.ARTMEAS.extend(cached['art']);v.METR.extend(cached['metrics'])
 else:m,events,shots=design();save(state,dict(config=config,master=m,events=events,shots=shots,art=v.ARTMEAS,metrics=v.METR))
 v.original.cache_clear()
 for s in shots:
  k=s['key']
  if s['segment_id']=='BRAND':continue
  entries=s['stages'];lst=R/(k+'.ffconcat');lines=['ffconcat version 1.0']
  for e in entries:lines += ["file '"+str(ROOT/e['file'])+"'",'option framerate 30',f"duration {e['frames']/30:.9f}"]
  lines += ["file '"+str(ROOT/entries[-1]['file'])+"'",'option framerate 30'];lst.write_text('\n'.join(lines)+'\n')
  filt,moving=camera(s) if entries[0]['kind']=='art' else ('[0:v]fps=30,format=yuv420p[v]',False)
  args=['-threads',1,'-f','concat','-safe',0,'-i',lst]
  if len(entries)==1:args=['-loop',1,'-framerate',30,'-threads',1,'-t',s['frames']/30,'-i',ROOT/entries[0]['file']]
  cfg=dict(stages=[(sha(ROOT/e['file']),e['frames']) for e in entries],filter=filt,scale=S,encoding='finite30fps-decoder1-filter2-encoder2-lookahead5')
  out=R/(k+'.mp4');stamp=out.with_suffix('.json')
  if 'design' not in sys.argv:
   if not(out.exists() and stamp.exists() and read(stamp)==json.loads(json.dumps(cfg))):
    ff([*args,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-an','-frames:v',s['frames'],'-c:v','libx264','-preset','veryfast','-threads',2,'-x264-params','rc-lookahead=5:sync-lookahead=0','-crf',16,'-profile:v','high','-pix_fmt','yuv420p','-video_track_timescale',15360,'-progress',R/(k+'_progress.txt'),out]);save(stamp,cfg)
   assert int(next(x for x in probe(out)['streams'] if x['codec_type']=='video')['nb_frames'])==s['frames']
  s.update(encoded_file=str(out.relative_to(ROOT)),moving=moving);print('SHOT',LANG,S,k,s['frames'],flush=True)
 save(ROOT/f'records/render_shots{SUFFIX}.json',shots);save(ROOT/f'records/art_scales{SUFFIX}.json',v.ARTMEAS);save(ROOT/f'records/frame_layout{SUFFIX}.json',v.METR);save(ROOT/f'records/phrase_events{SUFFIX}.json',events)
 if 'design' in sys.argv:return
 out=ROOT/f'_work/picture_master{SUFFIX}.mp4';record=ROOT/f'records/encoding_method{SUFFIX}.json';inputs=[dict(key=s['key'],sha256=sha(ROOT/s['encoded_file']),frames=s['frames']) for s in shots]
 previous=read(record) if record.exists() else {}
 if out.exists() and previous.get('inputs')==inputs and previous.get('master_sha256')==sha(out):return
 cmd=['ffmpeg','-y','-nostdin','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s',f'{W}x{H}','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-x264-params','rc-lookahead=5:sync-lookahead=0','-crf','17','-profile:v','high','-pix_fmt','yuv420p','-g','60','-bf','2','-video_track_timescale','15360','-movie_timescale','48000','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-movflags','+faststart','-progress',str(ROOT/f'_work/master{SUFFIX}_progress.txt'),str(out)]
 with (ROOT/f'records/encode{SUFFIX}.log').open('w') as log:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for s in shots:
    args=['ffmpeg','-nostdin','-v','error','-threads','1','-i',str(ROOT/s['encoded_file']),'-map','0:v:0','-an']
    if s['segment_id']=='BRAND' and S==2:args+=['-vf',f'scale={W}:{H}:flags=lanczos','-filter_threads','1']
    subprocess.run([*args,'-frames:v',str(s['frames']),'-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
   enc.stdin.close();assert enc.wait()==0
  except BaseException:enc.kill();enc.wait();raise
 save(record,dict(method='Independent decoders for each logical shot including OP/ED, raw yuv420p frames to one H.264 encoder',inputs=inputs,master_sha256=sha(out),command=cmd))
 print('MASTER',LANG,S,flush=True)
if __name__=='__main__':run()
