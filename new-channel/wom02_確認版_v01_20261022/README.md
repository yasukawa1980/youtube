# Quiet Origins 第2話「ハロウィン」確認版 v01

2026-10-22制作。英日共通 **6分37.666667秒／11,930フレーム／1920×1080・30fps**。
本人の通し試聴・発音確認待ち。YouTube投稿・Release公開なし。

## Macでの再生

保存先：`/Users/ryo/Desktop/新チャンネル/EP002_Halloween/確認版_v01_20261022`。`deliverables/preview.html` を開くと、英日字幕入り確認版と発音試聴を選べる。通常版は字幕焼き込みなし。MP4・M4A・原寸画像はGitに入れていない。

## Claudeからの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-4f8dd80c55b7917fde61)、Release ID **419736724**。全21添付を、Release IDによるメタデータ取得後、各Asset IDのRESTから再取得してSHA-256・サイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/419736724 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

添付を同じフォルダに保存すれば `preview.html` から再生できる。[ハッシュ一覧](deliverables/SHA256SUMS_shared.txt)。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP002_Halloween_en_v01_1080p30.mp4 | 662959299 | 56,696,906 |
| EP002_Halloween_en_v01_1080p30.srt | 662959598 | 7,509 |
| EP002_Halloween_ja_v01_1080p30.mp4 | 662959693 | 56,690,129 |
| EP002_Halloween_ja_v01_1080p30.srt | 662959966 | 9,369 |
| EP002_Halloween_en_v01_subtitled_review_1080p30.mp4 | 662960076 | 61,459,366 |
| EP002_Halloween_ja_v01_subtitled_review_1080p30.mp4 | 662960339 | 61,601,691 |
| EP002_audio_en.m4a | 662960650 | 9,080,249 |
| EP002_upload_info_en.md | 662960989 | 4,436 |
| EP002_pronunciation_en.m4a | 662961068 | 1,368,131 |
| EP002_pronunciation_en.txt | 662961130 | 1,325 |
| EP002_audio_ja.m4a | 662961194 | 9,073,472 |
| EP002_upload_info_ja.md | 662961303 | 4,463 |
| EP002_pronunciation_ja.m4a | 662961363 | 736,718 |
| EP002_pronunciation_ja.txt | 662961460 | 1,076 |
| EP002_thumbnail_en.jpg | 662961541 | 566,337 |
| VOICE_CREDITS.txt | 662961624 | 164 |
| preview.html | 662961688 | 1,822 |
| R01_reconstruction_v01.png | 662961737 | 2,279,240 |
| R02_reconstruction_v01.png | 662961847 | 2,542,724 |
| R03_reconstruction_v01.png | 662961931 | 2,298,139 |
| SHA256SUMS_shared.txt | 662962026 | 1,893 |

## 検品資料

- [全ショット一覧 1](frames/final_storyboard_1.jpg)
- [全ショット一覧 2](frames/final_storyboard_2.jpg)
- [全ショット一覧 3](frames/final_storyboard_3.jpg)
- [全ショット一覧 4](frames/final_storyboard_4.jpg)

- [音声・映像の実測](records/qc_v01.json)
- [全字幕2サイズの配置検査](records/subtitle_layout_validation.json)、[全字幕の重ね描き画像](frames/)
- [台本どおりの読み上げ文と時刻：英語](records/narration_timeline_en.json)／[日本語](records/narration_timeline_ja.json)
- [読み上げ置き換え一覧](records/reading_replacements.json)／[固有名詞33箇所の時刻範囲](records/pronunciation_locations.json)
- [再現画3点・実行プロンプト・SHA-256](records/ai_images.json)
- [原素材と共通映像の保全](records/source_preservation.json)

## 再現手順

Python 3.12に `../requirements_wom02.txt` の無料依存関係を入れ、既存のKokoro/VOICEVOXモデルを使う。使用環境は [runtime.json](records/runtime.json)。生成済みAI画像は上のDraft Releaseから指定素材フォルダへ置ける。`prepare` は保存済み `episodes/EP002_Halloween/records/ai_images.json` を読む。

```sh
python new-channel/wom02_produce.py prepare
python new-channel/wom02_produce.py en
python new-channel/wom02_produce.py ja
python new-channel/wom02_produce.py timeline
python new-channel/wom02_visuals.py
python new-channel/wom02_produce.py audio
python new-channel/wom02_render.py pictures
python new-channel/wom02_render.py package
python new-channel/wom02_render.py reviews
python new-channel/wom02_validate.py layout
python new-channel/wom02_validate.py frames
python new-channel/wom02_render.py verify
python new-channel/wom02_delivery.py docs
```

`share` は非公開Draft Releaseの作成・添付・再取得を行う。既存添付とハッシュが違う場合は上書きせず停止する。修正版は別バージョンにする。今回の本編では既存オープニングv02・エンドカードv01の音量を保持し、接続周辺のBGMだけフェードさせた。
