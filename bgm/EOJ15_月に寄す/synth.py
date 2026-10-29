# -*- coding: utf-8 -*-
"""和楽器の合成（numpy と scipy だけ）。箏＝撥弦、笙＝加算、尺八＝倍音＋息。"""
import numpy as np

SR = 48000


def midi_hz(n):
    return 440.0 * 2 ** ((n - 69) / 12.0)


_KOTO_CACHE = {}


def koto(note, dur, vel=1.0, sr=SR, bright=0.5, damp=0.996):
    """箏：撥弦（Karplus-Strong）。遅延長ごとのブロック処理で一括計算する。"""
    key = (note, round(dur, 3), round(bright, 3), round(damp, 5))
    if key in _KOTO_CACHE:
        return _KOTO_CACHE[key] * vel
    f = midi_hz(note)
    N = int(sr * dur)
    L = max(2, int(round(sr / f)))
    rng = np.random.default_rng(int(note * 977 + dur * 131) & 0xffffffff)
    exc = rng.standard_normal(L)
    k = max(1, int(L * (1.0 - bright)))
    exc = np.convolve(exc, np.ones(k) / k, mode='same')
    exc *= np.linspace(1.0, 0.2, L)
    exc /= (np.abs(exc).max() + 1e-9)
    y = np.zeros(N + L + 2)
    y[L + 2:L + 2 + min(L, N)] = exc[:min(L, N)]
    g = 0.5 * damp ** (1.0 + (note - 55) / 36.0)
    s0 = L + 2
    for i in range(s0, s0 + N, L):
        j = min(i + L, s0 + N)
        y[i:j] += g * (y[i - L:j - L] + y[i - L - 1:j - L - 1])
    out = y[s0:s0 + N].copy()
    atk = int(sr * 0.004)
    if N > atk:
        out[:atk] += rng.standard_normal(atk) * np.linspace(1, 0, atk) ** 2 * 0.25
    rel = int(sr * 0.05)
    if N > rel:
        out[-rel:] *= np.linspace(1, 0, rel)
    out = (out * 0.5).astype(np.float32)
    if len(_KOTO_CACHE) < 400:
        _KOTO_CACHE[key] = out
    return out * vel


def sho(notes, dur, vel=1.0, sr=SR, breath=0.02):
    """笙：奇数倍音の強い持続音。わずかなうなりと息のノイズ。"""
    N = int(sr * dur)
    if N < 64:
        return np.zeros(max(N, 0), dtype=np.float32)
    t = np.arange(N) / sr
    out = np.zeros(N)
    rng = np.random.default_rng((sum(notes) * 31 + N) & 0xffffffff)
    for n in notes:
        f = midi_hz(n)
        for h, a in ((1, 1.0), (2, 0.15), (3, 0.55), (4, 0.08), (5, 0.30), (7, 0.14), (9, 0.07)):
            if f * h > sr / 2.2:
                break
            out += a * np.sin(2 * np.pi * (f * h + rng.uniform(-0.35, 0.35)) * t
                              + rng.uniform(0, 6.283))
    out /= max(1, len(notes)) * 2.4
    out += rng.standard_normal(N) * breath * 0.3
    a = max(1, int(sr * min(2.5, dur * 0.35)))
    r = max(1, int(sr * min(3.0, dur * 0.40)))
    env = np.ones(N)
    env[:a] = np.linspace(0, 1, a) ** 1.6
    env[N - r:] = np.linspace(1, 0, r) ** 1.4
    return (out * env * vel).astype(np.float32)


