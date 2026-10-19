# -*- coding: utf-8 -*-
"""EOJ14：リストの「コンソレーション（慰め）」を軸に、ロマン派の静かな小品8曲で1時間の床を組む
（EOJ13 の album.py を写した）。

**コンソレーション第3番で始まり、第3番に還る。** 陽（01-03）→ 陰（04-05）→ 陽（06-07 朝の祈り）→ 還る。

★素材は Mutopia。選曲は `_調査_素材.py`（骨格＝0.45拍以上の音で音階の合い方を測る）。
  リスト3曲は浄書が CC BY（説明文にクレジット）。メンデルスゾーン・チャイコフスキーは PD、
  グリーグ「アルバムの綴り」は CC BY。音高と音価だけを使う。
★ピアノ独奏曲なので トラック1＝右手（旋律の側）・2＝左手（EOJ10 と同じ組み方）。
★グリーグ Op.12-7 だけテンポ変化（112→100→88 の rit.）があるので `warp_for` で伸ばす（EOJ10 と同じ）。
"""
import json, math, os, re, subprocess, time
import numpy as np
from scipy import signal
from scipy.io import wavfile
import synth, piano, midiparse

SR = synth.SR
OUT = 'album'
XFADE = 8.0
MEL_HOLD = 1.6
SPREAD = 0.35
HP_HZ = 25.0

def expand(segs):
    """区間 (lo, hi) を順に並べる `prep`（節を選ぶ・繰り返しを展開する）。"""
    def prep(notes):
        out, at = [], 0.0
        for lo, hi in segs:
            out += [(at + t - lo, d, n, v, tr) for t, d, n, v, tr in notes if lo <= t < hi]
            at += hi - lo
        out.sort(key=lambda x: (x[0], x[2]))
        return out
    return prep


def chain(*fs):
    """★テンポ地図で伸ばしてから繰り返す。順序が要る（逆にすると区切りが定まらない）。"""
    fs = [f for f in fs if f]
    if not fs:
        return None

    def prep(notes):
        for f in fs:
            notes = f(notes)
        return notes
    return prep


def thin(tr=2, grid=0.5, keep=0.4):
    """★伴奏の細かい音型を間引く `prep`（アヴェ・マリアの6連符）。

    トラック tr のうち、**grid 拍の格子に乗る打点と keep 拍以上の音だけ残す**。
    6連符は1拍に6打点あり、23.5bpmでも箏が5.0音/秒になった（EOJ11 の上限は3.4）。
    半拍の格子なら1拍2打点＝3分の1に減り、和声の形（分散の頭）は残る。"""
    def prep(notes):
        return [x for x in notes if x[4] != tr or x[1] >= keep
                or abs(x[0] / grid - round(x[0] / grid)) < 0.02]
    return prep


def top(tr=1, to=9):
    """★合唱（S+A が1トラック）の打点ごとに**いちばん上の音だけ**を tr に残し、残りを to へ回す `prep`。
    piano.build の旋律抜きは「単音か、次の音と MEL_GAP 半音以上離れた頂点」しか採らないので、
    ソプラノとアルトが3度・6度で寄り添う合唱では旋律がほとんど箏へ落ちる。"""
    def prep(notes):
        hi = {}
        for x in notes:
            if x[4] == tr:
                k = round(x[0], 3)
                if k not in hi or x[2] > hi[k][2]:
                    hi[k] = x
        keep = {id(v) for v in hi.values()}
        return [x if x[4] != tr or id(x) in keep else (x[0], x[1], x[2], x[3], to) for x in notes]
    return prep


def tempo_map(src):
    """MIDIのテンポ変化から「拍 → 基準テンポでの拍」の写像を作る（ECJ10 の build.py と同じ）。"""
    div, tempos, _ = midiparse.parse(src)
    seen = {}
    for tick, us in tempos:
        seen.setdefault(tick, us)       # 同じ時刻の重複（トラックごとの写し）は最初を取る
    pts = sorted(seen.items())
    return [(t / div, us) for t, us in pts]


