"""候補曲の計測と、同一生成の別テイク検出。

旧 analyze_tracks_vol*.py + check_duplicates_vol*.py。
結果は _work/analysis.json に落とし、選抜と曲順はそれを読む。
（旧版は print した表を正規表現で読み直していて、書式を変えると壊れた）

計測するもの:
  key       キー推定（Krumhansl-Schmuckler）
  I / TP    ラウドネスとトゥルーピーク
  breath    1-5kHz のスペクトル平坦度。息の目立つ笛で 0.05〜0.2。
            尺八は一致度だけで選ぶと純音に近い個体が勝つので、ここで足切りする。
  bright    8kHz以上 / 200-1000Hz のエネルギー比(dB)。
  sim       メルスペクトログラム系列のスライディング相関（全ペア）。
            平均クロマは全曲ドローン支配で 0.93〜0.99 に張り付き使えない。
            0.5以上=同一生成の別テイク / 0.3前後=やや近い / 0.2以下=別の曲。
"""
import itertools
import os

import numpy as np
from scipy.signal import correlate

from .ffutil import audio_md5, duration, measure_loudness, pcm_mono, save_json

SR = 22050
PITCH = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

N, HOP, NB = 2048, 1024, 40
DEC = 4                              # 時間方向の間引き → 実効ホップ約186ms
WIN = int(30 * SR / HOP / DEC)       # 30秒窓


def _melbank():
    f = np.fft.rfftfreq(N, 1 / SR)
    edges = np.linspace(2595 * np.log10(1 + 80 / 700),
                        2595 * np.log10(1 + 8000 / 700), NB + 2)
    hz = 700 * (10 ** (edges / 2595) - 1)
    B = np.zeros((NB, len(f)))
    for i in range(NB):
        lo, mid, hi = hz[i], hz[i + 1], hz[i + 2]
        l = (f >= lo) & (f <= mid)
        r = (f > mid) & (f <= hi)
        B[i, l] = (f[l] - lo) / (mid - lo + 1e-9)
        B[i, r] = (hi - f[r]) / (hi - mid + 1e-9)
    return B


MB = _melbank()


