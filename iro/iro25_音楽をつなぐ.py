"""IRO25 の3時間の音を組む（25分作業＋5分休憩 × 6）。iro22_音楽をつなぐ.py を土台にした（Claude 2026-11-21）。

選曲は検品の結果から自動で決める（`iro/iro25_試作検品.json`＝AST、`iro/iro25_全曲検品.json`＝無音・尾・LUFS）：
- 除外：人声の最大 0.05 以上／サックスの反応 0.1 以上（直近5巻の IRO24 で主役）／途中の無音2秒以上／長さが 200秒未満か 300秒超（作業曲）
- 尾の切れ（最後1秒が −28dB より大きい）は、その種類が7曲目に来るブロックにだけ1曲置ける（25:00 でフェード＝尾は流れない）
- 作業 42曲：A→F を回す（1ブロック7曲）。7曲目はブロック b で 'ABCDEF'[b]
- 休憩 6曲：G→H を交互（約5分半の曲を 300秒で切る）
- 同じ種類の中では人声の値が小さい順に使う

- 1曲ごとに：頭と尾の無音を切る（−50dB）→ 検品の LUFS から −14 LUFS へ合わせる
- 頭に OPEN 秒の無音（扉ムービーを入れる処理が本編の 4.2秒から使う）
- 作業ブロック：7曲を4秒の等電力クロスフェードでつなぎ、25:00 ちょうどで 6秒フェードアウト
- 休憩：作業より2dB静かに、頭3秒・尾6秒（最後の休憩は12秒）のフェード
- 切り替えの合図：作業→休憩は下がる2音、休憩→作業は上がる2音のチャイム（IRO01・14・22 と同じ自前合成のベル）
- ★8GBのMacで3時間を1配列に持たない（IRO24 の教訓）→ ブロックごとに f32 の生ファイルへ書き足す

出力：ESD-02 の music_bed.wav（48kHz・24bit）と 選曲と時刻.json
  python iro25_音楽をつなぐ.py plan   # 選曲だけ表示
  python iro25_音楽をつなぐ.py        # 書き出し
"""
import json, subprocess, os, sys
from pathlib import Path
import numpy as np

SR = 48000
ROOT = Path(__file__).resolve().parent
SSD = '/Volumes/ESD-02/IRO/IRO25_素材_冬のポモドーロ3時間'
SRC = '/Volumes/ESD-02/Suno書き出し/IRO25_全72曲/wav'
AST = json.load(open(ROOT / 'iro25_試作検品.json'))
QC = json.load(open(ROOT / 'iro25_全曲検品.json'))
FOCUS, BREAK, NB = 1500, 300, 6
OPEN = 4.2
XF = 4.0
TARGET = -14.0
VOICE_MAX, TAIL_DB = 0.05, -28.0


