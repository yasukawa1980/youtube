"""Publication copy, image credits, pronunciation table and bilingual review notes."""
from pathlib import Path
import re,shutil
from wom16_voice import ROOT,HERE,read,content
from wom16_art import ASSETS
from wom16_readings import EN,JA
from wom15_metadata import stamp

EN_TERMS=['Siren','sirène','sirena','Circe','Odysseus','Boeotia','Euripides','Apollonius of Rhodes','Ovid','Persephone','ba-bird','Isidore of Seville']
JA_TERMS='セイレーン シレーヌ シレーナ キルケー オデュッセウス ボイオティア エウリピデス アポロニオス オウィディウス ペルセポネ バー イシドルス 臍 蝋 鱗 帆柱 鷲 紋章 12巻 2人 紀元前412年 西暦700年ごろ 600年代の初め 紀元前7世紀 紀元前3世紀'.split()
SOURCES=[('Homer, Odyssey XII.39–54, 158–200','SR09-A'),('Euripides, Helen 167–169','SR10-A'),('Apollonius of Rhodes, Argonautica IV.896–899','SR11-A'),('Ovid, Metamorphoses V.552–563','SR12-A'),('Liber monstrorum I.6, ed. Jules Berger de Xivrey (1836), p. 25','SR05-A'),('Isidore of Seville, Etymologiae XI.3.30–31','SR08-A'),('Thomas of Cantimpré (attr.), De naturis rerum, BSB Clm 3206, f. 66r','SR07-T')]
def make():
    out=ROOT/'deliverables';out.mkdir(exist_ok=True)
    research=(HERE/'research/wom16_原典訳文_20261127.md').read_text()
    links=re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)',research)
    refs=[name+'\n'+ASSETS[k]['page'] for name,k in SOURCES]
    refs.append('Northumberland Bestiary, Getty Ms. 100, f. 14r\n'+next(url for title,url in links if 'Gettyの該当葉' in title))
    for prefix in ['Karoglou','Biers','Di Sciacca','Faral']:
        title,url=next((title,url) for title,url in links if prefix in title)
        refs.append({'Karoglou':'K. Karoglou','Biers':'W. R. Biers','Di Sciacca':'C. Di Sciacca','Faral':'E. Faral'}[prefix]+', '+title.split(',',1)[-1].split('、特に')[0].strip()+'\n'+url)
    credits=[]
    for k,a in ASSETS.items():
        credits.append(' · '.join([k,a['title'],a['artist'],a['date'],a['museum'],a['accession'],a['rights']])+'\n'+a['page']+'\n'+a['terms'])
    (out/'EP016_source_credits.md').write_text('# Quiet Origins EP016\n\n'+'\n\n'.join(credits)+'\n')
    audio='English voice: Kokoro / Heart (af_heart)\n日本語の声: VOICEVOX:冥鳴ひまり\nMusic: QO_THEME_A02 / Suno'
    (out/'EP016_audio_README.txt').write_text('Quiet Origins EP016\n\n'+audio+'\n')
    m_en=read(ROOT/'en/records/master_timeline.json')
    for lang in ('en','ja'):
        c=content(lang);en=lang=='en';m=read(ROOT/lang/'records/master_timeline.json')
        chapters=[]
        for chapter in c['chapters']:
            sg=next(x for x in m_en['segments'] if x['chapter']==chapter['id'])
            chapters.append(stamp(0 if sg['id']=='P01' else sg['start'])+' '+chapter['title'])
        intro=('Homer tells us what the Sirens sing. A Greek perfume vessel gives a siren wings and a beard. Centuries later, a Latin book describes a scaly tail. Follow the objects and the written lines that preserve both shapes.' if en else 'ホメロスはセイレーンの歌を伝え、ギリシャの香油の器には翼と髭をもつ姿が残ります。やがてラテン語の本には鱗のある魚の尾が現れます。器物と原文の行をたどり、二つの姿が同じ名で呼ばれた時代を見ていきます。')
        image='The Metropolitan Museum of Art (Open Access, CC0) · The Cleveland Museum of Art (CC0)\ne-rara: Universitätsbibliothek Basel, ETH-Bibliothek Zürich, Zentralbibliothek Zürich, Stiftung der Werke von C.G. Jung (Public Domain Mark)\nWellcome Collection (Public Domain Mark) · Bayerische Staatsbibliothek München (Public Domain Mark)'
        body='\n\n'.join(['# '+c['title'],intro,'\n'.join(chapters),('Sources and references' if en else '出典・参考資料')+'\n'+'\n\n'.join(refs),('Image credits' if en else '素材クレジット')+'\n'+image,'Voice: Kokoro / Heart (af_heart)\nMusic: QO_THEME_A02 / Suno.'])
        assert len(body)<5000 and 'Waterhouse' not in body
        (out/f'EP016_upload_info_{lang}.md').write_text(body+'\n\n---\n\n'+('Editor note. If publishing the Japanese audio, credit both voices in both descriptions.' if en else '投稿担当者用メモ。日本語音声を公開するときは、英日の両概要欄に両方の声を記載。')+' Kokoro / Heart (af_heart) · VOICEVOX:冥鳴ひまり\n')
        txt=['Quiet Origins EP016 · '+lang,'本人試聴用。該当する文の頭からの時刻。','']
        for term in EN_TERMS if en else JA_TERMS:
            for seg in m['segments']:
                for cue in seg['cues']:
                    pattern=r'\bsirens?\b' if term=='Siren' else r'\b'+re.escape(term)+r'\b'
                    present=re.search(pattern,cue['text'],re.I) if en else term in cue['text']
                    if present:
                        txt.append(f"{stamp(cue['start'])}  {cue['start']:.3f}s  {cue['id']}  {term}  /  {cue['text']}")
        txt+=['','初回の合成から変更した読み上げ入力',*[a+' → '+b for a,b in (EN if en else JA).items()]]
        if not en:
            txt+=['','合成時の読み（VOICEVOXの最終クエリ）']
            for seg in m['segments']:
                for cue in seg['cues']:
                    if any(t in cue['text'] for t in JA_TERMS):
                        query=read(ROOT/f"audio/ja/sentences/{cue['id']}.json")
                        txt.append(cue['id']+'  '+query['kana'])
        (out/f'EP016_pronunciation_{lang}.txt').write_text('\n'.join(txt)+'\n')
        for f in (ROOT/lang/'deliverables').glob('EP016*'):
            if f.suffix in {'.wav','.m4a','.srt'}:shutil.copy2(f,out/f.name)
    for path in (HERE/'サムネ確認用/wom16').glob('wom16_サムネ*.jpg'):shutil.copy2(path,out/path.name)
if __name__=='__main__':make()
