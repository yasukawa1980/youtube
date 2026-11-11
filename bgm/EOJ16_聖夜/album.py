# -*- coding: utf-8 -*-
"""EOJ16：クリスマスの賛美歌16曲で2時間の床を組む（EOJ15 の album.py を写した）。

**「きよしこの夜」で始まり、「きよしこの夜」（いちばん遅く）に還る。**
宵（01-04・陽）→ 底（05-08・都節3曲）→ 夜半（09-12）→ 朝（13-16）。画は4曲ごとに4場面。

★素材は Mutopia。使った版はすべて PD（`source/一覧.tsv`）。音高と音価だけを使う。
★音階は `_調査_調と音階.py`（骨格のずれ／潰れ／保持率）で決めた。長調は「原調のヨナ抜き」（＝律で主音+7）が
  保持率8〜9割で最良になる曲が多い。きよしこの夜は都節でも ずれ3%・潰れ6% で崩れない（06に置いた）。
★賛美歌の譜は トラック1＝S+A・2＝T+B。`top(1, 2)` でいちばん上の音（ソプラノ）だけを旋律の側に残す。
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


def tie(tr=1, gap=0.05):
    """★同じ高さで続く音を1本につなぐ `prep`（パーセル「寒さの歌」）。

    声が同じ音を8分で刻み続ける（寒さに震える描写）ので、そのままでは旋律が2.8秒に1音と吹きすぎる。
    笙で伸ばせば震えは和音の揺れとして残る。"""
    def prep(notes):
        out, last = [], {}
        for x in sorted(notes, key=lambda x: (x[0], x[2])):
            if x[4] != tr:
                out.append(x)
                continue
            p = last.get(x[2])
            if p is not None and abs(out[p][0] + out[p][1] - x[0]) <= gap:
                t, d, n, v, k = out[p]
                out[p] = (t, x[0] + x[1] - t, n, v, k)
                continue
            last = {x[2]: len(out)}
            out.append(x)
        out.sort(key=lambda x: (x[0], x[2]))
        return out
    return prep


def fill(rest=0.9, tr=2, back=4.0, hold=2.0):
    """★全休止を埋める `prep`（グリーグ「山の歌」）。

    中間部にまる1小節の休み（4拍）が4箇所あり、36bpm では6.7秒・残響が切れたあと**4.5〜5.8秒の無音**になった
    （本編 42:46〜46:12 に6箇所・ショートCにも5.2秒）。音価を伸ばしても箏は減衰するだけで効かなかった。
    **休みの頭に、直前 back 拍の最低音を左手（tr）として1つ置く** → 笙の窓の最低音になり、休みの小節を笙が保つ。
    楽譜に無い音を足すのはこの休みだけ（打点は動かさないので尺も変わらない）。
    ★長く伸ばす音も**hold 拍で鳴り止むとみなす**（箏は減衰し、旋律の笙は9秒で切れる）。
      48拍目の旋律7拍・50拍目の低音5拍だけの小節で、本編 42:46 に4.5秒の無音が残ったため。"""
    def prep(notes):
        notes = sorted(notes, key=lambda x: (x[0], x[2]))
        add, end = [], 0.0
        for t, d, n, v, k in notes:
            prev = [x for x in notes if end - back <= x[0] < end]
            if t - end > rest and prev:          # 曲頭の休み（前に音が無い）は埋めない
                lo = min(prev, key=lambda x: x[2])
                add.append((end, t - end, lo[2], lo[3], tr))
            end = max(end, t + min(d, hold))
        print('      全休止を笙で保つ: ' + '  '.join('%.0f拍(%.0f拍)' % (a[0], a[1]) for a in add if a[1] >= 2))
        return sorted(notes + add, key=lambda x: (x[0], x[2]))
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
HYMN = dict(rh=(1,), lh=(2,), top=True)
SRC = {
    'SN':  dict(src=S + 'SN_orig.mid', label='グルーバー きよしこの夜（原典）', bar=3.0, rh=(1,), lh=(8,), top=8),
    'SNH': dict(src=S + 'SN_hymn.mid', label='グルーバー きよしこの夜（賛美歌）', bar=3.0, **HYMN),
    'ADF': dict(src=S + 'ADF.mid', label='ウェイド 神の御子は今宵しも', bar=4.0, **HYMN),
    'GKW': dict(src=S + 'GKW.mid', label='伝承 Good King Wenceslas', bar=4.0, **HYMN),
    'VOM': dict(src=S + 'VOM.mid', label='バッハ 高き天より BWV606', bar=4.0, rh=(1,), lh=(2, 3)),
    'GSL': dict(src=S + 'GSL.mid', label='伝承 グリーンスリーブス', bar=3.0, **HYMN),
    'VENI': dict(src=S + 'VENI.mid', label='伝承 久しく待ちにし', bar=4.0, **HYMN),
    'ROS': dict(src=S + 'ROS.mid', label='伝承 エサイの根より', bar=2.0, **HYMN),   # ★70拍。4拍に丸めると繰り返しの継ぎ目に4.8秒の無音（11/11実測）
    'OHN': dict(src=S + 'OHN.mid', label='アダン さやかに星はきらめき', bar=4.0, rh=(2,), lh=(3, 4), thin=(3, 1.0)),
    'MID': dict(src=S + 'MID.mid', label='ウィリス 天なる神には', bar=3.0, **HYMN),
    'HARK': dict(src=S + 'HARK.mid', label='メンデルスゾーン 天には栄え', bar=4.0, **HYMN),
    'NOEL': dict(src=S + 'NOEL.mid', label='伝承 牧人ひつじを', bar=3.0, **HYMN),
    'JOY': dict(src=S + 'JOY.mid', label='ヘンデル（伝） もろびとこぞりて', bar=2.0, **HYMN),
    'DULCI': dict(src=S + 'DULCI.mid', label='バッハ 甘き喜びのうちに BWV751', bar=4.0, rh=(1,), lh=(2, 3), top=True,
                  cut=224),
}
for _v in SRC.values():
    _t = _v.get('top')
    _v['prep'] = chain(top(1, 2 if _t is True else _t) if _t else None,
                       thin(*_v['thin']) if _v.get('thin') else None,
                       expand([(0.0, _v['cut'])]) if _v.get('cut') else None)
    _v['ped'] = _v['bar'] if _v['bar'] >= 4 else _v['bar'] * 2   # 2/4・3/4・6/8 は2小節を笙の窓に

# (通し, 題, 曲, 音階, 主音pc, 移調, bpm, 旋律, 繰り返し, 箏, 笙, 旋律音量, 息, 残響)
# 主音pc：律の主音（ヨナ抜きT＝律T+7）。C=0 C#=1 D=2 D#=3 E=4 F=5 F#=6 G=7 G#=8 A=9 A#=10 B=11
TRACKS = [
    (1,  'きよしこの夜',   'SN',   'ritsu',        9, 0, 20.0, 'shakuhachi', 4, 0.38, 0.28, 0.70, 0.40, 4.4),
    (2,  '神の御子',       'ADF',  'ritsu',        4, 0, 21.0, 'sho',        2, 0.38, 0.28, 0.64, 0.40, 4.6),
    (3,  'ウェンセスラス', 'GKW',  'ritsu',        4, 0, 27.0, 'koto',       3, 0.38, 0.28, 0.62, 0.38, 4.6),
    (4,  '高き天より',     'VOM',  'ritsu',        2, 0, 16.0, None,         3, 0.36, 0.30, 0.00, 0.34, 5.0),
    (5,  'グリーンスリーブス', 'GSL', 'miyakobushi', 3, 0, 20.0, 'shakuhachi', 3, 0.36, 0.30, 0.66, 0.36, 5.0),
    (6,  '深い夜の聖夜',   'SNH',  'miyakobushi',  5, 0, 19.0, 'sho',        4, 0.34, 0.32, 0.62, 0.32, 5.4),
    (7,  '待ちわびる',     'VENI', 'miyakobushi',  2, 0, 20.0, None,         4, 0.34, 0.36, 0.00, 0.30, 5.6),
    (8,  'エサイの根',     'ROS',  'ritsu',        0, 0, 19.0, 'shakuhachi', 2, 0.36, 0.30, 0.64, 0.34, 5.0),
    (9,  'さやかに星は',   'OHN',  'ritsu',        7, 0, 17.0, 'shakuhachi', 1, 0.36, 0.28, 0.70, 0.40, 4.8),
    (10, '天なる神には',   'MID',  'ritsu',        5, 0, 19.0, 'koto',       3, 0.38, 0.28, 0.62, 0.38, 4.6),
    (11, '天には栄え',     'HARK', 'ritsu',        0, 0, 21.0, 'sho',        2, 0.38, 0.28, 0.64, 0.38, 4.6),
    (12, '牧人',           'NOEL', 'ritsu',        9, 0, 19.0, None,         2, 0.36, 0.32, 0.00, 0.34, 5.0),
    (13, 'もろびとこぞりて', 'JOY', 'ritsu',       9, 0, 20.0, 'shakuhachi', 4, 0.38, 0.28, 0.66, 0.38, 4.6),
    (14, '甘き喜び',       'DULCI', 'ritsu',       7, 0, 28.0, 'sho',        1, 0.38, 0.28, 0.62, 0.38, 4.6),
    (15, '星の名残',       'OHN',  'ritsu',        2, 0, 17.0, None,         1, 0.36, 0.30, 0.00, 0.34, 5.0),
    (16, '還る',           'SN',   'ritsu',        9, 0, 17.0, 'shakuhachi', 3, 0.36, 0.30, 0.58, 0.34, 4.8),
]
# ★旋律が8分音符で歩く曲は mel_hold を下げて尺八・笙へ回す（20bpm の8分＝1.5秒 < 1.6）
HOLD = {1: 1.2, 5: 1.2, 6: 1.2, 10: 1.2, 13: 1.2, 16: 1.2}
SCENES = ['宵', '夜', '聖夜', '朝']
STITCHED = '_work/聖夜_2時間.wav'


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
                           air=air, rt=rt, mel_hold=HOLD.get(no, MEL_HOLD), ret_audio=True, quiet=True)
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
    """bgmkit 用の `_work/manifest.json`。**画は4曲ごと＝4場面**（16曲・2時間）。"""
    durs = [float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                  '-of', 'csv=p=0', p], capture_output=True, text=True).stdout)
            for p in paths]
    at, starts = 0.0, []
    for i, d in enumerate(durs):
        starts.append(at)
        at += d - XFADE
    cuts = [starts[i] for i in (0, 4, 8, 12)]
    man = dict(total=round(total, 4), xf=XFADE,
               tracks=[dict(start=round(c, 2), name=n) for c, n in zip(cuts, SCENES)])
    json.dump(man, open('_work/manifest.json', 'w'), ensure_ascii=False, indent=1)
    print('  画の切替: ' + '  '.join('%d:%02d' % (int(c) // 60, int(c) % 60) for c in cuts))
    print('  変奏の頭: ' + '  '.join('%d:%02d' % (int(s) // 60, int(s) % 60) for s in starts))


if __name__ == '__main__':
    t0 = time.time()
    stitch(level(build()))
    print('（通し %.0f秒）' % (time.time() - t0))
