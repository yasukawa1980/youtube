"""EP008ショートの確認資料、非公開共有向けZIP、Git用報告。投稿は別依頼。"""
import csv,hashlib,html,json,shutil,zipfile,sys
from pathlib import Path
from wom08_shorts_render import ROOT,REQUEST,read,save,sha,FPS,VERSION
from wom08_shorts import REPO
DEST=REPO/'new-channel/wom_ショート_EP008_確認版_v01_20261030'

def review():
 for name in ['media_qc','subtitle_qc','motion_qc','asset_usage','safe_crop_qc','headline_qc']:assert read(ROOT/f'records/{name}.json')['passed']
 media=read(ROOT/'records/media_qc.json')['media']
 save(ROOT/'records/visual_review.json',{'passed':True,'video_sha256':{m['id']:m['sha256'] for m in media},'inspected':'最終MP4の0/0.5/1/1.5/2/2.5秒の18枚、2秒おきの全3本の一覧、および資料の原画像。','findings':['冒頭見出しは3本とも字が欠けず、札・字幕と非重複。2.0〜2.3秒で消える。','K1は封鎖扉と右側の守護像を縦に切り出し、像の頭部を残す。杯→刊本p258で終わる。','K2はN03の見出し全体を残す。N02は同じ記事内のドイル説とバッジの反論を2つの抜粋で提示。N01は見出しの段だけ。顔写真・事故の大見出しなし。','K3は1923–27年の模写、フイTT40の別墓でKV62でない札を維持。1869カードは本編v03の文字の画素を縦に並べ替え、1892行を含めない。','K3は最後にB157階段へ切り替え、3本とも最後まで絵か紙面が残る。','字幕は承認済みの台本と一致し、各行4〜5語、最大2行。年号だけの画面なし。'],'human_full_listening':False,'ai_visual_assets_used':False,'new_visual_generation':False,'K3_script_approval':read(ROOT/'records/script_approval.json')})

