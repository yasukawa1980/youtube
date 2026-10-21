"""v08: move existing Japanese N01 samples; v02 ident +7 dB. No TTS, no picture change."""
import argparse, copy, os, re, shutil, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw
from wom01_multilingual_render import read, save, sha, ff, measure, probe

BASE=Path('/Users/ryo/Desktop/新チャンネル')
OLD=BASE/'EP001_Anubis/Quiet_Origins_v07_20261021'
AUDIO=BASE/'EP001_Anubis/C採用_はかり修正_v04_20261021'
ROOT=BASE/'EP001_Anubis/Quiet_Origins_v08_20261021'
MOLD=BASE/'ブランド素材/オープニング_エンドカード_動画試作_v01_20261021'
MROOT=BASE/'ブランド素材/オープニング_エンドカード_動画試作_v02_20261021'
SHIFTS=[0,.8,1.6,2.6,4.1]
CUT=872/30

def stream_hash(p, stream):
 return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map',stream,'-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def prepare():
 assert not (ROOT/'records/audio_revision.json').exists(), 'Already prepared; do not overwrite'
 for root in [ROOT,MROOT]:
  for d in ['deliverables','records','_work','review']:(root/d).mkdir(parents=True,exist_ok=True)
 for p in (OLD/'records').glob('*.json'):
  if p.name in ['content.json','content_en.json','master_timeline.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_cues_en.json','subtitle_cues_ja.json']:
   shutil.copy2(p,ROOT/'records'/p.name)
 timeline=read(ROOT/'records/narration_timeline_ja.json');oldc=copy.deepcopy(timeline['segments'][0]['cues']);newc=timeline['segments'][0]['cues']
 for c,shift in zip(newc,SHIFTS):
  c['start']+=shift;c['end']+=shift
 timeline['segments'][0]['duration_seconds']+=4.1
 timeline['segments'][0]['delivery']='Existing C samples; N01 intersentence gaps +0.8,+0.8,+1.0,+1.5 seconds'
 save(ROOT/'records/narration_timeline_ja.json',timeline)
 for track,subtype in [('narration','PCM_16'),('normalized','FLOAT')]:
  original,sr=sf.read(AUDIO/f'audio/ja/{track}.wav',dtype='float32');new=original.copy()
  first=round(oldc[0]['start']*sr);last=round(CUT*sr)
  # Original gaps contain digital silence; verify before replacing only N01.
  mask=np.zeros(last-first,bool)
  padding=240 if track=='normalized' else 0
  for c in oldc:mask[max(0,round(c['start']*sr)-first-padding):round(c['end']*sr)-first+padding]=True
  assert np.max(np.abs(original[first:last][~mask]))<1e-6
  new[first:last]=0
  checks=[]
  for a,b in zip(oldc,newc):
   start=max(first,round(a['start']*sr)-padding);stop=round(a['end']*sr)+padding
   xpad=original[start:stop];j=start+round((b['start']-a['start'])*sr);new[j:j+len(xpad)]=xpad
   x=original[round(a['start']*sr):round(a['end']*sr)];i=round(b['start']*sr)
   assert np.array_equal(new[i:i+len(x)],x)
   if track=='narration':
    p=AUDIO/a['audio_file'];assert sha(p)==a['audio_sha256']
    raw,rs=sf.read(p,dtype='float32');assert rs==sr and np.array_equal(raw,x)
   checks.append({'id':a['id'],'old_start':a['start'],'new_start':b['start'],'new_end':b['end'],'samples_identical':True,'source_sha256':a['audio_sha256']})
  assert np.array_equal(new[last:],original[last:])
  out=ROOT/f'audio/ja/{track}.wav';out.parent.mkdir(parents=True,exist_ok=True);sf.write(out,new,sr,subtype=subtype)
  if track=='normalized':norm_old,norm_new=original,new
 save(ROOT/'records/voice_sample_checks.json',{'passed':True,'sentences':checks,'sample_rate':sr,'N02_onward_sample_identical':True,'wait_before_opening_seconds':CUT-newc[-1]['end'],'tts_regenerated':False})
 bgm_path=ROOT/'audio/common_bgm.wav';shutil.copy2(AUDIO/'audio/common_bgm.wav',bgm_path)
 assert sha(bgm_path)==read(OLD/'records/audio_qc.json')['bgm']['sha256']
 bgm,_=sf.read(bgm_path,dtype='float32');oldmix,_=sf.read(AUDIO/'audio/ja/mix.wav',dtype='float32')
 # Recover the original fixed narration gain (rounded to the original 0.01dB measurement precision).
 estimated=np.sum(norm_old[:last]*(oldmix[:last,0]-bgm[:last,0]))/np.sum(norm_old[:last]**2)
 gain_db=round(float(20*np.log10(estimated)),2);gain=10**(gain_db/20)
 assert np.max(np.abs(oldmix-(norm_old[:,None]*gain+bgm)))<1e-6
 mixed=oldmix.copy();mixed[first:last]=norm_new[first:last,None]*gain+bgm[first:last]
 assert np.array_equal(mixed[last:],oldmix[last:])
 sf.write(ROOT/'audio/ja/mix.wav',mixed,sr,subtype='FLOAT')
 ff(['-i',ROOT/'audio/ja/mix.wav','-ar',48000,'-c:a','pcm_s24le',ROOT/'deliverables/EP001_audio_ja.wav'])
 old_pcm,pcm_sr=sf.read(AUDIO/'deliverables/EP001_audio_ja.wav',dtype='int32');new_pcm,_=sf.read(ROOT/'deliverables/EP001_audio_ja.wav',dtype='int32')
 assert np.array_equal(old_pcm[round(CUT*pcm_sr):],new_pcm[round(CUT*pcm_sr):])
 ff(['-i',ROOT/'deliverables/EP001_audio_ja.wav','-c:a','aac','-b:a','192k','-metadata:s:a:0','language=jpn',ROOT/'deliverables/EP001_audio_ja.m4a'])
 for n in ['EP001_audio_en.m4a','EP001_thumbnail_en.jpg','VOICE_CREDITS.txt']:shutil.copy2(OLD/'deliverables'/n,ROOT/'deliverables'/n)
 env=dict(os.environ,WOM_EPISODE_ROOT=str(ROOT))
 subprocess.run([os.sys.executable,str(Path(__file__).with_name('wom01_rebuild_subtitles.py'))],env=env,check=True)
 for lang in ['en','ja']:
  s=ROOT/f'deliverables/EP001_字幕_{lang}.srt';old=OLD/f'deliverables/EP001_Anubis_{lang}_v07_1080p30.srt'
  if lang=='en':assert s.read_bytes()==old.read_bytes()
  else:assert s.read_bytes().split(b'\n\n')[6:]==old.read_bytes().split(b'\n\n')[6:]
  shutil.copy2(s,ROOT/f'deliverables/EP001_Anubis_{lang}_v08_1080p30.srt')
  src=OLD/f'deliverables/EP001_Anubis_{lang}_v07_1080p30.mp4';out=ROOT/f'deliverables/EP001_Anubis_{lang}_v08_1080p30.mp4'
  if lang=='en':shutil.copy2(src,out)
  else:ff(['-i',src,'-i',ROOT/'deliverables/EP001_audio_ja.m4a','-map','0:v','-map','1:a','-c','copy','-metadata','title=Quiet Origins / EP001 — Anubis v08','-movflags','+faststart',out])
 stats=measure(ROOT/'deliverables/EP001_audio_ja.m4a');assert abs(float(stats['input_i'])+16)<=.2
 save(ROOT/'records/audio_revision.json',{'narration_gain_db':gain_db,'bgm_sha256':sha(bgm_path),'bgm_identical_to_v07':True,'ja_audio':stats,'subtitle_N01_count':6,'subtitle_other_130_byte_identical':True,'english_srt_byte_identical':True,'full_ident_not_inserted':True,'final_48khz_pcm_N02_onward_sample_identical':True,'normalized_sample_padding_seconds':.01})
 print('PREPARED',stats,flush=True)

