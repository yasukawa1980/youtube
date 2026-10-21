"""EP002 review documents and explicitly requested non-public GitHub Draft Release.
Sharing never publishes a Release and uses Release-ID REST download verification.
"""
import argparse,hashlib,html,json,os,re,shutil,subprocess,math
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image
from wom02_produce import ROOT,REPO,MEDIA,MODELS,OP,END,read,save,sha,ff,measure,content,SR,PHONEMES,REPLACEMENTS
GHREPO='yasukawa1980/youtube';TAG='wom02-halloween-v01-20261022'
GUIDE=REPO/'new-channel/wom02_確認版_v01_20261022'

def mm(t):n=int(t);return f'{n//60:02}:{n%60:02}'
def docs():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start']
  chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters})
 a=read(ROOT/'records/source_assets.json')['assets'];sources=c['en']['sources']
 for l in ['en','ja']:
  intro=('Where does Halloween come from? Follow the written record through Samhain, All Hallows’ Eve, Burns’s poem, and the customs that crossed the Atlantic.' if l=='en' else 'ハロウィンはどこから来たのでしょう。サウィン、諸聖人の日の前夜、バーンズの詩、海を渡った習慣を、書き残された記録からたどります。')
  title=c[l]['title'];s=f'# Quiet Origins / EP002 — {"Upload information" if l=="en" else "投稿情報"}\n\n確認版v01。公開・予約操作は未実施。\n\n## Title\n\n{title}\n\n## Description\n\n{intro}\n\n'
  s+='This video uses synthetic narration and clearly labelled AI-generated historical reconstructions. Reconstructions are illustrative, not eyewitness records.\n\n'
  s+='Chapters\n'+'\n'.join(x['timestamp']+' '+x[l] for x in chapters)+'\n\nSources\n'
  for x in sources:s+='- '+x['id']+': '+x['title']+(' — '+x['url'] if x.get('url') else '')+'\n'
  s+='\nImage credits and terms\n'
  for x in a:s+='- '+x['id']+': '+x['credit']+' '+x['page_url']+'\n'
  s+='\nNYPL describes A02 as public domain under United States law and does not determine its status in other countries. Library of Congress records state no known restrictions. The 1938 California photograph is not the 1927 Canadian newspaper report. The Wellcome title page is Vol. II (1786), used to introduce the publication, not the page containing the claim.\n'
  s+='\nEnglish voice: Kokoro / Heart (af_heart), synthetic speech.\n日本語音声：VOICEVOX:冥鳴ひまり（C設定）。\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nAI reconstructions: R01–R03, built-in image generation; edited with explicit AI RECONSTRUCTION labels.\nMusic: original synthesized ambient score by the Quiet Origins production workflow.\n\n#Halloween #History #QuietOrigins\n'
  s+='\n## 制作・確認メモ（概要欄に貼り付けない）\n\n'
  s+=f'共通尺 {m["duration_seconds"]:.6f}秒。オープニング {m["brand_intervals"]["opening"]}、エンドカード {m["brand_intervals"]["endcard"]}。\n'
  s+='出典の状態は承認済み入力JSONを維持。H-S01・H-S02の学術資料該当ページ、H-S04の原典本文、H-S06の引用原典、1927年記事の原文などは入力で未確認のものを確認済みと扱わない。今回の素材・制作検品は台本の全史実の再検証ではない。\n'
  (ROOT/f'deliverables/EP002_upload_info_{l}.md').write_text(s)
 (ROOT/'deliverables/VOICE_CREDITS.txt').write_text('English: Kokoro / Heart (af_heart)\n日本語音声：VOICEVOX:冥鳴ひまり（C設定）\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\n')
 # Pronunciation auditions use whole native sentences, with a transcript and seek times.
 names={'en':['Samhain','Samonios','Coligny','Vallancey','Tara',"Hallowe'en",'guising','837'],'ja':['サウィン','サモニオス','ヴァランシー','グレゴリウス','オール・ハロウズ・イヴ','ガイジング','837年']}
 auditionrecords=[]
 for l in ['en','ja']:
  tl=read(ROOT/f'records/narration_timeline_{l}.json');cues=[x for seg in tl['segments'] for x in seg['cues']];chosen=[];seen=set()
  for name in names[l]:
   match=next((x for x in cues if name in x['text']),None)
   if match and match['id'] not in seen:chosen.append(match);seen.add(match['id'])
  pieces=[];pos=0;lines=[]
  for cue in chosen:
   audio,sr=sf.read(ROOT/cue['audio_file'],dtype='float32');assert sr==SR
   lines.append(f"{mm(pos)} | 本編 {cue['start']:.3f}–{cue['end']:.3f}s | {cue['id']} | {cue['text']}")
   auditionrecords.append({'language':l,'sentence_id':cue['id'],'audition_start':pos,'main_start':cue['start'],'main_end':cue['end'],'text':cue['text'],'spoken_text':cue['spoken_text'],'replacements':cue['replacements'],'time_precision':'Whole sentence containing the word; not word-aligned'})
   pieces.extend([audio,np.zeros(round(1.2*SR),np.float32)]);pos+=(len(audio)/SR)+1.2
  wav=ROOT/f'_work/pronunciation_{l}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16')
  ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP002_pronunciation_{l}.m4a'])
  (ROOT/f'deliverables/EP002_pronunciation_{l}.txt').write_text('発音確認用。本人の試聴は未実施。時刻は単語を含む文の範囲。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_auditions.json',auditionrecords)
 config={'python':subprocess.check_output([os.sys.executable,'--version'],text=True).strip(),'interpreter':os.sys.executable,'models':{str(p):sha(p) for p in [MODELS/'Kokoro82M_v1/kokoro-v1.0.onnx',MODELS/'Kokoro82M_v1/voices-v1.0.bin',MODELS/'VOICEVOX_core_0.17.0_model_0.16.4/models/vvms/1.vvm']},'phoneme_overrides':PHONEMES,'replacement_input_suggestions':REPLACEMENTS,'phoneme_note':'Spelling proposals produced wrong vowels or letter names in eSpeak; these named words are supplied as explicit phonemes. Human auditory review remains pending.'}
 save(ROOT/'records/runtime.json',config)
 # Stable copied AI images are also attached to the draft, so Claude can obtain original outputs.
 for a in read(ROOT/'records/ai_images.json'):shutil.copy2(a['local_path'],ROOT/'deliverables'/Path(a['local_path']).name)
 cards=[]
 for l,label in [('en','English'),('ja','日本語')]:
  name=f'EP002_Halloween_{l}_v01_subtitled_review_1080p30.mp4'
  cards.append(f'<section><h2>{label}・字幕入り確認版</h2><video controls preload="metadata" src="{name}"></video><p><a href="EP002_Halloween_{l}_v01_1080p30.mp4">通常版（字幕焼き込みなし）</a> / <a href="EP002_Halloween_{l}_v01_1080p30.srt">SRT</a></p><h3>固有名詞の試聴</h3><audio controls preload="metadata" src="EP002_pronunciation_{l}.m4a"></audio><p><a href="EP002_pronunciation_{l}.txt">試聴箇所・時刻</a></p></section>')
 player='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins — Halloween v01</title><style>body{max-width:1120px;margin:32px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1{color:#d8b575}a{color:#d8b575}section{margin:36px 0}video{width:100%;max-height:70vh;background:black}audio{width:100%}</style><h1>Quiet Origins / Halloween</h1><p>確認版 v01 — 6分37.67秒。最初に英語Samhainの発音、英日の冒頭からロゴへの流れ、日本語の固有名詞をご確認ください。</p><img src="EP002_thumbnail_en.jpg" style="max-width:480px;width:100%">'''+''.join(cards)+'''<script>document.querySelectorAll('video,audio').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video,audio').forEach(w=>{if(w!==v)w.pause()})));</script></html>'''
 (ROOT/'deliverables/preview.html').write_text(player)
 print('DOCUMENTS',len(auditionrecords),'audition sentences',flush=True)

