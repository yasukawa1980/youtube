"""Correct the map poster checksum; preserve the initial QA ZIP as a historical asset."""
import json,shutil,subprocess,hashlib
from wom07_revision_v02 import ROOT,read,save,sha
from wom07_delivery_v02 import archive
from wom07_share_v02 import api,assert_anonymous_hidden,REPO,TAG

def main():
 existing=read(ROOT/'records/sharing_v02.json')
 if existing.get('historical_assets')==1 and (ROOT/'records/manifest_correction_v02.json').exists():
  shot=next(x for x in read(ROOT/'records/render_shots.json') if x['segment_id']=='P05');assert shot['sha256']==sha(ROOT/shot['file']);print('Manifest correction already verified',flush=True);return
 p=ROOT/'records/render_shots.json';shots=read(p);s=next(x for x in shots if x['segment_id']=='P05');old=s['sha256'];actual=sha(ROOT/s['file']);s['sha256']=actual;save(p,shots)
 save(ROOT/'records/manifest_correction_v02.json',{'date_jst':'2026-10-29','field':'render_shots.json / P05 / sha256','previous_value':old,'corrected_value':actual,'reason':'V01 poster hash was inherited when changing the asset and file path. Only the metadata checksum was stale.','video_and_audio_changed':False,'pixel_comparison_and_audio_checks_unchanged':True,'canonical_qa_asset':'EP007_v02_QA_records.zip','historical_qa_asset':'EP007_v02_QA_records_original_snapshot.zip'})
 state=read(ROOT/'records/sharing_v02.json');assert state['status']=='verified'
 r=api([f'repos/{REPO}/releases/{state["release_id"]}']);assert r['draft'] and r['tag_name']==TAG
 assert_anonymous_hidden(f'repos/{REPO}/releases/{r["id"]}')
 name='EP007_v02_QA_records.zip';history='EP007_v02_QA_records_original_snapshot.zip';original=ROOT/'deliverables'/name;backup=ROOT/'deliverables'/history
 oldasset=next(x for x in r['assets'] if x['name']==name);assert oldasset['digest']=='sha256:'+sha(original)
 shutil.copy2(original,backup)
 api(['--method','PATCH',f'repos/{REPO}/releases/assets/{oldasset["id"]}','--input','-'],{'name':history})
 evidence=[(p,str(p.relative_to(ROOT))) for folder in ['records','review'] for p in sorted((ROOT/folder).iterdir()) if p.suffix in ['.json','.jpg','.log'] and p.name not in ['sharing_v02.json','release_archives_v02.json']]
 evidence += [(p,'frame_hashes/'+p.name) for p in sorted((ROOT/'_work').glob('*.framemd5*')) if p.is_file()]
 updated=archive(name,evidence)
 subprocess.run(['gh','release','upload',TAG,str(original),'--repo',REPO],check=True)
 r=api([f'repos/{REPO}/releases/{r["id"]}']);assert r['draft'] and len(r['assets'])==9
 newasset=next(x for x in r['assets'] if x['name']==name);h=hashlib.sha256();size=0
 q=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPO}/releases/assets/{newasset["id"]}'],stdout=subprocess.PIPE)
 for chunk in iter(lambda:q.stdout.read(1048576),b''):h.update(chunk);size+=len(chunk)
 assert q.wait()==0 and h.hexdigest()==updated['sha256'] and size==updated['bytes'] and newasset['digest']=='sha256:'+h.hexdigest()
 assert_anonymous_hidden(f'repos/{REPO}/releases/assets/{newasset["id"]}')
 for c in state['assets']:
  current=next(a for a in r['assets'] if a['id']==c['asset_id']);assert current['digest']=='sha256:'+c['sha256'] and current['size']==c['bytes'];c.update(name=current['name'],browser_download_url=current['browser_download_url'])
  assert_anonymous_hidden(f'repos/{REPO}/releases/assets/{current["id"]}')
 state['assets'].append({'name':name,'asset_id':newasset['id'],'bytes':size,'sha256':h.hexdigest(),'rest_download_verified':True,'anonymous_http_status':404,'browser_download_url':newasset['browser_download_url']})
 state.update(current_assets=8,historical_assets=1,manifest_correction='records/manifest_correction_v02.json');save(ROOT/'records/sharing_v02.json',state)
 rows=read(ROOT/'records/release_archives_v02.json');oldrow=next(x for x in rows if x['name']==name);oldrow.update(name=history,path=str(backup),status='historical snapshot before poster-checksum correction');rows.append(updated);save(ROOT/'records/release_archives_v02.json',rows)
 body=r['body']+'\n\nQA metadata amendment: the inherited P05 poster checksum was corrected. Use EP007_v02_QA_records.zip. EP007_v02_QA_records_original_snapshot.zip is retained only as the historical pre-correction snapshot. No video/audio changed. 8 current assets + 1 historical QA archive. All 9 asset contents are REST/SHA-256 verified and anonymous access is 404.'
 result=api(['--method','PATCH',f'repos/{REPO}/releases/{r["id"]}','--input','-'],{'body':body,'draft':True});assert result['draft']
 print('MANIFEST CORRECTION VERIFIED; 8 CURRENT + 1 HISTORICAL ASSET',flush=True)
if __name__=='__main__':main()
