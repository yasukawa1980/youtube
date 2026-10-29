"""Three full-scene Ferris thumbnails; original painting remains uncropped in height."""
from PIL import Image,ImageDraw,ImageFont,ImageOps
import numpy as np,shutil
from wom08_produce import ROOT,REPO,save,sha
FONT='/System/Library/Fonts/Supplemental/Georgia Bold.ttf';SANS='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def main():
 dest=REPO/'new-channel/サムネ確認用/wom08';dest.mkdir(exist_ok=True,parents=True)
 records=[];files=[]
 for key,title,asset in [('A','NOT IN THE TOMB','B286'),('B','WHO STARTED IT?','B157'),('C','THE CURSE?','B170')]:
  source=Image.open(ROOT/f'assets/{asset}_cropped.png').convert('RGB')
  base=ImageOps.fit(source,(1280,720),Image.Resampling.LANCZOS,centering=(.5,.50))
  arr=np.asarray(base).astype(float);y=np.arange(720);opacity=.68*np.exp(-y/135)+.52*np.exp(-(719-y)/70);arr*=1-opacity[:,None,None];im=Image.fromarray(np.uint8(arr.clip(0,255)))
  d=ImageDraw.Draw(im);size=85
  while d.textlength(title,font=ImageFont.truetype(FONT,size))>1170:size-=1
  f=ImageFont.truetype(FONT,size);x=(1280-d.textlength(title,font=f))/2;d.text((x,22),title,font=f,fill='#fff6dc',stroke_width=2,stroke_fill='#231b16')
  d.text((55,652),'QUIET ORIGINS',font=ImageFont.truetype(SANS,28),fill='#f2d09a',stroke_width=1,stroke_fill='#231b16')
  name=f'wom08_サムネ{key}_20261029.jpg';p=dest/name;im.save(p,quality=92,optimize=True);assert p.stat().st_size<1000000;shutil.copy2(p,ROOT/'deliverables'/name);files.append(p);records.append({'option':key,'title':title,'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'size':[1280,720],'source':asset,'original_scan_colors_preserved':True})
 sheet=Image.new('RGB',(568,140),'#121a21');d=ImageDraw.Draw(sheet)
 for i,p in enumerate(files):
  x=16+184*i;d.text((x,8),chr(65+i),fill='white');sheet.paste(Image.open(p).resize((168,94),Image.Resampling.LANCZOS),(x,30))
 p=dest/'wom08_サムネ168px比較_20261029.jpg';sheet.save(p,quality=94);shutil.copy2(p,ROOT/'deliverables'/p.name);save(ROOT/'records/thumbnail_qc.json',{'outputs':records,'comparison':str(p),'human_choice':'pending'})
 print('THUMBNAILS',[(x['option'],x['bytes']) for x in records])
if __name__=='__main__':main()
