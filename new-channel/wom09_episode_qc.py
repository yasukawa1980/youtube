"""Episode-specific request checks and measured tables."""
import csv,json
from collections import Counter,defaultdict
from wom09_visuals import contrast
from PIL import Image
import numpy as np
from wom09_produce import ROOT,REPO,read,save,sha

def main():
 m=read(ROOT/'records/master_timeline.json');shots=read(ROOT/'records/render_shots.json');v=read(ROOT/'records/visual_manifest.json');contr=read(ROOT/'records/contrast.json');audio=read(ROOT/'records/audio_qc.json');subs=read(ROOT/'records/subtitle_validation.json')
 counts=Counter(s['original_asset_id'] for s in shots if 'original_asset_id' in s);assert len(counts)==12 and set(counts.values())=={1}
 requested={'met_202259','R06','met_437394','met_198621','met_247952','met_254876','MYK01','R04','R01','met_341207','met_253376','met_254896'};assert set(counts)==requested
 colors=defaultdict(lambda:{'shots':0,'seconds':0});rows=[]
 for s in shots:
  cls=s.get('color_class','brand');dt=s['frames']/30;colors[cls]['shots']+=1;colors[cls]['seconds']+=dt;rows.append({'key':s['key'],'class':cls,'start':s['start'],'end':s['end'],'seconds':dt})
  if cls=='warm_monochrome':assert dt<=30
 assert colors['color']['shots']==9 and colors['warm_monochrome']['shots']==3
 scaling=[{'key':s['key'],'source_pixels':s['original_pixels'],'crop_pixels':s['crop_pixels'],'initial_scale':s['native_initial_scale'],'max_scale':s['native_max_scale']} for s in shots if s['key'] in ['met_202259','MYK01','met_253376']];assert all(x['max_scale']<=1 for x in scaling)
 maxtext=max(b['bbox'][3] for s in v['shots'] for b in s['text_boxes']);assert maxtext<=700
 quotes={}
 for k,e in [('D_lastline','"Thus held they funeral for Hector tamer of horses."'),('D_gifts','"I fear the Grecians even when they offer gifts."')]:
  q=(ROOT/f'records/{k}_screen_quote.txt').read_text().strip();assert q==e;quotes[k]=q
 assert len(contr['cards'])==9 and all(min(c['foreground_contrast'],c['accent_contrast'])>=4.5 for c in contr['cards'])
 text='\n'.join(b['text'] for s in v['shots'] if s['key'] in requested for b in s['text_boxes']);assert 'Demodocus' not in text and 'とされる' in text
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
 for n in ['content.json','content_en.json']:assert sha(ROOT/'records'/n)==sha(REPO/'new-channel/episodes/EP009_TrojanHorse/records'/n)
 firstshot=shots[0];firstcue=next(c for c in read(ROOT/'records/narration_timeline_en.json')['segments'][0]['cues'] if c['text'].startswith('Yet the Iliad ends'))
 finish=round(firstcue['start']*30);assert f'min(on/{finish},1)' in firstshot['render_config']['filter']
 assert abs(finish/30-firstcue['start'])<1/30
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
 result={'source_video_sha256':sha(ROOT/'deliverables/EP009_TrojanHorse_en_v01_1080p30.mp4'),'passed':True,'content_shots':22,'brand_shots':2,'source_uses':dict(counts),'color_summary':dict(colors),'color_shots':rows,'native_scales':scaling,'opening_zoom_finish_seconds':finish/30,'opening_reference_cue_start':firstcue['start'],'maximum_text_bottom_y':maxtext,'exact_screen_quotes':quotes,'japanese_gaps':gaps,'maximum_japanese_wait_seconds':max(x['seconds'] for x in gaps),'opening_frames':first,'source_images_visually_inspected':True,'visual_review_notes':'Homer bust only; cameo including full mount; prints retain small figures without closeups; Mykonos lower massacre register absent. Final continuous contact sheets reviewed separately.','human_full_listening':False,'reading_replacements':read(ROOT/'records/reading_replacements.json'),'unchanged_scripts':True,'ai_images_or_video':False,'paid_generation':False}
 save(ROOT/'records/episode_specific_qc.json',result)
 for name,data in [('color_shots',rows),('native_scales',scaling),('contrast',[{k:c[k] for k in ['key','background','foreground','foreground_contrast','accent','accent_contrast','max_text_y']} for c in contr['cards']])]:
  with (ROOT/f'deliverables/EP009_{name}.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 print('EPISODE QC PASSED',dict(colors),'MAX JA GAP',result['maximum_japanese_wait_seconds'],flush=True)
if __name__=='__main__':main()
