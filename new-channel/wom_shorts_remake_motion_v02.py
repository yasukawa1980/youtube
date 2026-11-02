"""Measure every adjacent final-video frame within each artwork's common interior."""
import subprocess
import numpy as np
from wom_shorts_remake_v02 import ROOT,read,save,sha
def main():
 shots=read(ROOT/'records/visual_manifest.json')['shots'];heads=read(ROOT/'records/headlines.json');checks=[]
 for s in read(ROOT/'records/shorts.json')['shorts']:
  sid=s['id'];src=ROOT/f'deliverables/QO_short_remake_{sid}_v02.mp4';group=[g for g in shots if g['short_id']==sid]
  p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-pix_fmt','gray','-f','rawvideo','-'],stdout=subprocess.PIPE)
  for g in group:
   vps=[k['viewport'] for k in g['keyframes']] if 'keyframes' in g else [g['viewport']]
   x0=max(v[0] for v in vps);y0=max(300,max(v[1] for v in vps));x1=min(v[0]+v[2] for v in vps);y1=min(1010,min(v[1]+v[3] for v in vps));dx=(x1-x0)*.06;dy=(y1-y0)*.06
   x0,y0,x1,y1=map(round,[x0+dx,y0+dy,x1-dx,y1-dy]);mask=np.ones((y1-y0,x1-x0),bool)
   # Remove all headline plates for the whole first shot, so title fade is not motion.
   if g['start_frame']==0:
    from PIL import Image
    a=np.asarray(Image.open(ROOT/f'assets/{sid}_headline.png').convert('RGBA'))[:,:,3]
    mask&=a[y0:y1,x0:x1]==0
   assert mask.sum()>1000,(sid,g['asset_id'],[x0,y0,x1,y1]);last=None;ds=[]
   for i in range(g['frames']):
    data=p.stdout.read(1080*1920);assert len(data)==1080*1920
    a=np.frombuffer(data,np.uint8).reshape(1920,1080)[y0:y1,x0:x1].astype(np.int16)
    if last is not None:ds.append(float(abs(a-last)[mask].mean()))
    last=a
   med=float(np.median(ds));q95=float(np.quantile(ds,.95));ratio=q95/med if med else None;static=g['asset_id']=='D_timeline'
   checks.append(dict(id=sid,asset=g['asset_id'],roi_xyxy=[x0,y0,x1,y1],pixels=int(mask.sum()),frame_pairs=len(ds),median=med,p95=q95,ratio=ratio,static=static,passed=(q95<.1 if static else ratio is not None and ratio<=2.5),video_sha256=sha(src),frame_differences=ds))
   print('PIXEL MOTION',sid,g['asset_id'],ratio,checks[-1]['passed'],flush=True)
  assert not p.stdout.read(1) and p.wait()==0
 save(ROOT/'records/final_pixel_motion.json',dict(passed=all(x['passed'] for x in checks),method='Unfiltered mean absolute grayscale differences for every adjacent completed-video frame pair. Fixed ROI is the common interior of every keyframe viewport, above captions/CTA, with headline plates masked throughout the first shot. No seeking, zero pairs discarded. Static card uses absolute difference instead of undefined 0/0. Source-coordinate velocity is retained separately and is not a displayed-pixel measure.',checks=checks))
if __name__=='__main__':main()
