"""IRO LIVE01：IRO12 の本編から、ライブでループさせる2時間の素材を作る。

本編（iro12_完成.mp4）との違い：
- 頭の OPEN 4.2秒（無音・タイマーなし＝扉ムービー用の間）を外す → 0秒目から「FOCUS 1 / 4 25:00」
- 作業1の頭にも「上がる2音」のチャイムを足す（作業2〜4と同じ）→ ループの継ぎ目が普段の 休憩→作業 と同じになる
- 最後の終了画面（空の「次の動画」枠つき）を乗せない
- 音の最後の仕上げ（192kHz で見るリミッター）は本編と同じ

  python3 ループ素材を作る.py          ループ素材（7200秒）
  python3 ループ素材を作る.py seam     継ぎ目の確認用（尾60秒＋頭60秒）
"""
import os, sys, subprocess
import numpy as np

SR, FPS = 48000, 24
IRO12 = "/Volumes/ESD-02/IRO/IRO12_素材_ポモドーロ2時間/_work"
UNIT, BED, TDIR = IRO12 + "/unit.mp4", IRO12 + "/music_bed.wav", IRO12 + "/timer"
OUTD = "/Volumes/ESD-02/IRO/IRO_LIVE01"
OPEN, T = 4.2, 7200
TBOX = (70, 60)
LOOP = OUTD + "/iro12_ライブ用ループ_2時間.mp4"


# 音を組む.py（IRO12）と同じベル
def bell(freq, dur=3.2):
    t = np.arange(int(dur * SR)) / SR
    y = np.zeros_like(t)
    for ratio, amp, dec in ((1.0, 1.0, 1.6), (2.0, 0.35, 1.0), (2.76, 0.18, 0.7), (4.07, 0.07, 0.45)):
        y += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / dec)
    y *= np.minimum(1, t / 0.004)
    return y.astype(np.float32)


def chime_up():
    y = np.zeros(int(4.2 * SR), np.float32)
    b1, b2 = bell(659.25), bell(987.77)
    y[: len(b1)] += b1
    o = int(0.55 * SR); y[o:o + len(b2)] += b2 * 0.9
    y /= np.abs(y).max()
    y *= 10 ** (-15 / 20)
    return np.stack([y, y], axis=1)


def make_bed():
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(OPEN), "-i", BED, "-t", str(T),
                        "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(r, np.float32).reshape(-1, 2).copy()
    assert abs(len(x) / SR - T) < 0.01, len(x) / SR
    c = chime_up(); x[: len(c)] += c
    raw = OUTD + "/_bed.f32"; x.tofile(raw)
    out = OUTD + "/_bed_loop.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw,
                    "-af", "alimiter=limit=0.794:attack=3:release=60:level=0", "-c:a", "pcm_s24le", out], check=True)
    os.remove(raw)
    return out


def cmd_loop():
    os.makedirs(OUTD, exist_ok=True)
    bed = make_bed(); print("音:", bed, flush=True)
    lst = OUTD + "/_bg_list.txt"; open(lst, "w").write(f"file '{UNIT}'\n" * 4)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stats",
                    "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", bed,
                    "-framerate", "1", "-i", TDIR + "/%05d.png",
                    "-filter_complex",
                    f"[0:v]setpts=PTS-STARTPTS[bg];[2:v]fps={FPS},format=rgba[tm];"
                    f"[bg][tm]overlay={TBOX[0]}:{TBOX[1]}:eof_action=pass,format=yuv420p[v];"
                    f"[1:a]aresample=192000,alimiter=limit=0.5:attack=1:release=60:level=false,aresample=48000,volume=0.5dB[a]",
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "h264_videotoolbox", "-q:v", "85", "-profile:v", "high", "-g", str(FPS * 2),
                    "-r", str(FPS), "-c:a", "aac", "-b:a", "320k", "-t", str(T), "-movflags", "+faststart", LOOP], check=True)
    os.remove(bed)
    print("書き出し:", LOOP)


def cmd_seam():
    """ループの継ぎ目を ffmpeg でつないで聞く・見る用（尾60秒→頭60秒）"""
    out = OUTD + "/継ぎ目の確認_尾60秒_頭60秒.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-sseof", "-60", "-i", LOOP, "-t", "60", "-i", LOOP,
                    "-filter_complex", "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "h264_videotoolbox", "-q:v", "80",
                    "-c:a", "aac", "-b:a", "256k", out], check=True)
    print(out)


{"seam": cmd_seam}.get(sys.argv[1] if len(sys.argv) > 1 else "", cmd_loop)()
