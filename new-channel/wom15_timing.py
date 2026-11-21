"""EP015 shot and board cues on each narrator's own subtitle timeline."""
import sys, shutil, os
from pathlib import Path
from wom15_voice import ROOT, HERE, read, save, sha, content
import wom14_timeline
import wom14_music

# First shot starts with the segment. Each subsequent entry names its first spoken words.
CUTS = [
 [('D01-A',), ('D04-A','The early Christians','初期のキリスト教徒は')],
 [('D02-A',), ('D03-A','For about two centuries','およそ200年')],
 [('D05-T',)],
 [('D05-A',), ('D06-A','The same book also has','同じ本には')],
 [('D_board_empty',)],
 [('D04-B',), ('D07-A','There is support','これを支える'), ('D08-A','And in the four hundreds','そして400年代')],
 [('D_board_sun',), ('D09-A','What about the Saturnalia','では、サトゥルナリア'), ('D_board_sun_return','You may also hear','ミトラスという神の話')],
 [('D10-A',), ('D11-A','Later writers linked','後の書き手たちは')],
 [('D_count',), ('D12-A','Early in the four hundreds','400年代の初め')],
 [('D13-A',), ('D_board_calc','And here, too','そして、ここにも')],
 [('D14-A',), ('D_map','In the west','西の人々は')],
 [('D_board_both',)],
 [('D15-A',), ('D16-A','In the first century','1世紀'), ('D_markers','These were calendar markers','これは暦の上の目安')],
 [('D_board_all',), ('D01-C','Each has evidence','どちらにも証拠があり')],
 [('D17-A',)], [('credits',)]
]
EVENTS = {
 'P05': [('rome','So two celebrations','一冊の本の中で')],
 'P06': [('latin','and so church leaders','そこで教会の指導者たちは')],
 'P07': [('temple','But no one knows','けれど、その欄外'),('margin','It was printed','印刷されたのは'),('leo','Leo, too','レオも'),('before','And no clear source','そして、354年より前'),('saturnalia','You may also hear','ミトラスという神の話')],
 'P09': [('count','Nine months later','その9か月後'),('conceived','He is believed','主は3月25日に身ごもられたと信じ'),('born','And he was born','そして、言い伝え')],
 'P10': [('tertullian','And here, too','そして、ここにも'),('sermon','These writers','これらの書き手が'),('augustine','Their reasoning','その考えが'),('after','Or it may','あるいは、後から')],
 'P12': [('neither','Neither gives','どちらも、その日が')],
 'P14': [('pliny','So, why','では、クリスマス')]
}

def build(lang):
 wom14_timeline.ROOT=ROOT
 wom14_timeline.content=content
 wom14_timeline.build(lang)
 dst=ROOT/lang
 old=dst/f'deliverables/EP014_Oni_{lang}_v01_1080p30.srt'
 old.replace(dst/f'deliverables/EP015_December25_{lang}_v01_1080p30.srt')
 m=read(dst/'records/master_timeline.json')
 shots=[]; events=[]
 for i,seg in enumerate(m['segments']):
  p=seg['id']
  def at(en,ja):
   text=en if lang=='en' else ja
   cue=next(c for c in seg['cues'] if c['text'].startswith(text))
   return round(cue['start']*30),text,cue['id']
  starts=[(0 if i==0 else round(seg['start']*30),CUTS[i][0][0])]
  for key,en,ja in CUTS[i][1:]:
   frame,words,cid=at(en,ja);starts.append((frame,key))
   events.append(dict(key=key,segment=p,frame=frame,words=words,cue=cid))
  for k,(frame,key) in enumerate(starts):
   stop=starts[k+1][0] if k+1<len(starts) else round(seg['end']*30)
   shots.append(dict(key=key,segment=p,start=frame,end=stop))
  for key,en,ja in EVENTS.get(p,[]):
   frame,words,cid=at(en,ja);events.append(dict(key=key,segment=p,frame=frame,words=words,cue=cid))
  if p in ['P02','P16']:
   key='opening' if p=='P02' else 'endcard'
   a,b=m['brand_intervals'][key]
   shots.append(dict(key=key,segment=key,start=round(30*a),end=round(30*b)))
 assert all(a['end']==b['start'] for a,b in zip(shots,shots[1:]))
 save(dst/'records/shot_plan.json',shots);save(dst/'records/phrase_events.json',events)
 gaps=read(dst/'records/voice_gaps.json')
 gaps['policy']='0.92 s between segments rounded to 30 fps; P05/P07/P10/P12 board holds.'
 assert all(g['gap']>=.9 for g in gaps['gaps'])
 save(dst/'records/voice_gaps.json',gaps)

def audio(lang):
 dst=ROOT/lang
 wom14_music.ROOT=dst;wom14_music.LANGUAGES=[lang]
 wom14_music.build_audio()
 for ext in ['wav','m4a']:
  old=dst/f'deliverables/EP014_audio_{lang}.{ext}';old.replace(old.with_name(old.name.replace('014','015')))

if __name__=='__main__':
 for lang in (sys.argv[2:] or ['en','ja']):
  (build if sys.argv[1]=='timeline' else audio)(lang)