def api(args,data=None):return json.loads(subprocess.check_output(['gh','api',*args],input=json.dumps(data,ensure_ascii=False).encode() if data is not None else None))
def files():
 d=ROOT/'deliverables';names=[f'EP002_Halloween_{l}_v01_1080p30.{ext}' for l in ['en','ja'] for ext in ['mp4','srt']]
 names += [f'EP002_Halloween_{l}_v01_subtitled_review_1080p30.mp4' for l in ['en','ja']]
 names += [f'EP002_{stem}_{l}.{ext}' for l in ['en','ja'] for stem,ext in [('audio','m4a'),('upload_info','md'),('pronunciation','m4a'),('pronunciation','txt')]]
 names += ['EP002_thumbnail_en.jpg','VOICE_CREDITS.txt','preview.html']+[Path(a['local_path']).name for a in read(ROOT/'records/ai_images.json')]
 return [d/n for n in names]

def share():
 assert read(ROOT/'records/qc_v01.json')['passed'] and read(ROOT/'records/subtitle_layout_validation.json')['passed']
 assert read(ROOT/'records/shot_center_validation.json')['count']==39
 selected=files();manifest=ROOT/'deliverables/SHA256SUMS_shared.txt';manifest.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in selected));selected.append(manifest)
 state=ROOT/'records/sharing.json'
 if state.exists():r=api([f'repos/{GHREPO}/releases/{read(state)["release_id"]}'])
 else:
  r=next((x for x in api([f'repos/{GHREPO}/releases?per_page=100']) if x['tag_name']==TAG),None)
  if r is None:r=api(['--method','POST',f'repos/{GHREPO}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第2話 ハロウィン 確認版v01','body':'英語メイン・日本語第2言語。6分37.666667秒、11,930フレーム、1080p30。本編37ショット＋オープニング4秒＋エンドカード20秒。字幕なし通常版・字幕入り確認版・外部字幕・音声・発音試聴・投稿情報・再現画3点。英日映像同一。本人の発音・通し試聴待ち。YouTube投稿・公開・追加支出は行っていない。','draft':True})
 assert r['draft'];save(state,{'release_id':r['id'],'draft':True,'release_url':r['html_url'],'status':'uploading'})
 for p in selected:
  prior=next((a for a in r['assets'] if a['name']==p.name),None)
  if prior:assert prior['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GHREPO],check=True)
  print('UPLOADED',p.name,flush=True)
 r=api([f'repos/{GHREPO}/releases/{r["id"]}']);assert r['draft'];checks=[]
 for p in selected:
  a=next(x for x in r['assets'] if x['name']==p.name);proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GHREPO}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();n=0
  while True:
   b=proc.stdout.read(1048576)
   if not b:break
   h.update(b);n+=len(b)
  assert proc.wait()==0 and h.hexdigest()==sha(p) and n==p.stat().st_size
  checks.append({'name':p.name,'asset_id':a['id'],'bytes':n,'sha256':h.hexdigest(),'rest_download_verified':True});print('REST VERIFIED',p.name,flush=True)
 save(state,{'release_id':r['id'],'release_url':r['html_url'],'draft':True,'status':'verified','assets':checks})
 print('SHARED',r['id'],len(checks),flush=True)


