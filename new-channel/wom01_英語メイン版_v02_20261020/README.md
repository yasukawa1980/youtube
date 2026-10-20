# アヌビス第1話：英語メイン版 v02

2026-10-20、本人がB（Kokoro Heart / af_heart）を採用し、全編制作を承認。英語メイン、日本語は第2言語。**全編の技術検品とGitHub共有まで完了。本人の英語・日本語の通し試聴は未実施。**

2026-10-21：専用フォルダへの移行完了。チャンネル名は未定です。以下の149件・ハッシュ表はMac完成版とDraft Release添付の実測記録。Git上の英語SRTのみClaudeが150件に修正済みで、添付の差し替えは未実施です。最新字幕は [Git上のSRT](../episodes/EP001_Anubis/deliverables/EP001_字幕_en.srt) を参照。

## 見る・聞く

Mac保存先：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/英語メイン版_v02_20261020/deliverables/`

- `EP001_Anubis_en_v02.mp4`：英語本編、1920×1080 / 30fps。
- `EP001_review_en_720p.mp4`：英語確認用、1280×720 / 15fps。
- `EP001_review_ja_720p.mp4`：日本語確認用。同一の映像ストリームを使用。
- `EP001_audio_ja.m4a` / `.wav`：日本語の追加音声用。英語音源も保存。
- `EP001_字幕_en.srt` / `EP001_字幕_ja.srt`：外部字幕。動画に焼き込んでいない。

全ファイルの共通尺：**666.200秒（11:06）**。区間ごとに長い方の音声へ合わせ、短い方の末尾に余白を足した。BGMは同一ファイル・同一ダッキング。章の前に1.8秒以上、末尾はBGMを3秒かけてフェードアウト。

[GitHub Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-0d58f8a4bbc19dc235c6)。公開していない。Claudeは下記REST APIで取得できる（過去のv01で成功済みの方法）。今回もアップロード後に全共有ファイルをRESTで再取得し、SHA-256一致を確認した。

```sh
gh api repos/yasukawa1980/youtube/releases --jq '.[] | select(.tag_name=="wom01-en-ja-v02-20261020") | .assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| ファイル | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v02.mp4 | 659602161 | 99,566,474 |
| EP001_audio_en.m4a | 659602162 | 15,705,977 |
| EP001_audio_ja.m4a | 659602160 | 15,180,601 |
| EP001_review_en_720p.mp4 | 659602165 | 51,438,617 |
| EP001_review_ja_720p.mp4 | 659602158 | 50,913,241 |
| EP001_subtitles_en.srt | 659602386 | 13,217 |
| EP001_subtitles_ja.srt | 659602388 | 15,345 |
| SHA256SUMS_shared.txt | 659605941 | 620 |

Release上の字幕はファイル名の自動変換を避けるため `EP001_subtitles_en.srt` / `_ja.srt` とし、Macの日本語ファイル名と内容は同一。`SHA256SUMS_shared.txt` はReleaseに置いたファイルのみを対象とする。WAVなどMac限定のファイルは `SHA256SUMS_local.txt` に記録。

## 検品

| 言語 | 統合 LUFS | True Peak dBTP | SRT件数 |
|---|---:|---:|---:|
| en | -16.00 | -4.13 | 149 |
| ja | -16.02 | -3.74 | 136 |

- 共通尺、音声・映像の差1フレーム以内、全編デコード、字幕順序・範囲を確認。
- SRTは英語1行最大42字、日本語最大23字、どちらも2行まで。原稿の全文字を保持。文の境界は実測、文中の字幕ページ切替は文字数比。
- BGMはどちらかの語りがある区間で -36.50 dBFS。英語の語りに対して -18.60 dB、日本語に対して -17.96 dB。
- 55ショットすべてにゆっくりした拡大。図解の同一内容は最大2回。表示文字は英語。
- MET 557657は原寸で天秤を確認して切り出し。N14・N19の画面で判別できる範囲に拡大。小像・棺材片も拡大。
- 日本語115文のうち92文を既存キャッシュから再利用、23文を生成。無料VOICEVOXの復元・規約再同意は本人承認済み。
- 英語は試聴Bと同じモデル・声。字幕の時刻を取るため文単位で生成し、試聴版に近い速さへ区間ごとに調整。台本は空白区切り1,464語、発話631.973秒、約139.0語/分（内部の間を含む）。
- Claude・Codexとも、音声の直接聴感やASRによる読みの確認は行っていない。技術検品を「聞いて確認済み」と扱わない。

