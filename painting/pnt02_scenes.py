"""pnt02 plates: native museum JPEG pixels, fixed labels, bilingual source cards."""
from pathlib import Path
from functools import lru_cache
import os,re,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from pnt02_produce import ROOT,REPO,MEDIA,read,save
S=int(os.environ.get('PNT02_SCALE','1'));W,H=1920*S,1080*S
PAPER='#e9ddc4';INK='#382a24';LIGHT='#f8f1dc';MUT='#705744';BAR='#412f25';RUST='#944a35'
FT='/System/Library/Fonts/Supplemental/Georgia.ttf';FB='/System/Library/Fonts/Supplemental/Georgia Bold.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc';SANS='/System/Library/Fonts/Supplemental/Arial.ttf'
YRS=['1776','1777','1849','1851','1897','today']
METR=[];ARTMEAS={};CURRENT=''
FILES={'V01_full_1':'Met_97.34/DP-14511-001.jpg','V01_full_2':'Met_97.34/DP-14511-001.jpg','V01_D1':'Met_97.34/DP245004.jpg','V01_D2':'Met_97.34/DP245005.jpg','V01_D3':'Met_97.34/DP258218.jpg','V01_room':'Met_97.34/DP258191.jpg','V10':'SMB_3964830/smb3964830.jpg'}
BOXES={'V01_full_1':[0,42.5,4000,2292.5],'V01_full_2':[0,42.5,4000,2292.5],'V01_D1':[0,0,1589,3847],'V01_D2':[0,0,2611,2750],'V01_D3':[0,450,4000,2700],'V01_room':[0,0,2911,3880],'V10':[0,0,2940,3500]}
LETTER_HEAD='Head Quarters Newtown [Pa.] 27th Decemr 1776'
LETTER=[['“…the quantity of Ice, made that Night, impeded the passage of Boats so much, that it was three OClock before the Artillery could all be got over, and near four, before the Troops took up their line of march.”','その夜にできた大量の氷が舟の通過をひどく妨げ、砲兵をすべて渡し終えるまでに3時、部隊が行軍を始めるころには4時近くになっていた'],['“…passing the River in a very severe Night, and their March thro’ a violent Storm of Snow and Hail…”','非常に厳しい夜に川を渡り、雪と雹の激しい嵐の中を行軍した']]
RESOLUTION=['“Resolved, That the flag of the thirteen United States be thirteen stripes, alternate red and white; that the union be thirteen stars, white in a blue field, representing a new constellation.”','13の合衆国の旗を、赤と白を交互にした13本の縞とし、上隅の区画を、青地に白い13の星とし、新しい星座を表すものとする']
WHITTREDGE=['“…for the steersman and again for Washington himself.”','…舵を取る人のために、そしてまたワシントンその人のために']
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
 txt(im,tag,960,18,18,JA);txt(im,title,960,49,min(25,25*1770/max(1770,width(title,25,FT))),FT);txt(im,source,960,83,18,JA if any(ord(c)>255 for c in source) else SANS)
 line(dr,(65,105,1855,105),MUT)
def rail(im,yr):
 dr=ImageDraw.Draw(im);rect(dr,(0,915,1920,1080),fill=BAR);line(dr,(120,1008,1800,1008),'#c6b388',3)
 for i,n in enumerate(YRS):
  x=120+i*336;line(dr,(x,1000,x,1017),LIGHT,3)
  # Wide 1946–47 is centred over its tick, with 336 px between neighbours.
  txt(im,n,x,963 if n==yr else 1037,60 if n==yr else 26,FB if n==yr else SANS,LIGHT if n==yr else '#c9bda6',maxw=315,major=n==yr)

@lru_cache(3)
def artwork(k):
 return Image.open(MEDIA/FILES[k]).convert('RGB')

def paste_art(im,k):
 a=artwork(k);box=BOXES[k];w,h=box[2]-box[0],box[3]-box[1]
 scale=min(W/w,H/h);ww,hh=round(w*scale),round(h*scale)
 # Pillow's box argument samples original pixels directly, including half-pixel edges.
 q=a.resize((ww,hh),Image.Resampling.LANCZOS,box=tuple(box));x=(W-ww)//2;y=(H-hh)//2;im.paste(q,(x,y))
 ARTMEAS[k]=dict(crop_native_px=box,art_size=[w,h],native_output_scale=scale,pasted_box=[x/S,y/S,(x+ww)/S,(y+hh)/S],source=str(MEDIA/FILES[k]))

def art_overlay(k,yr=None):
 im=Image.new('RGBA',(W,H),(0,0,0,0))
 if k=='V10':header(im,'PRINT｜版画','Des Deutschen Vaterland von Moritz Arndt · 1848','Staatliche Museen zu Berlin, Kunstbibliothek · 1900,682 · PDM 1.0 · Photo: Dietmar Katz')
 else:
  tag='PAINTING｜絵画' if 'full' in k else 'GALLERY VIEW｜展示室' if k=='V01_room' else 'DETAIL｜部分'
  title='Emanuel Leutze · Washington Crossing the Delaware · 1851' if 'full' in k else 'Washington Crossing the Delaware · 1851'
  header(im,tag,title,'The Metropolitan Museum of Art · 97.34 · Public Domain / Open Access, CC0')
 if yr is not None:rail(im,yr)
 return im