def plan():
    names = sorted(k.replace('iro25_', '') for k in QC)
    why, ok, tail = {}, {}, set()
    for n in names:
        q, a = QC['iro25_' + n], AST.get('iro25_' + n)
        if a is None: why[n] = 'AST未実施'; continue
        if a['人声の最大'] >= VOICE_MAX: why[n] = f"人声 {a['人声の最大']}"; continue
        if a['監視'].get('Saxophone', 0) >= 0.1: why[n] = f"サックスの反応 {a['監視']['Saxophone']}（IRO24で使った楽器）"; continue
        if q['途中無音秒'] >= 2: why[n] = f"途中の無音 {q['途中無音秒']}秒"; continue
        if n[0] in 'ABCDEF' and not (200 <= q['秒'] <= 300): why[n] = f"長さ {q['秒']}秒"; continue
        if q['最後1秒dB'] > TAIL_DB: tail.add(n)
        ok.setdefault(n[0], []).append(n)
    for k in ok: ok[k].sort(key=lambda n: AST['iro25_' + n]['人声の最大'])
    pick = {}
    for b, k in enumerate('ABCDEF'):
        full = [n for n in ok.get(k, []) if n not in tail]
        cut = [n for n in ok.get(k, []) if n in tail]
        # 7曲目に回せる尾の切れは1曲まで（その種類が7曲目に来るのはブロック b の1回だけ）
        use = full[:7] if len(full) >= 7 else full + cut[:1]
        if len(use) < 7: raise SystemExit(f'{k} が {len(use)} 曲しかない（除外 {[(n, why[n]) for n in why if n[0] == k]}）')
        pick[k] = use
    seq_it = {k: [n for n in v if n not in tail] for k, v in pick.items()}
    tail_it = {k: [n for n in v if n in tail] for k, v in pick.items()}
    blocks = []
    for b in range(NB):
        blk = []
        for j in range(7):
            k = 'ABCDEF'[(7 * b + j) % 6]
            if j == 6 and tail_it[k]: blk.append(tail_it[k].pop(0))
            else: blk.append(seq_it[k].pop(0))
        blocks.append(blk)
    assert len({n for blk in blocks for n in blk}) == 42
    for blk in blocks: assert all(n not in tail for n in blk[:-1]), blk
    brk_ok = {k: ok.get(k, []) for k in 'GH'}
    breaks = [brk_ok['GH'[i % 2]][i // 2] for i in range(NB)]
    return blocks, breaks, why, tail


def load(name):
    f = f'{SRC}/iro25_{name}.wav'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(r, np.float32).reshape(-1, 2).copy()
    w = SR // 50
    e = np.sqrt((x[: len(x) // w * w].reshape(-1, w, 2) ** 2).mean(axis=(1, 2)))
    on = np.where(20 * np.log10(e + 1e-9) > -50)[0]
    a, b = max(0, on[0] * w - int(0.15 * SR)), min(len(x), (on[-1] + 1) * w + int(0.3 * SR))
    x = x[a:b]
    x *= 10 ** ((TARGET - QC[f'iro25_{name}']['LUFS']) / 20)
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
    if pos + len(x) < n: raise SystemExit(f'25分に届かない: {(pos + len(x)) / SR:.1f}s {files}')
    if len(starts) < len(files): raise SystemExit(f'{len(files)}曲目まで届く前に25分を超えた（{len(starts)}曲）{files}')
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
    blocks, breaks, why, tail = plan()
    print('除外:', why); print('尾の切れ:', sorted(tail))
    for b, blk in enumerate(blocks): print(f'FOCUS {b + 1}:', ' '.join(blk), '/ BREAK', breaks[b])
    if sys.argv[1:] == ['plan']: raise SystemExit
    os.makedirs(SSD, exist_ok=True)
    raw = f'{SSD}/music_bed_raw.f32'; tl = []
    with open(raw, 'wb') as fh:
        fh.write(np.zeros((int(round(OPEN * SR)), 2), np.float32).tobytes())
        t = OPEN
        for b, files in enumerate(blocks):
            fb, starts = focus_block(files)
            if b > 0:
                c = chime(True); fb[: len(c)] += c
            bb = break_block(breaks[b], last=(b == NB - 1))
            c = chime(False); bb[: len(c)] += c
            fh.write(fb.tobytes()); fh.write(bb.tobytes())
            tl.append(dict(focus=[t, t + FOCUS], brk=[t + FOCUS, t + FOCUS + BREAK],
                           tracks=[dict(name=f, at=round(t + s, 3)) for f, s in zip(files, starts)],
                           break_track=dict(name=breaks[b], at=t + FOCUS)))
            print(f'FOCUS {b + 1} {(t - OPEN) / 60:5.1f}分〜 7曲目 {starts[-1] / 60:.1f}分〜（{(FOCUS - starts[-1]):.0f}秒流れる） / BREAK {breaks[b]}', flush=True)
            del fb, bb
            t += FOCUS + BREAK
    json.dump(dict(blocks=blocks, breaks=breaks, excluded=why, tail_cut=sorted(tail), timeline=tl),
              open(f'{SSD}/選曲と時刻.json', 'w'), ensure_ascii=False, indent=1)
    out = f'{SSD}/music_bed.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw,
                    '-af', 'alimiter=limit=0.794:attack=3:release=60:level=0', '-c:a', 'pcm_s24le', out], check=True)
    os.remove(raw)
    print('書き出し:', out, f'（{t:.1f}秒）')
