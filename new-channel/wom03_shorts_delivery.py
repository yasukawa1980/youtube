"""Private draft delivery of EP003 Shorts; Release-ID REST verification."""
import argparse,csv,hashlib,html,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom03_shorts import ROOT,read,save,sha,FPS
from wom02_delivery import api
GH='yasukawa1980/youtube'
TAG='qo-shorts-ep003-v01-20261023'

def docs():
 rows=read(ROOT/'records/shorts.json')['shorts'];pages=read(ROOT/'records/caption_manifest.json');qc=read(ROOT/'records/media_qc.json');assert qc['passed']
 def stamp(frame):
  ms=round(frame/FPS*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for s in rows:
  stem=f'QO_short_{s["episode"]}_{s["id"]}_v01';groups=[p for p in pages if p['short_id']==s['id']]
  (ROOT/f'deliverables/{stem}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(p["start_frame"])} --> {stamp(p["end_frame"])}\n'+ '\n'.join(p['lines']) for i,p in enumerate(groups))+'\n')
  for suffix in ['mid','every2s']:shutil.copy2(ROOT/f'review/{stem}_{suffix}.jpg',ROOT/f'deliverables/{stem}_{suffix}.jpg')
 (ROOT/'deliverables/scripts.txt').write_text('\n\n'.join(f'{s["episode"]} {s["id"]} — {s["title_ja"]}\n{s["text"]}' for s in rows)+'\n')
 fields=['id','name','duration_seconds','frames','lufs','true_peak_dbtp','voice_onset_normalized_stem_seconds','bgm_during_narration_dbfs','cta_seconds']
 with (ROOT/'deliverables/qc_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:s[k] for k in fields} for s in qc['media'])
 cards=''.join(f'<section><h2>{s["episode"]} {s["id"]} — {html.escape(s["title_ja"])}</h2><video controls preload="metadata" src="QO_short_{s["episode"]}_{s["id"]}_v01.mp4"></video><p>{s["duration_seconds"]:.2f}秒・英語字幕入り</p></section>' for s in rows)
 (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins Shorts v01</title><style>body{max-width:1100px;margin:28px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,h2{color:#d8b575}h2{font-size:18px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px}video{width:100%;max-height:72vh;background:#000}a{color:#d8b575}</style><h1>Quiet Origins / Medusa Shorts v01</h1><p>第3話メドゥーサ 3本。英語音声・英語字幕、縦1080×1920。確認用・未投稿。</p><main>'+cards+'</main><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})));</script></html>')
 with (ROOT/'deliverables/motion_qc.csv').open('w',newline='') as f:
  fields=['short_id','asset_id','frame_pairs','median','p95','p95_over_median','passed']
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for p in read(ROOT/'records/motion_qc.json')['checks']:
   w.writerow(dict(short_id=p['short_id'],asset_id=p['asset_id'],passed=p['passed'],**{k:p['measurement'][k] for k in fields[2:-1]}))
 print('DOCS COMPLETE',flush=True)


def selected_files():
    files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.suffix in ['.mp4','.srt','.jpg','.csv','.txt','.html'] and p.name!='SHA256SUMS_shared.txt')
    assert len(files)==17
    return files

def share():
    qc=read(ROOT/'records/media_qc.json')
    visual=read(ROOT/'records/visual_review.json')
    assert all(read(ROOT/'records'/n)['passed'] for n in ['media_qc.json','visual_review.json','motion_qc.json','subtitle_qc.json','asset_usage.json'])
    for m in qc['media']:
        assert sha(ROOT/'deliverables'/m['name'])==m['sha256']==visual['video_sha256'][m['id']]
    files=selected_files()
    check=ROOT/'deliverables/SHA256SUMS_shared.txt'
    check.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(check)
    state=ROOT/'records/sharing.json'
    if state.exists(): r=api([f'repos/{GH}/releases/{read(state)["release_id"]}'])
    else:
        r=next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
        if r is None:
            r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins：メドゥーサ ショート3本 v01',body='本人依頼・Claudeの確定台本を維持。英語Kokoro af_heart、縦1080×1920・30fps、19.333/17.100/20.000秒。英語字幕入り。7素材各1回、M3は顔だけで背景にも刃・首元を含めない。−14LUFS付近、字幕・全フレームの動き・全編デコードを検査。YouTube未投稿、非公開Draftを維持。',draft=True))
    assert r['draft'] and r['published_at'] is None
    prior=read(state) if state.exists() else {}
    verified=prior.get('assets',prior.get('verified_assets',[]))
    save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='uploading',verified_assets=verified))
    for p in files:
        a=next((a for a in r['assets'] if a['name']==p.name),None)
        if a: assert a['state']=='uploaded' and a['size']==p.stat().st_size and a['digest']=='sha256:'+sha(p)
        else: subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
        print('UPLOADED',p.name,flush=True)
    r=api([f'repos/{GH}/releases/{r["id"]}'])
    assert r['draft'] and r['published_at'] is None and len(r['assets'])==len(files)
    checks=[]
    for p in files:
        a=next(a for a in r['assets'] if a['name']==p.name)
        cached=next((c for c in verified if c['asset_id']==a['id'] and c['sha256']==sha(p) and c['bytes']==p.stat().st_size and c['rest_download_verified']),None)
        if cached: checks.append(cached)
        else:
            for attempt in range(3):
                proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE)
                h=hashlib.sha256();count=0
                while True:
                    b=proc.stdout.read(1048576)
                    if not b: break
                    count+=len(b);h.update(b)
                ok=proc.wait()==0 and count==p.stat().st_size and h.hexdigest()==sha(p)==a['digest'].removeprefix('sha256:')
                if ok: break
            assert ok,p.name
            checks.append(dict(name=p.name,asset_id=a['id'],bytes=count,sha256=h.hexdigest(),rest_download_verified=True))
        save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='verifying',verified_assets=checks))
        print('REST VERIFIED',p.name,flush=True)
    save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='verified',assets=checks))
    print('SHARED',r['id'],len(checks),flush=True)

