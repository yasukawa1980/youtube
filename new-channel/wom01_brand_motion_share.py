"""Share the local brand-motion trial through a non-public Draft Release."""
import os,json,subprocess,hashlib,shutil
from pathlib import Path
from PIL import Image
from wom01_multilingual_render import read,save,sha
R=Path(os.environ['QO_MOTION_ROOT']);P=Path(__file__).resolve().parent
GUIDE=P/'branding/20261021_共通映像試作_v01';REPO='yasukawa1980/youtube';TAG='quiet-origins-motion-trial-v01-20261021'

def api(args,data=None):return json.loads(subprocess.check_output(['gh','api',*args],input=json.dumps(data).encode() if data else None))

def preview():
 def card(title,name,desc):return f'<article><h3>{title}</h3><video controls playsinline preload="metadata" src="{name}"></video><p>{desc}</p><a href="{name}">動画を直接開く</a></article>'
 cards=card('オープニング · 4秒','Quiet_Origins_opening_trial_v01.mp4','Qとタイトルが順に現れます。穏やかな低音と、小さな澄んだ一音。')+card('エンドカード · 20秒','Quiet_Origins_endcard_trial_v01.mp4','文字とQは固定。背景の光だけがゆっくり動き、音が最後の5秒で消えます。')
 jp=card('冒頭の接続 · 日本語 · 約56秒','EP001_ja_opening_connection_trial_v01.mp4','29.07秒でオープニングへ。33.07秒から本編に戻ります。')+card('末尾の接続 · 日本語 · 40秒','EP001_ja_endcard_connection_trial_v01.mp4','出典・音声クレジットとお礼の後、20秒地点からエンドカードへ移ります。')
 en=card('Opening connection · English','EP001_en_opening_connection_trial_v01.mp4','The ident starts at 29.07 seconds; the episode resumes at 33.07 seconds.')+card('Ending connection · English','EP001_en_endcard_connection_trial_v01.mp4','Credits and thanks, followed by the 20-second end card.')
 html='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiet Origins — 動きと音の試作</title><style>body{margin:0;background:#0c1820;color:#f4efdf;font:16px/1.8 system-ui}main{max-width:1380px;padding:32px;margin:auto}h1{font:36px Georgia}h2{color:#d8b575;font-size:22px;margin-top:40px}h3{font-size:17px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:30px}video{width:100%;background:#000;border:1px solid #30434c}a,summary{color:#d8b575}small{color:#b0bfc3}summary{cursor:pointer;font-size:20px;margin:25px 0}article{min-width:0}@media(max-width:850px){.grid{grid-template-columns:1fr}}</style><main><small>動画試作 v01 · 2026-10-21</small><h1>Quiet Origins</h1><p>音付きの試作です。再生ボタンを押して、表示の速さ・音の大きさ・本編とのつながりをご確認ください。</p><h2>まずは共通映像だけ</h2><div class="grid">'''+cards+'''</div><h2>アヌビスにつないだ確認版（字幕入り）</h2><div class="grid">'''+jp+'''</div><details><summary>英語版の接続も確認する</summary><div class="grid">'''+en+'''</div></details><p><small>エンドカード左側は、今後の動画案内用の余白です。クリックできる要素はYouTube側で設定するため、この試作には含みません。今回の制作は無料・ローカル。元のv07は保全し、全編への反映・YouTube投稿は行っていません。</small></p></main><script>document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(o=>{if(o!==v)o.pause()})))</script></html>'''
 (R/'deliverables/preview.html').write_text(html)

