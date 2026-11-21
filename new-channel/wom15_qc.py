"""Decode and measure EP015 deliverables, source excerpts, board clearance and artwork motion."""
import re,sys,subprocess,math
import numpy as np
from PIL import Image, ImageDraw, ImageFont,ImageColor
import imageio_ffmpeg
from wom14_produce import probe,measure
from wom15_render import ROOT,read,save,sha,FF,run,Path,encoder
from wom15_art import ASSETS,BOXES
from wom15_boards import PAPER,INK,SOFT,VERMILION
from wom14_subcheck import STYLE
def subs(lang):
 import wom14_subcheck
 dst=ROOT/lang;wom14_subcheck.ROOT=dst;wom14_subcheck.LANGUAGES=[lang];wom14_subcheck.main()
 src=dst/f'deliverables/EP015_December25_{lang}_v01_1080p30.mp4'
 out=src.with_name(src.name.replace('_1080p30','_subtitled_review_1080p30'))
 vf=f"subtitles='{src.with_suffix('.srt')}':original_size=1920x1080:force_style='{STYLE}'"
 run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-nostdin','-v','error','-threads','2','-i',src,'-filter_threads','2','-vf',vf,'-c:v','libx264','-preset','veryfast','-threads','2','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-c:a','copy','-video_track_timescale','15360','-movie_timescale','48000','-movflags','+faststart',out])
 validate(out,1920,read(dst/'records/shot_plan.json')[-1]['end'])
 r=subprocess.run([*FF,'-v','warning','-xerror','-i',out,'-f','null','-'],capture_output=True,text=True,check=True)
 assert not r.stderr.strip(),r.stderr[-1000:]
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
def check(lang,s):
 dst=ROOT/lang;sf='_4k' if s==2 else '';shots=read(dst/f'records/render_shots{sf}.json')
 src=dst/f'deliverables/EP015_December25_{lang}_v01_{1080*s}p30.mp4';n=shots[-1]['end'];review=dst/'review';review.mkdir(exist_ok=True)
 v=validate(src,s*1920,n);assert shots[-1]['end']-shots[-1]['start']==300
 triples=[];wanted={0,30,60,90};stills=[];layout=[];scales=[];motion=[]
 subtop=read(dst/'records/subtitle_layout_validation.json')['minimum_top']*s
 for sh in shots:
  a,b=sh['start'],sh['end'];tri=[a,(a+b-1)//2,b-1];triples.append(tri);wanted.update(tri);k=sh['key']
  for st in sh.get('stages',[]):
   meta=read(Path(st['meta']));geo=meta['geometry']
   if geo:
    scale=geo['scale']*(1.1 if sh['motion']=='opening' else 1.025 if sh['motion']=='art' else 1);assert scale<=1.000001;scales.append(dict(key=k,scale=scale))
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
    for t in meta['text']:assert t['ink_box'][3]<subtop
 frames=sorted(wanted);folder=dst/('_work/check_frames'+sf);folder.mkdir(exist_ok=True)
 cmd=[*FF,'-v','level+info','-xerror','-i',src,'-an','-vf','showinfo=checksum=0,select='+balanced(frames)+',scale=1280:720','-fps_mode','passthrough','-threads:v','1','-q:v','2',folder/'%03d.jpg']
 r=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,check=True)
 assert not re.search(r'\[(warning|error|fatal)\]',r.stderr)
 rows=re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+).*?fmt:(\w+).*?\bs:(\d+x\d+)',r.stderr)
 assert len(rows)==n and all((int(i),int(pts),pix,size)==(j,j*512,'yuv420p',f'{1920*s}x{1080*s}') for j,(i,pts,pix,size) in enumerate(rows))
 def img(f):return Image.open(folder/f'{frames.index(f)+1:03}.jpg')
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
 for sh in shots:
  if not sh.get('motion'):continue
  x,y,w,h=(900,380,560,400) if sh['key']!='D01-A' else (580,490,820,400)
  w*=s;h*=s;x*=s;y*=s
  proc=subprocess.Popen([str(a) for a in [*FF,'-ss',sh['start']/30,'-i',src,'-an','-frames:v',sh['frames'],'-vf',f'crop={w}:{h}:{x}:{y},format=gray','-threads:v','1','-f','rawvideo','pipe:1']],stdout=subprocess.PIPE)
  diff=[];prev=None
  for _ in range(sh['frames']):
   data=proc.stdout.read(w*h);assert len(data)==w*h
   cur=np.frombuffer(data,np.uint8).astype(np.int16)
   if prev is not None:diff.append(float(np.abs(cur-prev).mean()))
   prev=cur
  assert proc.wait()==0
  med=float(np.median(diff));p95=float(np.percentile(diff,95))
  motion.append(dict(key=sh['key'],median=med,p95=p95,ratio=p95/med if med else (1 if p95==0 else None)))
 q=measure(src);assert abs(float(q['input_i'])+16)<.5 and float(q['input_tp'])<=-1
 silence=subprocess.run(['ffmpeg','-hide_banner','-i',str(src),'-vn','-af','silencedetect=noise=-60dB:d=1','-f','null','-'],capture_output=True,text=True,check=True).stderr
 assert 'silence_start' not in silence
 save(dst/f'records/technical_qc{sf}.json',dict(file=src.name,sha256=sha(src),decoded_frames=n,profile=v['profile'],pixel_format=v['pix_fmt'],fps=v['avg_frame_rate'],decode_warnings=0,endcard_seconds=10,loudness=q,silences_over_one_second=0,motion=motion,layout=layout,scales=scales))
 print('QC',lang,s,n,[(m['key'],m['ratio']) for m in motion],flush=True)
if __name__=='__main__':
 if sys.argv[1]=='subtitles':subs(sys.argv[2])
 else:check(sys.argv[2],int(sys.argv[3]))
