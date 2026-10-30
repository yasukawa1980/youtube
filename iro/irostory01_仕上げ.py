#!/usr/bin/env python3
"""IRO小さな物語01 完成版。短い動作2本・窓の雨・生活音を仕上げる。

実行: bgm/.venv-audio-qc/bin/python iro/irostory01_仕上げ.py [audio|video|qc|all]
高解像度画像・音源・動画はBGM配下のみ。外部音源・音楽・音声生成APIなし。
"""
from pathlib import Path
import argparse, hashlib, json, math, subprocess, unicodedata
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.signal import butter, sosfilt
from scipy.io.wavfile import write as wavwrite

REPO = Path(__file__).resolve().parents[1]
BASE = Path('/Volumes/ESD-EPB/BGM/IRO/Stories/01_あと一ページのはずだった')
WORK, OUT, SRC = BASE/'_work/finish_v2', BASE/'投稿用', BASE/'開始画像'
W,H,FPS,SR,DURATION = 1920,1080,24,48000,90
MAIN = OUT/'irostory01_あと一ページのはずだった_完成v2.mp4'
MOTIONS = {3: BASE/'動作素材/dog_6s.mp4', 4: BASE/'動作素材/woman_6s.mp4'}
FILES = ['S1_reading.png','S2_awake.png','S3_waiting.png','S4_bookmark.png','S5_doorway.png','S6_walk.png']
# start/end seconds, source index, start/end crop width fraction, focus (x,y), caption
SHOTS = [
 (0,11,0,1,.975,(.5,.5),'雨の午後'),
 (11,18,0,.46,.445,(.235,.29),'窓の雨'),
 (18,25,0,.61,.585,(.735,.35),'あと一ページ'),
 (25,34,1,.63,.605,(.42,.64),'犬が目を覚ます'),
 (34,42,1,1,.98,(.5,.5),'目が合う'),
 (42,51,2,1,.975,(.5,.5),'玄関で待つ'),
 (51,56,2,.55,.535,(.27,.35),'リード'),
 (56,65,3,1,.97,(.5,.5),'本を閉じる'),
 (65,73,4,1,.98,(.5,.5),'行こう'),
 (73,84,5,.96,1,(.5,.5),'雨上がりの道'),
 (84,90,5,1,1,(.5,.5),'つづきは、帰ってから。'),
]

def run(args, **kw):
 return subprocess.run(list(map(str,args)),check=True,**kw)

def font(size, serif=False):
 needle='ヒラギノ明朝' if serif else 'ヒラギノ角ゴシック W3'
 p=next(p for p in Path('/System/Library/Fonts').iterdir() if needle in unicodedata.normalize('NFC',p.name))
 return ImageFont.truetype(str(p),size)

