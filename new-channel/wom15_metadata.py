"""EP015 publish copy, source ledger and listening timecodes."""
import re,math,shutil
from pathlib import Path
from wom15_voice import HERE,ROOT,read,save,sha,content
from wom15_art import ASSETS
from wom15_readings import EN,JA
OUT=ROOT/'deliverables'
SOURCES=['Luke 2 and Matthew 2','Clement of Alexandria, Stromateis I.21','Chronograph of 354, Depositio martyrum and civil calendar (25 December), ed. Mommsen (1892)','Aurelius Victor, De Caesaribus 35','Syriac marginal note, printed by J. S. Assemani, Bibliotheca Orientalis II (1721), p. 164','Leo the Great, Sermon 27','Macrobius, Saturnalia I.10','Tertullian, Adversus Iudaeos 8','De solstitiis et aequinoctiis','Augustine, De Trinitate IV.5','Epiphanius, Panarion 51','John Chrysostom, In diem natalem','Pliny the Elder, Natural History XVIII','Andrew McGowan, “Sanctifying the day”','Steven Hijmans, “Sol Invictus, the Winter Solstice, and the Origins of Christmas”']
LINK_KEYS=['ルカ2','ギリシア語 I.21','翻刻','古代史料を比較した研究','', '英訳 §IV','Macrobius I.10.18','Adversus Iudaeos 8','匿名説教の校訂本文','アウグスティヌス原文','エピファニオス 51.24','説教翻刻','ラテン語、§221','McGowan,','Hijmans, Mouseion']
EN_TERMS=['Clement of Alexandria','Valentinus','Filocalus','kalends','Judea','Aurelian','Sol','Syriac','Saturnalia','Macrobius','Mithras','Tertullian','Augustine','Armenian','Antioch','John Chrysostom','Pliny','solstice','equinox']
JA_TERMS=['フィロカルス','ウァレンティヌス','朔日','戦車競走','アウレリアヌス','壮麗','欄外','指導者','サン・ピエトロ聖堂','信徒','マクロビウス','テルトゥリアヌス','身ごもられた','主は','主が','洗礼','アンティオキア','ヨアンネス・クリュソストモス','大プリニウス','冬至','春分','一冊','一つ目','一覧','200年','354年','336年','274年','1721年','380年代','最初の行','暦のその行']
def stamp(t):
 n=int(t);return f'{n//60:02}:{n%60:02}'