def reviews():
 import imageio_ffmpeg
 r=ROOT/'subtitled_review'
 for d in ['deliverables','records','review','_work']:(r/d).mkdir(parents=True,exist_ok=True)
 # English picture/audio/subtitles unchanged: preserve the existing review byte-for-byte.
 shutil.copy2(OLD/'subtitled_review/deliverables/EP001_Anubis_en_v07_subtitled_review_1080p30.mp4',r/'deliverables/EP001_Anubis_en_v08_subtitled_review_1080p30.mp4')
 srt=ROOT/'deliverables/EP001_Anubis_ja_v08_1080p30.srt';shutil.copy2(srt,r/'_work/ja.srt')
 src=ROOT/'deliverables/EP001_Anubis_ja_v08_1080p30.mp4';out=r/'deliverables/EP001_Anubis_ja_v08_subtitled_review_1080p30.mp4'
 vf=f"subtitles='{r}/_work/ja.srt':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','warning','-i',str(src),'-vf',vf,'-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart','-progress',str(r/'_work/progress_ja.txt'),str(out)],check=True)
 save(r/'records/render_request.json',{'inputs':[{'language':lang,'video_sha256':sha(ROOT/f'deliverables/EP001_Anubis_{lang}_v08_1080p30.mp4'),'srt_sha256':sha(ROOT/f'deliverables/EP001_Anubis_{lang}_v08_1080p30.srt')} for lang in ['en','ja']]})
 print('REVIEWS DONE',flush=True)

