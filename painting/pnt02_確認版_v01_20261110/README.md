# pnt02 確認版v01の制作途中共有

**完成した確認版動画はまだありません。** このフォルダには英日音声・字幕の検品、素材・画角検証、文字カード案を置いています。年代帯のP07/P08指定の食い違いを本人へ確認中です。

[制作結果・未達条件・再開手順](../pnt02_制作結果_v01_20261110.md) · [サムネ2案](../サムネ確認用/pnt02/)

[非公開Draft Release（制作途中のみ）](https://github.com/yasukawa1980/youtube/releases/tag/untagged-37c878e25160c0b72f46)：ID **439743216**。Release ID指定のRESTで再取得し、添付2本のバイト数・SHA-256一致を確認。匿名アクセスは404。詳細は [sharing.json](sharing.json)。音声ZIPは初回の読み替えなし英日M4A/WAVとSRT、設計ZIPは静止画・サムネ・JSON記録です。**発音は未試聴。カード案の年代帯は仮配置であり、完成映像ではありません。**

英語321.200秒、日本語312.833333秒。音量は両言語−16.01 LUFS、ピーク英−2.40／日−5.20 dBTP。字幕74／70件、台本と空白以外一致。音声初回データは指定SSDに保全済みです。

SSD：`/Volumes/ESD-02/新チャンネル/PNT02_WashingtonCrossing/確認版_v01_20261110/`

完成版に向けて残る作業は、年代帯仕様の確認、発音、動画全5本の制作・検品、投稿情報、完成版Draft Releaseへの格納です。11/22中の確認版v01納品は未達です。投稿・予約・Release公開はしていません。

## 取得方法

`gh api repos/yasukawa1980/youtube/releases/439743216` で確認。添付は `gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT` で取得できます。

|ファイル|asset ID|バイト|SHA-256|
|---|---:|---:|---|
|PNT02_audio_subtitles_preliminary_v01.zip|729292432|188121684|`e7d2ba5d025bf261c7b0bd82ccbe46f35ae0f5fa63a37adf155dd10aa46ab96d`|
|PNT02_design_records_preliminary_v01.zip|729293088|1650520|`d6191e4c45f8a1c69d5f77f4afb1a8ed49d0ad5f976717213abebb10c3b73312`|

設計ZIP中のREADMEはアップロード前の案内です。取得先の最新値はこのGit上のREADMEとsharing.jsonを参照してください。
