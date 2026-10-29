"""第8話v02：v01の音声・字幕・区間を固定し、映像だけを改訂する。"""
import os, json, shutil, subprocess, math, csv
from pathlib import Path
os.environ['WOM08_ROOT']='/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v02_20261030'
import numpy as np
from PIL import Image,ImageDraw,ImageOps,ImageFilter,ImageEnhance
from wom08_produce import ROOT,REPO,read,save,sha,ff,probe
OLD=ROOT.parent/'確認版_v01_20261029'
if not (ROOT/'records/source_assets.json').exists():shutil.copy2(OLD/'records/source_assets.json',ROOT/'records/source_assets.json')
import wom08_visuals_v02_base as v
from wom08_render import camera
BROWN='#3b2c21';SAND='#e8d9b7';GOLD=v.GOLD
PHOTO=[k for k in v.images if k.startswith('B') and k not in ['B164','B241','B312']]
colors={a['id']:a for a in read(ROOT/'records/color_assets_v02.json')['assets'] if a['selected']}
PLAN={**v.PLAN,'P05':['B183','C01','B299','B300'],'P09':['B313','C02','B312'],'P10':['D_novels_1869','D_novels_1892'],'P11':['D_warning','C03'],'P13':['D_summary','C04']}

def luma(a):return np.dot(np.asarray(a,dtype=np.float32),[.2126,.7152,.0722])
def toned(im):
 y=luma(im)/255.;target=float(y.mean())*1.12;lo,hi=0.,2.
 ys=y[::8,::8]
 for _ in range(24):
  a=(lo+hi)/2;z=np.minimum(ys+a*ys*(1-ys),np.where(ys<254/255,253/255,1.));q=z*(1-z)
  rgb=np.stack([z+.14*q,z+.008*q,z-.23*q],axis=-1).clip(0,1)
  if luma(rgb).mean()<target:lo=a
  else:hi=a
 z=np.minimum(y+a*y*(1-y),np.where(y<254/255,253/255,1.));q=z*(1-z)
 rgb=np.stack([z+.14*q,z+.008*q,z-.23*q],axis=-1).clip(0,1)
 rgb=np.where(((y>1/255)&(y<3/255))[...,None],np.maximum(rgb,2/255),rgb)
 return Image.fromarray(np.uint8(np.rint(rgb*255)))

def paper(im):
 a=np.asarray(im).astype(float)/255;return Image.fromarray(np.uint8(np.rint(np.power(a,.95)*255)))

def texture(dark=False):
 rng=np.random.default_rng(8 if dark else 7);a=rng.normal(0,.8,(1080,1920,1));base=np.array([223,207,170] if dark else [232,217,183]);return Image.fromarray(np.uint8((base+a).clip(0,255)))

def color_comp(key):
 a=colors[key];art=Image.open(a['original_path']).convert('RGB');assert sha(a['original_path'])==a['sha256']
 im=texture();v.TEXT=[];v.BOXES=[]
 label={'C01':'FACSIMILE｜1923–27年の模写','C02':'PERIOD OBJECT｜同時代の品','C03':'TOMB CHAPEL, 5TH DYNASTY｜第5王朝の礼拝室','C04':'PERIOD OBJECT｜同時代の品'}[key]
 source={'C01':'Charles K. Wilkinson, 1923–27 • Tomb of Huy (TT40) • The Met 30.4.21 • CC0','C02':'Signet ring, ca. 1328–1318 BCE • The Met 22.9.3 • CC0','C03':'Mastaba of Perneb, ca. 2381–2323 BCE • The Met 13.183.3 • CC0','C04':'Necklace with Tutankhamun bead, ca. 1328–1318 BCE • The Met 66.99.163 • CC0'}[key]
 v.header(im,label,source)
 note={'C01':'TOMB OF HUY, NOT KV62｜フイの墓（TT40）の壁画を写したもの','C02':'CONTEMPORARY OBJECT, NOT A KV62 FIND｜同時代の品・KV62出土品ではない','C03':'NOT THE ONE QUOTED｜引用された礼拝室とは別の墓','C04':'MODERN RESTRINGING, NOT A KV62 FIND｜現代の再連結・KV62出土品ではない'}[key]
 v.text(im,(960,132),note,29,BROWN,True)
 if key=='C03':v.text(im,(960,181),'同時代の別の墓の礼拝室',29,BROWN,True)
 if key=='C04':art=v.crop(art,(.025,.36,.96,.64))
 if key=='C02':art=v.crop(art,(.1,.13,.91,.87))
 v.panel(im,art,(100,235 if key=='C03' else 205,1720,690))
 return im,dict(key=key,base_asset=key,source=source,label=label,texts=v.TEXT.copy(),art_boxes=v.BOXES.copy(),camera_band=[235 if key=='C03' else 205,930],met_id=a['met_id'],object_number=a['object_number'],rights='CC0',original_sha256=a['sha256'],crop_is_not_recoloring=True)

