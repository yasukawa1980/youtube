"""EP005 native graphic compositions; originals preserved, layout recorded in pixels."""
import math,os,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from wom05_produce import ROOT,REPO,MEDIA,read,save,sha,content,ff
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
 text(im,(92,18),'QUIET ORIGINS  /  EP005',28,GOLD)
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
USED=[k for s in content('en')['segments'] for k in s['visuals'] if k in assets]
originals={k:ImageOps.exif_transpose(Image.open(assets[k]['path'])).convert('RGB') for k in USED}
def crop(art,box):return art.crop(tuple(round(z*(art.width if i%2==0 else art.height)) for i,z in enumerate(box)))
CROPS={'met_57203':(.025,.015,.46,.63),'aic_26700':(.15,.16,.97,.91),'lacma_89199':(.52,.03,.99,.98)}
DETAILS={'ndl_1182143_010':(.600,.590,.655,.730),'ndl_958959_087':(.600,.150,.750,.280),'ndl_851648_028':(.52,.245,.96,.57)}
images={k:crop(a,CROPS[k]) if k in CROPS else a for k,a in originals.items()}
for a in read(ROOT/'records/ai_images.json'):images[a['id']]=Image.open(a['local_path']).convert('RGB')
SOURCES={
'met_40011_DP206881':'Katsushika Hokusai and his disciples • Album of Sketches • 19th c. • The Met, 14.76.59.1–.102',
'met_22470':'Tengu-bo armor mask • c. 1600 • The Met, '+assets['met_22470']['accession'],
'met_23997':'Bird-beaked tengu armor mask • 18th c. • The Met, '+assets['met_23997']['accession'],
'met_24145':'Mask in the Shape of a Mountain Demon’s Face • early 18th c. • Iron, lacquer, silk • The Met, 36.25.263a, b',
'met_57203':'Shibata Zeshin • Persimmons Branch and Wasp Nest above a Hedge (branch detail) • The Met, 36.100.118',
'met_59737':'Two Mythical Creatures (Tengu) Carrying a Parcel • late 19th c. • The Met, 91.1.1037',
'met_60361':'Yoshitsune as a Child with Tengu Fan • 19th c. • The Met, 10.211.1327',
'aic_154960':'Tsukioka Kogyo • Noh play Kurama Tengu • 1898 • Art Institute of Chicago, '+assets['aic_154960']['accession'],
'aic_26700':'Utagawa Hiroshige • Ushiwakamaru on Mount Kurama (detail) • c. 1832–34 • Art Institute of Chicago, 1925.3795',
'lacma_89199':'Kawanabe Kyosai • Yoshitsune Training with the Tengu Sojobo (detail) • 1863 • LACMA, M.84.31.530a-c',
'ndl_12865768_001':'Nihon Shoki • 1669 printed edition • frame 1 • National Diet Library Digital Collections',
'ndl_1182143_010':'Nihon Shoki, vol. 23 • 1926 facsimile • frame 10 • National Diet Library Digital Collections',
'ndl_958959_087':'Shiji, Tianguan shu • c. 1925 printed edition • frame 87 • National Diet Library Digital Collections',
'ndl_945414_003':'Kosho Konjaku Monogatari-shu • 1914 edited edition • frame 3 • National Diet Library Digital Collections',
'ndl_851648_028':'Hokusai manga, vol. 3 (1815), 1878 printing • frame 28 • National Diet Library Digital Collections'}
def diagram(im,key):
 d=ImageDraw.Draw(im);header(im,'SCHEMATIC｜模式図')
 if key=='D_gloss':
  text(im,(390,210),'天',140,GOLD);text(im,(390,380),'狗',140,GOLD)
  for y in range(270,490,25):d.line((560,y,560,y+10),fill=MUTED,width=3)
  text(im,(740,295),'heavenly dog｜天の犬',54)
  text(im,(740,455),'gloss: heavenly fox｜天の狐',48)
 elif key=='D_forms':
  # Separate forms are placed alongside one another, without replacement arrows.
  d.line((195,280,410,415),fill=GOLD,width=5);d.line((225,270,435,398),fill=GOLD,width=3);d.ellipse((422,394,448,420),fill=IVORY)
  d.arc((825,270,1045,495),100,330,fill=GOLD,width=6);d.line((1020,305,1110,365,1030,388),fill=GOLD,width=6);d.ellipse((982,330,995,343),fill=IVORY)
  d.arc((1420,270,1620,495),65,320,fill=GOLD,width=6);d.line((1588,325,1730,345,1730,370,1605,378),fill=GOLD,width=6);d.ellipse((1558,326,1571,339),fill=IVORY)
  for x,label in [(330,'Nihon Shoki, 720'),(960,'Konjaku Monogatari, 12th c.'),(1565,'masks & prints, 1700s–1800s')]:text(im,(x,590),label,31,GOLD,True)
 else:raise ValueError(key)
