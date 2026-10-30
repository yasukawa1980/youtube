"""第8話v03。文字カードの色とP10の文字配置だけを変更する。"""
import os,copy,subprocess,shutil,json,csv,math
from pathlib import Path
os.environ['WOM08_ROOT']='/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v03_20261030'
import numpy as np
from PIL import Image,ImageDraw
from wom08_produce import ROOT,REPO,read,save,sha,ff,probe
from wom08_render import camera
OLD=ROOT.parent/'確認版_v02_20261030'
ACCENT='#5a3a1a';BROWN='#3b2c21';GOLD='#d8b575'
CHANGED={'D_illness','D_novels_1869','D_novels_1892','D_warning','D_bmj','D_summary'}
# Established header/font helpers only; importing the photo module would reload all scans.
helper={};source=(REPO/'new-channel/wom08_visuals.py').read_text().split('assets={')[0]
exec(compile(source,'wom08_visuals_helpers','exec'),helper)

def texture(key):
 if key=='D_illness':return Image.new('RGB',(1920,1080),'#cdbd9b')
 dark=key=='D_novels_1892';rng=np.random.default_rng(8 if dark else 7)
 a=rng.normal(0,.8,(1080,1920,1));base=np.array([223,207,170] if dark else [232,217,183]);return Image.fromarray(np.uint8((base+a).clip(0,255)))

def card(key,stage=2):
 im=texture(key);bg=im.copy();helper['TEXT']=[];body=[]
 base='D_novels' if key.startswith('D_novels') else key
 sources={'D_illness':'Howard Carter, journal, March–April 1923 • Griffith Institute transcription','D_novels':'Alcott (1869) / Doyle (1892) • titles, not facsimile pages','D_warning':'Hetepherakhty, c. 2400 BC • Rijksmuseum van Oudheden commentary','D_bmj':'Nelson, BMJ 2002;325:1482–1484 • historical cohort study','D_summary':'Carter & Mace (1923) / US newspapers (April 1923) / earlier fiction'}
 helper['header'](im,'TITLE CARD｜文字カード' if base=='D_novels' else 'SCHEMATIC｜模式図',sources[base])
 def t(x,y,val,size=40,color=BROWN,serif=False):
  helper['text'](im,(x,y),val,size,color,True,serif)
  rec=helper['TEXT'][-1];rec.update(font_size=size,fill=color,centered=True,serif=serif);body.append(rec)
 d=ImageDraw.Draw(im)
 if base=='D_illness':
  t(960,260,'MARCH 1923｜1923年3月',50,ACCENT);t(960,350,'INFECTION, THEN PNEUMONIA',49);t(960,420,'感染症、のちに肺炎',44);t(960,570,'5 APRIL 1923, CAIRO｜1923年4月5日 カイロ',43,ACCENT)
 elif base=='D_novels':
  t(960,220,'1869  Louisa May Alcott',48,ACCENT);t(960,280,'Lost in a Pyramid; or, The Mummy’s Curse',69,BROWN,True);t(960,370,'ルイザ・メイ・オルコット',40);t(960,425,'「ピラミッドで迷って、あるいはミイラの呪い」',40)
  if key.endswith('1892'):
   t(960,500,'1892  Arthur Conan Doyle',48,ACCENT);t(960,560,'Lot No. 249',69,BROWN,True);t(960,645,'アーサー・コナン・ドイル「競売番号249」',40)
 elif base=='D_warning':
  xs=[365,960,1555];d.line((xs[0],300,xs[-1],300),fill='#59646b',width=4)
  for i,(x,a,b,c) in enumerate(zip(xs,['c. 2400 BC','c. 1330 BC','1922'],['TOMB CHAPEL WARNING','TUTANKHAMUN','DISCOVERY'],['前2400年ごろ 墓の礼拝室の警告','前1330年ごろ ツタンカーメン','1922年 発見'])):
   # Dots and rule retain v02 colors; only text color/size changes.
   d.ellipse((x-8,292,x+8,308),fill=GOLD if i==0 else '#b0bfc3');color=ACCENT if i==0 else BROWN
   t(x,365,a,49,color);t(x,439,b,32,color);t(x,495,c,27,color)
 elif base=='D_bmj':
  for i,(x,a,b,n) in enumerate([(520,'PRESENT AT KEY OPENINGS','開封に立ち会った人','25'),(1400,'NOT PRESENT','立ち会わなかった人','11')]):
   d.rounded_rectangle((x-385,175,x+385,470),radius=15,outline='#9a8668',width=3);t(x,210,a,34,ACCENT);t(x,270,b,34)
   if stage>=i+1:t(x,325,n,92)
  t(960,525,'NO STATISTICALLY SIGNIFICANT LINK',43,ACCENT);t(960,580,'統計的に有意な関連なし',38);t(960,649,'Nelson, BMJ 2002 • 死亡情報が分かった36人',26)
 elif base=='D_summary':
  for val,y in [('1869–1892 STORIES｜物語',230),('APRIL 1923 A DEATH｜1923年4月 死去',330),('NEWSPAPERS｜新聞',430)]:t(960,y,val,44)
  t(960,585,'“THE CURSE”｜「呪い」',64,ACCENT)
 else:raise ValueError(key)
 return im,{'texts':helper['TEXT'].copy(),'body_texts':body,'camera_band':[110,700]},bg

