# 第5話「天狗」ショート確認版 v01：3本完成

本人の「20秒以内はこだわっていないので全体のバランスが良ければ尺は大丈夫です」（2026-10-24）を反映し、T2の保留を解消。T1・T3は初回共有からファイルSHA-256一致。YouTube未投稿、Claude確認と本人試聴待ち。

Mac確認ページ：`/Users/ryo/Desktop/新チャンネル/ショート/EP005_確認版_v01_20261024/deliverables/preview.html`。

[完成3本の非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-a5c8e5bc7ab573c6b5c8)、Release ID **422594196**。全19添付をRelease ID指定RESTで再取得し、SHA-256・サイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/422594196 --jq '.assets[] | [.id,.name]'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 本 | 秒 | frames | LUFS | dBTP | 声の開始秒 |
|---|---:|---:|---:|---:|---:|
| T1 | 20.000 | 600 | -14.00 | -2.53 | 0.10 |
| T2 | 21.133 | 634 | -13.98 | -2.65 | 0.11 |
| T3 | 20.000 | 600 | -13.99 | -2.53 | 0.08 |

- T1：[2秒おき](frames/QO_short_EP005_T1_v01_every2s.jpg)／[中央](frames/QO_short_EP005_T1_v01_mid.jpg)
- T2：[2秒おき](frames/QO_short_EP005_T2_v01_every2s.jpg)／[中央](frames/QO_short_EP005_T2_v01_mid.jpg)
- T3：[2秒おき](frames/QO_short_EP005_T3_v01_every2s.jpg)／[中央](frames/QO_short_EP005_T3_v01_mid.jpg)

[素材一覧](deliverables/asset_usage.csv)／[台本](deliverables/scripts.txt)／[発音](records/reading_correction.json)／[T2速度調整](records/T2_video_retime.json)／[完成版の共有照合](records/sharing_complete.json)。

初回の部分共有Release `422564276` と `records/sharing.json`、`deliverables/T2_timing_pending.txt` は履歴として保全。**現在のT2は保留ではない。最新は上記の完成3本Releaseと本README。**

| 添付 | Asset ID | bytes |
|---|---:|---:|
| QO_short_EP005_T1_v01.mp4 | 671637687 | 1,869,440 |
| QO_short_EP005_T1_v01.srt | 671637806 | 634 |
| QO_short_EP005_T1_v01_every2s.jpg | 671637862 | 85,963 |
| QO_short_EP005_T1_v01_mid.jpg | 671637926 | 30,160 |
| QO_short_EP005_T2_v01.mp4 | 671637990 | 4,256,118 |
| QO_short_EP005_T2_v01.srt | 671638075 | 617 |
| QO_short_EP005_T2_v01_every2s.jpg | 671638148 | 173,744 |
| QO_short_EP005_T2_v01_mid.jpg | 671638206 | 72,175 |
| QO_short_EP005_T2_v01_transition.jpg | 671638242 | 135,562 |
| QO_short_EP005_T3_v01.mp4 | 671638294 | 16,477,471 |
| QO_short_EP005_T3_v01.srt | 671638384 | 564 |
| QO_short_EP005_T3_v01_every2s.jpg | 671638417 | 240,825 |
| QO_short_EP005_T3_v01_mid.jpg | 671638450 | 184,513 |
| asset_usage.csv | 671638493 | 878 |
| motion_qc.csv | 671638522 | 624 |
| preview.html | 671638571 | 1,514 |
| qc_summary.csv | 671638619 | 372 |
| scripts.txt | 671638652 | 857 |
| SHA256SUMS_shared.txt | 671638703 | 1,643 |
