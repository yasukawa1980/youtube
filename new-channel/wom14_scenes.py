"""EP014: native museum scans, measured bilingual cards and bounded source excerpts.
No generated artwork. Fractional source coordinates were checked against originals.
"""
import os,re,math,json
from pathlib import Path
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFont
from wom14_produce import ROOT,REPO,read,save
S=int(os.getenv('WOM14_SCALE','1')); W,H=1920*S,1080*S
PAPER='#e9ddc4';INK='#382a24';MUT='#695844';RUST='#943a2c';WHITE='#fff8e8'
EN='/System/Library/Fonts/Supplemental/Georgia.ttf';BOLD='/System/Library/Fonts/Supplemental/Georgia Bold.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc';BRUSH='/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
ASSETS={a['id']:a for a in read(REPO/'new-channel/research/wom14_素材台帳_20261109.json')['assets']}
METR=[];ARTMEAS=[];CURRENT=''
CLAIMS=[('They always looked like this','昔からこの姿'),('“Oni” means hidden','「おに」は「隠れる」'),('Horns and tiger skin come from a direction','角と虎の皮は方角から'),('Oni are the ones chased away','鬼は追い払われる側')]
STAMPS=[('NOT IN THE OLDEST RECORDS','最古の記録にはない'),('AN OLD GUESS','古くからの推測'),('A LATER EXPLANATION','後の時代の説明'),('THE ROLES CHANGED','役が入れかわった')]
# Work name and date are never confused with the date of an event narrated.
CAT={
'O01-A':('PAINTING｜絵画','Anonymous Japanese artist · Demon Intoning the Name of the Buddha · 1700s','Cleveland Museum of Art · 1982.26 · CC0'),
'O01-C':('PAINTING｜絵画','Kawanabe Kyosai · A Demon as a Mendicant Monk · 1850–1889','Rijksmuseum · AK-RAK-2000-14 · Public Domain'),
'O02-A':('PAINTING｜絵画','Miyagawa Issho · Shimabara Courtesans Exorcizing Demons · late 1700s','The Met · 2015.300.132 · Public Domain'),
'O02-B':('PAINTING｜絵画','Suzuki Kiitsu · Setsubun Festival at Sensoji · 1857','The Met · 2015.300.98 · Public Domain'),
'O02-D':('PAINTING｜絵画','Tani Buncho · Setsubun · 1773–1842','Rijksmuseum · AK-RAK-2015-2-3 · Public Domain'),
'O05-A':('PRINT｜版画','Utagawa Hiroshige · Autumn Moon at Ishiyama · c.1835','The Met · JP48 · Public Domain'),
'O16-A':('PRINT｜版画','Utagawa Hiroshige · Autumn Moon on the Tama River · c.1838','The Met · JP2480 · Public Domain'),
'O15-A':('PAINTING｜絵画','Ike Taiga · Bamboo and Rocks in Clearing Skies · mid-1700s','Cleveland Museum of Art · 1958.337 · CC0'),
'O09-A':('PRINT｜版画','Sugimura Jihei · At the Edge of the River Akutagawa · 1681–1703 (catalogue range)','The Met · JP3407 · Public Domain'),
'O10-A':('HANDSCROLL｜絵巻','Illustrated Legends of the Kitano Tenjin Shrine · late 13th century','The Met · 25.224a–e · Public Domain'),
'O14-B':('SKETCH ALBUM｜画帖','Kawanabe Kyosai · Snail Versus Demon · mid-to-late 1800s','Cleveland Museum of Art · 1991.125.t · CC0'),
'O03-23':('MANUSCRIPT (1940–41 FACSIMILE)｜写本（1940〜41年の複製）','Nihon Shoki · Book 26 · Saimei 7 · frame 23','National Diet Library Digital Collections · 1142412 · Public domain, protection period expired'),
'O04-272':('BOOK (1896)｜刊本（1896）','W. G. Aston · Nihongi, vol. II · p.272','Smithsonian Libraries and Archives · Public Domain / CC0'),
'O06-38':('PRINTED BOOK (LATE EDO REPRINT)｜刊本（江戸後期の再版）','Teisei Izumo Fudoki · Ayo · frame 38','National Diet Library Digital Collections · 2563532 · Public domain, protection period expired'),
'O08-31':('PRINTED BOOK (1617)｜刊本（1617）','Wamyo Ruijusho · 20-volume edition · vol.2 · frame 31','National Diet Library Digital Collections · 2544216 · Public domain, protection period expired'),
'O11-12':('PRINTED BOOK (1805 COPY; FIRST PUBLISHED 1779)｜刊本（1805年の本・初刊1779年）','Toriyama Sekien · Konjaku Gazu Zoku Hyakki · Oni · text only','Smithsonian Libraries and Archives · Public Domain / CC0'),
'R10-27':('PRINTED BOOK (1897)｜刊本（1897）','Shoku Nihongi · Keiun 3 · frame 27','National Diet Library Digital Collections · 991092 · Public domain, protection period expired'),
'R11-30':('PRINTED BOOK (1653 EDITION)｜刊本（1653年跋）','Oe no Masafusa · Goke Shidai, book 11 · frame 30 · main text only','National Diet Library Digital Collections · 12865891 · Public domain, protection period expired'),
'R12-1447':('PRINTED BOOK (1930)｜刊本（1930）','Gaun Nikkenroku Batsuyu · Bunnan 4 · printed p.332 / p.24','National Diet Library Digital Collections · 1920248 · Public domain, protection period expired')}
# Full-page display is restricted to the safe source area for Sekien and Goke.
SAFE={'O11-12':(.035,.17,.395,.435),'R11-30':(.103,.205,.445,.899)}
FOCUS={
'O01-A':(.22,.225,.80,.465),'O01-C':(.20,.56,.64,.70),'O02-A':(.13,.48,.88,.86),
'O02-D':(.10,.54,.87,.77),'O10-A':(.56,.50,.80,.81),'O14-B':(.53,.20,.88,.75),
'O03-23':(.235,.125,.39,.9),'O04-272':(.125,.36,.895,.475),'O06-38':(.60,.14,.705,.78),'O08-31':(.165,.25,.286,.785),
'O11-12':SAFE['O11-12'],'R10-27':(.165,.355,.196,.724),'R11-30':(.233,.205,.405,.90),'R12-1447':(.738,.20,.805,.88)}
# Two columns retained together for 目一鬼; the line-break order is not rearranged.
BOXES={
'O03-23':[[ (.33,.82,.375,.89),(.26,.14,.315,.78)]],
'O04-272':[[ (.132,.368,.886,.466) ],[(.148,.858,.265,.875)]],
'O06-38':[[ (.609,.151,.697,.765) ]],
'O08-31':[[ (.252,.697,.282,.784),(.211,.257,.248,.785),(.172,.257,.208,.55)],[(.172,.554,.205,.697)]],
'O11-12':[[ (.255,.302,.296,.399),(.205,.174,.25,.4),(.151,.174,.185,.25) ],[(.055,.175,.094,.255)]],
'R10-27':[[ (.169,.593,.191,.719) ]],
'R11-30':[[ (.373,.468,.401,.888),(.337,.207,.367,.496)],[(.241,.306,.27,.66)]],
'R12-1447':[[ (.768,.65,.793,.756) ],[(.768,.805,.793,.872),(.744,.207,.766,.328)]]}
NOTES={
'O03-23':('661 · “that evening, on Mount Asakura, an oni wearing a large hat looked down on the funeral”','661年・その夕べ、朝倉山の上に大きな笠の鬼が葬儀を見下ろした'),
'O06-38':('733 · “a one-eyed oni came and ate the farmer\'s son”','733年・目一つの鬼が来て、田を耕す人の息子を食べた'),
'R10-27':('706 · “a great exorcism was held for the first time”','706年・初めて大儺を行う'),
'R12-1447':('1447 · “oni out, fortune in”','1447年・鬼は外、福は内')}
@lru_cache(80)
def font(face):return ImageFont.truetype(face,160)
def width(st,h,face=EN):
 f=font(face);l,t,r,b=f.getbbox(st);return (r-l)*h/max(1,b-t)