## 本人に確認してほしい点

まず英語の冒頭90秒と次の固有名詞が多い区間を確認し、その後両言語を通して聴いてください。

| 区間 | 開始 | 内容 |
|---|---|---|
| N13 | 04:34 | A papyrus for one person |
| N16 | 05:47 | It looks like a wall painting |
| N19 | 07:07 | Before Osiris |
| N21 | 07:56 | Not only about death |

確認点は声の自然さ・固有名詞の発音・BGM・間。共通尺の指定に従い、短い言語の区間末尾は無音で埋めている。日本語の最長余白はN16の約9.46秒（BGMは継続）。この間の長さも確認対象。

## 画面と記録

[場面一覧1](frames/contact_1.jpg) / [2](frames/contact_2.jpg) / [3](frames/contact_3.jpg) / [4](frames/contact_4.jpg)

`frames/encoded_Nxx.jpg` は完成MP4から抽出、`Nxx_...jpg` はショット組版。元画像と実際の切り出しは [visual_manifest.json](../episodes/EP001_Anubis/records/visual_manifest.json)。

[共通タイムライン](../episodes/EP001_Anubis/records/master_timeline.json) /
[技術検品](../episodes/EP001_Anubis/records/qc.json) /
[字幕・同期検証](../episodes/EP001_Anubis/records/subtitle_alignment_validation.json) /
[追加メディア検証](../episodes/EP001_Anubis/records/media_validation.json)

## 再開方法

`new-channel/wom01_narrate.py` は `WOM_LANG=en|ja`、ほかの入口は `WOM_MULTILINGUAL=1` で新しい処理へ入る。既存v01用処理は保存してある。必ず `WOM_EPISODE_ROOT` を新しい制作フォルダ、`WOM_SOURCE_ROOT` を旧素材のあるフォルダへ指定する。

```sh
export WOM_EPISODE_ROOT='/Users/ryo/Desktop/新チャンネル/EP001_Anubis/英語メイン版_v02_20261020'
export WOM_SOURCE_ROOT='/Users/ryo/Desktop/新チャンネル/EP001_Anubis/旧制作素材'
export WOM_KOKORO_MODELS='/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1'
export WOM_VOICEVOX_RUNTIME='/Users/ryo/Desktop/BGM/_共通/音声モデル/VOICEVOX_core_0.17.0_model_0.16.4'
# records/requirements.txt と同じ依存関係のPython環境で実行する。
WOM_LANG=en python new-channel/wom01_narrate.py
WOM_LANG=ja python new-channel/wom01_narrate.py
WOM_MULTILINGUAL=1 python new-channel/wom01_make_visuals.py
WOM_MULTILINGUAL=1 python new-channel/wom01_render_episode.py
WOM_MULTILINGUAL=1 python new-channel/wom01_package_documents.py
```

音声のキャッシュは全文・設定・モデルハッシュを照合。映像キャッシュは組版画像のハッシュとフレーム数を照合する。本文・設定を変更した場合はタイムライン以降を再実行。2026-10-21に素材・出力を上記の専用フォルダへ移動し、参照先を更新した。音声モデルは既存の共通配置を利用する。指定SSD ESD-EPB は未接続で未同期。

有料契約・購入・有料API呼び出し・新チャンネル開設・YouTubeへの投稿は実施していない。追加支出0円。公開判断とStudioの多言語音声・AI開示確認は別途。
