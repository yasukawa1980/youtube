"""Step 1 only: three local English voices for N01-N04, in a shared 90s timeline."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

VOICES = [
    {"choice": "A", "voice": "am_michael", "language": "en-us", "label": "Michael / US English / male"},
    {"choice": "B", "voice": "af_heart", "language": "en-us", "label": "Heart / US English / female"},
    {"choice": "C", "voice": "bm_george", "language": "en-gb", "label": "George / British English / male"},
]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--script", type=Path, required=True)
    p.add_argument("--models", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    out = args.output
    (out / "_work").mkdir(parents=True, exist_ok=True)
    data = json.loads(args.script.read_text())
    segs = data["segments"][:4]
    assert [s["id"] for s in segs] == ["N01", "N02", "N03", "N04"]
    counts = [len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", s["text"])) for s in segs]
    sr, total = 24000, 90.0
    durations = [83 * n / sum(counts) for n in counts]
    starts, pos = [], 1.5
    for dur, gap in zip(durations, [0.5, 0.5, 1.8, 2.7]):
        starts.append(pos)
        pos += dur + gap
    assert abs(pos - total) < 1e-6
    ort.disable_telemetry_events()
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    tts = Kokoro.from_session(
        ort.InferenceSession(str(args.models / "kokoro-v1.0.onnx"), options,
                             providers=["CPUExecutionProvider"]),
        str(args.models / "voices-v1.0.bin"),
    )
    report = {
        "scope": "Step 1 only; voice choice pending; no full-episode production",
        "script_sha256": sha(args.script),
        "model_sha256": sha(args.models / "kokoro-v1.0.onnx"),
        "voices_sha256": sha(args.models / "voices-v1.0.bin"),
        "duration_seconds": total,
        "word_count": sum(counts),
        "scheduled_narration_seconds": 83,
        "words_per_minute_including_internal_pauses": sum(counts) * 60 / 83,
        "initial_music_seconds": 1.5,
        "chapter_C02_music_seconds": 1.8,
        "ending_music_seconds": 2.7,
        "segments": [
            {**s, "word_count": n, "start": start, "end": start+dur}
            for s, n, start, dur in zip(segs, counts, starts, durations)
        ],
        "voices": [],
        "human_listening": "pending",
    }
    for voice in VOICES:
        print(f"Generating {voice['choice']}: {voice['label']}", flush=True)
        track = np.zeros(round(total * sr), np.float32)
        results = []
        for seg, start, target in zip(segs, starts, durations):
            basename = f"{voice['choice']}_{voice['voice']}_{seg['id']}"
            cache = out / "_work" / f"{basename}.json"
            final = out / "_work" / f"{basename}_timed.wav"
            key = hashlib.sha256(json.dumps({
                "text": seg["text"], "voice": voice, "target": target,
                "model": report["model_sha256"], "engine": "kokoro-onnx 0.6.1",
            }, sort_keys=True).encode()).hexdigest()
            if cache.exists() and final.exists() and json.loads(cache.read_text()).get("key") == key:
                meta = json.loads(cache.read_text())
                audio, _ = sf.read(final, dtype="float32")
            else:
                speed, attempts = 0.82, []
                lower, upper, best = None, None, None
                for attempt in range(5):
                    audio, rate = tts.create(
                        seg["text"], voice=voice["voice"], lang=voice["language"],
                        speed=speed, sentence_pause=0.3, clause_pause=0.12,
                    )
                    assert rate == sr
                    raw_duration = len(audio)/sr
                    attempts.append({"speed": speed, "duration_seconds": raw_duration})
                    print(f"    {seg['id']} pass {attempt+1}: speed={speed:.4f}, "
                          f"duration={raw_duration:.3f}, target={target:.3f}", flush=True)
                    error = abs(raw_duration / target - 1)
                    if best is None or error < best[0]:
                        best = (error, audio.copy(), speed, attempt)
                    if abs(raw_duration / target - 1) < 0.025:
                        break
                    if raw_duration > target:
                        lower = speed
                    else:
                        upper = speed
                    speed = ((lower+upper)/2 if lower is not None and upper is not None
                             else speed * raw_duration / target)
                _, audio, chosen_speed, chosen_attempt = best
                raw = out / "_work" / f"{basename}_native.wav"
                sf.write(raw, audio, sr, subtype="PCM_16")
                tempo = (len(audio)/sr) / target
                if not 0.94 <= tempo <= 1.06:
                    raise RuntimeError(f"{basename}: residual tempo adjustment too large: {tempo}")
                # Tiny duration correction, pitch preserved. No text is cut to reach 90s.
                raw_bytes = run(["ffmpeg", "-v", "error", "-i", str(raw),
                                 "-af", f"atempo={tempo:.10f}",
                                 "-f", "f32le", "-ac", "1", "-ar", str(sr), "pipe:1"])
                audio = np.frombuffer(raw_bytes, dtype="<f4").copy()
                target_n = round(target * sr)
                difference = len(audio)-target_n
                if difference > 0:
                    tail_rms = float(np.sqrt(np.mean(audio[target_n:]**2)))
                    if tail_rms > 0.004:
                        raise RuntimeError(f"{basename}: audible tail would be truncated")
                    audio = audio[:target_n]
                elif difference < 0:
                    audio = np.pad(audio, (0, -difference))
                sf.write(final, audio, sr, subtype="PCM_16")
                meta = {"key": key, "id": seg["id"], "attempts": attempts,
                        "chosen_speed": chosen_speed, "chosen_attempt": chosen_attempt,
                        "final_atempo": tempo, "boundary_adjustment_samples": difference,
                        "duration_seconds": len(audio)/sr, "sha256": sha(final)}
                cache.write_text(json.dumps(meta, indent=2)+"\n")
            begin = round(start*sr)
            track[begin:begin+len(audio)] = audio
            results.append(meta)
            print(f"  {seg['id']}: {len(audio)/sr:.3f}s; native speed {meta['chosen_speed']:.4f}", flush=True)
        path = out / "_work" / f"{voice['choice']}_{voice['voice']}_dry.wav"
        sf.write(path, track, sr, subtype="PCM_16")
        report["voices"].append({**voice, "dry_file": path.name, "segments": results})
        (out / "voice_generation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print("All three local voices generated. Full episode remains untouched.", flush=True)


if __name__ == "__main__":
    main()
