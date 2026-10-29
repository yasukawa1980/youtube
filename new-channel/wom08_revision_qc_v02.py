"""第8話v02の保持条件・全ショット比較・実測輝度を検査する。"""
import os
os.environ['WOM08_ROOT']='/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v02_20261030'
import csv,subprocess,math,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
from wom08_produce import ROOT,REPO,read,save,sha,probe,OP,END
from wom01_quiet_origins import stream_hash
OLD=ROOT.parent/'確認版_v01_20261029';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'

def specific():
 m=read(ROOT/'records/master_timeline.json');shots=read(ROOT/'records/render_shots.json');vis=read(ROOT/'records/visual_manifest.json');files=[]
 for name in ['content.json','content_en.json','master_timeline.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_cues_en.json','subtitle_cues_ja.json','audio_qc.json']:
  assert sha(ROOT/'records'/name)==sha(OLD/'records'/name);files.append({'name':name,'sha256':sha(ROOT/'records'/name),'v01_byte_identical':True})
 for lang in ['en','ja']:
  src=OLD/f'deliverables/EP008_Tutankhamun_{lang}_v01_1080p30.mp4';dst=ROOT/f'deliverables/EP008_Tutankhamun_{lang}_v02_1080p30.mp4';h=stream_hash(src,'a');assert h==stream_hash(dst,'a')
  a=src.with_suffix('.srt');b=dst.with_suffix('.srt');assert sha(a)==sha(b)
  files.append({'language':lang,'audio_stream_sha256':h,'v01_audio_identical':True,'srt_sha256':sha(b),'v01_srt_byte_identical':True})
 for path in [OP,END]:assert read(ROOT/'records/request.json')['brand_sha256'][str(path)]==sha(path)
 oldshots=read(OLD/'records/render_shots.json')
 for key in ['opening','endcard','V01']:
  a=next(x for x in oldshots if x['key']==key);b=next(x for x in shots if x['key']==key);assert a['start']==b['start'] and a['end']==b['end']
  assert sha(OLD/a['encoded_file'])==sha(ROOT/b['encoded_file'])
 assert len(shots)==30 and sum(s['frames'] for s in shots)==10427
 bases=[s['base_asset'] for s in vis['shots'] if s.get('base_asset')];assert len(bases)==len(set(bases))==21
 for sid,expected in {'P05':['B183','C01','B299','B300'],'P09':['B313','C02','B312'],'P10':['D_novels_1869','D_novels_1892'],'P11':['D_warning','C03'],'P13':['D_summary','C04']}.items():assert [s['key'] for s in shots if s['segment_id']==sid]==expected
 c03=next(s for s in shots if s['key']=='C03');assert any('別の墓' in t['text'] for t in c03['texts']) and any('NOT THE ONE QUOTED' in t['text'] for t in c03['texts'])
 assert abs(m['brand_intervals']['endcard'][0]-(m['duration_seconds']-10))<1e-8
 # Paragraph boundaries and copied mix remain byte-identical to the verified v01.
 report={'passed':True,'shot_count':30,'base_assets_each_used_once':bases,'preservation_checks':files,'brand_and_candle_original_intermediates_sha_identical':True,'endcard_exact_last_10_seconds':True,'C03_explicit_other_tomb':True,'no_new_generation_or_spend':True,'human_full_listening':'音声v01と同一。本人によるv02全編視聴待ち。','source_usage':[{k:s[k] for k in ['key','segment_id','start','end']} for s in shots]}
 save(ROOT/'records/episode_specific_qc.json',report);print('V02 PRESERVATION PASS',flush=True)

