# 第10話クランプス 確認版v01（2026-11-03）

[制作結果](../wom10_制作結果_v01_20261103.md)。本人承認済み台本v02から制作。Claude確認・本人試聴待ち。公開・予約はしていません。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-f69fd9f936d90c014bae)／Release ID **431617156**／タグ `quiet-origins-ep010-v01-20261103`。

MP4は英日通常版・英日字幕入り確認版の4本。音声・SRT・固有名詞試聴、サムネ・投稿情報、検査記録は3つのZIPに分けました。全7ファイルをRelease ID指定のRESTから再取得し、ローカル原本とのサイズ・SHA256一致と匿名404を確認済み。

Draftの取得には認証が必要です。タグURLの404だけで不存在と判断せず、まず次のAPIを使用してください。

```sh
gh api repos/yasukawa1980/youtube/releases/431617156
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
| EP010_Krampus_en_v01_1080p30.mp4 | 702172548 | 171061099 |
| EP010_Krampus_en_v01_subtitled_review_1080p30.mp4 | 702173495 | 93503854 |
| EP010_Krampus_ja_v01_1080p30.mp4 | 702174006 | 170953853 |
| EP010_Krampus_ja_v01_subtitled_review_1080p30.mp4 | 702175102 | 93693306 |
| EP010_QA_records.zip | 702175729 | 9033241 |
| EP010_audio_and_subtitles.zip | 702175843 | 219236062 |
| EP010_thumbnails_and_metadata.zip | 702176754 | 576238 |

SHA256は [SHA256SUMS_shared.txt](SHA256SUMS_shared.txt)、REST照合記録は [sharing.json](records/sharing.json)。動画・音源の実体はGitに入れていません。

## 本人の確認

1. 英語・日本語の固有名詞試聴（`EP010_pronunciation_en.m4a` / `ja.m4a`）。初回の無置換音声を採用し、全126文のnative音声が初回保存と一致しています。時刻表は同名TXT。
2. 通し再生で声・字幕・映像の切替を確認。音の聴感と語の正しい発音は、人による確認が未実施です。
3. K03aの怖さが強すぎないか。子ども・長い舌を外した上部だけを使用しています。
4. サムネ [A](../サムネ確認用/wom10/EP010_thumbnail_A.jpg) / [B](../サムネ確認用/wom10/EP010_thumbnail_B.jpg) の選択。[168px比較](../サムネ確認用/wom10/EP010_thumbnails_168_comparison.jpg)。

公開予定は本人指定 **2026-11-08 09:00 JST**。予約時に同日のショートA1R（18:00予定）を含めた公開本数を照合してください。第10話のショートは本編合格後の別依頼です。
