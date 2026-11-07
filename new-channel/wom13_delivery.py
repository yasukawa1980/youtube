"""EP013 metadata, thumbnail variants and pronunciation audition index."""
import json,shutil,sys,re,zipfile
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageEnhance
from wom13_produce import ROOT,REPO,read,save,sha,ff,SR
from wom13_geometry import crop_native
from wom13_scenes import CROPS,FT,FB
D=ROOT/'deliverables';SHARE=REPO/'new-channel/wom13_確認版_v01_20261107';THUMB=REPO/'new-channel/サムネ確認用/wom13'
def mm(t):return f'{int(t)//60:02d}:{int(t)%60:02d}'
SOURCES=[
 ('Rijksmuseum, The Night Watch (SK-C-5), object record and museum texts','https://id.rijksmuseum.nl/200107928'),
 ('D. C. Meijer Jr., Oud Holland IV (1886), p.204; transcription of the Banninck Cocq family album caption','https://rkddb.rkd.nl/rkddb/digital_book/18750176_004_01_s019_text.pdf'),
 ('Samuel van Hoogstraten, Inleyding tot de hooge schoole der schilderkonst (Rotterdam, 1678), p.176','https://archive.org/details/totdehoogesch00hoog'),
 ('Rijksmuseum, The missing pieces (2021)','https://www.rijksmuseum.nl/nl/story/the-missing-pieces-of-the-night-watch-article'),
 ('Esther van Duijn, The Head and the Hands, Rijksmuseum Bulletin 68(3) (2020), pp.253–273, especially p.259','https://bulletin.rijksmuseum.nl/article/view/9675'),
 ('Dr. Wendy Schaller, Smarthistory, Rembrandt, The Night Watch','https://smarthistory.org/rembrandt-the-night-watch/'),
 ('Reference: National Gallery, London, NG289 (the Lundens copy)','https://www.nationalgallery.org.uk/paintings/gerrit-lundens-after-rembrandt-the-company-of-captain-banning-cocq-the-nightwatch'),
 ('Reference: S.A.C. Dudok van Heel, Rijksmuseum Bulletin 57(1) (2009), pp.42–87','https://bulletin.rijksmuseum.nl/article/download/11665/13205/23790')]
