from pathlib import Path
import json,shutil
from PIL import Image
repo=Path(__file__).resolve().parent
root=Path('/Users/ryo/Desktop/新チャンネル/ショート/EP005_確認版_v01_20261024')
read=lambda p:json.loads(p.read_text())
shared=read(root/'records/sharing.json');assert shared['status']=='verified' and shared['draft']
qc=read(root/'records/media_qc.json');rows=read(root/'records/shorts.json')['shorts'];shots=read(root/'records/render_shots.json');motion=read(root/'records/motion_qc.json')
guide=repo/'wom_ショート確認版_EP005_v01_20261024'
for d in ['records','frames','deliverables']:(guide/d).mkdir(parents=True,exist_ok=True)
for name in ['narration.json','shorts.json','audio_qc.json','visual_manifest.json','media_qc.json','motion_qc.json','subtitle_qc.json','asset_usage.json','frame_review.json','visual_review.json','sharing.json','reading_correction.json','caption_manifest.json','T2_timing_question.json']:
 shutil.copy2(root/'records'/name,guide/'records'/name)
for p in (root/'review').glob('*.jpg'):
 assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
 shutil.copy2(p,guide/'frames'/p.name)
for p in (root/'deliverables').iterdir():
 if p.suffix in ['.srt','.csv','.txt']:shutil.copy2(p,guide/'deliverables'/p.name)
 if p.suffix=='.mp4':
  dest=root.parent/p.name
  assert not dest.exists() or dest.read_bytes()==p.read_bytes()
  if not dest.exists():shutil.copy2(p,dest)
