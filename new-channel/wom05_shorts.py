"""EP005 Shorts: exact requested copy and main-episode narration settings.

The user waived the 20-second cap on 2026-10-24; preserve balanced pacing and the exact copy.
"""
import argparse
import re
from pathlib import Path
import wom_shorts_produce as base
from wom05_produce import PHONEMES as MAIN_PHONEMES
PHONEMES = {"Hokusai's": MAIN_PHONEMES["Hokusai"] + "z", **MAIN_PHONEMES}

ROOT = Path('/Users/ryo/Desktop/新チャンネル/ショート/EP005_確認版_v01_20261024')
REQUEST = Path(__file__).resolve().parent / 'wom_ショート制作依頼_EP005_20261024.md'
MAIN = Path('/Users/ryo/Desktop/新チャンネル/EP005_Tengu/確認版_v02_20261024')


def scripts():
    items = re.findall(r'^### (T[123]) — (.+?)\n\n> (.+)$', REQUEST.read_text(), re.M)
    assert len(items) == 3
    return [dict(id=id, episode='EP005', title_ja=title, text=text,
                 words=len(text.split())) for id, title, text in items]


def narration():
    main_readings = base.read(MAIN / 'records/reading_replacements.json')
    assert all(PHONEMES[r['display']] == r['phonemes'] for r in main_readings
               if r['language'] == 'en' and 'phonemes' in r)
    base.ROOT, base.REQUEST, base.PHONEMES, base.scripts = ROOT, REQUEST, PHONEMES, scripts
    (ROOT / 'records').mkdir(parents=True, exist_ok=True)
    base.save(ROOT / 'records/reading_correction.json', {
        'main_reading_replacements': str(MAIN / 'records/reading_replacements.json'),
        'main_reading_replacements_sha256': base.sha(MAIN / 'records/reading_replacements.json'),
        'phoneme_overrides_same_as_main': MAIN_PHONEMES,
        'possessive_inflection': {"Hokusai's": PHONEMES["Hokusai's"]},
        'possessive_note': 'Same Hokusai root + /z/; prevents standalone letter S from being spoken, as in the approved EP004 Shorts.',
        'tengu_and_Bin': 'Native tokenizer pronunciation, as in the main episode; no added override.',
        'text_unchanged': True, 'voice': 'af_heart', 'speed': .82,
        'sentence_pause': .3, 'clause_pause': .12,
    })
    base.narration()



import difflib, math, json, subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance
SR=base.SR;FPS=base.FPS;MODELS=base.MODELS;read=base.read;save=base.save;sha=base.sha;ff=base.ff;levels=base.levels;rms=base.rms;font=base.font

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
   key=re.sub(r"^[^A-Za-z]+|[^A-Za-z']+$",'',w);ph=PHONEMES.get(key,tts.tokenizer.phonemize(w,'en-us'))
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
  texts={
   'T1':["In the Nihon Shoki,", "a chronicle of 720,", "a great star crosses", "the sky in 637", "with a loud sound.", "A monk named Bin", "says it is not", "a falling star.", "It is a tengu,", "a celestial dog.", "Its barking sounds like thunder."],
   'T2':["In a tale from", "the twelfth century,", "a Buddha appears in", "a persimmon tree,", "shining and scattering flowers.", "One minister just keeps staring.", "At last the Buddha vanishes,", "and a great kite", "with a broken wing", "falls from the tree."],
   'T3':["Long-nosed tengu came later,", "but the bird never", "went away.", "In Hokusai's sketchbook,", "first published in 1815,", "the figure labeled tengu", "is still a great bird.", "For centuries, the two forms", "lived side by side."]
  }[s['id']]
  groups=[];pos=0
  for text in texts:
   end=pos+len(text.split());groups.append({'text':text,'word_start':pos,'word_end':end});pos=end
  for protected in ['of 720,','in 637','in 1815,']:
   if protected in s['text']:assert any(protected in g['text'] for g in groups),protected
  nframes=634 if s['id']=='T2' else 600;cta_frame=nframes-60
  for i,g in enumerate(groups):
   g['start_frame']=max(0,round(wordtimes[g['word_start']]['start']*FPS)) if i else 0
   g['end_frame']=max(g['start_frame']+1,round(wordtimes[groups[i+1]['word_start']]['start']*FPS)) if i+1<len(groups) else math.ceil(s['native_audio_duration']*FPS)
   assert g['end_frame']<=nframes
  assert ' '.join(g['text'] for g in groups)==s['text']
  row={**s,'words_timed':wordtimes,'alignment_ratio':matcher.ratio(),'context_adjusted_word_indices':sorted(set(context_mapped)),'alignment_method':'Native Kokoro phoneme durations mapped to script words by sequence alignment, with contextual phoneme substitutions assigned within adjacent aligned spans. These are model-derived word estimates, not human auditory verification.','caption_groups':groups,'frames':nframes,'duration_seconds':nframes/FPS,'cta_start':cta_frame/FPS,'cta_start_frame':cta_frame,'cta_text':'Full story on Quiet Origins'}
  allrows.append(row);print('CAPTIONS',s['id'],len(groups),'pages',nframes/FPS,'seconds',matcher.ratio(),flush=True)
 save(ROOT/'records/shorts.json',{'shorts':allrows,'request_sha256':sha(REQUEST)})