def compose(key):
 global TEXT,BOXES
 TEXT=[];BOXES=[];extra={};im=Image.new('RGB',(W,H),BG);source='';label=''
 if key in images:
  art=images[key];im=background(art)
  if key in DETAILS:
   panel(im,art,(80,110,860,820));panel(im,crop(originals[key],DETAILS[key]),(980,110,860,820));extra['detail_crop_normalized']=DETAILS[key]
  else:panel(im,art,(80,110,1760,820))
  source=SOURCES.get(key,'')
  if key.startswith('R'):label='AI RECONSTRUCTION｜AIによる再現'
  elif key.startswith('ndl'):label='PRINTED BOOK｜刊本'
  elif key=='met_40011_DP206881':label='DRAWING｜素描'
  elif key=='met_57203':label='PAINTING｜絵画'
  elif key=='aic_154960':label='NOH PRINT｜能の舞台の絵'
  elif key in ['aic_26700','lacma_89199']:label='PUBLIC DOMAIN PRINT｜パブリックドメインの版画'
  else:label='MUSEUM OBJECT｜博物館資料'
  header(im,label,source)
  if key in CROPS:extra['crop_normalized']=CROPS[key]
 elif key.startswith('V'):
  video=MEDIA/f'{key}_Kling_v01.mp4';poster=ROOT/f'assets/{key}_poster.png'
  if video.exists():
   ff(['-ss',3,'-i',video,'-frames:v',1,poster]);im=background(Image.open(poster).convert('RGB'))
  label='AI RECONSTRUCTION｜AIによる再現';source='Legend illustration｜説話のイメージ' if key=='V02' else ''
  header(im,label,source);BOXES=[[231,110,1689,930]]
 elif key.startswith('D_'):diagram(im,key);label='SCHEMATIC｜模式図'
 elif key=='credits':
  header(im)
  rows=[('English','Kokoro / Heart (af_heart)'),('日本語','VOICEVOX:冥鳴ひまり'),('Collections','The Metropolitan Museum of Art'),('Collections','Art Institute of Chicago • LACMA'),('Collections','National Diet Library Digital Collections'),('AI stills / video','OpenAI image generation / Kling AI'),('Music','Original ambient score • Quiet Origins')]
  for i,(a,b) in enumerate(rows):text(im,(145,175+i*71),a,28,GOLD);text(im,(460,175+i*71),b,28)
 else:raise ValueError(key)
 isart=key in images or key.startswith('V')
 return im,{'key':key,'base_asset':key if isart else None,'source':source,'label':label,'texts':TEXT.copy(),'art_boxes':BOXES.copy(),'camera_band':[110,930] if isart else [110,700],**extra}
def main():
 records=[]
 for seg in content('en')['segments']:
  for i,key in enumerate(seg['visuals']):
   im,rec=compose(key);p=ROOT/f'assets/{seg["id"]}_{i+1:02}_{key}.png';im.save(p);records.append({**rec,'segment_id':seg['id'],'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
 save(ROOT/'records/visual_manifest.json',{'shots':records,'canvas':[W,H],'foreground_max_box':[80,110,1840,930],'blur_background_brightness':.35})
 for key in ['met_24145','met_40011_DP206881']:
  art=images[key];im=background(art);panel(im,art,(1000,0,920,1080));d=ImageDraw.Draw(im);d.rectangle((0,0,1000,H),fill=BG)
  d.text((85,245),'TENGU',font=font(165,serif=True),fill=IVORY);d.text((90,455),'The First Was a Star',font=font(66,serif=True),fill=GOLD);d.line((92,590,905,590),fill=GOLD,width=3);d.text((92,860),'QUIET ORIGINS',font=font(49),fill=GOLD)
  im=im.resize((1280,720),Image.Resampling.LANCZOS);dest=ROOT/f'deliverables/EP005_thumbnail_{key}.jpg';im.save(dest,quality=90,optimize=True)
  p=REPO/f'new-channel/サムネ確認用/wom05/wom05_サムネ_{key}.jpg';im.save(p,quality=88,optimize=True);assert p.stat().st_size<1000000
 for batch in range(math.ceil(len(records)/12)):
  sheet=Image.new('RGB',(1280,1040),BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(records[batch*12:batch*12+12]):
   x=j%3*426;y=j//3*260;im=Image.open(ROOT/s['file']);sheet.paste(im.resize((426,240)),(x,y));d.text((x+8,y+241),s['segment_id']+' '+s['key'],font=font(14),fill=IVORY)
  sheet.save(ROOT/f'review/compositions_{batch+1}.jpg',quality=85)
 print('VISUALS',len(records),flush=True)
if __name__=='__main__':main()
