"""EP012: typography, evidence plates, measured timeline and thumbnail layouts."""
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from pathlib import Path
from functools import lru_cache
import math,re,json
from wom12_produce import ROOT,MEDIA,read,save,sha
W,H=1920,1080
PAPER='#e9ddc4'; INK='#382a24'; MUT='#705744'; RUST='#944a35'; LIGHT='#f8f1dc'; BAR='#412f25'
FT='/System/Library/Fonts/Supplemental/Georgia.ttf'; FB='/System/Library/Fonts/Supplemental/Georgia Bold.ttf'; JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'; SANS='/System/Library/Fonts/Supplemental/Arial.ttf'
YRS=['4th c.','1087','1812','1821','1823','1858','1863','1864','1881','1902','1904','1931']
CAT={
'N03-A':('MAGAZINE COVER｜雑誌の表紙','Frank A. Nankivell · Puck · December 3, 1902','Library of Congress 2010652186 · No known restrictions on publication'),
'N03-B':('MAGAZINE COVER｜雑誌の表紙','Frank A. Nankivell · Puck · December 7, 1904','Library of Congress 2011645591 · No known restrictions on publication'),
'N05-A':('PAINTING｜絵画','Gerard David · The Saint Anne Altarpiece: Saint Nicholas · c.1500/1520','National Gallery of Art 1942.9.17.a · Public Domain'),
'N06-A':('DRAWING｜素描','Jacopo da Empoli · Saint Nicholas of Bari · c.1610','National Gallery of Art 2018.94.1 · Public Domain'),
'N08_cover':('BOOK｜刊本',"The Children’s Friend · Cover · New York, 1821",'Yale University, Beinecke Rare Book & Manuscript Library · Shirley 4065 · Open Access Policy'),
'N08_p1':('BOOK｜刊本',"The Children’s Friend · Page 1 · New York, 1821",'Yale University, Beinecke Rare Book & Manuscript Library · Shirley 4065 · Open Access Policy'),
'N11-C':('ENGRAVING｜版画','Winslow Homer · Santa Claus and His Presents · December 25, 1858','The Metropolitan Museum of Art 36.13.5(3) · Public Domain'),
'N02-A':('ENGRAVING｜版画','Thomas Nast · Santa Claus in Camp · Harper’s Weekly · January 3, 1863','The Metropolitan Museum of Art 33.35.11 · Public Domain'),
'N04-A':('BOOK｜刊本','A Visit from St. Nicholas · L. Prang & Co. · Boston, 1864','Library of Congress 73169323 · scan 10 · see collection rights notice in credits'),
'N11-A':('CHRISTMAS CARD｜クリスマスカード','L. Prang & Co. · Christmas card proofs · c.1865–1899','New York Public Library 483580 · Public Domain (United States)'),
'N11-B':('CHRISTMAS CARD｜クリスマスカード','Elihu Vedder · Christmas Card · Prang competition, 1881','The Metropolitan Museum of Art 2019.469.1 · Public Domain'),
'N12-A':('PAINTING｜絵画','Alfred Sisley · First Snow at Veneux-Nadon · 1878','National Gallery of Art 1983.98.1 · Public Domain'),
'N12-B':('PAINTING｜絵画','André Giroux · Santa Trinità dei Monti in the Snow · 1825/1830','National Gallery of Art 1997.65.1 · Public Domain')}
Q1812='“…the good St. Nicholas came riding over the tops of the trees, in that self same waggon wherein he brings his yearly presents to children”'
Q1823=['He was chubby and plump, a right jolly old elf,',"He was dress'd all in fur, from his head to his foot,",'But a miniature sleigh, and eight tiny rein-deer,','His cheeks were like roses, his nose like a cherry;']
J1823=['丸々と太った、陽気な年寄りの妖精','頭から足まで毛皮をまとい','小さなそりと、8頭の小さなトナカイ','頬はばらのよう、鼻はさくらんぼのよう']
QS='“Santa appeared in a red coat before Sundblom painted him.” — The Coca-Cola Company'
@lru_cache(None)
def font(path,sz):return ImageFont.truetype(path,sz)
@lru_cache(15)
def art(k):return Image.open(next(MEDIA.glob(k+'_*.jpg'))).convert('RGB')
METR=[]; CURRENT=''; ARTMEAS={};TH=[]
def txt(im,st,cx,cy,height,maxw=1730,face=FT,fill=INK,major=False):
 f=font(face,155);l,t,r,b=f.getbbox(st); mask=Image.new('L',(r-l,b-t));ImageDraw.Draw(mask).text((-l,-t),st,font=f,fill=255);w=min(maxw,round(height*(r-l)/(b-t)));x=round(cx-w/2);y=round(cy-height/2);im.paste(fill,(x,y,x+w,y+height),mask.resize((w,height),Image.Resampling.LANCZOS));METR.append(dict(card=CURRENT,text=st,box=[x,y,x+w,y+height],major=major,ink_height=height,foreground=fill));return [x,y,x+w,y+height]
