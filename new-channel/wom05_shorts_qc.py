"""EP005 Shorts verification with the established full-frame/glyph checks."""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import wom_shorts_qc as legacy
from wom05_shorts import ROOT,REQUEST,SR,FPS,read,save,sha,ff,levels
from wom01_quiet_origins import stream_hash
legacy.ROOT=ROOT
legacy.REQUEST=REQUEST

def verify():
 rows=[s for s in read(ROOT/'records/shorts.json')['shorts'] if s['id'] in ['T1','T2','T3']];shots=read(ROOT/'records/render_shots.json');usage=[];media=[];audio=read(ROOT/'records/audio_qc.json');assert audio['passed'];assert read(ROOT/'records/narration.json')['request_sha256']==sha(REQUEST)
 for episode in ['EP005']:
  members={s['id'] for s in rows if s['episode']==episode};sources=[s['source']['sha256'] for s in shots if s['short_id'] in members];assert len(sources)==len(set(sources))
 for s in rows:
  for phrase in ['of 720,','in 637','in 1815,']:
   if phrase in s['text']:assert any(phrase in g['text'] for g in s['caption_groups'])
  id=s['id'];groups=[g for g in shots if g['short_id']==id];assert sum(g['frames'] for g in groups)==s['frames']
  for a,b in zip(groups,groups[1:]):assert a['end_frame']==b['start_frame']
  for g in groups:
   assert g['frames']/FPS>=1.5
   assert sha(Path(g['source']['path']))==g['source']['sha256'];assert sha(Path(g['encoded_file']))==g['encoded_sha256'];usage.append({'short_id':id,'episode':s['episode'],'asset_id':g['asset_id'],'start_seconds':g['start_frame']/FPS,'end_seconds':g['end_frame']/FPS,'use_count':1,'source_sha256':g['source']['sha256']})
   assert all(140<=t['bbox'][1]<t['bbox'][3]<=260 for t in g['texts'])
  p=ROOT/f'deliverables/QO_short_{s["episode"]}_{id}_v01.mp4';ff(['-i',p,'-f','null','-']);info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(t for t in info['streams'] if t['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',s['frames']);assert abs(float(info['format']['duration'])-s['frames']/FPS)<.04
  pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert v['time_base']=='1/15360' and pts==list(range(0,s['frames']*512,512))
  q=levels(p);assert abs(float(q['input_i'])+14)<=.15 and float(q['input_tp'])<=-1;assert stream_hash(p,'a')==stream_hash(ROOT/f'audio/{id}_final.m4a','a')
  voice,sr=sf.read(ROOT/f'audio/{id}_normalized.wav',dtype='float32');step=round(.01*sr);power=np.array([np.sqrt(np.mean(voice[i:i+step]**2)) for i in range(0,len(voice),step)]);onset=float(np.where(power>10**(-50/20))[0][0]*.01);assert onset<=.3
  aq=next(a for a in audio['reports'] if a['id']==id);assert abs(aq['bgm_during_narration_dbfs']+33.5)<.001
  media.append({'id':id,'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'frames':s['frames'],'duration_seconds':float(info['format']['duration']),'video_duration_seconds':s['duration_seconds'],'lufs':float(q['input_i']),'true_peak_dbtp':float(q['input_tp']),'voice_onset_normalized_stem_seconds':onset,'voice_onset_threshold_dbfs':-50,'voice_onset_window_seconds':.01,'bgm_during_narration_dbfs':aq['bgm_during_narration_dbfs'],'full_decode':True,'exact_pts_30fps':True,'audio_stream_matches_measured_m4a':True,'cta_seconds':s['duration_seconds']-s['cta_start']});print('VERIFIED',id,q['input_i'],q['input_tp'],onset,flush=True)
 assert len(usage)==7
 with (ROOT/'deliverables/asset_usage.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(usage[0]));w.writeheader();w.writerows(usage)
 save(ROOT/'records/asset_usage.json',{'passed':True,'unique_sources':7,'rows':usage,'same_source_not_repeated_within_episode':True})
 save(ROOT/'records/media_qc.json',{'passed':True,'media':media,'request_sha256':sha(REQUEST),'render_shots_sha256':sha(ROOT/'records/render_shots.json'),'audio_qc_sha256':sha(ROOT/'records/audio_qc.json'),'human_full_listening':False})



def glyphs():
 import imageio_ffmpeg
 rows=[s for s in read(ROOT/'records/shorts.json')['shorts'] if s['id'] in ['T1','T2','T3']];pages=read(ROOT/'records/caption_manifest.json');checks=[]
 for s in rows:
  id=s['id'];group=[p for p in pages if p['short_id']==id];folder=ROOT/f'_work/glyph_{id}';folder.mkdir(exist_ok=True);ns=[(p['start_frame']+p['end_frame']-1)//2 for p in group];expr='+'.join(f'eq(n\\,{n})' for n in ns)
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-f','lavfi','-i',f'color=c=black:size=1080x1920:rate=30:duration={s["duration_seconds"]:.9f}','-vf',f"ass='{ROOT}/_work/{id}.ass',select={expr}",'-fps_mode','passthrough','-pix_fmt','rgb24',str(folder/'%03d.png')],check=True)
  files=sorted(folder.glob('*.png'));assert len(files)==len(group)
  for p,f in zip(group,files):
   a=np.array(Image.open(f));ys,xs=np.where(a.max(axis=2)>10);assert len(xs);bbox=[int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1]
   assert bbox[0]>=80 and bbox[2]<=880 and bbox[1]>=1150 and bbox[3]<=1450,(id,p['text'],bbox)
   assert len(p['lines'])<=2 and all(len(line.split())<=5 for line in p['lines']);checks.append({'short_id':id,'page':p['page'],'text':p['text'],'glyph_bbox':bbox,'passed':True,'brand':p.get('brand',False)})
  spoken=' '.join(p['text'] for p in group if not p.get('brand'));assert spoken==s['text'];print('GLYPHS',id,len(group),flush=True)
 save(ROOT/'records/subtitle_qc.json',{'passed':True,'method':'Every caption page and CTA rendered with the same imageio FFmpeg/libass, ASS file, fonts, resolution and styles as the final MP4. Bounds include outlines and shadows (RGB maximum >10 over black).','caption_manifest_sha256':sha(ROOT/'records/caption_manifest.json'),'checks':checks,'text_matches_requested_script':True})


def frames():
 rows=[s for s in read(ROOT/'records/shorts.json')['shorts'] if s['id'] in ['T1','T2','T3']];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16);records=[]
 for s in rows:
  stem=f'QO_short_{s["episode"]}_{s["id"]}_v01';video=ROOT/f'deliverables/{stem}.mp4';times=list(np.arange(0,s['duration_seconds'],2));items=[]
  mid=ROOT/f'review/{stem}_mid.jpg';ff(['-ss',s['duration_seconds']/2,'-i',video,'-frames:v',1,'-vf','scale=720:1280','-q:v',3,mid])
  sheet=Image.new('RGB',(1280,math.ceil(len(times)/5)*480),'#0c1820');d=ImageDraw.Draw(sheet)
  for i,t in enumerate(times):
   frame=ROOT/f'_work/{stem}_{i:02}.jpg';ff(['-ss',float(t),'-i',video,'-frames:v',1,'-vf','scale=256:455','-q:v',3,frame]);x=i%5*256;y=i//5*480;sheet.paste(Image.open(frame),(x,y));d.text((x+8,y+456),f'{s["id"]} {t:.0f}s',font=font,fill='#f4efdf');items.append(float(t))
  out=ROOT/f'review/{stem}_every2s.jpg';sheet.thumbnail((1280,1280));sheet.save(out,quality=88,optimize=True);assert max(sheet.size)<=1280 and out.stat().st_size<1000000;records.append({'id':s['id'],'video_sha256':sha(video),'midpoint_seconds':s['duration_seconds']/2,'midpoint_jpg':mid.name,'every_2s_jpg':out.name,'sample_seconds':items});print('FRAMES',s['id'],len(times),flush=True)
 save(ROOT/'records/frame_review.json',{'shorts':records,'all_midpoints_and_every_2_seconds':True})


import math
from PIL import Image,ImageDraw,ImageFont
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['motion','glyphs','verify','frames']);a=p.parse_args()
 (legacy.motion if a.stage=='motion' else globals()[a.stage])()
