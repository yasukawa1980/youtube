"""v03 all-shot motion, unique usage and preserved v02 audio/SRT/segments."""
import argparse,csv,subprocess
from collections import Counter
from pathlib import Path
from wom02_revision_v03 import ROOT,PREV,read,save,sha,ff,probe,stream_hash
from wom02_v02_qc import motion_stats,roi

def motion():
 shots=read(ROOT/'records/render_shots.json');checks=[]
 for i,s in enumerate(shots):
  q=motion_stats(ROOT/s['encoded_file'],roi(s));assert q['frame_pairs']==s['frames']-1
  ok=q['p95_over_median'] is not None and q['p95_over_median']<=2.5
  checks.append({'shot_index':i+1,'segment_id':s['segment_id'],'asset_id':s.get('asset_id',s['key']),'key':s['key'],'start':s['start'],'end':s['end'],'frames':s['frames'],'measurement':q,'passed':ok,'brand_shot':s['segment_id']=='BRAND','encoded_sha256':sha(ROOT/s['encoded_file'])})
  print('MOTION',i+1,s['segment_id'],s['key'],q['p95_over_median'],ok,flush=True)
 save(ROOT/'records/motion_v03.json',{'method':'Every decoded frame at native output 30fps. Mean absolute consecutive-frame difference in 8-bit gray, same v02 ROI method: interior 70% of largest artwork, diagrams/brand x200,y200,w1520,h480. No downsampled frames, no removed samples, no percentile trimming. Source clips also measured at native 24fps in the central x200,y200,w1520,h680 ROI.','threshold':2.5,'complete':len(checks)==len(shots),'shots':checks,'all_passed':all(s['passed'] for s in checks),'production_passed':all(s['passed'] for s in checks if not s['brand_shot']),'frame_pairs':sum(s['measurement']['frame_pairs'] for s in checks)})

