"""EP002 native graphic compositions; originals preserved, layout recorded in pixels."""
import math,os,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from wom02_produce import ROOT,REPO,MEDIA,read,save,sha,content
Image.MAX_IMAGE_PIXELS=200000000
W,H=1920,1080;BG='#0c1820';GOLD='#d8b575';IVORY='#f4efdf';MUTED='#b0bfc3'
EN='/System/Library/Fonts/Supplemental/Arial.ttf';SERIF='/System/Library/Fonts/Supplemental/Georgia.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
TEXT=[];BOXES=[]
assets={a['id']:a for a in read(ROOT/'records/source_assets.json')['assets']}
images={k:ImageOps.exif_transpose(Image.open(a['original_local_path'])).convert('RGB') for k,a in assets.items()}
for a in read(ROOT/'records/ai_images.json'):images[a['id']]=Image.open(a['local_path']).convert('RGB')
SOURCES={'A01':'Library of Congress • William Nicholson, 1819 • LC-DIG-pga-07781',
 'A02':'NYPL • The witch • United States, ca. 1900–1910 • Image 1587780',
 'A03':'The Met • Osservanza Master, ca. 1430–40 • 1975.1.2484 • CC0',
 'A04':'The Met • Spanish Painter, ca. 1400 • 39.54 • CC0',
 'A05':'Lugdunum, Lyon • Photo: Ruthven, 2018 • Wikimedia Commons • CC0',
 'A06':'Wellcome Collection • Collectanea, Vol. II, 1786 • Public Domain',
 'A07':'Library of Congress • Dorothea Lange • California, USA, 1938 • LC-USF34-018556-D'}
LABEL={'A01':'PUBLIC DOMAIN PRINT｜パブリックドメインの版画','A02':'PUBLIC DOMAIN POSTCARD｜パブリックドメインの絵はがき','A03':'MUSEUM OBJECT｜博物館資料','A04':'MUSEUM OBJECT｜博物館資料','A05':'MUSEUM OBJECT｜博物館資料','A06':'PUBLIC DOMAIN BOOK｜パブリックドメインの書籍','A07':'ARCHIVAL PHOTOGRAPH｜記録写真'}
CROPS={'A01':(.32,.24,.68,.63),'A03':(.28,.38,.73,.88),'A04':(.26,.18,.75,.67),'A05':(.0,.31,.40,.67),'A06':(.08,.02,.95,.27)}

def font(size,value='',serif=False):return ImageFont.truetype(JA if any(ord(c)>0x2fff for c in value) else SERIF if serif else EN,size)
def text(im,xy,value,size=30,color=IVORY,center=False,serif=False):
 d=ImageDraw.Draw(im);f=font(size,value,serif)
 if center:xy=(xy[0]-d.textlength(value,font=f)/2,xy[1])
 bbox=d.textbbox(xy,value,font=f);assert bbox[2]<=1845 and bbox[3]<=700,(value,bbox)
 d.text(xy,value,font=f,fill=color);TEXT.append({'text':value,'bbox':list(bbox)})
def header(im,label='',source=''):
 d=ImageDraw.Draw(im);d.rectangle((0,0,W,142),fill=BG)
 text(im,(92,24),'QUIET ORIGINS  /  EP002',28,GOLD)
 if label:
  f=font(27,label);width=d.textlength(label,font=f);text(im,(1820-width,27),label,27,GOLD)
 if source:text(im,(92,94),source,28,MUTED)
