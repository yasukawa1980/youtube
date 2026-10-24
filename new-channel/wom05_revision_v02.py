"""EP005 v02: bounded visual corrections; v01 speech, subtitles and timing preserved."""
import argparse,copy,csv,hashlib,json,math,os,shutil,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
V1=Path('/Users/ryo/Desktop/新チャンネル/EP005_Tengu/確認版_v01_20261024')
ROOT=V1.parent/'確認版_v02_20261024'
os.environ['WOM05_ROOT']=str(V1)
from wom05_produce import REPO,MODELS,read,save,sha,ff,probe,measure
from wom05_render import camera
from wom01_quiet_origins import stream_hash
CHANGED={'ndl_12865768_001','V01','ndl_1182143_010','V02','aic_154960','aic_26700','met_60361','ndl_851648_028','D_forms'}

def prepare():
 for d in ['records','assets','review','deliverables','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 sharing=read(V1/'records/sharing.json');assert sharing['release_id']==422520343 and sharing['status']=='verified'
 preserved={}
 for a in sharing['assets']:
  p=V1/'deliverables'/a['name'];assert sha(p)==a['sha256'];preserved[p.name]=a['sha256']
 save(ROOT/'records/v01_inputs.json',{'release_id':422520343,'files':preserved,'revision_request_sha256':sha(REPO/'new-channel/wom05_修正依頼_v02_20261024.md')})
 for name in ['master_timeline','chapters','content','content_en','source_assets','subtitle_validation','subtitle_layout_validation','audio_qc','wav_sample_validation','reading_replacements','pronunciation_locations','narration_timeline_en','narration_timeline_ja']:
  shutil.copy2(V1/f'records/{name}.json',ROOT/f'records/{name}.json')
 for p in (V1/'deliverables').iterdir():
  if p.name.startswith(('EP005_audio_','EP005_pronunciation_','EP005_thumbnail_')) or p.name=='EP005_source_credits.md':shutil.copy2(p,ROOT/'deliverables'/p.name)
 for l in ['en','ja']:shutil.copy2(V1/f'deliverables/EP005_Tengu_{l}_v01_1080p30.srt',ROOT/f'deliverables/EP005_Tengu_{l}_v02_1080p30.srt')
 import wom05_visuals as v
 v.CROPS.update({'ndl_12865768_001':(.086,.031,.534,.950),'ndl_851648_028':(.525,.045,.968,.965)})
 v.DETAILS['ndl_1182143_010']=(.600,.570,.655,.730)
 for k in ['ndl_12865768_001','ndl_851648_028']:v.images[k]=v.crop(v.originals[k],v.CROPS[k])
 manifest=copy.deepcopy(read(V1/'records/visual_manifest.json'))
 for s in manifest['shots']:
  key=s['key']
  if key in {'ndl_12865768_001','ndl_1182143_010','ndl_851648_028'}:im,rec=v.compose(key)
  elif key=='D_forms':
   im=Image.open(V1/s['file']).convert('RGB');rec={k:val for k,val in s.items() if k not in ['file','sha256','segment_id']};d=ImageDraw.Draw(im)
   d.rectangle((1390,220,1800,540),fill=v.BG)
   # Human forehead/nose/lips/chin profile, clearly different from the bird beak.
   d.line([(1475,500),(1462,465),(1440,422),(1436,350),(1454,306),(1494,284),(1540,286),(1582,308),(1589,344),(1740,344),(1744,365),(1591,369),(1598,393),(1581,400),(1593,412),(1583,439),(1560,453),(1535,456),(1535,502)],fill=v.GOLD,width=6,joint='curve')
   d.line([(1543,330),(1570,335)],fill=v.GOLD,width=5);d.line([(1550,347),(1568,347)],fill=v.IVORY,width=4)
   d.line([(1567,407),(1588,407)],fill=v.GOLD,width=4)
   # Small angular tokin cap resting on the forehead.
   d.polygon([(1514,286),(1522,250),(1569,250),(1582,303),(1540,286)],fill=v.BG,outline=v.GOLD,width=5)
   rec['diagram_revision']='Human profile with straight long nose, lips/chin and small tokin cap; bird unchanged.'
  else:s['file']=str(V1/s['file']);continue
  path=ROOT/'assets'/f'{key}_v02.png';im.save(path);s.update(rec,file=str(path),sha256=sha(path));im.resize((1280,720)).save(ROOT/'review'/f'{key}_composition_v02.jpg',quality=90)
 save(ROOT/'records/visual_manifest.json',manifest)
 old=next(s for s in read(V1/'records/render_shots.json') if s['key']=='V02')
 ff(['-ss',6,'-i',V1/old['encoded_file'],'-frames:v',1,'-vf','crop=1458:820:231:110',ROOT/'assets/V02_start_frame_v02.png'])
 print('PREPARED',ROOT,flush=True)

def align():
 import onnxruntime as ort,soundfile as sf
 from kokoro_onnx import Kokoro
 ort.disable_telemetry_events();opt=ort.SessionOptions();opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
 folder=MODELS/'Kokoro82M_v1';tts=Kokoro.from_session(ort.InferenceSession(str(folder/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(folder/'voices-v1.0.bin'))
 cue=next(s for s in read(V1/'records/narration_timeline_en.json')['segments'] if s['id']=='P11')['cues'][-1]
 a,sr,timings=tts.create_timed(cue['text'],voice='af_heart',lang='en-us',speed=.82,sentence_pause=.3,clause_pause=.12)
 old,sr0=sf.read(V1/cue['audio_file'],dtype='int16');pcm=np.clip(np.floor(a*32768),-32768,32767).astype(np.int16)
 print('ALIGN CHECK',sr,sr0,len(pcm),len(old),'maxerr',int(np.max(np.abs(pcm.astype(int)-old.astype(int)))) if len(pcm)==len(old) else None,flush=True)
 assert sr==sr0==24000 and len(pcm)==len(old)
 env=lambda x:np.sqrt(np.mean(x[:len(x)//240*240].astype(float).reshape(-1,240)**2,axis=1))
 corr=float(np.corrcoef(env(pcm),env(old))[0,1]);print('ENVELOPE CORRELATION',corr,flush=True);assert corr>.99
 matched=bool(np.array_equal(pcm,old))
 rows=[dict(x) if isinstance(x,dict) else vars(x) if hasattr(x,'__dict__') else x for x in timings]
 print('TIMINGS SAMPLE',repr(rows[:3]),flush=True)
 save(ROOT/'records/P11_english_phonemes.json',{'sentence':cue,'synthesis_pcm_identical':matched,'envelope_10ms_correlation':corr,'method':'Same model and synthesis input; inference used only for deterministic duration output. Original audio is never replaced.','maximum_pcm_lsb_difference':int(np.max(np.abs(pcm.astype(int)-old.astype(int)))),'phonemes':rows})


def cut_times():
 x=read(ROOT/'records/P11_english_phonemes.json');rows=x['phonemes'];phon=''.join(r['phoneme'] for r in rows);needle='ɪn smˈɔːl';i=phon.index(needle)
 assert all(len(r['phoneme'])==1 for r in rows)
 en_edo=x['sentence']['start']+rows[0]['start'];en_small=x['sentence']['start']+rows[i]['start']
 ja=next(s for s in read(V1/'records/narration_timeline_ja.json')['segments'] if s['id']=='P11')['cues'][-1]
 q=next(q['config'] for q in read(V1/'records/queries_ja.json') if q['sentence_id']=='P11-03')
 rate=24000/256;speed=q['speed_scale'];nf=lambda t:int(np.rint(t*rate/speed));pos=nf(q['pre_phoneme_length']);moras=[]
 for phrase in q['accent_phrases']:
  for m in phrase['moras']:
   n=nf(m.get('consonant_length') or 0)+nf(m['vowel_length']);moras.append({'text':m['text'],'start':ja['start']+pos/rate,'end':ja['start']+(pos+n)/rate});pos+=n
  if phrase['pause_mora']:pos+=nf(phrase['pause_mora']['vowel_length'])
 pos+=nf(q['post_phoneme_length']);scale=(ja['end']-ja['start'])/(pos/rate)
 for m in moras:
  for k in ['start','end']:m[k]=ja['start']+(m[k]-ja['start'])*scale
 kana=''.join(m['text'] for m in moras);offset=kana.index('コノチイサナ');j=0
 for m in moras:
  if j==offset:ja_small=m['start'];break
  j+=len(m['text'])
 cuts=[round(245.8*30),round(en_edo*30),round(en_small*30),8156];assert min(np.diff(cuts))>=45
 compare=[{'phrase':'Edo-period artists / 江戸時代の作り手たちは','english':en_edo,'japanese':moras[0]['start'],'cut':cuts[1]/30},{'phrase':'in small carvings / この小さな彫り物','english':en_small,'japanese':ja_small,'cut':cuts[2]/30}]
 for c in compare:c.update(japanese_delay_seconds=c['cut']-c['japanese'],japanese_mismatch_over_one_second=abs(c['cut']-c['japanese'])>=1)
 save(ROOT/'records/P11_alignment.json',{'cut_frames':cuts,'comparisons':compare,'english_method':'Kokoro phoneme duration output, original same-length waveform envelope correlation > 0.99; analysis synthesis not used in final audio','japanese_method':'Saved VOICEVOX mora lengths and speed, calibrated to original sentence duration; estimated internal positions, not forced alignment','japanese_query_duration_scale':scale,'japanese_duration_reconstructed':pos/rate,'japanese_duration_actual':ja['end']-ja['start'],'japanese_moras':moras,'decision':'English word timing is authoritative per revision request. Japanese is earlier by >1 second; recorded, audio and total duration unchanged.'})
 print('CUTS',cuts,'COMPARE',compare,flush=True)

def render_static():
 shots=copy.deepcopy(read(V1/'records/render_shots.json'));manifest=read(ROOT/'records/visual_manifest.json')['shots'];bounds=read(ROOT/'records/P11_alignment.json')['cut_frames']
 for s in shots:
  key=s['key'];old=copy.deepcopy(s)
  if key not in CHANGED:s['encoded_file']=str(V1/s['encoded_file']);continue
  s.update(next(x for x in manifest if x['key']==key))
  if key in ['aic_154960','aic_26700','met_60361']:
   j=['aic_154960','aic_26700','met_60361'].index(key);s.update(start=bounds[j]/30,end=bounds[j+1]/30,frames=bounds[j+1]-bounds[j])
  if key in ['V01','V02']:
   s['encoded_file']=str(ROOT/f'_work/render/{key}_v02.mp4');continue
  out=ROOT/f'_work/render/{key}_v02.mp4';filt=camera(s['frames'],s['camera_band'],False,.03);cfg={'image_sha256':sha(s['file']),'frames':s['frames'],'filter':filt}
  if not (out.exists() and out.with_suffix('.json').exists() and read(out.with_suffix('.json'))==cfg):
   ff(['-loop',1,'-framerate',30,'-i',s['file'],'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out]);save(out.with_suffix('.json'),cfg)
  s['encoded_file']=str(out);print('RENDERED',key,s['frames'],flush=True)
 save(ROOT/'records/render_shots.json',shots)

def encode_video(key,video,source_seconds):
 import wom05_visuals as vis
 old=next(s for s in read(V1/'records/render_shots.json') if s['key']==key);n=old['frames'];poster=ROOT/f'assets/{key}_new_poster.png'
 ff(['-i',video,'-frames:v',1,poster]);base=vis.background(Image.open(poster).convert('RGB'));prior=Image.open(V1/old['file']);base.paste(prior.crop((0,0,1920,110)),(0,0));basepath=ROOT/f'assets/{key}_background_v02.png';base.save(basepath)
 if key=='V02':
  # Keep original first six seconds, and replace only the later movement.
  n-=180
 z=f'(1+0.03*on/{max(1,n-1)})';x=f'(W-W/{z})/2';y=f'(H-H/{z})/2'
 pers=f"perspective=x0='{x}':y0='{y}':x1='W-{x}':y1='{y}':x2='{x}':y2='H-{y}':x3='W-{x}':y3='H-{y}':sense=source:eval=frame:interpolation=cubic"
 factor=n/30/source_seconds
 filt=f'[1:v]trim=duration={source_seconds},setpts=(PTS-STARTPTS)*{factor},scale=1458:820:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.25,format=yuv444p,{pers}[art];[0:v][art]overlay=231:110:shortest=1,format=yuv420p[v]'
 out=ROOT/f'_work/render/{key}_tail.mp4' if key=='V02' else ROOT/f'_work/render/{key}_v02.mp4'
 ff(['-loop',1,'-framerate',30,'-i',basepath,'-i',video,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',n,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out])
 if key=='V02':
  ff(['-i',V1/old['encoded_file'],'-i',out,'-filter_complex_threads',2,'-filter_complex','[0:v]trim=end_frame=180,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]','-map','[v]','-frames:v',old['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',ROOT/'_work/render/V02_v02.mp4'])
 print('VIDEO RENDERED',key,flush=True)

def video_records():
 shots=read(ROOT/'records/render_shots.json');manifest=read(ROOT/'records/visual_manifest.json')
 for k in ['V01','V02']:
  source=ROOT/'assets/V01_night_grade_v03.mp4' if k=='V01' else V1.parent/'素材/V02_Kling_v03.mp4'
  s=next(s for s in shots if s['key']==k);base=ROOT/f'assets/{k}_background_v02.png'
  for name in ['source_start_frame','source_end_frame','source_fps','time_scale','timestamp_mapping']:s.pop(name,None)
  s.update(file=str(base),sha256=sha(base),source_video=str(source),source_video_sha256=sha(source),revision='v02',source_seconds=[0,10] if k=='V01' else [0,6])
  if k=='V02':s.update(prefix_source=str(V1/next(s for s in read(V1/'records/render_shots.json') if s['key']=='V02')['encoded_file']),prefix_source_frames=[0,180],tail_output_frames=258)
  m=next(m for m in manifest['shots'] if m['key']==k);m.update(file=str(base),sha256=sha(base))
 save(ROOT/'records/render_shots.json',shots);save(ROOT/'records/visual_manifest.json',manifest)

def package():
 shots=read(ROOT/'records/render_shots.json');assert sum(s['frames'] for s in shots)==11065
 assert all(Path(s['encoded_file']).exists() for s in shots)
 listing=ROOT/'_work/concat.txt';listing.write_text(''.join(f"file '{s['encoded_file']}'\nduration {s['frames']/30:.9f}\n" for s in shots))
 raw=ROOT/'_work/picture_concat.mp4';ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw]);pic=ROOT/'_work/picture_master.mp4'
 ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movie_timescale',48000,'-movflags','+faststart',pic])
 for l in ['en','ja']:
  ff(['-i',pic,'-i',V1/f'deliverables/EP005_Tengu_{l}_v01_1080p30.mp4','-map','0:v:0','-map','1:a:0','-map_metadata',1,'-c','copy','-movie_timescale',48000,'-movflags','+faststart',ROOT/f'deliverables/EP005_Tengu_{l}_v02_1080p30.mp4']);print('PACKAGED',l,flush=True)

def reviews():
 import imageio_ffmpeg
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP005_Tengu_{l}_v02_1080p30.mp4';out=ROOT/f'deliverables/EP005_Tengu_{l}_v02_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(src),'-vf',vf,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-movie_timescale','48000','-movflags','+faststart',str(out)],check=True);print('REVIEW',l,flush=True)

def hashes(path):
 cache=ROOT/'_work'/('framemd5_'+sha(path)+'.txt')
 if not cache.exists():
  with cache.open('wb') as out:subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(path),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','framemd5','-'],stdout=out,check=True)
 return [l.split(',')[-1].strip() for l in cache.read_text().splitlines() if l and not l.startswith('#')]

def verify():
 oldshots=read(V1/'records/render_shots.json');shots=read(ROOT/'records/render_shots.json');allowed=np.zeros(11065,dtype=bool);unchanged_shots=0
 for old,s in zip(oldshots,shots):
  assert old['key']==s['key']
  if s['key'] in CHANGED:allowed[round(s['start']*30):round(s['end']*30)]=True
  else:
   assert old['start']==s['start'] and old['end']==s['end'] and sha(V1/old['encoded_file'])==sha(s['encoded_file']);unchanged_shots+=1
 files=[]
 for l in ['en','ja']:
  old=V1/f'deliverables/EP005_Tengu_{l}_v01_1080p30.mp4';ah=stream_hash(old,'a')
  assert (ROOT/f'deliverables/EP005_Tengu_{l}_v02_1080p30.srt').read_bytes()==old.with_suffix('.srt').read_bytes()
  for suffix in ['m4a','wav']:assert sha(ROOT/f'deliverables/EP005_audio_{l}.{suffix}')==sha(V1/f'deliverables/EP005_audio_{l}.{suffix}')
  for review in [False,True]:
   p=ROOT/f'deliverables/EP005_Tengu_{l}_v02{"_subtitled_review" if review else ""}_1080p30.mp4';ff(['-i',p,'-f','null','-']);info=probe(p);v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio')
   assert [v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames'])]==[1920,1080,'30/1',11065]
   assert v['time_base']=='1/15360' and int(v['duration_ts'])==11065*512 and a['time_base']=='1/48000' and int(a['duration_ts'])==17704000
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert pts==list(range(0,11065*512,512))
   assert stream_hash(p,'a')==ah
   files.append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'audio_stream_sha256':ah,'audio_identical_v01':True,'video_stream_sha256':stream_hash(p,'v'),'full_decode':True,'frames':11065,'exact_30fps_pts':True,'audio_samples':17704000});print('VERIFIED',p.name,flush=True)
 assert files[0]['video_stream_sha256']==files[2]['video_stream_sha256']
 old=hashes(V1/'deliverables/EP005_Tengu_en_v01_1080p30.mp4');new=hashes(ROOT/'deliverables/EP005_Tengu_en_v02_1080p30.mp4');assert len(old)==len(new)==11065
 dif=np.array([a!=b for a,b in zip(old,new)]);assert not np.any(dif & ~allowed)
 for n in ['content.json','content_en.json','master_timeline.json']:assert sha(ROOT/'records'/n)==sha(V1/'records'/n)
 save(ROOT/'records/qc_v02.json',{'passed':True,'files':files,'duration_seconds':11065/30,'frames':11065,'changed_frames':int(dif.sum()),'unchanged_frames':int((~allowed).sum()),'unchanged_encoded_shots':unchanged_shots,'all_frames_outside_changed_shots_pixel_identical':True,'srt_byte_identical':True,'m4a_wav_byte_identical':True,'audio_stream_identical_v01':True,'script_timeline_byte_identical':True,'shared_video_stream':True,'loudness_unchanged_from_v01':read(V1/'records/audio_qc.json'),'human_full_listening':False})
 print('FRAME COMPARISON',int((~allowed).sum()),'unchanged frames outside corrections',flush=True)

def motion():
 import wom05_motion as m
 m.ROOT=ROOT;checks=[]
 for s in read(ROOT/'records/render_shots.json'):
  if s['key'] not in CHANGED:continue
  q=m.motion_stats(Path(s['encoded_file']),m.roi(s));ok=q['p95_over_median'] is not None and q['p95_over_median']<=2.5;checks.append({'key':s['key'],'start':s['start'],'end':s['end'],'measurement':q,'passed':ok,'sha256':sha(s['encoded_file'])});print('MOTION',s['key'],q['p95_over_median'],ok,flush=True)
 save(ROOT/'records/motion_v02.json',{'passed':all(x['passed'] for x in checks),'shots':checks,'method':'Every decoded consecutive frame; same ROI and MAD method as v01; no discarded differences.'})

def frames():
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16);records=[]
 for i,s in enumerate(read(ROOT/'records/render_shots.json'),1):
  if s['key'] not in CHANGED:continue
  for tag,n in [('start',0),('mid',s['frames']//2),('end',s['frames']-1)]:
   path=ROOT/f'review/shot_{i:02}_{tag}.jpg';ff(['-ss',n/30,'-i',s['encoded_file'],'-frames:v',1,'-vf','scale=1280:720','-q:v',3,path]);records.append({'shot':i,'key':s['key'],'frame':n,'time':s['start']+n/30,'file':path.name,'sha256':sha(path)})
 for batch in range(math.ceil(len(records)/9)):
  sheet=Image.new('RGB',(1280,800),'#0c1820');d=ImageDraw.Draw(sheet)
  for j,r in enumerate(records[batch*9:batch*9+9]):
   x=j%3*426;y=j//3*266;sheet.paste(Image.open(ROOT/'review'/r['file']).resize((426,240)),(x,y));d.text((x+6,y+242),f"{r['shot']:02} {r['key']} {r['time']:.3f}s",font=font,fill='white')
  sheet.save(ROOT/f'review/changed_shots_{batch+1}.jpg',quality=88,optimize=True)
 for key in ['V01','V02']:
  s=next(s for s in read(ROOT/'records/render_shots.json') if s['key']==key);sheet=Image.new('RGB',(1280,1040),'#0c1820');d=ImageDraw.Draw(sheet)
  for j,n in enumerate(np.linspace(0,s['frames']-1,12).round().astype(int)):
   p=ROOT/f'_work/{key}_seq_{j}.jpg';ff(['-ss',int(n)/30,'-i',s['encoded_file'],'-frames:v',1,'-vf','scale=426:240','-q:v',3,p]);x=j%3*426;y=j//3*260;sheet.paste(Image.open(p),(x,y));d.text((x+6,y+242),f'{key} +{n/30:.2f}s',font=font,fill='white')
  sheet.save(ROOT/f'review/{key}_final_sequence_v02.jpg',quality=88,optimize=True)
 save(ROOT/'records/changed_frame_samples.json',{'frames':records});print('FRAMES',len(records),flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','align','cut_times','render_static','video_records','package','reviews','verify','motion','frames']);a=p.parse_args();globals()[a.stage]()
