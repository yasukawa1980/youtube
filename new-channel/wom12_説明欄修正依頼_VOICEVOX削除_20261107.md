# 依頼：第12話本編の説明欄から VOICEVOX の表記を消す（2026-11-07 Claude作成）

状態：**本人指示（2026-11-07「VOICEVOX:冥鳴ひまりだけ消しておいて下さい」）。** CodexまたはMac側のClaudeが、YouTube Studioで行う。クラウドのClaudeからはStudioに届かない。

対象：Quiet Origins（`UCfLJOojEY9VB3rvrjICk90Q`）第12話本編 **`_C9RKwdvb9Y`**（11/14 09:00公開予約）。第12話では日本語音声を追加していないため、声のクレジットのVOICEVOXは不要。

## 変えるところ（英語の説明と、日本語翻訳の説明の両方）

| 今 | 直したあと |
|---|---|
| `Voice: Kokoro / Heart (af_heart) · VOICEVOX:冥鳴ひまり` | `Voice: Kokoro / Heart (af_heart)` |
| `https://www.meimeihimari.com/terms-of-use`（次の行） | **行ごと削除**（VOICEVOXの利用規約へのリンクで、上の表記を消すと対応する声がなくなるため） |

- **ほかの文字は1文字も変えない**（チャプター・出典・クレジット・ハッシュタグ）。
- リポジトリの `wom12_確認版_v02_20261105/EP012_upload_info_en.md`・`EP012_upload_info_ja.md` はClaudeが同じように直した。ただし日本語の説明は、予約時にチャプター時刻を英語版の時刻（00:00／00:57／01:42／03:21／04:34）へ直して登録してある（[投稿結果](wom12_投稿結果_EP012_20261107.md)）。**Studioに今ある本文から上の2か所だけを消す**（ファイルの本文を貼り直さない）。
- 公開予約（11/14 09:00）・タイトル・字幕・終了画面・ほかの設定は変えない。保存後、説明を読み戻して、2か所が消え、それ以外が変わっていないこと（チャプター5つが残っていること）を確かめる。
- ショートN1〜N3の説明は `Narration: Kokoro / Heart (af_heart), synthetic speech.` でVOICEVOXの表記はないので、触らない。

## 記録

[投稿結果](wom12_投稿結果_EP012_20261107.md)の末尾に「説明欄の修正（日時・変えた2か所・読み戻しの結果）」を追記して `bgm/production` にpush。想定外の画面があれば止めて報告する。
