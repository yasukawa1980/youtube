"""EP005 review documents and private draft delivery; never publishes a release."""
import argparse,csv,hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image
from wom05_produce import ROOT,REPO,MEDIA,MODELS,read,save,sha,ff,content,SR,PHONEMES,REPLACEMENTS
GH='yasukawa1980/youtube';TAG='wom05-tengu-v01-20261024';GUIDE=REPO/'new-channel/wom05_確認版_v01_20261024'
def api(args,data=None):
 p=subprocess.run(['gh','api',*args],input=json.dumps(data) if data is not None else None,capture_output=True,text=True,check=True);return json.loads(p.stdout)
def mm(t):n=int(t);return f'{n//60:02}:{n%60:02}'
def share():
 qc=read(ROOT/'records/qc_v01.json');assert qc['passed'];assert read(ROOT/'records/motion_v01.json')['passed'];assert read(ROOT/'records/visual_review.json')['passed'];assert read(ROOT/'records/subtitle_layout_validation.json')['passed']
 assert read(ROOT/'records/final_checks.json')['passed'];wav=read(ROOT/'records/wav_sample_validation.json');assert wav['passed']
 assert read(ROOT/'records/container_precision.json')['passed']
 for f in wav['files']:assert sha(ROOT/'deliverables'/f['file'])==f['sha256']
 visual=read(ROOT/'records/visual_review.json');assert visual['video_sha256']==sha(ROOT/'deliverables/EP005_Tengu_en_v01_1080p30.mp4');assert visual['visual_manifest_sha256']==sha(ROOT/'records/visual_manifest.json');assert visual['render_shots_sha256']==sha(ROOT/'records/render_shots.json')
 for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 for p in (ROOT/'records').glob('*.json'):
  if p.name not in ['sharing.json','render_progress.json']:shutil.copy2(p,ROOT/'deliverables'/p.name)
 with zipfile.ZipFile(ROOT/'deliverables/EP005_review_frames.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((ROOT/'review').glob('*.jpg')):z.write(p,p.name)
 files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.name!='SHA256SUMS_shared.txt');hashfile=ROOT/'deliverables/SHA256SUMS_shared.txt';hashfile.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(hashfile)
 state=ROOT/'records/sharing.json'
 r=api([f'repos/{GH}/releases/{read(state)["release_id"]}']) if state.exists() and read(state).get('status')!='superseded_before_final_delivery' else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
 if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第5話 天狗 v01（英日確認版）','body':'承認済み台本v02。英日共通映像368.833333秒・11065フレーム。通常版、字幕入り確認版、SRT、M4A、サンプル一致WAV、サムネ2案、試聴音声、原寸AI素材、検査記録。本人の試聴・動きの自然さの確認待ち。Releaseは非公開Draftを維持し、YouTube投稿なし。','draft':True})
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


