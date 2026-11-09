import os
"""PNT02 video assembly and technical QA. Existing approved brand clips are read-only."""
import argparse,math,re,json,subprocess,shutil
from pathlib import Path
import numpy as np
from fractions import Fraction
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from pnt02_produce import LANGUAGES,VERSION,ROOT,REPO,OP,END,FPS,SR,read,save,sha,ff,probe,measure,content
from wom01_quiet_origins import stream_hash

def check_current_motion():
 from pnt02_picture import motion
 import sys
 scales=read(ROOT/'records/art_scales.json')
 outdated=False
 for shot in read(ROOT/'records/render_shots.json'):
  if shot.get('moving'):
   expected=motion(shot['key'],shot['frames'],1)
   outdated |= scales[shot['key']]['motion_start_native_box']!=expected['motion_start_native_box']
 if outdated:
  # A corrected crop invalidates only that shot's cache, then the full master.
  assert len(LANGUAGES)==1
  env=dict(os.environ,PNT02_SCALE='1');env.pop('PNT02_ROOT',None);env.pop('PNT02_LANG',None)
  print('REFRESH CORRECTED MOTION',LANGUAGES[0],flush=True)
  subprocess.run([sys.executable,str(REPO/'painting/pnt02_picture.py'),LANGUAGES[0],'1'],env=env,check=True)
  check_current_motion()

def package():
 check_current_motion()
 assert len(LANGUAGES)==1, "Set PNT02_LANG and per-language PNT02_ROOT"
 for l in LANGUAGES:
  out=ROOT/f'deliverables/PNT02_WashingtonCrossing_{l}_{VERSION}_1080p30.mp4'
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',ROOT/f'deliverables/PNT02_audio_{l}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-metadata','title=Quiet Origins / Washington Crossing the Delaware','-metadata','comment=English: Kokoro/af_heart. Japanese: VOICEVOX:冥鳴ひまり. External subtitles.','-movie_timescale',48000,'-movflags','+faststart',out])
  print('PACKAGED',l,flush=True)

def package4k():
 out=ROOT/f'deliverables/PNT02_WashingtonCrossing_en_{VERSION}_2160p30.mp4'
 ff(['-i',ROOT/'_work/picture_master_4k.mp4','-i',ROOT/'deliverables/PNT02_audio_en.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language=eng','-metadata','title=Quiet Origins / Washington Crossing the Delaware','-movie_timescale',48000,'-movflags','+faststart',out])
 original=ROOT/f'deliverables/PNT02_WashingtonCrossing_en_{VERSION}_1080p30.mp4'
 assert stream_hash(original,'a')==stream_hash(out,'a')
 v=next(s for s in probe(out)['streams'] if s['codec_type']=='video')
 assert (v['width'],v['height'],v['profile'],v['pix_fmt'],v['avg_frame_rate'])==(3840,2160,'High','yuv420p','30/1')
 save(ROOT/'records/4k_audio_integrity.json',dict(audio_stream_identical_to_1080=True,audio_stream_sha256=stream_hash(out,'a'),video_sha256=sha(out),source='native original image plates; common 1080p brand clips scaled with Lanczos'))
 print('PACKAGED 4K',flush=True)

def reviews():
 binary=imageio_ffmpeg.get_ffmpeg_exe()
 for l in LANGUAGES:
  src=ROOT/f'deliverables/PNT02_WashingtonCrossing_{l}_{VERSION}_1080p30.mp4';out=ROOT/f'deliverables/PNT02_WashingtonCrossing_{l}_{VERSION}_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=49'"
  subprocess.run([binary,'-nostdin','-y','-v','error','-threads','1','-i',str(src),'-filter_threads','1','-vf',vf,'-c:v','libx264','-threads','2','-preset','veryfast','-x264-params','rc-lookahead=5:sync-lookahead=0','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-movie_timescale','48000','-movflags','+faststart','-progress',str(ROOT/f'_work/subtitles_{l}_progress.txt'),str(out)],check=True)
  assert stream_hash(src,'a')==stream_hash(out,'a');print('SUBTITLE REVIEW',l,flush=True)

