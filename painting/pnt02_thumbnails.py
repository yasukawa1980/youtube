"""Two approved thumbnail concepts; native crops, no recolouring or generated pixels."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont

BASE=Path('/Volumes/ESD-02/新チャンネル/PNT02_WashingtonCrossing/素材/Met_97.34')
OUT=Path(__file__).resolve().parent/'サムネ確認用/pnt02'
FONT='/System/Library/Fonts/Supplemental/Arial Bold.ttf'

def text(im,words,xy,size,fill='#fff2d7'):
 d=ImageDraw.Draw(im);f=ImageFont.truetype(FONT,size)
 d.text(xy,words,font=f,fill=fill,stroke_width=3,stroke_fill='#171310')

def main():
 OUT.mkdir(parents=True,exist_ok=True);rows=[]
 # Native 16:9 windows, downsampled to 1280. The flag and Washington's face remain recognizable.
 boxes={'A':('DP245005.jpg',(0,500,2611,1968.6875)),
        'B':('DP-14511-001.jpg',(0,42.5,4000,2292.5))}
 for key,(name,box) in boxes.items():
  src=Image.open(BASE/name).convert('RGB');im=src.resize((1280,720),Image.Resampling.LANCZOS,box=box)
  # Opaque type panels leave source colours unchanged everywhere else.
  dr=ImageDraw.Draw(im);dr.rectangle((0,0,1280,119),fill='#1e1b18');dr.rectangle((0,650,1280,720),fill='#1e1b18')
  if key=='A':
   text(im,'NOT IN 1776?',(36,17),91);text(im,'1851',(1030,540),76)
  else:text(im,'1776 → 1851',(35,17),91)
  text(im,'QUIET ORIGINS',(398,661),42)
  p=OUT/f'pnt02_サムネ_{key}.jpg';im.save(p,quality=93,optimize=True)
  assert p.stat().st_size<1_000_000
  rows.append(dict(concept=key,source=str(BASE/name),native_crop=box,output=[1280,720],scale=1280/(box[2]-box[0]),brightness=1,contrast=1,bytes=p.stat().st_size))
 comparison=Image.new('RGB',(336,95),'#171717')
 for i,key in enumerate(['A','B']):
  with Image.open(OUT/f'pnt02_サムネ_{key}.jpg') as im:comparison.paste(im.resize((168,95),Image.Resampling.LANCZOS),(i*168,0))
 comparison.save(OUT/'pnt02_168px比較.jpg',quality=94)
 (OUT/'thumbnail_metrics.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(rows,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
