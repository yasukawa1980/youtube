"""EP006 native graphic compositions; originals preserved, layout recorded in pixels."""
import math,os,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from wom06_produce import ROOT,REPO,MEDIA,read,save,sha,content,ff
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
 text(im,(92,18),'QUIET ORIGINS  /  EP006',28,GOLD)
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

assets={a['key']:a for a in read(ROOT/'records/source_assets.json')['assets']}
USED=[]
for seg in content('en')['segments']:
 for key in seg['visuals']:
  USED.extend(key[7:-1].split(',') if key.startswith('D_pair(') else [key] if key in assets else [])
assert len(USED)==len(set(USED))
originals={k:ImageOps.exif_transpose(Image.open(assets[k]['path'])).convert('RGB') for k in USED}
for k in USED:assert sha(assets[k]['path'])==assets[k]['sha256'],k
def crop(art,box):return art.crop(tuple(round(z*(art.width if i%2==0 else art.height)) for i,z in enumerate(box)))
CROPS={'met_437153':(.12,.10,.95,.355)}
DETAILS={'met_544442':(.38,.19,.62,.52),'museo_Inv01_011':(.31,.40,.57,.72),'hesiod_159':(.055,.475,.885,.548),'jebb1904_15':(.045,.770,.90,.850)}
images={k:crop(a,CROPS[k]) if k in CROPS else a for k,a in originals.items()}
SOURCES={
'met_255101':'Terracotta relief of a sphinx • 1st half of 5th c. BCE • The Met, 61.11.8',
'met_286141':'Francis Frith • The Great Pyramid and The Great Sphinx • 1858 • The Met, 2005.100.555',
'museo_Inv02_008':'Attributed to V. R. Lanzone • 1865–70 • Archivio Museo Egizio, Inv02_008',
'museo_Album1_004':'V. R. Lanzone • 1865–70 • Archivio Museo Egizio, Album1_004',
'met_544442':'Sphinx of Hatshepsut • ca. 1473–1458 BCE • The Met, 31.3.166',
'museo_Inv01_011':'F. Bonfils • 1875–77 • Archivio Museo Egizio, Inv01_011',
'met_544823':'Sphinx of Amenhotep II • ca. 1427–1396 BCE • The Met, 30.8.72',
'met_565105':'Scarab with the Representation of a Sphinx • ca. 1200–945 BCE • The Met, 09.180.998',
'hesiod_159':'Hesiod, Theogony • Evelyn-White tr., 1920 printing • p. 103 • University of California Libraries / IA',
'met_248501':'Marble capital and sphinx finial • Attic, ca. 530 BCE • The Met, 11.185d, x',
'met_329999':'Bronze sphinx • late 6th–early 5th c. BCE • The Met, 2021.40.14',
'met_247343':'Terracotta sphinx lekythos • ca. 380–360 BCE • The Met, 06.1021.180',
'jebb1904_15':'Sophocles, Oedipus the King • Jebb tr., 1904 • p. 7, line 130 • Online Library of Liberty',
'met_437153':'Gustave Moreau • Oedipus and the Sphinx (upper detail) • 1864 • The Met, 21.134.1',
'met_261777':'Félix Bonfils • Pyramides et le Sphinx • 1860s–70s, printed ca. 1870 • The Met, 1976.561.2',
'norden_109':'Norden, plate XLVII, London 1780 • Wellcome Collection / Internet Archive',
'museo_Inv02_007':'Anonymous (possibly V. R. Lanzone) • 1875 • Archivio Museo Egizio, Inv02_007'}
def diagram(im,key):
 d=ImageDraw.Draw(im)
 if key.startswith('D_pair('):
  header(im,'SCHEMATIC｜模式図','Senwosret III • The Met, 17.9.2  /  Terracotta sphinx plaque • The Met, X.189')
  for k,x in [('met_544186',130),('met_256761',1040)]:panel(im,images[k],(x,140,750,420))
  for x,label in [(505,'EGYPT｜エジプト'),(1415,'GREECE｜ギリシャ')]:text(im,(x,615),label,40,GOLD,True)
 elif key=='D_riddle':
  header(im,'SCHEMATIC｜模式図')
  # Faceless line figures, no time-of-day symbols. Four points, two feet, then two feet plus cane.
  d.ellipse((475,335,535,395),outline=GOLD,width=7)
  d.line([(470,415),(490,390)],fill=GOLD,width=8)
  d.line([(260,415),(350,395),(470,415)],fill=GOLD,width=8)
  for points in [[(280,410),(245,485),(200,515)],[(330,405),(335,475),(300,515)],[(430,410),(450,515)],[(465,415),(505,515)]]:d.line(points,fill=GOLD,width=8)
  for x,stoop in [(960,False),(1510,True)]:
   d.ellipse((x-30,230,x+30,290),outline=GOLD,width=7)
   hip=x-25 if stoop else x
   d.line([(x,295),(hip,420),(hip-65,530)],fill=GOLD,width=8)
   d.line([(hip,420),(hip+65,530)],fill=GOLD,width=8)
   d.line([(x-5,325),(x-85,390)],fill=GOLD,width=8)
   d.line([(x-5,325),(x+65,380)],fill=GOLD,width=8)
   if stoop:d.line([(x+65,380),(x+90,380),(x+90,530)],fill=IVORY,width=8)
  for x,label in [(360,'four-footed｜四つ足'),(960,'two-footed｜二つ足'),(1545,'three-footed｜三つ足')]:text(im,(x,615),label,34,GOLD,True)
 else:raise ValueError(key)