def audio():
    reports=[r for r in read(ROOT/'records/audio_qc.json')['reports'] if r['id']!='T2']
    source=MAIN.parent/'確認版_v01_20261024/audio/common_bgm_and_brand.wav'
    for i,s in enumerate(read(ROOT/'records/shorts.json')['shorts']):
        if s['id']!='T2': continue
        id=s['id']; n=s['frames']*SR//FPS
        q=levels(Path(s['audio_file'])); normal=ROOT/f'audio/{id}_normalized.wav'
        filt=f"loudnorm=I=-14:TP=-1.5:LRA=7:linear=true:measured_I={q['input_i']}:measured_TP={q['input_tp']}:measured_LRA={q['input_lra']}:measured_thresh={q['input_thresh']}:offset={q['target_offset']}"
        ff(['-i',s['audio_file'],'-af',filt,'-ar',SR,'-c:a','pcm_f32le',normal])
        voice,sr=sf.read(normal,dtype='float32'); assert sr==SR and len(voice)<=n
        voice=np.pad(voice,(0,n-len(voice)))
        # 120–180s are quiet underscore only, outside opening/end-card intervals.
        start=120+20*i
        music,sr=sf.read(source,start=round(start*SR),frames=n,dtype='float32')
        assert sr==SR and len(music)==n
        active=np.zeros(n,bool)
        active[round(s['voice_onset_seconds']*SR):round(s['last_voice_activity_seconds']*SR)]=True
        music*=10**((-33.5-rms(music[active]))/20)
        music[-round(.12*SR):]*=np.linspace(1,0,round(.12*SR))[:,None]
        sf.write(ROOT/f'audio/{id}_bgm.wav',music,SR,subtype='FLOAT')
        mix=ROOT/f'audio/{id}_mix.wav'; gain=0
        for attempt in range(5):
            sf.write(mix,voice[:,None]*10**(gain/20)+music,SR,subtype='FLOAT')
            q=levels(mix); delta=-14-float(q['input_i'])
            if abs(delta)<.04: break
            gain+=delta
        assert abs(float(q['input_i'])+14)<=.1 and float(q['input_tp'])<=-1.1,q
        out=ROOT/f'audio/{id}_final.m4a'
        ff(['-i',mix,'-ar',48000,'-c:a','aac','-b:a','192k',out]); final=levels(out)
        limiter_db=None
        # Measure the encoded AAC too: codec reconstruction can add intersample peaks.
        if float(final['input_tp'])>-1:
            for ceiling in [-3,-4,-5]:
                filt=f'aresample=192000,alimiter=limit={10**(ceiling/20)}:level=false:latency=true,aresample=48000'
                ff(['-i',mix,'-af',filt,'-ar',48000,'-c:a','aac','-b:a','192k',out]); final=levels(out)
                limiter_db=ceiling
                if abs(float(final['input_i'])+14)<=.15 and float(final['input_tp'])<=-1: break
        assert abs(float(final['input_i'])+14)<=.15 and float(final['input_tp'])<=-1
        reports.append(dict(id=id,mix=final,voice_onset_native=s['voice_onset_seconds'],
            bgm_source=str(source),bgm_source_sha256=sha(source),bgm_excerpt_start_seconds=start,
            bgm_during_narration_dbfs=rms(music[active]),voice_gain_after_normalization_db=gain,
            final_file=str(out),sha256=sha(out),voice_rate_or_pitch_processing=False,
            aac_peak_limiter_ceiling_dbfs=limiter_db))
        print('AUDIO',id,final['input_i'],final['input_tp'],flush=True)
    save(ROOT/'records/audio_qc.json',dict(passed=True,target_lufs=-14,maximum_true_peak_db=-1,reports=reports))