def panel(im,art,box):
 x,y,w,h=box;a=ImageOps.contain(art,(w,h),Image.Resampling.LANCZOS);pos=(x+(w-a.width)//2,y+(h-a.height)//2);im.paste(a,pos);BOXES.append([*pos,pos[0]+a.width,pos[1]+a.height])
def background(art):
 im=ImageOps.fit(art,(W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(55));im=ImageEnhance.Brightness(im).enhance(.35)
 return im

def arrow(d,a,b):
 d.line((*a,*b),fill=GOLD,width=6);dx,dy=b[0]-a[0],b[1]-a[1];ang=math.atan2(dy,dx)
 pts=[b,(b[0]-22*math.cos(ang-.6),b[1]-22*math.sin(ang-.6)),(b[0]-22*math.cos(ang+.6),b[1]-22*math.sin(ang+.6))];d.polygon(pts,fill=GOLD)
def icon(d,kind,x,y,scale=1):
 s=scale;c=GOLD
 def line(points,w=5):d.line([(x+a*s,y+b*s) for a,b in points],fill=c,width=round(w*s))
 def ellipse(box):d.ellipse(tuple([x+box[0]*s,y+box[1]*s,x+box[2]*s,y+box[3]*s]),outline=c,width=round(4*s))
 if kind=='calendar':
  d.rounded_rectangle((x-65*s,y-65*s,x+65*s,y+65*s),10,outline=c,width=4);line([(-65,-30),(65,-30)])
  for a in [-32,0,32]:
   for b in [0,30]:ellipse((a-5,b-5,a+5,b+5))
 elif kind=='book':
  line([(-75,-55),(-10,-45),(0,-35),(10,-45),(75,-55),(75,55),(10,65),(0,75),(-10,65),(-75,55),(-75,-55)])
  line([(0,-35),(0,75)])
 elif kind=='nuts':
  for a,b in [(-35,20),(30,20),(0,-28)]:ellipse((a-23,b-25,a+23,b+25));line([(a-18,b-15),(a+18,b-15)],3)
 elif kind=='ship':
  line([(-90,20),(85,20),(55,60),(-60,60),(-90,20)]);line([(0,20),(0,-80),(65,0),(0,0)])
  for dy in [75,95]:line([(-95,dy),(-65,dy-8),(-30,dy),(5,dy-8),(40,dy),(75,dy-8),(95,dy)],3)
 elif kind=='quill':
  line([(-55,65),(55,-65)]);d.polygon([(x-40*s,y+35*s),(x-25*s,y-35*s),(x+65*s,y-80*s),(x+40*s,y-10*s)],outline=c,width=4)
 elif kind=='person':
  ellipse((-25,-75,25,-25));line([(0,-25),(0,35),(-35,80)]);line([(0,35),(35,80)]);line([(-50,10),(0,-10),(50,10)])
 elif kind=='lantern':
  ellipse((-22,-70,22,-30));d.rectangle((x-35*s,y-30*s,x+35*s,y+50*s),outline=c,width=4);line([(-45,50),(45,50)]);ellipse((-6,-5,6,25))
 elif kind=='root':
  ellipse((-65,-50,65,65));line([(-20,-50),(0,-75),(20,-50)]);line([(-40,-8),(-15,-8)]);line([(15,-8),(40,-8)]);line([(-30,30),(0,42),(30,30)])
 elif kind=='sun':
  ellipse((-30,-30,30,30))
  for an in range(0,360,45):
   r=math.radians(an);line([(45*math.cos(r),45*math.sin(r)),(65*math.cos(r),65*math.sin(r))],4)

def season(im,d,compact=False):
 cx,cy,r=(960,415,190) if not compact else (1320,415,170)
 d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=MUTED,width=10)
 d.arc((cx-r,cy-r,cx+r,cy+r),270,360,fill=GOLD,width=20)
 for ang in [0,90,180,270]:
  a=math.radians(ang);d.ellipse((cx+r*math.cos(a)-7,cy+r*math.sin(a)-7,cx+r*math.cos(a)+7,cy+r*math.sin(a)+7),fill=GOLD)
 text(im,(cx,cy-18),'Samhain',40,GOLD,True,True)
 text(im,(cx,cy+r+34),'Winter begins｜冬のはじまり',29,MUTED,True)
 icon(d,'sun',cx-r-100,cy,.55)

def compose(key):
 global TEXT,BOXES
 TEXT=[];BOXES=[];base=key.replace('_detail','');detailed=key.endswith('_detail')
 if base in images:
  art=images[base];im=background(art)
  if detailed:
   panel(im,art,(100,164,600,526));box=CROPS[base];crop=art.crop(tuple(round(v*(art.width if i%2==0 else art.height)) for i,v in enumerate(box)))
   panel(im,crop,(775,164,1045,526))
  else:panel(im,art,(100,154,1720,536))
  if base.startswith('R'):header(im,'AI RECONSTRUCTION｜AIによる再現','')
  else:header(im,LABEL[base],SOURCES[base])
  if base=='A07':text(im,(960,653),'1938 • California, USA｜米国カリフォルニア',27,GOLD,True)
 else:
  im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);header(im)
  if key=='D_trail':
   order=['A03','A06','A01','A02'];years=['1430–1440','1786','1819','1900–1910'];labels=['The Met','Wellcome','Library of Congress','NYPL']
   for i,(a,year,label) in enumerate(zip(order,years,labels)):
    x=110+i*450;panel(im,images[a],(x,190,350,360));text(im,(x+175,575),year,33,GOLD,True);text(im,(x+175,630),label,26,MUTED,True)
   # Chronology follows object dates, not list order in the request's parenthetical.
  elif key=='D_texts':
   d.rounded_rectangle((150,230,750,580),24,outline='#42535b',width=3);icon(d,'book',450,355,1.1)
   text(im,(450,490),'8th–12th c.｜8〜12世紀',34,GOLD,True);season(im,d,True)
  elif key=='D_season':season(im,d)
  elif key=='D_story_record':
   icon(d,'person',430,340,1);icon(d,'quill',1430,340,1.3);arrow(d,(650,390),(1200,390))
   for i in range(6):d.line((720+i*75,460,720+i*75,490),fill=MUTED,width=3)
   text(im,(430,550),'Event｜出来事',35,IVORY,True);text(im,(1430,550),'Later story｜後世の物語',35,IVORY,True)
  elif key=='D_calendar':
   for x,month,day,title in [(300,'OCT',31,'Eve｜前夜'),(1100,'NOV',1,'All Saints｜諸聖人の日')]:
    d.rounded_rectangle((x,200,x+520,600),25,outline=MUTED,width=4);d.rectangle((x+2,202,x+518,285),fill='#243942')
    text(im,(x+260,218),month,46,GOLD,True);text(im,(x+260,315),str(day),140,IVORY,True,True);text(im,(x+260,625),title,34,GOLD,True)
  elif key=='D_jack':
   icon(d,'person',320,350,.9);icon(d,'lantern',430,360,.8)
   # Three small light symbols over waves represent marsh lights.
   for x in [650,715,780]:d.ellipse((x-10,320,x+10,340),fill=GOLD);d.line((x-22,420,x,410,x+22,420),fill=MUTED,width=3)
   arrow(d,(900,380),(1160,380));icon(d,'root',1450,350,1.5)
   text(im,(550,570),'1600s',55,GOLD,True,True);text(im,(1450,570),'1800s',55,GOLD,True,True)
  elif key=='D_layers':
   rows=[('ship','1800s–1900s'),('nuts','1700s–1800s'),('calendar','800s'),('sun','Season｜季節')]
   for i,(kind,year) in enumerate(rows):
    y=200+i*120;left=360-i*50;right=1560+i*50;d.rounded_rectangle((left,y,right,y+100),16,fill=['#28434c','#233d46','#1e3540','#192d37'][i],outline='#50606a',width=2)
    icon(d,kind,620,y+45,.40);text(im,(1030,y+20),year,39,GOLD,True)
  elif key=='credits':
   rows=[('English','Kokoro / Heart (af_heart)'),('日本語','VOICEVOX:冥鳴ひまり'),('Collections','The Met • Library of Congress • NYPL'),('Collections','Wellcome Collection • Wikimedia Commons / Ruthven (CC0)'),('Reconstructions','AI-generated • R01–R03'),('Music','Original ambient score • Quiet Origins')]
   for i,(a,b) in enumerate(rows):
    y=200+i*76;text(im,(145,y),a,30,GOLD);text(im,(470,y),b,28,IVORY)
  else:raise ValueError(key)
 assert all(b[3]<=700 for b in BOXES) and all(x['bbox'][3]<=700 for x in TEXT)
 return im,{'key':key,'base_asset':base if base in images else None,'source':SOURCES.get(base,''),'label':('AI RECONSTRUCTION｜AIによる再現' if base.startswith('R') else LABEL.get(base,'')),'texts':TEXT.copy(),'art_boxes':BOXES.copy(),'crop_normalized':CROPS.get(base) if detailed else None}

