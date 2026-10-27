"""EP006 Shorts: exact requested scripts, main-film readings, native duration gate.

Run narration before picture production. Never rewrite or accelerate a failed read.
"""
import dataclasses
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parent.parent
REQUEST = REPO / 'new-channel/wom_ショート制作依頼_EP006_20261027.md'
ROOT = Path('/Users/ryo/Desktop/新チャンネル/ショート/EP006_確認版_v01_20261027')
READINGS = Path('/Users/ryo/Desktop/新チャンネル/EP006_Sphinx/確認版_v02_20261027/records/reading_replacements.json')
MODELS = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
SR = 24000


def sha(path):
    return hashlib.file_digest(Path(path).open('rb'), 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def narration():
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    from importlib.metadata import version
    ort.disable_telemetry_events()
    assert version('kokoro-onnx') == '0.6.1'
    assert version('onnxruntime') == '1.31.0'
    opt = ort.SessionOptions()
    opt.intra_op_num_threads = 4
    opt.inter_op_num_threads = 1
    tts = Kokoro.from_session(ort.InferenceSession(
        str(MODELS / 'kokoro-v1.0.onnx'), opt,
        providers=['CPUExecutionProvider']), str(MODELS / 'voices-v1.0.bin'))
    for folder in ['audio', 'records', 'review', 'deliverables', '_work']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    readings = json.loads(READINGS.read_text())
    (ROOT / 'records/reading_replacements.json').write_bytes(READINGS.read_bytes())
    english = [r for r in readings if r['language'] == 'en']
    phoneme_map = {r['display']: r['phonemes'] for r in english if 'phonemes' in r}
    replacements = {r['display']: r['spoken'] for r in english}
    items = re.findall(r'^### (S[123]) — (.+)\n\n> (.+)$', REQUEST.read_text(), re.M)
    assert len(items) == 3
    rows = []
    for sid, title, text in items:
        speech = text
        for before, after in replacements.items():
            speech = speech.replace(before, after)
        # Same root-word splitting and phoneme joins as wom06_produce.narrate.
        parts = re.split('(' + '|'.join(re.escape(k) for k in phoneme_map) + ')', speech)
        phonemes = ' '.join(phoneme_map.get(part, tts.tokenizer.phonemize(part, 'en-us'))
                            for part in parts if part.strip())
        assert tts.tokenizer.known(phonemes) == phonemes
        config = dict(text=text, spoken_text=speech, phonemes=phonemes,
                      voice='af_heart', speed=.82, sentence_pause=.3,
                      clause_pause=.12, trim=True,
                      request_sha256=sha(REQUEST), reading_replacements_sha256=sha(READINGS),
                      model_sha256=sha(MODELS / 'kokoro-v1.0.onnx'),
                      voices_sha256=sha(MODELS / 'voices-v1.0.bin'),
                      versions={k: version(k) for k in ['kokoro-onnx', 'onnxruntime', 'numpy', 'phonemizer']})
        audio_path = ROOT / f'audio/{sid}_native.wav'
        stamp = audio_path.with_suffix('.json')
        timed = ROOT / f'records/{sid}_phoneme_timings.json'
        if audio_path.exists() and stamp.exists() and json.loads(stamp.read_text()) == config and timed.exists():
            audio, sr = sf.read(audio_path, dtype='float32')
        else:
            audio, sr, timings = tts.create_timed(
                phonemes, voice='af_heart', speed=.82, lang='en-us',
                is_phonemes=True, trim=True, sentence_pause=.3, clause_pause=.12)
            assert sr == SR
            sf.write(audio_path, audio, SR, subtype='PCM_16')
            save(stamp, config)
            save(timed, {'available': bool(timings), 'timings': [dataclasses.asdict(t) for t in timings]})
        assert sr == SR
        rms = np.array([np.sqrt(np.mean(audio[i:i+240] ** 2)) for i in range(0, len(audio), 240)])
        active = np.where(rms > 10 ** (-50 / 20))[0]
        assert len(active)
        row = dict(id=sid, title=title, text=text, words=len(text.split()),
                   audio_file=str(audio_path), audio_sha256=sha(audio_path),
                   native_audio_duration=len(audio)/SR,
                   voice_onset_seconds=int(active[0])*.01,
                   last_voice_activity_seconds=min(len(audio), (int(active[-1])+1)*240)/SR,
                   within_22_seconds=len(audio)/SR <= 22,
                   readings_applied=[r for r in english if r['display'] in text])
        rows.append(row)
        print(f"NATIVE {sid}: {row['native_audio_duration']:.6f}s; onset {row['voice_onset_seconds']:.2f}s", flush=True)
    passed = all(r['within_22_seconds'] for r in rows)
    save(ROOT / 'records/narration.json', dict(
        request_sha256=sha(REQUEST), reading_replacements_sha256=sha(READINGS),
        scripts=rows, all_within_22_seconds=passed, text_unchanged=True,
        speech_speed_modified_to_fit=False, human_full_listening=False,
        gate='Stop picture production and report if any native read exceeds 22 seconds.'))
    if not passed:
        raise SystemExit('STOP: Native narration exceeds 22 seconds; no rewriting, acceleration or picture production.')
    print('NARRATION DURATION GATE PASSED', flush=True)


if __name__ == '__main__':
    narration()
