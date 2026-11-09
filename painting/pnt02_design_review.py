"""Small review JPGs and analytic checks; these are NOT decoded final-video evidence."""
import io,json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from pnt02_produce import REPO,save
from pnt02_shots import plan
from pnt02_picture import motion
import pnt02_scenes as v

OUT=REPO/'painting/pnt02_確認版_v01_20261110'

def frame(shot,absolute_frame):
 key=shot['key'];offset=absolute_frame-round(shot['start']*30)
 if shot['segment_id']=='BRAND':
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(offset/30),'-i',shot['encoded_file'],'-frames:v','1','-vf','scale=1280:720','-f','image2pipe','-c:v','mjpeg','-'])
  return Image.open(io.BytesIO(b)).convert('RGB')
 stage=next(e for e in shot['stages'] if e['start_frame']<=absolute_frame<e['start_frame']+e['frames'])
 if key not in v.FILES:return v.scene(key,stage['stage'],stage['year']).resize((1280,720),Image.Resampling.LANCZOS)
 im=v.scene(key);info=motion(key,shot['frames'],1);u=offset/max(1,shot['frames']-1)
 # Interpolate zoom parameter, not endpoint rectangles; matches the renderer.
 amount=info['max_zoom']-1;direction=info['motion'];z=1+amount*(1-u if direction=='out' else 1 if direction in ['down','right'] else u)
 l,t,r,b=v.BOXES[key];w,h=r-l,b-t;ax=u if direction=='right' else .47 if 'full' in key else .5;ay=u if direction=='down' else .48 if 'full' in key else .5
 x=l+(w-w/z)*ax;y=t+(h-h/z)*ay
 px=v.ARTMEAS[key]['pasted_box'];xx,yy,x1,y1=map(round,px)
 im.paste(v.artwork(key).resize((x1-xx,y1-yy),Image.Resampling.LANCZOS,box=(x,y,x+w/z,y+h/z)),(xx,yy))
 im=Image.alpha_composite(im.convert('RGBA'),v.art_overlay(key,stage['year'])).convert('RGB')
 return im.resize((1280,720),Image.Resampling.LANCZOS)

def main():
 records=[];font=ImageFont.truetype(v.SANS,19)
 for lang in ['en','ja']:
  shots=plan(lang)['shots'];samples=[]
  for i,s in enumerate(shots):
   f=round(s['start']*30)+(s['frames']-1)//2;im=frame(s,f);p=OUT/f'design_{lang}_{i+1:02d}_{s["key"]}.jpg';im.save(p,quality=88,optimize=True)
   assert p.stat().st_size<1_000_000
   records.append(dict(language=lang,shot=s['key'],frame=f,time=f/30,file=p.name,status='planned_frame_not_final_video'))
   small=im.resize((640,360),Image.Resampling.LANCZOS);ImageDraw.Draw(small).rectangle((0,334,640,360),fill='#171717');ImageDraw.Draw(small).text((8,338),f'DESIGN {lang} {i+1:02d} {s["key"]} / {f/30:.3f}s',font=font,fill='white');samples.append(small)
  for page in range((len(samples)+3)//4):
   sheet=Image.new('RGB',(1280,720),'#171717')
   for j,im in enumerate(samples[page*4:page*4+4]):sheet.paste(im,((j%2)*640,(j//2)*360))
   sheet.save(OUT/f'design_{lang}_sheet_{page+1:02d}.jpg',quality=89,optimize=True)
 save(OUT/'design_review.json',dict(status='design_only_not_final_video_QA',frames=records))
 save(OUT/'corrected_design_metrics.json',v.METR)
 print('Design frames:',len(records),'contact sheets: 10')
if __name__=='__main__':main()
