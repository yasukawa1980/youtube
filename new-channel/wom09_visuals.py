"""EP009 source-only layouts. No generative imaging or restoration.
Original pixels are cropped, fitted, and (prints only) given a warm monochrome tone.
Every text box and maximum source-pixel scale is recorded for review.
"""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance
from wom09_produce import ROOT,REPO,read,save,sha,content
EN='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
SERIF='/System/Library/Fonts/Supplemental/Georgia.ttf'
JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
BG='#e8d9b7';INK='#3b2c21';ACCENT='#5a3a1a'
TEXT=[]
def font(n,style='en'):return ImageFont.truetype({'en':EN,'bold':BOLD,'serif':SERIF,'ja':JA}[style],n)
def text(im,s,xy,size=38,style='en',fill=INK,anchor='lt',maxwidth=1780):
 d=ImageDraw.Draw(im);f=font(size,style)
 while d.textbbox(xy,s,font=f,anchor=anchor)[2]-d.textbbox(xy,s,font=f,anchor=anchor)[0]>maxwidth:
  size-=1;assert size>=18,(s,maxwidth);f=font(size,style)
 box=d.textbbox(xy,s,font=f,anchor=anchor);assert box[0]>=25 and box[2]<=1895 and box[3]<=700,(s,box)
 d.text(xy,s,font=f,fill=fill,anchor=anchor);TEXT.append({'text':s,'bbox':list(box),'font_size':size,'color':fill})
def center(im,s,y,size=44,style='en',fill=INK,width=1750):text(im,s,(960,y),size,style,fill,'mt',width)
def base(label,source=None,note=None):
 im=Image.new('RGB',(1920,1080),BG)
 text(im,label,(48,15),23,'ja',ACCENT)
 if source:text(im,source,(48,46),26,'en',maxwidth=1824)
 if note:text(im,note,(48,80),20,'ja',maxwidth=1824)
 ImageDraw.Draw(im).line((48,108,1872,108),fill=ACCENT,width=1)
 return im
SOURCES={
'met_202259':('ARTWORK｜美術作品','Dish depicting the Trojan Horse, Italy, mid-16th c. — The Met, 59.23.2','Later imagining｜後世の想像図'),
'R06':('PRINT｜版画','After John Flaxman, Odyssey title page, 1805 — Rijksmuseum, RP-P-1975-75-41','Later imagining｜後世の想像図'),
'met_437394':('ARTWORK｜美術作品','Rembrandt, Aristotle with a Bust of Homer, 1653 — The Met, 61.198','Homer bust detail｜ホメロスの胸像部分　·　Later imagining｜後世の想像図'),
'met_198621':('ARTWORK｜美術作品','Priam Supplicating Achilles for the Body of Hector, c. 1815–25 — The Met, 40.20.40','Later imagining｜後世の想像図'),
'met_247952':('ARTWORK｜美術作品','Kithara player, terracotta neck-pelike, c. 500 BC — The Met, 07.286.72','キタラ奏者'),
'met_254876':('ARTWORK｜美術作品','Terracotta neck-amphora, c. 540 BC — The Met, 56.171.18','Menelaus and Helen (as identified by the museum)｜メネラオスとヘレネとされる場面'),
'MYK01':('PHOTO｜写真','Relief pithos, Mykonos, c. 670 BC — Archaeological Museum of Mykonos 2240. Photo: AbelDionis (CC0)',None),
'R04':('PRINT｜版画','The Trojan Horse brought into Troy, 1663 — Rijksmuseum, RP-P-OB-207.716','Later imagining｜後世の想像図'),
'R01':('PRINT｜版画','The Trojan Horse, in or before 1571 — Rijksmuseum, RP-P-2007-160','Later imagining｜後世の想像図'),
'met_341207':('ARTWORK｜美術作品','The Acropolis from the West, 1834 — The Met, 1972.92.4','The bronze horse does not survive｜青銅の木馬像は現存しない'),
'met_253376':('ARTWORK｜美術作品','Carnelian scarab with the Trojan Horse, Etruscan, 500–475 BC — The Met, 32.11.7',None),
'met_254896':('ARTWORK｜美術作品','Kithara player, terracotta amphora, Berlin Painter, c. 490 BC — The Met, 56.171.38','キタラ奏者'),
}
CROPS={'met_437394':(.045,.435,.325,.895),'met_253376':(.34,.32,.66,.69),'R06':(.115,.155,.88,.86)}
ZOOM={'met_202259':.07,'MYK01':.06,'met_253376':.05,'met_198621':.025,'R04':.025,'R01':.035,'R06':.10,'met_437394':.07,'met_247952':.10,'met_254876':.08,'met_254896':.10,'met_341207':.04}

