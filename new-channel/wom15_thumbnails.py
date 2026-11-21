"""Approved Savoldo and Sandir photographs for the two editorial thumbnails."""
from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
HERE=Path(__file__).resolve().parent
DEST=HERE/'サムネ確認用/wom15'
SRC=Path('/Volumes/ESD-02/新チャンネル/EP015_December25/素材')
FONT='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
COLOR='#fff3cb'
def centered(draw,words,rect,size):
 x,y,r,b=rect
 font=ImageFont.truetype(FONT,size)
 box=draw.multiline_textbbox((0,0),words,font=font,align='center',spacing=0)
 draw.multiline_text(((x+r-box[2]-box[0])/2,(y+b-box[3]-box[1])/2),words,font=font,fill=COLOR,align='center',spacing=0,stroke_width=1,stroke_fill='#453523')

def run():
 panel=Image.new('RGB',(360,121),'#eee5cd')
 for i,key in enumerate('AB'):
  im=Image.new('RGB',(1280,720),'#201a16')
  if key=='A':
   src=Image.open(SRC/'D01-A.jpg')
   art=ImageOps.fit(src,(1280,650),centering=(.5,1))
   im.paste(art);d=ImageDraw.Draw(im)
   d.rounded_rectangle((28,20,463,215),radius=10,fill='#201a16')
   centered(d,'WHY\nDEC 25?',(35,17,456,213),91)
  else:
   coin=Image.open(SRC/'D04-B.jpg').convert('RGB')
   coin=ImageOps.fit(coin,(730,650),centering=(.5,.5))
   ImageDraw.Draw(im).rectangle((0,0,745,650),fill='white')
   im.paste(coin,((764-coin.width)//2,(650-coin.height)//2))
   d=ImageDraw.Draw(im);centered(d,"THE SUN'S\nBIRTHDAY?",(733,85,1260,565),86)
  d.rectangle((0,650,1280,720),fill='#201a16')
  centered(d,'QUIET ORIGINS',(0,652,1280,716),47)
  path=DEST/f'wom15_サムネ{key}.jpg';im.save(path,quality=93,optimize=True);assert path.stat().st_size<1_000_000
  panel.paste(im.resize((168,95),Image.Resampling.LANCZOS),(5+181*i,23))
  ImageDraw.Draw(panel).text((6+181*i,4),key,fill='#201a16',font=ImageFont.truetype(FONT,16))
 panel.save(DEST/'wom15_サムネAB_168px.jpg',quality=95)
if __name__=='__main__':run()