def export():
 sharing=read(ROOT/'records/sharing.json');assert sharing['status']=='verified' and sharing['draft']
 qc=read(ROOT/'records/qc_v01.json');m=read(ROOT/'records/master_timeline.json');layout=read(ROOT/'records/subtitle_layout_validation.json')
 for d in ['records','frames','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
 recordnames=['request.json','runtime.json','ai_images.json','source_assets.json','source_preservation.json','master_timeline.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_cues_en.json','subtitle_cues_ja.json','subtitle_validation.json','subtitle_layout_validation.json','sentence_boundary_validation.json','reading_replacements.json','pronunciation_locations.json','pronunciation_auditions.json','visual_manifest.json','render_shots.json','shot_center_validation.json','visual_review.json','audio_qc.json','qc_v01.json','sharing.json','chapters.json']
 for n in recordnames:shutil.copy2(ROOT/'records'/n,GUIDE/'records'/n)
 for p in (ROOT/'review').glob('*.jpg'):
  if p.name.startswith(('final_storyboard','subtitles_')):
   im=Image.open(p);assert max(im.size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,GUIDE/'frames'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.txt','.html']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
 canonical=REPO/'new-channel/episodes/EP002_Halloween';(canonical/'deliverables').mkdir(parents=True,exist_ok=True)
 for n in ['ai_images.json','runtime.json','master_timeline.json','reading_replacements.json','pronunciation_locations.json','qc_v01.json','sharing.json','chapters.json']:shutil.copy2(ROOT/'records'/n,canonical/'records'/n)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md'] or p.name=='VOICE_CREDITS.txt':shutil.copy2(p,canonical/'deliverables'/p.name)
 previews=REPO/'new-channel/サムネ確認用/wom02'
 for a in read(ROOT/'records/ai_images.json'):
  im=Image.open(a['local_path']).convert('RGB');im.thumbnail((1280,1280));im.save(previews/(a['id']+'_再現画_確認.jpg'),quality=87,optimize=True)
 frames='\n'.join(f'- [全ショット一覧 {i}](frames/final_storyboard_{i}.jpg)' for i in range(1,5))
 table='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in sharing['assets'])
 guide=f"""# Quiet Origins 第2話「ハロウィン」確認版 v01

2026-10-22制作。英日共通 **6分37.666667秒／11,930フレーム／1920×1080・30fps**。
本人の通し試聴・発音確認待ち。YouTube投稿・Release公開なし。

## Macでの再生

保存先：`{ROOT}`。`deliverables/preview.html` を開くと、英日字幕入り確認版と発音試聴を選べる。通常版は字幕焼き込みなし。MP4・M4A・原寸画像はGitに入れていない。

## Claudeからの取得

[非公開Draft Release]({sharing['release_url']})、Release ID **{sharing['release_id']}**。全{len(sharing['assets'])}添付を、Release IDによるメタデータ取得後、各Asset IDのRESTから再取得してSHA-256・サイズを照合済み。

```sh
gh api repos/{GHREPO}/releases/{sharing['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GHREPO}/releases/assets/ASSET_ID > FILE_NAME
```

添付を同じフォルダに保存すれば `preview.html` から再生できる。[ハッシュ一覧](deliverables/SHA256SUMS_shared.txt)。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}

## 検品資料

{frames}

- [音声・映像の実測](records/qc_v01.json)
- [全字幕2サイズの配置検査](records/subtitle_layout_validation.json)、[全字幕の重ね描き画像](frames/)
- [台本どおりの読み上げ文と時刻：英語](records/narration_timeline_en.json)／[日本語](records/narration_timeline_ja.json)
- [読み上げ置き換え一覧](records/reading_replacements.json)／[固有名詞33箇所の時刻範囲](records/pronunciation_locations.json)
- [再現画3点・実行プロンプト・SHA-256](records/ai_images.json)
- [原素材と共通映像の保全](records/source_preservation.json)

## 再現手順

Python 3.12に `../requirements_wom02.txt` の無料依存関係を入れ、既存のKokoro/VOICEVOXモデルを使う。使用環境は [runtime.json](records/runtime.json)。生成済みAI画像は上のDraft Releaseから指定素材フォルダへ置ける。`prepare` は保存済み `episodes/EP002_Halloween/records/ai_images.json` を読む。

```sh
python new-channel/wom02_produce.py prepare
python new-channel/wom02_produce.py en
python new-channel/wom02_produce.py ja
python new-channel/wom02_produce.py timeline
python new-channel/wom02_visuals.py
python new-channel/wom02_produce.py audio
python new-channel/wom02_render.py pictures
python new-channel/wom02_render.py package
python new-channel/wom02_render.py reviews
python new-channel/wom02_validate.py layout
python new-channel/wom02_validate.py frames
python new-channel/wom02_render.py verify
python new-channel/wom02_delivery.py docs
```

`share` は非公開Draft Releaseの作成・添付・再取得を行う。既存添付とハッシュが違う場合は上書きせず停止する。修正版は別バージョンにする。今回の本編では既存オープニングv02・エンドカードv01の音量を保持し、接続周辺のBGMだけフェードさせた。
"""
 (GUIDE/'README.md').write_text(guide)
 en=qc['files'][0]['loudness'];ja=qc['files'][2]['loudness'];srt=layout['actual_srt_checks']
 report=f"""# Quiet Origins 第2話「ハロウィン」制作結果 v01（2026-10-22）

[制作依頼](wom02_制作依頼_20261022.md)の確認版を制作。[再生・Claude取得・全検品資料](wom02_確認版_v01_20261022/README.md)。

## 完成物

- 英日それぞれの通常版MP4、字幕入り確認版MP4、外部SRT、主音声M4A。
- 英語サムネ、英日投稿情報、VOICEVOXを含むクレジット、再生ページ。
- 固有名詞の試聴M4Aと台本・時刻一覧。英語8文、日本語6文（含む文単位で切り出し）。
- 組み込み画像生成による再現画R01〜R03、実行プロンプト、SHA-256。原寸3枚はMacとDraft Releaseに保存。
- 全39ショットの実動画中央フレーム一覧、英日全字幕をFontSize 14／26で重ねた確認一覧。

Mac保存先：`{ROOT}`。元のA01〜A07と第1話共通映像はハッシュ一致で保全。既存の動画や第1話の投稿状態は変更していない。

## 実測検品

| 項目 | 結果 |
|---|---|
| 共通尺 | {m['duration_seconds']:.6f}秒（6分37.67秒） |
| 映像 | 1920×1080、30fps、11,930フレーム。通常版の英日映像ストリームSHA-256一致 |
| フレーム時刻 | 4動画ともPTSは1/15360のtime baseで512刻み＝厳密な1/30秒。重複・欠落なし |
| 全編デコード | 通常版・字幕入り版の英日4本、成功 |
| 英語音量 | {en['input_i']} LUFS、{en['input_tp']} dBTP |
| 日本語音量 | {ja['input_i']} LUFS、{ja['input_tp']} dBTP |
| BGM | 語り区間を基準に−33.5 dBFS、間で+4dB。承認済み共通映像の音量は保持 |
| 無音 | 完成ミックスを−60dB閾値で検査し、1秒以上の無音なし。語りの意図した間にはBGMあり |
| SRT本文 | 英85件・日87件。入力JSONと一致（レイアウト用の改行・空白のみ正規化） |
| SRT最短・行長 | 英{srt['en']['minimum_seconds']:.3f}秒／最大42字、日{srt['ja']['minimum_seconds']:.3f}秒／最大22字。2行以内 |
| 文の切れ目 | 独立合成した文の実測境界と、挿入した無音サンプルを照合済み。文中のページ送りは文字量配分で、単語強制アラインメントではない |
| 画面配置 | 文字・図・資料の配置はy≤700。最大ズーム後も範囲内。全172字幕×2サイズ＝344描画の非重複を画素で確認 |
| 字幕最上端 | FontSize 14：英938px／日936px。FontSize 26：英855px／日850px |
| オープニング | H02後、38.666667〜42.666667秒（承認済み4秒v02） |
| 日本語→ロゴの待ち | {m['ja_wait_before_opening']:.3f}秒。3秒以内のため文間の追加引き延ばし不要 |
| エンドカード | 377.666667〜397.666667秒（承認済み20秒v01） |
| A07 | 1938年・米国カリフォルニアの札。1927年の記事の文が英日とも終わった後、318.000秒から表示（フレーム丸めの誤差範囲内） |

## 読みと試聴

依頼の綴り案をeSpeakで検査すると、Sow-inが `/soʊ/`、大文字のGUYやLANなどが文字読みになるため、6語を発音記号で明示した。Samhainは `sˈaʊɪn`。全置き換えは [読み上げ一覧](wom02_確認版_v01_20261022/records/reading_replacements.json)、実行用記号は [runtime.json](wom02_確認版_v01_20261022/records/runtime.json)。表示用台本・字幕は変更していない。日本語は冥鳴ひまりCの役割別設定で、英語に合わせた加速なし。英語はHeartの第1話基本設定0.82を使用し、第1話専用の区間ごとの速度表は移植していない。

**発音記号・波形・数値の検査は行ったが、人による聴感確認は未実施。** 最初に英語のSamhain、続いて冒頭からロゴへの流れ、日本語の固有名詞を試聴してほしい。時刻記録は各語を含む文の範囲で、単語の厳密な開始時刻とは区別する。

## 画像と台本の扱い

資料を上部に置き、同じ画像の拡大・強いぼかし・35%の明るさで背景を埋めた。指定のdetail場面は全体＋部分拡大。図解は濃紺、文字は最小限。D_trailは作品年代に従いA03→A06→A01→A02の順に並べた。コリニー暦の拡大は碑文の部分であり、特定の文字列をSamoniosと同定する札は付けていない。

A06は第2巻の扉、A07は1938年の写真という区別を保持。入力で未確認とされた学術資料の該当ページや原典本文を、今回の制作で確認済みとは扱っていない。R01はタラの正確な復元ではなく、R01〜R03すべてにAI再現の札を付けた。

## 共有

[非公開Draft Release]({sharing['release_url']})、Release ID **{sharing['release_id']}**。全{len(sharing['assets'])}添付のREST再取得とSHA-256・サイズ一致を確認。取得手順・Asset IDは[確認版の入口](wom02_確認版_v01_20261022/README.md)。追加契約・購入・YouTube投稿・Release公開は行っていない。

制作コード・台帳・字幕・投稿情報・確認JPGを`bgm/production`へ共有する。動画・音声・原寸画像・中間ファイルはGit対象外。指定SSDへの同期は未実施。
"""
 (REPO/'new-channel/wom02_制作結果_v01_20261022.md').write_text(report)
 print('EXPORTED',GUIDE,flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','export']);args=p.parse_args();globals()[args.stage]()
