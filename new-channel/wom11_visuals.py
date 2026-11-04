"""EP011 approved source crops, bilingual cards and measured layout. No generated imagery."""
import math,copy
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from wom11_produce import ROOT,REPO,read,save,sha,content
from wom09_visuals import contrast
BG='#e8d9b7';INK='#3b2c21';ACCENT='#5a3a1a'
EN='/System/Library/Fonts/Supplemental/Arial.ttf';BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf';COND='/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
TEXT=[];BOXES=[]
def draw(im,s,x,y,h=60,font=BOLD,width=1830,major=True):
 f=ImageFont.truetype(font,200);b=f.getbbox(s);w=round((b[2]-b[0])*h/(b[3]-b[1]));assert w<=width,(s,w,width)
 mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),s,font=f,fill=255);mask=mask.resize((w,h),Image.Resampling.LANCZOS);x=round(x-w/2);y=round(y)
 assert x>=12 and x+w<=1908 and y+h<=900,(s,x,y,w,h)
 im.paste(INK,(x,y,x+w,y+h),mask);TEXT.append(dict(text=s,bbox=[x,y,x+w,y+h],glyph_height=h,font=font,major=major,color=INK));return TEXT[-1]
def base(label,source=None):
 im=Image.new('RGB',(1920,1080),BG);draw(im,label,960,18,23,JA,major=False)
 if source:draw(im,source,960,58,21,EN,major=False)
 ImageDraw.Draw(im).line((32,105,1888,105),fill=ACCENT,width=1);return im
CONFIG={
'E01A_10_scale':(551786,10,'PAPYRUS｜パピルス',[1200,1040,2240,1460]),
'E01A_05':(551786,5,'PAPYRUS｜パピルス',[0,150,4000,1050]),
'E01A_13':(551786,13,'PAPYRUS｜パピルス',[0,150,4000,940]),
'E01A_10_osiris':(551786,10,'PAPYRUS｜パピルス',[35,450,740,1460]),
'E01A_10_beam':(551786,10,'PAPYRUS｜パピルス',[1480,1050,2040,1320]),
'E01A_10_ammit':(551786,10,'PAPYRUS｜パピルス',[2240,1040,2800,1460]),
'E06A':(243713,0,'AMULET｜護符',None),'E06B':(551381,0,'AMULET｜護符',None),
'E07A_03':(550986,3,'AMULET｜護符',None),'E07A_01':(550986,1,'AMULET｜護符',None),
'E08A':(558378,0,'AMULET｜護符',None),'E11B':(545802,0,'STATUETTE｜小像',None),
'E10A':(420448,0,'ARTWORK｜美術作品',None),'E10B':(12074,0,'ARTWORK｜美術作品',None),
'R01':(557657,0,'PAPYRUS｜パピルス',None)}
def art(key,assets):
 n,idx,label,crop=CONFIG[key];a=assets[n];src=a['images'][idx];orig=Image.open(src['file']).convert('RGB')
 title=a['title'].replace('Book of the Dead of the Priest of Horus, Imhotep (Imuthes)','Book of the Dead of Imhotep (Imuthes)')
 if n==557657:title='Funerary papyrus: judgment before Osiris (42 gods)'
 # Long catalog titles can be wrapped only in headers; concise titles preserve identification.
 if n==551786:title='Book of the Dead of Imhotep (Imuthes)'
 source=f"{title}, {a['date']} — The Met {a['accession']} (CC0)"
 if len(source)>145:source=f"{title} — {a['date']} / Met {a['accession']} (CC0)"
 im=base(label,source)
 if crop is None:
  fractions={'E10B':(.23,.28,.86,.74),'E07A_01':(.19,.17,.81,.80),'E07A_03':(.23,.18,.83,.80),'E08A':(.32,.23,.66,.77),'E06A':(.15,.15,.85,.86),'E06B':(.12,.22,.9,.8)}
  crop=[round(v*d) for v,d in zip(fractions.get(key,(0,0,1,1)),[orig.width,orig.height]*2)]
 part=orig.crop(crop);zoom=.03
 if key=='E01A_10_scale':scale=1.7;zoom=-.035
 elif key=='E01A_10_beam':scale=3.4/(1+.02);zoom=.02
 else:scale=min(1790/part.width,930/part.height,.965/(1+zoom))
 w,h=round(part.width*scale),round(part.height*scale);x=(1920-w)//2;y=110+(970-h)//2;im.paste(part.resize((w,h),Image.Resampling.LANCZOS),(x,y))
 maxscale=scale*max(1,1+zoom)
 if key in ['E01A_05','E01A_13']:maxscale=scale*2
 if key=='R01':maxscale=scale*2.2
 return im,dict(original_asset_id=str(n),original_source=src['file'],original_sha256=src['sha256'],source_text=[label,source],original_pixels=list(orig.size),crop_pixels=crop,art_boxes=[[x,y,x+w,y+h]],camera_band=[110,1080],zoom_amount=zoom,native_initial_scale=scale,native_max_scale=maxscale,color_class='color',approved_upscale_exception=key in ['E01A_10_scale','E01A_10_beam'],section_index=idx)