def _chroma(x, n=4096, hop=2048):
    f = np.fft.rfftfreq(n, 1 / SR)
    ok = (f > 55) & (f < 2000)
    midi = np.zeros_like(f)
    midi[ok] = 69 + 12 * np.log2(f[ok] / 440.0)
    cls = np.mod(np.round(midi).astype(int), 12)
    w = np.hanning(n)
    nf = max(0, (len(x) - n) // hop)
    C = np.zeros((nf, 12))
    for i in range(nf):
        S = np.abs(np.fft.rfft(x[i * hop:i * hop + n] * w))
        for c in range(12):
            C[i, c] = S[ok & (cls == c)].sum()
    C /= (C.sum(axis=1, keepdims=True) + 1e-9)
    return C


def _key_of(v):
    best = (-9, None)
    for i in range(12):
        for name, prof in (("", MAJ), ("m", MIN)):
            r = np.corrcoef(np.roll(v, -i), prof)[0, 1]
            if r > best[0]:
                best = (r, PITCH[i] + name)
    return best[1]


def _flatness(x, lo, hi):
    """発音している区間だけのスペクトル平坦度の中央値。

    パワースペクトル（振幅の2乗）で測ること。振幅のままだと値が6倍ほど大きく出て、
    息の目安 0.05〜0.2 がそのまま使えなくなる（順位は変わらないが閾値が意味を失う）。
    """
    n, hop = 2048, 1024
    f = np.fft.rfftfreq(n, 1 / SR)
    ok = (f > lo) & (f < hi)
    w = np.hanning(n)
    vals = []
    for i in range(0, max(0, len(x) - n), hop * 20):
        S = np.abs(np.fft.rfft(x[i:i + n] * w))[ok] + 1e-12
        if S.mean() < 1e-6:
            continue
        P = S ** 2
        vals.append(np.exp(np.log(P).mean()) / P.mean())
    return float(np.median(vals)) if vals else 0.0


def _brightness(x):
    n, w = 4096, np.hanning(4096)
    fr = np.fft.rfftfreq(n, 1 / SR)
    hi, lo = (fr >= 8000), (fr >= 200) & (fr <= 1000)
    H = L = 0.0
    for i in range(0, max(0, len(x) - n), n * 10):
        P = np.abs(np.fft.rfft(x[i:i + n] * w)) ** 2
        H += P[hi].sum()
        L += P[lo].sum()
    return float(10 * np.log10((H + 1e-20) / (L + 1e-20)))


def _mel(x):
    nf = max(0, (len(x) - N) // HOP)
    w = np.hanning(N)
    S = np.empty((nf, N // 2 + 1), dtype=np.float32)
    for i in range(nf):
        S[i] = np.abs(np.fft.rfft(x[i * HOP:i * HOP + N] * w))
    M = np.log1p(S @ MB.T)[::DEC]
    M -= M.mean(axis=0)
    M /= (M.std(axis=0) + 1e-9)
    return M.T.astype(np.float64)


def _best_match(A, B):
    """Aから3か所の30秒窓を取り、Bの全位置と相関させた最大値。"""
    if A.shape[1] < WIN + 2 or B.shape[1] < WIN + 2:
        return 0.0
    best = 0.0
    cs = np.concatenate([[0.0], np.cumsum(B ** 2, axis=1).sum(axis=0)])
    m = np.concatenate([[0.0], np.cumsum(B, axis=1).sum(axis=0)])
    for start in np.linspace(0, A.shape[1] - WIN - 1, 3).astype(int):
        a = A[:, start:start + WIN]
        a = a - a.mean(axis=1, keepdims=True)
        na = np.sqrt((a ** 2).sum())
        acc = None
        for b in range(NB):
            c = correlate(B[b], a[b], mode="valid", method="fft")
            acc = c if acc is None else acc + c
        L = len(acc)
        e = cs[WIN:WIN + L] - cs[0:L]
        s = m[WIN:WIN + L] - m[0:L]
        nb = np.sqrt(np.maximum(e - s * s / (WIN * NB), 1e-9))
        best = max(best, float((acc / (na * nb + 1e-9)).max()))
    return best


def kind_of(cfg, filename):
    """ファイル名から音色の種類を引く。Suno の " (1).wav" は同じ種類の別テイク。

    ★NFC に正規化してから引く。Suno の日本語ファイル名は「ピ」が ヒ+゚ に分解された
      NFD で落ちてくることがあり、素の文字列比較だと Vol.13 では8本中7本が外れた。
    """
    import re
    import unicodedata
    base = re.sub(r" \(\d+\)\.wav$|\.wav$", "", unicodedata.normalize("NFC", filename))
    kinds = {unicodedata.normalize("NFC", k): v for k, v in cfg.get("kinds", {}).items()}
    if base not in kinds:
        raise SystemExit(
            f"kinds に '{base}' がありません（{filename}）。巻のYAMLに追記してください。")
    return kinds[base]


def run(cfg):
    src = cfg.tracks_dir
    # ★先頭が "." のものは除く。ExFAT の外付けでは AppleDouble（._名前）が湧き、
    #   readdir には出るのに開けない幽霊エントリになることがある（3時間版で遭遇）。
    files = sorted(f for f in os.listdir(src)
                   if f.lower().endswith((".wav", ".mp3", ".flac")) and not f.startswith("."))
    if not files:
        raise SystemExit(f"楽曲が見つかりません: {src}")

    acfg = cfg["audio"]
    breath_band = cfg.get("breath_band", [1000, 5000])

    print(f"{len(files)}本を計測します（{src}）\n")
    tracks, feats, md5s = {}, {}, {}
    for f in files:
        p = os.path.join(src, f)
        x = pcm_mono(p, SR)
        ln = measure_loudness(p, acfg)
        md5 = audio_md5(p)
        tracks[f] = dict(
            file=f, dur=round(duration(p), 3), kind=kind_of(cfg, f),
            key=_key_of(_chroma(x).mean(axis=0)),
            I=float(ln["input_i"]), TP=float(ln["input_tp"]),
            breath=round(_flatness(x, breath_band[0], breath_band[1]), 4),
            bright=round(_brightness(x), 1), md5=md5,
        )
        feats[f] = _mel(x)
        md5s.setdefault(md5, []).append(f)
        t = tracks[f]
        print(f"  {f:36s} {t['dur']:6.1f}s {t['kind']:9s} {t['key']:>3s} "
              f"I={t['I']:6.1f} 息={t['breath']:.4f} 明={t['bright']:6.1f}dB")

    dupes = {k: v for k, v in md5s.items() if len(v) > 1}
    if dupes:
        print("\n★ 完全に同一の音源（デコード後MD5が一致）")
        for v in dupes.values():
            print("   " + " = ".join(v))
        print("   → 実質1本です。テイク数を数え直してください。")

    print("\n時間構造の一致度を総当たりで計算中...")
    sim = {}
    for a, b in itertools.combinations(files, 2):
        s = max(_best_match(feats[a], feats[b]), _best_match(feats[b], feats[a]))
        sim[f"{a}\t{b}"] = round(s, 4)

    print("\n一致度（1.0=同一音源 / 0.5以上=同一生成の別テイク / 0.2以下=別の曲）")
    for k, s in sorted(sim.items(), key=lambda kv: -kv[1]):
        if s < 0.15:
            continue
        a, b = k.split("\t")
        tag = "★別テイク" if s >= 0.50 else ("・やや近い" if s >= 0.30 else "")
        print(f"  {s:.3f}  {a[:31]:33s} x {b[:31]:33s} {tag}")

    out = cfg.wpath("analysis.json")
    save_json(out, dict(tracks=tracks, sim=sim))
    print(f"\n書き出し: {out}")
    return out
