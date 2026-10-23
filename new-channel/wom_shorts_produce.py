"""Quiet Origins EP001/EP002 English Shorts; immutable requested copy, native voice.

First run narration. Stop before picture production if any native read exceeds 20s.
"""
import argparse,difflib,json,math,os,re,subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from wom01_multilingual_render import read,save,sha,ff,rms
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance

REPO=Path(__file__).resolve().parent.parent
ROOT=Path(os.environ.get('QO_SHORTS_ROOT','/Users/ryo/Desktop/新チャンネル/ショート/確認版_v01_20261022'))
REQUEST=REPO/'new-channel/wom_ショート制作依頼_EP001_EP002_20261022.md'
MODELS=Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
SR=24000;FPS=30
PHONEMES={'Samhain':'sˈaʊɪn','Vallancey':'vəlˈænsi'}
BG='#0c1820';GOLD='#d8b575';IVORY='#f4efdf'
EN='/System/Library/Fonts/Supplemental/Arial.ttf';BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
EP1=Path('/Users/ryo/Desktop/新チャンネル/EP001_Anubis')
EP2=Path('/Users/ryo/Desktop/新チャンネル/EP002_Halloween')

def font(size,text='',bold=False):return ImageFont.truetype(JA if any(ord(c)>0x2fff for c in text) else BOLD if bold else EN,size)
def levels(path):
 p=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(path),'-af','loudnorm=I=-14:TP=-1.5:LRA=7:print_format=json','-f','null','-'],check=True,capture_output=True,text=True)
 return json.loads(re.findall(r'\{\s*"input_i".*?\}',p.stderr,re.S)[-1])

def scripts():
 text=REQUEST.read_text();items=re.findall(r'^\*\*(A[123]|H[123]) — (.+?)\*\*\n> (.+)$',text,re.M);assert len(items)==6
 return [{'id':id,'episode':'EP001' if id.startswith('A') else 'EP002','title_ja':title,'text':script,'words':len(script.split())} for id,title,script in items]