DENIALS=['I have not stolen.','I have done no murder.','I have spoken no lies.','I have made [no man] to weep.','I have not turned back water at its springtide.']
DENIALS_JA=['盗まなかった','人を殺めなかった','うそを語らなかった','誰も泣かせなかった','増水の時に水をせき止めなかった']
def card(key,stage=99):
 im=base('SCHEMATIC｜模式図' if key=='D_summary' else 'TITLE CARD｜文字カード');d=ImageDraw.Draw(im)
 if key=='D_goingforth':
  for text,y,h,f in [('“GOING FORTH BY DAY”',330,82,BOLD),('「日のもとに出る」',450,60,JA),('The choice of spells varied from scroll to scroll',600,44,EN),('収める呪文は巻物ごとに異なった',675,36,JA)]:draw(im,text,960,y,h,f,major=h>=60)
 elif key=='D_1842':
  for text,y,h,f in [('1842',275,125,BOLD),('KARL RICHARD LEPSIUS',455,60,BOLD),('カール・リヒャルト・レプシウス',550,40,JA),('Das Todtenbuch der Ägypter — a papyrus in Turin',650,40,EN),('トリノのパピルスを『死者の書』の題で出版',720,34,JA)]:draw(im,text,960,y,h,f,major=h>=60)
 elif key=='D_spell125':
  for text,y,h,f in [('SPELL 125',340,100,BOLD),('125章',480,60,JA),('THE JUDGMENT',600,60,BOLD),('裁きの場面',700,40,JA)]:draw(im,text,960,y,h,f,major=h>=60)
 elif key=='D_denials':
  draw(im,'The Negative Confession · E. A. Wallis Budge, 1895 · from different versions',960,140,25,EN,major=False)
  draw(im,'否定告白（バッジ英訳1895、いくつかの写本から）',960,185,25,JA,major=False)
  for i,(en,ja) in enumerate(zip(DENIALS,DENIALS_JA)):
   if i>=stage:continue
   y=255+i*115;draw(im,en,960,y,60,COND);draw(im,ja,960,y+75,27,JA,major=False)
 elif key=='D_truevoice':
  for text,y,h,f in [('TRUE OF VOICE',330,90,BOLD),('声正しき者',460,60,JA),('a title added after the names of the dead',610,44,EN),('死者の名のあとに添えられた言葉',685,38,JA)]:draw(im,text,960,y,h,f,major=h>=60)
 elif key=='D_summary':
  rows=[(['NEGATIVE','CONFESSION'],['否定告白']),(['42 GODS'],['42柱の神々']),(['SPELL 30B','— WORDS','FOR THE','HEART'],['30B章','心臓への言葉']),(['THE SCALE','IN BALANCE'],['天秤がつり合う']),(['BEFORE','OSIRIS'],['オシリスの前へ'])]
  for i,(en,ja) in enumerate(rows):
   x=12+i*378;box=[x,235,x+366,845];d.rounded_rectangle(box,12,outline=ACCENT,width=3);start=len(TEXT);height=len(en)*78-18+25+len(ja)*37;y=round((235+845-height)/2)
   for line in en:draw(im,line,x+183,y,60,COND,width=324);y+=78
   y+=7
   for line in ja:draw(im,line,x+183,y,28,JA,width=324,major=False);y+=37
   ts=TEXT[start:];bb=[min(t['bbox'][0] for t in ts),min(t['bbox'][1] for t in ts),max(t['bbox'][2] for t in ts),max(t['bbox'][3] for t in ts)];gaps=[bb[0]-x-3,bb[1]-238,x+363-bb[2],842-bb[3]];assert min(gaps)>=18,(i,gaps);BOXES.append(dict(index=i+1,box=box,text_bbox=bb,padding_px=gaps,min_padding_px=min(gaps)))
   if i<4:d.line((x+369,540,x+375,540),fill=ACCENT,width=3);d.polygon([(x+375,540),(x+370,536),(x+370,544)],fill=ACCENT)
 else:raise KeyError(key)
 return im
