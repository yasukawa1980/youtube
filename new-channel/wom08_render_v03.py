"""EP008 video assembly and technical QA. Existing approved brand clips are read-only."""
import os
os.environ.setdefault('WOM08_ROOT', '/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v03_20261030')
import argparse,math,re,json,subprocess,shutil
from pathlib import Path
import numpy as np
from fractions import Fraction
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from wom08_produce import ROOT,REPO,OP,END,FPS,SR,read,save,sha,ff,probe,measure,content,ai_video
from wom01_quiet_origins import stream_hash

def camera(count,band=(110,930),rim=False,amount=.03,direction=None):
 t=f'on/{max(1,count-1)}'
 z=f'(1+{amount}*{t})';x=f'(W-W/{z})/2';y='0' if rim else f'(H-H/{z})/2'
 if direction=='ferris_group':x=f'(W-W/{z})*0.28';y=f'(H-H/{z})*0.5'
 if direction=='audubon_head':x=f'(W-W/{z})*0.68';y=f'(H-H/{z})*0.15'
 if direction=='bottom_to_top':z='1.08';x=f'(W-W/{z})/2';y=f'(H-H/{z})*(1-{t})'
 top,bottom=band;h=bottom-top
 p=f"perspective=x0='{x}':y0='{y}':x1='{x}+W/{z}':y1='{y}':x2='{x}':y2='{y}+H/{z}':x3='{x}+W/{z}':y3='{y}+H/{z}':sense=source:eval=frame:interpolation=cubic"
 return f'[0:v]split=2[base][art];[art]crop=1920:{h}:0:{top},format=yuv444p,{p}[moving];[base][moving]overlay=0:{top}:format=yuv444,format=yuv420p[v]'


def package():
 for l in ['en','ja']:
  out=ROOT/f'deliverables/EP008_Tutankhamun_{l}_v03_1080p30.mp4'
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',ROOT/f'deliverables/EP008_audio_{l}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-metadata','title=Quiet Origins / Tutankhamun','-metadata','comment=English: Kokoro/af_heart. Japanese: VOICEVOX:冥鳴ひまり. AI videos: V01 candle only, Kling AI. External subtitles.','-movie_timescale',48000,'-movflags','+faststart',out])
  print('PACKAGED',l,flush=True)

