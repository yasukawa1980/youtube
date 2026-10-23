"""EP004 native graphic compositions; originals preserved, layout recorded in pixels."""
import math,os,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from wom04_produce import ROOT,REPO,MEDIA,read,save,sha,content,ff
Image.MAX_IMAGE_PIXELS=200000000
W,H=1920,1080;BG='#0c1820';GOLD='#d8b575';IVORY='#f4efdf';MUTED='#b0bfc3'
EN='/System/Library/Fonts/Supplemental/Arial.ttf';SERIF='/System/Library/Fonts/Supplemental/Georgia.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
TEXT=[];BOXES=[]
def font(size,value='',serif=False):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Unicode.ttf' if any(0x1f00<=ord(c)<=0x1fff for c in value) else JA if any(ord(c)>0x2fff for c in value) else SERIF if serif else EN,size)
def text(im,xy,value,size=30,color=IVORY,center=False,serif=False):
 d=ImageDraw.Draw(im);f=font(size,value,serif)
 if center:xy=(xy[0]-d.textlength(value,font=f)/2,xy[1])
 bbox=d.textbbox(xy,value,font=f);assert bbox[2]<=1845 and bbox[3]<=700,(value,bbox)
 d.text(xy,value,font=f,fill=color);TEXT.append({'text':value,'bbox':list(bbox)})
def header(im,label='',source=''):
 d=ImageDraw.Draw(im);d.rectangle((0,0,W,109),fill=BG)
 text(im,(92,18),'QUIET ORIGINS  /  EP004',28,GOLD)
 if label:
  f=font(27,label);width=d.textlength(label,font=f);text(im,(1820-width,21),label,27,GOLD)
 if source:
  size=23
  while d.textlength(source,font=font(size,source))>1730:size-=1
  assert size>=17,(source,size)
  text(im,(92,69),source,size,MUTED)
