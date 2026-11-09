"""EP014 bilingual metadata, audition index, evidence bundles and draft handoff."""
import json,shutil,re,zipfile
from pathlib import Path
import numpy as np
import soundfile as sf
from wom14_produce import ROOT,REPO,read,save,sha,ff,SR
from wom14_scenes import ASSETS,CAT,BOXES,SAFE
D=ROOT/'deliverables';SHARE=REPO/'new-channel/wom14_確認版_v01_20261110'
def mm(t):return f'{int(t)//60:02d}:{int(t)%60:02d}'
SOURCES=[
('Nihon Shoki (completed 720), book 26, Saimei 7 (661); Kitano manuscript, 1940–41 facsimile','https://dl.ndl.go.jp/pid/1142412/1/23'),
('W. G. Aston, Nihongi, vol. II (1896), p.272','https://library.si.edu/digital-library/book/nihongi2asto'),
('Izumo Fudoki (733); Teisei Izumo Fudoki, late Edo reprint, Ayo village','https://dl.ndl.go.jp/pid/2563532/1/38'),
('Wamyo Ruijusho (931–938); Nawa Doen edition (1617), vol.2','https://dl.ndl.go.jp/pid/2544216/1/31'),
('Tales of Ise, episode 6; edition by Sasaki Nobutsuna (1892)','https://dl.ndl.go.jp/pid/877528/1/18'),
('Toriyama Sekien, Konjaku Gazu Zoku Hyakki (first published 1779); 1805 copy, Oni','https://library.si.edu/digital-library/book/konjakuzokuhyak1tori'),
('Shoku Nihongi, Keiun 3 (706); Kokushi Taikei, vol.2 (1897)','https://dl.ndl.go.jp/pid/991092/1/27'),
('Oe no Masafusa, Goke Shidai, book 11; edition with 1653 colophon','https://dl.ndl.go.jp/pid/12865891/1/30'),
('Gaun Nikkenroku Batsuyu, Bunnan 4 (1447), 12th month, 22nd day; Zoku Shiseki Shuran, vol.3 (1930)','https://dl.ndl.go.jp/pid/1920248/1/170'),
('Reference: Kanmon Nikki, Oei 32 (1425), first month, eighth day','https://dl.ndl.go.jp/pid/2591323/1/4'),
('Reference: National Diet Library, Setsubun and bean throwing','https://www.ndl.go.jp/kaleido/entry/21/1.html'),
('Reference: Alexandre GRAS, study of tsuina and changes in the hoso role (2004), pp.36–43; paraphrase only','https://nagoya.repo.nii.ac.jp/records/6593')]
def metadata():
 D.mkdir(exist_ok=True);SHARE.mkdir(parents=True,exist_ok=True)
 shots=read(ROOT/'en/records/render_shots.json');ids=[s['key'] for s in shots if s['key'] in ASSETS];assert len(ids)==19 and len(set(ids))==19
 credits=[]
 for k in ids:
  a=ASSETS[k];credits.append(CAT[k][1]+' — '+CAT[k][2]+'.\n'+a['work_url'])
 credit='\n\n'.join(credits);master=read(ROOT/'en/records/master_timeline.json')
 legend='The Metropolitan Museum of Art (Met): Public Domain. Cleveland Museum of Art (CMA): CC0. Rijksmuseum: Public Domain. Smithsonian Libraries and Archives (SLA): Public Domain / CC0. National Diet Library Digital Collections (NDL): public domain, protection period expired.'
 short=[]
 for k in ids:
  line=CAT[k][2]
  for old,new in [('Cleveland Museum of Art','CMA'),('The Met','Met'),('Smithsonian Libraries and Archives','SLA'),('National Diet Library Digital Collections','NDL')]:line=line.replace(old,new)
  for rights in [' · Public Domain / CC0',' · Public domain, protection period expired',' · Public Domain',' · CC0']:line=line.replace(rights,'')
  short.append(CAT[k][1]+' — '+line+'\n'+ASSETS[k]['work_url'])
 compact_credit=legend+'\n\n'+'\n\n'.join(short)
 for lang in ['en','ja']:
  c=read(ROOT/'records'/('content_en.json' if lang=='en' else 'content.json'));chapters=[]
  for ch in c['chapters']:
   s=next(s for s in master['segments'] if s['chapter']==ch['id']);chapters.append(mm(s['start'] if chapters else 0)+' '+ch['title'])
  intro=('Why tiger skin? We test four familiar claims about oni against old records, pictures, and the changing roles of a court ritual.' if lang=='en' else '鬼はなぜ虎の皮を着ているのでしょうか。姿、語源、丑寅の方角、追儺の役割。四つのよく知られた説明を、古い記録と絵で確かめます。')
  text='\n\n'.join(['# '+c['title'],intro,'\n'.join(chapters),('Sources and references' if lang=='en' else '出典・参考資料')+'\n\n'+'\n\n'.join(t+'\n'+u for t,u in SOURCES),('Image credits' if lang=='en' else '素材クレジット')+'\n\n'+compact_credit,'Voice: Kokoro / Heart (af_heart)\nMusic: QO_THEME_A02 / Suno.','#Oni #JapaneseFolklore #Setsubun #QuietOrigins' if lang=='en' else '#鬼 #日本の伝承 #節分 #QuietOrigins'])+'\n'
  if lang=='en':assert not re.search(r'[\u3040-\u30ff\u3400-\u9fff]',text)
  description=text.split('\n\n',1)[1];assert len(description.encode('utf-8'))<=5000,(lang,len(description.encode('utf-8')))
  save(ROOT/lang/'records/upload_metadata_validation.json',dict(description_characters=len(description),description_utf8_bytes=len(description.encode('utf-8')),maximum_bytes=5000,reference='https://developers.google.com/youtube/data/reference/rest/v3/videos#snippet.description',english_titles_only=lang=='en',title=c['title']))
  path=D/f'EP014_upload_info_{lang}.md';path.write_text(text);shutil.copy2(path,SHARE/path.name)
  save(ROOT/lang/'records/chapters.json',{'timebase':'English master for both descriptions, as requested','chapters':chapters})
  for p in (ROOT/lang/'deliverables').iterdir():
   if p.suffix in ['.mp4','.srt','.wav','.m4a']:shutil.copy2(p,D/p.name)
 (D/'EP014_source_credits.md').write_text(credit+'\n\n'+'\n\n'.join(t+'\n'+u for t,u in SOURCES)+'\n')
 save(ROOT/'records/asset_usage.json',{'full_screen':{k:ids.count(k) for k in ids},'R_reference_pages_authorized_for_video':['R10-27','R11-30','R12-1447'],'thumbnails':{'O01-A':2,'O03-23':1},'not_counted_as_video_reuse':'thumbnail variants only'})
