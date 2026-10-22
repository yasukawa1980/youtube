"""v02 verification: full-frame-rate foreground motion, unchanged audio/timing, layouts."""
import argparse,json,math,subprocess,shutil,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom02_revision_v02 import ROOT,PREV,REPO,read,save,sha,ff,probe,stream_hash

def roi(shot):
 if shot.get('wide_pan'):return [260,180,1400,350]
 boxes=shot.get('art_boxes',[])
 if boxes:
  b=max(boxes,key=lambda b:(b[2]-b[0])*(b[3]-b[1]));x0,y0,x1,y1=b;dx=(x1-x0)*.15;dy=(y1-y0)*.15;x,y=round(x0+dx),round(y0+dy);w,h=round(x1-x0-2*dx),round(y1-y0-2*dy)
  return [max(0,x),max(0,y),min(w,1920-x),min(h,1080-y)]
 return [200,200,1520,480]

def motion_stats(path,rect):
 signature=hashlib.sha256((sha(path)+json.dumps(rect)+'gray-exact-fullrate-v1').encode()).hexdigest();cache=ROOT/'_work/motion_cache'/f'{signature}.json'
 if cache.exists():return read(cache)
 x,y,w,h=rect;cmd=['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(path),'-vf',f'format=gray,crop={w}:{h}:{x}:{y}:exact=1','-f','rawvideo','-pix_fmt','gray','-'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE);prior=None;ds=[];n=w*h
 while True:
  data=p.stdout.read(n)
  if not data:break
  assert len(data)==n
  a=np.frombuffer(data,dtype=np.uint8).astype(np.int16)
  if prior is not None:ds.append(float(np.abs(a-prior).mean()))
  prior=a
 assert p.wait()==0 and ds
 med=float(np.median(ds));q95=float(np.quantile(ds,.95));result={'roi_xywh':rect,'frame_pairs':len(ds),'median_mad_8bit':med,'p95_mad_8bit':q95,'p95_over_median':q95/med if med else (1 if q95==0 else None),'frame_differences':ds}
 save(cache,result);return result

def baseline():
 for s in read(PREV/'records/render_shots.json'):
  if s['segment_id']=='BRAND':continue
  q=motion_stats(PREV/s['encoded_file'],roi(s));print('BASELINE',s['segment_id'],s['key'],round(q['p95_over_median'],3),flush=True)

def motion(limit=0):
 old=read(PREV/'records/render_shots.json');new=read(ROOT/'records/render_shots.json') if (ROOT/'records/render_shots.json').exists() else []
 if not new:
  manifest=iter(read(ROOT/'records/visual_manifest.json')['shots']);new=[]
  for i,s in enumerate(old):
   if s['segment_id']=='BRAND':new.append(s)
   else:new.append({**next(manifest),**{k:s[k] for k in ['start','end','frames']},'encoded_file':f'_work/render/{s["segment_id"]}_{i+1:02}_subpixel.mp4'})
 checks=[]
 for i,(a,b) in enumerate(zip(old,new)):
  if a['segment_id']=='BRAND':continue
  before=motion_stats(PREV/a['encoded_file'],roi(a));after=motion_stats(ROOT/b['encoded_file'],roi(b))
  assert before['frame_pairs']==a['frames']-1 and after['frame_pairs']==b['frames']-1
  passed=after['p95_over_median'] is not None and after['p95_over_median']<=2.5
  checks.append({'shot_index':i+1,'segment_id':a['segment_id'],'before_key':a['key'],'after_key':b['key'],'start':a['start'],'end':a['end'],'before':before,'after':after,'passed':passed,'before_encoded_sha256':sha(PREV/a['encoded_file']),'after_encoded_sha256':sha(ROOT/b['encoded_file'])})
  print('MOTION',i+1,a['segment_id'],f"{before['p95_over_median']:.3f}",f"{after['p95_over_median']:.3f}",passed,flush=True)
  if limit and len(checks)>=limit:break
 report={'method':'Every decoded frame at 30fps, grayscale 8-bit foreground ROI. Mean absolute pixel difference between consecutive frames. Interior 70% of largest foreground image; diagrams use x200,y200,w1520,h480; H02 pan uses x260,y180,w1400,h350. No downsampling, temporal filtering, dropped samples or percentile trimming. Same algorithm for v01/v02; layout-specific ROI follows the enlarged artwork.','threshold':2.5,'shots':checks,'all_passed':all(x['passed'] for x in checks),'complete':len(checks)==37,'full_frame_pair_count_per_version':sum(x['after']['frame_pairs'] for x in checks),'failures':[x['shot_index'] for x in checks if not x['passed']]}
 save(ROOT/'records'/('motion_comparison.json' if not limit else 'motion_sample.json'),report)
 print('MOTION SUMMARY',len(checks),report['all_passed'],report['failures'],flush=True)

def verify():
 old=read(PREV/'records/render_shots.json');new=read(ROOT/'records/render_shots.json');assert len(old)==len(new)==39
 assert [(s['start'],s['end'],s['frames']) for s in old]==[(s['start'],s['end'],s['frames']) for s in new]
 assert sha(PREV/'records/master_timeline.json')==sha(ROOT/'records/master_timeline.json')
 allfiles=[]
 for l in ['en','ja']:
  src=PREV/f'deliverables/EP002_Halloween_{l}_v01_1080p30.mp4';audiohash=stream_hash(src,'a');srt=ROOT/f'deliverables/EP002_Halloween_{l}_v02_1080p30.srt';assert sha(src.with_suffix('.srt'))==sha(srt)
  for review in [False,True]:
   p=ROOT/f'deliverables/EP002_Halloween_{l}_v02{"_subtitled_review" if review else ""}_1080p30.mp4';ff(['-i',p,'-f','null','-']);d=probe(p);v=next(s for s in d['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==11930 and v['avg_frame_rate']=='30/1'
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert v['time_base']=='1/15360' and pts==list(range(0,11930*512,512))
   assert abs(float(d['format']['duration'])-397.6666666667)<1/30
   ah=stream_hash(p,'a');assert ah==audiohash
   allfiles.append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'video_stream_sha256':stream_hash(p,'v'),'audio_stream_sha256':ah,'audio_identical_to_v01':True,'srt_sha256':sha(srt),'srt_identical_to_v01':True,'full_decode':True,'exact_pts_30fps':True,'frames':11930,'duration_seconds':float(d['format']['duration'])})
   print('VERIFIED',p.name,flush=True)
 assert allfiles[0]['video_stream_sha256']==allfiles[2]['video_stream_sha256']==stream_hash(ROOT/'_work/picture_master.mp4','v')
 # Compare every decoded brand frame in final masters, not just the source files.
 def brand_hashes(p):
  expr='between(n\\,1160\\,1279)+between(n\\,11330\\,11929)'
  out=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(p),'-map','0:v:0','-an','-vf',f'select={expr}','-fps_mode','passthrough','-f','framemd5','-'],text=True)
  return [x.rsplit(',',1)[-1].strip() for x in out.splitlines() if not x.startswith('#')]
 b1=brand_hashes(PREV/'deliverables/EP002_Halloween_en_v01_1080p30.mp4');b2=brand_hashes(ROOT/'deliverables/EP002_Halloween_en_v02_1080p30.mp4');assert b1==b2 and len(b1)==720
 assert sha(PREV/'deliverables/EP002_thumbnail_en.jpg')==sha(ROOT/'deliverables/EP002_thumbnail_en.jpg')
 save(ROOT/'records/qc_v02.json',{'passed':True,'duration_seconds':397.6666666667,'frames':11930,'files':allfiles,'shot_timings_identical':True,'audio_and_srt_identical':True,'brand_frames_identical_count':720,'thumbnail_identical':True,'human_full_listening':False})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['motion','verify','baseline']);p.add_argument('--limit',type=int,default=0);a=p.parse_args()
 if a.stage=='motion':motion(a.limit)
 elif a.stage=='baseline':baseline()
 else:verify()
