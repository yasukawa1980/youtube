"""Extract a version-labelled Claude review pack without changing production media.

Requires ffmpeg/ffprobe, Pillow and numpy. Media output stays outside Git.
Example:
  python wom01_prepare_review.py --episode-root PATH --review-dir PATH --media-dir PATH
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def run(args):
    return subprocess.run(args, check=True, capture_output=True).stdout


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stamp(seconds):
    return f"{int(seconds)//60:02}:{seconds%60:06.3f}"


def db(value):
    return round(20 * math.log10(max(float(value), 1e-10)), 2)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode-root", required=True, type=Path)
    ap.add_argument("--review-dir", required=True, type=Path)
    ap.add_argument("--media-dir", required=True, type=Path)
    args = ap.parse_args()
    source = args.episode_root / "deliverables/EP001_アヌビス_完成試作_v01.mp4"
    timeline_path = args.episode_root / "records/narration_timeline.json"
    timeline = json.loads(timeline_path.read_text())
    review, media = args.review_dir, args.media_dir
    review.mkdir(parents=True, exist_ok=True)
    media.mkdir(parents=True, exist_ok=True)
    (review / "frames").mkdir(exist_ok=True)
    probe = json.loads(run(["ffprobe", "-v", "error", "-show_format",
                           "-show_streams", "-of", "json", str(source)]))
    duration = float(probe["format"]["duration"])
    if abs(duration - timeline["duration_seconds"]) > 0.1:
        raise ValueError("Source duration does not match the provided timeline")
    # Preserve stereo samples: mono mixing could hide opposite-phase peaks.
    raw = run(["ffmpeg", "-v", "error", "-i", str(source), "-map", "0:a:0",
               "-f", "f32le", "-ac", "2", "-ar", "48000", "pipe:1"])
    samples = np.frombuffer(raw, dtype="<f4").reshape(-1, 2)
    rows = []
    md = ["# v01 日本語試作：映像と音声の対応表", "",
          "対象は2026-10-15制作のv01。Claudeのv02修正・英語化は未反映。",
          "画像は実際のMP4から抽出。文章・発話時刻は音声合成時の記録で、"
          "音声認識による書き起こしではありません。音量は完成MP4の音声を再測定。",
          "無音検出はBGM込みの音声が−45 dBFS未満となる20ms区間を連結したもの。"
          "語間の間や発音の正しさを判定するものではありません。", ""]
    for seg in timeline["segments"]:
        # Two samples show both visuals used in most segments.
        frames = []
        for fraction, label in [(0.25, "a"), (0.75, "b")]:
            t = seg["start"] + (seg["end"] - seg["start"]) * fraction
            path = review / "frames" / f"{seg['id']}_{label}_{t:07.3f}s.jpg"
            run(["ffmpeg", "-v", "error", "-nostdin", "-n", "-ss", str(t),
                 "-i", str(source), "-frames:v", "1", "-vf", "scale=1280:-2",
                 "-q:v", "3", str(path)])
            frames.append({"time_seconds": round(t, 3),
                           "path": path.relative_to(review).as_posix()})
        x = samples[int(seg["start"] * 48000):int(seg["end"] * 48000)]
        rms = float(np.sqrt(np.mean(x.astype(np.float64) ** 2)))
        peak = float(np.max(np.abs(x)))
        row = {"id": seg["id"], "start": seg["start"], "end": seg["end"],
               "rms_dbfs": db(rms), "sample_peak_dbfs": db(peak), "frames": frames}
        rows.append(row)
        md += [f"## {seg['id']} {stamp(seg['start'])}–{stamp(seg['end'])} {seg['heading']}", "",
               f"音声RMS {db(rms)} dBFS／サンプルピーク {db(peak)} dBFS"
               "（トゥルーピークとは別の値）", ""]
        for frame in frames:
            md += [f"![{seg['id']} {stamp(frame['time_seconds'])}]({frame['path']})", ""]
        md += ["|開始|終了|合成時の入力文|", "|---|---|---|"]
        for cue in seg["cues"]:
            md.append(f"|{stamp(cue['start'])}|{stamp(cue['end'])}|{cue['text']}|")
        md.append("")
    block = 960  # 20 ms at 48 kHz.
    blocks = samples[:len(samples)//block*block].reshape(-1, block, 2)
    levels = np.sqrt(np.mean(blocks.astype(np.float64)**2, axis=(1, 2)))
    quiet = levels < 10**(-45/20)
    intervals, begin = [], None
    for i, is_quiet in enumerate(np.append(quiet, False)):
        if is_quiet and begin is None:
            begin = i
        if not is_quiet and begin is not None:
            if (i - begin)*0.02 >= 0.5:
                intervals.append({"start": round(begin*0.02, 3),
                                  "end": round(i*0.02, 3)})
            begin = None
    # Plot a level overview from decoded samples, without external chart tools.
    plot = Image.new("RGB", (1280, 420), "#101820")
    draw = ImageDraw.Draw(plot)
    for level in [-60, -45, -30, -15, 0]:
        y = 350 - int((level + 60)/60*300)
        draw.line((60, y, 1260, y), fill="#344754")
        draw.text((4, y-4), f"{level} dBFS", fill="white")
    for px in range(1200):
        left = int(px/1200*len(levels))
        right = max(left+1, int((px+1)/1200*len(levels)))
        value = db(np.max(levels[left:right]))
        y = max(50, min(350, 350-int((value+60)/60*300)))
        draw.line((60+px, 350, 60+px, y), fill="#6eb9ba")
    for sec in range(0, int(duration)+1, 60):
        draw.text((60+int(sec/duration*1200), 365), stamp(sec), fill="white")
    draw.text((60, 15), "v01 JA - mixed audio, 20 ms RMS envelope (not perceived quality)",
              fill="white")
    plot.save(review / "audio_levels.jpg", quality=90)
    (review / "映像と発話の対応.md").write_text("\n".join(md).rstrip()+"\n")
    report = {
        "reviewed_version": "v01_ja_2026-10-15",
        "source_name": source.name, "source_sha256": digest(source),
        "timeline_sha256": digest(timeline_path), "duration_seconds": duration,
        "decoded_sample_rate": 48000, "decoded_channels": 2,
        "decoded_duration_seconds": len(samples)/48000,
        "decoded_samples_at_or_above_full_scale": int(np.count_nonzero(np.abs(samples) >= 1)),
        "quiet_definition": "mixed audio RMS below -45 dBFS in 20 ms windows, at least 0.5 s",
        "quiet_intervals": intervals, "segments": rows,
        "sentence_count": sum(len(s["cues"]) for s in timeline["segments"]),
        "frame_count": sum(len(r["frames"]) for r in rows),
        "human_listening": "not_performed", "asr": "not_performed",
        "claude_media_access": "not_verified",
    }
    (review / "measured_review.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    preview = media / "wom01_v01_ja_review_720p.mp4"
    audio = media / "wom01_v01_ja_original_audio.m4a"
    print("Extracted frames and audio measurements; encoding review video.", flush=True)
    run(["ffmpeg", "-v", "error", "-nostdin", "-n", "-i", str(source),
         "-map", "0:v:0", "-map", "0:a:0", "-vf", "scale=1280:-2",
         "-r", "15", "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
         "-c:a", "copy", "-movflags", "+faststart", str(preview)])
    run(["ffmpeg", "-v", "error", "-nostdin", "-n", "-i", str(source),
         "-map", "0:a:0", "-c:a", "copy", "-movflags", "+faststart", str(audio)])
    assets = []
    for path in [preview, audio]:
        run(["ffmpeg", "-v", "error", "-nostdin", "-i", str(path), "-f", "null", "-"])
        info = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                              "-of", "json", str(path)]))
        assets.append({"name": path.name, "bytes": path.stat().st_size,
                       "sha256": digest(path), "duration_seconds": float(info["format"]["duration"]),
                       "full_decode": "pass"})
    manifest = {"source_sha256": report["source_sha256"], "version": report["reviewed_version"],
                "assets": assets, "audio": "AAC copied unchanged from source; no re-encoding",
                "video": "720p 15fps proxy; review source at 1080p 30fps for final motion judgment"}
    (review / "media_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n")
    (media / "SHA256SUMS.txt").write_text("".join(f"{a['sha256']}  {a['name']}\n" for a in assets))
    print(json.dumps({"frames": report["frame_count"], "sentences": report["sentence_count"],
                      "media": assets}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