def narration():
 import onnxruntime as ort
 ort.disable_telemetry_events()
 from kokoro_onnx import Kokoro
 opt=ort.SessionOptions();opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
 tts=Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(MODELS/'voices-v1.0.bin'))
 for d in ['audio','records','deliverables','review','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 rows=[]
 for s in scripts():
  phonemes=tts.tokenizer.phonemize(s['text'],'en-us')
  if any(word in s['text'] for word in PHONEMES):
   parts=re.split('('+'|'.join(PHONEMES)+')',s['text']);phonemes=' '.join(PHONEMES.get(part,tts.tokenizer.phonemize(part,'en-us')) for part in parts if part.strip())
  assert tts.tokenizer.known(phonemes)==phonemes
  cfg={'text':s['text'],'phonemes':phonemes,'voice':'af_heart','speed':.82,'sentence_pause':.3,'clause_pause':.12,'trim':True,'request_sha256':sha(REQUEST),'model_sha256':sha(MODELS/'kokoro-v1.0.onnx')}
  path=ROOT/f'audio/{s["id"]}_native.wav';stamp=path.with_suffix('.json');timed=ROOT/f'records/{s["id"]}_phoneme_timings.json'
  if path.exists() and stamp.exists() and read(stamp)==cfg:a,sr=sf.read(path,dtype='float32')
  else:
   a,sr,times=tts.create_timed(phonemes,voice='af_heart',speed=.82,lang='en-us',is_phonemes=True,trim=True,sentence_pause=.3,clause_pause=.12);assert sr==SR
   sf.write(path,a,SR,subtype='PCM_16');save(stamp,cfg)
   save(timed,{'available':bool(times),'timings':[vars(t) if hasattr(t,'__dict__') else {'repr':repr(t)} for t in times]})
  # Detect voice onset with 10ms windows at -50dBFS; this is before any BGM.
  block=240;levels=np.array([np.sqrt(np.mean(a[i:i+block]**2)) for i in range(0,len(a),block)]);active=np.where(levels>10**(-50/20))[0];assert len(active)
  onset=int(active[0])*block/SR;end=min(len(a),(int(active[-1])+1)*block)/SR
  row={**s,'audio_file':str(path),'audio_sha256':sha(path),'native_audio_duration':len(a)/SR,'voice_onset_seconds':onset,'last_voice_activity_seconds':end,'native_voice':'Kokoro / af_heart','speed':.82,'timing_available':read(timed)['available'],'within_20_seconds':len(a)/SR<=20}
  rows.append(row);print('NATIVE',s['id'],f'{len(a)/SR:.6f}s',f'onset {onset:.3f}s',s['words'],'words',flush=True)
 save(ROOT/'records/narration.json',{'request_sha256':sha(REQUEST),'scripts':rows,'all_within_20_seconds':all(s['within_20_seconds'] for s in rows),'text_unchanged':True,'speech_speed_modified_to_fit':False,'human_full_listening':False})
 if not all(s['within_20_seconds'] for s in rows):raise SystemExit('STOP: Native narration exceeds 20 seconds; report to user, do not rewrite or accelerate.')
 print('NARRATION DURATION GATE PASSED',flush=True)

def captions():
 from kokoro_onnx.tokenizer import Tokenizer
 # Use the same tokenizer through the existing model session, without synthesizing again.
 import onnxruntime as ort
 ort.disable_telemetry_events()
 from kokoro_onnx import Kokoro
 opt=ort.SessionOptions();opt.intra_op_num_threads=2
 tts=Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(MODELS/'voices-v1.0.bin'))
 nar=read(ROOT/'records/narration.json');assert nar['all_within_20_seconds'];allrows=[]
 for s in nar['scripts']:
  times=read(ROOT/f'records/{s["id"]}_phoneme_timings.json')['timings'];words=s['text'].split();ignored=set(' \t\nˈˌː.,;:!?—-()');expected=[];owners=[]
  for i,w in enumerate(words):
   key=re.sub(r'[^A-Za-z]','',w);ph=PHONEMES.get(key,tts.tokenizer.phonemize(w,'en-us'))
   clean=[c for c in ph if c not in ignored];expected.extend(clean);owners.extend([i]*len(clean))
  native=[t for t in times if t['phoneme'] not in ignored];matcher=difflib.SequenceMatcher(None,expected,[t['phoneme'] for t in native],autojunk=False);assert matcher.ratio()>.8
  aligned={i:[] for i in range(len(words))}
  for block in matcher.get_matching_blocks():
   for j in range(block.size):aligned[owners[block.a+j]].append(block.b+j)
  # Context changes articles (standalone "a" vs unstressed schwa). Attribute those
  # edit spans to their neighboring native phoneme interval, preserving order.
  context_mapped=[]
  for tag,i1,i2,j1,j2 in matcher.get_opcodes():
   if tag=='equal':continue
   for index in range(i1,i2):
    target=j1+round((index-i1)/max(1,i2-i1-1)*max(0,j2-j1-1));target=min(len(native)-1,target)
    aligned[owners[index]].append(target);context_mapped.append(owners[index])
  assert all(aligned.values())
  wordtimes=[{'word':w,'start':native[min(aligned[i])]['start'],'end':native[max(aligned[i])]['end']} for i,w in enumerate(words)]
  assert all(a['start']<=b['start'] for a,b in zip(wordtimes,wordtimes[1:]))
  # Sentence-aware groups of at most five words. Long printed words wrap to two lines.
  groups=[];pos=0
  for sentence in re.split(r'(?<=[.!?])\s+',s['text']):
   ws=sentence.split();count=math.ceil(len(ws)/5);bounds=[round(i*len(ws)/count) for i in range(count+1)]
   for a,b in zip(bounds,bounds[1:]):groups.append({'text':' '.join(ws[a:b]),'word_start':pos+a,'word_end':pos+b})
   pos+=len(ws)
  nframes=math.ceil((s['native_audio_duration']+2)*FPS);cta_frame=nframes-60;assert 450<=nframes<=600
  for i,g in enumerate(groups):
   g['start_frame']=max(0,round(wordtimes[g['word_start']]['start']*FPS)) if i else 0
   g['end_frame']=max(g['start_frame']+1,round(wordtimes[groups[i+1]['word_start']]['start']*FPS)) if i+1<len(groups) else cta_frame
   assert g['end_frame']<=cta_frame
  assert ' '.join(g['text'] for g in groups)==s['text']
  row={**s,'words_timed':wordtimes,'alignment_ratio':matcher.ratio(),'context_adjusted_word_indices':sorted(set(context_mapped)),'alignment_method':'Native Kokoro phoneme durations mapped to script words by sequence alignment, with contextual phoneme substitutions assigned within adjacent aligned spans. These are model-derived word estimates, not human auditory verification.','caption_groups':groups,'frames':nframes,'duration_seconds':nframes/FPS,'cta_start':cta_frame/FPS,'cta_start_frame':cta_frame,'cta_text':'Full story on Quiet Origins'}
  allrows.append(row);print('CAPTIONS',s['id'],len(groups),'pages',nframes/FPS,'seconds',matcher.ratio(),flush=True)
 save(ROOT/'records/shorts.json',{'shorts':allrows,'request_sha256':sha(REQUEST)})

