# Quiet Origins：アヌビス v09（オープニング・エンドカード組み込み全編）

本人が試聴承認したv08＋オープニングv02（4秒）＋エンドカードv01（20秒）を全編へ組み込み。702.000秒、21,060フレーム、1080p30。英日で映像ストリームは同一。ロゴ29.066667〜33.066667秒、エンドカード682〜702秒、先頭0.7秒ディゾルブ。

通常版は字幕焼き込みなし。英150・日136件のSRTは本文と改行を保ち、N02以降+4秒。最後の日本語お礼は681.691秒まで残し、682秒以降は字幕なし。字幕入り確認用コピーも添付。

本編音声を全体再正規化せず、接続部以外は元の音量を維持。動画は共通映像をCRF18で一度書き出し、英日音声をAAC192kで別々に結合。チャプターと女性声クレジットを更新した英日投稿情報を添付。

本人の公開指示待ち。YouTube投稿・Release公開・追加支出は行っていない。

## 確認用動画と保存先

Mac：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/Quiet_Origins_v09_20261021`。`deliverables/preview.html` はまとめて再生するページ。全編の字幕入り確認動画は `subtitled_review/deliverables/`、その他は `deliverables/`。
共有添付を同じフォルダに取得すれば `preview.html` から再生できます。

## 実測と保全

[qc_v09.json](records/qc_v09.json)、[画面確認](records/visual_review.json)、[共有照合](records/sharing.json)。音の聴感は本人の試聴待ち。以前の版は保存済み。指定SSDは未同期。追加支出・YouTube投稿・Release公開なし。

## Claudeからの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-fa61b8a06f8ce4f3b64d)／Release ID **419415882**。全14件をRESTで再取得しSHA-256とサイズを照合済み。

```sh
gh api repos/yasukawa1980/youtube/releases/419415882 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v09_1080p30.mp4 | 662111451 | 183,154,458 |
| EP001_Anubis_en_v09_1080p30.srt | 662111889 | 13,252 |
| EP001_Anubis_ja_v09_1080p30.mp4 | 662111954 | 182,633,175 |
| EP001_Anubis_ja_v09_1080p30.srt | 662112541 | 15,346 |
| EP001_Anubis_en_v09_subtitled_review_1080p30.mp4 | 662112610 | 174,154,175 |
| EP001_Anubis_ja_v09_subtitled_review_1080p30.mp4 | 662113053 | 173,845,939 |
| EP001_audio_en.m4a | 662113486 | 16,538,208 |
| EP001_audio_ja.m4a | 662113590 | 16,016,925 |
| EP001_thumbnail_en.jpg | 662113714 | 407,649 |
| VOICE_CREDITS.txt | 662113802 | 129 |
| EP001_upload_info_en.md | 662113863 | 4,008 |
| EP001_upload_info_ja.md | 662113918 | 3,862 |
| preview.html | 662113978 | 1,819 |
| SHA256SUMS_shared.txt | 662114023 | 1,224 |