def motion():
 for p in (MOLD/'deliverables').iterdir():
  if 'endcard' in p.name:shutil.copy2(p,MROOT/'deliverables'/p.name)
 oldwav=MOLD/'deliverables/Quiet_Origins_opening_trial_v01.wav';x,sr=sf.read(oldwav);y=x*10**(7/20)
 wav=MROOT/'deliverables/Quiet_Origins_opening_trial_v02.wav';sf.write(wav,y,sr,subtype='PCM_24')
 op=MROOT/'deliverables/Quiet_Origins_opening_trial_v02.mp4'
 ff(['-i',MOLD/'deliverables/Quiet_Origins_opening_trial_v01.mp4','-i',wav,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-ar',48000,'-t',4,'-movflags','+faststart',op])
 assert stream_hash(op,'0:v')==stream_hash(MOLD/'deliverables/Quiet_Origins_opening_trial_v01.mp4','0:v')
 stats=measure(wav);assert abs(float(stats['input_i'])+22)<.1 and float(stats['input_tp'])<-1
 save(MROOT/'records/opening_audio.json',{'gain_db':7,'wav':stats,'picture_stream_identical_to_v01':True,'tone_duration_fades_unchanged':True})
 end=1555/30
 for lang in ['en','ja']:
  src=ROOT/f'subtitled_review/deliverables/EP001_Anubis_{lang}_v08_subtitled_review_1080p30.mp4'
  filt=f"[0:v]trim=0:{CUT},setpts=PTS-STARTPTS[v0];[0:a]atrim=0:{CUT},asetpts=PTS-STARTPTS,aresample=48000,afade=t=out:st={CUT-.12}:d=0.12[a0];[1:v]setpts=PTS-STARTPTS[v1];[1:a]aresample=48000,asetpts=PTS-STARTPTS[a1];[0:v]trim=start={CUT}:end={end},setpts=PTS-STARTPTS[v2];[0:a]atrim=start={CUT}:end={end},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.015[a2];[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]"
  out=MROOT/f'deliverables/EP001_{lang}_opening_connection_trial_v02.mp4'
  ff(['-i',src,'-i',op,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf',18,'-threads',4,'-c:a','aac','-b:a','192k','-ar',48000,'-r',30,'-video_track_timescale',15360,'-movflags','+faststart',out])
 print('MOTION DONE',flush=True)

def verify():
 results=[]
 for root in [ROOT,MROOT]:
  paths=list((root/'deliverables').glob('*.mp4'))
  if root==ROOT:paths+=list((root/'subtitled_review/deliverables').glob('*.mp4'))
  for p in paths:
   q=probe(p);v=next(s for s in q['streams'] if s['codec_type']=='video');frames=20481 if root==ROOT else 1675 if 'opening_connection' in p.name else 1200 if 'endcard_connection' in p.name else 120 if 'opening_trial' in p.name else 600
   assert int(v['nb_frames'])==frames and v['avg_frame_rate']=='30/1' and v['width']==1920 and v['height']==1080
   pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert pts==list(range(0,frames*512,512))
   ff(['-i',p,'-f','null','-']);levels=measure(p);assert float(levels['input_tp'])<-1
   results.append({'file':str(p.relative_to(BASE)),'frames':frames,'duration':float(q['format']['duration']),'full_decode':True,'exact_pts':True,'audio':levels,'sha256':sha(p)})
   print('VERIFIED',p.name,flush=True)
 for lang in ['en','ja']:
  new=ROOT/f'deliverables/EP001_Anubis_{lang}_v08_1080p30.mp4';old=OLD/f'deliverables/EP001_Anubis_{lang}_v07_1080p30.mp4';assert stream_hash(new,'0:v')==stream_hash(old,'0:v')
  if lang=='en':assert stream_hash(new,'0:a')==stream_hash(old,'0:a')
 for p in (MROOT/'deliverables').glob('*endcard*'):assert sha(p)==sha(MOLD/'deliverables'/p.name)
 # EBU short-term values with a full 3s window inside the 4s ident (exclude speech-straddling windows).
 short={}
 for lang in ['en','ja']:
  p=MROOT/f'deliverables/EP001_{lang}_opening_connection_trial_v02.mp4'
  r=subprocess.run(['ffmpeg','-hide_banner','-i',str(p),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,check=True)
  pairs=[(float(a),float(b)) for a,b in re.findall(r't:\s*([\d.]+).*?S:\s*(-?[\d.]+)',r.stderr)]
  vals=[b for a,b in pairs if CUT+3<=a<CUT+4];assert vals and all(-23<=v<=-20 for v in vals),(lang,vals)
  short[lang]={'window_end_times':[a for a,b in pairs if CUT+3<=a<CUT+4],'short_term_lufs':vals}
 save(ROOT/'records/qc_v08.json',{'passed':True,'files':[r for r in results if 'Quiet_Origins_v08' in r['file']],'v07_video_streams_identical':True,'english_audio_stream_identical':True,'human_listening':False})
 save(MROOT/'records/qc_v02.json',{'passed':True,'files':[r for r in results if '動画試作_v02' in r['file']],'short_term_opening':short,'endcard_files_byte_identical_to_v01':True,'human_listening':False})
 # Retain proof that every previously shared v07 master remains unchanged.
 for line in (OLD/'deliverables/SHA256SUMS_shared.txt').read_text().splitlines():
  digest,name=line.split('  ',1);matches=list((OLD/'deliverables').glob(name))+list((OLD/'subtitled_review/deliverables').glob(name));assert matches and all(sha(p)==digest for p in matches)
 print('ALL CHECKS PASSED',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','reviews','motion','verify']);a=p.parse_args()
 if a.stage!='verify':assert not (ROOT/'records/sharing.json').exists(), 'Shared outputs are immutable; use a new version'
 globals()[a.stage]()
