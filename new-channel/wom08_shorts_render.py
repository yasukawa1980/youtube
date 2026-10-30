"""EP008 Shorts: native-word cuts, seven unique sources, single final encoder."""
import os
import argparse, difflib, math, json, re, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance, ImageFont
import wom_shorts_produce as base
from wom08_shorts import ROOT, REQUEST, READINGS, MODELS, SR, sha, save
CONFIG = json.loads(Path(os.environ['QO_EP008_CONFIG']).read_text()) if os.environ.get('QO_EP008_CONFIG') else {}
VERSION = CONFIG.get('version', 'v01')
FPS=30;read=base.read;ff=base.ff;levels=base.levels;rms=base.rms;font=base.font
MAIN=READINGS.parent.parent
PHONEMES={r['display']:r['phonemes'] for r in read(READINGS) if r['language']=='en' and 'phonemes' in r}
REPLACEMENTS={r['display']:r['spoken'] for r in read(READINGS) if r['language']=='en'}
Image.MAX_IMAGE_PIXELS=200000000
def captions():
 from kokoro_onnx.tokenizer import Tokenizer
 # Use the same tokenizer through the existing model session, without synthesizing again.
 import onnxruntime as ort
 ort.disable_telemetry_events()
 from kokoro_onnx import Kokoro
 opt=ort.SessionOptions();opt.intra_op_num_threads=2
 tts=Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(MODELS/'voices-v1.0.bin'))
 nar=read(ROOT/'records/narration.json');assert nar['all_within_22_seconds'];allrows=[]
 for s in nar['scripts']:
  times=read(ROOT/f'records/{s["id"]}_phoneme_timings.json')['timings'];words=s['text'].split();ignored=set(' \t\nˈˌː.,;:!?—-()');expected=[];owners=[]
  for i,w in enumerate(words):
   key=re.sub(r"^[^A-Za-z]+|[^A-Za-z']+$",'',w);ph=PHONEMES.get(key.rstrip("'"),tts.tokenizer.phonemize(REPLACEMENTS.get(w.rstrip(',.'),w),'en-us'))
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
  texts=CAPTIONS[s['id']]
  groups=[];pos=0
  for text in texts:
   end=pos+len(text.split());groups.append({'text':text,'word_start':pos,'word_end':end});pos=end
  for protected in ['April 1923,','In 1869,']:
   if protected in s['text']:assert any(protected in g['text'] for g in groups),protected
  nframes=max(540,math.ceil((s['native_audio_duration']+.15)*FPS));assert math.ceil(s['native_audio_duration']*FPS)<=nframes<=660;cta_frame=nframes-60
  for i,g in enumerate(groups):
   g['start_frame']=max(0,round(wordtimes[g['word_start']]['start']*FPS)) if i else 0
   g['end_frame']=max(g['start_frame']+1,round(wordtimes[groups[i+1]['word_start']]['start']*FPS)) if i+1<len(groups) else math.ceil(s['native_audio_duration']*FPS)
   assert g['end_frame']<=nframes
  assert ' '.join(g['text'] for g in groups)==s['text']
  row={**s,'episode':'EP008','title_ja':s['title'],'words_timed':wordtimes,'alignment_ratio':matcher.ratio(),'context_adjusted_word_indices':sorted(set(context_mapped)),'alignment_method':'Native Kokoro phoneme durations mapped to script words by sequence alignment, with contextual phoneme substitutions assigned within adjacent aligned spans. These are model-derived word estimates, not human auditory verification.','caption_groups':groups,'frames':nframes,'duration_seconds':nframes/FPS,'cta_start':cta_frame/FPS,'cta_start_frame':cta_frame,'cta_text':'Full story on Quiet Origins'}
  allrows.append(row);print('CAPTIONS',s['id'],len(groups),'pages',nframes/FPS,'seconds',matcher.ratio(),flush=True)
 save(ROOT/'records/shorts.json',{'shorts':allrows,'request_sha256':sha(REQUEST)})


def phrase_frame(s, phrase):
    words=[re.sub(r"[^a-z0-9']",'',w['word'].lower()) for w in s['words_timed']]
    needle=phrase.lower().split()
    j=next(j for j in range(len(words)) if words[j:j+len(needle)]==needle)
    return round(s['words_timed'][j]['start']*FPS)


