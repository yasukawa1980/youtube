"""Decode and measure EP016 deliverables, source excerpts, board clearance and artwork motion."""
import re,sys,subprocess,math
import numpy as np
from PIL import Image, ImageDraw, ImageFont,ImageColor
import imageio_ffmpeg
from wom14_produce import probe,measure
from wom16_render import ROOT,read,save,sha,FF,run,Path,assemble,cards_to_refresh
from wom16_art import ASSETS,BOXES
from wom15_boards import PAPER,INK,SOFT,VERMILION,RULE
from wom14_subcheck import STYLE
def subs(lang):
 from wom01_subtitles import to_srt
 dst=ROOT/lang
 cues=read(dst/f'records/subtitle_cues_{lang}.json')['cues']
 sr=dst/'_work/sub_bounds.srt'
 sr.write_text(to_srt([dict(text=c['text'],start=i,end=i+.99) for i,c in enumerate(cues)]))
 vf=f"subtitles='{sr}':original_size=1920x1080:force_style='{STYLE}'"
 cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-filter_threads','2','-threads','1','-f','lavfi','-i',f'color=c=0x00fa50:s=1920x1080:r=1:d={len(cues)}','-vf',vf,'-threads:v','1','-pix_fmt','rgb24','-f','rawvideo','-']
 rows=[]
 with subprocess.Popen(cmd,stdout=subprocess.PIPE) as proc:
  for i,c in enumerate(cues):
   a=np.frombuffer(proc.stdout.read(1920*1080*3),np.uint8).reshape(1080,1920,3)
   mask=np.abs(a.astype(np.int16)-a[0,0].astype(np.int16)).max(axis=2)>16
   yy,xx=np.where(mask);assert len(yy)
   rows.append(dict(cue=i+1,start=c['start'],end=c['end'],bbox=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)]))
  assert proc.wait()==0
 top=min(r['bbox'][1] for r in rows);assert top>905
 save(dst/'records/subtitle_layout_validation.json',dict(minimum_top=top,rows=rows,style=STYLE))
 src=dst/f'deliverables/EP016_Sirens_{lang}_v01_1080p30.mp4'
 out=src.with_name(src.name.replace('_1080p30','_subtitled_review_1080p30'))
 vf=f"subtitles='{src.with_suffix('.srt')}':original_size=1920x1080:force_style='{STYLE}'"
 run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-nostdin','-v','error','-threads','2','-i',src,'-filter_threads','2','-vf',vf,'-c:v','libx264','-preset','veryfast','-threads','2','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-c:a','copy','-video_track_timescale','15360','-movie_timescale','48000','-movflags','+faststart',out])
 validate(out,1920,read(dst/'records/shot_plan.json')[-1]['end'])
 r=subprocess.run([*FF,'-v','warning','-xerror','-i',out,'-f','null','-'],capture_output=True,text=True,check=True)
 assert not r.stderr.strip(),r.stderr[-1000:]
 review=dst/'review';review.mkdir(exist_ok=True)
 shots=read(dst/'records/shot_plan.json');timeline=read(dst/'records/master_timeline.json')
 for key in ('D_tl_all','credits'):
  cut=next(sh for sh in shots if sh['key']==key)
  cue=next(c for seg in timeline['segments'] for c in seg['cues'] if c['start']>=cut['start']/30 and c['end']<cut['end']/30)
  run([*FF,'-ss',(cue['start']+cue['end'])/2,'-i',out,'-frames:v','1','-vf','scale=1280:720','-threads:v','1','-q:v','2',review/f'subtitle_{lang}_{key}.jpg'])
 save(dst/'records/subtitled_review.json',dict(file=out.name,sha256=sha(out),continuous_decode_warnings=0))
