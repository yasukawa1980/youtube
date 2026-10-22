"""EP003 video assembly and technical QA. Existing approved brand clips are read-only."""
import argparse,math,re,json,subprocess,shutil
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from wom03_produce import ROOT,REPO,OP,END,FPS,SR,read,save,sha,ff,probe,measure,content
from wom01_quiet_origins import stream_hash

def camera(count,band=(110,930),wide=None):
 z=f'(1+0.03*on/{max(1,count-1)})';x=f'(W-W/{z})/2';y=f'(H-H/{z})/2'
 if wide is not None:
  # Source is a 3840px strip; the viewport moves 1920px across the full H02 interval.
  phase,offset,total=wide;x=f'(1920*(on+{offset})/{max(1,total-1)})';y='0'
  pr=f"perspective=x0='{x}':y0=0:x1='{x}+1920':y1=0:x2='{x}':y2=H:x3='{x}+1920':y3=H:sense=source:eval=frame:interpolation=cubic,scale=1920:590,format=yuv420p"
  return pr
 top,bottom=band;h=bottom-top
 p=f"perspective=x0='{x}':y0='{y}':x1='W-{x}':y1='{y}':x2='{x}':y2='H-{y}':x3='W-{x}':y3='H-{y}':sense=source:eval=frame:interpolation=cubic"
 return f'[0:v]split=2[base][art];[art]crop=1920:{h}:0:{top},format=yuv444p,{p}[moving];[base][moving]overlay=0:{top}:format=yuv444,format=yuv420p[v]'


def pictures():
 master=read(ROOT/'records/master_timeline.json');manifest=read(ROOT/'records/visual_manifest.json')['shots'];shots=[];parts=[];missing=[]
 prior=Path('/Users/ryo/Desktop/新チャンネル/EP002_Halloween/確認版_v04_20261022')
 def card(key):
  s=next(s for s in read(prior/'records/render_shots.json') if s['key']==key);src=prior/s['encoded_file'];out=ROOT/f'_work/render/{key}.mp4'
  if not out.exists():shutil.copy2(src,out)
  assert sha(src)==sha(out);a,b=master['brand_intervals'][key];parts.append(out);shots.append({**s,'start':a,'end':b,'encoded_file':str(out.relative_to(ROOT)),'approved_brand_source':str(src),'source_sha256':sha(src)})
 for i,seg in enumerate(master['segments']):
  group=[s for s in manifest if s['segment_id']==seg['id']];a=0 if i==0 else round(seg['start']*30);b=round(seg['end']*30);bounds=np.linspace(a,b,len(group)+1).round().astype(int)
  if seg['id']=='M13':bounds[1]=a+180
  for j,s in enumerate(group):
   key=s['key'];n=int(bounds[j+1]-bounds[j]);out=ROOT/f'_work/render/{seg["id"]}_{j+1:02}_{key}.mp4';stamp=out.with_suffix('.json');filt=camera(n,s['camera_band']);args=['-loop',1,'-framerate',30,'-i',ROOT/s['file']];cfg={'image_sha256':sha(ROOT/s['file']),'frames':n,'crf':18}
   if key.startswith('V'):
    video=ROOT.parent/f'素材/{key}_Kling_v01.mp4'
    if not video.exists():missing.append(key);continue
    cfg['video_sha256']=sha(video);v=next(x for x in probe(video)['streams'] if x['codec_type']=='video');fps=eval(v['avg_frame_rate']);frames=min(int(v['nb_frames']),round(fps*10));factor=(n/30)/(frames/fps)
    z=f'(1+0.03*on/{max(1,n-1)})';x=f'(W-W/{z})/2';y=f'(H-H/{z})/2';pers=f"perspective=x0='{x}':y0='{y}':x1='W-{x}':y1='{y}':x2='{x}':y2='H-{y}':x3='W-{x}':y3='H-{y}':sense=source:eval=frame:interpolation=cubic"
    filt=f'[1:v]trim=end_frame={frames},setpts=(PTS-STARTPTS)*{factor:.12f},scale=1458:820:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.25,format=yuv444p,{pers}[art];[0:v][art]overlay=231:110:shortest=1,format=yuv420p[v]';args+=['-i',video]
   elif s.get('face_reveal'):
    args+=['-loop',1,'-framerate',30,'-i',ROOT/s['face_reveal']];cfg['face_sha256']=sha(ROOT/s['face_reveal']);fade=n/30*.35
    # Smooth two-second reveal of a face-only crop; whole object remains in view.
    filt=f'[1:v]format=rgba,fade=t=in:st={fade:.8f}:d=2:alpha=1[face];[0:v][face]overlay=0:0[composed];'+camera(n,s['camera_band']).replace('[0:v]','[composed]')
   cfg['filter']=filt
   if not(out.exists() and stamp.exists() and read(stamp)==cfg):
    ff([*args,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',n,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out]);save(stamp,cfg)
   parts.append(out);shots.append({**s,'start':int(bounds[j])/30,'end':int(bounds[j+1])/30,'frames':n,'encoded_file':str(out.relative_to(ROOT))});print('RENDERED',seg['id'],key,n,flush=True)
  if i==1:card('opening')
 card('endcard')
 if missing:save(ROOT/'records/render_progress.json',{'completed':shots,'missing':missing});print('WAITING',missing,flush=True);return
 assert sum(s['frames'] for s in shots)==round(master['duration_seconds']*30)
 save(ROOT/'records/render_shots.json',shots);listing=ROOT/'_work/concat.txt';listing.write_text(''.join(f"file '{p}'\nduration {s['frames']/30:.9f}\n" for p,s in zip(parts,shots)))
 raw=ROOT/'_work/picture_concat.mp4';ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw]);ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movflags','+faststart',ROOT/'_work/picture_master.mp4'])
 print('PICTURES COMPLETE',len(shots),flush=True)

def package():
 for l in ['en','ja']:
  out=ROOT/f'deliverables/EP003_Medusa_{l}_v01_1080p30.mp4'
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',ROOT/f'deliverables/EP003_audio_{l}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-metadata','title=Quiet Origins / Medusa','-metadata','comment=English: Kokoro/af_heart. Japanese: VOICEVOX:冥鳴ひまり. AI reconstructions R01-R03. External subtitles.','-movflags','+faststart',out])
  print('PACKAGED',l,flush=True)

def reviews():
 binary=imageio_ffmpeg.get_ffmpeg_exe()
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP003_Medusa_{l}_v01_1080p30.mp4';out=ROOT/f'deliverables/EP003_Medusa_{l}_v01_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
  subprocess.run([binary,'-nostdin','-y','-v','error','-i',str(src),'-vf',vf,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-movflags','+faststart','-progress',str(ROOT/f'_work/subtitles_{l}_progress.txt'),str(out)],check=True)
  assert stream_hash(src,'a')==stream_hash(out,'a');print('SUBTITLE REVIEW',l,flush=True)

def verify():
 master=read(ROOT/'records/master_timeline.json');frames=round(master['duration_seconds']*30);files=[]
 for l in ['en','ja']:
  for review in [False,True]:
   out=ROOT/f'deliverables/EP003_Medusa_{l}_v01{"_subtitled_review" if review else ""}_1080p30.mp4'
   ff(['-i',out,'-f','null','-']);p=probe(out);v=next(s for s in p['streams'] if s['codec_type']=='video')
   assert [v['width'],v['height']]==[1920,1080] and v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==frames
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(out)],text=True).splitlines()))
   assert v['time_base']=='1/15360' and pts==list(range(0,frames*512,512))
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
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['pictures','package','reviews','verify']);a=p.parse_args();globals()[a.stage]()
