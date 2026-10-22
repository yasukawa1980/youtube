"""EP003 review documents and private draft delivery; never publishes a release."""
import argparse,csv,hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image
from wom03_produce import ROOT,REPO,MEDIA,MODELS,read,save,sha,ff,content,SR,PHONEMES,REPLACEMENTS
GH='yasukawa1980/youtube';TAG='wom03-medusa-v01-exact-20261023';GUIDE=REPO/'new-channel/wom03_確認版_v01_20261023'
def api(args,data=None):
 p=subprocess.run(['gh','api',*args],input=json.dumps(data) if data is not None else None,capture_output=True,text=True,check=True);return json.loads(p.stdout)
def mm(t):n=int(t);return f'{n//60:02}:{n%60:02}'
def docs():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters})
 shots=read(ROOT/'records/render_shots.json');usage=[{'asset_id':s['key'],'segment':s['segment_id'],'shot':i+1,'start':s['start'],'end':s['end'],'uses':1} for i,s in enumerate(shots) if s['segment_id']!='BRAND'];assert len({s['asset_id'] for s in usage})==len(usage)==35
 with (ROOT/'deliverables/EP003_asset_usage_v01.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(usage[0]));w.writeheader();w.writerows(usage)
 save(ROOT/'records/asset_usage_v01.json',usage)
 used={x['asset_id'] for x in usage};a=[x for x in read(ROOT/'records/source_assets.json')['items'] if x['id'] in used]
 full_credits='# EP003 — Museum image credits\n\nThe Metropolitan Museum of Art, Open Access / Public Domain / CC0.\n\n'
 for x in a:full_credits+=f'## {x["id"]} — {x["title"]}\n\n{x["date"]}; {x["accession"]}. {x["credit"]}\n\n{x["object_url"]}\n\nRights: {x["rights"]}\n\n'
 (ROOT/'deliverables/EP003_source_credits.md').write_text(full_credits)
 sources=[('Hesiod, Theogony 270–294. H. G. Evelyn-White, 1914','https://www.theoi.com/Text/HesiodTheogony.html'),('Homer, Iliad 5.738–742. A. T. Murray, 1924','https://www.theoi.com/Text/HomerIliad5.html'),('Pindar, Pythian 12. Ernest Myers, 1874 (1904 reprint): fair-faced','https://www.gutenberg.org/cache/epub/10717/pg10717-images.html'),('Pindar, Pythian 12. F. A. Paley, 1868: fair-cheeked','https://en.wikisource.org/wiki/Odes_of_Pindar_(Paley)/Pythian_Ode_12'),('Ovid, Metamorphoses 4.794–803. Frank Justus Miller, 1916; 1921 edition, 1951 reprint','https://en.wikisource.org/wiki/Metamorphoses_(Miller)/Book_IV'),('[Apollodorus], Library 2.4.3. J. G. Frazer, 1921','https://www.theoi.com/Text/Apollodorus2.html'),('Madeleine Glennon, Medusa in Ancient Greek Art. The Met, 2017','https://www.metmuseum.org/essays/medusa-in-ancient-greek-art')]
 sources.append(('Elizabeth Hadley, More than a Monster: Medusa Misunderstood. Dartmouth Libraries exhibition, 2024 (modern reception)','https://www.library.dartmouth.edu/exhibits/more-than-a-monster'))
 for l in ['en','ja']:
  intro=('Monster or victim? Ancient sources give Medusa more than one story. Follow Hesiod, early Greek art, Pindar, Ovid, and a later sculpture by Canova.' if l=='en' else '怪物か、犠牲者か。古代の資料は、メドゥーサの異なる姿を伝えています。ヘシオドス、古代ギリシアの美術、ピンダロス、オウィディウス、そしてカノーヴァの彫刻をたどります。')
  disclosure=('This video uses synthetic narration. Labelled AI reconstructions illustrate atmosphere; they are not historical evidence or exact reconstructions of real sites. Modern interpretations are distinguished from ancient accounts.' if l=='en' else '音声には合成音声を使用しています。AIによる再現には札を付け、雰囲気を示す挿絵として用いています。史料そのものや実在の遺跡の正確な復元ではありません。現代の解釈と古代の記述を区別して紹介します。')
  s=f'# Quiet Origins / EP003 — {"Upload information" if l=="en" else "投稿情報"}\n\n確認版v01。公開・予約操作は未実施。\n\n## Title\n\n{c[l]["title"]}\n\n## Description\n\n{intro}\n\n{disclosure}\n\nChapters\n'
  s+='\n'.join(x['timestamp']+' '+x[l] for x in chapters)+'\n\nSources\n'
  s+='\n'.join(f'- {title}\n  {url}' for title,url in sources)+'\n\nImage credits — The Metropolitan Museum of Art (The Met), Open Access / Public Domain / CC0\n'
  for x in a:s+=f'- {x["id"]} / {x["accession"]}: {x["object_url"]}\n'
  s+='\nhttps://www.metmuseum.org/hubs/open-access\nhttps://creativecommons.org/publicdomain/zero/1.0/\n\nEnglish voice: Kokoro / Heart (af_heart), synthetic speech.\n日本語音声：VOICEVOX:冥鳴ひまり（C設定）。\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nAI stills: OpenAI image generation — R01, R02, R03, R05, R06, R07, R08, R09, R10.\nAI video: Kling AI 3.0 — V01–V04.\nDiagrams and original synthesized ambient music: Quiet Origins.\n\n#Medusa #GreekMythology #QuietOrigins\n'
  assert len(s.split('## Description\n\n',1)[1])<=5000 and len(c[l]['title'])<=100
  s+=f'\n## 制作・確認メモ（概要欄に貼り付けない）\n\n台本v03。共通尺 {m["duration_seconds"]:.6f}秒。エンドカード開始 {m["brand_intervals"]["endcard"][0]:.6f}秒。投稿用の英日WAVは48kHz・24bit、各{round(m["duration_seconds"]*48000):,}サンプル。全作品の名称・年代・Credit LineはEP003_source_credits.mdに収録。\n'
  s+='原典確認2件はClaudeのv03で解消。OvidはMiller訳、Pindarのfair-cheekedはPaley訳を採用しMyers訳と併記。A21の乗り手はベレロポン。A22は1606年の後世の版画。本人の全編試聴・動きの自然さの確認は未実施。\n'
  (ROOT/f'deliverables/EP003_upload_info_{l}.md').write_text(s)
 names={'en':['Hesiod','Theogony','Stheno','Euryale','Chrysaor','gorgoneia','aegis','aulos','Pindar','Metamorphoses','Apollodorus','Canova','700 BCE','8 CE'],'ja':['ステンノ','エウリュアレ','クリュサオル','ゴルゴネイオン','神統記']};auditions=[];locations=[]
 for l in ['en','ja']:
  cues=[c for s in read(ROOT/f'records/narration_timeline_{l}.json')['segments'] for c in s['cues']];chosen=[];seen=set()
  for name in names[l]:
   for cue in cues:
    if name in cue['text']:locations.append({'language':l,'word':name,'sentence_id':cue['id'],'start':cue['start'],'end':cue['end']})
   cue=next((c for c in cues if name in c['text']),None)
   if cue and cue['id'] not in seen:chosen.append(cue);seen.add(cue['id'])
  pieces=[];pos=0;lines=[]
  for cue in chosen:
   audio,sr=sf.read(ROOT/cue['audio_file'],dtype='float32');assert sr==SR;lines.append(f"{mm(pos)} | 本編 {cue['start']:.3f}–{cue['end']:.3f}s | {cue['id']} | {cue['text']}");auditions.append({'language':l,'audition_start':pos,'main_start':cue['start'],'main_end':cue['end'],**cue});pieces.extend([audio,np.zeros(round(1.2*SR),np.float32)]);pos+=len(audio)/SR+1.2
  wav=ROOT/f'_work/pronunciation_{l}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16');ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP003_pronunciation_{l}.m4a']);(ROOT/f'deliverables/EP003_pronunciation_{l}.txt').write_text('本人の試聴用。時刻は単語を含む文の範囲。聴感確認は未実施。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_auditions.json',auditions);save(ROOT/'records/pronunciation_locations.json',locations)
 save(ROOT/'records/runtime.json',{'python':sys.version,'interpreter':sys.executable,'models':{str(p):sha(p) for p in [MODELS/'Kokoro82M_v1/kokoro-v1.0.onnx',MODELS/'Kokoro82M_v1/voices-v1.0.bin',MODELS/'VOICEVOX_core_0.17.0_model_0.16.4/models/vvms/1.vvm']},'phoneme_overrides':PHONEMES,'reading_replacements':REPLACEMENTS,'human_auditory_review':False})
 for kind in ['ai_images','ai_videos']:
  for x in read(ROOT/f'records/{kind}.json'):shutil.copy2(x['local_path'],ROOT/'deliverables'/Path(x['local_path']).name)
 cards=[]
 for l,label in [('en','English'),('ja','日本語')]:
  cards.append(f'<section><h2>{label}</h2><video controls preload="metadata" src="EP003_Medusa_{l}_v01_subtitled_review_1080p30.mp4"></video><p><a href="EP003_Medusa_{l}_v01_1080p30.mp4">通常版</a> / <a href="EP003_Medusa_{l}_v01_1080p30.srt">SRT</a> / <a href="EP003_audio_{l}.wav">投稿用WAV</a></p><h3>固有名詞の試聴</h3><audio controls src="EP003_pronunciation_{l}.m4a"></audio><p><a href="EP003_pronunciation_{l}.txt">試聴箇所と本編時刻</a></p></section>')
 player='<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins — Medusa v01</title><style>body{max-width:1120px;margin:32px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,a{color:#d8b575}section{margin:36px 0}video{width:100%;max-height:70vh;background:black}audio{width:100%}</style><h1>Quiet Origins / Medusa</h1><p>確認版 v01 — 6分43.67秒。固有名詞、冒頭からロゴへの流れ、M12の語りの調子、動画の自然さをご確認ください。</p><img src="EP003_thumbnail_A24.jpg" style="width:48%"><img src="EP003_thumbnail_A04.jpg" style="width:48%">'+''.join(cards)+'<script>document.querySelectorAll("video,audio").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video,audio").forEach(w=>{if(w!==v)w.pause()})));</script></html>'
 (ROOT/'deliverables/preview.html').write_text(player)
 print('DOCS',len(a),'museum objects',len(locations),'pronunciation locations',flush=True)

