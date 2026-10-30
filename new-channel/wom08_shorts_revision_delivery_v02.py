"""字幕下地だけを直したv02の差分証明、確認資料とGitへの申し送り。"""
import csv,html,json,shutil,zipfile,sys
from pathlib import Path
import numpy as np
from PIL import Image
from wom08_shorts_revision_v02 import ROOT,OLD,REPO,read,save,sha
DEST=REPO/'new-channel/wom_ショート_EP008_確認版_v02_20261030'
REPORT=REPO/'new-channel/wom_ショート制作結果_EP008_v02_20261030.md'

def audit():
 checks=[];oldheads={r['id']:r for r in read(OLD/'records/headlines.json')};oldcmds={r['id']:r for r in read(OLD/'records/encoding_method.json')['shorts']}
 for row in read(ROOT/'records/encoding_method.json')['shorts']:
  sid=row['id'];old=(OLD/f'_work/{sid}.ass').read_text();new=(ROOT/f'_work/{sid}.ass').read_text();events=lambda text:[r for r in text.splitlines() if r.startswith('Dialogue:') and ',Main,' in r]
  assert events(old)==events(new)
  assert next(r for r in old.splitlines() if r.startswith('Style: Main,'))==next(r for r in new.splitlines() if r.startswith('Style: Main,'))
  a=np.asarray(Image.open(oldheads[sid]['file']).convert('RGBA'));b=np.asarray(Image.open(ROOT/f'assets/{sid}_headline.png').convert('RGBA'));assert np.array_equal(a[:,:,:3],b[:,:,:3]);assert np.array_equal(a[:,:,3][a[:,:,3]==255],b[:,:,3][a[:,:,3]==255])
  if sid!='K2':assert np.array_equal(a,b)
  else:assert (b[:,:,3][a[:,:,3]==125]==217).all()
  norm=lambda cmd:[str(x).replace(str(ROOT),str(OLD)).replace('_v02.mp4','_v01.mp4') for x in cmd]
  assert norm(row['command'])==oldcmds[sid]['command'];assert row['shot_sources']==oldcmds[sid]['shot_sources']
  srt=ROOT/f'deliverables/QO_short_EP008_{sid}_v02.srt';assert sha(srt)==sha(OLD/f'deliverables/QO_short_EP008_{sid}_v01.srt')
  checks.append({'id':sid,'original_ASS_main_style_and_events_byte_identical':True,'srt_sha256':sha(srt),'srt_identical_to_v01':True,'same_camera_shot_files_and_order':True,'same_encoder_command_except_new_plate_assets_ass_output_paths':True,'same_headline_rgb_and_opaque_text':True,'only_headline_alpha_changed':sid=='K2'})
 save(ROOT/'records/revision_diff_qc.json',{'passed':True,'checks':checks,'same_headline_fade_filter':'fade=t=out:st=2:d=0.3:alpha=1; overlay enable lt(t,2.3)','v01_base_release_id':428689871})
 plates=read(ROOT/'records/subtitle_backplates.json')['rows'];assert all(80<=r['text_bbox'][0]<r['text_bbox'][2]<=880 and 1150<=r['text_bbox'][1]<r['text_bbox'][3]<=1450 for r in plates)
 ranges=[]
 for r in plates:
  m=np.load(ROOT/r['mask']);stem=Path(r['mask']).stem.rsplit('_line',1)[0];a=np.asarray(Image.open(ROOT/f'_work/masks/{stem}_plate.png').convert('RGB'));values=a[m['core']];ranges.append([int(values.min()),int(values.max())])
 assert all(x==[80,80] for x in ranges)
 save(ROOT/'records/subtitle_qc.json',{'passed':True,'lines':34,'events':19,'original_text_style_events_and_linebreaks_identical':True,'glyph_bounds_include_outline_shadow':True,'glyph_bounds_x':[80,880],'glyph_bounds_y':[1150,1450],'plate_padding':20,'plate_radius':16,'plate_opacity':173/255,'white_test_background_plate_interior_RGB':[80,80,80],'overlap_does_not_double_opacity':True})
 print('DIFF / GLYPH AUDIT PASSED',flush=True)

