# wom01 アヌビス：英語メイン・字幕焼き込みなしへの切り替え手順

決定日：2026-10-20（本人）。作成：Claude。Codexが手順2以降をMac側で実施する。

## 決定事項

- **メイン言語は英語。日本語は必須の第2言語。** そのほかの言語は、2〜3本で作業時間と反応を測ってから検討する（第1候補はスペイン語）。
- **字幕は焼き込まない。** 字幕は英語・日本語のSRTファイルとしてYouTubeに追加する。
- **映像は1本、音声は言語ごとの別トラック。** YouTubeの多言語音声機能を使う想定。使えるかどうか・条件は投稿前にStudioの画面で確認する。使えない場合の代替案は末尾に記載。
- 次の回からは英語の台本を先に書き、日本語はその訳として作る。EP001は日本語v02が先にあるため、英語版をv02と同じ区間・出典・画面割りで作った。

未決定（本人）：英語の声。新チャンネルの開設・名称・投稿。

## 台本ファイル

| 言語 | ファイル | 状態 |
|---|---|---|
| 英語（メイン） | `worlds-of-mystery/EP001_Anubis/records/content_en.json` | Claude作成。28区間・1,464語・8,083字。150語/分で約9.8分。音声未生成 |
| 日本語 | `worlds-of-mystery/EP001_Anubis/records/content.json` | v02（`bgm/wom01_Claudeレビュー修正_v02.md`）。音声は一部未生成 |

両ファイルの区間ID・出典・画面（`visuals`）は同じにしてある。片方の内容を変えたら、もう片方も同じ区間を直すこと。英語版の固有名詞・年代の表記はMetの英語表記に合わせた（Nauny、Nakhtamun、Nedjemankh、Ammut、Amenemhat I、c. 1050 BCE、7.7 cm、bronze or copper alloy）。

## Codexの作業

### 1. 英語の声（本人の選択待ち）

追加の契約・購入はしない（未承認）。ローカルで動く無料の音声合成から候補を出し、冒頭90秒（N01〜N04）の試聴版を2〜3声作って本人に選んでもらう。

- 候補例：Kokoro（Apache-2.0）の英語の声。ドキュメンタリー調なら落ち着いた男声・女声を米英それぞれ1つずつ。
- 採用前に、モデルと声の利用規約で商用利用とクレジット表記の条件を確認し、`records/voice_license.json` に英語分を追記する。
- 規約が確認できない声は使わない。

### 2. 言語ごとのナレーション

- `wom01_narrate.py` を言語別に実行できるようにする（例：`WOM_LANG=en|ja`）。出力を言語別に分ける：`audio/en/`、`audio/ja/`、`records/narration_timeline_en.json`、`records/narration_timeline_ja.json`。
- 日本語の読み替え表（`spoken_text`）は日本語専用。英語には別の表を使う（例：BCE → "B C E"、7.7 cm → "seven point seven centimeters" など、試聴して必要なものだけ）。
- 日本語は、v02で変えた文だけを再生成する（キャッシュを再利用）。

### 3. 共通の時間軸（重要）

多言語音声は**どの言語でも映像と同じ長さ**である必要がある。区間ごとの長さは言語で変わるため、次の方法で揃える。

- 区間の長さ ＝ 英語と日本語のうち長い方の区間ナレーション長 ＋ 現在と同じ区間間の間（ま）。
- 短い方の言語は、区間の末尾に無音を足す（話し始めの位置は全言語で区間の先頭に揃える）。
- 結果を `records/master_timeline.json` に保存する（区間ID・開始・終了・各言語の発話長）。映像・各言語の音声・各言語のSRTはすべてこの時間軸から作る。
- BGMは全言語で共通。各言語の音声トラック ＝ その言語のナレーション（無音で埋めたもの）＋共通BGM。ラウドネスは言語ごとに現在と同じ目標（−16 LUFS／TP −2 dBTP 程度）に合わせる。

### 4. 画面の文字

映像は1本なので、画面の文字は1言語だけになる。**英語にして、量を減らす。**