def panel(im,art,box):
 x,y,w,h=box;a=ImageOps.contain(art,(w,h),Image.Resampling.LANCZOS);pos=(x+(w-a.width)//2,y+(h-a.height)//2);im.paste(a,pos);BOXES.append([*pos,pos[0]+a.width,pos[1]+a.height])
def background(art):
 im=ImageOps.fit(art,(W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(55));im=ImageEnhance.Brightness(im).enhance(.35)
 return im

assets={a['asset_id']:a for a in read(ROOT/'records/source_assets.json')['assets']}
USED=['A01','A02','A04','A05','A06','A07','A08','A09','A10','A11','A12','A13','A14','A15','A16','A17','A21','A29']
originals={k:ImageOps.exif_transpose(Image.open(assets[k]['local_path'])).convert('RGB') for k in USED}
# Crops are non-destructive display instructions, measured on the original photographs.
CROPS={'A13':(.022,.505,.455,.94),'A04':(.66,.025,.968,.49),'A07':(.435,.075,.615,.265),'A08':(.33,.125,.62,.35),'A21':(.02,.425,.98,.98),'A14':(.079,.036,.935,.63),'A15':(.29,.485,.565,.642)}
def crop(art,box):return art.crop(tuple(round(z*(art.width if i%2==0 else art.height)) for i,z in enumerate(box)))
images={k:crop(a,CROPS[k]) if k in CROPS else a for k,a in originals.items()}
for a in read(ROOT/'records/ai_images.json'):images[a['id']]=Image.open(a['local_path']).convert('RGB')
SOURCES={
 'A01':'Pithos • Crete, c. 675 BCE • Louvre, CA 4523 • Photo: Jastrow (PD)',
 'A02':'Relief pithos • c. 670 BCE • Louvre, CA 795 • Photo: Shonagon (CC0)',
 'A04':'Guido Reni, Prometheus with a torch (scene 4) • 1603 • The Met, 51.501.4891',
 'A05':'Chous: return of Hephaestus • c. 430–420 BCE • The Met, 08.258.22',
 'A06':'Lekythos: Athena • c. 480 BCE • The Met, 27.122.6',
 'A07':'Terracotta Aphrodite (head detail) • 3rd c. BCE • The Met, 12.232.12',
 'A08':'Bronze Hermes (head and shoulders) • 1st c. BCE–2nd c. CE • The Met, 97.22.1',
 'A09':'Lenormant Athena • Roman period • NAM Athens, 128 • Photo: Jona Lendering / Livius (CC0)',
 'A10':'Terracotta pyxis with lid • late 5th c. BCE • The Met, 75.2.18a, b',
 'A11':'Dürer, Erasmus of Rotterdam • 1526 • The Met, 19.73.120',
 'A12':'Erasmus, Adagia • Aldus, Venice, 1508 • fol. 12r • ULiège Library, R00134C',
 'A13':'Master Z.B.M., Pandora Opening Her Box (detail) • 1557 • NGA, 1972.33.8',
 'A14':'Serwouters, Pandora en Epimetheus • 1601–1657 • Rijksmuseum, RP-P-1886-A-10526',
 'A15':'Van Nijmegen, Pandora ceiling design (detail) • 1677–1755 • Rijksmuseum, RP-T-1968-157',
 'A16':'Psyche opening the box, plate 28 • 1530–1560 • The Met, 41.71.3(28)',
 'A17':'Hesiod, Works and Days | later manuscript • c. 1500–1525 • Houghton, MS Gr 20, fol. 10',
 'A21':'Bonasone, Epimetheus opens Pandora’s urn (detail) • 16th c. • Rijksmuseum, RP-P-1962-338',
 'A29':'Frederic Edwin Church, The Parthenon • 1871 • The Met, 15.30.67'}
PRINTS=['A04','A13','A14','A16','A21']
LABELS={'A11':'PUBLIC DOMAIN PRINT｜パブリックドメインの版画','A15':'DRAWING｜素描','A17':'MANUSCRIPT｜写本','A12':'PRINTED BOOK｜刊本','A29':'PAINTING｜絵画'}
def diagram(im,key):
 d=ImageDraw.Draw(im);header(im,'SCHEMATIC｜模式図')
 if key=='D_elpis':
  text(im,(960,240),'ἐλπίς / elpis',88,GOLD,True,True)
  text(im,(960,430),'hope｜希望',58,IVORY,True)
  text(im,(960,555),'expectation｜予想',58,IVORY,True)
 elif key=='D_timeline':
  for i,(name,date) in enumerate([('Hesiod','c. 700 BCE'),('Babrius',''),('Erasmus','1508'),('paintings','1500s–1800s')]):
   x=285+i*450
   if i<2:
    d.line([(x-65,285),(x-70,320),(x-112,370),(x-120,445),(x-92,505),(x+92,505),(x+120,445),(x+112,370),(x+70,320),(x+65,285)],fill=GOLD,width=5)
    d.ellipse((x-75,270,x+75,300),outline=GOLD,width=5)
    if i==1:d.ellipse((x+110,484,x+175,505),outline=GOLD,width=4)
    else:d.arc((x-100,365,x+100,425),0,180,fill=GOLD,width=3)
   elif i==2:
    d.rounded_rectangle((x-105,350,x+105,475),radius=10,outline=GOLD,width=5);d.line((x-105,385,x+105,385),fill=GOLD,width=4)
   else:
    d.rectangle((x-155,270,x+155,510),outline=MUTED,width=4)
    d.rectangle((x-88,365,x+88,460),outline=GOLD,width=5);d.polygon([(x-88,365),(x-65,325),(x+108,325),(x+88,365)],outline=GOLD,width=4)
   text(im,(x,555),name,35,IVORY,True);text(im,(x,615),date,31,GOLD,True)
 else:raise ValueError(key)
def compose(key):
 global TEXT,BOXES
 TEXT=[];BOXES=[];extra={};im=Image.new('RGB',(W,H),BG);source='';label=''
 if key in images:
  art=images[key];im=background(art)
  if key=='A12':
   panel(im,art,(80,110,860,820));box=(.045,.565,.68,.642)
   panel(im,crop(art,box),(980,110,860,820));extra['detail_crop_normalized']=box
  else:panel(im,art,(80,110,1760,820))
  source=SOURCES.get(key,'')
  label='AI RECONSTRUCTION｜AIによる再現' if key.startswith('R') else LABELS.get(key,'PUBLIC DOMAIN PRINT｜パブリックドメインの版画' if key in PRINTS else 'MUSEUM OBJECT｜博物館資料')
  header(im,label,source)
  if key in CROPS:extra['crop_normalized']=CROPS[key]
 elif key.startswith('V'):
  video=MEDIA/f'{key}_Kling_v01.mp4';poster=ROOT/f'assets/{key}_poster.png'
  if video.exists():
   if not poster.exists():ff(['-ss',5,'-i',video,'-frames:v',1,poster])
   im=background(Image.open(poster).convert('RGB'))
  label='AI RECONSTRUCTION｜AIによる再現';source='Fable illustration｜寓話のイメージ' if key=='V02' else ''
  header(im,label,source);BOXES=[[231,110,1689,930]]
 elif key.startswith('D_'):diagram(im,key);label='SCHEMATIC｜模式図'
 elif key=='credits':
  header(im)
  rows=[('English','Kokoro / Heart (af_heart)'),('日本語','VOICEVOX:冥鳴ひまり'),('Collections','The Met • Louvre • NAM Athens • NGA'),('Collections','Rijksmuseum • Houghton Library • ULiège Library'),('Photographs','Jastrow • Shonagon • Jona Lendering / Livius'),('AI stills / video','OpenAI image generation / Kling AI'),('Music','Original ambient score • Quiet Origins')]
  for i,(a,b) in enumerate(rows):text(im,(145,175+i*71),a,28,GOLD);text(im,(460,175+i*71),b,28)
 else:raise ValueError(key)
 return im,{'key':key,'base_asset':key if key[0] in 'ARV' else None,'source':source,'label':label,'texts':TEXT.copy(),'art_boxes':BOXES.copy(),'camera_band':[110,930] if key[0] in 'ARV' else [110,700],**extra}
def main():
 records=[]
 for seg in content('en')['segments']:
  for i,key in enumerate(seg['visuals']):
   im,rec=compose(key);p=ROOT/f'assets/{seg["id"]}_{i+1:02}_{key}.png';im.save(p);records.append({**rec,'segment_id':seg['id'],'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
 save(ROOT/'records/visual_manifest.json',{'shots':records,'canvas':[W,H],'foreground_max_box':[80,110,1840,930],'blur_background_brightness':.35})
 for key in ['A01','A21']:
  art=images[key] if key=='A01' else crop(originals[key],(.45,.58,.98,.98))
  im=background(art);panel(im,art,(1000,0,920,1080));d=ImageDraw.Draw(im);d.rectangle((0,0,1000,H),fill=BG)
  d.text((85,245),'PANDORA',font=font(145,serif=True),fill=IVORY);d.text((90,440),'Never a Box',font=font(78,serif=True),fill=GOLD);d.line((92,590,905,590),fill=GOLD,width=3);d.text((92,860),'QUIET ORIGINS',font=font(49),fill=GOLD)
  im.save(ROOT/f'deliverables/EP004_thumbnail_{key}.jpg',quality=94,optimize=True)
  p=REPO/f'new-channel/サムネ確認用/wom04/wom04_サムネ_{key}.jpg';im.resize((1280,720),Image.Resampling.LANCZOS).save(p,quality=88,optimize=True);assert p.stat().st_size<1000000
 for batch in range(math.ceil(len(records)/12)):
  sheet=Image.new('RGB',(1280,1040),BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(records[batch*12:batch*12+12]):
   x=j%3*426;y=j//3*260;im=Image.open(ROOT/s['file']);sheet.paste(im.resize((426,240)),(x,y));d.text((x+8,y+241),s['segment_id']+' '+s['key'],font=font(14),fill=IVORY)
  sheet.save(ROOT/f'review/compositions_{batch+1}.jpg',quality=85)
 print('VISUALS',len(records),flush=True)
if __name__=='__main__':main()
