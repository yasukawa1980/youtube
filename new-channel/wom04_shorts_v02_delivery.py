"""Private draft delivery of EP004 Shorts; Release-ID REST verification."""
import argparse,csv,hashlib,html,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom04_shorts_v02 import ROOT,V1,REQUEST,read,save,sha,FPS
from wom02_delivery import api
GH='yasukawa1980/youtube'
TAG='qo-shorts-ep004-v02-20261024'

def docs():
 rows=read(ROOT/'records/shorts.json')['shorts'];pages=read(ROOT/'records/caption_manifest.json');qc=read(ROOT/'records/media_qc.json');assert qc['passed']
 def stamp(frame):
  ms=round(frame/FPS*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for s in rows:
  stem=f'QO_short_{s["episode"]}_{s["id"]}_v02';groups=[p for p in pages if p['short_id']==s['id']]
  (ROOT/f'deliverables/{stem}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(p["start_frame"])} --> {stamp(p["end_frame"])}\n'+ '\n'.join(p['lines']) for i,p in enumerate(groups))+'\n')
  for suffix in ['mid','every2s']:shutil.copy2(ROOT/f'review/{stem}_{suffix}.jpg',ROOT/f'deliverables/{stem}_{suffix}.jpg')
 (ROOT/'deliverables/scripts.txt').write_text('\n\n'.join(f'{s["episode"]} {s["id"]} — {s["title_ja"]}\n{s["text"]}' for s in rows)+'\n')
 fields=['id','name','duration_seconds','frames','lufs','true_peak_dbtp','voice_onset_normalized_stem_seconds','bgm_during_narration_dbfs','cta_seconds']
 with (ROOT/'deliverables/qc_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:s[k] for k in fields} for s in qc['media'])
 cards=''.join(f'<section><h2>{s["episode"]} {s["id"]} — {html.escape(s["title_ja"])}</h2><video controls preload="metadata" src="QO_short_{s["episode"]}_{s["id"]}_v02.mp4"></video><p>{s["duration_seconds"]:.2f}秒・英語字幕入り</p></section>' for s in rows)
 (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins Shorts v02</title><style>body{max-width:1100px;margin:28px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,h2{color:#d8b575}h2{font-size:18px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px}video{width:100%;max-height:72vh;background:#000}a{color:#d8b575}</style><h1>Quiet Origins / Pandora Shorts v02</h1><p>第4話パンドラ 3本。英語音声・英語字幕、縦1080×1920。確認用・未投稿。</p><main>'+cards+'</main><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})));</script></html>')
 with (ROOT/'deliverables/motion_qc.csv').open('w',newline='') as f:
  fields=['short_id','asset_id','frame_pairs','median','p95','p95_over_median','passed']
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for p in read(ROOT/'records/motion_qc.json')['checks']:
   w.writerow(dict(short_id=p['short_id'],asset_id=p['asset_id'],passed=p['passed'],**{k:p['measurement'][k] for k in fields[2:-1]}))
 for name in ['QO_short_EP004_P1_v02_about.jpg','QO_short_EP004_P2_v02_A12_motion.jpg','QO_short_EP004_P3_v02_A02_motion.jpg']:shutil.copy2(ROOT/'review'/name,ROOT/'deliverables'/name)
 print('DOCS COMPLETE',flush=True)


def selected_files():
    files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.suffix in ['.mp4','.srt','.jpg','.csv','.txt','.html'] and p.name!='SHA256SUMS_shared.txt')
    assert len(files)==20
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
            r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins：パンドラ ショート3本 v02',body='Claude指定の3点を修正。P1 aboutの字幕区切り、P2 A12の段落全体とPixideへの移動、P3 A02の胴の動物2段。3本の音声はv01とストリームSHA-256一致。切替・台本・札・出典を維持。19/20/19.667秒、字幕・動き・全編デコード検査済み。YouTube未投稿、非公開Draft。',draft=True))
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
    q=read(ROOT/'records/media_qc.json');share=read(ROOT/'records/sharing.json');assert q['passed'] and share['status']=='verified' and share['draft'] and len(share['assets'])==21
    repo=Path(__file__).resolve().parent;guide=repo/'wom_ショート確認版_EP004_v02_20261024'
    for d in ['records','frames','deliverables']:(guide/d).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,guide/'records'/p.name)
    for p in (ROOT/'review').glob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        shutil.copy2(p,guide/'frames'/p.name)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.csv','.srt','.txt']:shutil.copy2(p,guide/'deliverables'/p.name)
        if p.suffix=='.mp4':
            dest=ROOT.parent/p.name
            if dest.exists():assert sha(dest)==sha(p)
            else:shutil.copy2(p,dest)
    for id in ['P2','P3']:assert (ROOT/f'deliverables/QO_short_EP004_{id}_v02.srt').read_bytes()==(V1/f'deliverables/QO_short_EP004_{id}_v01.srt').read_bytes()
    table='\n'.join(f"| {m['id']} | {m['video_duration_seconds']:.3f} | {m['lufs']:.2f} | {m['true_peak_dbtp']:.2f} | 一致 |" for m in q['media'])
    motion='\n'.join(f"| {m['short_id']} / {m['asset_id']} | {m['measurement']['p95_over_median']:.6f} |" for m in read(ROOT/'records/motion_qc.json')['checks'])
    frames='\n'.join(f"- {m['id']}：[中央](frames/{Path(m['name']).stem}_mid.jpg)／[2秒おき](frames/{Path(m['name']).stem}_every2s.jpg)" for m in q['media'])
    assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in share['assets'])
    summary=f"""Claudeの修正依頼3点を反映。**3本の音声はv01とストリームSHA-256一致。台本・尺・切替時刻・素材・札・出典は維持。YouTube未投稿。**

Mac再生ページ：`{ROOT}/deliverables/preview.html`。[新規非公開Draft Release]({share['release_url']})、Release ID **{share['release_id']}**。21添付・{sum(a['bytes'] for a in share['assets']):,} bytesをRESTで再取得しSHA-256・サイズ一致。

| 本 | 秒 | LUFS | dBTP | v01音声との比較 |
|---|---:|---:|---:|---|
{table}
"""
    (guide/'README.md').write_text('# パンドラ ショート3本 v02\n\n'+summary+f"""
```sh
gh api repos/yasukawa1980/youtube/releases/{share['release_id']} --jq '.assets[] | [.id,.name]'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

{frames}

[aboutの字幕](frames/QO_short_EP004_P1_v02_about.jpg)／[A12の始点・中央・終点](frames/QO_short_EP004_P2_v02_A12_motion.jpg)／[A02の始点・中央・終点](frames/QO_short_EP004_P3_v02_A02_motion.jpg)。[音声一致検査](records/media_qc.json)／[動き](records/motion_qc.json)／[変更記録](records/revision.json)。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}
""")
    (repo/'wom_ショート制作結果_EP004_v02_20261024.md').write_text('# パンドラ ショートv02 修正結果（2026-10-24）\n\n[依頼](wom_ショート修正依頼_EP004_v02_20261024.md)（694574b）の3点を反映。[確認資料](wom_ショート確認版_EP004_v02_20261024/README.md)。\n\n'+summary+f"""
## 変更箇所

- P1：`made on Crete,` ／ `about one and a half`＋改行＋`meters tall.`。aboutの音素由来開始時刻に合わせ448フレーム（14.933秒）から後半字幕。映像本体はv01とストリーム一致。
- P2 A12：正規化[.04,.375,.74,.70]。目安より左へ.02・上へ.01広げ、見出しと左端の文字を保持。前景を最大1080×860枠へ縦横比維持で配置。0.97→1.00倍の小数拡大に、原画像y=.60（Pixide/Pixidem付近）が前景枠中央へ近づく上方向移動を加えた。終点も段落の横幅をほぼ全幅維持（半分以上）。下線・囲みなし。
- P3 A02：正規化[.08,.40,.92,.86]。胴の動物の帯2段を大きく表示。上端.40を守り、頸部の人物図像y.17〜.37は前景にもぼかし背景にも含めない。

切り出し以外の札・出典はv01画像の既存領域をコピー。A12以外の拡大方法はv01と同一。変更したA12・A02以外の5ショットはv01の符号化済み映像を再利用。切替はP1 12.600秒、P2 6.133/13.567秒、P3 5.333秒のまま。

## 検査

3本のAACストリームSHA-256をv01と照合して一致、再合成・再エンコードなし。P2・P3は字幕ASSとSRTもv01とバイト一致。P1は字幕本文の連結が台本と一致し、指定の改行を確認。全31字幕画面の輪郭・影込み範囲をx80〜880・y1150〜1450で検査。全編デコード・30fpsの全PTS・尺・音量を最終MP4で確認。

2秒おき30画像・中央3画像・A12/A02の始点中央終点・P1修正字幕を目視確認。全編の人による試聴は未実施。各ショットの全フレーム差分（前景内側70%、グレースケール平均絶対差、間引き・平滑化なし）を検査。

| 本／素材 | p95÷中央値 |
|---|---:|
{motion}

全件2.5以下。既存v01を保全し、Macショート直下にもv02 MP4をコピー。動画・音源はGitへ入れない。公開・投稿・投稿予約は実施していない。

再現：wom04_shorts_v02.py prepare → render、wom04_shorts_v02_qc.py verify → glyphs → motion → frames、画像確認後にwom04_shorts_v02_delivery.py docs → share → report。
""")
    print('REPORT READY',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','report']);a=p.parse_args();globals()[a.stage]()
