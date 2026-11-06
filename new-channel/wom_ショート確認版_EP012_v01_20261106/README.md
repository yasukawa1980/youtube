# 第12話 ショートN1〜N3 確認版v01

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-5ce540156022c207fe9c)。Release ID **436626831**。4添付をRESTで全量再取得し、バイト数とSHA-256一致、匿名404を確認。

[制作結果と確認点](../wom_ショート制作結果_EP012_20261106.md)。動画の試聴後、N1の人物サイズ・N2の範囲・N3の引用カードを確認してください。

|ファイル|asset ID|バイト|SHA-256|
|---|---:|---:|---|
|QO_short_EP012_N1_v01.mp4|717502933|7292300|`05967239144d07c67f807b383616be728b1fee90be2ffc162675d9b182110824`|
|QO_short_EP012_N2_v01.mp4|717503067|21161913|`f430486279bd8a599caf18b0b27068a78be771fd7ffdbf0c4d685481a3ee31db`|
|QO_short_EP012_N3_v01.mp4|717503188|2646197|`3c28a61d7d320238b0033a4b6c4a9a75e472908f3b17789f2f9ab9ea49f15af6`|
|EP012_shorts_review_v01.zip|717503286|12666181|`a7855c9aaf08c3d44960b71de9647ff85edd6b95d0d0d5728e5f691f6e201609`|

`gh api repos/yasukawa1980/youtube/releases/436626831` で一覧を取得し、`gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT` で保存。
