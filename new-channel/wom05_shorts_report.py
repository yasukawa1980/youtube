"""Write the completed EP005 Shorts handoff, preserving the earlier partial release."""
from pathlib import Path
import json,shutil
from PIL import Image
from wom05_shorts import ROOT as root, read, sha
repo=Path(__file__).resolve().parent
guide=repo/'wom_ショート確認版_EP005_v01_20261024'
shared=read(root/'records/sharing_complete.json');assert shared['status']=='verified' and shared['draft']
qc=read(root/'records/media_qc.json');assert len(qc['media'])==3
rows=read(root/'records/shorts.json')['shorts'];shots=read(root/'records/render_shots.json');motion=read(root/'records/motion_qc.json')
old=read(root/'records/sharing.json')
for m in qc['media']:
 if m['id'] in ['T1','T3']:
  a=next(a for a in old['assets'] if a['name']==m['name']);assert m['sha256']==a['sha256']
for d in ['records','frames','deliverables']:(guide/d).mkdir(parents=True,exist_ok=True)
for name in ['narration.json','shorts.json','audio_qc.json','visual_manifest.json','media_qc.json','motion_qc.json','subtitle_qc.json','asset_usage.json','frame_review.json','visual_review.json','sharing_complete.json','reading_correction.json','caption_manifest.json','T2_timing_question.json','T2_video_retime.json']:
 shutil.copy2(root/'records'/name,guide/'records'/name)
for p in (root/'review').glob('*.jpg'):
 assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
 shutil.copy2(p,guide/'frames'/p.name)
for p in (root/'deliverables').iterdir():
 if p.suffix in ['.srt','.csv','.txt'] and p.name!='T2_timing_pending.txt':shutil.copy2(p,guide/'deliverables'/p.name)
 if p.suffix=='.mp4':
  dest=root.parent/p.name
  assert not dest.exists() or sha(dest)==sha(p)
  if not dest.exists():shutil.copy2(p,dest)