def audition():
 terms={'en':['oni','Nihon Shoki','Saimei','Ihase','Asakura','Izumo Fudoki','Ayo','Minamoto no Shitagou','Wamyō Ruijushō','Kitano Tenjin','Toriyama Sekien','ushitora','Gōke Shidai','hōsō','Setsubun','Ise'], 'ja':['斉明天皇','亡骸','磐瀬宮','朝倉山','出雲国風土記','阿用','源順','和名類聚抄','北野天神縁起絵巻','鳥山石燕','丑寅','江家次第','方相','戈','楯','殿上人','禅僧','異形','群臣','角']};results={}
 for lang in ['en','ja']:
  cues=[c for s in read(ROOT/lang/'records/master_timeline.json')['segments'] for c in s['cues']];selected=[c for c in cues if any(w in c['text'] for w in terms[lang])];pieces=[];lines=['各語を含む文の時刻。語そのものの厳密な強制アラインメントではありません。','Sentence intervals contain the listed words; not forced word-level alignment.'];rows=[];pos=0
  for c in selected:
   a,sr=sf.read(ROOT/c['audio_file']);assert sr==SR;words=[w for w in terms[lang] if w in c['text']];pieces.extend([a,np.zeros(SR)]);lines.append(f"sample {mm(pos)} | main {mm(c['start'])} / {c['start']:.3f}–{c['end']:.3f}s | {c['id']} | {', '.join(words)} | {c['text']}");rows.append(dict(sentence=c['id'],main_start=c['start'],main_end=c['end'],sample_start=pos,terms=words,replacements=c['replacements']));pos+=len(a)/SR+1
  missing=[w for w in terms[lang] if not any(w in c['text'] for c in cues)]
  if missing:lines.append('Not spoken in approved script: '+', '.join(missing))
  tmp=ROOT/f'_work/audition_{lang}.wav';tmp.parent.mkdir(exist_ok=True);sf.write(tmp,np.concatenate(pieces),SR);ff(['-i',tmp,'-c:a','aac','-b:a','160k',D/f'EP014_pronunciation_{lang}.m4a']);(D/f'EP014_pronunciation_{lang}.txt').write_text('\n'.join(lines)+'\n');results[lang]={'sentences':rows,'terms_not_in_script':missing}
 save(ROOT/'records/pronunciation_review.json',dict(human_listening_completed=False,basis=read(ROOT/'records/reading_diagnostic_note.json'),languages=results))