def quote(im,texts):
 box=(75,147,1845,748);dr=ImageDraw.Draw(im);dr.rounded_rectangle(tuple(v*S for v in box),14*S,fill=LIGHT,outline='#bbab8a',width=2*S)
 rows=[(wrap(t,h,f),h,f) for t,h,f in zip(texts,[60,31],[FT,JA])]
 total=sum(len(ll)*h+(len(ll)-1)*17 for ll,h,f in rows)+32
 assert total<=531,(CURRENT,total)
 y=447.5-total/2
 for ll,h,f in rows:
  for st in ll:txt(im,st,960,y+h/2,h,f,major=h==60,box=box);y+=h+17
  y+=15

def eventcard(im,year,en,ja):
 box=(75,147,1845,748);rect(ImageDraw.Draw(im),box,fill=LIGHT)
 txt(im,year,960,285,110,FB,major=True,box=box)
 lines=wrap(en,45,FT,1600);y=440-(len(lines)-1)*32
 for st in lines:txt(im,st,960,y,45,FT,box=box);y+=64
 lines=wrap(ja,31,JA,1600)
 for i,st in enumerate(lines):txt(im,st,960,640+i*49,31,JA,box=box)

def scene(k,stage=0,yr=None):
 global CURRENT;CURRENT=k
 im=Image.new('RGB',(W,H),PAPER)
 if k in FILES:
  im.paste('#14110f',(0,0,W,H));paste_art(im,k)
  # Labels and chronology are overlaid AFTER motion in the renderer.
  return im
 if k in ['D_letter_head','D_letter']:
  header(im,'TITLE CARD｜文字カード','George Washington to John Hancock, 27 December 1776 — as transcribed in Founders Online','ワシントンからハンコックへの手紙（翻刻）')
  quote(im,[LETTER_HEAD,''] if k=='D_letter_head' else LETTER[stage])
 elif k=='D_resolution':
  header(im,'TITLE CARD｜文字カード','Resolution of the Continental Congress, 14 June 1777 — as quoted by the U.S. National Archives','大陸会議の決議（1777年6月14日）');quote(im,RESOLUTION)
 elif k=='D_whittredge':
  header(im,'TITLE CARD｜文字カード','Worthington Whittredge, recollection — as quoted in J. K. Howat, The Metropolitan Museum of Art Bulletin, 1968','ホイットリッジの回想（Metの1968年の論文の引用）');quote(im,WHITTREDGE)
 elif k=='D_leutze':
  header(im,'TITLE CARD｜文字カード','Emanuel Leutze','U.S. Department of State · Smithsonian American Art Museum')
  eventcard(im,*[('1816','Schwäbisch Gmünd, Württemberg','1816年 ドイツ・シュヴェービッシュ・グミュント'),('1825','United States','1825年 アメリカへ'),('1841','Düsseldorf','1841年 デュッセルドルフ')][stage])
 elif k=='D_bremen':
  header(im,'TITLE CARD｜文字カード','Two versions of a painting','The Metropolitan Museum of Art Bulletin · 1968 / 2011')
  eventcard(im,*[('November 1850','fire in the studio','アトリエの火事'),('1851','second version begun','2枚目に着手'),('1942','first version lost in an air raid, Bremen','最初の絵がブレーメンで空襲により失われる')][stage])
 elif k=='D_1853':
  header(im,'TITLE CARD｜文字カード','The image reaches New York','Metropolitan Museum of Art Bulletin, 1968 · Library of Congress, 2020633689')
  eventcard(im,*[('1851','New York','ニューヨークで展示'),('1853','Engraving by Paul Girardet after Leutze, published by Goupil & Co., New York','ジラルデによる版画（グーピル社、ニューヨーク）')][stage])
 elif k=='D_timeline_intro':
  header(im,'TITLE CARD｜文字カード','The painting through time','Quiet Origins / Washington Crossing the Delaware')
  txt(im,'A painting. Six moments.',960,290,73,FB,major=True);txt(im,'一枚の絵、六つの時点',960,395,40,JA)
  dr=ImageDraw.Draw(im)
  for i,st in enumerate(YRS):
   x=180+i*312;rect(dr,(x-141,520,x+141,642),fill=INK if i<=min(stage,5) else LIGHT);txt(im,st,x,580,52,FB,LIGHT if i<=min(stage,5) else MUT,maxw=264)
  if stage>=6:
   u=(stage-5)/30;original=im.copy();im=Image.new('RGB',(W,H),PAPER);sw=round(W*(1-.14*u));sh=round(H*(1-.85*u));im.paste(original.resize((sw,sh),Image.Resampling.LANCZOS),((W-sw)//2,round((H-sh)*u)));target=Image.new('RGB',(W,H),PAPER);rail(target,'—');im.paste(target.crop((0,915*S,round(W*u),H)),(0,915*S))
 elif k=='credits':
  header(im,'CREDITS｜クレジット','Sources & voices','Quiet Origins / Washington Crossing the Delaware');rect(ImageDraw.Draw(im),(75,147,1845,748),fill=LIGHT)
  lines=['The Metropolitan Museum of Art · Open Access, CC0','Staatliche Museen zu Berlin, Kunstbibliothek','Public Domain Mark 1.0 · Photo: Dietmar Katz','English narration: Kokoro / Heart (af_heart)','日本語ナレーション：VOICEVOX：冥鳴ひまり','Music: Quiet Origins Theme A02 · Suno']
  for i,st in enumerate(lines):txt(im,st,960,220+i*86,33,JA if i==4 else FT)
 else:raise ValueError(k)
 if yr is not None:rail(im,yr)
 return im
