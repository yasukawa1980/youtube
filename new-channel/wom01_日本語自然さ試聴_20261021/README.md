# 日本語の自然さ：無料の比較テスト（2026-10-21）

本人の「無料のままでテストしたい」という依頼で制作。英語の採用済みBとは別の、今回限りのA/B/Cです。音声は全候補 **VOICEVOX:冥鳴ひまり（style 14）**。N01〜N04の16文を欠落なく使用し、各87.5秒にそろえました。

## 聴く順番

まずBとAを比べ、次にCを聴いてください。Bは控えめな調整案で、採用済み・自然さ確認済みという意味ではありません。各候補にBGMありと声だけがあります。文のつながり、語尾、間、抑揚が自然か、演出が強すぎないかを確認してください。

| 候補 | 内容 | BGMあり LUFS | 声だけ LUFS | 最終文終了 |
|---|---|---:|---:|---:|
| A | 現行音声（比較用に音量を統一） | -15.99 | -16.04 | 86.388秒 |
| B | 控えめに抑揚・間を調整 | -16.03 | -16.02 | 79.421秒 |
| C | Bより強弱と間を広げた調整 | -16.03 | -16.03 | 82.415秒 |

Aは既存v03の冒頭の元音声を再利用。比較のためミックスを統一しているので、元MP4の音声トラックそのものではありません。B/Cは文の役割ごとに話速・抑揚を変え、読点・文間・段落間の長さを調整。Bの話速は0.97〜1.02、Cは0.955〜1.005で、英語区間に収めるための加速はしません。文字・意味・語順と声の種類は維持し、アクセント型の個別修正はしていません。

共通BGMはv03と同じ曲で、フェード前の目標RMS −33.5 dBFS。比較では語りの間の増量を外し、同じBGMトラックを全候補に使用。約−16 LUFSへ音量を統一しました。候補による話し終わりの違いは末尾の余白で吸収しています。

## 保存と取得

Mac：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/日本語自然さ試聴_20261021`。`試聴ページ.html` をブラウザーで開くと6音源を選べます。音源・試聴専用SRTは `deliverables/`。

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-fe430ccd363d692242f4)。Release ID **419042790**。添付全11件をRESTで再取得してSHA-256一致を確認しました。ZIPは試聴ページ・音源・SRT・案内の一式です。

```sh
gh api repos/yasukawa1980/youtube/releases/419042790 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_ja_A.srt | 660992618 | 2,052 |
| EP001_ja_A_BGM.m4a | 660992669 | 1,325,643 |
| EP001_ja_A_voice_only.m4a | 660992745 | 1,008,229 |
| EP001_ja_B.srt | 660992795 | 2,052 |
| EP001_ja_B_BGM.m4a | 660992839 | 1,321,160 |
| EP001_ja_B_voice_only.m4a | 660992897 | 1,004,024 |
| EP001_ja_C.srt | 660992937 | 2,052 |
| EP001_ja_C_BGM.m4a | 660992986 | 1,330,805 |
| EP001_ja_C_voice_only.m4a | 660993061 | 1,013,245 |
| SHA256SUMS.txt | 660993111 | 774 |
| EP001_ja_natural_audition.zip | 660993144 | 6,748,608 |

## 検品と範囲

[音量・制作記録](records/qc.json)、[発話設定](records/prosody_settings.json)、[共有確認](records/sharing_verification.json)。16文の原文・順序保持、音声時刻の重なりなし、全音源のデコードを確認。元v03ナレーションのハッシュ不変。自然さ・アクセント・読みの聴感確認は未実施で、本人の試聴待ちです。

全編、英語B、既存v03メディアは変更していません。今回のSRTは試聴用です。Claudeのv03日本語字幕修正・画面下の出典配置修正は今回の試聴テストには含めず、元の申し送りに残っています。チャンネル名は未定、投稿・開設・追加契約・購入なし。指定SSD ESD-EPBは未同期です。

## 再現・クレジット

`../wom01_日本語自然さ試聴.py` を使用。`WOM_AUDITION_ROOT` に新規出力先、`WOM_PREVIOUS_ROOT` にv03、`WOM_VOICEVOX_RUNTIME` に既存ランタイムを指定します。Core 0.17.0 / VVM 0.16.4、既存1.vvmのみ。全クエリはMacの `records/queries.json` に保管。

**VOICEVOX:冥鳴ひまり**：[音声利用規約](https://www.meimeihimari.com/terms-of-use)／[VOICEVOX利用規約](https://voicevox.hiroshiba.jp/term/)。
