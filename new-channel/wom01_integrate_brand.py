"""v09 full assembly from approved v08 / opening v02 / end-card v01; no publication."""
import argparse,copy,os,re,shutil,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw
from wom01_multilingual_render import ff,save,read,sha,probe,measure
from wom01_subtitled_review import cues
BASE=Path('/Users/ryo/Desktop/新チャンネル')
OLD=BASE/'EP001_Anubis/Quiet_Origins_v08_20261021'
BRAND=BASE/'ブランド素材/オープニング_エンドカード_動画試作_v02_20261021'
ROOT=BASE/'EP001_Anubis/Quiet_Origins_v09_20261021'
REPO=Path(__file__).resolve().parent.parent
CUT=872/30; SOURCE_END=678.7; END_START=682.; DURATION=702.; FRAMES=21060; SR=48000
OP=BRAND/'deliverables/Quiet_Origins_opening_trial_v02.mp4'
END=BRAND/'deliverables/Quiet_Origins_endcard_trial_v01.mp4'

def stamp(ms):
 h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def milliseconds(t):
 h,m,s,ms=map(int,re.split('[:,]',t));return ((h*60+m)*60+s)*1000+ms

def validate_metadata():
 chapters=read(ROOT/'records/chapters.json')['chapters'];results=[]
 for lang in ['en','ja']:
  p=ROOT/f'deliverables/EP001_投稿用情報_{lang}.md';s=p.read_text()
  actual=re.findall(r'^(\d\d:\d\d) (.+)$',s,re.M);assert actual==[(c['timestamp'],c[lang]) for c in chapters]
  assert 'VOICEVOX:冥鳴ひまり' in s and '雀松朱司' not in s
  assert p.read_bytes()==(REPO/f'new-channel/episodes/EP001_Anubis/deliverables/{p.name}').read_bytes()
  results.append({'language':lang,'chapters':len(actual),'all_times_titles_match':True,'current_voice_credit':True,'repo_local_byte_identical':True})
 combined=(REPO/'new-channel/wom01_アップロード情報.md').read_text();assert len(re.findall(r'^\d\d:\d\d ',combined,re.M))==14
 save(ROOT/'records/metadata_validation.json',{'passed':True,'languages':results,'combined_chapter_entries':14})

def preserve_sources():
 checked=[]
 for root in [OLD,BRAND]:
  for line in (root/'deliverables/SHA256SUMS_shared.txt').read_text().splitlines():
   digest,name=line.split('  ',1);ps=list((root/'deliverables').glob(name))+list((root/'subtitled_review/deliverables').glob(name))
   assert ps and all(sha(p)==digest for p in ps);checked.append({'name':name,'sha256':digest})
 save(ROOT/'records/source_preservation.json',{'passed':True,'checked_files':checked,'source_roots':[str(OLD),str(BRAND)]})

