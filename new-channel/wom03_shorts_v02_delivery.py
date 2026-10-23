"""EP003 Shorts v02: private draft and revision-focused delivery report."""
import argparse,csv,hashlib,html,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom03_shorts_v02 import ROOT,V1,REQUEST,read,save,sha,FPS
from wom02_delivery import api
GH='yasukawa1980/youtube'
TAG='qo-shorts-ep003-v02-20261023'

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
 (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins Shorts v02</title><style>body{max-width:1100px;margin:28px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,h2{color:#d8b575}h2{font-size:18px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px}video{width:100%;max-height:72vh;background:#000}a{color:#d8b575}</style><h1>Quiet Origins / Medusa Shorts v02</h1><p>第3話メドゥーサ 3本。英語音声・英語字幕、縦1080×1920。確認用・未投稿。</p><main>'+cards+'</main><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})));</script></html>')
 with (ROOT/'deliverables/motion_qc.csv').open('w',newline='') as f:
  fields=['short_id','asset_id','frame_pairs','median','p95','p95_over_median','passed']
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for p in read(ROOT/'records/motion_qc.json')['checks']:
   w.writerow(dict(short_id=p['short_id'],asset_id=p['asset_id'],passed=p['passed'],**{k:p['measurement'][k] for k in fields[2:-1]}))
 for name in ['QO_short_EP003_M2_v02_cut_check.jpg','QO_short_EP003_M3_v02_450_BCE.jpg']:
  shutil.copy2(ROOT/'review'/name,ROOT/'deliverables'/name)
 print('DOCS COMPLETE',flush=True)


def selected_files():
    files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.suffix in ['.mp4','.srt','.jpg','.csv','.txt','.html'] and p.name!='SHA256SUMS_shared.txt')
    assert len(files)==19
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
            r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins：メドゥーサ ショート3本 v02',body='Claudeの修正依頼に従いM2の素材切替とM3の450 BCE字幕だけを修正。M1はv01とバイト一致、3本の音声はv01とストリーム一致。19.333/17.100/20.000秒。字幕枠・全フレームの動き・全編デコードを検査。YouTube未投稿、非公開Draftを維持。',draft=True))
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
    shared=read(ROOT/'records/sharing.json');q=read(ROOT/'records/media_qc.json')
    assert shared['status']=='verified' and shared['draft'] and len(shared['assets'])==20 and q['passed']
    for id in ['M1','M2']:
        assert (ROOT/f'deliverables/QO_short_EP003_{id}_v02.srt').read_bytes()==(V1/f'deliverables/QO_short_EP003_{id}_v01.srt').read_bytes()
    rev=read(ROOT/'records/revision.json');motion=read(ROOT/'records/motion_qc.json')
    repo=Path(__file__).resolve().parent;guide=repo/'wom_ショート確認版_EP003_v02_20261023'
    for name in ['records','frames','deliverables']:(guide/name).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,guide/'records'/p.name)
    for p in (ROOT/'review').glob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        shutil.copy2(p,guide/'frames'/p.name)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.csv','.srt','.txt']:shutil.copy2(p,guide/'deliverables'/p.name)
    table='\n'.join(f"| {m['id']} | {m['video_duration_seconds']:.3f} | {m['frames']} | {m['lufs']:.2f} | {m['true_peak_dbtp']:.2f} | 一致 |" for m in q['media'])
    moves='\n'.join(f"| {m['short_id']} / {m['asset_id']} | {m['measurement']['p95_over_median']:.6f} | 合格 |" for m in motion['checks'])
    assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in shared['assets'])
    frames='\n'.join(f"- {m['id']}：[中央](frames/{Path(m['name']).stem}_mid.jpg)／[2秒おき](frames/{Path(m['name']).stem}_every2s.jpg)" for m in q['media'])
    summary=f'''M2の素材切替・M3の年代字幕だけを修正。M1はv01とMP4全体が一致、3本の音声はv01とストリーム一致。**YouTube未投稿。v01を保全。**

Mac：`{ROOT}/deliverables/preview.html`。[新しい非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全20添付のSHA-256とサイズをRelease ID指定RESTで照合済み。動画はGitに含めない。

| ID | 秒 | フレーム | LUFS | dBTP | v01との音声 |
|---|---:|---:|---:|---:|---|
{table}
'''
    (guide/'README.md').write_text('# メドゥーサ ショート3本 v02\n\n'+summary+f'''
```sh
gh api repos/{GH}/releases/{shared['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

{frames}

[M2切替の前後フレーム](frames/QO_short_EP003_M2_v02_cut_check.jpg)／[M3の450 BCE](frames/QO_short_EP003_M3_v02_450_BCE.jpg)。[変更時刻](records/revision.json)／[音声一致](records/media_qc.json)／[字幕枠](records/subtitle_qc.json)／[全フレームの動き](records/motion_qc.json)。

再現：既存v01メディアを使い `wom03_shorts_v02.py prepare → render`、`wom03_shorts_v02_qc.py verify → motion → glyphs → frames`。画像確認を `visual_review.json` に記録後、`wom03_shorts_v02_delivery.py docs → share → report`。音声の再合成・再エンコードなし。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}
''')
    (repo/'wom_ショート制作結果_EP003_v02_20261023.md').write_text('''# メドゥーサ ショート v02 修正結果（2026-10-23）

[Claudeの修正依頼](wom_ショート修正依頼_EP003_v02_20261023.md)（取得時コミット `0acdc19`）の2点を反映。[確認画像・取得先](wom_ショート確認版_EP003_v02_20261023/README.md)。既存の本編と投稿予約は変更していない。

'''+summary+f'''
## M2の切替

v01のKokoro音素から割り当てた語時刻を、最も近い30fpsフレームへ丸めて採用。聴感で確定した時刻とはしていない。

| 対象 | 音素由来の語の開始秒 | 候補フレームと秒 | 結果 |
|---|---:|---|---|
| drinking cups | {rev['drinking_onset_native_seconds']:.6f} | {rev['drinking_start_frame']} / {rev['drinking_start_seconds']:.6f} | A08をここから表示 |
| and shields | {rev['and_shields_onset_native_seconds']:.6f} | {rev['and_shields_candidate_frame']} / {rev['and_shields_candidate_seconds']:.6f} | 杯が{rev['candidate_eye_cup_seconds']:.3f}秒になるため不採用 |
| A26：依頼の例外 | v01の境界を継承 | {rev['shield_start_frame']} / {rev['shield_start_seconds']:.6f} | 元の時刻を採用 |

A04はframe 0〜207、A08は208〜280（6.933333〜9.366667秒未満、**2.433333秒**）、A26は281〜512。A04は「on roof tiles,」を含む字幕の終わりまで残る。実際のMP4の境界前後4フレーム（207/208/280/281）で、札と素材の切替を目視確認。

## M3の字幕

旧 `in Athens around 450` と `BCE, she sleeps with` を次の2画面へ変更し、SRTも同じ区切りにした。

- frame 166〜271（5.533333〜9.066667秒未満）：`in Athens` ／ `around 450 BCE,`
- frame 272〜298（9.066667〜9.966667秒未満）：`she sleeps with`

450とBCEは同じ画面・同じ行。台本全文の語・句読点・順番と、それ以外の字幕画面は維持。1行最大5語・2行以内、輪郭と影を含めx80〜880・y1150〜1450に全30字幕画面が収まることを、同じlibass・フォントで検証。

## 維持と再検証

v01のAACを無変換コピーし、全3本の音声ストリームSHA-256一致を確認。語り・BGM・音量の再処理なし。M1はMP4全体のSHA-256一致、M1/M2のSRTはバイト一致、M2のASSも一致。M3の字幕を入れる前の映像ストリームはv01と一致。素材7点・札・出典・0.97→1.00倍の小数座標拡大は同じ。素材の重複なし。M3は安全な顔の切り出しを維持。

最終3本の1080×1920・30fps・全PTS・全編デコード・音量とピークを検査。7ショット全30fpsフレーム、前景内側70%の平均絶対差でp95÷中央値≤2.5を再確認。時間方向の間引きや平滑化なし。

| ショート / 素材 | p95÷中央値 | 結果 |
|---|---:|---|
{moves}

M2/M3の2秒おき画像と修正箇所の画像を目視確認。本人による全編試聴は未実施。MP4×3・SRT×3・中央JPG×3・2秒おきJPG×3・修正箇所JPG×2・CSV×3・台本・再生ページ・チェックサムの全20添付、合計{sum(a['bytes'] for a in shared['assets']):,} bytes。全添付をRESTで再取得・照合済み。Release未公開、追加支出なし。Claude確認・本人試聴の後、投稿は別依頼で行う。
''')
    print('REPORT READY',guide,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','report']);a=p.parse_args();globals()[a.stage]()
