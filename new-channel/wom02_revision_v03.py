"""EP002 v03: each source is confined to one shot; v02 audio/SRT/segments frozen."""
import argparse,copy,json,os,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
os.environ['WOM02_ROOT']=os.environ.get('WOM02_V03_ROOT','/Users/ryo/Desktop/新チャンネル/EP002_Halloween/確認版_v03_20261022')
os.environ['WOM02_V02_ROOT']=os.environ['WOM02_ROOT']
from wom02_produce import ROOT,REPO,MEDIA,read,save,sha,ff,probe
from wom01_quiet_origins import stream_hash
from wom02_revision_v02 import camera
PREV=ROOT.parent/'確認版_v02_20261022'
PLAN={
 'H01':['R01','A02'],'H02':['N01','N02'],'H03':['R04','D_texts'],
 'H04':['R05','R06'],'H05':['D_story_record','N03'],'H06':['A05_detail','N04'],
 'H07':['A06_detail','N05'],'H08':['N06','D_season'],'H09':['A04_detail','N07'],
 'H10':['A03_detail','N08'],'H11':['D_calendar','N09'],'H12':['A01','R03'],
 'H13':['N10','N11'],'H14':['R02','D_jack'],'H15':['N18','N12','N13'],
 'H16':['N14','N15','A07'],'H17':['D_layers','N16'],'H18':['N17'],'H19':['credits']}

