"""Claude合格の2本でIRO18を仕上げる。生成・投稿・予約は行わない。"""
from pathlib import Path
import argparse, importlib.util, json, subprocess, random, hashlib
import cv2,numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1];OLD=R/'bgm/IRO/IRO18_毛糸の季節がやってきた'
TRIAL=Path('/Users/ryo/Desktop/BGM/IRO/Chill/18_毛糸の季節がやってきた/手直し_20261018')
OUT=TRIAL.parent/'完成_20261019';WORK=OUT/'_work';KIT=OUT/'投稿用';REVIEW=R/'iro/iro18_完成検品_20261019'
FF='/opt/homebrew/bin/ffmpeg';FP='/opt/homebrew/bin/ffprobe';FPS=24
PREFIX=543;TOTAL=173223;CARD=360;BODY=TOTAL-PREFIX-CARD
MAIN=KIT/'iro18_毛糸の季節がやってきた_扉入り.mp4'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
prep=load('prep',R/'iro/iro18_手直し試作_20261018.py')
fix=load('fix',R/'iro/iro18_房と糸の境界を検品_20261018.py')
door=load('door',R/'bgm/IRO/irokit/扉ムービーを入れる.py')
def run(args):subprocess.run([FF,'-y','-v','error',*map(str,args)],check=True)
def probe(p):return json.loads(subprocess.check_output([FP,'-v','error','-show_streams','-show_format','-of','json',str(p)]))
def video(p):return next(x for x in probe(p)['streams']if x['codec_type']=='video')
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb')as f:
  while b:=f.read(8*1024*1024):h.update(b)
 return h.hexdigest()
def encopts():return ['-c:v','h264_videotoolbox','-allow_sw','1','-q:v','85','-profile:v','high','-bf','0','-g','192','-r','24','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv']
def encoder(p):return subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1920x1080','-r','24','-i','-','-an',*encopts(),str(p)],stdin=subprocess.PIPE)
def cached(name,path):
 dest=WORK/(name+'.npy')
 if not dest.exists():
  a=np.lib.format.open_memmap(dest,mode='w+',dtype=np.uint8,shape=(192,1080,1920,3));c=cv2.VideoCapture(str(path))
  for k in range(192):
   ok,b=c.read();assert ok;a[k]=cv2.cvtColor(cv2.resize(b,(1920,1080),interpolation=cv2.INTER_LANCZOS4),cv2.COLOR_BGR2RGB)
  c.release();a.flush()
 return np.load(dest,mmap_mode='r')
def plan():
 rng=random.Random(18192026);seq=[1]
 while len(seq)<(BODY+191)//192:
  n=rng.choice([1,2])
  if len(seq)>1 and seq[-1]==seq[-2]==n:n=3-n
  seq.append(n)
 events=[]
 for cycle in range(6):
  for tag,t in [('C',280),('D',644),('C',1134)]:
   at=(cycle*1197+t)*24
   if at+192<=BODY:events.append({'tag':tag,'body_frame':at,'final_frame':PREFIX+at,'final_seconds':(PREFIX+at)/24})
 assert max(len(list(g))for _,g in __import__('itertools').groupby(seq))==2
 rows=[]
 for i,n in enumerate(seq):
  ev=next((x for x in events if i*192<x['body_frame']+192 and(i+1)*192>x['body_frame']),None)
  key=f"take{n}_{ev['tag']}_{i*192-ev['body_frame']:+d}"if ev else f'take{n}_rgb'
  rows.append({'index':i,'take':n,'start_body_frame':i*192,'frames':min(192,BODY-i*192),'key':key,'event':ev})
 data={'seed':18192026,'fps':24,'prefix_frames':PREFIX,'total_frames':TOTAL,'body_frames':BODY,'endcard_frames':CARD,'sequence':seq,'take_counts':{str(n):seq.count(n)for n in[1,2]},'max_same_take_run':2,'loop_crossfade':False,'events':events,'segments':rows}
 (WORK/'構成.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');return data

