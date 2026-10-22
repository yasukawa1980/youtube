"""EP003 native graphic compositions; originals preserved, layout recorded in pixels."""
import math,os,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from wom03_produce import ROOT,REPO,MEDIA,read,save,sha,content,ff
Image.MAX_IMAGE_PIXELS=200000000
W,H=1920,1080;BG='#0c1820';GOLD='#d8b575';IVORY='#f4efdf';MUTED='#b0bfc3'
EN='/System/Library/Fonts/Supplemental/Arial.ttf';SERIF='/System/Library/Fonts/Supplemental/Georgia.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
TEXT=[];BOXES=[]
def font(size,value='',serif=False):return ImageFont.truetype(JA if any(ord(c)>0x2fff for c in value) else SERIF if serif else EN,size)
def text(im,xy,value,size=30,color=IVORY,center=False,serif=False):
 d=ImageDraw.Draw(im);f=font(size,value,serif)
 if center:xy=(xy[0]-d.textlength(value,font=f)/2,xy[1])
 bbox=d.textbbox(xy,value,font=f);assert bbox[2]<=1845 and bbox[3]<=700,(value,bbox)
 d.text(xy,value,font=f,fill=color);TEXT.append({'text':value,'bbox':list(bbox)})
def header(im,label='',source=''):
 d=ImageDraw.Draw(im);d.rectangle((0,0,W,109),fill=BG)
 text(im,(92,18),'QUIET ORIGINS  /  EP003',28,GOLD)
 if label:
  f=font(27,label);width=d.textlength(label,font=f);text(im,(1820-width,21),label,27,GOLD)
 if source:text(im,(92,72),source,23,MUTED)
