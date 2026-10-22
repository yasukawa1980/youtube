# Quiet Origins 第3話「メドゥーサ」確認版v01

台本v03。403.666667秒・12,110フレーム・1080p30。Mac：`/Users/ryo/Desktop/新チャンネル/EP003_Medusa/確認版_v01_20261023`。Mac制作フォルダ内の `deliverables/preview.html` で再生できます。別環境ではDraftの全添付を同じフォルダへ保存してから `preview.html` を開いてください。Git内の案内フォルダには動画・音声・原寸素材を置いていません。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-789d8d377dae7654e722)、Release ID **421292434**。全74添付をREST再取得し、SHA-256・bytes一致。YouTube投稿・Release公開はしていません。

```sh
gh api repos/yasukawa1980/youtube/releases/421292434 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

[検査結果](records/qc_v01.json)／[動きの測定](deliverables/EP003_motion_v01.csv)／[素材使用一覧](deliverables/EP003_asset_usage_v01.csv)／[読み補正一覧](records/reading_replacements.json)／[全発音箇所](records/pronunciation_locations.json)。時刻は単語を含む文の範囲です。

再現手順：既存Python環境で `wom03_produce.py prepare → en → ja → timeline → audio`、`wom03_visuals.py`、`wom03_render.py pictures → package → reviews → precision → verify`、`wom03_validate.py layout → frames`、`wom03_motion.py`、`wom03_final_checks.py`。目視確認記録後に `wom03_delivery.py docs → share → export`。画像生成・Kling動画は保存済み原本を使用し、再実行で自動生成しない。

本人の試聴項目：英語固有名詞（Stheno、Euryale、Chrysaor、gorgoneia、aegis、aulos、Canova）、日本語の固有名詞と神統記、冒頭〜ロゴ、M12の語りの調子。全編の動きの自然さと発音の聴感確認は未実施です。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP003_Medusa_en_v01_1080p30.mp4 | 667364804 | 143,840,490 |
| EP003_Medusa_en_v01_1080p30.srt | 667365165 | 7,557 |
| EP003_Medusa_en_v01_subtitled_review_1080p30.mp4 | 667365230 | 136,674,992 |
| EP003_Medusa_ja_v01_1080p30.mp4 | 667365645 | 143,666,251 |
| EP003_Medusa_ja_v01_1080p30.srt | 667366011 | 9,291 |
| EP003_Medusa_ja_v01_subtitled_review_1080p30.mp4 | 667366086 | 136,499,329 |
| EP003_asset_usage_v01.csv | 667366542 | 1,626 |
| EP003_audio_en.m4a | 667366612 | 9,314,184 |
| EP003_audio_en.wav | 667366755 | 116,256,102 |
| EP003_audio_ja.m4a | 667367291 | 9,139,957 |
| EP003_audio_ja.wav | 667367404 | 116,256,102 |
| EP003_motion_v01.csv | 667367872 | 3,655 |
| EP003_pronunciation_en.m4a | 667367950 | 2,020,757 |
| EP003_pronunciation_en.txt | 667368044 | 1,779 |
| EP003_pronunciation_ja.m4a | 667368077 | 500,512 |
| EP003_pronunciation_ja.txt | 667368122 | 753 |
| EP003_review_frames.zip | 667368168 | 11,325,064 |
| EP003_source_credits.md | 667368307 | 3,706 |
| EP003_thumbnail_A04.jpg | 667368364 | 231,313 |
| EP003_thumbnail_A24.jpg | 667368397 | 193,676 |
| EP003_upload_info_en.md | 667368452 | 4,296 |
| EP003_upload_info_ja.md | 667368492 | 4,511 |
| R01_reconstruction_v01.png | 667368532 | 2,998,772 |
| R02_reconstruction_v01.png | 667368584 | 2,936,997 |
| R03_reconstruction_v01.png | 667368639 | 2,854,555 |
| R05_reconstruction_v01.png | 667368716 | 2,844,950 |
| R06_reconstruction_v01.png | 667368783 | 2,642,241 |
| R07_reconstruction_v01.png | 667368836 | 2,790,784 |
| R08_reconstruction_v01.png | 667368880 | 2,421,678 |
| R09_reconstruction_v01.png | 667368917 | 2,596,464 |
| R10_reconstruction_v01.png | 667368970 | 3,060,902 |
| V01_Kling_v01.mp4 | 667369047 | 10,771,715 |
| V02_Kling_v01.mp4 | 667369113 | 26,938,746 |
| V03_Kling_v01.mp4 | 667369267 | 14,289,349 |
| V04_Kling_v01.mp4 | 667369343 | 18,783,995 |
| ai_images.json | 667369450 | 12,093 |
| ai_videos.json | 667369494 | 17,121 |
| asset_usage_v01.json | 667369540 | 4,951 |
| audio_qc.json | 667369594 | 735 |
| chapters.json | 667369641 | 1,182 |
| container_precision.json | 667369698 | 3,184 |
| content.json | 667369759 | 12,094 |
| content_en.json | 667369786 | 10,198 |
| final_checks.json | 667369833 | 30,948 |
| first_pass_pronunciation_analysis.json | 667369866 | 14,916 |
| intermediate_release.json | 667369891 | 329 |
| master_timeline.json | 667369934 | 4,858 |
| motion_v01.json | 667369975 | 365,038 |
| narration_segments_en.json | 667370031 | 46,259 |
| narration_segments_ja.json | 667370077 | 51,262 |
| narration_timeline_en.json | 667370117 | 49,978 |
| narration_timeline_ja.json | 667370151 | 54,967 |
| preview.html | 667370194 | 1,773 |
| pronunciation_auditions.json | 667370241 | 11,254 |
| pronunciation_locations.json | 667370275 | 3,561 |
| qc_v01.json | 667370318 | 3,768 |
| queries_en.json | 667370360 | 21,065 |
| queries_ja.json | 667370415 | 734,628 |
| reading_replacements.json | 667370465 | 3,004 |
| render_shots.json | 667370489 | 42,807 |
| request.json | 667370533 | 1,600 |
| runtime.json | 667370602 | 1,331 |
| sentence_boundary_validation.json | 667370638 | 18,833 |
| shot_center_validation.json | 667370678 | 12,537 |
| source_assets.json | 667370718 | 71,173 |
| source_preservation.json | 667370746 | 11,876 |
| subtitle_cues_en.json | 667370796 | 15,942 |
| subtitle_cues_ja.json | 667370838 | 17,074 |
| subtitle_layout_validation.json | 667370860 | 88,705 |
| subtitle_validation.json | 667370892 | 238 |
| visual_manifest.json | 667370938 | 41,702 |
| visual_review.json | 667370997 | 1,425 |
| wav_sample_validation.json | 667371023 | 648 |
| SHA256SUMS_shared.txt | 667371064 | 6,554 |
