"""IRO23 の2時間の音を組む（区切りなしのカフェ。IRO22 の 音楽をつなぐ.py からポモドーロの区切りとチャイムを外した）。

選曲は検品の JSON から自動で決める（`python iro23_音楽をつなぐ.py pick` で一覧だけ出す）：
- 除外：人声の最大 0.05 以上・途中に2秒以上の無音・尾の切れ（最後5秒の中央が本体より −10dB に届かない＝切れている）
- 除外：B・C・E・F（リードでない主役）で判定器の「サックス」が 0.15 以上（伴奏にサックスが混ざった疑い。IRO21・22 のサックスなしの曲は 0.11 以下だった）
- 除外：B・E・F で主役のラベルが 0.1 に届かない曲（F-01b はギターが上位。オルゴールは判定器にラベルが無い）
- 除外：B・E・F でピアノ／電気ピアノのほうが主役より高い曲（F-04b・B-02b。ピアノは IRO18 と重なる）
- A（アコーディオン）・D（バンドネオン）は判定器がほぼ全曲を「サックス」と読む（Accordion のラベルは 0.03 以下）。リードの音色の取り違えと見て除外はせず、サックスの値の低い順に使う
- ★10/28：A・C のプロンプトの念押し（2回目以降）では値は下がらなかったので、試作と区別しない
- C→D→E→F→A→B の順に回す（雨の午後の頭はオルゴールから）。同じ種類はちょうど6曲離れる

- 1曲ごとに：頭と尾の無音を切る（−50dB）→ 検品の LUFS から −14 LUFS へ合わせる
- 頭に OPEN 秒の無音（扉ムービーを入れる.py が本編の 4.2秒から使う）
- 4秒の等電力クロスフェードでつなぎ、2時間ちょうどで12秒フェードアウト

出力：ESD-02 の music_bed.wav（48kHz・24bit）と 選曲と時刻.json
"""
import json, subprocess, os, sys
import numpy as np

SR = 48000
SSD = '/Volumes/ESD-02/IRO/IRO23_素材_雨やどりのカフェ2時間'
SRC = '/Volumes/ESD-02/Suno書き出し/IRO23_全48曲/wav'
QC = f'{SSD}/全48曲_検品.json'
AI = f'{SSD}/全48曲_自動判定.json'
T = 7200
OPEN = 4.2
XF = 4.0
TARGET = -14.0
KINDS = 'CDEFAB'
REED = {'A', 'D'}


def candidates():
    qc = json.load(open(QC)); ai = json.load(open(AI)); ok, bad = {k: [] for k in KINDS}, {}
    for name, q in sorted(qc.items()):
        tag = name.split('_')[1]; kind = tag[0]; why = []; a = ai[name]
        sax = dict(a['上位']).get('Saxophone', 0.0); lead = max(a['主役ラベル'].values())
        if a['人声の最大'] >= 0.05: why.append(f"人声{a['人声の最大']}")
        if q['途中無音秒'] >= 2: why.append(f"途中無音{q['途中無音秒']}秒")
        if q['最後5秒の中央dB'] > q['本体の中央dB'] - 10 and q['最後1秒dB'] > -45: why.append('尾の切れ')
        if kind not in REED and sax >= 0.15: why.append(f'サックス{sax}')
        if kind in 'BEF' and lead < 0.1: why.append(f'主役{lead}')   # オルゴールは判定器にラベルが無いので見ない
        pno = max(dict(a['上位']).get('Piano', 0.0), dict(a['上位']).get('Electric piano', 0.0))
        if kind in 'BEF' and pno > lead: why.append(f'ピアノ{pno}＞主役{lead}')   # ピアノは IRO18 と重なるので主役にできない
        if why: bad[tag] = why; continue
        ok[kind].append((sax if kind in REED else a['人声の最大'], tag))
    for k in KINDS: ok[k] = [t for _, t in sorted(ok[k])]
    return ok, bad


def order(n):
    ok, bad = candidates(); it = {k: iter(v) for k, v in ok.items()}; seq = []
    for i in range(n):
        k = KINDS[i % 6]; t = next(it[k], None)
        if t is None: raise SystemExit(f'{k} の候補が足りない（{i + 1}曲目）')
        seq.append(t)
    return seq, ok, bad


def load(name, lu):
    f = f'{SRC}/iro23_{name}.wav'
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(r, np.float32).reshape(-1, 2).copy()
    w = SR // 50
    e = np.sqrt((x[: len(x) // w * w].reshape(-1, w, 2) ** 2).mean(axis=(1, 2)))
    on = np.where(20 * np.log10(e + 1e-9) > -50)[0]
    a, b = max(0, on[0] * w - int(0.15 * SR)), min(len(x), (on[-1] + 1) * w + int(0.3 * SR))
    x = x[a:b]
    x *= 10 ** ((TARGET - lu[f'iro23_{name}']) / 20)
    return x


def fade(n, kind):
    t = np.linspace(0, 1, n, dtype=np.float32)
    return np.sin(t * np.pi / 2) if kind == 'in' else np.cos(t * np.pi / 2)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'pick':
        seq, ok, bad = order(32)
        print('除外:', bad); print('候補数:', {k: len(v) for k, v in ok.items()}); print('並び:', seq); sys.exit()
    lu = {k: v['LUFS'] for k, v in json.load(open(QC)).items()}
    seq, ok, bad = order(32)
    n = T * SR; out = np.zeros((n, 2), np.float32); pos, xf = 0, int(XF * SR); used = []
    for i, f in enumerate(seq):
        x = load(f, lu)
        if i > 0: x[:xf] *= fade(xf, 'in')[:, None]
        else: x[: int(3 * SR)] *= fade(int(3 * SR), 'in')[:, None]
        x[-xf:] *= fade(xf, 'out')[:, None]
        used.append(dict(name=f, at=round(OPEN + pos / SR, 3)))
        end = min(n, pos + len(x)); out[pos:end] += x[: end - pos]
        if pos + len(x) >= n: break
        pos += len(x) - xf
    else:
        raise SystemExit('2時間に届かない')
    fo = int(12 * SR); out[-fo:] *= fade(fo, 'out')[:, None]
    print(f'{len(used)}曲。最後の {used[-1]["name"]} は {(T + OPEN - used[-1]["at"]):.0f}秒流れる')
    os.makedirs(SSD, exist_ok=True)
    raw = f'{SSD}/music_bed_raw.f32'
    with open(raw, 'wb') as fh:
        fh.write(np.zeros((int(round(OPEN * SR)), 2), np.float32).tobytes()); fh.write(out.tobytes())
    json.dump(dict(tracks=used, excluded=bad), open(f'{SSD}/選曲と時刻.json', 'w'), ensure_ascii=False, indent=1)
    dst = f'{SSD}/music_bed.wav'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', raw,
                    '-af', 'alimiter=limit=0.794:attack=3:release=60:level=0', '-c:a', 'pcm_s24le', dst], check=True)
    os.remove(raw)
    print('書き出し:', dst, f'（{T + OPEN:.1f}秒）')
