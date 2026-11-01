"""EP009 v02: preserve v01; revise nine card layouts and bust luminance only."""
import os
from pathlib import Path
BASE=Path('/Users/ryo/Desktop/新チャンネル/EP009_TrojanHorse/確認版_v01_20261101')
os.environ.setdefault('WOM09_ROOT',str(BASE.with_name('確認版_v02_20261101')))
import argparse,copy,shutil,subprocess,re,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom09_produce import ROOT,read,save,sha
from wom09_visuals import EN,BOLD,SERIF,JA,BG,INK,ACCENT,contrast
JB='/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
FONTS={'en':EN,'bold':BOLD,'serif':SERIF,'ja':JA,'ja_bold':JB}

def clone(a,b):
 b.parent.mkdir(parents=True,exist_ok=True)
 if not b.exists():subprocess.run(['/bin/cp','-c',str(a),str(b)],check=True)
 assert a.stat().st_ino!=b.stat().st_ino,'Use independent APFS clones, never hard links'

def prepare():
 for d in ['records','assets','review','deliverables','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 names=['content.json','content_en.json','master_timeline.json','source_assets.json','request.json','audio_qc.json','reading_replacements.json','pronunciation_locations.json','chapters.json','subtitle_validation.json','first_pass_preserved.json','first_pass_identity.json','brand_audio_validation.json','environment.json','thumbnails.json']
 names += [f'{stem}_{lang}.json' for stem in ['narration_timeline','narration_segments','subtitle_cues','queries'] for lang in ['en','ja']]
 for n in names:
  a=BASE/'records'/n;b=ROOT/'records'/n
  if not b.exists():shutil.copy2(a,b)
  else:assert sha(a)==sha(b),n
 for folder in ['assets','audio','_work/render']:
  for a in (BASE/folder).rglob('*'):
   if a.is_file():clone(a,ROOT/a.relative_to(BASE))
 for a in (BASE/'deliverables').iterdir():
  if a.suffix in ['.wav','.m4a','.srt','.jpg','.md','.txt']:
   clone(a,ROOT/'deliverables'/a.name.replace('_v01_','_v02_'))
 save(ROOT/'records/v01_baseline.json',{'root':str(BASE),'immutable_deliverables':{p.name:sha(p) for p in (BASE/'deliverables').iterdir() if p.is_file()},'request':'wom09_修正依頼_v02_20261101.md','scope':['nine card typography/layouts','Rembrandt bust mean luminance +10%'],'copy_method':'APFS copy-on-write clones with distinct inodes; v01 never overwritten'})
 print('V02 PREPARED',ROOT,flush=True)

def commands(key):
 c=[];g=[]
 def t(s,x,y,n,style='en',stage=0):c.append({'text':s,'x':x,'y':y,'font_size':n,'style':style,'stage':stage})
 def mid(s,y,n,style='en',stage=0):t(s,960,y,n,style,stage)
 if key=='D_lastline':
  mid('"Thus held they funeral for',0,86,'serif');mid('Hector tamer of horses."',110,86,'serif');mid('こうして彼らは、馬を馴らすヘクトルの葬儀を営んだ。',245,49,'ja')
 elif key=='D_nohorse':
  mid('NO HORSE',0,143,'bold');mid('IN THE ILIAD',164,137,'bold');mid('『イリアス』に木馬は出てこない',344,62,'ja')
 elif key=='D_options':
  mid('Odyssey, Book 8｜『オデュッセイア』8巻',0,55,'ja')
  for i,(en,ja) in enumerate([('BREAK IT OPEN','打ち割る'),('THROW IT ONTO THE ROCKS','岩の上へ投げ落とす'),('KEEP IT FOR THE GODS','神々への捧げ物に')]):
   mid(en,95+130*i,60,'bold',i+1);mid(ja,161+130*i,43,'ja',i+1)
 elif key=='D_passages':
  for i,(en,ja) in enumerate([('Odyssey 4  Helen and the voices','4巻 ヘレネと妻たちの声'),('Odyssey 8  The song of Demodocus','8巻 デモドコスの歌'),("Odyssey 11  Achilles' son",'11巻 アキレウスの息子')]):
   mid(en,i*122,60);mid(ja,65+i*122,42,'ja')
  mid('A FEW DOZEN LINES · NO NUMBER OF MEN',379,60,'bold',1);mid('合わせて数十行・人数の記述なし',448,44,'ja_bold',1)
 elif key=='D_lostpoems':
  t('LITTLE ILIAD ·',480,130,60,'bold');t('SACK OF TROY',480,205,60,'bold');t('『小イリアス』『イリオスの陥落』',480,300,38,'ja');t('(not surviving in full｜全文は残らない)',480,360,36,'ja')
  t('LATER SUMMARIES｜後世の要約',1440,0,49,'ja')
  for i,(en,ja) in enumerate([('THE HORSE','木馬'),('A BROKEN WALL','崩された城壁'),('LAOCOÖN AND THE SERPENTS','ラオコーンと大蛇'),('SINON','シノン')]):
   t(en,1440,88+i*101,42,'bold',i+1);t(ja,1440,140+i*101,35,'ja',i+1)
  g.append(('arrow',(914,239,1006,239)))
 elif key=='D_gifts':
  mid('"I fear the Grecians even',0,88,'serif');mid('when they offer gifts."',112,88,'serif');mid('timeo Danaos et dona ferentes',245,47,'serif');mid('私は、贈り物を携えたギリシャ人さえ恐れる',324,52,'ja')
 elif key=='D_timeline':
  for x,en,date,ja,jdate in [(350,"HOMER'S POEMS",'8th–7th c. BC','ホメロスの詩','前8〜7世紀ごろ'),(960,'MYKONOS JAR','c. 670 BC','ミコノスの甕','前670年ごろ'),(1570,'AENEID','c. 29–19 BC','アエネーイス','前29〜19年ごろ')]:
   t(en,x,0,60,'bold');t(date,x,82,46);t(ja,x,205,46,'ja');t(jdate,x,285,39,'ja')
  g.append(('timeline',(350,404,1570,404)))
 elif key=='D_count':
  t('50?',530,0,228,'bold');t('3,000?',1390,0,228,'bold');mid('Apollodorus, Epitome 5.14 (citing the Little Iliad for 3,000)',275,46);mid('アポロドーロス『摘要』（3000人は『小イリアス』の作者による）',352,43,'ja')
 elif key=='D_summary':
  rows=[(['ILIAD —','NONE'],['イリアス：なし']),(['ODYSSEY —','A FEW DOZEN','LINES'],['オデュッセイア：','数十行']),(['LOST POEMS','& PICTURES'],['失われた詩と絵']),(['AENEID —','A DETAILED','STORY'],['アエネーイス：','詳しい物語'])]
  for i,(en,ja) in enumerate(rows):
   x=273+i*458
   for j,line in enumerate(en):t(line,x,j*79,60,'bold')
   for j,line in enumerate(ja):t(line,x,270+j*48,35,'ja')
   g.append(('box',(x-205,-45,x+205,400)))
   if i<3:g.append(('arrow',(x+214,177,x+244,177)))
 else:raise KeyError(key)
 return c,g

def layouts():
 m=copy.deepcopy(read(BASE/'records/visual_manifest.json'));old={s['key']:copy.deepcopy(s) for s in m['shots']};cards=[];bounds=[]
 for s in m['shots']:
  key=s['key']
  if not key.startswith('D_'):continue
  c,g=commands(key);dummy=ImageDraw.Draw(Image.new('RGB',(1920,1080)))
  for a in c:a['font']=ImageFont.truetype(FONTS[a['style']],a['font_size']);a['raw_bbox']=dummy.textbbox((a['x'],a['y']),a['text'],font=a['font'],anchor='mt')
  lo=min(a['raw_bbox'][1] for a in c);hi=max(a['raw_bbox'][3] for a in c);dy=round(404-(lo+hi)/2)
  header=[b for b in s['text_boxes'] if b['bbox'][3]<=108];variants=[]
  for v in s['stages']:
   stage=v['stage'];has_reveal=key in ['D_options','D_passages','D_lostpoems'];im=Image.new('RGB',(1920,1080),BG);im.paste(Image.open(BASE/s['file']).crop((0,0,1920,110)),(0,0));d=ImageDraw.Draw(im);boxes=[]
   for kind,xy in g:
    x0,y0,x1,y1=xy
    if kind=='timeline':
     d.line((x0,404,x1,404),fill=ACCENT,width=5)
     for x in [350,960,1570]:d.ellipse((x-11,393,x+11,415),fill=ACCENT)
    elif kind=='box':d.rounded_rectangle((x0,y0+dy,x1,y1+dy),radius=12,outline=ACCENT,width=3)
    else:d.line((x0,y0+dy,x1,y1+dy),fill=ACCENT,width=5);d.polygon([(x1,y1+dy),(x1-15,y1+dy-10),(x1-15,y1+dy+10)],fill=ACCENT)
   for a in c:
    if has_reveal and a['stage']>stage:continue
    xy=(a['x'],a['y']+dy);b=d.textbbox(xy,a['text'],font=a['font'],anchor='mt');assert 48<=b[0] and b[2]<=1872 and 110<=b[1] and b[3]<=700,(key,a['text'],b)
    d.text(xy,a['text'],font=a['font'],fill=INK,anchor='mt');boxes.append({'text':a['text'],'bbox':list(b),'font_size':a['font_size'],'font_style':a['style'],'color':INK})
   p=ROOT/v['file'];im.save(p);variants.append({**v,'text_boxes':header+boxes})
  im.save(ROOT/s['file']);s['stages']=variants;s['text_boxes']=header+boxes
  before=''.join(a['text'] for a in old[key]['text_boxes']);after=''.join(a['text'] for a in s['text_boxes']);clean=lambda x:re.sub(r'\s+','',x)
  assert clean(before)==clean(after),(key,before,after)
  top=min(b['bbox'][1] for b in boxes);bottom=max(b['bbox'][3] for b in boxes);assert abs((top+bottom)/2-404)<=.5
  cards.append({'key':key,'background':BG,'foreground':INK,'foreground_contrast':contrast(INK,BG),'accent':ACCENT,'accent_contrast':contrast(ACCENT,BG),'max_text_y':bottom,'text_boxes':s['text_boxes']})
  bounds.append({'key':key,'top_y':top,'bottom_y':bottom,'center_y':(top+bottom)/2,'min_font_px':min(b['font_size'] for b in boxes),'max_font_px':max(b['font_size'] for b in boxes),'body_text_boxes':boxes,'v01_text_boxes':old[key]['text_boxes'],'fixed_positions_during_row_reveals':True})
  print('CARD',key,top,bottom,flush=True)
 # Brighten only existing displayed artwork pixels. A common RGB gain based on
 # luminance preserves channel ratios; a smooth highlight shoulder avoids clipping.
 s=next(s for s in m['shots'] if s['key']=='met_437394');im=Image.open(BASE/s['file']).convert('RGB');x0,y0,x1,y1=s['art_boxes'][0];a=np.asarray(im.crop((x0,y0,x1,y1))).astype(float);lum=a@np.array([.2126,.7152,.0722]);target=lum.mean()*1.1
 def adjusted(k):
  gain=1+k*(1-(a.max(axis=2)/255)**2);out=np.rint(a*gain[:,:,None]);return np.clip(out,0,255).astype(np.uint8)
 lo,hi=0.,.3
 for _ in range(35):
  mid=(lo+hi)/2;b=adjusted(mid)
  if (b@np.array([.2126,.7152,.0722])).mean()<target:lo=mid
  else:hi=mid
 b=adjusted((lo+hi)/2);assert np.count_nonzero(b==255)<=np.count_nonzero(a==255);assert np.count_nonzero(b==0)<=np.count_nonzero(a==0)
 im.paste(Image.fromarray(b),(x0,y0));im.save(ROOT/s['file']);mean0=float(lum.mean());mean1=float((b@np.array([.2126,.7152,.0722])).mean());assert abs(mean1/mean0-1.1)<.0001
 save(ROOT/'records/bust_luminance_v02.json',{'roi_xyxy':[x0,y0,x1,y1],'v01_mean_luma_8bit':mean0,'v02_mean_luma_8bit':mean1,'increase_percent':(mean1/mean0-1)*100,'gain_parameter':(lo+hi)/2,'v01_black_channels':int((a==0).sum()),'v02_black_channels':int((b==0).sum()),'v01_white_channels':int((a==255).sum()),'v02_white_channels':int((b==255).sum()),'method':'Smooth luminance-dependent common RGB multiplier; original RGB ratios retained before 8-bit rounding. Pixels outside the art box unchanged.'})
 save(ROOT/'records/visual_manifest.json',m);save(ROOT/'records/contrast.json',{'passed':True,'cards':cards});save(ROOT/'records/card_layout_v02.json',{'target_center_y':404,'safe_y':[110,700],'minimum_side_margin':48,'cards':bounds})
 for key,expected in [('D_lastline','"Thus held they funeral for Hector tamer of horses."'),('D_gifts','"I fear the Grecians even when they offer gifts."')]:
  actual=' '.join(a['text'] for a in commands(key)[0] if a['style']=='serif' and a['font_size']>=80);assert actual==expected;(ROOT/f'records/{key}_screen_quote.txt').write_text(actual+'\n')
 sheet=Image.new('RGB',(1280,4*260),BG);d=ImageDraw.Draw(sheet)
 selected=[s for s in m['shots'] if s['key'].startswith('D_') or s['key']=='met_437394']
 for i,s in enumerate(selected):
  x=i%3*426;y=i//3*260;im=Image.open(ROOT/s['file']);im.thumbnail((426,240));sheet.paste(im,(x,y+20));d.text((x+6,y),s['key'],fill=INK)
 sheet.save(ROOT/'review/layout_v02.jpg',quality=88,optimize=True)
 print('BUST LUMINANCE',mean0,mean1,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','layouts']);args=p.parse_args();globals()[args.stage]()
