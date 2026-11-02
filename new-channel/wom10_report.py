"""Make the Git-visible EP010 review handoff after private REST verification."""
import shutil
from pathlib import Path
from PIL import Image
from wom10_produce import ROOT,REPO,read,sha
def main():
 share=read(ROOT/'records/sharing.json');assert share['status']=='verified' and len(share['assets'])==7
 out=REPO/'new-channel/wom10_確認版_v01_20261103';out.mkdir(parents=True,exist_ok=True)
 for folder in ['records','確認画像']:(out/folder).mkdir(exist_ok=True)
 for p in ROOT.glob('records/*'):
  if p.suffix in ['.json','.txt','.log']:shutil.copy2(p,out/'records'/p.name)
 for p in ROOT.glob('review/*.jpg'):
  if p.name.startswith(('continuous_','opening_','thumbnail_')):
   assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,out/'確認画像'/p.name)
 for p in ROOT.glob('deliverables/*'):
  if p.suffix in ['.md','.txt','.srt','.csv']:
   shutil.copy2(p,out/p.name)
   if p.suffix=='.csv':(out/p.name).write_text(p.read_text())
 thumbs=REPO/'new-channel/サムネ確認用/wom10';thumbs.mkdir(exist_ok=True,parents=True)
 for p in ROOT.glob('deliverables/*.jpg'):
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,thumbs/p.name)
 (out/'SHA256SUMS_shared.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in share['assets']))
 text=f'''# 第10話クランプス 確認版v01（2026-11-03）

[制作結果](../wom10_制作結果_v01_20261103.md)。本人承認済み台本v02から制作。Claude確認・本人試聴待ち。公開・予約はしていません。

[非公開Draft Release]({share['release_url']})／Release ID **{share['release_id']}**／タグ `{share['tag']}`。

MP4は英日通常版・英日字幕入り確認版の4本。音声・SRT・固有名詞試聴、サムネ・投稿情報、検査記録は3つのZIPに分けました。全7ファイルをRelease ID指定のRESTから再取得し、ローカル原本とのサイズ・SHA256一致と匿名404を確認済み。

Draftの取得には認証が必要です。タグURLの404だけで不存在と判断せず、まず次のAPIを使用してください。

```sh
gh api repos/yasukawa1980/youtube/releases/{share['release_id']}
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
'''
 for a in share['assets']:text+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
 text+='''
SHA256は [SHA256SUMS_shared.txt](SHA256SUMS_shared.txt)、REST照合記録は [sharing.json](records/sharing.json)。動画・音源の実体はGitに入れていません。

## 本人の確認

1. 英語・日本語の固有名詞試聴（`EP010_pronunciation_en.m4a` / `ja.m4a`）。初回の無置換音声を採用し、全126文のnative音声が初回保存と一致しています。時刻表は同名TXT。
2. 通し再生で声・字幕・映像の切替を確認。音の聴感と語の正しい発音は、人による確認が未実施です。
3. K03aの怖さが強すぎないか。子ども・長い舌を外した上部だけを使用しています。
4. サムネ [A](../サムネ確認用/wom10/EP010_thumbnail_A.jpg) / [B](../サムネ確認用/wom10/EP010_thumbnail_B.jpg) の選択。[168px比較](../サムネ確認用/wom10/EP010_thumbnails_168_comparison.jpg)。

公開予定は本人指定 **2026-11-08 09:00 JST**。予約時に同日のショートA1R（18:00予定）を含めた公開本数を照合してください。第10話のショートは本編合格後の別依頼です。
'''
 (out/'README.md').write_text(text)
 m=read(ROOT/'records/master_timeline.json');q=read(ROOT/'records/qc_v01.json');e=read(ROOT/'records/episode_specific_qc.json');c=read(ROOT/'records/contrast.json');mot=read(ROOT/'records/final_video_motion.json');sub=read(ROOT/'records/subtitle_validation.json')
 assert all(read(ROOT/f'records/{n}.json')['passed'] for n in ['qc_v01','episode_specific_qc','final_video_motion','continuous_qc','subtitle_layout_validation','first_pass_identity','source_identity'])
 text=f'''# Quiet Origins 第10話クランプス 制作結果v01

2026-11-02着手、11-03共有完了。承認済み台本v02から英日確認版を制作。**Claude確認・本人試聴待ち**です。YouTube投稿・予約・Release公開・追加課金はしていません。

[取得案内](wom10_確認版_v01_20261103/README.md)／[非公開Draft Release]({share['release_url']})（ID `{share['release_id']}`）。英日通常版2本・字幕入り確認版2本・資料ZIP3本を、REST再取得で全件照合済み。全assetの匿名取得404。

## 完成ファイル

- 共通尺 **{m['duration_seconds']:.6f}秒（6分07.267秒）**、**11,018フレーム**。1920×1080・30fps CFR・H.264 High・yuv420p。
- 全20ショットを個別にデコードし、非圧縮フレームを1つの映像エンコーダーへ渡して書き出し。ブランド素材も同じ経路。
- 4本すべて先頭から終端まで連続デコード警告0。英日通常版の映像ストリームSHA256一致、各字幕入り確認版の音声は通常版と一致。
- オープニングはP02の後51.000〜55.000秒。共通エンドカードは357.266667〜367.266667秒、正確に最後10秒。
- 指定SSD保存先：`{ROOT}`。11/2に作成したフォルダ名を保持。音源・原寸素材・動画をGitに追加していない。

| 言語 | 完成音量 LUFS | dBTP | 字幕数 | 最短字幕 秒 | 最大行長 |
|---|---:|---:|---:|---:|---:|
'''
 for lang in ['en','ja']:
  f=next(x for x in q['files'] if f'_{lang}_v01_1080p30' in x['name']);s=sub[lang];text+=f"| {lang} | {f['loudness']['input_i']} | {f['loudness']['input_tp']} | {s['count']} | {s['min_seconds']:.3f} | {s['max_line_chars']} |\n"
 text+='''
SRT本文は台本と一致（改行・レイアウトの空白を除いて照合）、2行以内。実SRTも照合し、通常・拡大字幕の全ページを描画してカードと重ならないことを確認。台本の文言変更なし。

英語はKokoro/Heart（af_heart）、speed=0.82。日本語はVOICEVOX:冥鳴ひまり、既存C設定。最初の無置換音声を保存し、その126文とnative音声がSHA256一致。読み替え0件。共通尺に合わせた調整は文間の間のみで、話速・ピッチの加工なし。固有名詞の正しい発音・聴感は本人試聴待ち。語を含む文の時刻一覧と試聴用音声を同梱。

BGMは既存QO_THEME_A02のみ。語り時RMS差18.000dB、切れ目は最大+6dB、100Hzハイパスと2〜4kHz抑制、3秒クロスフェード。完成ミックスに−60dB以下が1秒続く無音なし。日本語の区間内・末尾の待ちは最大1.921秒。

## 素材と画面

採用原典11点を各1回。絵はがき4、美術作品4、写真3。使用しないK05a/K05d/K07a、刊本画像、生成画像・生成動画は入れていない。収集済み14点の中から承認された11点を使用し、当初調査目安の25点を満たしたとの主張はしない。

| 種別 | ショット数 | 秒 |
|---|---:|---:|
'''
 for name,row in e['color_summary'].items():text+=f"| {name} | {row['shots']} | {row['seconds']:.3f} |\n"
 text+='''
写真3点は暖かい単色調整。カラー8点は原色を保持。札・年代・所蔵・作品番号を上部に固定。

- K01aは全体を高さいっぱいに出し、0秒から顔側を軸に寄る。かご・足元の人物の年齢を断定しない。
- K03aは角・顔・枝束の上部だけ。子どもと長い舌の全体を切り抜きから除外。怖さの印象は本人確認事項。
- K09bは左端の武器を外し、演者の列を横へ移動。K09aの札はJagdpercht（1892）で、クランプスと呼ばない。K07bの色票を除外。
- K04aの札は作品名Saint Nicholas Providing Dowries。窓を指す矢印や説明は入れていない。K10aをアルプスと書いていない。

| 原典 | 最大原寸倍率 |
|---|---:|
'''
 for r in e['native_scales']:text+=f"| {r['key']} | {r['max_scale']:.4f} |\n"
 text+='''
全原典1.0倍以下。完成動画の全隣接フレームを固定領域で比較し、動素材のp95/中央値は最大'''+f"{max(x['ratio'] for x in mot['checks'] if not x['static_source']):.3f}"+'''（基準2.5以下）。静止カードは速度比を使わず、可逆圧縮の中間映像で指定した行表示時刻以外の画素変化0を確認。完成MP4の圧縮に由来する微差は記録に残している。

## 6枚の文字カード

| カード | 文字/地の比 | 主要字高 px | 箱内最小余白 px |
|---|---:|---:|---:|
'''
 for card in c['cards']:text+=f"| {card['key']} | {card['foreground_contrast']:.3f} | {card['minimum_major_glyph_height']} | {card['minimum_box_padding'] if card['minimum_box_padding'] is not None else '枠なし'} |\n"
 text+='''
主要字高は名目フォントサイズではなく可視字形を測定。日本語補助行・出典は小さめ。最下端y700以内。箱ありはD_summaryのみで、内側余白19px以上。完成動画から抜いた画像でもカードのコントラスト4.5以上。

D_grimmは指定どおり `"I can well imagine that even in heathen times..."`（末尾3点）。D_summaryの悪魔の供の箱に年代なし。D_namesは大まかな地理模式図で、3つの札を英語語りの該当句に合わせて表示。英日で映像を共通にするため、区間内の細かな表示時刻は英語基準。

## 目視と申し送り

全20ショットの先頭・中央・末尾を完成動画の連続デコードから抽出。英日とも60枚を記録し、英語版の全一覧、日本語版の冒頭一覧、両言語全フレームの形式・札の画素照合を確認。英日通常版の映像ストリームは同一。これは静止画点検で、人の通し試聴の代わりではない。

サムネAはクランプスの顔と同じ作品由来のぼかした緑地で構成し、かごの人物を主役にしない。Bは司教と緑の悪魔の顔。1280×720・1MB未満、168px比較を同梱。生成や描き足しなし。

本人には固有名詞の発音（英日）、K03aの怖さ、冒頭の伝わり方、サムネA/B、全編連続再生を確認してもらう。11/8 09:00 JST公開予定、予約未実施。11/8 18:00予定のA1Rを含め、予約時に当日のチャンネル合計を確認する。第10話ショートはまだ制作しない。

検査JSON・出典・音声時刻・英日投稿情報は [確認版フォルダ](wom10_確認版_v01_20261103/README.md)。制作は `wom10_produce.py`、画面 `wom10_visuals.py`、書き出し `wom10_pictures.py` / `wom10_render.py`、共有 `wom10_share.py`。既存の共通処理を再利用した。
'''
 (REPO/'new-channel/wom10_制作結果_v01_20261103.md').write_text(text)
 print('EP010 REPOSITORY HANDOFF COMPLETE',flush=True)
if __name__=='__main__':main()
