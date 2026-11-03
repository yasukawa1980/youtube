# Quiet Origins 第10話ショート3本 確認版v01（2026-11-03）

本人承認済み台本の英語版3本。**Claude確認・本人試聴待ち。YouTubeには投稿していません。** K2のみ24.533333秒を本人が例外承認済み。

| ID | 見出し | 尺 | 字幕ページ |
|---|---|---:|---:|
| K1 | KRAMPUS WORKS FOR A SAINT | 21.533333秒 | 6 |
| K2 | THE POSTCARD THAT MADE KRAMPUS | 24.533333秒 | 8 |
| K3 | GOLD THROUGH THE WINDOW? | 20.933333秒 | 6 |

## 確認動画・ZIP

新しい非公開Draft Release。公開状態に変更しない。
- Release ID: **432684675**
- [Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-ba389b8557310fdc7715)
- REST: `GET /repos/yasukawa1980/youtube/releases/432684675`

| ファイル | Asset ID | bytes | SHA-256 |
|---|---:|---:|---|
| EP010_shorts_review_v01.zip | 705576923 | 18,166,643 | `ea89044443155631e65766bbe2cecdb1aa306419c426a45d348f234b789d9d1f` |
| QO_short_EP010_K1_v01.mp4 | 705577064 | 49,405,840 | `e1583489ab1365ea9bfa81fd173295f9ff736309db9de87f26ddf3ba1ddfcb0f` |
| QO_short_EP010_K2_v01.mp4 | 705577233 | 38,074,782 | `d5fa294d10a5894453d5e976a4f8e9cb4ef26199cac3dfa7ca87e180446d655b` |
| QO_short_EP010_K3_v01.mp4 | 705577395 | 9,552,961 | `40e3d04edb73705a6932083445ca995118ade6b875ea14115ac9f7cee83ae5c1` |

Release ID指定のRESTで4資産すべてを再取得し、サイズ・SHA-256がローカルと一致。匿名アクセスはRelease・各資産とも404。Draft維持。

取得は `gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/<Asset ID>` を使う。ブラウザーのDraft表示名よりIDを優先する。

## Claude確認の入口

- `確認画像/K1_all_captions.jpg` など：全字幕ページ。
- `確認画像/K1_opening.jpg` など：0／0.5／1.0／1.5／2.0／2.5秒。各フレームの個別JPGは同名サブフォルダ。
- `確認画像/K1_every2s.jpg` など：2秒おき。
- `確認画像/K1_CTA.jpg` など：最後2.5秒の案内。
- `records/card_texts.json`：D_1869とD_houseの文字列・文字寸法。
- `records/final_qc.json`：尺・音量・字幕コントラスト・形式・連続デコード。
- `records/final_pixel_motion.json`：完成動画の全隣接フレームで測定した動き。
- `records/visual_manifest.json`／`source_assets.json`：素材9点（原資料7点＋文字カード2点）、構図、拡大率、権利。

素材は3本で重複なし。K06bは指示どおり余白を含む原はがき全体を0フレームから表示し、他2本の最初の主役と同様、はがき自体の高さを画面の約7割にした。K01aは全幅を維持して人物を小さくし、顔・毛皮から鎖へゆっくり下移動。K03aは使用していない。

元の台本・音声速度は変更していない。K1 21.533333秒／K2 24.533333秒／K3 20.933333秒は最終映像フレーム数÷30で、コンテナの表示尺は音声パケットの丸めでわずかに異なる。人による全編試聴は未実施。
