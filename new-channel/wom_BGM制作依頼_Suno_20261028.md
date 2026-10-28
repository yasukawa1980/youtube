# Codexへの依頼：Quiet OriginsのBGMをSunoで作る（2026-10-28 Claude）

状態：**本人承認済み（2026-10-28「大丈夫です」＝Sunoで作る）。** 方針と根拠は [wom_BGM見直し案_20261027.md](wom_BGM見直し案_20261027.md)（本人方針：テーマによるが壮大で威厳のある感じ）、[他チャンネルの調査](wom_他チャンネル調査_音楽とショート_20261027.md)。

**Sunoのクレジットの上限：100**（Claudeの提案。本人が変える場合はこの行を直す）。上限に近づいたら止めて報告する。追加の購入・契約の変更はしない。

## 背景（短く）

今のBGMは制作スクリプトで作った低い電子音（147Hz・220Hzの持続音と、14秒ごとの1音）。第6話で測ると、エネルギーの58%が200Hz未満、500Hzより上は0%で、**スマホのスピーカーではほぼ聞こえない**。音量の差（語りより約18dB小さい）は一般的な範囲なので変えず、**曲そのものを、本物の楽器の響きの曲に替える**。

## 作る曲（最初の一式）

**優先1：共通テーマと行事（第7話サンクスギビングに使う）。** 優先2はクレジットが残れば。

| 優先 | 曲 | 使う回 | Sunoへの指示（スタイル欄の素案。英語で入れる） |
|---|---|---|---|
| 1 | 共通テーマA | 全回の土台 | slow cinematic orchestral, majestic and solemn, warm low strings, soft French horns, distant timpani, documentary, no vocals, instrumental, 64 BPM |
| 1 | 共通テーマB | 全回の土台（Aと違う調・雰囲気） | slow orchestral, dignified and reflective, piano and string ensemble, gentle brass swells, no vocals, instrumental, 60 BPM |
| 1 | 行事・アメリカ | 第7話サンクスギビング、サンタなど | warm solemn orchestral, early American hymn-like strings, soft horn, autumn, hopeful but serious, no vocals, instrumental, 66 BPM |
| 2 | エジプト・中東 | アヌビス、スフィンクス、ツタンカーメン | majestic ancient Egypt, low strings, oud, ney flute, soft frame drum, slow, no vocals, instrumental |
| 2 | ギリシャ・ローマ | メドゥーサ、パンドラ、セイレーン | epic ancient Greek, lyre and harp, low strings, brass swells, slow, no vocals, instrumental |
| 2 | 日本 | 天狗など | majestic Japanese, distant taiko, koto, shakuhachi, low strings, slow, no vocals, instrumental |

- 共通の除外（Exclude styles）：vocals, choir with lyrics, rap, EDM, heavy drums, drum kit, electric guitar, synth lead。
- 各曲：2〜4候補を作り、良いものを1〜2曲残す。長さは2分以上（本編ではつないで使う）。
- **行事・アメリカの曲で、先住民の音楽をまねた音（羽根飾りを連想させる太鼓・笛の決まり文句など）は使わない**（第7話はワンパノアグの人々を扱うため。ステレオタイプを避ける）。

## 検品（IROと同じ方法＋追加）

1. **歌が入っていないか**：IROと同じ自動判定（AST）と、波形・スペクトルの目視。人の声らしいものは不採用。
2. **スマホで聞こえるか**：エネルギーのうち **500Hz〜4kHz** の割合を測る（今の電子音は0%）。目安として10%以上。
3. **語りとぶつかりすぎないか**：2〜4kHzが極端に強い曲（明るい金管・シンバルの連打など）は避ける。
4. **静かな区間があるか**：曲の中に、語りの下で使える落ち着いた区間が30秒以上あるか（壮大な盛り上がりは章の始まりなどに使う）。
5. つないでも切れ目が目立たない区間（開始・終了の時刻）を記録する。
6. ラウドネス・ピーク、長さ、SHA-256。

## 試聴用のデモ（本人がスマホで聴く用）

採用候補の曲ごとに、**第6話の英語のナレーション（冒頭の約60秒、オープニングまで）** に合わせた試しのミックスを作る。混ぜ方は見直し案のとおり：

- 語りの最中：音楽は語りより約18dB小さく（今と同じ差）。
- 語りの切れ目・オープニング前後：+6dB。
- 音楽の100Hz以下を削り、2〜4kHzを3〜4dB下げる。
- 全体 −16 LUFS、ピーク −1 dBTP以下。
- 比べるため、**今の電子音のBGMのまま**の同じ60秒も1本作る。

デモは非公開のDraft Releaseに置き、Release ID指定のRESTで照合する。本人はスマホのスピーカーとイヤホンで聴いて選ぶ。

## 権利と記録

- Sunoの利用条件（本人の有料プランでの商用利用）を、IROと同じく記録する。曲ごとにSunoの曲ID・作成日時・スタイルの指示・使ったクレジットを記録。
- 原音はMac `/Users/ryo/Desktop/新チャンネル/_共通/BGM/` に置き、Gitに入れない。
- 結果を `new-channel/wom_BGM制作結果_<日付>.md` に書き、`bgm/production` にpushする（fetch／pullしてから）。

## しないこと

- 公開済み・予約済みの動画の音の差し替え。スフィンクスのショートv03への適用（冒頭の見出しの効果を分けて見るため）。
- 歌入りの曲の採用。クレジット上限を超える生成。追加の購入。
