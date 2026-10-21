"""Share v08 and motion v02 only as private drafts; verify all downloads with REST."""
import hashlib, html, json, os, shutil, subprocess
from pathlib import Path
from wom01_opening_revision import ROOT,MROOT,OLD,MOLD,BASE,read,save,sha
REPO='yasukawa1980/youtube';REPO_ROOT=Path(__file__).resolve().parent.parent

def api(args,data=None):
 return json.loads(subprocess.check_output(['gh','api',*args],input=json.dumps(data,ensure_ascii=False).encode() if data is not None else None))

def preview(root,files):
 cards=[]
 labels={'EP001_ja_opening_connection_trial_v02.mp4':'日本語：冒頭＋オープニング（約56秒）','EP001_en_opening_connection_trial_v02.mp4':'English: opening connection (56 seconds)','Quiet_Origins_opening_trial_v02.mp4':'オープニング単体：音量＋7 dB（4秒）','EP001_ja_endcard_connection_trial_v01.mp4':'日本語：末尾＋エンドカード（変更なし）','EP001_en_endcard_connection_trial_v01.mp4':'English: end-card connection (unchanged)','Quiet_Origins_endcard_trial_v01.mp4':'エンドカード単体（変更なし）'}
 for p in sorted(files,key=lambda p:(0 if 'ja_opening' in p.name else 1,p.name)):
  if p.suffix!='.mp4':continue
  label=labels.get(p.name,('日本語' if '_ja_' in p.name else 'English')+('：字幕入り確認版' if 'subtitled' in p.name else '：通常版・字幕焼き込みなし'))
  video_src=html.escape(os.path.relpath(p,root/'deliverables'))
  cards.append(f'<section><h2>{html.escape(label)}</h2><video controls preload="metadata" src="{video_src}" data-fallback="{html.escape(p.name)}"></video></section>')
 text='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins — 確認用</title><style>body{margin:32px auto;max-width:1120px;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,h2{font-weight:500}h1{color:#d8b575}h2{font-size:19px}section{margin:30px 0}video{width:100%;max-height:72vh;background:#000}p{max-width:900px}</style><h1>Quiet Origins</h1><p>冒頭の文と文の間、最後の問いの前の溜め、オープニングの音量をご確認ください。日本語の話し終わりからロゴまで約1.45秒です。本編への全編組み込みは次の段階です。</p>'''+''.join(cards)+'''<script>document.querySelectorAll('video').forEach(v=>v.addEventListener('error',()=>{if(!v.dataset.tried){v.dataset.tried='1';v.src=v.dataset.fallback;}}));document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(w=>{if(w!==v)w.pause()})))</script></html>'''
 out=root/'deliverables/preview.html';out.write_text(text);return out

