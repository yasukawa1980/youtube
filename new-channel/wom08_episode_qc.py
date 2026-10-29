"""第8話の台本・素材・ブランド・音声・切り出し範囲の検証。"""
import json
import numpy as np
import soundfile as sf
from PIL import Image
from wom08_produce import ROOT,REPO,OP,END,SR,read,save,sha

def main():
 m=read(ROOT/'records/master_timeline.json');shots=read(ROOT/'records/render_shots.json');v=read(ROOT/'records/visual_manifest.json');request=read(ROOT/'records/request.json')
 assert len(shots)==25 and len(v['shots'])==23
 bases=[s['base_asset'] for s in v['shots'] if s.get('base_asset')];assert len(bases)==len(set(bases))==17
 used=v['unique_originals'];assert len(used)==len(set(used))==16
 assert [s['key'] for s in shots if s['segment_id']=='P04']==['B170','B164']
 assert [s['key'] for s in shots if s['segment_id']=='P05']==['B183','B299','B300']
 assert {s['key'] for s in shots if s['key'] in ['B286','B299','B300','B305']}=={'B286','B299','B300'}
 assert len([s for s in shots if s['key'].startswith('V')])==1
 for name in ['content.json','content_en.json']:assert sha(ROOT/'records'/name)==sha(REPO/'new-channel/episodes/EP008_Tutankhamun/records'/name)
 waits={s['id']:s['end']-s['cues'][-1]['end'] for s in read(ROOT/'records/narration_timeline_ja.json')['segments']};assert max(waits.values())<=3
 assert m['brand_intervals']['opening'][0]==m['segments'][1]['end'];assert abs(m['brand_intervals']['endcard'][0]-(m['duration_seconds']-10))<1e-8
 for p in [OP,END]:assert request['brand_sha256'][str(p)]==sha(p)
 ar=read(ROOT/'records/audio_qc.json');assert set(ar['sources'])=={'QO_THEME_A02'}
 audio=[]
 for l in ['en','ja']:
  info=sf.info(ROOT/f'deliverables/EP008_audio_{l}.wav');assert info.samplerate==48000 and info.frames==round(m['duration_seconds']*48000) and info.subtype=='PCM_24'
  x,sr=sf.read(ROOT/f'audio/{l}/mix.wav',dtype='float32');assert sr==SR
  for name,(a,b) in m['brand_intervals'].items():
   y,fs=sf.read(ROOT/f'_work/{name}.wav',dtype='float32');assert np.array_equal(x[round(a*sr):round(b*sr)],y[:round((b-a)*sr)])
  assert ar['languages'][l]['P07_pause_boost_db']==0
  audio.append({'language':l,'wav_frames':info.frames,'brand_audio_sample_identical':True,'P07_boost_db':0})
 opening=[]
 for l in ['en','ja']:
  ims=[np.asarray(Image.open(ROOT/f'review/opening_{l}_{i:02d}.jpg')).astype(float) for i in range(1,5)]
  diffs=[float(abs(a-b)[75:].mean()) for a,b in zip(ims,ims[1:])];assert min(diffs)>0
  opening.append({'language':l,'rgb_MAD_between_0_1_2_3s':diffs,'nonblack_fraction':float((ims[0][75:].max(axis=2)>25).mean()),'source':'B286','full_bleed':True})
 # Compositions contain only approved article strips, including their blurred backgrounds.
 news=[]
 for s in v['shots']:
  if s['key'].startswith('N'):
   assert s['background_also_uses_only_crop'] and s['crop_normalized'][0]>=.278
   news.append({k:s[k] for k in ['key','crop_normalized','detail_crop_normalized','background_also_uses_only_crop']})
 report={'passed':True,'script_hashes':request['input_scripts'],'shot_count':25,'source_usage':[{k:s[k] for k in ['key','segment_id','start','end']} for s in shots],'base_assets_each_used_once':bases,'japanese_end_wait_seconds':waits,'max_ja_wait_seconds':max(waits.values()),'audio':audio,'opening':opening,'newspaper_crops':news,'crop_rule':'All visible foreground and blurred background derive solely from documented crop; camera operates on that composition, never on the full newspaper.','human_full_listening':'pending','AI_semantic_review':'1-second interval samples inspected: single candle, no person, writing, tomb or modern object. This is sampled visual inspection, not automated semantic certification of every frame.','p258_note':'The actual printed wish begins Live thy Ka. Earlier research shorthand May thy Ka is corrected by the source image itself; approved narration is a meaning summary and unchanged.'}
 save(ROOT/'records/episode_specific_qc.json',report);print('EP008 SPECIFIC PASSED; max JA wait',max(waits.values()))
if __name__=='__main__':main()
