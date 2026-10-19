"""SOJ09：波の実録の性格を全編で測る。48kHz・ステレオでデコード。

  python3 SOJ09_制作/波の性格.py ファイル…

SOJ08 の「音の性格」「ピークで選び直した」を1本にまとめ、波に要る物差しを足した。
  - LUFS（全編）と、−17.6 に揃えたときの標本ピーク・99%点・−2.5dBFS超の秒数
    ★SOJ08 で TP +2.0 が出た原因は近接のしぶき。波の砕けも同じことが起きる
  - 重心・<300Hz・3-8kHz の割合（遠い波ほど重心が下がる＝弧の並べ方に使う）
  - 波の周期（包絡の自己相関の山）と、うねりの深さ（0.5秒包絡の 90%点−10%点）
    ★浅すぎると「ただのザー」、深すぎると砕けるたびに起こす
  - 風の吹かれ：<80Hz の1秒ごとの音量の跳ね（マイクの吹かれは低域だけが突然跳ねる）
  - 左右相関（中域）：実質モノラルを落とす
"""
import subprocess
import sys

import numpy as np
from scipy.signal import stft, butter, sosfilt

SR = 48000


def lufs(f):
    r = subprocess.run(["ffmpeg", "-nostats", "-i", f, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = r.rfind("Integrated loudness")
    return float(r[i:].split("I:")[1].split("LUFS")[0])


for f in sys.argv[1:]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "2", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, "<f4").reshape(-1, 2)
    dur = len(x) / SR
    L = lufs(f)
    g = 10 ** ((-17.6 - L) / 20)
    sec = np.abs(x[: int(dur) * SR]).max(1).reshape(-1, SR).max(1) * g
    pk = 20 * np.log10(sec + 1e-12)
    over = int((pk > -2.5).sum())

    m = x.mean(1)
    fr, t, Z = stft(m[::2], SR // 2, nperseg=2048, noverlap=1024)  # 24kHz で十分
    P = np.abs(Z) ** 2
    spec = P.mean(1)
    cen = (fr * spec).sum() / spec.sum()

    def share(lo, hi):
        k = (fr >= lo) & (fr < hi)
        return 100 * spec[k].sum() / spec.sum()

    # 波の包絡：200-4000Hz の音量を0.5秒ごと
    hop = t[1] - t[0]
    band = (fr >= 200) & (fr < 4000)
    e = P[band].sum(0)
    n = int(0.5 / hop)
    env = 10 * np.log10(e[: len(e) // n * n].reshape(-1, n).mean(1) + 1e-12)
    depth = np.percentile(env, 90) - np.percentile(env, 10)
    # 周期：60秒ならしを引いた包絡の自己相関で 4〜30秒の最大の山
    k60 = 120
    d = env - np.convolve(env, np.ones(k60) / k60, "same")
    d = d[k60:-k60] if len(d) > 3 * k60 else d
    d = d - d.mean()
    ac = np.correlate(d, d, "full")[len(d) - 1:]
    ac /= ac[0]
    lo, hi = 8, 60  # 0.5秒刻みで 4〜30秒
    j = lo + int(np.argmax(ac[lo:hi]))
    period, regular = j * 0.5, ac[j]

    # 風の吹かれ：<80Hz を1秒ごと、10秒中央値からの跳ね >8dB の秒数
    sos = butter(4, 80, "lowpass", fs=SR, output="sos")
    lw = sosfilt(sos, m)
    lw = 10 * np.log10((lw[: int(dur) * SR] ** 2).reshape(-1, SR).mean(1) + 1e-15)
    med = np.array([np.median(lw[max(0, i - 5): i + 5]) for i in range(len(lw))])
    gust = int((lw - med > 8).sum())

    # 左右相関（300-3000Hz）
    sos2 = butter(4, [300, 3000], "bandpass", fs=SR, output="sos")
    a, b = sosfilt(sos2, x[:, 0]), sosfilt(sos2, x[:, 1])
    corr = float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else 1.0

    name = f.split("/")[-1].replace("prev_", "").replace(".mp3", "")
    print(f"{name:8s} {dur/60:5.1f}分 {L:6.1f}LUFS  ピーク{pk.max():+5.1f} 99%{np.percentile(pk,99):+5.1f} 超{over:4d}秒  "
          f"重心{cen:5.0f}Hz <300 {share(0,300):4.1f}% 3-8k {share(3000,8000):4.1f}%  "
          f"周期{period:4.1f}s 規則{regular:4.2f} 深さ{depth:4.1f}dB  吹かれ{gust:3d}秒  LR{corr:5.2f}", flush=True)
