# 第12話ショート N1 確認版v03

**出典と絵の重なり修正・検品・非公開共有済み。本人試聴・Claude確認待ち。YouTube未投稿・未予約。N2 v01・N3 v02を継続。**

[Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-dee2acb1ce0b37da8168) — Release ID **436671292**。MP4 1本と確認ZIPの2添付をRelease ID指定RESTで列挙・再取得し、SHA-256・サイズ一致、匿名404を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/436671292
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
| QO_short_EP012_N1_v03.mp4 | 717620742 | 6761992 |
| EP012_N1_review_v03.zip | 717620850 | 4063562 |

[SHA-256一覧](SHA256SUMS_shared.txt)／[修正結果](../wom_ショート制作結果_EP012_v03_20261107.md)／[N2 v01](../wom_ショート確認版_EP012_v01_20261106/README.md)／[N3 v02](../wom_ショート確認版_EP012_v02_20261107/README.md)。ZIPには指定時刻の画像・出典部分の拡大画像・座標・倍率・全フレーム比較・音声一致記録を収録。
