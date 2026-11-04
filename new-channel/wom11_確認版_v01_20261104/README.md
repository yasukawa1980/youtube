# 第11話「心臓の計量」確認版v01 取得案内

本人承認済み台本v02と、天秤の表示B案を反映。**Claude確認・本人試聴待ち。YouTube未投稿、Release未公開。**

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-e9c3acc2f18d49dd7b69)、Release ID **433561970**。英日1080p通常版、英日字幕入り確認版、英語4K拡大版、資料ZIP3本。計8ファイルをRelease ID指定RESTで再取得し、バイト数・SHA-256一致、匿名404を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/433561970
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
| EP011_QA_records_v01.zip | 708412256 | 11162264 |
| EP011_WeighingOfTheHeart_en_v01_1080p30.mp4 | 708412478 | 187040257 |
| EP011_WeighingOfTheHeart_en_v01_subtitled_review_1080p30.mp4 | 708414664 | 82200544 |
| EP011_WeighingOfTheHeart_ja_v01_1080p30.mp4 | 708415492 | 186936399 |
| EP011_WeighingOfTheHeart_ja_v01_subtitled_review_1080p30.mp4 | 708417278 | 82537131 |
| EP011_audio_and_subtitles_v01.zip | 708418001 | 227493421 |
| EP011_thumbnails_and_metadata_v01.zip | 708420234 | 470386 |
| EP011_WeighingOfTheHeart_en_v01_2160p30.mp4 | 708420279 | 1335932360 |

[SHA-256一覧](SHA256SUMS_shared.txt)／[制作結果](../wom11_制作結果_v01_20261104.md)。

英語4Kは1080p完成版の通常拡大。固有名詞の試聴抜粋は音声・字幕ZIP内。サムネはA/Bから本人が選択する。日本語は同尺の別音声として使用可能。
