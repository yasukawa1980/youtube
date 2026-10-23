"""EP004 Shorts: preserve Claude's copy and the approved Heart settings."""
import argparse
import difflib
import json
import math
import re
import subprocess
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageEnhance
from pathlib import Path

import wom_shorts_produce as base
from wom04_produce import PHONEMES as MAIN_PHONEMES

# Keep the main episode's name pronunciation; the possessive suffix is /z/,
# rather than the isolated letter-name /es/ produced by splitting off "'s".
PHONEMES = {"Hesiod's": MAIN_PHONEMES['Hesiod']+'z', **MAIN_PHONEMES}

ROOT = Path('/Users/ryo/Desktop/新チャンネル/ショート/EP004_確認版_v01_20261024')
REQUEST = Path(__file__).resolve().parent / 'wom_ショート制作依頼_EP004_20261023.md'


def scripts():
    items = re.findall(r'^### (P[123]) — (.+?)\n\n> (.+)$', REQUEST.read_text(), re.M)
    assert len(items) == 3
    return [dict(id=id, episode='EP004', title_ja=title, text=text,
                 words=len(text.split())) for id, title, text in items]


base.ROOT = ROOT
base.REQUEST = REQUEST
base.PHONEMES = PHONEMES
base.scripts = scripts

MEDIA = Path('/Users/ryo/Desktop/新チャンネル/EP004_Pandora/確認版_v01_20261023')


def audio():
    reports=[]
    source=MEDIA/'audio/common_bgm_and_brand.wav'
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


def registry():
    from wom04_visuals import SOURCES,LABELS
    assets={}
    for a in read(MEDIA/'records/source_assets.json')['assets']:
        aid=a['asset_id']
        if aid not in ['A01','A02','A10','A11','A12','A21']:continue
        assert sha(Path(a['local_path']))==a['sha256']
        assets[aid]=dict(id=aid,path=a['local_path'],sha256=a['sha256'],kind='image',
            label=LABELS.get(aid,'PUBLIC DOMAIN PRINT｜パブリックドメインの版画' if aid=='A21' else 'MUSEUM OBJECT｜博物館資料'),
            source=SOURCES[aid],original_record=a,source_url=a['object_url'])
    a=next(a for a in read(MEDIA/'records/ai_images.json') if a['id']=='R04')
    assert sha(Path(a['local_path']))==a['sha256']
    assets['R04']=dict(id='R04',path=a['local_path'],sha256=a['sha256'],kind='image',
        label='AI RECONSTRUCTION｜AIによる再現',source='OpenAI image generation • R04 • Illustration',original_record=a)
    return assets


