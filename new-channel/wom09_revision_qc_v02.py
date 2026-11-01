"""Matched-time comparison and invariants for EP009 layout-only revision."""
import os
os.environ.setdefault('WOM09_ROOT','/Users/ryo/Desktop/新チャンネル/EP009_TrojanHorse/確認版_v02_20261101')
from pathlib import Path
import json,subprocess,csv,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom09_produce import ROOT,read,save,sha
from wom09_revision_v02 import BASE
from wom09_visuals import EN,BG,INK,contrast
from wom01_quiet_origins import stream_hash

def main():
 shots=read(ROOT/'records/render_shots.json');oldshots=read(BASE/'records/render_shots.json');manifest=read(ROOT/'records/visual_manifest.json');oldmanifest=read(BASE/'records/visual_manifest.json')
 invariant=['key','segment_id','start','end','frames','stage_change_frames']
 assert [{k:s.get(k) for k in invariant} for s in shots]==[{k:s.get(k) for k in invariant} for s in oldshots]
 assert read(ROOT/'records/master_timeline.json')==read(BASE/'records/master_timeline.json')
 baseline=read(ROOT/'records/v01_baseline.json');assert all(sha(BASE/'deliverables'/n)==h for n,h in baseline['immutable_deliverables'].items())
 same=[]
 for lang in ['en','ja']:
  for suffix in ['wav','m4a']:
   n=f'EP009_audio_{lang}.{suffix}';assert sha(ROOT/'deliverables'/n)==sha(BASE/'deliverables'/n);same.append({'name':n,'sha256':sha(ROOT/'deliverables'/n)})
  n=f'EP009_TrojanHorse_{lang}_v02_1080p30.srt';oldn=n.replace('_v02_','_v01_');assert sha(ROOT/'deliverables'/n)==sha(BASE/'deliverables'/oldn);same.append({'name':n,'v01_name':oldn,'sha256':sha(ROOT/'deliverables'/n)})
  for review in ['', '_subtitled_review']:
   a=ROOT/f'deliverables/EP009_TrojanHorse_{lang}_v02{review}_1080p30.mp4';b=BASE/f'deliverables/EP009_TrojanHorse_{lang}_v01{review}_1080p30.mp4';assert stream_hash(a,'a')==stream_hash(b,'a');same.append({'name':a.name,'audio_stream_sha256':stream_hash(a,'a')})
 changed=[];header=[]
 for a,b in zip(manifest['shots'],oldmanifest['shots']):
  assert a['key']==b['key']
  p,q=ROOT/a['file'],BASE/b['file'];aa=np.asarray(Image.open(p));bb=np.asarray(Image.open(q));assert np.array_equal(aa[:110],bb[:110]),a['key'];header.append(a['key'])
  if not np.array_equal(aa,bb):changed.append(a['key'])
  if not a['key'].startswith('D_'):assert a['text_boxes']==b['text_boxes']
 assert set(changed)=={s['key'] for s in shots if s['key'].startswith('D_')}|{'met_437394'}
 selected=[]
 for s in shots:
  if s['key'].startswith('D_') or s['key']=='met_437394':
   local=max((s['frames']-1)//2,max(s.get('stage_change_frames',[]) or [0])+30);local=min(local,s['frames']-1);selected.append({'key':s['key'],'frame':round(s['start']*30)+local,'seconds':s['start']+local/30})
 expr='+'.join(f'eq(n\\,{x["frame"]})' for x in selected)
 for version,folder in [('v01',BASE),('v02',ROOT)]:
  dst=ROOT/f'_work/comparison_{version}';dst.mkdir(exist_ok=True)
  cmd=['ffmpeg','-nostdin','-y','-v','warning','-threads','2','-i',str(folder/f'deliverables/EP009_TrojanHorse_en_{version}_1080p30.mp4'),'-vf',f'select={expr},scale=1280:720','-fps_mode','passthrough','-pix_fmt','rgb24',str(dst/'%02d.png')]
  r=subprocess.run(cmd,capture_output=True,text=True,check=True);assert not r.stderr.strip()
  assert len(list(dst.glob('*.png')))==len(selected)
 comparisons=[];font=ImageFont.truetype(EN,22)
 for i,item in enumerate(selected,1):
  pair=Image.new('RGB',(1280,400),BG);d=ImageDraw.Draw(pair)
  for j,version in enumerate(['v01','v02']):
   d.text((j*640+14,9),f'{version}  {item["key"]}  {item["seconds"]:.3f}s',font=font,fill=INK)
   im=Image.open(ROOT/f'_work/comparison_{version}/{i:02d}.png');pair.paste(im.resize((640,360),Image.Resampling.LANCZOS),(j*640,40))
  path=ROOT/f'review/compare_{item["key"]}.jpg';pair.save(path,quality=91,optimize=True);comparisons.append({**item,'file':str(path.relative_to(ROOT)),'sha256':sha(path)})
  if item['key']=='met_437394':
   s=next(s for s in shots if s['key']==item['key']);x0,y0,x1,y1=s['art_boxes'][0];dx=(x1-x0)*.15;dy=(y1-y0)*.15;box=[round(v*2/3) for v in [x0+dx,y0+dy,x1-dx,y1-dy]];stats=[]
   for version in ['v01','v02']:
    a=np.asarray(Image.open(ROOT/f'_work/comparison_{version}/{i:02d}.png').crop(box)).astype(float);l=a@np.array([.2126,.7152,.0722]);stats.append({'version':version,'mean_luma':float(l.mean()),'black_pixels':int((l<=1).sum()),'white_pixels':int((l>=254).sum())})
   save(ROOT/'records/encoded_bust_comparison.json',{'frame':item['frame'],'roi_1280_xyxy':box,'stats':stats,'increase_percent':(stats[1]['mean_luma']/stats[0]['mean_luma']-1)*100})
 layout=read(ROOT/'records/card_layout_v02.json');rows=[]
 for c in layout['cards']:
  before=[t for t in c['v01_text_boxes'] if t['bbox'][1]>=110];before_min=min(x['font_size'] for x in before);before_max=max(x['font_size'] for x in before)
  rows.append({'key':c['key'],'v01_top_y':min(x['bbox'][1] for x in before),'v01_bottom_y':max(x['bbox'][3] for x in before),'v02_top_y':c['top_y'],'v02_bottom_y':c['bottom_y'],'v02_center_y':c['center_y'],'v01_font_min':before_min,'v01_font_max':before_max,'v02_font_min':c['min_font_px'],'v02_font_max':c['max_font_px'],'body_contrast':contrast(INK,BG),'accent_contrast':contrast('#5a3a1a',BG)})
  assert abs(c['center_y']-404)<=.5 and c['bottom_y']<=700 and c['top_y']>=110
  assert all(48<=b['bbox'][0] and b['bbox'][2]<=1872 for b in c['body_text_boxes'])
 for key,expected in [('D_lastline','"Thus held they funeral for Hector tamer of horses."'),('D_gifts','"I fear the Grecians even when they offer gifts."')]:assert (ROOT/f'records/{key}_screen_quote.txt').read_text().strip()==expected
 passes=next(c for c in layout['cards'] if c['key']=='D_passages')['body_text_boxes'];conclusion=next(b for b in passes if b['text'].startswith('A FEW DOZEN'));assert conclusion['font_size']>=60 and conclusion['font_style']=='bold'
 with (ROOT/'deliverables/EP009_layout_comparison_v02.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
 save(ROOT/'records/revision_qc_v02.json',{'passed':True,'changed_visuals':changed,'unchanged_header_count':len(header),'v01_deliverables_preserved':True,'timing_and_reveal_frames_unchanged':True,'same_audio_and_srt':same,'layout_rows':rows,'comparisons':comparisons,'human_full_listening':False,'comparison_extraction':'Continuous decode, same absolute frame in v01 and v02, later than final row reveal for animated cards'})
 print('V02 REVISION QC PASSED',len(comparisons),'comparisons',flush=True)
if __name__=='__main__':main()
