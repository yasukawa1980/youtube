# 第11話「心臓の計量」確認版v02 取得案内

Claudeの[確認メモ](../wom11_Claude確認_v01_20261104.md)にある映像4か所を修正。**音声・字幕・台本はv01とハッシュ一致。サムネは本人承認のA。** v01は保全。本人試聴・Claudeの最終確認待ち。YouTube未投稿、Release未公開。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-6d59adfae4cbe4dc79a2)、Release ID **433612391**。

```sh
gh api repos/yasukawa1980/youtube/releases/433612391
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

英日1080p通常版、英日字幕入り確認版、英語4K通常拡大版と資料ZIP3本。全8添付をRESTで再取得し、サイズ・SHA-256一致、匿名404を確認。

| ファイル | asset ID | bytes |
|---|---:|---:|
| EP011_QA_records_v02.zip | 708603462 | 11162776 |
| EP011_WeighingOfTheHeart_en_v02_1080p30.mp4 | 708603669 | 184936505 |
| EP011_WeighingOfTheHeart_en_v02_subtitled_review_1080p30.mp4 | 708605628 | 82250234 |
| EP011_WeighingOfTheHeart_ja_v02_1080p30.mp4 | 708606437 | 184832647 |
| EP011_WeighingOfTheHeart_ja_v02_subtitled_review_1080p30.mp4 | 708608778 | 82776837 |
| EP011_audio_and_subtitles_v02.zip | 708610007 | 227493421 |
| EP011_thumbnails_and_metadata_v02.zip | 708612526 | 154672 |
| EP011_WeighingOfTheHeart_en_v02_2160p30.mp4 | 708612619 | 1332635490 |

4K版はRESTのRange指定で全159範囲を取得し、欠落・重複のない全体のサイズとSHA-256を照合済み。

[SHA-256一覧](SHA256SUMS_shared.txt)／[修正結果](../wom11_制作結果_v02_20261104.md)／[採用サムネA](EP011_thumbnail_A.jpg)。音声・字幕ZIP内の発音抜粋はv01と同一なので、試聴はどちらの版でもよい。