def art(key,asset):
 im=base(*SOURCES[key]);original=Image.open(asset['path']).convert('RGB');crop=CROPS.get(key,(0,0,1,1));coords=tuple(round(v*d) for v,d in zip(crop,[original.width,original.height]*2));a=original.crop(coords)
 if key.startswith('R'):a=ImageOps.colorize(ImageOps.autocontrast(ImageOps.grayscale(a),cutoff=.5),black='#443422',white='#f1e4c7')
 if key=='met_437394':
  arr=np.asarray(a)/255.;a=Image.fromarray(np.uint8(np.clip(arr**.78*255,0,255)))
 maxscale=.93/(1+ZOOM[key]) if key in ['met_202259','MYK01','met_253376'] else 1
 scale=min(1790/a.width,910/a.height,maxscale)
 # Cameo retains its complete mount; original margins remain visible.
 w,h=round(a.width*scale),round(a.height*scale);a=a.resize((w,h),Image.Resampling.LANCZOS);x=(1920-w)//2;y=115+(965-h)//2;im.paste(a,(x,y))
 return im,{'source':asset['page'],'label':SOURCES[key][0],'source_text':list(SOURCES[key]),'original_sha256':sha(asset['path']),'original_pixels':list(original.size),'crop_pixels':list(coords),'crop_normalized':crop,'art_boxes':[[x,y,x+w,y+h]],'camera_band':[110,1080],'zoom_amount':ZOOM[key],'native_initial_scale':max(w/(coords[2]-coords[0]),h/(coords[3]-coords[1])),'native_max_scale':max(w/(coords[2]-coords[0]),h/(coords[3]-coords[1]))*(1+ZOOM[key]),'color_class':'warm_monochrome' if key.startswith('R') else 'color','original_asset_id':key}

