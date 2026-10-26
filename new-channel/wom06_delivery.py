"""EP006 local review documents. Does not upload or publish anything."""
import json, sys, csv, shutil
from pathlib import Path
import numpy as np
import soundfile as sf
from wom06_produce import ROOT,REPO,read,save,sha,ff,content,SR
SOURCES=[
 ('Breasted, Ancient Records of Egypt II (1906), §815, pp. 323–324','https://archive.org/details/ancientrecordsof02brea/page/n355/mode/1up'),
 ('Hesiod, Theogony 326, Evelyn-White tr. (1914); image: 1920 printing, p. 103','https://archive.org/details/hesiodhomerichym00hesi/page/n159/mode/1up'),
 ('Sophocles, Oedipus the King, Jebb tr. (1904), p. 7, line 130','https://oll-resources.s3.us-east-2.amazonaws.com/oll3/store/titles/1155/0561_Bk.pdf'),
 ('Athenaeus 10.456b, Gulick tr. — web transcription consulted','https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Athenaeus/10E*.html'),
 ('[Apollodorus], Library 3.5.8, Frazer tr. (1921) — web transcription consulted','https://www.theoi.com/Text/Apollodorus3.html'),
 ('Herodotus 2.175, Macaulay tr. (1890) — web transcription consulted','https://lexundria.com/hdt/2.175/mcly'),
 ('Norden, plates XLV–XLVII, London 1780; image: plate XLVII','https://archive.org/details/b33543975/page/n109/mode/1up'),
 ('Mark Lehner / AERA, Who Built the Sphinx?','https://aeraweb.org/projects/who-built-the-sphinx/')]
def mm(t):
 n=int(t);return f'{n//60:02}:{n%60:02}'
def auditions():
 names={'en':['Giza','Khafre','Hatshepsut','Horemakhet','Thutmose','Hesiod','Attica','Sophocles','Oedipus','Athenaeus','Herodotus','Sais','androsphinxes','Frederic Norden','1730s','1798'],
 'ja':['守り手','作り手','頭巾','ホルエムアケト','トトメス4世','碑','前700年','前530年','前400年代','ビブリオテーケー','アテナイオス','奉納','1730年代','1798年']}
 locations=[]
 for lang in ['en','ja']:
  cues=[c for s in read(ROOT/f'records/narration_timeline_{lang}.json')['segments'] for c in s['cues']];chosen=[];seen=set()
  for name in names[lang]:
   for c in cues:
    if name in c['text']:locations.append({'language':lang,'word':name,'sentence_id':c['id'],'start':c['start'],'end':c['end']})
   cue=next((c for c in cues if name in c['text']),None)
   if cue and cue['id'] not in seen:chosen.append(cue);seen.add(cue['id'])
  pieces=[];pos=0;lines=[]
  for c in chosen:
   a,sr=sf.read(ROOT/c['audio_file'],dtype='float32');assert sr==SR
   lines.append(f"{mm(pos)} | 本編 {c['start']:.3f}–{c['end']:.3f}s | {c['id']} | {c['text']}")
   pieces.extend([a,np.zeros(round(1.2*SR),np.float32)]);pos+=len(a)/SR+1.2
  wav=ROOT/f'_work/pronunciation_{lang}.wav';sf.write(wav,np.concatenate(pieces),SR,subtype='PCM_16')
  ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','192k',ROOT/f'deliverables/EP006_pronunciation_{lang}.m4a'])
  (ROOT/f'deliverables/EP006_pronunciation_{lang}.txt').write_text('本人試聴用。時刻は単語を含む文の範囲です。人による聴感確認は未実施。\n\n'+'\n'.join(lines)+'\n')
 save(ROOT/'records/pronunciation_locations.json',locations)