def parts(base_only=False):
 data=plan();pack=WORK/'parts';pack.mkdir(exist_ok=True)
 raw={n:cached(f'raw_take{n}',TRIAL/f'Kling_編み物試作{n}_原本.mp4')for n in[1,2]}
 dogs={n:cached(f'dog_{n}',OLD/f"Kling素材/{'D_v2'if n=='D'else n}.mp4")for n in['B1','C','D']}
 ref=np.array(Image.open(TRIAL/'18_start_編む手元_Kling用.png').convert('RGB'))
 mask=np.zeros((1080,1920),np.uint8);cv2.fillPoly(mask,[np.array(fix.PERSON,np.int32)],255)
 pa=(cv2.GaussianBlur(mask.astype(np.float32)/255,(0,0),18)*(mask>0))[:,:,None]
 dm=np.zeros((1080,1920),np.float32);cv2.ellipse(dm,(409,862),(241,154),0,0,360,1,-1);dm=(cv2.GaussianBlur(dm,(0,0),8)*(dm>0))[:,:,None]
 x,y,w,h=cv2.boundingRect(mask);ps=(slice(y,y+h),slice(x,x+w))
 x,y,w,h=cv2.boundingRect(np.uint8(dm[:,:,0]>0));ds=(slice(y,y+h),slice(x,x+w))
 dogmask=prep.dog_mask()
 unique={f'take{n}_rgb':{'take':n,'event':None}for n in[1,2]}
 if not base_only:unique.update({r['key']:r for r in data['segments']if r['event']})
 for count,(key,row)in enumerate(unique.items(),1):
  dest=pack/(key+'.mp4')
  if dest.exists():
   try:
    if int(video(dest)['nb_frames'])==192:continue
   except (subprocess.CalledProcessError,KeyError,ValueError):pass
  enc=encoder(dest);n=row['take'];ev=row['event'];delta=row['start_body_frame']-ev['body_frame'] if ev else 0
  for k in range(192):
   fixed=ref.copy();fixed[ps]=np.uint8(np.clip(ref[ps]*(1-pa[ps])+raw[n][k][ps]*pa[ps]+.5,0,255))
   base=fixed;base[ds]=np.uint8(np.clip(fixed[ds]*(1-dm[ds])+dogs['B1'][k][ds]*dm[ds]+.5,0,255))
   pos=delta+k
   if ev and 0<=pos<192:
    a=min(1,(pos+1)/12,(192-pos)/12);base[ds]=np.uint8(np.clip(base[ds]*(1-dm[ds]*a)+dogs[ev['tag']][pos][ds]*dm[ds]*a+.5,0,255))
   im=Image.fromarray(base);zoom=im.resize((2688,1512),Image.Resampling.LANCZOS).crop((164,400,2084,1480))
   enc.stdin.write(np.array(Image.composite(zoom,im,dogmask)).tobytes())
  enc.stdin.close();assert enc.wait()==0;assert int(video(dest)['nb_frames'])==192
  print('映像部品',count,'/',len(unique),key,flush=True)
 print('parts complete',len(unique),'event variants',flush=True)

def assets():
 # 既存の帯・文字組みをそのまま、新しい開始絵に適用する。
 stage=WORK/'静止画';(stage/'開始画像').mkdir(parents=True,exist_ok=True)
 import shutil
 shutil.copy2(TRIAL/'18_start_編む手元_犬1.4倍.png',stage/'開始画像/18_start.png')
 # 既存静止画スクリプトを専用コピー上で使う。参照モジュールの場所だけ絶対化。
 source=(OLD/'静止画の仕上げ.py').read_text().replace("ROOT.parent/'irokit/endcard.py'",repr(str(R/'bgm/IRO/irokit/endcard.py')))
 exec(compile(source,str(OLD/'静止画の仕上げ.py'),'exec'),{'__file__':str(stage/'build.py'),'__name__':'__main__'})
 for name in ['iro18_サムネ.jpg','iro18_サムネ.png','サムネ_168px.png','iro_エンドカード_IRO18.png']:shutil.copy2(stage/name,OUT/name)
 shutil.copy2(stage/'iro18_サムネ.jpg',KIT/'iro18_サムネ.jpg')
 print('thumbnail and card complete',flush=True)