def make_ass(s):
    sid=s['id'];records=[]
    pages=s['caption_groups']+[dict(text=s['cta_text'],start_frame=s['cta_start_frame'],end_frame=s['frames'],brand=True)]
    ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding','Style: Main,Arial,68,&H00DFF0F4,&H00DFF0F4,&H0010180C,&HAA10180C,-1,0,0,0,100,100,0,0,1,4,1,5,80,200,0,1','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    def tm(frame):
        ticks=round(frame/FPS*100);return f'{ticks//360000}:{ticks//6000%60:02}:{ticks//100%60:02}.{ticks%100:02}'
    for i,p in enumerate(pages):
        words=p['text'].split();d=ImageDraw.Draw(Image.new('RGB',(1,1)));lines=[]
        for size in ([36] if p.get('brand') else range(68,39,-2)):
            f=font(size,bold=True)
            if len(words)<=5 and d.textlength(p['text'],font=f)<=770:lines=[p['text']];break
            candidates=[[' '.join(words[:cut]),' '.join(words[cut:])] for cut in range(1,len(words)) if 4<=cut<=5 and 4<=len(words)-cut<=5]
            if not candidates:continue
            best=min(candidates,key=lambda lines:max(d.textlength(line,font=f) for line in lines))
            if max(d.textlength(line,font=f) for line in best)<=770:lines=best;break
        assert lines and len(lines)<=2 and all(4<=len(x.split())<=5 for x in lines)
        ypos=1410 if p.get('brand') else 1250
        content='\\N'.join(lines);override=f'{{\\an5\\pos(480,{ypos})\\fs{size}}}'
        ass.append(f'Dialogue: 0,{tm(p["start_frame"])},{tm(p["end_frame"])},Main,,0,0,0,,{override}{content}')
        records.append(dict(short_id=sid,page=i+1,**p,lines=lines,font_size=size,position=[480,ypos]))
    path=ROOT/f'_work/{sid}.ass';path.write_text('\n'.join(ass)+'\n')
    return path,records