def sound():
 rng=np.random.default_rng(103001); n=SR*DURATION; t=np.arange(n)/SR
 mix=np.zeros((n,2),np.float32)
 # Rain heard from inside: broad, non-tonal, independent stereo detail.
 env=np.interp(t,[0,8,18,25,30,34,42,65,73,90],[.7,.75,.5,.15,.025,0,0,0,0,0])
 common=rng.normal(size=n).astype(np.float32)
 for ch in range(2):
  noise=.7*common+.7*rng.normal(size=n)
  bed=sosfilt(butter(2,[180,4000],btype='bandpass',fs=SR,output='sos'),noise)
  slow=1+.09*np.sin(2*np.pi*t/13+ch)+.05*np.sin(2*np.pi*t/7.7)
  mix[:,ch]=bed*.024*env*slow
 # Low outdoor air appears when the door opens, with no tonal drone.
 airenv=np.interp(t,[0,64.3,66,73,86,90],[0,0,.4,.6,.55,0])
 for ch in range(2):
  air=sosfilt(butter(2,[100,1100],btype='bandpass',fs=SR,output='sos'),rng.normal(size=n))
  mix[:,ch]+=air*.022*airenv
 events=[]
 def add(at,x,amp=1,pan=.5,kind=''):
  k=int(at*SR); m=min(len(x),n-k)
  if m<=0:return
  x=x[:m]*amp
  mix[k:k+m,0]+=x*np.sqrt(1-pan);mix[k:k+m,1]+=x*np.sqrt(pan)
  if kind:events.append({'time':round(at,3),'kind':kind})
 def noise(d,lo,hi):
  return sosfilt(butter(2,[lo,hi],btype='bandpass',fs=SR,output='sos'),rng.normal(size=int(d*SR)))
 # Tiny irregular drip impacts, with filtered noise rather than pitched notes.
 for at in np.sort(rng.uniform(.5,30,130)):
  d=.065; u=np.arange(int(d*SR))/SR
  drop=noise(d,600,5100)*np.exp(-u/.012)*(1-np.exp(-u/.0008))
  amp=.036*np.interp(at,[0,18,25,30],[1,.55,.16,0])*rng.uniform(.4,1)
  add(at,drop,amp,rng.uniform(.08,.92))
 # Page/fabric swishes: irregular envelopes prevent a synthetic sweep tone.
 for at,d,amp in [(18.15,.65,.025),(34.3,.45,.018),(55.5,.65,.026)]:
  u=np.linspace(0,1,int(d*SR)); x=noise(d,450,6500)*np.sin(np.pi*u)**1.7*(.7+.3*np.sin(u*39)**2)
  add(at,x,amp,.62,'紙／衣擦れ（合成）')
 # Dog's soft steps toward hallway, off-screen between shots.
 for at in [41.25,41.5,41.78]:
  u=np.arange(int(.13*SR))/SR
  add(at,noise(.13,100,1300)*np.exp(-u/.022),.042,.55,'犬の足音（合成・場面移行のみ）')
 # Book touching wood, gentle and dry.
 u=np.arange(int(.22*SR))/SR
 add(56.08,noise(.22,80,1800)*np.exp(-u/.035),.067,.6,'本を置く音（合成）')
 # Brief non-harmonic metal ticks from the leash clasp; not music.
 for at in [63.6,63.72,64.1]:
  u=np.arange(int(.16*SR))/SR
  x=sum(np.sin(2*np.pi*f*u)*np.exp(-u/tau) for f,tau in [(2173,.018),(3421,.027),(5987,.013)])
  add(at,x,.007,.55,'リードの金具（合成）')
 # Latch then a soft door movement, before the open-door image.
 u=np.arange(int(.12*SR))/SR
 add(64.65,noise(.12,250,3300)*np.exp(-u/.012),.043,.4,'ドアのラッチ（合成）')
 # Footfalls ease into the distance. No metronomic exact interval.
 at=72.6; step=0
 while at<74.4:
  d=.23;u=np.arange(int(d*SR))/SR
  x=noise(d,70,1800)*np.exp(-u/.035)+noise(d,1700,6200)*np.exp(-u/.055)*.22
  gain=.055*np.interp(at,[72.6,73.4,74.4],[1,.55,0])
  add(at,x,gain,.46+(.05 if step%2 else -.05),'濡れた道の足音（合成）')
  if step%2==0:add(at+.21,noise(.11,200,3000)*np.exp(-np.arange(int(.11*SR))/SR/.022),gain*.35,.64)
  at+=rng.uniform(.54,.72);step+=1
 fade=np.minimum(np.clip(t/1.2,0,1),np.clip((DURATION-t)/3,0,1))
 mix*=fade[:,None]
 # One whole-program gain; preserve relative dynamics. No peak clipping.
 peak=float(np.max(np.abs(mix)));mix*=.46/max(peak,1e-9)
 wavwrite(BASE/'音源/irostory01_生活音_仕上げv2.wav',SR,(mix*32767).astype(np.int16))
 (BASE/'音源/irostory01_音の配置_v2.json').write_text(json.dumps(events,ensure_ascii=False,indent=2))
 print('Audio complete; original synthesized Foley, no external recordings.',flush=True)

