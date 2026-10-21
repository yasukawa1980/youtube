# アヌビス第1話 v04：C採用・「はかり」修正・字幕同期

2026-10-21、本人の「Cでお願いします。字幕も合わせて。秤を『はかり』に修正」という依頼を反映しました。日本語は **VOICEVOX:冥鳴ひまり・試聴C**、英語は採用済み **B / af_heart** です。

## 完成内容

- 日本語115文にCの抑揚・間・話速を適用。冒頭の承認済みCは、読みを直す2文以外の14文をそのまま再利用。残り101文を生成しました。
- 「秤」の単独語4か所（N01-03、N02-03、N17-02、N19-01）を読み上げ用入力で「はかり」に修正。エンジンのカナが「ハカリ」であることを確認。**表示する字幕は「秤」のまま**。天秤＝てんびん、秤量＝ひょうりょうは保持。[読み修正記録](records/reading_corrections.json)。
- 英日共通尺 **682.700秒（11分22.7秒）**、1080p30、20,481フレーム。v03から16.5秒延長し、日本語を旧英語区間に合わせて加速しない構成にしました。
- 英語の元音声28区間はハッシュ不変で、[v03の全編音声とのサンプル一致](records/english_v03_preservation.json)も確認。共通尺の変化に合わせて音声配置・英語字幕の時刻も更新。
- 外部字幕は英語150件・日本語136件。Claudeによる日本語の短すぎるページの修正を引き継ぎ、今回の新音声に同期。字幕焼き込みなし。
- 出典・注記を上部へ移し、下部に字幕用余白を確保。55ショットの素材・順序を維持。小数座標の滑らかな拡大、H.264 CRF18で書き出し。
- BGMはv03と同じ語り中の目標−33.5 dBFS、語りの間は4dB増量。英語 -16.01 LUFS、日本語 -16.00 LUFS。

## 再生・取得

Mac：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/C採用_はかり修正_v04_20261021/deliverables/`

- 日本語全編：`EP001_Anubis_ja_v04_1080p30.mp4`
- 英語全編：`EP001_Anubis_en_v04_1080p30.mp4`
- 全編と同名の `.srt` を同じフォルダに保存。外部字幕対応プレーヤーで同じ言語の字幕を読み込んでください。
- `EP001_ja_hakari_check.m4a`：修正した4文だけの確認用。`EP001_ja_v04_first90s.mp4`：冒頭90秒。
- `EP001_audio_en.m4a` / `EP001_audio_ja.m4a`：全編音源。WAVはMacのみ。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-49d00ab6af9b15c390c5)、Release ID **419063998**。全10添付をRESTで再取得しSHA-256一致を確認。既存v03と試聴版は保持しました。

```sh
gh api repos/yasukawa1980/youtube/releases/419063998 --jq '.assets[] | "\(.id) \(.name) \(.digest)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v04_1080p30.mp4 | 661072986 | 166,169,510 |
| EP001_Anubis_ja_v04_1080p30.mp4 | 661073340 | 165,639,478 |
| EP001_audio_en.m4a | 661073665 | 16,143,257 |
| EP001_audio_ja.m4a | 661073739 | 15,613,221 |
| EP001_Anubis_en_v04_1080p30.srt | 661073836 | 13,252 |
| EP001_Anubis_ja_v04_1080p30.srt | 661073887 | 15,346 |
| EP001_ja_v04_first90s.mp4 | 661073934 | 16,306,961 |
| EP001_ja_hakari_check.m4a | 661074048 | 333,954 |
| VOICE_CREDITS.txt | 661074103 | 129 |
| SHA256SUMS_shared.txt | 661074151 | 830 |

## 検品と残る確認

[全編検品](records/qc_v04.json)／[字幕・波形・配置](records/subtitle_and_layout_validation.json)／[音量](records/audio_qc.json)／[共有照合](records/sharing_verification_v04.json)。

- 英日とも全編デコード成功、30fps・同尺・映像ストリームのハッシュ一致。[全20,481フレームの時刻と音声結合の確認](records/final_stream_validation.json)も実施。
- 日本語115文すべての元音声サンプルと、全編の対応区間が一致。英語・日本語の全28区間でも波形一致を確認。
- 字幕は本文の欠落・重なり・尺超過なし、文境界一致。最大2行、英語42字／行・日本語23字／行。最短表示は英語1.502秒、日本語1.553秒。
- [字幕配置の確認図](frames/subtitle_layout_simulation.jpg)は、代表5種類×英日、文字56px・行高68px・下余白34pxで重ねた**配置シミュレーション**です。実プレーヤーのスクリーンショットではありません。ローカルFFmpegにはlibassがなく、Pillowで作成。外部字幕の位置・大きさは再生環境で変わります。画面上部の見出し・出典と重ならないことを確認しました。
- 実際のMP4から抽出：[冒頭](frames/frame_010.jpg)／[75秒](frames/frame_075.jpg)／[440秒](frames/frame_440.jpg)／[終盤](frames/frame_672.jpg)。

**本人の通し視聴・聴感確認はまだです。** まず「はかり」確認音源を聴き、日本語全編でCの自然さと字幕のタイミングを確認してください。エンジンの読みと波形・時刻は検証していますが、人による全編の発音確認を代替しません。

Claudeのv03申し送りA（日本語字幕）・B（出典配置と画質）・C（日本語の加速回避）は、このv04の新音声・新時刻へ適用。旧v03の添付差し替えは行わず、最新確認対象をv04へ更新しています。チャンネル名は未定で画面の仮称は継続。

## 再現・条件

`../wom01_finalize_c.py` を `prepare → narration → timeline → visuals → audio → pictures → package` の順で実行。`WOM_EPISODE_ROOT` は新規出力先、`WOM_PREVIOUS_ROOT` はv03、`WOM_AUDITION_ROOT` はC試聴先、`WOM_SOURCE_ROOT` は旧素材、`WOM_VOICEVOX_RUNTIME` は既存ランタイムを指定。字幕・波形・配置検品は `../wom01_validate_c.py`。全クエリはMacの `records/queries.json`、Gitには要約を保存。

**VOICEVOX:冥鳴ひまり**：[音声利用規約](https://www.meimeihimari.com/terms-of-use)／[VOICEVOX利用規約](https://voicevox.hiroshiba.jp/term/)。Core0.17.0 / VVM0.16.4、既存1.vvmを使用。無料・ローカルのみ、追加契約・購入・投稿・チャンネル開設なし。SSD ESD-EPBは未同期。
