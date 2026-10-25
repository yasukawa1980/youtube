"""音楽候補の全編自動検査。聴感や楽器の正確な同定の合格宣言はしない。"""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np


def decode(path, rate=16000, channels=1):
    return np.frombuffer(subprocess.check_output([
        'ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-ar', str(rate),
        '-ac', str(channels), '-f', 'f32le', '-']), '<f4')


def runs(mask, step):
    padded = np.r_[False, mask, False].astype(np.int8)
    starts = np.flatnonzero(np.diff(padded) == 1)
    ends = np.flatnonzero(np.diff(padded) == -1)
    return [{'start': round(float(s * step), 3), 'end': round(float(e * step), 3)}
            for s, e in zip(starts, ends)]


def acoustic(path):
    y = decode(path)
    frames = y[:len(y) // 4000 * 4000].reshape(-1, 4000)
    db = 20 * np.log10(np.sqrt(np.mean(frames ** 2, axis=1)) + 1e-12)
    active = np.flatnonzero(db > -60)
    if not active.size:
        raise ValueError(f'音楽が検出できません: {path}')
    dur = len(y) / 16000
    head = max(0., active[0] * .25 - .15)
    tail = min(dur, (active[-1] + 1) * .25 + .3)
    gaps = [r for r in runs(db < -50, .25)
            if r['end'] - r['start'] >= 1.5 and r['start'] > 3 and r['end'] < dur - 3]
    lu = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path),
                         '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                        capture_output=True, text=True, check=True).stderr
    lufs = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', lu)[-1])
    tp = float(re.findall(r'Peak:\s+(-?[\d.]+)', lu)[-1])
    hi = decode(path, 48000)
    n = 4096
    f = np.fft.rfftfreq(n, 1 / 48000)
    energy = np.zeros(n // 2 + 1)
    for i in range(0, len(hi) - n + 1, n):
        energy += np.abs(np.fft.rfft(hi[i:i + n] * np.hanning(n))) ** 2
    return y, {'duration': dur, 'trim_head': round(head, 3), 'trim_tail': round(tail, 3),
               'usable_seconds': round(tail - head, 3), 'inner_silences_lt50db': gaps,
               'last_second_rms_db': round(float(20 * np.log10(np.sqrt(np.mean(y[-16000:] ** 2)) + 1e-12)), 3),
               'rms_90_10_db': round(float(np.percentile(db[12:-12], 90) - np.percentile(db[12:-12], 10)), 3),
               'lufs': lufs, 'true_peak_dbtp': tp,
               'energy_above_8khz_fraction': round(float(energy[f >= 8000].sum() / max(energy.sum(), 1e-20)), 6)}


def main():
    import torch
    from transformers import ASTFeatureExtractor, ASTForAudioClassification
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('files', type=Path, nargs='+')
    args = parser.parse_args()
    torch.set_num_threads(2)
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    extractor = ASTFeatureExtractor.from_pretrained(args.model, local_files_only=True)
    model = ASTForAudioClassification.from_pretrained(args.model, local_files_only=True,
                                                     attn_implementation='sdpa').to(device).eval()
    labels = model.config.id2label
    voice_terms = ('speech', 'singing', 'choir', 'chant', 'humming', 'whisper', 'conversation',
                   'narration', 'rapping', 'vocal', 'babbl', 'shout', 'scream')
    voice = [i for i, label in labels.items() if any(t in label.lower() for t in voice_terms)
             and label not in ('Singing bowl', 'Whale vocalization')]
    report = json.loads(args.report.read_text()) if args.report.exists() else {
        'method': 'Local AST AudioSet; 10-second windows / 5-second stride including final samples',
        'limitation': '自動スクリーニング。人声の完全な不在・楽器の同定・聴感を保証しない。直接試聴未実施。',
        'files': {}}
    for path in args.files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        old = report['files'].get(path.stem)
        if old and old.get('file_sha256') == digest:
            print(path.stem, 'cache', flush=True); continue
        y, row = acoustic(path)
        starts = list(range(0, max(1, len(y) - 160000 + 1), 80000))
        final = max(0, len(y) - 160000)
        if starts[-1] != final:
            starts.append(final)
        probs = []
        for i in range(0, len(starts), 6):
            chunks = [np.pad(y[s:s + 160000], (0, max(0, 160000 - len(y[s:s + 160000]))))
                      for s in starts[i:i + 6]]
            inputs = extractor(chunks, sampling_rate=16000, return_tensors='pt').to(device)
            with torch.inference_mode():
                probs.append(model(**inputs).logits.sigmoid().cpu().numpy())
        p = np.concatenate(probs)
        means = p.mean(axis=0)
        top = np.argsort(means)[-12:][::-1]
        vi = np.unravel_index(np.argmax(p[:, voice]), p[:, voice].shape)
        row.update(file=str(path.resolve()), file_sha256=digest,
                   voice_max=round(float(p[:, voice].max()), 6),
                   voice_peak_label=labels[voice[vi[1]]], voice_peak_seconds=starts[vi[0]] / 16000,
                   class_mean_top={labels[int(i)]: round(float(means[i]), 6) for i in top},
                   windows=[{'seconds': s / 16000, 'voice_max': round(float(scores[voice].max()), 6),
                             'top': {labels[int(k)]: round(float(scores[k]), 5)
                                     for k in np.argsort(scores)[-5:][::-1]}}
                            for s, scores in zip(starts, p)],
                   direct_listening='not_performed', screening_device=device)
        row['flags'] = []
        if row['voice_max'] >= .15:
            row['flags'].append('voice_score_ge_0.15_requires_review')
        if row['inner_silences_lt50db']:
            row['flags'].append('internal_silence_requires_review')
        if row['last_second_rms_db'] > -38:
            row['flags'].append('nonquiet_tail_terminal_slot_only')
        report['files'][path.stem] = row
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
        print(path.stem, {k: row[k] for k in ('duration', 'usable_seconds', 'voice_max', 'lufs', 'flags')}, flush=True)


if __name__ == '__main__':
    main()