def make_warp(src, ref_bpm):
    tm = tempo_map(src)
    ref = 60e6 / ref_bpm

    def W(b):
        acc, prev_b, prev_us = 0.0, 0.0, tm[0][1]
        for tb, us in tm[1:]:
            if tb >= b:
                break
            acc += (tb - prev_b) * prev_us / ref
            prev_b, prev_us = tb, us
        return acc + (b - prev_b) * prev_us / ref
    return W


def warp_for(src, ref_bpm, segs=None):
    """テンポ地図で拍を伸ばす（segs があればその順に並べ直す）。ECJ10 の `prep_for` と同じ。"""
    W = make_warp(src, ref_bpm)

    def prep(notes):
        end = max(t + d for t, d, *_ in notes)
        out, at = [], 0.0
        for lo, hi in (segs or [(0.0, end + 1e-6)]):
            for t, d, n, v, tr in notes:
                if lo <= t < hi:
                    out.append((at + W(t) - W(lo), W(t + d) - W(t), n, v, tr))
            at += W(hi) - W(lo)
        out.sort(key=lambda x: (x[0], x[2]))
        return out
    return prep



# bar：小節の拍数（四分音符で数える。繰り返しの区切りを丸める・笙の窓）。ref：テンポ地図の基準（変化のある曲だけ）
S = 'source/mids/'
SRC = {
    'C3': dict(src=S + 'LisztF__liszt-consolation-no3.mid', label='リスト コンソレーション第3番', bar=4.0, top=True),
    'C1': dict(src=S + 'LisztF__liszt-consolation-no1.mid', label='リスト コンソレーション第1番', bar=4.0),
    'OF': dict(src=S + 'TchaikovskyPI__16OldFrenchSong.mid', label='チャイコフスキー 古いフランスの歌', bar=2.0),
    'AB': dict(src=S + 'GriegE__No03_Albumblatt.mid', label='グリーグ アルバムの綴り Op.12-7', bar=2.0, ref=112),
    'GO': dict(src=S + 'Mendelssohn-BartholdyF__Lieder-ohne-Worte-Venetianisches-Gondellied-Op19-No6.mid',
               label='メンデルスゾーン ヴェネツィアの舟歌 Op.19-6', bar=3.0),
    'M85': dict(src=S + 'Mendelssohn-BartholdyF__LiederOhneWorte_-_Op85_No1.mid',
                label='メンデルスゾーン 無言歌 Op.85-1', bar=2.0),
    'MP': dict(src=S + 'TchaikovskyPI__01MorningPrayer.mid', label='チャイコフスキー 朝の祈り', bar=3.0),
}
for _v in SRC.values():
    _v['rh'], _v['lh'] = (1,), (2,)
    _v['prep'] = chain(warp_for(_v['src'], _v['ref']) if _v.get('ref') else None,
                       top(1, 2) if _v.get('top') else None)
    _v['ped'] = _v['bar'] if _v['bar'] >= 4 else _v['bar'] * 2   # 2/4・3/4・6/8 は2小節を笙の窓に

# (通し, 題, 曲, 音階, 主音pc, 移調, bpm, 旋律, 繰り返し, 箏, 笙, 旋律音量, 息, 残響)
TRACKS = [
    (1, '慰め',       'C3',  'ritsu',        1, 0, 36.0, 'shakuhachi', 1, 0.40, 0.26, 0.72, 0.42, 4.2),
    (2, '灯',         'C1',  'ritsu',        2, 0, 28.0, 'sho',        2, 0.38, 0.28, 0.66, 0.40, 4.6),
    (3, '古い歌',     'OF',  'ritsu',        7, 0, 28.0, 'shakuhachi', 3, 0.38, 0.28, 0.66, 0.38, 4.8),
    (4, '翳る',       'AB',  'miyakobushi', 10, 0, 20.0, 'sho',        1, 0.34, 0.32, 0.64, 0.34, 5.2),
    (5, '底',         'GO',  'miyakobushi',  6, 0, 20.0, None,         1, 0.34, 0.36, 0.00, 0.30, 5.6),
    (6, '無言歌',     'M85', 'ritsu',        2, 0, 26.0, 'shakuhachi', 2, 0.38, 0.28, 0.60, 0.38, 4.8),
    (7, '朝の祈り',   'MP',  'ritsu',        4, 0, 30.0, 'sho',        3, 0.38, 0.26, 0.66, 0.36, 4.6),
    (8, '還る',       'C3',  'ritsu',        1, 0, 32.0, 'shakuhachi', 1, 0.36, 0.30, 0.58, 0.34, 4.8),
]
SCENES = ['夕べ', '夜', '月', '白む']
STITCHED = '_work/慰め_1時間.wav'