def shakuhachi(note, dur, vel=1.0, sr=SR, air=0.55, muraiki=0.0):
    """尺八：細い笛の倍音＋息のノイズ。muraiki を上げると頭の息が音より前に出る。"""
    from scipy.signal import lfilter, butter
    f = midi_hz(note)
    N = int(sr * dur)
    if N < 64:
        return np.zeros(max(N, 0), dtype=np.float32)
    t = np.arange(N) / sr
    rng = np.random.default_rng(int(note * 613 + dur * 271) & 0xffffffff)
    drift = -0.35 * np.exp(-t / max(0.05, dur * 0.12))
    vib_on = np.clip((t - dur * 0.45) / max(0.2, dur * 0.35), 0, 1)
    vib = 0.22 * vib_on * np.sin(2 * np.pi * 4.6 * t + rng.uniform(0, 6.283))
    ph = np.cumsum(2 * np.pi * f * 2 ** ((drift + vib) / 12.0) / sr)
    tone = np.zeros(N)
    for h, a in ((1, 1.0), (2, 0.26), (3, 0.42), (4, 0.10), (5, 0.16), (6, 0.05), (7, 0.07)):
        if f * h > sr / 2.2:
            break
        tone += a * np.sin(h * ph)
    tone /= 2.1
    lo = min(0.90, f * 1.6 / (sr / 2))
    hi = min(0.98, max(lo + 0.02, f * 7.0 / (sr / 2)))
    b2, a2 = butter(2, [lo, hi], btype='band')
    breath = lfilter(b2, a2, rng.standard_normal(N))
    breath /= (np.abs(breath).max() + 1e-9)
    atk = max(1, int(sr * (0.10 + 0.10 * muraiki)))
    env = np.ones(N)
    env[:atk] = np.linspace(0, 1, atk) ** (1.4 - 0.7 * muraiki)
    rel = max(1, int(min(N * 0.4, sr * 0.5)))
    env[N - rel:] *= np.linspace(1, 0, rel) ** 1.3
    benv = env.copy()
    hd = min(N, int(sr * 0.22))
    benv[:hd] += np.linspace(1.0, 0.0, hd) ** 1.5 * (0.6 + 2.2 * muraiki)
    return ((tone * env + breath * air * benv * 0.55) * vel * 0.42).astype(np.float32)


def _comb(x, d, g):
    y = np.zeros(len(x) + d)
    y[d:] = x
    for i in range(d, len(y), d):
        j = min(i + d, len(y))
        y[i:j] += g * y[i - d:j - d]
    return y[d:]


def _allpass(x, d, g):
    """y[n] = -g x[n] + x[n-d] + g y[n-d]"""
    xp = np.concatenate([np.zeros(d), x])
    base = -g * xp + np.concatenate([np.zeros(d), xp[:-d]])
    y = np.zeros(len(xp))
    y[:d] = base[:d]
    for i in range(d, len(y), d):
        j = min(i + d, len(y))
        y[i:j] = base[i:j] + g * y[i - d:j - d]
    return y[d:]


def reverb(x, sr=SR, rt=3.4, mix=0.30):
    """シュレーダー残響（櫛型4＋オールパス2）。遅延長ごとのブロック処理。"""
    x = x.astype(np.float64)
    wet = np.zeros_like(x)
    for dl in (0.0297, 0.0371, 0.0411, 0.0437):
        wet += _comb(x, int(sr * dl), 10 ** (-3 * dl / rt))
    wet /= 4.0
    for dl, g in ((0.0050, 0.7), (0.0017, 0.7)):
        wet = _allpass(wet, int(sr * dl), g)
    return ((1 - mix) * x + mix * wet).astype(np.float32)


def write_wav(path, x, sr=SR):
    from scipy.io import wavfile
    x = np.asarray(x, dtype=np.float64)
    x = x / (np.abs(x).max() + 1e-9) * 0.89
    if x.ndim == 2:
        x = x.T
    wavfile.write(path, sr, (x * 32767).astype(np.int16))


# ─────────────────────────────────────────────────────────────
# 打楽器（2026年9月2日 追加）。既存の関数には手を触れていない。
#
# 膜の振動は正弦波ではない。円形膜の固有振動は基音に対して
# 1.000 / 1.594 / 2.136 / 2.296 … という非整数比（ベッセル関数の零点）で並ぶ。
# ここを整数倍音にすると太鼓ではなく「低い笛」になるので、比を実際の値で持つ。
# 高い振動ほど速く消えるので、減衰も比ごとに変える。
# ─────────────────────────────────────────────────────────────

_MEMBRANE = ((1.000, 1.00), (1.594, 0.46), (2.136, 0.30), (2.296, 0.26),
             (2.653, 0.17), (2.918, 0.13), (3.156, 0.10), (3.501, 0.075),
             (3.600, 0.055), (4.060, 0.04))

