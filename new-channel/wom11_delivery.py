"""EP011 review metadata, source-only thumbnails, and pronunciation excerpts."""
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
from wom11_produce import ROOT,REPO,read,save,sha,ff,content,SR
from wom11_visuals import BG,INK,BOLD
SOURCES=[
('E. A. Wallis Budge, The Book of the Dead: The Papyrus of Ani (1895), pp. 257–259, 344–351; text reference only','https://archive.org/details/TheBookOfTheDead-Budge-1895'),
('Richard Lepsius, Das Todtenbuch der Ägypter (1842); bibliographic reference','https://etana.org/node/11883'),
('Research: Foy Scalf (ed.), Book of the Dead: Becoming God in Ancient Egypt (2017)','https://isac-idb-static.uchicago.edu/multimedia/239131/oimp39.pdf'),
('Reference: UCL Digital Egypt, Book of the Dead questions','https://www.ucl.ac.uk/museums-static/digitalegypt/literature/religious/bdquestions.html'),
('Reference: Museo Egizio, The Book of the Dead of Kha','https://www.museoegizio.it/en/explore/news/the-book-of-the-dead-of-kha-analysis-and-studies'),
('Reference: Walters Art Museum, Heart Scarab 42.30; text only','https://art.thewalters.org/object/42.30/'),
('Reference: British Museum, Papyrus of Ani; text only, no BM image used','https://artsandculture.google.com/asset/papyrus-from-the-book-of-the-dead-of-ani/UgHfZBaRoZAhvg')]
def mm(t):return f'{int(t)//60:02}:{int(t)%60:02}'
def auditions():
 names={'en':['Maat','Ammit','Thoth','Lepsius','Annu','Heliopolis','scarab','Spell 30B','springtide'], 'ja':['天秤','42柱','二つの真理の間','殺めなかった','増水','大きく歩む者','アンヌ','30B章','125章','心臓スカラベ','声正しき者','甲虫','秤を守る者','現代の訳']};locations=[]
 for lang in ['en','ja']:
  cues=[c for s in read(ROOT/f'records/narration_timeline_{lang}.json')['segments'] for c in s['cues']];chosen=[];seen=set()
  for word in names[lang]:
   matching=[c for c in cues if word in c['text']];assert matching,word
   locations.extend({'language':lang,'word':word,'sentence_id':c['id'],'start':c['start'],'end':c['end']} for c in matching)
   if matching[0]['id'] not in seen:chosen.append(matching[0]);seen.add(matching[0]['id'])
  chosen.sort(key=lambda x:x['start']);pieces=[];pos=0;lines=[]
  for c in chosen:
   a,sr=sf.read(ROOT/c['audio_file'],dtype='float32');assert sr==SR;lines.append(f"{mm(pos)} | 本編 {c['start']:.3f}–{c['end']:.3f}s | {c['id']} | {c['text']} | 読み替え {c['replacements']}");pieces.extend([a,np.zeros(round(1.2*SR),np.float32)]);pos+=len(a)/SR+1.2
  wav=ROOT/f'_work/pronunciation_{lang}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16');ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP011_pronunciation_{lang}.m4a'])
  (ROOT/f'deliverables/EP011_pronunciation_{lang}.txt').write_text('本人試聴用。時刻は単語を含む文の範囲。聴感確認は未実施。日本語6種類は音声クエリの誤読を直し、英語は無置換の初回音声を採用。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_locations.json',locations)
