# Quiet Origins アヌビス v05：字幕入り確認用

2026-10-21、本人の「Claudeの申し送り確認と、確認用の字幕入り動画作成」に対応。

## Claudeの申し送りと対応

[Claudeのv05確認](../wom01_Claude確認_v05_20261021.md)（`e62371d`）は、名称・音声クレジット・尺・フレーム・音声・SRTに問題なし、**v05の再生成は不要**という結論。
標準サイズの字幕は図解・クレジットに重なる80件すべてで重なりなし。極端な拡大で3行に折り返した場合だけ4件が重なるため、第2話以降の参考として記録されています。

通常のv05は変更せず、**標準サイズの字幕を焼き込んだ確認用コピー2本**を作成しました。英語音声には英語字幕、日本語音声には日本語字幕です。

## 開くだけで字幕が表示される動画

Mac保存先：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/字幕入り確認用_v05_20261021/deliverables/`

- 日本語：`EP001_Anubis_ja_v05_subtitled_review_1080p30.mp4`
- 英語：`EP001_Anubis_en_v05_subtitled_review_1080p30.mp4`
- **SRTの読み込み不要。字幕は映像に固定されているためオフにできません。** 外部字幕を重ねる必要はありません。
- 字幕なしの通常版は [v05の案内](../wom01_Quiet_Origins_v05_20261021/README.md)にあります。

英語150件・日本語136件、本文・時刻は既存v05のSRTをそのまま使用。libassの設定は `original_size=1920x1080 / FontSize=14 / BorderStyle=3 / MarginV=12`。白字・黒背景の標準サイズです。
音声・BGMはコピーし再エンコードなし。映像のみ字幕を描画してH.264 CRF18で再エンコード。

## 検品

- 両言語とも **682.700秒、1920×1080、30fps、20,481フレーム**。全編デコード成功、全フレームのPTSが1/30秒刻みで連続。
- 音声ストリームのSHA-256はv05と一致。元のMP4・SRTのSHA-256も制作前後で一致。
- 英語150件・日本語136件の全字幕について、表示中のフレームで焼き込み文字の画素が増えていることを元動画との比較で確認。0.3秒以上の字幕の隙間では字幕が残っていないことも確認。
- [実際の字幕入り動画の確認画像](frames/subtitled_review_contact.jpg)。冒頭・箱型図解・天秤・クレジット等を画像で確認。Claudeが拡大字幕の重なりを指摘した4件も標準サイズで確認。
- [全編検品](records/qc.json)／[全字幕の表示検査](records/subtitle_presence_checks.json)／[画像確認](records/visual_review.json)。画素検査はOCRや人の通し視聴の代替ではありません。

本人の全編試聴は引き続き未確認。「はかり」4か所・07:18の「オシリス」・間・BGMの聴感は、元のv05と同じ確認項目です。

## Claudeの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-6c38c58ad1a522313754)／Release ID **419137582**。全4添付をRESTで再取得しSHA-256一致。

```sh
gh api repos/yasukawa1980/youtube/releases/419137582 --jq '.assets[] | "\(.id) \(.name) \(.digest)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v05_subtitled_review_1080p30.mp4 | 661288001 | 159,732,805 |
| EP001_Anubis_ja_v05_subtitled_review_1080p30.mp4 | 661288313 | 159,614,187 |
| VOICE_CREDITS.txt | 661288859 | 129 |
| SHA256SUMS_shared.txt | 661288923 | 314 |

## 再現・条件

`../wom01_subtitled_review.py render` → `verify`。`WOM_EPISODE_ROOT` は通常版v05、`WOM_REVIEW_ROOT` は新規の確認用フォルダを指定。既存の一時Python環境とimageio-ffmpeg 0.6.0（FFmpeg7.1/libass）を使用。画像確認記録の作成後、`../wom01_share_subtitled_review.py` でDraft共有・再取得照合。
日本語音声：VOICEVOX:冥鳴ひまり／英語：Kokoro / Heart (af_heart)。追加契約・購入・YouTube投稿・チャンネル開設・Release公開なし。元のv05とそのDraft Releaseは変更なし。指定SSD ESD-EPBは未接続のため未同期。
