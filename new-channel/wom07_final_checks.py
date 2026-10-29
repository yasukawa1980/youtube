"""Checks specific to the approved EP007 handoff, alongside full decode QA."""
import json
import numpy as np
from PIL import Image,ImageDraw
import soundfile as sf
from wom07_produce import ROOT,REPO,read,save,sha,SR,OP,END,probe

def main():
 m=read(ROOT/'records/master_timeline.json');shots=read(ROOT/'records/render_shots.json');visual=read(ROOT/'records/visual_manifest.json');request=read(ROOT/'records/request.json')
 assert len(shots)==21 and len(visual['unique_originals'])==12
 assert len(visual['unique_originals'])==len(set(visual['unique_originals']))
 base=[s['base_asset'] for s in shots if s.get('base_asset')];assert len(base)==len(set(base))==16
 assert [s['key'] for s in shots if s['segment_id'] in ['P03','P04']]==['G01-01','G02-02','G02-01']
 assert [s['key'] for s in shots if s['segment_id']=='P08']==['G11-02']
 assert [s['key'] for s in shots if s['segment_id']=='P07']==['G14-01','G14-02','G14-04']
 assert next(s for s in shots if s['segment_id']=='P09')['key']=='D_young'
 assert m['brand_intervals']['opening'][0]==m['segments'][1]['end']
 assert abs(m['brand_intervals']['endcard'][0]-(m['duration_seconds']-10))<1e-8
 ja=read(ROOT/'records/narration_timeline_ja.json')['segments'];waits={s['id']:s['end']-s['cues'][-1]['end'] for s in ja};assert max(waits.values())<=3
 for p in [OP,END]:assert request['brand_sha256'][str(p)]==sha(p)
 audio=[]
 for lang in ['en','ja']:
  wav=ROOT/f'deliverables/EP007_audio_{lang}.wav';info=sf.info(wav);assert info.samplerate==48000 and info.frames==round(m['duration_seconds']*48000) and info.subtype=='PCM_24'
  mix,sr=sf.read(ROOT/f'audio/{lang}/mix.wav',dtype='float32');assert sr==SR
  for name in ['opening','endcard']:
   a,b=m['brand_intervals'][name];expected,fs=sf.read(ROOT/f'_work/{name}.wav',dtype='float32');actual=mix[round(a*sr):round(b*sr)];assert np.array_equal(actual,expected[:len(actual)]),(lang,name)
  audio.append({'language':lang,'wav_frames':info.frames,'wav_sample_rate':info.samplerate,'wav_subtype':info.subtype,'brand_audio_matches_24k_mix_reference':True})
 ferris=next(s for s in shots if s['key']=='G07-01');assert 'No known restrictions on publication' in ferris['source'] and 'CC0' not in ferris['source'] and 'PD' not in ferris['source']
 c=ferris['crop_normalized'];bx0,by0,bx1,by1=ferris['art_boxes'][0];orig=[.18,.39,.43,.57]
 p0=[bx0+(orig[0]-c[0])/(c[2]-c[0])*(bx1-bx0),by0+(orig[1]-c[1])/(c[3]-c[1])*(by1-by0),bx0+(orig[2]-c[0])/(c[2]-c[0])*(bx1-bx0),by0+(orig[3]-c[1])/(c[3]-c[1])*(by1-by0)]
 z=1.18;left=(1920-1920/z)*.28;top=(820-820/z)*.5
 end=[(p0[0]-left)*z,(p0[1]-110-top)*z+110,(p0[2]-left)*z,(p0[3]-110-top)*z+110]
 assert end[0]>=0 and end[1]>=110 and end[2]<=1920 and end[3]<=930
 index=shots.index(ferris);frame=Image.open(ROOT/f'_work/continuous_en/{index*3+3:03d}.png').convert('RGB');d=ImageDraw.Draw(frame);d.rectangle(tuple(v*2/3 for v in end),outline='#ffd26f',width=2);frame.save(ROOT/'review/ferris_endpoint_scope.jpg',quality=90,optimize=True)
 initial=[]
 for lang in ['en','ja']:
  ims=[np.asarray(Image.open(ROOT/f'review/opening_{lang}_{i:02d}.jpg').convert('RGB')).astype(float) for i in range(1,5)]
  differences=[float(abs(a-b)[75:].mean()) for a,b in zip(ims,ims[1:])];assert min(differences)>0.5
  bright=float((ims[0][75:].max(axis=2)>25).mean());assert bright>.5
  initial.append({'language':lang,'sample_times':[0,1,2,3],'adjacent_sample_rgb_MAD':differences,'first_image_nonblack_fraction':bright,'full_bleed_source':True})
 save(ROOT/'records/episode_specific_qc.json',{'passed':True,'unique_source_asset_count':len(base),'source_occurrences':[{k:s[k] for k in ['segment_id','key','start','end']} for s in shots],'book_order_passed':True,'japanese_end_wait_seconds':waits,'max_ja_wait_seconds':max(waits.values()),'brand_sources_unchanged':True,'audio':audio,'ferris_original_guard_roi':orig,'ferris_endpoint_guard_bbox':end,'ferris_endpoint_scope_preserved':True,'opening_checks':initial,'style_requirement':'NOT PASSED: see visual_style_review.json','human_listening':'pending'})
 print('EPISODE SPECIFIC QC PASSED; VISUAL STYLE STILL UNAPPROVED',flush=True)
if __name__=='__main__':main()
