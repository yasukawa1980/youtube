"""EP008: documented native compositions using original scans; no text rewriting."""
import math
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance
from wom08_produce import ROOT,REPO,read,save,sha,content,ff,ai_video
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
 text(im,(92,18),'QUIET ORIGINS  /  EP008',28,GOLD)
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
PLAN={s['id']:s['visuals'] for s in content('en')['segments']}
PLAN['P04']=['B170','B164'] # Production request order takes precedence over JSON visual hint.
USED=[x for v in PLAN.values() for x in v if x in assets]
assert len(USED)==len(set(USED))
# Coordinates apply to complete unrotated source scans; approved article columns only.
CROPS={
 'B286':(.10,.10,.88,.81),'B151':(.10,.10,.90,.835),'B157':(.10,.07,.90,.89),
 'B170':(.085,.085,.915,.89),'B183':(.09,.10,.91,.84),'B299':(.10,.08,.90,.85),
 'B300':(.10,.10,.90,.84),'B237':(.10,.11,.90,.80),'B313':(.11,.16,.88,.81),'B246':(.09,.09,.91,.82),
 'N03':(.600,.102,.720,.985),'N01':(.309,.144,.438,.716),'N02':(.278,.160,.414,.754),
 'B164':(.22,.085,.97,.182),'B241':(.025,.242,.82,.325),'B312':(.245,.588,.965,.694)}
ROTATIONS={'B286':270,'B170':270,'B183':90,'B246':270,'B313':90}
images={}
for k in USED:
 a=assets[k];assert sha(a['path'])==a['sha256'];im=Image.open(a['path']).convert('RGB');im=crop(im,CROPS[k]);im=im.rotate(ROTATIONS.get(k,0),expand=True)
 if k=='B313':im=im.crop((0,round(im.height*.075),im.width,im.height))
 images[k]=im
 im.save(ROOT/f'assets/{k}_cropped.png')
def diagram(im,key):
 header(im,'TITLE CARD｜文字カード' if key=='D_novels' else 'SCHEMATIC｜模式図',{'D_illness':'Howard Carter, journal, March–April 1923 • Griffith Institute transcription','D_novels':'Alcott (1869) / Doyle (1892) • titles, not facsimile pages','D_warning':'Hetepherakhty, c. 2400 BC • Rijksmuseum van Oudheden commentary','D_bmj':'Nelson, BMJ 2002;325:1482–1484 • historical cohort study','D_summary':'Carter & Mace (1923) / US newspapers (April 1923) / earlier fiction'}[key]);d=ImageDraw.Draw(im)
 if key=='D_illness':
  text(im,(960,260),'MARCH 1923｜1923年3月',47,GOLD,True)
  text(im,(960,350),'INFECTION, THEN PNEUMONIA',45,IVORY,True)
  text(im,(960,420),'感染症、のちに肺炎',40,IVORY,True)
  text(im,(960,570),'5 APRIL 1923, CAIRO｜1923年4月5日 カイロ',39,GOLD,True)
 elif key=='D_novels':
  rows=[('1869  Louisa May Alcott','Lost in a Pyramid; or, The Mummy’s Curse','ルイザ・メイ・オルコット','「ピラミッドで迷って、あるいはミイラの呪い」'),('1892  Arthur Conan Doyle','Lot No. 249','アーサー・コナン・ドイル「競売番号249」','')]
  for i,(a,b,c,e) in enumerate(rows):
   y=180+i*280;text(im,(140,y),a,40,GOLD);text(im,(140,y+60),b,43,IVORY,False,True);text(im,(140,y+125),c,31);
   if e:text(im,(140,y+171),e,31)
 elif key=='D_warning':
  xs=[365,960,1555];d.line((xs[0],300,xs[-1],300),fill='#59646b',width=4)
  for x,a,b,c in zip(xs,['c. 2400 BC','c. 1330 BC','1922'],['TOMB CHAPEL WARNING','TUTANKHAMUN','DISCOVERY'],['前2400年ごろ 墓の礼拝室の警告','前1330年ごろ ツタンカーメン','1922年 発見']):
   color=GOLD if x==xs[0] else MUTED;d.ellipse((x-8,292,x+8,308),fill=color);text(im,(x,365),a,45,color,True);text(im,(x,439),b,29,color,True);text(im,(x,495),c,25,color,True)
 elif key=='D_bmj':
  for x,a,b,n in [(520,'PRESENT AT KEY OPENINGS','開封に立ち会った人','25'),(1400,'NOT PRESENT','立ち会わなかった人','11')]:
   d.rounded_rectangle((x-385,175,x+385,470),radius=15,outline='#5f7078',width=3);text(im,(x,210),a,30,GOLD,True);text(im,(x,270),b,31,IVORY,True);text(im,(x,325),n,92,IVORY,True)
  text(im,(960,525),'NO STATISTICALLY SIGNIFICANT LINK',38,GOLD,True);text(im,(960,580),'統計的に有意な関連なし',33,IVORY,True);text(im,(960,649),'Nelson, BMJ 2002 • 死亡情報が分かった36人',23,MUTED,True)
 elif key=='D_summary':
  rows=[('1869–1892 STORIES｜物語',230),('APRIL 1923 A DEATH｜1923年4月 死去',330),('NEWSPAPERS｜新聞',430)]
  for val,y in rows:text(im,(960,y),val,39,IVORY,True)
  text(im,(960,585),'“THE CURSE”｜「呪い」',55,GOLD,True)
