"""Bilingual EP015 evidence board, date diagrams and credit plates."""
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageColor
PAPER='#f5eedf'; INK='#29251e'; VERMILION='#873b2e'; RULE='#736651'; SOFT='#635b50'
LATIN='/System/Library/Fonts/Supplemental/'
JP=str(next(Path('/System/Library/Fonts').glob('*角* W5.ttc')))
@lru_cache(maxsize=96)
def font(size,face):
 path={'ja':JP,'header':LATIN+'Georgia Bold.ttf','main':LATIN+'Arial Narrow Bold.ttf','small':LATIN+'Arial.ttf'}[face]
 return ImageFont.truetype(path,size)

WORDS={
 'rome': '354 · ROME · ONE BOOK, TWO ENTRIES ON DEC 25｜354年・ローマ・一冊の本に、12月25日の行が二つ',
 'temple':"274 · AURELIAN'S TEMPLE OF SOL｜274年・アウレリアヌスのソルの神殿",
 'margin':'SYRIAC MARGIN NOTE (PRINTED 1721)｜シリア語の欄外の書き込み（1721年刊）',
 'unknown':'AUTHOR AND DATE UNKNOWN｜筆者・年代は不明',
 'leo':'5TH C. · LEO: BOWING TO THE SUN｜400年代・レオ：太陽に頭を下げる人々',
 'before':'NO CLEAR SOURCE BEFORE 354｜354年より前のはっきりした資料はない',
 'saturnalia':'SATURNALIA: DEC 17–23｜サトゥルナリア：12月17〜23日',
 'tertullian':'C. 200 · TERTULLIAN: DIED MARCH 25｜200年ごろ・テルトゥリアヌス：亡くなった日は3月25日',
 'sermon':'4TH C. SERMON · CONCEIVED MARCH 25｜300年代の説教：3月25日に身ごもられた',
 'augustine':'EARLY 5TH C. · AUGUSTINE: MAR 25 → DEC 25｜400年代初め・アウグスティヌス：3月25日→12月25日',
 'after':'AFTER THE DATE EXISTED｜祭りができた後の説明',
 'neither':'NEITHER RECORDS THE CHOICE｜どちらも、選ばれたときの記録ではない',
 'pliny':'1ST C. · PLINY: SOLSTICE ≈ DEC 25, EQUINOX ≈ MAR 25｜1世紀・プリニウス：冬至は12月25日ごろ、春分は3月25日ごろ'}
LEFT=['temple','margin','unknown','leo','before','saturnalia']
RIGHT=['tertullian','sermon','augustine','after']
class Plate:
 def __init__(self,s):
  self.s=s;self.im=Image.new('RGB',(1920*s,1080*s),PAPER);self.d=ImageDraw.Draw(self.im);self.metrics=[]
 def box(self,b,fill=None,edge=None,width=1):
  self.d.rectangle(tuple(round(v*self.s) for v in b),fill=fill,outline=edge,width=width*self.s)
 def line(self,pts,fill=RULE,w=2):
  self.d.line([(round(x*self.s),round(y*self.s)) for x,y in pts],fill=fill,width=w*self.s)
 def text(self,t,b,size,face='main',color=INK,minimum=None):
  x,y,r,z=[round(v*self.s) for v in b];minimum=minimum if minimum is not None else size
  for pt in range(size,minimum-1,-1):
   f=font(pt*self.s,face);l,top,rr,bb=self.d.textbbox((0,0),t,font=f);w=rr-l;h=bb-top
   if w<=r-x and h<=z-y:break
  else:raise ValueError((t,b,size,round(w/self.s)))
  ink_height=max(h,(52 if size>=52 else 40)*self.s) if face=='main' and size>=40 else h
  ink_height=min(ink_height,z-y)
  cx=(x+r-w)//2;cy=(y+z-ink_height)//2
  if ink_height==h:self.d.text((cx-l,cy-top),t,font=f,fill=color)
  else:
   mask=Image.new('L',(w,h));ImageDraw.Draw(mask).text((-l,-top),t,font=f,fill=255)
   self.im.paste(ImageColor.getrgb(color),(cx,cy,cx+w,cy+ink_height),mask.resize((w,ink_height),Image.Resampling.LANCZOS))
  h=ink_height
  self.metrics.append(dict(text=t,font_px=pt*self.s,ink_height=h,ink_box=[cx,cy,cx+w,cy+h],color=color))
 def pair(self,val,b,size=44,jp=28,edge=RULE,color=INK):
  x,y,r,z=b
  if edge:self.box(b,PAPER,edge,2)
  a,j=val.split('｜')
  mid=y+(z-y)*.56
  prior=len(self.metrics)
  self.text(a,(x+10,y+4,r-10,mid),size,color=color)
  self.text(j,(x+10,mid,r-10,z-4),jp,'ja',color)
  if edge:self.padding(prior,b)
 def padding(self,prior,b):
  x,y,r,z=[v*self.s for v in b]
  for t in self.metrics[prior:]:
   l,top,right,bottom=t['ink_box'];t['padding']=int(min(l-x,top-y,r-right,z-bottom))
 def label(self,t):
  self.text(t,(38,16,411,50),23,'ja',SOFT)