def wrap(st,h,face,maxw):
 tokens=list(st) if face in [JA,BRUSH] else st.split(' ');sep='' if face in [JA,BRUSH] else ' ';out=[];cur=''
 for t in tokens:
  q=cur+sep+t if cur else t
  if cur and width(q,h,face)>maxw:out.append(cur);cur=t
  else:cur=q
 if cur:out.append(cur)
 return out
def text(im,st,cx,cy,h,face=EN,color=INK,maxw=1800,major=False,box=None,bg=PAPER,record=True):
 f=font(face);l,t,r,b=f.getbbox(st);ww=round((r-l)*h/max(1,b-t)*S);hh=round(h*S)
 assert ww<=maxw*S+2,(CURRENT,st,ww/S,maxw)
 mask=Image.new('L',(r-l,b-t));ImageDraw.Draw(mask).text((-l,-t),st,font=f,fill=255);mask=mask.resize((ww,hh),Image.Resampling.LANCZOS)
 x=round(cx*S-ww/2);y=round(cy*S-hh/2);im.paste(color,(x,y,x+ww,y+hh),mask)
 bounds=[x/S,y/S,(x+ww)/S,(y+hh)/S]
 if record:
  row=dict(card=CURRENT,text=st,ink_height=h,box=bounds,major=major,foreground=color,background=bg)
  if box:row['padding']=min(bounds[0]-box[0],bounds[1]-box[1],box[2]-bounds[2],box[3]-bounds[3])
  METR.append(row)
 return bounds
