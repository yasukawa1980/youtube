# IRO18 手直し試作の再現

本人が指定した設計をコピー保存した [手直し設計_Codexへ.md](手直し設計_Codexへ.md) に基づく。元の設計・素材は `bgm/IRO/IRO18_毛糸の季節がやってきた/` に残し、移動していない。新規スクリプト・共有資料だけを `iro/` に保存。

1. `python3 iro/iro18_手直し試作_20261018.py --generated <内蔵imagegenで生成した1672x941 PNG>`
2. `python3 iro/iro18_犬拡大検品_20261018.py`
3. Klingを本人許可済みの1本だけUIで生成。プロンプトは [保存済み](../iro18_Kling試作プロンプト_20261018.txt)。取得動画をMac試作フォルダの `Kling_編み物試作1_原本.mp4` へコピー。
4. `python3 iro/iro18_編み物試作を検品_20261018.py`
5. `python3 iro/iro18_試作見本をまとめる_20261018.py`（保存済み完成画面 `/private/tmp/iro18_kling_completed.png` が必要）

依存：Python3・Pillow・NumPy・OpenCV、`/opt/homebrew/bin/ffmpeg` と `ffprobe`、macOS標準ヒラギノ・Avenir。画像の生成には内蔵imagegenを使用し、最終プロンプトは [こちら](../iro18_手元画像プロンプト_20261018.txt)。旧針の除去も手元変更マスクに含める。

これらは試作・検品用のスクリプト。本編・投稿用・旧素材への書き込みやKling自動送信は行わない。今回の作業は [Claude検品用_要約.md](Claude検品用_要約.md) で停止。
