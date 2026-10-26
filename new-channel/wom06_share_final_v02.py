"""Final v02 draft. Keeps earlier draft intact; audio is referenced from verified v01."""
import hashlib,subprocess,zipfile,time
from wom06_revision_v02 import ROOT
from wom06_produce import read,save,sha
from wom06_share_v02 import api,GH
TAG='wom06-sphinx-v02-final-20261027'
def main():
 for n in ['qc_v02','continuous_qc','motion_v02','thumbnail_qc','asset_usage_v02','credit_revision','visual_review_v02']:assert read(ROOT/f'records/{n}.json')['passed'],n
 pixel=read(ROOT/'records/pixel_comparison.json');assert pixel['outside_nonidentical_frames']==112
 acceptance=read(ROOT/'records/pixel_requirement_acceptance.json');assert acceptance['user_exact_reply']=='圧縮差を許容してv02を確定'
 qc=read(ROOT/'records/qc_v02.json')
 for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 visual=read(ROOT/'records/visual_review_v02.json');assert visual['video_sha256']==sha(ROOT/'deliverables/EP006_Sphinx_en_v02_1080p30.mp4') and visual['render_shots_sha256']==sha(ROOT/'records/render_shots.json')
 out=ROOT/'deliverables';statepath=ROOT/'records/sharing_final.json'
 def archive(path,items):
  with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for p,name in sorted(items,key=lambda x:x[1]):
    info=zipfile.ZipInfo(name,date_time=(2026,10,27,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 archive(out/'EP006_records_v02_confirmed.zip',[(p,p.name) for p in (ROOT/'records').glob('*.json') if not p.name.startswith('sharing')])
 archive(out/'EP006_review_frames_v02.zip',[(p,p.name) for p in (ROOT/'review').iterdir() if p.suffix in ['.jpg','.png']])
 names=[f['name'] for f in qc['files']]+[f'EP006_Sphinx_{l}_v02_1080p30.srt' for l in ['en','ja']]+['EP006_asset_usage_v02.csv','EP006_source_credits.md','EP006_upload_info_en.md','EP006_upload_info_ja.md','EP006_records_v02_confirmed.zip','EP006_review_frames_v02.zip','EP006_v02_approval.json','preview.html','wom06_サムネ168px比較_20261027.jpg']+[f'wom06_サムネ案{i}_20261027.jpg' for i in [1,2,3]]
 files=[out/n for n in sorted(names)];checksum=out/'SHA256SUMS_v02_confirmed.txt';checksum.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(checksum)
 r=api([f'repos/{GH}/releases/{read(statepath)["release_id"]}']) if statepath.exists() else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
 body='第6話修正版v02・最終確定版。P09の顔→翼の移動方向まで確認済み。6区間修正・サムネ3案。英日共通365.166667秒／10955フレーム。音声・SRT・M4A・WAVはv01同一、4本の連続デコード警告0。変更外8662フレーム中8550が画素一致、直前112フレームの微小な圧縮差は本人が許容（承認文：圧縮差を許容してv02を確定）。本編M4A・WAVとKling原本はv01 Release 424086149を参照、SRTは再添付。記録はEP006_records_v02_confirmed.zip、承認はEP006_v02_approval.json。先行確認用Draft 424414685は履歴として保全。非公開Draft、YouTube投稿・予約・公開なし。'
 if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第6話 スフィンクス v02 最終確定版（非公開）','body':body,'draft':True})
 assert r['draft'];save(statepath,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
 for p in files:
  old=next((a for a in r['assets'] if a['name']==p.name or a.get('digest')=='sha256:'+sha(p)),None)
  if old:assert old['state']=='uploaded' and old['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
  print('UPLOADED',p.name,flush=True)
 r=api([f'repos/{GH}/releases/{r["id"]}']);assert r['draft'] and len(r['assets'])==len(files);checks=[]
 for p in files:
  a=next(a for a in r['assets'] if a['name']==p.name or a.get('digest')=='sha256:'+sha(p))
  for attempt in range(3):
   proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();count=0
   while True:
    b=proc.stdout.read(1048576)
    if not b:break
    h.update(b);count+=len(b)
   code=proc.wait()
   if code==0 and h.hexdigest()==sha(p) and count==p.stat().st_size and a['digest']=='sha256:'+h.hexdigest():break
   if attempt==2:raise RuntimeError(f'REST verification failed: {p.name}, exit={code}, bytes={count}')
   time.sleep(2)
  checks.append({'name':p.name,'github_name':a['name'],'asset_id':a['id'],'bytes':count,'sha256':h.hexdigest(),'rest_download_verified':True});print('REST VERIFIED',p.name,flush=True)
 state={'release_id':r['id'],'draft':True,'status':'verified','release_url':r['html_url'],'tag':TAG,'assets':checks,'pixel_criterion_met':False,'acceptance':acceptance['status'],'latest_records_archive':'EP006_records_v02_confirmed.zip','latest_checksum':checksum.name,'audio_reused_from_release_id':424086149,'superseded_review_release_id':424414685}
 save(statepath,state);save(ROOT/'records/sharing.json',state)
 old=api([f'repos/{GH}/releases/424414685']);assert old['draft']
 api(['--method','PATCH',f'repos/{GH}/releases/424414685','--input','-'],{'draft':True,'name':'Quiet Origins：第6話 v02 先行確認版（最終版あり・保全）','body':f'このDraftは先行確認用の保存履歴です。P09の移動方向まで確認した最終確定版はRelease ID {r["id"]}、{r["html_url"]}。この先行版の添付は保全し、公開していません。'})
 print('FINAL SHARED',r['id'],len(checks),flush=True)
if __name__=='__main__':main()
