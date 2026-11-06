"""EP013 native-resolution plates from verified museum pixels; no generated imagery."""
from pathlib import Path
from functools import lru_cache
import os,re,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom13_produce import ROOT,REPO,read,save
from wom13_geometry import crop_native,ITEMS
S=int(os.environ.get('WOM13_SCALE','1')); W,H=1920*S,1080*S
PAPER='#e9ddc4';INK='#382a24';LIGHT='#f8f1dc';MUT='#705744';BAR='#412f25';RUST='#944a35'
FT='/System/Library/Fonts/Supplemental/Georgia.ttf';FB='/System/Library/Fonts/Supplemental/Georgia Bold.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc';SANS='/System/Library/Fonts/Supplemental/Arial.ttf'
YRS=['1642','1678','1715','1797','1946–47','today']
METR=[];ARTMEAS={};CURRENT=''
CROPS={r['id']:r['proposed'] for r in read(REPO/'new-channel/research/wom13_切り出し検証_20261107.json')['proposed_boxes']}
CAT={
 'V05':('PRINT｜版画','Zacharias Webber II · View of the Kloveniersdoelen · 1664','Rijksmuseum, Amsterdam · RP-P-AO-25-25-1 · Public Domain'),
 'V06':('PAINTING｜絵画','Nicolaes Eliasz Pickenoy · Civic Guards under Jan Claesz Vlooswijck · 1642','Rijksmuseum, Amsterdam · SK-C-1177 · Public Domain'),
 'V07':('DRAWING｜素描','Hendrik Spilman, after Berckheyde · Amsterdam Town Hall · 1731–1784','Later exterior view｜後世の外観図 · Rijksmuseum · KOG-AA-2-4-112 · Public Domain'),
 'V08':('PRINT｜版画','Adolphe Mouilleron · La ronde de nuit · 19th century','Rijksmuseum, Amsterdam · RP-P-1896-A-19326 · Public Domain'),
 'V02_L':('COPY｜模写','Attributed to Gerrit Lundens · Copy after The Night Watch · c.1642–55','National Gallery, London, on loan to Rijksmuseum · SK-C-1453 · Public Domain')}
ALBUM=[
 '“…de Jonge Heer van Purmerlandt, als Capiteyn, geeft last aan zijnen Lieutenant, de Heer van Vlaerdingen, om sijn Compaignie Burgers te doen marcheren.”',
 '“…the young lord of Purmerland, as captain, orders his lieutenant, the lord of Vlaardingen, to have his company of citizens march.”',
 '…プルメルラントの若い領主が隊長として、副官であるフラールディンゲンの領主に、市民の一隊を行進させるよう命じている']
HOOG=[[
 '“…maekende meer werks van het groote beelt zijner verkiezing, als van de byzondere afbeeltsels, die hem waren aenbesteet.”',
 '“…making more of the great picture of his own choosing than of the separate portraits he had been commissioned to paint.”',
 '…注文を受けた一人ひとりの肖像よりも、自ら選んだ大きな全体像に力を注いだ'],[
 '“Schoon ik wel gewilt hadde, dat hy \'er meer lichts in ontsteeken had.”',
 '“Though I would have wished that he had put more light into it.”',
 'もっと光を入れてくれていたら、と私は思うのだけれど']]
@lru_cache(None)
def font(face,n=160):return ImageFont.truetype(face,n*S)
def rect(dr,box,**kw):dr.rectangle(tuple(round(v*S) for v in box),**kw)
def line(dr,pts,fill,width=2):dr.line(tuple(round(v*S) for v in pts),fill=fill,width=max(1,round(width*S)))
def txt(im,st,cx,cy,height,face=FT,fill=INK,maxw=1770,major=False,underline=None,box=None):
 f=font(face);l,t,r,b=f.getbbox(st); mask=Image.new('L',(r-l,b-t));ImageDraw.Draw(mask).text((-l,-t),st,font=f,fill=255)
 w=height*(r-l)/(b-t);assert w<=maxw+1,(CURRENT,st,w,maxw)
 ww,hh=round(w*S),round(height*S);x,y=round(cx*S-ww/2),round(cy*S-hh/2);im.paste(fill,(x,y,x+ww,y+hh),mask.resize((ww,hh),Image.Resampling.LANCZOS))
 bounds=[x/S,y/S,(x+ww)/S,(y+hh)/S]
 row=dict(card=CURRENT,text=st,box=bounds,major=major,ink_height=height,foreground=fill,background=LIGHT if box else PAPER)
 if box:row['plate_padding']=min(bounds[0]-box[0],bounds[1]-box[1],box[2]-bounds[2],box[3]-bounds[3])
 METR.append(row)
 if underline and underline in st:
  i=st.index(underline);a=f.getlength(st[:i]);b0=f.getlength(st[:i+len(underline)]);scale=hh/(b-t);ImageDraw.Draw(im).line((round(x+a*scale),y+hh+4*S,round(x+b0*scale),y+hh+4*S),fill=RUST,width=3*S)
 return bounds
