"""Build local preview and GitHub-readable EP006 evidence after verified delivery."""
import argparse,csv,json,shutil
from pathlib import Path
from PIL import Image
from wom06_produce import ROOT,REPO,read,save,sha
GUIDE=REPO/'new-channel/wom06_確認版_v01_20261026'
def preview():
 out=ROOT/'deliverables';sections=[]
 for lang,title in [('en','English'),('ja','日本語')]:
  name=f'EP006_Sphinx_{lang}_v01_subtitled_review_1080p30.mp4'
  sections.append(f'<section><h2>{title}・字幕入り確認版</h2><video controls preload="metadata" src="{name}"></video><p><a href="EP006_Sphinx_{lang}_v01_1080p30.mp4">字幕なし本編</a> · <a href="EP006_Sphinx_{lang}_v01_1080p30.srt">SRT</a> · <a href="EP006_audio_{lang}.wav">投稿用WAV</a></p><h3>固有名詞の試聴</h3><audio controls preload="metadata" src="EP006_pronunciation_{lang}.m4a"></audio><p><a href="EP006_pronunciation_{lang}.txt">試聴位置一覧</a></p></section>')
 html='<!doctype html><html lang="ja"><meta charset="utf-8"><title>Quiet Origins — EP006 Sphinx v01</title><style>body{max-width:1100px;margin:40px auto;padding:0 24px;background:#0c1820;color:#eee8dc;font:17px/1.7 system-ui}h1,h2{font-weight:500;color:#d8b575}a{color:#b9d4e5}video{width:100%}audio{width:min(100%,600px)}section{margin:50px 0}img{width:48%;vertical-align:top}</style><h1>Quiet Origins · Sphinx</h1><p>英日共通 6分5.17秒。本人の試聴・映像確認用です。</p><p>固有名詞の読み、P10のモローの切り出し、先頭からの通し再生をご確認ください。</p>'+''.join(sections)+'<h2>サムネ候補</h2><img src="EP006_thumbnail_museo_Album1_004.jpg" alt="古写真案"> <img src="EP006_thumbnail_met_544442.jpg" alt="ハトシェプスト案"><p>同じフォルダに添付ファイルを保存して開いてください。再生は手動開始です。</p></html>'
 (out/'preview.html').write_text(html)