def thumbnails():
 for d in [D,SHARE,THUMB]:d.mkdir(parents=True,exist_ok=True)
 def text(im,st,x,y,size,anchor='mm'):
  ImageDraw.Draw(im).text((x,y),st,font=ImageFont.truetype(FB,size),fill='#fff2d5',anchor=anchor,stroke_width=1)
 bounds=[round(v*(14645 if j%2==0 else 12158)) for j,v in enumerate(CROPS['D1'])]
 a=crop_native('V01',bounds).resize((1280,720),Image.Resampling.LANCZOS);a=ImageEnhance.Brightness(a).enhance(1.10)
 layer=Image.new('RGBA',a.size);dr=ImageDraw.Draw(layer);dr.rectangle((0,0,1280,112),fill=(12,10,8,210));dr.rectangle((0,578,1280,720),fill=(12,10,8,235));a=Image.alpha_composite(a.convert('RGBA'),layer).convert('RGB')
 text(a,'NOT AT NIGHT?',640,60,94);text(a,'1642',1120,629,70);text(a,'QUIET ORIGINS',475,649,45)
 b=Image.new('RGB',(1280,720),'#14110f');im=crop_native('V01',(0,0,14645,12158));im.thumbnail((1280,720),Image.Resampling.LANCZOS);im=ImageEnhance.Brightness(im).enhance(1.10);b.paste(im,((1280-im.width)//2,0))
 overlay=Image.new('RGBA',b.size);dr=ImageDraw.Draw(overlay);dr.rectangle((0,0,1280,130),fill=(12,10,8,205));dr.rectangle((0,644,1280,720),fill=(12,10,8,235));b=Image.alpha_composite(b.convert('RGBA'),overlay).convert('RGB')
 text(b,'1642',420,68,104);text(b,'1797',860,68,104)
 dr=ImageDraw.Draw(b);dr.line((580,68,700,68),fill='#fff2d5',width=8);dr.line((672,43,700,68,672,93),fill='#fff2d5',width=8)
 text(b,'QUIET ORIGINS',640,683,43)
 for name,im in [('A',a),('B',b)]:
  p=D/f'EP013_thumbnail_{name}.jpg';im.save(p,quality=94,optimize=True);assert p.stat().st_size<1000000;shutil.copy2(p,THUMB/p.name)
 compare=Image.new('RGB',(336,121),'#14110f');dr=ImageDraw.Draw(compare)
 for i,im in enumerate([a,b]):compare.paste(im.resize((168,95),Image.Resampling.LANCZOS),(i*168,26));dr.text((i*168+5,7),'A' if i==0 else 'B',fill='white')
 compare.save(D/'EP013_thumbnail_comparison_168px.jpg',quality=95);shutil.copy2(D/'EP013_thumbnail_comparison_168px.jpg',THUMB)
 save(ROOT/'records/thumbnails.json',dict(source='verified Rijksmuseum V01',A_crop=bounds,B='whole verified V01, height fit',uniform_brightness=1.10,contrast=1.0,no_local_enhancement=True,no_AI=True,files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in D.glob('*.jpg')]))
def metadata():
 for d in [D,SHARE]:d.mkdir(parents=True,exist_ok=True)
 assets=[a for a in read(REPO/'new-channel/research/wom13_素材台帳_20261107.json')['assets'] if a.get('production_file')]
 credits=[]
 for a in assets:
  title=a['title'];title={'V05':'View of the Kloveniersdoelen in Amsterdam','V06':'Civic Guards under Captain Jan Claesz Vlooswijck and Lieutenant Gerrit Hudde','V07':'Amsterdam Town Hall','V08':'La ronde de nuit'}.get(a['id'],title)
  credits.append(f"{a['creator']}, {title}, {a['date']} — Rijksmuseum, Amsterdam, {a['accession']} (Public Domain)."+(' National Gallery, London, on loan to the Rijksmuseum.' if a['id']=='V02' else '')+'\n'+a['object_url'])
 credit_text='\n\n'.join(credits)
 for lang in ['en','ja']:
  r=ROOT/lang;m=read(r/'records/master_timeline.json');c=read(r/'records'/('content_en.json' if lang=='en' else 'content.json'))
  chapter=[]
  for ch in c['chapters']:
   s=next(s for s in m['segments'] if s['chapter']==ch['id']);chapter.append(mm(s['start'] if chapter else 0)+' '+ch['title'])
  description=("Is Rembrandt's The Night Watch really a scene at night? Follow the painting from the civic guard hall it was made for, through early descriptions and the cutting of its edges, to the name recorded long after Rembrandt's lifetime. Historical texts and museum collections help distinguish a later name from the scene on the canvas." if lang=='en' else 'レンブラントの「夜警」は、本当に夜の場面なのでしょうか。市民隊の大広間のために描かれた絵を、隊長家に残る説明、弟子の言葉、切り詰め、後世に現れた名前からたどります。歴史資料と美術館の解説を手がかりに、呼び名と描かれた場面を考えます。')
  text='\n\n'.join([c['title'],description,'\n'.join(chapter),('Sources and references' if lang=='en' else '出典・参考資料')+'\n'+'\n\n'.join(a+'\n'+u for a,u in SOURCES),('Image credits' if lang=='en' else '画像クレジット')+'\n'+credit_text,'Voice: Kokoro / Heart (af_heart) · VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nMusic: QO_THEME_A02 / Suno.\nNarration uses synthetic speech.','#ArtHistory #Rembrandt #NightWatch #QuietOrigins' if lang=='en' else '#美術史 #レンブラント #夜警 #QuietOrigins'])+'\n'
  path=D/f'EP013_upload_info_{lang}.md';path.write_text(text);shutil.copy2(path,SHARE)
  save(r/'records/chapters.json',chapter)
  for p in (r/'deliverables').glob('*'):
   if p.suffix in ['.mp4','.m4a','.wav','.srt']:shutil.copy2(p,D/p.name)
 (D/'EP013_source_credits.md').write_text(credit_text+'\n\n'+ '\n'.join(a+'\n'+u for a,u in SOURCES)+'\n')
def audition():
 terms={'en':['Rembrandt','Banninck Cocq','Ruytenburch','arquebusiers','Purmerland','Vlaardingen','Hoogstraten','Lundens','sixteen forty-two','seventeen ninety-seven','nineteen forty-six'], 'ja':['一隊','火縄銃手','集会所','副官','領主','模写','文献','明暗','1946年から47年']}
 info={}
 for lang in ['en','ja']:
  m=read(ROOT/lang/'records/master_timeline.json');cues=[c for s in m['segments'] for c in s['cues']];selected={c['id']:c for word in terms[lang] for c in cues if word in c['text']};pieces=[];lines=[];pos=0;rows=[]
  for c in selected.values():
   a,sr=sf.read(ROOT/c['audio_file']);assert sr==SR;pieces.extend([a,np.zeros(SR)]);words=[w for w in terms[lang] if w in c['text']]
   lines.append(f"{mm(pos)} | {c['id']} | main {c['start']:.3f}–{c['end']:.3f}s | {', '.join(words)} | {c['text']}");rows.append(dict(sentence=c['id'],main_start=c['start'],main_end=c['end'],sample_start=pos,terms=words,replacements=c['replacements']));pos+=len(a)/SR+1
  tmp=ROOT/f'_work/audition_{lang}.wav';sf.write(tmp,np.concatenate(pieces),SR);ff(['-i',tmp,'-c:a','aac','-b:a','160k',D/f'EP013_pronunciation_{lang}.m4a']);(D/f'EP013_pronunciation_{lang}.txt').write_text('\n'.join(lines)+'\n');info[lang]=rows
 save(ROOT/'records/pronunciation_review.json',dict(human_listening_completed=False,official_audio_reference='https://www.rijksmuseum.nl/nl/story/nachtwachtverhaal',official_audio_listened=False,official_audio_note='Official 13-minute Joan Kuhlman audio located; no auditory comparison capability in this session. Proper names not respelled based on an unheard recording.',corrections_basis='VOICEVOX mora-query inspection: 一隊 イチタイ→イッタイ; 副官 フッカン→フクカン. First pass audio preserved. No changes to proper names, script or subtitle text.',languages=info))
def archive():
 for lang in ['en','ja']:
  for name in ['qc_v01','continuous_qc','layout_qc','final_video_motion','subtitle_layout_validation']:
   assert read(ROOT/lang/'records'/f'{name}.json')['passed'],(lang,name)
  for name in ['content.json','content_en.json']:
   assert sha(ROOT/lang/'records'/name)==sha(REPO/'new-channel/episodes/EP013_NightWatch/records'/name)
 for name in ['continuous_qc_4k','layout_qc_4k']:assert read(ROOT/'en/records'/f'{name}.json')['passed']
 assert read(ROOT/'en/records/4k_audio_integrity.json')['audio_stream_identical_to_1080']
 assert read(ROOT/'records/visual_review.json')['reviewed']
 metadata();audition()
 for lang in ['en','ja']:
  r=ROOT/lang;dest=SHARE/'records'/lang;dest.mkdir(parents=True,exist_ok=True)
  for name in ['master_timeline','render_shots','art_scales','frame_layout','rail_switches','subtitle_validation','subtitle_layout_validation','voice_gaps','audio_qc','qc_v01','continuous_qc','final_video_motion','chapters','layout_qc','render_shots_4k','art_scales_4k','continuous_qc_4k','layout_qc_4k','4k_audio_integrity','encoding_method','encoding_method_4k','container_precision']:
   p=r/'records'/f'{name}.json'
   if p.exists():shutil.copy2(p,dest)
  for p in (r/'review').glob('*sheet*.jpg'):shutil.copy2(p,SHARE)
  for p in (r/'review').glob('opening_*.jpg'):shutil.copy2(p,SHARE)
  for p in (r/'review').glob('stage_*.jpg'):shutil.copy2(p,SHARE)
  for p in (r/'review').glob('subtitle_sample_*.jpg'):shutil.copy2(p,SHARE)
 for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,SHARE/'records')
 groups={'audio_and_subtitles':[p for p in D.iterdir() if p.suffix in ['.m4a','.wav','.srt','.txt']], 'thumbnails_and_metadata':[p for p in D.iterdir() if p.suffix in ['.jpg','.md']], 'QA_records':list((SHARE/'records').rglob('*.json'))+list(SHARE.glob('*.jpg'))}
 for group,files in groups.items():
  p=D/f'EP013_{group}_v01.zip'
  with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
   for f in sorted(files):z.write(f,f.relative_to(SHARE) if f.is_relative_to(SHARE) else f.name)
  with zipfile.ZipFile(p) as z:assert z.testzip() is None

