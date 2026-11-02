"""Approved old-short remakes: native narration and mandatory 24-second gate.

Uses the approved main-film Heart settings. Never accelerates or edits copy.
"""
import dataclasses
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parent
REQUEST = REPO / 'wom_ショート作り直し依頼_旧型5本_20261102.md'
ROOT = Path('/Volumes/ESD-02/新チャンネル/ショート/作り直し_v01_20261102')
MODELS = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
MEDIA = Path('/Users/ryo/Desktop/新チャンネル')

def sha(p):
    return hashlib.file_digest(Path(p).open('rb'), 'sha256').hexdigest()

def save(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def narration():
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    from importlib.metadata import version
    ort.disable_telemetry_events()
    assert ROOT.parents[2].is_dir(), 'Specified SSD is unavailable'
    for folder in ['audio', 'records', 'review', 'deliverables', '_work']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    opt = ort.SessionOptions()
    opt.intra_op_num_threads = 4
    opt.inter_op_num_threads = 1
    tts = Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'), opt,
        providers=['CPUExecutionProvider']), str(MODELS/'voices-v1.0.bin'))
    sources = {
        'M1R': MEDIA/'EP003_Medusa/確認版_v02_20261023/records/reading_replacements.json',
        'P1R': MEDIA/'EP004_Pandora/確認版_v01_20261023/records/reading_replacements.json',
        'T1R': MEDIA/'EP005_Tengu/確認版_v02_20261024/records/reading_replacements.json',
    }
    scripts = re.findall(r'^### (A1R|M1R|P1R|T1R|A3R) — (.+)\n\n見出し：\*\*(.+)\*\*\n\n> (.+)$', REQUEST.read_text(), re.M)
    assert len(scripts) == 5
    rows = []
    for sid, title, headline, text in scripts:
        readings = json.loads(sources[sid].read_text()) if sid in sources else []
        english = [r for r in readings if r['language'] == 'en']
        replacements = {r['display']: r['spoken'] for r in english}
        phoneme_map = {r['display']: r['phonemes'] for r in english if 'phonemes' in r}
        speech = text
        for before, after in replacements.items():
            speech = speech.replace(before, after)
        parts = re.split('('+'|'.join(map(re.escape, phoneme_map))+')', speech) if phoneme_map else [speech]
        phonemes = ' '.join(phoneme_map.get(p, tts.tokenizer.phonemize(p, 'en-us')) for p in parts if p.strip())
        assert tts.tokenizer.known(phonemes) == phonemes
        cfg = dict(text=text, spoken_text=speech, phonemes=phonemes, voice='af_heart', speed=.82,
                   sentence_pause=.3, clause_pause=.12, trim=True, request_sha256=sha(REQUEST),
                   model_sha256=sha(MODELS/'kokoro-v1.0.onnx'), voices_sha256=sha(MODELS/'voices-v1.0.bin'),
                   versions={p:version(p) for p in ['kokoro-onnx','onnxruntime','numpy']},
                   readings_source=str(sources.get(sid, REPO/'wom01_multilingual_narration.py')),
                   applied_readings=[r for r in english if r['display'] in text])
        p = ROOT/f'audio/{sid}_native.wav'
        stamp = p.with_suffix('.json')
        timing = ROOT/f'records/{sid}_phoneme_timings.json'
        if p.exists() and stamp.exists() and json.loads(stamp.read_text()) == cfg and timing.exists():
            a, sr = sf.read(p, dtype='float32')
        else:
            a, sr, times = tts.create_timed(phonemes, voice='af_heart', speed=.82, lang='en-us',
                is_phonemes=True, trim=True, sentence_pause=.3, clause_pause=.12)
            sf.write(p, a, sr, subtype='PCM_16')
            save(stamp, cfg)
            save(timing, dict(available=bool(times), timings=[dataclasses.asdict(t) for t in times]))
        assert sr == 24000
        rms = np.array([np.sqrt(np.mean(a[i:i+240]**2)) for i in range(0,len(a),240)])
        active = np.where(rms > 10**(-50/20))[0]
        duration = math.ceil((len(a)/sr+2.5)*30)/30
        row = dict(id=sid,title=title,headline=headline,text=text,words=len(text.split()),
                   audio_file=str(p),audio_sha256=sha(p),native_audio_duration=len(a)/sr,
                   voice_onset_seconds=int(active[0])*.01,
                   last_voice_activity_seconds=min(len(a),(int(active[-1])+1)*240)/sr,
                   final_duration_seconds=duration,within_24_seconds=duration<=24,
                   readings_applied=cfg['applied_readings'])
        rows.append(row)
        print(f'{sid}: voice={len(a)/sr:.6f}s CTA included={duration:.6f}s onset={row["voice_onset_seconds"]:.2f}s', flush=True)
    result = dict(request_sha256=sha(REQUEST), scripts=rows,all_within_24_seconds=all(r['within_24_seconds'] for r in rows),
                  text_unchanged=True,speech_speed_modified_to_fit=False,human_full_listening=False,
                  gate='24 seconds including 2.5-second CTA; stop picture production and report on failure')
    save(ROOT/'records/narration.json',result)
    if not result['all_within_24_seconds']:
        raise SystemExit('STOP: duration gate failed. No picture production, rewriting or acceleration.')

if __name__ == '__main__':
    narration()
