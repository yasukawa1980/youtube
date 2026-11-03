"""Git-visible completed v02/4K delivery handoff, after REST verification."""
import shutil
import os
os.environ.setdefault('WOM10_ROOT','/Volumes/ESD-02/新チャンネル/EP010_Krampus/確認版_v02_20261103')
from pathlib import Path
from PIL import Image
from wom10_produce import ROOT,REPO,read,sha

def main():
 share=read(ROOT/'records/sharing_v02.json');assert share['status']=='verified' and len(share['assets'])==8
 qc=read(ROOT/'records/qc_v02.json');rev=read(ROOT/'records/revision_qc_v02.json');enc=read(ROOT/'records/4k_encoding_v02.json');assert qc['passed'] and rev['passed']
 out=REPO/'new-channel/wom10_確認版_v02_20261103';out.mkdir(parents=True,exist_ok=True)
 for n in ['records','確認画像']:(out/n).mkdir(exist_ok=True)
 names=['qc_v02','revision_qc_v02','continuous_qc','final_video_motion','4k_encoding_v02','sharing_v02','layout_v02','v02_owner_approval','visual_manifest','render_shots','master_timeline','subtitle_validation','source_assets','source_identity','first_pass_identity','audio_qc','reading_replacements','pronunciation_locations','release_archives_v02','encoding_method','container_precision']
 for name in names:shutil.copy2(ROOT/f'records/{name}.json',out/'records'/f'{name}.json')
 for p in ROOT.glob('deliverables/*'):
  if p.suffix in ['.srt','.md','.txt','.csv']:(out/p.name).write_text(p.read_text())
 for p in ROOT.glob('review/*.jpg'):
  if p.name.startswith(('continuous_','opening_','subtitles_')) or p.name in ['K03a_approved_v02.jpg','D_summary_v02.jpg','D_names_v02.jpg','D_dec6_v02.jpg','D_1869_v02.jpg','D_grimm_v02.jpg','D_noancient_v02.jpg']:
   assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,out/'確認画像'/p.name)
 (out/'SHA256SUMS_shared.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in share['assets']))
 text=f'''# 第10話クランプス v02・英語4K版 取得案内

**投稿に使用する映像は `EP010_Krampus_en_v02_2160p30.mp4`。v01の4K版は使わない。** 日本語は `EP010_audio_ja.wav` またはM4Aを音声トラック用に使用する。英日SRTはv01と同じ本文・時刻。

[非公開Draft Release]({share['release_url']})、Release ID **{share['release_id']}**。4本の1080p（英日通常版・字幕入り確認版）、英語4K版、資料ZIP3本の計8ファイル。全件REST再取得でSHA256とバイト数一致、匿名404を確認。公開・予約はしていない。

```sh
 gh api repos/yasukawa1980/youtube/releases/{share['release_id']}
 gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
'''
 for a in share['assets']:text+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
 text+='\n[SHA256SUMS](SHA256SUMS_shared.txt)／[完成・検査結果](../wom10_制作結果_v02_20261103.md)。\n\n音声はv01と同一。本人の試聴はv01でもよい。サムネAはClaude推奨、本人の最終選択待ち。公開予定11/8 09:00 JST。ショートA1Rの予定18:00を含む当日の公開本数は予約時に照合する。\n'
 (out/'README.md').write_text(text)
 layout=read(ROOT/'records/layout_v02.json');summary=next(c for c in layout['cards'] if c['key']=='D_summary');motion=read(ROOT/'records/final_video_motion.json')
 text=f'''# 第10話クランプス 制作結果v02・英語4K版（2026-11-03）

**v02完成、英語4K版作成、非公開共有・REST検証完了。Claude確認・本人試聴待ち。** [取得案内](wom10_確認版_v02_20261103/README.md)。Release ID `{share['release_id']}`。

## 修正

- K03a：本人回答「上半身を広く見せる構図で進める」を反映。原寸矩形 `[150,100,3350,2500]`、表示高864px。上半身・枝束を広く入れ、子どもを除外。舌は途中まで入ることを本人了承。原画の消去・描き足しなし。最大原寸倍率0.3690以下。
- D_names：地図を高さ約622pxへ拡大し国名を図中に追加。右側の3名称は固定86ポイント・cap height61px。下の一文を拡大。札の表示切替時刻はv01のまま。
- D_summary：上3・下2へ組み直し。通常幅Arial Boldの固定83ポイント・cap height60px。行別縮小・横圧縮なし。箱内の最小余白 **{rev['summary_minimum_padding']}px**（条件24px以上）。文字は空白・改行以外v01と一致。
- D_dec6 / D_1869 / D_grimm / D_noancient：字の大きさと文字を保ち、本文グループの上下中心をy550へ移動。

[上半身](wom10_確認版_v02_20261103/確認画像/K03a_approved_v02.jpg)／[地図](wom10_確認版_v02_20261103/確認画像/D_names_v02.jpg)／[まとめ](wom10_確認版_v02_20261103/確認画像/D_summary_v02.jpg)。

## 1080pと変更範囲

英日367.266667秒、11,018フレーム、1920×1080・30fps CFR・H.264 High・yuv420p。全ショットを個別にデコードし、非圧縮フレームから単一エンコーダーで組み立て。全4完成動画の連続デコード警告0。英日通常版の映像ストリーム一致。

音声ストリームはv01と一致。英日WAV、SRT、台本、共通タイムラインもSHA256一致。切替時刻・動きの設定を保持。画面の変更はK03aと6カードのみで、他11ショットの入力画像画素は同一。最終の再圧縮後の全画素一致を主張するものではない。

字幕入り確認版は従来どおりFontSize14。カード文字の最下端y{rev['card_maximum_text_bottom']}、字幕の最上端y{rev['subtitle_minimum_top']}、間隔{rev['clearance_px']}px。拡大した図解は、任意にFontSize26へ大きくした場合まで重なりを保証していない。

全20ショットの先頭・中央・末尾を英日とも連続デコードから抽出。札と年代・所蔵の一致を画素照合。動素材の完成画素によるp95/中央値は最大{max(c['ratio'] for c in motion['checks'] if not c['static_source']):.3f}、全2.5以下。静止カードは指定行表示以外の中間画素変化0。エンドカードは最後10秒。

## 英語4K版

`wom10_4k.py v02 en` でv02英語1080pから3840×2160へLanczos拡大。既存のx264 veryfast、40Mbps指定・上限45Mbps・GOP15・yuv420pを使用。細部を新たに生成する処理ではない。日本語は音声トラック用なので4K映像を別に作っていない。

実測：**{enc['frames']:,}フレーム**、**{enc['duration']:.6f}秒**、平均 **{enc['bit_rate']/1e6:.3f}Mbps**、**{enc['bytes']:,}bytes**。H.264 High／yuv420p／30fps。全編デコード警告0。音声ストリームは入力1080pと一致。入力と出力のSHA256を記録。

**投稿用はv02の4K版。既存v01の4K版は使用しない。** 旧ファイルを削除・移動・改名せず、この記録で区別する。YouTube側の自動画質改善効果は公開後の確認事項で、現時点で保証しない。

8ファイルすべてをRelease ID指定RESTで再取得し、バイト数・SHA256一致、匿名取得404を確認。音源・動画・原寸画像はGitに追加していない。保存先 `{ROOT}`。

## 次の確認

音声はv01のまま試聴できる。本人の発音・通し再生・サムネ選択、Claudeのv02画面確認待ち。公開・予約・追加課金なし。公開予定11/8 09:00 JST、同日のA1R 18:00予定を含めて予約時に本数照合する。
'''
 (REPO/'new-channel/wom10_制作結果_v02_20261103.md').write_text(text)
 (REPO/'new-channel/wom10_修正進捗_v02_20261103.md').write_text('# 第10話 v02修正完了\n\nK03aは本人が上半身構図を承認。v02と英語4K版を完成・非公開共有済み。\n\n[完成結果](wom10_制作結果_v02_20261103.md)／[取得案内](wom10_確認版_v02_20261103/README.md)。v01の4K版は投稿に使用しない。\n')
 print('FINAL V02 HANDOFF READY',flush=True)
if __name__=='__main__':main()
