"""EP006 private Draft Release delivery; checks all bytes by Release ID REST download."""
import hashlib,json,shutil,subprocess,time,zipfile
from pathlib import Path
from wom06_produce import ROOT,REPO,read,save,sha
GH='yasukawa1980/youtube';TAG='wom06-sphinx-v01-20261026'
def api(args,data=None):
 p=subprocess.run(['gh','api',*args],input=json.dumps(data) if data is not None else None,capture_output=True,text=True,check=True)
 return json.loads(p.stdout)
def share():
 for name in ['qc_v01','continuous_qc','motion_v01','final_video_motion','visual_review','subtitle_layout_validation','final_checks','wav_sample_validation','container_precision']:
  assert read(ROOT/f'records/{name}.json')['passed'],name
 qc=read(ROOT/'records/qc_v01.json');visual=read(ROOT/'records/visual_review.json')
 for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 for f in read(ROOT/'records/wav_sample_validation.json')['files']:assert sha(ROOT/'deliverables'/f['file'])==f['sha256']
 for c in read(ROOT/'records/continuous_qc.json')['checks']:
  assert c['video_sha256']==sha(ROOT/f'deliverables/EP006_Sphinx_{c["language"]}_v01_1080p30.mp4')
 assert visual['video_sha256']==sha(ROOT/'deliverables/EP006_Sphinx_en_v01_1080p30.mp4')
 assert visual['render_shots_sha256']==sha(ROOT/'records/render_shots.json')
 assert visual['visual_manifest_sha256']==sha(ROOT/'records/visual_manifest.json')
 out=ROOT/'deliverables';state=ROOT/'records/sharing.json'
 # Deterministic archives allow an interrupted upload to resume without replacing assets.
 def archive(path,items):
  with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for p,name in sorted(items,key=lambda x:x[1]):
    info=zipfile.ZipInfo(name,date_time=(2026,10,26,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 archive(out/'EP006_records.zip',[(p,p.name) for p in (ROOT/'records').glob('*.json') if p.name not in ['sharing.json','still_render_progress.json']])
 archive(out/'EP006_review_frames.zip',[(p,p.name) for p in (ROOT/'review').glob('*.jpg')])
 gen=read(ROOT/'records/kling_generation.json')
 archive(out/'EP006_Kling_originals.zip',[(Path(c['local_path']),Path(c['local_path']).name) for c in gen['clips']]+[(ROOT/'records/kling_generation.json','kling_generation.json')])
 files=sorted(p for p in out.iterdir() if p.is_file() and p.name!='SHA256SUMS_shared.txt')
 checksum=out/'SHA256SUMS_shared.txt';checksum.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(checksum)
 r=api([f'repos/{GH}/releases/{read(state)["release_id"]}']) if state.exists() else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
 if r is None:
  r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第6話 スフィンクス v01（英日確認版）','body':'承認済み台本v02。英日共通映像365.166667秒・10955フレーム。通常版、字幕入り確認版、SRT、M4A、48kHz/24bit WAV、サムネ2案、固有名詞試聴音声、Kling生成原本5本（採用3本）、検査記録。Kling実測272クレジット。本人の試聴・映像確認待ち。非公開Draftを維持し、YouTube投稿なし。','draft':True})
 assert r['draft'];save(state,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
 for p in files:
  old=next((a for a in r['assets'] if a['name']==p.name),None)
  if old:assert old['state']=='uploaded' and old['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
  print('UPLOADED',p.name,flush=True)
 r=api([f'repos/{GH}/releases/{r["id"]}']);assert r['draft'] and len(r['assets'])==len(files);checks=[]
 for p in files:
  a=next(a for a in r['assets'] if a['name']==p.name)
  for attempt in range(3):
   proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();count=0
   while True:
    b=proc.stdout.read(1048576)
    if not b:break
    h.update(b);count+=len(b)
   code=proc.wait()
   if code==0 and h.hexdigest()==sha(p) and count==p.stat().st_size and a['digest']=='sha256:'+h.hexdigest():break
   if attempt==2:raise RuntimeError(f'REST download mismatch: {p.name}, exit={code}, bytes={count}')
   time.sleep(2)
  checks.append({'name':p.name,'asset_id':a['id'],'bytes':count,'sha256':h.hexdigest(),'rest_download_verified':True});print('REST VERIFIED',p.name,flush=True)
 save(state,{'release_id':r['id'],'draft':True,'status':'verified','release_url':r['html_url'],'tag':TAG,'assets':checks});print('SHARED',r['id'],len(checks),flush=True)
if __name__=='__main__':share()