def panel(im,art,box):
 x,y,w,h=box;a=ImageOps.contain(art,(w,h),Image.Resampling.LANCZOS);pos=(x+(w-a.width)//2,y+(h-a.height)//2);im.paste(a,pos);BOXES.append([*pos,pos[0]+a.width,pos[1]+a.height])
def background(art):
 im=ImageOps.fit(art,(W,H),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(55));im=ImageEnhance.Brightness(im).enhance(.35)
 return im

assets={a['id']:a for a in read(ROOT/'records/source_assets.json')['items']}
VIEWS={'A03':1,'A07':1}
images={k:ImageOps.exif_transpose(Image.open(a['originals'][VIEWS.get(k,0)]['path'])).convert('RGB') for k,a in assets.items()}
for a in read(ROOT/'records/ai_images.json'):images[a['id']]=Image.open(a['local_path']).convert('RGB')
TITLES={'A01':'Terracotta pelike','A02':'Canova, Perseus with the Head of Medusa','A03':'Terracotta antefix','A04':'Terracotta painted gorgoneion antefix','A05':'Terracotta Siana cup','A07':'Terracotta stand','A08':'Terracotta eye-cup','A13':'Terracotta column-krater','A14':'Marble statue of Athena','A15':'Terracotta lekythos','A17':'Terracotta antefix','A18':'Gold gorgoneion pendant','A20':'Grave stele of Kalliades','A21':'Bronze mirror: Bellerophon on Pegasus','A22':'Tempesta, Metamorphoses, plate 41','A23':'Terracotta kylix','A24':'Bronze chariot-pole ornament','A25':'Carnelian intaglio: head of Medusa','A26':'Terracotta relief: Achilles with a Gorgon shield'}
# Detail crops are measured against unaltered Met photographs. No generated restoration.
DETAILS={'A05':(2,(.12,.05,.9,.94)),'A21':(1,(.22,.12,.77,.64)),'A07':(0,(.18,.12,.82,.90)),'A14':(0,(.36,.38,.73,.59)),
 'A01':(2,(.70,.438,.835,.513)),'A02':(3,(.405,.36,.64,.653))}

def crop_view(key,view,box):
 art=Image.open(assets[key]['originals'][view]['path']).convert('RGB')
 return art.crop(tuple(round(z*(art.width if i%2==0 else art.height)) for i,z in enumerate(box)))

def diagram(im,key):
 d=ImageDraw.Draw(im);header(im,'SCHEMATIC｜模式図')
 if key=='D_timeline':
  # Literary chronology is approximate; Homer and Hesiod overlap.
  names=[('Hesiod｜ヘシオドス','c. 700 BCE'),('Homer｜ホメロス','8th–7th c. BCE'),('Pindar｜ピンダロス','c. 490 BCE'),('Ovid｜オウィディウス','c. 8 CE'),('[Apollodorus]','1st–2nd c. CE')]
  d.line((210,370,1710,370),fill=GOLD,width=4)
  for i,(name,year) in enumerate(names):
   x=230+i*365;d.ellipse((x-10,360,x+10,380),fill=GOLD);text(im,(x,260),name,27,IVORY,True);text(im,(x,420),year,28,GOLD,True)
   if i==4:text(im,(x,465),'アポロドーロスの名の書',21,MUTED,True)
 elif key=='D_four':
  rows=[('Born a Gorgon','生まれたゴルゴン','Hesiod, Theogony','c. 700 BCE'),('A protecting face','守る顔','Gorgoneia','6th c. BCE'),('A sleeping face','眠る顔','The Met 45.11.1','c. 450–440 BCE'),('A punished woman','罰せられた女性','Ovid, Metamorphoses','c. 8 CE')]
  for i,(en,ja,src,yr) in enumerate(rows):
   x=275+i*455;d.ellipse((x-62,225,x+62,349),outline=GOLD,width=4)
   if i==0:
    for dx in [-35,0,35]:d.arc((x+dx-25,190,x+dx+25,250),180,340,fill=GOLD,width=4)
   elif i==1:d.line((x-85,215,x-85,330,x,390,x+85,330,x+85,215),fill=GOLD,width=4)
   for dx in [-25,25]:
    if i==2:d.arc((x+dx-14,268,x+dx+14,288),0,180,fill=GOLD,width=3)
    else:d.ellipse((x+dx-4,272,x+dx+4,280),fill=GOLD)
   d.arc((x-23,290,x+23,320),0 if i<3 else 180,180 if i<3 else 360,fill=GOLD,width=3)
   text(im,(x,425),en,29,IVORY,True);text(im,(x,475),ja,28,IVORY,True);text(im,(x,555),src,27,MUTED,True);text(im,(x,605),yr,28,GOLD,True)
 else:raise ValueError(key)

def compose(key):
 global TEXT,BOXES
 TEXT=[];BOXES=[];extra={};im=Image.new('RGB',(W,H),BG)
 if key in images:
  art=images[key];im=background(art)
  if key in DETAILS:
   panel(im,art,(80,110,860,820));view,box=DETAILS[key];detail=crop_view(key,view,box)
   if key in ['A01','A02']:
    # Reveal only the face within this single continuous shot, retaining the whole object.
    overlay=Image.new('RGBA',(W,H));panel(overlay,detail,(980,110,860,820));p=ROOT/f'assets/{key}_face_reveal.png';overlay.save(p);extra={'face_reveal':str(p.relative_to(ROOT)),'face_reveal_start_fraction':.35}
   else:panel(im,detail,(980,110,860,820))
   extra.update(detail_view=view,detail_crop_normalized=box)
  else:
   # Crop only empty photographic margins for tiny objects; original pixels remain untouched.
   if key=='A25':art=art.crop((round(art.width*.32),round(art.height*.24),round(art.width*.67),round(art.height*.77)))
   if key=='A18':art=art.crop((round(art.width*.28),round(art.height*.18),round(art.width*.72),round(art.height*.78)))
   if key=='A08':art=art.crop((round(art.width*.22),round(art.height*.17),round(art.width*.76),round(art.height*.85)))
   panel(im,art,(80,110,1760,820))
  source='' if key.startswith('R') else f"The Met • {TITLES[key]} • {assets[key]['date']} • {assets[key]['accession']} • CC0"
  label='AI RECONSTRUCTION｜AIによる再現' if key.startswith('R') else 'PUBLIC DOMAIN PRINT｜パブリックドメインの版画' if key=='A22' else 'MUSEUM OBJECT｜博物館資料'
  header(im,label,source)
 elif key.startswith('V'):
  video=MEDIA/f'{key}_Kling_v01.mp4';poster=ROOT/f'assets/{key}_poster.png'
  if video.exists():
   if not poster.exists():ff(['-ss',5,'-i',video,'-frames:v',1,poster])
   im=background(Image.open(poster).convert('RGB'))
  header(im,'AI RECONSTRUCTION｜AIによる再現');BOXES=[[231,110,1689,930]];source='';label='AI RECONSTRUCTION｜AIによる再現'
 elif key.startswith('D_'):
  diagram(im,key);source='';label='SCHEMATIC｜模式図'
 elif key=='credits':
  header(im);source='';label=''
  rows=[('English','Kokoro / Heart (af_heart)'),('日本語','VOICEVOX:冥鳴ひまり'),('Collection','The Metropolitan Museum of Art • Public Domain / CC0'),('AI images','OpenAI image generation'),('AI video','Kling AI'),('Music','Original ambient score • Quiet Origins')]
  for i,(a,b) in enumerate(rows):text(im,(145,190+i*76),a,30,GOLD);text(im,(470,190+i*76),b,28)
 else:raise ValueError(key)
 assert all(t['bbox'][3]<=700 for t in TEXT)
 return im,{'key':key,'base_asset':key if key[0] in 'ARV' else None,'source':source,'label':label,'texts':TEXT.copy(),'art_boxes':BOXES.copy(),'camera_band':[110,930] if key[0] in 'ARV' else [110,700],**extra}

def main():
 records=[]
 for seg in content('en')['segments']:
  for i,key in enumerate(seg['visuals']):
   im,rec=compose(key);p=ROOT/f'assets/{seg["id"]}_{i+1:02}_{key}.png';im.save(p);records.append({**rec,'segment_id':seg['id'],'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
 save(ROOT/'records/visual_manifest.json',{'shots':records,'canvas':[W,H],'foreground_max_box':[80,110,1840,930],'blur_background_brightness':.35})
 for key in ['A24','A04']:
  art=images[key];im=background(art);panel(im,art,(1000,0,920,1080));d=ImageDraw.Draw(im);d.rectangle((0,0,1000,H),fill=BG)
  d.text((85,245),'MEDUSA',font=font(145,serif=True),fill=IVORY);d.text((90,440),'Monster or Victim?',font=font(78,serif=True),fill=GOLD);d.line((92,590,905,590),fill=GOLD,width=3);d.text((92,860),'QUIET ORIGINS',font=font(49),fill=GOLD)
  im.save(ROOT/f'deliverables/EP003_thumbnail_{key}.jpg',quality=94,optimize=True);p=REPO/f'new-channel/サムネ確認用/wom03/wom03_サムネ_{key}.jpg';im.resize((1280,720)).save(p,quality=88,optimize=True);assert p.stat().st_size<1000000
 for batch in range(math.ceil(len(records)/12)):
  sheet=Image.new('RGB',(1280,1040),BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(records[batch*12:batch*12+12]):
   x=j%3*426;y=j//3*260;im=Image.open(ROOT/s['file']);
   if s.get('face_reveal'):im.paste(Image.open(ROOT/s['face_reveal']),(0,0),Image.open(ROOT/s['face_reveal']))
   sheet.paste(im.resize((426,240)),(x,y));d.text((x+8,y+241),s['segment_id']+' '+s['key'],font=font(14),fill=IVORY)
  sheet.save(ROOT/f'review/compositions_{batch+1}.jpg',quality=85)
 print('VISUALS',len(records),flush=True)
if __name__=='__main__':main()