def width(st,h,face):
 f=font(face);l,t,r,b=f.getbbox(st);return h*(r-l)/max(1,b-t)
def wrap(st,h,face,maxw=1640):
 tokens=list(st) if face==JA else st.split(' ');sep='' if face==JA else ' ';out=[];cur=''
 for tok in tokens:
  test=cur+sep+tok if cur else tok
  if width(test,h,face)>maxw and cur:out.append(cur);cur=tok
  else:cur=test
 if cur:out.append(cur)
 if face==JA and len(out)>1:
  n=len(out);limit=math.ceil(len(st)/n);out=[st[i:i+limit] for i in range(0,len(st),limit)]
 assert ''.join(out).replace(' ','')==st.replace(' ','')
 return out
def header(im,tag,title='',source=''):
 dr=ImageDraw.Draw(im);rect(dr,(0,0,1920,106),fill=PAPER)
 txt(im,tag,960,18,18,JA);txt(im,title,960,49,25,FT);txt(im,source,960,83,18,JA if any(ord(c)>255 for c in source) else SANS)
 line(dr,(65,105,1855,105),MUT)
def rail(im,yr):
 dr=ImageDraw.Draw(im);rect(dr,(0,915,1920,1080),fill=BAR);line(dr,(120,1008,1800,1008),'#c6b388',3)
 for i,n in enumerate(YRS):
  x=120+i*336;line(dr,(x,1000,x,1017),LIGHT,3)
  # Wide 1946–47 is centred over its tick, with 336 px between neighbours.
  txt(im,n,x,963 if n==yr else 1037,60 if n==yr else 26,FB if n==yr else SANS,LIGHT if n==yr else '#c9bda6',maxw=315,major=n==yr)
def dimensions(id):return ITEMS[id]['width'],ITEMS[id]['height']
@lru_cache(3)
def artwork(k):
 id='V01' if k.startswith('V01') else 'V02' if k in ['D_cut','V02_L'] else k
 w,h=dimensions(id);box=[0,0,w,h]
 if k.startswith('V01_D'):box=[round(v*(w if j%2==0 else h)) for j,v in enumerate(CROPS[k[4:]])]
 if k=='V02_L':box=[0,round(.48*h),round(.37*w),round(.48*h)+round(.37*w*9/16)]
 return crop_native(id,box),box,id
def paste_art(im,k,band=(110,810),full=False):
 a,box,id=artwork(k);lo,hi=band;scale=min(W/a.width,(hi-lo)*S/a.height);size=(round(a.width*scale),round(a.height*scale));q=a.resize(size,Image.Resampling.LANCZOS);x=(W-q.width)//2;y=round(lo*S)+((hi-lo)*S-q.height)//2;im.paste(q,(x,y))
 ARTMEAS[k]=dict(id=id,crop_native_px=box,art_size=list(a.size),band=list(band),start_scale=scale/S,native_output_scale=scale,pasted_box=[x/S,y/S,(x+q.width)/S,(y+q.height)/S])
 return x,y,q.width,q.height
def quote(im,texts,terms):
 dr=ImageDraw.Draw(im);box=(75,147,1845,748);dr.rounded_rectangle(tuple(v*S for v in box),14*S,fill=LIGHT,outline='#bbab8a',width=2*S)
 rows=[]
 for text,h,face,term in zip(texts,[60,35,31],[FT,FT,JA],terms):
  ll=wrap(text,h,face);rows.append((ll,h,face,term))
 total=sum(len(ll)*(h+17)-17 for ll,h,_,_ in rows)+48
 assert total<=550,(CURRENT,total,rows)
 y=447.5-total/2
 for ll,h,face,term in rows:
  for st in ll:txt(im,st,960,y+h/2,h,face,major=h==60,underline=term,box=box);y+=h+17
  y+=7
def sidebar(im,k):
 # Separate overlay; remains fixed as the artwork moves beneath it.
 for i,(st,h) in enumerate([('PAINTING',18),('絵画',18),('Rembrandt',22),('The Night',22),('Watch',22),('1642',29),('Rijksmuseum',17),('SK-C-5',18),('Public Domain',16)]):
  txt(im,st,120,150+i*40,h,JA if st=='絵画' else FT,LIGHT,maxw=215)
