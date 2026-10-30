# Quiet Origins 第8話 確認版v03（2026-10-30）

**文字カードの修正・技術検査・非公開Draft共有を完了。本人とClaudeの文字の読みやすさの確認待ち。**

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-680324c88e74cae4605e)、Release ID **428569306**。英日4動画＋4ZIPの計8資産をRelease ID指定RESTから再取得し、全件サイズ・SHA-256一致、匿名404、Draftを維持。

## 視聴・取得

- `EP008_Tutankhamun_ja_v03_subtitled_review_1080p30.mp4`：日本語・字幕付き確認版。
- `EP008_Tutankhamun_en_v03_subtitled_review_1080p30.mp4`：英語・字幕付き確認版。
- `EP008_Tutankhamun_{en,ja}_v03_1080p30.mp4`：字幕なし。
- `EP008_audio_and_subtitles.zip`：英日音声・SRT・発音抜粋。音声の試聴はv02でしても同じ。
- `EP008_thumbnails_and_metadata.zip`：変更していないサムネA〜D・168px比較・投稿情報と出典、v03コントラスト表。
- `EP008_QA_records.zip`：全検査記録、v02→v03のカード比較、英日全ショット一覧。
- `EP008_AI_scene_review.zip`：v01から引き継いだろうそく原動画。

認証して `gh api repos/yasukawa1980/youtube/releases/428569306` から資産IDを取得し、`gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE` でダウンロードできる。[全資産のID・SHA-256](records/sharing.json)。

## 修正内容と保持条件

- 砂色の地の強調文字を **#5A3A1A** に変更。本文の **#3B2C21** は保持。紺色の出典帯の文字色は保持。
- P10の英語題名は **43→69px、1.604651倍**。英日とも中央に揃え、文字群を中央寄りへ。1869の行から始まり「In 1892」で2行目が増えるタイミング、後半の紙色・質感、3%のゆっくりしたズームはv02と同じ。
- P07/P11/P12/P13も一部を少し拡大。文字列は全カードでv02と完全一致。5種類、P10の前後半を含む実際の6ショットだけを変更。
- 文字の旧・新区画を除く全画素はv02と一致。背景の色・質感、年表の線・点、BMJの枠などを保持。残り **24ショット** の元画像・中間動画はv02とSHA-256一致。
- 台本・英日音声・BGM・SRT・全ショットの順序と開始終了時刻・総尺・OP/END・カラー資料・写真・サムネを保持。[保持検査](records/episode_specific_qc.json)。音声ストリームのSHAとSRTのバイトをv02と照合して一致。
- 全体を指定どおり単一エンコーダーで再生成しているため、未変更ショットの完成MP4には再圧縮によるごく小さな画素差があり得る。未変更の元画像と中間動画を新たに加工していないことはハッシュで確認。
- 追加生成・購入・YouTube投稿なし。非公開Draftを維持。

## コントラスト比の実測

**全て4.5以上、最小 5.522575。** 各行は、そのカードの該当色の全文字領域で最も低かった値。

|カード|強調色 #5A3A1A|本文 #3B2C21|
|---|---:|---:|
|D_illness|5.522575|7.236457|
|D_novels_1869|7.040556|9.225529|
|D_novels_1892|6.377542|8.356754|
|D_warning|7.040556|9.225529|
|D_bmj|7.040556|9.225529|
|D_summary|7.040556|9.225529|


実際の文字色と、描画前の同じ背景画像の各文字bbox内全画素を測定。sRGBを線形化して相対輝度を求め、`(L明+0.05)/(L暗+0.05)` で算出。アンチエイリアス縁の混色を文字色として測らず、文字本来の色で比較する。[W3Cの定義と測定上の説明](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)。

[全文字列・サイズ・bbox・比率のJSON](records/contrast_validation.json) ／ [CSV](EP008_contrast_v03.csv)。

## v02→v03比較