def wrap(st,n):
 import textwrap
 return textwrap.wrap(st,n,break_long_words=False,break_on_hyphens=False)
def centered(im,lines,y,h,step=0,face=FT,major=False):
 for i,line in enumerate(lines):txt(im,line,960,y+i*(step or h+17),h,1650,face,major=major)
def header(im,tag,title='',source=''):
 dr=ImageDraw.Draw(im);dr.rectangle((0,0,W,106),fill=PAPER);txt(im,tag,960,20,19,1700,JA);txt(im,title or 'Quiet Origins  /  The Red Suit',960,52,26,1770,FB); 
 if source:txt(im,source,960,85,18,1780,SANS)
 dr.line((65,105,1855,105),fill=MUT,width=2)
def plate(im):ImageDraw.Draw(im).rounded_rectangle((75,147,1845,748),14,fill=LIGHT,outline='#bbab8a',width=2)
def fitted(im,k,box,enh=1,anchor=(.5,.5)):
 a=art(k);x,y,x1,y1=box;w,h=x1-x,y1-y;scale=min(w/a.width,h/a.height,1)*enh;sz=(round(a.width*scale),round(a.height*scale));a=a.resize(sz,Image.Resampling.LANCZOS);cw=min(w,a.width);ch=min(h,a.height);ax=round((a.width-cw)*anchor[0]);ay=round((a.height-ch)*anchor[1]);im.paste(a.crop((ax,ay,ax+cw,ay+ch)),(x+(w-cw)//2,y+(h-ch)//2));return scale
LINE2=[('1821','N08_p1'),('1864','N04-A'),('1902','N03-A'),('1904','N03-B')];LINE3=[('4th c.','N05-A'),('1087','N06-A'),('1812',None),('1821','N08_p1'),('1823',None),('1858','N11-C'),('1863','N02-A'),('1864','N04-A'),('1881',None),('1902','N03-A'),('1904','N03-B'),('1931',None)]
def lineup(im,rows):
 for ri,row in enumerate(rows):
  n=len(row);step=round(1710/n);h=340 if len(rows)==1 else 202;y=248 if len(rows)==1 else 174+ri*294
  for i,(yr,k) in enumerate(row):
   cx=round(960+(i-(n-1)/2)*step);half=step//2-10;dr=ImageDraw.Draw(im);dr.rounded_rectangle((cx-half,y-10,cx+half,y+h+53),6,fill=LIGHT,outline='#baa98b',width=2)
   if k:fitted(im,k,(cx-half+11,y,cx+half-11,y+h))
   else:txt(im,{'1812':'Waggon','1823':'Poem','1881':'Engraving','1931':'Advertisements'}[yr],cx,y+h//2,29,2*half-32,FT)
   txt(im,yr,cx,y+h+25,31,2*half-22,FB)
def rail(im,yr,unlocked=False):
 dr=ImageDraw.Draw(im);dr.rectangle((0,915,1920,1079),fill=BAR);dr.line((120,1008,1800,1008),fill='#c6b388',width=3)
 for i,n in enumerate(YRS):
  x=round(120+i*1680/11);dr.line((x,1000,x,1017),fill=LIGHT,width=3)
  if n=='1931' and not unlocked:dr.rectangle((x-28,971,x+28,992),outline='#b5a68f',width=2);continue
  txt(im,n,x,963 if n==yr else 1037,60 if n==yr else 26,144,FB if n==yr else SANS,LIGHT if n==yr else '#c9bda6',major=n==yr)
def scene(k,stage=0,yr=None,unlocked=False):
 global CURRENT;CURRENT=k;im=Image.new('RGB',(W,H),PAPER);dr=ImageDraw.Draw(im)
 if k in CAT:
  box=(60,107,1860,1079) if k=='N03-A' else (80,110,1840,810);anchor=(.5,.5);zoom=1
  if k=='N11-C':a=art(k);a=a.crop((0,0,a.width,round(a.height*.52)));a.thumbnail((1640,700));im.paste(a,((W-a.width)//2,110+(700-a.height)//2));scale=a.width/art(k).width
  else:scale=fitted(im,k,box,zoom,anchor)
  ARTMEAS[k]=dict(source=str(next(MEDIA.glob(k+'_*.jpg'))),start_scale=scale,band=[box[1],box[3]],art_size=list(art(k).size));header(im,*CAT[k]);
 elif k in ('D_lineup2','D_lineup3'):
  header(im,'EVIDENCE IN ORDER｜年代順の資料','Four appearances' if k=='D_lineup2' else 'From bishop to advertising','Quiet Origins  /  Comparative plate');lineup(im,[LINE2] if k=='D_lineup2' else [LINE3[:6],LINE3[6:]])
 elif k=='D_timeline_intro':
  header(im,'TITLE CARD｜文字カード','Tracing the changes');plate(im);txt(im,'A history in twelve dates',960,265,72,1600,FB,major=True);txt(im,'12の年代をたどる',960,363,39,1600,JA)
  for i,y in enumerate(YRS):
   cx=round(275+(i%6)*272);cy=481+(i//6)*122;dr.rounded_rectangle((cx-113,cy-44,cx+113,cy+45),5,fill=INK if i<=stage else PAPER);txt(im,y if y!='1931' else '□',cx,cy,38,198,SANS,LIGHT if i<=stage else MUT)
  if stage>=12:
   u=(stage-11)/30;initial=im.copy();im=Image.new('RGB',(W,H),PAPER);sw=round(W*(1-.14*u));sh=round(H*(1-.85*u));im.paste(initial.resize((sw,sh),Image.Resampling.LANCZOS),(round((W-sw)/2),round((H-sh)*u)));target=Image.new('RGB',(W,H),PAPER);rail(target,'—');partial=target.crop((0,915,round(W*u),1080));im.paste(partial,(0,915))
 elif k=='credits':
  header(im,'CREDITS｜クレジット','Sources & voices');plate(im)
  ll=['The Metropolitan Museum of Art · National Gallery of Art · New York Public Library','Library of Congress · Yale University, Beinecke Rare Book & Manuscript Library','Kokoro: Heart (af_heart)  /  VOICEVOX：冥鳴ひまり','Music: Quiet Origins Theme A02 · Suno']
  for i,x in enumerate(ll):txt(im,x,960,288+100*i,36,1580,JA if i==2 else FT)
 else:
  if k=='D_1823':im=ImageEnhance.Brightness(ImageOps.fit(art('N12-B'),(W,H)).filter(ImageFilter.GaussianBlur(13))).enhance(.43)
  header(im,'TITLE CARD｜文字カード',{'D_1812':'Washington Irving, A History of New York, 2nd ed., 1812, p.106','D_1823':'Troy Sentinel, December 23, 1823','D_1931':'An illustrator and a commission','D_1881':'An engraving by Thomas Nast','D_1931q':'The familiar story'}[k],{'D_1812':'アーヴィング『ニューヨーク史』改訂第2版（1812）','D_1823':'Backdrop: André Giroux, 1825/1830 · NGA 1997.65.1','D_1931':'The Coca-Cola Company · historical account','D_1881':'Harper’s Weekly, January 1, 1881','D_1931q':'Quiet Origins / Episode 12'}[k] if k!='D_1812' else 'A History of New York · vol. I, p.106');plate(im)
  if k=='D_1812':
   txt(im,'アーヴィング『ニューヨーク史』改訂第2版（1812）',960,211,32,1610,JA);lines=['“…the good St. Nicholas came riding over','the tops of the trees, in that self same','waggon wherein he brings his yearly','presents to children”'];assert ' '.join(lines)==Q1812;centered(im,lines,309,60,78,major=True)
   if stage:
    m=METR[-2]['box'];w=font(FT,155).getlength('waggon')/font(FT,155).getlength(lines[2]);dr.line((m[0],m[3]+3,round(m[0]+(m[2]-m[0])*w),m[3]+3),fill=RUST,width=4)
   centered(im,['善き聖ニコラスが、毎年子どもたちへ贈り物を運ぶあの同じ車に乗って、','木々のてっぺんの上をやって来た'],641,29,45,JA)
  if k=='D_1823':
   txt(im,'『トロイ・センティネル』1823年12月23日',960,236,35,1600,JA);q=Q1823[stage] if stage>=0 else "Account of a Visit from St. Nicholas";centered(im,wrap(q,29),350,62,92,major=True);txt(im,J1823[stage] if stage>=0 else "無署名で掲載された詩",960,625,39,1560,JA)
  if k=='D_1931q':txt(im,'1931?',960,382,141,1580,FB,major=True);txt(im,'the year of the famous advertisements｜有名な広告の年',960,588,41,1570,JA)
  if k=='D_1881':
   txt(im,'1881',960,330,116,1500,FB,major=True);txt(im,'Thomas Nast, “Merry Old Santa Claus,” Harper’s Weekly',960,486,43,1570,FT);txt(im,'printed in black and white',960,565,36,1570,FT);txt(im,'ナスト「陽気なサンタじいさん」— 白黒の印刷',960,645,36,1570,JA)
  if k=='D_1931':
   txt(im,'1931–1964',960,296,95,1600,FB,major=True);txt(im,'Haddon Sundblom paints Santa for Coca-Cola',960,427,42,1600,FT);txt(im,'サンドブロムがコカ・コーラのためにサンタを描く',960,505,32,1580,JA);centered(im,wrap(QS,62),615,34,47)
 if yr:rail(im,yr,unlocked)
 return im
