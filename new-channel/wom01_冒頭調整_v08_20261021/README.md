# Quiet Origins：アヌビス v08（日本語冒頭の間・字幕調整）

本人承認の申し送りを反映。日本語N01の既存5文をそのまま配置し、4か所の間を+0.8/+0.8/+1.0/+1.5秒。話し終わり27.622667秒、オープニングまで1.444秒。
映像ストリーム・英語音声・BGMはv07と同一。日本語N02以降の語りサンプルと130字幕も同一。全編682.700秒・20,481フレーム。通常版は字幕焼き込みなし、字幕入り確認用コピーを別添付。オープニング・エンドカードはまだ全編には挿入していない。日本語全編約−16 LUFS。

## 確認用動画と保存先

Mac：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/Quiet_Origins_v08_20261021`。`deliverables/preview.html` はまとめて再生するページ。全編の字幕入り確認動画は `subtitled_review/deliverables/`、その他は `deliverables/`。
共有添付を同じフォルダに取得すれば `preview.html` から再生できます。

## 実測と保全

[qc_v08.json](records/qc_v08.json)、[画面確認](records/visual_review.json)、[共有照合](records/sharing.json)。音の聴感は本人の試聴待ち。以前の版は保存済み。指定SSDは未同期。追加支出・YouTube投稿・Release公開なし。

## Claudeからの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-87350936d2f2f0fa9d00)／Release ID **419342296**。全12件をRESTで再取得しSHA-256とサイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/419342296 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v08_1080p30.mp4 | 661916351 | 194,048,913 |
| EP001_Anubis_en_v08_1080p30.srt | 661917044 | 13,252 |
| EP001_Anubis_ja_v08_1080p30.mp4 | 661917106 | 193,514,711 |
| EP001_Anubis_ja_v08_1080p30.srt | 661917652 | 15,346 |
| EP001_audio_en.m4a | 661917733 | 16,143,257 |
| EP001_audio_ja.m4a | 661917824 | 15,609,039 |
| EP001_thumbnail_en.jpg | 661918011 | 407,649 |
| VOICE_CREDITS.txt | 661918080 | 129 |
| EP001_Anubis_en_v08_subtitled_review_1080p30.mp4 | 661918133 | 184,680,236 |
| EP001_Anubis_ja_v08_subtitled_review_1080p30.mp4 | 661918627 | 184,375,425 |
| preview.html | 661919211 | 1,917 |
| SHA256SUMS_shared.txt | 661919281 | 1,044 |