# f0=基音Hz / rt=胴の残り(秒) / bend=打った直後の音程の動き(半音・負で下がる)
# slap=撥や指の当たる音の量 / band=その帯域 / body=胴の量
DRUMS = {
    '大太鼓': dict(f0=54.0,  rt=2.40, bend=-2.6, slap=0.20, band=(110, 1600), body=1.00),
    '宮太鼓': dict(f0=88.0,  rt=1.10, bend=-2.0, slap=0.34, band=(180, 3200), body=0.95),
    '締太鼓': dict(f0=210.0, rt=0.36, bend=-1.2, slap=0.62, band=(700, 8000), body=0.80),
    '小鼓':   dict(f0=340.0, rt=0.50, bend=+3.4, slap=0.42, band=(800, 6500), body=0.90),
    '大鼓':   dict(f0=520.0, rt=0.22, bend=+1.0, slap=0.70, band=(1200, 9000), body=0.65),
}

_DRUM_CACHE = {}


def drum(kind='宮太鼓', vel=1.0, sr=SR, f0=None, rt=None, bend=None,
         slap=None, body=None, dur=None, seed=0):
    """和太鼓・鼓。DRUMS の型を呼び、必要なら1つずつ上書きする。"""
    from scipy.signal import lfilter, butter
    d = DRUMS[kind]
    f0 = d['f0'] if f0 is None else f0
    rt = d['rt'] if rt is None else rt
    bend = d['bend'] if bend is None else bend
    slap = d['slap'] if slap is None else slap
    body = d['body'] if body is None else body
    dur = min(6.0, rt * 2.6 + 0.15) if dur is None else dur
    key = (kind, round(f0, 2), round(rt, 3), round(bend, 2),
           round(slap, 3), round(body, 3), round(dur, 3), seed)
    if key in _DRUM_CACHE:
        return _DRUM_CACHE[key] * vel

    N = int(sr * dur)
    if N < 32:
        return np.zeros(max(N, 0), dtype=np.float32)
    t = np.arange(N) / sr
    rng = np.random.default_rng((hash(key) ^ 0x5bf03635) & 0xffffffff)

    # 打った直後だけ音程が動く（皮の張りが戻る）。時定数は残りに比例させる。
    glide = 2 ** ((bend * np.exp(-t / max(0.01, rt * 0.22))) / 12.0)

    out = np.zeros(N)
    for ratio, amp in _MEMBRANE:
        f = f0 * ratio
        if f > sr / 2.2:
            break
        # 高い振動ほど速く消える
        tau = rt / (1.0 + 0.85 * (ratio - 1.0))
        ph = np.cumsum(2 * np.pi * f * glide / sr) + rng.uniform(0, 6.283)
        out += amp * np.sin(ph) * np.exp(-t / max(0.008, tau))
    out *= body / 1.9

    # 撥や指が皮に当たる音。ごく短い帯域雑音。
    if slap > 0:
        lo = max(20.0, d['band'][0]) / (sr / 2)
        hi = min(0.97, d['band'][1] / (sr / 2))
        b2, a2 = butter(2, [lo, hi], btype='band')
        n = lfilter(b2, a2, rng.standard_normal(N))
        n /= (np.abs(n).max() + 1e-9)
        out += n * slap * np.exp(-t / max(0.003, 0.012 + 0.05 * slap))

    out[:12] *= np.linspace(0, 1, 12)
    rel = max(1, int(sr * 0.02))
    out[-rel:] *= np.linspace(1, 0, rel)
    out = (out * 0.55).astype(np.float32)
    if len(_DRUM_CACHE) < 200:
        _DRUM_CACHE[key] = out
    return out * vel


def ki(vel=1.0, sr=SR, dur=0.34, seed=0):
    """柝（き）／拍子木。木を打ち合わせる音。膜ではないので高い共鳴3本＋撥音。"""
    from scipy.signal import lfilter, butter
    N = int(sr * dur)
    t = np.arange(N) / sr
    rng = np.random.default_rng((seed * 7919 + 13) & 0xffffffff)
    out = np.zeros(N)
    for f, a, tau in ((1180.0, 1.00, 0.055), (2460.0, 0.55, 0.032),
                      (3870.0, 0.30, 0.020), (5400.0, 0.16, 0.013)):
        out += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.283)) * np.exp(-t / tau)
    b2, a2 = butter(2, [900 / (sr / 2), 0.95], btype='band')
    n = lfilter(b2, a2, rng.standard_normal(N))
    n /= (np.abs(n).max() + 1e-9)
    out = out / 2.0 + n * 0.9 * np.exp(-t / 0.004)
    out[:8] *= np.linspace(0, 1, 8)
    out[-int(sr * 0.01):] *= np.linspace(1, 0, int(sr * 0.01))
    return (out * 0.5 * vel).astype(np.float32)
