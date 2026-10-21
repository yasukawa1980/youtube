"""EP001 common timeline, external subtitles, moving pictures and bilingual audio.

WOM_EPISODE_ROOT contains content, generated narration and English compositions.
Run with --stage timeline|audio|pictures|package|all. All paths in JSON are relative.
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw

from wom01_subtitles import sentence_cues, to_srt

FPS, SR = 30, 24000


def ff(args):
    return subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", *map(str, args)],
                          check=True, capture_output=True)


def read(path):
    return json.loads(path.read_text())


def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def measure(path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", str(path), "-af",
                        "loudnorm=I=-16:TP=-3:LRA=7:print_format=json", "-f", "null", "-"],
                       check=True, capture_output=True, text=True)
    return json.loads(re.findall(r'\{\s*"input_i".*?\}', r.stderr, re.S)[-1])


def rms(x):
    return 20*math.log10(max(float(np.sqrt(np.mean(x.astype(np.float64)**2))), 1e-10))


def build_timeline(root):
    languages = os.environ.get("WOM_LANGUAGES", "en,ja").split(",")
    assert languages in (["en"], ["en", "ja"])
    narr = {lang: read(root / f"records/narration_segments_{lang}.json") for lang in languages}
    en = narr["en"]["segments"]
    for value in narr.values():
        assert [s["id"] for s in en] == [s["id"] for s in value["segments"]]
    master, pos = [], 1.8
    for i, e in enumerate(en):
        lengths = {lang: narr[lang]["segments"][i]["duration_seconds"] for lang in languages}
        duration = max(lengths.values())
        speech_end = pos+duration
        if i == len(en)-1:
            gap = 5
        else:
            gap = 1.8 if en[i+1]["chapter"] != e["chapter"] else float(os.environ.get("WOM_SENTENCE_BLOCK_GAP", ".35"))
        end = math.ceil((speech_end+gap)*FPS)/FPS
        master.append({"id": e["id"], "chapter": e["chapter"], "heading": e["heading"],
                       "start": pos, "speech_end": speech_end, "end": end,
                       "speech_seconds": lengths,
                       "padding_seconds": {lang: end-pos-d for lang, d in lengths.items()},
                       "gap_min_seconds": gap})
        pos = end
    data = {"fps": FPS, "sample_rate": SR, "duration_seconds": pos, "languages": languages,
            "common_bilingual_timeline_finalized": languages == ["en", "ja"],
            "initial_music_seconds": 1.8, "chapter_music_seconds_min": 1.8,
            "end_card_music_seconds_min": 5, "subtitles_burned_in": False, "segments": master}
    save(root / "records/master_timeline.json", data)
    for lang in languages:
        track = np.zeros(round(pos*SR), np.float32)
        segments, all_cues = [], []
        for common, seg in zip(master, narr[lang]["segments"]):
            audio, sr = sf.read(root / seg["audio_file"], dtype="float32")
            assert sr == SR
            a = round(common["start"]*SR)
            track[a:a+len(audio)] = audio
            cues = [{**c, "start": c["start"]+common["start"], "end": c["end"]+common["start"]}
                    for c in seg["cues"]]
            segments.append({**seg, "start": common["start"], "end": common["end"], "cues": cues})
            for c in cues:
                all_cues.extend(sentence_cues(c, lang))
        sf.write(root / f"audio/{lang}/narration.wav", track, SR, subtype="PCM_16")
        save(root / f"records/narration_timeline_{lang}.json", {
            **narr[lang], "segments": segments, "duration_seconds": pos,
            "sentence_boundary_timing": "measured synthesis plus master segment offset",
        })
        prev = 0
        for c in all_cues:
            assert 0 <= prev <= c["start"] < c["end"] <= pos
            prev = c["end"]
            assert len(c["text"].splitlines()) <= 2
        (root / f"deliverables/EP001_字幕_{lang}.srt").write_text(to_srt(all_cues))
        save(root / f"records/subtitle_cues_{lang}.json", {
            "timing": "measured sentence boundaries; within-sentence page changes proportional to text length",
            "count": len(all_cues), "cues": all_cues,
        })
    print(f"MASTER {pos:.6f}s; {len(master)} matched segments", flush=True)


def make_audio(root):
    master = read(root / "records/master_timeline.json")
    duration = master["duration_seconds"]
    n = round(duration*SR)
    t = np.arange(n)/SR
    # Same original synthesized score as v01, extended without looping the end fade.
    slow = .66+.34*np.sin(2*np.pi*t/53)**2
    base = .006*np.sin(2*np.pi*146.832384*t)*slow+.003*np.sin(2*np.pi*220*t+.5)
    notes = np.array([293.664768, 349.228231, 440., 391.995436, 293.664768, 523.251131])
    local = t % 14
    pitch = notes[np.floor(t/14).astype(int) % len(notes)]
    pluck = .018*np.sin(2*np.pi*pitch*local)*np.exp(-local/2.1)*(1-np.exp(-local/.045))
    music = np.stack([base+pluck, base+.92*pluck+.0017*np.sin(2*np.pi*293.664768*t+.45)], axis=1).astype(np.float32)
    mask = np.zeros(n, bool)
    duck = np.ones(n, np.float32)
    for seg in master["segments"]:
        a, b = seg["start"], seg["speech_end"]
        mask[round(a*SR):round(b*SR)] = True
        attack = np.clip((t-(a-.18))/.18, 0, 1)
        release = np.clip(((b+.40)-t)/.40, 0, 1)
        duck = np.minimum(duck, 1-np.minimum(attack, release))
    music *= 10**((float(os.environ.get("WOM_BGM_DBFS", "-36.5"))-rms(music[mask]))/20)
    music *= (10**((4*duck)/20))[:, None]
    fade = np.minimum(np.clip(t/.7, 0, 1), np.clip((duration-t)/3, 0, 1))
    music *= fade[:, None]
    sf.write(root / "audio/common_bgm.wav", music, SR, subtype="FLOAT")
    report = {"bgm": {"shared_across_languages": True, "during_either_narration_rms_dbfs": rms(music[mask]),
                      "pause_boost_db": 4, "fade_out_seconds": 3,
                      "sha256": sha(root / "audio/common_bgm.wav"),
                      "ducking": "union of English/Japanese paragraph spans; 180ms attack, 400ms release"},
              "languages": {}}
    for lang in master["languages"]:
        dry = root / f"audio/{lang}/narration.wav"
        norm = root / f"audio/{lang}/normalized.wav"
        first = measure(dry)
        settings = ("loudnorm=I=-16:TP=-3:LRA=7:linear=true:"
                    f"measured_I={first['input_i']}:measured_TP={first['input_tp']}:"
                    f"measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:"
                    f"offset={first['target_offset']}")
        ff(["-i", dry, "-af", settings, "-ar", SR, "-ac", 1, "-c:a", "pcm_f32le", norm])
        voice, sr = sf.read(norm, dtype="float32")
        assert sr == SR and abs(len(voice)-n) < 10
        voice = np.pad(voice[:n], (0, max(0, n-len(voice))))
        gain, mixpath = 0.0, root / f"audio/{lang}/mix.wav"
        for _ in range(4):
            sf.write(mixpath, voice[:, None]*10**(gain/20)+music, SR, subtype="FLOAT")
            stats = measure(mixpath)
            correction = -16-float(stats["input_i"])
            if abs(correction) <= .1:
                break
            gain += correction
        assert float(stats["input_tp"]) <= -2
        final = root / f"deliverables/EP001_audio_{lang}.wav"
        ff(["-i", mixpath, "-ar", 48000, "-c:a", "pcm_s24le", final])
        aac = root / f"deliverables/EP001_audio_{lang}.m4a"
        ff(["-i", final, "-c:a", "aac", "-b:a", "192k", "-metadata:s:a:0",
            "language="+("eng" if lang == "en" else "jpn"), aac])
        # Narration RMS only while this language's sentences are active.
        active = np.zeros(n, bool)
        for seg in read(root / f"records/narration_timeline_{lang}.json")["segments"]:
            for c in seg["cues"]:
                active[round(c["start"]*SR):round(c["end"]*SR)] = True
        voice_db = rms(voice[active]*10**(gain/20))
        report["languages"][lang] = {
            "wav": measure(final), "aac": measure(aac), "narration_active_rms_dbfs": voice_db,
            "bgm_under_this_voice_rms_dbfs": rms(music[active]),
            "bgm_relative_to_narration_db": rms(music[active])-voice_db,
        }
        print(lang, report["languages"][lang], flush=True)
    save(root / "records/audio_qc.json", report)


def make_pictures(root):
    master = read(root / "records/master_timeline.json")
    manifest = read(root / "records/visual_manifest.json")
    work = root / "_work/render"
    work.mkdir(parents=True, exist_ok=True)
    parts, shots = [], []
    for i, seg in enumerate(master["segments"]):
        images = [s for s in manifest["shots"] if s["segment_id"] == seg["id"]]
        first = 0 if i == 0 else round(seg["start"]*FPS)
        last = round(seg["end"]*FPS)
        bounds = np.linspace(first, last, len(images)+1).round().astype(int)
        for j, image in enumerate(images):
            count = int(bounds[j+1]-bounds[j])
            picture = root / image["file"]
            key = hashlib.sha256(f"{sha(picture)}:{count}:zoom2.5:x264-crf21-v1".encode()).hexdigest()[:12]
            path = work / f'{seg["id"]}_{j:02}_{key}.mp4'
            if not path.exists():
                zoom = f"1+0.025*on/{max(count-1, 1)}"
                vf = (f"scale=3840:2160,zoompan=z='{zoom}':x='iw/2-iw/zoom/2':"
                      f"y='ih/2-ih/zoom/2':d={count}:s=1920x1080:fps=30,format=yuv420p")
                ff(["-i", picture, "-vf", vf, "-frames:v", count, "-an", "-c:v", "libx264",
                    "-threads", 4, "-preset", "veryfast", "-crf", 21, "-color_primaries", "bt709",
                    "-color_trc", "bt709", "-colorspace", "bt709", path])
            actual = probe(path)
            assert abs(float(actual["format"]["duration"])-count/FPS) < 1/FPS
            parts.append(path)
            shots.append({**image, "start": int(bounds[j])/FPS, "end": int(bounds[j+1])/FPS,
                          "frames": count, "camera": "2.5 percent continuous slow zoom",
                          "encoded_file": str(path.relative_to(root))})
        print("PICTURE", seg["id"], flush=True)
    concat = work / "concat.txt"
    concat.write_text("".join(f"file '{p}'\n" for p in parts))
    ff(["-f", "concat", "-safe", 0, "-i", concat, "-c", "copy", "-movflags", "+faststart",
        root / "_work/picture_master.mp4"])
    save(root / "records/render_shots.json", shots)


def probe(path):
    return json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_format",
                                               "-show_streams", "-of", "json", str(path)]))


def package(root):
    master = read(root / "records/master_timeline.json")
    total = master["duration_seconds"]
    deliver = root / "deliverables"
    picture = root / "_work/picture_master.mp4"
    main = deliver / "EP001_Anubis_en_v02.mp4"
    ff(["-i", picture, "-i", deliver / "EP001_audio_en.m4a", "-map", "0:v:0", "-map", "1:a:0",
        "-c", "copy", "-metadata:s:a:0", "language=eng", "-movflags", "+faststart", main])
    # Both previews share the same encoded picture stream.
    preview_picture = root / "_work/preview_picture.mp4"
    ff(["-i", picture, "-vf", "scale=1280:720,fps=15", "-c:v", "libx264", "-threads", 4,
        "-preset", "veryfast", "-crf", 24, "-an", preview_picture])
    files = [main]
    for lang in master["languages"]:
        p = deliver / f"EP001_review_{lang}_720p.mp4"
        ff(["-i", preview_picture, "-i", deliver / f"EP001_audio_{lang}.m4a",
            "-map", "0:v:0", "-map", "1:a:0", "-c", "copy", "-movflags", "+faststart",
            "-metadata:s:a:0", "language="+("eng" if lang == "en" else "jpn"), p])
        files += [p, deliver / f"EP001_audio_{lang}.wav", deliver / f"EP001_audio_{lang}.m4a"]
    qc = {"version": "v02-en-primary", "selected_voice": "B / af_heart",
          "languages": master["languages"],
          "common_bilingual_timeline_finalized": master["common_bilingual_timeline_finalized"],
          "duration_seconds": total, "subtitles_burned_in": False,
          "human_listening_en_full": False, "human_listening_ja_full": False,
          "publication_performed": False, "files": [], "subtitles": {}}
    for p in files:
        ff(["-i", p, "-f", "null", "-"])
        info = probe(p)
        assert abs(float(info["format"]["duration"])-total) <= 1/FPS
        for stream in info["streams"]:
            assert abs(float(stream["duration"])-total) <= 1/FPS
            assert stream["codec_type"] != "subtitle"
        stat = measure(p)
        assert abs(float(stat["input_i"])+16) <= .5
        assert float(stat["input_tp"]) <= -2
        qc["files"].append({"file": p.name, "bytes": p.stat().st_size, "sha256": sha(p),
                            "duration_seconds": float(info["format"]["duration"]),
                            "integrated_lufs": float(stat["input_i"]), "true_peak_dbtp": float(stat["input_tp"]),
                            "full_decode": "pass", "streams": [
                                {k: s.get(k) for k in ("codec_type", "codec_name", "duration", "width", "height", "avg_frame_rate")}
                                for s in info["streams"]]})
        print("QC", p.name, stat["input_i"], stat["input_tp"], flush=True)
    for lang in master["languages"]:
        cues = read(root / f"records/subtitle_cues_{lang}.json")["cues"]
        srt = deliver / f"EP001_字幕_{lang}.srt"
        qc["subtitles"][lang] = {"count": len(cues), "max_lines": max(len(c["text"].splitlines()) for c in cues),
                                 "max_line_length": max(len(l) for c in cues for l in c["text"].splitlines()),
                                 "ordered_within_duration": True, "sha256": sha(srt)}
    save(root / "records/qc.json", qc)
    checkfiles = files + list(deliver.glob("*.srt"))
    (deliver / "SHA256SUMS.txt").write_text("".join(f"{sha(p)}  {p.name}\n" for p in checkfiles))
    # Final encoded frames, not merely source PNGs, for independent review.
    rows = []
    for i, seg in enumerate(master["segments"]):
        sec = (seg["start"]+seg["end"])/2 + .25
        p = root / "review" / f'encoded_{seg["id"]}.jpg'
        ff(["-ss", sec, "-i", main, "-frames:v", 1, "-vf", "scale=1280:-2", "-q:v", 3, p])
        im = Image.open(p).convert("RGB")
        im.thumbnail((384, 216))
        rows.append((seg["id"], sec, im.copy()))
    sheet = Image.new("RGB", (1152, math.ceil(len(rows)/3)*245), "#0c1820")
    draw = ImageDraw.Draw(sheet)
    for i, (name, sec, im) in enumerate(rows):
        x, y = (i % 3)*384, (i//3)*245
        sheet.paste(im, (x, y))
        draw.text((x+10, y+218), f"{name} / {sec:.1f}s", fill="white")
    # Detailed sheet is for reading; small pages are Git-friendly at <=1280px.
    sheet.save(root / "review/contact_all.jpg", quality=83)
    for i in range(math.ceil(len(rows)/9)):
        page = sheet.crop((0, i*735, 1152, min((i+1)*735, sheet.height)))
        page.save(root / "review" / f"contact_{i+1}.jpg", quality=86)
    print(f"Delivery ({', '.join(master['languages'])}) decoded and measured.", flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage", choices=["timeline", "audio", "pictures", "package", "all"], default="all")
    stage = p.parse_args().stage
    root = Path(os.environ["WOM_EPISODE_ROOT"])
    for name, fn in (("timeline", build_timeline), ("audio", make_audio),
                     ("pictures", make_pictures), ("package", package)):
        if stage in (name, "all"):
            fn(root)


if __name__ == "__main__":
    main()
