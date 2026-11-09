"""IRO24 の3時間の音を組む（IRO23 の 音楽をつなぐ.py を下敷きに、3時間・クリスマスジャズの6種へ）。

選曲は検品の JSON から自動で決める（`python iro24_音楽をつなぐ.py pick` で一覧だけ出す）：
- 除外：人声の最大 0.05 以上・途中に2秒以上の無音・尾の切れ（最後5秒の中央が本体より −10dB に届かず、最後1秒も −28dB より大きい）
  ★IRO23 の「最後1秒 −45dB」だと、最後の4〜5秒で −31〜−44dB まで下がる短いフェードの24曲まで外れた（4秒重ねでつなぐので問題ない）
- 除外：A・B・E（サックスでない主役）で判定器の「サックス」が 0.15 以上（伴奏にサックスが混ざった疑い）
- D（チェロ）・F（ホルン）は試作から判定器が「サックス」0.1〜0.19 と読む（弓・金管の取り違えと見る）→ 0.30 以上だけ除外し、低い順に使う
- 除外：B・E でピアノ／電気ピアノが 0.14 を超える曲（0.12 だと候補が46曲で3時間ぎりぎり→0.137 の2曲を戻した）（試作の B-01・E-01 は 0.13〜0.25 で伴奏のピアノが前に出ていた。
  ビブラフォン・グロッケンは判定器がほぼ拾わない＝IRO18 のビブラフォン曲でも 0.02〜0.06 なので主役のラベルでは切らない）
- 除外：F でホルン系（Brass instrument）が 0.1 に届かない曲
- 並べ方：残りの多い種類から選ぶ。同じ種類は4曲以上あけ、金属の打鍵 B・E は隣に置かない（候補数が E 6・B 6・A/F 10 とばらつくので A→F の順回しはできない）

- 1曲ごとに：頭と尾の無音を切る（−50dB）→ 検品の LUFS から −14 LUFS へ合わせる
- 頭に OPEN 秒の無音（扉ムービーを入れる.py が本編の 4.2秒から使う）
- 4秒の等電力クロスフェードでつなぎ、3時間ちょうどで12秒フェードアウト

出力：ESD-02 の music_bed.wav（48kHz・24bit）と 選曲と時刻.json
"""
import json, subprocess, os, sys
import numpy as np

SR = 48000
SSD = '/Volumes/ESD-02/IRO/IRO24_素材_クリスマス3時間'
SRC = '/Volumes/ESD-02/Suno書き出し/IRO24_全60曲/wav'
QC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iro24_全曲物理検品.json')
AI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iro24_全曲検品.json')
T = 10800
OPEN = 4.2
XF = 4.0
TARGET = -14.0
KINDS = 'ABCDEF'
REED = {'D', 'F'}


def candidates():
    qc = json.load(open(QC)); ai = json.load(open(AI)); ok, bad = {k: [] for k in KINDS}, {}
    for name, q in sorted(qc.items()):
        tag = name.split('_')[1]; kind = tag[0]; why = []; a = ai[name]
        w = a.get('監視', {}); sax = w.get('Saxophone', 0.0)
        pno = max(w.get('Piano', 0.0), w.get('Electric piano', 0.0))
        if a['人声の最大'] >= 0.05: why.append(f"人声{a['人声の最大']}")
        if q['途中無音秒'] >= 2: why.append(f"途中無音{q['途中無音秒']}秒")
        if q['最後5秒の中央dB'] > q['本体の中央dB'] - 10 and q['最後1秒dB'] > -28: why.append('尾の切れ')
        if kind in 'ABE' and sax >= 0.15: why.append(f'サックス{sax}')
        if kind in REED and sax >= 0.30: why.append(f'サックス{sax}')
        if kind in 'BE' and pno > 0.14: why.append(f'ピアノ{pno}')
        if kind == 'F' and a['主役ラベル'].get('Brass instrument', 0.0) < 0.1: why.append(f"ホルン{a['主役ラベル'].get('Brass instrument')}")
        if why: bad[tag] = why; continue
        ok[kind].append((sax if kind in REED else a['人声の最大'], tag))
    for k in KINDS: ok[k] = [t for _, t in sorted(ok[k])]
    return ok, bad