def dcfix(x, hz=HP_HZ):
    """ECJ07 build.py と同じ。箏の1音あたりのDC（+1.7%）が重なって溜まるのを25Hzで落とす。

    零位相（`sosfiltfilt`）なので前後の滲みが出ない。25Hzは箏の最低音（E2＝82Hz）より
    ずっと下で、音楽の成分は落ちない。★`synth.py` は直さない（公開済みの巻が同じ関数を使う）。"""
    sos = signal.butter(4, hz, 'hp', fs=SR, output='sos')
    return np.vstack([signal.sosfiltfilt(sos, x[i]).astype(np.float32) for i in range(x.shape[0])])


def trim(x, thr=1e-3, fade=0.3):
    """頭の無音を落とし、尾は −60dB で切って fade 秒で閉じる（ECJ08 以降と同じ）。

    ★床では**尾を切るのが特に効く**。`piano.build` は末尾に12秒の余白を足すので、
      そのまま繋ぐと8秒のクロスフェードが「無音と無音」の重なりになって曲間が空く。"""
    e = np.abs(x).max(axis=0)
    i = np.where(e > thr)[0]
    if not len(i):
        return x
    a = max(0, i[0] - int(SR * 0.02))
    b = min(x.shape[1], i[-1] + int(SR * fade))
    y = x[:, a:b].copy()
    n = int(SR * fade)
    y[:, -n:] *= np.linspace(1, 0, n, dtype=np.float32)
    return y


def write(path, x, peak=0.89):
    """`synth.write_wav` と同じ（ピーク正規化して16bitで書く）。
    ★DC除去のあとで自分で正規化したいので、書き出しだけ切り出してある。"""
    x = np.asarray(x, dtype=np.float64)
    x = x / (np.abs(x).max() + 1e-9) * peak
    wavfile.write(path, SR, (x.T * 32767).astype(np.int16))


def repeat(n, bar=None):
    """★短い曲を n 回続けて鳴らす `prep`（この巻の要）。

    区切りは**小節に丸めた曲の終わり**に置く（最後の和音の実長で繋ぐと半端な位置で次が始まる）。
    `piano.build` は読んだ直後・音階へ写す前にこれを掛けるので、繰り返しの中は
    どの回も同じ音階・同じ主音になる。"""
    def prep(notes):
        end = max(t + d for t, d, *_ in notes)
        if bar:
            end = math.ceil(end / bar) * bar
        out = []
        for k in range(n):
            out += [(t + k * end, d, nn, v, tr) for t, d, nn, v, tr in notes]
        out.sort(key=lambda x: (x[0], x[2]))
        return out
    return prep


