import argparse,csv,json,hashlib,subprocess
from pathlib import Path
import numpy as np
from wom09_produce import ROOT,read,save,sha
def roi(shot):
 if shot.get('wide_pan'):return [260,180,1400,350]
 boxes=shot.get('art_boxes',[])
 if boxes:
  b=max(boxes,key=lambda b:(b[2]-b[0])*(b[3]-b[1]));x0,y0,x1,y1=b;dx=(x1-x0)*.15;dy=(y1-y0)*.15;x,y=round(x0+dx),round(y0+dy);w,h=round(x1-x0-2*dx),round(y1-y0-2*dy)
  return [max(0,x),max(0,y),min(w,1920-x),min(h,1080-y)]
 return [200,200,1520,480]

def motion_stats(path,rect):
 signature=hashlib.sha256((sha(path)+json.dumps(rect)+'gray-exact-passthrough-v2').encode()).hexdigest();cache=ROOT/'_work/motion_cache'/f'{signature}.json'
 if cache.exists():return read(cache)
 x,y,w,h=rect;cmd=['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(path),'-vf',f'format=gray,crop={w}:{h}:{x}:{y}:exact=1','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE);prior=None;ds=[];n=w*h
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