def order(n):
    ok, bad = candidates(); left = {k: list(v) for k, v in ok.items()}; seq, kinds = [], []
    for i in range(n):
        def allowed(k):
            if not left[k] or k in kinds[-4:]: return False
            if kinds and {k, kinds[-1]} == {'B', 'E'}: return False
            return True
        cand = [k for k in KINDS if allowed(k)]
        if not cand: print(f'並べられる候補が尽きた（{i + 1}曲目）'); break
        k = max(cand, key=lambda k: (len(left[k]), -KINDS.index(k)))
        seq.append(left[k].pop(0)); kinds.append(k)
    return seq, ok, bad


def load(name, lu):
    f = f'{SRC}/iro24_{name}.wav'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(r, np.float32).reshape(-1, 2).copy()
    w = SR // 50
    e = np.sqrt((x[: len(x) // w * w].reshape(-1, w, 2) ** 2).mean(axis=(1, 2)))
    on = np.where(20 * np.log10(e + 1e-9) > -50)[0]
    a, b = max(0, on[0] * w - int(0.15 * SR)), min(len(x), (on[-1] + 1) * w + int(0.3 * SR))
    x = x[a:b]
    x *= 10 ** ((TARGET - lu[f'iro24_{name}']) / 20)
    return x


def fade(n, kind):
    t = np.linspace(0, 1, n, dtype=np.float32)
    return np.sin(t * np.pi / 2) if kind == 'in' else np.cos(t * np.pi / 2)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'pick':
        seq, ok, bad = order(56)
        print('除外:', bad); print('候補数:', {k: len(v) for k, v in ok.items()}); print('並び:', seq); sys.exit()
    lu = {k: v['LUFS'] for k, v in json.load(open(QC)).items()}
    seq, ok, bad = order(56)
    # ★3時間を1つの配列に持つと約4GB（8GBのMacでは危ない）→ 1曲ずつ raw に書き足し、重なり4秒だけ持ち越す
    os.makedirs(SSD, exist_ok=True)
    raw = f'{SSD}/music_bed_raw.f32'; n = T * SR; xf = int(XF * SR); written = 0; tail = None; used = []
    with open(raw, 'wb') as fh:
        fh.write(np.zeros((int(round(OPEN * SR)), 2), np.float32).tobytes())
        for i, f in enumerate(seq):
            x = load(f, lu)
            if i > 0: x[:xf] *= fade(xf, 'in')[:, None]; x[:xf] += tail
            else: x[: int(3 * SR)] *= fade(int(3 * SR), 'in')[:, None]
            x[-xf:] *= fade(xf, 'out')[:, None]
            used.append(dict(name=f, at=round(OPEN + written / SR, 3)))
            fh.write(x[:-xf].tobytes()); written += len(x) - xf; tail = x[-xf:].copy()
            if written >= n: break
        else:
            raise SystemExit(f'3時間に届かない（{written / SR:.0f}秒）')
    print(f'{len(used)}曲。最後の {used[-1]["name"]} は {(T + OPEN - used[-1]["at"]):.0f}秒流れる')
    json.dump(dict(tracks=used, excluded=bad), open(f'{SSD}/選曲と時刻.json', 'w'), ensure_ascii=False, indent=1)
    dst = f'{SSD}/music_bed.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw, '-t', f'{T + OPEN:.3f}',
                    '-af', f'afade=t=out:st={T + OPEN - 12:.3f}:d=12,alimiter=limit=0.794:attack=3:release=60:level=0', '-c:a', 'pcm_s24le', dst], check=True)
    os.remove(raw)
    print('書き出し:', dst, f'（{T + OPEN:.1f}秒）')
