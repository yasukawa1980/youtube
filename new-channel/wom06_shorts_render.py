"""EP006 Shorts: native-word cuts, nine unique sources, single final encoder."""
import os
import argparse, difflib, math, json, re, subprocess
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance
import wom_shorts_produce as base
from wom06_shorts import ROOT, REQUEST, READINGS, MODELS, SR, sha, save
CONFIG = json.loads(Path(os.environ['QO_EP006_CONFIG']).read_text()) if os.environ.get('QO_EP006_CONFIG') else {}
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
  texts={
   'S1':["Sophocles' play Oedipus the King", "remembers the riddling Sphinx,", "but it never gives", "the words of the riddle.", "Later writers do:", "what has one voice,", "and becomes four-footed,", "two-footed, and three-footed?", "A human being.", "In these texts, there is", "no morning, noon, or evening."],
   'S2':["The Great Sphinx of Giza", "is not a woman.", "It has a lion's body", "and the face of a king,", "in the royal headcloth", "of a pharaoh.", "Hatshepsut, a woman who ruled", "as pharaoh, appears as", "a sphinx too, with", "a king's ceremonial beard."],
   'S3':["It is often said", "that Napoleon's soldiers shot off", "the Sphinx's nose.", "Yet drawings by the Danish traveler", "Frederic Norden, who visited", "in the 1730s,", "already show the face", "without its nose.", "They were printed long before", "Napoleon came to Egypt", "in 1798."]
  }[s['id']]
  texts=CONFIG.get('caption_texts',{}).get(s['id'],texts)
  groups=[];pos=0
  for text in texts:
   end=pos+len(text.split());groups.append({'text':text,'word_start':pos,'word_end':end});pos=end
  for protected in ['in the 1730s,','in 1798.']:
   if protected in s['text']:assert any(protected in g['text'] for g in groups),protected
  nframes=CONFIG.get('frame_counts',{'S1':600,'S2':540,'S3':650})[s['id']];assert math.ceil(s['native_audio_duration']*FPS)<=nframes<=660;cta_frame=nframes-60
  for i,g in enumerate(groups):
   g['start_frame']=max(0,round(wordtimes[g['word_start']]['start']*FPS)) if i else 0
   g['end_frame']=max(g['start_frame']+1,round(wordtimes[groups[i+1]['word_start']]['start']*FPS)) if i+1<len(groups) else math.ceil(s['native_audio_duration']*FPS)
   assert g['end_frame']<=nframes
  assert ' '.join(g['text'] for g in groups)==s['text']
  row={**s,'episode':'EP006','title_ja':s['title'],'words_timed':wordtimes,'alignment_ratio':matcher.ratio(),'context_adjusted_word_indices':sorted(set(context_mapped)),'alignment_method':'Native Kokoro phoneme durations mapped to script words by sequence alignment, with contextual phoneme substitutions assigned within adjacent aligned spans. These are model-derived word estimates, not human auditory verification.','caption_groups':groups,'frames':nframes,'duration_seconds':nframes/FPS,'cta_start':cta_frame/FPS,'cta_start_frame':cta_frame,'cta_text':'Full story on Quiet Origins'}
  allrows.append(row);print('CAPTIONS',s['id'],len(groups),'pages',nframes/FPS,'seconds',matcher.ratio(),flush=True)
 save(ROOT/'records/shorts.json',{'shorts':allrows,'request_sha256':sha(REQUEST)})


