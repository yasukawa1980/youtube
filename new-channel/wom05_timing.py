"""Slow the kite's descent using measured source motion, retaining the apparition timing."""
import subprocess,numpy as np
from wom05_produce import ROOT,save,sha
src=ROOT/'assets/V02_softlight_v02.mp4'
p=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',str(src),'-vf','scale=480:270,format=gray,crop=336:188:72:40','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE)
prior=None;ds=[]
while True:
 data=p.stdout.read(336*188)
 if not data:break
 a=np.frombuffer(data,np.uint8).astype(np.int16)
 if prior is not None:ds.append(float(np.abs(a-prior).mean()))
 prior=a
assert p.wait()==0
# Six source frames per bin = 0.25 s at the actual 24fps; preserve the first 4.5 s.
raw=np.array(ds);smoothed=np.convolve(np.pad(raw,(3,3),mode='edge'),np.ones(7)/7,mode='valid')
weights=[]
for a in range(108,240,6):weights.append(float(smoothed[a:min(a+6,len(smoothed))].sum()))
floor=max(weights)*.012;weights=[max(floor,x) for x in weights]
save(ROOT/'records/V02_motion_timing.json',{'source_sha256':sha(src),'source_fps':24,'preserved_first_seconds':4.5,'source_bin_seconds':.25,'source_motion_weights':weights,'method':'After the 4.5 s apparition, allocate time in proportion to measured source motion (7-frame smoothing, 0.25 s bins). Optical-flow interpolation supplies smooth 30fps descent. No source frames removed.'})
print('Motion timing curve',len(weights),flush=True)
