# Quiet Origins 第2話「ハロウィン」v04

**397.666667秒・11,930フレーム・1080p30。** H03の重複する円を外し、ブランドを承認済みの共通版へ復元。

Mac：`/Users/ryo/Desktop/新チャンネル/EP002_Halloween/確認版_v04_20261022`。`deliverables/preview.html` で英日通常版・字幕入り確認版・発音試聴を再生。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-dfd1fd12ac83a882a218)、Release ID **420337497**。全26添付をRESTで再取得しSHA-256・サイズを照合済み。素材原寸は[v03の取得案内](../wom02_確認版_v03_20261022/README.md)（Release 420277076）を継続利用する。

```sh
gh api repos/yasukawa1980/youtube/releases/420337497 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP002_Halloween_en_v04_1080p30.mp4 | 664774990 | 155,236,312 |
| EP002_Halloween_en_v04_1080p30.srt | 664775189 | 7,509 |
| EP002_Halloween_en_v04_subtitled_review_1080p30.mp4 | 664775211 | 145,880,373 |
| EP002_Halloween_ja_v04_1080p30.mp4 | 664775522 | 155,229,535 |
| EP002_Halloween_ja_v04_1080p30.srt | 664775868 | 9,369 |
| EP002_Halloween_ja_v04_subtitled_review_1080p30.mp4 | 664775934 | 145,856,143 |
| EP002_asset_usage_v04.csv | 664776300 | 1,866 |
| EP002_audio_en.m4a | 664776346 | 9,080,249 |
| EP002_audio_ja.m4a | 664776427 | 9,073,472 |
| EP002_motion_v04.csv | 664776476 | 3,277 |
| EP002_pronunciation_en.m4a | 664776539 | 1,368,131 |
| EP002_pronunciation_en.txt | 664776596 | 1,325 |
| EP002_pronunciation_ja.m4a | 664776642 | 736,718 |
| EP002_pronunciation_ja.txt | 664776694 | 1,076 |
| EP002_thumbnail_en.jpg | 664776735 | 566,337 |
| EP002_upload_info_en.md | 664776779 | 5,224 |
| EP002_upload_info_ja.md | 664776820 | 5,251 |
| H03_D_texts_v04_center.jpg | 664776859 | 16,296 |
| N07_Met_All_Saints_31.67.9.jpg | 664776918 | 2,664,662 |
| VOICE_CREDITS.txt | 664776973 | 164 |
| frame_identity_v04.json | 664777031 | 1,440,594 |
| layout_v04.json | 664777074 | 3,657 |
| motion_v04.json | 664777134 | 362,203 |
| preview.html | 664777220 | 1,878 |
| qc_v04.json | 664777274 | 3,720 |
| SHA256SUMS_shared.txt | 664777330 | 2,315 |

- [H03修正後の中央フレーム](frames/D_texts_v04.jpg)／[変更なしのH08](frames/D_season_v04.jpg)
- [全フレームの画素一致](records/frame_identity_v04.json)／[音声・SRT・尺などの検査](records/qc_v04.json)
- [動きの測定](deliverables/EP002_motion_v04.csv)（本編38件合格、ブランド2件対象外）
- [素材使用一覧](deliverables/EP002_asset_usage_v04.csv)（本編38素材各1回）

画素一致の対象は通常版。字幕入り確認版は同じSRT・スタイルを通常版へ再描画した派生物で、音声はコピー。本人による全編の試聴・生成動画の自然さの確認は引き続き必要。

再現：既存Python環境で `wom02_revision_v04.py prepare → pictures → review → identity → verify → frames`。中央フレームを目視後 `visual_review_v04.json` に記録し、`wom02_v04_delivery.py docs → share → export`。入力は保存済みv03・v02と既存素材。メディア原寸・中間物はGitへ追加しない。