def rect(im,box,fill=None,outline=None,w=2):ImageDraw.Draw(im).rectangle(tuple(round(v*S) for v in box),fill=fill,outline=outline,width=round(w*S))
def header(im,tag,title='',source=''):
 for st,y,h,face in [(tag,24,20,JA),(title,60,25,EN),(source,97,19,EN)]:
  if st:text(im,st,960,y,h,face,maxw=1840)
 ImageDraw.Draw(im).line((60*S,121*S,1860*S,121*S),fill=MUT,width=S)
@lru_cache(1)
def original(k):return Image.open(ASSETS[k]['original_path']).convert('RGB')
def boxpx(k,box):
 w,h=ASSETS[k]['original_dimensions'];return tuple(round(v*(w if i%2==0 else h)) for i,v in enumerate(box))
def paste_art(im,k,crop=None,band=(130,900),highlight=None):
 crop=crop or SAFE.get(k,(0,0,1,1));src=original(k);b=boxpx(k,crop);a=src.crop(b)
 if k=='O11-12':
  # A non-rectangular text-only clipping removes the mountain line below the last columns.
  mask=Image.new('L',a.size,0);poly=[(.035,.17),(.395,.17),(.395,.385),(.30,.435),(.035,.435)]
  pp=[((x*src.width-b[0]),(y*src.height-b[1])) for x,y in poly];ImageDraw.Draw(mask).polygon(pp,fill=255)
  clean=Image.new('RGB',a.size,PAPER);clean.paste(a,(0,0),mask);a=clean
 maxw=1840*S;maxh=(band[1]-band[0])*S
 scale=min(1.0,maxw/a.width,maxh/a.height);sz=(round(a.width*scale),round(a.height*scale));x=(W-sz[0])//2;y=round(band[0]*S)+(round(maxh)-sz[1])//2
 im.paste(a.resize(sz,Image.Resampling.LANCZOS),(x,y))
 if highlight is not None:
  for q in BOXES[k][highlight]:
   native=boxpx(k,q);v=[x+(native[0]-b[0])*scale,y+(native[1]-b[1])*scale,x+(native[2]-b[0])*scale,y+(native[3]-b[1])*scale]
   assert v[0]>=x-2 and v[1]>=y-2 and v[2]<=x+sz[0]+2 and v[3]<=y+sz[1]+2,(k,crop,q)
   ImageDraw.Draw(im).rectangle(v,outline=RUST,width=2*S)
 ARTMEAS.append(dict(key=k,crop_fraction=list(crop),native_box=list(b),output_box=[x/S,y/S,(x+sz[0])/S,(y+sz[1])/S],native_scale=scale,highlight=highlight,scale_factor=S))
 return (x/S,y/S,(x+sz[0])/S,(y+sz[1])/S)