- 区間の見出し・キャプションは `content_en.json` の `heading`／`caption` を使う。日本語の視聴者には、日本語字幕と日本語の概要欄で補う。
- 史料のラベル（館名・作品番号・Open Access (CC0)）は英語のまま残す。
- 「AI画像イメージ」表示 → `AI reconstruction`。史料画像の表示 → `Museum object`。模写には `Facsimile (copy on paper)` を付ける。N03のナレーションで「右上に表示」と説明しているので、表示の位置は右上のままにする。
- 図解6枚（balance・roles・journey・timeline・evidence・credits）の日本語の文字を英語にする。
- 字幕の帯を置かないので、画面下部の余白は詰めてよい。

### 5. 書き出し

- `wom01_render_episode.py` から、字幕PNGの焼き込み（caption_track の overlay）を外す。映像には字幕を入れない。
- 出力：映像＋英語音声のMP4（メインとしてアップロードする本体）、日本語音声トラック（AACまたはWAV。YouTubeの追加音声として上げる）、`EP001_字幕_en.srt`、`EP001_字幕_ja.srt`。
- SRTは v02 で入れた改行ロジック（`wrap`）を日本語に使う。英語は1行42字前後で単語の区切りで改行し、同時に表示するのは2行まで。時刻は master_timeline から作る。
- 区間映像のキャッシュは、区間の長さが変わるので作り直しになる。画像（assets/composed）のうち、文字のない史料画像・AI画像は使い回す。

### 6. 検品

- 映像と各言語の音声の尺が一致していること（差は1フレーム以内）。
- 全編デコード、言語ごとのラウドネス・トゥルーピーク。
- SRTの時刻が順番どおりで尺の中に収まっていること、改行が単語・語の途中でないこと。
- 画面に日本語の文字が残っていないこと（代表場面の一覧を英語版で作り直し、`サムネ確認用/Worlds of Mystery/wom01_本編場面確認.jpg` を差し替える）。
- MET 557657（N14・N19）の画像に天秤の場面が見えているか、原寸で確認する（v02の依頼から継続）。
- `qc.json` を言語別の項目に更新する。本人の試聴は英語・日本語とも未実施として記録する。

### 7. 共有

- 台本・タイムライン・SRT・検品記録・確認用JPGをコミットしてpushする。MP4・音声はGitに入れない（`.gitignore` どおり）。
- コミットメッセージに実測値（尺、各言語のLUFS/TP、SRTの件数）を書く。

## 投稿情報（英語・下書き）

チャプターの時刻は master_timeline 確定後に入れる。

**Title:** Anubis: Judge of the Dead, or Protector? | What Museum Objects Reveal

**Description（冒頭）:**

> Anubis, the canine-headed god of ancient Egypt, is famous for weighing the heart of the dead. But did he really judge alone? Using public collections and curatorial notes from The Metropolitan Museum of Art, this episode follows what Anubis actually does in the sources: guarding tombs, protecting the body, and overseeing the scale.
>
> We distinguish between photographs of museum objects, a modern facsimile of a wall painting, explanatory diagrams, and AI-generated reconstructions. Religious beliefs and myths are presented as beliefs, not as historical events.
>
> Narration: synthetic voice (credit TBD). Some images are AI-generated reconstructions. Music: original ambient score made for this video.

この後に Sources（S01〜S12・URL）、画像のクレジット（The Metropolitan Museum of Art, Open Access / CC0、作品ID）、注意書き（MET 557830 は Nina de Garis Davies による模写、MET 590939・547871 は同定に不確実性あり）を続ける。日本語のタイトル・概要欄は、YouTubeのタイトル・説明の翻訳機能で日本語版として追加する（既存の `bgm/wom01_アップロード情報.md` を v02 の内容で更新したもの）。

**AIの使用の開示：** Studioの「AIの使用」の質問に答える。概要欄の文だけで済ませない。

## 多言語音声が使えない場合の代替案

1. 英語音声の動画1本＋日本語字幕のSRT（日本語音声なし）。
2. 日本語音声版を、同じ映像の別の動画として作る（チャンネルの分け方は本人が決める）。

どちらにするかは本人に確認してから進める。