def audio():
 rows=read(ROOT/'records/shorts.json')['shorts'];reports=[]
 bgms={'EP001':EP1/'Quiet_Origins_v08_20261021/audio/common_bgm.wav','EP002':EP2/'確認版_v01_20261022/audio/common_bgm_and_brand.wav'}
 assert sha(bgms['EP001'])==read(REPO/'new-channel/wom01_Quiet_Origins_v05_20261021/records/audio_qc.json')['bgm']['sha256']
 for i,s in enumerate(rows):
  id=s['id'];n=s['frames']*SR//FPS;native,sr=sf.read(s['audio_file'],dtype='float32');assert sr==SR
  q=levels(Path(s['audio_file']));normal=ROOT/f'audio/{id}_normalized.wav'
  filt=f"loudnorm=I=-14:TP=-1.5:LRA=7:linear=true:measured_I={q['input_i']}:measured_TP={q['input_tp']}:measured_LRA={q['input_lra']}:measured_thresh={q['input_thresh']}:offset={q['target_offset']}"
  ff(['-i',s['audio_file'],'-af',filt,'-ar',SR,'-c:a','pcm_f32le',normal]);voice,sr=sf.read(normal,dtype='float32');voice=np.pad(voice[:n],(0,max(0,n-len(voice))))
  source=bgms[s['episode']];start=50+24*i if s['episode']=='EP001' else 60+24*(i-3)
  music,sr=sf.read(source,start=round(start*SR),frames=n,dtype='float32');assert sr==SR and len(music)==n
  # The selected EP002 times are outside its brand intervals. No narration is in these stems.
  active=np.zeros(n,bool);active[round(s['voice_onset_seconds']*SR):round(s['last_voice_activity_seconds']*SR)]=True
  music*=10**((-33.5-rms(music[active]))/20)
  music[-round(.12*SR):]*=np.linspace(1,0,round(.12*SR))[:,None]
  stem=ROOT/f'audio/{id}_bgm.wav';sf.write(stem,music,SR,subtype='FLOAT');mix=ROOT/f'audio/{id}_mix.wav';gain=0
  for attempt in range(5):
   sf.write(mix,voice[:,None]*10**(gain/20)+music,SR,subtype='FLOAT');q=levels(mix);delta=-14-float(q['input_i'])
   if abs(delta)<.04:break
   gain+=delta
  assert abs(float(q['input_i'])+14)<=.1 and float(q['input_tp'])<=-1.1,q
  out=ROOT/f'audio/{id}_final.m4a';ff(['-i',mix,'-ar',48000,'-c:a','aac','-b:a','192k',out]);final=levels(out);assert abs(float(final['input_i'])+14)<=.15 and float(final['input_tp'])<=-1
  reports.append({'id':id,'mix':final,'voice_onset_native':s['voice_onset_seconds'],'bgm_source':str(source),'bgm_source_sha256':sha(source),'bgm_excerpt_start_seconds':start,'bgm_during_narration_dbfs':rms(music[active]),'voice_gain_after_normalization_db':gain,'final_file':str(out),'sha256':sha(out),'voice_rate_or_pitch_processing':False});print('AUDIO',id,final['input_i'],final['input_tp'],flush=True)
 save(ROOT/'records/audio_qc.json',{'passed':True,'target_lufs':-14,'maximum_true_peak_db':-1,'reports':reports})

