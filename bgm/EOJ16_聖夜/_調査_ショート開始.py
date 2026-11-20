# -*- coding: utf-8 -*-
"""ショートの開始位置を測る（EOJ13 の決め方：2秒刻みで「45秒の本体」と「頭4秒」を測り、
本体が曲の中央値±1dB の中で頭がいちばん大きい所を採る）。曲の頭と尾の30秒（クロスフェード）は避ける。"""
import glob, subprocess, sys
import numpy as np
from scipy.io import wavfile

FIN = '/Users/ryo/Desktop/BGM/5_Echoes of Old Japan/EOJ16_素材_聖夜/_work/music_bed.wav'  # 整音済みの本編
XF = 8.0
# 章の頭は 構成.md の表（album/ の _lv.wav は残していない）
T = ['0:00:00','0:07:42','0:15:13','0:22:41','0:30:08','0:37:16','0:44:45','0:51:53','0:59:10','1:06:35','1:14:07','1:21:38','1:29:07','1:36:37','1:44:34','1:52:00']
starts = [sum(int(v) * k for v, k in zip(t.split(':'), (3600, 60, 1))) for t in T]
TOTAL = 7143.8
durs = [b - a + XF for a, b in zip(starts, starts[1:] + [TOTAL - XF])]
print('章の頭:', '  '.join('%d:%02d:%02d' % (s // 3600, s % 3600 // 60, s % 60) for s in starts))
sr, x = wavfile.read(FIN)
m = (x.astype(np.float64) / 32768).mean(axis=1) ** 2
c = np.concatenate([[0], np.cumsum(m)])
db = lambda a, b: 10 * np.log10((c[int(b * sr)] - c[int(a * sr)]) / ((b - a) * sr) + 1e-12)
for no in map(int, sys.argv[1:]):
    a, b = starts[no - 1] + 30, starts[no - 1] + durs[no - 1] - XF - 30 - 45
    ts = np.arange(a, b, 2.0)
    body = np.array([db(t, t + 45) for t in ts]); head = np.array([db(t, t + 4) for t in ts])
    med = np.median(body); ok = np.abs(body - med) <= 1.0
    i = np.argmax(np.where(ok, head - body, -99))
    t = ts[i]
    print('%02d  %d:%02d:%02d  本体 %.1fdB（中央値 %.1f）  頭 %+.1fdB' % (no, t // 3600, t % 3600 // 60, t % 60, body[i], med, head[i] - body[i]))