def title_layer(kind):
 im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im)
 if kind=='open':
  for y in range(345):
   d.line((0,y,1000,y),fill=(12,27,29,int(158*(1-y/345))))
  d.text((92,58),'IRO SOUNDS  /  小さな物語 01',font=font(25),fill=(235,221,194,255))
  d.text((88,112),'あと一ページ、',font=font(65,True),fill=(255,249,231,255),stroke_width=1)
  d.text((88,195),'のはずだった。',font=font(65,True),fill=(255,249,231,255),stroke_width=1)
 else:
  for y in range(780,H):d.line((0,y,W,y),fill=(8,22,25,int(185*(y-780)/(H-780))))
  d.text((W/2,920),'つづきは、帰ってから。',font=font(49,True),fill=(255,248,231,255),anchor='mm')
  d.text((W/2,996),'IRO SOUNDS  /  小さな物語',font=font(22),fill=(233,224,202,255),anchor='mm')
 return np.array(im)

def blend_layer(frame,layer,alpha):
 a=(layer[:,:,3:4].astype(np.float32)/255*alpha)
 return (frame*(1-a)+layer[:,:,:3]*a).astype(np.uint8)

def camera(src,s,t):
 a,b,idx,f0,f1,(cx,cy),_=s
 u=np.clip((t-a)/(b-a),0,1);u=u*u*(3-2*u)
 f=f0+(f1-f0)*u;ih,iw=src.shape[:2]
 cw=min(iw*f,ih*W/H);ch=cw*H/W
 x=np.clip(cx*iw-cw/2,0,iw-cw);y=np.clip(cy*ih-ch/2,0,ih-ch)
 matrix=np.array([[cw/W,0,x],[0,ch/H,y]],np.float32)
 return cv2.warpAffine(src,matrix,(W,H),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,borderMode=cv2.BORDER_REPLICATE)

class Rain:
 """Window-only original particle animation, in the 1672x941 source coordinates."""
 def __init__(self):
  mask=np.zeros((941,1672),np.uint8)
  panes=[[(25,20),(119,34),(121,253),(25,240)],
   [(151,40),(389,84),(390,278),(150,258)],
   [(151,282),(390,304),(390,502),(165,496)],
   [(438,0),(548,0),(598,92),(600,295),(438,280)],
   [(438,308),(597,321),(597,373),(552,403),(534,490),(438,501)]]
  for p in panes:cv2.fillPoly(mask,[np.array(p,np.int32)],255)
  self.mask=cv2.GaussianBlur(mask,(5,5),0).astype(np.float32)/255
  r=np.random.default_rng(103002)
  self.drops=[(r.uniform(-3,27),r.uniform(2,5),r.uniform(25,600),r.uniform(0,490),r.uniform(8,22),r.uniform(.65,1.3)) for _ in range(240)]
 def apply(self,im,t):
  strength=float(np.interp(t,[0,15,23,27,30],[1,.85,.4,.12,0]))
  if strength==0:return im
  layer=np.zeros((941,1672),np.uint8)
  for start,dur,x,y,speed,sz in self.drops:
   u=t-start
   if not 0<=u<dur:continue
   fade=min(u/.35,(dur-u)/.5,1)*strength
   px=int(x+1.5*np.sin(u*.9));py=int(y+u*speed)
   cv2.line(layer,(px,py-int(12*sz)),(px,py),int(70*fade),1,cv2.LINE_AA)
   cv2.ellipse(layer,(px,py),(max(1,int(2*sz)),max(2,int(3*sz))),0,0,360,int(125*fade),-1,cv2.LINE_AA)
  alpha=layer.astype(np.float32)/255*self.mask*.43
  if im.shape[:2]!=(941,1672):alpha=cv2.resize(alpha,(im.shape[1],im.shape[0]))
  return (im.astype(np.float32)*(1-alpha[:,:,None])+np.array([213,226,230])*alpha[:,:,None]).astype(np.uint8)

