"""Private draft delivery of the single-shot Pandora revision."""
import argparse,hashlib,html,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom04_revision_v02 import ROOT,V1,REPO,REQUEST,read,save,sha
from wom02_delivery import api
GH='yasukawa1980/youtube';TAG='wom04-pandora-v02-20261023'


def docs():
    q=read(ROOT/'records/qc_v02.json');assert q['passed']
    assert read(ROOT/'records/motion_A04_v02.json')['passed'] and read(ROOT/'records/visual_review_v02.json')['passed']
    for p in (ROOT/'review').glob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        shutil.copy2(p,ROOT/'deliverables'/p.name)
    for name in ['qc_v02.json','motion_A04_v02.json','revision.json']:
        shutil.copy2(ROOT/'records'/name,ROOT/'deliverables'/name)
    cards=''.join(f'<section><h2>{label}</h2><video controls preload="metadata" src="EP004_Pandora_{lang}_v02_1080p30.mp4"></video><p><a href="EP004_Pandora_{lang}_v02_1080p30.srt">SRT字幕（v01と同じ）</a></p></section>' for lang,label in [('en','English'),('ja','日本語')])
    (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Pandora v02</title><style>body{max-width:1100px;margin:24px auto;padding:0 18px;background:#0c1820;color:#f4efdf;font:17px/1.7 system-ui}h1,h2,a{color:#d8b575}video{width:100%;max-height:70vh}section{margin:30px 0}img{width:100%}</style><h1>Quiet Origins / Pandora v02</h1><p>0:51〜1:02のA04だけを修正。音声・字幕と他のショットはv01のまま。未投稿。</p><h2>修正箇所だけ（11秒）</h2><video controls src="EP004_A04_v02_preview.mp4"></video><img src="A04_v02_composition.jpg">'+cards+'<script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})));</script></html>')
    print('DOCS READY',flush=True)


def share():
    qc=read(ROOT/'records/qc_v02.json');visual=read(ROOT/'records/visual_review_v02.json')
    assert qc['passed'] and visual['passed'] and read(ROOT/'records/motion_A04_v02.json')['passed']
    for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
    assert visual['video_sha256']==qc['files'][0]['sha256']
    files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.name!='SHA256SUMS_shared.txt')
    assert len(files)==18,len(files)
    check=ROOT/'deliverables/SHA256SUMS_shared.txt';check.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(check)
    state=ROOT/'records/sharing.json'
    r=api([f'repos/{GH}/releases/{read(state)["release_id"]}']) if state.exists() else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
    if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins：パンドラ v02（A04の切り出し修正）',body='A04の0:51〜1:02だけを修正。英日通常版429.566667秒・12887フレーム。A04以外12557フレームの復号画素がv01と一致。音声ストリーム・字幕・投稿情報・日本語WAVはv01と一致。A04の動きと切り出しを確認。11秒の部分確認動画を同梱。新規生成・追加支出・YouTube投稿なし。非公開Draftを維持。',draft=True))
    assert r['draft'] and r['published_at'] is None
    prior=read(state) if state.exists() else {};verified=prior.get('assets',prior.get('verified_assets',[]))
    save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='uploading',verified_assets=verified))
    for p in files:
        a=next((a for a in r['assets'] if a['name']==p.name),None)
        if a:assert a['state']=='uploaded' and a['size']==p.stat().st_size and a['digest']=='sha256:'+sha(p)
        else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
        print('UPLOADED',p.name,flush=True)
    r=api([f'repos/{GH}/releases/{r["id"]}']);assert r['draft'] and r['published_at'] is None and len(r['assets'])==len(files)
    checks=[]
    for p in files:
        a=next(a for a in r['assets'] if a['name']==p.name)
        cached=next((c for c in verified if c['asset_id']==a['id'] and c['sha256']==sha(p) and c['bytes']==p.stat().st_size and c['rest_download_verified']),None)
        if cached:checks.append(cached)
        else:
            for attempt in range(3):
                proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();count=0
                while True:
                    b=proc.stdout.read(1048576)
                    if not b:break
                    count+=len(b);h.update(b)
                ok=proc.wait()==0 and count==p.stat().st_size and h.hexdigest()==sha(p)==a['digest'].removeprefix('sha256:')
                if ok:break
            assert ok,p.name
            checks.append(dict(name=p.name,asset_id=a['id'],bytes=count,sha256=h.hexdigest(),rest_download_verified=True))
        save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='verifying',verified_assets=checks))
        print('REST VERIFIED',p.name,flush=True)
    save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='verified',assets=checks))
    print('SHARED',r['id'],len(checks),flush=True)


