"""Render only the three 90-second English voice audition videos.

Uses source artwork without replacing it, creates English editorial layouts,
normalizes narration and raises/ducks the existing original ambient music.
No subtitles are burned into the pictures.
"""
import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H, FPS, SR = 1920, 1080, 30, 24000
BG, IVORY, GOLD, MUTED = "#0c1820", "#f4efdf", "#d8b575", "#b0bfc3"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
TITLE = "/System/Library/Fonts/Supplemental/Georgia.ttf"


def run(args):
    return subprocess.run(args, check=True, capture_output=True)


def ff(args):
    return run(["ffmpeg", "-nostdin", "-y", "-v", "error", *args])


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(draw, xy, value, size=42, color=IVORY, serif=False):
    font = ImageFont.truetype(TITLE if serif else FONT, size)
    draw.text(xy, value, font=font, fill=color)


def header(image, heading, kind, footer=""):
    # 6% safe margins also accommodate the small full-frame camera move.
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, W, 180), fill=BG)
    draw.rectangle((0, 965, W, H), fill=BG)
    text(draw, (110, 38), "WORLDS OF MYSTERY  /  ENGLISH VOICE AUDITION", 26, GOLD)
    text(draw, (110, 94), heading, 53, serif=True)
    font = ImageFont.truetype(FONT, 33)
    width = draw.textlength(kind, font=font) + 44
    draw.rounded_rectangle((W-110-width, 34, W-110, 84), radius=10, fill="#243942")
    text(draw, (W-88-width, 40), kind, 33, GOLD)
    if footer:
        text(draw, (110, 993), footer, 29, MUTED)
    return image