def docs():
 assert read(ROOT/'records/visual_review.json')['passed'];rows=read(ROOT/'records/shorts.json')['shorts'];pages=read(ROOT/'records/caption_manifest.json');media=read(ROOT/'records/media_qc.json')['media']
 def stamp(n):
  ms=round(n/FPS*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for s in rows:
  stem=f'QO_short_EP008_{s["id"]}_{VERSION}';pp=[p for p in pages if p['short_id']==s['id']]
  (ROOT/f'deliverables/{stem}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(p["start_frame"])} --> {stamp(p["end_frame"])}\n'+'\n'.join(p['lines']) for i,p in enumerate(pp))+'\n')
 (ROOT/'deliverables/scripts.txt').write_text('\n\n'.join(s['id']+' — '+s['title']+'\n'+s['text'] for s in rows)+'\n')
 fields=['id','name','duration_seconds','frames','lufs','true_peak_dbtp','voice_onset_normalized_stem_seconds','bgm_during_narration_dbfs','final_mix_first_10ms_dbfs','cta_seconds']
 with (ROOT/'deliverables/qc_summary.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows({k:m[k] for k in fields} for m in media)
 with (ROOT/'deliverables/motion_qc.csv').open('w',newline='') as f:
  fields=['short_id','asset_id','frame_pairs','median','p95','p95_over_median','passed'];w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader()
  for c in read(ROOT/'records/motion_qc.json')['checks']:w.writerow(dict(short_id=c['short_id'],asset_id=c['asset_id'],passed=c['passed'],**{k:c['measurement'][k] for k in fields[2:-1]}))
 cards=''.join(f'<section><h2>{s["id"]}</h2><video controls preload="metadata" src="QO_short_EP008_{s["id"]}_v01.mp4"></video><p>{s["duration_seconds"]:.3f}秒・英語字幕入り</p></section>' for s in rows)
 (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>第8話ショート確認版</title><style>body{max-width:1100px;margin:24px auto;padding:16px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}video{width:100%;max-height:75vh}h1,h2{color:#d8b575}</style><h1>Quiet Origins 第8話ショート K1〜K3 v01</h1><p>確認用・未投稿。K3冒頭は本人承認で「墓の発見より古い」に修正。ほかの台本文・見出しを維持。</p><main>'+cards+'</main><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})));</script></html>')
 mroot=Path('/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v03_20261030');credit=(mroot/'deliverables/EP008_source_credits.md').read_text();(ROOT/'deliverables/source_credits.md').write_text('# 第8話ショートの資料\n\n使用：K1 B286・B313・B312／K2 N03・N02・N01／K3 C01・D_novels（1869）・B157。9素材各1回。以下は本編の出典台帳を添付したもの。\n\n'+credit)
 (ROOT/'deliverables/upload_plan_draft.md').write_text('# 投稿予定・未実施\n\nK1 11/4 18:00、K2 11/5 12:00、K3 11/5 18:00（JST）は依頼書の案。今回の依頼は制作のみで、予約・投稿は行っていない。\n\nK3冒頭だけは本人承認で「older than the discovery of Tutankhamun\'s tomb」に変更。投稿用の題も墓の発見との比較だと分かる形で、投稿依頼時に確定する。\n\n関連動画は第8話本編。公開後に設定する予定。投稿前にチャンネル当日の本編＋ショート合計3本以下、ショート2本以下を再照合する。\n')
 with zipfile.ZipFile(ROOT/'deliverables/production_records.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted((ROOT/'records').iterdir()):
   if p.suffix in ['.json','.log'] and not p.name.startswith('sharing'):z.write(p,'records/'+p.name)
  for p in sorted((ROOT/'review').rglob('*.jpg')):z.write(p,'review/'+str(p.relative_to(ROOT/'review')))
  for p in sorted((ROOT/'deliverables').iterdir()):
   if p.suffix in ['.srt','.csv','.txt','.html','.md'] and p.name!='SHA256SUMS_shared.txt':z.write(p,p.name)
  for p in (ROOT/'audio').glob('K*_native.wav'):z.write(p,'native_voice/'+p.name)
  for name in ['wom08_shorts.py','wom08_shorts_render.py','wom08_shorts_visuals.py','wom08_shorts_qc.py','wom08_shorts_delivery.py','wom08_shorts_share.py']:z.write(REPO/'new-channel'/name,'scripts/'+name)
 with zipfile.ZipFile(ROOT/'deliverables/production_records.zip') as z:assert z.testzip() is None
 files=sorted([*(ROOT/'deliverables').glob('QO_short_EP008_*.mp4'),ROOT/'deliverables/production_records.zip']);assert len(files)==4
 (ROOT/'deliverables/SHA256SUMS_shared.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
 print('SHORTS DOCS / ARCHIVE READY',flush=True)

def handoff():
 sharing=read(ROOT/'records/sharing.json');assert sharing['draft'] and sharing['status']=='verified' and len(sharing['assets'])==5
 for d in ['records','review','deliverables']:(DEST/d).mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,DEST/'records'/p.name)
 for p in (ROOT/'review').rglob('*.jpg'):
  if p.name.startswith('planned_'):continue
  q=DEST/'review'/p.relative_to(ROOT/'review');q.parent.mkdir(parents=True,exist_ok=True);assert p.stat().st_size<1000000;shutil.copy2(p,q)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.csv','.txt','.md']:shutil.copy2(p,DEST/'deliverables'/p.name)
 media=read(ROOT/'records/media_qc.json')['media'];audio={a['id']:a for a in read(ROOT/'records/audio_qc.json')['reports']};shots=read(ROOT/'records/render_shots.json');motion=read(ROOT/'records/motion_qc.json');safe=read(ROOT/'records/safe_crop_qc.json');maxratio=max(c['measurement']['p95_over_median'] for c in motion['checks'])
 lines=['# 第8話「ツタンカーメンの呪い」ショート K1〜K3 制作結果（2026-10-30）','','**英語版3本・確認版v01を制作し、技術検査・非公開Draft共有を完了。本人の試聴とClaudeの確認待ち。YouTube未投稿。**','',f'[非公開Draft Release]({sharing["release_url"]})、Release ID **{sharing["release_id"]}**。3動画・資料ZIP・SHA一覧の5資産をRelease ID指定RESTで再取得し、全件サイズ・SHA-256一致、匿名404、Draft維持を確認。',f'[確認版README](wom_ショート_EP008_確認版_v01_20261030/README.md) ／ [全資産IDとSHA](wom_ショート_EP008_確認版_v01_20261030/records/sharing.json)。','','## 台本と音声','','本人のこのチャットでの承認により、K3冒頭だけ `The mummy\'s curse is older than the discovery of Tutankhamun\'s tomb.` に修正。「墓そのものより古い」という誤解を避け、1869年と1922年の発見の比較にした。ほかの台本文と見出しは依頼書を維持。承認記録は [script_approval.json](wom_ショート_EP008_確認版_v01_20261030/records/script_approval.json)。','','本編v03と同じKokoro af_heart、speed 0.82、sentence pause 0.3／clause pause 0.12、同じTutankhamun・Carnarvon・Louisa May Alcott・年号の読み補正。新しく読み上げ、速度・ピッチ加工なし。自然な読みの時点で3本とも22秒以内。K1は映像の末尾を18秒まで、K2/K3は約0.15秒の余白だけ追加。','', '|動画|尺|フレーム|LUFS|dBTP|声の開始|','|---|---:|---:|---:|---:|---:|']
 for m in media:lines.append(f'|{m["id"]}|{m["duration_seconds"]:.3f}秒|{m["frames"]}|{m["lufs"]:.2f}|{m["true_peak_dbtp"]:.2f}|{m["voice_onset_normalized_stem_seconds"]:.2f}秒|')
 lines+=['','1080×1920／30fps固定／H.264 High／yuv420p。全ショットを個別デコード→各動画1つのエンコーダー。全編デコード警告・エラー0、全フレームの形式1種類、全PTSが30fps等間隔。声の開始は10ms窓・−50dBFSで測定。','','## BGM','','QO_THEME_A02のみ。100Hzハイパス、2828Hz／1oct／−3.5dB EQ。語りのRMSより15dB低くし、0秒からフェードインなし。分離ステムと完成MP4の冒頭10msでも非無音を確認。末尾のみ0.12秒フェード。','', '|動画|元音源区間|語りdBFS|BGM dBFS|冒頭BGM dBFS|','|---|---|---:|---:|---:|']
 for sid,a in audio.items():lines.append(f'|{sid}|{a["bgm_excerpt_start_seconds"]:.2f}–{a["bgm_excerpt_end_seconds"]:.2f}秒|{a["voice_during_narration_dbfs"]:.2f}|{a["bgm_during_narration_dbfs"]:.2f}|{a["bgm_first_10ms_dbfs"]:.2f}|')
 lines+=['','値は最終音量調整後・ピーク制御前のステム。完成AAC/MP4でも−14LUFSとピーク≤−1dBTPを測定。','','## 資料と切り替え','','9素材は3本を通して各1回。切替はKokoro音素長から推定した語時刻に最も近いフレーム（最大ずれ1/60秒）。人による語時刻の聞き取り計測ではない。各表示1.5秒以上。','', '|動画|素材|区間|切り替え語／推定語時刻|','|---|---|---|---|']
 for s in shots:
  cue='冒頭' if s['cut_phrase'] is None else f'{s["cut_phrase"]}／{s["cut_word_seconds"]:.6f}秒';lines.append(f'|{s["short_id"]}|{s["asset_id"]}|{s["start_frame"]/30:.6f}–{s["end_frame"]/30:.6f}秒|{cue}|')
 lines+=['',f'動きのp95÷中央値は全9ショットで最大 **{maxratio:.6f}**（≤2.5）。完成MP4の全隣接フレームを測定。冒頭だけ固定札・字幕・フェード見出しを空間的に除いてカメラの動きを測定し、時間方向の間引きなし。','','## 画面確認','','- 見出しは第7話と同じGeorgia Bold／生成り #f4efdf／字高100px、同じ位置。0フレームから表示、2.0〜2.3秒で消える。アルファ値を全70フレームで検査。','- 冒頭の0・0.5・1・1.5・2・2.5秒の18画像を連続デコードから取得し、欠け・札と字幕との重なりなしを確認。','- K1の冒頭は像の頭部を残す縦切り出し。K2は元新聞の見出しの端が欠けないよう同じ記事の余白まで含め、上部札の下に配置。K3は王の場面を大きく表示。','- 冒頭の資料矩形の高さ（ぼかし背景を除く）：'+ ' ／ '.join(f'{x["id"]} {100*x["fraction"]:.3f}%' for x in safe['first_art_height_fractions'])+'。低解像度の紙面・模写は8割以上を保ちながら過剰な拡大を抑えた。','- 本編v03と同じ札・出典文字列を維持。C01は1923–27年の模写・フイTT40でKV62ではないことを明記。発掘写真は同じセピア、新聞は白黒、図解は砂色と濃い茶色。','- N02はドイル説とバッジの反論の2抜粋を同じ1ショット内に配置。N01は見出し段だけ。K2全659フレームのカメラが、確認した記事の画素だけからなる合成画像内に留まることを検査。顔写真・事故の大見出しなし。','- D_novelsは本編v03の1869ブロックの画素を縦へ並べ替え、1892の行は含めない。','- 英語字幕は承認済み台本と一致。1行4〜5語・最大2行、輪郭と影を含めx80–880／y1150–1450内。年号1923/1869は文脈の語と一緒に表示し、数字だけに分けない。','- 3本とも最後約10秒に絵か紙面を含め、末尾まで画像が残る。K1は杯→刊本、K2は新聞、K3は最後4.200秒が階段の写真。CTA Full story on Quiet Originsは最後2秒だけ、読み上げなし。','','## 次の確認','','本人：3本の声とBGMの聴きやすさ。Claude：台本・字幕・札・切替・後半の画像。人による全編試聴は未実施。投稿と予約は別依頼。11/4 18:00、11/5 12:00・18:00は依頼書の案のまま、未予約。投稿前に当日のチャンネル本数を再照合する。','',f'Mac：`{ROOT}`。入口は `deliverables/preview.html`。追加契約・購入なし、新しいAI画像・AI動画なし。原寸・音声・動画はGitに含めていない。']
 (REPO/'new-channel/wom_ショート制作結果_EP008_20261030.md').write_text('\n'.join(lines)+'\n')
 (DEST/'README.md').write_text(f'# Quiet Origins 第8話ショート K1〜K3 v01\n\n[制作結果・実測値](../wom_ショート制作結果_EP008_20261030.md)\n\n[非公開Draft]({sharing["release_url"]})、Release ID **{sharing["release_id"]}**。3動画＋確認資料ZIP＋SHA一覧の5資産をRESTで再取得して全SHA一致。匿名404、Draft維持、YouTube未投稿。\n\nAPI `GET /repos/yasukawa1980/youtube/releases/{sharing["release_id"]}` で資産IDを取得し、`gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE` で取得。ZIPを動画3本と同じ場所へ展開するとpreview.htmlから再生できる。\n\n[共有SHA](deliverables/SHA256SUMS_shared.txt) ／ [REST照合](records/sharing.json)\n\n[冒頭K1](review/K1_opening_0_to_2_5s.jpg) ／ [K2](review/K2_opening_0_to_2_5s.jpg) ／ [K3](review/K3_opening_0_to_2_5s.jpg)\n\n[2秒おきK1](review/QO_short_EP008_K1_v01_every2s.jpg) ／ [K2](review/QO_short_EP008_K2_v01_every2s.jpg) ／ [K3](review/QO_short_EP008_K3_v01_every2s.jpg)\n\nローカル：`{ROOT}/deliverables/preview.html`\n')
 print('EP008 SHORTS HANDOFF COMPLETE',flush=True)
if __name__=='__main__':globals()[sys.argv[1]]()
