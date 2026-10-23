# メドゥーサ ショート3本 v02

M2の素材切替・M3の年代字幕だけを修正。M1はv01とMP4全体が一致、3本の音声はv01とストリーム一致。**YouTube未投稿。v01を保全。**

Mac：`/Users/ryo/Desktop/新チャンネル/ショート/EP003_確認版_v02_20261023/deliverables/preview.html`。[新しい非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-fa8b643504a53bcffbe7)、Release ID **421392117**。全20添付のSHA-256とサイズをRelease ID指定RESTで照合済み。動画はGitに含めない。

| ID | 秒 | フレーム | LUFS | dBTP | v01との音声 |
|---|---:|---:|---:|---:|---|
| M1 | 19.333 | 580 | -14.06 | -2.90 | 一致 |
| M2 | 17.100 | 513 | -14.00 | -2.00 | 一致 |
| M3 | 20.000 | 600 | -14.02 | -2.33 | 一致 |

```sh
gh api repos/yasukawa1980/youtube/releases/421392117 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

- M1：[中央](frames/QO_short_EP003_M1_v02_mid.jpg)／[2秒おき](frames/QO_short_EP003_M1_v02_every2s.jpg)
- M2：[中央](frames/QO_short_EP003_M2_v02_mid.jpg)／[2秒おき](frames/QO_short_EP003_M2_v02_every2s.jpg)
- M3：[中央](frames/QO_short_EP003_M3_v02_mid.jpg)／[2秒おき](frames/QO_short_EP003_M3_v02_every2s.jpg)

[M2切替の前後フレーム](frames/QO_short_EP003_M2_v02_cut_check.jpg)／[M3の450 BCE](frames/QO_short_EP003_M3_v02_450_BCE.jpg)。[変更時刻](records/revision.json)／[音声一致](records/media_qc.json)／[字幕枠](records/subtitle_qc.json)／[全フレームの動き](records/motion_qc.json)。

再現：既存v01メディアを使い `wom03_shorts_v02.py prepare → render`、`wom03_shorts_v02_qc.py verify → motion → glyphs → frames`。画像確認を `visual_review.json` に記録後、`wom03_shorts_v02_delivery.py docs → share → report`。音声の再合成・再エンコードなし。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| QO_short_EP003_M1_v02.mp4 | 667736550 | 8,385,611 |
| QO_short_EP003_M1_v02.srt | 667736645 | 572 |
| QO_short_EP003_M1_v02_every2s.jpg | 667736706 | 222,833 |
| QO_short_EP003_M1_v02_mid.jpg | 667736755 | 110,937 |
| QO_short_EP003_M2_v02.mp4 | 667736815 | 3,715,318 |
| QO_short_EP003_M2_v02.srt | 667736944 | 531 |
| QO_short_EP003_M2_v02_cut_check.jpg | 667736998 | 111,750 |
| QO_short_EP003_M2_v02_every2s.jpg | 667737040 | 146,766 |
| QO_short_EP003_M2_v02_mid.jpg | 667737117 | 58,345 |
| QO_short_EP003_M3_v02.mp4 | 667737231 | 3,715,704 |
| QO_short_EP003_M3_v02.srt | 667737300 | 606 |
| QO_short_EP003_M3_v02_450_BCE.jpg | 667737368 | 58,998 |
| QO_short_EP003_M3_v02_every2s.jpg | 667737420 | 205,618 |
| QO_short_EP003_M3_v02_mid.jpg | 667737493 | 82,696 |
| asset_usage.csv | 667737564 | 747 |
| motion_qc.csv | 667737634 | 584 |
| preview.html | 667737697 | 1,433 |
| qc_summary.csv | 667737762 | 398 |
| scripts.txt | 667737824 | 858 |
| SHA256SUMS_shared.txt | 667737871 | 1,742 |