def board(s,active,anim=None,dy=0):
 p=Plate(s);p.label('EVIDENCE BOARD｜証拠ボード')
 p.pair('THE SUN FESTIVAL｜太陽の祭り',(56,56,934,164),62,34,None)
 p.pair('THE CALCULATION｜計算',(986,56,1864,164),62,34,None)
 p.line([(960,269),(960,737)],RULE,1)
 def card(key,b,small=False,stamp=False):
  if key not in active:return
  x,y,r,z=b
  if key==anim or (key=='unknown' and anim=='margin'):y+=dy;z+=dy
  if small or stamp:
   a,j=WORDS[key].split('｜')
   if stamp:p.box((x,y,r,z),PAPER,VERMILION,2)
   # Two pieces on one line, measured separately in their respective scripts.
   fs=25 if not stamp else 23
   width=p.d.textlength(a,font=font(fs*s,'main'))/s+p.d.textlength(j,font=font((fs-2)*s,'ja'))/s+20
   start=(x+r-width)/2;split=start+p.d.textlength(a,font=font(fs*s,'main'))/s+2
   color=VERMILION if stamp else SOFT
   prior=len(p.metrics)
   p.text(a,(start-2,y+2,split,z-2),fs,color=color)
   p.text(j,(split+12,y+2,r-(start-x)+4,z-2),fs-2,'ja',color)
   if stamp:p.padding(prior,(x,y,r,z))
  else:p.pair(WORDS[key],(x,y,r,z),43,28)
 card('rome',(350,176,1570,261))
 for i,(keys,x) in enumerate([(LEFT,48),(RIGHT,982)]):
  for key,(y,z) in zip([keys[0],keys[1],keys[3] if i==0 else keys[2]],[(279,370),(389,480),(545,636)]):
   card(key,(x,y,x+888,z))
 card('unknown',(170,489,819,528),stamp=True)
 card('before',(62,645,922,687),stamp=True);card('after',(1001,645,1850,687),stamp=True)
 card('saturnalia',(48,699,936,742),small=True)
 card('neither',(160,747,1760,790),small=True);card('pliny',(115,798,1805,891))
 return p

