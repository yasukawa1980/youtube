# Quiet Origins 第2話「ハロウィン」v03

**6分37.666667秒・11,930フレーム・1080p30。** 本編38素材を各1ショットだけ使用。英日音声・SRT・H01〜H19区間時刻はv02と同一。

Mac：`/Users/ryo/Desktop/新チャンネル/EP002_Halloween/確認版_v03_20261022`。`deliverables/preview.html` から英日通常版・字幕入り確認版・発音試聴を選べる。

## Claudeからの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-eafc4f6bfe6c470f16b8)、Release ID **420277076**。全44添付をRelease ID指定のREST→各Asset IDで再取得し、SHA-256・サイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/420277076 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP002_Halloween_en_v03_1080p30.mp4 | 664551585 | 168,452,931 |
| EP002_Halloween_en_v03_1080p30.srt | 664552075 | 7,509 |
| EP002_Halloween_ja_v03_1080p30.mp4 | 664552115 | 168,446,154 |
| EP002_Halloween_ja_v03_1080p30.srt | 664563689 | 9,369 |
| EP002_Halloween_en_v03_subtitled_review_1080p30.mp4 | 664563729 | 158,040,505 |
| EP002_Halloween_ja_v03_subtitled_review_1080p30.mp4 | 664564162 | 158,016,763 |
| EP002_audio_en.m4a | 664564616 | 9,080,249 |
| EP002_upload_info_en.md | 664564657 | 4,916 |
| EP002_pronunciation_en.m4a | 664564705 | 1,368,131 |
| EP002_pronunciation_en.txt | 664564769 | 1,325 |
| EP002_audio_ja.m4a | 664564838 | 9,073,472 |
| EP002_upload_info_ja.md | 664564920 | 4,943 |
| EP002_pronunciation_ja.m4a | 664564951 | 736,718 |
| EP002_pronunciation_ja.txt | 664564993 | 1,076 |
| EP002_thumbnail_en.jpg | 664565061 | 566,337 |
| VOICE_CREDITS.txt | 664565103 | 164 |
| preview.html | 664565159 | 1,845 |
| EP002_motion_v03.csv | 664565212 | 4,846 |
| EP002_asset_usage_v03.csv | 664565274 | 1,866 |
| R01_reconstruction_v01.png | 664565326 | 2,279,240 |
| R02_reconstruction_v01.png | 664565366 | 2,542,724 |
| R03_reconstruction_v01.png | 664565444 | 2,298,139 |
| R04_reconstruction_v02.png | 664565543 | 2,518,689 |
| R05_reconstruction_v02.png | 664565584 | 2,867,674 |
| R06_reconstruction_v02.png | 664565637 | 2,678,218 |
| N02_reconstruction_v03.png | 664565698 | 2,691,543 |
| N03_reconstruction_v03.png | 664565764 | 2,477,170 |
| N05_reconstruction_v03.png | 664565818 | 2,844,818 |
| N08_reconstruction_v03.png | 664565865 | 3,025,422 |
| N10_reconstruction_v03.png | 664565923 | 2,949,776 |
| N11_reconstruction_v03.png | 664565954 | 2,647,636 |
| N13_reconstruction_v03.png | 664566018 | 2,700,259 |
| N14_reconstruction_v03.png | 664566100 | 2,950,301 |
| N15_reconstruction_v03.png | 664566163 | 2,545,280 |
| N18_reconstruction_v03.png | 664566204 | 2,414,150 |
| N01_Kling_v03_take02.mp4 | 664566305 | 16,747,287 |
| N06_Kling_v03.mp4 | 664566455 | 15,458,164 |
| N09_Kling_v03.mp4 | 664566538 | 15,870,852 |
| N12_Kling_v03.mp4 | 664566661 | 11,865,145 |
| N16_Kling_v03.mp4 | 664566758 | 14,399,913 |
| N17_Kling_v03.mp4 | 664566899 | 20,374,489 |
| N01_Kling_v03.mp4 | 664567022 | 13,735,814 |
| N07_Met_All_Saints_31.67.9.jpg | 664567089 | 2,664,662 |
| SHA256SUMS_shared.txt | 664567151 | 3,973 |

## 検品入口

- [素材ごとの使用一覧](deliverables/EP002_asset_usage_v03.csv)／[検査JSON](records/asset_usage_v03.json)
- [全40ショットの動き](deliverables/EP002_motion_v03.csv)／[差分全配列](records/motion_v03.json)
- [音声・SRT・区間時刻とブランド派生映像](records/qc_v03.json)
- [字幕172件×2サイズの配置検査](records/subtitle_layout_validation.json)
- [中央フレーム一覧1](frames/final_storyboard_1.jpg)／[2](frames/final_storyboard_2.jpg)／[3](frames/final_storyboard_3.jpg)／[4](frames/final_storyboard_4.jpg)
- [全字幕の重ね描き一覧](frames/)
- [追加静止画のプロンプト・SHA](records/new_stills_v03.json)／[Kling動画のプロンプト・消費記録](records/new_videos_v03.json)／[追加PD史料](records/new_sources_v03.json)

N01の採用素材は `N01_Kling_v03_take02.mp4`。`N01_Kling_v03.mp4` は不採用の初回を保全した監査用ファイルで、完成動画には使用していない。

再現：既存Python環境で `wom02_revision_v03.py prepare → visuals → brand → pictures → package → review`。`wom02_v03_qc.py usage → motion → verify`、`wom02_v03_review.py layout → frames`。確認後 `wom02_v03_delivery.py docs → share → export`。v02・原寸素材が入力として必要。原寸素材をGitへ追加しない。
