"""EP010: eleven catalogued originals and six bilingual evidence cards."""
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from wom10_produce import ROOT,REPO,read,save,sha,content
from wom09_visuals import contrast
BG='#e8d9b7';INK='#3b2c21';ACCENT='#5a3a1a'
EN='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
COND='/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf'
JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
TEXT=[];BOXES=[]
def draw(im,s,x,y,h=60,font=BOLD,width=1800,major=True):
 f=ImageFont.truetype(font,200);b=f.getbbox(s);w=round((b[2]-b[0])*h/(b[3]-b[1]));assert w<=width,(s,w,width)
 mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),s,font=f,fill=255);mask=mask.resize((w,h),Image.Resampling.LANCZOS);x=round(x-w/2);y=round(y)
 assert x>=25 and x+w<=1895 and y+h<=700,(s,x,y,w,h)
 im.paste(INK,(x,y,x+w,y+h),mask);TEXT.append(dict(text=s,bbox=[x,y,x+w,y+h],glyph_height=h,font=font,major=major,color=INK));return TEXT[-1]
def base(label,source=None):
 im=Image.new('RGB',(1920,1080),BG);draw(im,label,960,20,23,JA,major=False)
 if source:draw(im,source,960,60,23,EN,major=False)
 ImageDraw.Draw(im).line((48,108,1872,108),fill=ACCENT,width=1);return im
SOURCES={
'K01a':('POSTCARD｜絵はがき','Wiener Werkstätte postcard no. 247, Josef von Divéky, 1909 — Wien Museum, 101968/101 (CC0)'),
'K06a':('POSTCARD｜絵はがき','Wiener Werkstätte postcard no. 541, 1911 — Wien Museum, 101968/146 (CC0)'),
'K06b':('POSTCARD｜絵はがき','Wiener Werkstätte postcard no. 238, Josef von Divéky, 1909 — Wien Museum, 311065 (CC0)'),
'K03a':('POSTCARD｜絵はがき','Wiener Werkstätte postcard no. 542, 1911 — Wien Museum, 101968/147 (CC0)'),
'K05b':('ARTWORK｜美術作品','Saint Nicholas, stained glass, Austria, 1340–50 — The Met, 65.97.5 (CC0)'),
'K04a':('ARTWORK｜美術作品','Bicci di Lorenzo, Saint Nicholas Providing Dowries, 1433–35 — The Met, 88.3.89 (CC0)'),
'K05c':('ARTWORK｜美術作品','Blessing Bishop (Saint Nicholas of Bari), c. 1350–75 — The Met, 25.120.218 (CC0)'),
'K09b':('PHOTO｜写真','Nikolo play, Ennstal, Styria, photo 1896 — Volkskundemuseum Wien, pos/409 (Public Domain)'),
'K09a':('PHOTO｜写真','Jagdpercht, St. Johann im Pongau, photo 1892 — Volkskundemuseum Wien, pos/167 (Public Domain)'),
'K07b':('PHOTO｜写真','Krampus and Nicholas figures, Naschmarkt, Vienna, photo 1915 — Wien Museum, 40607 (CC0)'),
'K10a':('ARTWORK｜美術作品','Henry Farrer, Winter Scene in Moonlight, 1869 — The Met, 1999.19 (CC0)')}
CROPS={'K03a':(.025,.025,.70,.22),'K06b':(.02,.02,.98,.66),'K09b':(.16,.18,.98,.82),'K09a':(.08,.08,.92,.90),'K07b':(.025,.025,.975,.88)}
def art(key,a):
 im=base(*SOURCES[key]);orig=Image.open(a['original_path']).convert('RGB');crop=CROPS.get(key,(0,0,1,1));coords=[round(v*d) for v,d in zip(crop,[orig.width,orig.height]*2)];part=orig.crop(coords)
 if key in ['K09a','K09b','K07b']:part=ImageOps.colorize(ImageOps.autocontrast(ImageOps.grayscale(part),cutoff=.5),black='#443422',white='#f1e4c7')
 zoom=.045 if key!='K03a' else .025;scale=min(1790/part.width,950/part.height,.97/(1+zoom));w,h=round(part.width*scale),round(part.height*scale);x=(1920-w)//2;y=110+(970-h)//2;im.paste(part.resize((w,h),Image.Resampling.LANCZOS),(x,y))
 return im,dict(original_asset_id=key,original_source=a['original_path'],original_sha256=sha(a['original_path']),source_text=list(SOURCES[key]),original_pixels=list(orig.size),crop_pixels=coords,art_boxes=[[x,y,x+w,y+h]],camera_band=[110,1080],zoom_amount=zoom,native_initial_scale=scale,native_max_scale=max(w/part.width,h/part.height)*(1+zoom),color_class='warm_monochrome' if key in ['K09a','K09b','K07b'] else 'color')
