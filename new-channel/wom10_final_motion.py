import os
os.environ.setdefault('WOM10_ROOT','/Volumes/ESD-02/新チャンネル/EP010_Krampus/確認版_v01_20261102')
"""Unfiltered consecutive-frame motion check; explicit diagram reveals checked separately."""
import csv,subprocess
import numpy as np
from wom10_produce import ROOT,read,save,sha
from wom10_motion import roi,motion_stats

def main():
 src=ROOT/'deliverables/EP010_Krampus_en_v01_1080p30.mp4';shots=read(ROOT/'records/render_shots.json')
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
 rows=[{k:c[k] for k in ['key','median','p95','ratio','static_source','motion_ratio_applicable','passed']} for c in checks]
 with (ROOT/'deliverables/EP010_motion_v01.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 assert result['passed'],[(x['key'],x['ratio'],x.get('actual_change_frames')) for x in checks if not x['passed']]
if __name__=='__main__':main()
