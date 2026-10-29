# -*- coding: utf-8 -*-
"""EOJ13 の素材候補を測る：トラックの中身・拍数・テンポ・骨格（0.45拍以上）での音階の合い方。"""
import glob, os, collections, sys
import midiparse, wafu
N = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

def mel(ns, tr, th=0.45):
    g = collections.defaultdict(list)
    for t, d, n, v, k in ns:
        if k == tr and d >= th: g[round(t, 3)].append(n)
    return [(t, max(v)) for t, v in sorted(g.items())]

for p in sorted(glob.glob('source/mids/*.mid')):
    ns, tempos, div = midiparse.notes(p)
    ns = [x for x in ns if x[1] > 0]
    cnt = collections.Counter(x[4] for x in ns)
    med = {k: sorted(x[2] for x in ns if x[4] == k)[cnt[k] // 2] for k in cnt}
    end = max(t + d for t, d, *_ in ns)
    bpm0 = 60e6 / tempos[0][1] if tempos else 120
    print('\n%s  %.0f拍  テンポ%d個(初%.0fbpm)  ' % (os.path.basename(p), end, len(tempos), bpm0)
          + '  '.join('tr%d:%d音/中%s' % (k, cnt[k], med[k]) for k in sorted(cnt)))
    for tr in sorted(cnt, key=lambda k: -med[k])[:2]:
        m0 = mel(ns, tr)
        if len(m0) < 15: continue
        iv0 = [b[1] - a[1] for a, b in zip(m0, m0[1:])]
        res = []
        for sc in ('ritsu', 'miyakobushi'):
            for t in range(12):
                m1 = mel(wafu.transform(ns, t, sc), tr)
                iv1 = [b[1] - a[1] for a, b in zip(m1, m1[1:])]
                sh = sum(abs(a - c) >= 2 for a, c in zip(iv0, iv1)) / len(iv0) * 100
                cr = sum(a != 0 and c == 0 for a, c in zip(iv0, iv1)) / len(iv0) * 100
                res.append((sh + cr, sh, cr, sc, N[t]))
        res.sort()
        bm = min((r for r in res if r[3] == 'miyakobushi'))
        print('   tr%d 骨格%d音  最良 %s%s %.1f/%.1f   都節最良 %s %.1f/%.1f'
              % (tr, len(m0), res[0][3][:3], res[0][4], res[0][1], res[0][2], bm[4], bm[1], bm[2]))