def audio():
    reports=[]
    source=MAIN.parent/'確認版_v01_20261026/audio/common_bgm_and_brand.wav'
    for i,s in enumerate(read(ROOT/'records/shorts.json')['shorts']):
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
    assert read(ROOT/'records/narration.json')['all_within_22_seconds']
    sources={a['id']:a for a in read(MAIN/'records/source_assets.json')['assets']}
    mainshots={a['key']:a for a in read(MAIN/'records/visual_manifest.json')['shots']}
    assets={};shots=[];(ROOT/'assets').mkdir(exist_ok=True)
    specs={
        'S1':[('met_437153',None),('jebb1904_15','but it never gives'),('D_riddle','what has one voice')],
        'S2':[('museo_Inv02_008',None),('museo_Album1_004','the face of a king'),('met_544442','Hatshepsut')],
        'S3':[('museo_Inv27_001',None),('norden_109','Yet drawings'),('norden_105','They were printed')]}
    specs.update(CONFIG.get('visual_specs',{}))
    for row in read(ROOT/'records/shorts.json')['shorts']:
        sid=row['id'];plans=specs[sid]
        starts=[0 if phrase is None else phrase_frame(row,phrase) for aid,phrase in plans]
        for i,(aid,phrase) in enumerate(plans):
            crop=None;norm=None
            if aid=='D_riddle':
                m=mainshots[aid];path=Path(m['file']);original_sha=m['sha256']
                im=Image.open(path).convert('RGB');crop=[150,210,1770,680]
            else:
                original=sources[aid];path=Path(original.get('path',original.get('local_path')));original_sha=original['sha256']
                im=ImageOps.exif_transpose(Image.open(path)).convert('RGB')
                m=mainshots.get(aid,dict(label='ENGRAVING｜銅版画',source='Norden, plate XLV, London 1780 • Wellcome Collection / Internet Archive'))
                norm=m.get('crop_normalized')
                if aid=='met_544442':norm=[.35,.17,.65,.57]
                if aid=='museo_Inv27_001':norm=[.35,.015,.80,.48]
                if aid=='norden_109':norm=[.27,.07,.66,.76]
                if norm:crop=[round(v*k) for v,k in zip(norm,[im.width,im.height,im.width,im.height])]
                if aid=='jebb1904_15':crop=m['detail_crop_pixels'];norm=m['detail_crop_normalized']
            assert sha(path)==original_sha
            if aid=='met_437153':assert norm==[.12,.10,.95,.33]
            if aid=='jebb1904_15':assert crop==[60,1400,1015,1524]
            piece=im.crop(crop) if crop else im
            a=dict(id=aid,path=str(path),sha256=sha(path),kind='image',label=m['label'],source=m['source'])
            assets[aid]=a
            # Background and foreground both originate strictly inside the safe crop.
            bg=ImageEnhance.Brightness(ImageOps.fit(piece,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.30)
            d=ImageDraw.Draw(bg);d.rectangle((0,120,1079,269),fill=base.BG)
            texts=[];lines=[(140,'QUIET ORIGINS / EP006',25,base.GOLD),(181,a['label'],25,base.GOLD)]
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
            out=ROOT/f'assets/{sid}_{aid}.png';bg.save(out)
            stop=starts[i+1] if i+1<len(starts) else row['frames'];assert stop-starts[i]>=45
            endzoom={'met_544442':1.18,'museo_Inv27_001':1.10,'norden_109':1.22}.get(aid,1.0)
            shots.append(dict(short_id=sid,asset_id=aid,start_frame=starts[i],end_frame=stop,frames=stop-starts[i],
                file=str(out),sha256=sha(out),source=a,texts=texts,art_box=[x,y,x+fit.width,y+fit.height],
                source_crop_pixels=crop,source_crop_normalized=norm,background_also_uses_only_crop=True,
                zoom_start=.97,zoom_end=endzoom,viewport=[0,270,1080,860],cut_phrase=phrase,
                cut_word_seconds=None if phrase is None else next(w['start'] for w in row['words_timed'] if round(w['start']*FPS)==starts[i]),
                target_center=[.70,.43] if aid=='norden_109' else [.5,.5]))
    assert len({s['source']['sha256'] for s in shots})==len(shots)==9
    save(ROOT/'records/visual_manifest.json',dict(shots=shots,assets=assets,same_source_not_repeated=True))
    print('VISUALS',len(shots),flush=True)


def camera(s):
    phase=f'on/{max(1,s["frames"]-1)}'
    z=f'({s["zoom_start"]}*exp(log({s["zoom_end"]}/{s["zoom_start"]})*{phase}))'
    cx,cy=s['target_center'];cx*=1080;cy*=860
    x=f'(W/2+({cx}-W/2)*{phase}-W/(2*{z}))'
    y=f'(H/2+({cy}-H/2)*{phase}-H/(2*{z}))'
    p=f"perspective=x0='{x}':y0='{y}':x1='{x}+W/{z}':y1='{y}':x2='{x}':y2='{y}+H/{z}':x3='{x}+W/{z}':y3='{y}+H/{z}':sense=source:eval=frame:interpolation=cubic"
    return f'[0:v]split=2[base][art];[art]crop=1080:860:0:270,format=yuv444p,{p}[moving];[base][moving]overlay=0:270:format=yuv444,format=yuv420p[v]'


def make_ass(s):
    sid=s['id'];records=[]
    pages=s['caption_groups']+[dict(text=s['cta_text'],start_frame=s['cta_start_frame'],end_frame=s['frames'],brand=True)]
    ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding','Style: Main,Arial,68,&H00DFF0F4,&H00DFF0F4,&H0010180C,&HAA10180C,-1,0,0,0,100,100,0,0,1,4,1,5,80,200,0,1','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    def tm(frame):
        ticks=round(frame/FPS*100);return f'{ticks//360000}:{ticks//6000%60:02}:{ticks//100%60:02}.{ticks%100:02}'
    for i,p in enumerate(pages):
        words=p['text'].split();d=ImageDraw.Draw(Image.new('RGB',(1,1)));lines=[]
        for size in ([36] if p.get('brand') else range(68,49,-2)):
            f=font(size,bold=True)
            if len(words)<=5 and d.textlength(p['text'],font=f)<=770:lines=[p['text']];break
            candidates=[[' '.join(words[:cut]),' '.join(words[cut:])] for cut in range(1,len(words)) if cut<=5 and len(words)-cut<=5]
            best=min(candidates,key=lambda lines:max(d.textlength(line,font=f) for line in lines))
            if max(d.textlength(line,font=f) for line in best)<=770:lines=best;break
        assert lines and len(lines)<=2 and max(len(x.split()) for x in lines)<=5
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
        cfg=dict(image=s['sha256'],frames=s['frames'],camera=camera(s),source_sha=s['source']['sha256'],crf=18)
        if not(path.exists() and stamp.exists() and read(stamp)==cfg):
            ff(['-loop',1,'-framerate',30,'-i',s['file'],'-filter_complex_threads',2,'-filter_complex',camera(s),'-map','[v]',
                '-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-profile:v','high',
                '-pix_fmt','yuv420p','-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',path])
            save(stamp,cfg)
        rendered.append(dict(**s,encoded_file=str(path),encoded_sha256=sha(path)))
        print('SHOT',s['short_id'],s['asset_id'],flush=True)
    save(ROOT/'records/render_shots.json',rendered)
    for s in rows:
        sid=s['id'];ap,records=make_ass(s);captionrecords.extend(records)
        group=[r for r in rendered if r['short_id']==sid]
        out=ROOT/f'deliverables/QO_short_EP006_{sid}_{VERSION}.mp4'
        # Every shot has an independent decoder. Only decoded frames reach this one final encoder.
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s','1080x1920','-r','30','-i','pipe:0',
             '-i',str(ROOT/f'audio/{sid}_final.m4a'),'-vf',f"ass='{ap}'",'-map','0:v:0','-map','1:a:0',
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


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['captions','audio','visuals','render']);args=p.parse_args();globals()[args.stage]()