def phrase_frame(s, phrase):
    words=[re.sub(r"[^a-z']",'',w['word'].lower()) for w in s['words_timed']]
    needle=phrase.lower().split()
    j=next(j for j in range(len(words)) if words[j:j+len(needle)]==needle)
    return round(s['words_timed'][j]['start']*FPS)


def visuals():
    sources={a['key']:a for a in read(MAIN/'records/source_assets.json')['assets']}
    mainshots={a['key']:a for a in read(MAIN/'records/visual_manifest.json')['shots']}
    assets={};shots=[]
    (ROOT/'assets').mkdir(exist_ok=True)
    for row in read(ROOT/'records/shorts.json')['shorts']:
        id=row['id']
        specs={'T1':[('V01',None),('ndl_1182143_010','it is a tengu')],
               'T2':[('met_57203',None),('V02','a buddha appears')],
               'T3':[('met_24145',None),('ndl_851648_028',"in hokusai's sketchbook"),('lacma_89199','for centuries')]}[id]
        starts=[0 if phrase is None else phrase_frame(row,phrase) for aid,phrase in specs]
        for i,(aid,phrase) in enumerate(specs):
            m=mainshots[aid];crop=None
            if aid.startswith('V'):
                path=MAIN/'assets/V01_night_grade_v03.mp4' if aid=='V01' else MAIN/'_work/render/V02_v02.mp4'
                poster=ROOT/f'_work/{aid}_poster.jpg'
                fil='scale=1080:608' if aid=='V01' else 'crop=1458:820:231:110,scale=1080:608'
                ff(['-i',path,'-frames:v',1,'-vf',fil,poster])
                piece=Image.open(poster).convert('RGB')
                a=dict(id=aid,path=str(path),sha256=sha(path),kind='video',label=m['label'],source=m['source'])
            else:
                original=sources[aid];path=Path(original['path']);assert sha(path)==original['sha256']
                im=ImageOps.exif_transpose(Image.open(path)).convert('RGB')
                norm=m.get('crop_normalized')
                if aid.startswith('ndl'): norm=m['detail_crop_normalized']
                if norm:crop=[round(v*k) for v,k in zip(norm,[im.width,im.height,im.width,im.height])];piece=im.crop(crop)
                else:piece=im
                a=dict(id=aid,path=str(path),sha256=sha(path),kind='image',label=m['label'],source=m['source'],original_record=original)
            assets[aid]=a
            bg=ImageEnhance.Brightness(ImageOps.fit(piece,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.30)
            d=ImageDraw.Draw(bg);d.rectangle((0,120,1079,269),fill=base.BG)
            texts=[]
            lines=[(140,'QUIET ORIGINS / EP005',25,base.GOLD),(181,a['label'],25,base.GOLD)]
            # Keep the complete approved source wording, wrapping it rather than shrinking to unreadable type.
            source_lines=[];current=''
            for word in a['source'].split():
                test=(current+' '+word).strip()
                if d.textlength(test,font=font(20,test))>920 and current:source_lines.append(current);current=word
                else:current=test
            if current:source_lines.append(current)
            assert len(source_lines)<=2
            lines += [(213+24*j,line,20,base.IVORY) for j,line in enumerate(source_lines)]
            for y,value,size,color in lines:
                while d.textlength(value,font=font(size,value))>920:size-=1
                f=font(size,value);box=d.textbbox((80,y),value,font=f)
                assert box[2]<=1000 and 140<=box[1]<box[3]<=260,(value,box)
                d.text((80,y),value,font=f,fill=color);texts.append(dict(text=value,bbox=list(box)))
            fit=ImageOps.contain(piece,(1080,860),Image.Resampling.LANCZOS)
            x=(1080-fit.width)//2;y=270+(860-fit.height)//2;bg.paste(fit,(x,y))
            out=ROOT/f'assets/{id}_{aid}.png';bg.save(out)
            stop=starts[i+1] if i+1<len(starts) else row['frames']
            assert (stop-starts[i])/FPS>=1.5
            shots.append(dict(short_id=id,asset_id=aid,start_frame=starts[i],end_frame=stop,frames=stop-starts[i],
                file=str(out),sha256=sha(out),source=a,texts=texts,art_box=[x,y,x+fit.width,y+fit.height],
                source_crop_pixels=crop,source_crop_normalized=norm if not aid.startswith('V') else None,
                zoom_start=.97,zoom_end=1.,viewport=[0,270,1080,860],cut_phrase=phrase,
                cut_word_seconds=None if phrase is None else row['words_timed'][next(j for j in range(len(row['words_timed'])) if round(row['words_timed'][j]['start']*FPS)==starts[i])]['start']))
    assert len({s['source']['sha256'] for s in shots})==len(shots)==7
    save(ROOT/'records/visual_manifest.json',dict(shots=shots,assets=assets,same_source_not_repeated=True))
    t2=next(s for s in read(ROOT/'records/shorts.json')['shorts'] if s['id']=='T2')
    save(ROOT/'records/T2_timing_question.json',dict(cut_at_a_Buddha_seconds=phrase_frame(t2,'a buddha appears')/30,
        vanish_phrase_seconds=phrase_frame(t2,'at last')/30,main_source_vanish_begin_seconds=4.2,
        main_source_seconds=14.6,duration_with_only_light_retimed=phrase_frame(t2,'at last')/30+14.6-4.2,
        status='resolved_duration_cap_waived_by_user',user_instruction='20秒以内はこだわっていないので全体のバランスが良ければ尺は大丈夫です',note='T2 is 634 frames / 21.133333s. Only the light prefix is stretched; the accepted bird tail remains at its main-episode frame rate. No new AI generation.'))
    print('VISUALS',len(shots),flush=True)


def camera(s):
    import wom04_shorts
    return wom04_shorts.camera(s)


def render_video_shot(s,path):
    if s['asset_id']=='V02':
        x,y,x1,y1=s['art_box']
        prefix_frames=251;source_prefix=126;tail_frames=312
        assert s['frames']==prefix_frames+tail_frames
        factor=prefix_frames/source_prefix
        # Use the already softened/approved main-episode composite. Crop away its header only.
        # Stretch the apparition prefix, then retain all 312 tail frames at native 30fps.
        fc=(f'[1:v]crop=1458:820:231:110,scale={x1-x}:{y1-y}:flags=lanczos,split=2[p][t];'
            f'[p]trim=end_frame={source_prefix},setpts=(PTS-STARTPTS)*{factor:.12f},'
            f'minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,'
            f'tpad=stop_mode=clone:stop_duration=0.2,trim=end_frame={prefix_frames},setpts=N/(30*TB)[light];'
            f'[t]trim=start_frame={source_prefix}:end_frame=438,setpts=N/(30*TB)[bird];'
            f'[light][bird]concat=n=2:v=1:a=0[art];'
            f'[0:v][art]overlay={x}:{y}:shortest=1,format=yuv420p[v]')
        ff(['-loop',1,'-framerate',30,'-i',s['file'],'-i',s['source']['path'],
            '-filter_complex_threads',2,'-filter_complex',fc,'-map','[v]',
            '-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast',
            '-crf',18,'-pix_fmt','yuv420p','-video_track_timescale',15360,path])
        save(ROOT/'records/T2_video_retime.json',dict(source=s['source']['path'],source_sha256=s['source']['sha256'],
            source_prefix_frames=[0,126],output_prefix_frames=251,light_time_factor=factor,
            source_bird_frames=[126,438],output_bird_frames=312,bird_speed_factor=1,
            source_crop_xywh=[231,110,1458,820],output_art_box=s['art_box'],
            cut_frame=71,vanish_frame=322,end_frame=634,interpolation='Optical flow on light prefix only',
            tail_timing='Every source frame 126..437 kept in order at 30fps; no speed change or frame dropping.'))
        return
    x,y,x1,y1=s['art_box'];factor=s['frames']/FPS/10
    fc=f'[1:v]setpts=(PTS-STARTPTS)*{factor:.12f},scale={x1-x}:{y1-y}:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.2[art];[0:v][art]overlay={x}:{y}:shortest=1,format=yuv420p[v]'
    args=['-loop',1,'-framerate',30,'-i',s['file'],'-i',s['source']['path'],'-filter_complex_threads',2,'-filter_complex',fc,'-map','[v]']
    ff([*args,'-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-pix_fmt','yuv420p','-video_track_timescale',15360,path])

def render():
 import imageio_ffmpeg
 shots=[s for s in read(ROOT/'records/visual_manifest.json')['shots'] if s['short_id'] in ['T1','T2','T3']];rows=[s for s in read(ROOT/'records/shorts.json')['shorts'] if s['id'] in ['T1','T2','T3']];rendered=[];captionrecords=[p for p in read(ROOT/'records/caption_manifest.json') if p['short_id']!='T2']
 for s in shots:
  path=ROOT/f'_work/{s["short_id"]}_{s["asset_id"]}.mp4';stamp=path.with_suffix('.json');cfg={'image':s['sha256'],'frames':s['frames'],'camera':camera(s),'source_sha':s['source']['sha256']}
  if not(path.exists() and stamp.exists() and read(stamp)==cfg):
   if s['source']['kind']=='video':render_video_shot(s,path)
   else:
    args=['-loop',1,'-framerate',30,'-i',s['file'],'-filter_complex_threads',2,'-filter_complex',camera(s),'-map','[v]']
    ff([*args,'-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-pix_fmt','yuv420p','-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',path])
   save(stamp,cfg)
  rendered.append({**s,'encoded_file':str(path),'encoded_sha256':sha(path)});print('SHOT',s['short_id'],s['asset_id'],flush=True)
 save(ROOT/'records/render_shots.json',rendered)
 for s in rows:
  if s['id']!='T2':continue
  id=s['id'];group=[r for r in rendered if r['short_id']==id];listing=ROOT/f'_work/{id}_concat.txt';listing.write_text(''.join(f"file '{r['encoded_file']}'\nduration {r['frames']/FPS:.9f}\n" for r in group));picture=ROOT/f'_work/{id}_picture.mp4'
  ff(['-f','concat','-safe',0,'-i',listing,'-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512',picture])
  pages=s['caption_groups']+[{'text':s['cta_text'],'start_frame':s['cta_start_frame'],'end_frame':s['frames'],'brand':True}];ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding','Style: Main,Arial,68,&H00DFF0F4,&H00DFF0F4,&H0010180C,&HAA10180C,-1,0,0,0,100,100,0,0,1,4,1,5,80,200,0,1','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
  def tm(frame):
   ticks=round(frame/FPS*100);return f'{ticks//360000}:{ticks//6000%60:02}:{ticks//100%60:02}.{ticks%100:02}'
  for i,p in enumerate(pages):
   words=p['text'].split();d=ImageDraw.Draw(Image.new('RGB',(1,1)));lines=[]
   for size in ([36] if p.get('brand') else range(68,53,-2)):
    f=font(size,bold=True)
    if len(words)<=5 and d.textlength(p['text'],font=f)<=770:lines=[p['text']];break
    candidates=[[' '.join(words[:cut]),' '.join(words[cut:])] for cut in range(1,len(words)) if cut<=5 and len(words)-cut<=5]
    best=min(candidates,key=lambda lines:max(d.textlength(line,font=f) for line in lines))
    if max(d.textlength(line,font=f) for line in best)<=770:lines=best;break
   assert len(lines)<=2 and max(len(x.split()) for x in lines)<=5
   ypos=1410 if p.get('brand') else 1250
   content='\\N'.join(lines);override=f'{{\\an5\\pos(480,{ypos})\\fs{size}}}';ass.append(f'Dialogue: 0,{tm(p["start_frame"])},{tm(p["end_frame"])},Main,,0,0,0,,{override}{content}')
   captionrecords.append({'short_id':id,'page':i+1,**p,'lines':lines,'font_size':size,'position':[480,ypos]})
  ap=ROOT/f'_work/{id}.ass';ap.write_text('\n'.join(ass)+'\n');out=ROOT/f'deliverables/QO_short_{s["episode"]}_{id}_v01.mp4'
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(picture),'-i',str(ROOT/f'audio/{id}_final.m4a'),'-vf',f"ass='{ap}'",'-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-frames:v',str(s['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True);print('RENDERED',id,flush=True)
 save(ROOT/'records/render_shots.json',rendered);save(ROOT/'records/caption_manifest.json',captionrecords)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['narration','captions','audio','visuals','render'])
    args=parser.parse_args()
    globals()[args.stage]()