def card(key,stage=99):
 im=base('SCHEMATIC｜模式図' if key in ['D_names','D_summary'] else 'TITLE CARD｜文字カード');d=ImageDraw.Draw(im)
 if key=='D_dec6':
  draw(im,'DECEMBER 6',960,245,100);draw(im,'12月6日',960,375,60,JA);draw(im,"SAINT NICHOLAS'S FEAST DAY",960,480,60,COND);draw(im,'聖ニコラウスの祝日',960,575,43,JA,major=False)
 elif key=='D_1869':
  draw(im,'1869',960,185,125);draw(im,'THE FIRST OFFICIAL POSTCARD',960,360,60,COND);draw(im,'(AUSTRIA-HUNGARY)',960,440,60,COND);draw(im,'世界初の公式はがき（オーストリア＝ハンガリー）',960,535,36,JA,major=False);draw(im,'as it is often called',960,610,32,EN,major=False);draw(im,'とよく言われる',960,660,26,JA,major=False)
 elif key=='D_grimm':
  draw(im,'Jacob Grimm, Teutonic Mythology, trans. Stallybrass (1883), p. 515',960,153,26,EN,major=False)
  draw(im,'"I can well imagine that even',960,265,60);draw(im,'in heathen times..."',960,349,60);draw(im,'異教の時代にも……と十分想像できる',960,455,42,JA,major=False)
  draw(im,'IMAGINED, NOT RECORDED',960,555,60,COND);draw(im,'想像であって、記録ではない',960,642,36,JA,major=False)
 elif key=='D_noancient':
  draw(im,'NO ANCIENT TEXT',960,265,85,COND);draw(im,'NAMES KRAMPUS',960,378,85,COND);draw(im,'クランプスの名を記した古代の文献はない',960,535,44,JA,major=False)
 elif key=='D_names':
  # Deliberately schematic country outlines; points are approximate geographic locations.
  germany=[(350,160),(460,172),(468,205),(554,235),(535,300),(570,350),(533,400),(545,445),(478,465),(420,452),(350,475),(314,420),(270,405),(300,352),(269,290),(310,252),(300,210)]
  austria=[(345,490),(409,477),(468,482),(510,465),(569,470),(626,459),(649,488),(613,517),(535,531),(480,524),(423,537),(361,523)]
  d.polygon(germany,fill='#d2c2a0',outline=ACCENT,width=2);d.polygon(austria,fill='#c6b18a',outline=ACCENT,width=2)
  rows=[('KNECHT RUPRECHT','— much of Germany','ドイツの多くの地域',(410,300)),('KLAUBAUF','— parts of Tyrol and Carinthia','チロル・ケルンテンの一部',(435,515)),('KRAMPUS','— Austria','オーストリア',(580,500))]
  for i,(name,en,ja,pt) in enumerate(rows):
   if stage<i+1:continue
   y=150+i*158;d.line([pt,(710,y+40),(760,y+40)],fill=ACCENT,width=2);d.ellipse((pt[0]-7,pt[1]-7,pt[0]+7,pt[1]+7),fill=ACCENT)
   draw(im,name,1305,y,60,COND,width=1090);draw(im,en,1305,y+74,31,EN,width=1090,major=False);draw(im,ja,1305,y+119,28,JA,width=1090,major=False)
  draw(im,'Names and roles varied from valley to valley',960,635,26,EN,major=False);draw(im,'名前も役目も谷ごとに違った',960,675,23,JA,major=False)
 elif key=='D_summary':
  rows=[(['4th c. —','NICHOLAS,','BISHOP','OF MYRA'],['4世紀 ミュラの','司教ニコラウス']),(['13th c. —','GOLDEN','LEGEND'],['13世紀','『黄金伝説』']),(['DEVILS','IN THE','SAINT\'S','SERVICE'],['聖人に仕える悪魔']),(['1869 →','c. 1910 —','POSTCARDS'],['1869〜1910年ごろ','絵はがき']),(['19th c. —','GRIMM','IMAGINES','A PAGAN','PAST'],['19世紀 グリムが','異教の過去を想像'])]
  for i,(en,ja) in enumerate(rows):
   x=44+i*374;box=[x,145,x+346,700];d.rounded_rectangle(box,12,outline=ACCENT,width=3);start=len(TEXT);total=len(en)*68+18+len(ja)*36;y=round((145+700-total)/2)
   for line in en:draw(im,line,x+173,y,60,'/System/Library/Fonts/Supplemental/Arial Narrow Bold.ttf' if '→' in line else COND,width=304);y+=68
   y+=18
   for line in ja:draw(im,line,x+173,y,27,JA,width=304,major=False);y+=36
   texts=TEXT[start:];bb=[min(t['bbox'][0] for t in texts),min(t['bbox'][1] for t in texts),max(t['bbox'][2] for t in texts),max(t['bbox'][3] for t in texts)];gaps=[bb[0]-x-3,bb[1]-148,x+343-bb[2],697-bb[3]];assert min(gaps)>=18,(i,gaps);BOXES.append(dict(index=i+1,box=box,text_bbox=bb,padding_px=gaps,min_padding_px=min(gaps)))
   if i<4:d.line((x+352,422,x+367,422),fill=ACCENT,width=3);d.polygon([(x+367,422),(x+359,417),(x+359,427)],fill=ACCENT)
 else:raise KeyError(key)
 return im
