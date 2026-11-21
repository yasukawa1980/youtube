"""Native-resolution artwork, source boxes and bilingual museum captions for EP015."""
import re
from functools import lru_cache
from PIL import Image,ImageDraw
from wom15_boards import Plate,font,PAPER,INK,SOFT,VERMILION
from wom15_voice import HERE,ROOT,read
MANIFEST=read(HERE/'research/wom15_素材台帳_20261120.json')
ASSETS={a['candidate_id']:a for a in MANIFEST['assets'] if a['candidate_id'] not in {'D05-B','D06-I','D11-B','D13-B','D17-B','D17-C'}}
SCRIPT=(HERE/'wom15_制作依頼_20261121.md').read_text()
LABELS={};NOTES={}
for ln in SCRIPT.splitlines():
 m=re.match(r'^- \*\*(D\d\d-[AT])\*\*',ln)
 if not m:continue
 quoted=re.findall(r'札[ ：]*\**`([^`]+)`',ln)
 if quoted:LABELS[m[1]]=quoted[0]
 quoted=re.findall(r'注[： ]+`([^`]+)`',ln)
 if quoted:NOTES[m[1]]=quoted[0]
for k in ASSETS:
 if k.startswith('D04'):LABELS[k]='COIN · PHOTO: SANDIR (CC0)｜硬貨・写真 Sandir（CC0）'
 elif k not in LABELS:LABELS[k]='PAINTING｜絵画'
BOXES={
 'D02-A':[(.05,.44,.72,.63)], 'D03-A':[(.08,.55,.79,.66)],
 'D05-A':[(.148,.300,.701,.320)], 'D06-A':[(.465,.732,.804,.748)],
 'D07-A':[(.21,.43,.49,.79),(.49,.42,.78,.78)],
 'D08-A':[(.33,.457,.63,.585)],'D09-A':[(.32,.61,.955,.65)],
 'D10-A':[(.16,.61,.72,.65)],'D12-A':[(.056,.074,.380,.109),(.055,.147,.382,.179)],
 'D14-A':[(.287,.549,.945,.569),(.287,.579,.947,.601)],
 'D16-A':[(.18,.523,.597,.548)]}
@lru_cache(maxsize=2)
def original(k):
 im=Image.open(ASSETS[k]['original_path']).convert('RGB')
 return im.transpose(Image.Transpose.ROTATE_90) if k=='D08-A' else im
def lines(t,w,sz,face,s):
 d=ImageDraw.Draw(Image.new('L',(1,1)));f=font(sz*s,face)
 isja=bool(re.search(r'[ぁ-龯]',t))
 tokens=list(t) if isja else t.split();sep='' if isja else ' '
 parts=[];line=''
 for token in tokens:
  new=sep.join([line,token]) if line else token
  if line and d.textlength(new,font=f)>w*s:parts.append(line);line=token
  else:line=new
 if line:parts.append(line)
 return parts

def block(p,t,x,y,w,size,face,color=INK):
 for ln in lines(t,w,size,face,p.s):
  f=font(size*p.s,face);p.d.text((x*p.s,y*p.s),ln,font=f,fill=color,anchor='lt')
  bounds=p.d.textbbox((x*p.s,y*p.s),ln,font=f,anchor='lt')
  p.metrics.append(dict(text=ln,font_px=size*p.s,ink_box=list(bounds),color=color))
  y+=round(size*1.31)
 return y

