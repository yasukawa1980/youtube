"""Measure every adjacent decoded frame inside the artwork, excluding fixed labels and the timeline."""
from wom12_produce import *
import numpy as np

def main():
 m=read(ROOT/'records/render_shots.json');sc=read(ROOT/'records/art_scales.json');master=ROOT/'_work/picture_master.mp4';out=[]
 for row in m:
  k=row['key'];
  if k not in sc or k=='N11-A':continue
  # Inner detail of the art band (not the wide unchanging paper margins).
  a=sc[k];w,h=a['art_size'];lo,hi=a['band'];ww=round(min(w*a['start_scale'],1650)*.70)//2*2;hh=round((hi-lo)*.6)//2*2;x=(1920-ww)//2;y=round(lo+(hi-lo-hh)*.5);n=row['frames'];cmd=['ffmpeg','-nostdin','-v','error','-threads','2','-ss',str(row['start']),'-i',str(master),'-frames:v',str(n),'-vf',f'format=gray,crop={ww}:{hh}:{x}:{y}:exact=1','-pix_fmt','gray','-fps_mode','passthrough','-f','rawvideo','-'];pr=subprocess.Popen(cmd,stdout=subprocess.PIPE);prev=None;diff=[]
  for _ in range(n):
   b=pr.stdout.read(ww*hh);assert len(b)==ww*hh,(k,len(b));cur=np.frombuffer(b,np.uint8).astype(np.int16)
   if prev is not None:diff.append(float(np.abs(cur-prev).mean()))
   prev=cur
  assert pr.wait()==0;median=np.median(diff);p95=np.percentile(diff,95);ratio=float(p95/median) if median else (1 if p95==0 else None);out.append(dict(shot=k,roi=[x,y,ww,hh],adjacent_pairs=n-1,median=float(median),p95=float(p95),ratio=ratio,passed=ratio is not None and ratio<=2.5));print(k,ratio,flush=True)
 save(ROOT/'records/final_video_motion.json',dict(passed=all(i['passed'] for i in out),method='All adjacent frames of each moving content shot in the final picture master. Fixed cards, intentional reveals, static Prang sheet and common brand excluded.',checks=out))
if __name__=='__main__':main()
