"""EP007: documented native compositions using original scans; no text rewriting."""
import math
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from wom07_produce import ROOT,REPO,read,save,sha,content,ff,ai_video
Image.MAX_IMAGE_PIXELS=200000000
W,H=1920,1080;BG='#0c1820';GOLD='#d8b575';IVORY='#f4efdf';MUTED='#b0bfc3'
EN='/System/Library/Fonts/Supplemental/Arial.ttf';SERIF='/System/Library/Fonts/Supplemental/Georgia.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
TEXT=[];BOXES=[]
def font(size,value='',serif=False):return ImageFont.truetype(JA if any(ord(c)>0x2fff for c in value) else SERIF if serif else EN,size)
def text(im,xy,value,size=30,color=IVORY,center=False,serif=False):
 d=ImageDraw.Draw(im);f=font(size,value,serif)
 if center:xy=(xy[0]-d.textlength(value,font=f)/2,xy[1])
 bbox=d.textbbox(xy,value,font=f);assert bbox[0]>=65 and bbox[2]<=1850 and bbox[3]<=700,(value,bbox)
 d.text(xy,value,font=f,fill=color);TEXT.append({'text':value,'bbox':list(bbox)})
def header(im,label='',source=''):
 d=ImageDraw.Draw(im);d.rectangle((0,0,W,109),fill=BG)
 text(im,(92,18),'QUIET ORIGINS  /  EP007',28,GOLD)
 if label:
  f=font(27,label);text(im,(1820-d.textlength(label,font=f),21),label,27,GOLD)
 if source:
  size=23
  while d.textlength(source,font=font(size,source))>1730:size-=1
  assert size>=17,(source,size)
  text(im,(92,69),source,size,MUTED)