def main():
 m=read(ROOT/'records/master_timeline.json');c={l:content(l) for l in ['en','ja']};chapters=[]
 for i,ch in enumerate(c['en']['chapters']):
  s=next(s for s in m['segments'] if s['chapter']==ch['id']);t=0 if i==0 else s['start'];chapters.append({'id':ch['id'],'seconds':t,'timestamp':mm(t),'en':ch['title'],'ja':c['ja']['chapters'][i]['title']})
 save(ROOT/'records/chapters.json',{'chapters':chapters})
 manifest=read(ROOT/'records/visual_manifest.json');used=set(manifest['unique_originals']);assets=[a for a in read(ROOT/'records/source_assets.json')['assets'] if a['id'] in used];assert len(assets)==19
 credits='# EP006 — Source image credits\n\n'
 for a in assets:
  credits+=f"## {a['id']} — {a['title']}\n\n{a['artist']}; {a['date']}; {a['museum']}; {a['accession']}.\n\n{a['object_url']}\n\nRights: {a['rights']}.\n{a.get('rights_url','')}\n\n"
 (ROOT/'deliverables/EP006_source_credits.md').write_text(credits)
 for lang in ['en','ja']:
  intro=("Egypt's royal guardian and the riddling monster of Thebes share a name. This episode follows their different histories through ancient texts, museum objects and historic photographs. We distinguish a text's claims from modern retellings, and a printed edition's date from the age of the story." if lang=='en' else 'エジプトの王の守り手と、テーバイのなぞかけの怪物。一つの名前を分け合う二つのスフィンクスを、古い文献・博物館の資料・古写真でたどります。書物に実際に書かれたことと後世の語り直し、物語の時代と今回使う刊本の年を区別しています。')
  disclosure=('Synthetic narration and clearly labelled, painterly AI videos are used. AI scenes are illustrations, not historical evidence or exact archaeological reconstructions.' if lang=='en' else '音声合成と、札を付けた絵画的なAI映像を使用しています。AI場面は挿絵であり、史料や特定の遺跡の正確な復元ではありません。')
  body=intro+'\n\n'+disclosure+'\n\nChapters\n'+'\n'.join(x['timestamp']+' '+x[lang] for x in chapters)+'\n\nSources\n'+'\n'.join(a+'\n'+b for a,b in SOURCES)
  body+='\n\nImage credits\nThe Metropolitan Museum of Art — CC0 / Open Access\nFrancis Frith (1858); Félix Bonfils (1860s–70s, printed ca. 1870); Gustave Moreau (1864, upper detail).\n'
  for a in assets:
   if a['id'].startswith('met_'):body+=a['accession']+': '+a['object_url']+'\n'
  body+='Archivio Museo Egizio — CC0\nAttributed to V. R. Lanzone, Inv02_008 (1865–70); V. R. Lanzone, Album1_004 (1865–70); F. Bonfils, Inv01_011 (1875–77); anonymous, possibly V. R. Lanzone, Inv02_007 (1875).\n'
  # These supplied URLs come from the saved museum records.
  for a in assets:
   if a['id'].startswith('museo_'):body+=a['object_url']+'\n'
  body+='Wellcome Collection via Internet Archive — Norden, Public Domain Mark.\nUniversity of California Libraries via Internet Archive — Hesiod, public domain.\nOnline Library of Liberty — Jebb/Sophocles, public-domain text and original scan.\n\nEnglish voice: Kokoro / Heart (af_heart).\n日本語音声：VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nhttps://voicevox.hiroshiba.jp/\nAI video: Kling AI (V01–V03).\nDiagrams and original synthesized ambient music: Quiet Origins.\n\n#Sphinx #AncientHistory #QuietOrigins\n'
  assert len(body)<=5000,(lang,len(body));assert len(c[lang]['title'])<=100
  info=f"# EP006 投稿情報・下書き\n\n## Title\n\n{c[lang]['title']}\n\n## Description\n\n{body}\n## 制作メモ（概要欄には含めない）\n\n共通尺 {m['duration_seconds']:.6f}秒。映像未完成・Kling未生成・公開日未定・YouTube投稿未実施。AI生成完了と最終映像の照合後に確定してください。\n"
  (ROOT/f'deliverables/EP006_upload_info_{lang}.md').write_text(info)
 if '--docs-only' not in sys.argv:auditions()
 print('LOCAL REVIEW DOCS COMPLETE',flush=True)
if __name__=='__main__':main()
