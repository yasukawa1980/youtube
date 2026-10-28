# Quiet Origins：BGM試聴 v01（2026-10-29）

[結果と実測](../wom_BGM制作結果_20261029.md)。共通A・共通B・行事アメリカを各2候補、旧BGM比較を1本。すべて同じ英語ナレーション64.533秒。

**本人試聴・選曲待ち。** スマホのスピーカーとイヤホンで、音楽が聞こえるか、語りを邪魔しないか、番組に合うかを比較。共通テーマを1〜2曲、アメリカを1曲選ぶ。数値だけで最終採用していない。

- [Draft Release（要ログイン・push権限）](https://github.com/yasukawa1980/youtube/releases/tag/untagged-1e88140ed022435317bf)
- Release ID：`426920724`
- tag：`quiet-origins-bgm-v01-20261029`
- `QO_BGM_listening_set.zip`：試聴HTML＋MP3 7本。解凍し「試聴.html」を開く。
- `QO_BGM_demo_WAVs.zip`：WAV 7本。
- `QO_BGM_QA_records.zip`：AST・音響記録・ハッシュ・波形／スペクトル・Suno証跡。
- 個別MP3：`QO_THEME_A01/A02`、`QO_THEME_B01/B02`、`QO_AMERICA01/02`、`QO_BASELINE_OLD` に `_EP006_demo.mp3` を付けた7本。

Mac：`/Users/ryo/Desktop/新チャンネル/_共通/BGM/20261029_Suno/試聴版_v01/`。原音6本は親フォルダ。Gitには原音・試聴音声を含めない。

## Claudeの取得

Draftはtagによる取得で見つからない場合がある。**Release ID→asset ID指定のRESTで取得**する。`gh release download` は使わない。

```sh
gh api repos/yasukawa1980/youtube/releases/426920724 --jq '.assets[] | [.id,.name,.size,.digest] | @tsv'
# 上の実際のasset IDを使い、必要なファイル名で保存する。
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILENAME
```

[全添付のID・SHA-256・再取得照合記録](../research/wom_BGM_sharing_20261029.json)。添付はDraftのまま維持する。APIや認証トークンを文書に貼らない。

## 添付照合完了

10件すべてRelease ID指定の一覧から取得したasset IDでREST再取得し、バイト数・SHA-256が一致。匿名取得は全件404。

| ファイル | asset ID | bytes |
|---|---:|---:|
| QO_AMERICA01_EP006_demo.mp3 | 685628914 | 1,550,061 |
| QO_AMERICA02_EP006_demo.mp3 | 685629022 | 1,550,061 |
| QO_BASELINE_OLD_EP006_demo.mp3 | 685629104 | 1,550,061 |
| QO_BGM_listening_set.zip | 685629226 | 10,617,718 |
| QO_BGM_QA_records.zip | 685634214 | 670,256 |
| QO_BGM_demo_WAVs.zip | 685634362 | 123,188,975 |
| QO_THEME_A01_EP006_demo.mp3 | 685635062 | 1,550,061 |
| QO_THEME_A02_EP006_demo.mp3 | 685635155 | 1,550,061 |
| QO_THEME_B01_EP006_demo.mp3 | 685635242 | 1,550,061 |
| QO_THEME_B02_EP006_demo.mp3 | 685635348 | 1,550,061 |
