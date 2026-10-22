"""EP002 v04: remove the repeated circle; restore approved v02 brand pixels.

Reuse encoded v03 shots without re-encoding. Only D_texts is rendered anew.
"""
import argparse,copy,os,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
os.environ['WOM02_ROOT']=os.environ.get('WOM02_V04_ROOT','/Users/ryo/Desktop/新チャンネル/EP002_Halloween/確認版_v04_20261022')
os.environ['WOM02_V02_ROOT']=os.environ['WOM02_ROOT']
from wom02_produce import ROOT,REPO,read,save,sha,ff,probe
from wom01_quiet_origins import stream_hash
from wom02_revision_v02 import camera
PREV=ROOT.parent/'確認版_v03_20261022'
V02=ROOT.parent/'確認版_v02_20261022'

def prepare():
 for d in ['records','deliverables','assets','review','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 for n in ['content.json','content_en.json','master_timeline.json','source_assets.json','ai_images.json','new_stills_v03.json','new_videos_v03.json','new_sources_v03.json','subtitle_cues_en.json','subtitle_cues_ja.json','narration_timeline_en.json','narration_timeline_ja.json','audio_qc.json','chapters.json','pronunciation_locations.json']:
  shutil.copy2(PREV/'records'/n,ROOT/'records'/n)
 for p in (PREV/'deliverables').iterdir():
  if p.suffix in ['.srt','.m4a','.jpg','.txt'] and p.name!='SHA256SUMS_shared.txt':shutil.copy2(p,ROOT/'deliverables'/p.name.replace('_v03_','_v04_'))
 old=read(PREV/'records/render_shots.json');brands={s['key']:s for s in read(V02/'records/render_shots.json') if s['segment_id']=='BRAND'};shots=[];preserved=[]
 for s0 in old:
  s=copy.deepcopy(s0)
  if s['segment_id']=='BRAND':
   b=brands[s['key']];assert (s['start'],s['end'],s['frames'])==(b['start'],b['end'],b['frames']);s=copy.deepcopy(b);s['encoded_file']=f'_work/render/brand_{s["key"]}_v04.mp4';src=V02/b['encoded_file']
  else:
   src=PREV/s['encoded_file'];shutil.copy2(PREV/s['file'],ROOT/s['file'])
   if s['key']=='D_texts':
    # The entire right-hand circle, label and sun lie to the right of x=800.
    # Keep every pixel of the book panel and header in their existing positions.
    im=Image.open(ROOT/s['file']).convert('RGB');ImageDraw.Draw(im).rectangle((800,150,1919,699),fill='#0c1820');im.save(ROOT/s['file'])
    s['texts']=[t for t in s['texts'] if t['text'] not in ['Samhain','Winter begins｜冬のはじまり']];s['sha256']=sha(ROOT/s['file']);s['encoded_file']='_work/render/H03_02_D_texts_v04.mp4';shots.append(s);continue
  dst=ROOT/s['encoded_file'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert sha(src)==sha(dst);preserved.append({'key':s['key'],'reference':str(src),'encoded_sha256':sha(src)});shots.append(s)
 manifest=copy.deepcopy(read(PREV/'records/visual_manifest.json'));manifest['shots']=[{k:v for k,v in s.items() if k!='encoded_file'} for s in shots if s['segment_id']!='BRAND']
 save(ROOT/'records/visual_manifest.json',manifest);save(ROOT/'records/render_shots.json',shots);save(ROOT/'records/preservation_v04.json',{'previous_root':str(PREV),'brand_reference_root':str(V02),'encoded_copies':preserved,'changed_keys':['D_texts','opening','endcard'],'no_new_generated_assets':True})
 print('PREPARED',len(shots),flush=True)

def pictures():
 shots=read(ROOT/'records/render_shots.json');s=next(s for s in shots if s['key']=='D_texts');out=ROOT/s['encoded_file']
 ff(['-loop',1,'-framerate',30,'-i',ROOT/s['file'],'-filter_complex_threads',2,'-filter_complex',camera(s['frames'],s['camera_band']),'-map','[v]','-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out])
 listing=ROOT/'_work/concat.txt';listing.write_text(''.join(f"file '{ROOT/s['encoded_file']}'\nduration {s['frames']/30:.9f}\n" for s in shots))
 raw=ROOT/'_work/picture_concat.mp4';ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw]);ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movflags','+faststart',ROOT/'_work/picture_master.mp4'])
 for l in ['en','ja']:
  ff(['-i',ROOT/'_work/picture_master.mp4','-i',PREV/f'deliverables/EP002_Halloween_{l}_v03_1080p30.mp4','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if l=='en' else 'jpn'),'-movflags','+faststart',ROOT/f'deliverables/EP002_Halloween_{l}_v04_1080p30.mp4'])
 print('PICTURES COMPLETE',flush=True)

def review():
 import imageio_ffmpeg
 for l in ['en','ja']:
  src=ROOT/f'deliverables/EP002_Halloween_{l}_v04_1080p30.mp4';out=ROOT/f'deliverables/EP002_Halloween_{l}_v04_subtitled_review_1080p30.mp4';srt=ROOT/f'_work/{l}.srt';shutil.copy2(src.with_suffix('.srt'),srt)
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(src),'-vf',f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'",'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True);print('REVIEW',l,flush=True)

def frame_hashes(p):
 raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(p),'-map','0:v:0','-an','-f','framemd5','-'],text=True)
 return [line.rsplit(',',1)[-1].strip() for line in raw.splitlines() if not line.startswith('#')]

def identity():
 from wom02_v02_qc import motion_stats,roi
 old=read(PREV/'records/render_shots.json');new=read(ROOT/'records/render_shots.json');assert len(old)==len(new)==40
 assert [(s['key'],s['start'],s['end'],s['frames']) for s in old]==[(s['key'],s['start'],s['end'],s['frames']) for s in new]
 assert sha(PREV/'records/master_timeline.json')==sha(ROOT/'records/master_timeline.json')
 ref3=frame_hashes(PREV/'deliverables/EP002_Halloween_en_v03_1080p30.mp4');ref2=frame_hashes(V02/'deliverables/EP002_Halloween_en_v02_1080p30.mp4');cur=frame_hashes(ROOT/'deliverables/EP002_Halloween_en_v04_1080p30.mp4');assert len(ref3)==len(ref2)==len(cur)==11930
 records=[]
 for s in new:
  start=round(s['start']*30);end=round(s['end']*30);key=s['key'];expected=ref2 if s['segment_id']=='BRAND' else ref3
  if key=='D_texts':assert all(a!=b for a,b in zip(cur[start:end],ref3[start:end]));expected_new=frame_hashes(ROOT/s['encoded_file']);assert expected_new==cur[start:end]
  else:assert cur[start:end]==expected[start:end]
  records.append({'key':key,'segment_id':s['segment_id'],'start_frame':start,'end_frame_exclusive':end,'frames':end-start,'reference':'new D_texts clip' if key=='D_texts' else 'v02' if s['segment_id']=='BRAND' else 'v03','all_frame_hashes_match':True})
 save(ROOT/'records/frame_identity_v04.json',{'passed':True,'video_sha256':sha(ROOT/'deliverables/EP002_Halloween_en_v04_1080p30.mp4'),'render_shots_sha256':sha(ROOT/'records/render_shots.json'),'method':'MD5 of every decoded yuv420p frame in the final normal English MP4; Japanese compressed video stream equality verified separately. Subtitle-burned review copies are re-encoded derivatives, not the pixel-identity reference.','shots':records,'frames_v03_identical':sum(r['frames'] for r in records if r['reference']=='v03'),'brand_frames_v02_identical':720,'new_diagram_frames_verified':252,'decoded_frame_md5_v04':cur,'decoded_frame_md5_v03':ref3,'decoded_frame_md5_v02':ref2})
 previous_motion=read(PREV/'records/motion_v03.json');motion=[]
 for i,s in enumerate(new):
  if s['segment_id']=='BRAND':motion.append({'key':s['key'],'segment_id':'BRAND','excluded':True,'reason':'Approved common brand with fades; outside image zoom motion criterion.'});continue
  if s['key']=='D_texts':q=motion_stats(ROOT/s['encoded_file'],roi(s))
  else:
   before=previous_motion['shots'][i];assert sha(ROOT/s['encoded_file'])==before['encoded_sha256'];q=before['measurement']
  assert q['frame_pairs']==s['frames']-1 and q['p95_over_median']<=2.5
  motion.append({'key':s['key'],'segment_id':s['segment_id'],'excluded':False,'measurement':q,'passed':True,'encoded_sha256':sha(ROOT/s['encoded_file']),'measurement_reused_for_identical_encoded_bytes':s['key']!='D_texts'})
 save(ROOT/'records/motion_v04.json',{'passed':True,'threshold':2.5,'tested_main_shots':38,'brand_excluded':2,'shots':motion})
 print('IDENTITY AND MOTION PASSED',flush=True)

def verify():
 evidence=read(ROOT/'records/frame_identity_v04.json');assert evidence['passed'] and evidence['video_sha256']==sha(ROOT/'deliverables/EP002_Halloween_en_v04_1080p30.mp4');assert evidence['render_shots_sha256']==sha(ROOT/'records/render_shots.json');assert read(ROOT/'records/motion_v04.json')['passed']
 allfiles=[]
 for l in ['en','ja']:
  reference=PREV/f'deliverables/EP002_Halloween_{l}_v03_1080p30.mp4';ah=stream_hash(reference,'a');srt=ROOT/f'deliverables/EP002_Halloween_{l}_v04_1080p30.srt';assert sha(srt)==sha(reference.with_suffix('.srt'))
  for review in [False,True]:
   p=ROOT/f'deliverables/EP002_Halloween_{l}_v04{"_subtitled_review" if review else ""}_1080p30.mp4';ff(['-i',p,'-f','null','-']);d=probe(p);v=next(s for s in d['streams'] if s['codec_type']=='video');assert v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==11930 and v['time_base']=='1/15360'
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert pts==list(range(0,11930*512,512));assert abs(float(d['format']['duration'])-397.6666666667)<1/30;assert stream_hash(p,'a')==ah
   allfiles.append({'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'frames':11930,'duration_seconds':float(d['format']['duration']),'full_decode':True,'exact_pts_30fps':True,'video_stream_sha256':stream_hash(p,'v'),'audio_stream_sha256':ah,'audio_identical_to_v03':True,'srt_sha256':sha(srt),'srt_identical_to_v03':True});print('VERIFIED',p.name,flush=True)
 assert allfiles[0]['video_stream_sha256']==allfiles[2]['video_stream_sha256']
 assert sha(PREV/'deliverables/EP002_thumbnail_en.jpg')==sha(ROOT/'deliverables/EP002_thumbnail_en.jpg')
 manifest=read(ROOT/'records/visual_manifest.json');before=read(PREV/'records/visual_manifest.json');layout=[]
 for a,b in zip(manifest['shots'],before['shots']):
  if a['key']!='D_texts':assert a==b and sha(ROOT/a['file'])==sha(PREV/b['file'])
  else:
   assert [t['text'] for t in a['texts']]==['QUIET ORIGINS  /  EP002','8th–12th c.｜8〜12世紀'];assert max(t['bbox'][3] for t in a['texts'])<=700
   im=Image.open(ROOT/a['file']);orig=Image.open(PREV/b['file']);assert im.crop((0,0,800,1080)).tobytes()==orig.crop((0,0,800,1080)).tobytes();assert im.crop((800,150,1920,700)).getextrema()==((12,12),(24,24),(32,32))
  layout.append({'key':a['key'],'passed':True,'layout_unchanged':a['key']!='D_texts'})
 prior_layout=read(PREV/'records/subtitle_layout_validation.json');assert prior_layout['passed'];save(ROOT/'records/layout_v04.json',{'passed':True,'checks':layout,'reference_v03_layout_sha256':sha(PREV/'records/subtitle_layout_validation.json'),'method':'37 main layouts unchanged, D_texts only removes right-hand diagram and text. No text added or moved; SRTs and rendering styles unchanged.','minimum_glyph_top':prior_layout['minimum_glyph_top']})
 originals=read(ROOT.parent/'確認版_v01_20261022/records/request.json')['brand_sha256']
 for p,h in originals.items():assert sha(Path(p))==h
 save(ROOT/'records/qc_v04.json',{'passed':True,'files':allfiles,'render_shots_sha256':sha(ROOT/'records/render_shots.json'),'visual_manifest_sha256':sha(ROOT/'records/visual_manifest.json'),'shot_timings_identical_to_v03':True,'frames':11930,'duration_seconds':397.6666666667,'brand_frames_identical_to_v02':720,'other_frames_identical_to_v03':10958,'diagram_changed_frames':252,'thumbnail_identical':True,'shared_brand_original_sha256':originals,'human_full_listening':False})
 print('QC PASSED: 10958 v03 frames, 720 v02 brand frames, 252 diagram frames',flush=True)

def frames():
 shots=read(ROOT/'records/render_shots.json');video=ROOT/'deliverables/EP002_Halloween_en_v04_1080p30.mp4'
 for key in ['D_texts','D_season','opening','endcard']:
  s=next(s for s in shots if s['key']==key);ff(['-ss',(s['start']+s['end'])/2,'-i',video,'-frames:v',1,'-vf','scale=1280:720','-q:v',3,ROOT/f'review/{key}_v04.jpg'])
 print('FRAMES READY',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','pictures','review','identity','verify','frames']);a=p.parse_args();globals()[a.stage]()
