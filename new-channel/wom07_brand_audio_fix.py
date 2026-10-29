"""Remove normalization pre-ringing at brand boundaries; retain encoded picture packets."""
import shutil,numpy as np,soundfile as sf
from wom07_produce import ROOT,read,save,sha,ff,measure,SR
from wom01_quiet_origins import stream_hash

def main():
 state=ROOT/'records/brand_audio_boundary_correction.json'
 if state.exists():print('Already corrected');return
 m=read(ROOT/'records/master_timeline.json');mix=ROOT/'audio/en/mix.wav';x,sr=sf.read(mix,dtype='float32');assert sr==SR;items=[]
 backup=ROOT/'_work/brand_audio_boundary_inputs';backup.mkdir(exist_ok=True)
 shutil.copy2(mix,backup/'mix_en_original.wav')
 for name,(a,b) in m['brand_intervals'].items():
  lo,hi=round(a*sr),round(b*sr);y,fs=sf.read(ROOT/f'_work/{name}.wav',dtype='float32');diff=x[lo:hi]-y[:hi-lo]
  items.append({'interval':name,'changed_samples':int(np.any(diff!=0,axis=1).sum()),'max_absolute_difference':float(abs(diff).max())});x[lo:hi]=y[:hi-lo]
 sf.write(mix,x,sr,subtype='FLOAT')
 aac=ROOT/'deliverables/EP007_audio_en.m4a';wav=ROOT/'deliverables/EP007_audio_en.wav'
 for p in [aac,wav]:shutil.copy2(p,backup/p.name)
 ff(['-i',mix,'-ar',48000,'-c:a','aac','-b:a','192k','-movie_timescale',48000,aac])
 ff(['-i',mix,'-ar',48000,'-af',f'aresample=48000,apad=whole_len={round(m["duration_seconds"]*48000)},atrim=end_sample={round(m["duration_seconds"]*48000)}','-c:a','pcm_s24le',wav])
 videos=[]
 for p in sorted((ROOT/'deliverables').glob('EP007_Thanksgiving_en_*.mp4')):
  oldsha=sha(p);h=stream_hash(p,'v');old=backup/p.name;shutil.copy2(p,old)
  ff(['-i',old,'-i',aac,'-map','0:v:0','-map','1:a:0','-map_metadata',0,'-metadata:s:a:0','language=eng','-c','copy','-movie_timescale',48000,'-movflags','+faststart',p]);assert stream_hash(p,'v')==h
  videos.append({'name':p.name,'old_sha256':oldsha,'new_sha256':sha(p),'unchanged_video_stream_sha256':h})
 audio=read(ROOT/'records/audio_qc.json');audio['languages']['en']['levels']=measure(aac);audio['brand_boundary_correction']=items;save(ROOT/'records/audio_qc.json',audio)
 # Existing visual checks remain valid because every encoded picture packet is identical.
 clean=next(x for x in videos if '_subtitled_' not in x['name'])
 for name in ['continuous_qc','final_video_motion']:
  p=ROOT/f'records/{name}.json';d=read(p)
  rows=d['checks'] if name=='continuous_qc' else [d]
  for row in rows:
   if row.get('video_sha256')==clean['old_sha256']:row['video_sha256']=clean['new_sha256'];row['audio_only_remux_video_evidence']=clean
  save(p,d)
 save(state,{'corrections':items,'picture_packets_unchanged':videos,'scope':'English mix only. Original inputs retained. Full final container decode and audio QA will be rerun; visual frame evidence reused only after encoded video SHA equality.'})
 print('BRAND AUDIO CORRECTED',items,flush=True)
if __name__=='__main__':main()
