"""Compare every decoded final-video pixel outside D_summary against v02."""
from wom09_revision_v03 import BASE
from wom09_produce import ROOT,read,save,sha
import subprocess

def frame_hashes(p):
 cmd=['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(p),'-map','0:v:0','-an','-pix_fmt','yuv420p','-f','framemd5','-']
 raw=subprocess.check_output(cmd).decode();return [line.rsplit(',',1)[1].strip() for line in raw.splitlines() if line and not line.startswith('#')]

def main():
 movies=[BASE/'deliverables/EP009_TrojanHorse_en_v02_1080p30.mp4',ROOT/'deliverables/EP009_TrojanHorse_en_v03_1080p30.mp4']
 hashes=[frame_hashes(p) for p in movies];assert len(hashes[0])==len(hashes[1])==11293
 checks=[]
 for s in read(ROOT/'records/render_shots.json'):
  start=round(s['start']*30);end=start+s['frames'];diff=[i for i in range(start,end) if hashes[0][i]!=hashes[1][i]]
  checks.append({'key':s['key'],'frames':s['frames'],'equal_decoded_frames':s['frames']-len(diff),'different_decoded_frames':len(diff),'difference_frame_indices':diff})
 unchanged=[c for c in checks if c['key']!='D_summary'];passed=all(c['different_decoded_frames']==0 for c in unchanged)
 save(ROOT/'records/final_pixel_comparison_v03.json',{'passed':passed,'comparison_complete':True,'scope':'Full-resolution yuv420p decoded frames from both completed main videos, before RGB conversion. All unchanged shots checked at every frame. English/Japanese share the same video stream (verified separately).','videos':[{'path':str(p),'sha256':sha(p)} for p in movies],'checks':checks,'unchanged_shots':23,'unchanged_frames':sum(c['frames'] for c in unchanged),'all_unchanged_final_pixels_equal':passed})
 print('FINAL PIXEL CHECK',passed,[(c['key'],c['different_decoded_frames']) for c in checks],flush=True)

def quantify_differences():
 import numpy as np
 state=read(ROOT/'records/final_pixel_comparison_v03.json');indices=sorted(i for c in state['checks'] if c['key']!='D_summary' for i in c['difference_frame_indices'])
 if not indices:return
 expr='+'.join(f'eq(n\\,{i})' for i in indices);arrays=[]
 for movie in state['videos']:
  raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-threads','2','-i',movie['path'],'-vf',f'select={expr}','-fps_mode','passthrough','-pix_fmt','yuv420p','-f','rawvideo','-'])
  arrays.append(np.frombuffer(raw,np.uint8).reshape(len(indices),1920*1080*3//2))
 diff=np.abs(arrays[0].astype(np.int16)-arrays[1].astype(np.int16));y=diff[:,:1920*1080]
 state.update(comparison_complete=True,compression_difference={'frames':indices,'start_seconds':indices[0]/30,'end_seconds_exclusive':(indices[-1]+1)/30,'yuv_mean_absolute_difference_8bit':float(diff.mean()),'yuv_max_absolute_difference_8bit':int(diff.max()),'luma_mean_absolute_difference_8bit':float(y.mean()),'luma_max_absolute_difference_8bit':int(y.max()),'luma_changed_sample_fraction':float((y!=0).mean()),'reason':'Same source pixels; changed look-ahead context in the required single lossy H.264 encode. v02 keyframe at9224 is four frames before changed summary; preserve source and required encoding method.'})
 save(ROOT/'records/final_pixel_comparison_v03.json',state);print('COMPRESSION DIFFERENCE',state['compression_difference'],flush=True)

if __name__=='__main__':
 main();quantify_differences()
