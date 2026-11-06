# 第12話ショート N1・N3 確認版v02

**絵の拡大修正・検品・非公開共有済み。本人試聴・Claude確認待ち。YouTube未投稿・未予約。N2は合格済みv01を継続。**

[Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-37cfa10c6ca782462f44) — Release ID **436648343**。MP4 2本と確認ZIPの全3添付を、Release ID指定RESTで列挙・再取得し、SHA-256とサイズ一致、匿名404を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/436648343
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
| QO_short_EP012_N1_v02.mp4 | 717558808 | 6783461 |
| QO_short_EP012_N3_v02.mp4 | 717558912 | 2583612 |
| EP012_shorts_review_v02.zip | 717559040 | 4951212 |

[SHA-256一覧](SHA256SUMS_shared.txt)／[修正結果](../wom_ショート制作結果_EP012_v02_20261107.md)／[N2 v01取得先](../wom_ショート確認版_EP012_v01_20261106/README.md)。確認ZIPには指定時刻の画像・全字幕ページ・座標・倍率・全フレーム比較・音声一致記録を収録。