def main():
 records=[]
 for seg in content('en')['segments']:
  for i,key in enumerate(seg['visuals']):
   im,rec=compose(key);p=ROOT/f'assets/{seg["id"]}_{i+1:02}_{key}.png';im.save(p)
   records.append({**rec,'segment_id':seg['id'],'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
 save(ROOT/'records/visual_manifest.json',{'shots':records,'canvas':[W,H],'text_art_bottom_limit':700,'blur_background_brightness':.35,'D_trail_order':'A03, A06, A01, A02 chronological by object date'})
 # Thumbnail uses the same Georgia/Arial/Hiragino families as EP001.
 im=ImageOps.fit(images['A02'],(W,H),centering=(.5,.4));im.paste(ImageOps.fit(images['A02'],(940,H),centering=(.5,.4)),(980,0));d=ImageDraw.Draw(im);d.rectangle((0,0,1000,H),fill=BG)
 d.text((85,245),'HALLOWEEN',font=font(127,serif=True),fill=IVORY);d.text((90,430),'Celtic or Not?',font=font(82,serif=True),fill=GOLD);d.line((92,580,875,580),fill=GOLD,width=3);d.text((92,860),'QUIET ORIGINS',font=font(49),fill=GOLD)
 im.save(ROOT/'deliverables/EP002_thumbnail_en.jpg',quality=94,optimize=True)
 small=im.resize((1280,720),Image.Resampling.LANCZOS);p=REPO/'new-channel/サムネ確認用/wom02/wom02_サムネ.jpg';small.save(p,quality=88,optimize=True);assert p.stat().st_size<1000000
 # Source check sheets before rendering; final shot sheets will be extracted from MP4.
 for batch in range(math.ceil(len(records)/12)):
  subset=records[batch*12:batch*12+12];sheet=Image.new('RGB',(1280,1040),BG);draw=ImageDraw.Draw(sheet)
  for k,s in enumerate(subset):
   x=(k%3)*426;y=(k//3)*260;pic=Image.open(ROOT/s['file']).resize((426,240));sheet.paste(pic,(x,y));draw.text((x+8,y+241),s['segment_id']+' '+s['key'],font=font(14),fill=IVORY)
  sheet.save(ROOT/f'review/compositions_{batch+1}.jpg',quality=85,optimize=True)
 print('VISUALS',len(records),flush=True)
if __name__=='__main__':main()
