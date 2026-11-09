"""Two requested editorial thumbnails from unchanged CC0 / PD source pixels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from wom14_produce import ROOT,REPO,read,save,sha
from wom14_scenes import ASSETS,FOCUS,boxpx
FONT='/System/Library/Fonts/Supplemental/Arial Bold.ttf';SERIF='/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
def lettering(im,s,box,maxsize=110):
 d=ImageDraw.Draw(im)
 for size in range(maxsize,20,-1):
  f=ImageFont.truetype(FONT,size);bb=d.multiline_textbbox((0,0),s,font=f,spacing=8,align='center')
  if bb[2]-bb[0]<=box[2]-box[0] and bb[3]-bb[1]<=box[3]-box[1]:break
 x=(box[0]+box[2]-(bb[2]-bb[0]))/2-bb[0];y=(box[1]+box[3]-(bb[3]-bb[1]))/2-bb[1];d.multiline_text((x,y),s,font=f,spacing=8,align='center',fill='#fff5d9')
def run():
 dest=ROOT/'deliverables';dest.mkdir(exist_ok=True);repo=REPO/'new-channel/サムネ確認用/wom14';repo.mkdir(parents=True,exist_ok=True)
 a=Image.open(ASSETS['O01-A']['original_path']).convert('RGB').crop(boxpx('O01-A',FOCUS['O01-A']))
 for key in ['A','B']:
  im=Image.new('RGB',(1280,720),'#261d18');q=a.resize((760,760),Image.Resampling.LANCZOS);im.paste(q,(0,-30))
  if key=='A':lettering(im,'WHY\nTIGER\nSKIN?',(785,95,1255,575),120)
  else:
   rect=(755,0,1280,720);ImageDraw.Draw(im).rectangle(rect,fill='#261d18');lettering(im,'THE FIRST ONI\nWORE A HAT',(745,35,1270,275),71)
   src=Image.open(ASSETS['O03-23']['original_path']).convert('RGB');hat=src.crop(boxpx('O03-23',(.26,.47,.307,.61)));hat.thumbnail((320,310));im.paste(hat,((755+1280-hat.width)//2,310));ImageDraw.Draw(im).rectangle(((755+1280-hat.width)//2-3,307,(755+1280+hat.width)//2+3,313+hat.height),outline='#ead4a9',width=3)
  ImageDraw.Draw(im).rectangle((0,638,1280,720),fill='#261d18');lettering(im,'QUIET ORIGINS',(40,647,1240,703),44)
  for folder in [dest,repo]:im.save(folder/f'EP014_thumbnail_{key}_v01.jpg',quality=94,optimize=True)
 panel=Image.new('RGB',(400,145),'#e9ddc4');d=ImageDraw.Draw(panel)
 for i,k in enumerate(['A','B']):
  im=Image.open(dest/f'EP014_thumbnail_{k}_v01.jpg');im=im.resize((168,95),Image.Resampling.LANCZOS);panel.paste(im,(16+i*200,28));d.text((16+i*200,8),k,fill='#382a24')
 for folder in [dest,repo]:panel.save(folder/'EP014_thumbnail_AB_168px_v01.jpg',quality=95)
 save(ROOT/'records/thumbnails.json',{'source':'Unchanged source pixels, editorial text and crops only','files':[{'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in dest.glob('*thumbnail*.jpg')],'B_hat_native_box':list(boxpx('O03-23',(.26,.47,.307,.61)))})
if __name__=='__main__':run()