# Schematic shorelines in degrees of longitude and latitude. No political boundaries.
SHORES=[
 [(-5.6,36),(-2.4,36.8),(-.7,37.6),(.2,38.8),(-.3,39.5),(.8,40.7),(3.2,42.4),(3.1,43.1),(4.6,43.5),(6.1,43.1),(7.5,43.8),(8.8,44.4),(10,44),(10.4,43),(11.4,42.3),(12.3,41.7),(13.7,41.2),(14.4,40.7),(15.6,40),(15.7,38.9),(16,38),(16.6,38.5),(16.5,39),(17.1,39.4),(16.5,40.1),(16.9,40.5),(18.5,39.8),(18.3,40.4),(16.2,41.3),(16.1,41.8),(15.2,41.9),(14.2,42.5),(12.3,44.1),(12.2,45.3),(13.5,45.7),(13.9,44.8),(14.6,45.3),(15.3,44.1),(16.7,43.5),(18.5,42.4),(19.5,41.8),(19.3,40.4),(20.2,39.6),(21.2,38.9),(21,38.2),(21.6,37.6),(21.7,36.8),(22.5,36.5),(23,36.4),(23.2,37.3),(22.9,37.9),(23.9,37.7),(24,38.2),(23.1,39.1),(22.6,40.1),(22.7,40.6),(24,40.1),(24.6,40.9),(26,40.8),(26.3,40.1),(26.2,39.5),(26.7,38.9),(26.4,38.3),(27.2,37.9),(27.2,37),(28.2,36.7),(29.1,36.6),(29.8,36.2),(30.6,36.9),(32,36.5),(32.8,36),(34.1,36.3),(34.9,36.7),(35.6,36.6),(36.2,36.9),(35.9,36.2),(35.7,35.6),(35.8,34.8),(35.5,33.8),(35,32.8),(34.4,31.6),(33.4,31.1),(32.2,31.3),(31.5,31.5),(30.5,31.5),(29.9,31.2),(28.4,31.1),(25.1,31.6),(23.1,32.4),(21.4,32.8),(20.1,32.1),(19.6,30.9),(18.7,30.3),(17,31.1),(15.5,31.4),(14.8,32.4),(12.1,32.8),(11.1,33.1),(10.2,33.9),(11.1,35.2),(10.5,35.9),(11.1,37.1),(10.3,36.8),(9.8,37.3),(7.8,36.9),(6.4,37),(5.3,36.6),(3,36.8),(1,36.5),(-1.2,35.4),(-2.9,35.3),(-4.7,35.2),(-5.5,35.9)],
 [(12.4,38),(13.4,38.2),(15.6,38.3),(15.2,37.2),(15.1,36.7),(13.4,37.1),(12.4,38)],[(8.2,40.9),(9.4,41.2),(9.8,40),(9.5,39.1),(8.5,39),(8.2,40.9)],[(8.6,42.5),(9.5,43),(9.4,41.4),(8.8,41.6),(8.6,42.5)],[(23.5,35.5),(26.2,35.3),(25.7,35),(23.5,35.2),(23.5,35.5)],[(32.3,35),(34.6,35.7),(33.9,34.9),(32.6,34.6),(32.3,35)]]
def diagram(key,s,step=0):
 p=Plate(s);p.label('DIAGRAM｜模式図')
 if key=='D_count':
  p.pair('MAR 25｜3月25日',(170,155,740,330),80,49,None)
  p.pair('DEC 25｜12月25日',(1180,155,1750,330),80,49,None)
  for i,month in enumerate(['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']):
   x=74+i*148;lit=2<=i<=2+step
   p.box((x,400,x+138,532),INK if lit else PAPER,RULE)
   p.text(month,(x+3,408,x+135,522),53,color=PAPER if lit else INK)
   p.padding(len(p.metrics)-1,(x,400,x+138,532))
  p.pair('+ 9 months｜＋9か月',(535,605,1385,802),79,48,None)
 if key=='D_map':
  def pos(lon,lat):return (145+(lon+6)*38,165+(46-lat)*49)
  for shore in SHORES:p.line([pos(*point) for point in shore],RULE,3)
  for lon,lat,label in [(12.5,41.9,'ROME｜ローマ'),(36.16,36.2,'ANTIOCH｜アンティオキア')]:
   x,y=pos(lon,lat);p.d.ellipse(tuple(round(v*s) for v in (x-8,y-8,x+8,y+8)),fill=VERMILION)
   b=(x-230,y-127,x+130,y-17) if lon<20 else (x-250,y+15,x+115,y+125)
   p.pair(label,b,56,34,None)
 if key=='D_markers':
  p.d.ellipse(tuple(v*s for v in (570,115,1160,705)),outline=RULE,width=4*s)
  for x,y in [(865,115),(1160,410)]:p.d.ellipse(tuple(v*s for v in (x-10,y-10,x+10,y+10)),fill=VERMILION)
  p.pair('DEC 25 · WINTER SOLSTICE｜12月25日・冬至',(70,155,842,300),54,37,None)
  p.pair('MAR 25 · SPRING EQUINOX｜3月25日・春分',(1090,452,1890,602),54,37,None)
  p.pair("Pliny's calendar markers, not measurements｜プリニウスの暦の目安（観測ではない）",(240,750,1680,885),53,35,None)
 return p
