# スフィンクス ショート冒頭比較 v02

S1・S3は冒頭修正、S2は元の完成MP4と同一。YouTube未投稿。

[変更・検査・再生案内](../wom_ショート冒頭修正結果_EP006_v02_20261027.md)。

ClaudeはGitHubの非公開Draft Release **425093235** からMP4を取得する。旧版は **425054637**。19添付をREST再取得しSHA-256・サイズ一致、Draft未公開・匿名取得404を検証済み。

```sh
gh api repos/yasukawa1980/youtube/releases/425093235 --jq '.assets[] | [.name,.id,.size] | @tsv'
```

対象の返却asset IDを使い、`gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<ID>` で取得。キー・トークンを出力しない。

[チェックサム](deliverables/SHA256SUMS_shared.txt)／[再取得照合](records/sharing_complete.json)。原寸素材・音源・動画はGitに含めていない。