def thumbnails():
 assets={a['met_object_id']:a for a in read(ROOT/'records/source_assets.json')['assets']};checks=[]
 for option,n,idx in [('A',550986,1),('B',551786,10)]:
  src=assets[n]['images'][idx];original=Image.open(src['file']).convert('RGB')
  if option=='A':
   crop=[600,760,2050,3100];im=ImageOps.fit(original.crop((0,0,500,2000)),(1280,720),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(24));obj=original.crop(crop);obj.thumbnail((560,720));im.paste(obj,(1280-obj.width,0));lines=['COULD YOU','FAIL?'];xy=(40,240);size=104;color=INK;stroke='#f6f0e3'
  else:
   crop=[1320,1040,2120,1490];im=original.crop(crop).resize((1280,720),Image.Resampling.LANCZOS);lines=['HEART VS.','FEATHER?'];xy=(40,390);size=96;color='#fff9e8';stroke='#302316'
  d=ImageDraw.Draw(im);f=ImageFont.truetype(BOLD,size)
  for j,line in enumerate(lines):d.text((xy[0],xy[1]+j*(size+8)),line,font=f,fill=color,stroke_width=5,stroke_fill=stroke)
  d.rectangle((0,654,1280,720),fill=BG);d.text((38,669),'QUIET ORIGINS',font=ImageFont.truetype(BOLD,34),fill=INK)
  dst=ROOT/f'deliverables/EP011_thumbnail_{option}.jpg';im.save(dst,quality=92,optimize=True);assert dst.stat().st_size<1000000
  im.resize((168,95),Image.Resampling.LANCZOS).save(ROOT/f'review/thumbnail_{option}_168.jpg',quality=95)
  checks.append(dict(option=option,source=src['file'],source_sha256=src['sha256'],crop_pixels=crop,source_scale=720/(crop[3]-crop[1]),image_size=[1280,720],bytes=dst.stat().st_size,sha256=sha(dst),text=' '.join(lines)))
 sheet=Image.new('RGB',(336,124),BG);d=ImageDraw.Draw(sheet)
 for i,k in enumerate(['A','B']):sheet.paste(Image.open(ROOT/f'review/thumbnail_{k}_168.jpg'),(168*i,29));d.text((168*i+6,5),k,font=ImageFont.truetype(BOLD,18),fill=INK)
 sheet.save(ROOT/'deliverables/EP011_thumbnails_168_comparison.jpg',quality=95);save(ROOT/'records/thumbnails.json',checks)
def main():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters});used=read(ROOT/'records/visual_manifest.json')['unique_originals'];assets=[a for a in read(ROOT/'records/source_assets.json')['assets'] if str(a['met_object_id']) in used]
 credit='# EP011 — Source image credits\n\n'
 for a in assets:credit+=f"## Met {a['met_object_id']} — {a['title']}\n\n{a['artist']}; {a['date']}; {a['museum']}; {a['accession']}.\n\n{a['object_url']}\n\nRights: {a['rights']}\n{a['rights_evidence']['policy_url']}\n\n"
 credit+='Original colors retained. Owner-approved conventional scaling: P01 1.7×, P10 3.4× maximum. No reconstruction. Book scans consulted for textual research only. Met 557657 is the only reused EP001 work.\n';(ROOT/'deliverables/EP011_source_credits.md').write_text(credit)
 for lang in ['en','ja']:
  intro=("Could you fail the Weighing of the Heart? We read the Book of the Dead through museum papyri, a list of wrongs never done, forty-two gods, and a spell addressed to the heart." if lang=='en' else '心臓の計量で、落ちることはあったのでしょうか。死者の書の呼び名、否定告白、42柱の神々、心臓への呪文を、刊本の英訳と美術館の資料からたどります。')
  disclosure=('Narration uses synthetic speech. Museum objects are labelled with their names, dates and sources. The English quotations follow Budge (1895); the denials draw on different versions. Modern research is listed separately. Book scans are not used as video images.' if lang=='en' else 'ナレーションは音声合成です。資料には作品名・年代・出典を表示しています。引用はバッジ英訳1895年版に基づき、否定告白は複数の写本に対応する文を紹介しています。現代研究は参照資料として区別しています。刊本画像は映像に使用していません。')
  body=intro+'\n\n'+disclosure+'\n\n'+('Chapters' if lang=='en' else 'チャプター')+'\n'+'\n'.join(x['timestamp']+' '+x[lang] for x in chapters)+'\n\n'+('Sources and references' if lang=='en' else '出典・参照資料')+'\n'+'\n'.join(a+'\n'+b for a,b in SOURCES)
  body+='\n\nImage credits\nThe Metropolitan Museum of Art — Open Access, CC0.\nhttps://www.metmuseum.org/hubs/open-access\n'
  body+='\n'.join(a['accession']+' — '+a['title']+'\n'+a['object_url'] for a in assets)
  body+='\n\nEnglish voice: Kokoro / Heart (af_heart)\n日本語音声：VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nMusic: QO_THEME_A02 — Suno.\nDiagrams and editing: Quiet Origins.\n\n#BookOfTheDead #AncientEgypt #QuietOrigins\n';assert len(body)<=5000,(lang,len(body))
  info=f"# EP011 投稿情報・下書き\n\n## Title\n\n{c[lang]['title']}\n\n## Description\n\n{body}\n## 制作メモ（概要欄に含めない）\n\n共通尺 {m['duration_seconds']:.6f}秒。概要欄 {len(body)}字。本人の全編試聴とサムネA/B選択待ち。公開予定2026-11-10 09:00 JST（予約・投稿は未実施）。\n"
  (ROOT/f'deliverables/EP011_upload_info_{lang}.md').write_text(info)
 auditions();thumbnails();print('DELIVERY COMPLETE',flush=True)
if __name__=='__main__':main()
