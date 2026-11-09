"""Create a private draft for unfinished pnt02 assets; never publish or replace assets."""
from pathlib import Path
import hashlib,json,subprocess
from pnt02_produce import ROOT,REPO,sha,save
REPOSITORY='yasukawa1980/youtube'
TAG='qo-pnt02-v01-preproduction-20261110'
RECORD=REPO/'painting/pnt02_確認版_v01_20261110/sharing.json'

def api(endpoint,method='GET',data=None):
 args=['gh','api','--method',method,endpoint]
 if data is not None:args+=['--input','-']
 p=subprocess.run(args,input=json.dumps(data) if data is not None else None,capture_output=True,text=True,check=True)
 return json.loads(p.stdout)

def main():
 files=[ROOT/'deliverables'/name for name in ['PNT02_audio_subtitles_preliminary_v01.zip','PNT02_design_records_preliminary_v01.zip']]
 assert all(p.exists() for p in files)
 releases=api(f'repos/{REPOSITORY}/releases?per_page=100')
 r=next((r for r in releases if r['tag_name']==TAG),None)
 if r is None:
  r=api(f'repos/{REPOSITORY}/releases','POST',dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins 絵画02 pnt02 v01 制作途中（音声・字幕・設計のみ／非公開）',body='完成確認版動画ではありません。年代帯P07/P08の指定確認待ち。初回英日音声・SRT、素材と画角の検証、静止画カード案、サムネ案を保存。発音は未試聴。動画5本、動画検品、最終投稿情報は未完了。台本文変更なし。公開・投稿しない。',draft=True))
 assert r['draft'] is True
 hidden=subprocess.check_output(['curl','-q','-sS','-o','/dev/null','-w','%{http_code}','-H','Accept: application/vnd.github+json',f'https://api.github.com/repos/{REPOSITORY}/releases/{r["id"]}'],text=True)
 assert hidden=='404',hidden
 state=dict(release_id=r['id'],tag=TAG,url=r['html_url'],draft=True,status='uploading_preproduction_only',video_completed=False,anonymous_http_status=hidden,assets=[])
 save(RECORD,state)
 for p in files:
  old=next((a for a in r['assets'] if a['name']==p.name),None)
  if old:assert old['digest']=='sha256:'+sha(p), 'Existing different asset: preserve it and use a new filename'
  else:subprocess.run(['gh','api','--method','POST',f'https://uploads.github.com/repos/{REPOSITORY}/releases/{r["id"]}/assets?name={p.name}','-H','Content-Type: application/octet-stream','--input',str(p),'--silent'],check=True)
  print('UPLOADED',p.name,flush=True)
 r=api(f'repos/{REPOSITORY}/releases/{r["id"]}')
 assert r['draft'] is True
 for p in files:
  a=next(a for a in r['assets'] if a['name']==p.name);expected=sha(p)
  assert a['size']==p.stat().st_size and a['digest']=='sha256:'+expected
  q=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPOSITORY}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  h=hashlib.sha256();size=0
  for chunk in iter(lambda:q.stdout.read(1024*1024),b''):h.update(chunk);size+=len(chunk)
  assert q.wait()==0 and h.hexdigest()==expected and size==p.stat().st_size
  state['assets'].append(dict(name=p.name,asset_id=a['id'],bytes=size,sha256=expected,rest_download_verified=True));save(RECORD,state)
  print('REST VERIFIED',p.name,flush=True)
 state['status']='preproduction_shared_not_complete_v01';save(RECORD,state)
 print('DRAFT RELEASE',r['id'],flush=True)
if __name__=='__main__':main()
