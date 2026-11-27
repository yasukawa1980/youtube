"""Time the approved EP016 shots to each language's own native narration."""
import math
import sys
import subprocess
from wom16_voice import ROOT, content, read, save
import wom14_timeline
import wom14_music

CUTS = {
    'SR09-B':('So Odysseus','そこでオデュッセウス'),
    'SR09-C':('Homer speaks','ホメロスが語る'),
    'D_tl_voice':('He gives them','ホメロスが与えたのは'),
    'SR03-A':('They appear','絵付けの壺'),
    'SR11-A':('In the third','紀元前3世紀'),
    'SR03-B':('Greek artists also','ギリシャでは、'),
    'SR07-T':('And one medieval','そして、ある中世'),
}
def timeline(lang):
    wom14_timeline.ROOT = ROOT
    wom14_timeline.content = content
    wom14_timeline.build(lang, holds={'P12':1.5})
    dst=ROOT/lang
    (dst/f'deliverables/EP014_Oni_{lang}_v01_1080p30.srt').replace(dst/f'deliverables/EP016_Sirens_{lang}_v01_1080p30.srt')
    m=read(dst/'records/master_timeline.json')
    shots=[]; events=[]
    for i,seg in enumerate(m['segments']):
        keys=seg['visuals']
        starts=[0 if not i else round(seg['start']*30)]
        def cue(words):
            prefix=words[0 if lang=='en' else 1]
            c=next(c for c in seg['cues'] if c['text'].startswith(prefix))
            return round(c['start']*30),prefix
        for k in keys[1:]:
            if k in CUTS: f,label=cue(CUTS[k])
            else: f,label=math.ceil(seg['speech_end']*30),'語りの終了直後'
            starts.append(f)
            events.append(dict(key=k,frame=f,words=label,segment=seg['id']))
        for evt,prefix in {
                'P02':[('SR09-A_1',('Whoever hears','その歌を聞いた'))],
                'P06':[('SR12-A_1',('But they kept','けれど、娘の顔'))],
                'P08':[('SR05-A_1',('But they have','けれど、鱗'))],
        }.get(seg['id'],[]):
            f,label=cue(prefix)
            events.append(dict(key=evt,frame=f,words=label,segment=seg['id']))
        if seg['id']=='P12':
            f,label=cue(('For centuries after that','そのあとも何世紀'))
            events.append(dict(key='summary',frame=f,words=label,segment='P12'))
        for k,a,b in zip(keys,starts,starts[1:]+[round(seg['end']*30)]):
            shots.append(dict(key=k,segment=seg['id'],start=a,end=b))
        brand={'P02':'opening','P14':'endcard'}.get(seg['id'])
        if brand:
            a,b=[round(v*30) for v in m['brand_intervals'][brand]]
            shots.append(dict(key=brand,segment=brand,start=a,end=b))
    assert all(a['end']==b['start'] for a,b in zip(shots,shots[1:]))
    assert all(x['end']-x['start']>=27 for x in shots)
    save(dst/'records/shot_plan.json',shots);save(dst/'records/phrase_events.json',events)

def audio(lang):
    dst=ROOT/lang;wom14_music.ROOT=dst;wom14_music.LANGUAGES=[lang]
    def ff_audio(args):
        command=['ffmpeg','-nostdin','-y','-v','error','-threads','2','-filter_threads','2',*map(str,args[:-1]),'-threads','2',str(args[-1])]
        return subprocess.run(command,check=True,capture_output=True)
    wom14_music.ff=ff_audio
    wom14_music.build_audio()
    for ext in ('wav','m4a'):
        p=dst/f'deliverables/EP014_audio_{lang}.{ext}';p.replace(p.with_name(p.name.replace('014','016')))
if __name__=='__main__':
    for lang in ('en','ja'):
        (timeline if sys.argv[1]=='timeline' else audio)(lang)
