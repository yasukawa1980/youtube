# Quiet Origins：オープニング・エンドカード試作 v02

オープニング既存音声を+7 dB、4秒・音色・フェード・映像を維持。単体約−22 LUFS。英日の字幕入り冒頭接続版を更新し、日本語はv08の間と字幕を反映。
エンドカード単体と英日末尾接続版はv01をバイト一致で継続使用（ファイル名もv01）。本編に挿入する前の試聴用。日本語の最後の問いの前（19.9〜21.7秒）の溜めと、ロゴ部分の音量を確認してください。

## 確認用動画と保存先

Mac：`/Users/ryo/Desktop/新チャンネル/ブランド素材/オープニング_エンドカード_動画試作_v02_20261021`。`deliverables/preview.html` はまとめて再生するページ。動画6本と単体音声2本は `deliverables/`。本編v08は別フォルダ。
共有添付を同じフォルダに取得すれば `preview.html` から再生できます。

## 実測と保全

[qc_v02.json](records/qc_v02.json)、[画面確認](records/visual_review.json)、[共有照合](records/sharing.json)。音の聴感は本人の試聴待ち。以前の版は保存済み。指定SSDは未同期。追加支出・YouTube投稿・Release公開なし。

## Claudeからの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-e83776552752086a4d81)／Release ID **419345783**。全10件をRESTで再取得しSHA-256とサイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/419345783 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_en_endcard_connection_trial_v01.mp4 | 661924860 | 4,051,909 |
| EP001_en_opening_connection_trial_v02.mp4 | 661925005 | 10,506,159 |
| EP001_ja_endcard_connection_trial_v01.mp4 | 661925082 | 4,077,679 |
| EP001_ja_opening_connection_trial_v02.mp4 | 661925155 | 10,455,317 |
| Quiet_Origins_endcard_trial_v01.mp4 | 661925320 | 1,771,061 |
| Quiet_Origins_opening_trial_v02.mp4 | 661925428 | 844,119 |
| Quiet_Origins_endcard_trial_v01.wav | 661925529 | 5,760,044 |
| Quiet_Origins_opening_trial_v02.wav | 661926504 | 1,152,044 |
| preview.html | 661926655 | 2,317 |
| SHA256SUMS_shared.txt | 661926756 | 919 |