class Motion:
 def __init__(self,path):
  self.cap=cv2.VideoCapture(str(path));self.fps=self.cap.get(cv2.CAP_PROP_FPS)
  self.count=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT));self.pos=-1;self.last=None
  if not self.cap.isOpened() or self.count<24 or self.fps<=0:raise RuntimeError(f'Invalid motion: {path}')
 def frame(self,seconds):
  ix=min(self.count-1,max(0,int(seconds*self.fps)))
  if ix<self.pos:self.cap.set(cv2.CAP_PROP_POS_FRAMES,ix);self.pos=ix-1
  while self.pos<ix:
   ok,img=self.cap.read()
   if not ok:raise RuntimeError('Unexpected end of motion clip')
   self.last=cv2.cvtColor(img,cv2.COLOR_BGR2RGB);self.pos+=1
  return cv2.resize(self.last,(1672,941),interpolation=cv2.INTER_AREA)

def normalize_audio(raw,audio,dest):
 # Two-pass linear normalization: one fixed gain, no pumping of the quiet ending.
 af='loudnorm=I=-24:TP=-3:LRA=20'
 measured=run(['ffmpeg','-hide_banner','-i',audio,'-af',af+':print_format=json','-f','null','-'],capture_output=True,text=True).stderr
 m=json.loads(measured[measured.rfind('{'):measured.rfind('}')+1])
 fixed=af+':linear=true:measured_I='+m['input_i']+':measured_TP='+m['input_tp']+':measured_LRA='+m['input_lra']+':measured_thresh='+m['input_thresh']+':offset='+m['target_offset']
 run(['ffmpeg','-y','-v','error','-i',raw,'-i',audio,'-map','0:v','-map','1:a','-c:v','copy','-af',fixed,'-c:a','aac','-b:a','256k','-ar',SR,'-t',90,'-movflags','+faststart',dest])

