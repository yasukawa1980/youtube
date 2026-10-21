# Quiet Origins：オープニング・エンドカードの動画試作 v01

2026-10-21。本人の「進めて下さい」により、4秒オープニング・20秒エンドカードと、アヌビスに接続した英日確認版を制作。**本人の試聴・方向確認待ち。全編への反映は未実施。**

## 再生

Mac保存先：`/Users/ryo/Desktop/新チャンネル/ブランド素材/オープニング_エンドカード_動画試作_v01_20261021`。
`deliverables/preview.html` を開くと6本を再生できる。動画を直接開く場合も `deliverables/`。

- `Quiet_Origins_opening_trial_v01.mp4`：4秒、音付き。
- `Quiet_Origins_endcard_trial_v01.mp4`：20秒、音付き。
- `EP001_ja_opening_connection_trial_v01.mp4`：日本語の冒頭接続、55.833秒。
- `EP001_ja_endcard_connection_trial_v01.mp4`：日本語の末尾接続、40秒。
- 英語の接続確認版は同じ名前の `ja` を `en` にした2本。
- 単体の音はPCM24bit・48kHz・ステレオWAVでも保存。

## 反映したデザインと音

- 採用済みQアイコンの金色の画素を、動画合成用のアルファマットで取り出して使用。Qを再生成・描き直していない。原素材のSHA-256は [制作依頼記録](records/request.json)。
- 濃紺・金色・アイボリーを維持。背景の地図風の等高線・航路と光はコードで制作した抽象模様で、特定の地域を表さない。静止画ラフの装飾をそのまま動かしたものではない。
- オープニング：Qを0.18〜1.15秒、タイトルを1.05〜2.05秒にフェードイン。光が静かに横切る。全体を一枚の画像としてズームする動きは使っていない。
- エンドカード：タイトル・Q・締めの言葉は固定。背景の光だけがゆっくり変化する。配置確認用の枠は [別のガイド画像](frames/endcard_layout_guide.jpg) に分離し、動画には焼き込んでいない。左側は今後の動画案内用の余白。クリック要素は未設定。
- 音はローカルで新規合成したD/A系の穏やかな音と短い澄んだ音。外部サービス・購入・追加の画像生成は使用していない。単体WAVの実測は冒頭−29.00 LUFS、末尾−30.00 LUFS。末尾の音は最後の5秒でフェードアウト。MP4の測定は下表。

## 本編との接続

- 冒頭はv07の0〜51.833秒を使用し、N01/N02の段落境界29.067秒に4秒のオープニングを挿入。接続版は33.067秒で本編に戻る。語りや字幕を途中で分割していない。切り口の小さな音量フェードだけを加えた。
- 末尾はv07の658〜678.7秒（クレジットとお礼）を使用し、678秒から0.7秒でエンドカードへ切り替える。日本語の最後の発話は677.691秒で終わる。接続確認版は40秒。旧末尾の音楽だけの4秒はこの抜粋では省くが、元のv07は変更していない。
- 字幕は既存の字幕入り確認版を使い、元の画面と一緒に移動。ロゴ中に本編字幕が残っていないことを英日で確認。

## 検品

全6動画：1920×1080・30fps、全編デコード成功、PTS間隔一定、クリッピングなし。単体音声の始端・終端の5msも小さな音量で終わることを確認。元v07の共有10ファイルはSHA-256一致で保全を検証。画像の確認は実際のMP4抽出フレームで実施。聴感・全編の人による再生は未確認で、本人の試聴を待つ。

| 動画 | 秒 | フレーム | LUFS | dBTP |
|---|---:|---:|---:|---:|
| EP001_en_endcard_connection_trial_v01.mp4 | 40.000 | 1200 | -18.42 | -3.89 |
| EP001_en_opening_connection_trial_v01.mp4 | 55.844 | 1675 | -16.07 | -4.08 |
| EP001_ja_endcard_connection_trial_v01.mp4 | 40.000 | 1200 | -17.41 | -5.47 |
| EP001_ja_opening_connection_trial_v01.mp4 | 55.844 | 1675 | -16.54 | -5.13 |
| Quiet_Origins_endcard_trial_v01.mp4 | 20.000 | 600 | -30.01 | -23.18 |
| Quiet_Origins_opening_trial_v01.mp4 | 4.000 | 120 | -29.01 | -23.57 |

[冒頭の動き](frames/opening_storyboard.jpg)／[末尾の画面](frames/endcard_storyboard.jpg)／[日本語接続](frames/connection_ja.jpg)／[英語接続](frames/connection_en.jpg)。

[検品記録](records/qc.json)／[フェード・字幕検査](records/additional_checks.json)／[画面確認](records/visual_review.json)／[接続時刻](records/connection_plan.json)。

## Claudeへの共有

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-dcd2d3d24c76fa9fbc5f)、Release ID **419241526**。全10添付をRESTで再取得してSHA-256一致。

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_en_endcard_connection_trial_v01.mp4 | 661631985 | 4,051,909 |
| EP001_en_opening_connection_trial_v01.mp4 | 661632097 | 10,485,828 |
| EP001_ja_endcard_connection_trial_v01.mp4 | 661632196 | 4,077,679 |
| EP001_ja_opening_connection_trial_v01.mp4 | 661632292 | 10,428,669 |
| Quiet_Origins_endcard_trial_v01.mp4 | 661632424 | 1,771,061 |
| Quiet_Origins_opening_trial_v01.mp4 | 661632497 | 824,144 |
| Quiet_Origins_endcard_trial_v01.wav | 661632559 | 5,760,044 |
| Quiet_Origins_opening_trial_v01.wav | 661632654 | 1,152,044 |
| preview.html | 661632742 | 3,592 |
| SHA256SUMS_shared.txt | 661632814 | 919 |

```sh
gh api repos/yasukawa1980/youtube/releases/419241526 --jq '.assets[] | "\(.id) \(.name)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

コード：`new-channel/wom01_brand_motion.py`、`wom01_brand_motion_review.py`、`wom01_brand_motion_share.py`。出力先は環境変数 `QO_MOTION_ROOT` で指定し、prepare → pictures → sound → connections → verify の順に実行。画面検査後に共有する。

全編制作・投稿・Studio設定・追加支出はなし。指定SSD ESD-EPBへの同期は未実施。
