import os
"""Render logical shots independently; join decoded raw frames through one AVC encoder."""
import sys,subprocess,math,json,shutil
from PIL import Image,ImageDraw
from wom12_produce import ROOT,OP,END,read,save,sha,ff,probe
from wom12_scenes import *
from wom12_render import camera
FPS=30
R=ROOT/'_work/render'; R.mkdir(exist_ok=True,parents=True)
def run():
 lang=os.environ.get('WOM12_LANG','en')
 t=read(ROOT/'records/master_timeline.json'); en={x['id']:x for x in read(ROOT/f'records/narration_timeline_{lang}.json')['segments']};subs=read(ROOT/f'records/subtitle_cues_{lang}.json')['cues']; segments={x['id']:x for x in t['segments']}; clock=[]; shots=[]; slide_rows=[];ticks=[]
 def phrase(p,word):
  if 'WOM12_LANG' in os.environ:
   from wom12_retime import phrase_frame
   return phrase_frame(lang,p,word,en,subs,clock)
  c=next(c for c in en[p]['cues'] if word.lower() in c['text'].lower()); ss=[x for x in subs if x['sentence_id']==c['id']];line=' '.join(c['text'].lower().split());target=line.index(word.lower());pos=0
  for page in ss:
   st=' '.join(page['text'].lower().split());e=pos+len(st)
   if target<e: f=round((page['start']+(page['end']-page['start'])*max(0,target-pos)/len(st))*30);break
   pos=e+1
  else:f=round(c['start']*30)
  clock.append(dict(segment=p,word=word,cue=c['id'],reference='English master subtitle page + within-page character interpolation',frame=f,time=f/30));return f
 def st(p):return round(segments[p]['start']*30) if p!='P01' else 0
 def ed(p):return round(segments[p]['end']*30)
 for p,word,year in [('P03','fourth century','4th c.'),('P04','ten eighty-seven','1087'),('P05','eighteen twelve','1812'),('P06','eighteen twenty-one','1821'),('P07','eighteen twenty-three','1823'),('P08','eighteen fifty-eight','1858'),('P08','eighteen sixty-three','1863'),('P08','eighteen eighty-one','1881'),('P09','eighteen sixty-four','1864'),('P09','nineteen oh two','1902'),('P09','nineteen oh four','1904'),('P10','nineteen thirty-one','1931')]:ticks.append((phrase(p,word),year))
 def shot(p,k,start,end,extra=[]):
  assert end>start,(p,k,start,end);ev=sorted(set([start,end]+[f for f,y in ticks if start<f<end]+[f for f,z in extra if start<f<end]+([ed('P12')] if k=='N12-A' else [])));frames=[]
  for i,(a,b) in enumerate(zip(ev,ev[1:])):
   if b<=a:continue
   stage=next((z for f,z in reversed(extra) if f<=a),0);yr=None if not(st('P03')<=a<ed('P12')) else next((n for f,n in reversed(ticks) if f<=a),'—');im=scene(k,stage,yr,a>=ticks[-1][0]);path=R/f'{p}_{k}_{i:02}.png';im.save(path,compress_level=2);frames.append(dict(f=a,n=b-a,p=path,yr=yr,stage=stage))
  shots.append(dict(key=k,segment_id=p,start=start/30,end=end/30,frames=end-start,file=str(frames[0]['p'].relative_to(ROOT)),stages=[dict(start_frame=v['f'],frames=v['n'],year=v['yr'],stage=v['stage'],file=str(v['p'].relative_to(ROOT))) for v in frames],source=CAT[k][1] if k in CAT else k))
 def cut(p,keys,starts):
  if p=='P09' and 'WOM12_LANG' in os.environ and starts[2]-starts[1]<60:starts[1]=starts[2]-75
  points=[st(p)]+starts+[ed(p)]
  for k,a,b in zip(keys,points,points[1:]):shot(p,k,a,b)
 cut('P01',['N03-A','D_1931q'],[phrase('P01','many people believe')]);p='P02';shot(p,'D_timeline_intro',st(p),ed(p),[(round(st(p)+(ed(p)-st(p)-40)*i/11),i) for i in range(12)]+[(ed(p)-30+i,12+i) for i in range(30)])
 def brand(k,path):
  a,b=t['brand_intervals'][k];shots.append(dict(key=k,segment_id='BRAND',start=a,end=b,frames=round((b-a)*30),encoded_file=str(path),source='Quiet Origins common brand v02'))
 brand('opening',OP);cut('P03',['N05-A'],[]);cut('P04',['N06-A'],[]);shot('P05','D_1812',st('P05'),ed('P05'),[(phrase('P05','There is no sleigh here yet'),1)]);cut('P06',['N08_cover','N08_p1'],[phrase('P06','Its first page begins')]);shot('P07','D_1823',st('P07'),ed('P07'),[(st('P07'),-1)]+[(phrase('P07',w),i) for i,w in enumerate(['Its Saint Nicholas is chubby','He is dressed','He drives a miniature','His cheeks are like roses'])]);cut('P08',['N11-C','N02-A','D_1881'],[phrase('P08','Soon after'),phrase('P08','In eighteen eighty-one')]);cut('P09',['N04-A','N11-A','N11-B','N03-B','D_lineup2'],[phrase('P09','So his coat'),phrase('P09','But red kept'),phrase('P09','In December'),phrase('P09','decades before')]);cut('P10',['D_1931'],[]);cut('P11',['D_lineup3'],[]);shot('P12','N12-A',st('P12'),ed('P13'));cut('P14',['credits'],[]);brand('endcard',END)
 save(ROOT/'records/frame_layout.json',METR);save(ROOT/'records/rail_switches.json',dict(events=clock,ticks=ticks,subtitle_reference=lang+' subtitle page and character offset' if 'WOM12_LANG' in os.environ else 'English master; shared video for Japanese.'));save(ROOT/'records/art_scales.json',ARTMEAS);save(ROOT/'records/render_shots.json',shots)
 if 'design' in sys.argv:return
 for s in shots:
  if s['segment_id']=='BRAND':continue
  k=s['key'];out=R/f'{k}.mp4';entries=s['stages'];lst=R/f'{k}.ffconcat';lines=['ffconcat version 1.0']
  for e in entries:lines += ["file '"+str(ROOT/e['file'])+"'",'option framerate 30',f"duration {e['frames']/30:.9f}"]
  lines+= ["file '"+str(ROOT/entries[-1]['file'])+"'",'option framerate 30'];lst.write_text('\n'.join(lines)+'\n');amount=.042;direction=None
  if k=='N03-A':amount=.12;direction='face'
  if k=='N05-A':amount=.075;direction='scroll_down'
  if k=='N08_p1':amount=.7;direction='Yale'
  if k=='N02-A':amount=.85;direction='Nast'
  if k=='N12-A':amount=.035
  moving=k in CAT and k!='N11-A';band=ARTMEAS[k]['band'] if k in ARTMEAS else (110,810)
  if moving:
   f=camera(s['frames'],band,amount=amount,direction=direction).replace('[0:v]split','[0:v]fps=30,split');ARTMEAS[k]['end_scale_upper_bound']=ARTMEAS[k]['start_scale']*(1.10 if direction=='scroll_down' else 1+amount)
  else:f='[0:v]fps=30,format=yuv420p[v]'
  cfg={'stages':[(sha(ROOT/e['file']),e['frames']) for e in entries],'filter':f};stamp=out.with_suffix('.json');
  if not(out.exists() and stamp.exists() and json.loads(stamp.read_text())==json.loads(json.dumps(cfg))):
   ff(['-f','concat','-safe',0,'-i',lst,'-filter_complex_threads',2,'-filter_complex',f,'-map','[v]','-an','-frames:v',s['frames'],'-c:v','libx264','-preset','veryfast','-threads',3,'-profile:v','high','-pix_fmt','yuv420p','-crf',15,'-video_track_timescale',15360,out]);save(stamp,cfg)
  s['encoded_file']=str(out.relative_to(ROOT));assert int(next(x for x in probe(out)['streams'] if x['codec_type']=='video')['nb_frames'])==s['frames'];print('SHOT',k,s['frames'],flush=True)
 save(ROOT/'records/art_scales.json',ARTMEAS);save(ROOT/'records/render_shots.json',shots);assert sum(s['frames'] for s in shots)==round(t['duration_seconds']*30);assert len({s['key'] for s in shots})==len(shots)
 out=ROOT/'_work/picture_master.mp4';cmd=['ffmpeg','-y','-nostdin','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s','1920x1080','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-g','60','-bf','2','-video_track_timescale','15360','-movie_timescale','48000','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-movflags','+faststart',str(out)]
 with (ROOT/'records/encode.log').open('w') as log:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for s in shots:subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(ROOT/s['encoded_file']),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
   enc.stdin.close();assert enc.wait()==0
  except BaseException:enc.kill();enc.wait();raise
 save(ROOT/'records/encoding_method.json',dict(method='independent shot decoders through one uncompressed yuv420p pipe to one AVC encoder',shots=[s['key'] for s in shots],command=cmd))
if __name__=='__main__':run()
