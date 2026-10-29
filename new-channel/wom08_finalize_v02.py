"""検査とDraftのREST照合が済んだ第8話v02をGitHub確認用にまとめる。"""
import os
os.environ['WOM08_ROOT']='/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v02_20261030'
import shutil,json
from pathlib import Path
from wom08_produce import ROOT,REPO,read,sha

def main():
 records=ROOT/'records';qc=read(records/'qc_v02.json');sharing=read(records/'sharing.json');motion=read(records/'final_video_motion.json');specific=read(records/'episode_specific_qc.json');cont=read(records/'continuous_qc.json');layout=read(records/'subtitle_layout_validation.json');lum=read(records/'luminance_comparison.json');tone=read(records/'tone_measurements.json')
 assert all(x['passed'] for x in [qc,motion,specific,cont,layout]);assert sharing['draft'] and sharing['status']=='verified' and len(sharing['assets'])==8
 dest=REPO/'new-channel/wom08_確認版_v02_20261030';(dest/'records').mkdir(exist_ok=True,parents=True);(dest/'review').mkdir(exist_ok=True)
 for p in records.glob('*.json'):shutil.copy2(p,dest/'records'/p.name)
 for pattern in ['compositions_*.jpg','comparison_sheet_*.jpg','continuous_*_sheet_*.jpg','opening_*.jpg']:
  for p in (ROOT/'review').glob(pattern):shutil.copy2(p,dest/'review'/p.name)
 shots=read(records/'render_shots.json');i=next(i for i,s in enumerate(shots,1) if s['key']=='C03');shutil.copy2(ROOT/f'review/center_en_{i:02d}.jpg',dest/'review/C03_other_tomb_label.jpg')
 for p in (ROOT/'deliverables').glob('*.md'):shutil.copy2(p,dest/p.name)
 for p in (ROOT/'deliverables').glob('*.csv'):shutil.copy2(p,dest/p.name)
 moving=[c for c in motion['checks'] if c['motion_ratio_applicable']];maxratio=max(c['ratio'] for c in moving);photos=[x for x in tone['measurements'] if x['key'] in tone['photos']];lo=min(x['increase_percent'] for x in photos);hi=max(x['increase_percent'] for x in photos)
 video_photos=[r for r in lum['shots'] if r['key'] in tone['photos']];vlow=min(r['increase_percent'] for r in video_photos);vhigh=max(r['increase_percent'] for r in video_photos)
 def table():
  s='|ショット|区間|素材|v01平均輝度|v02平均輝度|変化|\n|---:|---|---|---:|---:|---:|\n'
  for r in lum['shots']:s+=f"|{r['shot']}|{r['segment']}|{r['key']}|{r['v01_mean_luma']:.3f}|{r['v02_mean_luma']:.3f}|{r['increase_percent']:+.2f}%|\n"
  return s
 readme=f'''# Quiet Origins 第8話 確認版v02（2026-10-30）

**映像修正・技術検査・非公開DraftのREST再取得照合済み。本人の全編視聴とClaudeの内容確認待ち。**

[非公開Draft Release]({sharing['release_url']}) — Release ID **{sharing['release_id']}**。8資産すべてのサイズ・SHA-256一致。匿名アクセス404、Draftを維持。

## 取得と確認

- `EP008_Tutankhamun_ja_v02_subtitled_review_1080p30.mp4`：日本語・字幕付き。
- `EP008_Tutankhamun_en_v02_subtitled_review_1080p30.mp4`：英語・字幕付き。
- `EP008_Tutankhamun_{{en,ja}}_v02_1080p30.mp4`：字幕なし。
- `EP008_audio_and_subtitles.zip`：英日音声・SRT・v01と同じ発音確認抜粋。
- `EP008_thumbnails_and_metadata.zip`：サムネA〜D・168px比較・英日投稿情報・出典・平均輝度表。
- `EP008_QA_records.zip`：全ショットの比較画像、英日連続デコード画像と検査JSON。
- `EP008_AI_scene_review.zip`：再利用したv01ろうそく原動画。

認証後 `gh api repos/yasukawa1980/youtube/releases/{sharing['release_id']}` で資産IDを確認し、`gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE` で取得する。全ID・SHAは [sharing.json](records/sharing.json)。

## 修正と保持

- カラー4作品をP05/P09/P11/P13へ挿入。C01はフイTT40の1923–27年の模写、C02は王名入り金指輪、C03はペルネブの彩色礼拝室、C04は王名ビーズと護符の首飾り（現代の再連結）。すべてThe MetのPublic Domain画像、Open Access CC0。[候補・選定理由](../research/wom08_追加カラー素材_20261030.md)。
- C01は別墓の模写、C02/C04は同時代の品でKV62出土品ではないことを表示。C03は引用されたヘテプヘルアクティとは別の墓であることを [確認画像](review/C03_other_tomb_label.jpg) に記録。
- 発掘写真10点は同じ単色セピア。元クロップ（3000px以内へ縮小した比較）に対するRec.709平均輝度が **{lo:.3f}〜{hi:.3f}%上昇**。黒≤1／白≥254の画素数は増加なし。完成動画の同区間の全画面平均輝度も **{vlow:.3f}〜{vhigh:.3f}%上昇**し、目安10〜15%内。刊本は紙色を保って約2%明るく、新聞は白黒を維持。
- 図解は砂色地・濃茶文字。金色は保ち、細い縁で判読性を補強。P07は落ち着いた砂色。P10は1869の行から始め、英語「In 1892」の開始で2行目を追加、紙色・質感を変えて各画面を3%ズーム。P11/P13は指定の語りでカラーへ切替。P12の数字25→11は研究対象の説明中に約2秒→5秒で表示（実フレームは検査JSONに保存）。
- **台本v02.1・英日音声・BGM・字幕・全区間時刻・347.566667秒を保持**。v01との音声ストリームSHA一致、SRTバイト一致、台本・マスター時刻JSONもバイト一致。[保持検査](records/episode_specific_qc.json)。OP・END・P14ろうそくはv01と同じ原動画・中間映像。追加生成・購入・支出0。

## 実測検査

- 1920×1080、30fps固定、**10,427フレーム**、H.264 High / yuv420p。全30ショットを個別デコードして非圧縮フレームを単一エンコーダーへ入力。
- 英日字幕なし・字幕付き4本を先頭から末尾までデコードし警告・エラー0。英日本編は全フレーム同一形式、SPS profile_idc=100のみ。各30ショットの先頭・中央・末尾90画像ずつを連続デコードから取得。[検査](records/continuous_qc.json)。
- 英日本編の映像ストリーム同一。音声は両言語ともv01と同一、字幕付きも同じ音声。英日とも **-16.00 LUFS**。
- 動く{len(moving)}ショットの最終動画全隣接フレームで p95÷中央値の最大 **{maxratio:.6f}**（2.5以下）。静止4画面はロスレス中間物の全差分0、D_bmjは意図した数字2回の表示切替を確認。最終動画の差分値は静止画も含めて全件保存し、数値を丸めて0扱いにしていない。[動きの検査](records/final_video_motion.json)。
- 英75／日78字幕を標準・拡大で実描画し、画面本文と非重複。画面本文はズームを含めy≤700。全SRTはv01と一致。[字幕検査](records/subtitle_layout_validation.json)。
- 元資料20点とAI1点は各1ショット。カラー4作品はすべて異なる。P01は0秒からB286。ENDは **337.566667〜347.566667秒**、末尾ちょうど10秒。

## 全ショットのv01→v02比較

v02の各ショットの中央と同じ時刻のv01フレームを比較した。全30ショットの比較は以下の8枚。個別比較30枚もQA ZIPに入っている。

'''
 for j in range(1,9):readme+=f'- [比較 {j}](review/comparison_sheet_{j:02d}.jpg)\n'
 readme+='\n英日それぞれの先頭・中央・末尾一覧：\n\n'
 for l in ['en','ja']:
  for j in range(1,9):readme+=f'- [{l} 一覧{j}](review/continuous_{l}_sheet_{j:02d}.jpg)\n'
 readme+='\n全画面平均輝度は完成動画の全フレームを160×90へ面積平均縮小し、8bitグレーで測定。v01もv02と同じ区間で測定。カラー挿入・文字カードの背景変更を含む値なので、写真クロップの10〜15%目標とは別の実測。OP/ENDは再エンコードの僅差がある。\n\n'+table()
 readme+='\n[CSV](EP008_luminance_v01_v02.csv) ／ [全フレーム測定方法・JSON](records/luminance_comparison.json)。\n\nサムネA〜Dは [168px比較](../サムネ確認用/wom08/wom08_サムネ168px比較_v02_20261030.jpg)。Dはフイの墓の模写を使用し、文言はNOT IN THE TOMB。\n\n## 次の確認\n\n本人：英日全編の映像と明るさ、発音・BGM。Claude：資料の札・別墓の区別・出典・サムネ4案。公開目標11/4 09:00 JSTを維持。YouTube未投稿、Releaseは非公開Draft。\n'
 (dest/'README.md').write_text(readme)
 report=f'''# Quiet Origins 第8話 確認版v02 制作結果（2026-10-30）

**確認版v02を制作し、検査と非公開Draft共有を完了。本人の全編視聴・Claude確認待ち。**

[非公開Draft Release]({sharing['release_url']})、Release ID **{sharing['release_id']}**。英日4動画＋4ZIPの計8資産をRelease ID指定RESTで再取得し、全件サイズ・SHA-256一致、匿名404、Draft維持を確認。

カラー資料4点を追加し、写真10ショットの完成動画の平均輝度を **{vlow:.3f}〜{vhigh:.3f}%** 上げて単色セピアに調整。図解は砂色地、P10は題名の順次表示とズーム、P11/P13はカラーへの切替。サムネはA〜Dの4案。

音声・BGM・字幕はv01と同一（音声ストリームSHAとSRTバイト比較済み）。台本v02.1・区間時刻・総尺 **347.566667秒／10,427フレーム**、OP・END・ろうそく原動画を保持。追加生成・支出0。

全30ショットを個別デコードして単一エンコーダーで組立。英日4本の全編デコード警告・エラー0、本編全フレームの形式1種類。動く{len(moving)}ショットのp95÷中央値は最大 **{maxratio:.6f}**。全ショット比較・平均輝度表・字幕検査・カラー資料の条件は [確認版README](wom08_確認版_v02_20261030/README.md) にまとめた。

- [日本語・字幕付き確認版]({ROOT}/deliverables/EP008_Tutankhamun_ja_v02_subtitled_review_1080p30.mp4)
- [英語・字幕付き確認版]({ROOT}/deliverables/EP008_Tutankhamun_en_v02_subtitled_review_1080p30.mp4)
- [サムネ168px比較](サムネ確認用/wom08/wom08_サムネ168px比較_v02_20261030.jpg)
- [追加カラー資料・選定理由](research/wom08_追加カラー素材_20261030.md)

C01はフイの墓TT40の1923–27年の模写。C02/C04はKV62出土品ではない。C03はペルネブで、引用したヘテプヘルアクティとは別の礼拝室と明示。C04は現代の再連結と表示。

公開目標11/4 09:00 JST。YouTube未投稿、Draft非公開を維持。
'''
 (REPO/'new-channel/wom08_制作結果_v02_20261030.md').write_text(report)
 print('FINALIZED',sharing['release_id'],'motion_max',maxratio,'photos',lo,hi,flush=True)
if __name__=='__main__':main()
