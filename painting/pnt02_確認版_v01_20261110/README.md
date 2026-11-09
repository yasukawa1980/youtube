# pnt02 確認版v01 取得案内

非公開Draft Release ID：`439743216`。動画5本完成、本人試聴待ち。旧 preliminary ZIP は制作途中の履歴資料。公開しない。

[制作結果と未確認項目](../pnt02_制作結果_v01_20261110.md) · [最終数値](final_summary.json) · [再取得照合](final_sharing.json)

## 数値IDで取得

認証済みGitHub CLIで確認する。Releaseを公開する必要はない。

```sh
gh api repos/yasukawa1980/youtube/releases/439743216
gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/<Asset ID> > <保存名>
```

|ファイル|Asset ID|バイト数|
|---|---:|---:|
|PNT02_WashingtonCrossing_en_v01_1080p30.mp4|729400258|65,934,520|
|PNT02_WashingtonCrossing_en_v01_2160p30.mp4|729400893|333,810,526|
|PNT02_WashingtonCrossing_en_v01_subtitled_review_1080p30.mp4|729403929|36,509,341|
|PNT02_WashingtonCrossing_ja_v01_1080p30.mp4|729404465|66,831,021|
|PNT02_WashingtonCrossing_ja_v01_subtitled_review_1080p30.mp4|729405237|36,321,552|
|PNT02_audio_subtitles_final_v01.zip|729405695|188,122,317|
|PNT02_final_QC_metadata_thumbnails_v01.zip|729406947|30,351,052|

7資産すべて数値IDで再取得済み。サイズ・SHA-256一致。SHA-256全値は `final_sharing.json`。

## レビュー画像・記録

- `en/final_video_review/`：英1080p・4Kの先頭/中央/末尾の一覧、カード状態、冒頭・字幕。
- `ja/final_video_review/`：日本語1080pの同じ確認資料。
- `continuous_*_sheet_*.jpg` は最終MP4から連続デコードした一覧。`design_*`・`card_*` は以前の設計画像。
- 音声と字幕は `PNT02_audio_subtitles_final_v01.zip`。資料・サムネ・投稿情報は `PNT02_final_QC_metadata_thumbnails_v01.zip`。
- 発音は未聴取。固有名、難読語、発話と帯の厳密な同期、テンポ、縦置き・文字カード、サムネA/Bは本人確認。
