"""EP004 review documents and private draft delivery; never publishes a release."""
import argparse,csv,hashlib,json,shutil,subprocess,sys,zipfile
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image
from wom04_produce import ROOT,REPO,MEDIA,MODELS,read,save,sha,ff,content,SR,PHONEMES,REPLACEMENTS
GH='yasukawa1980/youtube';TAG='wom04-pandora-v01-exact-20261023';GUIDE=REPO/'new-channel/wom04_確認版_v01_20261023'
def api(args,data=None):
 p=subprocess.run(['gh','api',*args],input=json.dumps(data) if data is not None else None,capture_output=True,text=True,check=True);return json.loads(p.stdout)
def mm(t):n=int(t);return f'{n//60:02}:{n%60:02}'
def docs():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters})
 shots=read(ROOT/'records/render_shots.json');usage=[{'asset_id':s['key'],'segment':s['segment_id'],'shot':i+1,'start':s['start'],'end':s['end'],'uses':1} for i,s in enumerate(shots) if s['segment_id']!='BRAND'];assert len({s['asset_id'] for s in usage})==len(usage)==29
 with (ROOT/'deliverables/EP004_asset_usage_v01.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(usage[0]));w.writeheader();w.writerows(usage)
 save(ROOT/'records/asset_usage_v01.json',usage)
 used={x['asset_id'] for x in usage};a=[x for x in read(ROOT/'records/source_assets.json')['assets'] if x['asset_id'] in used]
 full_credits='# EP004 — Source image credits\n\n'
 for x in a:
  full_credits+=f'## {x["asset_id"]} — {x["title"]}\n\n{x["date"]}; {x["museum"]}; {x["accession_number"]}. {x["artist"]}\n\n{x["object_url"]}\n\nRights: {x["rights_status"]}. {x["rights_evidence"]}\n{x["rights_url"]}\n\n'
 (ROOT/'deliverables/EP004_source_credits.md').write_text(full_credits)
 sources=[('Hesiod, Works and Days 42–105; H. G. Evelyn-White, 1914','https://www.theoi.com/Text/HesiodWorksDays.html'),('Hesiod, Theogony 570–612; H. G. Evelyn-White, 1914','https://www.theoi.com/Text/HesiodTheogony.html'),('Pausanias 1.24.7; W. H. S. Jones, 1918','https://www.theoi.com/Text/Pausanias1B.html#24'),('Babrius 58; James Davies, 1860, p.52','https://elfinspell.com/ClassicalTexts/Babrius/Part1-Fables40-79.html'),('Erasmus, Adagia I.i.31; Aldus, Venice 1508, f.12r; ULiège','https://donum.uliege.be/handle/2268.1/10063'),('Apuleius, Metamorphoses 6.16–21; William Adlington, 1566 (1639 reprint)','https://www.gutenberg.org/files/1666/1666-h/1666-h.htm')]
 for l in ['en','ja']:
  intro=("Pandora's familiar box began as a large storage jar. Follow the vessels through Hesiod, a fable by Babrius, Erasmus's printed book, and later paintings. The sources tell different stories about what was inside." if l=='en' else 'パンドラの「箱」は、古い資料では大きな壺でした。ヘシオドス、バブリオスの寓話、エラスムスの刊本、後世の絵画をたどり、容器と、その中にあったものの違いを見ていきます。')
  disclosure=('This video uses synthetic narration. Labelled AI reconstructions illustrate atmosphere; they are not historical evidence or exact reconstructions of real sites. Modern interpretations are distinguished from ancient accounts.' if l=='en' else '音声には合成音声を使用しています。AIによる再現には札を付け、雰囲気を示す挿絵として用いています。史料そのものや実在の遺跡の正確な復元ではありません。現代の解釈と古代の記述を区別して紹介します。')
  s=f'# Quiet Origins / EP004 — {"Upload information" if l=="en" else "投稿情報"}\n\n確認版v01。公開・予約操作は未実施。\n\n## Title\n\n{c[l]["title"]}\n\n## Description\n\n{intro}\n\n{disclosure}\n\nChapters\n'
  s+='\n'.join(x['timestamp']+' '+x[l] for x in chapters)+'\n\nSources\n'
  s+='\n'.join(f'- {title}\n  {url}' for title,url in sources)+'\n\nReference: Dora and Erwin Panofsky, Pandora’s Box: The Changing Aspects of a Mythical Symbol (1956).\n\nImage credits — Public Domain / CC0\n'
  for x in a:s+=f'- {x["asset_id"]} / {x["museum"]} / {x["accession_number"]}: {x["object_url"]}\n'
  s+='\nPhotographs: A01 Jastrow (PD; distributed edit Ptyx); A02 Shonagon (CC0); A09 Jona Lendering / Livius (CC0).\nEnglish voice: Kokoro / Heart (af_heart), synthetic speech.\n日本語音声：VOICEVOX:冥鳴ひまり（C設定）。\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nAI stills: OpenAI image generation — R01–R05.\nAI video: Kling AI 3.0 — V01–V03.\nDiagrams and original synthesized ambient music: Quiet Origins.\n\n#Pandora #GreekMythology #QuietOrigins\n'
  assert len(s.split('## Description\n\n',1)[1])<=5000 and len(c[l]['title'])<=100
  s+=f'\n## 制作・確認メモ（概要欄に貼り付けない）\n\n台本v02a。共通尺 {m["duration_seconds"]:.6f}秒。エンドカード開始 {m["brand_intervals"]["endcard"][0]:.6f}秒。投稿用の英日WAVは48kHz・24bit、各{round(m["duration_seconds"]*48000):,}サンプル。全作品の名称・年代・権利・写真作者はEP004_source_credits.mdに収録。\n'
  s+='原典の追加確認3件は台本と一致。表示台本は変更なし。本人の全編試聴・動きの自然さの確認は未実施。\n'
  (ROOT/f'deliverables/EP004_upload_info_{l}.md').write_text(s)
 names={'en':['Hesiod','Theogony','Hephaestus','Epimetheus','pithos','elpis','Pausanias','Babrius','pyxis','Psyche','Erasmus','Adages'],'ja':['神統記','ヘパイストス','エピメテウス','ピトス','ピュクシス','壺','櫃','格言集','鍛冶','小箱']};auditions=[];locations=[]
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
  wav=ROOT/f'_work/pronunciation_{l}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16');ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP004_pronunciation_{l}.m4a']);(ROOT/f'deliverables/EP004_pronunciation_{l}.txt').write_text('本人の試聴用。時刻は単語を含む文の範囲。聴感確認は未実施。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_auditions.json',auditions);save(ROOT/'records/pronunciation_locations.json',locations)
 save(ROOT/'records/runtime.json',{'python':sys.version,'interpreter':sys.executable,'models':{str(p):sha(p) for p in [MODELS/'Kokoro82M_v1/kokoro-v1.0.onnx',MODELS/'Kokoro82M_v1/voices-v1.0.bin',MODELS/'VOICEVOX_core_0.17.0_model_0.16.4/models/vvms/1.vvm']},'phoneme_overrides':PHONEMES,'reading_replacements':REPLACEMENTS,'human_auditory_review':False})
 for kind in ['ai_images','ai_videos']:
  for x in read(ROOT/f'records/{kind}.json'):shutil.copy2(x['local_path'],ROOT/'deliverables'/Path(x['local_path']).name)
 cards=[]
 for l,label in [('en','English'),('ja','日本語')]:
  cards.append(f'<section><h2>{label}</h2><video controls preload="metadata" src="EP004_Pandora_{l}_v01_subtitled_review_1080p30.mp4"></video><p><a href="EP004_Pandora_{l}_v01_1080p30.mp4">通常版</a> / <a href="EP004_Pandora_{l}_v01_1080p30.srt">SRT</a> / <a href="EP004_audio_{l}.wav">投稿用WAV</a></p><h3>固有名詞の試聴</h3><audio controls src="EP004_pronunciation_{l}.m4a"></audio><p><a href="EP004_pronunciation_{l}.txt">試聴箇所と本編時刻</a></p></section>')
 player='<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins — Pandora v01</title><style>body{max-width:1120px;margin:32px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,a{color:#d8b575}section{margin:36px 0}video{width:100%;max-height:70vh;background:black}audio{width:100%}</style><h1>Quiet Origins / Pandora</h1><p>確認版 v01 — 7分9.57秒。固有名詞、冒頭からロゴへの流れ、P05の語りの調子、動画の自然さをご確認ください。</p><img src="EP004_thumbnail_A01.jpg" style="width:48%"><img src="EP004_thumbnail_A21.jpg" style="width:48%">'+''.join(cards)+'<script>document.querySelectorAll("video,audio").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video,audio").forEach(w=>{if(w!==v)w.pause()})));</script></html>'
 (ROOT/'deliverables/preview.html').write_text(player)
 print('DOCS',len(a),'museum objects',len(locations),'pronunciation locations',flush=True)