def panel(im,art,box):
 x,y,w,h=box;a=ImageOps.contain(art,(w,h),Image.Resampling.LANCZOS);pos=(x+(w-a.width)//2,y+(h-a.height)//2);im.paste(a,pos);BOXES.append([*pos,pos[0]+a.width,pos[1]+a.height])
def background(art):return ImageEnhance.Brightness(ImageOps.fit(art,(W,H)).filter(ImageFilter.GaussianBlur(55))).enhance(.35)
def crop(art,box):return art.crop(tuple(round(z*(art.width if i%2==0 else art.height)) for i,z in enumerate(box)))
assets={a['key']:a for a in read(ROOT/'records/source_assets.json')['assets']}
PLAN={s['id']:[('D_young' if x=='G04-01|D_young' else x) for x in s['visuals']] for s in content('en')['segments']}
USED=[x for values in PLAN.values() for x in values if x in assets];assert len(USED)==len(set(USED))
originals={k:ImageOps.exif_transpose(Image.open(assets[k]['path'])).convert('RGB') for k in USED}
for k in USED:assert sha(assets[k]['path'])==assets[k]['sha256']
# Remove scan frame, mount and color chart. Coordinates refer to the complete original.
CROPS={'G07-01':(.116,.185,.854,.763)}
DETAILS={'G02-02':(.175,.145,.87,.24),'G02-01':(.065,.058,.795,.248),'G14-02':(.07,.652,.76,.735),'G14-04':(.065,.075,.755,.134),'G11-02':(.075,.42,.80,.47)}
images={k:crop(v,CROPS[k]) if k in CROPS else v for k,v in originals.items()}
SOURCES={
'G01-01':"Mourt's Relation, London 1622 • Boston Public Library / Internet Archive",
'G02-02':"Mourt's Relation, London 1622 • p. 60 • Boston Public Library / Internet Archive",
'G02-01':"Mourt's Relation, London 1622 • p. 61 • Boston Public Library / Internet Archive",
'G11-02':"Mourt's Relation, London 1622 • p. 37 • Boston Public Library / Internet Archive",
'G14-01':'Winslow, Good Newes, London 1624 • Boston Public Library / Internet Archive',
'G14-02':'Winslow, Good Newes, London 1624 • p. 49 • Boston Public Library / Internet Archive',
'G14-04':'Winslow, Good Newes, London 1624 • p. 51 • Boston Public Library / Internet Archive',
'G08-01':"Harper's Weekly, 27 Nov 1858 (after Winslow Homer) • The Metropolitan Museum of Art",
'G08-02':"Harper's Weekly, 29 Nov 1862 (after Winslow Homer) • The Metropolitan Museum of Art",
'G09-01':'Audubon, The Birds of America, Plate I (1827–30) • University of South Carolina Libraries',
'G06-01':'Proclamation, 3 Oct 1863, National Archives • first page',
'G07-01':'J. L. G. Ferris, The First Thanksgiving 1621 — reproduction print c. 1932, Library of Congress (No known restrictions on publication)'}
def diagram(im,key):
 header(im,'SCHEMATIC｜模式図');d=ImageDraw.Draw(im)
 if key=='D_young':
  for x in [480,1440]:d.ellipse((x-9,305,x+9,323),fill=GOLD)
  d.line((490,314,1430,314),fill='#52636a',width=3)
  for x,a,b in [(480,'1621 LETTER','1621年の手紙'),(1440,'1841 NOTE','1841年の注')]:
   text(im,(x,365),a,47,GOLD,True);text(im,(x,435),b,37,IVORY,True)
  text(im,(1440,565),'"the first Thanksgiving"',42,IVORY,True,True)
 elif key=='D_timeline':
  xs=[290,735,1180,1625];d.line((xs[0],320,xs[-1],320),fill='#40515b',width=4)
  for i,(x,a,b) in enumerate(zip(xs,['1621 LETTER','1841 NAME','1863 NOVEMBER DATE','20TH CENTURY PICTURE'],['1621年の手紙','1841年 名前','1863年 11月の日付','20世紀 絵'])):
   color=GOLD if i==0 else '#819095';d.ellipse((x-10,310,x+10,330),fill=color);text(im,(x,390),a,29,color,True);text(im,(x,450),b,29,color,True)
 else:raise ValueError(key)
def compose(key):
 global TEXT,BOXES
 TEXT=[];BOXES=[];extra={};im=Image.new('RGB',(W,H),BG);source='';label=''
 if key in images:
  art=images[key];im=background(art)
  if key in DETAILS:
   panel(im,art,(70,135,510,795));panel(im,crop(originals[key],DETAILS[key]),(640,150,1200,720));extra['detail_crop_normalized']=DETAILS[key]
   if key=='G02-01':extra['detail_pan_end_normalized']=[.065,.20,.795,.39]
  else:panel(im,art,(80,110,1760,820))
  source=SOURCES[key]
  label=('WOOD ENGRAVING｜木版画' if key.startswith('G08') else 'ENGRAVING｜銅版画' if key=='G09-01' else 'ARCHIVAL DOCUMENT｜公文書' if key=='G06-01' else 'LATER PAINTING｜後世の想像図' if key=='G07-01' else 'PRINTED BOOK｜刊本')
  header(im,label,source)
  if key in CROPS:extra.update(crop_normalized=CROPS[key],background_also_uses_only_crop=True)
 elif key.startswith('V'):
  poster=ROOT/f'assets/{key}_poster.png';video=ai_video(key)
  if video.exists():
   ff(['-i',video,'-frames:v',1,poster]);im=ImageOps.fit(Image.open(poster).convert('RGB'),(W,H))
  else:extra['missing_video']=True
  # Full bleed image; small fixed header above the moving full-frame content.
  label='AI RECONSTRUCTION｜AIによる再現';header(im,label);BOXES=[[0,110,1920,1080]];extra['full_bleed']=True
 elif key.startswith('D_'):diagram(im,key);label='SCHEMATIC｜模式図'
 elif key=='credits':
  header(im)
  rows=[('English','Kokoro / Heart (af_heart)'),('日本語','VOICEVOX:冥鳴ひまり'),('Collections','Boston Public Library • The Metropolitan Museum of Art'),('Collections','University of South Carolina Libraries • National Archives'),('Collections','Library of Congress'),('AI video','Kling AI'),('Music','Suno • QO_THEME_A02 / QO_AMERICA01')]
  for i,(a,b) in enumerate(rows):text(im,(135,175+i*71),a,26,GOLD);text(im,(390,175+i*71),b,26)
 else:raise ValueError(key)
 return im,{'key':key,'base_asset':key if key in images or key.startswith('V') else None,'source':source,'label':label,'texts':TEXT.copy(),'art_boxes':BOXES.copy(),'camera_band':[110,930] if key in images else [110,1080] if key.startswith('V') else [110,700],**extra}
def main():
 records=[]
 for seg,keys in PLAN.items():
  for i,key in enumerate(keys):
   im,rec=compose(key);p=ROOT/f'assets/{seg}_{i+1:02}_{key}.png';im.save(p);records.append({**rec,'segment_id':seg,'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
 save(ROOT/'records/visual_manifest.json',{'shots':records,'canvas':[W,H],'unique_originals':USED,'P09':'D_young'})
 # Extra original-only detail image, for continuous pan within the single P04 shot.
 crop(originals['G02-01'],(.065,.058,.795,.39)).resize((1200,768),Image.Resampling.LANCZOS).save(ROOT/'assets/G02-01_detail_pan.png')
 images['G07-01'].save(ROOT/'assets/G07-01_chart_removed.png')
 for batch in range(math.ceil(len(records)/12)):
  sheet=Image.new('RGB',(1280,1040),BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(records[batch*12:batch*12+12]):
   x=j%3*426;y=j//3*260;sheet.paste(Image.open(ROOT/s['file']).resize((426,240)),(x,y));d.text((x+8,y+241),s['segment_id']+' '+s['key'],font=font(14),fill=IVORY)
  sheet.save(ROOT/f'review/compositions_{batch+1}.jpg',quality=85)
 print('VISUALS',len(records),flush=True)
if __name__=='__main__':main()
