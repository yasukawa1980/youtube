# -*- coding: utf-8 -*-
"""EOJ15 の整音済wavを独立に測る（尺・I・LRA・TP・DC）。
`album.py` の出力を信用せず、できた物を読んで測る。

★継ぎ目の確認は**7箇所すべて**を並べる。 `master.edges` は manifest（＝画の切替4箇所）しか
  見ないので、変奏どうしの継ぎ目（8変奏＝7箇所）は3箇所しか聴けない。"""
import glob, json, os, re, subprocess, sys
import numpy as np
from scipy.io import wavfile

VOLS = [('EOJ15_月に寄す', 'eoj15')]
XFADE = 8.0
BASE = os.path.dirname(os.path.abspath(__file__))


def run(a):
    return subprocess.run(a, capture_output=True, text=True)


def ebur(p):
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af',
             'ebur128=peak=true:framelog=quiet', '-f', 'null', '-'])
    return dict(re.findall(r'^\s+(I|LRA|Peak):\s+(-?[\d.]+)', r.stderr, re.M))


def dur(p):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                      '-of', 'csv=p=0', p]).stdout)


def dc(p):
    sr, x = wavfile.read(p)
    x = x.astype(np.float32) / 32768.0
    return float(np.abs(x.mean(axis=0)).max()), float(np.abs(x).max())


def joins(d, fin, out):
    """変奏の継ぎ目（クロスフェードの中心）の前後12秒を並べて1本にする。"""
    ps = sorted(glob.glob(os.path.join(d, 'album', '*_lv.wav')))
    at, starts = 0.0, []
    for p in ps:
        starts.append(at)
        at += dur(p) - XFADE
    mids = [s + XFADE / 2 for s in starts[1:]]
    segs = []
    for i, t in enumerate(mids):
        q = os.path.join(d, '_work', '_j%02d.wav' % i)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(max(0.0, t - 12)),
                        '-t', '24', '-i', fin, '-af', 'afade=t=in:d=1,afade=t=out:st=23:d=1',
                        '-c:a', 'pcm_s16le', q], check=True)
        segs.append(q)
    ins = []
    for q in segs:
        ins += ['-i', q]
    fc = ''.join('[%d:a]' % i for i in range(len(segs))) + 'concat=n=%d:v=0:a=1[o]' % len(segs)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins +
                   ['-filter_complex', fc, '-map', '[o]', '-c:a', 'libmp3lame', '-b:a', '192k',
                    out], check=True)
    for q in segs:
        os.remove(q)
    return mids


print('%-22s %9s %7s %6s %7s %8s %7s' % ('巻', '尺', 'I', 'LRA', 'TP', 'DC', 'ピーク'))
for d, tag in VOLS:
    p = os.path.join(BASE, d, '_work', '%s_整音済.wav' % tag)
    g = ebur(p)
    s = dur(p)
    o, pk = dc(p)
    print('%-22s %2d分%02d秒 %7s %6s %7s %8.6f %7.3f'
          % (d, int(s) // 60, int(s) % 60, g['I'], g['LRA'], g['Peak'], o, pk))
    m = joins(os.path.join(BASE, d), p, os.path.join(BASE, d, '_work', '_確認_継ぎ目7箇所.mp3'))
    print('   継ぎ目: ' + '  '.join('%d:%02d' % (int(t) // 60, int(t) % 60) for t in m))