def report():
 shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified' and shared['draft']
 qc=read(ROOT/'records/qc_v01.json');motion=read(ROOT/'records/motion_v01.json');assert qc['passed'] and motion['passed']
 GUIDE.mkdir(exist_ok=True);(GUIDE/'records').mkdir(exist_ok=True);(GUIDE/'frames').mkdir(exist_ok=True)
 for p in (ROOT/'records').glob('*.json'):
  if p.name!='still_render_progress.json':shutil.copy2(p,GUIDE/'records'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.md','.srt','.txt','.csv','.html']:
   shutil.copy2(p,GUIDE/p.name)
   # Keep previously shared paths current without moving or removing them.
   if (GUIDE/'deliverables').exists():shutil.copy2(p,GUIDE/'deliverables'/p.name)
 for p in (ROOT/'review').glob('*.jpg'):
  if p.name.startswith(('continuous_','center_','kling_','subtitles_')):
   assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
   shutil.copy2(p,GUIDE/'frames'/p.name)
 shutil.copy2(ROOT/'records/visual_manifest.json',REPO/'new-channel/research/wom06_画面構成_v01_20261026.json')
 moreau=next(i+1 for i,s in enumerate(read(ROOT/'records/render_shots.json')) if s['key']=='met_437153')
 ratio=max(s['measurement']['p95_over_median'] for s in motion['shots']);total=sum(a['bytes'] for a in shared['assets'])
 final_motion=read(ROOT/'records/final_video_motion.json');final_ratio=max(c['ratio'] for c in final_motion['checks'] if c['motion_ratio_applicable'])
 rows='\n'.join(f"| {f['name']} | {f['loudness']['input_i']} | {f['loudness']['input_tp']} |" for f in qc['files'])
 text=f'''# EP006 スフィンクス — 英日確認版 v01（2026-10-26）

英日確認版を制作し、[非公開Draft Release]({shared['release_url']})へ保存しました。**本人の試聴・映像確認待ち**です。YouTubeには投稿していません。

## 完成物と共有

- 共通尺 **365.166667秒（6分5.17秒）・10,955フレーム・30fps CFR**。
- 字幕なし英日MP4、字幕入り英日確認版、英日SRT、英日M4A・48kHz/24bit WAV、サムネ2案、固有名詞の試聴音声・時刻表、英日投稿情報、出典クレジット、検査記録。
- Release ID **{shared['release_id']}**。全**{len(shared['assets'])}添付・{total:,} bytes**をRelease ID指定RESTから再取得し、SHA-256・bytes・GitHub digestの一致を確認。
- [取得・再生案内](wom06_確認版_v01_20261026/README.md)。高解像度資料・音声・動画はGitには追加していません。

## 実測した検査

全25ショット（本編23＋OP＋エンドカード）をそれぞれ独立にデコードし、非圧縮yuv420pを単一のH.264エンコーダーへ渡しました。圧縮ショットの連結はしていません。

- 通常版の英日それぞれ全10,955フレームを先頭から連続デコード。警告・エラー0、全フレーム1920×1080/yuv420p、全SPSのprofile_idc=100（High）。
- 各ショットの先頭・中央・末尾、計75枚×2言語をシークなしの連続デコードから抽出。[英語一覧1](wom06_確認版_v01_20261026/frames/continuous_en_sheet_01.jpg)／[日本語一覧1](wom06_確認版_v01_20261026/frames/continuous_ja_sheet_01.jpg)。各7枚の一覧と25枚の中央画像を保存。
- 字幕入り確認版も含む4本で連続デコード、30fpsの全PTS、尺・フレーム数を検査。通常版の英日映像ストリームは同一。字幕入り版の音声も対応する通常版と同一。
- 個別ショット中間映像23本の全隣接フレームを測定。p95÷中央値の最大 **{ratio:.4f} ≤ 2.5**（完全静止は0/0を1と記録）。ROIと全測定値は [motion_v01.json](wom06_確認版_v01_20261026/records/motion_v01.json)、一覧はCSV。
- 最終MP4も先頭から全フレームを測定し、動く20ショットの最大は **{final_ratio:.4f} ≤ 2.5**。静止3画面は元の全フレーム差が厳密に0であることを確認。最終圧縮で生じる差の比率は未定義または89となるため、動きの指標としては適用外とし、生の測定値を [final_video_motion.json](wom06_確認版_v01_20261026/records/final_video_motion.json) に変更せず記録。共通ブランド動画は動き評価の対象外。
- SRT英84件・日89件、本文は改行等のレイアウト空白を除き承認済み台本と一致。最短英1.489333秒／日1.4秒、最長行英42字／日22字、2行以内。
- 全字幕を14・26の両サイズで描画して重なりを検査。画面文字の最下端y=655、字幕の最上端は拡大時も英855／日851。
- OPはP02後の40.300〜44.300秒。エンドカードは355.166667〜365.166667秒、最後のちょうど10秒。共通素材の原本SHAは変更なし。
- 日本語のOP前待ち1.412667秒。WAVは両言語とも48kHz・24bit・2ch・17,528,000サンプル。
- 下記4本とも−60dB基準で1秒以上の無音0件。

| ファイル | LUFS | dBTP |
|---|---:|---:|
{rows}

## 資料・構図

採用資料19点を各1回。P02の比較図内の2点を含みます。同一刊本の別ページ、同じ原写真の別印画は重複していません。原本のSHA-256は素材台帳と一致。資料札・出典・刊年・撮影者を上部に配置しました。

モローは原画像の正規化 **[.12,.10,.95,.355]** を先に切り出し、背景ぼかしを含む全構成をその画像だけから作成。動きの終点もその外には出ません。[本編の中央フレーム](wom06_確認版_v01_20261026/frames/center_en_{moreau:02d}.jpg)／[先頭・中央・末尾](wom06_確認版_v01_20261026/frames/continuous_en_shot_{moreau:02d}.jpg)。これは構成案ではなく完成MP4の連続デコードから取った画像です。

指定の範囲では、男性側の胸の一部が画面下端に残ります。女性側の胸と下部の犠牲者は映していません。露出の許容については本人の確認待ちです。

図解は指定どおり比較図となぞなぞの3つの線画。朝・昼・晩の記号は使っていません。資料の拡大範囲はvisual_manifestに記録。ヘシオドス・Jebbの引用行は枠・下線なし。

## Kling

ブラウザ接続が復旧し、Kling 3.0・1080p・16:9・音声なしで生成しました。初回8秒×3本（64×3=192）、修正5秒×2本（40×2=80）、**合計272クレジット**。UI残高651→379と一致、上限300以内です。追加購入・契約変更はありません。

- V01：初回の手前の像の顔の細部とCG調が強かったため、遠景の絵画調へ修正したv02を採用。特定の王の肖像は指定せず、人物は描いていません。像の一般的な顔形は見えます。
- V02：初回は影が空を通ったため不採用。v02は岩の表面に落ちる翼の影だけに修正。
- V02元動画の24fpsには不均一な動きがあり、8fpsで動きを取り直して光学フローで30fpsへ補間。使用部分のp95÷中央値は5.0966→1.8834。中央の約2.9秒を使用しています。V01・V03は全尺をゆっくり伸ばして使用。処理内容・使用元フレーム区間はrender_shotsに記録。
- V03：初回を採用。遠景のスフィンクスとピラミッド、夕暮れの横移動。
- 採用3本の全尺に分散したフレームを確認し、読める文字・観光客・現代建物・人物の顔がないことを確認。これは人による通し視聴済みという意味ではありません。
- 原本5本を保全し、Draft ReleaseのEP006_Kling_originals.zipへ収録。プロンプト・生成日・設定・費用・SHAは [生成記録](wom06_確認版_v01_20261026/records/kling_generation.json)。

## 読みと本人の確認

初回は置き換えなしの135文（英63・日72）を音声・クエリごと保全。その記録された読み・音素列を根拠に、17文・20件の入力を修正しました。字幕本文は変更なし。「碑」のイシブミは正しい読みのため変更していません。初回と修正後の比較、変更語の文の時刻はreading_audit・reading_replacements・pronunciation_locationsに記録しています。

1. 英語のKhafre、Hatshepsut、Horemakhet、Thutmose、Hesiod、Oedipus、Athenaeus、Herodotus、Sais、androsphinxes、Norden。
2. 日本語のホルエムアケト、トトメス4世、ビブリオテーケー、アテナイオス、紀元前、頭巾、碑、奉納。
3. P10のモローの切り出しに気になる露出がないか。
4. 先頭からの連続再生で、映像の乱れ・動き・音声の自然さ。

**人による聴感・通し視聴は未実施。公開日は本人確認後に決定します。**

Mac保存先：`{ROOT}`。
'''
 (REPO/'new-channel/wom06_制作結果_v01_20261026.md').write_text(text)
 guide=f'''# EP006 スフィンクス v01 — 取得・再生案内

[非公開Draft Release]({shared['release_url']})／Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をRESTから再取得し、SHA-256一致を確認済みです。公開していません。

最初は `EP006_Sphinx_ja_v01_subtitled_review_1080p30.mp4` または英語の同名 `en` 版をご覧ください。通常版は字幕焼き込みなしです。

Macでは `{ROOT}/deliverables/preview.html` を開くと両言語・固有名詞試聴・サムネ2案を確認できます。他の環境ではReleaseの `preview.html` とMP4/M4A/JPGを同じフォルダへ取得して開いてください。

## Claudeからの取得

Draftは通常のタグURLや未認証アクセスで取得できない場合があります。認証済みRESTで**Release ID**を指定してください。

```sh
gh api repos/yasukawa1980/youtube/releases/{shared['release_id']}
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

asset ID・SHA・bytesの全一覧：[sharing.json](records/sharing.json)。検査一式は `EP006_records.zip`、抽出画像は `EP006_review_frames.zip`、Kling原本5本は `EP006_Kling_originals.zip`。

[制作結果と本人の確認項目](../wom06_制作結果_v01_20261026.md)／[モロー本編中央](frames/center_en_{moreau:02d}.jpg)／[英語の読み時刻](EP006_pronunciation_en.txt)／[日本語の読み時刻](EP006_pronunciation_ja.txt)。
'''
 (GUIDE/'README.md').write_text(guide)
 print('REPORT',shared['release_id'],len(shared['assets']),total,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['preview','report']);a=p.parse_args();globals()[a.stage]()
