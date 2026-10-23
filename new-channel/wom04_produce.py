"""Quiet Origins EP004 v01. Local synthesis, shared timeline and media assembly.
Usage: Python 3.12 with the existing WOM02/03 local audio environment: python wom04_produce.py prepare|en|ja|timeline|audio
No paid APIs, publication or changes to EP001. Reuses approved local engines/settings.
"""
import argparse,copy,json,math,os,re,shutil,subprocess
from dataclasses import asdict
from pathlib import Path
import numpy as np
import soundfile as sf
from wom01_multilingual_render import read,save,sha as _file_sha,ff,probe,measure,rms
from wom01_subtitles import pages,to_srt
from wom01_日本語自然さ試聴 import SPEED,INTONATION
REPO=Path(__file__).resolve().parent.parent
ROOT=Path(os.environ.get('WOM04_ROOT','/Users/ryo/Desktop/新チャンネル/EP004_Pandora/確認版_v01_20261023'))
MEDIA=ROOT.parent/'素材'
MODELS=Path('/Users/ryo/Desktop/BGM/_共通/音声モデル')
BRAND=Path('/Users/ryo/Desktop/新チャンネル/ブランド素材/オープニング_エンドカード_動画試作_v02_20261021/deliverables')
OP=BRAND/'Quiet_Origins_opening_trial_v02.mp4';END=Path('/Users/ryo/Desktop/新チャンネル/ブランド素材/エンドカード_共通版_v02_20261023/deliverables/Quiet_Origins_endcard_v02.mp4')
SR=24000;FPS=30
def sha(path):return _file_sha(Path(path))
PHONEMES={'Hesiod':'hˈiːsiəd','Theogony':'θiˈɑːɡəni','Hephaestus':'həfˈɛstəs','Epimetheus':'ˌɛpɪmˈiːθiəs','pithos':'pˈɪθɑːs','elpis':'ˈɛlpɪs','Pausanias':'pɔːsˈeɪniəs','Babrius':'bˈeɪbɹiəs','pyxis':'pˈɪksɪs'}
REPLACEMENTS={'en':{k:k for k in PHONEMES},'ja':{'神統記':'しんとうき','鍛冶':'かじ','ヘパイストス':'ヘパイストス','壺の縁':'壺のふち','伝わる後の':'伝わるのちの','刷られた':'すられた','小箱':'こばこ'}}

def content(lang):return read(ROOT/'records'/('content_en.json' if lang=='en' else 'content.json'))
def spoken(text,lang):
 changes=[]
 for a,b in REPLACEMENTS[lang].items():
  if a in text:changes.append({'display':a,'spoken':b,'count':text.count(a)});text=text.replace(a,b)
 return text,changes

