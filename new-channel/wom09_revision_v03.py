"""EP009 v03: repair only D_summary; keep v02 immutable."""
import os
from pathlib import Path
BASE=Path('/Users/ryo/Desktop/新チャンネル/EP009_TrojanHorse/確認版_v02_20261101')
os.environ.setdefault('WOM09_ROOT','/Volumes/ESD-02/新チャンネル/EP009_TrojanHorse/確認版_v03_20261101')
import argparse,copy,shutil,re
from PIL import Image,ImageDraw,ImageFont
from wom09_produce import ROOT,read,save,sha
from wom09_visuals import EN,BOLD,JA,BG,INK,ACCENT,contrast

def prepare():
 for d in ['records','assets','review','deliverables','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 names=['content.json','content_en.json','master_timeline.json','source_assets.json','request.json','audio_qc.json','reading_replacements.json','pronunciation_locations.json','chapters.json','subtitle_validation.json','first_pass_preserved.json','first_pass_identity.json','brand_audio_validation.json','environment.json','thumbnails.json','contrast.json','bust_luminance_v02.json']
 names += [f'{stem}_{lang}.json' for stem in ['narration_timeline','narration_segments','subtitle_cues','queries'] for lang in ['en','ja']]
 for n in names:shutil.copy2(BASE/'records'/n,ROOT/'records'/n)
 for folder in ['assets','_work/render']:
  for a in (BASE/folder).rglob('*'):
   if a.is_file():
    b=ROOT/a.relative_to(BASE);b.parent.mkdir(parents=True,exist_ok=True)
    if not b.exists():shutil.copy2(a,b)
 for a in (BASE/'deliverables').iterdir():
  if a.suffix in ['.wav','.m4a','.srt','.jpg','.md','.txt']:
   b=ROOT/'deliverables'/a.name.replace('_v02_','_v03_')
   if not b.exists():shutil.copy2(a,b)
 save(ROOT/'records/v02_baseline.json',{'root':str(BASE),'immutable_deliverables':{p.name:sha(p) for p in (BASE/'deliverables').iterdir() if p.is_file()},'request':'wom09_修正依頼_v03_20261101.md','scope':['D_summary layout only'],'storage':'User explicitly selected ESD-02 for new v03 files; no existing media moved'})
 print('V03 PREPARED',ROOT,flush=True)

def layout():
 m=copy.deepcopy(read(BASE/'records/visual_manifest.json'));s=next(x for x in m['shots'] if x['key']=='D_summary');old=copy.deepcopy(s)
 rows=[(['ILIAD —','NONE'],['イリアス：なし']),(['ODYSSEY —','A FEW DOZEN','LINES'],['オデュッセイア：','数十行']),(['LOST POEMS','& PICTURES'],['失われた詩と絵']),(['AENEID —','A DETAILED','STORY'],['アエネーイス：','詳しい物語'])]
 im=Image.new('RGB',(1920,1080),BG);im.paste(Image.open(BASE/s['file']).crop((0,0,1920,110)),(0,0));d=ImageDraw.Draw(im)
 cmds=[];boxes=[];arrows=[]
 for i,(en,ja) in enumerate(rows):
  x0=48+i*476;x1=x0+396;cx=(x0+x1)/2;box=[x0,184,x1,624];boxes.append({'index':i+1,'outline_xyxy':box,'stroke_width':3,'inner_xyxy':[x0+3,187,x1-3,621]})
  d.rounded_rectangle(box,radius=12,outline=ACCENT,width=3)
  for j,t in enumerate(en):cmds.append({'box':i+1,'text':t,'x':cx,'y':240+j*66,'font_size':48,'style':'bold','font':ImageFont.truetype(BOLD,48)})
  for j,t in enumerate(ja):cmds.append({'box':i+1,'text':t,'x':cx,'y':490+j*48,'font_size':35,'style':'ja','font':ImageFont.truetype(JA,35)})
  if i<3:
   ax0=x1+20;ax1=x1+60;d.line((ax0,404,ax1,404),fill=ACCENT,width=5);d.polygon([(ax1,404),(ax1-13,395),(ax1-13,413)],fill=ACCENT)
   arrows.append({'index':i+1,'xyxy':[ax0,395,ax1,413],'length_px':ax1-ax0,'left_gap_px':ax0-x1,'right_gap_px':x0+476-ax1})
 raw=[d.textbbox((a['x'],a['y']),a['text'],font=a['font'],anchor='mt') for a in cmds];dy=round(404-(min(x[1] for x in raw)+max(x[3] for x in raw))/2)
 texts=[]
 for a in cmds:
  xy=(a['x'],a['y']+dy);b=list(d.textbbox(xy,a['text'],font=a['font'],anchor='mt'));d.text(xy,a['text'],font=a['font'],fill=INK,anchor='mt');texts.append({'text':a['text'],'bbox':b,'font_size':a['font_size'],'font_style':a['style'],'color':INK,'box':a['box']})
 for box in boxes:
  ts=[t for t in texts if t['box']==box['index']];bb=[min(t['bbox'][0] for t in ts),min(t['bbox'][1] for t in ts),max(t['bbox'][2] for t in ts),max(t['bbox'][3] for t in ts)];inn=box['inner_xyxy'];gaps={'left':bb[0]-inn[0],'top':bb[1]-inn[1],'right':inn[2]-bb[2],'bottom':inn[3]-bb[3]};assert min(gaps.values())>=24,(box,gaps);box.update(text_bbox=bb,gaps_px=gaps,texts=ts)
 assert all(a['length_px']>=40 and min(a['left_gap_px'],a['right_gap_px'])>=16 for a in arrows)
 header=[b for b in s['text_boxes'] if b['bbox'][3]<=108];s['text_boxes']=header+texts
 clean=lambda text:re.sub(r'\s+','',text)
 assert clean(''.join(t['text'] for t in old['text_boxes']))==clean(''.join(t['text'] for t in s['text_boxes']))
 for v in s['stages']:im.save(ROOT/v['file']);v['text_boxes']=s['text_boxes']
 im.save(ROOT/s['file']);save(ROOT/'records/visual_manifest.json',m)
 rec={'passed':True,'boxes':boxes,'arrows':arrows,'english_font_px':48,'japanese_font_px':35,'overall_xyxy':[48,184,1872,624],'overall_center_y':404,'text_center_y':(min(t['bbox'][1] for t in texts)+max(t['bbox'][3] for t in texts))/2,'body_contrast':contrast(INK,BG),'accent_contrast':contrast(ACCENT,BG),'wording_unchanged_ignoring_whitespace':True}
 save(ROOT/'records/summary_layout_v03.json',rec)
 c=read(ROOT/'records/contrast.json');card=next(c for c in c['cards'] if c['key']=='D_summary');card.update(text_boxes=s['text_boxes'],max_text_y=max(t['bbox'][3] for t in texts));save(ROOT/'records/contrast.json',c)
 im.resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/'review/D_summary_v03.jpg',quality=93,optimize=True)
 print('SUMMARY GAPS',[(x['index'],x['gaps_px']) for x in boxes],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','layout']);a=p.parse_args();globals()[a.stage]()