def card_comp(key,stage=2):
 base='D_novels' if key.startswith('D_novels') else key
 im=texture(key=='D_novels_1892') if base!='D_illness' else Image.new('RGB',(1920,1080),'#cdbd9b')
 v.TEXT=[];v.BOXES=[]
 original_text=v.text
 def brown_text(im,xy,value,size=30,color=v.IVORY,center=False,serif=False):
  result=original_text(im,xy,value,size,BROWN if color in [v.IVORY,v.MUTED] else color,center,serif)
  if color==GOLD:
   f=v.font(size,value,serif);d=ImageDraw.Draw(im);pos=(xy[0]-d.textlength(value,font=f)/2,xy[1]) if center else xy
   d.text(pos,value,font=f,fill=GOLD,stroke_width=1,stroke_fill='#70582e')
  return result
 # The header remains the established navy strip, so its glyphs stay legible.
 original_header=v.header
 def header(im,label='',source=''):
  v.text=original_text;original_header(im,label,source);v.text=brown_text
 v.header=header;v.text=brown_text
 try:
  if base=='D_novels':
   v.header(im,'TITLE CARD｜文字カード','Alcott (1869) / Doyle (1892) • titles, not facsimile pages')
   rows=[('1869  Louisa May Alcott','Lost in a Pyramid; or, The Mummy’s Curse','ルイザ・メイ・オルコット','「ピラミッドで迷って、あるいはミイラの呪い」'),('1892  Arthur Conan Doyle','Lot No. 249','アーサー・コナン・ドイル「競売番号249」','')]
   for i,(a,b,c,e) in enumerate(rows[:1 if key.endswith('1869') else 2]):
    y=180+i*280;v.text(im,(140,y),a,40,GOLD);v.text(im,(140,y+60),b,43,v.IVORY,False,True);v.text(im,(140,y+125),c,31)
    if e:v.text(im,(140,y+171),e,31)
  elif base=='D_bmj':
   v.header(im,'SCHEMATIC｜模式図','Nelson, BMJ 2002;325:1482–1484 • historical cohort study');d=ImageDraw.Draw(im)
   for i,(x,a,b,n) in enumerate([(520,'PRESENT AT KEY OPENINGS','開封に立ち会った人','25'),(1400,'NOT PRESENT','立ち会わなかった人','11')]):
    d.rounded_rectangle((x-385,175,x+385,470),radius=15,outline='#9a8668',width=3);v.text(im,(x,210),a,30,GOLD,True);v.text(im,(x,270),b,31,v.IVORY,True)
    if stage>=i+1:v.text(im,(x,325),n,92,v.IVORY,True)
   for val,y,size,col in [('NO STATISTICALLY SIGNIFICANT LINK',525,38,GOLD),('統計的に有意な関連なし',580,33,v.IVORY),('Nelson, BMJ 2002 • 死亡情報が分かった36人',649,23,v.MUTED)]:v.text(im,(960,y),val,size,col,True)
  else:v.diagram(im,base)
 finally:v.text=original_text;v.header=original_header
 return im,dict(key=key,base_asset=None,source='',label='TITLE CARD｜文字カード' if base=='D_novels' else 'SCHEMATIC｜模式図',texts=v.TEXT.copy(),art_boxes=[],camera_band=[110,700],static_source=base not in ['D_novels','D_bmj'],intentional_reveal=base=='D_bmj')

