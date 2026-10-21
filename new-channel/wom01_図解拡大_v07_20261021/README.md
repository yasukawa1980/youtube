# Quiet Origins：アヌビス第1話 v07（神々の切り出し・図解拡大）

2026-10-21。本人の実行依頼により、[Claudeの本人承認済み案](../wom01_Claude確認_v06_20261021.md)を反映。

## 完成動画

Mac保存先：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/Quiet_Origins_v07_20261021`。

- 字幕入り日本語確認用：`subtitled_review/deliverables/EP001_Anubis_ja_v07_subtitled_review_1080p30.mp4`
- 字幕入り英語確認用：`subtitled_review/deliverables/EP001_Anubis_en_v07_subtitled_review_1080p30.mp4`
- 通常版（字幕焼き込みなし）：`deliverables/EP001_Anubis_ja_v07_1080p30.mp4` / `EP001_Anubis_en_v07_1080p30.mp4`
- 英日SRT・音声M4A・サムネ・声のクレジット：`deliverables/`。

通常版の英日MP4は同一映像と言語別音声。字幕入り確認版はFontSize14の表示を焼き込んだ別コピー。

## 変更と維持

- N17・N18：アヌビス（548344の天秤の横）、トト（552247のトキの頭で筆記具を持つ神）、オシリス（548344の右端の玉座）を個別に切り出した。原寸の画像とMetの公式解説を照合。元画像・原寸サイズ・切り出し座標・表示位置・参照URLを[画像台帳](records/visual_manifest.json)に記録。名前と配置はv06を維持。
- N03・N07・N08・N09・N10・N17・N18・N22・N27の計9ショットを修正。一般の写真枠の横幅は1.2倍、縦は字幕領域に合わせ最大440px。札は23→28px。年表と神々の図は年代・名前の場所を確保するため縦の拡大を抑えた。残り46ショットは画像・エンコード済み映像をv06から再利用しハッシュ一致を確認。
- 年表・神名・クレジットを含め、文字と写真・図の箱の下端はy≤700px。全字幕を2サイズ（14／26）で実描画し、184条件で重なりなし。保守的な最小余白は126px。
- 英日音声ストリーム・SRT・サムネはv06と同一。尺682.700秒、20,481フレーム、55ショットの順序・開始・終了時刻を維持。英日映像ストリームも同一。
- 通常版と字幕入り確認版の計4本で全編デコード・PTSを検査。確認版では英150・日136字幕と空白区間を検査。
- v06は保全。YouTube動画投稿・追加支出なし。指定SSDへの同期は未実施。全編の聴感は未確認（音声は変更していない）。

## Claudeからの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-c0eb22ac9be2d5ce8b94)／Release ID **419197633**。全11添付をRelease IDからRESTで再取得してSHA-256一致を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/419197633 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v07_1080p30.mp4 | 661486426 | 194,048,913 |
| EP001_Anubis_en_v07_1080p30.srt | 661486855 | 13,252 |
| EP001_Anubis_ja_v07_1080p30.mp4 | 661486908 | 193,518,881 |
| EP001_Anubis_ja_v07_1080p30.srt | 661487309 | 15,346 |
| EP001_audio_en.m4a | 661487351 | 16,143,257 |
| EP001_audio_ja.m4a | 661487403 | 15,613,221 |
| EP001_thumbnail_en.jpg | 661487456 | 407,649 |
| VOICE_CREDITS.txt | 661487477 | 129 |
| EP001_Anubis_en_v07_subtitled_review_1080p30.mp4 | 661487529 | 184,680,236 |
| EP001_Anubis_ja_v07_subtitled_review_1080p30.mp4 | 661488003 | 184,367,140 |
| SHA256SUMS_shared.txt | 661488423 | 965 |

[検品](records/qc_v07.json)／[全字幕の重なり検査](records/subtitle_layout_all.json)／[画面の確認記録](records/visual_review.json)／[字幕入り版検品](records/review_qc.json)／[共有照合](records/sharing_verification_v07.json)。

全55ショットの中央フレームは `frames/midpoints_01.jpg`〜`midpoints_05.jpg`。全字幕表示例は `frames/font14_*.jpg` / `font26_*.jpg`。語りの自然さ・はかり4か所・オシリスの抑揚など以前からの本人試聴項目は継続。

## 再現と比較資料

制作は `wom01_enlarge_visuals.py`、範囲・保全確認は `wom01_check_enlarged_visuals.py`、共有は `wom01_share_enlarged_visuals.py`。共通の映像・字幕検品処理は `wom01_minimal_text.py` を版番号を指定して再利用する。

- [v06→v07 比較1](frames/v07_before_after_01.jpg)／[比較2](frames/v07_before_after_02.jpg)／[比較3](frames/v07_before_after_03.jpg)
- [原画像の切り出し位置](frames/v07_crop_sources.jpg)／[英日字幕入りの神々の場面](frames/v07_roles_subtitles.jpg)
- [変更範囲とv06保全の検証](records/scope_verification_v07.json)

神々の姿は [Met 548344](https://www.metmuseum.org/art/collection/search/548344) と [Met 552247](https://www.metmuseum.org/art/collection/search/552247) の公式解説と照合した。
