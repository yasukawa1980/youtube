"""EP009 upload drafts and pronunciation audition excerpts; no publication."""
import numpy as np
import soundfile as sf
from wom09_produce import ROOT,read,save,ff,content,SR
SOURCES=[
('Homer, Iliad 24, trans. Lang, Leaf & Myers (1883), p.503','https://archive.org/details/iliadofhom00home'),
('Homer, Odyssey 4, 8, 11, trans. Butcher & Lang (1879)','https://archive.org/details/odysseyhomer02langgoog'),
('Proclus, Chrestomathy (Little Iliad; Sack of Ilium), trans. Evelyn-White (1914). Web transcription consulted','https://www.theoi.com/Text/EpicCycle.html'),
('Virgil, Aeneid 2, trans. J. W. Mackail (1885), p.25','https://archive.org/details/india.history.resource.78363'),
('Pausanias 1.23.8, trans. W. H. S. Jones (1918). Web transcription consulted','https://www.theoi.com/Text/Pausanias1B.html'),
('Apollodorus, Epitome 5.14, trans. J. G. Frazer (1921). Web transcription consulted','https://www.theoi.com/Text/ApollodorusE.html'),
('Relief pithos, Archaeological Museum of Mykonos 2240, c.670 BC. Museum/university reference','https://dcc.dickinson.edu/images/mykonos-pithos'),
('Reference only: Homeric dating — University of Chicago Library','https://www.lib.uchicago.edu/collex/exhibits/homer-print-transmission-and-reception-homers-works/homer-print/'),
('Reference only: computer meaning — Merriam-Webster','https://www.merriam-webster.com/dictionary/Trojan%20horse')]
def mm(t):return f'{int(t)//60:02}:{int(t)%60:02}'
def auditions():
 names={'en':['Iliad','Achilles','Demodocus','Epeius','Menelaus','Laocoön','Sinon','Mykonos','Aeneid','Aeneas','Pausanias','670 BC'], 'ja':['馬を馴らす','宴','冥界','小イリアス','イリオスの陥落','甕','携えた','紀元前670年']};locations=[]
 for lang in ['en','ja']:
  cues=[c for s in read(ROOT/f'records/narration_timeline_{lang}.json')['segments'] for c in s['cues']];chosen=[];seen=set()
  for word in names[lang]:
   matching=[c for c in cues if word in c['text']];assert matching,word
   locations.extend({'language':lang,'word':word,'sentence_id':c['id'],'start':c['start'],'end':c['end']} for c in matching)
   if matching[0]['id'] not in seen:chosen.append(matching[0]);seen.add(matching[0]['id'])
  chosen.sort(key=lambda x:x['start']);pieces=[];pos=0;lines=[]
  for c in chosen:
   a,sr=sf.read(ROOT/c['audio_file'],dtype='float32');assert sr==SR;lines.append(f"{mm(pos)} | 本編 {c['start']:.3f}–{c['end']:.3f}s | {c['id']} | {c['text']}");pieces.extend([a,np.zeros(round(1.2*SR),np.float32)]);pos+=len(a)/SR+1.2
  wav=ROOT/f'_work/pronunciation_{lang}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16');ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP009_pronunciation_{lang}.m4a'])
  (ROOT/f'deliverables/EP009_pronunciation_{lang}.txt').write_text('本人試聴用。時刻は単語を含む文の範囲。聴感確認は未実施。初回無置換音声を採用。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_locations.json',locations)
def main():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters});used=read(ROOT/'records/visual_manifest.json')['unique_originals'];assets=[next(a for a in read(ROOT/'records/source_assets.json')['assets'] if a['key']==key) for key in used]
 credit='# EP009 — Source image credits\n\n'
 for a in assets:credit+=f"## {a['key']} — {a['title']}\n\n{a['artist']}; {a['date']}; {a['museum']}; {a['accession']}.\n\n{a['page']}\n\nRights: {a['rights']}\n{a['rights_url']}\n\n"
 credit+='Prints R06/R04/R01: warm monochrome tonal adjustment, no reconstructed colors. Rembrandt: bust-only crop and modest midtone lift. Gem: detail crop. All other originals retain source colors.\n'
 (ROOT/'deliverables/EP009_source_credits.md').write_text(credit)
 met=', '.join(a['accession'] for a in assets if a['key'].startswith('met_'));rijks=', '.join(a['accession'] for a in assets if a['key'].startswith('R'))
 for lang in ['en','ja']:
  intro=("Is the Trojan horse in the Iliad? We follow a funeral, a song at a feast, lost Greek poems, an ancient image, and Virgil's Aeneid to see how the famous story reached us." if lang=='en' else 'トロイの木馬は『イリアス』に出てくるのでしょうか。ヘクトルの葬儀、宴の歌、失われたギリシャの詩、古代の図像、そして『アエネーイス』をたどります。')
  disclosure=('Narration uses synthetic speech. Works of art and photographs are labelled with their dates and sources; later works are identified as later imaginings. Printed book scans are research references only and do not appear in the video.' if lang=='en' else 'ナレーションは音声合成です。美術作品・写真には年代と出典を表示し、後世の想像図を区別しています。刊本スキャンは調査参照のみで、映像には使用していません。Web翻刻・研究・辞書は参照資料として区別しています。')
  body=intro+'\n\n'+disclosure+'\n\n'+('Chapters' if lang=='en' else 'チャプター')+'\n'+'\n'.join(x['timestamp']+' '+x[lang] for x in chapters)+'\n\n'+('Sources' if lang=='en' else '出典')+'\n'+'\n'.join(a+'\n'+b for a,b in SOURCES)
  body+='\n\nImage credits\nThe Metropolitan Museum of Art — Open Access, CC0. Accession nos.: '+met+'.\nhttps://www.metmuseum.org/policies/image-resources\nRijksmuseum — Public domain. Object nos.: '+rijks+'.\nhttps://www.rijksmuseum.nl/en/collection\nMykonos 2240: Photo AbelDionis, CC0, via Wikimedia Commons.\nhttps://commons.wikimedia.org/wiki/File:Mykonos_Pithos_2240_(Trojan_Horse_detail).jpg\n'
  body+='\nEnglish voice: Kokoro / Heart (af_heart)\n日本語音声：VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nMusic: QO_THEME_A02 — Suno.\nDiagrams and editing: Quiet Origins.\n\n#TrojanHorse #History #QuietOrigins\n';assert len(body)<=5000,(lang,len(body))
  info=f"# EP009 投稿情報・下書き\n\n## Title\n\n{c[lang]['title']}\n\n## Description\n\n{body}\n## 制作メモ（概要欄に含めない）\n\n共通尺 {m['duration_seconds']:.6f}秒。概要欄 {len(body)}字。本人の全編試聴とサムネA/B選択待ち。公開目標2026-11-06 09:00 JST（予約・投稿は未実施）。\n"
  (ROOT/f'deliverables/EP009_upload_info_{lang}.md').write_text(info)
 auditions();print('DELIVERY DOCS COMPLETE',flush=True)
if __name__=='__main__':main()
