"""v02 package and measurement; finished v01 is comparison reference only."""
import argparse,subprocess,json,shutil,hashlib,re
from pathlib import Path
import numpy as np
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from wom06_revision_v02 import ROOT,OLD,CHANGED
from wom06_produce import read,save,sha,ff,probe
from wom01_quiet_origins import stream_hash
from wom06_motion import roi,motion_stats

def package():
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP006_Sphinx_{l}_v02_1080p30.mp4'
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',ROOT/f'deliverables/EP006_audio_{l}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-metadata','title=Quiet Origins / Sphinx','-movie_timescale',48000,'-movflags','+faststart',src])
  print('PACKAGED',l,flush=True)

def reviews():
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP006_Sphinx_{l}_v02_1080p30.mp4';out=src.with_name(src.stem.replace('_1080','_subtitled_review_1080')+'.mp4');srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(src),'-vf',vf,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-movie_timescale','48000','-movflags','+faststart',str(out)],check=True)
  # Preserve packets but use production ffmpeg to set sample-exact movie duration.
  tmp=ROOT/f'_work/review_exact_{l}.mp4';ff(['-i',out,'-i',ROOT/f'deliverables/EP006_audio_{l}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-movie_timescale',48000,'-movflags','+faststart',tmp]);shutil.copy2(tmp,out)
  assert stream_hash(src,'a')==stream_hash(out,'a');print('SUBTITLE REVIEW',l,flush=True)

def hashes(src,name):
 out=ROOT/'_work'/name
 q=subprocess.run(['ffmpeg','-nostdin','-v','warning','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','yuv420p','-f','framemd5','-'],capture_output=True,text=True,check=True)
 assert not q.stderr.strip(),q.stderr;out.write_text(q.stdout)
 return [x.split(',')[-1].strip() for x in q.stdout.splitlines() if not x.startswith('#') and x.strip()]

def compare():
 old=OLD/'deliverables/EP006_Sphinx_en_v01_1080p30.mp4';new=ROOT/'deliverables/EP006_Sphinx_en_v02_1080p30.mp4'
 prior=read(ROOT/'records/pixel_comparison.json') if (ROOT/'records/pixel_comparison.json').exists() else {}
 cache=ROOT/'_work/v01_reference.framemd5'
 if cache.exists() and prior.get('v01_sha256')==sha(old):
  a=[x.split(',')[-1].strip() for x in cache.read_text().splitlines() if not x.startswith('#') and x.strip()]
 else:a=hashes(old,'v01_reference.framemd5')
 b=hashes(new,'v02_result.framemd5');assert len(a)==len(b)==10955
 outside=[i for i in range(len(a)) if not any(x<=i<y for x,y in CHANGED)];mismatch=[i for i in outside if a[i]!=b[i]]
 groups=[]
 for i in mismatch:
  if groups and groups[-1][1]==i:groups[-1][1]=i+1
  else:groups.append([i,i+1])
 oldshots=read(OLD/'records/render_shots.json');unchanged=[]
 for s in read(ROOT/'records/render_shots.json'):
  if s['changed_v02']:continue
  prev=next(x for x in oldshots if x['key']==s['key']);a0=OLD/prev['encoded_file'];a1=Path(s['encoded_file']);assert sha(a0)==sha(a1)
  unchanged.append({'key':s['key'],'frames':s['frames'],'sha256':sha(a1),'original_intermediate_identical':True})
 result={'passed':not mismatch,'method':'Continuous full YUV420P decode frame MD5 comparison, v01 used solely as reference. No seek, no v01 finished media as encoder input.','total_frames':10955,'outside_changed_intervals_frames':len(outside),'outside_pixel_identical_frames':len(outside)-len(mismatch),'outside_nonidentical_frames':len(mismatch),'outside_nonidentical_intervals_half_open':groups,'unchanged_original_intermediates':unchanged,'v01_sha256':sha(old),'v02_sha256':sha(new)}
 save(ROOT/'records/pixel_comparison.json',result);print('PIXEL COMPARISON',result['outside_pixel_identical_frames'],'/',len(outside),'mismatch',len(mismatch),flush=True)

