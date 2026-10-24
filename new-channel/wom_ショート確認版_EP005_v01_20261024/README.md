# 第5話「天狗」ショート確認版 v01：T1・T3完成、T2保留

**3本完成ではない。** T1・T3は検査済み。T2は音声と素材準備までで、映像の尺の方針を本人に確認中。YouTube未投稿。

Mac確認ページ：`/Users/ryo/Desktop/新チャンネル/ショート/EP005_確認版_v01_20261024/deliverables/preview.html`。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-46b0ae0ab52baefc2e7a)、Release ID **422564276**。全16添付をRelease ID指定RESTで再取得し、SHA-256・サイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/422564276 --jq '.assets[] | [.id,.name]'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 本 | 秒 | frames | LUFS | dBTP | 声の開始秒 |
|---|---:|---:|---:|---:|---:|
| T1 | 20.000 | 600 | -14.00 | -2.53 | 0.10 |
| T3 | 20.000 | 600 | -13.99 | -2.53 | 0.08 |

- T1：[2秒おき](frames/QO_short_EP005_T1_v01_every2s.jpg)／[中央](frames/QO_short_EP005_T1_v01_mid.jpg)
- T3：[2秒おき](frames/QO_short_EP005_T3_v01_every2s.jpg)／[中央](frames/QO_short_EP005_T3_v01_mid.jpg)

T2の確認用音声は `EP005_T2_native_for_script_review.wav`。完成動画ではない。[尺の問題](records/T2_timing_question.json)／[発音の継承](records/reading_correction.json)／[照合記録](records/sharing.json)。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP005_T2_native_for_script_review.wav | 671502276 | 785,578 |
| QO_short_EP005_T1_v01.mp4 | 671502338 | 1,869,440 |
| QO_short_EP005_T1_v01.srt | 671502404 | 634 |
| QO_short_EP005_T1_v01_every2s.jpg | 671502453 | 85,963 |
| QO_short_EP005_T1_v01_mid.jpg | 671502508 | 30,160 |
| QO_short_EP005_T3_v01.mp4 | 671502561 | 16,477,471 |
| QO_short_EP005_T3_v01.srt | 671502658 | 564 |
| QO_short_EP005_T3_v01_every2s.jpg | 671502718 | 240,825 |
| QO_short_EP005_T3_v01_mid.jpg | 671502778 | 184,513 |
| T2_timing_pending.txt | 671502813 | 402 |
| asset_usage.csv | 671502845 | 649 |
| motion_qc.csv | 671502899 | 474 |
| preview.html | 671502926 | 1,269 |
| qc_summary.csv | 671502984 | 286 |
| scripts.txt | 671503014 | 568 |
| SHA256SUMS_shared.txt | 671503053 | 1,352 |