def report():
    shared=read(ROOT/'records/sharing.json');q=read(ROOT/'records/qc_v02.json');mo=read(ROOT/'records/motion_A04_v02.json');rev=read(ROOT/'records/revision.json')
    assert shared['status']=='verified' and shared['draft'] and q['passed'] and mo['passed']
    guide=REPO/'new-channel/wom04_確認版_v02_20261023'
    for d in ['records','frames','deliverables']:(guide/d).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,guide/'records'/p.name)
    for p in (ROOT/'review').glob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        shutil.copy2(p,guide/'frames'/p.name)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.srt','.md','.txt']:shutil.copy2(p,guide/'deliverables'/p.name)
    table='\n'.join(f"| {x['name']} | {x['asset_id']} | {x['bytes']:,} |" for x in shared['assets'])
    measures='\n'.join(f"| {f['name']} | {f['loudness']['input_i']} | {f['loudness']['input_tp']} | 一致 |" for f in q['files'])
    (guide/'README.md').write_text(f'''# Quiet Origins パンドラ v02

A04（0:51〜1:02）の切り出しだけ修正。英日通常版429.566667秒・12,887フレーム。**Claude確認待ち・YouTube未投稿。v01を保全。**

Mac：`{ROOT}/deliverables/preview.html`。修正箇所だけの11秒MP4も同梱。全編は通常版＋v01と同一の外部SRT。全編の字幕焼き込み版は再生成していない。

[新しい非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をRelease ID指定RESTで再取得し、SHA-256・サイズが一致。

```sh
gh api repos/{GH}/releases/{shared['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

[修正後の構図](frames/A04_v02_composition.jpg)／[修正前後](frames/A04_before_after.jpg)／[修正区間6時点](frames/A04_v02_six_frames.jpg)。[全フレーム照合・音声一致](records/qc_v02.json)／[動き](records/motion_A04_v02.json)／[切り出し座標](records/revision.json)。

再現：既存v01素材を用い `wom04_revision_v02.py prepare → render → verify → motion → preview`。画像を目視し `visual_review_v02.json` に対象のハッシュと結果を保存してから、`wom04_revision_v02_delivery.py docs → share → report`。原寸資料や音声モデルの再生成なし。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}
''')
    (REPO/'new-channel/wom04_制作結果_v02_20261023.md').write_text(f'''# 第4話「パンドラ」v02 修正結果（2026-10-23）

[Claudeの修正依頼](wom04_Claude確認_v01_20261023.md)どおり、P03・ショット1のA04だけを切り出し直した。[再生・取得・確認画像](wom04_確認版_v02_20261023/README.md)。**v01保全・Claude確認待ち・YouTube未投稿。予約日時も未変更。**

## 切り出し

原画像3259×3119pxの正規化座標を `[0.660,0.025,0.968,0.490]` から **`[0.770,0.025,0.968,0.490]`** へ変更。ピクセルでは `{rev['crop_pixels']}`。槍より左にある正面向きの像を外し、右の松明を持つ人物と、その後ろの兜の人物を残した。ぼかし背景も同じ切り出しから作成。生成加工・塗りつぶしはしていない。

縦820pxの枠を維持し、前景は365×820px、画面座標 `{rev['art_box']}`。上部110pxはv01の画素をそのままコピーしたため、札・出典・書体・位置は同一。尺11秒（0:51〜1:02、330フレーム）と3%の小数座標による拡大方式を維持。

実際の完成動画の51/53/55/57/59/61.966667秒を抽出して目視確認し、左の像が前景にもぼかし背景にも映っていないこと、松明・右の人物・後ろの兜が残ることを確認。動きは全329フレーム対、前景の内側70%のグレースケール平均絶対差で **p95÷中央値={mo['measurement']['p95_over_median']:.6f} ≤2.5**。時間方向の間引き・平滑化・サンプル除去なし。

## 変更範囲の実測

英語通常版のv01/v02を全フレーム復号し、YUV420pの全画素MD5を比較。12,887フレーム中、異なるのはA04の **frame 1530〜1859（330枚）だけ**。それ以外の **12,557枚は画素一致**。共通オープニング・エンドカードを含む他の30ショットは既存の圧縮データを無変換で再利用。

英日通常版の圧縮映像ストリームSHA-256が一致し、同じ修正映像であることを確認。英日それぞれのAACはv01のMP4から無変換コピーし、音声ストリームSHA-256が一致。SRT（英98・日99件）・投稿情報・日本語WAVはv01とバイト一致。音声の再合成・音量調整は行っていない。

| 通常版 | LUFS | dBTP | v01との音声 |
|---|---:|---:|---|
{measures}

両言語とも429.566667秒・12,887フレーム・1920×1080・30fps。全編デコード・全PTSを確認し、映像は1/15360秒で512tick刻み、音声は48kHz・20,619,200サンプルのまま。共通エンドカードの最後10秒、英日字幕・チャプター・サムネ・投稿情報は維持。

## 共有

Mac：`{ROOT}`。新規[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付・{sum(x['bytes'] for x in shared['assets']):,} bytesをRelease ID指定RESTで再取得し、SHA-256・サイズ一致。英日通常版・同一SRT・同一日本語WAV・サムネ2案・同一投稿情報・出典・確認JPG・検査JSON・再生ページ・11秒の部分確認動画を含む。

11秒の部分確認動画は画像確認用で、投稿用は英語の通常版。全編の字幕焼き込み版は再生成していない。v01の資料・メディアと非公開Draftは残した。新しいAI生成・契約・購入・YouTube投稿・予約操作はなし。本修正での全編の聴感確認は未実施。次はClaudeが切り出しと同一性を確認し、合格後に別の投稿依頼へ進む。
''')
    print('REPORT READY',guide,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','report']);a=p.parse_args();globals()[a.stage]()