def comparison():
 shots=read(ROOT/'records/render_shots.json');centers=[round(s['start']*30)+(s['frames']-1)//2 for s in shots];expr='+'.join(f'eq(n\\,{n})' for n in centers);results={}
 for version,root in [('v01',OLD),('v02',ROOT)]:
  src=root/f'deliverables/EP008_Tutankhamun_en_{version}_1080p30.mp4';dest=ROOT/f'_work/compare_{version}';dest.mkdir(exist_ok=True)
  subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-threads','2','-i',str(src),'-vf',f'select={expr},scale=960:540','-fps_mode','passthrough',str(dest/'%03d.jpg')],check=True)
  # Whole-stream grayscale luma, all decoded frames; no seeking or sparse averaging.
  p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-vf','scale=160:90:flags=area,format=gray','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','pipe:1'],stdout=subprocess.PIPE)
  vals=[]
  for s in shots:
   values=[]
   for _ in range(s['frames']):
    data=p.stdout.read(14400);assert len(data)==14400;values.append(float(np.frombuffer(data,np.uint8).mean()))
   vals.append(float(np.mean(values)))
  assert not p.stdout.read(1) and p.wait()==0;results[version]=vals;print('LUMA',version,len(vals),flush=True)
 rows=[];f=ImageFont.truetype(JA,18)
 for i,s in enumerate(shots):
  old,new=results['v01'][i],results['v02'][i];r=dict(shot=i+1,segment=s['segment_id'],key=s['key'],start=s['start'],end=s['end'],frames=s['frames'],v01_mean_luma=old,v02_mean_luma=new,increase_percent=(new/old-1)*100,center_frame=centers[i]);rows.append(r)
  im=Image.new('RGB',(1280,395),'#18222b');d=ImageDraw.Draw(im)
  for j,ver in enumerate(['v01','v02']):im.paste(Image.open(ROOT/f'_work/compare_{ver}/{i+1:03d}.jpg').resize((640,360)),(j*640,30))
  d.text((10,4),f'{i+1:02d} {s["segment_id"]} {s["key"]}  v01 → v02  同じ時刻の中央フレーム {centers[i]}',font=f,fill='#f4efdf');im.save(ROOT/f'review/compare_{i+1:02d}_{s["key"]}.jpg',quality=87,optimize=True)
 for batch in range(math.ceil(len(shots)/4)):
  im=Image.new('RGB',(1280,1580),'#18222b')
  for j,s in enumerate(shots[batch*4:batch*4+4]):im.paste(Image.open(ROOT/f'review/compare_{batch*4+j+1:02d}_{s["key"]}.jpg'),(0,j*395))
  im.save(ROOT/f'review/comparison_sheet_{batch+1:02d}.jpg',quality=85,optimize=True)
 with (ROOT/'deliverables/EP008_luminance_v01_v02.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 save(ROOT/'records/luminance_comparison.json',{'method':'完成動画を先頭から連続デコード。全フレームを160×90面積平均縮小した8bitグレーの全画面平均。v02の各ショットの同じ区間でv01も測定。カラー差し替えは色調補正の目標値の対象外。','shots':rows})
 print('COMPARISON COMPLETE',flush=True)

def thumbnails():
 dest=REPO/'new-channel/サムネ確認用/wom08';files=[];records=[];font='/System/Library/Fonts/Supplemental/Georgia Bold.ttf';sans='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
 for key,title,asset in [('A','NOT IN THE TOMB','B286'),('B','WHO STARTED IT?','B157'),('C','THE CURSE?','B170'),('D','NOT IN THE TOMB','C01')]:
  if asset=='C01':
   a=next(a for a in read(ROOT/'records/color_assets_v02.json')['assets'] if a['id']=='C01');im=Image.open(a['original_path']).convert('RGB');im=im.crop((round(im.width*.45),0,im.width,im.height))
  else:im=Image.open(ROOT/f'assets/{asset}_toned.png').convert('RGB')
  im=ImageOps.fit(im,(1280,720),Image.Resampling.LANCZOS,centering=(.65 if key=='D' else .5,.5));arr=np.asarray(im).astype(float);y=np.arange(720);opacity=.60*np.exp(-y/135)+.38*np.exp(-(719-y)/70);arr*=1-opacity[:,None,None];im=Image.fromarray(np.uint8(arr.clip(0,255)));d=ImageDraw.Draw(im);size=85
  while d.textlength(title,font=ImageFont.truetype(font,size))>1170:size-=1
  ft=ImageFont.truetype(font,size);d.text(((1280-d.textlength(title,font=ft))/2,22),title,font=ft,fill='#fff6dc',stroke_width=2,stroke_fill='#231b16');d.text((55,652),'QUIET ORIGINS',font=ImageFont.truetype(sans,28),fill='#f2d09a',stroke_width=1,stroke_fill='#231b16')
  p=dest/f'wom08_サムネ{key}_v02_20261030.jpg';im.save(p,quality=92,optimize=True);assert p.stat().st_size<1000000;shutil.copy2(p,ROOT/'deliverables'/p.name);files.append(p);records.append({'option':key,'file':str(p),'source':asset,'sha256':sha(p),'bytes':p.stat().st_size,'size':[1280,720]})
 sheet=Image.new('RGB',(752,140),'#18222b');d=ImageDraw.Draw(sheet)
 for i,p in enumerate(files):x=16+184*i;d.text((x,8),chr(65+i),fill='white');sheet.paste(Image.open(p).resize((168,94),Image.Resampling.LANCZOS),(x,30))
 p=dest/'wom08_サムネ168px比較_v02_20261030.jpg';sheet.save(p,quality=94);shutil.copy2(p,ROOT/'deliverables'/p.name);save(ROOT/'records/thumbnail_qc.json',{'outputs':records,'comparison':str(p),'human_choice':'pending'})
 print('V02 THUMBNAILS COMPLETE',flush=True)

if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