def build():
    os.makedirs(OUT, exist_ok=True)
    paths, total = [], 0.0
    for no, name, key, sc, tpc, tr, bpm, mel, rep, kg, sg, mg, air, rt in TRACKS:
        s = SRC[key]
        p = '%s/%02d_%s.wav' % (OUT, no, name)
        t0 = time.time()
        x, info = piano.build('%02d %s' % (no, name), s['src'], bpm=bpm, scale=sc, tonic_pc=tpc,
                           transpose=tr, rh_tr=s['rh'], lh_tr=s['lh'], pedal_beats=s['ped'],
                           prep=chain(s.get('prep'), repeat(rep, s['bar']) if rep > 1 else None),
                           melody=mel or 'shakuhachi',
                           koto_gain=kg, sho_gain=sg, mel_gain=0.0 if mel is None else mg,
                           air=air, rt=rt, mel_hold=MEL_HOLD, ret_audio=True, quiet=True)
        x = trim(x)
        dc = float(np.abs(x.mean(axis=1)).max())
        x = dcfix(x)
        write(p, x)
        sec = x.shape[1] / SR
        total += sec
        paths.append(p)
        print('%02d %-8s %-24s %-11s 主音%2d %5.1fbpm ×%d %-10s %6.1f秒  DC%+.4f  (%.0fs)'
              % (no, name, s['label'], sc, tpc, bpm, rep, mel or 'なし', sec, dc, time.time() - t0))
        nm = info['mel'] if mel else 0
        print('      旋律 %s  箏 %.1f音/秒  笙 %d'
              % ('%d音＝%.1f秒に1音' % (nm, sec / nm) if nm else '（なし）',
                 (info['inner'] + info['swing']) / sec, info['sho']))
    print('  素の合計 %.1f分  （繋ぐと %.1f分）'
          % (total / 60, (total - XFADE * (len(paths) - 1)) / 60))
    return paths


def level(paths):
    """★変奏ごとの音量を揃える（EOJ06 で足した工程）。

    `write` は書き出すたびにピーク0.89へ正規化するので、変奏の音量は「その変奏の波高率」で
    決まってしまう。**いちばん静かな変奏を動かさず、差を SPREAD 倍に詰める。下げるだけ。**"""
    ii = []
    for p in paths:
        r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af',
                            'ebur128=peak=true:framelog=quiet', '-f', 'null', '-'],
                           capture_output=True, text=True)
        ii.append(float(re.search(r'I:\s+(-?[\d.]+)', r.stderr).group(1)))
    lo = min(ii)
    outs = []
    print('  ── 変奏の音量を揃える（元の差 %.1fLU → %.1fLU）'
          % (max(ii) - lo, (max(ii) - lo) * SPREAD))
    for p, i in zip(paths, ii):
        g = -(1.0 - SPREAD) * (i - lo)
        q = p.replace('.wav', '_lv.wav')
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', p,
                        '-af', 'volume=%.2fdB' % g, '-c:a', 'pcm_s16le', q], check=True)
        print('     %-24s %6.1f → %6.1f LUFS  (%+.2fdB)'
              % (os.path.basename(p), i, i + g, g))
        outs.append(q)
    return outs


def stitch(paths, out=STITCHED):
    os.makedirs('_work', exist_ok=True)
    ins = []
    for p in paths:
        ins += ['-i', p]
    fc, prev = [], '[0:a]'
    for i in range(1, len(paths)):
        lab = '[x%d]' % i
        fc.append('%s[%d:a]acrossfade=d=%g:c1=tri:c2=tri%s' % (prev, i, XFADE, lab))
        prev = lab
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins +
                   ['-filter_complex', ';'.join(fc), '-map', prev, out], check=True)
    sec = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                'format=duration', '-of', 'csv=p=0', out],
                               capture_output=True, text=True).stdout)
    print('  %s  %d分%02d秒' % (out, int(sec) // 60, int(sec) % 60))
    manifest(paths, sec)
    return out, sec


def manifest(paths, total):
    """bgmkit 用の `_work/manifest.json`。**画は2変奏ごと＝4場面**（EOJ06 と同じ）。"""
    durs = [float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                  '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
            for p in paths]
    at, starts = 0.0, []
    for i, d in enumerate(durs):
        starts.append(at)
        at += d - XFADE
    cuts = [starts[i] for i in (0, 2, 4, 6)]
    man = dict(total=round(total, 4), xf=XFADE,
               tracks=[dict(start=round(c, 2), name=n) for c, n in zip(cuts, SCENES)])
    json.dump(man, open('_work/manifest.json', 'w'), ensure_ascii=False, indent=1)
    print('  画の切替: ' + '  '.join('%d:%02d' % (int(c) // 60, int(c) % 60) for c in cuts))
    print('  変奏の頭: ' + '  '.join('%d:%02d' % (int(s) // 60, int(s) % 60) for s in starts))


if __name__ == '__main__':
    t0 = time.time()
    stitch(level(build()))
    print('（通し %.0f秒）' % (time.time() - t0))