def art(k,s,u=0,idx=0,highlight=False):
 p=Plate(s);im=original(k);iw,ih=im.size;a=ASSETS[k];page=k in BOXES or k=='D05-T'
 if k=='D01-A':
  # Keep the illuminated child, white cloth and the hands immediately above in the opening.
  # The 4K picture reaches native sampling at maximum magnification.
  scale=min(1.,s*.80)*(1-.09090909*u)
  center=(iw*.489,ih-(1080*s/scale)/2)
  area=(0,0,1920,1080)
 else:
  area=(690,0,1920,1080);aw=1230*s;ah=1080*s
  overview=min(aw/iw,ah/ih,1.)
  center=(iw/2,ih/2);scale=overview
  if k in BOXES:
   box=BOXES[k][idx];x,y,r,b=box
   dest=min(1.,aw/((r-x)*iw*1.14),ah/((b-y)*ih*1.25))
   scale=overview+(dest-overview)*u
   cx=iw*(x+r)/2;cy=ih*(y+b)/2
   center=((iw/2)*(1-u)+cx*u,(ih/2)*(1-u)+cy*u)
  elif k!='D05-T':scale=min(1,overview*(1+.045*u))
  else:center=(iw/2+iw*(u-.5)*.012,ih/2)
 x,y,r,b=area;ow=(r-x)*s;oh=(b-y)*s
 cx,cy=center
 # Constrain a crop to the page when it fills the panel, and otherwise show its paper edge.
 def anchor(c,dim,span):
  return max(span/2,min(dim-span/2,c)) if dim>=span else dim/2
 cx=anchor(cx,iw,ow/scale);cy=anchor(cy,ih,oh/scale)
 left=cx-ow/(2*scale);top=cy-oh/(2*scale)
 tile=im.transform((ow,oh),Image.Transform.AFFINE,(1/scale,0,left,0,1/scale,top),Image.Resampling.BICUBIC,fillcolor=PAPER)
 p.im.paste(tile,(x*s,y*s))
 rect=None
 if highlight and k in BOXES and k!='D08-A':
  x0,y0,x1,y1=BOXES[k][idx]
  rect=[round(x*s+(v*iw-left)*scale) if i%2==0 else round(y*s+(v*ih-top)*scale) for i,v in enumerate([x0,y0,x1,y1])]
  p.d.rectangle(rect,outline=VERMILION,width=2*s)
 if k=='D01-A':
  # Place identification on the upper edge, clear of the child and the subtitle band.
  p.box((0,0,710,128),INK)
  block(p,LABELS[k],24,9,655,19,'ja',PAPER)
  block(p,a['title'],24,37,655,32,'header',PAPER)
  block(p,'Giovanni Girolamo Savoldo · 1530s · NGA 1961.9.86',24,88,665,21,'small',PAPER)
 else:
  p.box((0,0,684,1080),PAPER)
  tag,ja=LABELS[k].split('｜');pos=block(p,tag,38,40,610,27,'main')
  pos=block(p,ja,38,pos+3,610,23,'ja',SOFT)+20;p.line([(38,pos),(645,pos)])
  if k in NOTES:
   en,jp=NOTES[k].split('｜');pos=block(p,en,38,pos+27,600,37,'header')
   pos=block(p,jp,38,pos+12,602,27,'ja')
  title=a['title'].split(' ── ')[0]
  y=max(pos+40,568 if page else 292)
  y=block(p,title,38,y,605,31 if page else 44,'header')
  author=a['author'].split(' ／')[0]
  y=block(p,author,38,y+14,605,23,'ja' if re.search('[ぁ-龯]',author) else 'small',SOFT)
  y=block(p,a['date'],38,y+5,602,27,'ja',INK)
  if k not in ['D11-A','D13-A']:
   holding='Sandir / Numista · CC0' if k.startswith('D04') else a['holding'].split('、')[0]
   y=block(p,holding,38,y+10,605,20,'small',SOFT)
  assert y<921,(k,y)
 return p,dict(key=k,scale=scale,source_size=[iw,ih],crop_origin=[left,top],source_box=BOXES[k][idx] if k in BOXES else None,output_box=rect,rotated_ccw=k=='D08-A')

def credits(s):
 p=Plate(s);p.pair('QUIET ORIGINS｜クワイエット・オリジンズ',(130,86,1790,245),70,36,None)
 rows=['Kokoro / Heart (af_heart)     ·     VOICEVOX:冥鳴ひまり','National Gallery of Art     ·     Princeton University Art Museum','Universitätsbibliothek Basel     ·     ETH-Bibliothek Zürich     ·     Zentralbibliothek Zürich','Universitätsbibliothek Heidelberg     ·     Universitäts- und Landesbibliothek Bonn','Internet Archive  /  University of Toronto  ·  Getty Research Institute  ·  Grinnell College','Coin photographs by Sandir / Numista (CC0)','QO_THEME_A02 / Suno']
 p.line([(285,269),(1635,269)])
 for i,t in enumerate(rows):p.text(t,(82,311+73*i,1838,370+73*i),36,'ja' if i==0 else 'small')
 return p
