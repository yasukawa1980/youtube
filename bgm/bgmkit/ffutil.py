"""ffmpeg / ffprobe の薄いラッパと、全モジュール共通の小道具。"""
import json
import os
import re
import subprocess
import sys

import numpy as np


def run(args, check=False):
    """ffmpeg系を呼んで CompletedProcess を返す（stderrもテキストで取る）。"""
    r = subprocess.run(args, capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.stderr.write(r.stderr[-4000:])
        raise SystemExit(f"失敗: {' '.join(args[:3])}...")
    return r


def ff(args, check=True):
    """進捗表示を抑えた ffmpeg 実行。"""
    return run(["ffmpeg", "-y", "-nostats", "-v", "warning"] + args, check=check)


def duration(path):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path])
    return float(r.stdout.strip())


def pcm_mono(path, sr):
    """モノラルf32で丸ごとデコードして numpy 配列にする。"""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1",
                        "-ar", str(sr), "-f", "f32le", "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.float32)


def audio_md5(path):
    """デコード後のMD5。Sunoは同じ曲を別名で吐くのでファイル名では重複を判別できない。"""
    r = run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a",
             "-f", "md5", "-"])
    return r.stdout.strip().replace("MD5=", "")


def measure_loudness(path, cfg, ss=None, t=None):
    """loudnorm の1パス目。measured_* 一式を dict で返す。"""
    args = ["-nostats"]
    if ss is not None:
        args += ["-ss", f"{ss}"]
    if t is not None:
        args += ["-t", f"{t}"]
    args += ["-i", path, "-af",
             f"loudnorm=I={cfg['target_lufs']}:TP={cfg['true_peak']}"
             f":LRA={cfg['lra']}:print_format=json", "-f", "null", "-"]
    r = run(["ffmpeg"] + args)
    m = re.search(r"\{[^{}]*input_i[^{}]*\}", r.stderr, re.S)
    if not m:
        raise SystemExit(f"loudnorm の測定に失敗: {os.path.basename(path)}")
    return json.loads(m.group(0))


def silence_bounds(path, dur, cfg):
    """頭と尻の無音を検出して、切り出す [head, tail] を返す。

    頭は cfg['head_pad'] 秒だけ残す（いきなり鳴り始めると不自然なため）。
    尻は最後の無音の始まりに cfg['tail_pad'] 秒足したところで切る。
    """
    r = run(["ffmpeg", "-nostats", "-i", path, "-af",
             f"silencedetect=n={cfg['silence_thresh_db']}dB:d={cfg['silence_min']}",
             "-f", "null", "-"])
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    head = max(0.0, en[0] - cfg["head_pad"]) if (st and st[0] < 0.1 and en) else 0.0
    tail = dur
    if st and st[-1] > dur - 6 and (not en or en[-1] >= dur - 0.05):
        tail = min(dur, st[-1] + cfg["tail_pad"])
    return head, tail


def mmss(sec):
    return f"{int(sec) // 60:02d}:{int(sec) % 60:02d}"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