def share():
 qc=read(ROOT/'records/qc_v01.json');assert qc['passed'];assert read(ROOT/'records/motion_v01.json')['passed'];assert read(ROOT/'records/visual_review.json')['passed'];assert read(ROOT/'records/subtitle_layout_validation.json')['passed']
 assert read(ROOT/'records/final_checks.json')['passed'];wav=read(ROOT/'records/wav_sample_validation.json');assert wav['passed']
 assert read(ROOT/'records/container_precision.json')['passed']
 for f in wav['files']:assert sha(ROOT/'deliverables'/f['file'])==f['sha256']
 visual=read(ROOT/'records/visual_review.json');assert visual['video_sha256']==sha(ROOT/'deliverables/EP003_Medusa_en_v01_1080p30.mp4');assert visual['visual_manifest_sha256']==sha(ROOT/'records/visual_manifest.json');assert visual['render_shots_sha256']==sha(ROOT/'records/render_shots.json')
 for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 for p in (ROOT/'records').glob('*.json'):
  if p.name not in ['sharing.json','render_progress.json']:shutil.copy2(p,ROOT/'deliverables'/p.name)
 with zipfile.ZipFile(ROOT/'deliverables/EP003_review_frames.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((ROOT/'review').glob('*.jpg')):z.write(p,p.name)
 files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.name!='SHA256SUMS_shared.txt');hashfile=ROOT/'deliverables/SHA256SUMS_shared.txt';hashfile.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(hashfile)
 state=ROOT/'records/sharing.json'
 r=api([f'repos/{GH}/releases/{read(state)["release_id"]}']) if state.exists() and read(state).get('status')!='superseded_before_final_delivery' else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
 if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第3話 メドゥーサ v01（英日確認版）','body':'Claude修正版台本v03。英日共通映像403.666667秒・12110フレーム。通常版、字幕入り確認版、SRT、M4A、サンプル一致WAV、サムネ2案、試聴音声、原寸AI素材、検査記録。本人の試聴・動きの自然さの確認待ち。Releaseは非公開Draftを維持し、YouTube投稿なし。','draft':True})
 assert r['draft'];save(state,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
 for p in files:
  old=next((a for a in r['assets'] if a['name']==p.name),None)
  if old:assert old['state']=='uploaded' and old['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
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
 shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified'
 for d in ['records','frames','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,GUIDE/'records'/p.name)
 canonical=REPO/'new-channel/episodes/EP003_Medusa/records'
 for name in ['qc_v01.json','sharing.json','master_timeline.json','reading_replacements.json','pronunciation_locations.json','chapters.json']:shutil.copy2(ROOT/'records'/name,canonical/name)
 for p in (ROOT/'review').glob('*.jpg'):
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,GUIDE/'frames'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.txt','.csv','.html']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
 table='\n'.join(f'| {a["name"]} | {a["asset_id"]} | {a["bytes"]:,} |' for a in shared['assets'])
 (GUIDE/'README.md').write_text(f'''# Quiet Origins 第3話「メドゥーサ」確認版v01

台本v03。403.666667秒・12,110フレーム・1080p30。Mac：`{ROOT}`。Mac制作フォルダ内の `deliverables/preview.html` で再生できます。別環境ではDraftの全添付を同じフォルダへ保存してから `preview.html` を開いてください。Git内の案内フォルダには動画・音声・原寸素材を置いていません。

[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をREST再取得し、SHA-256・bytes一致。YouTube投稿・Release公開はしていません。

```sh
gh api repos/{GH}/releases/{shared['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

[検査結果](records/qc_v01.json)／[動きの測定](deliverables/EP003_motion_v01.csv)／[素材使用一覧](deliverables/EP003_asset_usage_v01.csv)／[読み補正一覧](records/reading_replacements.json)／[全発音箇所](records/pronunciation_locations.json)。時刻は単語を含む文の範囲です。

再現手順：既存Python環境で `wom03_produce.py prepare → en → ja → timeline → audio`、`wom03_visuals.py`、`wom03_render.py pictures → package → reviews → precision → verify`、`wom03_validate.py layout → frames`、`wom03_motion.py`、`wom03_final_checks.py`。目視確認記録後に `wom03_delivery.py docs → share → export`。画像生成・Kling動画は保存済み原本を使用し、再実行で自動生成しない。

本人の試聴項目：英語固有名詞（Stheno、Euryale、Chrysaor、gorgoneia、aegis、aulos、Canova）、日本語の固有名詞と神統記、冒頭〜ロゴ、M12の語りの調子。全編の動きの自然さと発音の聴感確認は未実施です。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}
''')
 qc=read(ROOT/'records/qc_v01.json');motion=read(ROOT/'records/motion_v01.json');final=read(ROOT/'records/final_checks.json');subs=read(ROOT/'records/subtitle_validation.json');levels=read(ROOT/'records/audio_qc.json');repl=read(ROOT/'records/reading_replacements.json')
 peak=max(s['measurement']['p95_over_median'] for s in motion['shots']);size=sum(a['bytes'] for a in shared['assets']);report=REPO/'new-channel/wom03_制作結果_v01_20261023.md';old=report.read_text() if report.exists() else ''
 marker='<!-- 工程0履歴 -->'
 if marker in old:old=old.split(marker,1)[1]
 current=f'''# 第3話「メドゥーサ」確認版v01 制作結果（2026-10-23）

**Claude修正版台本v03から確認版を制作完了。403.666667秒・12,110フレーム・1920×1080・30fps。** [再生・取得案内](wom03_確認版_v01_20261023/README.md)。公開前の本人試聴は未実施。

## 台本と構成

- 原典5件の照合で生じたM03日本語・M13英日の確認事項は、Claudeの `c50e370` によるv03で解消。表示台本は変更していない。
- 本編35ショット＋共通ブランド2カット。博物館資料19作品、再現画9点、Kling動画4本、模式図2点、クレジット1点。素材IDは全35件各1回。[使用一覧](wom03_確認版_v01_20261023/deliverables/EP003_asset_usage_v01.csv)。R04は依頼書のショット割りにないため生成していない。
- A01・A02は全体と顔だけの拡大を同じショットで併記し、3%の滑らかな動きに統一。依頼書の全体→顔の順次表示から、許容されているDの並置方式へ調整。首元・切り口へ寄らない。A22は6秒間、全体だけ。A21はベレロポン、A13は作品名だけの札。M12の再現画・動画に人物なし。
- AI静止画は組み込みOpenAI image generation、動画はKling AI 3.0。4本×80＝**320クレジット**、既存契約枠内。プロンプト・生成日・原寸ファイルSHA-256・生成元URLを記録。追加契約・購入なし。

## 実測した検査結果

| 項目 | 結果 |
|---|---|
| 完成MP4 | 英日通常版・字幕入り版4本すべて全編デコード、正確な1/30秒PTS、各12,110フレーム |
| 英日映像 | 通常版の圧縮映像ストリームSHA-256が同一 |
| 音量・ピーク | 英語 {levels['languages']['en']['input_i']} LUFS / {levels['languages']['en']['input_tp']} dBTP、日本語 {levels['languages']['ja']['input_i']} LUFS / {levels['languages']['ja']['input_tp']} dBTP |
| BGM | 語り区間 {levels['bgm_during_narration_dbfs']:.3f} dBFS、間で+4 dB |
| 無音 | 完成音声で−60dB基準・1秒以上の無音0件 |
| 投稿用WAV | 両言語48kHz・24bit・**19,376,000サンプル**。動画1フレームあたり1,600サンプルで尺一致 |
| MP4・M4A内部時刻 | movie timescaleを48kHzへ統一。映像duration_ts=6,200,320（1/15,360秒）、音声duration_ts=19,376,000（1/48,000秒）で同尺。圧縮映像・音声は補正前とSHA-256一致 |
| 字幕 | 英語{subs['en']['count']}件・日本語{subs['ja']['count']}件。本文は台本と空白・改行以外一致。最短1.4秒以上、英42字／日23字以内、最大2行 |
| 字幕配置 | 全175字幕×FontSize14／26＝350描画。図解・クレジット文字y≤700、字幕と文字の重なりなし |
| 動き | 本編35件すべてp95÷中央値≤2.5、最大 **{peak:.6f}**。全フレーム測定。共通ブランドは対象外 |
| ブランド | 完成動画から720フレームを抽出比較し、承認済み共通版と全画素MD5一致 |
| エンドカード | 383.666667秒から403.666667秒までの正確な最後20秒 |
| OP前の日本語待ち | {final['ja_wait_before_opening']:.6f}秒。音声の加速なし、文間で調整 |
| 原本保全 | 博物館原本72枚、AI原本13件のSHA-256一致 |

[映像・音声検査](wom03_確認版_v01_20261023/records/qc_v01.json)／[動きの全測定値](wom03_確認版_v01_20261023/deliverables/EP003_motion_v01.csv)／[ブランド・配置検査](wom03_確認版_v01_20261023/records/final_checks.json)。

## 発音と本人確認

初回は置換なしで生成して保全。その後、合成器の音素・カナ解析で明らかな読み違いを検出し、読み上げ入力のみ補正した。Hesiod、Theogony、Stheno、Euryale、Chrysaor、gorgoneia、aulos、Apollodorus、8 CE、日本語の神統記、計{len(repl)}出現箇所。聴感による確認済みとはしていない。

[補正一覧](wom03_確認版_v01_20261023/records/reading_replacements.json)と[初回解析](wom03_確認版_v01_20261023/records/first_pass_pronunciation_analysis.json)、固有名詞25箇所の文単位時刻、英日試聴用音声を添付。単語単位の強制アラインメントは行っていない。

本人の確認項目は、英語Stheno／Euryale／Chrysaor／gorgoneia／aegis／aulos／Canova、日本語固有名詞と神統記、冒頭からロゴまでの流れ、M12の語りの調子、全編の動きの自然さ。AI動画は各6時点の画像を目視し、人物・読める文字・目立つ形状崩れがないことを確認したが、人による全編再生確認は未実施。

## 保存・共有

Mac：`{ROOT}`。

新規[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付・{size:,} bytesをRelease ID指定のRESTで再取得し、サイズ・SHA-256を照合。英日通常版・字幕入り版、SRT、M4A、WAV、サムネ2案、試聴音声、英日投稿情報、全資料クレジット、AI原寸素材、検査記録を収録。

時刻情報補正前の中間Draft（ID 421286655）は、未採用と明記して非公開のまま保全。最終納品は上記Release IDのみ。補正はコンテナ時刻の丸めを解消するもので、映像・音声の内容は変更していない。[補正前後の照合](wom03_確認版_v01_20261023/records/container_precision.json)。

投稿情報はOvidのMiller訳、PindarのMyers 1874とPaley 1868を併記し、全博物館資料の作品URLを掲載。概要欄は英日とも5,000文字以内、題名は100文字以内。YouTube投稿・予約・Release公開は未実施。

制作途中は `6a2ce0b` で共有済み。最終成果もリモート最新履歴上へ適用してpushする。分岐した本体の古い履歴は送信しない。

<details><summary>原典照合で停止した時点の記録（確認事項は解消済み）</summary>

'''
 old=old.removesuffix('\n</details>\n');report.write_text(current+marker+old+'\n</details>\n')
 print('EXPORTED',GUIDE,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','export']);a=p.parse_args();globals()[a.stage]()