def prepare():
 for d in ['records','audio/en/sentences','audio/ja/sentences','assets','review','deliverables','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 for n in ['content.json','content_en.json']:
  src=REPO/'new-channel/episodes/EP004_Pandora/records'/n;dst=ROOT/'records'/n
  if dst.exists():assert sha(src)==sha(dst),'Input changed; use a new version'
  else:shutil.copy2(src,dst)
 assets=read(REPO/'new-channel/research/wom04_素材台帳_20261023.json')
 save(ROOT/'records/source_assets.json',assets)
 save(ROOT/'records/request.json',{'input_scripts':{n:sha(ROOT/'records'/n) for n in ['content.json','content_en.json']},'opening':str(OP),'endcard':str(END),'brand_sha256':{str(p):sha(p) for p in [OP,END]},'english_speed':.82,'english_note':'EP001 base Heart setting; no episode-specific EP001 pacing values transplanted','japanese_delivery':'C / style 14 / no acceleration to fit English','human_listening':False,'paid_services':'Kling existing subscription only; not started','youtube_posted':False})
 print('PREPARED',ROOT,flush=True)

def role(cid,text):
 if cid=='P01-01':return 'opening'
 if '?' in text or 'でしょう' in text:return 'question'
 if text.startswith(('けれど','しかし','ただし','それでも')):return 'contrast'
 if cid.startswith(('P16','P17')):return 'conclusion'
 if text.startswith(('今回は','では、','そして、')):return 'transition'
 if any(x in text for x in ['世紀','年に','記され','教皇','美術館']):return 'explanation'
 return 'plain'

def narrate(lang):
 if lang=='en':
  import onnxruntime as ort
  from kokoro_onnx import Kokoro
  ort.disable_telemetry_events();opt=ort.SessionOptions();opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
  folder=MODELS/'Kokoro82M_v1';tts=Kokoro.from_session(ort.InferenceSession(str(folder/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(folder/'voices-v1.0.bin'))
 else:
  from voicevox_core.blocking import Onnxruntime,OpenJtalk,Synthesizer,VoiceModelFile,UserDict
  from voicevox_core import UserDictWord
  runtime=MODELS/'VOICEVOX_core_0.17.0_model_0.16.4'
  jtalk=OpenJtalk(str(runtime/'dict/open_jtalk_dic_utf_8-1.11'))
  userdict=UserDict();userdict.add_word(UserDictWord(surface='ヘパイストス',pronunciation='ヘパイストス',accent_type=3,word_type='PROPER_NOUN',priority=10));jtalk.use_user_dict(userdict)
  tts=Synthesizer(Onnxruntime.load_once(filename=str(next((runtime/'onnxruntime/lib').glob('*.dylib')))),jtalk,acceleration_mode='CPU',cpu_num_threads=2)
  with VoiceModelFile.open(str(runtime/'models/vvms/1.vvm')) as m:tts.load_voice_model(m)
 records=[];queries=[]
 for seg in content(lang)['segments']:
  texts=re.split(r'(?<=[.!?])\s+',seg['text']) if lang=='en' else re.findall(r'[^。！？]+[。！？]?',seg['text'])
  cues=[];pieces=[];cursor=0
  for j,text in enumerate(texts,1):
   cid=f'{seg["id"]}-{j:02}';speech,changes=spoken(text,lang);r=role(cid,text)
   if lang=='ja':
    for c in changes:
     if c['display']=='ヘパイストス':c['method']='VOICEVOX user dictionary: ヘパイストス, accent 3, proper noun, priority 10'
   if lang=='en':
    cfg={'text':speech,'voice':'af_heart','speed':.82,'sentence_pause':.3,'clause_pause':.12};q=None
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

def timeline():
 narr={l:read(ROOT/f'records/narration_segments_{l}.json') for l in ['en','ja']}
 # Spread P02's excess JA tail into existing sentence gaps, preserving every audio sample.
 e,j=[narr[l]['segments'][1] for l in ['en','ja']];extra=max(0,e['duration_seconds']-j['duration_seconds']-1.0)
 if extra and len(j['cues'])>1:
  inc=extra/(len(j['cues'])-1);pieces=[];pos=0;new=copy.deepcopy(j)
  for k,c in enumerate(new['cues']):
   a,sr=sf.read(ROOT/c['audio_file'],dtype='float32');c['start']=pos/SR;pieces.append(a);pos+=len(a);c['end']=pos/SR
   if k<len(new['cues'])-1:
    oldgap=j['cues'][k+1]['start']-j['cues'][k]['end'];z=np.zeros(round((oldgap+inc)*SR),np.float32);pieces.append(z);pos+=len(z)
  p=ROOT/'audio/ja/P02_opening_paced.wav';sf.write(p,np.concatenate(pieces),SR,subtype='PCM_16');new['audio_file']=str(p.relative_to(ROOT));new['duration_seconds']=pos/SR;narr['ja']['segments'][1]=new
 master=[];pos=1.8;op=None
 for i,e in enumerate(narr['en']['segments']):
  lengths={l:narr[l]['segments'][i]['duration_seconds'] for l in narr}
  gap=1.4 if i==1 else (1.2 if i==len(narr['en']['segments'])-1 else 1.8 if narr['en']['segments'][i+1]['chapter']!=e['chapter'] else .9)
  end=math.ceil((pos+max(lengths.values())+gap)*FPS)/FPS
  master.append({'id':e['id'],'chapter':e['chapter'],'start':pos,'speech_end':pos+max(lengths.values()),'end':end,'speech_seconds':lengths})
  pos=end
  if i==1:op=[pos,pos+4];pos+=4
 endcard=[pos,pos+10];duration=endcard[1]
 masterdata={'fps':FPS,'sample_rate':SR,'duration_seconds':duration,'languages':['en','ja'],'segments':master,'brand_intervals':{'opening':op,'endcard':endcard},'opening_ja_gap_redistributed':extra,'ja_wait_before_opening':op[0]-master[1]['start']-narr['ja']['segments'][1]['duration_seconds']}
 assert masterdata['ja_wait_before_opening']<=3
 save(ROOT/'records/master_timeline.json',masterdata)
 replacements=[];subchecks={}
 for l in narr:
  track=np.zeros(round(duration*SR),np.float32);segments=[];sub=[]
  for common,s in zip(master,narr[l]['segments']):
   a,sr=sf.read(ROOT/s['audio_file'],dtype='float32');n=round(common['start']*SR);track[n:n+len(a)]=a
   cues=[{**c,'start':c['start']+common['start'],'end':c['end']+common['start']} for c in s['cues']]
   segments.append({**s,**common,'cues':cues})
   for c in cues:
    chunks=pages(c['text'],l);weights=np.array([len(x.replace('\n','')) for x in chunks],dtype=float);p=c['start']
    span=c['end']-c['start'];durations=span*weights/weights.sum()
    if len(chunks)>1:
     assert span>=1.4*len(chunks),(l,c)
     fixed=np.zeros(len(chunks),bool)
     while np.any(durations<1.4-1e-9):
      fixed|=durations<1.4;durations[fixed]=1.4
      durations[~fixed]=(span-1.4*fixed.sum())*weights[~fixed]/weights[~fixed].sum()
    for k,chunk in enumerate(chunks):
     end=c['end'] if k==len(chunks)-1 else p+float(durations[k])
     sub.append({'sentence_id':c['id'],'start':p,'end':end,'text':chunk});p=end
    for change in c['replacements']:replacements.append({'language':l,'sentence_id':c['id'],'start':c['start'],'end':c['end'],**change})
  # Short final pages may hold into silence; never overlap the next cue or a brand card.
  for i,c in enumerate(sub):
   if c['end']-c['start']<1.4-1e-6:
    cap=sub[i+1]['start']-.01 if i+1<len(sub) else endcard[0]-.05
    assert c['start']+1.4<=cap,(l,c)
    c['end']=c['start']+1.4
  clean=lambda x:re.sub(r'\s+','',x)
  assert clean(''.join(c['text'] for c in sub))==clean(''.join(s['text'] for s in content(l)['segments']))
  assert all(len(c['text'].splitlines())<=2 and max(map(len,c['text'].splitlines()))<=(42 if l=='en' else 23) for c in sub)
  assert all(c['end']-c['start']>=1.4-1e-6 for c in sub)
  assert all(a['end']<=b['start'] for a,b in zip(sub,sub[1:]))
  sf.write(ROOT/f'audio/{l}/narration.wav',track,SR,subtype='PCM_16')
  save(ROOT/f'records/narration_timeline_{l}.json',{'language':l,'duration_seconds':duration,'segments':segments})
  save(ROOT/f'records/subtitle_cues_{l}.json',{'count':len(sub),'cues':sub,'timing':'Exact synthesized sentence boundaries; within-sentence pages weighted by text length','script_matches_ignoring_layout_whitespace':True})
  (ROOT/f'deliverables/EP004_Pandora_{l}_v01_1080p30.srt').write_text(to_srt(sub))
  subchecks[l]={'count':len(sub),'min_seconds':min(c['end']-c['start'] for c in sub),'max_line_chars':max(len(line) for c in sub for line in c['text'].splitlines()),'script_matches':True}
 save(ROOT/'records/reading_replacements.json',replacements);save(ROOT/'records/subtitle_validation.json',subchecks)
 print('TIMELINE',duration,'OPENING',op,'ENDCARD',endcard,'SUBTITLES',subchecks,flush=True)

def audio():
 m=read(ROOT/'records/master_timeline.json');duration=m['duration_seconds'];n=round(duration*SR);t=np.arange(n)/SR
 base=.006*np.sin(2*np.pi*146.832384*t)*(.66+.34*np.sin(2*np.pi*t/53)**2)+.003*np.sin(2*np.pi*220*t+.5)
 notes=np.array([293.664768,349.228231,440.,391.995436,293.664768,523.251131]);local=t%14;pitch=notes[np.floor(t/14).astype(int)%len(notes)]
 pluck=.018*np.sin(2*np.pi*pitch*local)*np.exp(-local/2.1)*(1-np.exp(-local/.045))
 music=np.stack([base+pluck,base+.92*pluck+.0017*np.sin(2*np.pi*293.664768*t+.45)],axis=1).astype(np.float32)
 mask=np.zeros(n,bool);duck=np.ones(n,np.float32)
 for s in m['segments']:
  a,b=s['start'],s['speech_end'];mask[round(a*SR):round(b*SR)]=True
  duck=np.minimum(duck,1-np.minimum(np.clip((t-(a-.18))/.18,0,1),np.clip((b+.4-t)/.4,0,1)))
 music*=10**((-33.5-rms(music[mask]))/20);music*=10**((4*duck)/20)[:,None];music*=np.clip(t/.7,0,1)[:,None]
 for key,p in [('opening',OP),('endcard',END)]:
  a,b=m['brand_intervals'][key];music[round(a*SR):round(b*SR)]=0
  # 200ms local fades at junctions; approved card audio keeps its original level.
  for boundary,reverse in [(a,False),(b,True)]:
   if boundary>=duration:continue
   i,j=(round((boundary-.2)*SR),round(boundary*SR)) if not reverse else (round(boundary*SR),round((boundary+.2)*SR))
   music[i:j]*=np.linspace(1 if not reverse else 0,0 if not reverse else 1,j-i)[:,None]
  wav=ROOT/f'_work/{key}.wav';ff(['-i',p,'-vn','-ar',SR,'-ac',2,'-c:a','pcm_f32le',wav]);audi,sr=sf.read(wav,dtype='float32');count=round((b-a)*SR)
  music[round(a*SR):round(b*SR)]=np.pad(audi[:count],((0,max(0,count-len(audi))),(0,0)))
 sf.write(ROOT/'audio/common_bgm_and_brand.wav',music,SR,subtype='FLOAT');report={'bgm_during_narration_dbfs':rms(music[mask]),'pause_boost_db':4,'languages':{}}
 for l in ['en','ja']:
  dry=ROOT/f'audio/{l}/narration.wav';q=measure(dry);normal=ROOT/f'audio/{l}/normalized.wav'
  filt=f"loudnorm=I=-16:TP=-3:LRA=7:linear=true:measured_I={q['input_i']}:measured_TP={q['input_tp']}:measured_LRA={q['input_lra']}:measured_thresh={q['input_thresh']}:offset={q['target_offset']}"
  ff(['-i',dry,'-af',filt,'-ar',SR,'-c:a','pcm_f32le',normal]);voice,sr=sf.read(normal,dtype='float32');voice=np.pad(voice[:n],(0,max(0,n-len(voice))))
  mix=ROOT/f'audio/{l}/mix.wav';gain=0
  for _ in range(5):
   sf.write(mix,voice[:,None]*10**(gain/20)+music,SR,subtype='FLOAT');q=measure(mix);delta=-16-float(q['input_i'])
   if abs(delta)<.08:break
   gain+=delta
  assert float(q['input_tp'])<=-1
  out=ROOT/f'deliverables/EP004_audio_{l}.m4a';ff(['-i',mix,'-ar',48000,'-c:a','aac','-b:a','192k','-movie_timescale',48000,out]);report['languages'][l]=measure(out)
  ff(['-i',mix,'-ar',48000,'-af',f'aresample=48000,apad=whole_len={round(duration*48000)},atrim=end_sample={round(duration*48000)}','-c:a','pcm_s24le',ROOT/f'deliverables/EP004_audio_{l}.wav'])
  print('AUDIO',l,report['languages'][l],flush=True)
 save(ROOT/'records/audio_qc.json',report)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','en','ja','timeline','audio']);a=p.parse_args()
 if a.stage in ['en','ja']:narrate(a.stage)
 else:globals()[a.stage]()