def card(key,stage=99):
 im=base('TITLE CARD｜文字カード' if key in ['D_lastline','D_nohorse','D_gifts'] else 'SCHEMATIC｜模式図')
 d=ImageDraw.Draw(im)
 if key=='D_lastline':
  text(im,'Iliad, Book 24 — trans. Lang, Leaf & Myers (1883)',(48,53),27)
  center(im,'"Thus held they funeral for',285,66,'serif');center(im,'Hector tamer of horses."',375,66,'serif')
  center(im,'こうして彼らは、馬を馴らすヘクトルの葬儀を営んだ。',520,38,'ja')
 elif key=='D_nohorse':
  center(im,'NO HORSE',280,110,'bold');center(im,'IN THE ILIAD',410,105,'bold');center(im,'『イリアス』に木馬は出てこない',575,48,'ja')
 elif key=='D_options':
  center(im,'Odyssey, Book 8｜『オデュッセイア』8巻',170,42,'ja')
  rows=[('BREAK IT OPEN','打ち割る'),('THROW IT ONTO THE ROCKS','岩の上へ投げ落とす'),('KEEP IT FOR THE GODS','神々への捧げ物に')]
  for i,(en,ja) in enumerate(rows):
   if stage>=i+1:
    y=280+i*127;text(im,en,(180,y),43,'bold');text(im,ja,(180,y+55),33,'ja')
 elif key=='D_passages':
  for i,(en,ja) in enumerate([('Odyssey 4  Helen and the voices','4巻 ヘレネと妻たちの声'),('Odyssey 8  The song of Demodocus','8巻 デモドコスの歌'),("Odyssey 11  Achilles' son",'11巻 アキレウスの息子')]):
   text(im,en,(170,170+i*125),44);text(im,ja,(170,225+i*125),32,'ja')
  if stage>=1:
   center(im,'A FEW DOZEN LINES · NO NUMBER OF MEN',590,38,'bold');center(im,'合わせて数十行・人数の記述なし',645,30,'ja')
 elif key=='D_lostpoems':
  text(im,'LITTLE ILIAD ·',(110,220),41,'bold',maxwidth=670);text(im,'SACK OF TROY',(110,280),41,'bold');text(im,'『小イリアス』『イリオスの陥落』',(110,350),29,'ja',maxwidth=690)
  text(im,'(not surviving in full｜全文は残らない)',(110,410),28,'ja',maxwidth=690)
  d.line((805,330,965,330),fill=ACCENT,width=5);d.polygon([(965,330),(940,317),(940,343)],fill=ACCENT)
  text(im,'LATER SUMMARIES｜後世の要約',(1020,165),38,'ja',maxwidth=790)
  for i,(en,ja) in enumerate([('THE HORSE','木馬'),('A BROKEN WALL','崩された城壁'),('LAOCOÖN AND THE SERPENTS','ラオコーンと大蛇'),('SINON','シノン')]):
   if stage>=i+1:
    text(im,en,(1020,255+i*104),32,'bold',maxwidth=790);text(im,ja,(1020,297+i*104),27,'ja')
 elif key=='D_gifts':
  text(im,'Aeneid 2.49 — trans. J. W. Mackail (1885)',(48,53),27)
  center(im,'"I fear the Grecians even',270,68,'serif');center(im,'when they offer gifts."',360,68,'serif')
  center(im,'timeo Danaos et dona ferentes',477,36,'serif');center(im,'私は、贈り物を携えたギリシャ人さえ恐れる',565,40,'ja')
 elif key=='D_timeline':
  d.line((330,340,1590,340),fill=ACCENT,width=4)
  for x,en,date,ja,jdate in [(330,"HOMER'S POEMS",'8th–7th c. BC','ホメロスの詩','前8〜7世紀ごろ'),(960,'MYKONOS JAR','c. 670 BC','ミコノスの甕','前670年ごろ'),(1590,'AENEID','c. 29–19 BC','アエネーイス','前29〜19年ごろ')]:
   d.ellipse((x-9,331,x+9,349),fill=ACCENT)
   text(im,en,(x,230),40,'bold',anchor='mt',maxwidth=565);text(im,date,(x,285),35,anchor='mt')
   text(im,ja,(x,400),35,'ja',anchor='mt');text(im,jdate,(x,453),30,'ja',anchor='mt')
 elif key=='D_count':
  text(im,'50?',(530,235),175,'bold',anchor='mt');text(im,'3,000?',(1370,235),175,'bold',anchor='mt')
  center(im,'Apollodorus, Epitome 5.14 (citing the Little Iliad for 3,000)',510,35)
  center(im,'アポロドーロス『摘要』（3000人は『小イリアス』の作者による）',570,33,'ja')
 elif key=='D_summary':
  rows=[(['ILIAD —','NONE'],'イリアス：なし'),(['ODYSSEY —','A FEW DOZEN','LINES'],'オデュッセイア：数十行'),(['LOST POEMS','& PICTURES'],'失われた詩と絵'),(['AENEID —','A DETAILED','STORY'],'アエネーイス：詳しい物語')]
  for i,(lines,ja) in enumerate(rows):
   x=55+i*475;d.rounded_rectangle((x,220,x+390,630),radius=10,outline=ACCENT,width=2)
   for j,line in enumerate(lines):text(im,line,(x+195,280+j*63),37,'bold',anchor='mt',maxwidth=360)
   text(im,ja,(x+195,538),27,'ja',anchor='mt',maxwidth=365)
   if i<3:d.line((x+403,420,x+455,420),fill=ACCENT,width=4);d.polygon([(x+455,420),(x+440,411),(x+440,429)],fill=ACCENT)
 else:raise KeyError(key)
 return im

