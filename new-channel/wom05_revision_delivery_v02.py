"""EP005 revision v02: upload text and verified private draft delivery."""
import argparse,html,json,re,shutil,subprocess,time,zipfile,hashlib
from pathlib import Path
from PIL import Image
from wom05_revision_v02 import ROOT,V1,REPO,read,save,sha
GH='yasukawa1980/youtube';TAG='wom05-tengu-v02-20261024';GUIDE=REPO/'new-channel/wom05_確認版_v02_20261024'
def api(args,data=None):
 p=subprocess.run(['gh','api',*args],input=json.dumps(data) if data is not None else None,capture_output=True,text=True,check=True);return json.loads(p.stdout)
def docs():
 used={s['key'] for s in read(V1/'records/render_shots.json')};assets=[a for a in read(V1/'records/source_assets.json')['assets'] if a['key'] in used]
 chapters=read(ROOT/'records/chapters.json')['chapters'];credits=[]
 for museum in dict.fromkeys(a['museum'] for a in assets):
  credits.append(museum+':')
  for a in assets:
   if a['museum']!=museum:continue
   artist=a['artist'].split('\n')[0] if a['artist'] else ''
   title=html.unescape(re.sub('<[^>]+>','',a['title']));date=a['date'] or 'date not specified'
   line='- '+(artist+', ' if artist else '')+f'{title}, {date}. {a["accession"]}'
   if a['key'].startswith('ndl'):line+='; コマ '+a['page'].rsplit('/',1)[-1]
   credits.append(line)
  credits.append(next(a['page'] for a in assets if a['museum']==museum))
 sources=[('W. G. Aston, Nihongi, vol. II (1896), Book XXIII, pp. 167–168','https://en.wikisource.org/wiki/Nihongi/Book_XXIII'),('Nihon Shoki, vol. 23: 1926 facsimile, frame 10','https://dl.ndl.go.jp/pid/1182143/1/10'),('Shiji, Tianguan shu: c. 1925 printed edition, frame 87','https://dl.ndl.go.jp/pid/958959/1/87'),('Konjaku Monogatari-shu 20-2 (transcription consulted)','https://yatanavi.org/text/k_konjaku/k_konjaku20-2'),('Konjaku Monogatari-shu 20-3 (transcription consulted)','https://yatanavi.org/text/k_konjaku/k_konjaku20-3'),('Uji Shui Monogatari, tale 32 (transcription consulted)','https://yatanavi.org/text/yomeiuji/uji032')]
 for lang in ['en','ja']:
  c=read(ROOT/'records'/('content_en.json' if lang=='en' else 'content.json'))
  old=(V1/f'deliverables/EP005_upload_info_{lang}.md').read_text();intro=old.split('## Description\n\n')[1].split('\n\nChapters')[0]
  body=intro+'\n\n'+('Chapters' if lang=='en' else 'チャプター')+'\n'+'\n'.join(x['timestamp']+' '+x[lang] for x in chapters)
  body+='\n\n'+('Sources' if lang=='en' else '出典')+'\n'+'\n'.join('- '+a+' — '+b for a,b in sources)
  body+='\n'+('References only (images not used): Tengu Zoshi (c. 1296); Zegaibo-e (c. 1354). Modern annotations are not quoted.' if lang=='en' else '参考（画像不使用）：『天狗草紙』（1296年ごろ）、『是害房絵』（1354年ごろ）。現代の注釈は引用していません。')
  body+='\n\n'+('Images — Public Domain / CC0' if lang=='en' else '画像（パブリックドメイン／CC0）')+'\n'+'\n'.join(credits)
  if lang=='en':body+='\n\nAI reconstructions (still images): OpenAI image generation. AI video clips: Kling AI, with local editing. All are labelled "AI RECONSTRUCTION" on screen. Diagrams: Quiet Origins.\nEnglish voice: Kokoro / Heart (af_heart), synthetic speech.\nJapanese voice: VOICEVOX:冥鳴ひまり — https://www.meimeihimari.com/terms-of-use / https://voicevox.hiroshiba.jp/\nMusic: original ambient score by Quiet Origins.\n\n#Tengu #JapaneseFolklore #QuietOrigins\n'
  else:body+='\n\nAIによる再現画：OpenAIの画像生成。AIによる再現映像：Kling AI（一部を編集）。画面には「AI RECONSTRUCTION｜AIによる再現」と表示しています。図解：Quiet Origins。\n英語の声：Kokoro / Heart (af_heart)、合成音声。\n日本語の声：VOICEVOX:冥鳴ひまり — https://www.meimeihimari.com/terms-of-use / https://voicevox.hiroshiba.jp/\n音楽：Quiet Origins によるオリジナルのアンビエント。\n\n#天狗 #日本の伝説 #QuietOrigins\n'
  assert len(body)<=5000,(lang,len(body))
  (ROOT/f'deliverables/EP005_upload_info_{lang}.md').write_text('# EP005 投稿情報 v02\n\n## '+('Title' if lang=='en' else 'タイトル')+'\n\n'+c['title']+'\n\n## '+('Description' if lang=='en' else '説明')+'\n\n'+body)
  print('DESCRIPTION',lang,len(body),flush=True)
 preview=(V1/'deliverables/preview.html').read_text().replace('v01','v02');preview=preview.replace('確認版v02 —','修正版v02（音声・字幕はv01と同じ）—');(ROOT/'deliverables/preview.html').write_text(preview)
 (ROOT/'deliverables/review_notes.md').write_text('第5話 天狗 修正版v02\n\n英日の音声・字幕・総尺はv01と同じ。サムネイル第一候補はEP005_thumbnail_met_24145.jpg。修正箇所はreview_frames.zip参照。本人による聴感確認は未実施。P11は英語の語時刻を優先し、日本語の該当語より約4.35秒／6.72秒遅れて絵が切り替わります。\n')