def report():
 sharing=read(ROOT/'records/sharing.json');assert sharing['draft'] and sharing['status']=='verified' and len(sharing['assets'])==8
 shutil.copy2(ROOT/'records/sharing.json',SHARE/'records')
 lines=['# 第13話「夜警」確認版v01 制作結果（2026-11-07）','','D6の範囲修正は本人承認済み。英語・日本語1080p、英語4K、英日字幕入り確認版を制作し、非公開Draft Releaseで共有した。公開・予約はしていない。','',
 '|言語|総尺|フレーム|OP|ED|音量|ピーク|字幕|','|---|---:|---:|---|---|---:|---:|---:|']
 for lang in ['en','ja']:
  r=ROOT/lang;m=read(r/'records/master_timeline.json');q=read(r/'records/qc_v01.json');assert q['passed'];q=q['files'][0];sub=read(r/'records/subtitle_validation.json');audio=q['loudness'];op,ed=[m['brand_intervals'][k] for k in ['opening','endcard']]
  lines.append(f"|{lang}|{m['duration_seconds']:.3f}秒|{q['frames']:,}|{op[0]:.3f}–{op[1]:.3f}|{ed[0]:.3f}–{ed[1]:.3f}|{audio['input_i']} LUFS|{audio['input_tp']} dBTP|{sub['count']}件|")
 lines +=['','目安318秒に対し、英語は16.8秒短く、日本語は3.2秒短い。尺に合わせた加速はなし。各14区間の配置後PCMをネイティブ合成音声と全サンプル照合した。区間末は約0.92秒、P02の後に4秒OP、最後の10秒が共通ED。英日は別の時間割。','',
 '## 素材と画角','','館の公式IIIFからClaudeが取得した38タイルを照合し、再圧縮しない8bit RGB PNG6点（計340,052,049 bytes）を作成。全タイルの画素一致、権利PDM確認。再ダウンロード・AI画像・生成復元・色修正はなし。詳細は[原寸結合記録](wom13_原寸結合と画角確認_20261107.md)。','',
 'D6は本人が承認した `(0.42,0.075,0.78,0.318922726)`。細部21組の重なり最大16.795%（D4/D7）、全組25%以下。V01全体は2回、細部D1〜D7各1回。V02はP08で全体の模式図と左端詳細の2画面。原典頁・修復写真・復元パネルは本編に使っていない。','',
 '|ショット|開始範囲（原寸px）|終了範囲（原寸px）|最小切出幅px|4K最大表示倍率|','|---|---|---|---:|---:|']
 sc=read(ROOT/'en/records/art_scales_4k.json')
 for k,a in sc.items():
  if 'max_zoom' not in a:continue
  box=lambda v:', '.join(f'{x:.1f}' for x in v)
  lines.append(f"|{k}|{box(a['motion_start_native_box'])}|{box(a['motion_end_native_box'])}|{a['minimum_native_crop_width']:.2f}|{a['max_native_scale']:.4f}|")
 lines +=['','4K版は原寸画像から3840×2160の画面を作成。共通OP/EDのみ元の1080pからLanczos拡大。主役の細部の最小切出幅は3,850.20pxで原寸超えなし。','',
 '模式図は原寸6点の相似変換で作図、最大残差196.880px＝模写幅1.8842%（基準2%以下）。左端の失われた男性2人と子ども1人は館2021年説明図と目視照合。別の手前の少年とは区別。[照合記録](research/wom13_V02左端人物照合_20261107.json)。館の図は参照だけで、本編には未使用。V07は公式作品記録の種別に合わせDRAWING｜素描と表示（依頼のPRINTを訂正）、1731–1784・後世の外観図。V05は1664、V08は19th century。','',
 '## 検品','','全22ショットを個別にデコードし、非圧縮フレームを一つのエンコーダーへ入力。通常英日・字幕入り英日・英語4Kの5本を先頭から最後までデコードし警告0。通常版英日と4Kは全フレームで形式1種類、H.264 High/yuv420p/CFR30fps、PTS間隔一致。各ショットの先頭・中央・末尾、引用カード各段階、冒頭0/1/2/3秒を確認用画像に保存。','',
 'SRTは台本と空白を除いて完全一致。最短1.4秒、最大2行、英42字/日23字以内。実際の字幕描画で全139ページの年代帯との最小間隔15px。引用原文・訳文は指定と一致し、本文主要行60px以上、訳文最小31px、札最小18px。引用カードの最小コントラスト6.823、最小内側余白78px。','',
 '|言語|動きの最大p95/中央値|測定ショット|','|---|---:|---:|']
 for lang in ['en','ja']:
  q=read(ROOT/lang/'records/final_video_motion.json');assert q['passed'];lines.append(f"|{lang}|{max(c['ratio'] for c in q['checks']):.4f}|{len(q['checks'])}|")
 lines+=['','QO_THEME_A02のみ使用。語り中のBGMは音声より18dB低く、区間の空きは最大+6dB、P08/P10は静かなまま。全編ミックスに−60dB以下が1秒以上続く区間なし。字幕入り確認版・4Kの音声ストリームは対応する通常版と一致。','',
 '## 本人の試聴待ち','','耳による通し試聴・固有名の正誤判断は未実施。館の公式音声「Nachtwachtverhaal」は所在を確認したが聴覚照合はできておらず、聴いた資料としては記録していない。固有名を未確認の音写へ置き換えず、初回の読みを保持した。発音確認用M4Aと各語を含む文の時刻TXTを添付。','',
 '日本語はVOICEVOX音素解析で確認した2語のみ入力を修正：一隊（イチタイ→イッタイ）、副官（フッカン→フクカン）。台本・字幕はそのまま、修正前の初回音声を保全。英語のBanninck Cocq、Ruytenburch、arquebusiers、Purmerland、Vlaardingen、Hoogstraten、Lundens、年の読み、日本語の読みと間、暗い細部と3言語カードの見やすさ、サムネA/Bを本人に確認してもらう。','',
 '## 共有','',f"[非公開Draft Release]({sharing['release_url']})、ID `{sharing['release_id']}`。8添付をRelease ID経由のRESTで全量再取得、バイト数・SHA-256一致、匿名アクセス404。公開には切り替えていない。[取得案内](wom13_確認版_v01_20261107/README.md)。",'',f'SSD保存先：`{ROOT}`。追加課金・アカウント作成なし。']
 (REPO/'new-channel/wom13_制作結果_v01_20261107.md').write_text('\n'.join(lines)+'\n')
 readme=['# 第13話「夜警」確認版v01','',f"[非公開Draft Releaseを開く]({sharing['release_url']})。本人試聴・Claude確認用。英語5分1.2秒、日本語5分14.8秒。",'',
 '[制作結果と検品](../wom13_制作結果_v01_20261107.md)・[英語投稿情報](EP013_upload_info_en.md)・[日本語投稿情報](EP013_upload_info_ja.md)。',
 '','発音・テンポは本人試聴待ち。音声ZIPの `EP013_pronunciation_en/ja.m4a` と同名TXTに確認箇所をまとめた。動画は通常版（字幕なし）と字幕入り確認版の英日、英語4K。','',
 '|添付|asset ID|バイト|SHA-256|','|---|---:|---:|---|']
 for a in sharing['assets']:readme.append(f"|{a['name']}|{a['asset_id']}|{a['bytes']}|`{a['sha256']}`|")
 readme+=['',f"`gh api repos/yasukawa1980/youtube/releases/{sharing['release_id']}` で一覧を取得。各添付は `gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT` で取得。",'',f'SSD保存先：`{ROOT}`。']
 (SHARE/'README.md').write_text('\n'.join(readme)+'\n')
if __name__=='__main__':globals()[sys.argv[1]]()