def prepare():
 assert not ROOT.exists()
 for d in ['_work','records','review','deliverables']:(ROOT/d).mkdir(parents=True)
 master=read(OLD/'records/master_timeline.json');master['duration_seconds']=DURATION
 for seg in master['segments']:
  if seg['id']!='N01':
   for key in ['start','speech_end','end']:
    if key in seg:seg[key]=min(seg[key],SOURCE_END)+4
 master['brand_intervals']={'opening':[CUT,CUT+4],'endcard':[END_START,DURATION],'end_dissolve':[682,682.7]}
 save(ROOT/'records/master_timeline.json',master)
 for lang in ['en','ja']:
  old=OLD/f'deliverables/EP001_Anubis_{lang}_v08_1080p30.srt';blocks=old.read_text().strip().split('\n\n');new=[]
  for block in blocks:
   lines=block.splitlines();a,b=map(milliseconds,lines[1].split(' --> '));assert b<=29067 or a>=29067
   if a>=29067:a+=4000;b+=4000
   lines[1]=f'{stamp(a)} --> {stamp(b)}';new.append('\n'.join(lines))
  out=ROOT/f'deliverables/EP001_Anubis_{lang}_v09_1080p30.srt';out.write_text('\n\n'.join(new)+'\n')
  cs=cues(out);assert len(cs)==(150 if lang=='en' else 136);assert max(c['end'] for c in cs)<END_START
  for a,b in zip(cues(old),cs):
   assert a['text']==b['text'];delta=4 if a['start']>=29.067 else 0
   assert abs(b['start']-a['start']-delta)<1e-6 and abs(b['end']-a['end']-delta)<1e-6
  save(ROOT/f'records/subtitle_cues_{lang}.json',{'count':len(cs),'cues':cs,'body_linebreaks_and_count_identical':True,'timing_rule':'All N02 onward cues +4.000 seconds'})
  tl=read(OLD/f'records/narration_timeline_{lang}.json');tl['duration_seconds']=DURATION
  for seg in tl['segments']:
   if seg['id']!='N01':
    seg['start']+=4;seg['end']=min(seg['end'],SOURCE_END)+4
    for c in seg['cues']:c['start']+=4;c['end']+=4
  save(ROOT/f'records/narration_timeline_{lang}.json',tl)
 for name in ['VOICE_CREDITS.txt','EP001_thumbnail_en.jpg']:shutil.copy2(OLD/'deliverables'/name,ROOT/'deliverables'/name)
 chapters=[]
 original=read(OLD/'records/master_timeline.json')
 for i,ch in enumerate(read(OLD/'records/content.json')['chapters']):
  seg=next(s for s in original['segments'] if s['chapter']==ch['id']);actual=0 if i==0 else seg['start']+4;display=int(actual)
  en=read(OLD/'records/content_en.json')['chapters'][i]['title'];chapters.append({'id':ch['id'],'actual_seconds':actual,'display_seconds':display,'timestamp':f'{display//60:02}:{display%60:02}','ja':ch['title'],'en':en})
  assert actual-display<1
 save(ROOT/'records/chapters.json',{'chapters':chapters,'measurement':'First frame of chapter from approved v08 timeline +120 frames; C01 starts at video frame 0'})
 for lang in ['en','ja']:
  p=REPO/f'new-channel/episodes/EP001_Anubis/deliverables/EP001_投稿用情報_{lang}.md';s=p.read_text()
  block='Chapters\n'+'\n'.join(c['timestamp']+' '+c[lang] for c in chapters)
  s=re.sub(r'Chapters\n(?:\d\d:\d\d[^\n]*\n?)+',block+'\n',s)
  s=s.replace('VOICEVOX:雀松朱司','VOICEVOX:冥鳴ひまり').replace('英語・日本語の共通尺確定。','Quiet Origins / v09。英語・日本語の共通尺11分42秒（702秒）。オープニング・エンドカード組み込み済み。')
  s=s.replace('新チャンネル・契約・購入・投稿操作は行っていない。','Quiet Originsは本人承認により開設・ブランド設定済み。この動画の投稿・公開はしていない。')
  p.write_text(s);(ROOT/'deliverables'/p.name).write_text(s)
 # Keep the combined and legacy entry points consistent with the current bilingual metadata.
 en=(ROOT/'deliverables/EP001_投稿用情報_en.md').read_text();ja=(ROOT/'deliverables/EP001_投稿用情報_ja.md').read_text()
 (REPO/'new-channel/wom01_アップロード情報.md').write_text(en+'\n\n---\n\n'+ja)
 (REPO/'new-channel/episodes/EP001_Anubis/deliverables/EP001_投稿用情報.md').write_text(ja)
 save(ROOT/'records/assembly_plan.json',{'source_episode':str(OLD),'opening':str(OP),'endcard':str(END),'cut_seconds':CUT,'source_end_seconds':SOURCE_END,'endcard_start_seconds':END_START,'dissolve_seconds':.7,'duration_seconds':DURATION,'expected_frames':FRAMES,'subtitle_ambiguity_resolution':'Handoff says no captions after 678s, but JA thanks ends at 677.691+4=681.691s. Preserve thanks; no captions after endcard begins at 682s.','owner_approved_v08_and_opening_v02':True,'paid_services':False,'youtube_posted':False,'ssd_sync':False,'source_hashes':{str(p):sha(p) for p in [OP,END,*[OLD/f'deliverables/EP001_Anubis_{lang}_v08_1080p30.mp4' for lang in ['en','ja']]]}})
 validate_metadata()
 print('PREPARED 702s / 21060 frames',flush=True)

def video():
 src=OLD/'deliverables/EP001_Anubis_en_v08_1080p30.mp4'
 filt=f'[0:v]split=2[s0][s1];[s0]trim=start_frame=0:end_frame=872,setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS[v1];[s1]trim=start_frame=872:end_frame=20361,setpts=PTS-STARTPTS[v2];[v0][v1][v2]concat=n=3:v=1:a=0,format=yuv420p,settb=AVTB[body];[2:v]setpts=PTS-STARTPTS,format=yuv420p,settb=AVTB[end];[body][end]xfade=transition=fade:duration=0.7:offset=682[v]'
 ff(['-i',src,'-i',OP,'-i',END,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-an','-c:v','libx264','-preset','veryfast','-crf',18,'-threads',4,'-pix_fmt','yuv420p','-r',30,'-t',DURATION,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart','-progress',ROOT/'_work/video_progress.txt',ROOT/'_work/common_picture.mp4'])
 print('COMMON VIDEO DONE',flush=True)

