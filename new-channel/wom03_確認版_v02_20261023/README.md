# メドゥーサ確認版v02（台本v04）

399.566667秒・11,987フレーム・19,179,200サンプル。Mac：`/Users/ryo/Desktop/新チャンネル/EP003_Medusa/確認版_v02_20261023`。`deliverables/preview.html`から全編と変更箇所を再生できます。

M01〜M17はv01と映像・AACパケット一致、デコード音声差分0、SRT一致。M18に一文を追加。共通版v02のエンドカードは389.566667秒から最後の10秒。サムネ2案はv01と同一。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-aa53da2ce46effd1c9c9)、Release ID **421322526**。全56添付をRelease ID指定RESTで再取得してサイズ・SHA-256一致。

```sh
gh api repos/yasukawa1980/youtube/releases/421322526 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

別環境では全添付を同じフォルダへ保存しpreview.htmlを開いてください。Git内には動画・音声を置いていません。原寸AI素材・v01全検査はRelease **421292434**に保全。

制作記録のM01〜M17の素材・文別WAVの相対参照はv01フォルダ、M18はv02フォルダが基準です。[実在確認済みの参照先とSHA-256](records/source_path_resolution.json)。

[技術検査](records/qc_v02.json)／[M01〜M17のSRT照合](records/srt_prefix_preservation.json)／[共通エンドカードの作り方とSHA-256](records/endcard_v02.json)。

本人試聴：M18の英日のお願い、10秒エンドカードの終わり方。未確認の固有名詞・神統記・M12の調子も引き続き確認対象。
再現：既存環境で `wom03_revision_v02.py prepare → narrate → brand → timeline → audio → pictures → package → reviews → verify → docs`、目視確認記録後 `share → export`。v01を読取専用入力として使用。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP003_M18_endcard_en_v02.mp4 | 667472416 | 3,370,166 |
| EP003_M18_endcard_ja_v02.mp4 | 667472498 | 3,359,447 |
| EP003_Medusa_en_v02_1080p30.mp4 | 667472612 | 143,683,578 |
| EP003_Medusa_en_v02_1080p30.srt | 667473141 | 7,712 |
| EP003_Medusa_en_v02_subtitled_review_1080p30.mp4 | 667473195 | 136,509,382 |
| EP003_Medusa_ja_v02_1080p30.mp4 | 667473596 | 143,497,835 |
| EP003_Medusa_ja_v02_1080p30.srt | 667474086 | 9,417 |
| EP003_Medusa_ja_v02_subtitled_review_1080p30.mp4 | 667474146 | 136,320,923 |
| EP003_asset_usage_v02.csv | 667474614 | 1,591 |
| EP003_audio_en.m4a | 667474644 | 9,291,211 |
| EP003_audio_en.wav | 667474723 | 115,075,244 |
| EP003_audio_ja.m4a | 667475211 | 9,105,480 |
| EP003_audio_ja.wav | 667475295 | 115,075,244 |
| EP003_pronunciation_en.m4a | 667475610 | 2,020,757 |
| EP003_pronunciation_en.txt | 667475663 | 1,779 |
| EP003_pronunciation_ja.m4a | 667475712 | 500,512 |
| EP003_pronunciation_ja.txt | 667475758 | 753 |
| EP003_review_frames_v02.zip | 667475839 | 296,860 |
| EP003_source_credits.md | 667475884 | 3,706 |
| EP003_thumbnail_A04.jpg | 667475932 | 231,313 |
| EP003_thumbnail_A24.jpg | 667475996 | 193,676 |
| EP003_upload_info_en.md | 667476032 | 4,316 |
| EP003_upload_info_ja.md | 667476060 | 4,531 |
| Quiet_Origins_endcard_v02.mp4 | 667476108 | 1,255,819 |
| Quiet_Origins_endcard_v02.wav | 667476156 | 2,880,044 |
| ai_images.json | 667476198 | 12,093 |
| ai_videos.json | 667476260 | 17,121 |
| asset_usage_v02.json | 667476303 | 4,952 |
| audio_revision_v02.json | 667476355 | 3,988 |
| chapters.json | 667476400 | 1,182 |
| content.json | 667476452 | 12,184 |
| content_en.json | 667476516 | 10,285 |
| endcard_v02.json | 667476562 | 3,327 |
| master_timeline.json | 667476591 | 5,042 |
| motion_v02.json | 667476619 | 370,848 |
| narration_segments_en.json | 667476660 | 46,922 |
| narration_segments_ja.json | 667476718 | 51,892 |
| narration_timeline_en.json | 667476794 | 50,640 |
| narration_timeline_ja.json | 667476853 | 55,633 |
| preview.html | 667476898 | 1,461 |
| pronunciation_locations.json | 667476942 | 3,561 |
| qc_v02.json | 667476971 | 5,927 |
| queries_en.json | 667477023 | 1,468 |
| queries_ja.json | 667477074 | 52,406 |
| reading_replacements.json | 667477132 | 3,004 |
| render_shots.json | 667477181 | 48,907 |
| revision_request.json | 667477251 | 688 |
| source_assets.json | 667477293 | 71,173 |
| srt_prefix_preservation.json | 667477353 | 309 |
| subtitle_cues_en.json | 667477408 | 16,211 |
| subtitle_cues_ja.json | 667477439 | 17,225 |
| subtitle_layout_v02.json | 667477489 | 6,781 |
| subtitle_validation.json | 667477536 | 300 |
| visual_manifest.json | 667477585 | 41,702 |
| visual_review_v02.json | 667477645 | 1,280 |
| SHA256SUMS_shared.txt | 667477702 | 4,950 |
