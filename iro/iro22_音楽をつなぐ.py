"""IRO22 の2時間の音を組む（25分作業＋5分休憩 × 4）。IRO14 の 音を組む.py を土台にした。

選曲（全56曲の検品 _work/全56曲_検品.json・試作16曲_検品.json から）：
- 除外：C-01a（人声 0.061）・H-02a（人声 0.060）・F-01a（途中に1秒の無音）・E-04b／F-03b（尾の切れ）
- 作業 28曲：A→F を回す（1ブロック7曲）。7曲目（25:00 でフェード・84秒だけ流れる）に尾の切れた A-03a・B-04a・C-03a を置く
- 休憩 4曲：G-02b → H-01b → G-02a → H-02b（約5分半の曲を 300秒で切る）

- 1曲ごとに：頭と尾の無音を切る（−50dB）→ 検品の LUFS から −14 LUFS へ合わせる
- 頭に OPEN 秒の無音（扉ムービーを入れる.py が本編の 4.2秒から使う → そこで 25:00 が始まる）
- 作業ブロック：7曲を4秒の等電力クロスフェードでつなぎ、25:00 ちょうどで 6秒フェードアウト
- 休憩：作業より2dB静かに、頭3秒・尾6秒（最後の休憩は12秒）のフェード
- 切り替えの合図：作業→休憩は下がる2音、休憩→作業は上がる2音のチャイム（IRO01・14 と同じ自前合成のベル）

出力：ESD-02 の music_bed.wav（48kHz・24bit）と 選曲と時刻.json
"""
import json, subprocess, os
import numpy as np

SR = 48000
SSD = '/Volumes/ESD-02/IRO/IRO22_素材_夕方のポモドーロ2時間'
SRC = '/Volumes/ESD-02/Suno書き出し/IRO22_全56曲'
QC = '/Users/ryo/Desktop/BGM/IRO/Study/22_日が暮れるまで集中する/_work/全56曲_検品.json'
FOCUS, BREAK = 1500, 300
OPEN = 4.2
XF = 4.0
TARGET = -14.0

PICK = {
    'A': ['A-01b', 'A-03a', 'A-02a', 'A-01a', 'A-02b'],
    'B': ['B-02a', 'B-03b', 'B-04a', 'B-01b', 'B-03a'],
    'C': ['C-01b', 'C-02a', 'C-04a', 'C-03a', 'C-02b'],
    'D': ['D-01a', 'D-02b', 'D-03b', 'D-04a', 'D-02a'],
    'E': ['E-01a', 'E-02a', 'E-03b', 'E-04a'],
    'F': ['F-01b', 'F-02a', 'F-04a', 'F-02b'],
}
BREAKS = ['G-02b', 'H-01b', 'G-02a', 'H-02b']
TAIL_CUT = {'A-03a', 'B-04a', 'C-03a'}

LU = {k: v['LUFS'] for k, v in json.load(open(QC)).items()}


def order():
    it = {k: iter(v) for k, v in PICK.items()}
    seq = [next(it['ABCDEF'[i % 6]]) for i in range(28)]
    blocks = [seq[b * 7:(b + 1) * 7] for b in range(4)]
    for b in blocks:
        assert all(x not in TAIL_CUT for x in b[:-1]), b   # 尾の切れた曲は7曲目だけ
    assert len(set(seq)) == 28
    return blocks