def share():
 qc=read(ROOT/'records/qc_v01.json');assert qc['passed'];assert read(ROOT/'records/motion_v01.json')['passed'];assert read(ROOT/'records/visual_review.json')['passed'];assert read(ROOT/'records/subtitle_layout_validation.json')['passed']
 assert read(ROOT/'records/final_checks.json')['passed'];wav=read(ROOT/'records/wav_sample_validation.json');assert wav['passed']
 assert read(ROOT/'records/container_precision.json')['passed']
 for f in wav['files']:assert sha(ROOT/'deliverables'/f['file'])==f['sha256']
 visual=read(ROOT/'records/visual_review.json');assert visual['video_sha256']==sha(ROOT/'deliverables/EP004_Pandora_en_v01_1080p30.mp4');assert visual['visual_manifest_sha256']==sha(ROOT/'records/visual_manifest.json');assert visual['render_shots_sha256']==sha(ROOT/'records/render_shots.json')
 for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 for p in (ROOT/'records').glob('*.json'):
  if p.name not in ['sharing.json','render_progress.json']:shutil.copy2(p,ROOT/'deliverables'/p.name)
 with zipfile.ZipFile(ROOT/'deliverables/EP004_review_frames.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((ROOT/'review').glob('*.jpg')):z.write(p,p.name)
 files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.name!='SHA256SUMS_shared.txt');hashfile=ROOT/'deliverables/SHA256SUMS_shared.txt';hashfile.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(hashfile)
 state=ROOT/'records/sharing.json'
 r=api([f'repos/{GH}/releases/{read(state)["release_id"]}']) if state.exists() and read(state).get('status')!='superseded_before_final_delivery' else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
 if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第4話 パンドラ v01（英日確認版）','body':'承認済み台本v02a。英日共通映像429.566667秒・12887フレーム。通常版、字幕入り確認版、SRT、M4A、サンプル一致WAV、サムネ2案、試聴音声、原寸AI素材、検査記録。本人の試聴・動きの自然さの確認待ち。Releaseは非公開Draftを維持し、YouTube投稿なし。','draft':True})
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
 for p in (ROOT/'records').glob('*.json'):
  if p.name!='render_progress.json':shutil.copy2(p,GUIDE/'records'/p.name)
 for p in (ROOT/'review').glob('*.jpg'):
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,GUIDE/'frames'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.txt','.csv']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
 m=read(ROOT/'records/master_timeline.json');qc=read(ROOT/'records/qc_v01.json');mo=read(ROOT/'records/motion_v01.json');subs=read(ROOT/'records/subtitle_validation.json');levels=read(ROOT/'records/audio_qc.json')
 table='\n'.join(f'| {x["name"]} | {x["asset_id"]} | {x["bytes"]:,} |' for x in shared['assets'])
 (GUIDE/'README.md').write_text(f"""# Quiet Origins 第4話「パンドラ」確認版v01

台本v02a。{m['duration_seconds']:.6f}秒・{round(m['duration_seconds']*30):,}フレーム・1080p30。
Mac：`{ROOT}`。`deliverables/preview.html` で確認できます。別環境ではDraftの全添付を同じフォルダに保存してpreview.htmlを開いてください。Gitにはコード・資料・記録・字幕・小型JPGだけを保存しています。

[非公開Draft Release]({shared['release_url']})。Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をREST再取得し、SHA-256・bytes一致。本人試聴待ち。

```sh
gh api repos/{GH}/releases/{shared['release_id']}
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

[検査](records/qc_v01.json) / [素材使用](deliverables/EP004_asset_usage_v01.csv) / [動き](deliverables/EP004_motion_v01.csv) / [読み補正](records/reading_replacements.json) / [試聴時刻](records/pronunciation_locations.json)。時刻は単語を含む文の範囲です。

本人試聴項目：Hephaestus、Epimetheus、pithos、elpis、Pausanias、Babrius、pyxis、Psyche。日本語のヘパイストス、エピメテウス、ピトス、ピュクシス、壺、櫃、格言集。冒頭からOPへの流れとP05の語りの調子。人による全編再生・聴感確認は未実施。

再現：wom04_produce.py prepare/en/ja/timeline/audio、wom04_visuals.py、wom04_render.py pictures/package/reviews/precision/verify、wom04_validate.py layout/frames、wom04_motion.py、wom04_final_checks.py。画像・動画は保存原本を使用し、自動再生成しません。目視確認記録後、wom04_delivery.py docs/share/export。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}
""")
 peak=max(x['measurement']['p95_over_median'] for x in mo['shots'])
 report=f"""# 第4話「パンドラ」確認版v01 制作結果（2026-10-23）

承認済み台本v02aから制作。**{m['duration_seconds']:.6f}秒・{round(m['duration_seconds']*30):,}フレーム・1920×1080・30fps。** [取得・再生案内](wom04_確認版_v01_20261023/README.md)。本人の試聴は未実施。

## 台本・構成

原典追加確認3件は台本と一致し、f26ed6dで共有済み。英日表示台本は無変更、日本語は壺に統一。本編29ショット＋共通ブランド2カット。博物館資料18件・再現画5枚・AI動画3本・模式図2点・クレジット1点を各1回使用。

指定の裸体回避クロップを適用。A01は全体から縁側へ3%の緩い寄り。A09は縦820pxの枠内、台座拡大なし。A12は全体とPixideの箇所を並置し、枠・下線なし。資料の画素に生成加工はしていない。

AI静止画は組み込みOpenAI image generation。Kling動画は既存契約枠内で生成し、V01の壁付き暖炉、V03の現代的扉が映る初稿を不採用として保全。修正版を採用。生成・クレジット・原本SHAはai_videos.jsonとai_generation_costs.json。追加契約・購入なし。

## 実測検査

| 項目 | 結果 |
|---|---|
| 全編デコード | 英日通常版・字幕入り版4本、1/30秒PTS・各{round(m['duration_seconds']*30):,}フレーム |
| 映像共通 | 英日通常版の圧縮映像ストリームSHA-256一致 |
| 音量 | 英{levels['languages']['en']['input_i']} LUFS / {levels['languages']['en']['input_tp']} dBTP、日{levels['languages']['ja']['input_i']} LUFS / {levels['languages']['ja']['input_tp']} dBTP |
| BGM | 語り下{levels['bgm_during_narration_dbfs']:.3f} dBFS、間+4 dB |
| 無音 | −60 dB・1秒以上0件 |
| WAV | 英日48kHz・24bit・各{round(m['duration_seconds']*48000):,}サンプル、動画と尺一致 |
| SRT | 英{subs['en']['count']}・日{subs['ja']['count']}。台本と空白・改行以外一致、最短1.4秒以上、42/23字・2行以内 |
| 字幕配置 | 全197字幕×14/26＝394描画、図解・クレジットy≤700、文字重なりなし |
| 動き | 29件すべてp95÷中央値≤2.5、最大{peak:.6f} |
| ブランド | 共通OP120・エンドカード300フレーム、完成映像から抽出した画素が承認済み素材と一致 |
| エンドカード | {m['brand_intervals']['endcard'][0]:.6f}秒から正確な最後10秒 |
| OP前の日本語待ち | {m['ja_wait_before_opening']:.6f}秒 |

[全検査記録](wom04_確認版_v01_20261023/records/final_checks.json)。原本・AI素材のSHA-256照合済み。全ショット中央フレーム、全字幕重ね描き、AI動画の複数時点を確認。滑らかさは数値測定であり、人による全編再生確認は未実施。

## 発音と本人確認

初回は置換なしで生成し保全。合成器の音素・カナ解析に基づき明らかな読み違いだけ補正。聴感で確認済みとはしていない。補正一覧・単語を含む文の時刻・初回解析・英日試聴音声を添付。台本表示は変更なし。

本人試聴は固有名詞、冒頭〜OP、P05の語りの調子、動画の自然さ。詳しくは[案内](wom04_確認版_v01_20261023/README.md)。

## 共有

新規[非公開Draft Release]({shared['release_url']})、ID **{shared['release_id']}**。全{len(shared['assets'])}添付・{sum(x['bytes'] for x in shared['assets']):,} bytesをRelease ID指定RESTで再取得し、SHA-256・サイズ一致。英日MP4・字幕入り確認版・SRT・M4A・WAV・サムネ2案・試聴音声・投稿情報・原寸AI素材・検査記録を収録。

投稿情報に訳者・年・写真作者3名と採用作品18件を記載。Panofsky 1956は参考書として書名のみ。英日概要欄5,000字以内、題名100字以内。YouTube投稿・予約・Release公開なし。

制作ファイルと小型の検査資料はリモート最新履歴上でコミットしてbgm/productionへpush。分岐した既存履歴は送信していない。
"""
 (REPO/'new-channel/wom04_制作結果_v01_20261023.md').write_text(report)
 print('EXPORTED',GUIDE,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','export']);a=p.parse_args();globals()[a.stage]()