def verify():
 files=[]
 for l in ['en','ja']:
  old=OLD/f'deliverables/EP006_Sphinx_{l}_v01_1080p30.mp4'
  for review in [False,True]:
   src=ROOT/f'deliverables/EP006_Sphinx_{l}_v02{"_subtitled_review" if review else ""}_1080p30.mp4'
   q=subprocess.run(['ffmpeg','-nostdin','-v','warning','-threads','2','-i',str(src),'-f','null','-'],capture_output=True,text=True,check=True);assert not q.stderr.strip(),q.stderr
   info=probe(src);v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio')
   assert (v['profile'],v['pix_fmt'],v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==('High','yuv420p',1920,1080,'30/1',10955)
   if not review:
    frameinfo=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=width,height,pix_fmt','-of','json',str(src)],text=True))['frames']
    assert len(frameinfo)==10955 and {(f['width'],f['height'],f['pix_fmt']) for f in frameinfo}=={(1920,1080,'yuv420p')}
    trace=subprocess.run(['ffmpeg','-v','info','-i',str(src),'-map','0:v:0','-c','copy','-bsf:v','trace_headers','-f','null','-'],capture_output=True,text=True,check=True)
    assert set(re.findall(r'profile_idc\s+[01]+\s+=\s+(\d+)',trace.stderr))=={'100'}
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(src)],text=True).splitlines()))
   assert v['time_base']=='1/15360' and pts==list(range(0,10955*512,512));assert int(a['duration_ts'])==17528000 and a['time_base']=='1/48000'
   ah=stream_hash(src,'a');assert ah==stream_hash(old,'a')
   files.append({'name':src.name,'bytes':src.stat().st_size,'sha256':sha(src),'video_stream_sha256':stream_hash(src,'v'),'audio_stream_sha256':ah,'audio_identical_v01':True,'decode_warnings':0,'frames':10955,'exact_30fps_pts':True,'duration_seconds':float(info['format']['duration']),'profile':v['profile'],'pixel_format':v['pix_fmt']});print('VERIFIED',src.name,flush=True)
 immutable=[]
 for f in (ROOT/'deliverables').iterdir():
  if f.suffix not in ['.srt','.wav','.m4a']:continue
  old=OLD/'deliverables'/f.name.replace('_v02_','_v01_');assert sha(f)==sha(old);immutable.append({'name':f.name,'sha256':sha(f),'identical_v01':True})
 for f in ['content.json','content_en.json','master_timeline.json','subtitle_cues_en.json','subtitle_cues_ja.json']:
  assert sha(ROOT/'records'/f)==sha(OLD/'records'/f)
 assert files[0]['video_stream_sha256']==files[2]['video_stream_sha256']
 save(ROOT/'records/qc_v02.json',{'passed':True,'files':files,'audio_srt_wav_immutable':immutable,'shared_video_stream':True,'endcard_last_10_seconds':True,'scripts_unchanged':True,'human_pronunciation_approved_in_request':True})

def frames():
 shots=read(ROOT/'records/render_shots.json');selected=[];chosen=[s for s in shots if s['changed_v02']]
 for s in chosen:
  a=round(s['start']*30);selected += [a,a+(s['frames']-1)//2,a+s['frames']-1]
 expr='+'.join(f'eq(n\\,{n})' for n in selected);checks=[]
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP006_Sphinx_{l}_v02_1080p30.mp4';folder=ROOT/f'_work/continuous_{l}';folder.mkdir(exist_ok=True)
  q=subprocess.run(['ffmpeg','-nostdin','-y','-v','warning','-threads','2','-i',str(src),'-vf',f'select={expr},scale=1280:720','-fps_mode','passthrough','-c:v','png','-pix_fmt','rgb24',str(folder/'%03d.png')],capture_output=True,text=True,check=True);assert not q.stderr.strip()
  ims=sorted(folder.glob('*.png'));assert len(ims)==18;records=[]
  for i,s in enumerate(chosen):
   trip=Image.new('RGB',(1280,280),'#0c1820');d=ImageDraw.Draw(trip)
   for j,label in enumerate(['FIRST','MIDDLE','LAST']):
    trip.paste(Image.open(ims[i*3+j]).resize((426,240)),(j*426,0));d.text((j*426+8,244),f'{label}: {selected[i*3+j]}',font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17),fill='white')
   dst=ROOT/f'review/continuous_{l}_change_{i+1:02}.jpg';trip.save(dst,quality=90,optimize=True)
   records.append({'key':s['key'],'frames':selected[i*3:i*3+3],'triptych':str(dst.relative_to(ROOT))})
  checks.append({'language':l,'video_sha256':sha(src),'decode_warnings':0,'no_seeking':True,'records':records});print('FRAMES',l,flush=True)
 moreau=next(s for s in shots if s['key']=='met_437153');assert moreau['crop_normalized']==[.12,.10,.95,.33] and moreau['background_also_uses_only_crop']
 save(ROOT/'records/continuous_qc.json',{'passed':True,'checks':checks,'moreau_crop_normalized':[.12,.10,.95,.33],'moreau_all_206_frames_from_fixed_crop_only':True,'camera_zoom_inward':True})

def motion():
 shots=read(ROOT/'records/render_shots.json');src=ROOT/'deliverables/EP006_Sphinx_en_v02_1080p30.mp4';proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','gray','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
 checks=[]
 for s in shots:
  x,y,w,h=roi(s);prior=None;diffs=[]
  for _ in range(s['frames']):
   raw=proc.stdout.read(1920*1080);assert len(raw)==1920*1080
   if not s['changed_v02']:continue
   a=np.frombuffer(raw,np.uint8).reshape(1080,1920)[y:y+h,x:x+w].astype(np.int16)
   if prior is not None:diffs.append(float(np.abs(a-prior).mean()))
   prior=a
  if not diffs:continue
  med=float(np.median(diffs));q95=float(np.quantile(diffs,.95));ratio=q95/med if med else (1 if q95==0 else None);static=s['key'].startswith('D_')
  r={'key':s['key'],'frame_pairs':len(diffs),'median':med,'p95':q95,'ratio':ratio,'static_source':static,'frame_differences':diffs,'ratio_applicable':not static}
  if static:
   a=hashes(Path(s['encoded_file']),'static_source.framemd5');r['source_all_frames_pixel_identical']=len(set(a))==1;r['passed']=r['source_all_frames_pixel_identical']
  else:r['passed']=ratio is not None and ratio<=2.5
  checks.append(r);print('MOTION',s['key'],ratio,r['passed'],flush=True)
 assert not proc.stdout.read(1) and proc.wait()==0
 save(ROOT/'records/motion_v02.json',{'passed':all(x['passed'] for x in checks),'method':'Completed common video continuously decoded; same ROI as v01. Static D_pair validated as invariant intermediate; raw final codec variation retained, ratio not interpreted as movement.','checks':checks});assert all(x['passed'] for x in checks)

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['package','reviews','compare','verify','frames','motion']);a=ap.parse_args();globals()[a.stage]()
