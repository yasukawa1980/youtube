"""Episode-specific measurable constraints, with the owner's explicit B exception."""
import json,csv,re
from collections import Counter
from pathlib import Path
from wom11_produce import ROOT,REPO,read,save,sha,VERSION
from wom11_visuals import DENIALS

def main():
 m=read(ROOT/'records/visual_manifest.json');shots=m['shots'];cards=read(ROOT/'records/contrast.json')['cards'];counts=Counter(s['key'] for s in shots);assert all(v==1 for v in counts.values())
 allowed={551786,557657,243713,551381,550986,558378,545802,12074,420448}
 if VERSION=='v02':allowed.remove(12074)
 assert set(map(int,m['unique_originals']))==allowed
 for s in shots:
  if 'original_source' in s:assert sha(s['original_source'])==s['original_sha256']
  if s.get('approved_upscale_exception'):assert s['native_max_scale']<=({'E01A_10_scale':1.7,'E01A_10_beam':3.4,'E01A_10_ammit':2.7}[s['key']])+1e-8
  elif 'native_max_scale' in s:assert s['native_max_scale']<=1
  if s.get('original_asset_id')=='551786':assert 'Spell 125' not in ' '.join(s['source_text'])
 assert next(s for s in shots if s['key']=='E07A_01')['original_asset_id']=='550986'
 for c in cards:
  assert c['minimum_major_glyph_height']>=60 and c['foreground_contrast']>=4.5
  if c['minimum_box_padding'] is not None:assert c['minimum_box_padding']>=(32 if VERSION=='v02' else 18)
 denials=[t['text'] for c in cards if c['key']=='D_denials' for t in c['text_boxes'] if t['major']];assert denials==DENIALS
 assert any('Todtenbuch' in t['text'] for c in cards if c['key']=='D_1842' for t in c['text_boxes'])
 assert not any('Totenbuch' in t['text'] for c in cards for t in c['text_boxes'])
 cropitems=[s for s in shots if s['key'].startswith('E01A_10')];overlaps=[]
 for i,a in enumerate(cropitems):
  for b in cropitems[i+1:]:
   x,y,r,d=a['crop_pixels'];u,v,q,w=b['crop_pixels'];area=max(0,min(r,q)-max(x,u))*max(0,min(d,w)-max(y,v))
   if area:overlaps.append([a['key'],b['key'],area]);assert {a['key'],b['key']}=={'E01A_10_scale','E01A_10_beam'}
 for n in ['content.json','content_en.json']:assert sha(ROOT/'records'/n)==sha(REPO/'new-channel/episodes/EP011_WeighingOfTheHeart/records'/n)
 # Compare native sentences with the retained first pass, distinguishing changed pronunciation from pacing.
 first=read(ROOT/'records/first_pass_preserved.json');identities=[]
 for l in ['en','ja']:
  original={c['sentence_id']:c['sha256'] for c in first['languages'][l]}
  for seg in read(ROOT/f'records/narration_segments_{l}.json')['segments']:
   for c in seg['cues']:
    equal=c['audio_sha256']==original[c['id']];assert equal or c['replacements'];identities.append({'language':l,'sentence_id':c['id'],'unchanged_from_first_pass':equal,'replacements':c['replacements']})
 replacements=read(ROOT/'records/reading_replacements.json')
 # Check phoneme query evidence for the six corrections and preserve the evidence for human listening.
 qs=read(ROOT/'records/queries_ja.json');qm={x['sentence_id']:''.join(''.join(m['text'] for m in ap['moras']) for ap in x['config']['accent_phrases']) for x in qs}
 pronunciation=[]
 for r in replacements:pronunciation.append({**r,'query_moras':qm[r['sentence_id']]})
 expected={'P05-02':'フタツノシンリノマ','P05-04':'シンリノヌシ','P08-06':'ハカリオマモルモノ','P08-07':'ゲンダイノヤク','P09-02':'コオチュウ','P11-04':'コエタダシキモノ'}
 for cid,s in expected.items():assert s in qm[cid],(cid,s,qm[cid])
 assert 'テンビン' in qm['P10-01'] and 'テンハカリ' not in qm['P10-01']
 result={'passed':True,'used_unique_works':9,'content_shots':len(shots),'key_uses':dict(counts),'original_overlap_exceptions':overlaps,'B_approval':read(REPO/'new-channel/research/wom11_制作事前検証_20261104.json')['owner_answer'],'crops_and_scales':[{k:s[k] for k in ['key','original_asset_id','crop_pixels','native_max_scale','approved_upscale_exception']} for s in shots if 'original_asset_id' in s],'quote_exact':True,'scripts_unchanged':True,'native_sentence_identity':identities,'reading_query_evidence':pronunciation,'human_listening':False,'P06_fifth_line':'Displayed for two seconds from its English narration onset, then cut to water artwork during the same sentence.','image_color_restoration':False}
 save(ROOT/'records/episode_qc.json',result)
 if VERSION=='v02':
  result.update(used_unique_works=8,P06_fifth_line='Full five-line card stays until the end of P06; no water painting.',ammit_approval='Owner approved ordinary 2.3–2.7x scaling in Claude review 2026-11-04')
  save(ROOT/'records/episode_qc.json',result)
 for name,rows in [('crop_scales',result['crops_and_scales']),('card_metrics',[{'key':c['key'],'contrast':c['foreground_contrast'],'minimum_major_glyph_height':c['minimum_major_glyph_height'],'minimum_box_padding':c['minimum_box_padding']} for c in cards])]:
  with (ROOT/f'deliverables/EP011_{name}.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 print('EPISODE QC PASS',len(shots),len(identities),'sentences',len(replacements),'readings',flush=True)
if __name__=='__main__':main()
