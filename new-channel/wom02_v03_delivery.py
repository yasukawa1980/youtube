"""Private draft delivery for v03, with exact REST roundtrip verification."""
import argparse,csv,hashlib,json,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom02_revision_v03 import ROOT,PREV,REPO,read,save,sha
from wom02_delivery import api
GH='yasukawa1980/youtube';TAG='wom02-halloween-v03-20261022';GUIDE=REPO/'new-channel/wom02_確認版_v03_20261022'

def docs():
 motion=read(ROOT/'records/motion_v03.json');assert motion['complete'];rows=[]
 for s in motion['shots']:
  q=s['measurement'];rows.append({'shot':s['shot_index'],'segment':s['segment_id'],'asset_id':s['asset_id'],'start':s['start'],'end':s['end'],'frames':s['frames'],'frame_pairs':q['frame_pairs'],'median':q['median_mad_8bit'],'p95':q['p95_mad_8bit'],'p95_over_median':q['p95_over_median'],'passed':s['passed'],'brand_shot':s['brand_shot']})
 with (ROOT/'deliverables/EP002_motion_v03.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for lang in ['en','ja']:
  text=(PREV/f'deliverables/EP002_upload_info_{lang}.md').read_text();text+='\n\n映像v03：素材は各1ショット。追加：Met All Saints (Greek Painter, possibly 18th century), 31.67.9, CC0 / https://www.metmuseum.org/art/collection/search/436578\nAI静止画：OpenAI image_gen R01–R06、N02/03/05/08/10/11/13/14/15/18。AI動画：Kling AI 3.0 N01/06/09/12/16/17。N04は自作模式図。音声・SRT・共通尺はv02と同一。\n'
  (ROOT/f'deliverables/EP002_upload_info_{lang}.md').write_text(text)
 for a in read(ROOT/'records/ai_images.json')+read(ROOT/'records/new_videos_v03.json'):
  shutil.copy2(a['local_path'],ROOT/'deliverables'/Path(a['local_path']).name)
  for b in a.get('rejected_attempts',[]):shutil.copy2(b['local_path'],ROOT/'deliverables'/Path(b['local_path']).name)
 for a in read(ROOT/'records/new_sources_v03.json'):shutil.copy2(a['original_local_path'],ROOT/'deliverables'/Path(a['original_local_path']).name)
 player=(PREV/'deliverables/preview.html').read_text().replace('_v02_','_v03_').replace('Halloween v02','Halloween v03').replace('確認版 v02','確認版 v03')
 player=player.replace('資料の大きさ、滑らかな動き、H03〜H05の再現画、1938年の写真の札をご確認ください。音声・字幕はv01と同一です。','素材の重複がない構成、Kling動画6本、新しい再現画をご確認ください。音声・字幕・区間時刻はv02と同一です。')
 (ROOT/'deliverables/preview.html').write_text(player);print('DOCS',len(rows),flush=True)

def selected_files():
 d=ROOT/'deliverables';names=[f'EP002_Halloween_{l}_v03_1080p30.{ext}' for l in ['en','ja'] for ext in ['mp4','srt']]
 names += [f'EP002_Halloween_{l}_v03_subtitled_review_1080p30.mp4' for l in ['en','ja']]
 names += [f'EP002_{kind}_{l}.{ext}' for l in ['en','ja'] for kind,ext in [('audio','m4a'),('upload_info','md'),('pronunciation','m4a'),('pronunciation','txt')]]
 names += ['EP002_thumbnail_en.jpg','VOICE_CREDITS.txt','preview.html','EP002_motion_v03.csv','EP002_asset_usage_v03.csv']
 names += [Path(a['local_path']).name for a in read(ROOT/'records/ai_images.json')+read(ROOT/'records/new_videos_v03.json')]
 names += [Path(b['local_path']).name for a in read(ROOT/'records/new_videos_v03.json') for b in a.get('rejected_attempts',[])]
 names += [Path(a['original_local_path']).name for a in read(ROOT/'records/new_sources_v03.json')]
 assert len(names)==len(set(names));return [d/n for n in names]

def share():
 assert read(ROOT/'records/qc_v03.json')['passed'];m=read(ROOT/'records/motion_v03.json');assert m['complete'] and m['all_passed'];assert read(ROOT/'records/asset_usage_v03.json')['passed'];assert read(ROOT/'records/subtitle_layout_validation.json')['passed'];assert read(ROOT/'records/visual_review_v03.json')['passed']
 qc=read(ROOT/'records/qc_v03.json');assert qc['render_shots_sha256']==sha(ROOT/'records/render_shots.json')
 for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 shots=read(ROOT/'records/render_shots.json');assert len(m['shots'])==len(shots)
 for s,q in zip(shots,m['shots']):assert sha(ROOT/s['encoded_file'])==q['encoded_sha256']
 assert read(ROOT/'records/asset_usage_v03.json')['unique_asset_count']==len(read(ROOT/'records/visual_manifest.json')['shots'])
 assert read(ROOT/'records/subtitle_layout_validation.json')['visual_manifest_sha256']==sha(ROOT/'records/visual_manifest.json')
 assert read(ROOT/'records/shot_center_validation.json')['video_sha256']==qc['files'][0]['sha256']
 assert read(ROOT/'records/visual_review_v03.json')['video_sha256']==qc['files'][0]['sha256']
 files=selected_files();p=ROOT/'deliverables/SHA256SUMS_shared.txt';p.write_text(''.join(f'{sha(x)}  {x.name}\n' for x in files));files.append(p)
 state=ROOT/'records/sharing_v03.json'
 if state.exists():r=api([f'repos/{GH}/releases/{read(state)["release_id"]}'])
 else:
  r=next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
  if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第2話 ハロウィン v03（素材重複解消）','body':'本編38素材を各1ショットだけ使用。新規AI静止画10点、Kling動画6本、自作模式図1点、MetのPD作品1点。ブランド2カットも既存デザインを使う一定の拡大へ変更。v02の英日音声・SRT・H01〜H19区間時刻・共通尺397.666667秒・11,930フレームを維持。通常版・字幕入り確認版・使用一覧・全ショット測定表・原寸追加素材を共有。YouTube投稿・Release公開なし。','draft':True})
 assert r['draft'];save(state,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
 for p in files:
  old=next((a for a in r['assets'] if a['name']==p.name),None)
  if old:assert old['digest']=='sha256:'+sha(p)
  else:
   try:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
   except subprocess.CalledProcessError:
    # A successful upload can be followed by a retry's 422 response. Recover only exact bytes.
    fresh=api([f'repos/{GH}/releases/{r["id"]}']);found=next((a for a in fresh['assets'] if a['name']==p.name),None)
    if not(found and found['state']=='uploaded' and found['size']==p.stat().st_size and found['digest']=='sha256:'+sha(p)):raise
    print('RECOVERED COMPLETED UPLOAD',p.name,flush=True)
  print('UPLOADED',p.name,flush=True)
 r=api([f'repos/{GH}/releases/{r["id"]}']);assert r['draft'];checks=[]
 for p in files:
  a=next(a for a in r['assets'] if a['name']==p.name);proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();count=0
  while True:
   b=proc.stdout.read(1048576)
   if not b:break
   h.update(b);count+=len(b)
  assert proc.wait()==0 and h.hexdigest()==sha(p) and count==p.stat().st_size;checks.append({'name':p.name,'asset_id':a['id'],'bytes':count,'sha256':h.hexdigest(),'rest_download_verified':True});print('REST VERIFIED',p.name,flush=True)
 save(state,{'release_id':r['id'],'draft':True,'status':'verified','release_url':r['html_url'],'assets':checks});print('SHARED',r['id'],len(checks),flush=True)

def export():
 shared=read(ROOT/'records/sharing_v03.json');assert shared['status']=='verified';m=read(ROOT/'records/motion_v03.json');qc=read(ROOT/'records/qc_v03.json');use=read(ROOT/'records/asset_usage_v03.json');visual=read(ROOT/'records/visual_review_v03.json');assert m['all_passed'] and qc['passed'] and use['passed'] and visual['passed']
 for d in ['records','frames','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
 names=['master_timeline.json','ai_images.json','new_stills_v03.json','new_videos_v03.json','new_sources_v03.json','preservation.json','visual_manifest.json','render_shots.json','motion_v03.json','source_video_motion.json','brand_revision_v03.json','layout_geometry_v03.json','qc_v03.json','asset_usage_v03.json','subtitle_layout_validation.json','shot_center_validation.json','visual_review_v03.json','sharing_v03.json']
 for n in names:shutil.copy2(ROOT/'records'/n,GUIDE/'records'/n)
 for p in (ROOT/'review').glob('*.jpg'):
  if p.name.startswith(('final_storyboard','subtitles_','source_video_')):assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,GUIDE/'frames'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.txt','.csv','.html']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
 canonical=REPO/'new-channel/episodes/EP002_Halloween/records'
 for n in ['new_stills_v03.json','new_videos_v03.json','new_sources_v03.json','qc_v03.json','sharing_v03.json']:shutil.copy2(ROOT/'records'/n,canonical/n)
 previews=REPO/'new-channel/サムネ確認用/wom02';previews.mkdir(parents=True,exist_ok=True)
 for a in read(ROOT/'records/new_stills_v03.json')+read(ROOT/'records/new_sources_v03.json'):
  im=Image.open(a.get('local_path',a.get('original_local_path'))).convert('RGB');im.thumbnail((1280,1280));p=previews/f'{a["id"]}_素材_v03_確認.jpg';im.save(p,quality=87,optimize=True);assert p.stat().st_size<1000000
 usage='\n'.join(f"| {s['asset_id']} | {s['segment']} | {s['shot']} | {s['start']:.6f} | {s['end']:.6f} | 1 |" for s in use['rows'])
 table='\n'.join(f"| {s['shot_index']} | {s['segment_id']} / {s['key']} | {s['measurement']['median_mad_8bit']:.6f} | {s['measurement']['p95_mad_8bit']:.6f} | {s['measurement']['p95_over_median'] if s['measurement']['p95_over_median'] is not None else '中央値0'} | {'合格' if s['passed'] else '不合格'} |" for s in m['shots'])
 assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in shared['assets'])
 credits=visual['kling_credits_total']
 readme=f'''# Quiet Origins 第2話「ハロウィン」v03

**6分37.666667秒・11,930フレーム・1080p30。** 本編38素材を各1ショットだけ使用。英日音声・SRT・H01〜H19区間時刻はv02と同一。

Mac：`{ROOT}`。`deliverables/preview.html` から英日通常版・字幕入り確認版・発音試聴を選べる。

## Claudeからの取得

[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をRelease ID指定のREST→各Asset IDで再取得し、SHA-256・サイズを照合済み。

```sh
gh api repos/{GH}/releases/{shared['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}

## 検品入口

- [素材ごとの使用一覧](deliverables/EP002_asset_usage_v03.csv)／[検査JSON](records/asset_usage_v03.json)
- [全40ショットの動き](deliverables/EP002_motion_v03.csv)／[差分全配列](records/motion_v03.json)
- [音声・SRT・区間時刻とブランド派生映像](records/qc_v03.json)
- [字幕172件×2サイズの配置検査](records/subtitle_layout_validation.json)
- [中央フレーム一覧1](frames/final_storyboard_1.jpg)／[2](frames/final_storyboard_2.jpg)／[3](frames/final_storyboard_3.jpg)／[4](frames/final_storyboard_4.jpg)
- [全字幕の重ね描き一覧](frames/)
- [追加静止画のプロンプト・SHA](records/new_stills_v03.json)／[Kling動画のプロンプト・消費記録](records/new_videos_v03.json)／[追加PD史料](records/new_sources_v03.json)

N01の採用素材は `N01_Kling_v03_take02.mp4`。`N01_Kling_v03.mp4` は不採用の初回を保全した監査用ファイルで、完成動画には使用していない。

再現：既存Python環境で `wom02_revision_v03.py prepare → visuals → brand → pictures → package → review`。`wom02_v03_qc.py usage → motion → verify`、`wom02_v03_review.py layout → frames`。確認後 `wom02_v03_delivery.py docs → share → export`。v02・原寸素材が入力として必要。原寸素材をGitへ追加しない。
'''
 (GUIDE/'README.md').write_text(readme)
 report=f'''# 第2話「ハロウィン」v03 制作結果（2026-10-22）

[v03修正依頼](wom02_修正依頼_v03_20261022.md)を反映。[再生・Claude取得・検品入口](wom02_確認版_v03_20261022/README.md)。v02は保全。

## 変更内容

本編38素材をそれぞれ1ショットに限定した。全体＋部分拡大は同一ショット内の2枠で表示し、D_trailと縮小資料の再使用を廃止。H15・H16は3ショット、H18は1ショットへ変更。H15のカブの説明にかぼちゃが重ならないよう、新規のカブ再現画N18を286.666667秒まで配置し、その後N12→N13を各1回表示する。N12は10秒素材の冒頭4.666667秒を等速で使用。H16のA07は318.000秒開始を維持し、英日とも1927年の新聞の説明後に1938年の写真へ移る。

追加はAI静止画10点（N02/03/05/08/10/11/13/14/15/18）、Kling AI動画6本（N01/06/09/12/16/17）、自作模式図N04、Metの別作品N07。生成素材には編集で `AI RECONSTRUCTION｜AIによる再現` を付けた。N04はAI生成ではなく `SCHEMATIC｜模式図` と明記。v02の資料サイズ・小数座標の滑らかな拡大・上部の札と出典を継承した。

Kling：10秒・1080p・16:9・無音、1回80クレジット。消費計 **{credits}クレジット**。N01初回は原寸のp95/中央値3.1315で不合格として不採用、再生成の履歴を台帳に残した。既存残高内で実行し、契約変更・追加購入なし。UI上は「プロ」と表示されており、依頼文のStandardと名称が異なるため現在のプラン名は断定しない。生成元24fpsを光学フロー補間して30fps化し、同じ1ショット内で尺に合わせて再生（N12は冒頭を等速で抜粋）。末尾は補間の端を埋める短い保持を含む。H18は10秒素材を13.7秒へ伸ばし、ループや同素材の別ショットを作っていない。

## 追加史料の利用条件

N07：[Met「All Saints」](https://www.metmuseum.org/art/collection/search/436578)、Greek Painter、possibly 18th century、31.67.9。作品ページにPublic Domain、公式APIのisPublicDomain=true、[画像方針](https://www.metmuseum.org/policies/image-resources)にCC0を確認。商用利用・トリミング可。後世の聖人像の例として使い、中世の出来事の同時代史料とは扱わない。原寸のSHA-256・取得URLは台帳へ保存。

N11はキルマーノック版等の候補を検索したが、今回の確認範囲で所蔵館のPD/CC0明記と画像取得をそろえられず、依頼指定の古い詩集の再現画へ代替。N13の候補[NYPL「On Hallowe'en」](https://old-digitalcollections.nypl.org/items/510d47e3-4771-a3d9-e040-e00a18064a99)は権利状態を確定できない旨の表示があり不採用。別のPD候補も題材適合を確定できず、ランタンの再現画を採用した。非商用・CC BY-SAの画像は採用していない。

## 同一性・配置検査

- 通常版・字幕入り版4本は全編デコード成功。11,930フレーム、正確な30fps PTS、共通尺397.666667秒。
- 英日通常版の映像ストリームは同一。各言語の音声ストリームとSRTはv02とSHA-256一致。再合成・再正規化なし。
- 全19区間の開始・終了はv02と同一。ブランドのロゴ・文字のデザインはv02から取得し、EP002内だけ一定の3%拡大へ変更。派生した720フレームが完成MP4内で画素ハッシュ一致。共通ブランド原本は変更せず、サムネもバイト一致。
- 全40ショットの中央フレーム一覧を保存。図解・クレジット文字y≤700、写真・AIの札と出典はy<100。全172字幕×FontSize14/26の344描画を実動画フレームへ重ね、文字との重複がないことを検査。
- 追加静止画10点を確認し、動画6本は各6時点の時系列フレームを目視確認。全フレームの数値検査も実施。人の顔や手が動く生成動画は使っていない。本人による全編の動きの自然さ・聴感確認は未実施。

## 素材ごとの使用回数

同じ素材の全体・拡大を同じショットに並べる場合は1回として計数。ぼかし背景もそのショット内だけ。クレジットは素材IDを文字で列挙するだけで画像を再掲しない。ブランドのオープニング・エンドカードと動画外のサムネは別枠。

| 素材ID | 区間 | 全体ショット番号 | 開始秒 | 終了秒 | 回数 |
|---|---|---:|---:|---:|---:|
{usage}

## 全ショットの動き

{m['method']}

本編38＋ブランド2＝全40ショットの合否：**{'全件合格' if m['all_passed'] else '未合格あり'}**。全フレーム差分配列をJSONに保存し、比率をよく見せるためのサンプル除去や時間方向の平滑化は測定に行っていない。動画の光学フロー補間は編集処理として明記した。

ブランド2カットは、v02のフェードをそのまま測るとオープニング9.2006・エンドカード6.0438で基準を超えた。全ショット条件に合わせ、同じロゴ・文字のデザインを保った1枚から一定のゆっくりした拡大へ調整し、2カットとも基準内になった。音声・尺・切り替え時刻・共通ブランド原本は変更していない。

| # | 区間／素材 | 中央値 | p95 | p95÷中央値 | 判定 |
|---:|---|---:|---:|---:|---|
{table}

## 保存・共有

Mac：`{ROOT}`。新規[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をRelease ID指定のRESTで再取得してSHA-256・サイズ照合済み。YouTube投稿・Release公開なし。プロンプト・生成日・サービス名・SHA・消費クレジットを保存し、原寸はMacとDraft、Gitにはスクリプト・台帳・縮小確認JPGだけを置いた。
'''
 (REPO/'new-channel/wom02_制作結果_v03_20261022.md').write_text(report);print('EXPORTED',GUIDE,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','export']);a=p.parse_args();globals()[a.stage]()
