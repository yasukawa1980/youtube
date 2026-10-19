#!/usr/bin/env python3
"""WAVE11完成MP4から45秒の縦型ショート3本を生成する（WAVE10版を写した。うなりは3→1Hzの下降）。"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE / "本編映像" / "wave11_雪の無人駅_3時間.mp4"
DEFAULT_OUT = HERE / "ショート"
FONT_JP = Path("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc")
FONT_LATIN = Path("/System/Library/Fonts/Supplemental/Cochin.ttc")

# ★この巻は左右差が3→1Hzへ直線で下がる。切り出した45秒の真ん中の値を出す。
def beat_hz(start: float) -> float:
    middle = start + 22.5
    return 3.0 + (1.0 - 3.0) * middle / 10_800.0


SPECS = (
    # ★暮れ方の雪（いちばん明るい）・灯のともる駅（灯りが満ちる青い時刻）・雪の止んだ夜（本編の顔）。
    #   縦（x=1125）の平均輝度は 45.1 / 39.8 / 35.8（10/19実測。夜更け33.2・未明28.8は使わない）。
    #   ★Aは本編1:00〜1:08の登録のお願いを避けて900秒から
    {"tag": "A", "start": 900.0, "scene": "暮れ方の雪"},
    {"tag": "B", "start": 2700.0, "scene": "灯のともる駅"},
    {"tag": "C", "start": 4800.0, "scene": "雪の止んだ夜"},
)
# ★ホームの灯りの柱（x≈1160）と待合室の右端（x≈1720）が両方入る位置
CROP_X = 1125  # 1920幅から608幅を切る。anchor 0.86（x/1312）
# ★★登録のお願い（2026/9/28）。3行目を足し、文字の塊を1行ぶん（58px）上へずらす。
#   いちばん下の行は y1520 のまま（下へ足すとYouTubeが題名を重ねる帯に入る）。スクリムも同じだけ上げる。
LIFT = 58
CTA = "チャンネル登録で、次の巻をお届けします"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tracked(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
            font: ImageFont.FreeTypeFont, tracking: int, fill: tuple[int, ...]) -> None:
    x, y = xy
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += int(draw.textlength(char, font=font)) + tracking


def overlay(path: Path, scene: str, hz: float) -> None:
    width, height = 1080, 1920
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    alpha = np.zeros((height, 1), dtype=np.uint8)
    ramp = np.clip((np.arange(height) - (1040 - LIFT)) / 620, 0, 1) ** 1.55
    alpha[:, 0] = np.rint(ramp * 0.76 * 255).astype(np.uint8)
    scrim = np.zeros((height, width, 4), dtype=np.uint8)
    scrim[:, :, :3] = (5, 11, 26)
    scrim[:, :, 3] = np.repeat(alpha, width, axis=1)
    image.alpha_composite(Image.fromarray(scrim))

    draw = ImageDraw.Draw(image)
    gold = (220, 177, 92, 255)
    cream = (242, 235, 218, 255)
    brand_font = ImageFont.truetype(str(FONT_LATIN), 34, index=1)
    title_font = ImageFont.truetype(str(FONT_JP), 88, index=0)
    sub_font = ImageFont.truetype(str(FONT_JP), 34, index=0)
    x = 88

    def shadow(pos: tuple[int, int], text: str, font: ImageFont.FreeTypeFont) -> None:
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2)):
            draw.text((pos[0] + dx, pos[1] + dy), text, font=font, fill=(0, 0, 0, 180))

    tracked(draw, (x, 1238 - LIFT), "WAVES OF JAPAN", brand_font, 9, (0, 0, 0, 180))
    tracked(draw, (x, 1236 - LIFT), "WAVES OF JAPAN", brand_font, 9, gold)
    draw.line(((x, 1292 - LIFT), (522, 1292 - LIFT)), fill=(220, 177, 92, 210), width=2)

    shadow((x, 1330 - LIFT), "雪の無人駅", title_font)
    draw.text((x, 1330 - LIFT), "雪の無人駅", font=title_font, fill=cream)
    line1 = f"{scene}・{hz:.1f}Hz の左右差（3→1Hz）"
    shadow((x, 1462 - LIFT), line1, sub_font)
    draw.text((x, 1462 - LIFT), line1, font=sub_font, fill=(242, 235, 218, 235))
    shadow((x, 1520 - LIFT), "3時間版はチャンネルに", sub_font)
    draw.text((x, 1520 - LIFT), "3時間版はチャンネルに", font=sub_font,
              fill=(242, 235, 218, 225))
    shadow((x, 1520), CTA, sub_font)
    draw.text((x, 1520), CTA, font=sub_font, fill=(242, 235, 218, 225))
    image.save(path)


def probe(path: Path) -> dict:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size:stream=codec_name,codec_type,width,height,r_frame_rate,sample_rate,channels",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def render(source: Path, out_dir: Path, selected: set[str]) -> list[dict]:
    out_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    for spec in SPECS:
        if spec["tag"] not in selected:
            continue
        tag = str(spec["tag"])
        ov = out_dir / f"_overlay_{tag}.png"
        out = out_dir / f"wave11_ショート_{tag}.mp4"
        overlay(ov, str(spec["scene"]), beat_hz(float(spec["start"])))
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", str(spec["start"]), "-i", str(source),
            "-loop", "1", "-i", str(ov), "-t", "45",
            "-filter_complex",
            f"[0:v]crop=608:1080:{CROP_X}:0,scale=1080:1920:flags=lanczos,"
            "format=yuv420p[v];[v][1:v]overlay=0:0:shortest=1[vout];"
            "[0:a]loudnorm=I=-16:TP=-2:LRA=7[aout]",
            "-map", "[vout]", "-map", "[aout]", "-frames:v", "1350",
            "-c:v", "libx264", "-preset", "fast", "-crf", "19",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
            "-movflags", "+faststart", str(out),
        ]
        subprocess.run(cmd, check=True)
        records.append({
            **spec,
            "hz": round(beat_hz(float(spec["start"])), 2),
            "file": str(out),
            "sha256": sha256(out),
            "probe": probe(out),
        })
        print(f"{tag}: {out}", flush=True)
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--only", default="ABC", help="生成するタグ。例: A または AC")
    args = parser.parse_args()
    if not args.source.is_file():
        raise SystemExit(f"完成MP4がありません: {args.source}")
    selected = set(args.only.upper())
    records = render(args.source, args.out_dir, selected)
    qa = {
        "source": str(args.source),
        "source_sha256": sha256(args.source),
        "crop": {"width": 608, "height": 1080, "x": CROP_X, "anchor": round(CROP_X / (1920 - 608), 2)},
        "output": {"width": 1080, "height": 1920, "fps": 30, "seconds": 45},
        "records": records,
    }
    (args.out_dir / "ショート生成検品.json").write_text(
        json.dumps(qa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