def usage():
 shots=read(ROOT/'records/render_shots.json');rows=[]
 for i,s in enumerate(shots):
  if s['segment_id']=='BRAND':continue
  rows.append({'asset_id':s['asset_id'],'segment':s['segment_id'],'shot':i+1,'segment_shot':s['segment_shot'],'start':s['start'],'end':s['end'],'frames':s['frames']})
 counts=Counter(x['asset_id'] for x in rows);assert all(x==1 for x in counts.values()) and len(rows)==38
 # Image composites only contain the same whole/detail source; no contact-sheet D_trail exists.
 assert not any('D_trail' in s['key'] for s in shots)
 with (ROOT/'deliverables/EP002_asset_usage_v03.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 originals={a['id']:(Path(a['original_local_path']),a['original_sha256']) for a in read(ROOT/'records/source_assets.json')['assets']}
 for a in read(ROOT/'records/new_sources_v03.json'):originals[a['id']]=(Path(a['original_local_path']),a['sha256'])
 for a in read(ROOT/'records/ai_images.json')+read(ROOT/'records/new_videos_v03.json'):originals[a['id']]=(Path(a['local_path']),a['sha256'])
 source_hashes={k:sha(p) for k,(p,h) in originals.items()};assert all(source_hashes[k]==h for k,(p,h) in originals.items())
 assert len(source_hashes)==len(set(source_hashes.values()))==30
 save(ROOT/'records/asset_usage_v03.json',{'passed':True,'unique_asset_count':len(counts),'counts':dict(counts),'rows':rows,'original_source_sha256':source_hashes,'unique_original_source_count':30,'same_shot_whole_and_detail_allowed':True,'thumbnail_excluded':True,'brand_opening_and_endcard_separate':True})
 print('USAGE',len(rows),'all exactly once',flush=True)

def sources():
 checks=[]
 for a in read(ROOT/'records/new_videos_v03.json'):
  q=motion_stats(Path(a['local_path']),[200,200,1520,680]);assert q['p95_over_median']<=2.5
  rec={'id':a['id'],'source_sha256':a['sha256'],'native_fps':'24/1','measurement':q,'passed':True}
  if a.get('rejected_attempts'):
   rec['rejected_attempts']=[{'sha256':b['sha256'],'reason':b['rejection_reason'],'measurement':motion_stats(Path(b['local_path']),[200,200,1520,680])} for b in a['rejected_attempts']]
  checks.append(rec);print('SOURCE',a['id'],q['p95_over_median'],flush=True)
 save(ROOT/'records/source_video_motion.json',checks)

def verify():
 old=read(PREV/'records/render_shots.json');new=read(ROOT/'records/render_shots.json');assert len(old)==39 and len(new)==40

 def spans(ss):
  return {sid:(min(s['start'] for s in ss if s['segment_id']==sid),max(s['end'] for s in ss if s['segment_id']==sid)) for sid in {s['segment_id'] for s in ss if s['segment_id']!='BRAND'}}
 assert spans(old)==spans(new)
 assert sha(PREV/'records/master_timeline.json')==sha(ROOT/'records/master_timeline.json')
 allfiles=[]
 for l in ['en','ja']:
  src=PREV/f'deliverables/EP002_Halloween_{l}_v02_1080p30.mp4';audiohash=stream_hash(src,'a');srt=ROOT/f'deliverables/EP002_Halloween_{l}_v03_1080p30.srt';assert sha(src.with_suffix('.srt'))==sha(srt)
  for review in [False,True]:
   p=ROOT/f'deliverables/EP002_Halloween_{l}_v03{"_subtitled_review" if review else ""}_1080p30.mp4';ff(['-i',p,'-f','null','-']);d=probe(p);v=next(s for s in d['streams'] if s['codec_type']=='video');assert int(v['nb_frames'])==11930 and v['avg_frame_rate']=='30/1'
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert v['time_base']=='1/15360' and pts==list(range(0,11930*512,512))
   assert abs(float(d['format']['duration'])-397.6666666667)<1/30
   ah=stream_hash(p,'a');assert ah==audiohash
   allfiles.append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'video_stream_sha256':stream_hash(p,'v'),'audio_stream_sha256':ah,'audio_identical_to_v02':True,'srt_sha256':sha(srt),'srt_identical_to_v02':True,'full_decode':True,'exact_pts_30fps':True,'frames':11930,'duration_seconds':float(d['format']['duration'])})
   print('VERIFIED',p.name,flush=True)
 assert allfiles[0]['video_stream_sha256']==allfiles[2]['video_stream_sha256']==stream_hash(ROOT/'_work/picture_master.mp4','v')
 # Verify all 720 derived brand frames in the final master, and preserve the v02 source files.
 def brand_hashes(p):
  expr='between(n\\,1160\\,1279)+between(n\\,11330\\,11929)'
  out=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(p),'-map','0:v:0','-an','-vf',f'select={expr}','-fps_mode','passthrough','-f','framemd5','-'],text=True)
  return [x.rsplit(',',1)[-1].strip() for x in out.splitlines() if not x.startswith('#')]
 b1=brand_hashes(PREV/'deliverables/EP002_Halloween_en_v02_1080p30.mp4');b2=brand_hashes(ROOT/'deliverables/EP002_Halloween_en_v03_1080p30.mp4');assert len(b1)==len(b2)==720 and b1!=b2
 expected=[]
 for s in read(ROOT/'records/brand_revision_v03.json')['records']:
  raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(ROOT/s['encoded_file']),'-map','0:v:0','-an','-f','framemd5','-'],text=True)
  expected.extend(line.rsplit(',',1)[-1].strip() for line in raw.splitlines() if not line.startswith('#'))
  assert sha(PREV/next(t['encoded_file'] for t in old if t['key']==s['key']))==s['source_encoded_sha256']
 assert b2==expected

 assert sha(PREV/'deliverables/EP002_thumbnail_en.jpg')==sha(ROOT/'deliverables/EP002_thumbnail_en.jpg')
 shared_brand=read(ROOT.parent/'確認版_v01_20261022/records/request.json')['brand_sha256']
 for path,h in shared_brand.items():assert sha(Path(path))==h
 save(ROOT/'records/qc_v03.json',{'passed':True,'render_shots_sha256':sha(ROOT/'records/render_shots.json'),'duration_seconds':397.6666666667,'frames':11930,'files':allfiles,'segment_timings_identical':True, 'within_segment_cuts_revised':True,'audio_and_srt_identical':True,'brand_derived_frames_verified_count':720,'brand_frames_identical_to_v02':False,'shared_brand_sources_untouched':True,'shared_brand_original_sha256':shared_brand,'thumbnail_identical':True,'human_full_listening':False})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['motion','usage','sources','verify']);a=p.parse_args();globals()[a.stage]()
