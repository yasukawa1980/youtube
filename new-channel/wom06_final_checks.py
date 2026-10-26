"""Source preservation, unique use and exact audio/brand checks for EP006."""
import csv,json,subprocess
from collections import Counter
from pathlib import Path
import soundfile as sf
from wom06_produce import ROOT,REPO,OP,END,read,save,sha,probe

def main():
 shots=read(ROOT/'records/render_shots.json');sources=read(ROOT/'records/source_assets.json')['assets'];byid={x['id']:x for x in sources};usage=[]
 for i,s in enumerate(shots):
  ids=s.get('base_assets',[]) or ([s['base_asset']] if s.get('base_asset') in byid else [])
  for key in ids:usage.append(dict(asset_id=key,shot=i+1,segment=s['segment_id'],start=s['start'],end=s['end'],uses=1,sha256=sha(byid[key]['path'])))
 counts=Counter(x['asset_id'] for x in usage);assert len(counts)==19 and set(counts.values())=={1}
 for x in usage:assert x['sha256']==byid[x['asset_id']]['sha256']
 for prefix in ['hesiod_','jebb1904_','norden_']:assert sum(x.startswith(prefix) for x in counts)==1
 with (ROOT/'deliverables/EP006_asset_usage_v01.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(usage[0]));w.writeheader();w.writerows(usage)
 save(ROOT/'records/asset_usage_v01.json',usage)
 request=read(ROOT/'records/request.json')
 for path,digest in request['brand_sha256'].items():assert sha(path)==digest
 for name,digest in request['input_scripts'].items():assert sha(ROOT/'records'/name)==sha(REPO/'new-channel/episodes/EP006_Sphinx/records'/name)==digest
 gen=read(ROOT/'records/kling_generation.json');assert gen['actual_credits_used']==sum(c['credits'] for c in gen['clips'])==272<=300
 assert gen['initial_balance']-gen['current_balance']==272
 for c in gen['clips']:assert sha(c['local_path'])==c['sha256']
 master=read(ROOT/'records/master_timeline.json');samples=round(master['duration_seconds']*48000);wav=[]
 for l in ['en','ja']:
  p=ROOT/f'deliverables/EP006_audio_{l}.wav';s=sf.info(p)
  assert (s.samplerate,s.channels,s.frames,s.subtype)==(48000,2,samples,'PCM_24')
  wav.append(dict(file=p.name,sha256=sha(p),sample_rate=48000,samples=samples,channels=2,subtype=s.subtype))
 save(ROOT/'records/wav_sample_validation.json',{'passed':True,'files':wav})
 assert shots[-1]['key']=='endcard' and shots[-1]['frames']==300 and abs(shots[-1]['start']-(master['duration_seconds']-10))<1e-8
 assert shots[3]['key']=='opening' and shots[3]['frames']==120
 save(ROOT/'records/final_checks.json',{'passed':True,'originals_unchanged':19,'every_original_one_use':True,'same_book_one_page':True,'brand_sources_unchanged':True,'script_inputs_unchanged':True,'kling_credits_used':272,'endcard_last_10_seconds':True,'human_listening_completed':False,'youtube_posted':False,'release_published':False})
 print('FINAL CHECKS: 19 originals; 272 credits; WAV 17528000 samples; passed',flush=True)
if __name__=='__main__':main()
