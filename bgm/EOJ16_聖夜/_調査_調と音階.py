# -*- coding: utf-8 -*-
"""EOJ16：曲ごとに調を推定し、5音の候補（律・都節）を旋律の骨格のずれ／潰れで並べる。
律(0,2,5,7,9) とヨナ抜き(0,2,4,7,9) は主音をずらすと同じ5音（律X＝ヨナ抜きX+5、つまりヨナ抜きT＝律T+7）なので、律だけで測る。
旋律は「打点ごとのいちばん上の音」（合唱は S+A が1トラック）。"""
import collections, glob, os
import midiparse, wafu
N = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
MAJ = [6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]
MIN = [6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17]
MELTR = {'OHN': 2}

def key(ns):
    h = [0.0]*12
    for t, d, n, v, k in ns: h[n % 12] += d
    def cor(a, b):
        ma, mb = sum(a)/12, sum(b)/12
        return sum((x-ma)*(y-mb) for x, y in zip(a, b)) / (sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))**.5
    c = [(cor(h, MAJ[-i:]+MAJ[:-i]), N[i]+'長') for i in range(12)] + [(cor(h, MIN[-i:]+MIN[:-i]), N[i]+'短') for i in range(12)]
    return max(c)[1]

def mel(ns, tr, th=0.45):
    g = collections.defaultdict(list)
    for t, d, n, v, k in ns:
        if k == tr and d >= th: g[round(t, 3)].append(n)
    return [(t, max(v)) for t, v in sorted(g.items())]

for p in sorted(glob.glob('source/mids/*.mid')):
    k0 = os.path.basename(p)[:-4]
    ns = [x for x in midiparse.notes(p)[0] if x[1] > 0]
    tr = MELTR.get(k0, 1)
    m0 = mel(ns, tr); iv0 = [b[1]-a[1] for a, b in zip(m0, m0[1:])]
    res = []
    for sc in ('ritsu', 'miyakobushi'):
        for t in range(12):
            m1 = mel(wafu.transform(ns, t, sc), tr); iv1 = [b[1]-a[1] for a, b in zip(m1, m1[1:])]
            sh = sum(abs(a-c) >= 2 for a, c in zip(iv0, iv1))/len(iv0)*100
            cr = sum(a != 0 and c == 0 for a, c in zip(iv0, iv1))/len(iv0)*100
            res.append((round(sh+cr, 1), sh, cr, sc, t))
    res.sort()
    kk = key(ns)
    tonic = N.index(kk[:-1])
    yon = [r for r in res if r[3] == 'ritsu' and r[4] == (tonic+7) % 12][0]
    print('%-8s %-5s 旋律tr%d %2d音 | 最良 ' % (k0, kk, tr, len(m0)) + '  '.join(
        '%s%s %.1f/%.1f' % ('律' if r[3]=='ritsu' else '都', N[r[4]], r[1], r[2]) for r in res[:3])
        + ' | 原調ヨナ抜き(律%s) %.1f/%.1f' % (N[yon[4]], yon[1], yon[2]))
