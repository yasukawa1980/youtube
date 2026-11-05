"""EP012 v02: keep each approved voice segment bit-exact on an independent timeline."""
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

from wom01_subtitles import to_srt
from wom12_produce import ROOT, SR, read, save, sha

BASE = Path('/Volumes/ESD-02/新チャンネル/EP012_SantaClaus')
OLD = BASE / '確認版_v01_20261105'
NEW = BASE / '確認版_v02_20261105'
JA = dict(zip(
    ['fourth century','ten eighty-seven','eighteen twelve','eighteen twenty-one','eighteen twenty-three','eighteen fifty-eight','eighteen sixty-three','eighteen eighty-one','eighteen sixty-four','nineteen oh two','nineteen oh four','nineteen thirty-one','many people believe','There is no sleigh here yet','Its first page begins','Its Saint Nicholas is chubby','He is dressed','He drives a miniature','His cheeks are like roses','Soon after','In eighteen eighty-one','So his coat','But red kept','In December','decades before'],
    ['4世紀','1087年','1812年','1821年','1823年','1858年','1863年','1881年','1864年','1902年','1904年','1931年','赤い服はそこから始まった','ここにはまだ','最初の頁は','詩の聖ニコラスは','頭から足まで','8頭の小さな','頬はばら','まもなく','1881年','上着の色は','けれど赤は','1902年12月','有名な清涼飲料']
))

def phrase_frame(lang, segment, word, speech, subs, events):
    target = JA[word] if lang == 'ja' else word
    clean = lambda text: re.sub(r'\s+', '', text.lower())
    cue = next(c for c in speech[segment]['cues'] if clean(target) in clean(c['text']))
    offset = clean(cue['text']).index(clean(target))
    for page in (p for p in subs if p['sentence_id'] == cue['id']):
        length = len(clean(page['text']))
        if offset < length:
            frame = round(30 * (page['start'] + offset / length * (page['end'] - page['start'])))
            events.append(dict(segment=segment, word=target, cue=cue['id'], subtitle=page['text'],
                               sentence=cue['text'], page_start=page['start'], page_end=page['end'],
                               frame=frame, time=frame/30))
            return frame
        offset -= length
    raise ValueError((lang, segment, word))

def build(lang):
    root = NEW / lang
    for folder in ['records', 'audio/'+lang, '_work/render', 'deliverables', 'review']:
        (root/folder).mkdir(parents=True, exist_ok=True)
    for filename in ['content.json', 'content_en.json']:
        (root/'records'/filename).write_bytes((OLD/'records'/filename).read_bytes())
    previous = read(OLD/f'records/narration_timeline_{lang}.json')['segments']
    original_subs = read(OLD/f'records/subtitle_cues_{lang}.json')['cues']
    oldtrack, sr = sf.read(OLD/f'audio/{lang}/narration.wav', dtype='int16')
    assert sr == SR
    pos = 54
    segments, subs, clips, gaps = [], [], [], []
    for s in previous:
        pcm, sr = sf.read(OLD/s['audio_file'], dtype='int16')
        start = pos / 30
        old_start = round(s['start'] * SR)
        assert sr == SR and np.array_equal(pcm, oldtrack[old_start:old_start+len(pcm)])
        end_voice = start + len(pcm)/SR
        hold = 1.5 if s['id'] in ['P09','P11'] else 0
        end = round(30*(end_voice + hold + .92))
        shift = start - s['start']
        cues = [dict(c, start=c['start']+shift, end=c['end']+shift) for c in s['cues']]
        segments.append(dict(s, start=start, speech_end=end_voice, end=end/30, cues=cues,
                             speech_seconds=len(pcm)/SR, source_sha256=sha(OLD/s['audio_file'])))
        clips.append((pos*800, pcm))
        subs.extend(dict(c, start=c['start']+shift, end=c['end']+shift) for c in original_subs
                    if c['sentence_id'].startswith(s['id']+'-'))
        gaps.append(dict(id=s['id'],speech_end=end_voice,following_boundary=end/30,
                         gap=end/30-end_voice,card_hold=hold))
        assert abs(gaps[-1]['gap']-hold-.92)<.1
        pos=end
        if s['id']=='P02':
            opening=[pos/30,pos/30+4]
            pos+=120
    endcard=[pos/30,pos/30+10]
    duration=endcard[1]
    track=np.zeros((pos+300)*800, dtype=np.int16)
    for offset, pcm in clips:
        track[offset:offset+len(pcm)]=pcm
    path=root/f'audio/{lang}/narration.wav'
    sf.write(path,track,SR,subtype='PCM_16')
    proc=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','silencedetect=n=-45dB:d=2','-f','null','-'],capture_output=True,text=True,check=True)
    starts=re.findall(r'silence_start: ([\d.]+)',proc.stderr)
    ends=re.findall(r'silence_end: ([\d.]+)',proc.stderr)
    assert len(starts)==len(ends)
    permitted=[('opening',*opening),('endcard',*endcard)]+[(g['id'],g['speech_end'],g['following_boundary']) for g in gaps if g['card_hold']]
    silence=[]
    for a,b in zip(map(float,starts),map(float,ends)):
        key=next((k for k,x,y in permitted if max(x,a)<min(y,b)),None)
        silence.append(dict(start=a,end=b,duration=b-a,reason=key))
    save(root/'records/voice_gaps.json',dict(gaps=gaps,silence=silence,opening=opening,endcard=endcard))
    assert all(x['reason'] for x in silence),silence
    for i,g in enumerate(gaps):
        g['next_voice_start']=segments[i+1]['start'] if i+1<len(segments) else None
        g['to_next_voice']=g['next_voice_start']-g['speech_end'] if g['next_voice_start'] is not None else None
    save(root/'records/voice_gaps.json',dict(gaps=gaps,silence=silence,opening=opening,endcard=endcard))
    master=dict(segments=segments,duration_seconds=duration,brand_intervals=dict(opening=opening,endcard=endcard))
    save(root/'records/master_timeline.json',master)
    save(root/f'records/narration_timeline_{lang}.json',master)
    save(root/f'records/subtitle_cues_{lang}.json',dict(cues=subs))
    script=read(root/'records'/('content_en.json' if lang=='en' else 'content.json'))
    clean=lambda text:re.sub(r'\s+','',text)
    assert clean(''.join(c['text'] for c in subs))==clean(''.join(s['text'] for s in script['segments']))
    srt=to_srt(subs)
    (root/f'deliverables/EP012_SantaClaus_{lang}_v02_1080p30.srt').write_text(srt)
    print(lang, duration, gaps[0],silence,flush=True)

if __name__=='__main__':
    for language in ['en','ja']:
        build(language)