def relative_luminance(rgb):
 a=np.asarray(rgb,dtype=np.float64)/255.;a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);return a@[.2126,.7152,.0722]

def prepare():
 for d in ['records','assets','review','deliverables','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 records=['content.json','content_en.json','master_timeline.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_cues_en.json','subtitle_cues_ja.json','subtitle_validation.json','audio_qc.json','reading_replacements.json','pronunciation_locations.json','ai_videos.json','kling_generation.json','request.json','bgm_band_comparison.json','source_assets.json','color_assets_v02.json','thumbnail_qc.json','chapters.json']
 for name in records:shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
 for p in (OLD/'deliverables').iterdir():
  if p.suffix in ['.wav','.m4a','.srt','.txt','.jpg','.md']:
   dst=ROOT/'deliverables'/(p.name.replace('_v02_','_v03_') if p.suffix=='.srt' else p.name)
   if not dst.exists():shutil.copy2(p,dst)
   assert sha(p)==sha(dst)
 manifest=read(OLD/'records/visual_manifest.json');contrasts=[];oldby={s['key']:s for s in manifest['shots']}
 for s in manifest['shots']:
  key=s['key']
  if key not in CHANGED:s['file']=str(OLD/s['file']);s['v02_image_reused']=True;continue
  im,data,bg=card(key);p=ROOT/f'assets/{s["segment_id"]}_{key}.png';im.save(p)
  assert [x['text'] for x in data['texts']]==[x['text'] for x in s['texts']],key
  # Navy source/header strip and all non-text backdrop pixels remain established v02 styling.
  assert np.array_equal(np.asarray(im)[:110],np.asarray(Image.open(OLD/s['file']))[:110]),key
  prior=np.asarray(Image.open(OLD/s['file']).convert('RGB'));current=np.asarray(im);mask=np.ones((1080,1920),bool)
  for row in s['texts']+data['texts']:
   x0,y0,x1,y1=row['bbox'];mask[max(0,math.floor(y0)-4):min(1080,math.ceil(y1)+4),max(0,math.floor(x0)-4):min(1920,math.ceil(x1)+4)]=False
  assert np.array_equal(prior[mask],current[mask]),(key,'文字領域以外に差分あり')
  s.update(data,file=str(p.relative_to(ROOT)),sha256=sha(p),nontext_pixels_identical_to_v02=True,revision='v03: body ink contrast / larger centered titles')
  y=relative_luminance(np.asarray(bg))
  for row in data['body_texts']:
   x0,y0,x1,y1=map(int,row['bbox']);l=y[y0:y1,x0:x1];fg=relative_luminance(np.array(tuple(bytes.fromhex(row['fill'][1:]))));ratios=(np.maximum(l,fg)+.05)/(np.minimum(l,fg)+.05)
   minimum=float(ratios.min());assert minimum>=4.5,(key,row['text'],minimum)
   contrasts.append({'key':key,'text':row['text'],'foreground':row['fill'],'font_size':row['font_size'],'bbox':row['bbox'],'background_min_luminance':float(l.min()),'minimum_contrast_ratio':minimum,'median_contrast_ratio':float(np.median(ratios)),'passed':True})
  if key=='D_bmj':
   for stage in [0,1]:card(key,stage)[0].save(ROOT/f'assets/D_bmj_stage{stage}.png')
 save(ROOT/'records/visual_manifest.json',manifest)
 save(ROOT/'records/contrast_validation.json',{'passed':True,'method':'WCAG相対輝度：sRGBを線形化し(.2126,.7152,.0722)で加重、(L明+.05)/(L暗+.05)。実際に描画した文字色と、描画前の同じ背景画像の各文字bbox内全画素から最小値を測定。アンチエイリアス縁の混色は文字色にはしない。紺のヘッダーは変更なし。','reference_urls':['https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html','https://www.w3.org/TR/WCAG22/#dfn-relative-luminance'],'accent':ACCENT,'body':BROWN,'novel_english_title_size':69,'v02_english_title_size':43,'enlargement':69/43,'minimum':min(r['minimum_contrast_ratio'] for r in contrasts),'rows':contrasts})
 with (ROOT/'deliverables/EP008_contrast_v03.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(contrasts[0]),lineterminator='\n');w.writeheader();w.writerows(contrasts)
 sheet=Image.new('RGB',(1280,1160),'#18222b');d=ImageDraw.Draw(sheet)
 for i,key in enumerate(['D_illness','D_novels_1869','D_novels_1892','D_warning','D_bmj','D_summary']):
  s=next(s for s in manifest['shots'] if s['key']==key);x=i%2*640;y0=i//2*386;sheet.paste(Image.open(ROOT/s['file']).resize((640,360)),(x,y0));d.text((x+8,y0+363),s['segment_id']+' '+key,fill='white')
 sheet.save(ROOT/'review/v03_cards.jpg',quality=90,optimize=True)
 print('V03 PREPARED; contrast minimum',min(r['minimum_contrast_ratio'] for r in contrasts),'titles',69/43,flush=True)

def pictures():
 manifest={s['key']:s for s in read(ROOT/'records/visual_manifest.json')['shots']};shots=copy.deepcopy(read(OLD/'records/render_shots.json'))
 for s in shots:
  key=s['key'];src=OLD/s['encoded_file']
  if key not in CHANGED:
   s['encoded_file']=str(src);s['v02_intermediate_sha256']=sha(src)
   if 'file' in s:s['file']=str(OLD/s['file'])
   continue
  new=manifest[key];s.update(new);n=s['frames'];out=ROOT/f'_work/render/{s["segment_id"]}_{key}.mp4';static=not key.startswith('D_novels');args=['-loop',1,'-framerate',30,'-i',ROOT/s['file']]
  if key=='D_bmj':
   args=['-loop',1,'-framerate',30,'-i',ROOT/'assets/D_bmj_stage0.png','-loop',1,'-framerate',30,'-i',ROOT/'assets/D_bmj_stage1.png','-loop',1,'-framerate',30,'-i',ROOT/s['file']]
   filt="[0:v][1:v]overlay=enable='gte(n,60)'[a];[a][2:v]overlay=enable='gte(n,150)',format=yuv420p[v]"
  else:filt='[0:v]format=yuv420p[v]' if static else camera(n,s['camera_band'],amount=.03)
  cfg={'frames':n,'filter':filt,'image_sha256':s['sha256'],'lossless_intermediate':static}
  stamp=out.with_suffix('.json')
  if not(out.exists() and stamp.exists() and read(stamp)==cfg):
   ff([*args,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',n,'-an','-c:v','libx264','-threads',2,'-preset','veryfast',*(['-qp',0,'-profile:v','high444'] if static else ['-crf',18,'-profile:v','high']),'-pix_fmt','yuv420p','-video_track_timescale',15360,out]);save(stamp,cfg)
  assert int(next(x for x in probe(out)['streams'] if x['codec_type']=='video')['nb_frames'])==n
  s.update(encoded_file=str(out.relative_to(ROOT)),render_config=cfg);print('V03 CARD',key,n,flush=True)
 assert len(shots)==30 and sum(s['frames'] for s in shots)==10427
 save(ROOT/'records/render_shots.json',shots)
 method=read(OLD/'records/encoding_method.json');cmd=method['command'];cmd[-1]=str(ROOT/'_work/picture_master.mp4');records=[]
 with (ROOT/'records/encode.log').open('w') as log:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for s in shots:
    src=ROOT/s['encoded_file'];subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True);records.append({'key':s['key'],'frames':s['frames'],'source_sha256':sha(src)});print('ASSEMBLE',s['key'],flush=True)
   enc.stdin.close();assert enc.wait()==0
  except BaseException:enc.kill();enc.wait();raise
 save(ROOT/'records/encoding_method.json',{'method':'Independent shot decoders feeding one raw-video encoder','shots':records,'command':cmd,'v02_unchanged_intermediates':24,'changed_card_shots':6})
 print('V03 PICTURE MASTER COMPLETE',flush=True)

if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
