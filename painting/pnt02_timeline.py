"""Independent English/Japanese PNT02 timelines, preserving native voice samples."""
import math,re,shutil
from pathlib import Path
import numpy as np
import soundfile as sf
from pnt02_produce import ROOT,SR,FPS,read,save,content,sha
from wom01_subtitles import pages,to_srt

def build(lang):
    dst=ROOT/lang
    for folder in ['records','audio/'+lang,'_work/render','review','deliverables']:(dst/folder).mkdir(parents=True,exist_ok=True)
    for name in ['content.json','content_en.json']:shutil.copy2(ROOT/'records'/name,dst/'records'/name)
    native=read(ROOT/f'records/narration_segments_{lang}.json')['segments']
    pos=54;clips=[];segments=[];subs=[];gaps=[]
    for s in native:
        pcm,sr=sf.read(ROOT/s['audio_file'],dtype='int16');assert sr==SR
        start=pos/FPS;speech_end=start+len(pcm)/SR;end=round((speech_end+.92)*FPS)
        cues=[dict(c,start=c['start']+start,end=c['end']+start) for c in s['cues']]
        segments.append(dict(s,start=start,speech_end=speech_end,end=end/FPS,cues=cues,source_sha256=sha(ROOT/s['audio_file'])))
        clips.append((pos*800,pcm));gaps.append(dict(segment=s['id'],speech_end=speech_end,boundary=end/FPS,gap=end/FPS-speech_end))
        for c in cues:
            chunks=pages(c['text'],lang);weights=np.array([len(x.replace('\n','')) for x in chunks],float);span=c['end']-c['start'];duration=span*weights/weights.sum()
            if len(chunks)>1:
                assert span>=1.4*len(chunks),(lang,c)
                fixed=np.zeros(len(chunks),bool)
                while np.any(duration<1.4-1e-9):
                    fixed|=duration<1.4;duration[fixed]=1.4;duration[~fixed]=(span-1.4*fixed.sum())*weights[~fixed]/weights[~fixed].sum()
            cursor=c['start']
            for k,chunk in enumerate(chunks):
                stop=c['end'] if k==len(chunks)-1 else cursor+duration[k]
                subs.append(dict(sentence_id=c['id'],start=cursor,end=float(stop),text=chunk));cursor=stop
        pos=end
        if s['id']=='P02':opening=[pos/FPS,pos/FPS+4];pos+=120
    endcard=[pos/FPS,pos/FPS+10];duration=endcard[1]
    for i,c in enumerate(subs):
        if c['end']-c['start']<1.4:
            cap=subs[i+1]['start']-.01 if i+1<len(subs) else endcard[0]-.05
            assert c['start']+1.4<=cap,(lang,c);c['end']=c['start']+1.4
    clean=lambda t:re.sub(r'\s+','',t)
    assert clean(''.join(x['text'] for x in subs))==clean(''.join(s['text'] for s in content(lang)['segments']))
    assert all(len(s['text'].splitlines())<=2 and max(map(len,s['text'].splitlines()))<=(42 if lang=='en' else 23) for s in subs)
    assert all(a['end']<=b['start'] for a,b in zip(subs,subs[1:]))
    track=np.zeros((pos+300)*800,dtype=np.int16)
    for n,a in clips:track[n:n+len(a)]=a
    sf.write(dst/f'audio/{lang}/narration.wav',track,SR,subtype='PCM_16')
    master=dict(language=lang,segments=segments,duration_seconds=duration,fps=30,brand_intervals=dict(opening=opening,endcard=endcard))
    save(dst/'records/master_timeline.json',master);save(dst/f'records/narration_timeline_{lang}.json',master)
    save(dst/f'records/subtitle_cues_{lang}.json',dict(cues=subs,count=len(subs),timing='native sentence boundaries, weighted pages with minimum1.4s'))
    save(dst/'records/subtitle_validation.json',dict(script_matches=True,min_seconds=min(c['end']-c['start'] for c in subs),max_line=max(len(x) for c in subs for x in c['text'].splitlines()),count=len(subs)))
    save(dst/'records/voice_gaps.json',dict(gaps=gaps,policy='0.92s between segments, except 4s brand opening; independent language timelines'))
    (dst/f'deliverables/PNT02_WashingtonCrossing_{lang}_v01_1080p30.srt').write_text(to_srt(subs))
    print(lang,duration,len(subs),flush=True)

if __name__=='__main__':
    for lang in ['en','ja']:build(lang)
