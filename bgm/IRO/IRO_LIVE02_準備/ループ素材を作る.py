"""IRO LIVE02：IRO11 の素材から、OBS でループさせる素材（1時間40分）を作る。

- 絵：IRO11 の単位 unit.mp4（25分・頭と尻が同じ絵）を4回つなぐ＝6001秒。再エンコードしない（-c:v copy）
- 音：music_bed.wav（41曲・7182秒）の先頭6001秒。ループの継ぎ目（尾→頭）が切れないように、
  頭の6秒に「6001秒目から先の6秒（フェードアウト）」を等電力で重ねる。
  → 尾は bed[6001) の直前で終わり、頭は bed[6001〜] のフェードアウト＋bed[0〜] のフェードインで始まる＝つながる
- 音の仕上げは本編（画面とサムネを作る.py final）と同じ：192kHz で見るリミッター＋0.5dB
- 終了画面・オープニング・扉ムービーは入れない

  python3 ループ素材を作る.py          ループ素材
  python3 ループ素材を作る.py seam     継ぎ目の確認用（尾60秒＋頭60秒）
"""
import os, sys, subprocess
import numpy as np

SR = 48000
W = "/Volumes/ESD-02/IRO/IRO11_素材_Lofi2時間/_work"
UNIT, BED = W + "/unit.mp4", W + "/music_bed.wav"
OUTD = "/Volumes/ESD-02/IRO/IRO_LIVE02"
N, D = 4, 6.0
LOOP = OUTD + "/iro11_ライブ用ループ_1時間40分.mp4"


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                capture_output=True, text=True).stdout)


def read(s, d):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(s), "-t", str(d), "-i", BED, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                       capture_output=True, check=True).stdout
    return np.frombuffer(r, np.float32).reshape(-1, 2).copy()


def cmd_loop():
    os.makedirs(OUTD, exist_ok=True)
    T = N * dur(UNIT)                                   # 6001.0
    n, nd = int(round(T * SR)), int(D * SR)
    x = read(0, T)[:n]
    assert len(x) == n, (len(x), n)
    tail = read(T, D)[:nd]
    th = np.linspace(0, np.pi / 2, nd, dtype=np.float32)[:, None]
    x[:nd] = x[:nd] * np.sin(th) + tail * np.cos(th)    # 等電力
    raw = OUTD + "/_bed.f32"; x.tofile(raw)
    lst = OUTD + "/_unit_list.txt"; open(lst, "w").write(f"file '{UNIT}'\n" * N)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stats",
                    "-f", "concat", "-safe", "0", "-i", lst,
                    "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw,
                    "-filter_complex", "[1:a]aresample=192000,alimiter=limit=0.5:attack=1:release=60:level=false,aresample=48000,volume=0.5dB[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "320k",
                    "-t", f"{T:.3f}", "-movflags", "+faststart", LOOP], check=True)
    os.remove(raw); os.remove(lst)
    print("書き出し:", LOOP, "長さ", T)


def cmd_seam():
    out = OUTD + "/継ぎ目の確認_尾60秒_頭60秒.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-sseof", "-60", "-i", LOOP, "-t", "60", "-i", LOOP,
                    "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "h264_videotoolbox", "-q:v", "80",
                    "-c:a", "aac", "-b:a", "256k", out], check=True)
    print(out)


{"seam": cmd_seam}.get(sys.argv[1] if len(sys.argv) > 1 else "", cmd_loop)()
