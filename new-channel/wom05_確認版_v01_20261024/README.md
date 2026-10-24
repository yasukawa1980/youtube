# Quiet Origins 第5話「天狗」確認版v01

承認済み台本v02。368.833333秒・11,065フレーム・1080p30。

Mac：`/Users/ryo/Desktop/新チャンネル/EP005_Tengu/確認版_v01_20261024/deliverables/preview.html`。別環境では[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-670e99225581f9efcc28)の添付を同じフォルダへ取得してpreview.htmlを開く。Release ID **422520343**。全78添付をREST再取得しSHA-256・bytes一致。

本人試聴項目：英日の固有名詞（[時刻](records/pronunciation_locations.json)）、P08柿の木の仏の映像・語りの調子、P12守り神の一文。人による全編試聴は未実施。YouTube投稿・予約・Release公開なし。

[実測検査](records/qc_v01.json) / [素材使用](deliverables/EP005_asset_usage_v01.csv) / [動き](deliverables/EP005_motion_v01.csv) / [読み補正](records/reading_replacements.json) / [出典](deliverables/EP005_source_credits.md)。

```sh
gh api repos/yasukawa1980/youtube/releases/422520343
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

再現：wom05_produce.py prepare/en/ja/timeline/audio、wom05_visuals.py、wom05_render.py pictures/package/reviews/precision/verify、wom05_validate.py layout/frames、wom05_motion.py、wom05_final_checks.py。目視記録後、wom05_delivery.py docs/share/export。