def samples(languages=None):
 for lang in (languages or ['en','ja']):
  r=ROOT/lang;shots=read(r/'records/render_shots.json');cues=read(r/f'records/subtitle_cues_{lang}.json')['cues'];src=r/f'deliverables/EP014_Oni_{lang}_v01_subtitled_review_1080p30.mp4';rows=[]
  for k in ['D_features','D_check_list','D_check_1','D_check_3','D_check_all','O06-38','O11-12','R11-30']:
   shot=next(s for s in shots if s['key']==k);candidates=[c for c in cues if min(c['end'],shot['end'])-max(c['start'],shot['start'])>.1];c=min(candidates,key=lambda c:abs((c['start']+c['end'])/2-(shot['start']+shot['end'])/2));t=(max(c['start'],shot['start'])+min(c['end'],shot['end']))/2
   path=r/f'review/subtitle_sample_{lang}_{k}.jpg';ff(['-threads',1,'-ss',t,'-i',src,'-frames:v',1,'-vf','scale=1280:720','-filter_threads',1,'-q:v',2,path]);rows.append(dict(shot=k,time=t,cue=c,file=path.name))
  save(r/'records/subtitle_samples.json',rows)
 print('VISUAL SAMPLES READY',flush=True)

def archive():
 for lang in ['en','ja']:
  for name in ['qc_v01','continuous_qc','layout_qc','final_video_motion','subtitle_layout_validation']:assert read(ROOT/lang/'records'/f'{name}.json')['passed'],(lang,name)
  for name in ['content.json','content_en.json']:assert sha(ROOT/lang/'records'/name)==sha(REPO/'new-channel/episodes/EP014_Oni/records'/name)
 for name in ['continuous_qc_4k','layout_qc_4k','final_video_motion_4k']:assert read(ROOT/'en/records'/f'{name}.json')['passed']
 assert read(ROOT/'en/records/4k_audio_integrity.json')['audio_stream_identical_to_1080'];assert read(ROOT/'records/visual_review.json')['reviewed']
 metadata();audition()
 for lang in ['en','ja']:
  r=ROOT/lang;dest=SHARE/'records'/lang;dest.mkdir(parents=True,exist_ok=True)
  for p in (r/'records').glob('*.json'):shutil.copy2(p,dest/p.name)
  for pattern in ['*sheet*.jpg','opening_*.jpg','stage_*.jpg','subtitle_sample_*.jpg']:
   for p in (r/'review').glob(pattern):shutil.copy2(p,SHARE/p.name)
 for p in (ROOT/'records').glob('*.json'):
  if p.name not in ['sharing.json']:shutil.copy2(p,SHARE/'records'/p.name)
 for p in D.glob('*.srt'):shutil.copy2(p,SHARE/p.name)
 for p in D.glob('*pronunciation*.txt'):shutil.copy2(p,SHARE/p.name)
 groups={'audio_and_subtitles':[p for p in D.iterdir() if p.suffix in ['.m4a','.wav','.srt','.txt']],'thumbnails_and_metadata':[p for p in D.iterdir() if p.suffix in ['.jpg','.md']],'QA_records':[p for p in (SHARE/'records').rglob('*.json') if p.name not in ['sharing.json','deliverable_manifest.json']]+list(SHARE.glob('*.jpg'))}
 for key,files in groups.items():
  path=D/f'EP014_{key}_v01.zip'
  with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
   for p in sorted(files):z.write(p,p.relative_to(SHARE) if p.is_relative_to(SHARE) else p.name)
  with zipfile.ZipFile(path) as z:assert z.testzip() is None
 save(ROOT/'records/deliverable_manifest.json',[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in D.iterdir() if p.is_file()])
 print('ARCHIVES READY',flush=True)
