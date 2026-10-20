"""Generate local VOICEVOX narration, with one file per complete sentence."""
import json
import re
import math
import wave
import hashlib
from pathlib import Path
import os
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile

ROOT = Path(os.environ['WOM_EPISODE_ROOT']).expanduser().resolve()
RUNTIME = Path('/private/tmp/wom_voicevox_core')
CONTENT = json.loads((ROOT/'records/content.json').read_text())
ort = Onnxruntime.load_once(filename=str(next((RUNTIME/'onnxruntime/lib').glob('*.dylib'))))
synth = Synthesizer(ort, OpenJtalk(str(RUNTIME/'dict/open_jtalk_dic_utf_8-1.11')),
                    acceleration_mode='CPU', cpu_num_threads=2)
with VoiceModelFile.open(str(RUNTIME/'models/vvms/12.vvm')) as model:
    synth.load_voice_model(model)

def spoken_text(text):
    for a,b in {
      '七・七':'ななてんなな', 'エーアイ':'エーアイ',
      'ナクトアメン':'ナクトアメン', 'アメンエムハト一世':'アメンエムハト、いっせい',
      '紀元前千五十年頃':'きげんぜん、せんごじゅうねんごろ',
      '紀元前二千年頃':'きげんぜん、にせんねんごろ',
      '死者の書':'ししゃのしょ', '棺材':'かんざい', '秤量':'ひょうりょう',
      '祭具':'さいぐ', 'アンク':'アンク', 'ナウニ':'ナウニ',
      '紀元前千九百八十年頃':'きげんぜん、せんきゅうひゃくはちじゅうねんごろ',
      '二〇一九年':'にせんじゅうきゅうねん', '銅合金':'どうごうきん',
      '何柱':'なんはしら', 'AI':'エーアイ'
    }.items(): text = text.replace(a,b)
    return text

sr=24000
all_frames=[]
timeline=[]
current=0
gap_frames=round(0.16*sr)
for seg in CONTENT['segments']:
    start=current
    sentences=re.findall(r'[^。！？]+[。！？]?',seg['text'])
    cues=[]
    for j,text in enumerate(sentences,1):
        spoken=spoken_text(text)
        config={'style_id':52,'speed_scale':1.03,'intonation_scale':0.88,
                'pre_phoneme_length':0.08,'post_phoneme_length':0.17,
                'output_sampling_rate':sr,'spoken_text':spoken}
        key=hashlib.sha256(json.dumps(config,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
        path=ROOT/'audio/segments'/f'{seg["id"]}_{j:02d}_{key[:8]}.wav'
        qpath=path.with_suffix('.json')
        if not path.exists():
            q=synth.create_audio_query(spoken,52)
            q.speed_scale=1.03
            q.intonation_scale=0.88
            q.pre_phoneme_length=0.08
            q.post_phoneme_length=0.17
            q.output_sampling_rate=sr
            path.write_bytes(synth.synthesis(q,52))
            qpath.write_text(json.dumps(config,ensure_ascii=False,indent=2))
        with wave.open(str(path),'rb') as wav:
            assert wav.getframerate()==sr and wav.getnchannels()==1 and wav.getsampwidth()==2
            frames=wav.readframes(wav.getnframes())
            n=len(frames)//2
        cue={'id':f'{seg["id"]}-{j:02d}','text':text,'spoken_text':spoken,
             'start':current/sr,'end':(current+n)/sr,
             'audio_file':str(path.relative_to(ROOT)), 'input_hash':key}
        cues.append(cue)
        all_frames.extend([frames,b'\0\0'*gap_frames]); current += n+gap_frames
    # Deliberate thinking pause between sections; no timed text during the pause.
    gap=0.8 if not timeline or timeline[-1]['chapter']!=seg['chapter'] else 0.35
    n=round(gap*sr); all_frames.append(b'\0\0'*n); current+=n
    timeline.append({**seg,'start':start/sr,'end':current/sr,'cues':cues})
    print(seg['id'],f'{start/sr:.2f} → {current/sr:.2f}',flush=True)

# Give the end card time to breathe.
tail=round(5*sr);all_frames.append(b'\0\0'*tail);current+=tail
out=ROOT/'audio/narration.wav'
with wave.open(str(out),'wb') as wav:
    wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sr)
    for frames in all_frames: wav.writeframesraw(frames)
record={'sample_rate':sr,'duration_seconds':current/sr,'voice':'VOICEVOX:雀松朱司',
        'style_id':52,'core_version':'0.17.0','model_version':'0.16.4',
        'runtime_version':'1.17.3','sentence_boundary_timing':True,
        'human_auditory_review_completed':False,'segments':timeline}
(ROOT/'records/narration_timeline.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
print('TOTAL',current/sr,'seconds',out,flush=True)
