"""EP005 video assembly and technical QA. Existing approved brand clips are read-only."""
import argparse,math,re,json,subprocess,shutil
from pathlib import Path
import numpy as np
from fractions import Fraction
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from wom05_produce import ROOT,REPO,OP,END,FPS,SR,read,save,sha,ff,probe,measure,content
from wom01_quiet_origins import stream_hash

def camera(count,band=(110,930),rim=False,amount=.03):
 z=f'(1+{amount}*on/{max(1,count-1)})';x=f'(W-W/{z})/2';y='0' if rim else f'(H-H/{z})/2'
 top,bottom=band;h=bottom-top
 p=f"perspective=x0='{x}':y0='{y}':x1='W-{x}':y1='{y}':x2='{x}':y2='H-{y}':x3='W-{x}':y3='H-{y}':sense=source:eval=frame:interpolation=cubic"
 return f'[0:v]split=2[base][art];[art]crop=1920:{h}:0:{top},format=yuv444p,{p}[moving];[base][moving]overlay=0:{top}:format=yuv444,format=yuv420p[v]'


def pictures():
 master=read(ROOT/'records/master_timeline.json');narr={l:read(ROOT/f'records/narration_timeline_{l}.json') for l in ['en','ja']};manifest=read(ROOT/'records/visual_manifest.json')['shots'];shots=[];parts=[];missing=[]
 def card(key):
  item=next(s for s in read(ROOT/'records/approved_brand_extracts.json') if s['key']==key)
  src=Path(item['encoded_file']);out=ROOT/f'_work/render/{key}.mp4';a,b=master['brand_intervals'][key];frames=round((b-a)*30)
  if not out.exists() or sha(src)!=sha(out):shutil.copy2(src,out)
  assert sha(src)==sha(out)
  parts.append(out);shots.append({**item,'start':a,'end':b,'frames':frames,'encoded_file':str(out.relative_to(ROOT)),'unchanged_encoded_brand_source':str(src),'unchanged_encoded_brand_sha256':sha(src)})
 for i,seg in enumerate(master['segments']):
  group=[s for s in manifest if s['segment_id']==seg['id']];a=0 if i==0 else round(seg['start']*30);b=round(seg['end']*30);bounds=np.linspace(a,b,len(group)+1).round().astype(int)
  def cue_start(index):
   return min(next(x for x in narr[l]['segments'] if x['id']==seg['id'])['cues'][index]['start'] for l in narr)
  if seg['id'] in ['P01','P09']:bounds[1]=round(cue_start(-1)*30)
  if seg['id']=='P03':bounds[1]=round(cue_start(2)*30)
  if seg['id']=='P08':bounds[1]=round(cue_start(1)*30)
  if seg['id']=='P11':
   bounds[1]=round(cue_start(2)*30)
   times=[]
   for l,phrase in [('en','in small carvings'),('ja','この小さな彫り物')]:
    c=next(x for x in narr[l]['segments'] if x['id']=='P11')['cues'][-1]
    times.append(c['start']+(c['end']-c['start'])*c['text'].index(phrase)/len(c['text']))
   bounds[2]=round(min(times)*30)
  if seg['id']=='P12':bounds[1]=round(cue_start(2)*30);bounds[2]=round(cue_start(3)*30)
  assert all(bounds[j+1]>bounds[j] for j in range(len(group)))
  for j,s in enumerate(group):
   key=s['key'];n=int(bounds[j+1]-bounds[j]);out=ROOT/f'_work/render/{seg["id"]}_{j+1:02}_{key}.mp4';stamp=out.with_suffix('.json');filt=camera(n,s['camera_band'],key in ['met_40011_DP206881','R01'],.04 if key=='met_24145' else .03);args=['-loop',1,'-framerate',30,'-i',ROOT/s['file']];cfg={'image_sha256':sha(ROOT/s['file']),'frames':n,'crf':18}
   if key.startswith('V'):
    video=ROOT/'assets/V02_softlight_v02.mp4' if key=='V02' else ROOT.parent/f'素材/{key}_Kling_v02.mp4'
    if not video.exists():missing.append(key);continue
    cfg['video_sha256']=sha(video);v=next(x for x in probe(video)['streams'] if x['codec_type']=='video');fps=float(Fraction(v['avg_frame_rate']));end_frame=min(int(v['nb_frames']),round(fps*10));start_frame=0;frames=end_frame-start_frame;factor=(n/30)/(frames/fps)
    z=f'(1+0.03*on/{max(1,n-1)})';x=f'(W-W/{z})/2';y=f'(H-H/{z})/2';pers=f"perspective=x0='{x}':y0='{y}':x1='W-{x}':y1='{y}':x2='{x}':y2='H-{y}':x3='W-{x}':y3='H-{y}':sense=source:eval=frame:interpolation=cubic"
    filt=f'[1:v]trim=start_frame={start_frame}:end_frame={end_frame},setpts=(PTS-STARTPTS)*{factor:.12f},scale=1458:820:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.25,format=yuv444p,{pers}[art];[0:v][art]overlay=231:110:shortest=1,format=yuv420p[v]';args+=['-i',video]
   cfg['filter']=filt
   if not(out.exists() and stamp.exists() and read(stamp)==cfg):
    ff([*args,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',n,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out]);save(stamp,cfg)
   record={**s}
   if key.startswith('V'):record.update({'source_video':str(video),'source_start_frame':start_frame,'source_end_frame':end_frame,'source_fps':fps,'time_scale':factor,'zoom_percent':3})
   else:record['zoom_percent']=4 if key=='met_24145' else 3
   parts.append(out);shots.append({**record,'start':int(bounds[j])/30,'end':int(bounds[j+1])/30,'frames':n,'encoded_file':str(out.relative_to(ROOT))});print('RENDERED',seg['id'],key,n,flush=True)
  if i==1:card('opening')
 card('endcard')
 if missing:save(ROOT/'records/render_progress.json',{'completed':shots,'missing':missing});print('WAITING',missing,flush=True);return
 assert sum(s['frames'] for s in shots)==round(master['duration_seconds']*30)
 save(ROOT/'records/render_shots.json',shots);listing=ROOT/'_work/concat.txt';listing.write_text(''.join(f"file '{p}'\nduration {s['frames']/30:.9f}\n" for p,s in zip(parts,shots)))
 raw=ROOT/'_work/picture_concat.mp4';ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw]);ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movie_timescale',48000,'-movflags','+faststart',ROOT/'_work/picture_master.mp4'])
 print('PICTURES COMPLETE',len(shots),flush=True)