def make_visuals(root, out):
    visuals = out / "_work" / "visuals"
    visuals.mkdir(parents=True, exist_ok=True)
    im = Image.new("RGB", (W, H), BG)
    art = ImageOps.contain(
        Image.open(root/"assets/generated/01_anubis_chamber.png").convert("RGB"),
        (1720, 785), method=Image.Resampling.LANCZOS)
    im.paste(art, ((W-art.width)//2, 180+(785-art.height)//2))
    header(im, "Anubis: the god beside the scale", "AI reconstruction")
    im.save(visuals/"hero.png")

    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    d.line((960, 290, 960, 800), fill=GOLD, width=9)
    d.line((500, 440, 1420, 440), fill=GOLD, width=9)
    d.line((830, 805, 1090, 805), fill=GOLD, width=9)
    d.ellipse((943, 267, 977, 301), fill=GOLD)
    for x in [540, 1380]:
        d.line((x, 440, x-140, 690), fill=GOLD, width=4)
        d.line((x, 440, x+140, 690), fill=GOLD, width=4)
        d.arc((x-150, 610, x+150, 790), 0, 180, fill=GOLD, width=6)
    d.ellipse((475, 590, 545, 660), fill="#b66061")
    d.ellipse((535, 590, 605, 660), fill="#b66061")
    d.polygon([(475, 630), (605, 630), (540, 713)], fill="#b66061")
    d.line((1340, 710, 1415, 555), fill=IVORY, width=5)
    for i in range(10):
        x, y = 1352+i*6, 688-i*12
        d.line((x-28, y-8, x+28, y-18), fill=IVORY, width=4)
    text(d, (440, 845), "The heart", 48)
    text(d, (1185, 845), "A symbol of Maat", 48)
    header(im, "The weighing of the heart", "Concept diagram",
           "Based on Met sources S04 / S05. Symbols vary between objects.")
    im.save(visuals/"balance.png")

    specs = [
        ("met_548344_detail", "548344", "Nauny's Book of the Dead", "Museum object",
         (0.10, 0.37, 0.97, 0.90), "30.3.31"),
        ("met_544075", "544075", "A watchful canine", "Museum object", None, "69.105"),
        ("met_544075_detail", "544075", "Lying down, but ears up", "Museum object",
         (0.20, 0.03, 0.97, 0.92), "69.105"),
        ("met_557830", "557830", "A modern copy of an ancient wall painting", "Facsimile",
         None, "33.8.21"),
    ]
    for key, oid, title, label, crop, number in specs:
        source = Image.open(root/f"assets/museum/met_{oid}.jpg").convert("RGB")
        if crop:
            source = source.crop(tuple(round(v*(source.width if i%2==0 else source.height))
                                       for i, v in enumerate(crop)))
        im = Image.new("RGB", (W, H), BG)
        art = ImageOps.contain(source, (1720, 780), Image.Resampling.LANCZOS)
        im.paste(art, ((W-art.width)//2, 180+(780-art.height)//2))
        header(im, title, label, f"The Metropolitan Museum of Art  /  {number}  /  Open Access (CC0)")
        im.save(visuals/f"{key}.png")

    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    items = [("01", "Museum objects", "Photographs of surviving evidence"),
             ("02", "Interpretation", "What the museum sources explain"),
             ("03", "Reconstructions", "Images that help us picture the past")]
    for i, (num, title, caption) in enumerate(items):
        y = 235+i*220
        d.rounded_rectangle((130, y, 1790, y+180), 22, fill="#1a303a", outline="#42535b", width=2)
        text(d, (175, y+49), num, 65, GOLD)
        text(d, (330, y+30), title, 51, serif=True)
        text(d, (330, y+105), caption, 37, MUTED)
    header(im, "Objects and reconstructions", "Viewing guide")
    im.save(visuals/"evidence.png")
    return visuals


def loudness(path):
    result = run(["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path), "-af",
                  "loudnorm=I=-16:TP=-3:LRA=7:print_format=json", "-f", "null", "-"])
    return json.loads(re.findall(r"\{\s*\"input_i\".*?\}", result.stderr.decode(), re.S)[-1])


def rms_db(x):
    return 20*math.log10(max(float(np.sqrt(np.mean(x.astype(np.float64)**2))), 1e-10))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--visuals-only", action="store_true")
    parser.add_argument("--pictures-only", action="store_true")
    args = parser.parse_args()
    root, out = args.episode_root, args.output
    work = out/"_work"
    visuals = make_visuals(root, out)
    if args.visuals_only:
        print("English preview layouts ready.", flush=True)
        return
    data = json.loads((out/"voice_generation.json").read_text())
    # Cut the same common pictures against all three voices.
    shot_specs = []
    for i, seg in enumerate(data["segments"]):
        a = 0 if i == 0 else seg["start"]
        b = data["segments"][i+1]["start"] if i < 3 else 90.0
        midpoint = (a+b)/2
        for name, left, right in zip(seg["visuals"], [a, midpoint], [midpoint, b]):
            shot_specs.append((name, round(left*FPS), round(right*FPS)))
    parts = []
    for index, (key, first, last) in enumerate(shot_specs):
        path = work/f"picture_{index:02}.mp4"
        count = last-first
        if not path.exists():
            # Oversampling avoids visible integer-pixel steps in the slow zoom.
            zoom = f"1+0.025*on/{max(count-1,1)}"
            vf = (f"scale=3840:2160,zoompan=z='{zoom}':"
                  f"x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':"
                  f"d={count}:s=1920x1080:fps=30,format=yuv420p")
            ff(["-i", str(visuals/f"{key}.png"), "-vf", vf, "-frames:v", str(count),
                "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", str(path)])
        parts.append(path)
    concat = work/"pictures.txt"
    concat.write_text("".join(f"file '{p.as_posix()}'\n" for p in parts))
    master = work/"picture_90s.mp4"
    ff(["-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(master)])
    print("Common 1080p/30fps, subtitle-free picture track ready.", flush=True)
    if args.pictures_only:
        return

    n = SR*90
    raw = ff(["-i", str(root/"audio/original_ambient.wav"), "-t", "90",
              "-ar", str(SR), "-ac", "2", "-f", "f32le", "pipe:1"]).stdout
    music = np.frombuffer(raw, dtype="<f4").reshape(-1, 2).copy()[:n]
    speech_mask = np.zeros(n, bool)
    time = np.arange(n)/SR
    # A scheduled duck holds the lower level through each spoken paragraph;
    # it does not pump the music in tiny gaps between words.
    duck = np.ones(n)
    for seg in data["segments"]:
        speech_mask[round(seg["start"]*SR):round(seg["end"]*SR)] = True
        attack = np.clip((time-(seg["start"]-0.18))/0.18, 0, 1)
        release = np.clip(((seg["end"]+0.40)-time)/0.40, 0, 1)
        duck = np.minimum(duck, 1-np.minimum(attack, release))
    music *= 10**((-36.5-rms_db(music[speech_mask]))/20)
    music *= (10**((4*duck)/20))[:, None]
    fade = np.minimum(np.clip(time/0.7, 0, 1), np.clip((90-time)/2.7, 0, 1))
    music *= fade[:, None]
    sf.write(work/"music_raised_ducked.wav", music, SR, subtype="FLOAT")
    report = {
        "scope": "N01-N04 audition only; full production awaits owner voice choice",
        "duration_seconds": 90, "subtitles_burned_in": False,
        "video": {"width": W, "height": H, "fps": FPS, "shots": len(parts),
                  "camera": "2.5% slow zoom in every shot"},
        "bgm": {
            "source_sha256": sha(root/"audio/original_ambient.wav"),
            "during_narration_rms_dbfs": rms_db(music[speech_mask]),
            "chapter_gap_rms_dbfs": rms_db(music[round((data['segments'][3]['start']-1.3)*SR):
                                                   round((data['segments'][3]['start']-0.3)*SR)]),
            "nominal_pause_boost_db": 4,
            "fade_out_seconds": 2.7,
            "duck_method": "shared paragraph schedule, 180ms attack and 400ms release",
        },
        "voices": [],
        "human_listening": "pending",
    }
    for voice in data["voices"]:
        dry = work/voice["dry_file"]
        norm = work/f"{voice['choice']}_normalized.wav"
        first = loudness(dry)
        settings = ("loudnorm=I=-16:TP=-3:LRA=7:linear=true:"
                    f"measured_I={first['input_i']}:measured_TP={first['input_tp']}:"
                    f"measured_LRA={first['input_lra']}:measured_thresh={first['input_thresh']}:"
                    f"offset={first['target_offset']}")
        ff(["-i", str(dry), "-af", settings, "-ar", str(SR), "-ac", "1",
            "-c:a", "pcm_f32le", str(norm)])
        narration, sr = sf.read(norm, dtype="float32")
        assert sr == SR and abs(len(narration)-n) < 10
        narration = np.pad(narration[:n], (0, max(0, n-len(narration))))
        gain_db = 0.0
        mixed = work/f"{voice['choice']}_mixed.wav"
        for _ in range(3):
            mix = narration[:, None]*10**(gain_db/20)+music
            sf.write(mixed, mix, SR, subtype="FLOAT")
            measure = loudness(mixed)
            correction = -16-float(measure["input_i"])
            if abs(correction) <= 0.15:
                break
            gain_db += correction
        if float(measure["input_tp"]) > -2.0:
            raise RuntimeError(f"{voice['choice']}: mix true peak exceeds -2 dBTP")
        filename = f"wom01_voice_{voice['choice']}_{voice['voice']}_90s.mp4"
        path = out/filename
        ff(["-i", str(master), "-i", str(mixed), "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", "90", "-movflags", "+faststart",
            "-metadata", f"title=Anubis voice {voice['choice']} - {voice['label']}",
            "-metadata:s:a:0", "language=eng", str(path)])
        ff(["-i", str(path), "-f", "null", "-"])
        final = loudness(path)
        probe = json.loads(run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                               "-of", "json", str(path)]).stdout)
        assert abs(float(probe["format"]["duration"])-90) < 1/FPS
        assert abs(float(final["input_i"])+16) <= .5
        assert float(final["input_tp"]) <= -2
        assert all(s["codec_type"] != "subtitle" for s in probe["streams"])
        record = {**{k:voice[k] for k in ["choice", "voice", "language", "label"]},
                  "file": filename, "bytes": path.stat().st_size, "sha256": sha(path),
                  "duration_seconds": float(probe["format"]["duration"]),
                  "integrated_lufs": float(final["input_i"]),
                  "true_peak_dbtp": float(final["input_tp"]), "lra_lu": float(final["input_lra"]),
                  "narration_rms_dbfs": rms_db(narration[speech_mask]*10**(gain_db/20)),
                  "bgm_relative_to_narration_db": rms_db(music[speech_mask])-rms_db(narration[speech_mask]*10**(gain_db/20)),
                  "full_decode": "pass"}
        report["voices"].append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
        (out/"audition_qc.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    (out/"SHA256SUMS.txt").write_text("".join(f"{v['sha256']}  {v['file']}\n" for v in report["voices"]))
    for sec in [8, 20, 32, 46, 57, 65, 77, 86]:
        ff(["-ss", str(sec), "-i", str(out/report["voices"][0]["file"]),
            "-frames:v", "1", "-vf", "scale=1280:-2", "-q:v", "3",
            str(out/f"frame_{sec:02}s.jpg")])
    print("Three 90-second audition videos decoded and measured.", flush=True)


if __name__ == "__main__":
    main()
