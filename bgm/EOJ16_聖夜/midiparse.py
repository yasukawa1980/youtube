# -*- coding: utf-8 -*-
"""標準MIDIファイルの最小パーサ（音高・音価だけ取り出す）。"""
import struct

def _vlq(b, i):
    v = 0
    while True:
        c = b[i]; i += 1
        v = (v << 7) | (c & 0x7f)
        if not c & 0x80:
            return v, i

def parse(path):
    b = open(path, 'rb').read()
    assert b[:4] == b'MThd'
    fmt, ntrk, div = struct.unpack('>HHH', b[8:14])
    i = 14
    tracks, tempos = [], []
    for _ in range(ntrk):
        assert b[i:i+4] == b'MTrk', b[i:i+4]
        ln = struct.unpack('>I', b[i+4:i+8])[0]
        d = b[i+8:i+8+ln]; i += 8 + ln
        j, t, run, ev = 0, 0, None, []
        while j < len(d):
            dt, j = _vlq(d, j); t += dt
            st = d[j]
            if st & 0x80:
                run = st; j += 1
            else:
                st = run
            if st == 0xff:
                mt = d[j]; j += 1
                ln2, j = _vlq(d, j)
                pay = d[j:j+ln2]; j += ln2
                if mt == 0x51:
                    tempos.append((t, pay[0] << 16 | pay[1] << 8 | pay[2]))
            elif st in (0xf0, 0xf7):
                ln2, j = _vlq(d, j); j += ln2
            else:
                hi = st & 0xf0
                n = 1 if hi in (0xc0, 0xd0) else 2
                a = d[j:j+n]; j += n
                if hi == 0x90 and a[1] > 0:
                    ev.append((t, 'on', a[0], a[1]))
                elif hi == 0x80 or (hi == 0x90 and a[1] == 0):
                    ev.append((t, 'off', a[0], 0))
        tracks.append(ev)
    return div, tempos, tracks

def notes(path):
    """[(開始拍, 長さ拍, ノート番号, ベロシティ, トラック番号)] を返す。単位は四分音符。"""
    div, tempos, tracks = parse(path)
    out = []
    for ti, ev in enumerate(tracks):
        held = {}
        for t, kind, n, v in ev:
            if kind == 'on':
                held.setdefault(n, []).append((t, v))
            else:
                if held.get(n):
                    t0, v0 = held[n].pop(0)
                    out.append((t0 / div, (t - t0) / div, n, v0, ti))
    out.sort(key=lambda x: (x[0], x[2]))
    return out, tempos, div