def registry():
 assets={}
 museum=read(REPO/'new-channel/episodes/EP001_Anubis/records/museum_assets.json')
 for a in museum:
  if a['object_id'] not in [557830,552247,548344,544075]:continue
  path=EP1/'旧制作素材'/a['file'];assert sha(path)==a['sha256'];id=a['asset_id'];assets[id]={**a,'id':id,'path':str(path),'kind':'image','label':'FACSIMILE｜模写' if a['object_id']==557830 else 'MUSEUM OBJECT｜博物館資料','source':f"The Met • {'N. de Garis Davies • ' if a['object_id']==557830 else ''}{a['object_number']} • CC0"}
 old=EP2/'確認版_v04_20261022/records';source=read(old/'source_assets.json')['assets']
 for a in source:
  if a['id'] not in ['A06','A03']:continue
  assets[a['id']]={'id':a['id'],'path':a['original_local_path'],'sha256':a['original_sha256'],'kind':'image','label':'PUBLIC DOMAIN BOOK｜パブリックドメインの書籍' if a['id']=='A06' else 'MUSEUM OBJECT｜博物館資料','source':'Wellcome Collection • Collectanea II, 1786 • PD' if a['id']=='A06' else 'The Met • 1975.1.2484 • CC0','original_record':a}
 for name,kind,filename in [('R02','image','ai_images.json'),('N08','image','ai_images.json'),('N06','video','new_videos_v03.json'),('N12','video','new_videos_v03.json')]:
  a=next(a for a in read(old/filename) if a['id']==name);assets[name]={'id':name,'path':a['local_path'],'sha256':a['sha256'],'kind':kind,'label':'AI RECONSTRUCTION｜AIによる再現','source':f"{'Kling AI 3.0' if kind=='video' else 'OpenAI image generation'} • {name} • Illustration",'original_record':a}
 for a in assets.values():assert sha(Path(a['path']))==a['sha256']
 return assets

def word_frame(s,word):
 return round(next(w['start'] for w in s['words_timed'] if re.sub(r'[^A-Za-z]','',w['word']).lower()==word.lower())*FPS)