def report():
 s=read(ROOT/'records/sharing.json');assert s['draft'] and s['status']=='verified' and len(s['assets'])==8;shutil.copy2(ROOT/'records/sharing.json',SHARE/'records/sharing.json')
 lines=['# Quiet Origins 第14話「鬼」確認版v01 制作結果（2026-11-10）','','承認済み台本v02から英日1080p・字幕入り確認版・英語4Kを制作し、非公開Draft Releaseへ保存。公開予定は2026年11月18日09:00 JST。公開・予約は行っていない。台本本文と字幕本文は維持。','', '|言語|総尺|目安522秒との差|フレーム|音量|ピーク|字幕|','|---|---:|---:|---:|---:|---:|---:|']
 for l in ['en','ja']:
  r=ROOT/l;m=read(r/'records/master_timeline.json');q=read(r/'records/qc_v01.json')['files'][0];sub=read(r/'records/subtitle_validation.json');a=q['loudness'];lines.append(f"|{l}|{m['duration_seconds']:.3f}秒|{m['duration_seconds']-522:+.3f}秒|{q['frames']}|{a['input_i']} LUFS|{a['input_tp']} dBTP|{sub['count']}件|")
 lines += ['', '第12話の音声設定を継承。尺に合わせた加速なし。英日別の時間割で、区間間は約0.92秒。P06・P11・P13はこの間で語り後0.9秒以上の札の保持を確保。P14の一覧は次の絵への切替まで1.5秒以上。P02後に4秒OP、EDは総尺のちょうど10秒前から。','', '## 素材と原典の表示','','採用19素材は各1ショット。R10-27・R11-30・R12-1447も承認どおり映像へ採用。素材のSHA-256を台帳と照合。原寸から各出力サイズへ描画し、全素材の倍率は1.0以下。共通OP・EDだけは1080p原版を4Kへ拡大。','', '北野本の指定概略範囲は引用の末尾を欠くため、原寸実見で下端を延長。石燕は矩形の右下に山の線が入るため、解説文字のみの多角形切り出しにした。全頁を見せる規則の例外として、石燕は最初から文字だけ、江家次第は最初から左頁本文だけを表示。目一鬼は改行をまたぐ2列をまとめて囲み、文字の順を並べ替えていない。','', '石燕の「といへり」は、指定のショット割りで方角図へ移る前に囲む。ナレーションがその結語を述べるのは方角図の区間であり、逐語ハイライトとの同時性は主張しない。','', '## 検品','','31ショット（OP・ED含む）を個別デコードし、非圧縮フレームを一つのH.264エンコーダーへ渡した。静止画入力は30fps・有限フレーム、4Kはショットごとの再開点あり。通常英日・字幕入り英日・英語4Kを全編デコードし、警告0。通常版と4Kは全フレームの形式1種類・連続PTSを確認。H.264 High / yuv420p / CFR30fps。','', '|言語|文字コントラスト最小|箱内余白最小|実字幕との最小間隔|動きp95/中央値の最大|','|---|---:|---:|---:|---:|']
 for l in ['en','ja']:
  r=ROOT/l;q=read(r/'records/layout_qc.json');sub=read(r/'records/subtitle_layout_validation.json');motion=read(r/'records/final_video_motion.json');lines.append(f"|{l}|{q['contrast_min']:.3f}|{q['padding_min']:.1f}px|{sub['min_gap']}px|{max(x['ratio'] for x in motion['checks']):.3f}|")
 lines += ['', '点検カードの主要行52px、文字カードの主要行60px以上。札の文言は指定と一致。0.25秒の押印動作は30fpsの8フレーム（約0.267秒）で表現。出現時刻・字幕ページ・対応語句は phrase_events.json。各ショットの先頭・中央・末尾、冒頭0/1/2/3秒、原典囲み各段階を確認画像に保存。','', 'SRTは改行・空白を除いて台本本文と一致。最短1.4秒、2行以内、英42字・日23字以下。実際と同じlibass設定で全ページの文字と背景箱の範囲を測定し、画面本文との非重複を確認。BGMはQO_THEME_A02のみ。全編ミックスに−60dB以下が1秒以上続く意図しない無音なし。','', '## 読みと本人の試聴','','初回の無置換音声を保全し、英語はトークナイザーの音素、日本語はOpenJTalkのモーラから明白な誤読だけを修正。修正一覧、初回記録、固有名の文時刻TXTと抜粋M4Aを添付。語単位の強制アラインメントではなく、その語を含む文の時刻。英語台本にushitoraという語自体はないため、読み上げ時刻はない。耳による通し試聴・固有名の最終判断は本人確認待ち。','', 'サムネはA「WHY TIGER SKIN?」、B「THE FIRST ONI WORE A HAT」。指定のCC0の鬼と北野本の文字だけで作成し、描き足し・AI画像はない。1280×720・1MB以下と168px比較画像を添付。','', '## 共有','',f"[非公開Draft Release]({s['release_url']})（ID `{s['release_id']}`）。8添付をRelease ID経由のRESTで全量再取得し、サイズ・SHA-256一致、匿名404を確認。",'', '[取得案内・検品画像・投稿情報](wom14_確認版_v01_20261110/README.md)。', '', f'原寸・出力保存先：`{ROOT.parent}`。']
 lines += ['', '## 素材の使用回数・原寸に対する最大倍率', '', '|素材|全画面使用回数（各言語）|英1080p|日1080p|英4K|', '|---|---:|---:|---:|---:|']
 scale_sets=[read(ROOT/l/'records'/name) for l,name in [('en','art_scales.json'),('ja','art_scales.json'),('en','art_scales_4k.json')]]
 usage=read(ROOT/'records/asset_usage.json')['full_screen']
 for k,count in usage.items():
  vals=[max(max(a['native_scale'],a.get('max_native_scale',0)) for a in ss if a['key']==k) for ss in scale_sets]
  lines.append(f"|{k}|{count}|{vals[0]:.4f}|{vals[1]:.4f}|{vals[2]:.4f}|")
 lines += ['', '## 動きの実測', '', '|素材|英1080p p95/中央値|日1080p p95/中央値|英4K p95/中央値|', '|---|---:|---:|---:|']
 motions=[{a['shot']:a for a in read(ROOT/l/'records/final_video_motion.json')['checks']} for l in ['en','ja']]
 motion4={a['shot']:a for a in read(ROOT/'en/records/final_video_motion_4k.json')['checks']}
 for k in motions[0]:
  ratio4=f"{motion4[k]['ratio']:.3f}" if k in motion4 else '静止（原寸上限）'
  lines.append(f"|{k}|{motions[0][k]['ratio']:.3f}|{motions[1][k]['ratio']:.3f}|{ratio4}|")
 lines += ['', '意図的な原典への寄り・札の出現・カードの段階表示・共通OP/EDを除く、連続する作品カメラ移動の全隣接フレームを測定。', '', '## カードの文字・箱内余白', '', '|言語・出力|文字コントラスト最小|箱内余白最小|主要行の字高|', '|---|---:|---:|---|']
 for l,suffix in [('en',''),('ja',''),('en','_4k')]:
  q=read(ROOT/l/'records'/f'layout_qc{suffix}.json');factor=2 if suffix else 1
  lines.append(f"|{l}{suffix}|{q['contrast_min']:.3f}|{q['padding_min']*factor:.1f}px|点検 {52*factor}px / 文字 {60*factor}px以上|")
 lines += ['', '個別の文字・枠・各段階の実測は添付 `frame_layout*.json` と `layout_qc*.json`。原典の囲み一覧は `stage_*.jpg`、札の時刻一覧は `phrase_events.json`。']
 (REPO/'new-channel/wom14_制作結果_v01_20261110.md').write_text('\n'.join(lines)+'\n')
 readme=['# 第14話「鬼」確認版v01','',f"[非公開Draft Release]({s['release_url']})。英語7分31.43秒、日本語7分30.83秒。本人試聴・Claude確認用。",'','[制作結果](../wom14_制作結果_v01_20261110.md)・[英語投稿情報](EP014_upload_info_en.md)・[日本語投稿情報](EP014_upload_info_ja.md)。','', '英日通常1080p、英語4K、英日字幕入り1080pの5本。音声・字幕ZIPにWAV/M4A/SRT、固有名の抜粋音声と時刻TXT。サムネ2案は168px比較画像も収録。QA ZIPに全編検品と画面一覧。','', '|添付|asset ID|バイト|SHA-256|','|---|---:|---:|---|']
 for a in s['assets']:readme.append(f"|{a['name']}|{a['asset_id']}|{a['bytes']}|`{a['sha256']}`|")
 readme+=['',f"一覧は `gh api repos/yasukawa1980/youtube/releases/{s['release_id']}`。添付は `gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT`。",'',f'SSD出力：`{ROOT}`。公開・予約はしていない。']
 (SHARE/'README.md').write_text('\n'.join(readme)+'\n');print('REPORT WRITTEN',flush=True)
if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
