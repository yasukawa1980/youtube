# Quiet Origins：アヌビス第1話 v06（画面文字の整理）

2026-10-21。本人の実行依頼により、[Claudeの本人承認済み案](../wom01_画面文字削減案_20261021.md)を反映。

## 完成動画

Mac保存先：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/Quiet_Origins_v06_20261021`。

- 字幕入り日本語確認用：`subtitled_review/deliverables/EP001_Anubis_ja_v06_subtitled_review_1080p30.mp4`
- 字幕入り英語確認用：`subtitled_review/deliverables/EP001_Anubis_en_v06_subtitled_review_1080p30.mp4`
- 通常版（字幕焼き込みなし）：`deliverables/EP001_Anubis_ja_v06_1080p30.mp4` / `EP001_Anubis_en_v06_1080p30.mp4`
- 英日SRT・音声M4A・サムネ・声のクレジット：`deliverables/`。

通常版の英日MP4は同一映像と言語別音声。字幕入り確認版はFontSize14の表示を焼き込んだ別コピー。

## 変更と維持

- 55ショットの英語見出し・補足文を削除。ブランド名・話数、出典は維持。
- 資料・再現画の札は `MUSEUM OBJECT｜博物館資料`、`AI RECONSTRUCTION｜AIによる再現`、`FACSIMILE｜模写`。
- 図解13ショット：天秤のラベルを削除、資料例・時代順の写真・矢印・＋・神3柱の画像と英日名などへ置き換え。N20では2秒かけてパピルス画像を切り替える。素材・切り出しは[画像台帳](records/visual_manifest.json)に記録。
- 元の写真・模写・再現画41ショットはy220以降の画素がv05と一致。既存の出典の位置と書式を維持。新規の画像生成なし。
- クレジットはv05の文言を維持。拡大字幕3行にも余白を確保するため、4行の箱を上へ詰めた。
- 全画面の文字の下端は最大698px。図解・クレジットと重なる全字幕を2サイズで実描画し、184条件で重なりなし。保守的な最小余白は128px。
- 英日音声ストリーム・SRT・サムネはv05と同一。尺682.700秒、20,481フレーム、55ショットの順序・開始・終了時刻を維持。英日映像ストリームも同一。
- 通常版と字幕入り確認版の計4本で全編デコード・PTSを検査。確認版では英150・日136字幕と空白区間を検査。
- v05は保全。YouTube動画投稿・追加支出なし。指定SSDへの同期は未実施。全編の聴感は未確認（音声は変更していない）。

## Claudeからの取得

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-d937bb40827824f1b937)／Release ID **419181754**。全11添付をRelease IDからRESTで再取得してSHA-256一致を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/419181754 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v06_1080p30.mp4 | 661427935 | 189,056,399 |
| EP001_Anubis_en_v06_1080p30.srt | 661428385 | 13,252 |
| EP001_Anubis_ja_v06_1080p30.mp4 | 661428433 | 188,526,367 |
| EP001_Anubis_ja_v06_1080p30.srt | 661428956 | 15,346 |
| EP001_audio_en.m4a | 661429001 | 16,143,257 |
| EP001_audio_ja.m4a | 661429125 | 15,613,221 |
| EP001_thumbnail_en.jpg | 661429258 | 407,649 |
| VOICE_CREDITS.txt | 661429333 | 129 |
| EP001_Anubis_en_v06_subtitled_review_1080p30.mp4 | 661429396 | 180,570,685 |
| EP001_Anubis_ja_v06_subtitled_review_1080p30.mp4 | 661430756 | 179,866,119 |
| SHA256SUMS_shared.txt | 661431327 | 965 |

[検品](records/qc_v06.json)／[全字幕の重なり検査](records/subtitle_layout_all.json)／[全55ショットの目視記録](records/visual_review.json)／[字幕入り版検品](records/review_qc.json)／[共有照合](records/sharing_verification_v06.json)。

全55ショットの中央フレームは `frames/midpoints_01.jpg`〜`midpoints_05.jpg`。全字幕表示例は `frames/font14_*.jpg` / `font26_*.jpg`。語りの自然さ・はかり4か所・オシリスの抑揚など以前からの本人試聴項目は継続。
