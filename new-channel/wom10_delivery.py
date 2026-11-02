"""EP010 upload drafts and pronunciation audition excerpts; no publication."""
import numpy as np
import soundfile as sf
from wom10_produce import ROOT,read,save,ff,content,SR
SOURCES=[
('Michael Ott, St. Nicholas of Myra, The Catholic Encyclopedia 11 (1911). Web transcription','https://www.newadvent.org/cathen/11063b.htm'),
('Jacobus de Voragine, The Golden Legend, trans. Caxton, ed. Ellis (1900), vol. 2, pp. 110–111','https://sourcebooks.web.fordham.edu/basis/goldenlegend/GL-vol2-nicholas.asp'),
('Jacob Grimm, Teutonic Mythology, trans. Stallybrass, vol. II (1883), p. 515','https://archive.org/details/teutonicmytholo02grim'),
('Reference: Susanne Breuss, Der Krampus, Wien Museum Magazin (2020)','https://magazin.wienmuseum.at/der-krampus'),
('Reference: University of Innsbruck, Klaubauf','https://www.uibk.ac.at/de/geschichte-ekw/datenbanken/feste-und-braeuche/klaubauf/'),
('Reference: Stephen Winick, Library of Congress Folklife Today (2025)','https://blogs.loc.gov/folklife/2025/12/krampus-origins-and-development-of-a-winter-devil/'),
('Reference: Austrian Post, History','https://www.post.at/en/i/c/history')]
def mm(t):return f'{int(t)//60:02}:{int(t)%60:02}'
def auditions():
 names={'en':['Krampus','Myra','Knecht Ruprecht','Klaubauf','Tyrol','Carinthia','Perchten','1869'], 'ja':['聖ニコラウス','黄金伝説','嫁げる','三度','クネヒト・ループレヒト','クラウバウフ','ケルンテン','ペルヒテン','1869年','12月5日','12月6日','異教']};locations=[]
 for lang in ['en','ja']:
  cues=[c for s in read(ROOT/f'records/narration_timeline_{lang}.json')['segments'] for c in s['cues']];chosen=[];seen=set()
  for word in names[lang]:
   matching=[c for c in cues if word in c['text']];assert matching,word
   locations.extend({'language':lang,'word':word,'sentence_id':c['id'],'start':c['start'],'end':c['end']} for c in matching)
   if matching[0]['id'] not in seen:chosen.append(matching[0]);seen.add(matching[0]['id'])
  chosen.sort(key=lambda x:x['start']);pieces=[];pos=0;lines=[]
  for c in chosen:
   a,sr=sf.read(ROOT/c['audio_file'],dtype='float32');assert sr==SR;lines.append(f"{mm(pos)} | 本編 {c['start']:.3f}–{c['end']:.3f}s | {c['id']} | {c['text']}");pieces.extend([a,np.zeros(round(1.2*SR),np.float32)]);pos+=len(a)/SR+1.2
  wav=ROOT/f'_work/pronunciation_{lang}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16');ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP010_pronunciation_{lang}.m4a'])
  (ROOT/f'deliverables/EP010_pronunciation_{lang}.txt').write_text('本人試聴用。時刻は単語を含む文の範囲。聴感確認は未実施。初回無置換音声を採用。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_locations.json',locations)
def main():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters});used=read(ROOT/'records/visual_manifest.json')['unique_originals'];assets=[next(a for a in read(ROOT/'records/source_assets.json')['assets'] if a['id']==key) for key in used]
 credit='# EP010 — Source image credits\n\n'
 for a in assets:credit+=f"## {a['id']} — {a['title']}\n\n{a['artist']}; {a['date']}; {a['institution']}; {a['object_number']}.\n\n{a['object_url']}\n\nRights: {a['rights']}\n{a['rights_url']}\n\n"
 credit+='K09a/K09b/K07b: warm monochrome tonal adjustment. Original colors retained for all other images. No reconstructed colors. Book scans were consulted for textual research only.\n'
 (ROOT/'deliverables/EP010_source_credits.md').write_text(credit)
 groups={name:', '.join(a['object_number'] for a in assets if a['institution']==name) for name in sorted(set(a['institution'] for a in assets))}
 for lang in ['en','ja']:
  intro=("Is Krampus really older than Christmas? We follow a bishop's legend, devils in Saint Nicholas customs, colorful postcards, and nineteenth-century ideas about a pagan past." if lang=='en' else 'クランプスは本当にクリスマスより古いのでしょうか。司教の伝説、ニコラウスの行事に登場する悪魔、絵はがきの流行、そして19世紀に想像された異教の過去を、資料と作品からたどります。')
  disclosure=('Narration uses synthetic speech. Artworks, postcards and photographs are labelled with their dates and sources. Book scans were used for textual research only.' if lang=='en' else 'ナレーションは音声合成です。美術作品・絵はがき・写真には年代と出典を表示しています。刊本画像は本文照合のみに使用し、映像には使っていません。研究・現代解説は参照資料として区別しています。')
  body=intro+'\n\n'+disclosure+'\n\n'+('Chapters' if lang=='en' else 'チャプター')+'\n'+'\n'.join(x['timestamp']+' '+x[lang] for x in chapters)+'\n\n'+('Sources' if lang=='en' else '出典')+'\n'+'\n'.join(a+'\n'+b for a,b in SOURCES)
  body+='\n\nImage credits\n'
  for institution,numbers in groups.items():
   rights='Public Domain Mark' if institution=='Volkskundemuseum Wien' else 'Open Access, CC0' if institution=='The Metropolitan Museum of Art' else 'CC0'
   body+=institution+' — '+rights+'. Object nos.: '+numbers+'.\n'
  body+='Warm monochrome tone applied to the three historical photographs.\n'
  body+='\nEnglish voice: Kokoro / Heart (af_heart)\n日本語音声：VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nMusic: QO_THEME_A02 — Suno.\nDiagrams and editing: Quiet Origins.\n\n#Krampus #History #QuietOrigins\n';assert len(body)<=5000,(lang,len(body))
  info=f"# EP010 投稿情報・下書き\n\n## Title\n\n{c[lang]['title']}\n\n## Description\n\n{body}\n## 制作メモ（概要欄に含めない）\n\n共通尺 {m['duration_seconds']:.6f}秒。概要欄 {len(body)}字。本人の全編試聴とサムネA/B選択待ち。公開目標2026-11-08 09:00 JST（予約・投稿は未実施）。\n"
  (ROOT/f'deliverables/EP010_upload_info_{lang}.md').write_text(info)
 auditions();print('DELIVERY DOCS COMPLETE',flush=True)
if __name__=='__main__':main()