完成した両動画を先頭から連続デコードし、同じ中央フレームを左右に並べた。[カード全体一覧](review/v03_cards.jpg)。

- [P07 D_illness](review/comparison_v02_v03_01_D_illness.jpg)
- [P10 D_novels_1869](review/comparison_v02_v03_02_D_novels_1869.jpg)
- [P10 D_novels_1892](review/comparison_v02_v03_03_D_novels_1892.jpg)
- [P11 D_warning](review/comparison_v02_v03_04_D_warning.jpg)
- [P12 D_bmj](review/comparison_v02_v03_05_D_bmj.jpg)
- [P13 D_summary](review/comparison_v02_v03_06_D_summary.jpg)

[比較一覧1](review/cards_comparison_sheet_1.jpg) ／ [比較一覧2](review/cards_comparison_sheet_2.jpg)。

## 動画・字幕の検査

- 共通 **347.566667秒、10,427フレーム**、1920×1080、30fps固定、H.264 High / yuv420p。
- 30ショットを個別デコーダーで非圧縮フレームへ戻し、単一エンコーダーへ入力。
- 英日字幕なし・字幕付きの4本を先頭から末尾までデコードし、警告・エラー0。英日本編は全フレームで形式1種類、SPS profile_idc=100のみ。
- 英日各30ショットの先頭・中央・末尾90画像を、連続デコードから取得。英日本編の映像ストリーム同一。
- 完成v03の動く23ショットの全隣接フレームで p95÷中央値の最大 **1.640256**（2.5以下）。静止4画面は中間物の差分0、D_bmjは60/150フレームでの意図した2回の数字表示を確認。最終動画の全差分は静止画も含め保存。[動きの検査](records/final_video_motion.json)。
- D_bmjの最終圧縮由来の微小差分は中央値 **0.000002741**／p95 **0.000213816**（8bit階調）、比率 **78.000**。カメラ移動のない段階表示のため移動ショットの比率判定には含めず、ロスレス中間物で数字の2回の表示切替以外の全差分0を確認した。数値を丸めて0扱いにせず、全差分を記録。
- 音声はv02と同一で、英日とも **-16.00 LUFS**。字幕75件（英）・78件（日）はv02とバイト一致。
- 標準・拡大字幕の全ページを実描画し、文字カードと非重複。本文はズームを含め **y≤700**。[字幕の検査](records/subtitle_layout_validation.json)。
- ENDは **337.566667〜347.566667秒**、末尾ちょうど10秒。

英日全ショットの先頭・中央・末尾一覧：

- [en 一覧1](review/continuous_en_sheet_01.jpg)
- [en 一覧2](review/continuous_en_sheet_02.jpg)
- [en 一覧3](review/continuous_en_sheet_03.jpg)
- [en 一覧4](review/continuous_en_sheet_04.jpg)
- [en 一覧5](review/continuous_en_sheet_05.jpg)
- [en 一覧6](review/continuous_en_sheet_06.jpg)
- [en 一覧7](review/continuous_en_sheet_07.jpg)
- [en 一覧8](review/continuous_en_sheet_08.jpg)
- [ja 一覧1](review/continuous_ja_sheet_01.jpg)
- [ja 一覧2](review/continuous_ja_sheet_02.jpg)
- [ja 一覧3](review/continuous_ja_sheet_03.jpg)
- [ja 一覧4](review/continuous_ja_sheet_04.jpg)
- [ja 一覧5](review/continuous_ja_sheet_05.jpg)
- [ja 一覧6](review/continuous_ja_sheet_06.jpg)
- [ja 一覧7](review/continuous_ja_sheet_07.jpg)
- [ja 一覧8](review/continuous_ja_sheet_08.jpg)

## 次の確認

本人・Claude：強調文字とP10の大きさ・位置・読みやすさ。音声はv02での試聴も同じ。サムネはv02の4案を維持（ClaudeのおすすめD、本人の選択待ち）。公開目標11/4 09:00 JSTを維持。
