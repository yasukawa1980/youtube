# Quiet Origins パンドラ ショート3本 v01

確認用・YouTube未投稿。英語音声と英語字幕、縦1080×1920・30fps。

Mac再生ページ：`/Users/ryo/Desktop/新チャンネル/ショート/EP004_確認版_v01_20261024/deliverables/preview.html`。完成MP4は `/Users/ryo/Desktop/新チャンネル/ショート` にも保存。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-4bfd217af695d4a46ef4)、Release ID **422102895**。添付18点をRelease ID指定RESTで取得し直し、SHA-256とバイト数を照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/422102895 --jq '.assets[] | [.id,.name]'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| ID | 秒 | フレーム | LUFS | dBTP | 声の開始秒 | 末尾案内秒 |
|---|---:|---:|---:|---:|---:|---:|
| P1 | 19.000 | 570 | -13.99 | -2.18 | 0.09 | 2.000 |
| P2 | 20.000 | 600 | -14.00 | -2.16 | 0.05 | 1.967 |
| P3 | 19.667 | 590 | -14.01 | -2.25 | 0.09 | 2.000 |

- P1：[中央](frames/QO_short_EP004_P1_v01_mid.jpg)／[2秒おき](frames/QO_short_EP004_P1_v01_every2s.jpg)
- P2：[中央](frames/QO_short_EP004_P2_v01_mid.jpg)／[2秒おき](frames/QO_short_EP004_P2_v01_every2s.jpg)
- P3：[中央](frames/QO_short_EP004_P3_v01_mid.jpg)／[2秒おき](frames/QO_short_EP004_P3_v01_every2s.jpg)

[使用素材](deliverables/asset_usage.csv)／[台本](deliverables/scripts.txt)／[発音の継承](records/reading_correction.json)／[共有照合](records/sharing.json)。SRTは動画へ焼き込んだ字幕と同じ。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| QO_short_EP004_P1_v01.mp4 | 669790978 | 4,858,309 |
| QO_short_EP004_P1_v01.srt | 669791115 | 529 |
| QO_short_EP004_P1_v01_every2s.jpg | 669791189 | 195,250 |
| QO_short_EP004_P1_v01_mid.jpg | 669791279 | 105,015 |
| QO_short_EP004_P2_v01.mp4 | 669791376 | 7,037,938 |
| QO_short_EP004_P2_v01.srt | 669791518 | 598 |
| QO_short_EP004_P2_v01_every2s.jpg | 669791636 | 160,762 |
| QO_short_EP004_P2_v01_mid.jpg | 669791723 | 71,132 |
| QO_short_EP004_P3_v01.mp4 | 669791819 | 7,497,369 |
| QO_short_EP004_P3_v01.srt | 669791971 | 628 |
| QO_short_EP004_P3_v01_every2s.jpg | 669792049 | 150,752 |
| QO_short_EP004_P3_v01_mid.jpg | 669792151 | 41,572 |
| asset_usage.csv | 669792224 | 805 |
| motion_qc.csv | 669792311 | 588 |
| preview.html | 669792392 | 1,423 |
| qc_summary.csv | 669792458 | 387 |
| scripts.txt | 669792559 | 867 |
| SHA256SUMS_shared.txt | 669792633 | 1,540 |
