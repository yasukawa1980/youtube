"""EP008 video assembly and technical QA. Existing approved brand clips are read-only."""
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


def pictures(partial=False,ai_only=False):
 master=read(ROOT/'records/master_timeline.json');manifest=read(ROOT/'records/visual_manifest.json')['shots']
 for key in ['V01']:
  if partial:continue
  assert ai_video(key).exists(), f'{key} has not been generated; do not encode a placeholder'
  assert not next(s for s in manifest if s['key']==key).get('missing_video'), 'Re-run visuals after downloading videos'
 narr=read(ROOT/'records/narration_timeline_en.json')['segments'];shots=[]
 def card(key,path):
  a,b=master['brand_intervals'][key];n=round((b-a)*30)
  v=next(s for s in probe(path)['streams'] if s['codec_type']=='video')
  assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',n)
  shots.append({'key':key,'segment_id':'BRAND','start':a,'end':b,'frames':n,'encoded_file':str(path),'original_source':str(path),'original_sha256':sha(path)})
 for i,seg in enumerate(master['segments']):
  group=[s for s in manifest if s['segment_id']==seg['id']];a=0 if i==0 else round(seg['start']*30);b=round(seg['end']*30)
  bounds=np.linspace(a,b,len(group)+1).round().astype(int)
  # Paragraph cuts share the primary English sentence boundaries.
  starts={'P03':['Carter had'], 'P04':['Asked if'], 'P05':['Robbers had','On the sixteenth'], 'P06':['Lord Carnarvon'], 'P08':['The writer'], 'P09':['One alabaster'], 'P12':['In 2002']}
  for j,phrase in enumerate(starts.get(seg['id'],[]),1):
   cue=next(c for c in narr[i]['cues'] if phrase in c['text']);fraction=len(cue['text'].split(phrase)[0])/len(cue['text']);bounds[j]=round((cue['start']+(cue['end']-cue['start'])*fraction)*30)
  assert all(bounds[j+1]>bounds[j] for j in range(len(group)))
  for j,s in enumerate(group):
   key=s['key'];n=int(bounds[j+1]-bounds[j]);out=ROOT/f'_work/render/{seg["id"]}_{j+1:02}_{key}.mp4';stamp=out.with_suffix('.json')
   if partial and key.startswith('V'):continue
   if ai_only and not key.startswith('V'):continue
   args=['-loop',1,'-framerate',30,'-i',ROOT/s['file']]
   direction='bottom_to_top' if key=='B157' else None
   filt=camera(n,s['camera_band'],amount=.18 if key=='G07-01' else .24 if key=='G09-01' else .03,direction=direction);cfg={'image_sha256':sha(ROOT/s['file']),'frames':n,'crf':18}
   static=key.startswith('D_') or key=='credits'
   if static:
    filt='[0:v]format=yuv420p[v]';cfg['lossless_static_intermediate']=True
   if key=='G02-01':
    original=ROOT/'assets/G02-01_detail_pan.png';args+=['-loop',1,'-framerate',30,'-i',original]
    progress=f'on/{max(1,n-1)}';y=f'(.142/.332*{progress})*H'
    trans=f"perspective=x0='0':y0='{y}':x1='W':y1='{y}':x2='0':y2='{y}+(.19/.332)*H':x3='W':y3='{y}+(.19/.332)*H':sense=source:eval=frame:interpolation=cubic"
    box=s['art_boxes'][1];x0,y0,x1,y1=box
    filt=f'[1:v]format=yuv444p,{trans},scale={x1-x0}:{y1-y0}:flags=lanczos[detail];[0:v][detail]overlay={x0}:{y0}:format=yuv444,format=yuv420p[v]'
    cfg.update(detail_pan_start=s['detail_crop_normalized'],detail_pan_end=s['detail_pan_end_normalized'],detail_source_sha256=sha(original))
   if key.startswith('V'):
    video=ai_video(key);v=next(x for x in probe(video)['streams'] if x['codec_type']=='video');fps=float(Fraction(v['avg_frame_rate']));count=int(v['nb_frames'])
    used=min(count,round(n/30*fps));first=0;factor=(n/30)/(used/fps)
    cfg['video_sha256']=sha(video)
    filt=f'[1:v]trim=start_frame={first}:end_frame={first+used},setpts=(PTS-STARTPTS)*{factor:.12f},scale=1280:720:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=1920:1080:flags=lanczos,tpad=start_mode=clone:start_duration=0.034:stop_mode=clone:stop_duration=0.25[art];[0:v]crop=1920:110:0:0[header];[art][header]overlay=0:0:shortest=1,format=yuv420p[v]';args+=['-i',video]
    cfg.update({'source_start_frame':first,'source_frames_used':used,'time_scale':factor,'full_bleed':True})
   cfg['filter']=filt
   if not(out.exists() and stamp.exists() and read(stamp)==cfg):
    quality=['-qp',0,'-profile:v','high444'] if static else ['-crf',18,'-profile:v','high']
    ff([*args,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',n,'-an','-c:v','libx264','-threads',2,'-preset','veryfast',*quality,'-pix_fmt','yuv420p','-video_track_timescale',15360,out]);save(stamp,cfg)
   actual=int(next(v for v in probe(out)['streams'] if v['codec_type']=='video')['nb_frames'])
   if actual<n:
    assert key.startswith('V') and n-actual<=30,(key,actual,n)
    backup=ROOT/f'_work/{out.stem}_before_tail_pad.mp4'
    if not backup.exists():shutil.copy2(out,backup)
    ff(['-i',backup,'-vf','setpts=N/(30*TB),tpad=stop_mode=clone:stop_duration=1','-frames:v',n,'-fps_mode','passthrough','-an','-c:v','libx264','-threads',2,'-preset','veryfast','-crf',18,'-profile:v','high','-pix_fmt','yuv420p','-video_track_timescale',15360,out])
    save(ROOT/f'records/{key}_tail_normalization.json',{'input_frames':actual,'output_frames':n,'held_tail_frames':n-actual,'reason':'Optical-flow boundary frames; exact common timeline'})
   assert int(next(v for v in probe(out)['streams'] if v['codec_type']=='video')['nb_frames'])==n
   shots.append({**s,'start':int(bounds[j])/30,'end':int(bounds[j+1])/30,'frames':n,'encoded_file':str(out.relative_to(ROOT)),'camera_direction':direction,'render_config':cfg})
   print('RENDERED',seg['id'],key,n,flush=True)
  if i==1:card('opening',OP)
 card('endcard',END)
 if partial:
  save(ROOT/'records/still_render_progress.json',shots);print('STILLS COMPLETE',len(shots),flush=True);return
 if ai_only:
  save(ROOT/'records/ai_render_progress.json',shots);print('AI RENDERS COMPLETE',flush=True);return
 assert sum(s['frames'] for s in shots)==round(master['duration_seconds']*30)
 save(ROOT/'records/render_shots.json',shots)
 # Independent fresh decoders -> raw yuv420p frames -> exactly one encoder.
 out=ROOT/'_work/picture_master.mp4';records=[]
 cmd=['ffmpeg','-nostdin','-y','-v','warning','-f','rawvideo','-pixel_format','yuv420p','-video_size','1920x1080','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','3','-preset','medium','-crf','16','-profile:v','high','-level:v','4.1','-pix_fmt','yuv420p','-g','60','-bf','2','-maxrate','20M','-bufsize','30M','-fps_mode','passthrough','-video_track_timescale','15360','-movie_timescale','48000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(out)]
 with (ROOT/'records/encode.log').open('w') as log:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for shot in shots:
    src=ROOT/shot['encoded_file'];info=next(x for x in probe(src)['streams'] if x['codec_type']=='video')
    assert int(info['nb_frames'])==shot['frames'] and (info['width'],info['height'])==(1920,1080)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
    records.append({'key':shot['key'],'frames':shot['frames'],'input_profile':info['profile']})
   enc.stdin.close();assert enc.wait()==0
  except BaseException:
   enc.kill();enc.wait();raise
 save(ROOT/'records/encoding_method.json',{'method':'Independent shot decoders feeding one raw-video encoder','shots':records,'command':cmd})
 print('PICTURES COMPLETE',len(shots),flush=True)

def package():
 for l in ['en','ja']:
  out=ROOT/f'deliverables/EP008_Tutankhamun_{l}_v01_1080p30.mp4'
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',ROOT/f'deliverables/EP008_audio_{l}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-metadata','title=Quiet Origins / Tutankhamun','-metadata','comment=English: Kokoro/af_heart. Japanese: VOICEVOX:冥鳴ひまり. AI videos: V01 candle only, Kling AI. External subtitles.','-movie_timescale',48000,'-movflags','+faststart',out])
  print('PACKAGED',l,flush=True)

def reviews():
 binary=imageio_ffmpeg.get_ffmpeg_exe()
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP008_Tutankhamun_{l}_v01_1080p30.mp4';out=ROOT/f'deliverables/EP008_Tutankhamun_{l}_v01_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
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
   out=ROOT/f'deliverables/EP008_Tutankhamun_{l}_v01{"_subtitled_review" if review else ""}_1080p30.mp4'
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
 save(ROOT/'records/qc_v01.json',{'passed':True,'duration_seconds':master['duration_seconds'],'frames':frames,'fps':30,'human_full_listening':False,'files':files,'shared_video_stream':True,'subtitled_audio_unchanged':True})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['ai','stills','pictures','package','reviews','precision','verify']);a=p.parse_args()
 if a.stage=='ai':pictures(ai_only=True)
 elif a.stage=='stills':pictures(partial=True)
 else:globals()[a.stage]()
