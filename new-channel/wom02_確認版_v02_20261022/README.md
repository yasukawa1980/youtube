# Quiet Origins 第2話「ハロウィン」v02

映像修正版。**6分37.666667秒・11,930フレーム・1080p30**。音声・SRT・尺・切り替え時刻・共通映像・サムネはv01と同一。

Mac：`/Users/ryo/Desktop/新チャンネル/EP002_Halloween/確認版_v02_20261022`。`deliverables/preview.html` から英日字幕入り版・通常版・発音試聴を選べる。

## Claudeからの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-65ab2547d87b6b3a655a)、Release ID **420175772**。全25添付をREST再取得してSHA-256・サイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/420175772 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP002_Halloween_en_v02_1080p30.mp4 | 664170092 | 117,543,463 |
| EP002_Halloween_en_v02_1080p30.srt | 664170400 | 7,509 |
| EP002_Halloween_ja_v02_1080p30.mp4 | 664170445 | 117,536,686 |
| EP002_Halloween_ja_v02_1080p30.srt | 664170741 | 9,369 |
| EP002_Halloween_en_v02_subtitled_review_1080p30.mp4 | 664170795 | 112,401,617 |
| EP002_Halloween_ja_v02_subtitled_review_1080p30.mp4 | 664171064 | 112,375,730 |
| EP002_audio_en.m4a | 664171294 | 9,080,249 |
| EP002_upload_info_en.md | 664171351 | 4,552 |
| EP002_pronunciation_en.m4a | 664171407 | 1,368,131 |
| EP002_pronunciation_en.txt | 664171450 | 1,325 |
| EP002_audio_ja.m4a | 664171485 | 9,073,472 |
| EP002_upload_info_ja.md | 664171560 | 4,579 |
| EP002_pronunciation_ja.m4a | 664171594 | 736,718 |
| EP002_pronunciation_ja.txt | 664171638 | 1,076 |
| EP002_thumbnail_en.jpg | 664171674 | 566,337 |
| VOICE_CREDITS.txt | 664171727 | 164 |
| preview.html | 664171760 | 1,849 |
| EP002_motion_comparison_v02.csv | 664171791 | 6,272 |
| R01_reconstruction_v01.png | 664171846 | 2,279,240 |
| R02_reconstruction_v01.png | 664171876 | 2,542,724 |
| R03_reconstruction_v01.png | 664171905 | 2,298,139 |
| R04_reconstruction_v02.png | 664171970 | 2,518,689 |
| R05_reconstruction_v02.png | 664172022 | 2,867,674 |
| R06_reconstruction_v02.png | 664172595 | 2,678,218 |
| SHA256SUMS_shared.txt | 664172678 | 2,270 |

## 検査と画像

- [全37ショットの動きの測定](records/motion_comparison.json)／[比較CSV](deliverables/EP002_motion_comparison_v02.csv)
- [音声・字幕・時刻の同一性](records/qc_v02.json)
- [全字幕の配置検査](records/subtitle_layout_validation.json)
- [全ショット一覧1](frames/final_storyboard_1.jpg)／[2](frames/final_storyboard_2.jpg)／[3](frames/final_storyboard_3.jpg)／[4](frames/final_storyboard_4.jpg)
- [全字幕2サイズの重ね描き一覧](frames/)
- [再現画R01〜R06、実行プロンプト、SHA-256](records/ai_images.json)

## 再現手順

v01と同じPython環境・依存関係。原寸R04〜R06はこのDraftからMac素材フォルダへ保存。`wom02_revision_v02.py prepare → visuals → pictures → package → review`、`wom02_v02_qc.py motion → verify`、`wom02_v02_review.py layout → frames`。検査後 `wom02_v02_delivery.py docs → share → export`。v01の出力フォルダは読み取り専用の入力として使う。YouTube投稿・Release公開は行わない。
