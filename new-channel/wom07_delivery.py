"""EP007 bilingual metadata and pronunciation excerpts, no publication."""
import json,shutil
import numpy as np
import soundfile as sf
from wom07_produce import ROOT,REPO,read,save,sha,ff,content,SR
SOURCES=[
("Winslow, letter of 11 Dec 1621, in Mourt's Relation (London, 1622), pp. 37, 60–64",'https://archive.org/details/relationoriourna00daws'),
('Winslow, Good Newes from New-England (London, 1624), pp. 49–51','https://archive.org/details/goodnewesfromnew00wins'),
('Bradford, History of Plymouth Plantation, ed. Deane (Boston, 1856), pp. 105, 141–142','https://archive.org/details/historyofplymout00brad_0'),
('Young, Chronicles of the Pilgrim Fathers (Boston, 1841), p. 231 n. 3; text reference only','https://archive.org/details/chroniclesofpilg00youn/page/n261/mode/1up'),
('Hale to Lincoln, 28 Sept 1863, Library of Congress; web transcription consulted','https://tile.loc.gov/storage-services/service/mss/mal/266/2669900/2669900.pdf'),
('Lincoln, Proclamation 106, 3 Oct 1863, National Archives','https://catalog.archives.gov/id/299960'),
('Proclamation full text; web transcription consulted','https://www.presidency.ucsb.edu/documents/proclamation-106-thanksgiving-day-1863'),
('Plimoth Patuxet Museums; commentary on the English colonists','https://plimoth.org/yath/unit-4/eye-witness-account-of-the-1621-harvest-celebration'),
('United American Indians of New England; National Day of Mourning','https://www.uaine.org/')]
def mm(t):return f'{int(t)//60:02}:{int(t)%60:02}'
def auditions():
 names={'en':['Plymouth',"Mourt's",'Massasoit','fowling','venison','Josepha',"Cole's Hill",'1621','1623','1841','1856','1863','1970'], 'ja':['数行','総督','断食','服喪','ニューイングランド先住民連合','1621','1623','1841','1856','1863','1970']};locations=[]
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
  wav=ROOT/f'_work/pronunciation_{lang}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16');ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP007_pronunciation_{lang}.m4a'])
  (ROOT/f'deliverables/EP007_pronunciation_{lang}.txt').write_text('本人試聴用。時刻は単語を含む文の範囲。聴感確認は未実施。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_locations.json',locations)
def main():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters})
 used=set(read(ROOT/'records/visual_manifest.json')['unique_originals']);assets=[a for a in read(ROOT/'records/source_assets.json')['assets'] if a['id'] in used]
 credit='# EP007 — Source image credits\n\n'
 for a in assets:credit+=f"## {a['id']} — {a['title']}\n\n{a['creator']}; {a['date']}; {a['institution']}.\n\n{a['work_url']}\n\nRights: {a['rights_statement']}\n{a.get('rights_url','')}\n\n"
 (ROOT/'deliverables/EP007_source_credits.md').write_text(credit)
 for lang in ['en','ja']:
  intro=("What does the surviving letter actually say about the 1621 harvest feast? We follow the printed record, the later name, the November date and the painting that shaped a familiar image." if lang=='en' else '1621年の収穫の宴を伝える手紙には、何が書かれているのでしょうか。刊本の原文をたどり、「最初の感謝祭」という名前、11月の日付、後世の絵が重なっていく過程を見ていきます。')
  disclosure=('Synthetic narration and clearly labelled AI reconstructions are used. AI scenes are illustrations, not historical evidence or precise architectural reconstructions. The opening table shows a familiar later image, not the documented menu of 1621.' if lang=='en' else '音声合成と、札を付けたAI再現映像を使用しています。AI場面は史料や正確な建築復元ではありません。冒頭の食卓は後世の一般的なイメージであり、1621年の献立を再現したものではありません。')
  body=intro+'\n\n'+disclosure+'\n\nChapters\n'+'\n'.join(x['timestamp']+' '+x[lang] for x in chapters)+'\n\nSources\n'+'\n'.join(a+'\n'+b for a,b in SOURCES)
  body+='\n\nImage credits\nBoston Public Library via Internet Archive — Mourt\'s Relation (1622), Good Newes (1624).\nThe Metropolitan Museum of Art — Harper\'s Weekly, 27 Nov 1858 and 29 Nov 1862 (after Winslow Homer), CC0.\nUniversity of South Carolina Libraries — Audubon, The Birds of America, Plate I (1827–30), public domain.\nNational Archives — Proclamation, 3 Oct 1863, first page.\nLibrary of Congress — J. L. G. Ferris, The First Thanksgiving 1621, reproduction print c. 1932. No known restrictions on publication.\nhttps://www.loc.gov/item/2001699850/\n'
  for a in assets:
   if a['id'] in ['G08-01','G08-02','G09-01']:body+=a['work_url']+'\n'
  body+='\nEnglish voice: Kokoro / Heart (af_heart)\n日本語音声：VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nAI video: Kling AI (V01–V04).\nMusic: Suno — QO_THEME_A02, QO_AMERICA01.\nDiagrams and editing: Quiet Origins.\n\n#Thanksgiving #History #QuietOrigins\n'
  assert len(body)<=5000,(lang,len(body))
  info=f"# EP007 投稿情報・下書き\n\n## Title\n\n{c[lang]['title']}\n\n## Description\n\n{body}\n## 制作メモ（概要欄に含めない）\n\n共通尺 {m['duration_seconds']:.6f}秒。本人の試聴待ち。Kling累計296クレジット。AI映像の絵画的表現は未達のため確認事項。公開日未定・YouTube投稿なし。\n"
  (ROOT/f'deliverables/EP007_upload_info_{lang}.md').write_text(info)
 auditions();print('DELIVERY DOCS COMPLETE',flush=True)
if __name__=='__main__':main()