def docs():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters})
 shots=read(ROOT/'records/render_shots.json');usage=[{'asset_id':s['key'],'segment':s['segment_id'],'shot':i+1,'start':s['start'],'end':s['end'],'uses':1} for i,s in enumerate(shots) if s['segment_id']!='BRAND'];assert len({s['asset_id'] for s in usage})==len(usage)==24
 with (ROOT/'deliverables/EP005_asset_usage_v01.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(usage[0]));w.writeheader();w.writerows(usage)
 save(ROOT/'records/asset_usage_v01.json',usage)
 used={x['asset_id'] for x in usage};assets=[x for x in read(ROOT/'records/source_assets.json')['assets'] if x['key'] in used];assert len(assets)==15
 credits='# EP005 — Source image credits\n\n'
 for x in assets:credits+=f'## {x["key"]} — {x["title"]}\n\n{x["artist"]}; {x["date"]}; {x["museum"]}; {x["accession"]}.\n\n{x["page"]}\n\nRights: {x["rights"]}. {x["rights_evidence"]}\n\n'
 (ROOT/'deliverables/EP005_source_credits.md').write_text(credits)
 sources=[('W. G. Aston, Nihongi, vol. II (1896), Book XXIII, pp. 167–168','https://en.wikisource.org/wiki/Nihongi/Book_XXIII'),('Nihon Shoki, vol. 23: 1926 facsimile, frame 10','https://dl.ndl.go.jp/pid/1182143/1/10'),('Shiji, Tianguan shu: c. 1925 printed edition, frame 87','https://dl.ndl.go.jp/pid/958959/1/87'),('Konjaku Monogatari-shu 20-2 / 20-3 (transcription consulted)','https://yatanavi.org/text/k_konjaku/k_konjaku20-2'),('Konjaku Monogatari-shu 20-3','https://yatanavi.org/text/k_konjaku/k_konjaku20-3'),('Uji Shui Monogatari, tale 32 (transcription consulted)','https://yatanavi.org/text/yomeiuji/uji032')]
 for l in ['en','ja']:
  intro=('The oldest Japanese tengu is a star. Follow the word from the Nihon Shoki through medieval bird tales to long-nosed masks, carvings and prints. The bird form remained alongside the later long-nosed figure.' if l=='en' else '日本のいちばん古い記録に出てくる天狗は、星でした。『日本書紀』から中世の鳥の説話、長い鼻の面・根付・版画へ。鳥の姿と鼻の高い姿が並んで残ったことを、文献と資料でたどります。')
  disclosure=('Synthetic narration and labelled AI illustrations are used. AI scenes are atmospheric illustrations, not historical evidence or exact reconstructions of real sacred sites.' if l=='en' else '音声合成と、札を付けたAIによる再現画を使用しています。再現画は雰囲気を示す挿絵であり、史料や実在する寺社の正確な復元ではありません。')
  body=intro+'\n\n'+disclosure+'\n\nChapters\n'+'\n'.join(x['timestamp']+' '+x[l] for x in chapters)+'\n\nSources\n'+'\n'.join(f'{a}\n{b}' for a,b in sources)
  body+='\n\nReferences only (images not used): Tengu Zoshi (c. 1296); Zegaibo-e (c. 1354). Modern annotations are not quoted.\n\nImage credits — Public Domain / CC0\n'
  for museum in dict.fromkeys(x['museum'] for x in assets):
   body+=museum+'\n'
   for x in assets:
    if x['museum']==museum:body+=f'{x["accession"]}: {x["page"]}\n'
  body+='\nEnglish voice: Kokoro / Heart (af_heart), synthetic speech.\n日本語音声：VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nAI stills: OpenAI image generation (R01–R03).\nAI video: Kling AI (V01–V03), with local editing for the soft light silhouette.\nDiagrams and original synthesized ambient music: Quiet Origins.\n\n#Tengu #JapaneseFolklore #QuietOrigins\n'
  assert len(body)<=5000 and len(c[l]['title'])<=100
  (ROOT/f'deliverables/EP005_upload_info_{l}.md').write_text(f'# EP005 投稿情報（確認版v01）\n\n## Title\n\n{c[l]["title"]}\n\n## Description\n\n{body}\n## 制作メモ（概要欄に含めない）\n\n共通尺{m["duration_seconds"]:.6f}秒。公開日未定・YouTube投稿未実施。本人試聴待ち。全作品名・権利はEP005_source_credits.md参照。\n')
 auditions()
 for kind in ['ai_images','ai_videos']:
  for x in read(ROOT/f'records/{kind}.json'):shutil.copy2(x['local_path'],ROOT/'deliverables'/Path(x['local_path']).name)
 cards=[]
 for l,label in [('en','English'),('ja','日本語')]:cards.append(f'<section><h2>{label}</h2><video controls preload="metadata" src="EP005_Tengu_{l}_v01_subtitled_review_1080p30.mp4"></video><p><a href="EP005_Tengu_{l}_v01_1080p30.mp4">通常版</a> / <a href="EP005_Tengu_{l}_v01_1080p30.srt">SRT</a> / <a href="EP005_audio_{l}.wav">投稿用WAV</a></p><h3>固有名詞の試聴</h3><audio controls src="EP005_pronunciation_{l}.m4a"></audio><p><a href="EP005_pronunciation_{l}.txt">試聴箇所と本編時刻</a></p></section>')
 html='<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins — Tengu v01</title><style>body{max-width:1120px;margin:32px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,a{color:#d8b575}section{margin:36px 0}video{width:100%;max-height:70vh;background:black}audio{width:100%}</style><h1>Quiet Origins / 天狗</h1><p>確認版v01 — 6分8.83秒。英日の固有名詞、柿の木の仏の場面、守り神の一文、動画の自然さをご確認ください。</p><img src="EP005_thumbnail_met_24145.jpg" style="width:48%"><img src="EP005_thumbnail_met_40011_DP206881.jpg" style="width:48%">'+''.join(cards)+'</html>'
 (ROOT/'deliverables/preview.html').write_text(html)
 print('DOCS',len(assets),flush=True)

def auditions():
 names={'en':['tengu','Nihon Shoki','Konjaku Monogatari','Tengu Zōshi','karasu tengu','yamabushi','Kurama','Ushiwakamaru','Minamoto no Yoshitsune','Hokusai','Kyoto'],'ja':['旻','今昔物語集','天狗草紙','烏天狗','鳶','兵法','絵手本','地の雷','仏','鞍馬','牛若丸','守り手']};locations=[]
 for l in ['en','ja']:
  cues=[c for s in read(ROOT/f'records/narration_timeline_{l}.json')['segments'] for c in s['cues']];chosen=[];seen=set()
  for name in names[l]:
   for cue in cues:
    if name in cue['text']:locations.append({'language':l,'word':name,'sentence_id':cue['id'],'start':cue['start'],'end':cue['end']})
   cue=next((c for c in cues if name in c['text']),None)
   if cue and cue['id'] not in seen:chosen.append(cue);seen.add(cue['id'])
  pieces=[];pos=0;lines=[]
  for cue in chosen:
   a,sr=sf.read(ROOT/cue['audio_file'],dtype='float32');assert sr==SR;lines.append(f"{mm(pos)} | 本編 {cue['start']:.3f}–{cue['end']:.3f}s | {cue['id']} | {cue['text']}");pieces.extend([a,np.zeros(round(1.2*SR),np.float32)]);pos+=len(a)/SR+1.2
  wav=ROOT/f'_work/pronunciation_{l}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16');ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP005_pronunciation_{l}.m4a']);(ROOT/f'deliverables/EP005_pronunciation_{l}.txt').write_text('本人試聴用。時刻は単語を含む文の範囲。人による聴感確認は未実施。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_locations.json',locations)
 save(ROOT/'records/runtime.json',{'python':sys.version,'interpreter':sys.executable,'phoneme_overrides':PHONEMES,'reading_replacements':REPLACEMENTS,'human_auditory_review':False})

