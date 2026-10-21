"""Inspect actual caption/gap frames and preserve v01 motion inputs."""
import subprocess
import numpy as np
from PIL import Image,ImageDraw
from wom01_opening_revision import ROOT,MROOT,MOLD,OLD,read,save,sha

def sheet(root,name,video,times):
 result=Image.new('RGB',(1280,260*((len(times)+1)//2)),(12,24,32));draw=ImageDraw.Draw(result)
 for i,t in enumerate(times):
  out=root/f'review/{name}_{i:02}.jpg'
  subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-vf','scale=640:360','-q:v','3',str(out)],check=True)
  im=Image.open(out);im.thumbnail((448,252));x=(i%2)*640;y=(i//2)*260
  result.paste(im,(x+184,y));draw.text((x+10,y+10),f'{t:.2f}s',fill='white')
 result.thumbnail((1280,1280));result.save(root/f'review/{name}_storyboard.jpg',quality=90)

p=ROOT/'subtitled_review/deliverables/EP001_Anubis_ja_v08_subtitled_review_1080p30.mp4'
sheet(ROOT,'ja_N01',p,[3,5.1,7,9.8,12,15.4,18,20.7,23,26])
for lang in ['ja','en']:
 p=MROOT/f'deliverables/EP001_{lang}_opening_connection_trial_v02.mp4'
 sheet(MROOT,f'connection_{lang}',p,[27,28.5,29.3,30.5,32.7,34.2])
 for t in [29.3,30.5,32.7]:
  raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','crop=1920:180:0:900','-f','rawvideo','-pix_fmt','rgb24','-'])
  a=np.frombuffer(raw,np.uint8).reshape(180,1920,3);assert np.sum(a.mean(axis=2)>150)==0
for line in (MOLD/'deliverables/SHA256SUMS_shared.txt').read_text().splitlines():
 digest,name=line.split('  ',1);assert sha(MOLD/'deliverables'/name)==digest
save(MROOT/'records/additional_checks.json',{'passed':True,'no_episode_captions_during_ident':True,'all_previous_motion_v01_shared_files_preserved':True,'ident_sample_times':[29.3,30.5,32.7]})
print('ACTUAL FRAME SHEETS READY',flush=True)
