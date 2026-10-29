"""Measure every adjacent frame in the completed common video, without seeking."""
import csv,subprocess,sys
import numpy as np
from wom08_produce import ROOT,read,save,sha
from wom08_motion import roi

def classify(result):
 inputs={s['key']:s['measurement'] for s in read(ROOT/'records/motion_v01.json')['shots']}
 for c in result['checks']:
  if c['static_source']:
   c['source_all_frame_differences_zero']=all(x==0 for x in inputs[c['key']]['frame_differences'])
   c['motion_ratio_applicable']=False
   c['status']='Static source; final codec differences reported, not interpreted as movement'
   c['passed']=c['source_all_frame_differences_zero']
  else:
   c['motion_ratio_applicable']=True;c['passed']=c['ratio'] is not None and c['ratio']<=2.5
 result['passed']=all(c['passed'] for c in result['checks'])
 result['method']='Completed English MP4 continuously decoded, every adjacent frame per shot, same grayscale ROI as intermediate measurement. Shared video stream covers Japanese. Moving sources: raw p95/median <=2.5. Known static sources: lossless intermediate must have every frame difference exactly zero; final raw codec differences and undefined/unstable ratios are retained without modification and excluded from motion-ratio assessment. Brand excluded.'
 save(ROOT/'records/final_video_motion.json',result)
 assert result['passed']
 return result

def main():
 src=ROOT/'deliverables/EP008_Tutankhamun_en_v01_1080p30.mp4';shots=read(ROOT/'records/render_shots.json')
 p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','gray','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE)
 checks=[];total=0
 for s in shots:
  rect=roi(s);x,y,w,h=rect;prior=None;diffs=[]
  for _ in range(s['frames']):
   data=p.stdout.read(1920*1080);assert len(data)==1920*1080
   total+=1
   if s['segment_id']=='BRAND':continue
   a=np.frombuffer(data,np.uint8).reshape(1080,1920)[y:y+h,x:x+w].astype(np.int16)
   if prior is not None:diffs.append(float(np.abs(a-prior).mean()))
   prior=a
  if not diffs:continue
  med=float(np.median(diffs));q95=float(np.quantile(diffs,.95));ratio=q95/med if med else (1 if q95==0 else None)
  static=s['key'].startswith('D_') or s['key']=='credits'
  # A known constant source has no meaningful motion ratio. Its measured
  # output differences remain visible in the report and are never zeroed.
  passed=None if static else ratio is not None and ratio<=2.5
  checks.append(dict(key=s['key'],roi_xywh=rect,frame_pairs=len(diffs),median=med,p95=q95,ratio=ratio,maximum_mad=max(diffs),static_source=static,passed=passed,frame_differences=diffs))
  print('FINAL MOTION',s['key'],ratio,'static' if static else 'moving',passed,flush=True)
 assert not p.stdout.read(1) and p.wait()==0 and total==round(read(ROOT/'records/master_timeline.json')['duration_seconds']*30)
 classify({'video_sha256':sha(src),'decoded_frames':total,'checks':checks})
if __name__=='__main__':
 if '--classify-existing' in sys.argv:
  result=read(ROOT/'records/final_video_motion.json');assert result['video_sha256']==sha(ROOT/'deliverables/EP008_Tutankhamun_en_v01_1080p30.mp4');classify(result)
 else:main()
