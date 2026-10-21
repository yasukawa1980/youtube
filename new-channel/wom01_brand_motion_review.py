"""Actual-frame storyboards and sound-envelope QA for the Quiet Origins motion trial."""
import os,json,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw
from wom01_multilingual_render import save,read
R=Path(os.environ['QO_MOTION_ROOT'])

def frame(name,t,out):
 subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-ss',str(t),'-i',str(R/'deliverables'/name),'-frames:v','1','-vf','scale=960:540','-q:v','3',str(out)],check=True)
 return Image.open(out)

def sheet(name,samples):
 out=Image.new('RGB',(1920,390*((len(samples)+2)//3)),(12,24,32));d=ImageDraw.Draw(out)
 for i,(file,t,label) in enumerate(samples):
  p=R/f'review/{name}_{i:02}.jpg';im=frame(file,t,p);im.thumbnail((640,360));xy=((i%3)*640,(i//3)*390);out.paste(im,(xy[0],xy[1]+30));d.text((xy[0]+8,xy[1]+6),label,fill='white')
 out.thumbnail((1280,1280));out.save(R/f'review/{name}.jpg',quality=90)

sheet('opening_storyboard',[('Quiet_Origins_opening_trial_v01.mp4',t,f'Opening {t:.2f}s') for t in [0,.5,1,1.5,2.3,3.9]])
sheet('endcard_storyboard',[('Quiet_Origins_endcard_trial_v01.mp4',t,f'Endcard {t:.2f}s') for t in [0,10,19.9]])
for lang in ['ja','en']:
 samples=[]
 for t in [28.9,31,33.6]:samples.append((f'EP001_{lang}_opening_connection_trial_v01.mp4',t,f'{lang} opening connection {t:.2f}s'))
 for t in [19.5,20.35,21]:samples.append((f'EP001_{lang}_endcard_connection_trial_v01.mp4',t,f'{lang} ending connection {t:.2f}s'))
 sheet(f'connection_{lang}',samples)
checks=[]
for kind in ['opening','endcard']:
 x,sr=sf.read(R/f'deliverables/Quiet_Origins_{kind}_trial_v01.wav');assert sr==48000
 rms=lambda a:float(20*np.log10(max(np.sqrt(np.mean(a*a)),1e-12)))
 first=rms(x[:240]);last=rms(x[-240:]);assert first<-65 and last<-65,(kind,first,last)
 checks.append({'kind':kind,'first_5ms_rms_dbfs':first,'last_5ms_rms_dbfs':last,'max_sample_step':float(np.max(np.abs(np.diff(x,axis=0)))),'peak_amplitude':float(np.max(np.abs(x)))})
# Detect unwanted retained episode captions during the ident.
for lang in ['ja','en']:
 p=R/f'deliverables/EP001_{lang}_opening_connection_trial_v01.mp4'
 for t in [29.3,30.5,32.7]:
  raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(p),'-frames:v','1','-vf','crop=1920:180:0:900','-f','rawvideo','-pix_fmt','rgb24','-'])
  a=np.frombuffer(raw,np.uint8).reshape(180,1920,3);assert np.sum(a.mean(axis=2)>150)==0,(lang,t)
save(R/'records/additional_checks.json',{'passed':True,'sound_envelopes':checks,'no_retained_episode_captions_during_ident':True,'sampled_ident_times':[29.3,30.5,32.7],'actual_frame_sheets':['opening_storyboard.jpg','endcard_storyboard.jpg','connection_ja.jpg','connection_en.jpg']})
print('REVIEW SHEETS + ENVELOPE / CAPTION CHECKS PASS')