def credits():
 im=base('CREDITS｜クレジット')
 for y,en,ja in [(170,'QUIET ORIGINS',''),(270,'Narration: Kokoro / Heart (af_heart)','日本語音声：VOICEVOX:冥鳴ひまり'),(390,'The Metropolitan Museum of Art · Rijksmuseum','Archaeological Museum of Mykonos'),(500,'Mykonos photograph: AbelDionis · CC0',''),(590,'Music: QO_THEME_A02 · Suno','')]:
  center(im,en,y,45 if y==170 else 34,'bold' if y==170 else 'en')
  if ja:center(im,ja,y+50,29,'ja' if y==270 else 'en')
 return im

def contrast(a,b):
 def lum(c):
  rgb=[int(c[i:i+2],16)/255 for i in (1,3,5)];v=[x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb];return sum(x*y for x,y in zip(v,[.2126,.7152,.0722]))
 v=sorted([lum(a),lum(b)]);return (v[1]+.05)/(v[0]+.05)

def main():
 assets={a['key']:a for a in read(ROOT/'records/source_assets.json')['assets']};shots=[];cards=[]
 stages={'D_options':3,'D_lostpoems':4,'D_passages':1}
 for seg in content('en')['segments']:
  for key in seg['visuals']:
   TEXT.clear();meta={};variants=[]
   if key in SOURCES:im,meta=art(key,assets[key])
   elif key=='credits':im=credits();meta={'color_class':'credits','camera_band':[110,1080]}
   else:
    for s in range(stages.get(key,0)+1):
     TEXT.clear();stage=99 if key not in stages else s;im=card(key,stage);p=ROOT/f'assets/{key}_stage{s}.png';im.save(p);variants.append({'stage':s,'file':str(p.relative_to(ROOT)),'text_boxes':list(TEXT)})
    meta={'color_class':'diagram','camera_band':[110,1080],'stages':variants}
    cards.append({'key':key,'background':BG,'foreground':INK,'foreground_contrast':contrast(INK,BG),'accent':ACCENT,'accent_contrast':contrast(ACCENT,BG),'max_text_y':max(t['bbox'][3] for t in TEXT),'text_boxes':list(TEXT)})
   path=ROOT/f'assets/{key}.png';im.save(path)
   shots.append({'key':key,'segment_id':seg['id'],'file':str(path.relative_to(ROOT)),'text_boxes':list(TEXT),**meta})
 assert len(shots)==22 and len(cards)==9
 used=[s['key'] for s in shots if s['key'] in SOURCES];assert len(used)==len(set(used))==12
 for s in shots:
  if s['key'] in ['met_202259','MYK01','met_253376']:assert s['native_max_scale']<=1.0
 assert all(min(c['foreground_contrast'],c['accent_contrast'])>=4.5 for c in cards)
 for key,expected in [('D_lastline','"Thus held they funeral for Hector tamer of horses."'),('D_gifts','"I fear the Grecians even when they offer gifts."')]:
  q=next(c for c in cards if c['key']==key);quote=' '.join(t['text'] for t in q['text_boxes'] if t['font_size']>=60);assert quote==expected;(ROOT/f'records/{key}_screen_quote.txt').write_text(quote+'\n')
 save(ROOT/'records/visual_manifest.json',{'shots':shots,'unique_originals':used,'generative_imaging':False})
 save(ROOT/'records/contrast.json',{'passed':True,'cards':cards,'method':'WCAG sRGB relative luminance; exact solid background and text RGB values'})
 sheet=Image.new('RGB',(1280,math.ceil(len(shots)/3)*270),BG);d=ImageDraw.Draw(sheet)
 for i,s in enumerate(shots):
  x=i%3*426;y=i//3*270;im=Image.open(ROOT/s['file']);im.thumbnail((426,240));sheet.paste(im,(x,y+27));d.text((x+8,y+5),s['segment_id']+' '+s['key'],font=font(17),fill=INK)
 sheet.save(ROOT/'review/storyboard.jpg',quality=85,optimize=True)
 print('VISUALS',len(shots),'ART',len(used),'CARDS',len(cards),flush=True)
if __name__=='__main__':main()