def package():
 for l in ['en','ja']:
  out=ROOT/f'deliverables/EP005_Tengu_{l}_v01_1080p30.mp4'
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',ROOT/f'deliverables/EP005_audio_{l}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-metadata','title=Quiet Origins / Tengu','-metadata','comment=English: Kokoro/af_heart. Japanese: VOICEVOX:冥鳴ひまり. AI stills: R01-R03. AI videos: V01-V03. External subtitles.','-movie_timescale',48000,'-movflags','+faststart',out])
  print('PACKAGED',l,flush=True)

def reviews():
 binary=imageio_ffmpeg.get_ffmpeg_exe()
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP005_Tengu_{l}_v01_1080p30.mp4';out=ROOT/f'deliverables/EP005_Tengu_{l}_v01_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
  subprocess.run([binary,'-nostdin','-y','-v','error','-i',str(src),'-vf',vf,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-movie_timescale','48000','-movflags','+faststart','-progress',str(ROOT/f'_work/subtitles_{l}_progress.txt'),str(out)],check=True)
  assert stream_hash(src,'a')==stream_hash(out,'a');print('SUBTITLE REVIEW',l,flush=True)

def precision():
 """Preserve encoded packets while making movie and track durations sample-exact."""
 state=ROOT/'records/container_precision.json'
 if state.exists() and all(sha(ROOT/'deliverables'/x['name'])==x['after_sha256'] for x in read(state)['files']):return
 m=read(ROOT/'records/master_timeline.json');samples=round(m['duration_seconds']*48000);frames=round(m['duration_seconds']*30);records=[]
 files=[ROOT/f'deliverables/EP005_audio_{l}.m4a' for l in ['en','ja']]+sorted((ROOT/'deliverables').glob('EP005_Tengu_*.mp4'))
 for p in files:
  before={s['codec_type']:stream_hash(p,'v' if s['codec_type']=='video' else 'a') for s in probe(p)['streams'] if s['codec_type'] in ['video','audio']};oldsha=sha(p)
  info=probe(p)
  if all(int(s['duration_ts'])==(frames*512 if s['codec_type']=='video' else samples) for s in info['streams']) and abs(float(info['format']['duration'])-samples/48000)<0.000002:
   records.append({'name':p.name,'before_sha256':oldsha,'after_sha256':oldsha,'already_sample_exact':True,'encoded_streams_identical':True,'stream_hashes':before,'duration_seconds':info['format']['duration']});continue
  backup=ROOT/'_work/container_precision_inputs'/f'{oldsha}_{p.name}';backup.parent.mkdir(exist_ok=True)
  if not backup.exists():shutil.copy2(p,backup)
  args=['-i',backup]
  if p.suffix=='.mp4':
   lang='en' if '_en_' in p.name else 'ja';args+=['-i',ROOT/f'deliverables/EP005_audio_{lang}.m4a','-map','0:v:0','-map','1:a:0','-map_metadata',0,'-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn')]
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
   out=ROOT/f'deliverables/EP005_Tengu_{l}_v01{"_subtitled_review" if review else ""}_1080p30.mp4'
   ff(['-i',out,'-f','null','-']);p=probe(out);v=next(s for s in p['streams'] if s['codec_type']=='video')
   assert [v['width'],v['height']]==[1920,1080] and v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==frames
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(out)],text=True).splitlines()))
   assert v['time_base']=='1/15360' and pts==list(range(0,frames*512,512))
   assert int(v['duration_ts'])==frames*512
   av=next(s for s in p['streams'] if s['codec_type']=='audio');assert av['time_base']=='1/48000' and int(av['duration_ts'])==round(master['duration_seconds']*48000)
   assert abs(float(p['format']['duration'])-master['duration_seconds'])<1/30
   levels=measure(out);assert abs(float(levels['input_i'])+16)<.3 and float(levels['input_tp'])<=-1
   silence=subprocess.run(['ffmpeg','-hide_banner','-i',str(out),'-af','silencedetect=noise=-60dB:d=1','-f','null','-'],capture_output=True,text=True,check=True).stderr
   silent=[float(x) for x in re.findall(r'silence_duration: ([\d.]+)',silence)]
   assert not silent,('Unintended full-mix silence',l,silent)
   files.append({'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'video_stream_sha256':stream_hash(out,'v'),'audio_stream_sha256':stream_hash(out,'a'),'full_decode':True,'exact_30fps_pts':True,'frames':frames,'duration':float(p['format']['duration']),'loudness':levels,'silence_over_1s_at_minus60dB':silent})
   print('VERIFIED',out.name,levels['input_i'],flush=True)
 assert files[0]['video_stream_sha256']==files[2]['video_stream_sha256']
 assert files[0]['audio_stream_sha256']==files[1]['audio_stream_sha256'] and files[2]['audio_stream_sha256']==files[3]['audio_stream_sha256']
 save(ROOT/'records/qc_v01.json',{'passed':True,'duration_seconds':master['duration_seconds'],'frames':frames,'fps':30,'human_full_listening':False,'files':files,'shared_video_stream':True,'subtitled_audio_unchanged':True})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['pictures','package','reviews','precision','verify']);a=p.parse_args();globals()[a.stage]()
