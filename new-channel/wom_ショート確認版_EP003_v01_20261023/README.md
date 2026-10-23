# Quiet Origins メドゥーサ ショート3本 v01

英語音声・英語字幕入り。縦1080×1920・30fps。**YouTube未投稿。Claudeと本人の確認待ち。**

Mac：`/Users/ryo/Desktop/新チャンネル/ショート/EP003_確認版_v01_20261023/deliverables/preview.html` で3本を再生できる。Gitには動画を入れていない。Claudeは以下の非公開Draftから取得する。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-c5e64c61e7b5ec470e76)、Release ID **421362774**。全18添付をRelease ID指定RESTで再取得し、SHA-256とバイト数が一致した。

```sh
gh api repos/yasukawa1980/youtube/releases/421362774 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| ID | 秒 | フレーム | LUFS | dBTP | 声の開始秒 | 末尾案内秒 |
|---|---:|---:|---:|---:|---:|---:|
| M1 | 19.333 | 580 | -14.06 | -2.90 | 0.12 | 2.000 |
| M2 | 17.100 | 513 | -14.00 | -2.00 | 0.06 | 2.000 |
| M3 | 20.000 | 600 | -14.02 | -2.33 | 0.12 | 1.533 |

- M1：[中央](frames/QO_short_EP003_M1_v01_mid.jpg)／[2秒おき](frames/QO_short_EP003_M1_v01_every2s.jpg)
- M2：[中央](frames/QO_short_EP003_M2_v01_mid.jpg)／[2秒おき](frames/QO_short_EP003_M2_v01_every2s.jpg)
- M3：[中央](frames/QO_short_EP003_M3_v01_mid.jpg)／[2秒おき](frames/QO_short_EP003_M3_v01_every2s.jpg)

[使用一覧](deliverables/asset_usage.csv)／[台本](deliverables/scripts.txt)／[字幕検査](records/subtitle_qc.json)／[動き](records/motion_qc.json)／[共有照合](records/sharing.json)。SRTは検品用で、動画には同じ字幕が焼き込み済み。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| QO_short_EP003_M1_v01.mp4 | 667626862 | 8,385,611 |
| QO_short_EP003_M1_v01.srt | 667626951 | 572 |
| QO_short_EP003_M1_v01_every2s.jpg | 667627039 | 222,833 |
| QO_short_EP003_M1_v01_mid.jpg | 667627092 | 110,937 |
| QO_short_EP003_M2_v01.mp4 | 667627137 | 3,662,802 |
| QO_short_EP003_M2_v01.srt | 667627195 | 531 |
| QO_short_EP003_M2_v01_every2s.jpg | 667627242 | 143,714 |
| QO_short_EP003_M2_v01_mid.jpg | 667627297 | 58,680 |
| QO_short_EP003_M3_v01.mp4 | 667627337 | 3,712,232 |
| QO_short_EP003_M3_v01.srt | 667627427 | 606 |
| QO_short_EP003_M3_v01_every2s.jpg | 667627467 | 204,999 |
| QO_short_EP003_M3_v01_mid.jpg | 667627501 | 82,699 |
| asset_usage.csv | 667627545 | 805 |
| motion_qc.csv | 667627598 | 587 |
| preview.html | 667627638 | 1,433 |
| qc_summary.csv | 667627694 | 398 |
| scripts.txt | 667627752 | 858 |
| SHA256SUMS_shared.txt | 667627785 | 1,540 |

## 再現手順

既存のMacメディア・Kokoroモデル・Python音声制作環境を使用する。`wom03_shorts.py narration → captions → audio → visuals → render`、`wom03_shorts_qc.py motion → glyphs → verify → frames` の順で実行。画像を目視確認して `records/visual_review.json` に対象動画ハッシュと結果を記録後、`wom03_shorts_delivery.py docs → share → report`。字幕の割当と描画・検査は共有した `wom_shorts_produce.py`・`wom_shorts_qc.py` を再利用する。動画・モデル・原寸資料はGitには含めない。
