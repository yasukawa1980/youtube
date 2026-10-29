# Quiet Origins 第8話 確認版v02（2026-10-30）

**映像修正・技術検査・非公開DraftのREST再取得照合済み。本人の全編視聴とClaudeの内容確認待ち。**

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-05475a3cd514d6896c2e) — Release ID **428188580**。8資産すべてのサイズ・SHA-256一致。匿名アクセス404、Draftを維持。

## 取得と確認

- `EP008_Tutankhamun_ja_v02_subtitled_review_1080p30.mp4`：日本語・字幕付き。
- `EP008_Tutankhamun_en_v02_subtitled_review_1080p30.mp4`：英語・字幕付き。
- `EP008_Tutankhamun_{en,ja}_v02_1080p30.mp4`：字幕なし。
- `EP008_audio_and_subtitles.zip`：英日音声・SRT・v01と同じ発音確認抜粋。
- `EP008_thumbnails_and_metadata.zip`：サムネA〜D・168px比較・英日投稿情報・出典・平均輝度表。
- `EP008_QA_records.zip`：全ショットの比較画像、英日連続デコード画像と検査JSON。
- `EP008_AI_scene_review.zip`：再利用したv01ろうそく原動画。

認証後 `gh api repos/yasukawa1980/youtube/releases/428188580` で資産IDを確認し、`gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE` で取得する。全ID・SHAは [sharing.json](records/sharing.json)。

## 修正と保持

- カラー4作品をP05/P09/P11/P13へ挿入。C01はフイTT40の1923–27年の模写、C02は王名入り金指輪、C03はペルネブの彩色礼拝室、C04は王名ビーズと護符の首飾り（現代の再連結）。すべてThe MetのPublic Domain画像、Open Access CC0。[候補・選定理由](../research/wom08_追加カラー素材_20261030.md)。
- C01は別墓の模写、C02/C04は同時代の品でKV62出土品ではないことを表示。C03は引用されたヘテプヘルアクティとは別の墓であることを [確認画像](review/C03_other_tomb_label.jpg) に記録。
- 発掘写真10点は同じ単色セピア。元クロップ（3000px以内へ縮小した比較）に対するRec.709平均輝度が **11.320〜12.879%上昇**。黒≤1／白≥254の画素数は増加なし。完成動画の同区間の全画面平均輝度も **12.126〜13.164%上昇**し、目安10〜15%内。刊本は紙色を保って約2%明るく、新聞は白黒を維持。
- 図解は砂色地・濃茶文字。金色は保ち、細い縁で判読性を補強。P07は落ち着いた砂色。P10は1869の行から始め、英語「In 1892」の開始で2行目を追加、紙色・質感を変えて各画面を3%ズーム。P11/P13は指定の語りでカラーへ切替。P12の数字25→11は研究対象の説明中に約2秒→5秒で表示（実フレームは検査JSONに保存）。
- **台本v02.1・英日音声・BGM・字幕・全区間時刻・347.566667秒を保持**。v01との音声ストリームSHA一致、SRTバイト一致、台本・マスター時刻JSONもバイト一致。[保持検査](records/episode_specific_qc.json)。OP・END・P14ろうそくはv01と同じ原動画・中間映像。追加生成・購入・支出0。

## 実測検査

- 1920×1080、30fps固定、**10,427フレーム**、H.264 High / yuv420p。全30ショットを個別デコードして非圧縮フレームを単一エンコーダーへ入力。
- 英日字幕なし・字幕付き4本を先頭から末尾までデコードし警告・エラー0。英日本編は全フレーム同一形式、SPS profile_idc=100のみ。各30ショットの先頭・中央・末尾90画像ずつを連続デコードから取得。[検査](records/continuous_qc.json)。
- 英日本編の映像ストリーム同一。音声は両言語ともv01と同一、字幕付きも同じ音声。英日とも **-16.00 LUFS**。
- 動く23ショットの最終動画全隣接フレームで p95÷中央値の最大 **1.640256**（2.5以下）。静止4画面はロスレス中間物の全差分0、D_bmjは意図した数字2回の表示切替を確認。最終動画の差分値は静止画も含めて全件保存し、数値を丸めて0扱いにしていない。[動きの検査](records/final_video_motion.json)。
- 英75／日78字幕を標準・拡大で実描画し、画面本文と非重複。画面本文はズームを含めy≤700。全SRTはv01と一致。[字幕検査](records/subtitle_layout_validation.json)。
- 元資料20点とAI1点は各1ショット。カラー4作品はすべて異なる。P01は0秒からB286。ENDは **337.566667〜347.566667秒**、末尾ちょうど10秒。