def card(k,stage=0,stamp_scale=1.0):
 global CURRENT;CURRENT=k
 im=Image.new('RGB',(W,H),PAPER)
 if k.startswith('D_check'):
  header(im,'CLAIM CHECK｜通説の点検','Four claims. The old sources.','Quiet Origins · Oni')
  active=None if k in ['D_check_all','D_check_list'] else int(k[-1])-1
  for i,((en,ja),(se,sj)) in enumerate(zip(CLAIMS,STAMPS)):
   box=(55,145+i*183,1120,316+i*183);right=(1150,box[1]+12,1860,box[3]-12)
   lit=k=='D_check_all' or (k=='D_check_list' and i<stage) or i==active
   col=INK if lit else MUT
   rect(im,box,fill='#f6ecd9' if lit else PAPER,outline='#b9a78a',w=1)
   lines=wrap(en,52,EN,1000);height=len(lines)*60+35;top=(box[1]+box[3]-height)/2
   for j,s in enumerate(lines):text(im,s,587.5,top+26+j*60,52,EN,col,1000,True,box,'#f6ecd9' if lit else PAPER)
   text(im,ja,587.5,top+len(lines)*60+15,27,JA,col,1000,False,box,'#f6ecd9' if lit else PAPER)
   stamped=k=='D_check_all' or (i==active and stage>=1)
   if stamped:
    layer=Image.new('RGBA',(W,H),(0,0,0,0));rect(layer,right,fill=PAPER,outline=RUST,w=3)
    sl=wrap(se,37,BOLD,650);y=(right[1]+right[3]-(len(sl)*46+30))/2
    for j,s in enumerate(sl):text(layer,s,1505,y+18.5+j*46,37,BOLD,RUST,650,box=right)
    text(layer,sj,1505,y+len(sl)*46+15,24,JA,RUST,650,box=right)
    if stamp_scale!=1:
     q=layer.crop(tuple(round(v*S) for v in right));q=q.resize((round(q.width*stamp_scale),round(q.height*stamp_scale)),Image.Resampling.LANCZOS);im.paste(q,(round(1505*S-q.width/2),round((right[1]+right[3])/2*S-q.height/2)),q)
    else:im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
 elif k=='D_features':
  header(im,'TITLE CARD｜文字カード','The familiar picture','Quiet Origins · Oni')
  terms=[('red or blue skin','赤や青の肌'),('horns','角'),('tiger-skin loincloth','虎の皮の腰巻き'),('iron club','金棒')]
  for i,(en,ja) in enumerate(terms[:stage]):
   y=245+i*170;text(im,en,960,y,66,EN,major=True);text(im,ja,960,y+65,33,JA)
 elif k=='D_kanji_oni':
  header(im,'TITLE CARD｜文字カード','A character in the oldest records','Quiet Origins · Oni')
  text(im,'鬼',960,440,420,BRUSH,major=True)
  text(im,'the character read as “oni” today',960,735,36,EN);text(im,'いま「おに」と読む字',960,793,30,JA)
 elif k=='D_compass':
  header(im,'DIAGRAM｜模式図','The twelve zodiac directions','Quiet Origins · Oni')
  cx,cy,r=730,510,275;dr=ImageDraw.Draw(im);dr.ellipse(((cx-r)*S,(cy-r)*S,(cx+r)*S,(cy+r)*S),outline=MUT,width=2*S)
  chars='子丑寅卯辰巳午未申酉戌亥'
  for i,c in enumerate(chars):
   angle=i*math.pi/6;x=cx+math.sin(angle)*r;y=cy-math.cos(angle)*r;text(im,c,x,y,60,JA,RUST if c in '丑寅' else INK,major=True)
  text(im,'N',cx,cy-r-75,37,BOLD);text(im,'北',cx,cy-r-30,25,JA)
  for i,st in enumerate(['ushitora','NE · “demon gate”']):text(im,st,1430,395+i*70,44 if i else 64,EN,maxw=680,major=i==0)
  text(im,'丑寅・北東・鬼門',1430,570,36,JA,maxw=680)
  dr.line((950*S,295*S,1120*S,355*S),fill=RUST,width=3*S)
 elif k=='credits':
  header(im,'CREDITS｜クレジット','Sources & voices','Quiet Origins · Oni')
  lines=['The Metropolitan Museum of Art · Public Domain','Cleveland Museum of Art · CC0','Rijksmuseum · Public Domain','Smithsonian Libraries and Archives · Public Domain / CC0','National Diet Library Digital Collections · public domain, protection period expired','国立国会図書館：インターネット公開（保護期間満了）','Voice: Kokoro / Heart (af_heart)','Music: QO_THEME_A02 / Suno']
  for i,st in enumerate(lines):text(im,st,960,210+i*85,30 if i!=5 else 26,JA if i==5 else EN,maxw=1800)
 else:raise ValueError(k)
 return im

def art_scene(k,crop=None,highlight=None):
 global CURRENT;CURRENT=k
 im=Image.new('RGB',(W,H),PAPER)
 if k=='O01-A':
  paste_art(im,k,crop or FOCUS[k],(0,1080));
  for i,st in enumerate(['PAINTING｜絵画','Anonymous Japanese artist','Demon Intoning','the Name of the Buddha','1700s','Cleveland Museum','of Art · 1982.26','CC0']):text(im,st,215,160+i*64,22,JA if i==0 else EN,maxw=395)
  return im
 header(im,*CAT[k]);band=(130,905)
 if k in NOTES:
  en,ja=NOTES[k];enlines=wrap(en,23,EN,1800)
  for i,st in enumerate(enlines):text(im,st,960,150+i*30,23,EN)
  text(im,ja,960,150+len(enlines)*30,22,JA);band=(205 if len(enlines)==1 else 235,905)
 paste_art(im,k,crop,band,highlight)
 return im
