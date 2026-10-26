import sys, json
from pathlib import Path
sys.path.insert(0,'new-channel')
from wom06_produce import ROOT,read,save,sha
from kokoro_onnx.tokenizer import Tokenizer
old=ROOT/'audio/first_pass_unmodified';report={'human_auditory_review':False,'method':'Compare recorded synthesizer inputs/phonemes, not a human listening test','changes':[]};tokenizer=Tokenizer()
for lang in ['en','ja']:
 def kana(cfg):return ''.join(''.join(m['text'] for m in p['moras'])+('、' if p.get('pause_mora') else '') for p in cfg['accent_phrases'])
 for seg in read(ROOT/f'records/narration_timeline_{lang}.json')['segments']:
  for cue in seg['cues']:
   if not cue['replacements']:continue
   before=read(old/lang/'sentences'/f'{cue["id"]}.json');after=read(ROOT/f'audio/{lang}/sentences/{cue["id"]}.json')
   b=kana(before) if lang=='ja' else tokenizer.phonemize(before['text'])
   a=kana(after) if lang=='ja' else after.get('phonemes',tokenizer.phonemize(after['text']))
   report['changes'].append({'language':lang,'sentence_id':cue['id'],'start':cue['start'],'end':cue['end'],'text':cue['text'],'changes':cue['replacements'],'before':b,'after':a})
   if lang=='ja':
    for c in cue['replacements']:
     expected={'守り手':'マモリテ','作り手':'ツクリテ','いちばん上':'イチバンウエ','前700年':'キゲンゼン','前530年':'キゲンゼン','前400年代':'キゲンゼン'}[c['display']]
     assert expected in a,(cue['id'],expected,a)
report['japanese_changed_readings_checked']=True
save(ROOT/'records/reading_audit.json',report)
print('READING AUDIT',len(report['changes']))