def validate(src,w,n):
 v=next(x for x in probe(src)['streams'] if x['codec_type']=='video')
 assert (v['profile'],v['pix_fmt'],v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==('High','yuv420p',w,w*9//16,'30/1',n),v
 assert abs(float(probe(src)['format']['duration'])-n/30)<.002
 return v
def luminance(col):
 c=np.array(ImageColor.getrgb(col))/255
 return float(np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4)@np.array([.2126,.7152,.0722]))
def balanced(frames):
 if len(frames)==1:return f'eq(n\\,{frames[0]})'
 mid=len(frames)//2;return '('+balanced(frames[:mid])+'+'+balanced(frames[mid:])+')'
def silhouette_sheet(boardimg,path):
 sheet=Image.new('RGB',(800,142),PAPER)
 draw=ImageDraw.Draw(sheet)
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
 for n,(cx,label) in enumerate(zip([257,712,1183,1647],['VOICE','BIRD','FISH TAIL','WING AND TAIL'])):
  x=round(cx/1.5)-65
  tile=boardimg.crop((x,104,x+130,202))
  sheet.paste(tile,(n*200+35,5))
  draw.text((n*200+100,125),label,font=font,fill=INK,anchor='mm')
 sheet.save(path,quality=95)
def check(lang,s):
 dst=ROOT/lang;sf='_4k' if s==2 else '';shots=read(dst/f'records/render_shots{sf}.json')
 assert not cards_to_refresh(shots), 'Rebuild updated timeline cards before QC'
 src=dst/f'deliverables/EP016_Sirens_{lang}_v01_{1080*s}p30.mp4';n=shots[-1]['end'];review=dst/'review';review.mkdir(exist_ok=True)
 v=validate(src,s*1920,n);assert shots[-1]['end']-shots[-1]['start']==300
 triples=[];wanted={0,30,60,90};stills=[];layout=[];scales=[];motion=[];plate_checks=[]
 subtop=read(dst/'records/subtitle_layout_validation.json')['minimum_top']*s
 for sh in shots:
  a,b=sh['start'],sh['end'];tri=[a,(a+b-1)//2,b-1];triples.append(tri);wanted.update(tri);k=sh['key']
  for st in sh.get('stages',[]):
   meta=read(Path(st['meta']));geo=meta['geometry']
   if (k.startswith('D_tl_') or k=='credits'):
    plate_checks.append((k,st['frame'],st['file']));wanted.add(st['frame'])
   if geo:
    scale=geo['scale']*(1.1 if sh['motion']=='opening' else 1.05 if sh['motion']=='art' else 1);assert scale<=1.000001;scales.append(dict(key=k,scale=scale))
    if geo['output_box']:
     f=st['frame'];wanted.add(f);stills.append((k,f,geo['output_box']))
   if k.startswith('D_') or k=='credits':
    for row in meta['text']:
     fg=row['color'];bg=INK if fg==PAPER else PAPER
     lum=sorted([luminance(fg),luminance(bg)])
     ratio=(lum[1]+.05)/(lum[0]+.05);assert ratio>=4.5
     y=row['ink_box'][3]
     assert y<subtop,(k,y,subtop)
     layout.append(dict(key=k,frame=st['frame'],text=row['text'],ink_height=row['ink_box'][3]-row['ink_box'][1],gap=subtop-y,contrast=round(ratio,3),padding=row.get('padding')))
   elif geo:
    for t in meta['text']:
     y=t['ink_box'][3]; assert y<subtop
     layout.append(dict(key=k,frame=st['frame'],text=t['text'],gap=subtop-y,ink_height=t['ink_box'][3]-t['ink_box'][1],padding=t.get('padding'),contrast=None))
 frames=sorted(wanted);folder=dst/('_work/check_frames'+sf);folder.mkdir(exist_ok=True)
 cmd=[*FF,'-v','level+info','-xerror','-i',src,'-an','-vf','showinfo=checksum=0,select='+balanced(frames)+',scale=1280:720','-fps_mode','passthrough','-threads:v','1','-q:v','2',folder/'%03d.jpg']
 r=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,check=True)
 assert not re.search(r'\[(warning|error|fatal)\]',r.stderr)
 rows=re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+).*?fmt:(\w+).*?\bs:(\d+x\d+)',r.stderr)
 assert len(rows)==n and all((int(i),int(pts),pix,size)==(j,j*512,'yuv420p',f'{1920*s}x{1080*s}') for j,(i,pts,pix,size) in enumerate(rows))
 def img(f):return Image.open(folder/f'{frames.index(f)+1:03}.jpg')
 matches=[]
 for key,frame,path in plate_checks:
  with Image.open(path) as plate:
   reference=np.asarray(plate.resize((1280,720),Image.Resampling.LANCZOS),dtype=np.int16)
  with img(frame) as decoded:
   error=float(np.abs(reference-np.asarray(decoded,dtype=np.int16)).mean())
  assert error<5,(key,frame,error)
  matches.append(dict(key=key,frame=frame,mean_absolute_error=round(error,4)))
 save(dst/f'records/decoded_plates{sf}.json',matches)
 if s==2:
  # The native P06 page has symmetric paper margins to the nearest pixel.
  original=next(sh for sh in shots if sh['key']=='SR12-A')
  assert original['stages'][1]['frame']-original['start']==60
  pg=Image.open(ASSETS['SR12-A']['original']).convert('RGB')
  with Image.open(original['stages'][0]['file']) as plate:
   xx=(plate.width-pg.width)//2;yy=(plate.height-pg.height)//2
   mae=np.abs(np.asarray(pg,dtype=np.int16)-np.asarray(plate.crop((xx,yy,xx+pg.width,yy+pg.height)),dtype=np.int16)).mean()
   assert mae<4 and min(plate.getpixel((xx+50,yy-30)))>180
  save(dst/'records/native_P06_4k.json',dict(size=list(pg.size),x=xx,y=yy,frames=60,source_mean_absolute_error=float(mae),paper=PAPER))
 for j,f in enumerate([0,30,60,90]):img(f).save(review/f'opening_{lang}{sf}_{j}.jpg',quality=91)
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
 for ix in range(0,len(shots),5):
  group=shots[ix:ix+5];sheet=Image.new('RGB',(1280,274*len(group)),'#211f1a');d=ImageDraw.Draw(sheet)
  for j,sh in enumerate(group):
   for col,f in enumerate(triples[ix+j]):
    tile=img(f).resize((426,240),Image.Resampling.LANCZOS);sheet.paste(tile,(426*col,274*j+30))
    d.text((426*col+5,274*j+3),f"{sh['segment']}  {sh['key']}   f{f}",font=font,fill='white')
  sheet.save(review/f'continuous_{lang}{sf}_{ix//5+1:02}.jpg',quality=91)
 for ix in range(0,len(stills),5):
  group=stills[ix:ix+5];sheet=Image.new('RGB',(1120,225*len(group)),PAPER);d=ImageDraw.Draw(sheet)
  for j,(k,f,rect) in enumerate(group):
   im=img(f);box=[v/(1.5*s) for v in rect];x,y,r,b=box
   crop=im.crop((max(0,int(x)-16),max(0,int(y)-20),min(im.width,int(r)+16),min(im.height,int(b)+20)));crop.thumbnail((1100,185))
   sheet.paste(crop,(10,225*j+32));d.text((10,225*j+3),f'{k}  f{f}',fill=INK,font=font)
  sheet.save(review/f'source_lines_{lang}{sf}_{ix//5+1}.jpg',quality=95)
 credit=next(sh for sh in shots if sh['key']=='credits')
 if s==1:
  key=next(sh for sh in shots if sh['key']=='D_tl_all')
  boardimg=img((key['start']+key['end']-1)//2)
  silhouette_sheet(boardimg,review/f'silhouettes_{lang}.jpg')
 img((credit['start']+credit['end']-1)//2).save(review/f'credits_{lang}{sf}.jpg',quality=92)
 board=next(sh for sh in shots if sh['key']=='D_tl_all')
 midpoint=(board['start']+board['end'])//2
 raw=subprocess.check_output([str(a) for a in [*FF,'-ss',midpoint/30,'-i',src,
       '-an','-frames:v',1,'-threads:v',1,'-pix_fmt','rgb24','-f','rawvideo','pipe:1']])
 pixels=np.frombuffer(raw,np.uint8).reshape(1080*s,1920*s,3)
 def measured_color(region):
  return '#%02x%02x%02x'%tuple(np.median(region.reshape(-1,3),axis=0).astype(int))
 paper=measured_color(pixels[907*s:920*s,70*s:140*s])
 divider=measured_color(pixels[752*s:753*s,350*s:650*s])
 edge_ratio=(luminance(paper)+.05)/(luminance(divider)+.05)
 assert edge_ratio>=4.5,(paper,divider,edge_ratio)
 del pixels,raw
 for sh in shots:
  if not sh.get('motion'):continue
  x,y,w,h=(900,380,560,400) if sh['key']!='SR01-A' else (580,490,820,400)
  w*=s;h*=s;x*=s;y*=s
  proc=subprocess.Popen([str(a) for a in [*FF,'-ss',math.floor(sh['start']*1e6/30)/1e6,'-i',src,'-an','-frames:v',sh['frames'],'-vf',f'crop={w}:{h}:{x}:{y},format=gray','-threads:v','1','-fps_mode','passthrough','-f','rawvideo','pipe:1']],stdout=subprocess.PIPE)
  diff=[];prev=None
  for _ in range(sh['frames']):
   data=proc.stdout.read(w*h);assert len(data)==w*h
   cur=np.frombuffer(data,np.uint8).astype(np.int16)
   if prev is not None:diff.append(float(np.abs(cur-prev).mean()))
   prev=cur
  assert proc.wait()==0
  med=float(np.median(diff));p95=float(np.percentile(diff,95))
  assert any(x>0 for x in diff[-3:]),(sh['key'],'stationary camera tail')
  motion.append(dict(key=sh['key'],median=med,p95=p95,ratio=p95/med if med else None,
                     last_three_differences=diff[-3:]))
 audio_test=subprocess.run([*FF,'-v','info','-hide_banner','-i',str(src),'-vn','-af','loudnorm=I=-16:TP=-3:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
 import json
 q=json.loads(re.findall(r'\{\s*"input_i".*?\}',audio_test.stderr,re.S)[-1]);assert abs(float(q['input_i'])+16)<.5 and float(q['input_tp'])<=-1
 silence=subprocess.run([*FF,'-v','info','-hide_banner','-i',str(src),'-vn','-af','silencedetect=noise=-60dB:d=1','-f','null','-'],capture_output=True,text=True,check=True).stderr
 assert 'silence_start' not in silence
 save(dst/f'records/technical_qc{sf}.json',dict(file=src.name,sha256=sha(src),decoded_frames=n,profile=v['profile'],pixel_format=v['pix_fmt'],fps=v['avg_frame_rate'],decode_warnings=0,endcard_seconds=10,loudness=q,silences_over_one_second=0,motion=motion,layout=layout,scales=scales,decoded_board_colors=dict(frame=midpoint,paper=paper,divider=divider,contrast=edge_ratio)))
 print('QC',lang,s,n,[(m['key'],m['ratio']) for m in motion],flush=True)
if __name__=='__main__':
 lang=sys.argv[2];s=int(sys.argv[3]) if len(sys.argv)>3 else 1
 if sys.argv[1]=='subtitles':subs(lang)
 else:check(lang,s)
