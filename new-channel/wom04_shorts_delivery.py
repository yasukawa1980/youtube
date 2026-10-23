"""Private draft delivery of EP004 Shorts; Release-ID REST verification."""
import argparse,csv,hashlib,html,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom04_shorts import ROOT,read,save,sha,FPS
from wom02_delivery import api
GH='yasukawa1980/youtube'
TAG='qo-shorts-ep004-v01-20261024'

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
 (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins Shorts v01</title><style>body{max-width:1100px;margin:28px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,h2{color:#d8b575}h2{font-size:18px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px}video{width:100%;max-height:72vh;background:#000}a{color:#d8b575}</style><h1>Quiet Origins / Pandora Shorts v01</h1><p>第4話パンドラ 3本。英語音声・英語字幕、縦1080×1920。確認用・未投稿。</p><main>'+cards+'</main><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})));</script></html>')
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
            r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins：パンドラ ショート3本 v01',body='本人依頼・Claudeの確定台本を維持。英語Kokoro af_heart、縦1080×1920・30fps、19.000/20.000/19.667秒。英語字幕入り。7素材各1回、A21は本編の切り出し、A02は口縁のみ。−14LUFS付近、字幕・全フレームの動き・全編デコードを検査。YouTube未投稿、非公開Draftを維持。',draft=True))
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
    import json
    from wom04_shorts import PHONEMES,REQUEST,MEDIA
    shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified' and shared['draft']
    qc=read(ROOT/'records/media_qc.json');motion=read(ROOT/'records/motion_qc.json');rows=read(ROOT/'records/shorts.json')['shorts']
    assert qc['passed'] and motion['passed'] and len(shared['assets'])==18
    repo=Path(__file__).resolve().parent;guide=repo/'wom_ショート確認版_EP004_v01_20261024'
    for d in ['records','frames','deliverables']:(guide/d).mkdir(parents=True,exist_ok=True)
    names=['narration.json','shorts.json','audio_qc.json','visual_manifest.json','media_qc.json','motion_qc.json','subtitle_qc.json','asset_usage.json','frame_review.json','visual_review.json','sharing.json','reading_correction.json','caption_manifest.json']
    for name in names:shutil.copy2(ROOT/'records'/name,guide/'records'/name)
    for p in (ROOT/'review').glob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        shutil.copy2(p,guide/'frames'/p.name)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.srt','.csv','.txt']:shutil.copy2(p,guide/'deliverables'/p.name)
        if p.suffix=='.mp4':
            dest=ROOT.parent/p.name
            if dest.exists():assert sha(dest)==sha(p)
            else:shutil.copy2(p,dest)
    table='\n'.join(f"| {s['id']} | {s['video_duration_seconds']:.3f} | {s['frames']} | {s['lufs']:.2f} | {s['true_peak_dbtp']:.2f} | {s['voice_onset_normalized_stem_seconds']:.2f} | {s['cta_seconds']:.3f} |" for s in qc['media'])
    movement='\n'.join(f"| {m['short_id']} / {m['asset_id']} | {m['measurement']['p95_over_median']:.6f} |" for m in motion['checks'])
    shots=read(ROOT/'records/visual_manifest.json')['shots']
    cuts='\n'.join(f"| {s['short_id']} | {s['asset_id']} | {s['start_frame']/30:.3f}–{s['end_frame']/30:.3f} | {s['frames']/30:.3f} |" for s in shots)
    frames='\n'.join(f"- {s['id']}：[中央](frames/{Path(s['name']).stem}_mid.jpg)／[2秒おき](frames/{Path(s['name']).stem}_every2s.jpg)" for s in qc['media'])
    assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in shared['assets'])
    (guide/'README.md').write_text(f"""# Quiet Origins パンドラ ショート3本 v01

確認用・YouTube未投稿。英語音声と英語字幕、縦1080×1920・30fps。

Mac再生ページ：`{ROOT}/deliverables/preview.html`。完成MP4は `{ROOT.parent}` にも保存。

[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。添付18点をRelease ID指定RESTで取得し直し、SHA-256とバイト数を照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/{shared['release_id']} --jq '.assets[] | [.id,.name]'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| ID | 秒 | フレーム | LUFS | dBTP | 声の開始秒 | 末尾案内秒 |
|---|---:|---:|---:|---:|---:|---:|
{table}

{frames}

[使用素材](deliverables/asset_usage.csv)／[台本](deliverables/scripts.txt)／[発音の継承](records/reading_correction.json)／[共有照合](records/sharing.json)。SRTは動画へ焼き込んだ字幕と同じ。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}
""")
    (repo/'wom_ショート制作結果_EP004_20261024.md').write_text(f"""# 第4話「パンドラ」ショート制作結果（2026-10-24）

[依頼](wom_ショート制作依頼_EP004_20261023.md)（確定語数のコミットa0728e3）に基づきP1〜P3を制作。[確認画像・取得方法](wom_ショート確認版_EP004_v01_20261024/README.md)。YouTube未投稿。Claudeの確認と本人の試聴待ち。

| ID | 秒 | フレーム | LUFS | dBTP | 声の開始秒 | 末尾案内秒 |
|---|---:|---:|---:|---:|---:|---:|
{table}

## 音声

台本は依頼書と完全一致（41/38/44語）。Kokoro af_heart、本編と同じspeed=0.82、sentence_pause=0.3、clause_pause=0.12。ネイティブ音声はP1 16.992667秒、P2 18.019292秒、P3 17.666625秒。加速・ピッチ変更なし。最初の声は正規化した語りステムの10ms窓、−50dBFSで測定。

本編PHONEMESを継承。実際に台本にあるHesiod・pithos・pyxisは指定音素を使用。Hesiod'sは本編のHesiodの音素に所有格/z/を付け、切り離した文字Sの読みを防ぐEP003ショートの処理を継承。Erasmus・Zeusは本編にも個別音素指定がないため同じ標準トークナイザーを使用。「本編で指定済み」とはしていない。全対応をreading_correction.jsonに保存。

本編BGMステム `{MEDIA}/audio/common_bgm_and_brand.wav` の120/140/160秒から採取し、語り中−33.5dBFSへ調整。最終AACとMP4を測定。ピークリミッターの追加適用なし。CTAは音声なし。

## 字幕・切替・画面

全字幕本文が台本と一致。1行最大5語・2行以内。700 BCE、1508、one and a half metersは同じ字幕画面に保持。輪郭・影を含む全字幕とCTAの描画を同じlibassで検査し、x80〜880・y1150〜1450内。札と出典はy140〜260。A01写真Jastrow（PD）、A02写真Shonagon（CC0）を明記。

切替はKokoroの音素時刻から求めた語時刻を30fpsへ丸めた値。人による全編の聴感同期確認とは区別する。

| 本 | 素材 | 表示秒 | 表示時間 |
|---|---|---:|---:|
{cuts}

P1のA01はlike this one、P2のA12はIn his book、A10はbecame a pyxis、P3のA02はOnly hopeに対応。各1.5秒以上。

A01は全体、A21は本編と同じ正規化切り出し[.02,.425,.98,.98]。A02は口縁のみ[.20,.06,.83,.172]とし、頸部の人物図像を映さない。A12は本編のPixide段落の切り出し[.045,.565,.68,.642]を使用。下線・囲みなし。ぼかし背景も同じ安全な切り出しから作成。前景枠y270〜1130、縦横比を保持。0.97→1.00倍の小数座標でゆっくり拡大。

博物館・刊本6点と本編AI画像R04の計7点。原寸SHA-256を既存台帳と照合し、3本の間にも各動画内にも重複なし。新規AI画像・AI動画・追加購入なし。

## 検査と共有

最終MP4の全編デコード・1080×1920・30fpsの全PTS・15〜20秒・音量を検査。2秒おきの縮小画像と中央画像を目視確認。7ショット全フレームの前景内側70%のグレースケール平均絶対差を測り、全件p95÷中央値≤2.5。時間方向の間引き・平滑化なし。

| ショート／素材 | p95÷中央値 |
|---|---:|
{movement}

[非公開Draft]({shared['release_url']})、Release ID **{shared['release_id']}**。全18添付、合計{sum(a['bytes'] for a in shared['assets']):,} bytesをREST再取得しSHA-256・サイズ一致。未公開を照合。Gitにはスクリプト・報告・検査JSON・縮小画像・字幕・CSVを保存し、動画・音源は入れない。

再現：wom04_shorts.py narration → captions → audio → visuals → render、wom04_shorts_qc.py verify → motion → glyphs → frames。画像確認をvisual_review.jsonに記録後、wom04_shorts_delivery.py docs → share → report。

次はClaudeの確認と本人の試聴。投稿予定10/28 18:00・10/29 12:00・10/29 18:00は参考のみで未登録。投稿操作は別依頼。
""")
    print('REPORT READY',guide,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','report']);a=p.parse_args();globals()[a.stage]()
