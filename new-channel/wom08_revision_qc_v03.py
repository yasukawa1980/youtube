"""v03の限定変更・保持条件・文字カードの比較画像を検証する。"""
import os
os.environ.setdefault('WOM08_ROOT','/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v03_20261030')
import subprocess,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom08_produce import ROOT,REPO,read,save,sha,probe
from wom01_quiet_origins import stream_hash
OLD=ROOT.parent/'確認版_v02_20261030';CHANGED={'D_illness','D_novels_1869','D_novels_1892','D_warning','D_bmj','D_summary'}

def specific():
 old=read(OLD/'records/render_shots.json');shots=read(ROOT/'records/render_shots.json');m=read(ROOT/'records/master_timeline.json');checks=[]
 for name in ['content.json','content_en.json','master_timeline.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_cues_en.json','subtitle_cues_ja.json','audio_qc.json']:
  assert sha(ROOT/'records'/name)==sha(OLD/'records'/name);checks.append({'file':name,'v02_byte_identical':True,'sha256':sha(ROOT/'records'/name)})
 assert [(s['key'],s['segment_id'],s['start'],s['end'],s['frames']) for s in shots]==[(s['key'],s['segment_id'],s['start'],s['end'],s['frames']) for s in old]
 assert len(shots)==30 and sum(s['frames'] for s in shots)==10427
 untouched=[];old_motion={x['key']:x['encoded_sha256'] for x in read(OLD/'records/motion_v02.json')['shots']}
 for a,b in zip(old,shots):
  if 'file' in a:assert sha(OLD/a['file'])==a['sha256']
  assert [t['text'] for t in a.get('texts',[])]==[t['text'] for t in b.get('texts',[])]
  if a['key'] not in CHANGED:
   h=sha(OLD/a['encoded_file']);expected=a['original_sha256'] if a['segment_id']=='BRAND' else old_motion[a['key']];assert h==expected;assert sha(ROOT/b['encoded_file'])==h
   if 'file' in a:assert sha(OLD/a['file'])==sha(ROOT/b['file'])==a['sha256']
   untouched.append({'key':a['key'],'v02_intermediate_sha256':h,'identical':True})
  else:assert b['nontext_pixels_identical_to_v02']
 assert len(untouched)==24
 for lang in ['en','ja']:
  a=OLD/f'deliverables/EP008_Tutankhamun_{lang}_v02_1080p30.mp4';b=ROOT/f'deliverables/EP008_Tutankhamun_{lang}_v03_1080p30.mp4';h=stream_hash(a,'a');assert h==stream_hash(b,'a')
  assert sha(a.with_suffix('.srt'))==sha(b.with_suffix('.srt'))
  checks.append({'language':lang,'audio_stream_sha256':h,'v02_audio_identical':True,'srt_sha256':sha(b.with_suffix('.srt')),'v02_srt_byte_identical':True})
  for suffix in ['m4a','wav']:
   a=OLD/f'deliverables/EP008_audio_{lang}.{suffix}';b=ROOT/f'deliverables/EP008_audio_{lang}.{suffix}';assert sha(a)==sha(b)
 thumbnails=[]
 for a in (OLD/'deliverables').glob('*.jpg'):
  b=ROOT/'deliverables'/a.name;assert sha(a)==sha(b);thumbnails.append({'name':a.name,'sha256':sha(b),'v02_byte_identical':True})
 assert len(thumbnails)==5
 c=read(ROOT/'records/contrast_validation.json');assert c['passed'] and c['minimum']>=4.5 and abs(c['enlargement']-69/43)<1e-9
 bases=[s['base_asset'] for s in read(ROOT/'records/visual_manifest.json')['shots'] if s.get('base_asset')];assert len(bases)==len(set(bases))==21
 assert abs(m['brand_intervals']['endcard'][0]-(m['duration_seconds']-10))<1e-8
 save(ROOT/'records/episode_specific_qc.json',{'passed':True,'shot_count':30,'changed_actual_shots':6,'changed_card_groups':5,'preservation_checks':checks,'unchanged_24_shots':untouched,'card_strings_unchanged':True,'card_nontext_pixels_identical_to_v02':True,'thumbnails':thumbnails,'base_assets_each_used_once':bases,'endcard_exact_last_10_seconds':True,'no_additional_generation_purchase_or_post':True,'human_visual_review':'本人・Claudeのv03文字の読みやすさの確認待ち。音声はv02で試聴可。'})
 print('V03 PRESERVATION PASS',flush=True)

def comparison():
 shots=[s for s in read(ROOT/'records/render_shots.json') if s['key'] in CHANGED];frames=[round(s['start']*30)+(s['frames']-1)//2 for s in shots];expr='+'.join(f'eq(n\\,{n})' for n in frames)
 for version,root in [('v02',OLD),('v03',ROOT)]:
  dest=ROOT/f'_work/cards_{version}';dest.mkdir(exist_ok=True)
  src=root/f'deliverables/EP008_Tutankhamun_en_{version}_1080p30.mp4'
  subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-threads','2','-i',str(src),'-vf',f'select={expr},scale=960:540','-fps_mode','passthrough',str(dest/'%02d.png')],check=True)
  assert len(list(dest.glob('*.png')))==6
 font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',24);rows=[]
 for i,s in enumerate(shots,1):
  im=Image.new('RGB',(1920,590),'#18222b');d=ImageDraw.Draw(im)
  d.text((20,8),f'{s["segment_id"]} {s["key"]}  v02 → v03 ／ 同じ中央フレーム {frames[i-1]}',font=font,fill='white')
  im.paste(Image.open(ROOT/f'_work/cards_v02/{i:02d}.png'),(0,45));im.paste(Image.open(ROOT/f'_work/cards_v03/{i:02d}.png'),(960,45));name=f'comparison_v02_v03_{i:02d}_{s["key"]}.jpg';im.save(ROOT/'review'/name,quality=92,optimize=True)
  rows.append({'key':s['key'],'segment':s['segment_id'],'frame':frames[i-1],'file':'review/'+name})
 for batch in range(2):
  im=Image.new('RGB',(1280,1180),'#18222b')
  for j,r in enumerate(rows[batch*3:batch*3+3]):im.paste(Image.open(ROOT/r['file']).resize((1280,393)),(0,j*393))
  im.save(ROOT/f'review/cards_comparison_sheet_{batch+1}.jpg',quality=89,optimize=True)
 save(ROOT/'records/card_comparison.json',{'passed':True,'method':'完成動画を先頭から連続デコードし、同じグローバルフレームを選択。5種類のカード、P10前後半を含む実際の6ショット。','records':rows})
 print('V03 CARD COMPARISON COMPLETE',flush=True)

if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