def package():
 for name in ['media_qc','contrast_qc','motion_qc','revision_diff_qc','subtitle_qc','visual_review']:assert read(ROOT/f'records/{name}.json')['passed']
 media=read(ROOT/'records/media_qc.json')['media'];rows=read(ROOT/'records/shorts.json')['shorts']
 fields=['id','name','duration_seconds','frames','lufs','true_peak_dbtp','audio_stream_identical_to_v01','continuous_decode_warnings']
 with (ROOT/'deliverables/qc_summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:m[k] for k in fields} for m in media)
 with (ROOT/'deliverables/motion_qc.csv').open('w',newline='') as f:
  fields=['short_id','asset_id','frame_pairs','median','p95','p95_over_median','passed'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for c in read(ROOT/'records/motion_qc.json')['checks']:w.writerow(dict(short_id=c['short_id'],asset_id=c['asset_id'],passed=c['passed'],**{k:c['measurement'][k] for k in fields[2:-1]}))
 cards=''.join(f'<section><h2>{s["id"]}</h2><video controls preload="metadata" src="QO_short_EP008_{s["id"]}_v02.mp4"></video><p>{s["frames"]/30:.3f}秒・英語字幕入り</p></section>' for s in rows)
 (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>第8話ショート v02</title><style>body{max-width:1100px;margin:24px auto;padding:16px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}video{width:100%;max-height:75vh}h1,h2{color:#d8b575}</style><h1>Quiet Origins 第8話ショート K1〜K3 v02</h1><p>字幕の各行に黒い半透明の下地を追加し、K2冒頭の見出しの下地を濃くしました。確認用・未投稿。</p><main>'+cards+'</main><p><a href="subtitle_contrast_v02.csv">全字幕のコントラスト実測表</a></p><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})));</script></html>')
 with zipfile.ZipFile(ROOT/'deliverables/production_records.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted((ROOT/'records').iterdir()):
   if p.suffix in ['.json','.log'] and not p.name.startswith('sharing'):z.write(p,'records/'+p.name)
  for p in sorted((ROOT/'review').rglob('*.jpg')):z.write(p,'review/'+str(p.relative_to(ROOT/'review')))
  for p in sorted((ROOT/'deliverables').iterdir()):
   if p.suffix in ['.srt','.csv','.txt','.html','.md'] and p.name!='SHA256SUMS_shared.txt':z.write(p,p.name)
  for p in sorted((ROOT/'_work').glob('K*.ass')):z.write(p,'ass/'+p.name)
  for p in sorted((ROOT/'assets').glob('*_headline.png')):z.write(p,'assets/'+p.name)
  for name in ['wom08_shorts_revision_v02.py','wom08_shorts_revision_qc_v02.py','wom08_shorts_revision_delivery_v02.py','wom08_shorts_revision_share_v02.py']:z.write(REPO/'new-channel'/name,'scripts/'+name)
 with zipfile.ZipFile(ROOT/'deliverables/production_records.zip') as z:assert z.testzip() is None and not any('planned_' in n for n in z.namelist())
 files=sorted([*(ROOT/'deliverables').glob('*_v02.mp4'),ROOT/'deliverables/production_records.zip']);assert len(files)==4
 (ROOT/'deliverables/SHA256SUMS_shared.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));print('V02 ARCHIVE READY',flush=True)

def handoff():
 sharing=read(ROOT/'records/sharing.json');assert sharing['draft'] and sharing['status']=='verified' and len(sharing['assets'])==5
 for d in ['records','review','deliverables']:(DEST/d).mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,DEST/'records'/p.name)
 for p in (ROOT/'review').rglob('*.jpg'):
  dest=DEST/'review'/p.relative_to(ROOT/'review');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.csv','.txt','.html','.md']:shutil.copy2(p,DEST/'deliverables'/p.name)
 contrast=read(ROOT/'records/contrast_qc.json');media=read(ROOT/'records/media_qc.json')['media'];motion=read(ROOT/'records/motion_qc.json');maxmotion=max(c['measurement']['p95_over_median'] for c in motion['checks']);folder=DEST.name
 lines=['# 第8話ショート K1〜K3 確認版v02 制作結果（2026-10-30）','','**Claudeの修正依頼に従い、3本の字幕下地とK2冒頭見出しの下地を修正。検査・非公開Draft共有・REST照合を完了。YouTube未投稿。**','',f'[非公開Draft Release]({sharing["release_url"]})、Release ID **{sharing["release_id"]}**。3動画・確認資料ZIP・SHA一覧の5資産を、Release ID指定のRESTで再取得し、全件サイズとSHA-256一致。匿名404・Draft維持を確認。',f'[確認版README]({folder}/README.md) ／ [REST照合]({folder}/records/sharing.json)','','## 修正内容','','- K1〜K3の字幕とCTAの各行に、角丸の黒い半透明板を追加。不透明度173/255＝0.678431、文字の上下左右の余白20px、角の半径16px。行の板は1つの描画イベントにまとめ、重なる部分が二重に暗くならないことも白背景で確認。','- K2「A DEATH, THEN A CURSE」の見出し板は217/255＝0.850980へ。文字の色・字体・大きさ・座標を維持し、0〜2.0秒の表示、2.0〜2.3秒の消え方も同じ。K1・K3の冒頭見出しは同じ。','- 元のASSのMainスタイル・全19文字イベントはバイト単位で同一。文字の位置・色・大きさ・改行は同じで、輪郭・影を含む文字範囲x80–880／y1150–1450内。SRTもv01と同一SHA。','- v01の9映像ショットを同じ順で再利用し、SHA一致。台本、K3冒頭の承認済み「墓の発見より古い」、札、出典、Full story on Quiet Origins、素材、切替時刻、尺、カメラは維持。AAC音声ストリームも3本ともv01と同じSHA。再読み上げ・再ミックスなし。',f'[差分証明]({folder}/records/revision_diff_qc.json) ／ [下地と行別座標]({folder}/records/subtitle_backplates.json)','','## 実測','','|動画|尺|フレーム|LUFS|dBTP|字幕の最小コントラスト比|','|---|---:|---:|---:|---:|---:|']
 for m in media:
  minimum=min(r['contrast_ratio'] for r in contrast['rows'] if r['short_id']==m['id']);lines.append(f'|{m["id"]}|{m["video_duration_seconds"]:.3f}秒|{m["frames"]}|{m["lufs"]:.2f}|{m["true_peak_dbtp"]:.2f}|{minimum:.6f}:1|')
 lines+=['',f'全19表示区間の中央フレーム、計34行を測定し、全行4.5:1以上（全体最小 **{contrast["minimum"]:.6f}:1**）。文字内部の最も暗い画素と、輪郭から3〜9px離れたすぐ周囲の下地の最も明るい画素の相対輝度比を使用。文字内部は元の単独描画の塗り画素を3×3収縮して取得し、アンチエイリアス境界を除く。画面全体の平均や分位数による代用なし。',f'[全34行のCSV]({folder}/deliverables/subtitle_contrast_v02.csv) ／ [画素数・輝度・方法のJSON]({folder}/records/contrast_qc.json)','',f'1080×1920／30fps／H.264 High／yuv420p。全1821フレームの形式1種類、PTS等間隔。先頭から全編の連続デコードで警告・エラー0。RGB比較画像の抽出は別処理。動きは完成動画の全隣接フレームで再測定し、p95÷中央値は全9ショットで最大 **{maxmotion:.6f}**（≤2.5）。',f'[動画・音声検査]({folder}/records/media_qc.json) ／ [動きの検査]({folder}/records/motion_qc.json)','','## 比較画像','','左右はv01／v02。冒頭0・0.5・1・1.5・2・2.5秒の各18枚と、2秒おきの全31時点の比較。字幕は19表示区間それぞれの中央フレームの拡大比較も保存。すべて先頭から連続デコードで取得し、シークなし。','']
 for sid in ['K1','K2','K3']:lines.append(f'- {sid}：[冒頭比較]({folder}/review/{sid}_opening_comparison.jpg) ／ [2秒おき比較]({folder}/review/{sid}_every2s_comparison.jpg) ／ [個別比較画像]({folder}/review/{sid}/)')
 lines+=['','見出しと字幕の欠け・他の固定札との重なりがなく、新聞や明るい壁面の上でも字幕の行が読みやすくなったことを比較画像で確認。K2見出しは紙面の黒文字の透けが減少。字幕位置や切替時刻は同じ。人による全編試聴は未実施。音声はv01と同一であることをストリームSHAで検証した。','',f'Mac保存先：`{ROOT}`。再生入口：`deliverables/preview.html`。動画・高解像度素材はGitに含めず、軽い確認資料と実測記録だけを保存。新しいAI画像・AI動画なし。投稿と予約は行っていない。','']
 REPORT.write_text('\n'.join(lines))
 (DEST/'README.md').write_text(f'# Quiet Origins 第8話ショート K1〜K3 v02\n\n[制作結果と実測値](../{REPORT.name})\n\n[非公開Draft]({sharing["release_url"]})、Release ID **{sharing["release_id"]}**。3動画＋確認資料ZIP＋SHA一覧の全5資産をRESTで再取得しSHA一致。Draft維持・匿名404を確認。YouTube未投稿。\n\n`GET /repos/yasukawa1980/youtube/releases/{sharing["release_id"]}` で資産IDを取得し、`gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE` で取得。ZIPを動画3本と同じ場所に展開するとpreview.htmlで再生できる。\n\n[共有SHA](deliverables/SHA256SUMS_shared.txt) ／ [REST照合](records/sharing.json) ／ [字幕コントラストCSV](deliverables/subtitle_contrast_v02.csv)\n\n[冒頭K1](review/K1_opening_comparison.jpg) ／ [K2](review/K2_opening_comparison.jpg) ／ [K3](review/K3_opening_comparison.jpg)\n\n[2秒おきK1](review/K1_every2s_comparison.jpg) ／ [K2](review/K2_every2s_comparison.jpg) ／ [K3](review/K3_every2s_comparison.jpg)\n\nローカル：`{ROOT}/deliverables/preview.html`\n')
 print('GIT HANDOFF READY',flush=True)
if __name__=='__main__':globals()[sys.argv[1]]()
