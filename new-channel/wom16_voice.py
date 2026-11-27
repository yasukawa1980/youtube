"""Produce EP016 narration with the EP014 synthesis settings and preserve both first passes."""
from pathlib import Path
from dataclasses import asdict
import re, shutil, sys
import numpy as np
import soundfile as sf
from wom14_produce import MODELS, SR, read, save, sha
ROOT = Path('/Volumes/ESD-02/新チャンネル/EP016_Sirens/確認版_v01_20261127')
HERE = Path(__file__).resolve().parent
CORRECT_READINGS = '--correct' in sys.argv
REPLACEMENTS = read(ROOT/'records/approved_reading_corrections.json') if CORRECT_READINGS else {'ja':{},'en':{}}
PHONEMES = read(ROOT/'records/english_phoneme_corrections.json') if CORRECT_READINGS else {}

def content(lang):
 return read(ROOT/'records'/('content_en.json' if lang=='en' else 'content.json'))

def spoken(text,lang):
 changes=[]
 for original,reading in REPLACEMENTS[lang].items():
  if original in text:
   changes.append(dict(display=original,spoken=reading,count=text.count(original)))
   text=text.replace(original,reading)
 return text,changes

def prepare():
 assert ROOT.parents[2].is_mount(), 'ESD-02 must be mounted'
 for lang in ('en','ja'):
  (ROOT/f'audio/{lang}/sentences').mkdir(parents=True,exist_ok=True)
 (ROOT/'records').mkdir(exist_ok=True)
 for filename in ['content.json','content_en.json']:
  src=HERE/'episodes/EP016_Sirens/records'/filename
  dest=ROOT/'records'/filename
  if dest.exists():assert sha(src)==sha(dest)
  else:shutil.copyfile(src,dest)

def role(cid,text):
 if cid=='P01-01':return 'opening'
 if '?' in text or 'でしょう' in text:return 'question'
 if text.startswith(('けれど','しかし','ただし','それでも')):return 'contrast'
 if cid.startswith(('P12','P13')):return 'conclusion'
 if text.startswith(('今回は','では、','そして、')):return 'transition'
 if any(x in text for x in ['世紀','年に','記され','教皇','美術館']):return 'explanation'
 return 'plain'