def credits():
 im=base('CREDITS｜クレジット')
 for s,y,h,f in [('QUIET ORIGINS',270,65,BOLD),('Narration: Kokoro / Heart (af_heart)',420,35,EN),('日本語音声：VOICEVOX:冥鳴ひまり',490,34,JA),('The Metropolitan Museum of Art · Open Access (CC0)',600,34,EN),('Music: QO_THEME_A02 · Suno',710,36,EN)]:draw(im,s,960,y,h,f,major=False)
 return im
def main():
 assets={a['met_object_id']:a for a in read(ROOT/'records/source_assets.json')['assets']};shots=[];cards=[]
 for seg in content('en')['segments']:
  for key in seg['visuals']:
   TEXT.clear();BOXES.clear();meta={}
   if key in CONFIG:im,meta=art(key,assets)
   elif key=='credits':im=credits();meta=dict(color_class='credits',camera_band=[110,1080])
   else:
    variants=[]
    for stage in range(6) if key=='D_denials' else [99]:
     TEXT.clear();BOXES.clear();im=card(key,stage);p=ROOT/f'assets/{key}_stage{stage}.png';im.save(p);variants.append(dict(stage=stage,file=str(p.relative_to(ROOT)),text_boxes=copy.deepcopy(TEXT)))
    meta=dict(color_class='diagram',camera_band=[110,1080],stages=variants)
    major=[t for t in TEXT if t['major']];assert all(t['glyph_height']>=60 for t in major)
    cards.append(dict(key=key,foreground_contrast=contrast(INK,BG),accent_contrast=contrast(ACCENT,BG),text_boxes=copy.deepcopy(TEXT),boxes=copy.deepcopy(BOXES),minimum_major_glyph_height=min(t['glyph_height'] for t in major),minimum_box_padding=min((b['min_padding_px'] for b in BOXES),default=None)))
   p=ROOT/f'assets/{key}.png';im.save(p);shots.append(dict(key=key,segment_id=seg['id'],file=str(p.relative_to(ROOT)),text_boxes=copy.deepcopy(TEXT),**meta))
 assert len(cards)==6
 assert [t['text'] for c in cards if c['key']=='D_denials' for t in c['text_boxes'] if t['major']]==DENIALS
 save(ROOT/'records/visual_manifest.json',dict(shots=shots,unique_originals=sorted(set(s['original_asset_id'] for s in shots if 'original_asset_id' in s)),generative_imaging=False));save(ROOT/'records/contrast.json',dict(passed=True,cards=cards,method='WCAG solid RGB, actual raster glyph height, inner-stroke box clearance'))
 for start in range(0,len(shots),6):
  sheet=Image.new('RGB',(1280,810),BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(shots[start:start+6]):
   x=j%2*640;y=j//2*270;im=Image.open(ROOT/s['file']);im.thumbnail((480,270));sheet.paste(im,(x+160,y));d.text((x+8,y+10),s['segment_id']+'\n'+s['key'],fill=INK)
  sheet.save(ROOT/f'review/storyboard_{start//6+1:02d}.jpg',quality=90)
 print('VISUALS',len(shots),'CARDS',len(cards),flush=True)
if __name__=='__main__':main()
