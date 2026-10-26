# EP006 スフィンクス v01 — 取得・再生案内

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-605664bf941c970554af)／Release ID **424086149**。全26添付をRESTから再取得し、SHA-256一致を確認済みです。公開していません。

最初は `EP006_Sphinx_ja_v01_subtitled_review_1080p30.mp4` または英語の同名 `en` 版をご覧ください。通常版は字幕焼き込みなしです。

Macでは `/Users/ryo/Desktop/新チャンネル/EP006_Sphinx/確認版_v01_20261026/deliverables/preview.html` を開くと両言語・固有名詞試聴・サムネ2案を確認できます。他の環境ではReleaseの `preview.html` とMP4/M4A/JPGを同じフォルダへ取得して開いてください。

## Claudeからの取得

Draftは通常のタグURLや未認証アクセスで取得できない場合があります。認証済みRESTで**Release ID**を指定してください。

```sh
gh api repos/yasukawa1980/youtube/releases/424086149
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

asset ID・SHA・bytesの全一覧：[sharing.json](records/sharing.json)。検査一式は `EP006_records.zip`、抽出画像は `EP006_review_frames.zip`、Kling原本5本は `EP006_Kling_originals.zip`。

[制作結果と本人の確認項目](../wom06_制作結果_v01_20261026.md)／[モロー本編中央](frames/center_en_18.jpg)／[英語の読み時刻](EP006_pronunciation_en.txt)／[日本語の読み時刻](EP006_pronunciation_ja.txt)。