def narrate(lang):
 from wom01_日本語自然さ試聴 import SPEED,INTONATION
 if CORRECT_READINGS:
  assert (ROOT/'records/first_pass_preserved.json').exists(), 'Preserve the unmodified first synthesis before corrections'
 if lang=='en':
  import onnxruntime as ort
  from kokoro_onnx import Kokoro
  ort.disable_telemetry_events();opt=ort.SessionOptions();opt.intra_op_num_threads=2;opt.inter_op_num_threads=1
  folder=MODELS/'Kokoro82M_v1';tts=Kokoro.from_session(ort.InferenceSession(str(folder/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(folder/'voices-v1.0.bin'))
 else:
  from voicevox_core.blocking import Onnxruntime,OpenJtalk,Synthesizer,VoiceModelFile,UserDict
  from voicevox_core import UserDictWord
  runtime=MODELS/'VOICEVOX_core_0.17.0_model_0.16.4'
  jtalk=OpenJtalk(str(runtime/'dict/open_jtalk_dic_utf_8-1.11'))
  userdict=UserDict();jtalk.use_user_dict(userdict)
  tts=Synthesizer(Onnxruntime.load_once(filename=str(next((runtime/'onnxruntime/lib').glob('*.dylib')))),jtalk,acceleration_mode='CPU',cpu_num_threads=2)
  with VoiceModelFile.open(str(runtime/'models/vvms/1.vvm')) as m:tts.load_voice_model(m)
 records=[];queries=[]
 for seg in content(lang)['segments']:
  texts=[x.replace('W§ G§','W. G.') for x in re.split(r'(?<=[.!?])\s+',seg['text'].replace('W. G.','W§ G§'))] if lang=='en' else re.findall(r'[^。！？]+[。！？]?',seg['text'])
  if lang=='ja':
   # A full stop inside a quotation can be followed by the closing bracket and another stop.
   texts=re.findall(r'.+?(?:[。！？](?:[」』][。！？]?)?|$)',seg['text'])
  cues=[];pieces=[];cursor=0
  for j,text in enumerate(texts,1):
   cid=f'{seg["id"]}-{j:02}';speech,changes=spoken(text,lang);r=role(cid,text)
   if lang=='en':
    cfg={'text':speech,'voice':'af_heart','speed':.82,'sentence_pause':.3,'clause_pause':.12};q=None
    cfg['diagnostic_phonemes']=tts.tokenizer.phonemize(speech,'en-us')
    if any(k in speech for k in PHONEMES):
     parts=re.split('('+'|'.join(re.escape(k) for k in PHONEMES)+')',speech)
     cfg['phonemes']=' '.join(PHONEMES.get(part,tts.tokenizer.phonemize(part,'en-us')) for part in parts if part.strip())
     assert tts.tokenizer.known(cfg['phonemes'])==cfg['phonemes']
     for change in changes:
      if change['spoken'] in PHONEMES:change['phonemes']=PHONEMES[change['spoken']]

   else:
    q=tts.create_audio_query(speech,14);q.speed_scale=SPEED[r]-.015;q.intonation_scale=INTONATION[r]+.10
    q.pre_phoneme_length=.055;q.post_phoneme_length=.09;q.output_sampling_rate=SR
    for phrase in q.accent_phrases:
     if phrase.pause_mora is not None:phrase.pause_mora['vowel_length']=.255
    cfg=asdict(q)
   path=ROOT/f'audio/{lang}/sentences/{cid}.wav';stamp=path.with_suffix('.json')
   if not(path.exists() and stamp.exists() and read(stamp)==cfg):
    if lang=='en':a,sr=tts.create(cfg.get('phonemes',speech),voice='af_heart',lang='en-us',speed=.82,sentence_pause=.3,clause_pause=.12,is_phonemes='phonemes' in cfg);assert sr==SR;sf.write(path,a,SR,subtype='PCM_16')
    else:path.write_bytes(tts.synthesis(q,14))
    save(stamp,cfg)
   a,sr=sf.read(path,dtype='float32');assert sr==SR
   # Native synthesis boundaries are retained; no speed or pitch processing.
   c={'id':cid,'text':text,'spoken_text':speech,'start':cursor/SR,'end':(cursor+len(a))/SR,'audio_file':str(path.relative_to(ROOT)),'audio_sha256':sha(path),'replacements':changes,'role':r}
   cues.append(c);pieces.append(a);cursor+=len(a)
   gap=.3 if lang=='en' else (.4 if r in ['opening','contrast','question','conclusion'] else .32)
   gap=max(gap,1.45-len(a)/SR)
   if j<len(texts):pieces.append(np.zeros(round(gap*SR),np.float32));cursor+=len(pieces[-1])
   queries.append({'sentence_id':cid,'role':r,'config':cfg,'gap_after':gap if j<len(texts) else 0})
  track=np.concatenate(pieces);p=ROOT/f'audio/{lang}/{seg["id"]}.wav';sf.write(p,track,SR,subtype='PCM_16')
  records.append({**seg,'cues':cues,'audio_file':str(p.relative_to(ROOT)),'duration_seconds':len(track)/SR,'native_speed':.82 if lang=='en' else 'role-based C'})
  print('NARRATION',lang,seg['id'],round(len(track)/SR,3),flush=True)
 save(ROOT/f'records/narration_segments_{lang}.json',{'language':lang,'voice':'Kokoro / Heart (af_heart)' if lang=='en' else 'VOICEVOX:冥鳴ひまり','sample_rate':SR,'human_auditory_review_completed':False,'segments':records})
 save(ROOT/f'records/queries_{lang}.json',queries)

def freeze():
 """Keep the first synthesized samples and queries, without moving originals."""
 state=ROOT/'records/first_pass_preserved.json'
 if state.exists():return
 dest=ROOT/'audio/first_pass_unmodified'
 result={}
 for lang in ['en','ja']:
  rec=read(ROOT/f'records/narration_segments_{lang}.json')
  assert len(rec['segments'])==14
  assert all(not c['replacements'] for s in rec['segments'] for c in s['cues'])
  shutil.copytree(ROOT/f'audio/{lang}',dest/lang,dirs_exist_ok=True)
  for name in [f'narration_segments_{lang}.json',f'queries_{lang}.json']:
   shutil.copy2(ROOT/'records'/name,dest/name)
  result[lang]=[{'sentence_id':c['id'],'sha256':sha(dest/lang/'sentences'/f'{c["id"]}.wav')} for s in rec['segments'] for c in s['cues']]
 save(state,{'directory':str(dest),'languages':result,'human_listening':False})
 print('FIRST PASS PRESERVED',dest,flush=True)

if __name__ == '__main__':
 prepare()
 if sys.argv[1]=='first':
  for lang in ('en','ja'):narrate(lang)
  freeze()
 else:narrate(sys.argv[1])
