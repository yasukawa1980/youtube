"""EP008 bilingual metadata and pronunciation excerpts, no publication."""
import json,shutil
import numpy as np
import soundfile as sf
from wom08_produce import ROOT,REPO,read,save,sha,ff,content,SR
SOURCES=[
('Carter & Mace, The Tomb of Tut.ankh.Amen I (New York, 1923), pp.132,136,138,140–142,201,245,258; MIT Libraries copy','https://archive.org/details/tomboftutankhame00cart_1'),
('Howard Carter, journal, season 1; Griffith Institute transcription, text reference only','https://www.griffith.ox.ac.uk/discoveringTut/journals-and-diaries/season-1/journal.html'),
('The Albany Democrat, 5 Apr 1923, p1','https://oregonnews.uoregon.edu/lccn/sn96088451/1923-04-05/ed-1/seq-1/'),
('The Eugene Daily Guard, 6 Apr 1923, p1','https://oregonnews.uoregon.edu/lccn/sn96088107/1923-04-06/ed-1/seq-1/'),
('Morning Register, 6 Apr 1923, p1','https://oregonnews.uoregon.edu/lccn/sn96088115/1923-04-06/ed-1/seq-1/'),
('L. M. Alcott, Lost in a Pyramid; or, The Mummy’s Curse (1869); later transcription consulted','https://gutenberg.net.au/ebooks06/0603041h.html'),
('A. Conan Doyle, Lot No.249, Harper’s New Monthly Magazine, Sept1892, pp525–544; metadata/OCR, page images not reproduced','https://archive.org/details/sim_harpers-magazine_1892-09_85_508'),
('Offering chapel of Hetepherakhty, c.2400 BC; Rijksmuseum van Oudheden commentary, text reference only','https://www.rmo.nl/museumkennis/egypte/de-voorwerpen/offerkapel-van-hoge-ambtenaar/'),
('M. R. Nelson, The mummy’s curse: historical cohort study, BMJ 2002;325:1482–1484','https://doi.org/10.1136/bmj.325.7378.1482')]

def mm(t):return f'{int(t)//60:02}:{int(t)%60:02}'
def auditions():
 names={'en':['Tutankhamun','Carnarvon','Luxor','Marie Corelli','Arthur Conan Doyle','Louisa May Alcott','Lot No. 249','alabaster','2400 BC','1922','1923','1869','1892','1939','2002'], 'ja':['王家の谷','盗掘','埋葬室','礼拝室','競売番号249','若草物語','幾百万年','紀元前2400年','BMJ']};locations=[]
 for lang in ['en','ja']:
  cues=[c for s in read(ROOT/f'records/narration_timeline_{lang}.json')['segments'] for c in s['cues']];chosen=[];seen=set()
  for word in names[lang]:
   matching=[c for c in cues if word in c['text']]
   locations.extend({'language':lang,'word':word,'sentence_id':c['id'],'start':c['start'],'end':c['end']} for c in matching)
   if matching and matching[0]['id'] not in seen:chosen.append(matching[0]);seen.add(matching[0]['id'])
  chosen.sort(key=lambda x:x['start']);pieces=[];pos=0;lines=[]
  for c in chosen:
   a,sr=sf.read(ROOT/c['audio_file'],dtype='float32');assert sr==SR
   lines.append(f"{mm(pos)} | 本編 {c['start']:.3f}–{c['end']:.3f}s | {c['id']} | {c['text']}");pieces.extend([a,np.zeros(round(1.2*SR),np.float32)]);pos+=len(a)/SR+1.2
  wav=ROOT/f'_work/pronunciation_{lang}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16');ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP008_pronunciation_{lang}.m4a'])
  (ROOT/f'deliverables/EP008_pronunciation_{lang}.txt').write_text('本人試聴用。時刻は単語を含む文の範囲。聴感確認は未実施。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_locations.json',locations)
def main():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters})
 used=set(read(ROOT/'records/visual_manifest.json')['unique_originals']);assets=[a for a in read(ROOT/'records/source_assets.json')['assets'] if a['id'] in used]
 credit='# EP008 — Source image credits\n\n'
 for a in assets:credit+=f"## {a['id']} — {a['title']}\n\n{a['artist']}; {a['date']}; {a['holder']}.\n\n{a['object_url']}\n\nRights: {a['rights_statement']}\n{' / '.join(a['rights_urls'])}\n\n"
 (ROOT/'deliverables/EP008_source_credits.md').write_text(credit)
 for lang in ['en','ja']:
  intro=("Where did Tutankhamun’s curse come from? We follow the 1923 excavation account, contemporary newspaper debates and earlier fiction, and distinguish reported legends from the words recorded in the tomb." if lang=='en' else 'ツタンカーメンの呪いはどこから来たのでしょう。1923年の発掘記録、当時の新聞での議論、発見以前の小説をたどり、語られた伝説と墓に残された言葉を見比べます。')
  disclosure=('Synthetic narration is used. Only the candle scene in P14 is AI-generated (Kling AI); it does not recreate a historical event. Archival photos, newspaper columns and printed texts are labelled with their sources. The historical cohort study found no statistically significant association; its sample was small and records incomplete.' if lang=='en' else 'ナレーションは音声合成です。AI生成映像はP14のろうそく1場面（Kling AI）だけで、歴史上の出来事を再現するものではありません。資料写真・新聞・刊本には出典を表示しています。BMJ研究は小規模で記録に欠損があり、結論は「統計的に有意な関連を認めなかった」という範囲です。')
  body=intro+'\n\n'+disclosure+'\n\n'+('Chapters' if lang=='en' else 'チャプター')+'\n'+'\n'.join(x['timestamp']+' '+x[lang] for x in chapters)+'\n\n'+('Sources' if lang=='en' else '出典')+'\n'+'\n'.join(a+'\n'+b for a,b in SOURCES)
  body+='\n\nImage credits\nMIT Libraries via Internet Archive — Carter & Mace (1923), photographs by Harry Burton. Provider designation: No Copyright – United States (not CC0).\nhttps://archive.org/details/mitlibrariespublicdomain\nUniversity of Oregon Libraries — Historic Oregon Newspapers. Public Domain Mark 1.0.\nhttps://creativecommons.org/publicdomain/mark/1.0/\n'
  body+='\nEnglish voice: Kokoro / Heart (af_heart)\n日本語音声：VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nAI video: Kling AI (P14 candle only).\nMusic: Suno — QO_THEME_A02.\nDiagrams and editing: Quiet Origins.\n\n#Tutankhamun #History #QuietOrigins\n'
  assert len(body)<=5000,(lang,len(body))
  info=f"# EP008 投稿情報・下書き\n\n## Title\n\n{c[lang]['title']}\n\n## Description\n\n{body}\n## 制作メモ（概要欄に含めない）\n\n共通尺 {m['duration_seconds']:.6f}秒。本人の試聴待ち。Kling64クレジット（379→315）。AIはろうそく1本。公開目標11/4 09:00 JST・YouTube投稿なし。\n"
  (ROOT/f'deliverables/EP008_upload_info_{lang}.md').write_text(info)
 auditions();print('DELIVERY DOCS COMPLETE',flush=True)
if __name__=='__main__':main()