table='\n'.join(f"| {m['id']} | {m['video_duration_seconds']:.3f} | {m['frames']} | {m['lufs']:.2f} | {m['true_peak_dbtp']:.2f} | {m['voice_onset_normalized_stem_seconds']:.2f} |" for m in qc['media'])
cuts='\n'.join(f"| {s['short_id']} | {s['asset_id']} | {s['start_frame']/30:.3f}–{s['end_frame']/30:.3f} | {s['cut_phrase'] or '冒頭'} |" for s in shots)
move='\n'.join(f"| {m['short_id']} / {m['asset_id']} | {m['measurement']['p95_over_median']:.6f} |" for m in motion['checks'])
frames='\n'.join(f"- {m['id']}：[2秒おき](frames/{Path(m['name']).stem}_every2s.jpg)／[中央](frames/{Path(m['name']).stem}_mid.jpg)" for m in qc['media'])
assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in shared['assets'])
(guide/'README.md').write_text(f'''# 第5話「天狗」ショート確認版 v01：T1・T3完成、T2保留

**3本完成ではない。** T1・T3は検査済み。T2は音声と素材準備までで、映像の尺の方針を本人に確認中。YouTube未投稿。

Mac確認ページ：`{root}/deliverables/preview.html`。

[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をRelease ID指定RESTで再取得し、SHA-256・サイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/{shared['release_id']} --jq '.assets[] | [.id,.name]'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 本 | 秒 | frames | LUFS | dBTP | 声の開始秒 |
|---|---:|---:|---:|---:|---:|
{table}

{frames}

T2の確認用音声は `EP005_T2_native_for_script_review.wav`。完成動画ではない。[尺の問題](records/T2_timing_question.json)／[発音の継承](records/reading_correction.json)／[照合記録](records/sharing.json)。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}
''')
(repo/'wom_ショート制作結果_EP005_20261024.md').write_text(f'''# 第5話「天狗」ショート制作結果（2026-10-24）

[Claudeの依頼](wom_ショート制作依頼_EP005_20261024.md)に沿って制作。**T1・T3完成、T2は音声生成・素材準備までで保留。3本完成とは扱わない。** [確認画像・取得方法](wom_ショート確認版_EP005_v01_20261024/README.md)。YouTube未投稿。

## 完成した2本

| 本 | 秒 | frames | LUFS | dBTP | 声の開始秒 |
|---|---:|---:|---:|---:|---:|
{table}

縦1080×1920・30fps。全編デコード、全600フレームのPTS（1/15360秒単位、512ずつ）、最終AACの一致を確認。語りの下のBGMは−33.5 dBFS、ピーク−1 dBTP以下。字幕全文は依頼台本と一致。声の開始は正規化した語りステムを10ms窓・−50dBFSで測定。

## 台本・音声・字幕

英語のみ、Kokoro af_heart、speed=0.82、sentence_pause=0.3、clause_pause=0.12。本編の `reading_replacements.json` と英語音素指定を照合して継承。T1 43語、T2 40語、T3 35語、台本は変更していない。

最終ネイティブ音声はT1 **19.231958秒**、T2 **16.365292秒**、T3 **18.029292秒**。加速・ピッチ変更なし。Nihon ShokiとHokusaiは本編の音素。tenguとBinは本編にも個別指定がないため、本編と同じ標準トークナイザーの読みを維持。Hokusai'sは本編のHokusai＋所有格/z/とし、分割された文字Sが「エス」になるのを防いだ（合格済みEP004 Shortsと同じ処理）。T3の初回測定18.209958秒から、この発音修正後18.029292秒に更新。

本編v02で音声が保持されているv01の `audio/common_bgm_and_brand.wav` の静かな部分（T1 120秒〜、T2準備音声140秒〜、T3 160秒〜）を使用。新規AI画像・動画の生成なし、Klingクレジット使用なし。

字幕とCTAの輪郭・影を含め、同一libassで全ページの描画範囲を検査し、x80〜880・y1150〜1450に収まることを確認。字幕は最大2行、1行最大5語。`of 720,`・`in 637`・`in 1815,` は数字だけ別画面に分けず保持。最後の2秒（18.000〜20.000秒）に無音の `Full story on Quiet Origins` をy1410に表示。字幕の中心はy1250とし、T1の最後の語りと同時に出る時間も重ならない。

## 素材と切り替え

切替はKokoro音素時刻から語へ対応づけた値を30fpsに丸めた。モデル由来の推定語時刻であり、人が全編を聞いて照合したものではない。

| 本 | 素材 | 表示秒 | 切り替えの語 |
|---|---|---:|---|
{cuts}

T1は本編v02採用V01（夜の丘・火球）の10秒をゆっくり延ばして使用。日本書紀は本編v02の拡大矩形 `[0.600,0.565,0.655,0.745]` のみで「是」を保持。T3の北斎漫画は右頁内の詳細矩形 `[0.52,0.245,0.96,0.57]`、天狗の字と鳥を表示。LACMAは本編と同じ右側 `[0.52,0.03,0.99,0.98]` で、大天狗と黒い翼の烏天狗を中心に使用。刀の打ち合いへの拡大なし。

札・出典は本編と同じ文。長い出典は全文を2行へ折り返し、y140〜260内に保持。NDLの刊年とコマ番号を表示。前景y270〜1130、余白は同じ安全な切り出しのぼかし。静止画は小数座標で0.97→1.00倍。

完成2本では5素材すべて各1回、重複なし。T2用のmet_57203・V02を含む計画全7素材も重複なし。

全ショットを30fpsの全フレームで測定（前景の内側70%、グレースケールの隣接フレーム平均絶対差、間引き・平滑化なし）。全件p95÷中央値≤2.5。

| 本／素材 | p95÷中央値 |
|---|---:|
{move}

2秒おきと中央の縮小JPGを目視確認済み。音の全編聴感は本人の試聴待ち。

## T2で確認が必要な理由

依頼の「20秒以内」と「V02の光の部分の速さだけを調整してよい」を同時に守るため、ここで映像の書き出しを保留した。**音声そのものは16.365292秒で20秒以内**。

- `a Buddha appears` の開始：2.366667秒（71フレーム）。
- `At last the Buddha vanishes` の開始：10.733333秒（322フレーム）。
- 本編v02の顔をぼかした採用V02は14.600秒。目視で光から鳥への移行が始まるのは元動画の約4.2秒。
- 光の区間だけを延ばし、消え始めを10.733333秒に合わせて残りの動きを等速で保つと、末尾は約 **21.133333秒**（10.733333＋14.6−4.2）。

本人に「Claudeが台本を短縮する」か「鳶の後半も少し速めて20秒以内にする」かを質問済み、回答待ち。依頼の制限を勝手に緩めたり、台本を短くしたりしていない。T2の確認用音声WAV・未変更の台本・音素時刻・素材準備・この問題の記録は保存した。短縮の場合は、単純な語数だけでなく `At last` の開始を約9.6秒以前に置けるかが目安になる。

## 共有

[非公開Draft]({shared['release_url']})、Release ID **{shared['release_id']}**。完成動画2本とT2の音声・確認資料を含む全{len(shared['assets'])}添付、合計{sum(a['bytes'] for a in shared['assets']):,} bytesをREST再取得してSHA-256・サイズ一致、draft=true・published_at=nullを確認。

Mac確認ページ：`{root}/deliverables/preview.html`。完成MP4は `/Users/ryo/Desktop/新チャンネル/ショート/` にもコピー。Gitには制作スクリプト・報告・検査JSON・縮小JPG・SRT・CSV等のみを保存。

次はT2の方針決定→T2制作→Claudeの確認と本人の試聴。YouTube投稿は別依頼。
''')
p=repo/'Claude引き継ぎ_次のセッション.md';s=p.read_text()
s=s.replace('| 第5話のショート（T1〜T3） | **制作依頼を作成**（2026-10-24）。英語のみ、新しいAI生成なし（Klingの残り69）。投稿は第5話の公開日が決まってから | `wom_ショート制作依頼_EP005_20261024.md` |', '| 第5話のショート（T1〜T3） | **T1・T3は各20秒で制作・検査完了、T2は尺の方針を本人に確認中**（2026-10-24）。T2音声16.365秒は生成済みだが、光の部分だけ速度調整してAt lastに合わせると映像約21.13秒。台本短縮か鳶の後半の速度変更か回答待ち。新規AI生成なし | `wom_ショート制作結果_EP005_20261024.md` |')
p.write_text(s)
print('REPORT READY',shared['release_id'],len(shared['assets']),sum(a['bytes'] for a in shared['assets']))
