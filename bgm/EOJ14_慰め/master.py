# -*- coding: utf-8 -*-
"""二段掛けの loudnorm で整音する。EOJ06 の master.py をそのまま持ってきた。

★ECJ05は入力が −23.49 LUFS と低く、TP 側の制約で loudnorm が止まったので
  **目標を1dB高く置いて当て込んだ**（−13.0狙い → 実測 −14.4）。
  ECJ06 も自前合成で入力が低いはずだが、**当て込みが要るかは1回目の実測を見てから決める。**
★TP は −1.9 で指定して wav 実測 −1.6 に収める。15分の作品版は AAC 段で +0.4dB 上がる。"""
import json, os, re, subprocess, sys

SRC = '_work/慰め_1時間.wav'
FIN = '_work/eoj14_整音済.wav'
LUFS, TP = -14.0, -2.0   # ★1時間の床は TP −2.0 で焼く（EOJ06 で決めた）。
                         #   −1.6 だと wav −1.4 → AAC −1.0 で推奨上限ちょうどに乗る。
                         #   −2.0 なら wav −1.7 → AAC −1.1 で公開済みの EOJ03・EOJ04 と同じ所に着く
WANT = -14.0             # 楽器が鳴るラインは Whispers / DOJ と同じ −14


def run(args):
    return subprocess.run(args, capture_output=True, text=True)


def normalize(src, out, lufs=-18.0, tp=-1.5, lra=11.0):
    """1回目で実測し、その値を渡して2回目で当てる。単発では目標に届かない。"""
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-af',
             'loudnorm=I=%g:TP=%g:LRA=%g:print_format=json' % (lufs, tp, lra),
             '-f', 'null', '-'])
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', r.stderr, re.S)
    d = json.loads(m.group(0))
    print('  1回目の実測: I=%s LRA=%s TP=%s' % (d['input_i'], d['input_lra'], d['input_tp']))
    af = ('loudnorm=I=%g:TP=%g:LRA=%g:measured_I=%s:measured_LRA=%s:'
          'measured_TP=%s:measured_thresh=%s:offset=%s:linear=true:print_format=json'
          % (lufs, tp, lra, d['input_i'], d['input_lra'], d['input_tp'],
             d['input_thresh'], d['target_offset']))
    r = run(['ffmpeg', '-y', '-hide_banner', '-nostats', '-i', src, '-af', af,
             '-ar', '48000', '-c:a', 'pcm_s16le', out])
    print('  normalization_type:', re.search(r'"normalization_type"\s*:\s*"(\w+)"', r.stderr).group(1))
    return out


def measure(path):
    r = run(['ffmpeg', '-hide_banner', '-nostats', '-i', path,
             '-af', 'ebur128=peak=true:framelog=quiet', '-f', 'null', '-'])
    g = dict(re.findall(r'^\s+(I|LRA|Peak):\s+(-?[\d.]+)', r.stderr, re.M))
    return g


def edges(path, out='_work/_確認_曲の変わり目.mp3', half=12.0):
    """manifest の切替点の前後を切り出して並べる。"""
    man = json.load(open('_work/manifest.json'))
    starts = [t['start'] for t in man['tracks'][1:]]
    segs = []
    for i, t in enumerate(starts):
        p = '_work/_seg%02d.wav' % i
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error',
                        '-ss', str(max(0.0, t - half)), '-t', str(half * 2), '-i', path,
                        '-af', 'afade=t=in:d=1,afade=t=out:st=%g:d=1' % (half * 2 - 1),
                        '-c:a', 'pcm_s16le', p], check=True)
        segs.append(p)
    ins = []
    for p in segs:
        ins += ['-i', p]
    fc = ''.join('[%d:a]' % i for i in range(len(segs))) + 'concat=n=%d:v=0:a=1[o]' % len(segs)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + ins +
                   ['-filter_complex', fc, '-map', '[o]',
                    '-c:a', 'libmp3lame', '-b:a', '192k', out], check=True)
    for p in segs:
        os.remove(p)
    return out, starts


PRE = '_work/_前段リミッター.wav'
PRE_DB = -4.8   # ★EOJ14：入力TP −0.30 を +1.0dB 持ち上げると TP −2.0 に収まらず、loudnorm が dynamic に落ちた。
                #   まれな箏の打点だけを先に −4.8dBFS で抑え（サンプル値で抑えるので TP は1.2dB上に残る）、loudnorm を linear のまま掛ける。


def prelimit(src, out, db=PRE_DB):
    lim = 10 ** (db / 20)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', src, '-af',
                    'alimiter=limit=%.4f:attack=5:release=80:level=0:asc=1' % lim,
                    '-c:a', 'pcm_s24le', out], check=True)
    print('  前段リミッター %.1fdBFS 後:' % db, measure(out))
    return out


if __name__ == '__main__':
    print('整音（前段リミッター → 二段掛け）')
    normalize(prelimit(SRC, PRE), FIN, lufs=LUFS, tp=TP)
    print('  仕上がり:', measure(FIN))
    o, st = edges(FIN)
    print('曲の変わり目 %d箇所 → %s' % (len(st), o))
