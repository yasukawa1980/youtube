"""v02: keep the mouth and lower fangs above the brand strip; 24px B text clearance."""
from PIL import Image,ImageDraw,ImageFont
from wom14_v02 import ROOT,BASE,REPO,save,sha
from wom14_scenes import ASSETS,boxpx
from wom14_thumbnails import lettering,FONT

def run():
 dst=ROOT/'deliverables';repo=REPO/'new-channel/サムネ確認用/wom14';repo.mkdir(parents=True,exist_ok=True)
 src=Image.open(ASSETS['O01-A']['original_path']).convert('RGB')
 # v01 kept the eye size but the footer covered the bottom fangs. Lift artwork by 80px.
 crop=src.crop(boxpx('O01-A',(.22,.225,.80,.465)));face=crop.resize((760,760),Image.Resampling.LANCZOS)
 records=[]
 for key in ['A','B']:
  im=Image.new('RGB',(1280,720),'#261d18');im.paste(face,(0,-110))
  if key=='A':lettering(im,'WHY\nTIGER\nSKIN?',(785,95,1255,575),120)
  else:
   ImageDraw.Draw(im).rectangle((755,0,1280,720),fill='#261d18');lettering(im,'THE FIRST ONI\nWORE A HAT',(785,35,1260,275),71)
   hat=Image.open(ASSETS['O03-23']['original_path']).convert('RGB').crop(boxpx('O03-23',(.26,.47,.307,.61)));hat.thumbnail((320,310));x=(755+1280-hat.width)//2;im.paste(hat,(x,310));ImageDraw.Draw(im).rectangle((x-3,307,x+hat.width+3,313+hat.height),outline='#ead4a9',width=3)
  ImageDraw.Draw(im).rectangle((0,638,1280,720),fill='#261d18');lettering(im,'QUIET ORIGINS',(40,647,1240,703),44)
  for d in [dst,repo]:im.save(d/f'EP014_thumbnail_{key}_v02.jpg',quality=94,optimize=True)
  records.append(dict(variant=key,source_crop_fraction=[.22,.225,.80,.465],face_size=[760,760],face_offset=[0,-110],v01_face_offset=[0,-30],eye_scale_unchanged=True,footer_top=638,art_right=755 if key=='B' else 760,text_box_left=785,minimum_text_clearance=30 if key=='B' else 25,bytes=(dst/f'EP014_thumbnail_{key}_v02.jpg').stat().st_size))
 panel=Image.new('RGB',(400,145),'#e9ddc4');d=ImageDraw.Draw(panel)
 compare=Image.new('RGB',(1280,770),'#261d18');cd=ImageDraw.Draw(compare)
 for i,key in enumerate(['A','B']):
  im=Image.open(dst/f'EP014_thumbnail_{key}_v02.jpg');panel.paste(im.resize((168,95),Image.Resampling.LANCZOS),(16+i*200,28));d.text((16+i*200,8),key,fill='#382a24')
  before=Image.open(BASE/'deliverables'/f'EP014_thumbnail_{key}_v01.jpg');compare.paste(before.resize((640,360)),(0,i*385+25));compare.paste(im.resize((640,360)),(640,i*385+25));cd.text((5,i*385+5),key+' v01',fill='white');cd.text((645,i*385+5),key+' v02',fill='white')
 for folder in [dst,repo]:panel.save(folder/'EP014_thumbnail_AB_168px_v02.jpg',quality=95)
 compare.save(ROOT/'en/review/thumbnail_before_after_v02.jpg',quality=90)
 save(ROOT/'records/thumbnails_v02.json',records)
if __name__=='__main__':run()
