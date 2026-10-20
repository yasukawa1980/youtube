# アヌビス第1話 v03：映像・日本語女性声・BGM調整

2026-10-21、本人の「映像のかくつき修正、日本語女性声、BGM増量」の依頼で制作。英語字幕の差し替えに先立つ映像・音声確認版です。チャンネル名は未定、既存画面の仮称は残しています。

## 今回の変更

- 英語・日本語とも1080p・30fps。日本語の旧確認版は720p・15fpsでした。
- 拡大時の切り出し位置を整数画素で動かすzoompanから、小数座標を補間するperspectiveへ変更。画像部分だけを2.5%拡大し、見出しと出典の文字を固定しました。
- 日本語は女性声 **VOICEVOX:冥鳴ひまり（ノーマル、style 14）** で全115文を生成。VOICEVOX Core 0.17.0 / VVM 0.16.4。原稿の省略なし。基本速度1.0、区間を超える場合だけ話速を調整しています。
- BGMを旧-36.5 dBFSから目標-33.5 dBFSへ3dB増量。語りの間の4dB増量、末尾3秒のフェードを維持。
- 共通尺666.2秒（11分6.2秒）、英語Bの元ナレーションと全28区間の開始・終了時刻はv02と同じです。

## 再生するファイル

Mac：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/映像音声調整_v03_20261021/deliverables/`

- `EP001_Anubis_en_v03_1080p30.mp4`：英語全編。
- `EP001_Anubis_ja_v03_1080p30.mp4`：日本語女性声の全編。
- `EP001_en_v03_first90s.mp4` / `EP001_ja_v03_first90s.mp4`：冒頭約90秒。
- `EP001_audio_en.m4a` / `EP001_audio_ja.m4a`：言語別音源。WAVもMacに保管。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-28e2d6a3ff08fb02120d)。既存v02は保管したままです。アップロード後、添付全7ファイルをRESTで再取得し、SHA-256一致を確認しました。

```sh
gh api repos/yasukawa1980/youtube/releases/418626871 --jq '.assets[] | "\(.id) \(.name) \(.digest)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| ファイル | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v03_1080p30.mp4 | 659866706 | 154,926,772 |
| EP001_Anubis_ja_v03_1080p30.mp4 | 659867386 | 154,446,829 |
| EP001_en_v03_first90s.mp4 | 659867920 | 16,034,495 |
| EP001_ja_v03_first90s.mp4 | 659868058 | 15,982,511 |
| EP001_audio_en.m4a | 659868174 | 15,874,784 |
| EP001_audio_ja.m4a | 659868320 | 15,394,817 |
| SHA256SUMS_shared.txt | 659868433 | 550 |

## 技術検品

| 全編ファイル | 統合LUFS | True Peak dBTP |
|---|---:|---:|
| EP001_Anubis_en_v03_1080p30.mp4 | -16.01 | -3.79 |
| EP001_Anubis_ja_v03_1080p30.mp4 | -15.98 | -4.55 |

- BGMの語り中RMS：-33.50 dBFS。全体音量は約-16 LUFSに維持。
- 全55ショット・計19,986フレームの枚数と30fpsを確認。英日映像ストリームのハッシュ一致、全編デコード、共通尺を確認。
- 冒頭10秒のフレーム間画像差の10〜90パーセンタイルは旧0.087〜0.584、新0.088〜0.107。動きのばらつきが小さくなったことを示す補助的な数値で、全編の人による見え方の評価を代替しません。
- 場面抽出：[冒頭](frames/frame_008.jpg)／[90秒](frames/frame_090.jpg)／[4分](frames/frame_240.jpg)／[4分50秒](frames/frame_290.jpg)／[天秤](frames/frame_430.jpg)／[終盤](frames/frame_650.jpg)。
- [検品記録](records/qc_v03.json)／[追加確認](records/extra_validation_v03.json)／[音量](records/audio_qc.json)。

**本人の通し視聴・聴感確認は未実施です。** まず日本語の冒頭で女性声・話速・BGMを確認し、同じ場面を旧版と比較して動きを確認してください。日本語には英語との共通尺のためBGMだけの間も残っています。

## 字幕と次の作業

字幕焼き込みなし。今回のv03には外部SRTを添付していません。本人の指示どおり、英語字幕150件への差し替え作業は保留しています。日本語は女性声で文の発話時刻が変わったため、採用後にv03の `narration_timeline_ja.json` から字幕を再生成してください。旧男性版の日本語字幕を流用しないでください。

## 音声の条件・クレジット

日本語：**VOICEVOX:冥鳴ひまり**。[公式案内](https://voicevox.hiroshiba.jp/product/meimei_himari/)／[音声利用規約](https://www.meimeihimari.com/terms-of-use)／[VOICEVOX利用規約](https://voicevox.hiroshiba.jp/term/)。規約を確認し、ローカルで生成。クレジットは概要欄・共有案内から消さないでください。動画のメタデータと同梱の音声クレジットにも記載しています。

英語：Kokoro / af_heart。音声モデルの取得元とハッシュは [制作設定](records/revision_request.json)。有料契約・購入・有料音声API・チャンネル開設・YouTube投稿は実施していません。

## 再現方法

`../wom01_refine_av.py` を使用。新しい出力先を `WOM_EPISODE_ROOT`、v02制作先を `WOM_PREVIOUS_ROOT`、旧素材先を `WOM_SOURCE_ROOT` に設定します。

1. `prepare` で入力をコピー。
2. `WOM_LANG=ja WOM_JA_STYLE_ID=14 WOM_JA_MODEL=1.vvm WOM_JA_SPEED=1.0 WOM_JA_VOICE=冥鳴ひまり` と既存の `WOM_VOICEVOX_RUNTIME` を設定し、`wom01_multilingual_narration.py` を実行。
3. 同じ環境で `wom01_refine_av.py fit`、`align` を順に実行。
4. `WOM_BGM_DBFS=-33.5` を設定して `audio`。`pictures` で映像を生成し、`package` で結合・技術検品。

元のv02を出力先に指定しないでください。`records/japanese_pacing.json` は実測して調整した話速です。指定SSD ESD-EPBは未接続のため、この版もMac保存・GitHub共有まででSSD未同期です。