def render():
    import imageio_ffmpeg
    shots=read(ROOT/'records/visual_manifest.json')['shots'];rows=read(ROOT/'records/shorts.json')['shorts']
    rendered=[];captionrecords=[];encoding=[]
    for s in shots:
        path=ROOT/f'_work/{s["short_id"]}_{s["asset_id"]}.mp4';stamp=path.with_suffix('.json')
        cfg=dict(image=s['sha256'],header_sha256=sha(Path(s['header_file'])),frames=s['frames'],camera=camera(s),source_sha=s['source']['sha256'],crf=18)
        if not(path.exists() and stamp.exists() and read(stamp)==cfg):
            ff(['-loop',1,'-framerate',30,'-i',s['file'],'-loop',1,'-framerate',30,'-i',s['header_file'],'-filter_complex_threads',2,'-filter_complex',camera(s),'-map','[v]',
                '-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-profile:v','high',
                '-pix_fmt','yuv420p','-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',path])
            save(stamp,cfg)
        rendered.append(dict(**s,encoded_file=str(path),encoded_sha256=sha(path)))
        print('SHOT',s['short_id'],s['asset_id'],flush=True)
    save(ROOT/'records/render_shots.json',rendered)
    for s in rows:
        sid=s['id'];ap,records=make_ass(s);captionrecords.extend(records)
        group=[r for r in rendered if r['short_id']==sid]
        out=ROOT/f'deliverables/QO_short_EP008_{sid}_{VERSION}.mp4'
        # Every shot has an independent decoder. Only decoded frames reach this one final encoder.
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s','1080x1920','-r','30','-i','pipe:0',
             '-i',str(ROOT/f'audio/{sid}_final.m4a'),'-loop','1','-framerate','30','-i',str(ROOT/f'assets/{sid}_headline.png'),'-filter_complex_threads','2','-filter_complex',f"[2:v]format=rgba,fade=t=out:st=2:d=0.3:alpha=1[h];[0:v][h]overlay=0:0:enable='lt(t,2.3)'[t];[t]ass='{ap}'[v]",'-map','[v]','-map','1:a:0',
             '-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high',
             '-frames:v',str(s['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p',
             '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart',str(out)]
        with (ROOT/f'records/{sid}_encode.log').open('w') as log:
            enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
            try:
                for g in group:
                    subprocess.run(['ffmpeg','-nostdin','-v','warning','-threads','2','-i',g['encoded_file'],'-map','0:v:0','-an',
                                    '-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
                enc.stdin.close();assert enc.wait()==0
            except BaseException:enc.kill();enc.wait();raise
        encoding.append(dict(id=sid,command=cmd,video_sha256=sha(out),shot_sources=[dict(path=g['encoded_file'],sha256=g['encoded_sha256']) for g in group]))
        print('RENDERED',sid,flush=True)
    save(ROOT/'records/caption_manifest.json',captionrecords)
    save(ROOT/'records/encoding_method.json',dict(method='Individual shot decoders → raw yuv420p → one encoder per final video; subtitles in the same encoding pass. No MP4 bitstream concatenation.',shorts=encoding))



# 各行4〜5語、最大2行。年代は数字だけの画面へ分けない。
CAPTION_LENGTHS={'K1':[8,10,9,8,8],'K2':[9,8,9,9,10],'K3':[9,8,8,8,4,8]}
CAPTIONS={}
for _s in read(ROOT/'records/narration.json')['scripts']:
 _words=_s['text'].split();_pos=0;CAPTIONS[_s['id']]=[]
 for _count in CAPTION_LENGTHS[_s['id']]:
  CAPTIONS[_s['id']].append(' '.join(_words[_pos:_pos+_count]));_pos+=_count
 assert _pos==len(_words)
HEADLINES={'K1':['CURSE NOT FOUND','IN THE RECORDS'],'K2':['A DEATH,','THEN A CURSE'],'K3':["THE MUMMY'S",'CURSE, 1869']}

def audio():
    reports=[]
    musicroot=Path('/Users/ryo/Desktop/新チャンネル/_共通/BGM/20261029_Suno')
    for i,s in enumerate(read(ROOT/'records/shorts.json')['shorts']):
        sid=s['id'];n=s['frames']*SR//FPS
        normal=ROOT/f'audio/{sid}_normalized.wav'
        q=levels(Path(s['audio_file']))
        filt=f"loudnorm=I=-14:TP=-1.5:LRA=7:linear=true:measured_I={q['input_i']}:measured_TP={q['input_tp']}:measured_LRA={q['input_lra']}:measured_thresh={q['input_thresh']}:offset={q['target_offset']}"
        ff(['-i',s['audio_file'],'-af',filt,'-ar',SR,'-c:a','pcm_f32le',normal])
        voice,sr=sf.read(normal,dtype='float32');assert sr==SR and len(voice)<=n
        voice=np.pad(voice,(0,n-len(voice)))
        source=musicroot/'QO_THEME_A02.wav'
        start=[30,65,105][i];musicpath=ROOT/f'audio/{sid}_filtered_music.wav'
        ff(['-ss',start,'-i',source,'-t',n/SR,'-af','highpass=f=100,equalizer=f=2828:t=o:w=1:g=-3.5','-ar',SR,'-ac',2,'-c:a','pcm_f32le',musicpath])
        music,sr=sf.read(musicpath,dtype='float32');assert sr==SR and len(music)>=n
        music=music[:n];active=np.zeros(n,bool);active[round(s['voice_onset_seconds']*SR):round(s['last_voice_activity_seconds']*SR)]=True
        music*=10**((rms(voice[active])-15-rms(music[active]))/20)
        music[-round(.12*SR):]*=np.linspace(1,0,round(.12*SR))[:,None]
        gain=0;mix=ROOT/f'audio/{sid}_mix.wav'
        for attempt in range(5):
            factor=10**(gain/20);sf.write(mix,(voice[:,None]+music)*factor,SR,subtype='FLOAT')
            q=levels(mix);delta=-14-float(q['input_i'])
            if abs(delta)<.04:break
            gain+=delta
        out=ROOT/f'audio/{sid}_final.m4a'
        ff(['-i',mix,'-ar',48000,'-c:a','aac','-b:a','192k',out]);final=levels(out)
        limiter=None
        if float(final['input_tp'])>-1:
            correction=0
            for attempt in range(4):
                limiter='192kHz oversampled limiter, -2dBFS ceiling (FFmpeg 7.1)'
                filt=f'volume={correction}dB,aresample=192000,alimiter=limit={10**(-2/20)}:level=false:latency=true,aresample=48000'
                import imageio_ffmpeg
                subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(mix),'-af',filt,'-ar','48000','-c:a','aac','-b:a','192k',str(out)],check=True);final=levels(out)
                if abs(float(final['input_i'])+14)<=.1 and float(final['input_tp'])<=-1:break
                correction+=-14-float(final['input_i'])
        assert abs(float(final['input_i'])+14)<=.15 and float(final['input_tp'])<=-1, final
        sf.write(ROOT/f'audio/{sid}_bgm.wav',music*factor,SR,subtype='FLOAT')
        onset_rms=rms(music[:240]*factor);assert onset_rms>-70
        reports.append(dict(id=sid,mix=final,voice_onset_native=s['voice_onset_seconds'],bgm_source=str(source),bgm_source_sha256=sha(source),bgm_excerpt_start_seconds=start,bgm_excerpt_end_seconds=start+n/SR,bgm_during_narration_dbfs=rms(music[active]*factor),voice_during_narration_dbfs=rms(voice[active]*factor),bgm_relative_to_voice_db=-15,bgm_first_10ms_dbfs=onset_rms,bgm_fade_in=False,filter='highpass 100Hz; EQ 2828Hz, 1 octave, -3.5dB',final_file=str(out),sha256=sha(out),voice_rate_or_pitch_processing=False,peak_limiter=limiter))
        print('AUDIO',sid,final['input_i'],final['input_tp'],flush=True)
    save(ROOT/'records/audio_qc.json',dict(passed=True,target_lufs=-14,maximum_true_peak_db=-1,reports=reports))


def headline(sid):
    layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer);f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia Bold.ttf',136)
    boxes=[];top=350
    bottom=top+len(HEADLINES[sid])*122-22
    d.rounded_rectangle((84,top-18,876,bottom+18),radius=16,fill=(5,12,16,125))
    for j,text in enumerate(HEADLINES[sid]):
        b=d.textbbox((0,0),text,font=f);mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),text,font=f,fill=255)
        mask=mask.resize((min(770,round(mask.width*100/mask.height)),100),Image.Resampling.LANCZOS)
        x=480-mask.width//2;y=top+j*122;layer.paste((244,239,223,255),(x,y,x+mask.width,y+100),mask)
        boxes.append(dict(text=text,bbox=[x,y,x+mask.width,y+100],glyph_height=100))
    path=ROOT/f'assets/{sid}_headline.png';layer.save(path)
    return dict(id=sid,text=' '.join(HEADLINES[sid]),file=str(path),sha256=sha(path),font='Georgia Bold',color='#f4efdf',lines=boxes,overlay_bbox=[84,top-18,876,bottom+18],fade_start_seconds=2,fade_duration_seconds=.3)


def visuals():
    from wom08_shorts_visuals import build
    build(globals())


def camera(s):
    x,y,w,h=s['viewport'];n=s['frames'];z=f'exp(log({s["zoom_end"]})*on/{n-1})'
    dx=f'(W-W/{z})/2';dy=f'(H-H/{z})/2'
    p=f"perspective=x0='{dx}':y0='{dy}':x1='{dx}+W/{z}':y1='{dy}':x2='{dx}':y2='{dy}+H/{z}':x3='{dx}+W/{z}':y3='{dy}+H/{z}':sense=source:eval=frame:interpolation=cubic"
    return f'[0:v]split=2[base][art];[art]crop={w}:{h}:{x}:{y},format=yuv444p,{p}[moving];[base][moving]overlay={x}:{y}:format=yuv444[portrait];[portrait][1:v]overlay=0:0:format=yuv444,format=yuv420p[v]'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['captions','audio','visuals','render']);args=p.parse_args();globals()[args.stage]()