def export():
 shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified'
 for d in ['records','frames','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'records').glob('*.json'):
  if p.name!='render_progress.json':shutil.copy2(p,GUIDE/'records'/p.name)
 for p in (ROOT/'review').glob('*.jpg'):
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,GUIDE/'frames'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.txt','.csv']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
 m=read(ROOT/'records/master_timeline.json');levels=read(ROOT/'records/audio_qc.json');motion=read(ROOT/'records/motion_v01.json');sub=read(ROOT/'records/subtitle_validation.json');cost=read(ROOT/'records/ai_generation_costs.json')
 guide=f'''# Quiet Origins 第5話「天狗」確認版v01

承認済み台本v02。{m['duration_seconds']:.6f}秒・{round(m['duration_seconds']*30):,}フレーム・1080p30。

Mac：`{ROOT}/deliverables/preview.html`。別環境では[非公開Draft Release]({shared['release_url']})の添付を同じフォルダへ取得してpreview.htmlを開く。Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をREST再取得しSHA-256・bytes一致。

本人試聴項目：英日の固有名詞（[時刻](records/pronunciation_locations.json)）、P08柿の木の仏の映像・語りの調子、P12守り神の一文。人による全編試聴は未実施。YouTube投稿・予約・Release公開なし。

[実測検査](records/qc_v01.json) / [素材使用](deliverables/EP005_asset_usage_v01.csv) / [動き](deliverables/EP005_motion_v01.csv) / [読み補正](records/reading_replacements.json) / [出典](deliverables/EP005_source_credits.md)。

```sh
gh api repos/{GH}/releases/{shared['release_id']}
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

再現：wom05_produce.py prepare/en/ja/timeline/audio、wom05_visuals.py、wom05_render.py pictures/package/reviews/precision/verify、wom05_validate.py layout/frames、wom05_motion.py、wom05_final_checks.py。目視記録後、wom05_delivery.py docs/share/export。
'''
 (GUIDE/'README.md').write_text(guide)
 report=f'''# 第5話「天狗」確認版v01 制作結果（2026-10-24）

**6分8.83秒・11,065フレーム・1920×1080・30fps。** [取得・確認案内](wom05_確認版_v01_20261024/README.md)。承認済み台本v02の英日本文は変更なし。本人の全編試聴は未実施。

## 構成

資料15点・AI静止画3点・Kling動画3点・模式図2点・credits1点の本編24ショット。各素材1回。共通OP4秒とエンドカードv02の10秒を追加。P12のR03、P01のR01、P03のR02をショット表に合わせ、R02は指定された一般的な茅葺屋根の遠景を含めた。

NDLは刊年・コマ番号を記し、1926年複製、1925年頃の刊本、1914年校訂本、三編の初刊1815年／1878年刊本を区別。仮名の古訓は図に書かず、仏の顔や実在の僧の姿を生成しない。資料は原本を保全して非破壊の表示クロップ。

## 実測

| 項目 | 結果 |
|---|---|
| 英日映像 | 圧縮ストリームSHA-256一致 |
| 音量 | 英{levels['languages']['en']['input_i']} LUFS・{levels['languages']['en']['input_tp']} dBTP／日{levels['languages']['ja']['input_i']} LUFS・{levels['languages']['ja']['input_tp']} dBTP |
| SRT | 英{sub['en']['count']}／日{sub['ja']['count']}。本文一致、最短1.4秒、42/23字・2行以内 |
| WAV | 48kHz・24bit・各{round(m['duration_seconds']*48000):,}サンプル |
| 動き | 24件p95÷中央値≤2.5、最大{max(x['measurement']['p95_over_median'] for x in motion['shots']):.6f} |
| ブランド | 420フレーム画素一致、エンドカードは{m['brand_intervals']['endcard'][0]:.6f}秒から最後10秒 |
| OP前の日本語待ち | {m['ja_wait_before_opening']:.6f}秒 |

英日通常版・字幕入り確認版4本を全編デコード。全158字幕×2サイズの配置を検査。詳細は検査JSONと全ショット中央フレームに保存。滑らかさの数値検査と人による全編視聴は別に扱う。

## 発音・AI・共有

初回音声と合成器解析を保全し、明確な誤読だけを読み上げ入力で補正。表示台本・SRTは無変更。「旻（みん）」は声でみん1回。英日試聴用音声・変更語・時刻を添付。本人確認は固有名詞、P08、P12と動画の自然さ。

Klingの消費記録：{json.dumps(cost,ensure_ascii=False)}。追加購入なし。AIプロンプト・生成日・原本SHAを記録。初稿3本は指定外の建物、鳥形の光、流れ星不明瞭のため不採用として保全。修正版V02は座像の顔・手の細部を楕円の柔らかなぼかしで除き、鳥が現れる間に効果を消した。処理内容・元動画・派生動画のSHAはV02_softlight_processing.jsonに記録。

[非公開Draft Release]({shared['release_url']})、ID **{shared['release_id']}**。全{len(shared['assets'])}添付、{sum(x['bytes'] for x in shared['assets']):,} bytesをRelease ID指定RESTで再取得して照合。MP4・SRT・M4A・WAV・サムネ2案・試聴音声・投稿情報・AI原本・検査記録を収録。YouTube投稿・Release公開なし。
'''
 (REPO/'new-channel/wom05_制作結果_v01_20261024.md').write_text(report)
 print('EXPORTED',GUIDE,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','auditions','share','export']);a=p.parse_args();globals()[a.stage]()