def make_prefix():
 pack=WORK/'parts'
 prefix=WORK/'扉と間_543コマ.mp4'
 if not prefix.exists() or prefix.stat().st_mtime<(pack/'take1_rgb.mp4').stat().st_mtime:
  lead=WORK/'導入19コマ.mp4'
  run(['-i',pack/'take1_rgb.mp4','-vf','trim=start_frame=173:end_frame=192,setpts=PTS-STARTPTS','-an',*encopts(),lead])
  fc='[0:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS[a];[1:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS,tpad=start_duration=2.5:start_mode=clone[b];[a][b]xfade=transition=fade:duration=1:offset=19.333333,format=yuv420p[v]'
  run(['-i',door.MOVIE,'-i',lead,'-filter_complex',fc,'-map','[v]','-an','-frames:v',PREFIX,*encopts(),prefix])
 assert int(video(prefix)['nb_frames'])==PREFIX
 return prefix

def main_video(reuse_audio):
 assert reuse_audio,'音声は --reuse-audio で既存aac_at版を使う'
 data=json.loads((WORK/'構成.json').read_text());pack=WORK/'parts'
 prefix=make_prefix()
 files=[prefix]
 for row in data['segments']:
  p=pack/(row['key']+'.mp4');assert p.exists(),p
  if row['frames']!=192:
   tail=WORK/'本編末尾.mp4';run(['-i',p,'-an','-frames:v',row['frames'],'-c:v','copy',tail]);assert int(video(tail)['nb_frames'])==row['frames'];p=tail
  files.append(p)
 # 末尾15秒も女性は編み続け、同じ帯・文言の終了カードを2秒で表示。
 n=data['sequence'][-1];nextn=3-n
 listing=WORK/'カード背景.txt';listing.write_text(''.join(f"file '{pack/f'take{x}_rgb.mp4'}'\n"for x in[n,nextn,n]))
 card=WORK/'エンドカード15秒.mp4'
 run(['-ss',BODY%192/24,'-f','concat','-safe','0','-i',listing,'-loop','1','-framerate',24,'-i',OUT/'iro_エンドカード_IRO18.png','-filter_complex','[0:v]setpts=PTS-STARTPTS[b];[1:v]setpts=PTS-STARTPTS,format=rgba,fade=t=in:st=0.008333:d=2:alpha=1[c];[b][c]overlay=0:0,format=yuv420p[v]','-map','[v]','-an','-frames:v',360,*encopts(),card]);files.append(card)
 listing=WORK/'完成映像_連結.txt';listing.write_text(''.join(f"file '{p}'\n"for p in files))
 audio=WORK/'配信用音声.m4a';assert sha(audio)==sha(OLD/'_work/配信用音声.m4a')
 run(['-f','concat','-safe','0','-i',listing,'-i',audio,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',MAIN])
 assert int(video(MAIN)['nb_frames'])==TOTAL
 (WORK/'本編設定_実測.json').write_text(json.dumps({'file':str(MAIN),'duration':float(probe(MAIN)['format']['duration']),'video_frames':TOTAL,'actual_unit_offset':PREFIX/24,'actual_endcard_start':(TOTAL-CARD)/24,'original_audio_source':str((OLD/'_work/配信用音声.m4a').resolve()),'source_audio_sha256':sha(audio),'audio_reencoded':False,'loop_crossfade':False,'max_same_take_run':2},ensure_ascii=False,indent=2)+'\n')
 print('MAIN COMPLETE',str(MAIN),flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('step',choices=['assets','parts','bases','prefix','main']);ap.add_argument('--reuse-audio',action='store_true');a=ap.parse_args()
 for p in[WORK,KIT,REVIEW]:p.mkdir(parents=True,exist_ok=True)
 {'assets':assets,'parts':parts,'bases':lambda:parts(True),'prefix':make_prefix,'main':lambda:main_video(a.reuse_audio)}[a.step]()
