"""SOJ09「晩秋の浜辺」3608秒・無音本編を分割再開可能な形で作る（SOJ08 の build_full_video.py を写したもの）。"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess
import threading
import time


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
IMAGES = ROOT / "画像"
CARD_IMAGE = ROOT.parent.parent / "Whispers_ブランド素材/エンドカード_満月と水面_oldjapan.png"
CTA_IMAGE = HERE / "_cta.png"
PARTS = HERE / "_parts"
FPS = 30
W, H = 1920, 1080
TOTAL = 3608
STILL = False

def _roi(mask: Path) -> tuple[int, int, int, int]:
    """水域マスクの外接矩形＋余白16px（SOJ08 は手で書いていたのを自動にした）。"""
    import cv2  # noqa: PLC0415
    m = cv2.imread(str(mask), cv2.IMREAD_GRAYSCALE)
    ys, xs = (m > 0).nonzero()
    x0, y0 = max(0, int(xs.min()) - 16), max(0, int(ys.min()) - 16)
    x1, y1 = min(W, int(xs.max()) + 17), min(H, int(ys.max()) + 17)
    return (x0, y0, x1 - x0, y1 - y0)


# ★振幅は SOJ08 と同じ距離の段（近い場面ほど大きく、遠景は小さく）
SCENES = [
    {"name": "01_波打ち際_1130s_無音", "stem": "01_波打ち際_昼下がり", "seconds": 1130,
     "amps": (0.80, 0.36, 1.28, 0.58), "cta": True},
    {"name": "02_漁村の浜_1125s_無音", "stem": "02_漁村の浜_夕方", "seconds": 1125,
     "amps": (0.62, 0.28, 1.00, 0.45), "cta": False},
    {"name": "03_宿の縁側_560s_無音", "stem": "03_宿の縁側から_薄暮", "seconds": 560,
     "amps": (0.34, 0.14, 0.54, 0.23), "cta": False},
    {"name": "04_月夜の海_838s_無音", "stem": "04_月夜の海_夜", "seconds": 838,
     "amps": (0.24, 0.10, 0.42, 0.18), "cta": False},
]
for _s in SCENES:
    _s["image"] = IMAGES / f"{_s['stem']}.png"
    _s["mask"] = HERE / f"{_s['stem']}_水域マスク.png"
FINAL = HERE / "SOJ09_晩秋の浜辺_3608秒_無音.mp4"
ENCODE = [
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
    "-pix_fmt", "yuv420p", "-r", str(FPS),
    "-g", str(FPS), "-keyint_min", str(FPS), "-sc_threshold", "0",
    "-threads", "4",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format",
        "-of", "json", str(path),
    ]))


def valid_video(path: Path, frames: int) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        data = probe(path)
        video = next(s for s in data["streams"] if s["codec_type"] == "video")
        return (
            int(video["width"]) == W
            and int(video["height"]) == H
            and int(video.get("nb_frames", -1)) == frames
            and not any(s["codec_type"] == "audio" for s in data["streams"])
        )
    except Exception:
        return False


def motion_sources(seconds: int, amps: tuple[float, float, float, float]) -> list[str]:
    ax1, ax2, ay1, ay2 = amps
    xexpr = (
        f"128+{ax1}*sin(X/4.5+Y/8.5-N*0.029317)"
        f"+{ax2}*sin(X/10.5-Y/6.5+N*0.011173)"
    )
    yexpr = (
        f"128+{ay1}*sin(Y/2-N*0.057421+0.3*sin(X/11.5))"
        f"+{ay2}*sin(Y/5.5+X/15.5-N*0.019037)"
    )
    return [
        "-f", "lavfi", "-t", str(seconds), "-i",
        f"nullsrc=s=240x135:r={FPS},geq=lum='{xexpr}'",
        "-f", "lavfi", "-t", str(seconds), "-i",
        f"nullsrc=s=240x135:r={FPS},geq=lum='{yexpr}'",
    ]


def render_scene(scene: dict, status: dict, lock: threading.Lock) -> Path:
    output = HERE / f"{scene['name']}.mp4"
    expected = scene["seconds"] * FPS
    if valid_video(output, expected):
        with lock:
            print(f"SKIP valid {output.name}", flush=True)
        return output

    seconds = scene["seconds"]
    args = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-framerate", str(FPS), "-t", str(seconds), "-i", str(scene["image"]),
        "-loop", "1", "-framerate", str(FPS), "-t", str(seconds), "-i", str(scene["mask"]),
        *motion_sources(seconds, scene["amps"]),
    ]
    if scene["cta"]:
        args += ["-loop", "1", "-framerate", str(FPS), "-t", "69", "-i", str(CTA_IMAGE)]

    if STILL:
        # ★波の揺れ（displace）は本人が「表現がイマイチ」と判断したので静止画にした（2026-10-28）
        filters = ["[0:v]format=yuv420p[moved]"]
        out_label = "[moved]"
        if scene["cta"]:
            filters += [
                "[1:v]format=rgba,fade=t=in:st=60:d=1:alpha=1,"
                "fade=t=out:st=67:d=1:alpha=1[cta]",
                "[moved][cta]overlay=0:0:eof_action=pass[out]",
            ]
            out_label = "[out]"
        return _encode_scene(scene, output, expected, args_still(scene), filters, out_label, status, lock)

    rx, ry, rw, rh = scene.get("roi") or _roi(scene["mask"])
    # yuv420p の crop は位置と寸法を偶数に丸める。奇数のままだと映像側だけ 1px 縮み、
    # 変形の地図（scale で指定寸法ちょうど）と合わずに displace が止まる（場面3の 235px で発生）。
    # 位置は偶数へ切り下げ、寸法は偶数へ切り上げて、範囲が元より狭くならないようにする。（Claude 2026-09-30）
    rw, rh = rw + (rx % 2) + (rw + (rx % 2)) % 2, rh + (ry % 2) + (rh + (ry % 2)) % 2
    rx, ry = rx - rx % 2, ry - ry % 2
    rw, rh = min(rw, W - rx), min(rh, H - ry)
    filters = [
        "[0:v]format=yuv420p,split[full][forroi]",
        f"[forroi]crop={rw}:{rh}:{rx}:{ry},split[roi_base][roi_warp]",
        f"[2:v]scale={rw}:{rh}:flags=bicubic,format=gray[xmap]",
        f"[3:v]scale={rw}:{rh}:flags=bicubic,format=gray[ymap]",
        "[roi_warp][xmap][ymap]displace=edge=mirror[warped]",
        f"[1:v]format=gray,crop={rw}:{rh}:{rx}:{ry}[mask]",
        "[roi_base][warped][mask]maskedmerge[moved_roi]",
        f"[full][moved_roi]overlay={rx}:{ry}[moved]",
    ]
    out_label = "[moved]"
    if scene["cta"]:
        filters += [
            "[4:v]format=rgba,fade=t=in:st=60:d=1:alpha=1,"
            "fade=t=out:st=67:d=1:alpha=1[cta]",
            "[moved][cta]overlay=0:0:eof_action=pass[out]",
        ]
        out_label = "[out]"

    return _encode_scene(scene, output, expected, args, filters, out_label, status, lock)


def args_still(scene: dict) -> list[str]:
    seconds = scene["seconds"]
    args = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-framerate", str(FPS), "-t", str(seconds), "-i", str(scene["image"]),
    ]
    if scene["cta"]:
        args += ["-loop", "1", "-framerate", str(FPS), "-t", "69", "-i", str(CTA_IMAGE)]
    return args


def _encode_scene(scene, output, expected, args, filters, out_label, status, lock) -> Path:
    seconds = scene["seconds"]
    log_path = HERE / f"{scene['name']}.log"
    args += [
        "-filter_complex_threads", "2", "-filter_complex", ";".join(filters),
        "-map", out_label, "-an", "-t", str(seconds), *ENCODE,
        "-movflags", "+faststart", "-progress", "pipe:1", "-nostats", str(output),
    ]

    start = time.monotonic()
    with log_path.open("w") as log:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=log, text=True, bufsize=1)
        assert proc.stdout is not None
        last_report = 0.0
        for line in proc.stdout:
            if line.startswith("out_time="):
                raw = line.split("=", 1)[1].strip()
                fields = raw.split(":")
                if len(fields) != 3:
                    continue
                hh, mm, ss = fields
                done = int(hh) * 3600 + int(mm) * 60 + float(ss)
                now = time.monotonic()
                with lock:
                    status[scene["name"]] = (done, seconds)
                    if now - last_report >= 30:
                        print(f"PROGRESS {scene['name']} {done:.1f}/{seconds}s", flush=True)
                        last_report = now
        code = proc.wait()
    if code != 0 or not valid_video(output, expected):
        raise RuntimeError(f"scene render failed: {scene['name']} code={code}; see {log_path}")
    with lock:
        print(f"DONE {scene['name']} wall={time.monotonic() - start:.1f}s", flush=True)
    return output


def run_quiet(args: list[str], log_name: str) -> None:
    with (HERE / log_name).open("w") as log:
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=log, check=True)


def make_card() -> Path:
    output = HERE / "05_エンドカード_22s_無音.mp4"
    if valid_video(output, 22 * FPS):
        return output
    args = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-loop", "1", "-framerate", str(FPS), "-t", "22", "-i", str(CARD_IMAGE),
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},format=yuv420p",
        "-an", "-t", "22", *ENCODE, "-movflags", "+faststart", str(output),
    ]
    run_quiet(args, "05_エンドカード_22s_無音.log")
    if not valid_video(output, 22 * FPS):
        raise RuntimeError("card render failed")
    return output


def cut_copy(src: Path, start: int, seconds: int, output: Path) -> None:
    frames = seconds * FPS
    if valid_video(output, frames):
        return
    run_quiet([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        # ★-t だと区切りの外の2フレームまで拾う（01_body_1205 が 36152 フレームになった）。
        #   場面は GOP 30（1秒ごとに閉じたキーフレーム）なので、フレーム数で切れば正確。（Claude 2026-09-30）
        "-ss", str(start), "-i", str(src), "-frames:v", str(frames),
        "-map", "0:v:0", "-an", "-c:v", "copy",
        "-avoid_negative_ts", "make_zero", str(output),
    ], f"part_{output.stem}.log")
    if not valid_video(output, frames):
        raise RuntimeError(f"copy cut frame mismatch: {output}")


def transition(a: Path, a_start: int, b: Path, b_start: int, seconds: int, output: Path) -> None:
    frames = seconds * FPS
    if valid_video(output, frames):
        return
    args = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-ss", str(a_start), "-t", str(seconds), "-i", str(a),
        "-ss", str(b_start), "-t", str(seconds), "-i", str(b),
        "-filter_complex_threads", "2",
        "-filter_complex",
        f"[0:v]settb=AVTB,setpts=PTS-STARTPTS[a];"
        f"[1:v]settb=AVTB,setpts=PTS-STARTPTS[b];"
        f"[a][b]xfade=transition=fade:duration={seconds}:offset=0,format=yuv420p[out]",
        "-map", "[out]", "-an", "-t", str(seconds), *ENCODE,
        "-movflags", "+faststart", str(output),
    ]
    run_quiet(args, f"part_{output.stem}.log")
    if not valid_video(output, frames):
        raise RuntimeError(f"transition frame mismatch: {output}")


def assemble(scene_paths: list[Path], card: Path) -> Path:
    PARTS.mkdir(parents=True, exist_ok=True)
    # 場面 1130/1125/560/838 秒・15秒ディゾルブ・末尾カード（2秒ディゾルブ＋20秒）＝3608秒
    specs = [
        ("body", scene_paths[0], 0, 1115, "01_body_1115.mp4"),
        ("xf", scene_paths[0], 1115, scene_paths[1], 0, 15, "02_xfade_15.mp4"),
        ("body", scene_paths[1], 15, 1095, "03_body_1095.mp4"),
        ("xf", scene_paths[1], 1110, scene_paths[2], 0, 15, "04_xfade_15.mp4"),
        ("body", scene_paths[2], 15, 530, "05_body_530.mp4"),
        ("xf", scene_paths[2], 545, scene_paths[3], 0, 15, "06_xfade_15.mp4"),
        ("body", scene_paths[3], 15, 801, "07_body_801.mp4"),
        ("xf", scene_paths[3], 816, card, 0, 2, "08_card_xfade_2.mp4"),
        ("body", card, 2, 20, "09_card_body_20.mp4"),
    ]
    outputs: list[Path] = []
    for spec in specs:
        if spec[0] == "body":
            _, src, start, seconds, name = spec
            out = PARTS / name
            cut_copy(src, start, seconds, out)
        else:
            _, a, a_start, b, b_start, seconds, name = spec
            out = PARTS / name
            transition(a, a_start, b, b_start, seconds, out)
        outputs.append(out)

    concat_file = PARTS / "concat.txt"
    concat_file.write_text("".join(f"file '{p.resolve()}'\n" for p in outputs))
    if FINAL.exists():
        FINAL.unlink()
    run_quiet([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "concat", "-safe", "0", "-i", str(concat_file),
        "-map", "0:v:0", "-an", "-c:v", "copy", "-movflags", "+faststart", str(FINAL),
    ], "concat.log")
    if not valid_video(FINAL, TOTAL * FPS):
        raise RuntimeError("final frame count or stream validation failed")
    return FINAL


def main() -> None:
    global STILL, FINAL, PARTS
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--still", action="store_true", help="波を揺らさず静止画で作る（v02）")
    args = parser.parse_args()
    if args.still:
        STILL = True
        FINAL = HERE / "SOJ09_晩秋の浜辺_3608秒_無音_静止.mp4"
        PARTS = HERE / "_parts_静止"
        for s in SCENES:
            s["name"] += "_静止"
    report_name = "検品結果_静止.json" if STILL else "検品結果.json"
    required = [CARD_IMAGE, CTA_IMAGE, *[s["image"] for s in SCENES], *[s["mask"] for s in SCENES]]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise FileNotFoundError(missing)

    status: dict = {}
    lock = threading.Lock()
    scene_paths: dict[str, Path] = {}
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(render_scene, scene, status, lock): scene for scene in SCENES}
        for future in as_completed(futures):
            scene = futures[future]
            scene_paths[scene["name"]] = future.result()

    ordered = [scene_paths[s["name"]] for s in SCENES]
    card = make_card()
    final = assemble(ordered, card)

    subprocess.run([
        "ffmpeg", "-v", "error", "-xerror", "-i", str(final), "-f", "null", "-",
    ], check=True)
    data = probe(final)
    report = {
        "status": "silent_release_candidate_pending_human_full_view",
        "file": str(final),
        "sha256": sha256(final),
        "duration_seconds": float(data["format"]["duration"]),
        "frames": int(next(s for s in data["streams"] if s["codec_type"] == "video")["nb_frames"]),
        "resolution": f"{W}x{H}",
        "fps": FPS,
        "audio_streams": sum(s["codec_type"] == "audio" for s in data["streams"]),
        "scene_intermediates": [str(p) for p in ordered],
        "scene_intervals_seconds": [[0, 1130], [1115, 2240], [2225, 2785], [2770, 3608]],
        "scene_dissolves_seconds": [[1115, 1130], [2225, 2240], [2770, 2785]],
        "card_dissolve_seconds": [3586, 3588],
        "card_full_seconds": [3588, 3608],
        "cta_seconds": [60, 68],
        "motion": "none (still images)" if STILL else "water masks only; four incommensurate temporal phases; amplitudes reduced by distance in scenes 3 and 4",
        "full_decode": "passed",
        "pending": ["human full visual review", "audio mux by Claude"],
        "file_bytes": final.stat().st_size,
    }
    (HERE / report_name).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