def compose(key):
 global TEXT,BOXES
 TEXT=[];BOXES=[];im=Image.new('RGB',(W,H),BG);source='';label='';extra={}
 if key in images:
  art=images[key];im=background(art)
  full=key=='B286'
  if full:im=ImageOps.fit(art,(W,H),Image.Resampling.LANCZOS);BOXES=[[0,110,1920,1080]]
  elif key.startswith('N'):
   panel(im,art,(80,125,450,795))
   detail={'N01':(.309,.144,.438,.221),'N02':(.278,.594,.414,.690),'N03':(.600,.102,.720,.172)}[key]
   original=Image.open(assets[key]['path']).convert('RGB')
   panel(im,crop(original,detail),(600,150,1240,650));extra['detail_crop_normalized']=detail
  else:panel(im,art,(80,125,1760,795))
  a=assets[key];label='NEWSPAPER｜新聞' if key.startswith('N') else 'PRINTED BOOK｜刊本' if key in ['B164','B241','B312'] else 'EXCAVATION PHOTO｜発掘写真'
  source=(a['title'].split('：')[0]+' • '+a['date']+' • University of Oregon Libraries') if key.startswith('N') else 'Carter & Mace, The Tomb of Tut.ankh.Amen, vol. I (1923) • '+('p. '+str(a['printed_page']) if label.startswith('PRINTED') else 'photo: Harry Burton')+' • MIT Libraries'
  header(im,label,source);extra={**extra,'crop_normalized':CROPS[key],'rotation_degrees_ccw':ROTATIONS.get(key,0),'post_rotation_crop_top_fraction':.075 if key=='B313' else 0,'background_also_uses_only_crop':True,'full_bleed':full}
 elif key.startswith('D_'):diagram(im,key);label='TITLE CARD｜文字カード' if key=='D_novels' else 'SCHEMATIC｜模式図'
 elif key=='V01':
  video=ai_video(key);poster=ROOT/'assets/V01_poster.png'
  if video.exists():ff(['-i',video,'-frames:v',1,poster]);im=ImageOps.fit(Image.open(poster).convert('RGB'),(W,H))
  else:extra['missing_video']=True
  header(im,'AI IMAGE｜AI映像','Kling AI • candle scene only');label='AI IMAGE｜AI映像';BOXES=[[0,110,1920,1080]]
 elif key=='credits':
  header(im);rows=[('English','Kokoro / Heart (af_heart)'),('日本語','VOICEVOX:冥鳴ひまり'),('Collections','MIT Libraries • Carter & Mace (1923), photos: Harry Burton'),('Collections','University of Oregon Libraries • Public Domain Mark 1.0'),('AI video','Kling AI • P14 candle only'),('Music','Suno • QO_THEME_A02')]
  for i,(a,b) in enumerate(rows):text(im,(130,180+i*76),a,27,GOLD);text(im,(390,180+i*76),b,25)
 else:raise ValueError(key)
 return im,{'key':key,'base_asset':key if key in images or key=='V01' else None,'source':source,'label':label,'texts':TEXT.copy(),'art_boxes':BOXES.copy(),'camera_band':[110,1080] if extra.get('full_bleed') or key=='V01' else [110,930] if key in images else [110,700],**extra}
def main():
 records=[]
 for seg,keys in PLAN.items():
  for i,key in enumerate(keys):
   im,rec=compose(key);p=ROOT/f'assets/{seg}_{i+1:02}_{key}.png';im.save(p);records.append({**rec,'segment_id':seg,'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
 save(ROOT/'records/visual_manifest.json',{'shots':records,'canvas':[W,H],'unique_originals':USED})
 for batch in range(math.ceil(len(records)/12)):
  sheet=Image.new('RGB',(1280,1040),BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(records[batch*12:batch*12+12]):
   x=j%3*426;y=j//3*260;sheet.paste(Image.open(ROOT/s['file']).resize((426,240)),(x,y));d.text((x+8,y+241),s['segment_id']+' '+s['key'],font=font(14),fill=IVORY)
  sheet.save(ROOT/f'review/compositions_{batch+1}.jpg',quality=85)
 print('VISUALS',len(records),flush=True)
if __name__=='__main__':main()
