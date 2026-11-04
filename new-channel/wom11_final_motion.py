import os
os.environ.setdefault('WOM11_ROOT','/Volumes/ESD-02/新チャンネル/EP011_WeighingOfTheHeart/確認版_v01_20261104')
"""Unfiltered consecutive-frame motion check; explicit diagram reveals checked separately."""
import csv,subprocess
import numpy as np
from wom11_produce import ROOT,read,save,sha
from wom11_motion import roi,motion_stats

def finalize(result,shots):
 # Static-card reveals can lie outside the art-motion ROI (the fifth denial
 # is below y=680). Check every pixel of each lossless card intermediate.
 for row in result['checks']:
  s=next(s for s in shots if s['key']==row['key'])
  assert row['frame_pairs']==s['frames']-1
  if row['static_source']:
   q=motion_stats(ROOT/s['encoded_file'],[0,0,1920,1080])
   actual=[i+1 for i,v in enumerate(q['frame_differences']) if v!=0]
   expected=s.get('stage_change_frames',[])
   row.update(intermediate=q,stage_change_frames=expected,actual_change_frames=actual,passed=actual==expected,static_validation_roi='full 1920x1080 frame')
  else:
   ds=row['frame_differences'];med=float(np.median(ds));p95=float(np.quantile(ds,.95))
   assert med==row['median'] and p95==row['p95']
   row['passed']=med>0 and p95/med<=2.5
 result.update(passed=all(x['passed'] for x in result['checks']),validation_version=2)
 save(ROOT/'records/final_video_motion.json',result)
 rows=[{k:c[k] for k in ['key','median','p95','ratio','static_source','motion_ratio_applicable','passed']} for c in result['checks']]
 with (ROOT/'deliverables/EP011_motion_v01.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 assert result['passed'],[(x['key'],x['ratio'],x.get('actual_change_frames')) for x in result['checks'] if not x['passed']]
 print('FINAL MOTION VERIFIED',len(rows),flush=True)

def main():
 src=ROOT/'deliverables/EP011_WeighingOfTheHeart_en_v01_1080p30.mp4';shots=read(ROOT/'records/render_shots.json')
 state=ROOT/'records/final_video_motion.json'
 if state.exists() and read(state).get('video_sha256')==sha(src):
  cached=read(state)
  assert cached['decoded_frames']==sum(s['frames'] for s in shots)
  finalize(cached,shots);print('FINAL MOTION CACHE VERIFIED',flush=True);return
 p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','gray','-f','rawvideo','pipe:1'],stdout=subprocess.PIPE);checks=[];total=0
 for s in shots:
  rect=roi(s);x,y,w,h=rect;prior=None;diffs=[]
  for _ in range(s['frames']):
   data=p.stdout.read(1920*1080);assert len(data)==1920*1080;total+=1
   if s['segment_id']=='BRAND':continue
   a=np.frombuffer(data,np.uint8).reshape(1080,1920)[y:y+h,x:x+w].astype(np.int16)
   if prior is not None:diffs.append(float(np.abs(a-prior).mean()))
   prior=a
  if not diffs:continue
  med=float(np.median(diffs));q95=float(np.quantile(diffs,.95));ratio=q95/med if med else None
  static=s['key'].startswith('D_') or s['key']=='credits';q=motion_stats(ROOT/s['encoded_file'],rect)
  row={'key':s['key'],'roi_xywh':rect,'frame_pairs':len(diffs),'median':med,'p95':q95,'ratio':ratio,'maximum_mad':max(diffs),'static_source':static,'frame_differences':diffs,'intermediate':q,'motion_ratio_applicable':not static}
  if static:
   expected=s.get('stage_change_frames',[]);actual=[i+1 for i,v in enumerate(q['frame_differences']) if v!=0]
   row.update(stage_change_frames=expected,actual_change_frames=actual,passed=actual==expected,status='Lossless source is exactly static between requested row reveals; final codec differences retained, not interpreted as motion')
  else:row.update(passed=ratio is not None and ratio<=2.5,status='Every adjacent final-video frame, unfiltered p95/median')
  checks.append(row);print('MOTION',s['key'],ratio,row['passed'],flush=True)
 assert not p.stdout.read(1) and p.wait()==0 and total==round(read(ROOT/'records/master_timeline.json')['duration_seconds']*30)
 result={'passed':all(c['passed'] for c in checks),'video_sha256':sha(src),'decoded_frames':total,'checks':checks,'method':'Continuous completed-video decode with no seeking. Art: unfiltered p95/median <=2.5. Cards: lossless intermediate changes only at explicitly requested reveal frames. Brand excluded; static/card ratios are inapplicable.'};save(ROOT/'records/final_video_motion.json',result)
 finalize(result,shots)
if __name__=='__main__':main()