def share(root,tag,title,body,files,guide,qcname):
 assert read(root/'records'/qcname)['passed']
 assert read(root/'records/visual_review.json')['passed']
 player=preview(root,files);files.append(player)
 manifest=root/'deliverables/SHA256SUMS_shared.txt';manifest.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(manifest)
 state=root/'records/sharing.json'
 if state.exists():release=api([f'repos/{REPO}/releases/{read(state)["release_id"]}'])
 else:
  release=next((r for r in api([f'repos/{REPO}/releases?per_page=100']) if r['tag_name']==tag),None)
  if release is None:release=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],{'tag_name':tag,'target_commitish':'bgm/production','name':title,'body':body,'draft':True})
 assert release['draft'];checks=[]
 # Persist ID immediately for safe resumption after an interrupted upload.
 save(state,{'release_id':release['id'],'release_url':release['html_url'],'draft':True,'assets':[],'status':'uploading'})
 for p in files:
  a=next((a for a in release['assets'] if a['name']==p.name),None)
  if a:assert a['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',tag,str(p),'--repo',REPO],check=True)
  print('UPLOADED',p.name,flush=True)
 release=api([f'repos/{REPO}/releases/{release["id"]}']);assert release['draft']
 for p in files:
  a=next(a for a in release['assets'] if a['name']==p.name)
  proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPO}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE)
  digest=hashlib.sha256();size=0
  while True:
   block=proc.stdout.read(1024*1024)
   if not block:break
   digest.update(block);size+=len(block)
  assert proc.wait()==0 and digest.hexdigest()==sha(p) and size==p.stat().st_size
  checks.append({'name':p.name,'asset_id':a['id'],'bytes':size,'sha256':digest.hexdigest(),'rest_download_verified':True})
  print('VERIFIED',p.name,flush=True)
 save(state,{'release_id':release['id'],'release_url':release['html_url'],'draft':True,'assets':checks,'status':'verified'})
 for folder in ['records','frames','deliverables']:(guide/folder).mkdir(parents=True,exist_ok=True)
 for p in (root/'records').glob('*.json'):shutil.copy2(p,guide/'records'/p.name)
 for p in (root/'review').glob('*storyboard.jpg'):shutil.copy2(p,guide/'frames'/p.name)
 for p in (root/'deliverables').glob('*.srt'):shutil.copy2(p,guide/'deliverables'/p.name)
 if root==ROOT:
  for n in ['qc.json','subtitle_presence_checks.json']:shutil.copy2(root/'subtitled_review/records'/n,guide/'records'/('review_'+n))
 shutil.copy2(manifest,guide/manifest.name)
 location_note=('全編の字幕入り確認動画は `subtitled_review/deliverables/`、その他は `deliverables/`。' if root==ROOT else '動画6本と単体音声2本は `deliverables/`。本編v08は別フォルダ。')
 table='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in checks)
 (guide/'README.md').write_text(f'''# {title}

{body}

## 確認用動画と保存先

Mac：`{root}`。`deliverables/preview.html` はまとめて再生するページ。{location_note}
共有添付を同じフォルダに取得すれば `preview.html` から再生できます。

## 実測と保全

[{qcname}](records/{qcname})、[画面確認](records/visual_review.json)、[共有照合](records/sharing.json)。音の聴感は本人の試聴待ち。以前の版は保存済み。指定SSDは未同期。追加支出・YouTube投稿・Release公開なし。

## Claudeからの取得

[非公開Draft Release]({release['html_url']})／Release ID **{release['id']}**。全{len(checks)}件をRESTで再取得しSHA-256とサイズを照合済み。

```sh
gh api repos/{REPO}/releases/{release['id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{REPO}/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}
''')
 print('SHARED',release['id'],len(checks),flush=True)

def main():
 files=[ROOT/f'deliverables/EP001_Anubis_{lang}_v08_1080p30.{ext}' for lang in ['en','ja'] for ext in ['mp4','srt']]
 files += [ROOT/'deliverables'/n for n in ['EP001_audio_en.m4a','EP001_audio_ja.m4a','EP001_thumbnail_en.jpg','VOICE_CREDITS.txt']]
 files += [ROOT/f'subtitled_review/deliverables/EP001_Anubis_{lang}_v08_subtitled_review_1080p30.mp4' for lang in ['en','ja']]
 share(ROOT,'wom01-opening-pacing-v08-20261021','Quiet Origins：アヌビス v08（日本語冒頭の間・字幕調整）','''本人承認の申し送りを反映。日本語N01の既存5文をそのまま配置し、4か所の間を+0.8/+0.8/+1.0/+1.5秒。話し終わり27.622667秒、オープニングまで1.444秒。
映像ストリーム・英語音声・BGMはv07と同一。日本語N02以降の語りサンプルと130字幕も同一。全編682.700秒・20,481フレーム。通常版は字幕焼き込みなし、字幕入り確認用コピーを別添付。オープニング・エンドカードはまだ全編には挿入していない。日本語全編約−16 LUFS。''',files,REPO_ROOT/'new-channel/wom01_冒頭調整_v08_20261021','qc_v08.json')
 files=sorted((MROOT/'deliverables').glob('*.mp4'))+sorted((MROOT/'deliverables').glob('*.wav'))
 share(MROOT,'quiet-origins-motion-trial-v02-20261021','Quiet Origins：オープニング・エンドカード試作 v02','''オープニング既存音声を+7 dB、4秒・音色・フェード・映像を維持。単体約−22 LUFS。英日の字幕入り冒頭接続版を更新し、日本語はv08の間と字幕を反映。
エンドカード単体と英日末尾接続版はv01をバイト一致で継続使用（ファイル名もv01）。本編に挿入する前の試聴用。日本語の最後の問いの前（19.9〜21.7秒）の溜めと、ロゴ部分の音量を確認してください。''',files,REPO_ROOT/'new-channel/branding/20261021_共通映像試作_v02','qc_v02.json')
if __name__=='__main__':main()
