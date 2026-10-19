#!/usr/bin/env python3
"""v2で作り直した完成MP4を測る（2026-09-21）。

見るのは6つ。

1. 尺・フレーム数・解像度・音声ストリーム
2. ラウドネス・トゥルーピーク・LRA・2秒以上の無音
3. **単調さ**（周期の山と10分ブロックの幅）— v1で見落とした指標
4. **AAC後の左右信号**（設計値の±0.8Hzを0.005Hz刻みで探索し、実測周波数を出す）
5. 場面の輝度と、場面転換（12秒差で見る）
6. SHA-256
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SSD = Path("/Volumes/ESD-EPB/BGM/4_Waves of Japan")
TARGETS = {
    # ★ESD-EPBが外れているときは、内蔵の作業フォルダを見る（先に見つかったほうを使う）
    "wave11": HERE.parent / "WAVE11_雪の無人駅" / "本編映像" / "wave11_雪の無人駅_3時間.mp4",
    "wave10": HERE.parent / "WAVE10_時雨の山寺" / "本編映像" / "wave10_時雨の山寺_3時間.mp4",
    "wave09": HERE.parent / "WAVE09_天の川の高原" / "本編映像" / "wave09_天の川の高原_3時間.mp4",
    "wave08": HERE.parent / "WAVE08_朝顔の垣根" / "本編映像" / "wave08_朝顔の垣根_3時間.mp4",
    "wave07": HERE.parent / "WAVE07_月夜の芒原" / "本編映像" / "wave07_月夜の芒原_3時間.mp4",
    "wave06": SSD / "WAVE06_素材_花明かりの丘" / "wave06_花明かりの丘_3時間_v2.mp4",
    "wave05": SSD / "WAVE05_素材_雪明かりの書院" / "wave05_雪明かりの書院_3時間_v2.mp4",
}

spec = importlib.util.spec_from_file_location("kit", HERE / "連続合成.py")
KIT = importlib.util.module_from_spec(spec)
sys.modules["kit"] = KIT
spec.loader.exec_module(KIT)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size:stream=codec_name,codec_type,width,height,"
         "r_frame_rate,nb_frames,sample_rate,channels", "-of", "json", str(path)],
        check=True, capture_output=True, text=True).stdout
    return json.loads(out)


def full_scan(path: Path) -> dict:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
         "silencedetect=n=-55dB:d=2,loudnorm=I=-16.5:TP=-2.5:LRA=7:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True, check=True)
    data = json.loads(re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, re.S)[-1])
    return {"integrated_lufs": float(data["input_i"]),
            "true_peak_dbtp": float(data["input_tp"]),
            "lra_lu": float(data["input_lra"]),
            "silence_events": result.stderr.count("silence_start")}


def monotony(path: Path, rate: int = 2_000) -> dict:
    # ★2kHzモノラルで読む（原寸だと3時間で4.15GBをメモリに載せることになる）
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
                          "-ar", str(rate), "-f", "f32le", "-acodec", "pcm_f32le", "-"],
                         check=True, stdout=subprocess.PIPE).stdout
    samples = np.frombuffer(raw, dtype="<f4").reshape(-1, 1)
    return KIT.envelope_metrics(samples, rate)


def chunk_seams(path: Path, chunk: float = 300.0, rate: int = 2_000) -> dict:
    """★書き出しの単位の境界に欠落が無いかを名指しで測る。

    2026-09-21、FLACを `-c copy` で連結していたため300秒ごとに0.25秒の欠落が入り、
    3時間で35回のしゃっくりになっていた。既存の検品（尺・音量・無音2秒・左右信号）は
    どれも通ってしまい、単調さの指標に「300秒の山」として出て初めて気づいた。
    **合成を部分に分けて書く限り、この項目は必ず見ること。**
    """
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
                          "-ar", str(rate), "-f", "f32le", "-acodec", "pcm_f32le", "-"],
                         check=True, stdout=subprocess.PIPE).stdout
    x = np.frombuffer(raw, dtype="<f4")
    step = rate // 4
    n = len(x) // step
    envelope = 20 * np.log10(np.sqrt((x[:n * step].reshape(n, step) ** 2).mean(axis=1)) + 1e-9)
    per_second = rate / step
    drops = []
    for boundary in np.arange(chunk, len(envelope) / per_second - chunk, chunk):
        index = int(boundary * per_second)
        around = np.concatenate([envelope[index - 40:index - 4],
                                 envelope[index + 8:index + 44]]).mean()
        at = envelope[index - 2:index + 4].min()
        drops.append(float(around - at))
    return {"chunk_seconds": chunk, "seams": len(drops),
            "worst_drop_db": round(max(drops), 2) if drops else None,
            "median_drop_db": round(float(np.median(drops)), 2) if drops else None,
            "verdict": "欠落なし" if drops and max(drops) < 4.0 else "要確認"}


def frames(path: Path, times: list[float]) -> list[Image.Image]:
    out = []
    for t in times:
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1",
             "-f", "image2pipe", "-vcodec", "png", "-"],
            check=True, stdout=subprocess.PIPE).stdout
        out.append(Image.open(io.BytesIO(raw)).convert("RGB"))
    return out


def main() -> None:
    # ★既存の記録を残す。SSDが外れていると見つからない巻が出るので、
    #   毎回まっさらにすると前回の巻の検品が消える。
    out_path = HERE / "v2_完成検品.json"
    report = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    # 巻を指定したらその巻だけ（3時間の検品は1巻20分ほどかかるので、既刊を毎回やり直さない）
    wanted = set(sys.argv[1:]) or set(TARGETS)
    for volume, path in TARGETS.items():
        if volume not in wanted:
            continue
        if not path.exists():
            print(f"{volume}: まだありません"); continue
        print(f"=== {volume} ===", flush=True)
        cfg = KIT.VOLUMES[volume]
        scene_times = [960.0, 2_940.0, 5_040.0, 7_260.0, 9_600.0]
        shots = frames(path, scene_times + [1_914.0, 1_920.0, 1_926.0, 10_790.0])
        luminance = [round(float(np.asarray(im.convert("L"), dtype=np.float32).mean()), 1)
                     for im in shots[:5]]
        sheet = Image.new("RGB", (480 * 5, 270), (0, 0, 0))
        for index, im in enumerate(shots[:5]):
            sheet.paste(im.resize((480, 270)), (index * 480, 0))
        folder = HERE.parent / cfg["dir"] / "検品"
        folder.mkdir(parents=True, exist_ok=True)
        sheet.save(folder / "v2_完成_5場面.jpg", quality=92)
        transition = Image.new("RGB", (480 * 3, 270), (0, 0, 0))
        for index, im in enumerate(shots[5:8]):
            transition.paste(im.resize((480, 270)), (index * 480, 0))
        transition.save(folder / "v2_完成_転換12秒差.jpg", quality=92)
        shots[8].resize((480, 270)).save(folder / "v2_完成_エンドカード.jpg", quality=92)
        # 登録のお願い（1:00〜1:08）。出ていることを目で見るための1枚
        frames(path, [64.0])[0].save(folder / "v2_完成_登録のお願い_1分04秒.jpg", quality=92)

        report[volume] = {
            "file": str(path), "bytes": path.stat().st_size,
            "sha256": sha256(path), "probe": probe(path),
            "audio": full_scan(path), "monotony": monotony(path),
            "chunk_seams": chunk_seams(path),
            "beat_after_aac": KIT.verify_beat(cfg, path),
            "scene_luminance": luminance,
        }
        a = report[volume]["audio"]
        m = report[volume]["monotony"]
        print(f"  {a['integrated_lufs']} LUFS / TP {a['true_peak_dbtp']} / "
              f"LRA {a['lra_lu']} / 無音 {a['silence_events']}件", flush=True)
        c = report[volume]["chunk_seams"]
        print(f"  300秒境界の欠落: 最大 {c['worst_drop_db']}dB / "
              f"中央値 {c['median_drop_db']}dB → {c['verdict']}", flush=True)
        print(f"  周期の山 {m['strongest_period_height']:+.3f} @ "
              f"{m['strongest_period_seconds']}秒 / 10分幅 "
              f"{m['ten_minute_block_spread_db']}dB", flush=True)
        for row in report[volume]["beat_after_aac"]:
            print(f"  {row['position_seconds']:6.0f}秒 "
                  f"L {row['left_measured_hz']:.3f} R {row['right_measured_hz']:.3f} "
                  f"差 {row['measured_difference_hz']:.3f}Hz "
                  f"分離 {min(row['left_separation_db'], row['right_separation_db']):.1f}dB",
                  flush=True)
    out = out_path
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