def prepare():
 for d in ['records','deliverables','assets','review','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 for name in ['content.json','content_en.json','master_timeline.json','source_assets.json','subtitle_cues_en.json','subtitle_cues_ja.json','narration_timeline_en.json','narration_timeline_ja.json','chapters.json','reading_replacements.json','pronunciation_locations.json','audio_qc.json','runtime.json']:
  src=PREV/'records'/name;dst=ROOT/'records'/name
  if dst.exists():assert sha(src)==sha(dst)
  else:shutil.copy2(src,dst)
 preserved=[]
 for p in (PREV/'deliverables').iterdir():
  if p.suffix in ['.srt','.m4a','.jpg','.txt'] and p.name!='SHA256SUMS_shared.txt':
   dst=ROOT/'deliverables'/p.name.replace('_v02_','_v03_');shutil.copy2(p,dst);assert sha(p)==sha(dst);preserved.append({'source':str(p),'copy':str(dst),'sha256':sha(p)})
 registry=REPO/'new-channel/episodes/EP002_Halloween/records'
 for tmp,name in [('wom02_v03_stills.json','new_stills_v03.json'),('wom02_v03_videos.json','new_videos_v03.json')]:
  source=registry/name if (registry/name).exists() else Path('/private/tmp')/tmp;save(ROOT/'records'/name,read(source))
 save(ROOT/'records/ai_images.json',read(PREV/'records/ai_images.json')+read(ROOT/'records/new_stills_v03.json'))
 n07=MEDIA/'N07_Met_All_Saints_31.67.9.jpg'
 save(ROOT/'records/new_sources_v03.json',[{'id':'N07','title':'All Saints','artist':'Greek Painter','date_display':'possibly 18th century','object_number':'31.67.9','object_id':436578,'original_local_path':str(n07),'sha256':sha(n07),'work_url':'https://www.metmuseum.org/art/collection/search/436578','license_url':'https://www.metmuseum.org/policies/image-resources','license':'Public Domain / CC0 Open Access','isPublicDomain':True,'download_url':'https://images.metmuseum.org/CRDImages/ep/original/ep31.67.9.bw.R.jpg','checked_date':'2026-10-22','note':'Later icon used as an illustration of All Saints; not evidence for the date of the feast.'}])
 save(ROOT/'records/preservation.json',{'files':preserved,'master_sha256':sha(PREV/'records/master_timeline.json'),'previous_root':str(PREV)})
 for a in read(ROOT/'records/new_videos_v03.json'):
  assert sha(Path(a['local_path']))==a['sha256'];ff(['-ss',5,'-i',a['local_path'],'-frames:v',1,ROOT/f'assets/{a["id"]}_poster.png'])
 print('PREPARED',ROOT,flush=True)

def timings():
 old=read(PREV/'records/render_shots.json');out=[]
 for sid,keys in PLAN.items():
  group=[s for s in old if s['segment_id']==sid];start=round(group[0]['start']*30);end=round(group[-1]['end']*30)
  # Keep the 1938 photograph after both 1927 sentences; split the earlier hold at 307.3667s.
  bounds=[start,9221,9540,end] if sid=='H16' else [start,8600,8740,end] if sid=='H15' else [round(start+(end-start)*i/len(keys)) for i in range(len(keys)+1)]
  for i,key in enumerate(keys):out.append({'segment_id':sid,'key':key,'start':bounds[i]/30,'end':bounds[i+1]/30,'frames':bounds[i+1]-bounds[i],'segment_shot':i+1})
  if sid=='H02':out.extend(s for s in old if s['segment_id']=='BRAND' and s['key']=='opening')
 out.extend(s for s in old if s['segment_id']=='BRAND' and s['key']=='endcard');assert sum(s['frames'] for s in out)==11930
 for a,b in zip(out,out[1:]):assert round(a['end']*30)==round(b['start']*30)
 return out

def brand():
 from wom02_v02_qc import motion_stats
 state=ROOT/'records/brand_revision_v03.json'
 if state.exists():
  prior=read(state)
  if all(sha(ROOT/s['encoded_file'])==s['output_sha256'] and sha(PREV/next(t['encoded_file'] for t in read(PREV/'records/render_shots.json') if t['key']==s['key']))==s['source_encoded_sha256'] for s in prior['records']):
   print('BRAND CACHED',flush=True);return
 records=[]
 for s in read(PREV/'records/render_shots.json'):
  if s['segment_id']!='BRAND':continue
  key=s['key'];image=ROOT/f'assets/brand_{key}_v03.png';out=ROOT/f'_work/render/brand_{key}_v03.mp4';ff(['-ss',(s['end']-s['start'])/2,'-i',PREV/s['encoded_file'],'-frames:v',1,image]);filt=camera(s['frames'],[0,1080])
  ff(['-loop',1,'-framerate',30,'-i',image,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out])
  q=motion_stats(out,[200,200,1520,480]);assert q['p95_over_median']<=2.5;records.append({**s,'encoded_file':str(out.relative_to(ROOT)),'poster':str(image.relative_to(ROOT)),'source_encoded_sha256':sha(PREV/s['encoded_file']),'poster_sha256':sha(image),'output_sha256':sha(out),'motion':q,'change':'Existing design at its midpoint, continuous 3% subpixel zoom for all-shot motion criterion; episode-only derivative.'});print('BRAND',key,q['p95_over_median'],flush=True)
 save(state,{'records':records,'shared_brand_sources_modified':False,'audio_unchanged':True,'reason':'User v03 condition applies p95/median<=2.5 to every shot.'})

def visuals():
 import wom02_visuals as v
 def header(im,label='',source=''):
  ImageDraw.Draw(im).rectangle((0,0,1920,109),fill=v.BG);v.text(im,(92,18),'QUIET ORIGINS  /  EP002',28,v.GOLD)
  if label:
   w=ImageDraw.Draw(im).textlength(label,font=v.font(27,label));v.text(im,(1820-w,21),label,27,v.GOLD)
  if source:v.text(im,(92,72),source,23,v.MUTED)
 v.header=header
 def panel(im,art,box):
  x,y,w,h=box;z=min(w/art.width,h/art.height,1.5);size=(round(art.width*z),round(art.height*z));a=art.resize(size,Image.Resampling.LANCZOS);p=(x+(w-a.width)//2,y+(h-a.height)//2);im.paste(a,p);v.BOXES.append([*p,p[0]+a.width,p[1]+a.height]);return z
 v.panel=panel
 v.SOURCES['A07']='Library of Congress • Dorothea Lange • 1938 • California, USA｜米国カリフォルニア • LC-USF34-018556-D'
 v.images['N07']=Image.open(MEDIA/'N07_Met_All_Saints_31.67.9.jpg').convert('RGB');v.SOURCES['N07']='The Met • All Saints • Greek Painter, possibly 18th c. • 31.67.9 • CC0';v.LABEL['N07']='MUSEUM OBJECT｜博物館資料'
 videos={a['id']:a for a in read(ROOT/'records/new_videos_v03.json')}
 for key in videos:v.images[key]=Image.open(ROOT/f'assets/{key}_poster.png').convert('RGB')
 records=[]
 for shot in timings():
  if shot['segment_id']=='BRAND':continue
  key=shot['key'];base=key.replace('_detail','');v.TEXT=[];v.BOXES=[];extra={}
  if base in v.images:
   art=v.images[base];im=v.background(art)
   if key.endswith('_detail'):
    panel(im,art,(80,110,860,820));crop=v.CROPS[base];piece=art.crop(tuple(round(a*(art.width if i%2==0 else art.height)) for i,a in enumerate(crop)));panel(im,piece,(980,110,860,820))
   else:panel(im,art,(80,110,1760,820))
   generated=base.startswith('R') or base.startswith('N') and base!='N07';label='AI RECONSTRUCTION｜AIによる再現' if generated else v.LABEL[base];source=v.SOURCES.get(base,'')
   header(im,label,source);extra={'base_asset':base,'label':label,'source':source,'generated':generated,'camera_band':[110,930]}
   if base in videos:
    extra['video_asset']=videos[base]['local_path'];extra['video_sha256']=videos[base]['sha256'];extra['video_take']=videos[base].get('take',1)
    if base=='N12':extra['video_excerpt_realtime']=True
  elif key=='N04':
   im=Image.new('RGB',(1920,1080),v.BG);header(im,'SCHEMATIC｜模式図','Diagram by Quiet Origins • arrangement only; not a transcription｜配列の模式図・翻刻ではない');d=ImageDraw.Draw(im)
   for col in range(13):
    x=145+col*126;selected=col==6;d.rounded_rectangle((x,190,x+98,660),12,fill='#554b30' if selected else '#20343e',outline=v.GOLD if selected else '#51616a',width=4 if selected else 2)
    for row in range(15):d.line((x+19,226+row*27,x+79,226+row*27),fill=v.GOLD if selected else '#8b999d',width=2)
   extra={'diagram':True,'base_asset':None,'source':'Native schematic by Quiet Origins','label':'SCHEMATIC｜模式図','camera_band':[110,700]}
  elif key=='credits':
   im=Image.new('RGB',(1920,1080),v.BG);header(im);rows=[('English','Kokoro / Heart (af_heart)'),('日本語','VOICEVOX:冥鳴ひまり'),('Collections','The Met • Library of Congress • NYPL'),('Collections','Wellcome Collection • Wikimedia / Ruthven (CC0)'),('AI stills','OpenAI image_gen • R01–R06; N02,03,05,08,10,11,13–15,18'),('AI video','Kling AI 3.0 • N01,06,09,12,16,17'),('Diagrams','Quiet Origins • N04 and D_*'),('Music','Original ambient score • Quiet Origins')]
   for i,(a,b) in enumerate(rows):v.text(im,(130,170+i*62),a,27,v.GOLD);v.text(im,(400,170+i*62),b,26,v.IVORY)
   extra={'diagram':True,'base_asset':None,'source':'','label':'','camera_band':[110,700]}
  else:
   im,rec=v.compose(key);extra={k:rec[k] for k in ['base_asset','source','label']};extra.update(diagram=True,camera_band=[110,700])
  path=ROOT/f'assets/{shot["segment_id"]}_{shot["segment_shot"]:02}_{key}.png';im.save(path)
  texts=copy.deepcopy(v.TEXT);assert max(t['bbox'][3] for t in texts)<=700
  if base in v.images or key=='N04':assert max(t['bbox'][3] for t in texts)<100
  records.append({**shot,**extra,'asset_id':base,'file':str(path.relative_to(ROOT)),'sha256':sha(path),'texts':texts,'art_boxes':copy.deepcopy(v.BOXES)})
 assert len({s['asset_id'] for s in records})==len(records)
 save(ROOT/'records/visual_manifest.json',{'shots':records,'one_shot_per_asset':True,'foreground_max_box':[80,110,1840,930],'maximum_image_scale':1.5})
 print('VISUALS',len(records),'unique assets',flush=True)

def pictures(only=''):
 manifest=iter(read(ROOT/'records/visual_manifest.json')['shots']);parts=[];records=[];brands=read(ROOT/'records/brand_revision_v03.json')['records'];prior=read(ROOT/'records/render_shots.json') if (ROOT/'records/render_shots.json').exists() else []
 for i,s in enumerate(timings()):
  if s['segment_id']=='BRAND':
   if only:continue
   b=next(b for b in brands if b['key']==s['key']);dst=ROOT/b['encoded_file'];assert sha(dst)==b['output_sha256'];parts.append(dst);records.append({**s,'encoded_file':b['encoded_file'],'brand_derivative_v03':True,'source_design_sha256':b['poster_sha256']});continue
  a=next(manifest)
  if only and a['key']!=only:continue
  n=a['frames'];take=f'_take{a["video_take"]:02}' if a.get('video_take',1)>1 else '';out=ROOT/f'_work/render/{a["segment_id"]}_{a["segment_shot"]:02}_{a["key"]}_v03{take}.mp4';stamp=out.with_suffix('.json');filt=camera(n,a['camera_band']);cfg={'image_sha256':a['sha256'],'frames':n,'filter':filt,'crf':18,'video':a.get('video_sha256')}
  if a.get('video_excerpt_realtime'):cfg['video_excerpt_realtime']=True
  if not out.exists():
   old=next((s for s in prior if s.get('asset_id')==a['asset_id'] and s['frames']==n and s.get('sha256')==a['sha256']),None)
   if old:
    src=ROOT/old['encoded_file'];st=src.with_suffix('.json')
    if st.exists() and read(st)==cfg:shutil.copy2(src,out);shutil.copy2(st,stamp)
  if not(out.exists() and stamp.exists() and read(stamp)==cfg):
   if a.get('video_asset'):
    x,y,x1,y1=a['art_boxes'][0];w=x1-x;h=y1-y;factor=1 if a.get('video_excerpt_realtime') else n/300
    # Consume the complete first 10s as one continuous shot, with optical-flow interpolation.
    fc=f'[1:v]trim=end_frame=240,setpts=(PTS-STARTPTS)*{factor:.12f},scale={w}:{h}:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.15[art];[0:v][art]overlay={x}:{y}:shortest=1,format=yuv420p[v]'
    args=['-loop',1,'-framerate',30,'-i',ROOT/a['file'],'-i',a['video_asset'],'-filter_complex_threads',2,'-filter_complex',fc,'-map','[v]'];cfg['filter']=fc
   else:args=['-loop',1,'-framerate',30,'-i',ROOT/a['file'],'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]']
   ff([*args,'-frames:v',n,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out]);cfg['filter']=filt;save(stamp,cfg)
  parts.append(out);records.append({**a,'encoded_file':str(out.relative_to(ROOT))});print('PICTURE',i+1,a['segment_id'],a['key'],n,flush=True)
 if only:return
 save(ROOT/'records/render_shots.json',records);listing=ROOT/'_work/concat.txt';listing.write_text(''.join(f"file '{p}'\nduration {s['frames']/30:.9f}\n" for p,s in zip(parts,records)))
 raw=ROOT/'_work/picture_concat.mp4';ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw]);ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movflags','+faststart',ROOT/'_work/picture_master.mp4'])
 print('PICTURES COMPLETE',flush=True)

def package():
 for l in ['en','ja']:
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',PREV/f'deliverables/EP002_Halloween_{l}_v02_1080p30.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-movflags','+faststart',ROOT/f'deliverables/EP002_Halloween_{l}_v03_1080p30.mp4']);print('PACKAGED',l,flush=True)

def review():
 import imageio_ffmpeg
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP002_Halloween_{l}_v03_1080p30.mp4';out=ROOT/f'deliverables/EP002_Halloween_{l}_v03_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(src),'-vf',f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'",'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True);print('REVIEW',l,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','visuals','brand','pictures','package','review']);p.add_argument('--only',default='');a=p.parse_args()
 if a.stage=='pictures':pictures(a.only)
 else:globals()[a.stage]()