def report():
    shared=read(ROOT/'records/sharing.json'); assert shared['status']=='verified' and shared['draft']
    qc=read(ROOT/'records/media_qc.json'); motion=read(ROOT/'records/motion_qc.json')
    assert qc['passed'] and motion['passed'] and len(shared['assets'])==18
    repo=Path(__file__).resolve().parent
    guide=repo/'wom_ショート確認版_EP003_v01_20261023'
    for d in ['records','frames','deliverables']: (guide/d).mkdir(parents=True,exist_ok=True)
    for name in ['narration.json','shorts.json','audio_qc.json','visual_manifest.json','media_qc.json',
                 'motion_qc.json','subtitle_qc.json','asset_usage.json','frame_review.json',
                 'visual_review.json','sharing.json','reading_correction.json','caption_manifest.json']:
        shutil.copy2(ROOT/'records'/name,guide/'records'/name)
    for p in (ROOT/'review').glob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        shutil.copy2(p,guide/'frames'/p.name)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.srt','.csv','.txt']: shutil.copy2(p,guide/'deliverables'/p.name)
    table='\n'.join(f"| {s['id']} | {s['video_duration_seconds']:.3f} | {s['frames']} | {s['lufs']:.2f} | {s['true_peak_dbtp']:.2f} | {s['voice_onset_normalized_stem_seconds']:.2f} | {s['cta_seconds']:.3f} |" for s in qc['media'])
    moves='\n'.join(f"| {m['short_id']} / {m['asset_id']} | {m['measurement']['p95_over_median']:.6f} | 合格 |" for m in motion['checks'])
    assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in shared['assets'])
    frames='\n'.join(f"- {s['id']}：[中央](frames/{Path(s['name']).stem}_mid.jpg)／[2秒おき](frames/{Path(s['name']).stem}_every2s.jpg)" for s in qc['media'])
    (guide/'README.md').write_text(f'''# Quiet Origins メドゥーサ ショート3本 v01

英語音声・英語字幕入り。縦1080×1920・30fps。**YouTube未投稿。Claudeと本人の確認待ち。**

Mac：`{ROOT}/deliverables/preview.html` で3本を再生できる。Gitには動画を入れていない。Claudeは以下の非公開Draftから取得する。

[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全18添付をRelease ID指定RESTで再取得し、SHA-256とバイト数が一致した。

```sh
gh api repos/{GH}/releases/{shared['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

| ID | 秒 | フレーム | LUFS | dBTP | 声の開始秒 | 末尾案内秒 |
|---|---:|---:|---:|---:|---:|---:|
{table}

{frames}

[使用一覧](deliverables/asset_usage.csv)／[台本](deliverables/scripts.txt)／[字幕検査](records/subtitle_qc.json)／[動き](records/motion_qc.json)／[共有照合](records/sharing.json)。SRTは検品用で、動画には同じ字幕が焼き込み済み。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}
''')
    (repo/'wom_ショート制作結果_EP003_20261023.md').write_text(f'''# Quiet Origins 第3話メドゥーサ ショート制作結果（2026-10-23）

[Claudeの制作依頼](wom_ショート制作依頼_EP003_20261023.md)（コミット `d6eef03`）どおり、英語ショートM1〜M3を制作。[再生・取得・確認画像](wom_ショート確認版_EP003_v01_20261023/README.md)。**YouTube未投稿。既存の本編と投稿予約は変更していない。**

| ID | 秒 | フレーム | LUFS | dBTP | 声の開始秒 | 末尾案内秒 |
|---|---:|---:|---:|---:|---:|---:|
{table}

3本とも1080×1920・30fps、CRF18。全編デコード、正確な30fpsの全PTS、15〜20秒、ピーク−1dBTP以下を最終MP4で検査。声の開始は正規化した語りステムの10ms窓・−50dBFSで測定し、0.3秒以内。人による全編試聴は未実施。

## 音声と台本

依頼書の3台本を言い換え・追加せず、Kokoro af_heart、本編と同じspeed=0.82・sentence_pause=0.3・clause_pause=0.12で新規生成。Hesiod・Theogonyは本編の指定音素を使用。Hesiod’sの所有格が単独の文字Sとして音素化される点を検出し、表示文を変えず `hˈiːsiədz` に補正した。読み上げの加速・ピッチ変更なし。

ネイティブの語りはM1 17.322667秒、M2 15.086625秒、M3 18.436000秒。最後の案内 `Full story on Quiet Origins` は声では読まない。M1・M2は末尾2秒、M3は20秒以内に収めるため末尾1.533秒（依頼の「約2秒」）。オープニング・エンドカードなし。

本編BGMステムの120/140/160秒から、ブランド区間を避けた部分を使用。語りの下は各−33.5dBFS。全体は−14LUFS付近。M1はAAC化後のピークを抑えるため、192kHzでピークリミッター（天井−3dBFS、遅延補償あり）を適用し、最終AACとMP4で再測定した。M2・M3は追加リミッターなし。音声の速度は維持。

## 字幕と画面

字幕本文は台本と文字列一致。音素時刻を語へ対応させて切替を設定したモデル由来の推定であり、全字幕の聴感同期を確認済みとはしていない。1行最大5語・2行以内。案内を含む全30画面を同じlibass・フォントで描画し、輪郭と影を含めx80〜880・y1150〜1450内に収まることを検査。札と出典はy140〜260。

前景はy270〜1130、縦横比を保って大きく表示し、余白は同じ素材のぼかし背景。0.97→1.00倍の小数座標で緩やかに拡大する。素材と札・出典は2秒おきの画像で確認した。

- M1：R03 夜の海と岩場 → A05 走るゴルゴンの杯。札は作品名と出典のみで、三姉妹という説明札は加えていない。
- M2：A04 屋根瓦 → A08 眼杯の内側 → A26 ゴルゴンの盾の浮彫。各画像を1回だけ表示。
- M3：A01 眠る顔だけ → A17 穏やかな顔の屋根瓦。A01は追加画像view 2の正規化座標 `[0.700,0.438,0.835,0.513]` を切り出し、全体は表示しない。ぼかし背景にもこの顔の切り出しだけを使うため、刃・首元を含めない。

原寸ファイル7点を既存台帳のSHA-256と照合。3本の間にも各ショート内にも同じ素材の重複なし。博物館6点は既存のMet PD/CC0記録を継承、R03は既存のAI再現画。新規AI生成・追加購入なし。

## 動きと共有

7ショットの全30fpsフレームについて、前景内側70%のグレースケール平均絶対差を測定。札・字幕を除き、時間方向の間引き・サンプル除去・平滑化なし。全件p95÷中央値≤2.5。

| ショート / 素材 | p95÷中央値 | 結果 |
|---|---:|---|
{moves}

Mac保存先：`{ROOT}`。新規[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。MP4×3・SRT×3・中央JPG×3・2秒おきJPG×3・CSV×3・台本・再生ページ・チェックサムの全18添付、合計{sum(a['bytes'] for a in shared['assets']):,} bytes。Release ID指定RESTで全添付を取得し直し、全体SHA-256とサイズが一致。Releaseは未公開。Gitには報告・再現スクリプト・検査JSON・縮小JPG・字幕と表だけを共有する。

次はClaudeの確認と本人の試聴。その後の投稿は別依頼で行う。参考日程（10/30・11/3・11/5）は未登録。
''')
    print('REPORT READY',guide,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','report']);a=p.parse_args();globals()[a.stage]()