def visuals():
 assets=registry();rows=read(ROOT/'records/shorts.json')['shorts'];manifest=[];(ROOT/'assets').mkdir(exist_ok=True)
 for s in rows:
  id=s['id'];end=s['frames']
  specs={'A1':[('MET-557830',None),('MET-552247','Thoth')],'A2':[('MET-548344',None)],'A3':[('MET-544075',None)],'H1':[('A06',None),('N06','early')],'H2':[('R02',None),('N12','When')],'H3':[('A03',None),('N08','night')]}[id]
  starts=[0 if word is None else word_frame(s,word) for aid,word in specs];bounds=starts+[end];plans=[(aid,bounds[j],bounds[j+1]) for j,(aid,word) in enumerate(specs)]
  for j,(aid,start,stop) in enumerate(plans):
   a=assets[aid];path=Path(a['path']);poster=ROOT/f'assets/{aid}_poster.png'
   if a['kind']=='video':ff(['-ss',5,'-i',path,'-frames:v',1,poster]);art=Image.open(poster).convert('RGB')
   else:art=ImageOps.exif_transpose(Image.open(path)).convert('RGB')
   bg=ImageEnhance.Brightness(ImageOps.fit(art,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.30)
   # Frame and labels are fixed; only the artwork viewport moves.
   ImageDraw.Draw(bg).rectangle((0,120,1079,280),fill=BG)
   texts=[]
   for y,value,size,color in [(140,f'QUIET ORIGINS / {s["episode"]}',25,GOLD),(183,a['label'],25,GOLD),(229,a['source'],23,IVORY)]:
    d=ImageDraw.Draw(bg);f=font(size,value);box=d.textbbox((80,y),value,font=f);assert box[2]<=1000 and 140<=box[1]<box[3]<=260;d.text((80,y),value,font=f,fill=color);texts.append({'text':value,'bbox':list(box)})
   crop=None
   if aid=='MET-557830':crop=(276,833,3145,3033)
   elif aid=='MET-552247':crop=(80,240,1920,1120)
   piece=art.crop(crop) if crop else art;fit=ImageOps.contain(piece,(920,800),Image.Resampling.LANCZOS);x=80+(920-fit.width)//2;y=300+(800-fit.height)//2;bg.paste(fit,(x,y));out=ROOT/f'assets/{id}_{j+1:02}_{aid}.png';bg.save(out)
   entry={'short_id':id,'asset_id':aid,'start_frame':start,'end_frame':stop,'frames':stop-start,'file':str(out),'sha256':sha(out),'source':a,'texts':texts,'art_box':[x,y,x+fit.width,y+fit.height],'native_source_pixels':art.size,'source_crop_pixels':crop,'zoom':3.125 if id=='A2' else 1.03,'viewport':[80,300,920,800]}
   # Maat is the small feather-wearing figure in the right pan. The figure on
   # the balance beam is the baboon form of Thoth, not Maat (Met object 548344).
   if id=='A2':entry['target_center_in_viewport']=[.65*fit.width+(x-80),.7175*fit.height+(y-300)]
   manifest.append(entry)
 save(ROOT/'records/visual_manifest.json',{'shots':manifest,'assets':assets,'A1_note':'Thoth and Osiris are on the same Roman cartonnage MET-552247: shown together in one continuous shot, not repeated as separate shots.','one_use_per_source_within_episode':True});print('VISUALS',len(manifest),flush=True)

def camera(s):
 n=s['frames'];z=s['zoom'];phase=f'on/{max(1,n-1)}'
 # Linear logarithmic zoom keeps the relative speed uniform, including the larger A2 move.
 zoom=f'exp(log({z})*({phase}))';cx,cy=s.get('target_center_in_viewport',[460,400]);centerx=f'(460+({cx}-460)*({phase}))';centery=f'(400+({cy}-400)*({phase}))'
 x=f'({centerx}-W/(2*{zoom}))';y=f'({centery}-H/(2*{zoom}))'
 p=f"perspective=x0='{x}':y0='{y}':x1='{x}+W/{zoom}':y1='{y}':x2='{x}':y2='{y}+H/{zoom}':x3='{x}+W/{zoom}':y3='{y}+H/{zoom}':sense=source:eval=frame:interpolation=cubic"
 return f'[0:v]split=2[base][art];[art]crop=920:800:80:300,format=yuv444p,{p}[moving];[base][moving]overlay=80:300:format=yuv444,format=yuv420p[v]'

def render():
 import imageio_ffmpeg
 shots=read(ROOT/'records/visual_manifest.json')['shots'];rows=read(ROOT/'records/shorts.json')['shorts'];rendered=[];captionrecords=[]
 for s in shots:
  path=ROOT/f'_work/{s["short_id"]}_{s["asset_id"]}.mp4';stamp=path.with_suffix('.json');cfg={'image':s['sha256'],'frames':s['frames'],'camera':camera(s),'source_sha':s['source']['sha256']}
  if not(path.exists() and stamp.exists() and read(stamp)==cfg):
   if s['source']['kind']=='video':
    x,y,x1,y1=s['art_box'];factor=max(1,s['frames']/300)
    fc=f'[1:v]trim=end_frame=240,setpts=(PTS-STARTPTS)*{factor:.12f},scale={x1-x}:{y1-y}:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.15[art];[0:v][art]overlay={x}:{y}:shortest=1,format=yuv420p[v]'
    args=['-loop',1,'-framerate',30,'-i',s['file'],'-i',s['source']['path'],'-filter_complex_threads',2,'-filter_complex',fc,'-map','[v]']
   else:args=['-loop',1,'-framerate',30,'-i',s['file'],'-filter_complex_threads',2,'-filter_complex',camera(s),'-map','[v]']
   ff([*args,'-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-pix_fmt','yuv420p','-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',path]);save(stamp,cfg)
  rendered.append({**s,'encoded_file':str(path),'encoded_sha256':sha(path)});print('SHOT',s['short_id'],s['asset_id'],flush=True)
 save(ROOT/'records/render_shots.json',rendered)
 for s in rows:
  id=s['id'];group=[r for r in rendered if r['short_id']==id];listing=ROOT/f'_work/{id}_concat.txt';listing.write_text(''.join(f"file '{r['encoded_file']}'\nduration {r['frames']/FPS:.9f}\n" for r in group));picture=ROOT/f'_work/{id}_picture.mp4'
  ff(['-f','concat','-safe',0,'-i',listing,'-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512',picture])
  pages=s['caption_groups']+[{'text':s['cta_text'],'start_frame':s['cta_start_frame'],'end_frame':s['frames'],'brand':True}];ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding','Style: Main,Arial,68,&H00DFF0F4,&H00DFF0F4,&H0010180C,&HAA10180C,-1,0,0,0,100,100,0,0,1,4,1,5,80,200,0,1','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
  def tm(frame):
   ticks=round(frame/FPS*100);return f'{ticks//360000}:{ticks//6000%60:02}:{ticks//100%60:02}.{ticks%100:02}'
  for i,p in enumerate(pages):
   words=p['text'].split();d=ImageDraw.Draw(Image.new('RGB',(1,1)));lines=[]
   for size in ([44] if p.get('brand') else range(68,53,-2)):
    f=font(size,bold=True)
    if len(words)<=5 and d.textlength(p['text'],font=f)<=770:lines=[p['text']];break
    candidates=[[' '.join(words[:cut]),' '.join(words[cut:])] for cut in range(1,len(words)) if cut<=5 and len(words)-cut<=5]
    best=min(candidates,key=lambda lines:max(d.textlength(line,font=f) for line in lines))
    if max(d.textlength(line,font=f) for line in best)<=770:lines=best;break
   assert len(lines)<=2 and max(len(x.split()) for x in lines)<=5
   content='\\N'.join(lines);override=f'{{\\an5\\pos(480,1300)\\fs{size}}}';ass.append(f'Dialogue: 0,{tm(p["start_frame"])},{tm(p["end_frame"])},Main,,0,0,0,,{override}{content}')
   captionrecords.append({'short_id':id,'page':i+1,**p,'lines':lines,'font_size':size,'position':[480,1300]})
  ap=ROOT/f'_work/{id}.ass';ap.write_text('\n'.join(ass)+'\n');out=ROOT/f'deliverables/QO_short_{s["episode"]}_{id}_v01.mp4'
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(picture),'-i',str(ROOT/f'audio/{id}_final.m4a'),'-vf',f"ass='{ap}'",'-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-frames:v',str(s['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True);print('RENDERED',id,flush=True)
 save(ROOT/'records/render_shots.json',rendered);save(ROOT/'records/caption_manifest.json',captionrecords)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['narration','captions','audio','visuals','render']);a=p.parse_args();globals()[a.stage]()
