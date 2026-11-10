"""Resume 30f49cbb after 7ede2457 crop approval; never synthesize audio."""
import json
import re
import sys
import soundfile as sf
import numpy as np
from PIL import Image, ImageDraw
from pnt02_shorts_preflight import ROOT, MAIN, REPO, REGIONS, ARCHIVE, guard, save, sha

def verify_reuse():
    guard()
    request=(ROOT/'records/request.md').read_text()
    nar=json.loads((ROOT/'records/narration.json').read_text())
    scripts=dict(re.findall(r'^### (V[123]) — .+\n\n見出し：\*\*.+\*\*\n\n> (.+)$',request,re.M))
    mix=json.loads((ROOT/'records/audio_qc.json').read_text())['reports']
    rows=[]
    for s in nar['scripts']:
        sid=s['id'];wav=ROOT/f'audio/{sid}_native.wav'
        assert s['text']==scripts[sid]
        assert sha(wav)==s['audio_sha256']==sha(ARCHIVE/f'audio/{sid}_native.wav')
        info=sf.info(wav);assert info.frames==s['samples'] and info.samplerate==24000
        assert info.duration<=21.5 and s['planned_frames']<=720
        m=next(r for r in mix if r['id']==sid);final=ROOT/f'audio/{sid}_final.m4a'
        assert sha(final)==m['sha256']==sha(ARCHIVE/f'audio/{sid}_final.m4a')
        rows.append(dict(id=sid,native_sha256=sha(wav),mix_sha256=sha(final),seconds=info.duration,samples=info.frames))
    save(ROOT/'records/audio_reuse.json',dict(previous_stop='30f49cbb',request_commit='7ede2457',unchanged=True,files=rows))
    print('VERIFIED unchanged native WAV and mixed AAC: 3 each',flush=True)

def crop_evidence():
    guard()
    geometry=json.loads((ROOT/'records/crop_preflight.json').read_text())
    for key,r in geometry['regions'].items():
        box=r['requested_box'];im=Image.open(r['source']).convert('RGB')
        crop=im.crop(box);crop.thumbnail((1280,1280));crop.save(ROOT/f'review/{key}_requested_crop.jpg',quality=90)
        ImageDraw.Draw(im).rectangle(box,outline='#ff3838',width=10)
        im.thumbnail((1280,1280));im.save(ROOT/f'review/{key}_requested_boundary.jpg',quality=90)

def pronunciation():
    """Pair actual main-film sentences with actual short excerpts; no resynthesis."""
    guard()
    from kokoro_onnx.tokenizer import Tokenizer
    tokenizer=Tokenizer()
    main=json.loads((MAIN/'records/narration_segments_en.json').read_text())
    cues={c['id']:c for s in main['segments'] for c in s['cues']}
    shorts={s['id']:s for s in json.loads((ROOT/'records/shorts.json').read_text())['shorts']}
    specs=[('Leutze','P07-01','V2'),('Düsseldorf','P07-03','V2'),
           ('Whittredge','P09-02','V3'),('Houdon','P09-03','V3')]
    rows=[];out=ROOT/'audio/pronunciation_comparisons';out.mkdir(exist_ok=True)
    for name,cid,sid in specs:
        cue=cues[cid];s=shorts[sid]
        sentence=next(t for t in re.split(r'(?<=[.!?])\s+',s['text']) if name in t)
        words=s['text'].split();parts=sentence.split()
        start=next(i for i in range(len(words)) if words[i:i+len(parts)]==parts)
        end=start+len(parts)-1
        a=max(0,s['words_timed'][start]['start']-.15)
        b=min(s['native_audio_duration'],s['words_timed'][end]['end']+.2)
        mainpath=MAIN/cue['audio_file'];assert sha(mainpath)==cue['audio_sha256']
        mainaudio,sr=sf.read(mainpath,dtype='float32');shortaudio,ssr=sf.read(ROOT/f'audio/{sid}_native.wav',dtype='float32');assert sr==ssr==24000
        pair=np.concatenate([mainaudio,np.zeros(24000,dtype='float32'),shortaudio[round(a*sr):round(b*sr)]])
        path=out/f'{name}_main_then_{sid}.wav';sf.write(path,pair,sr,subtype='PCM_16')
        ph=tokenizer.phonemize(name,'en-us')
        mainph=tokenizer.phonemize(cue['spoken_text'],'en-us')
        shortph=json.loads((ROOT/f'audio/{sid}_native.json').read_text())['phonemes']
        clean=lambda v:re.sub(r'[\sˈˌː.,;:!?—-]','',v)
        assert clean(ph) in clean(mainph) and clean(ph) in clean(shortph),(name,ph)
        rows.append(dict(name=name,main_sentence_id=cid,main_sentence_text=cue['text'],main_file=str(mainpath),main_sha256=sha(mainpath),
                         short_id=sid,short_sentence_text=sentence,short_excerpt_seconds=[a,b],phonemes=ph,
                         same_phoneme_sequence=True,same_voice='af_heart',same_speed=.82,
                         output=str(path),sha256=sha(path),order='Original main-film sentence, 1 second silence, original short sentence excerpt',
                         timing_method='Native short word alignment; main sentence retained in full to avoid cutting a name',human_auditory_review_completed=False))
    save(ROOT/'records/pronunciation_comparisons.json',dict(no_resynthesis=True,checks=rows,human_auditory_review_completed=False))
    print('Created 4 main/short pronunciation comparisons; phoneme sequences match',flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
