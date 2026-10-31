"""sentences.json から朗読の音声（narration.wav）と字幕（narration.srt）を作る。

文ごとに合成してキャッシュする。読みや設定を変えた文だけ作り直される。
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile

HERE = Path(__file__).resolve().parent
R = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/VOICEVOX_core_0.17.0_model_0.16.4')
CACHE = HERE / 'cache'
SR = 24000
STYLE = 14            # 冥鳴ひまり ノーマル
VOICE = dict(speed_scale=0.9, intonation_scale=0.9, pitch_scale=0.0,
             pre_phoneme_length=0.1, post_phoneme_length=0.1)
GAP = dict(short=0.35, sentence=0.7, para=1.6, after_title=2.5, before_title=8.0,
           lead_in=1.5, after_opening=3.0, tail=20.0)
OPENING = ('なつめそうせき、ゆめじゅうや。', '夏目漱石『夢十夜』')

CACHE.mkdir(exist_ok=True)
ort = Onnxruntime.load_once(filename=str(next((R / 'onnxruntime/lib').glob('*.dylib'))))
synth = Synthesizer(ort, OpenJtalk(str(R / 'dict/open_jtalk_dic_utf_8-1.11')))
with VoiceModelFile.open(str(R / 'models/vvms/1.vvm')) as m:
    synth.load_voice_model(m)


def say(text):
    key = hashlib.sha256(json.dumps([text, STYLE, VOICE], ensure_ascii=False).encode()).hexdigest()[:16]
    path = CACHE / f'{key}.wav'
    if not path.exists():
        q = synth.create_audio_query(text, STYLE)
        for k, v in VOICE.items():
            setattr(q, k, v)
        q.output_sampling_rate = SR
        path.write_bytes(synth.synthesis(q, STYLE))
    audio, sr = sf.read(path, dtype='float32')
    assert sr == SR
    return audio


def ts(t):
    ms = round(t * 1000)
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


def main():
    items = json.loads((HERE / 'sentences.json').read_text())
    chunks, cues, t = [], [], 0.0

    def pad(sec):
        nonlocal t
        chunks.append(np.zeros(round(sec * SR), dtype='float32'))
        t += sec

    def add(spoken, shown):
        nonlocal t
        a = say(spoken)
        cues.append((t, t + len(a) / SR, shown))
        chunks.append(a)
        t += len(a) / SR

    pad(GAP['lead_in'])
    add(*OPENING)
    pad(GAP['after_opening'])
    chapters = []
    for i, o in enumerate(items):
        if o['kind'] == 'title':
            if i:
                pad(GAP['before_title'])
            chapters.append((t, o['display']))
            add(o['spoken'], o['display'])
            pad(GAP['after_title'])
            continue
        sents = list(zip(o['sentences'], o['display_sentences']))
        for j, (spk, shown) in enumerate(sents):
            add(spk, shown)
            if j + 1 < len(sents):
                pad(GAP['short'] if sents[j + 1][0].startswith('と') else GAP['sentence'])
        nxt = items[i + 1] if i + 1 < len(items) else None
        if nxt and nxt['kind'] == 'para':
            pad(GAP['para'])
    pad(GAP['tail'])

    audio = np.concatenate(chunks)
    sf.write(HERE / 'narration.wav', audio, SR, subtype='PCM_16')
    (HERE / 'narration.srt').write_text('\n'.join(
        f'{n}\n{ts(a)} --> {ts(b)}\n{text}\n' for n, (a, b, text) in enumerate(cues, 1)))
    (HERE / 'chapters.json').write_text(json.dumps(chapters, ensure_ascii=False))
    print(f'長さ {t / 60:.1f}分・字幕 {len(cues)}')
    for c, name in chapters:
        print(f'{int(c // 60)}:{int(c % 60):02d} {name}')


if __name__ == '__main__':
    main()
