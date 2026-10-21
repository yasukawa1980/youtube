"""Free local VOICEVOX prosody audition, preserving all existing full versions.

WOM_AUDITION_ROOT is a new dedicated output folder; WOM_PREVIOUS_ROOT is v03.
WOM_VOICEVOX_RUNTIME points to the existing Core 0.17.0 / VVM 0.16.4 runtime.
A reuses v03 dry narration. B/C synthesize N01-N04 without English-slot fitting.
All variants use the same score, loudness target and voice (style 14).
"""
import os,json,copy
from dataclasses import asdict
from pathlib import Path
import numpy as np
import soundfile as sf
from voicevox_core.blocking import Onnxruntime,OpenJtalk,Synthesizer,VoiceModelFile
from wom01_multilingual_render import ff,read,save,sha,measure,rms
from wom01_multilingual_narration import spoken_ja
from wom01_subtitles import sentence_cues,to_srt
SR=24000
# A sentence's role determines its delivery, rather than applying one setting to all.
ROLES={'N01-01':'opening','N01-03':'name','N01-05':'contrast','N02-01':'question',
       'N02-02':'list','N02-04':'guide','N03-01':'explanation','N03-02':'explanation',
       'N03-03':'transition','N04-02':'contrast','N04-03':'explanation','N04-04':'conclusion'}
SPEED={'opening':.97,'name':.99,'contrast':.98,'question':.97,'list':1.0,'guide':1.02,
       'explanation':1.02,'transition':1.0,'conclusion':.98,'plain':1.0}
INTONATION={'opening':1.04,'name':1.05,'contrast':1.08,'question':1.08,'list':1.03,
            'guide':1.03,'explanation':1.0,'transition':1.04,'conclusion':1.04,'plain':1.03}
# Pauses at the original commas, in order. Text and meanings are not rewritten.
PAUSES={'N01-01':[.24],'N01-02':[.20],'N01-03':[.20,.26],'N01-04':[.18],
        'N01-05':[.28,.24],'N02-01':[.23],'N02-02':[.23,.23],'N02-04':[.20,.26,.18],
        'N03-01':[.17],'N03-03':[.23],'N04-01':[.23],'N04-02':[.16,.22,.27],
        'N04-03':[.23],'N04-04':[.22]}