def reviews():
 binary=imageio_ffmpeg.get_ffmpeg_exe()
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP008_Tutankhamun_{l}_v03_1080p30.mp4';out=ROOT/f'deliverables/EP008_Tutankhamun_{l}_v03_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
  subprocess.run([binary,'-nostdin','-y','-v','error','-i',str(src),'-vf',vf,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-movie_timescale','48000','-movflags','+faststart','-progress',str(ROOT/f'_work/subtitles_{l}_progress.txt'),str(out)],check=True)
  assert stream_hash(src,'a')==stream_hash(out,'a');print('SUBTITLE REVIEW',l,flush=True)

def precision():
 """Preserve encoded packets while making movie and track durations sample-exact."""
 state=ROOT/'records/container_precision.json'
 if state.exists() and all(sha(ROOT/'deliverables'/x['name'])==x['after_sha256'] for x in read(state)['files']):return
 m=read(ROOT/'records/master_timeline.json');samples=round(m['duration_seconds']*48000);frames=round(m['duration_seconds']*30);records=[]
 files=[ROOT/f'deliverables/EP008_audio_{l}.m4a' for l in ['en','ja']]+sorted((ROOT/'deliverables').glob('EP008_Tutankhamun_*.mp4'))
 for p in files:
  before={s['codec_type']:stream_hash(p,'v' if s['codec_type']=='video' else 'a') for s in probe(p)['streams'] if s['codec_type'] in ['video','audio']};oldsha=sha(p)
  info=probe(p)
  if all(int(s['duration_ts'])==(frames*512 if s['codec_type']=='video' else samples) for s in info['streams']) and abs(float(info['format']['duration'])-samples/48000)<0.000002:
   records.append({'name':p.name,'before_sha256':oldsha,'after_sha256':oldsha,'already_sample_exact':True,'encoded_streams_identical':True,'stream_hashes':before,'duration_seconds':info['format']['duration']});continue
  backup=ROOT/'_work/container_precision_inputs'/f'{oldsha}_{p.name}';backup.parent.mkdir(exist_ok=True)
  if not backup.exists():shutil.copy2(p,backup)
  args=['-i',backup]
  if p.suffix=='.mp4':
   lang='en' if '_en_' in p.name else 'ja';args+=['-i',ROOT/f'deliverables/EP008_audio_{lang}.m4a','-map','0:v:0','-map','1:a:0','-map_metadata',0,'-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn')]
  else:args+=['-map',0]
  tmp=ROOT/'_work'/f'exact_{p.name}';ff([*args,'-c','copy','-movie_timescale',48000,'-movflags','+faststart',tmp])
  after={s['codec_type']:stream_hash(tmp,'v' if s['codec_type']=='video' else 'a') for s in probe(tmp)['streams'] if s['codec_type'] in ['video','audio']};assert before==after
  for s in probe(tmp)['streams']:assert int(s['duration_ts'])==(frames*512 if s['codec_type']=='video' else samples)
  shutil.copy2(tmp,p);records.append({'name':p.name,'before_sha256':oldsha,'after_sha256':sha(p),'encoded_streams_identical':True,'stream_hashes':after,'duration_seconds':probe(p)['format']['duration']})
 save(state,{'passed':True,'movie_timescale':48000,'video_frames':frames,'audio_samples':samples,'files':records})

def verify():
 master=read(ROOT/'records/master_timeline.json');frames=round(master['duration_seconds']*30);files=[]
 for l in ['en','ja']:
  for review in [False,True]:
   out=ROOT/f'deliverables/EP008_Tutankhamun_{l}_v03{"_subtitled_review" if review else ""}_1080p30.mp4'
   decoded=subprocess.run(['ffmpeg','-nostdin','-v','warning','-i',str(out),'-f','null','-'],capture_output=True,text=True,check=True)
   assert not decoded.stderr.strip(),decoded.stderr
   p=probe(out);v=next(s for s in p['streams'] if s['codec_type']=='video')
   assert (v['profile'],v['pix_fmt'])==('High','yuv420p')
   assert [v['width'],v['height']]==[1920,1080] and v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==frames
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(out)],text=True).splitlines()))
   assert v['time_base']=='1/15360' and pts==list(range(0,frames*512,512))
   assert int(v['duration_ts'])==frames*512
   av=next(s for s in p['streams'] if s['codec_type']=='audio');assert av['time_base']=='1/48000' and int(av['duration_ts'])==round(master['duration_seconds']*48000)
   assert abs(float(p['format']['duration'])-master['duration_seconds'])<1/30
   measured=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(out),'-vn','-af','loudnorm=I=-16:TP=-3:LRA=7:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
   levels=json.loads(re.findall(r'\{\s*"input_i".*?\}',measured.stderr,re.S)[-1]);assert abs(float(levels['input_i'])+16)<.3 and float(levels['input_tp'])<=-1
   silence=subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-vn','-af','silencedetect=noise=-60dB:d=1','-f','null','-'],capture_output=True,text=True,check=True).stderr
   silent=[float(x) for x in re.findall(r'silence_duration: ([\d.]+)',silence)]
   assert not silent,('Unintended full-mix silence',l,silent)
   files.append({'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'video_stream_sha256':stream_hash(out,'v'),'audio_stream_sha256':stream_hash(out,'a'),'full_decode':True,'decode_warnings':0,'profile':v['profile'],'pix_fmt':v['pix_fmt'],'exact_30fps_pts':True,'frames':frames,'duration':float(p['format']['duration']),'loudness':levels,'silence_over_1s_at_minus60dB':silent})
   print('VERIFIED',out.name,levels['input_i'],flush=True)
 assert files[0]['video_stream_sha256']==files[2]['video_stream_sha256']
 assert files[0]['audio_stream_sha256']==files[1]['audio_stream_sha256'] and files[2]['audio_stream_sha256']==files[3]['audio_stream_sha256']
 save(ROOT/'records/qc_v03.json',{'passed':True,'duration_seconds':master['duration_seconds'],'frames':frames,'fps':30,'human_full_listening':False,'files':files,'shared_video_stream':True,'subtitled_audio_unchanged':True})

if __name__=='__main__':
 import sys
 assert sys.argv[1] in ['package','reviews','precision','verify']
 globals()[sys.argv[1]]()
