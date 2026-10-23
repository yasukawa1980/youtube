# Quiet Origins パンドラ v02

A04（0:51〜1:02）の切り出しだけ修正。英日通常版429.566667秒・12,887フレーム。**Claude確認待ち・YouTube未投稿。v01を保全。**

Mac：`/Users/ryo/Desktop/新チャンネル/EP004_Pandora/確認版_v02_20261023/deliverables/preview.html`。修正箇所だけの11秒MP4も同梱。全編は通常版＋v01と同一の外部SRT。全編の字幕焼き込み版は再生成していない。

[新しい非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-fb1c0767579762444bf4)、Release ID **421630198**。全19添付をRelease ID指定RESTで再取得し、SHA-256・サイズが一致。

```sh
gh api repos/yasukawa1980/youtube/releases/421630198 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

[修正後の構図](frames/A04_v02_composition.jpg)／[修正前後](frames/A04_before_after.jpg)／[修正区間6時点](frames/A04_v02_six_frames.jpg)。[全フレーム照合・音声一致](records/qc_v02.json)／[動き](records/motion_A04_v02.json)／[切り出し座標](records/revision.json)。

再現：既存v01素材を用い `wom04_revision_v02.py prepare → render → verify → motion → preview`。画像を目視し `visual_review_v02.json` に対象のハッシュと結果を保存してから、`wom04_revision_v02_delivery.py docs → share → report`。原寸資料や音声モデルの再生成なし。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| A04_before_after.jpg | 668547119 | 75,033 |
| A04_v02_composition.jpg | 668547189 | 93,425 |
| A04_v02_six_frames.jpg | 668547245 | 105,524 |
| EP004_A04_v02_preview.mp4 | 668547308 | 2,349,514 |
| EP004_Pandora_en_v02_1080p30.mp4 | 668547399 | 121,399,994 |
| EP004_Pandora_en_v02_1080p30.srt | 668547735 | 8,116 |
| EP004_Pandora_ja_v02_1080p30.mp4 | 668547810 | 121,481,691 |
| EP004_Pandora_ja_v02_1080p30.srt | 668548207 | 10,631 |
| EP004_audio_ja.wav | 668548267 | 123,715,302 |
| EP004_source_credits.md | 668548649 | 6,537 |
| EP004_thumbnail_A01.jpg | 668548738 | 289,634 |
| EP004_thumbnail_A21.jpg | 668548832 | 473,829 |
| EP004_upload_info_en.md | 668548912 | 4,371 |
| EP004_upload_info_ja.md | 668548961 | 4,453 |
| motion_A04_v02.json | 668549008 | 9,239 |
| preview.html | 668549065 | 1,189 |
| qc_v02.json | 668549228 | 2,530 |
| revision.json | 668549284 | 780 |
| SHA256SUMS_shared.txt | 668549344 | 1,612 |