def scene(k,stage=0,yr=None):
 global CURRENT;CURRENT=k
 im=Image.new('RGB',(W,H),PAPER)
 if k.startswith('V01_full'):
  im.paste('#14110f',(0,0,W,H));paste_art(im,k,(0,1080),True)
 elif k.startswith('V01_D'):
  paste_art(im,k);header(im,'DETAIL｜部分','The Night Watch · 1642','Rijksmuseum, Amsterdam · SK-C-5 · Public Domain')
 elif k in CAT:
  paste_art(im,k);header(im,*CAT[k])
 elif k=='D_cut':
  im.paste('#14110f',(0,0,W,H));x,y,w,h=paste_art(im,k,(0,1080),True)
  pts=read(REPO/'new-channel/research/wom13_模写対応点_20261107.json')['V01_corners_in_V02_fraction'];poly=[(x+round(px*w),y+round(py*h)) for px,py in pts]
  mask=Image.new('L',(W,H),0);d=ImageDraw.Draw(mask);d.rectangle((x,y,x+w,y+h),fill=89);d.polygon(poly,fill=0)
  if stage==1:d.polygon([(x,y),(poly[0][0],y),poly[0],poly[3],(poly[3][0],y+h),(x,y+h)],fill=0)
  im.paste('#000000',(0,0,W,H),mask);ImageDraw.Draw(im).line(poly+[poly[0]],fill='#e5d3ae',width=2*S)
  # Compact attribution in unused side margins, not over the copy.
  for i,st in enumerate(['SCHEMATIC','模式図','Lundens','(attributed)','Copy, c.1642–55','NG London','on loan to','Rijksmuseum','SK-C-1453','Public Domain']):txt(im,st,112,120+i*39,17 if i else 19,JA if st=='模式図' else FT,LIGHT,maxw=205)
  overlay=Image.new('RGBA',(W,H),(0,0,0,0));rect(ImageDraw.Draw(overlay),(380,25,1540,92),fill=(20,17,15,225));txt(overlay,'Frame: the part that survives today｜枠：いまも残る範囲',960,58,26,JA,LIGHT,maxw=1120);im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB')
 elif k=='D_album':
  header(im,'TITLE CARD｜文字カード','Banninck Cocq family album — caption, as transcribed in Oud Holland, 1886, p.204','バニング・コック家のアルバムの説明（1886年の翻刻）');quote(im,ALBUM,['marcheren','march','行進させる'] if stage else [None]*3)
 elif k=='D_1678':
  header(im,'TITLE CARD｜文字カード','Samuel van Hoogstraten, Inleyding tot de hooge schoole der schilderkonst, Rotterdam, 1678, p.176','ホーホストラーテンの絵画論（1678年）');quote(im,HOOG[stage],['meer lichts','more light','もっと光を'] if stage else [None]*3)
 elif k=='D_1797':
  header(im,'TITLE CARD｜文字カード','A name appears in writing','Rijksmuseum · The Night Watch (SK-C-5)');rect(ImageDraw.Draw(im),(75,147,1845,748),fill=LIGHT);txt(im,'1797',960,310,145,FB,major=True)
  for i,st in enumerate(['the name “the Night Watch” first found in writing','— according to the Rijksmuseum']):txt(im,st,960,485+i*65,40,FT)
  txt(im,'「夜警」の名が文献に初めて現れる',960,647,33,JA);txt(im,'（アムステルダム国立美術館の説明による）',960,697,29,JA)
 elif k=='D_timeline_intro':
  header(im,'TITLE CARD｜文字カード','The painting through time','Quiet Origins / The Night Watch');txt(im,'A painting. Six moments.',960,290,73,FB,major=True);txt(im,'一枚の絵、六つの時点',960,395,40,JA)
  dr=ImageDraw.Draw(im)
  for i,st in enumerate(YRS):
   x=180+i*312;rect(dr,(x-141,520,x+141,642),fill=INK if i<=min(stage,5) else LIGHT);txt(im,st,x,580,52,FB,LIGHT if i<=min(stage,5) else MUT,maxw=264)
  if stage>=6:
   u=(stage-5)/30;original=im.copy();im=Image.new('RGB',(W,H),PAPER);sw=round(W*(1-.14*u));sh=round(H*(1-.85*u));im.paste(original.resize((sw,sh),Image.Resampling.LANCZOS),((W-sw)//2,round((H-sh)*u)));target=Image.new('RGB',(W,H),PAPER);rail(target,'—');im.paste(target.crop((0,915*S,round(W*u),H)),(0,915*S))
 elif k=='credits':
  header(im,'CREDITS｜クレジット','Sources & voices','Quiet Origins / The Night Watch');rect(ImageDraw.Draw(im),(75,147,1845,748),fill=LIGHT)
  for i,st in enumerate(['Rijksmuseum, Amsterdam · 6 images · Public Domain','Lundens copy: National Gallery, London, on loan to Rijksmuseum','English narration: Kokoro / Heart (af_heart)','日本語ナレーション：VOICEVOX：冥鳴ひまり','Music: Quiet Origins Theme A02 · Suno']):txt(im,st,960,255+i*95,33,JA if i==3 else FT)
 else:raise ValueError(k)
 if yr is not None:rail(im,yr)
 return im