def precision():
 """Preserve encoded packets while making movie and track durations sample-exact."""
 state=ROOT/'records/container_precision.json'
 current={f'PNT02_audio_{l}.m4a' for l in LANGUAGES}|{p.name for p in (ROOT/'deliverables').glob('PNT02_WashingtonCrossing_*.mp4')}
 if state.exists() and {x['name'] for x in read(state)['files']}==current and all((ROOT/'deliverables'/x['name']).exists() and sha(ROOT/'deliverables'/x['name'])==x['after_sha256'] for x in read(state)['files']):return
 m=read(ROOT/'records/master_timeline.json');samples=round(m['duration_seconds']*48000);frames=round(m['duration_seconds']*30);records=[]
 files=[ROOT/f'deliverables/PNT02_audio_{l}.m4a' for l in LANGUAGES]+sorted((ROOT/'deliverables').glob('PNT02_WashingtonCrossing_*.mp4'))
 for p in files:
  before={s['codec_type']:stream_hash(p,'v' if s['codec_type']=='video' else 'a') for s in probe(p)['streams'] if s['codec_type'] in ['video','audio']};oldsha=sha(p)
  info=probe(p)
  if all(int(s['duration_ts'])==(frames*512 if s['codec_type']=='video' else samples) for s in info['streams']) and abs(float(info['format']['duration'])-samples/48000)<0.000002:
   records.append({'name':p.name,'before_sha256':oldsha,'after_sha256':oldsha,'already_sample_exact':True,'encoded_streams_identical':True,'stream_hashes':before,'duration_seconds':info['format']['duration']});continue
  backup=ROOT/'_work/container_precision_inputs'/f'{oldsha}_{p.name}';backup.parent.mkdir(exist_ok=True)
  if not backup.exists():shutil.copy2(p,backup)
  args=['-i',backup]
  if p.suffix=='.mp4':
   lang='en' if '_en_' in p.name else 'ja';args+=['-i',ROOT/f'deliverables/PNT02_audio_{lang}.m4a','-map','0:v:0','-map','1:a:0','-map_metadata',0,'-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn')]
  else:args+=['-map',0]
  tmp=ROOT/'_work'/f'exact_{p.name}';ff([*args,'-c','copy','-movie_timescale',48000,'-movflags','+faststart',tmp])
  after={s['codec_type']:stream_hash(tmp,'v' if s['codec_type']=='video' else 'a') for s in probe(tmp)['streams'] if s['codec_type'] in ['video','audio']};assert before==after
  for s in probe(tmp)['streams']:assert int(s['duration_ts'])==(frames*512 if s['codec_type']=='video' else samples)
  shutil.copy2(tmp,p);records.append({'name':p.name,'before_sha256':oldsha,'after_sha256':sha(p),'encoded_streams_identical':True,'stream_hashes':after,'duration_seconds':probe(p)['format']['duration']})
 save(state,{'passed':True,'movie_timescale':48000,'video_frames':frames,'audio_samples':samples,'files':records})

def verify():
 assert len(LANGUAGES)==1, "Independent language timelines require one language per run"
 master=read(ROOT/'records/master_timeline.json');frames=round(master['duration_seconds']*30);files=[]
 for l in LANGUAGES:
  for review in [False,True]:
   out=ROOT/f'deliverables/PNT02_WashingtonCrossing_{l}_{VERSION}{"_subtitled_review" if review else ""}_1080p30.mp4'
   decoded=subprocess.run(['ffmpeg','-nostdin','-v','warning','-threads','1','-i',str(out),'-threads','1','-filter_threads','1','-f','null','-'],capture_output=True,text=True,check=True)
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
 if len(LANGUAGES)==2:assert files[0]['video_stream_sha256']==files[2]['video_stream_sha256']
 assert files[0]['audio_stream_sha256']==files[1]['audio_stream_sha256']
 if len(LANGUAGES)==2:assert files[2]['audio_stream_sha256']==files[3]['audio_stream_sha256']
 save(ROOT/f'records/qc_{VERSION}.json',{'passed':True,'duration_seconds':master['duration_seconds'],'frames':frames,'fps':30,'human_full_listening':False,'files':files,'shared_video_stream':len(LANGUAGES)==2,'subtitled_audio_unchanged':True})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['package','package4k','reviews','precision','verify']);a=p.parse_args();globals()[a.stage]()