def load(name):
    f = f'{SRC}/iro22_{name}.wav'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(r, np.float32).reshape(-1, 2).copy()
    w = SR // 50
    e = np.sqrt((x[: len(x) // w * w].reshape(-1, w, 2) ** 2).mean(axis=(1, 2)))
    on = np.where(20 * np.log10(e + 1e-9) > -50)[0]
    a, b = max(0, on[0] * w - int(0.15 * SR)), min(len(x), (on[-1] + 1) * w + int(0.3 * SR))
    x = x[a:b]
    x *= 10 ** ((TARGET - LU[f'iro22_{name}']) / 20)
    return x


def fade(n, kind):
    t = np.linspace(0, 1, n, dtype=np.float32)
    return np.sin(t * np.pi / 2) if kind == 'in' else np.cos(t * np.pi / 2)


def bell(freq, dur=3.2):
    t = np.arange(int(dur * SR)) / SR
    y = np.zeros_like(t)
    for ratio, amp, dec in ((1.0, 1.0, 1.6), (2.0, 0.35, 1.0), (2.76, 0.18, 0.7), (4.07, 0.07, 0.45)):
        y += amp * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / dec)
    y *= np.minimum(1, t / 0.004)
    return y.astype(np.float32)


def chime(up):
    f1, f2 = (659.25, 987.77) if up else (987.77, 659.25)
    y = np.zeros(int(4.2 * SR), np.float32)
    b1, b2 = bell(f1), bell(f2)
    y[: len(b1)] += b1
    o = int(0.55 * SR); y[o:o + len(b2)] += b2 * 0.9
    y /= np.abs(y).max()
    y *= 10 ** (-15 / 20)
    return np.stack([y, y], axis=1)


def focus_block(files):
    n = FOCUS * SR
    out = np.zeros((n, 2), np.float32)
    pos, xf = 0, int(XF * SR)
    starts = []
    for i, f in enumerate(files):
        x = load(f)
        if i > 0: x[:xf] *= fade(xf, 'in')[:, None]
        if i < len(files) - 1: x[-xf:] *= fade(xf, 'out')[:, None]
        if i == 0: x[: int(3 * SR)] *= fade(int(3 * SR), 'in')[:, None]
        starts.append(pos / SR)
        end = min(n, pos + len(x))
        out[pos:end] += x[: end - pos]
        if pos + len(x) >= n: break
        pos += len(x) - xf
    if pos + len(x) < n: raise SystemExit(f'25分に届かない: {(pos + len(x)) / SR:.1f}s')
    if len(starts) < len(files): raise SystemExit(f'{len(files)}曲目まで届く前に25分を超えた（{len(starts)}曲）')
    fo = int(6 * SR)
    out[-fo:] *= fade(fo, 'out')[:, None]
    return out, starts


def break_block(g, last=False):
    x = load(g); n = BREAK * SR
    if len(x) < n: raise SystemExit(f'{g} が {len(x) / SR:.1f}秒で5分に足りない')
    x = x[:n] * 10 ** (-2 / 20)
    x[: int(3 * SR)] *= fade(int(3 * SR), 'in')[:, None]
    fo = int((12 if last else 6) * SR)
    x[n - fo:] *= fade(fo, 'out')[:, None]
    return x


if __name__ == '__main__':
    os.makedirs(SSD, exist_ok=True)
    blocks = order()
    raw = f'{SSD}/music_bed_raw.f32'; tl = []
    with open(raw, 'wb') as fh:
        fh.write(np.zeros((int(round(OPEN * SR)), 2), np.float32).tobytes())
        t = OPEN
        for b, files in enumerate(blocks):
            fb, starts = focus_block(files)
            if b > 0:
                c = chime(True); fb[: len(c)] += c
            bb = break_block(BREAKS[b], last=(b == 3))
            c = chime(False); bb[: len(c)] += c
            fh.write(fb.tobytes()); fh.write(bb.tobytes())
            tl.append(dict(focus=[t, t + FOCUS], brk=[t + FOCUS, t + FOCUS + BREAK],
                           tracks=[dict(name=f, at=round(t + s, 3)) for f, s in zip(files, starts)],
                           break_track=dict(name=BREAKS[b], at=t + FOCUS)))
            print(f'FOCUS {b + 1} {(t - OPEN) / 60:5.1f}分〜 7曲目 {starts[-1] / 60:.1f}分〜（{(FOCUS - starts[-1]):.0f}秒流れる） / BREAK {BREAKS[b]}', flush=True)
            t += FOCUS + BREAK
    json.dump(dict(blocks=blocks, breaks=BREAKS, timeline=tl), open(f'{SSD}/選曲と時刻.json', 'w'), ensure_ascii=False, indent=1)
    out = f'{SSD}/music_bed.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw,
                    '-af', 'alimiter=limit=0.794:attack=3:release=60:level=0', '-c:a', 'pcm_s24le', out], check=True)
    os.remove(raw)
    print('書き出し:', out, f'（{t:.1f}秒）')
