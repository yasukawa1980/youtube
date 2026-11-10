"""PNT02 shorts: validate approved crops and synthesize with the main film settings.

Stop immediately at a failed geometry/duration gate; never accelerate the voice.
Run with _work/qo-production-python/bin/python (cv2: _work/pnt02-deps).
"""
import dataclasses
import hashlib
import itertools
import json
import math
import re
import shutil
import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
import soundfile as sf

REPO = Path(__file__).resolve().parent.parent
ROOT = Path('/Volumes/ESD-02/新チャンネル/ショート/PNT02_v01_20261110')
MAIN = Path('/Volumes/ESD-02/新チャンネル/PNT02_WashingtonCrossing/確認版_v01_20261110')
MEDIA = MAIN.parent/'素材'
MODELS = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
REQUEST = 'painting/pnt02_ショート制作依頼_20261110.md'
REQUEST_COMMIT = 'd727ace9'
REGIONS = {
    'V1_flag': ('D2', 'DP245005.jpg', [1350, 430, 2581, 1513]),
    'V3_steering': ('D3', 'DP258218.jpg', [2483, 620, 3983, 1939]),
    'V3_Washington': ('D2', 'DP245005.jpg', [192, 1058, 1347, 2075]),
}


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def guard():
    assert Path('/Volumes/ESD-02').is_mount(), 'STOP: ESD-02未接続'


def prepare():
    guard()
    for name in ['records', 'audio']:
        (ROOT/name).mkdir(parents=True, exist_ok=True)
    request = subprocess.check_output(['git', 'show', f'{REQUEST_COMMIT}:{REQUEST}'], cwd=REPO)
    target = ROOT/'records/request.md'
    if target.exists() and target.read_bytes() != request:
        previous = subprocess.check_output(['git', 'show', f'c03a213d:{REQUEST}'], cwd=REPO)
        assert target.read_bytes() == previous, 'STOP: unexpected existing request'
        archive = ROOT/'history/74dfc631_initial_stop'
        manifest = []
        for folder in ['audio', 'records']:
            for old in sorted((ROOT/folder).glob('*')):
                if not old.is_file():
                    continue
                dest = archive/old.relative_to(ROOT)
                dest.parent.mkdir(parents=True, exist_ok=True)
                if dest.exists():
                    assert sha(dest) == sha(old)
                else:
                    shutil.copy2(old, dest)
                manifest.append(dict(path=str(old.relative_to(ROOT)), sha256=sha(dest), bytes=dest.stat().st_size))
        save(archive/'manifest.json', dict(previous_stop='74dfc631', files=manifest))
    target.write_bytes(request)


def geometry():
    import cv2
    from PIL import Image
    prepare()
    source = REPO/'painting/pnt02_確認版_v01_20261110/detail_registration.json'
    registration = json.loads(source.read_text())
    transforms = {r['id']: np.asarray(r['homography']) for r in registration['registration']}
    rows = {}
    polygons = {}
    for key, (detail, filename, box) in REGIONS.items():
        path = MEDIA/'Met_97.34'/filename
        with Image.open(path) as im:
            size = im.size
        l, t, r, b = box
        assert 0 <= l < r <= size[0] and 0 <= t < b <= size[1]
        scale = max(1080/(r-l), 950/(b-t))*1.04
        assert scale <= 1, 'STOP: 原寸超過'
        polygon = cv2.perspectiveTransform(np.asarray([[[l,t],[r,t],[r,b],[l,b]]], np.float32), transforms[detail])[0]
        polygons[key] = polygon
        rows[key] = dict(source=str(path), source_sha256=sha(path), native_size=size,
                         requested_box=box, max_scale_at_1_04_zoom=scale,
                         polygon_in_full_px=polygon.tolist())
    checks = []
    for a, b in itertools.combinations(polygons, 2):
        area, _ = cv2.intersectConvexConvex(polygons[a], polygons[b])
        checks.append(dict(a=a, b=b, intersection_area_full_px2=float(area), passed=area == 0))
    result = dict(passed=all(r['passed'] for r in checks), regions=rows, checks=checks,
                  method='Main film SIFT homographies; intersect complete allowed crop envelopes in DP-14511-001 coordinates. All inward zoom frames are subsets. V2 full view exempt.',
                  registration_sha256=sha(source), visual_review_completed=False)
    save(ROOT/'records/crop_preflight.json', result)
    print(json.dumps(result, ensure_ascii=False), flush=True)
    assert result['passed'], 'STOP: 範囲の重複'


