# Quiet Origins 第4話「パンドラ」確認版v01

台本v02a。429.566667秒・12,887フレーム・1080p30。
Mac：`/Users/ryo/Desktop/新チャンネル/EP004_Pandora/確認版_v01_20261023`。`deliverables/preview.html` で確認できます。別環境ではDraftの全添付を同じフォルダに保存してpreview.htmlを開いてください。Gitにはコード・資料・記録・字幕・小型JPGだけを保存しています。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-c768e9bc37ecdf38c027)。Release ID **421509468**。全74添付をREST再取得し、SHA-256・bytes一致。本人試聴待ち。

```sh
gh api repos/yasukawa1980/youtube/releases/421509468
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

[検査](records/qc_v01.json) / [素材使用](deliverables/EP004_asset_usage_v01.csv) / [動き](deliverables/EP004_motion_v01.csv) / [読み補正](records/reading_replacements.json) / [試聴時刻](records/pronunciation_locations.json)。時刻は単語を含む文の範囲です。

本人試聴項目：Hephaestus、Epimetheus、pithos、elpis、Pausanias、Babrius、pyxis、Psyche。日本語のヘパイストス、エピメテウス、ピトス、ピュクシス、壺、櫃、格言集。冒頭からOPへの流れとP05の語りの調子。人による全編再生・聴感確認は未実施。

再現：wom04_produce.py prepare/en/ja/timeline/audio、wom04_visuals.py、wom04_render.py pictures/package/reviews/precision/verify、wom04_validate.py layout/frames、wom04_motion.py、wom04_final_checks.py。画像・動画は保存原本を使用し、自動再生成しません。目視確認記録後、wom04_delivery.py docs/share/export。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP004_Pandora_en_v01_1080p30.mp4 | 668177536 | 123,506,381 |
| EP004_Pandora_en_v01_1080p30.srt | 668178118 | 8,116 |
| EP004_Pandora_en_v01_subtitled_review_1080p30.mp4 | 668178174 | 121,431,818 |
| EP004_Pandora_ja_v01_1080p30.mp4 | 668178642 | 123,588,078 |
| EP004_Pandora_ja_v01_1080p30.srt | 668179051 | 10,631 |
| EP004_Pandora_ja_v01_subtitled_review_1080p30.mp4 | 668179131 | 121,557,851 |
| EP004_asset_usage_v01.csv | 668179621 | 1,128 |
| EP004_audio_en.m4a | 668179687 | 9,882,439 |
| EP004_audio_en.wav | 668179802 | 123,715,302 |
| EP004_audio_ja.m4a | 668180143 | 9,964,136 |
| EP004_audio_ja.wav | 668180253 | 123,715,302 |
| EP004_motion_v01.csv | 668180682 | 2,817 |
| EP004_pronunciation_en.m4a | 668180796 | 1,734,133 |
| EP004_pronunciation_en.txt | 668180874 | 1,651 |
| EP004_pronunciation_ja.m4a | 668180955 | 1,177,186 |
| EP004_pronunciation_ja.txt | 668181042 | 1,520 |
| EP004_review_frames.zip | 668181096 | 10,052,433 |
| EP004_source_credits.md | 668181231 | 6,537 |
| EP004_thumbnail_A01.jpg | 668181279 | 289,634 |
| EP004_thumbnail_A21.jpg | 668181342 | 473,829 |
| EP004_upload_info_en.md | 668181400 | 4,371 |
| EP004_upload_info_ja.md | 668181444 | 4,453 |
| R01_OpenAI_v01.png | 668181498 | 2,028,372 |
| R02_OpenAI_v01.png | 668181553 | 3,072,032 |
| R03_OpenAI_v01.png | 668181606 | 2,205,798 |
| R04_OpenAI_v01.png | 668181698 | 2,631,286 |
| R05_OpenAI_v01.png | 668181756 | 2,449,701 |
| V01_Kling_v01.mp4 | 668181848 | 23,450,938 |
| V02_Kling_v01.mp4 | 668181991 | 10,262,372 |
| V03_Kling_v01.mp4 | 668182120 | 15,294,914 |
| ai_generation_costs.json | 668182224 | 266 |
| ai_images.json | 668182307 | 6,456 |
| ai_video_attempts.json | 668182430 | 7,528 |
| ai_videos.json | 668182510 | 4,800 |
| asset_usage_v01.json | 668182563 | 3,877 |
| audio_qc.json | 668182609 | 735 |
| chapters.json | 668182670 | 962 |
| container_precision.json | 668182742 | 3,404 |
| content.json | 668182844 | 13,038 |
| content_en.json | 668182939 | 10,710 |
| final_checks.json | 668183025 | 24,903 |
| first_pass_pronunciation_analysis.json | 668183112 | 6,665 |
| master_timeline.json | 668183213 | 4,443 |
| motion_v01.json | 668183298 | 397,459 |
| narration_segments_en.json | 668183391 | 51,796 |
| narration_segments_en_first_pass.json | 668183482 | 47,750 |
| narration_segments_ja.json | 668183577 | 58,195 |
| narration_segments_ja_first_pass.json | 668183664 | 56,604 |
| narration_timeline_en.json | 668183745 | 55,148 |
| narration_timeline_ja.json | 668183824 | 61,292 |
| preview.html | 668183899 | 1,780 |
| pronunciation_auditions.json | 668183966 | 14,774 |
| pronunciation_locations.json | 668184035 | 7,806 |
| qc_v01.json | 668184126 | 3,773 |
| queries_en.json | 668184186 | 24,376 |
| queries_en_first_pass.json | 668184277 | 21,405 |
| queries_ja.json | 668184357 | 829,250 |
| queries_ja_first_pass.json | 668184444 | 830,266 |
| reading_replacements.json | 668184505 | 6,903 |
| render_shots.json | 668184586 | 36,710 |
| request.json | 668184675 | 1,375 |
| runtime.json | 668184762 | 1,568 |
| sentence_boundary_validation.json | 668184853 | 22,351 |
| shot_center_validation.json | 668184923 | 10,729 |
| source_assets.json | 668184993 | 49,224 |
| source_preservation.json | 668185070 | 4,199 |
| subtitle_cues_en.json | 668185120 | 17,029 |
| subtitle_cues_ja.json | 668185199 | 19,456 |
| subtitle_layout_validation.json | 668185263 | 98,910 |
| subtitle_validation.json | 668185343 | 251 |
| visual_manifest.json | 668185402 | 33,869 |
| visual_review.json | 668185448 | 1,923 |
| wav_sample_validation.json | 668185510 | 466 |
| SHA256SUMS_shared.txt | 668185565 | 6,546 |
