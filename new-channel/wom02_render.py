"""EP002 video assembly and technical QA. Existing approved brand clips are read-only."""
import argparse,math,re,json,subprocess,shutil
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from wom02_produce import ROOT,REPO,OP,END,FPS,SR,read,save,sha,ff,probe,measure,content
from wom01_quiet_origins import stream_hash

def pictures():
 master=read(ROOT/'records/master_timeline.json');manifest=read(ROOT/'records/visual_manifest.json')['shots'];shots=[];parts=[]
 def card(key,path,start,end):
  frames=round((end-start)*30);out=ROOT/f'_work/render/{key}.mp4'
  if not out.exists():ff(['-i',path,'-an','-vf','fps=30,scale=1920:1080,setsar=1,format=yuv420p','-frames:v',frames,'-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,out])
  assert int(probe(out)['streams'][0]['nb_frames'])==frames
  parts.append(out);shots.append({'key':key,'segment_id':'BRAND','start':start,'end':end,'frames':frames,'encoded_file':str(out.relative_to(ROOT))})
 for i,seg in enumerate(master['segments']):
  images=[s for s in manifest if s['segment_id']==seg['id']];a=0 if i==0 else round(seg['start']*30);b=round(seg['end']*30);bounds=np.linspace(a,b,len(images)+1).round().astype(int)
  if seg['id']=='H16':
   last_sentence=max(next(s for s in read(ROOT/f'records/narration_timeline_{l}.json')['segments'] if s['id']=='H16')['cues'][-1]['start'] for l in ['en','ja'])
   bounds[1]=round(last_sentence*30)
  for j,img in enumerate(images):
   count=int(bounds[j+1]-bounds[j]);out=ROOT/f'_work/render/{seg["id"]}_{j+1:02}.mp4';stamp=out.with_suffix('.json');cfg={'sha256':sha(ROOT/img['file']),'frames':count,'crf':18,'zoom':.025}
   if not(out.exists() and stamp.exists() and read(stamp)==cfg):
    # 2x oversampling gives continuous subpixel camera movement at 1080p.
    vf=f"scale=3840:2160,zoompan=z='1+0.025*on/{max(1,count-1)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={count}:s=1920x1080:fps=30,format=yuv420p"
    ff(['-i',ROOT/img['file'],'-vf',vf,'-frames:v',count,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out]);save(stamp,cfg)
   parts.append(out);shots.append({**img,'start':int(bounds[j])/30,'end':int(bounds[j+1])/30,'frames':count,'encoded_file':str(out.relative_to(ROOT))})
  print('RENDERED',seg['id'],flush=True)
  if i==1:card('opening',OP,*master['brand_intervals']['opening'])
 card('endcard',END,*master['brand_intervals']['endcard'])
 save(ROOT/'records/render_shots.json',shots)
 listing=ROOT/'_work/concat.txt';listing.write_text(''.join(f"file '{p}'\nduration {s['frames']/30:.9f}\n" for p,s in zip(parts,shots)))
 raw=ROOT/'_work/picture_concat.mp4';ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw])
 ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movflags','+faststart',ROOT/'_work/picture_master.mp4'])
 print('PICTURES COMPLETE',sum(s['frames'] for s in shots),flush=True)

def package():
 for l in ['en','ja']:
  out=ROOT/f'deliverables/EP002_Halloween_{l}_v01_1080p30.mp4'
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',ROOT/f'deliverables/EP002_audio_{l}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-metadata','title=Quiet Origins / Halloween','-metadata','comment=English: Kokoro/af_heart. Japanese: VOICEVOX:冥鳴ひまり. AI reconstructions R01-R03. External subtitles.','-movflags','+faststart',out])
  print('PACKAGED',l,flush=True)

def reviews():
 binary=imageio_ffmpeg.get_ffmpeg_exe()
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP002_Halloween_{l}_v01_1080p30.mp4';out=ROOT/f'deliverables/EP002_Halloween_{l}_v01_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
  subprocess.run([binary,'-nostdin','-y','-v','error','-i',str(src),'-vf',vf,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-movflags','+faststart','-progress',str(ROOT/f'_work/subtitles_{l}_progress.txt'),str(out)],check=True)
  assert stream_hash(src,'a')==stream_hash(out,'a');print('SUBTITLE REVIEW',l,flush=True)

def verify():
 master=read(ROOT/'records/master_timeline.json');frames=round(master['duration_seconds']*30);files=[]
 for l in ['en','ja']:
  for review in [False,True]:
   out=ROOT/f'deliverables/EP002_Halloween_{l}_v01{"_subtitled_review" if review else ""}_1080p30.mp4'
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
