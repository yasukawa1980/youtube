"""v04 review package, private draft and REST byte verification."""
import argparse,csv,hashlib,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom02_revision_v04 import ROOT,PREV,REPO,read,save,sha
from wom02_delivery import api
GH='yasukawa1980/youtube';TAG='wom02-halloween-v04-20261022'
GUIDE=REPO/'new-channel/wom02_確認版_v04_20261022'

def docs():
 for l in ['en','ja']:
  text=(PREV/f'deliverables/EP002_upload_info_{l}.md').read_text()
  text+='\n\n映像v04：H03 D_textsの右側の円を除去し、本の枠のみ表示。オープニングとエンドカードは承認済み共通版（v02と画素一致）へ復元。他の全ショット・音声・SRT・時刻・サムネはv03から維持。新規素材・追加クレジット消費なし。\n'
  (ROOT/f'deliverables/EP002_upload_info_{l}.md').write_text(text)
 player=(PREV/'deliverables/preview.html').read_text().replace('_v03_','_v04_').replace('Halloween v03','Halloween v04').replace('確認版 v03','確認版 v04').replace('素材の重複がない構成、Kling動画6本、新しい再現画をご確認ください。音声・字幕・区間時刻はv02と同一です。','H03は本の枠のみ表示。オープニングとエンドカードは承認済み共通版へ戻しました。音声・字幕・尺・全ショット時刻はv03と同一です。')
 (ROOT/'deliverables/preview.html').write_text(player)
 shutil.copy2(PREV/'deliverables/EP002_asset_usage_v03.csv',ROOT/'deliverables/EP002_asset_usage_v04.csv');save(ROOT/'records/asset_usage_v04.json',read(PREV/'records/asset_usage_v03.json'))
 rows=[]
 for s in read(ROOT/'records/motion_v04.json')['shots']:
  q=s.get('measurement',{});rows.append({'segment':s['segment_id'],'key':s['key'],'excluded':s['excluded'],'median':q.get('median_mad_8bit',''),'p95':q.get('p95_mad_8bit',''),'p95_over_median':q.get('p95_over_median',''),'result':'対象外（承認済み共通ブランド）' if s['excluded'] else '合格'})
 with (ROOT/'deliverables/EP002_motion_v04.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 for n in ['qc_v04.json','frame_identity_v04.json','motion_v04.json','layout_v04.json']:shutil.copy2(ROOT/'records'/n,ROOT/'deliverables'/n)
 shutil.copy2(ROOT/'review/D_texts_v04.jpg',ROOT/'deliverables/H03_D_texts_v04_center.jpg')
 print('DOCS COMPLETE',flush=True)

def selected_files():
 files=sorted((ROOT/'deliverables').iterdir());return [p for p in files if p.name!='SHA256SUMS_shared.txt']

def share():
 qc=read(ROOT/'records/qc_v04.json');assert qc['passed'] and read(ROOT/'records/visual_review_v04.json')['passed'];assert qc['render_shots_sha256']==sha(ROOT/'records/render_shots.json');assert qc['visual_manifest_sha256']==sha(ROOT/'records/visual_manifest.json')
 for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 assert read(ROOT/'records/visual_review_v04.json')['video_sha256']==qc['files'][0]['sha256']
 for n in ['qc_v04.json','frame_identity_v04.json','motion_v04.json','layout_v04.json']:assert sha(ROOT/'deliverables'/n)==sha(ROOT/'records'/n)
 files=selected_files();p=ROOT/'deliverables/SHA256SUMS_shared.txt';p.write_text(''.join(f'{sha(x)}  {x.name}\n' for x in files));files.append(p)
 state=ROOT/'records/sharing_v04.json'
 if state.exists():r=api([f'repos/{GH}/releases/{read(state)["release_id"]}'])
 else:
  r=next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
  if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第2話 ハロウィン v04（図解・ブランド修正）','body':'Claude確認v03の修正1・2を反映。H03は円を外し本の枠のみ。通常版の残り37ショット10,958フレームはv03と画素一致、ブランド720フレームはv02と一致。英日音声・SRT・全時刻・尺397.666667秒・11,930フレーム・サムネ維持。字幕入り版は通常版から再描画した確認用。追加素材の原寸はv03 Draft Release 420277076を参照。新規生成・購入・YouTube投稿・Release公開なし。','draft':True})
 assert r['draft'];save(state,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
 for p in files:
  old=next((a for a in r['assets'] if a['name']==p.name),None)
  if old:assert old['state']=='uploaded' and old['size']==p.stat().st_size and old['digest']=='sha256:'+sha(p)
  else:
   try:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
   except subprocess.CalledProcessError:
    fresh=api([f'repos/{GH}/releases/{r["id"]}']);a=next((a for a in fresh['assets'] if a['name']==p.name),None)
    if not(a and a['state']=='uploaded' and a['size']==p.stat().st_size and a['digest']=='sha256:'+sha(p)):raise
    print('RECOVERED COMPLETED UPLOAD',p.name,flush=True)
  print('UPLOADED',p.name,flush=True)
 r=api([f'repos/{GH}/releases/{r["id"]}']);assert r['draft'];checks=[];assert len(r['assets'])==len(files)
 for p in files:
  a=next(a for a in r['assets'] if a['name']==p.name);proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();count=0
  while True:
   b=proc.stdout.read(1048576)
   if not b:break
   h.update(b);count+=len(b)
  assert proc.wait()==0 and h.hexdigest()==sha(p) and count==p.stat().st_size and a['digest']=='sha256:'+h.hexdigest();checks.append({'name':p.name,'asset_id':a['id'],'bytes':count,'sha256':h.hexdigest(),'rest_download_verified':True});print('REST VERIFIED',p.name,flush=True)
 save(state,{'release_id':r['id'],'draft':True,'status':'verified','release_url':r['html_url'],'assets':checks});print('SHARED',r['id'],len(checks),flush=True)

def export():
 shared=read(ROOT/'records/sharing_v04.json');assert shared['status']=='verified';qc=read(ROOT/'records/qc_v04.json');assert qc['passed']
 for d in ['records','frames','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
 for n in ['qc_v04.json','frame_identity_v04.json','motion_v04.json','layout_v04.json','render_shots.json','visual_manifest.json','preservation_v04.json','visual_review_v04.json','sharing_v04.json','asset_usage_v04.json','master_timeline.json']:shutil.copy2(ROOT/'records'/n,GUIDE/'records'/n)
 for p in (ROOT/'review').glob('*.jpg'):
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,GUIDE/'frames'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.txt','.csv','.html']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
 canonical=REPO/'new-channel/episodes/EP002_Halloween/records'
 for n in ['qc_v04.json','sharing_v04.json']:shutil.copy2(ROOT/'records'/n,canonical/n)
 assets='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in shared['assets'])
 readme=f'''# Quiet Origins 第2話「ハロウィン」v04

**397.666667秒・11,930フレーム・1080p30。** H03の重複する円を外し、ブランドを承認済みの共通版へ復元。

Mac：`{ROOT}`。`deliverables/preview.html` で英日通常版・字幕入り確認版・発音試聴を再生。

[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をRESTで再取得しSHA-256・サイズを照合済み。素材原寸は[v03の取得案内](../wom02_確認版_v03_20261022/README.md)（Release 420277076）を継続利用する。

```sh
gh api repos/{GH}/releases/{shared['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
{assets}

- [H03修正後の中央フレーム](frames/D_texts_v04.jpg)／[変更なしのH08](frames/D_season_v04.jpg)
- [全フレームの画素一致](records/frame_identity_v04.json)／[音声・SRT・尺などの検査](records/qc_v04.json)
- [動きの測定](deliverables/EP002_motion_v04.csv)（本編38件合格、ブランド2件対象外）
- [素材使用一覧](deliverables/EP002_asset_usage_v04.csv)（本編38素材各1回）

画素一致の対象は通常版。字幕入り確認版は同じSRT・スタイルを通常版へ再描画した派生物で、音声はコピー。本人による全編の試聴・生成動画の自然さの確認は引き続き必要。

再現：既存Python環境で `wom02_revision_v04.py prepare → pictures → review → identity → verify → frames`。中央フレームを目視後 `visual_review_v04.json` に記録し、`wom02_v04_delivery.py docs → share → export`。入力は保存済みv03・v02と既存素材。メディア原寸・中間物はGitへ追加しない。
'''
 (GUIDE/'README.md').write_text(readme)
 report=f'''# 第2話「ハロウィン」v04 制作結果（2026-10-22）

[Claude確認v03](wom02_Claude確認_v03_20261022.md)「修正が必要な点」1・2を反映。[再生・取得案内](wom02_確認版_v04_20261022/README.md)。v03は保全。

## 修正内容

1. H03 D_texts（51.066667〜59.466667秒、252フレーム）の右側の円・太陽・Samhain／Winter beginsを除去。本の枠と「8th–12th c.｜8〜12世紀」は位置・大きさを維持。H08 D_seasonは変更なし。[完成動画の中央フレーム](wom02_確認版_v04_20261022/frames/D_texts_v04.jpg)。
2. オープニング38.666667〜42.666667秒（120フレーム）とエンドカード377.666667〜397.666667秒（600フレーム）をv02の承認済み共通版へ復元。ブランド2カットは画像の拡大の動きの基準から除外。

## 検査結果

- 通常版の完成MP4を全フレームデコードし、ブランド計720フレームはv02と画素MD5一致。H03以外の本編37ショット計10,958フレームはv03と全件一致。H03の252フレームは新規描画クリップと全件一致。[全ハッシュとショット別記録](wom02_確認版_v04_20261022/records/frame_identity_v04.json)。
- 英日通常版の圧縮映像ストリームも一致。音声ストリーム・SRT・サムネはv03と一致。全40ショットの開始・終了・フレーム数、マスター時刻表はv03と同一。
- 通常版・字幕入り確認版4本は全編デコード成功。各11,930フレーム、正確な30fps PTS、共通尺397.666667秒。字幕入り版は同一SRT・スタイルで再描画する確認用のため、画素一致の比較対象は通常版とした。
- 本編38ショットのp95÷中央値≤2.5は全件合格。D_textsのみ全フレームで再測定し、他37件は圧縮クリップのSHA-256一致を確認してv03の測定配列を継承。承認済みブランド2件は対象外。[測定一覧](wom02_確認版_v04_20261022/deliverables/EP002_motion_v04.csv)。
- 他37レイアウトと画像はv03と一致。D_textsは文字を削除するのみで既存の文字は移動なし。字幕・文字配置のv03検査を根拠に継承し、削除部分の単色化・本の領域の画素一致を追加検査。
- 素材の追加・再生成なし。利用条件はv03を継承。クレジットの追加消費なし。共通ブランド原本のSHA-256も維持。

本人による全編の動きの自然さ・聴感確認は未実施。Claude確認v03の本人確認項目（Kling動画6本の動き、N12→N13の短い切替、N06の雪景色、発音・話速）は引き続き確認対象。

## 保存と共有

Mac：`{ROOT}`。新規[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。英日通常版・字幕入り確認版・SRT・音声・サムネ・H03中央フレーム・検査JSON等、全{len(shared['assets'])}添付をRelease ID指定のRESTで再取得してSHA-256とサイズを照合済み。添付総量{sum(a['bytes'] for a in shared['assets']):,} bytes。素材原寸は既存v03 Draft Release 420277076を参照。YouTube投稿・Release公開・追加契約・購入なし。
'''
 (REPO/'new-channel/wom02_制作結果_v04_20261022.md').write_text(report);print('EXPORTED',GUIDE,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','export']);a=p.parse_args();globals()[a.stage]()
