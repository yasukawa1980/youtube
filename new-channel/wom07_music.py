"""Selected Suno tracks, recorded source spans, narration-aware ducking and brand preservation."""
import math
import numpy as np
import soundfile as sf
from wom07_produce import ROOT,SR,OP,END,read,save,sha,ff,measure,rms
from pathlib import Path
BGM=Path('/Users/ryo/Desktop/新チャンネル/_共通/BGM/20261029_Suno')
def band_energy(a):
 x=a.mean(axis=1);size=32768;power=np.zeros(size//2+1)
 for i in range(0,len(x)-size+1,size):power+=abs(np.fft.rfft(x[i:i+size]*np.hanning(size)))**2
 f=np.fft.rfftfreq(size,1/SR);return {name:float(power[mask].sum()/power.sum()*100) for name,mask in [('below_200Hz',f<200),('200_to_2000Hz',(f>=200)&(f<2000)),('at_or_above_2000Hz',f>=2000)]}
def build_audio():
 m=read(ROOT/'records/master_timeline.json');duration=m['duration_seconds'];n=round(duration*SR);t=np.arange(n)/SR
 tracks={};spans=[]
 for key in ['QO_THEME_A02','QO_AMERICA01']:
  src=BGM/(key+'.wav');out=ROOT/f'_work/{key}_filtered.wav'
  ff(['-i',src,'-af','highpass=f=100:p=2,equalizer=f=2828:t=o:w=1:g=-3.5','-ar',SR,'-ac',2,'-c:a','pcm_f32le',out]);a,sr=sf.read(out,dtype='float32');a*=10**((-23-rms(a))/20);tracks[key]=a
 a=tracks['QO_THEME_A02'];music=np.zeros((n,2),np.float32);weights=np.zeros(n,np.float32);fade=3.0;length=min(len(a)/SR-2,160);start=0
 while start<duration:
  count=min(round(length*SR),n-round(start*SR));source=round(10*SR);part=a[source:source+count]
  if len(part)<count:raise ValueError('Source span outside selected track')
  env=np.ones(count,np.float32);f=min(round(fade*SR),count)
  if start>0:env[:f]=np.linspace(0,1,f)
  if start+count/SR<duration:env[-f:]=np.linspace(1,0,f)
  lo=round(start*SR);music[lo:lo+count]+=part*env[:,None];weights[lo:lo+count]+=env
  spans.append({'track':'QO_THEME_A02','source_start':10,'source_end':10+count/SR,'timeline_start':start,'timeline_end':start+count/SR,'crossfade_seconds':fade});start+=length-fade
 assert np.all(weights>.99)
 music/=weights[:,None]
 seg={s['id']:s for s in m['segments']}
 for first,last,source in [('P04','P06',45.0),('P09','P10',90.0)]:
  start=seg[first]['start']-fade/2;end=seg[last]['end'];lo=round(start*SR);hi=round(end*SR);count=hi-lo
  src=tracks['QO_AMERICA01'];source=min(source,len(src)/SR-count/SR-1);part=src[round(source*SR):round(source*SR)+count];assert len(part)==count
  env=np.minimum(np.clip((t[lo:hi]-start)/fade,0,1),np.clip((end-t[lo:hi])/fade,0,1)).astype(np.float32)
  music[lo:hi]=music[lo:hi]*(1-env[:,None])+part*env[:,None]
  spans.append({'track':'QO_AMERICA01','source_start':source,'source_end':source+count/SR,'timeline_start':start,'timeline_end':end,'crossfade_seconds':fade})
 common=music.copy();brand=np.zeros_like(common);brandmask=np.zeros(n,bool)
 for key,path in [('opening',OP),('endcard',END)]:
  start,end=m['brand_intervals'][key];lo=round(start*SR);hi=round(end*SR);brandmask[lo:hi]=True;common[lo:hi]=0
  for boundary,reverse in [(start,False),(end,True)]:
   if boundary>=duration:continue
   i,j=(round((boundary-.15)*SR),round(boundary*SR)) if not reverse else (round(boundary*SR),round((boundary+.15)*SR))
   common[i:j]*=np.linspace(0 if reverse else 1,1 if reverse else 0,j-i)[:,None]
  out=ROOT/f'_work/{key}.wav';ff(['-i',path,'-vn','-ar',SR,'-ac',2,'-c:a','pcm_f32le',out]);b,sr=sf.read(out,dtype='float32');assert len(b)>=hi-lo;brand[lo:hi]=b[:hi-lo]
 # Opening begins with audible music under the first picture; no long fade from silence.
 common[:round(.08*SR)]*=np.linspace(.35,1,round(.08*SR))[:,None]
 report={'selection':{'common':'QO_THEME_A02','america':'QO_AMERICA01'},'sources':{k:{'path':str(BGM/(k+'.wav')),'sha256':sha(BGM/(k+'.wav'))} for k in tracks},'source_spans':spans,'filters':'highpass 100 Hz, 2 poles; equalizer 2828 Hz, one octave, -3.5 dB','pause_boost_db':6,'crossfade_seconds':3,'bgm_bands_percent':band_energy(common[~brandmask]),'languages':{}}
 sf.write(ROOT/'audio/common_selected_bgm.wav',common,SR,subtype='FLOAT')
 for lang in ['en','ja']:
  cues=[c for s in read(ROOT/f'records/narration_timeline_{lang}.json')['segments'] for c in s['cues']]
  mask=np.zeros(n,bool);envelope=np.ones(n,np.float32)
  for c in cues:
   start,end=c['start'],c['end'];mask[round(start*SR):round(end*SR)]=True
   # 180 ms anticipation and 250 ms release; short clause gaps do not pump.
   lo=max(0,round((start-.18)*SR));hi=min(n,round((end+.25)*SR));tt=t[lo:hi]
   down=np.minimum(np.clip((tt-(start-.18))/.18,0,1),np.clip((end+.25-tt)/.25,0,1));envelope[lo:hi]=np.minimum(envelope[lo:hi],1-down)
  dry=ROOT/f'audio/{lang}/narration.wav';q=measure(dry);normal=ROOT/f'audio/{lang}/normalized.wav'
  filt=f"loudnorm=I=-16:TP=-3:LRA=7:linear=true:measured_I={q['input_i']}:measured_TP={q['input_tp']}:measured_LRA={q['input_lra']}:measured_thresh={q['input_thresh']}:offset={q['target_offset']}"
  ff(['-i',dry,'-af',filt,'-ar',SR,'-c:a','pcm_f32le',normal]);voice,sr=sf.read(normal,dtype='float32');voice=np.pad(voice[:n],(0,max(0,n-len(voice))))
  voice[brandmask]=0 # Resampler pre-ringing must not enter the unchanged brand intervals.
  speechmask=mask&~brandmask;target=rms(voice[speechmask])-18
  bgm=common*10**((target-rms(common[speechmask]))/20)*10**((6*envelope[:,None])/20)
  mix=ROOT/f'audio/{lang}/mix.wav';gain=0
  for _ in range(6):
   v=voice*10**(gain/20);b=bgm*10**(gain/20);sf.write(mix,v[:,None]+b+brand,SR,subtype='FLOAT');q=measure(mix);delta=-16-float(q['input_i'])
   if abs(delta)<.07:break
   gain+=delta
  assert float(q['input_tp'])<=-1,q
  sf.write(ROOT/f'audio/{lang}/selected_bgm_ducked.wav',b,SR,subtype='FLOAT')
  breaks=(envelope>.99)&~brandmask
  out=ROOT/f'deliverables/EP007_audio_{lang}.m4a';ff(['-i',mix,'-ar',48000,'-c:a','aac','-b:a','192k','-movie_timescale',48000,out])
  ff(['-i',mix,'-ar',48000,'-af',f'aresample=48000,apad=whole_len={round(duration*48000)},atrim=end_sample={round(duration*48000)}','-c:a','pcm_s24le',ROOT/f'deliverables/EP007_audio_{lang}.wav'])
  report['languages'][lang]={'levels':measure(out),'voice_during_narration_dbfs':rms(v[speechmask]),'bgm_during_narration_dbfs':rms(b[speechmask]),'bgm_during_full_boost_breaks_dbfs':rms(b[breaks]),'voice_minus_bgm_db':rms(v[speechmask])-rms(b[speechmask]),'break_samples':int(breaks.sum()),'band_percent':band_energy(b[~brandmask]),'brand_samples_unchanged':True}
  print('AUDIO',lang,report['languages'][lang],flush=True)
 save(ROOT/'records/audio_qc.json',report)
if __name__=='__main__':build_audio()