def main():
 qc=read(R/'records/qc.json');assert qc['passed'] and len(qc['files'])==6 and read(R/'records/additional_checks.json')['passed'] and read(R/'records/visual_review.json')['passed']
 preview()
 files=sorted((R/'deliverables').glob('*.mp4'))+sorted((R/'deliverables').glob('*.wav'))+[R/'deliverables/preview.html']
 manifest=R/'deliverables/SHA256SUMS_shared.txt';manifest.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(manifest)
 release=next((x for x in api([f'repos/{REPO}/releases']) if x['tag_name']==TAG),None)
 if release is None:
  release=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins — 4秒オープニング・20秒エンドカード動画試作 v01','draft':True,'body':'本人承認により無料・ローカルで制作。音付き単体2本と英日それぞれの冒頭・末尾接続4本、WAV2本、比較HTML、SHA256。全6動画1920x1080/30fps。v07は保全。クリック要素の設定・全編反映・YouTube投稿は未実施。資料: new-channel/branding/20261021_共通映像試作_v01/README.md。preview.htmlとMP4を同じフォルダに保存して開く。'})
 assert release['draft']
 for p in files:
  a=next((x for x in release['assets'] if x['name']==p.name),None)
  if a:assert a['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',REPO],check=True)
  print('UPLOADED',p.name,flush=True)
 release=api([f'repos/{REPO}/releases/{release["id"]}']);assert release['draft'];checks=[]
 for p in files:
  a=next(x for x in release['assets'] if x['name']==p.name)
  data=subprocess.check_output(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPO}/releases/assets/{a["id"]}']);assert hashlib.sha256(data).hexdigest()==sha(p)
  checks.append({'name':p.name,'bytes':len(data),'asset_id':a['id'],'sha256':sha(p),'rest_verified':True});print('VERIFIED',p.name,flush=True)
 save(R/'records/sharing.json',{'release_id':release['id'],'url':release['html_url'],'draft':True,'assets':checks})
 for d in ['records','frames']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
 for p in (R/'records').glob('*.json'):shutil.copy2(p,GUIDE/'records'/p.name)
 for n in ['opening_storyboard.jpg','endcard_storyboard.jpg','connection_ja.jpg','connection_en.jpg','endcard_layout_guide.jpg']:
  im=Image.open(R/'review'/n);im.thumbnail((1280,1280));im.save(GUIDE/'frames'/n,quality=88)
 shutil.copy2(manifest,GUIDE/manifest.name)
 rows='\n'.join(f"| {f['name']} | {f['duration_seconds']:.3f} | {f['frames']} | {f['audio']['input_i']} | {f['audio']['input_tp']} |" for f in qc['files'])
 assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in checks)
 (GUIDE/'README.md').write_text(f'''# Quiet Origins：オープニング・エンドカードの動画試作 v01

2026-10-21。本人の「進めて下さい」により、4秒オープニング・20秒エンドカードと、アヌビスに接続した英日確認版を制作。**本人の試聴・方向確認待ち。全編への反映は未実施。**

## 再生

Mac保存先：`{R}`。
`deliverables/preview.html` を開くと6本を再生できる。動画を直接開く場合も `deliverables/`。

- `Quiet_Origins_opening_trial_v01.mp4`：4秒、音付き。
- `Quiet_Origins_endcard_trial_v01.mp4`：20秒、音付き。
- `EP001_ja_opening_connection_trial_v01.mp4`：日本語の冒頭接続、55.833秒。
- `EP001_ja_endcard_connection_trial_v01.mp4`：日本語の末尾接続、40秒。
- 英語の接続確認版は同じ名前の `ja` を `en` にした2本。
- 単体の音はPCM24bit・48kHz・ステレオWAVでも保存。

## 反映したデザインと音

- 採用済みQアイコンの金色の画素を、動画合成用のアルファマットで取り出して使用。Qを再生成・描き直していない。原素材のSHA-256は [制作依頼記録](records/request.json)。
- 濃紺・金色・アイボリーを維持。背景の地図風の等高線・航路と光はコードで制作した抽象模様で、特定の地域を表さない。静止画ラフの装飾をそのまま動かしたものではない。
- オープニング：Qを0.18〜1.15秒、タイトルを1.05〜2.05秒にフェードイン。光が静かに横切る。全体を一枚の画像としてズームする動きは使っていない。
- エンドカード：タイトル・Q・締めの言葉は固定。背景の光だけがゆっくり変化する。配置確認用の枠は [別のガイド画像](frames/endcard_layout_guide.jpg) に分離し、動画には焼き込んでいない。左側は今後の動画案内用の余白。クリック要素は未設定。
- 音はローカルで新規合成したD/A系の穏やかな音と短い澄んだ音。外部サービス・購入・追加の画像生成は使用していない。単体WAVの実測は冒頭−29.00 LUFS、末尾−30.00 LUFS。末尾の音は最後の5秒でフェードアウト。MP4の測定は下表。

## 本編との接続

- 冒頭はv07の0〜51.833秒を使用し、N01/N02の段落境界29.067秒に4秒のオープニングを挿入。接続版は33.067秒で本編に戻る。語りや字幕を途中で分割していない。切り口の小さな音量フェードだけを加えた。
- 末尾はv07の658〜678.7秒（クレジットとお礼）を使用し、678秒から0.7秒でエンドカードへ切り替える。日本語の最後の発話は677.691秒で終わる。接続確認版は40秒。旧末尾の音楽だけの4秒はこの抜粋では省くが、元のv07は変更していない。
- 字幕は既存の字幕入り確認版を使い、元の画面と一緒に移動。ロゴ中に本編字幕が残っていないことを英日で確認。

## 検品

全6動画：1920×1080・30fps、全編デコード成功、PTS間隔一定、クリッピングなし。単体音声の始端・終端の5msも小さな音量で終わることを確認。元v07の共有10ファイルはSHA-256一致で保全を検証。画像の確認は実際のMP4抽出フレームで実施。聴感・全編の人による再生は未確認で、本人の試聴を待つ。

| 動画 | 秒 | フレーム | LUFS | dBTP |
|---|---:|---:|---:|---:|
{rows}

[冒頭の動き](frames/opening_storyboard.jpg)／[末尾の画面](frames/endcard_storyboard.jpg)／[日本語接続](frames/connection_ja.jpg)／[英語接続](frames/connection_en.jpg)。

[検品記録](records/qc.json)／[フェード・字幕検査](records/additional_checks.json)／[画面確認](records/visual_review.json)／[接続時刻](records/connection_plan.json)。

## Claudeへの共有

[非公開Draft Release]({release['html_url']})、Release ID **{release['id']}**。全{len(checks)}添付をRESTで再取得してSHA-256一致。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}

```sh
gh api repos/{REPO}/releases/{release['id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{REPO}/releases/assets/ASSET_ID > FILE_NAME
```

コード：`new-channel/wom01_brand_motion.py`、`wom01_brand_motion_review.py`、`wom01_brand_motion_share.py`。出力先は環境変数 `QO_MOTION_ROOT` で指定し、prepare → pictures → sound → connections → verify の順に実行。画面検査後に共有する。

全編制作・投稿・Studio設定・追加支出はなし。指定SSD ESD-EPBへの同期は未実施。
''')
 print('SHARED',release['id'],len(checks),flush=True)
if __name__=='__main__':main()