## 全ショットのv01→v02比較

v02の各ショットの中央と同じ時刻のv01フレームを比較した。全30ショットの比較は以下の8枚。個別比較30枚もQA ZIPに入っている。

- [比較 1](review/comparison_sheet_01.jpg)
- [比較 2](review/comparison_sheet_02.jpg)
- [比較 3](review/comparison_sheet_03.jpg)
- [比較 4](review/comparison_sheet_04.jpg)
- [比較 5](review/comparison_sheet_05.jpg)
- [比較 6](review/comparison_sheet_06.jpg)
- [比較 7](review/comparison_sheet_07.jpg)
- [比較 8](review/comparison_sheet_08.jpg)

英日それぞれの先頭・中央・末尾一覧：

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

全画面平均輝度は完成動画の全フレームを160×90へ面積平均縮小し、8bitグレーで測定。v01もv02と同じ区間で測定。カラー挿入・文字カードの背景変更を含む値なので、写真クロップの10〜15%目標とは別の実測。OP/ENDは再エンコードの僅差がある。

|ショット|区間|素材|v01平均輝度|v02平均輝度|変化|
|---:|---|---|---:|---:|---:|
|1|P01|B286|114.676|129.126|+12.60%|
|2|P02|N03|94.262|95.284|+1.08%|
|3|BRAND|opening|22.090|22.090|+0.00%|
|4|P03|B151|49.480|55.758|+12.69%|
|5|P03|B157|45.634|51.577|+13.02%|
|6|P04|B170|65.688|74.004|+12.66%|
|7|P04|B164|75.436|77.551|+2.80%|
|8|P05|B183|65.692|74.340|+13.16%|
|9|P05|C01|66.509|157.211|+136.38%|
|10|P05|B299|49.111|55.254|+12.51%|
|11|P05|B300|48.595|54.698|+12.56%|
|12|P06|B237|61.836|69.561|+12.49%|
|13|P06|B241|75.553|77.889|+3.09%|
|14|P07|D_illness|20.485|168.420|+722.14%|
|15|P08|N01|96.054|97.055|+1.04%|
|16|P08|N02|99.191|100.285|+1.10%|
|17|P09|B313|61.196|69.232|+13.13%|
|18|P09|C02|61.982|157.889|+154.73%|
|19|P09|B312|85.896|88.166|+2.64%|
|20|P10|D_novels_1869|20.660|193.457|+836.40%|
|21|P10|D_novels_1892|20.660|183.153|+786.52%|
|22|P11|D_warning|19.936|193.242|+869.31%|
|23|P11|C03|19.936|179.145|+798.60%|
|24|P12|B246|68.093|76.350|+12.13%|
|25|P12|D_bmj|21.019|192.561|+816.14%|
|26|P13|D_summary|20.312|193.286|+851.58%|
|27|P13|C04|20.312|194.542|+857.77%|
|28|P14|V01|27.820|27.820|+0.00%|
|29|P15|credits|19.710|20.096|+1.96%|
|30|BRAND|endcard|20.363|20.363|+0.00%|

[CSV](EP008_luminance_v01_v02.csv) ／ [全フレーム測定方法・JSON](records/luminance_comparison.json)。

サムネA〜Dは [168px比較](../サムネ確認用/wom08/wom08_サムネ168px比較_v02_20261030.jpg)。Dはフイの墓の模写を使用し、文言はNOT IN THE TOMB。

## 次の確認

本人：英日全編の映像と明るさ、発音・BGM。Claude：資料の札・別墓の区別・出典・サムネ4案。公開目標11/4 09:00 JSTを維持。YouTube未投稿、Releaseは非公開Draft。
