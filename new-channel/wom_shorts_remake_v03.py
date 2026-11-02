"""Only subtitle typography changes: fixed font size, never per-line resampling."""
import argparse,shutil,copy
from PIL import Image,ImageDraw,ImageFont
import wom_shorts_remake_v02 as prev
from wom_shorts_remake_produce import read,save,sha
OLD=prev.ROOT;ROOT=OLD.parent/'作り直し_v03_20261103'
FONT=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf',55)
CAP=FONT.getbbox('H')[3]-FONT.getbbox('H')[1]
def prepare():
 for folder in ['assets','audio','records']:shutil.copytree(OLD/folder,ROOT/folder,dirs_exist_ok=True)
 for folder in ['deliverables','review','_work']:(ROOT/folder).mkdir(exist_ok=True)
 caps=read(OLD/'records/caption_manifest.json')
 for c in caps:
  layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer);rows=[]
  for line,y in zip(c['lines'],[1240] if len(c['lines'])==1 else [1198,1294]):
   b=FONT.getbbox(line);w=b[2]-b[0];h=b[3]-b[1];x=round(480-w/2);box=[x-18,y-20,x+w+18,y+60+20];assert box[0]>=80 and box[2]<=880
   d.rounded_rectangle(box,16,fill=(0,0,0,173));d.text((x-b[0],y),line,font=FONT,fill=(244,239,223,255))
   rows.append(dict(text=line,glyph_bbox=list(d.textbbox((x-b[0],y),line,font=FONT)),glyph_height=h,cap_height=CAP,font=FONT.path,font_size=55,horizontal_scale=1,resampling=False,plate_bbox=box))
  p=ROOT/('assets/'+__import__('pathlib').Path(c['file']).name);layer.save(p);c.update(file=str(p),rows=rows)
 save(ROOT/'records/caption_manifest.json',caps)
 for name in ['visual_manifest.json','encoding.json']:
  p=ROOT/'records'/name;p.write_text(p.read_text().replace(str(OLD),str(ROOT)))
 save(ROOT/'records/v03_typography.json',dict(font=FONT.path,font_size=55,cap_height=CAP,per_line_resize=False,unchanged=['script','audio','camera','timing','headline','CTA'],baseline='Same font origin and metrics on every row'))
 print('PREPARED cap height',CAP,flush=True)
def render(ids):
 prev.configure();prev.v1.ROOT=ROOT;prev.v1.render(ids,version='v03')
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('stage');a.add_argument('--ids',default='A1R,M1R,P1R,T1R,A3R');a=a.parse_args()
 if a.stage=='prepare':prepare()
 else:render(a.ids.split(','))
