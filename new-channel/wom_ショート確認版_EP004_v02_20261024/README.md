# パンドラ ショート3本 v02

Claudeの修正依頼3点を反映。**3本の音声はv01とストリームSHA-256一致。台本・尺・切替時刻・素材・札・出典は維持。YouTube未投稿。**

Mac再生ページ：`/Users/ryo/Desktop/新チャンネル/ショート/EP004_確認版_v02_20261024/deliverables/preview.html`。[新規非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-10faac7611cd87090140)、Release ID **422400092**。21添付・27,116,852 bytesをRESTで再取得しSHA-256・サイズ一致。

| 本 | 秒 | LUFS | dBTP | v01音声との比較 |
|---|---:|---:|---:|---|
| P1 | 19.000 | -13.99 | -2.18 | 一致 |
| P2 | 20.000 | -14.00 | -2.16 | 一致 |
| P3 | 19.667 | -14.01 | -2.25 | 一致 |

```sh
gh api repos/yasukawa1980/youtube/releases/422400092 --jq '.assets[] | [.id,.name]'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

- P1：[中央](frames/QO_short_EP004_P1_v02_mid.jpg)／[2秒おき](frames/QO_short_EP004_P1_v02_every2s.jpg)
- P2：[中央](frames/QO_short_EP004_P2_v02_mid.jpg)／[2秒おき](frames/QO_short_EP004_P2_v02_every2s.jpg)
- P3：[中央](frames/QO_short_EP004_P3_v02_mid.jpg)／[2秒おき](frames/QO_short_EP004_P3_v02_every2s.jpg)

[aboutの字幕](frames/QO_short_EP004_P1_v02_about.jpg)／[A12の始点・中央・終点](frames/QO_short_EP004_P2_v02_A12_motion.jpg)／[A02の始点・中央・終点](frames/QO_short_EP004_P3_v02_A02_motion.jpg)。[音声一致検査](records/media_qc.json)／[動き](records/motion_qc.json)／[変更記録](records/revision.json)。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| QO_short_EP004_P1_v02.mp4 | 670728861 | 4,858,851 |
| QO_short_EP004_P1_v02.srt | 670728937 | 529 |
| QO_short_EP004_P1_v02_about.jpg | 670728999 | 41,302 |
| QO_short_EP004_P1_v02_every2s.jpg | 670729053 | 195,266 |
| QO_short_EP004_P1_v02_mid.jpg | 670729100 | 105,015 |
| QO_short_EP004_P2_v02.mp4 | 670729157 | 8,797,202 |
| QO_short_EP004_P2_v02.srt | 670729256 | 598 |
| QO_short_EP004_P2_v02_A12_motion.jpg | 670729314 | 141,204 |
| QO_short_EP004_P2_v02_every2s.jpg | 670729377 | 193,998 |
| QO_short_EP004_P2_v02_mid.jpg | 670729441 | 162,935 |
| QO_short_EP004_P3_v02.mp4 | 670729493 | 12,210,648 |
| QO_short_EP004_P3_v02.srt | 670729559 | 628 |
| QO_short_EP004_P3_v02_A02_motion.jpg | 670729615 | 99,816 |
| QO_short_EP004_P3_v02_every2s.jpg | 670729664 | 203,736 |
| QO_short_EP004_P3_v02_mid.jpg | 670729733 | 99,268 |
| asset_usage.csv | 670729766 | 747 |
| motion_qc.csv | 670729798 | 588 |
| preview.html | 670729837 | 1,423 |
| qc_summary.csv | 670729883 | 387 |
| scripts.txt | 670729928 | 867 |
| SHA256SUMS_shared.txt | 670729977 | 1,844 |