def narration():
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    prepare()
    assert json.loads((ROOT/'records/crop_preflight.json').read_text())['passed']
    queries = json.loads((MAIN/'records/queries_en.json').read_text())
    assert all(q['config']['voice'] == 'af_heart' and q['config']['speed'] == .82
               and q['config']['sentence_pause'] == .3 and q['config']['clause_pause'] == .12
               and 'phonemes' not in q['config'] for q in queries)
    main_narration = json.loads((MAIN/'records/narration_segments_en.json').read_text())
    assert all(not c['replacements'] and c['text'] == c['spoken_text']
               for s in main_narration['segments'] for c in s['cues'])
    scripts = re.findall(r'^### (V[123]) — (.+)\n\n見出し：\*\*(.+)\*\*\n\n> (.+)$',
                         (ROOT/'records/request.md').read_text(), re.M)
    assert len(scripts) == 3
    ort.disable_telemetry_events()
    opt = ort.SessionOptions()
    opt.intra_op_num_threads = 2
    opt.inter_op_num_threads = 1
    tts = Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'), opt,
                             providers=['CPUExecutionProvider']), str(MODELS/'voices-v1.0.bin'))
    provenance = dict(request_commit=REQUEST_COMMIT, request_sha256=sha(ROOT/'records/request.md'),
                      main_queries_sha256=sha(MAIN/'records/queries_en.json'),
                      main_narration_sha256=sha(MAIN/'records/narration_segments_en.json'),
                      model_sha256=sha(MODELS/'kokoro-v1.0.onnx'), voices_sha256=sha(MODELS/'voices-v1.0.bin'),
                      versions={p: version(p) for p in ['kokoro-onnx', 'onnxruntime', 'numpy',
                                                       'phonemizer', 'espeakng-loader', 'soundfile']})
    rows = []
    for sid, title, headline, text in scripts:
        guard()
        phonemes = tts.tokenizer.phonemize(text, 'en-us')
        assert tts.tokenizer.known(phonemes) == phonemes
        cfg = dict(text=text, spoken_text=text, phonemes=phonemes, voice='af_heart', speed=.82,
                   sentence_pause=.3, clause_pause=.12, trim=True, applied_readings=[], **provenance)
        path = ROOT/f'audio/{sid}_native.wav'
        stamp = path.with_suffix('.json')
        timing = ROOT/f'records/{sid}_phoneme_timings.json'
        reuse = path.exists() and stamp.exists() and timing.exists() and json.loads(stamp.read_text()) == cfg
        if path.exists() and not reuse:
            archived = ROOT/'history/74dfc631_initial_stop'/path.relative_to(ROOT)
            assert archived.exists() and sha(archived) == sha(path), 'STOP: prior audio not archived'
        if reuse:
            audio, sr = sf.read(path, dtype='float32')
        else:
            audio, sr, times = tts.create_timed(phonemes, voice='af_heart', speed=.82, lang='en-us',
                        is_phonemes=True, trim=True, sentence_pause=.3, clause_pause=.12)
            sf.write(path, audio, sr, subtype='PCM_16')
            save(stamp, cfg)
            save(timing, {'timings': [dataclasses.asdict(t) for t in times]})
        assert sr == 24000
        energy = np.array([np.sqrt(np.mean(audio[i:i+240]**2)) for i in range(0, len(audio), 240)])
        active = np.where(energy > 10**(-50/20))[0]
        frames = math.ceil(len(audio)/sr*30) + 75
        row = dict(id=sid, title=title, headline=headline, text=text, whitespace_words=len(text.split()),
                   audio_file=str(path), audio_sha256=sha(path), samples=len(audio), sample_rate=sr,
                   native_audio_duration=len(audio)/sr, voice_onset_seconds=int(active[0])*.01,
                   last_voice_activity_seconds=min(len(audio), (int(active[-1])+1)*240)/sr,
                   cta_seconds=2.5, planned_frames=frames, planned_duration_seconds=frames/30,
                   within_21_5_seconds=len(audio)/sr <= 21.5,
                   within_24_seconds=frames <= 720)
        rows.append(row)
        result = dict(**provenance, scripts=rows, completed_count=len(rows), requested_count=3,
                      text_unchanged=True, speech_speed_modified_to_fit=False, human_full_listening=False,
                      all_within_24_seconds=len(rows) == 3 and all(r['within_24_seconds'] for r in rows),
                      gate='Same as EP013: ceil(native audio seconds * 30) + 75 CTA frames. Stop immediately above 720 frames.')
        save(ROOT/'records/narration.json', result)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        if not row['within_24_seconds'] or not row['within_21_5_seconds']:
            raise SystemExit('STOP: 24秒上限超過。後続の音声・映像制作は行わない。')


if __name__ == '__main__':
    {'geometry': geometry, 'narration': narration}[sys.argv[1]]()