def details():
 OUT.mkdir(exist_ok=True)
 links=re.findall(r'\[([^\]]+)\]\((https?://[^)]+)\)',(HERE/'research/wom15_原典訳文_20261120.md').read_text())
 refs=[]
 for name,match in zip(SOURCES,LINK_KEYS):
  url=next(v for k,v in links if k.startswith(match)) if match else ASSETS['D07-A']['object_url']
  refs.append(name+'\n'+url)
 refs[0]+='\n'+next(v for k,v in links if k=='マタイ2')
 refs[2]+='\n'+next(v for k,v in links if k.startswith('市民暦12月'))
 credits=[]
 for k,a in ASSETS.items():
  credits.append(' | '.join([k,a['title'],a['author'],a['date'],a['holding'],a['rights']]))
  credits.append(a['object_url']+'\n'+a['rights_url']+'\n')
 (OUT/'EP015_source_credits.md').write_text('# Quiet Origins EP015\n\n'+'\n'.join(credits))
 en=read(ROOT/'en/records/master_timeline.json')
 for l in ['en','ja']:
  c=content(l);m=read(ROOT/l/'records/master_timeline.json');chap=[]
  for ch in c['chapters']:
   seg=next(x for x in en['segments'] if x['chapter']==ch['id'])
   chap.append(stamp(0 if seg['id']=='P01' else seg['start'])+' '+ch['title'])
  intro=('A Roman book from 354 puts two celebrations on December 25. A marginal note, two church writers and a Roman calendar help us trace the evidence for the sun festival and the count from March 25.' if l=='en' else '354年にローマで作られた一冊の本には、12月25日に二つの祝いが記されています。太陽の祭りに合わせたのか、3月25日から9か月を数えたのか。欄外の書き込み、説教、暦の行を照らし合わせます。')
  image=('Image credits' if l=='en' else '素材クレジット')+'\n'+'\n'.join([
   'National Gallery of Art, Washington — Open Access, Public Domain.',
   'Princeton University Art Museum — Abbott Handerson Thayer, Monadnock, Winter Sunrise (1919), Public Domain.',
   'e-rara — Universitätsbibliothek Basel, ETH-Bibliothek Zürich and Zentralbibliothek Zürich. Public Domain Mark.',
   'Universitätsbibliothek Heidelberg — Strzygowski (1888), plate III. Public Domain Mark.',
   'Universitäts- und Landesbibliothek Bonn — Assemani (1721), p. 164. Public Domain Mark.',
   'Internet Archive — University of Toronto (Mommsen, 1892) and Getty Research Institute (Graevius, 1732), NOT_IN_COPYRIGHT. Grinnell College (Macrobius, 1485), Public Domain Mark.',
   'Coin photographs by Sandir / Numista (CC0).'])
  upload='\n\n'.join(['# '+c['title'],intro,'\n'.join(chap),('Sources and references' if l=='en' else '出典・参考資料')+'\n'+'\n\n'.join(refs), image,
   'Voice: Kokoro / Heart (af_heart)\nMusic: QO_THEME_A02 / Suno.'])
  assert len(upload)<5000
  note = ('Editor note (outside the YouTube description)\n\nPublish with English audio only. Use Japanese for the translated title and description. If the Japanese audio is published later, credit both voices in both descriptions: Kokoro / Heart (af_heart) and VOICEVOX:冥鳴ひまり.'
          if l=='en' else '投稿担当者用メモ（概要欄への貼り付け対象外）\n\n公開音声は英語のみ。日本語は題と概要欄の翻訳に使用する。将来、日本語音声も公開するときは、英日両方の概要欄に Kokoro / Heart (af_heart) と VOICEVOX:冥鳴ひまり の両方を記載する。')
  (OUT/f'EP015_upload_info_{l}.md').write_text(upload+'\n\n---\n\n## '+note+'\n')
  txt=['Quiet Origins EP015  '+l,'各語を含む文の開始時刻（この言語の本編・字幕入り確認版に共通）','']
  for term in (EN_TERMS if l=='en' else JA_TERMS):
   for seg in m['segments']:
    for cue in seg['cues']:
     if term not in cue['text']:continue
     txt.append(f"{stamp(cue['start'])}  {cue['start']:.3f}s  {cue['id']}  {term}  /  {cue['text']}")
  txt+=['','初回から変更した読み上げ入力・音素']
  for a,b in (EN if l=='en' else JA).items():txt.append(a+' → '+b)
  (OUT/f'EP015_pronunciation_{l}.txt').write_text('\n'.join(txt)+'\n')
  for file in (ROOT/l/'deliverables').glob('EP015*'):
   if '.part.' in file.name or file.suffix not in ('.mp4','.m4a','.wav','.srt'):
    continue
   target=OUT/file.name
   if not target.exists() or sha(target)!=sha(file):shutil.copy2(file,target)
 (OUT/'EP015_audio_README.txt').write_text(
  'Quiet Origins EP015 — 音声クレジット / Audio credits\n\n'
  'EP015_audio_ja.m4a / EP015_audio_ja.wav\n日本語の声 / Japanese voice: VOICEVOX:冥鳴ひまり\n\n'
  'EP015_audio_en.m4a / EP015_audio_en.wav\nEnglish voice: Kokoro / Heart (af_heart)\n\n'
  'BGM: QO_THEME_A02 / Suno\n\n日本語音声を単体で渡すときは、このファイルを同梱してください。\n')
 shutil.copy2(OUT/'EP015_audio_README.txt',ROOT/'ja/deliverables/EP015_audio_README.txt')
 for k in ('A','B','AB_168px'):
  src=HERE/f'サムネ確認用/wom15/wom15_サムネ{k}.jpg';shutil.copy2(src,OUT/f'EP015_thumbnail_{k}_v01.jpg')
if __name__=='__main__':details()