def share():
 qc=read(ROOT/'records/qc_v02.json');assert qc['passed'];assert read(ROOT/'records/motion_v02.json')['passed'];visual=read(ROOT/'records/visual_review.json');assert visual['passed'] and visual['video_sha256']==sha(ROOT/'deliverables/EP005_Tengu_en_v02_1080p30.mp4')
 for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
 for p in (ROOT/'records').glob('*.json'):
  if p.name not in ['sharing.json','transfer_checkpoint.json']:shutil.copy2(p,ROOT/'deliverables'/p.name)
 with zipfile.ZipFile(ROOT/'deliverables/EP005_v02_review_frames.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted((ROOT/'review').glob('*.jpg')):z.write(p,p.name)
 files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.name!='SHA256SUMS_shared.txt');hfile=ROOT/'deliverables/SHA256SUMS_shared.txt';hfile.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(hfile)
 state=ROOT/'records/sharing.json';r=api([f'repos/{GH}/releases/{read(state)["release_id"]}']) if state.exists() else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
 if r is None:r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins 第5話 天狗 v02（映像修正版）','body':'Claude依頼の映像・投稿情報を修正。音声・SRT・台本・総尺をv01と照合。変更対象外の全フレームを画素比較。本人試聴待ち、YouTube投稿なし。非公開Draftを維持。','draft':True})
 assert r['draft'];save(state,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
 for p in files:
  old=next((a for a in r['assets'] if a['name']==p.name),None)
  if old:assert old['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
  print('UPLOADED',p.name,flush=True)
 r=api([f'repos/{GH}/releases/{r["id"]}']);assert r['draft'] and len(r['assets'])==len(files);checks=[]
 checkpoint=ROOT/'records/transfer_checkpoint.json';prior=read(checkpoint) if checkpoint.exists() else []
 for p in files:
  a=next(a for a in r['assets'] if a['name']==p.name);known=next((c for c in prior if c['asset_id']==a['id'] and c['sha256']==sha(p) and a['digest']=='sha256:'+c['sha256']),None)
  if known:checks.append(known);continue
  for attempt in range(3):
   proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();count=0
   while True:
    b=proc.stdout.read(1048576)
    if not b:break
    h.update(b);count+=len(b)
   if proc.wait()==0 and h.hexdigest()==sha(p) and count==p.stat().st_size and a['digest']=='sha256:'+h.hexdigest():break
   if attempt==2:raise RuntimeError('REST verification failed: '+p.name)
   time.sleep(2)
  checks.append({'name':p.name,'asset_id':a['id'],'bytes':count,'sha256':h.hexdigest(),'rest_download_verified':True});save(checkpoint,checks);print('REST VERIFIED',p.name,flush=True)
 save(state,{'release_id':r['id'],'draft':True,'status':'verified','release_url':r['html_url'],'assets':checks});print('SHARED',r['id'],len(checks),flush=True)

def export():
 shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified';qc=read(ROOT/'records/qc_v02.json');motion=read(ROOT/'records/motion_v02.json');ai=read(ROOT/'records/ai_revision.json')
 for d in ['records','frames','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'records').glob('*.json'):
  if p.name!='transfer_checkpoint.json':shutil.copy2(p,GUIDE/'records'/p.name)
 for p in (ROOT/'review').glob('*.jpg'):
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000;shutil.copy2(p,GUIDE/'frames'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.md','.txt','.csv','.srt']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
 (GUIDE/'README.md').write_text(f'''# 第5話 天狗 v02 確認案内

6分8.83秒、11,065フレーム、1080p30。英日音声・SRT・総尺・台本はv01と同じ。

Mac：`{ROOT}/deliverables/preview.html`。

[非公開Draft Release]({shared['release_url']})、ID **{shared['release_id']}**。全{len(shared['assets'])}添付をREST再取得・SHA256照合済み。

```sh
gh api repos/{GH}/releases/{shared['release_id']}
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

[数値検査](records/qc_v02.json) / [動き](records/motion_v02.json) / [P11の語時刻](records/P11_alignment.json) / [AI生成・採否](records/ai_revision.json) / [目視](records/visual_review.json)。

本人試聴はv01音声でも可能。P08の語り、固有名詞、P12守り神の一文を確認。P11は英語に合わせ、日本語との4.35秒・6.72秒の差を記録。YouTube投稿なし。
''')
 report=f'''# 第5話「天狗」制作結果 v02（2026-10-24）

[修正依頼](wom05_修正依頼_v02_20261024.md)への対応。[取得案内](wom05_確認版_v02_20261024/README.md)。**6分8.83秒・11,065フレーム・1920×1080・30fps**。

- V01：{ai['V01']['decision']}。
- V02：{ai['V02']['decision']}。開始165.066667〜終了179.666667秒を維持。
- P11：能の絵245.8〜263.666667秒、広重263.666667〜268.733333秒、根付268.733333〜271.866667秒。英語の音素長に基づく。日本語の該当語より4.352秒・6.723秒遅い。音声を変えない条件を守り、差を記録した。
- 図解：鳥と区別できる人の横顔、直線の長い鼻、小さな頭巾に修正。文字・色・並びは維持。
- 資料：日本書紀は表紙だけ、P04の「是」を含むよう上へ拡大、北斎漫画は右頁だけに変更。背景にも同じ安全な切り出しを使用。
- 英日投稿情報：作者・作品名・年・所蔵番号を館別に記載。NDLは書名・刊年・コマ。日本語見出し・声・AI・音楽・ハッシュタグを日本語に変更。今昔20-2／20-3を1行ずつに整理。第一サムネは長い鼻の面。

英日音声ストリーム・SRT・M4A・WAVはv01と一致。英日の映像ストリームは相互一致。通常版・字幕入り版4本を全編検査。変更対象外の{qc['unchanged_frames']}フレームは全てv01と画素一致。変更9ショットの動きの最大p95÷中央値は{max(s['measurement']['p95_over_median'] for s in motion['shots']):.6f}（全件2.5以下）。共通OP・末尾10秒もそのまま。

Klingの今回の消費：{ai['credits_used']}クレジット（残高{ai['initial_balance']}→{ai['final_balance']}）。追加購入なし。生成プロンプト、元ファイルとSHA、採否を記録。

非公開Draft Release ID **{shared['release_id']}**、全{len(shared['assets'])}添付・{sum(a['bytes'] for a in shared['assets']):,} bytesをREST再取得して照合済み。本人による全編試聴は未実施。YouTube投稿・Release公開なし。
'''
 (REPO/'new-channel/wom05_制作結果_v02_20261024.md').write_text(report);print('EXPORTED',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share','export']);a=p.parse_args();globals()[a.stage]()