def visuals():
    assets=registry(); manifest=[]
    (ROOT/'assets').mkdir(exist_ok=True)
    for s in read(ROOT/'records/shorts.json')['shorts']:
        id=s['id']; end=s['frames']
        specs={'P1':[('R04',None),('A01','like this one')],
               'P2':[('A11',None),('A12','In his book'),('A10','became a pyxis')],
               'P3':[('A21',None),('A02','Only hope')]}[id]
        words=[re.sub(r'[^a-z]','',w['word'].lower()) for w in s['words_timed']]
        def phrase_frame(phrase):
            needle=phrase.lower().split()
            j=next(j for j in range(len(words)) if words[j:j+len(needle)]==needle)
            return round(s['words_timed'][j]['start']*FPS)
        starts=[0 if phrase is None else phrase_frame(phrase) for _,phrase in specs]
        for j,(aid,_) in enumerate(specs):
            a=assets[aid]; im=ImageOps.exif_transpose(Image.open(a['path'])).convert('RGB')
            crop=None
            crops={'A21':(.02,.425,.98,.98),'A02':(.20,.06,.83,.172),'A12':(.045,.565,.68,.642)}
            if aid in crops:
                w,h=im.size; crop=tuple(round(v*k) for v,k in zip(crops[aid],[w,h,w,h]));piece=im.crop(crop)
            else:piece=im
            bg=ImageEnhance.Brightness(ImageOps.fit(piece,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.30)
            d=ImageDraw.Draw(bg); d.rectangle((0,120,1079,269),fill=base.BG)
            texts=[]
            for y,value,size,color in [(140,'QUIET ORIGINS / EP004',25,base.GOLD),(183,a['label'],25,base.GOLD),(229,a['source'],23,base.IVORY)]:
                while d.textlength(value,font=font(size,value))>920: size-=1
                f=font(size,value); box=d.textbbox((80,y),value,font=f)
                assert box[2]<=1000 and 140<=box[1]<box[3]<=260
                d.text((80,y),value,font=f,fill=color); texts.append(dict(text=value,bbox=list(box)))
            if aid=='R04':
                fit=ImageOps.fit(piece,(1080,860),Image.Resampling.LANCZOS)
            else: fit=ImageOps.contain(piece,(1080,860),Image.Resampling.LANCZOS)
            x=(1080-fit.width)//2; y=270+(860-fit.height)//2; bg.paste(fit,(x,y))
            path=ROOT/f'assets/{id}_{aid}.png'; bg.save(path)
            stop=starts[j+1] if j+1<len(starts) else end
            assert (stop-starts[j])/FPS>=1.5,(id,aid)
            manifest.append(dict(short_id=id,asset_id=aid,start_frame=starts[j],end_frame=stop,
                frames=stop-starts[j],file=str(path),sha256=sha(path),source=a,texts=texts,
                art_box=[x,y,x+fit.width,y+fit.height],source_crop_pixels=crop,
                zoom_start=.97,zoom_end=1.,viewport=[0,270,1080,860]))
    hashes=[s['source']['sha256'] for s in manifest]
    assert len(hashes)==len(set(hashes))==7
    save(ROOT/'records/visual_manifest.json',dict(shots=manifest,assets=assets,
        same_source_not_repeated=True,A21_main_crop_in_foreground_and_background=True,A02_rim_only_no_figural_neck=True,A12_detail_no_highlight=True))
    print('VISUALS',len(manifest),flush=True)


def camera(s):
    z=f'(.97*exp(log(1/.97)*on/{max(1,s["frames"]-1)}))'
    x=f'(W/2-W/(2*{z}))';y=f'(H/2-H/(2*{z}))'
    p=f"perspective=x0='{x}':y0='{y}':x1='{x}+W/{z}':y1='{y}':x2='{x}':y2='{y}+H/{z}':x3='{x}+W/{z}':y3='{y}+H/{z}':sense=source:eval=frame:interpolation=cubic"
    return f'[0:v]split=2[base][art];[art]crop=1080:860:0:270,format=yuv444p,{p}[moving];[base][moving]overlay=0:270:format=yuv444,format=yuv420p[v]'


def render():
    base.camera=camera
    base.render()


SR=base.SR;FPS=base.FPS;MODELS=base.MODELS;read=base.read;save=base.save;sha=base.sha;ff=base.ff;levels=base.levels;rms=base.rms; font=base.font

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
  if s['id']=='P1':
   texts=["Pandora never opened a box.","In Hesiod's poem, from around","700 BCE, she lifts the","great lid of a jar.","The Greek word is pithos,","a storage jar like this one,","made on Crete, about","one and a half meters tall."]
   groups=[];pos=0
   for text in texts:
    end=pos+len(text.split());groups.append({'text':text,'word_start':pos,'word_end':end});pos=end
  for protected in ['700 BCE','one and a half meters','1508']:
   if protected in s['text']:assert any(protected in g['text'] for g in groups),protected
  nframes=min(600,max(450,math.ceil((s['native_audio_duration']+2)*FPS)));cta_frame=math.ceil(s['native_audio_duration']*FPS);assert 450<=nframes<=600 and cta_frame<nframes
  for i,g in enumerate(groups):
   g['start_frame']=max(0,round(wordtimes[g['word_start']]['start']*FPS)) if i else 0
   g['end_frame']=max(g['start_frame']+1,round(wordtimes[groups[i+1]['word_start']]['start']*FPS)) if i+1<len(groups) else cta_frame
   assert g['end_frame']<=cta_frame
  assert ' '.join(g['text'] for g in groups)==s['text']
  row={**s,'words_timed':wordtimes,'alignment_ratio':matcher.ratio(),'context_adjusted_word_indices':sorted(set(context_mapped)),'alignment_method':'Native Kokoro phoneme durations mapped to script words by sequence alignment, with contextual phoneme substitutions assigned within adjacent aligned spans. These are model-derived word estimates, not human auditory verification.','caption_groups':groups,'frames':nframes,'duration_seconds':nframes/FPS,'cta_start':cta_frame/FPS,'cta_start_frame':cta_frame,'cta_text':'Full story on Quiet Origins'}
  allrows.append(row);print('CAPTIONS',s['id'],len(groups),'pages',nframes/FPS,'seconds',matcher.ratio(),flush=True)
 save(ROOT/'records/shorts.json',{'shorts':allrows,'request_sha256':sha(REQUEST)})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['narration','captions','audio','visuals','render'])
    args = parser.parse_args()
    (base.narration if args.stage=='narration' else globals()[args.stage])()