def visuals():
 stats=[]
 for k,im in list(v.images.items()):
  im.thumbnail((3000,3000),Image.Resampling.LANCZOS)
  new=toned(im) if k in PHOTO else paper(im)
  a,b=luma(im),luma(new)
  stats.append(dict(key=k,old_mean=float(a.mean()),new_mean=float(b.mean()),increase_percent=float((b.mean()/a.mean()-1)*100),old_black=int((a<=1).sum()),new_black=int((b<=1).sum()),old_white=int((a>=254).sum()),new_white=int((b>=254).sum()),method='全画素共通の単色セピア曲線' if k in PHOTO else '紙面の輝度曲線'))
  if k in PHOTO:assert 10<=stats[-1]['increase_percent']<=15 and stats[-1]['new_black']<=stats[-1]['old_black'] and stats[-1]['new_white']<=stats[-1]['old_white'],stats[-1]
  print('TONE',k,round(stats[-1]['increase_percent'],3),flush=True)
  v.images[k]=new;new.save(ROOT/f'assets/{k}_toned.png')
 v.background=lambda art:ImageEnhance.Brightness(ImageOps.fit(art,(1920,1080)).filter(ImageFilter.GaussianBlur(55))).enhance(.355)
 records=[]
 for seg,keys in PLAN.items():
  for i,key in enumerate(keys):
   if key.startswith('C0'):im,rec=color_comp(key)
   elif key.startswith('D_'):im,rec=card_comp(key)
   elif key=='credits':
    im,rec=v.compose(key)
    # One added collection line, existing voice, AI and music credits retained.
    v.text(im,(130,636),'Collections',27,GOLD);v.text(im,(390,636),'The Metropolitan Museum of Art • Open Access (CC0)',25);rec['texts']=v.TEXT.copy();rec['static_source']=True
   else:im,rec=v.compose(key)
   p=ROOT/f'assets/{seg}_{i+1:02}_{key}.png';im.save(p);records.append({**rec,'segment_id':seg,'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
   if key=='D_bmj':
    for st in [0,1]:card_comp(key,st)[0].save(ROOT/f'assets/D_bmj_stage{st}.png')
 save(ROOT/'records/tone_measurements.json',{'photo_target':'元のクロップ内Rec.709平均輝度を10–15%上げる','photos':PHOTO,'measurements':stats})
 used=[r['base_asset'] for r in records if r.get('base_asset') and r['key']!='V01'];assert len(used)==len(set(used))==20
 save(ROOT/'records/visual_manifest.json',{'shots':records,'canvas':[1920,1080],'unique_originals':used})
 for batch in range(math.ceil(len(records)/9)):
  sheet=Image.new('RGB',(1280,800),'#18222b');d=ImageDraw.Draw(sheet)
  for j,s in enumerate(records[batch*9:batch*9+9]):
   x=j%3*426;y=j//3*266;sheet.paste(Image.open(ROOT/s['file']).resize((426,240)),(x,y));d.text((x+8,y+243),s['segment_id']+' '+s['key'],font=v.font(14),fill=v.IVORY)
  sheet.save(ROOT/f'review/compositions_{batch+1}.jpg',quality=85)
 print('V02 VISUALS',len(records),flush=True)

def pictures():
 old=read(OLD/'records/render_shots.json');manifest=read(ROOT/'records/visual_manifest.json')['shots'];master=read(ROOT/'records/master_timeline.json');narr=read(ROOT/'records/narration_timeline_en.json')['segments'];shots=[]
 def cut(seg,phrase):return round(next(c['start'] for s in narr if s['id']==seg for c in s['cues'] if c['text'].startswith(phrase))*30)
 for seg in master['segments']:
  sid=seg['id'];group=[s for s in manifest if s['segment_id']==sid];prev=[s for s in old if s['segment_id']==sid];bounds=[round(prev[0]['start']*30)]+[round(s['end']*30) for s in prev]
  if sid=='P05':bounds.insert(1,round((seg['start']+1.5)*30))
  if sid=='P09':bounds.insert(1,cut(sid,'Among'))
  if sid=='P10':bounds.insert(1,cut(sid,'In 1892'))
  if sid=='P11':bounds.insert(1,cut(sid,'One tomb'))
  if sid=='P13':bounds.insert(1,cut(sid,'The tomb'))
  assert len(bounds)==len(group)+1 and all(a<b for a,b in zip(bounds,bounds[1:])),(sid,bounds)
  for j,s in enumerate(group):
   key=s['key'];n=bounds[j+1]-bounds[j];out=ROOT/f'_work/render/{sid}_{j+1:02}_{key}.mp4';args=['-loop',1,'-framerate',30,'-i',ROOT/s['file']];static=s.get('static_source',False)
   if key=='V01':
    reuse=prev[0];src=OLD/reuse['encoded_file'];assert reuse['frames']==n
    shots.append({**s,'start':bounds[j]/30,'end':bounds[j+1]/30,'frames':n,'encoded_file':str(src),'v01_reuse_sha256':sha(src)});continue
   if key=='D_bmj':
    # Two deliberate number reveals; every frame difference remains in QA.
    args=['-loop',1,'-framerate',30,'-i',ROOT/'assets/D_bmj_stage0.png','-loop',1,'-framerate',30,'-i',ROOT/'assets/D_bmj_stage1.png','-loop',1,'-framerate',30,'-i',ROOT/s['file']]
    filt="[0:v][1:v]overlay=enable='gte(n,60)'[a];[a][2:v]overlay=enable='gte(n,150)',format=yuv420p[v]";static=True
   elif key.startswith('D_novels'):filt=camera(n,s['camera_band'],amount=.03)
   elif key.startswith('D_') or key=='credits':filt='[0:v]format=yuv420p[v]';static=True
   else:filt=camera(n,s['camera_band'],direction='bottom_to_top' if key=='B157' else None)
   cfg={'frames':n,'filter':filt,'image_sha256':s['sha256'],'lossless_intermediate':static}
   stamp=out.with_suffix('.json')
   if not(out.exists() and stamp.exists() and read(stamp)==cfg):
    ff([*args,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',n,'-an','-c:v','libx264','-threads',2,'-preset','veryfast',*(['-qp',0,'-profile:v','high444'] if static else ['-crf',18,'-profile:v','high']),'-pix_fmt','yuv420p','-video_track_timescale',15360,out]);save(stamp,cfg)
   assert int(next(x for x in probe(out)['streams'] if x['codec_type']=='video')['nb_frames'])==n
   shots.append({**s,'start':bounds[j]/30,'end':bounds[j+1]/30,'frames':n,'encoded_file':str(out.relative_to(ROOT)),'render_config':cfg})
   print('V02 RENDERED',sid,key,n,flush=True)
  if sid=='P02':shots.append(next(s for s in old if s['key']=='opening'))
 shots.append(next(s for s in old if s['key']=='endcard'));assert len(shots)==30 and sum(s['frames'] for s in shots)==10427
 save(ROOT/'records/render_shots.json',shots)
 out=ROOT/'_work/picture_master.mp4';records=[]
 cmd=['ffmpeg','-nostdin','-y','-v','warning','-f','rawvideo','-pixel_format','yuv420p','-video_size','1920x1080','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','3','-preset','medium','-crf','16','-profile:v','high','-level:v','4.1','-pix_fmt','yuv420p','-g','60','-bf','2','-maxrate','20M','-bufsize','30M','-fps_mode','passthrough','-video_track_timescale','15360','-movie_timescale','48000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(out)]
 with (ROOT/'records/encode.log').open('w') as log:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for s in shots:
    src=ROOT/s['encoded_file'];subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True);records.append({'key':s['key'],'frames':s['frames']});print('ASSEMBLE',s['key'],flush=True)
   enc.stdin.close();assert enc.wait()==0
  except BaseException:enc.kill();enc.wait();raise
 save(ROOT/'records/encoding_method.json',{'method':'Independent shot decoders feeding one raw-video encoder','shots':records,'command':cmd})
 print('V02 PICTURE MASTER COMPLETE',flush=True)

if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