table='\n'.join(f"| {m['id']} | {m['video_duration_seconds']:.3f} | {m['frames']} | {m['lufs']:.2f} | {m['true_peak_dbtp']:.2f} | {m['voice_onset_normalized_stem_seconds']:.2f} |" for m in qc['media'])
cuts='\n'.join(f"| {s['short_id']} | {s['asset_id']} | {s['start_frame']/30:.3f}–{s['end_frame']/30:.3f} | {s['cut_phrase'] or '冒頭'} |" for s in shots)
move='\n'.join(f"| {m['short_id']} / {m['asset_id']} | {m['measurement']['p95_over_median']:.6f} |" for m in motion['checks'])
frames='\n'.join(f"- {m['id']}：[2秒おき](frames/{Path(m['name']).stem}_every2s.jpg)／[中央](frames/{Path(m['name']).stem}_mid.jpg)" for m in qc['media'])
assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in shared['assets'])
(guide/'README.md').write_text(f'''# 第5話「天狗」ショート確認版 v01：3本完成

本人の「20秒以内はこだわっていないので全体のバランスが良ければ尺は大丈夫です」（2026-10-24）を反映し、T2の保留を解消。T1・T3は初回共有からファイルSHA-256一致。YouTube未投稿、Claude確認と本人試聴待ち。

Mac確認ページ：`{root}/deliverables/preview.html`。

[完成3本の非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をRelease ID指定RESTで再取得し、SHA-256・サイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/{shared['release_id']} --jq '.assets[] | [.id,.name]'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 本 | 秒 | frames | LUFS | dBTP | 声の開始秒 |
|---|---:|---:|---:|---:|---:|
{table}

{frames}

[素材一覧](deliverables/asset_usage.csv)／[台本](deliverables/scripts.txt)／[発音](records/reading_correction.json)／[T2速度調整](records/T2_video_retime.json)／[完成版の共有照合](records/sharing_complete.json)。

初回の部分共有Release `{old['release_id']}` と `records/sharing.json`、`deliverables/T2_timing_pending.txt` は履歴として保全。**現在のT2は保留ではない。最新は上記の完成3本Releaseと本README。**

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}
''')
(repo/'wom_ショート制作結果_EP005_20261024.md').write_text(f'''# 第5話「天狗」ショート制作結果（2026-10-24・3本完成）

[Claudeの依頼](wom_ショート制作依頼_EP005_20261024.md)に基づくT1〜T3が完成。[確認画像・取得方法](wom_ショート確認版_EP005_v01_20261024/README.md)。**YouTube未投稿。Claude確認と本人試聴待ち。**

## 本人の方針変更とT2の解決

2026-10-24の本人指示：「20秒以内はこだわっていないので全体のバランスが良ければ尺は大丈夫です」。依頼の20秒上限よりこの指示を優先し、T2を**21.133333秒**に仕上げた。台本を短縮せず、鳶の後半の速さも変えていない。T1・T3は初回共有Release `{old['release_id']}` と動画ファイル全体のSHA-256一致。

| 本 | 秒 | frames | LUFS | dBTP | 声の開始秒 |
|---|---:|---:|---:|---:|---:|
{table}

縦1080×1920・30fps。全編デコード、全PTS（time_base=1/15360・512ずつ）、最終AACとの一致を確認。語りの下のBGM−33.5 dBFS、ピーク−1 dBTP以下。声の開始は正規化した語りステムを10ms窓・−50dBFSで測定。

## T2の構成

- 0〜2.366667秒：met_57203の柿の枝。本編と同じ切り出しで蜂の巣へ寄らない。
- 2.366667秒（71フレーム）：「a Buddha appears」の開始に合わせ、処理済みV02へ切り替え。
- 10.733333秒（322フレーム）：「At last the Buddha vanishes」の開始に、元V02の光から鳥へ移る約4.2秒の位置を対応。
- V02の先頭126フレーム（4.2秒）だけを251フレーム（8.366667秒）へ延長し、光の部分にオプティカルフロー補間を適用。
- 元V02の126〜437フレームは順序・30fpsの速さを保ち、312フレーム（10.4秒）で最後まで表示。鳥の加速・フレーム間引きなし。元動画14.6秒＋光の延長＋冒頭の柿の枝＝21.133333秒。
- 語りの終了後は鳶の動きを見せ、最後の2秒（19.133333〜21.133333秒）に無音の `Full story on Quiet Origins` を表示。

本編v02の承認済み合成映像を使用し、既存の顔のぼかし処理を保持。元の前景矩形 `[231,110,1458,820]` から横長全体を取り出し、縦画面の前景へ配置。顔や細部へ追加の拡大なし。新しいAI生成は行っていない。

## 台本・音声・字幕

英語のみ、Kokoro af_heart、speed=0.82、sentence_pause=0.3、clause_pause=0.12。本編の `reading_replacements.json` と英語音素を照合。T1 43語、T2 40語、T3 35語、依頼台本をそのまま使用。

ネイティブ音声：T1 19.231958秒、T2 16.365292秒、T3 18.029292秒。加速・ピッチ変更なし。Nihon ShokiとHokusaiは本編の音素。tenguとBinは本編と同じ標準トークナイザー。Hokusai'sは本編のHokusaiに所有格/z/をつなぎ、文字Sを独立して「エス」と読ませない（合格済みEP004と同じ処理）。

BGMは本編v02でも保持しているv01の `audio/common_bgm_and_brand.wav` の120／140／160秒から使用。字幕本文は依頼台本と一致。`of 720,`・`in 637`・`in 1815,` を同一字幕画面に保持。最大2行・1行最大5語。輪郭・影を含めたlibass描画を検査し、x80〜880・y1150〜1450内。字幕中心y1250、末尾2秒のCTA中心y1410で重なりなし。人による全編聴感は本人の試聴待ち。

## 素材・切り替え・画面

切替はKokoroの音素時刻から求めた語時刻を30fpsに丸めた値（人の聴感による同期測定とは区別）。全素材1.5秒以上、7素材は3本を通じて各1回で重複なし。

| 本 | 素材 | 表示秒 | 切り替えの語 |
|---|---|---:|---|
{cuts}

日本書紀の拡大矩形は本編v02と同じ `[0.600,0.565,0.655,0.745]` で「是」を保持。北斎漫画は右頁内の詳細 `[0.52,0.245,0.96,0.57]` で天狗の字と鳥。LACMAは右側 `[0.52,0.03,0.99,0.98]` で大天狗と黒い翼の烏天狗、刀の打ち合いへの拡大なし。札・出典は本編と同じ文、NDLの刊年とコマを表示。長い出典は2行へ折り返し、y140〜260内。

前景y270〜1130、余白は同じ安全な切り出しのぼかし。静止画は小数座標で0.97→1.00倍。全ショットを30fpsの全フレームで測定（前景内側70%、グレーの隣接フレーム平均絶対差、間引き・平滑化なし）。

| 本／素材 | p95÷中央値 |
|---|---:|
{move}

動きの判定・条件は [motion_qc.json](wom_ショート確認版_EP005_v01_20261024/records/motion_qc.json) を参照。2秒おき・中央の縮小JPGとT2の変化前後・末尾を目視確認。仏の顔が見えず、鳥が枝の後ろへ沈むことを確認。

## 共有

[完成3本の非公開Draft]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付、合計{sum(a['bytes'] for a in shared['assets']):,} bytesをREST再取得してSHA-256・サイズ一致。draft=true・published_at=nullを確認。初回の部分共有Release `{old['release_id']}` は履歴として保全。

Mac確認ページ：`{root}/deliverables/preview.html`。完成MP4は `/Users/ryo/Desktop/新チャンネル/ショート/` にもコピー。Gitにはスクリプト・記録・縮小画像・SRT・CSVのみを保存。

次はClaudeの確認と本人の試聴。YouTube投稿は別依頼。追加購入・新規AI生成・Klingクレジット使用なし。
''')
p=repo/'Claude引き継ぎ_次のセッション.md';s=p.read_text()
lines=s.splitlines()
for i,line in enumerate(lines):
 if line.startswith('| 第5話のショート（T1〜T3） |'):
  lines[i]=f'| 第5話のショート（T1〜T3） | **3本制作・検査完了**（2026-10-24、完成版Draft Release `{shared["release_id"]}`）。T1/T3各20秒、T2は本人の「20秒にこだわらずバランス優先」に従い21.133秒。台本と鳶の後半の速さを維持。Claude確認・本人試聴待ち、未投稿、新規AI生成なし | `wom_ショート制作結果_EP005_20261024.md` |'
p.write_text('\n'.join(lines)+'\n')
print('REPORT READY',shared['release_id'],len(shared['assets']),sum(a['bytes'] for a in shared['assets']))
