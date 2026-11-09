# 第14話「鬼」確認版v01 制作途中

英日1080p通常版・字幕入り版の技術検品と画面一覧の確認まで完了。英語13,543フレーム・451.433秒・−16.01 LUFS、日本語13,525フレーム・450.833秒・−16.00 LUFS。いずれも全編デコード警告0。英語4Kは制作中。英日1080pの4本は非公開Draft Releaseへ先行格納し、Release ID経由のREST全量再取得でサイズ・SHA-256一致と匿名404を確認済み。

[英語投稿情報](EP014_upload_info_en.md)・[日本語投稿情報](EP014_upload_info_ja.md)。全31ショットの先頭・中央・末尾、冒頭0/1/2/3秒、字幕入り8場面を各言語で確認済み。

このフォルダは途中の検品画像・記録です。完成時に取得案内へ更新します。

[非公開Draft Release・1080p先行格納](https://github.com/yasukawa1980/youtube/releases/tag/untagged-935d399b2f81942c8238)（Release ID `439356085`）。4K・付属ZIPは後から同じDraftへ追加します。

|添付|asset ID|バイト|SHA-256|
|---|---:|---:|---|
|EP014_Oni_en_v01_1080p30.mp4|728111510|60463581|`a2da4480600b0b39fd8e955b05d3380bf0d7381f74da76130e69018f6691a5ec`|
|EP014_Oni_en_v01_subtitled_review_1080p30.mp4|728111870|43339590|`08748b0fb7dfd7fb6f62b0bcd337c029b2c85c765c630c735a867cfac87236ed`|
|EP014_Oni_ja_v01_1080p30.mp4|728112252|60254574|`60b347797bb2013a488912f41501d3177845ea2b217d033e6c5b7705328b4fba`|
|EP014_Oni_ja_v01_subtitled_review_1080p30.mp4|728112590|42923938|`286d616710adbc36084bdc8a08fe16d7ceeffa987a7093d12a79549082d90381`|

取得：`gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT`。一覧：`gh api repos/yasukawa1980/youtube/releases/439356085`。