def audio():
 records={}
 for lang in ['en','ja']:
  src=OLD/f'deliverables/EP001_audio_{lang}.m4a'
  filt=f'[0:a]asplit=2[s0][s1];[s0]atrim=0:{CUT},asetpts=PTS-STARTPTS,aresample=48000,afade=t=out:st={CUT-.12}:d=0.12[a0];[1:a]aresample=48000,asetpts=PTS-STARTPTS[a1];[s1]atrim=start={CUT}:end={SOURCE_END},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.015[a2];[a0][a1][a2]concat=n=3:v=0:a=1[body];[2:a]aresample=48000,asetpts=PTS-STARTPTS[end];[body][end]acrossfade=d=0.7:c1=tri:c2=tri[a]'
  wav=ROOT/f'deliverables/EP001_audio_{lang}.wav';aac=ROOT/f'deliverables/EP001_audio_{lang}.m4a'
  ff(['-i',src,'-i',BRAND/'deliverables/Quiet_Origins_opening_trial_v02.wav','-i',BRAND/'deliverables/Quiet_Origins_endcard_trial_v01.wav','-filter_complex',filt,'-map','[a]','-t',DURATION,'-ar',SR,'-c:a','pcm_s24le',wav])
  assert sf.info(wav).frames==int(DURATION*SR)
  ff(['-i',wav,'-c:a','aac','-b:a','192k','-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn'),aac])
  q=measure(aac);assert abs(float(q['input_i'])+16)<=.3 and float(q['input_tp'])<-1
  records[lang]=q;print('AUDIO',lang,q['input_i'],q['input_tp'],flush=True)
 save(ROOT/'records/audio_qc.json',records)

def package():
 for lang in ['en','ja']:
  out=ROOT/f'deliverables/EP001_Anubis_{lang}_v09_1080p30.mp4'
  ff(['-i',ROOT/'_work/common_picture.mp4','-i',ROOT/f'deliverables/EP001_audio_{lang}.m4a','-map','0:v','-map','1:a','-c','copy','-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn'),'-metadata','title=Quiet Origins / EP001 — Anubis v09','-metadata','comment=English: Kokoro Heart; Japanese: VOICEVOX:冥鳴ひまり. External subtitles.','-movflags','+faststart',out])
 print('PACKAGED',flush=True)

def decoded(p,out):
 ff(['-i',p,'-vn','-ar',SR,'-ac',2,'-c:a','pcm_f32le',out]);return sf.read(out,dtype='float32')[0]

def stream_hash(p,stream):
 return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map',stream,'-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def verify():
 results=[];audio_checks={};hashes=[]
 for lang in ['en','ja']:
  p=ROOT/f'deliverables/EP001_Anubis_{lang}_v09_1080p30.mp4';q=probe(p);v=q['streams'][0]
  assert int(v['nb_frames'])==FRAMES and float(q['format']['duration'])==DURATION and v['avg_frame_rate']=='30/1' and (v['width'],v['height'])==(1920,1080)
  pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert pts==list(range(0,FRAMES*512,512))
  ff(['-i',p,'-f','null','-']);hashes.append(stream_hash(p,'0:v'))
  a=decoded(OLD/f'deliverables/EP001_audio_{lang}.m4a',ROOT/f'_work/source_{lang}.wav');b=decoded(ROOT/f'deliverables/EP001_audio_{lang}.m4a',ROOT/f'_work/final_{lang}.wav');pcm,_=sf.read(ROOT/f'deliverables/EP001_audio_{lang}.wav',dtype='float32')
  checks=[]
  for start,end,delta in [(0,CUT-.13,0),(CUT+.02,678.,4)]:
   x=a[round(start*SR):round(end*SR)];y=b[round((start+delta)*SR):round((end+delta)*SR)];z=pcm[round((start+delta)*SR):round((end+delta)*SR)]
   assert len(x)==len(y)==len(z)
   pcm_error=float(np.max(np.abs(x-z)));assert pcm_error<2e-7
   snr=float(10*np.log10(np.sum(x.astype('float64')**2)/np.sum((x-y).astype('float64')**2)));assert snr>30
   checks.append({'source_range':[start,end],'shift_seconds':delta,'pcm_max_error':pcm_error,'aac_signal_to_error_db':snr})
  audio_checks[lang]={'aligned_source_comparisons':checks,'splice_fades_excluded_seconds':[.12,.015],'end_crossfade_excluded_source_range':[678,678.7]}
  results.append({'language':lang,'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'duration_seconds':DURATION,'frames':FRAMES,'full_decode':True,'exact_30fps_pts':True,'video_stream_sha256':hashes[-1]})
  print('VERIFIED',lang,checks,flush=True)
 assert hashes[0]==hashes[1]
 for p,digest in read(ROOT/'records/assembly_plan.json')['source_hashes'].items():assert sha(Path(p))==digest
 preserve_sources()
 save(ROOT/'records/audio_alignment.json',audio_checks)
 save(ROOT/'records/qc_v09.json',{'passed':True,'files':results,'bilingual_video_streams_identical':True,'source_files_preserved':True,'human_full_listening':False})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','video','audio','package','verify']);a=p.parse_args()
 if a.stage!='verify':assert not (ROOT/'records/sharing.json').exists(),'Shared outputs are immutable'
 globals()[a.stage]()