def video():
 missing=[str(p) for p in MOTIONS.values() if not p.is_file()]
 if missing:raise RuntimeError('完成版には動作2本が必要です。未取得: '+', '.join(missing))
 imgs=[cv2.cvtColor(cv2.imread(str(SRC/p)),cv2.COLOR_BGR2RGB) for p in FILES]
 mid=cv2.cvtColor(cv2.imread(str(SRC/'S1b_dog_awake_reading.png')),cv2.COLOR_BGR2RGB)
 rain=Rain();motions={k:Motion(p) for k,p in MOTIONS.items()}
 def source(si,t):
  s=SHOTS[si]
  im=motions[si].frame(t-s[0]) if si in motions else imgs[s[2]]
  # Generated clips stay full-frame; the final camera crop follows the original cut.
  return rain.apply(im,t) if s[2] in (0,1) else im
 op,ed=title_layer('open'),title_layer('end')
 raw=WORK/'irostory01_映像のみ_v2.mp4'
 log=(WORK/'render.log').open('w')
 enc=subprocess.Popen(['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(raw)],stdin=subprocess.PIPE,stderr=log)
 for i in range(DURATION*FPS):
  t=i/FPS; si=next(k for k,s in enumerate(SHOTS) if s[0]<=t<s[1]); s=SHOTS[si]
  frame=camera(source(si,t),s,t)
  # A short dissolve only at the beginning of each new cut.
  if si>0 and t-s[0]<.42:
   prev=SHOTS[si-1]; old=camera(source(si-1,prev[1]-1/FPS),prev,prev[1]-1/FPS)
   frame=cv2.addWeighted(old,1-(t-s[0])/.42,frame,(t-s[0])/.42,0)
  if 1<t<8.7:
   alpha=min((t-1)/1.1,(8.7-t)/1.1,1)
   frame=blend_layer(frame,op,alpha)
  if t>83.5:frame=blend_layer(frame,ed,min((t-83.5)/1.8,1))
  fade=min(t/.8,1,(90-t)/1.3)
  if fade<1:frame=(frame*max(0,fade)).astype(np.uint8)
  enc.stdin.write(frame.tobytes())
  if i%(FPS*10)==0:print(f'Video {t:.0f}/90 sec',flush=True)
 enc.stdin.close()
 if enc.wait()!=0:raise RuntimeError('ffmpeg render failed, see render.log')
 log.close()
 # Quiet short-film mix, retaining ambience/foley dynamics.
 normalize_audio(raw,BASE/'音源/irostory01_生活音_仕上げv2.wav',MAIN)
 print('Final mux complete',flush=True)
 # Thumbnail typography is a separate overlay, preserving the original scene.
 thumb=camera(imgs[2],SHOTS[5],45)
 overlay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(overlay)
 for x in range(1000):d.line((x,0,x,H),fill=(12,30,31,int(220*max(0,1-x/1000)**.5)))
 d.text((92,90),'IRO SOUNDS',font=font(32),fill=(235,217,179,255))
 d.text((87,255),'あと一ページ、',font=font(91,True),fill=(255,250,233,255))
 d.text((87,380),'のはずだった。',font=font(91,True),fill=(255,250,233,255))
 d.text((96,590),'犬と暮らす、小さな物語。',font=font(32),fill=(235,224,199,255))
 d.text((96,952),'音楽なし・セリフなし  /  90秒',font=font(26),fill=(235,224,199,255))
 thumb=blend_layer(thumb,np.array(overlay),1)
 small=Image.fromarray(thumb).resize((1280,720),Image.Resampling.LANCZOS)
 small.save(OUT/'irostory01_サムネ_v2.jpg',quality=90)
 repo_thumb=REPO/'サムネ確認用/IRO Sounds/irostory01_サムネ_v2.jpg'
 small.save(repo_thumb,quality=90)

def qc():
 data=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',MAIN],capture_output=True,text=True).stdout)
 dec=run(['ffmpeg','-v','error','-i',MAIN,'-f','null','-'],capture_output=True,text=True)
 loud=run(['ffmpeg','-hide_banner','-i',MAIN,'-vn','-af','loudnorm=I=-24:TP=-3:LRA=10:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
 ld=json.loads(loud[loud.rfind('{'):loud.rfind('}')+1])
 tiles=[]
 for sec in [4,14,21,26,28,30,35,37,39,46,60,69,78,86]:
  p=WORK/f'qc_{sec:02}.jpg'
  run(['ffmpeg','-y','-v','error','-ss',sec,'-i',MAIN,'-frames:v','1','-q:v','2',p])
  im=Image.open(p).resize((480,270));tiles.append((sec,im))
 sheet=Image.new('RGB',(1440,5*310),(23,29,29));draw=ImageDraw.Draw(sheet)
 for k,(sec,im) in enumerate(tiles):
  x=k%3*480;y=k//3*310;sheet.paste(im,(x,y));draw.text((x+12,y+279),f'{sec:02}s',font=font(18),fill=(243,237,220))
 sheet.save(OUT/'irostory01_場面確認_v2.jpg',quality=90)
 vs=next(s for s in data['streams'] if s['codec_type']=='video')
 aus=next(s for s in data['streams'] if s['codec_type']=='audio')
 report={'id':'irostory01','version':'finished_v2','date':'2026-10-30','file':str(MAIN),'duration_seconds':float(data['format']['duration']),'size_bytes':MAIN.stat().st_size,'width':vs['width'],'height':vs['height'],'frame_rate':vs['avg_frame_rate'],'video_codec':vs['codec_name'],'audio_codec':aus['codec_name'],'sample_rate':aus['sample_rate'],'channels':aus['channels'],'loudness':ld,'full_decode_errors':dec.stderr.strip(),'sha256':hashlib.sha256(MAIN.read_bytes()).hexdigest(),'source_images':7,'motion_clips':2,'shots':len(SHOTS),'audio_provenance':'独自の手続き合成。音楽・声・外部録音なし。雨の減衰・生活音の音量とタイミングを変更。','subjective_audio_review':'直接聴取による評価は未実施。本人の試聴用。','thumbnail_bytes':(OUT/'irostory01_サムネ_v2.jpg').stat().st_size}
 assert report['duration_seconds']==90 and report['width']==1920 and not report['full_decode_errors']
 assert float(ld['input_tp'])<=-2.5
 assert report['thumbnail_bytes']<1_000_000
 (REPO/'iro/irostory01_完成検品_v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('step',choices=['audio','video','qc','all'],default='all',nargs='?');args=parser.parse_args()
 for p in [WORK,OUT,BASE/'音源']:p.mkdir(parents=True,exist_ok=True)
 for name,fn in [('audio',sound),('video',video),('qc',qc)]:
  if args.step in [name,'all']:fn()