def compose(key):
 global TEXT,BOXES
 TEXT=[];BOXES=[];extra={};im=Image.new('RGB',(W,H),BG);source='';label=''
 if key in images:
  art=images[key];im=background(art)
  if key in DETAILS:
   panel(im,art,(80,110,860,820));panel(im,crop(originals[key],DETAILS[key]),(980,110,860,820));extra['detail_crop_normalized']=DETAILS[key]
  else:panel(im,art,(80,110,1760,820))
  source=SOURCES[key]
  if key.startswith('museo') or key in ['met_286141','met_261777']:label='HISTORIC PHOTOGRAPH｜古写真'
  elif key.startswith(('hesiod','jebb')):label='PRINTED BOOK｜刊本'
  elif key.startswith('norden'):label='ENGRAVING｜銅版画'
  elif key=='met_437153':label='PAINTING｜絵画'
  else:label='MUSEUM OBJECT｜博物館資料'
  header(im,label,source)
  if key in CROPS:extra['crop_normalized']=CROPS[key];extra['background_also_uses_only_crop']=True
 elif key.startswith('V'):
  video=MEDIA/f'{key}_Kling_v01.mp4';poster=ROOT/f'assets/{key}_poster.png'
  if video.exists():
   ff(['-i',video,'-vf',r'select=eq(n\,30)','-frames:v',1,poster]);im=background(Image.open(poster).convert('RGB'))
  else:extra['missing_video']=True
  label='AI RECONSTRUCTION｜AIによる再現';header(im,label,'Kling AI • painterly illustration');BOXES=[[231,110,1689,930]]
 elif key.startswith('D_'):diagram(im,key);label='SCHEMATIC｜模式図';extra['base_assets']=key[7:-1].split(',') if key.startswith('D_pair(') else []
 elif key=='credits':
  header(im)
  rows=[('English','Kokoro / Heart (af_heart)'),('日本語','VOICEVOX:冥鳴ひまり'),('Collections','The Metropolitan Museum of Art'),('Collections','Archivio Museo Egizio • Wellcome Collection'),('Texts','University of California Libraries • Online Library of Liberty'),('AI video','Kling AI'),('Music','Original ambient score • Quiet Origins')]
  for i,(a,b) in enumerate(rows):text(im,(145,175+i*71),a,27,GOLD);text(im,(420,175+i*71),b,27)
 else:raise ValueError(key)
 isart=key in images or key.startswith('V')
 return im,{'key':key,'base_asset':key if isart else None,'source':source,'label':label,'texts':TEXT.copy(),'art_boxes':BOXES.copy(),'camera_band':[110,930] if isart else [110,700],**extra}
def main():
 records=[]
 for seg in content('en')['segments']:
  for i,key in enumerate(seg['visuals']):
   im,rec=compose(key);p=ROOT/f'assets/{seg["id"]}_{i+1:02}_{key}.png';im.save(p);records.append({**rec,'segment_id':seg['id'],'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
 save(ROOT/'records/visual_manifest.json',{'shots':records,'canvas':[W,H],'foreground_max_box':[80,110,1840,930],'blur_background_brightness':.35,'unique_originals':USED})
 destdir=REPO/'new-channel/サムネ確認用/wom06';destdir.mkdir(parents=True,exist_ok=True)
 for key in ['museo_Album1_004','met_544442']:
  art=images[key];im=background(art);panel(im,art,(1000,0,920,1080));d=ImageDraw.Draw(im);d.rectangle((0,0,1000,H),fill=BG)
  d.text((85,245),'SPHINX',font=font(165,serif=True),fill=IVORY);d.text((90,455),'Never Asked a Riddle',font=font(66,serif=True),fill=GOLD);d.line((92,590,905,590),fill=GOLD,width=3);d.text((92,860),'QUIET ORIGINS',font=font(49),fill=GOLD)
  im=im.resize((1280,720),Image.Resampling.LANCZOS);dest=ROOT/f'deliverables/EP006_thumbnail_{key}.jpg';im.save(dest,quality=90,optimize=True)
  p=destdir/f'wom06_サムネ_{key}.jpg';im.save(p,quality=88,optimize=True);assert p.stat().st_size<1000000
 for batch in range(math.ceil(len(records)/12)):
  sheet=Image.new('RGB',(1280,1040),BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(records[batch*12:batch*12+12]):
   x=j%3*426;y=j//3*260;im=Image.open(ROOT/s['file']);sheet.paste(im.resize((426,240)),(x,y));d.text((x+8,y+241),s['segment_id']+' '+s['key'],font=font(14),fill=IVORY)
  sheet.save(ROOT/f'review/compositions_{batch+1}.jpg',quality=85)
 print('VISUALS',len(records),flush=True)
if __name__=='__main__':main()
