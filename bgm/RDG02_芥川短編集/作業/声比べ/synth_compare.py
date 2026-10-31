"""声の聞き比べ：sentences.json を各候補の声で読み、音量を -20 LUFS にそろえて書き出す。

VOICEVOX（冥鳴ひまり）は voicevox_core、AivisSpeech は起動中のエンジン（localhost:10101）の
VOICEVOX互換API（audio_query → synthesis）を使う。
使い方: python synth_compare.py <出力フォルダ> [aivisのstyle_id:名前 ...]
"""
import io
import json
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
SR = 24000
GAP = 0.7
SPEED, INTONATION = 0.9, 0.9      # RDG01と同じ
LUFS = -20


def himari(texts):
    from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
    r = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/VOICEVOX_core_0.17.0_model_0.16.4')
    ort = Onnxruntime.load_once(filename=str(next((r / 'onnxruntime/lib').glob('*.dylib'))))
    synth = Synthesizer(ort, OpenJtalk(str(r / 'dict/open_jtalk_dic_utf_8-1.11')))
    with VoiceModelFile.open(str(r / 'models/vvms/1.vvm')) as m:
        synth.load_voice_model(m)
    for t in texts:
        q = synth.create_audio_query(t, 14)
        q.speed_scale, q.intonation_scale = SPEED, INTONATION
        q.output_sampling_rate = SR
        yield synth.synthesis(q, 14)


def aivis(style):
    def gen(texts):
        base = 'http://127.0.0.1:10101'
        for t in texts:
            qs = urllib.parse.urlencode({'text': t, 'speaker': style})
            req = urllib.request.Request(f'{base}/audio_query?{qs}', method='POST')
            q = json.load(urllib.request.urlopen(req))
            q.update(speedScale=SPEED, outputSamplingRate=SR)
            req = urllib.request.Request(f'{base}/synthesis?speaker={style}', method='POST',
                                         data=json.dumps(q).encode(),
                                         headers={'Content-Type': 'application/json'})
            yield urllib.request.urlopen(req).read()
    return gen


def render(gen, texts, out):
    parts = []
    for wav in gen(texts):
        a, sr = sf.read(io.BytesIO(wav), dtype='float32')
        assert sr == SR, sr
        parts += [a if a.ndim == 1 else a.mean(1), np.zeros(round(GAP * SR), 'float32')]
    raw = out.with_suffix('.raw.wav')
    sf.write(raw, np.concatenate([np.zeros(SR // 2, 'float32')] + parts), SR, subtype='PCM_16')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af',
                    f'loudnorm=I={LUFS}:TP=-2:LRA=11', '-ar', '48000', '-c:a', 'libmp3lame',
                    '-b:a', '192k', out], check=True)
    raw.unlink()


def main():
    dest = Path(sys.argv[1])
    dest.mkdir(parents=True, exist_ok=True)
    texts = json.loads((HERE / 'sentences.json').read_text())
    jobs = [('00_冥鳴ひまり_今の声', himari)]
    for i, arg in enumerate(sys.argv[2:], 1):
        style, name = arg.split(':', 1)
        jobs.append((f'{i:02d}_{name}', aivis(int(style))))
    for name, gen in jobs:
        render(gen, texts, dest / f'{name}.mp3')
        print('書き出し', name)


if __name__ == '__main__':
    main()