def main():
 root=Path(os.environ['WOM_AUDITION_ROOT']).resolve();previous=Path(os.environ['WOM_PREVIOUS_ROOT']).resolve()
 assert root!=previous and not (root/'records/completed.json').exists(), 'Choose a fresh output folder'
 runtime=Path(os.environ['WOM_VOICEVOX_RUNTIME'])
 for d in ['records','deliverables','_work/A','_work/B','_work/C']: (root/d).mkdir(parents=True,exist_ok=True)
 source=read(previous/'records/narration_timeline_ja.json');segments=source['segments'][:4]
 assert [s['id'] for s in segments]==['N01','N02','N03','N04']
 model=runtime/'models/vvms/1.vvm';assert sha(model)=='8df20815be9a84a4b4723b9e778d2ef6a4df277e4872fe9efe29676a60e02774'
 synth=Synthesizer(Onnxruntime.load_once(filename=str(next((runtime/'onnxruntime/lib').glob('*.dylib')))),OpenJtalk(str(runtime/'dict/open_jtalk_dic_utf_8-1.11')),acceleration_mode='CPU',cpu_num_threads=2)
 with VoiceModelFile.open(str(model)) as m:synth.load_voice_model(m)
 tracks={};timelines={};settings=[]
 a,sr=sf.read(previous/'audio/ja/narration.wav',frames=round(87.5*SR),dtype='float32');assert sr==SR
 tracks['A']=a;timelines['A']=[copy.deepcopy(c) for s in segments for c in s['cues']]
 for variant in ['B','C']:
  pieces=[np.zeros(round(1.8*SR),np.float32)];cursor=len(pieces[0]);cues=[]
  for si,seg in enumerate(segments):
   for ci,c in enumerate(seg['cues']):
    role=ROLES.get(c['id'],'plain');q=synth.create_audio_query(spoken_ja(c['text']),14)
    q.speed_scale=SPEED[role]-(.015 if variant=='C' else 0)
    q.intonation_scale=INTONATION[role]+(.10 if variant=='C' else 0)
    q.pre_phoneme_length=.055;q.post_phoneme_length=.09;q.output_sampling_rate=SR
    pause_index=0
    for phrase in q.accent_phrases:
     if phrase.pause_mora is not None:
      values=PAUSES.get(c['id'],[])
      base=values[pause_index] if pause_index<len(values) else .20
      phrase.pause_mora['vowel_length']=base+(.055 if variant=='C' else 0)
      pause_index+=1
    out=root/f'_work/{variant}/{c["id"]}.wav';query=asdict(q)
    out.write_bytes(synth.synthesis(q,14));audio,sr=sf.read(out,dtype='float32');assert sr==SR
    start=cursor/SR;pieces.append(audio);cursor+=len(audio)
    cues.append({'id':c['id'],'text':c['text'],'start':start,'end':cursor/SR})
    gap=.30 if role in ['opening','contrast','question','conclusion'] else .22
    if ci==len(seg['cues'])-1:gap=.80
    if variant=='C':gap+=.10
    pieces.append(np.zeros(round(gap*SR),np.float32));cursor+=len(pieces[-1])
    settings.append({'variant':variant,'sentence_id':c['id'],'role':role,'query':query,'gap_after_seconds':gap,'audio_sha256':sha(out)})
    print(variant,c['id'],round(len(audio)/SR,3),flush=True)
  pieces.append(np.zeros(round(1.2*SR),np.float32));tracks[variant]=np.concatenate(pieces);timelines[variant]=cues
 save(root/'records/queries.json',settings)
 duration=max(len(x) for x in tracks.values())/SR
 n=round(duration*SR);t=np.arange(n)/SR
 # Same synthesized score as v03, with a constant bed for controlled comparison.
 slow=.66+.34*np.sin(2*np.pi*t/53)**2
 base=.006*np.sin(2*np.pi*146.832384*t)*slow+.003*np.sin(2*np.pi*220*t+.5)
 notes=np.array([293.664768,349.228231,440.,391.995436,293.664768,523.251131]);local=t%14
 pitch=notes[np.floor(t/14).astype(int)%len(notes)]
 pluck=.018*np.sin(2*np.pi*pitch*local)*np.exp(-local/2.1)*(1-np.exp(-local/.045))
 music=np.stack([base+pluck,base+.92*pluck+.0017*np.sin(2*np.pi*293.664768*t+.45)],axis=1).astype(np.float32)
 music*=10**((-33.5-rms(music))/20);music*=np.minimum(np.clip(t/.7,0,1),np.clip((duration-t)/2,0,1))[:,None]
 sf.write(root/'_work/common_bgm.wav',music,SR,subtype='FLOAT')
 qc={'voice':'VOICEVOX:冥鳴ひまり','style_id':14,'model_sha256':sha(model),'source_root':str(previous),
     'source_dry_sha256':sha(previous/'audio/ja/narration.wav'),'selected_segments':['N01','N02','N03','N04'],
     'sentence_count_each':16,'paid_services':False,'human_listening_completed':False,'full_version_changed':False,
     'bgm':'Same score for all candidates, constant -33.5 dBFS before fades; no pause boost in this comparison.',
     'common_duration_seconds':duration,'variants':{}}
 for v,track in tracks.items():
  track=np.pad(track,(0,n-len(track)));dry=root/f'_work/{v}/dry.wav';sf.write(dry,track,SR,subtype='FLOAT')
  first=measure(dry)
  norm=(f"loudnorm=I=-16:TP=-3:LRA=7:linear=true:measured_I={first['input_i']}:measured_TP={first['input_tp']}:measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:offset={first['target_offset']}")
  normalized=root/f'_work/{v}/normalized.wav';ff(['-i',dry,'-af',norm,'-ar',SR,'-ac',1,'-c:a','pcm_f32le',normalized])
  voice,sr=sf.read(normalized,dtype='float32');assert sr==SR and abs(len(voice)-n)<10
  voice=np.pad(voice[:n],(0,max(0,n-len(voice))))
  mixed=root/f'_work/{v}/mix.wav';gain=0
  for _ in range(4):
   sf.write(mixed,voice[:,None]*10**(gain/20)+music,SR,subtype='FLOAT')
   stats=measure(mixed);correction=-16-float(stats['input_i'])
   if abs(correction)<.1:break
   gain+=correction
  assert float(stats['input_tp'])<=-2
  outputs={}
  for suffix,src in [('BGM',mixed),('voice_only',normalized)]:
   dst=root/f'deliverables/EP001_ja_{v}_{suffix}.m4a'
   ff(['-i',src,'-c:a','aac','-b:a','192k','-metadata','artist=VOICEVOX:冥鳴ひまり','-metadata','title=EP001 Japanese audition '+v+' '+suffix,'-movflags','+faststart',dst])
   stats=measure(dst);assert abs(float(stats['input_i'])+16)<.2 and float(stats['input_tp'])<-1.5
   ff(['-i',dst,'-f','null','-'])
   outputs[suffix]={'file':dst.name,'sha256':sha(dst),'bytes':dst.stat().st_size,'loudness':stats}
  cues=timelines[v];assert len(cues)==16
  assert [x['text'] for x in cues]==[c['text'] for s in segments for c in s['cues']]
  assert all(0<=c['start']<c['end']<=duration for c in cues)
  assert all(a['end']<=b['start'] for a,b in zip(cues,cues[1:]))
  subtitles=[p for c in cues for p in sentence_cues(c,'ja')]
  (root/f'deliverables/EP001_ja_{v}.srt').write_text(to_srt(subtitles),encoding='utf-8')
  save(root/f'records/timeline_{v}.json',{'duration_seconds':duration,'voice':qc['voice'],'cues':cues})
  qc['variants'][v]={'speech_end_seconds':cues[-1]['end'],'audio':outputs}
  print('FINISHED',v,'duration',duration,flush=True)
 save(root/'records/qc.json',qc)
 files=sorted((root/'deliverables').glob('*'))
 (root/'deliverables/SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files),encoding='utf-8')
 save(root/'records/completed.json',{'complete':True,'duration_seconds':duration})
if __name__=='__main__':main()
