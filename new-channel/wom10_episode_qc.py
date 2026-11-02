"""Episode-specific request checks and measured tables."""
import csv,json
from collections import Counter,defaultdict
from wom10_visuals import contrast
from PIL import Image
import numpy as np
from wom10_produce import ROOT,REPO,read,save,sha

def main():
 m=read(ROOT/'records/master_timeline.json');shots=read(ROOT/'records/render_shots.json');v=read(ROOT/'records/visual_manifest.json');contr=read(ROOT/'records/contrast.json');audio=read(ROOT/'records/audio_qc.json');subs=read(ROOT/'records/subtitle_validation.json')
 counts=Counter(s['original_asset_id'] for s in shots if 'original_asset_id' in s);assert len(counts)==11 and set(counts.values())=={1}
 requested={'K01a','K06a','K05b','K04a','K05c','K09b','K06b','K03a','K09a','K07b','K10a'};assert set(counts)==requested
 colors=defaultdict(lambda:{'shots':0,'seconds':0});rows=[]
 for s in shots:
  cls=s.get('color_class','brand');dt=s['frames']/30;colors[cls]['shots']+=1;colors[cls]['seconds']+=dt;rows.append({'key':s['key'],'class':cls,'start':s['start'],'end':s['end'],'seconds':dt})
  if cls=='warm_monochrome':assert dt<=30
 assert colors['color']['shots']==8 and colors['warm_monochrome']['shots']==3
 scaling=[{'key':s['key'],'source_pixels':s['original_pixels'],'crop_pixels':s['crop_pixels'],'initial_scale':s['native_initial_scale'],'max_scale':s['native_max_scale']} for s in shots if 'original_asset_id' in s];assert all(x['max_scale']<=1 for x in scaling)
 maxtext=max(b['bbox'][3] for s in v['shots'] for b in s['text_boxes']);assert maxtext<=700
 quote=' '.join(t['text'] for c in contr['cards'] if c['key']=='D_grimm' for t in c['text_boxes'] if t['text'].startswith(('"I can','in heathen')))
 assert quote=='"I can well imagine that even in heathen times..."';quotes={'D_grimm':quote}
 assert len(contr['cards'])==6 and all(min(c['foreground_contrast'],c['accent_contrast'])>=4.5 for c in contr['cards'])
 assert all(c['minimum_major_glyph_height']>=60 for c in contr['cards'])
 summary=next(c for c in contr['cards'] if c['key']=='D_summary');assert summary['minimum_box_padding']>=18
 assert not any(c.isdigit() for c in ' '.join(t['text'] for t in summary['text_boxes'] if 790<t['bbox'][0]<1130))
 for key,forbidden in [('K09a','Krampus'),('K04a','window')]:
  row=next(s for s in v['shots'] if s['key']==key);assert forbidden not in ' '.join(b['text'] for b in row['text_boxes'])
 ja=read(ROOT/'records/narration_timeline_ja.json');gaps=[]
 for s in ja['segments']:
  for a,b in zip(s['cues'],s['cues'][1:]):gaps.append({'after':a['id'],'before':b['id'],'seconds':b['start']-a['end']})
  gaps.append({'after':s['cues'][-1]['id'],'before':'segment end','seconds':s['end']-s['cues'][-1]['end']})
 assert max(x['seconds'] for x in gaps)<=3
 for l in ['en','ja']:
  assert subs[l]['script_matches'] and subs[l]['min_seconds']>=1.4-1e-6
  levels=audio['languages'][l]['levels'];assert abs(float(levels['input_i'])+16)<.3 and float(levels['input_tp'])<=-1
  assert abs(audio['languages'][l]['voice_minus_bgm_db']-18)<.01
 assert m['brand_intervals']['endcard'][0]==m['duration_seconds']-10
 assert m['brand_intervals']['opening'][0]==m['segments'][1]['end']
 for n in ['content.json','content_en.json']:assert sha(ROOT/'records'/n)==sha(REPO/'new-channel/episodes/EP010_Krampus/records'/n)
 encoded_contrast=[]
 for i,shot in enumerate(shots):
  if not shot['key'].startswith('D_'):continue
  path=ROOT/f'_work/continuous_en/{i*3+2:03d}.png';arr=np.asarray(Image.open(path).convert('RGB'))
  bg=tuple(arr[500,10]);regions=[]
  for box in shot['text_boxes']:
   x0,y0,x1,y1=box['bbox']
   if y0<110:continue
   part=arr[int(y0*2/3):int(np.ceil(y1*2/3)),int(x0*2/3):int(np.ceil(x1*2/3))];regions.append(part.reshape(-1,3))
  region=np.concatenate(regions);dark=region[region.mean(axis=1)<110];assert len(dark)>0
  fg=Counter(map(tuple,dark.tolist())).most_common(1)[0][0]
  hexcolor=lambda c:'#'+''.join(f'{int(v):02x}' for v in c)
  ratio=contrast(hexcolor(bg),hexcolor(fg));assert ratio>=4.5
  encoded_contrast.append({'key':shot['key'],'background':hexcolor(bg),'dominant_dark_text':hexcolor(fg),'ratio':ratio,'source':str(path.relative_to(ROOT))})
 save(ROOT/'records/encoded_card_contrast.json',{'passed':True,'method':'Dominant dark RGB within recorded text bounding boxes and empty background RGB in continuous-decode 1280px PNG; decorative box borders and arrows excluded; antialiased edge colors are not nominal text colors','cards':encoded_contrast})
 first=[]
 for l in ['en','ja']:
  ims=[np.asarray(Image.open(ROOT/f'review/opening_{l}_{i:02d}.jpg')).astype(float) for i in range(1,5)];changes=[float(np.abs(b-a).mean()) for a,b in zip(ims,ims[1:])];assert all(x>0 for x in changes);assert min(a.mean() for a in ims)>30;first.append({'language':l,'mean_frame_brightness':[float(a.mean()) for a in ims],'1sec_adjacent_image_mad':changes})
 result={'source_video_sha256':sha(ROOT/'deliverables/EP010_Krampus_en_v01_1080p30.mp4'),'passed':True,'content_shots':18,'brand_shots':2,'source_uses':dict(counts),'color_summary':dict(colors),'color_shots':rows,'native_scales':scaling,'maximum_text_bottom_y':maxtext,'exact_screen_quotes':quotes,'japanese_gaps':gaps,'maximum_japanese_wait_seconds':max(x['seconds'] for x in gaps),'opening_frames':first,'source_images_visually_inspected':True,'visual_review_notes':'K03a restricted to horns, head and upper branches, without enlarged child or full tongue. K09b excludes left weapon; K07b color chart cropped out. K01a retains the whole postcard; figures remain small. Thumbnails and final contact sheets reviewed separately.','human_full_listening':False,'reading_replacements':read(ROOT/'records/reading_replacements.json'),'unchanged_scripts':True,'ai_images_or_video':False,'paid_generation':False}
 save(ROOT/'records/episode_specific_qc.json',result)
 for name,data in [('color_shots',rows),('native_scales',scaling),('contrast',[{k:c[k] for k in ['key','foreground_contrast','accent_contrast','minimum_major_glyph_height','minimum_box_padding','no_box']} for c in contr['cards']])]:
  with (ROOT/f'deliverables/EP010_{name}.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 print('EPISODE QC PASSED',dict(colors),'MAX JA GAP',result['maximum_japanese_wait_seconds'],flush=True)
if __name__=='__main__':main()
