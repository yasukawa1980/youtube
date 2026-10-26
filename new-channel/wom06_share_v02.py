"""Preserve v01 and deliver v02 as a private draft with explicit criterion status."""
import argparse,hashlib,json,subprocess,zipfile,time
from pathlib import Path
from wom06_revision_v02 import ROOT
from wom06_produce import read,save,sha
GH='yasukawa1980/youtube';TAG='wom06-sphinx-v02-20261027'
def api(args,data=None):
 p=subprocess.run(['gh','api',*args],input=json.dumps(data,ensure_ascii=False) if data is not None else None,capture_output=True,text=True,check=True);return json.loads(p.stdout)
def main():
 for n in ['qc_v02','continuous_qc','motion_v02','thumbnail_qc','asset_usage_v02','credit_revision','visual_review_v02']:assert read(ROOT/f'records/{n}.json')['passed'],n
 pixel=read(ROOT/'records/pixel_comparison.json');assert pixel['outside_nonidentical_frames']==112
 for f in read(ROOT/'records/qc_v02.json')['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 acceptance=read(ROOT/'records/pixel_requirement_acceptance.json');out=ROOT/'deliverables';state=ROOT/'records/sharing.json'
 def archive(path,items):
  with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for p,name in sorted(items,key=lambda x:x[1]):
    info=zipfile.ZipInfo(name,date_time=(2026,10,27,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 archive(out/'EP006_records_v02.zip',[(p,p.name) for p in (ROOT/'records').glob('*.json') if p.name!='sharing.json'])
 archive(out/'EP006_review_frames_v02.zip',[(p,p.name) for p in (ROOT/'review').iterdir() if p.suffix in ['.jpg','.png']])
 files=sorted(p for p in out.iterdir() if p.is_file() and p.name!='SHA256SUMS_shared.txt' and 'pronunciation' not in p.name)
 checksum=out/'SHA256SUMS_shared.txt';checksum.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(checksum)
 r=api([f'repos/{GH}/releases/{read(state)["release_id"]}']) if state.exists() else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
 body=f'第6話修正版v02。6区間修正・サムネ3案。英日共通365.166667秒、10955フレーム。音声・SRT・M4A・WAVはv01同一。4本の連続デコード警告0。注意：変更外8662フレーム中8550が画素完全一致、直前112フレームに圧縮差（平均輝度差0.059/255）。画素完全一致の条件は未達、扱い：{acceptance["status"]}。非公開Draftを維持。YouTube投稿・予約・公開なし。v01 Release 424086149は保全。'
 if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第6話 スフィンクス v02（英日修正版・確認用）','body':body,'draft':True})
 assert r['draft'];save(state,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
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
 save(state,{'release_id':r['id'],'draft':True,'status':'verified','release_url':r['html_url'],'tag':TAG,'assets':checks,'pixel_criterion_met':False,'acceptance':acceptance['status']});print('SHARED',r['id'],len(checks),flush=True)
if __name__=='__main__':main()
