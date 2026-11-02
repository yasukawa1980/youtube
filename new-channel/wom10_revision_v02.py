"""Only approved EP010 visual corrections; audio and timing are copied intact."""
import os,shutil,copy,json
from pathlib import Path
OLD=Path('/Volumes/ESD-02/新チャンネル/EP010_Krampus/確認版_v01_20261102')
ROOT=OLD.parent/'確認版_v02_20261103'
os.environ['WOM10_ROOT']=str(ROOT)
import wom10_visuals as v
from PIL import Image,ImageDraw,ImageFont
from wom10_produce import read,save,sha

def prepare():
 for name in ['records','assets','audio','_work/render']:shutil.copytree(OLD/name,ROOT/name,dirs_exist_ok=True)
 for n in ['review','deliverables','_work/render']:(ROOT/n).mkdir(parents=True,exist_ok=True)
 for p in (OLD/'deliverables').iterdir():
  if p.suffix in ['.wav','.m4a','.srt','.md','.jpg','.txt','.csv']:shutil.copy2(p,ROOT/'deliverables'/p.name.replace('_v01_','_v02_'))
 print('PREPARED V02',flush=True)

def line(im,text,x,y,size=83,font=v.BOLD,major=True):
 f=ImageFont.truetype(font,size);d=ImageDraw.Draw(im);b=f.getbbox(text);w=b[2]-b[0];h=b[3]-b[1];x=round(x-w/2);d.text((x-b[0],y-b[1]),text,font=f,fill=v.INK);r=dict(text=text,bbox=[x,y,x+w,y+h],font=font,font_size=size,glyph_height=h,cap_height=f.getbbox('H')[3]-f.getbbox('H')[1],major=major,color=v.INK);v.TEXT.append(r);return r

def summary():
 im=v.base('SCHEMATIC｜模式図');d=ImageDraw.Draw(im);v.BOXES.clear()
 rows=[(['4th c. —','NICHOLAS,','BISHOP OF','MYRA'],'4世紀 ミュラの司教ニコラウス'),(['13th c. —','GOLDEN','LEGEND'],'13世紀『黄金伝説』'),(['DEVILS IN','THE SAINT\'S','SERVICE'],'聖人に仕える悪魔'),(['1869 → c. 1910 —','POSTCARDS'],'1869〜1910年ごろ 絵はがき'),(['19th c. —','GRIMM IMAGINES','A PAGAN PAST'],'19世紀 グリムが異教の過去を想像')]
 for i,(en,ja) in enumerate(rows):
  x0=40+(i*620 if i<3 else (i-3)*920);x1=x0+(584 if i<3 else 880);y0,y1=(120,510) if i<3 else (530,920);box=[x0,y0,x1,y1];d.rounded_rectangle(box,12,outline=v.ACCENT,width=3);start=len(v.TEXT);height=len(en)*68-8+16+26;y=round((y0+y1-height)/2)
  for text in en:line(im,text,(x0+x1)/2,y);y+=68
  line(im,ja,(x0+x1)/2,y+8,28,v.JA,False)
  ts=v.TEXT[start:];bb=[min(t['bbox'][0] for t in ts),min(t['bbox'][1] for t in ts),max(t['bbox'][2] for t in ts),max(t['bbox'][3] for t in ts)];gaps=[bb[0]-x0-3,bb[1]-y0-3,x1-3-bb[2],y1-3-bb[3]];assert min(gaps)>=24,(i,gaps);v.BOXES.append(dict(index=i+1,box=box,text_bbox=bb,padding_px=gaps,min_padding_px=min(gaps)))
 return im

def names(stage):
 im=v.base('SCHEMATIC｜模式図');d=ImageDraw.Draw(im)
 transform=lambda p:(80+(p[0]-269)*1.6,200+(p[1]-160)*1.65)
 germany=[(350,160),(460,172),(468,205),(554,235),(535,300),(570,350),(533,400),(545,445),(478,465),(420,452),(350,475),(314,420),(270,405),(300,352),(269,290),(310,252),(300,210)]
 austria=[(345,490),(409,477),(468,482),(510,465),(569,470),(626,459),(649,488),(613,517),(535,531),(480,524),(423,537),(361,523)]
 for polygon,fill in [(germany,'#d2c2a0'),(austria,'#c6b18a')]:d.polygon([transform(p) for p in polygon],fill=fill,outline=v.ACCENT,width=2)
 line(im,'GERMANY',365,410,42);line(im,'ドイツ',365,465,32,v.JA,False);line(im,'AUSTRIA',445,750,30,v.BOLD,False);line(im,'オーストリア',445,782,22,v.JA,False)
 rows=[('KNECHT RUPRECHT','— much of Germany','ドイツの多くの地域'),('KLAUBAUF','— parts of Tyrol and Carinthia','チロル・ケルンテンの一部'),('KRAMPUS','— Austria','オーストリア')]
 for i,(en,region,ja) in enumerate(rows):
  if stage<i+1:continue
  y=230+i*200;line(im,en,1330,y,86,v.COND);line(im,region,1330,y+88,38,v.EN,False);line(im,ja,1330,y+140,36,v.JA,False)
 line(im,'Names and roles varied from valley to valley',960,850,49,v.EN,False);line(im,'名前も役目も谷ごとに違った',960,890,38,v.JA,False)
 return im

def layout():
 m=read(ROOT/'records/visual_manifest.json');cards=[]
 for s in m['shots']:
  key=s['key']
  if not key.startswith('D_'):continue
  variants=[]
  for stage in range(4) if key=='D_names' else [99]:
   v.TEXT.clear();v.BOXES.clear()
   if key=='D_summary':im=summary()
   elif key=='D_names':im=names(stage)
   else:
    im=v.card(key);body=[t for t in v.TEXT if t['bbox'][1]>110];lo=min(t['bbox'][1] for t in body);hi=max(t['bbox'][3] for t in body);dy=round(550-(lo+hi)/2);base=Image.new('RGB',(1920,1080),v.BG);base.paste(im.crop((0,0,1920,110)),(0,0));base.paste(im.crop((0,110,1920,1080)),(0,110+dy));im=base
    for t in body:t['bbox']=[t['bbox'][0],t['bbox'][1]+dy,t['bbox'][2],t['bbox'][3]+dy]
   p=ROOT/f'assets/{key}_stage{stage}.png';im.save(p);variants.append(dict(stage=stage,file=str(p.relative_to(ROOT)),text_boxes=copy.deepcopy(v.TEXT)))
  im.save(ROOT/s['file']);s.update(stages=variants,text_boxes=copy.deepcopy(v.TEXT));cards.append(dict(key=key,foreground_contrast=v.contrast(v.INK,v.BG),accent_contrast=v.contrast(v.ACCENT,v.BG),text_boxes=copy.deepcopy(v.TEXT),boxes=copy.deepcopy(v.BOXES)))
 save(ROOT/'records/visual_manifest.json',m);save(ROOT/'records/layout_v02.json',dict(cards=cards,changed=['D_names','D_summary','D_dec6','D_1869','D_grimm','D_noancient'],audio_unchanged=True))
 for s in m['shots']:
  if s['key'].startswith('D_'):
   im=Image.open(ROOT/s['file']);im.thumbnail((1280,720));im.save(ROOT/f'review/{s["key"]}_v02.jpg',quality=92)
 print('LAYOUT COMPLETE',flush=True)
if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
