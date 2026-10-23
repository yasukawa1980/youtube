"""EP003 Shorts verification with the established full-frame/glyph checks."""
import argparse,csv,json,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
import wom_shorts_qc as legacy
from wom03_shorts import ROOT,REQUEST,SR,FPS,read,save,sha,ff,levels
from wom01_quiet_origins import stream_hash
legacy.ROOT=ROOT
legacy.REQUEST=REQUEST

def verify():
 rows=read(ROOT/'records/shorts.json')['shorts'];shots=read(ROOT/'records/render_shots.json');usage=[];media=[];audio=read(ROOT/'records/audio_qc.json');assert audio['passed'];assert read(ROOT/'records/narration.json')['request_sha256']==sha(REQUEST)
 for episode in ['EP003']:
  members={s['id'] for s in rows if s['episode']==episode};sources=[s['source']['sha256'] for s in shots if s['short_id'] in members];assert len(sources)==len(set(sources))
 for s in rows:
  id=s['id'];groups=[g for g in shots if g['short_id']==id];assert sum(g['frames'] for g in groups)==s['frames']
  for a,b in zip(groups,groups[1:]):assert a['end_frame']==b['start_frame']
  for g in groups:
   assert sha(Path(g['source']['path']))==g['source']['sha256'];assert sha(Path(g['encoded_file']))==g['encoded_sha256'];usage.append({'short_id':id,'episode':s['episode'],'asset_id':g['asset_id'],'start_seconds':g['start_frame']/FPS,'end_seconds':g['end_frame']/FPS,'use_count':1,'source_sha256':g['source']['sha256']})
   assert all(140<=t['bbox'][1]<t['bbox'][3]<=260 for t in g['texts'])
  p=ROOT/f'deliverables/QO_short_{s["episode"]}_{id}_v01.mp4';ff(['-i',p,'-f','null','-']);info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(t for t in info['streams'] if t['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',s['frames']);assert 15<=float(info['format']['duration'])<=20
  pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert v['time_base']=='1/15360' and pts==list(range(0,s['frames']*512,512))
  q=levels(p);assert abs(float(q['input_i'])+14)<=.15 and float(q['input_tp'])<=-1;assert stream_hash(p,'a')==stream_hash(ROOT/f'audio/{id}_final.m4a','a')
  voice,sr=sf.read(ROOT/f'audio/{id}_normalized.wav',dtype='float32');step=round(.01*sr);power=np.array([np.sqrt(np.mean(voice[i:i+step]**2)) for i in range(0,len(voice),step)]);onset=float(np.where(power>10**(-50/20))[0][0]*.01);assert onset<=.3
  aq=next(a for a in audio['reports'] if a['id']==id);assert abs(aq['bgm_during_narration_dbfs']+33.5)<.001
  media.append({'id':id,'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'frames':s['frames'],'duration_seconds':float(info['format']['duration']),'video_duration_seconds':s['duration_seconds'],'lufs':float(q['input_i']),'true_peak_dbtp':float(q['input_tp']),'voice_onset_normalized_stem_seconds':onset,'voice_onset_threshold_dbfs':-50,'voice_onset_window_seconds':.01,'bgm_during_narration_dbfs':aq['bgm_during_narration_dbfs'],'full_decode':True,'exact_pts_30fps':True,'audio_stream_matches_measured_m4a':True,'cta_seconds':s['duration_seconds']-s['cta_start']});print('VERIFIED',id,q['input_i'],q['input_tp'],onset,flush=True)
 assert len(usage)==7
 with (ROOT/'deliverables/asset_usage.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(usage[0]));w.writeheader();w.writerows(usage)
 save(ROOT/'records/asset_usage.json',{'passed':True,'unique_sources':7,'rows':usage,'same_source_not_repeated_within_episode':True})
 save(ROOT/'records/media_qc.json',{'passed':True,'media':media,'request_sha256':sha(REQUEST),'render_shots_sha256':sha(ROOT/'records/render_shots.json'),'audio_qc_sha256':sha(ROOT/'records/audio_qc.json'),'human_full_listening':False})


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('stage',choices=['motion','glyphs','verify','frames'])
    a=p.parse_args()
    (verify if a.stage=='verify' else getattr(legacy,a.stage))()