def credits():
 im=base('CREDITS｜クレジット')
 for s,y,h,f in [('QUIET ORIGINS',175,65,BOLD),('Narration: Kokoro / Heart (af_heart)',285,35,EN),('日本語音声：VOICEVOX:冥鳴ひまり',345,34,JA),('Wien Museum · The Metropolitan Museum of Art',445,34,EN),('Volkskundemuseum Wien',505,34,EN),('Music: QO_THEME_A02 · Suno',610,36,EN)]:draw(im,s,960,y,h,f,major=False)
 return im
def main():
 assets={a['id']:a for a in read(ROOT/'records/source_assets.json')['assets']};shots=[];cards=[]
 for seg in content('en')['segments']:
  for key in seg['visuals']:
   TEXT.clear();BOXES.clear();meta={}
   if key in SOURCES:im,meta=art(key,assets[key])
   elif key=='credits':im=credits();meta=dict(color_class='credits',camera_band=[110,1080])
   else:
    variants=[]
    for stage in range(4) if key=='D_names' else [99]:
     TEXT.clear();BOXES.clear();im=card(key,stage);p=ROOT/f'assets/{key}_stage{stage}.png';im.save(p);variants.append(dict(stage=stage,file=str(p.relative_to(ROOT)),text_boxes=list(TEXT)))
    meta=dict(color_class='diagram',camera_band=[110,1080],stages=variants)
    major=[t for t in TEXT if t['major']];assert all(t['glyph_height']>=60 for t in major)
    cards.append(dict(key=key,foreground_contrast=contrast(INK,BG),accent_contrast=contrast(ACCENT,BG),text_boxes=list(TEXT),boxes=list(BOXES),minimum_major_glyph_height=min(t['glyph_height'] for t in major),minimum_box_padding=min((b['min_padding_px'] for b in BOXES),default=None),no_box=not BOXES))
   p=ROOT/f'assets/{key}.png';im.save(p);shots.append(dict(key=key,segment_id=seg['id'],file=str(p.relative_to(ROOT)),text_boxes=list(TEXT),**meta))
 assert len(shots)==18 and len(cards)==6
 used=[s['key'] for s in shots if 'original_asset_id' in s];assert len(used)==len(set(used))==11
 assert all(s['native_max_scale']<=1 for s in shots if 'native_max_scale' in s)
 quote=' '.join(t['text'] for c in cards if c['key']=='D_grimm' for t in c['text_boxes'] if t['text'].startswith(('"I can','in heathen')));assert quote=='"I can well imagine that even in heathen times..."'
 save(ROOT/'records/visual_manifest.json',dict(shots=shots,unique_originals=used,generative_imaging=False));save(ROOT/'records/contrast.json',dict(passed=True,cards=cards,method='WCAG solid RGB; actual visible raster glyph height; box clearances from inner stroke'))
 sheet=Image.new('RGB',(1280,math.ceil(len(shots)/3)*270),BG);d=ImageDraw.Draw(sheet)
 for i,s in enumerate(shots):
  x=i%3*426;y=i//3*270;im=Image.open(ROOT/s['file']);im.thumbnail((426,240));sheet.paste(im,(x,y+27));d.text((x+8,y+5),s['segment_id']+' '+s['key'],fill=INK)
 sheet.save(ROOT/'review/storyboard.jpg',quality=88);print('VISUALS',len(shots),'ART',len(used),'CARDS',len(cards),flush=True)
if __name__=='__main__':main()
