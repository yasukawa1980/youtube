"""Share picture-only v02 as a new private draft and export reproducible review records."""
import argparse,csv,hashlib,html,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom02_revision_v02 import ROOT,PREV,REPO,MEDIA,read,save,sha
from wom02_delivery import api
GH='yasukawa1980/youtube';TAG='wom02-halloween-v02-20261022';GUIDE=REPO/'new-channel/wom02_確認版_v02_20261022'

def docs():
 motion=read(ROOT/'records/motion_comparison.json');assert motion['complete']
 rows=[]
 for s in motion['shots']:
  rows.append({'shot':s['shot_index'],'segment':s['segment_id'],'v01_key':s['before_key'],'v02_key':s['after_key'],'start':s['start'],'end':s['end'],'v01_median':s['before']['median_mad_8bit'],'v01_p95':s['before']['p95_mad_8bit'],'v01_ratio':s['before']['p95_over_median'],'v02_median':s['after']['median_mad_8bit'],'v02_p95':s['after']['p95_mad_8bit'],'v02_ratio':s['after']['p95_over_median'],'passed':s['passed']})
 with (ROOT/'deliverables/EP002_motion_comparison_v02.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for lang in ['en','ja']:
  text=(PREV/f'deliverables/EP002_upload_info_{lang}.md').read_text().replace('確認版v01','確認版v02').replace('R01–R03','R01–R06')
  text+='\n映像v02：小数座標補間、資料の大型化、R04〜R06追加。音声・SRT・共通尺はv01と同一。\n'
  (ROOT/f'deliverables/EP002_upload_info_{lang}.md').write_text(text)
 for a in read(ROOT/'records/ai_images.json'):shutil.copy2(a['local_path'],ROOT/'deliverables'/Path(a['local_path']).name)
 player=(PREV/'deliverables/preview.html').read_text().replace('_v01_','_v02_').replace('Halloween v01','Halloween v02').replace('確認版 v01','確認版 v02')
 player=player.replace('最初に英語Samhainの発音、英日の冒頭からロゴへの流れ、日本語の固有名詞をご確認ください。','資料の大きさ、滑らかな動き、H03〜H05の再現画、1938年の写真の札をご確認ください。音声・字幕はv01と同一です。')
 (ROOT/'deliverables/preview.html').write_text(player)
 print('DOCS',len(rows),'motion rows',flush=True)

def selected_files():
 d=ROOT/'deliverables';names=[f'EP002_Halloween_{l}_v02_1080p30.{ext}' for l in ['en','ja'] for ext in ['mp4','srt']]
 names += [f'EP002_Halloween_{l}_v02_subtitled_review_1080p30.mp4' for l in ['en','ja']]
 names += [f'EP002_{kind}_{l}.{ext}' for l in ['en','ja'] for kind,ext in [('audio','m4a'),('upload_info','md'),('pronunciation','m4a'),('pronunciation','txt')]]
 names += ['EP002_thumbnail_en.jpg','VOICE_CREDITS.txt','preview.html','EP002_motion_comparison_v02.csv']+[Path(a['local_path']).name for a in read(ROOT/'records/ai_images.json')]
 return [d/x for x in names]

def share():
 assert read(ROOT/'records/qc_v02.json')['passed'];m=read(ROOT/'records/motion_comparison.json');assert m['complete'] and m['all_passed'];assert read(ROOT/'records/subtitle_layout_validation.json')['passed']
 files=selected_files();p=ROOT/'deliverables/SHA256SUMS_shared.txt';p.write_text(''.join(f'{sha(x)}  {x.name}\n' for x in files));files.append(p)
 state=ROOT/'records/sharing_v02.json'
 if state.exists():r=api([f'repos/{GH}/releases/{read(state)["release_id"]}'])
 else:
  r=next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
  if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第2話 ハロウィン v02（映像修正）','body':'v01を保全した映像修正版。資料大型化、小数座標補間、R04〜R06追加、1938年の札を上部へ移動。音声・SRT・尺397.666667秒・11,930フレーム・全39ショット境界はv01と同一。全37本編ショットのフレーム差分p95/中央値≤2.5を確認。通常版・字幕入り確認版・比較CSV・再現画を共有。YouTube投稿・Release公開なし。','draft':True})
 assert r['draft'];save(state,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
 for p in files:
  old=next((a for a in r['assets'] if a['name']==p.name),None)
  if old:assert old['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
  print('UPLOADED',p.name,flush=True)
 r=api([f'repos/{GH}/releases/{r["id"]}']);assert r['draft'];checks=[]
 for p in files:
  a=next(a for a in r['assets'] if a['name']==p.name);proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();count=0
  while True:
   block=proc.stdout.read(1048576)
   if not block:break
   h.update(block);count+=len(block)
  assert proc.wait()==0 and h.hexdigest()==sha(p) and count==p.stat().st_size;checks.append({'name':p.name,'asset_id':a['id'],'bytes':count,'sha256':h.hexdigest(),'rest_download_verified':True});print('REST VERIFIED',p.name,flush=True)
 save(state,{'release_id':r['id'],'draft':True,'status':'verified','release_url':r['html_url'],'assets':checks});print('SHARED',r['id'],len(checks),flush=True)

def export():
 shared=read(ROOT/'records/sharing_v02.json');assert shared['status']=='verified';m=read(ROOT/'records/motion_comparison.json');qc=read(ROOT/'records/qc_v02.json');assert m['all_passed'] and qc['passed']
 for d in ['records','frames','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
 recordnames=['master_timeline.json','ai_images.json','preservation.json','visual_manifest.json','render_shots.json','motion_comparison.json','qc_v02.json','subtitle_layout_validation.json','shot_center_validation.json','visual_review_v02.json','sharing_v02.json']
 for n in recordnames:shutil.copy2(ROOT/'records'/n,GUIDE/'records'/n)
 for p in (ROOT/'review').glob('*.jpg'):
  if p.name.startswith(('final_storyboard','subtitles_')):assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,GUIDE/'frames'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.txt','.csv','.html']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
 canonical=REPO/'new-channel/episodes/EP002_Halloween/records'
 for n in ['ai_images.json','motion_comparison.json','qc_v02.json','sharing_v02.json']:shutil.copy2(ROOT/'records'/n,canonical/(Path(n).stem+'_v02.json' if n=='ai_images.json' else n))
 for a in read(ROOT/'records/ai_images.json'):
  if a['id'] not in ['R04','R05','R06']:continue
  im=Image.open(a['local_path']).convert('RGB');im.thumbnail((1280,1280));im.save(REPO/f'new-channel/サムネ確認用/wom02/{a["id"]}_再現画_確認.jpg',quality=87,optimize=True)
 table='\n'.join(f"| {s['shot_index']} | {s['segment_id']} / {s['before_key']} → {s['after_key']} | {s['before']['median_mad_8bit']:.4f} | {s['before']['p95_mad_8bit']:.4f} | {s['before']['p95_over_median']:.3f} | {s['after']['median_mad_8bit']:.4f} | {s['after']['p95_mad_8bit']:.4f} | {s['after']['p95_over_median']:.3f} |" for s in m['shots'])
 assettable='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in shared['assets'])
 readme=f'''# Quiet Origins 第2話「ハロウィン」v02

映像修正版。**6分37.666667秒・11,930フレーム・1080p30**。音声・SRT・尺・切り替え時刻・共通映像・サムネはv01と同一。

Mac：`{ROOT}`。`deliverables/preview.html` から英日字幕入り版・通常版・発音試聴を選べる。

## Claudeからの取得

[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をREST再取得してSHA-256・サイズを照合済み。

```sh
gh api repos/{GH}/releases/{shared['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assettable}

## 検査と画像

- [全37ショットの動きの測定](records/motion_comparison.json)／[比較CSV](deliverables/EP002_motion_comparison_v02.csv)
- [音声・字幕・時刻の同一性](records/qc_v02.json)
- [全字幕の配置検査](records/subtitle_layout_validation.json)
- [全ショット一覧1](frames/final_storyboard_1.jpg)／[2](frames/final_storyboard_2.jpg)／[3](frames/final_storyboard_3.jpg)／[4](frames/final_storyboard_4.jpg)
- [全字幕2サイズの重ね描き一覧](frames/)
- [再現画R01〜R06、実行プロンプト、SHA-256](records/ai_images.json)

## 再現手順

v01と同じPython環境・依存関係。原寸R04〜R06はこのDraftからMac素材フォルダへ保存。`wom02_revision_v02.py prepare → visuals → pictures → package → review`、`wom02_v02_qc.py motion → verify`、`wom02_v02_review.py layout → frames`。検査後 `wom02_v02_delivery.py docs → share → export`。v01の出力フォルダは読み取り専用の入力として使う。YouTube投稿・Release公開は行わない。
'''
 (GUIDE/'README.md').write_text(readme)
 report=f'''# 第2話「ハロウィン」v02 制作結果（2026-10-22）

[修正依頼](wom02_修正依頼_v02_20261022.md)を反映した映像修正版。[再生・Claude取得・検品入口](wom02_確認版_v02_20261022/README.md)。v01は保全。

## 反映内容

1. 整数画素を刻むzoompanを、小数座標のcubic perspective補間へ変更。本編の画像とぼかし背景を同じ変換で動かし、札・出典は固定。通常の拡大幅3%。H02は4資料を順に見せる連続した小数座標の横移動。
2. 資料を最大1760×820px（x80〜1840、y110〜930）へ拡大。detailは860×820pxの2枠。縦横比を保ち、元画像の1.5倍を上限に配置。上部の文字はy<100。図解・クレジットの文字はy≤700。
3. R01はH01だけ。H02はD_trail、H03はR04→D_texts、H04はR05→R06、H05はD_story_record→R04の別トリミング。元の2ショットの境界はすべて維持。AI画像追加に伴いクレジットの素材ID範囲をR01〜R06へ更新。
4. A07の1938年・米国カリフォルニアを上部の出典行へ移動。写真内のネガ番号と重ならない。

## 同一性と技術検査

- 英日通常版の映像ストリームは同一。通常版・字幕入り版の4本とも全編デコードと正確な30fps PTSを確認。
- 各言語の音声ストリームSHA-256はv01と同一。主音声M4A・発音試聴M4Aもバイト一致でコピー。再合成・再正規化なし。
- 英85・日87件のSRTはv01とバイト一致。共通尺397.666667秒、11,930フレーム、全39ショットの開始・終了・フレーム数が同一。
- オープニング120フレーム＋エンドカード600フレームの計720フレームは、完成MP4から全フレームを抽出してv01との画素ハッシュ一致を確認。サムネもバイト一致。
- 全172字幕×FontSize14／26の344描画をv02の実動画フレームに重ねた一覧を保存。文字・図との重複なし。資料画像との重なりは依頼どおり許容。

## 動きの比較

**全37本編ショットが、p95÷中央値 ≤2.5 を満たした。基準を超えるショットは0件。**

方法：{m['method']}

v01とv02で同じ計算方法を使い、拡大前後の資料位置に合わせてROIを選んだ。再現画を入れ替えた場面は画像内容も異なるため、絶対差分の大小そのものを品質差とは扱わず、各版の時間的な跳びの比率を見る。元の39ショットのうち、引き継いだブランド映像2ショットはこのカメラ動作の検査対象外。全フレームの差分配列はJSONに保存。

| # | 区間／素材 v01→v02 | v01中央値 | v01 p95 | v01比率 | v02中央値 | v02 p95 | v02比率 |
|---:|---|---:|---:|---:|---:|---:|---:|
{table}

## 共有と確認

Mac：`{ROOT}`。新規[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付のREST再取得・ハッシュ一致を確認。原寸R04〜R06はMacとDraftへ保存し、Gitには縮小JPG・プロンプト・台帳のみを置く。

全ショット中央フレーム一覧を目視し、資料の大きさ、R01の使用区間、新しい再現画の札、A07の札の位置を確認。本人には、動画での動きの自然さと資料の大きさを確認してほしい。音の新規聴感評価は行っていない。追加契約・購入、YouTube投稿、Release公開はなし。
'''
 (REPO/'new-channel/wom02_制作結果_v02_20261022.md').write_text(report)
 print('EXPORTED',GUIDE,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','export']);a=p.parse_args();globals()[a.stage]()
