"""Actual v09 splice/subtitle samples and chapter-frame correspondence."""
import subprocess
import numpy as np
from PIL import Image,ImageDraw
from wom01_integrate_brand import ROOT,OLD,CUT,DURATION,read,save
from wom01_subtitled_review import selected_bottom_frames

def frame(video,t,width=640):
 data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',str(video),'-frames:v','1','-vf',f'scale={width}:-1','-f','rawvideo','-pix_fmt','rgb24','-'])
 return np.frombuffer(data,np.uint8).reshape(width*9//16,width,3)

def main():
 rows=[]
 for lang in ['en','ja']:
  clean=ROOT/f'deliverables/EP001_Anubis_{lang}_v09_1080p30.mp4';review=ROOT/f'subtitled_review/deliverables/EP001_Anubis_{lang}_v09_subtitled_review_1080p30.mp4'
  times=[29.2,29.7,30.2,30.7,31.2,31.7,32.2,32.7]+list(np.arange(682.1,702,.5));frames=[round(t*30) for t in times]
  a=selected_bottom_frames(clean,frames);b=selected_bottom_frames(review,frames);counts=[]
  for x,y in zip(a,b):
   n=int(((y.mean(2)-x.mean(2)>35)&(y.mean(2)>140)).sum());assert n<80,n;counts.append(n)
  samples=[27.0,29.3,31.,33.7,679.8,681.9,682.35,683.2,701.5]
  sheet=Image.new('RGB',(1280,260*3),(12,24,32));draw=ImageDraw.Draw(sheet)
  for i,t in enumerate(samples):
   im=Image.fromarray(frame(review,t));im.thumbnail((426,240));x=(i%3)*426;y=(i//3)*260;sheet.paste(im,(x,y+20));draw.text((x+8,y+3),f'{lang} {t:.2f}s',fill='white')
  sheet.save(ROOT/f'review/splices_{lang}_storyboard.jpg',quality=90)
  rows.append({'lang':lang,'blank_intervals_checked':[[CUT,CUT+4],[682,702]],'sample_times':times,'new_caption_pixels':counts,'all_passed':True})
 chapters=[]
 for c in read(ROOT/'records/chapters.json')['chapters']:
  actual=c['actual_seconds'];src=0.1 if actual==0 else actual-4+.1;target=actual+.1
  a=frame(OLD/'deliverables/EP001_Anubis_en_v08_1080p30.mp4',src);b=frame(ROOT/'deliverables/EP001_Anubis_en_v09_1080p30.mp4',target)
  mae=float(np.abs(a.astype(float)-b).mean());assert mae<4,mae
  chapters.append({**c,'comparison_mean_absolute_pixel_error':mae,'within_one_second':actual-c['display_seconds']<1})
 save(ROOT/'records/brand_subtitle_absence.json',{'passed':True,'languages':rows})
 save(ROOT/'records/chapter_frame_checks.json',{'passed':True,'chapters':chapters})
 print('SPLICE SHEETS + BLANK SUBTITLES + CHAPTERS PASS',flush=True)
if __name__=='__main__':main()
