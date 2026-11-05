"""Prepare review listening excerpts, factual credits and posting text; no publication."""
from wom12_produce import *
from wom12_scenes import CAT
from wom11_delivery import mm
import soundfile as sf,numpy as np
NAMES={'en':['Myra','Bari','Sinterklaas','Santeclaus','Troy','Clement Clarke Moore','Winslow Homer','Thomas Nast',"Harper's Weekly",'Puck','Haddon Sundblom','ten eighty-seven','nineteen oh four'],'ja':['遺骸','祝日','司教','改訂第2版','霜','駆る','頬','北軍','野営地','縞','淡い','清涼飲料','1087年','刷られ','星の柄']}
SOURCES='''Washington Irving, A History of New York, 2nd ed. (1812), vol. I, p.106: https://archive.org/details/ahistorynewyork31irvigoog
The Children’s Friend, New York (1821): https://collections.library.yale.edu/catalog/2014510
“Account of a Visit from St. Nicholas,” Troy Sentinel (December 23, 1823).
Harper’s Weekly (1858, 1863, 1881); Puck (December 1902 and 1904).
The Catholic Encyclopedia (1911): https://www.newadvent.org/cathen/11063b.htm
St. Nicholas Center: https://www.stnicholascenter.org/who-is-st-nicholas/saint-in-bari/bari-sailors-1087
The Coca-Cola Company, historical reference: https://www.coca-colacompany.com/about-us/history/haddon-sundblom-and-the-coca-cola-santas
Smithsonian National Museum of American History: https://americanhistory.si.edu/explore/stories/how-santa-brought-coca-cola-cold
The Strong National Museum of Play: https://www.museumofplay.org/blog/twas-the-night-before-christmas/
Library of Congress: https://blogs.loc.gov/bibliomania/2025/12/22/old-saint-nick-santa-claus-in-19th-century-american-print/'''
def main():
 t=read(ROOT/'records/master_timeline.json');src=read(ROOT/'records/source_assets.json');ya=read(ROOT/'records/yale_n08.json');credits=[];loc='The Library of Congress is not aware of any U.S. copyright or any other restrictions in the documents in this collection.'
 for a in src['assets']:
  k=a['id'].split('_')[0]
  if k not in CAT:continue
  label=loc if k=='N04-A' else 'No known restrictions on publication' if k.startswith('N03') else 'Public Domain (United States)' if k=='N11-A' else 'Public Domain';credits.append(f"{a['artist']}, {a['title']} — {a['institution']}, {a['accession']} ({label}). {a['work_url']}")
 credits+=['The Children’s Friend (1821), cover & p.1 — '+ya['credit']+'. '+ya['policy']+'. https://collections.library.yale.edu/catalog/2014510'];cr='\n'.join(credits); (ROOT/'deliverables/EP012_source_credits.md').write_text('# Source credits\n\n'+cr+'\n');locs=[]
 for lang in ['en','ja']:
  c=content(lang);tl=read(ROOT/f'records/narration_timeline_{lang}.json');cues=[u for s in tl['segments'] for u in s['cues']];selected=[]
  for w in NAMES[lang]:
   relevant=[u for u in cues if w.lower() in u['text'].lower()];assert relevant,w
   for u in relevant:locs.append(dict(language=lang,word=w,utterance=u['id'],start=u['start'],end=u['end'],replacements=u['replacements']))
   if relevant[0] not in selected:selected.append(relevant[0])
  selected.sort(key=lambda x:x['start']);pieces=[];pos=0;lines=[]
  for u in selected:
   a,sr=sf.read(ROOT/u['audio_file'],dtype='float32');lines.append(f"{mm(pos)} | {u['id']} | {u['start']:.3f}–{u['end']:.3f}s | {u['text']}");pieces.extend([a,np.zeros(round(1.2*sr),np.float32)]);pos+=len(a)/sr+1.2
  wav=ROOT/f'_work/preview_pronunciation_{lang}.wav';sf.write(wav,np.concatenate(pieces),sr);ff(['-i',wav,'-af','loudnorm=I=-16:TP=-3:LRA=7','-ar',48000,'-c:a','aac','-b:a','160k',ROOT/f'deliverables/EP012_pronunciation_{lang}.m4a']);(ROOT/f'deliverables/EP012_pronunciation_{lang}.txt').write_text('\n'.join(lines)+'\n')
  chapters=[]
  for chapter in c['chapters']:
   seg=next(s for s in t['segments'] if s['chapter']==chapter['id']);chapters.append((mm(0 if not chapters else seg['start']),chapter['title']))
  desc=('An 1821 picture and two early magazine covers show a red Santa long before 1931. Follow the evidence from a bishop in Myra to the Christmas figure we know today.' if lang=='en' else '1931年より前、サンタは何色だったのでしょう。1821年の絵本、1864年の淡い茶色の衣装、そして雑誌『パック』の赤い服を、年代順にたどります。');desc+='\n\n'+'\n'.join(a+' '+b for a,b in chapters)+'\n\nSources / 出典\n'+SOURCES+'\n\nImage credits / 素材クレジット\n'+cr+'\n\nVoice: Kokoro / Heart (af_heart) · VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\nMusic: QO_THEME_A02 / Suno.\n\n#SantaClaus #ChristmasHistory #QuietOrigins';assert len(desc)<=5000,len(desc);(ROOT/f'deliverables/EP012_upload_info_{lang}.md').write_text('# '+c['title']+'\n\n'+desc+'\n')
 save(ROOT/'records/pronunciation_locations.json',locs)
if __name__=='__main__':main()
