#!/usr/bin/env python3
"""静止画5場面＋ディゾルブだけで3時間の本編映像を作る（2026-09-21）。

**粒子（雪・花びら）は使わない。** 本人の判断で、WAVE05の雪が
「縁の硬い灰色の円と白い短い線を貼っただけ」に見えたため、全部やめた。
動きを足す場合は別途Codexへ回す。

粒子が無いので1フレームずつPythonで描く必要がない。ffmpegのxfadeだけで組めて、
書き出しは数分、ファイルは数百MBに収まる（花びら入りの旧版は3.69GBだった）。

場面の切り替えは開始時刻を中心とする10秒、末尾15秒が共通エンドカード（2秒で入る）。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from bgmkit.config import CTA_TEXT            # noqa: E402
from bgmkit.video import CTA_DEFAULT, _fade_over, _text_png   # noqa: E402

FPS = 30
SIZE = (1920, 1080)
TOTAL = 10_800.0
SCENE_STARTS = (0.0, 1_920.0, 3_960.0, 6_120.0, 8_400.0)
TRANSITION = 10.0
CARD_SECONDS = 15.0
CARD_XFADE = 2.0

VOLUMES = {
    "wave11": {
        "dir": "WAVE11_雪の無人駅",
        # ★ホームの灯りと待合室の窓は小さく明るい孤立物。5枚とも第3場面（基準画像）と同じ位置であること
        "images": ("wave11_01_暮れ方の雪.png", "wave11_02_灯のともる駅.png",
                   "wave11_03_雪の止んだ夜.png", "wave11_04_夜更けの雪明かり.png",
                   "wave11_05_未明の青.png"),
        "scenes": ("暮れ方の雪", "灯のともる駅", "雪の止んだ夜", "夜更けの雪明かり", "未明の青"),
        "output": "wave11_雪の無人駅_3時間.mp4",
        "cta": True,
    },
    "wave10": {
        "dir": "WAVE10_時雨の山寺",
        # ★石灯籠の火袋は小さく明るい孤立物。5枚とも第3場面（基準画像）と同じ位置であること
        "images": ("wave10_01_夕暮れの時雨.png", "wave10_02_灯ともし頃.png",
                   "wave10_03_雨上がりの山門.png", "wave10_04_夜更けの霧.png",
                   "wave10_05_未明の静けさ.png"),
        "scenes": ("夕暮れの時雨", "灯ともし頃", "雨上がりの山門", "夜更けの霧", "未明の静けさ"),
        "output": "wave10_時雨の山寺_3時間.mp4",
        "cta": True,
    },
    "wave09": {
        "dir": "WAVE09_天の川の高原",
        # ★空は5枚とも第3場面（基準画像）の空から作る。星の位置は構造上0画素で揃う
        "images": ("wave09_01_宵の天の川.png", "wave09_02_夜半の高原.png",
                   "wave09_03_満天.png", "wave09_04_未明の静けさ.png",
                   "wave09_05_薄明.png"),
        "scenes": ("宵の天の川", "夜半の高原", "満天", "未明の静けさ", "薄明"),
        "output": "wave09_天の川の高原_3時間.mp4",
        "cta": True,
    },
    "wave08": {
        "dir": "WAVE08_朝顔の垣根",
        "images": ("wave08_01_未明の藍.png", "wave08_02_蕾の垣根.png",
                   "wave08_03_ほどける花.png", "wave08_04_朝露.png",
                   "wave08_05_朝の光.png"),
        "scenes": ("未明の藍", "蕾の垣根", "ほどける花", "朝露", "朝の光"),
        "output": "wave08_朝顔の垣根_3時間.mp4",
        "cta": True,     # ★2026/9/28決定。WAVE08から入れる（既刊は1画素も変えない）
    },
    "wave07": {
        "dir": "WAVE07_月夜の芒原",
        "images": ("wave07_01_月の出.png", "wave07_02_宵の芒原.png",
                   "wave07_03_夜半の月.png", "wave07_04_未明前の風.png",
                   "wave07_05_薄明の露.png"),
        "scenes": ("月の出", "宵の芒原", "夜半の月", "未明前の風", "薄明の露"),
        "output": "wave07_月夜の芒原_3時間.mp4",
    },
    "wave06": {
        "dir": "WAVE06_花明かりの丘",
        "images": ("wave06_01_宵の花明かり.png", "wave06_02_花の帳.png",
                   "wave06_03_深夜の風.png", "wave06_04_花散らしの静けさ.png",
                   "wave06_05_未明の薄青.png"),
        "scenes": ("宵の花明かり", "花の帳", "深夜の風", "花散らしの静けさ", "未明の薄青"),
        "output": "wave06_花明かりの丘_3時間.mp4",
    },
    "wave05": {
        "dir": "WAVE05_雪明かりの書院",
        "images": ("wave05_01_deep_snow_night_v1.png", "wave05_02_snowfall_shoin_v1.png",
                   "wave05_03_snowlight_v1.png", "wave05_04_shinonome_v1.png",
                   "wave05_05_morning_white_v1.png"),
        "scenes": ("深雪の夜", "雪降る書院", "雪明かり", "東雲", "朝白"),
        "output": "wave05_雪明かりの書院_3時間.mp4",
    },
}
CARD = "WAVE05_雪明かりの書院/画像/エンドカード_waves.png"


class _TextCfg(dict):
    """bgmkit の `_text_png` に渡すための最小の巻設定（出力の大きさと、下地にする1枚目だけ）。"""
    images_dir = ""


def cta_png(folder: Path, first_image: Path) -> Path:
    """登録のお願いを透明PNGに焼く。見た目は bgmkit の本編と同じ（左下・ヒラギノ明朝44px）。

    ★下地の明るさは1枚目の場面で測る（1:00は必ず第1場面の中）。明るければ濃紺に反転する。
    """
    cfg = _TextCfg(video={"output": list(SIZE)}, images=[str(first_image)])
    out = folder / "本編映像" / "_cta.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    return Path(_text_png(cfg, 0, CTA_TEXT["video"], dict(CTA_DEFAULT), str(out), "登録のお願い"))


def plan() -> tuple[list[float], list[tuple[float, float]]]:
    """各入力の長さと、xfadeの (開始時刻, 長さ) を出す。

    xfade は出力の時間軸で offset を数え、出力長は入力長の和から
    かぶった分を引いたものになる。合計がちょうど10,800秒になるよう逆算する。
    """
    half = TRANSITION / 2
    offsets = [start - half for start in SCENE_STARTS[1:]]          # 場面の転換
    card_start = TOTAL - CARD_SECONDS
    durations = []
    previous_offset = 0.0
    for index, offset in enumerate(offsets):
        if index == 0:
            durations.append(offset + TRANSITION)                    # 最初の入力
        else:
            durations.append(offset + TRANSITION - previous_offset)
        previous_offset = offset
    # 5枚目：カードの転換が始まる時刻まで
    durations.append(card_start + CARD_XFADE - previous_offset)
    durations.append(CARD_SECONDS)                                   # エンドカード
    transitions = [(offset, TRANSITION) for offset in offsets]
    transitions.append((card_start, CARD_XFADE))
    total = sum(durations) - sum(d for _, d in transitions)
    if abs(total - TOTAL) > 1e-6:
        raise RuntimeError(f"合計が10,800秒になりません: {total}")
    return durations, transitions


def build(volume: str, root: Path, out_path: Path, audio: Path | None) -> Path:
    cfg = VOLUMES[volume]
    folder = root / cfg["dir"]
    images = [folder / "画像" / name for name in cfg["images"]]
    for image in images:
        if not image.exists():
            raise SystemExit(f"画像がありません: {image}")
    card = root / CARD
    durations, transitions = plan()

    args = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    for image, seconds in zip(images + [card], durations):
        args += ["-loop", "1", "-t", f"{seconds:.6f}", "-i", str(image)]
    cta = cfg.get("cta")
    if cta:
        st = CTA_DEFAULT
        if st["at"] + 2 * st["fade"] + st["hold"] > SCENE_STARTS[1] - TRANSITION / 2:
            raise SystemExit("登録のお願いが第1場面の中に収まりません")
        # 出し終わる少し先までだけ読む。以後は eof_action=pass で素通しにする
        args += ["-loop", "1", "-t", f"{st['at'] + 2 * st['fade'] + st['hold'] + 1:.2f}",
                 "-i", str(cta_png(folder, images[0]))]
    audio_index = 7 if cta else 6
    if audio is not None:
        args += ["-i", str(audio)]

    filters = []
    for index in range(6):
        filters.append(
            f"[{index}:v]scale={SIZE[0]}:{SIZE[1]}:flags=lanczos,setsar=1,"
            f"fps={FPS},format=yuv420p[s{index}]"
        )
    previous = "[s0]"
    for index, (offset, duration) in enumerate(transitions, start=1):
        label = f"[x{index}]" if index < len(transitions) else "[v]"
        filters.append(
            f"{previous}[s{index}]xfade=transition=fade:duration={duration}:"
            f"offset={offset}{label}"
        )
        previous = label
    out_label = "[v]"
    if cta:
        st = CTA_DEFAULT
        filters.append(_fade_over(6, st["at"], st["fade"], st["hold"], "v", "cta",
                                  ov=":eof_action=pass") + "[vc]")
        out_label = "[vc]"
    args += ["-filter_complex", ";".join(filters), "-map", out_label]
    if audio is not None:
        args += ["-map", f"{audio_index}:a:0", "-c:a", "aac", "-b:a", "320k"]
    else:
        args += ["-an"]
    args += [
        "-t", f"{TOTAL:.6f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", str(FPS * 10),
        "-movflags", "+faststart", str(out_path),
    ]
    subprocess.run(args, check=True)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("volume", choices=sorted(VOLUMES))
    parser.add_argument("--audio", type=Path, help="同時に多重化する音声")
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    durations, transitions = plan()
    print("入力の長さ:", [round(d, 3) for d in durations])
    print("転換:", [(round(o, 1), d) for o, d in transitions])
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    path = build(arguments.volume, root, arguments.out, arguments.audio)
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size:stream=codec_name,codec_type,width,height,nb_frames",
         "-of", "json", str(path)], check=True, capture_output=True, text=True)
    print(json.dumps(json.loads(probe.stdout), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
