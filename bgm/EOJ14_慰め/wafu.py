# -*- coding: utf-8 -*-
"""西洋音階の楽曲データを和の音階へ写す。"""

# 主音からの音程（半音）
SCALES = {
    'miyakobushi': (0, 1, 5, 7, 8),      # 都節：短調をこれへ
    'yonanuki':    (0, 2, 4, 7, 9),      # ヨナ抜き長音階：長調をこれへ
    'ritsu':       (0, 2, 5, 7, 9),      # 律：都節より明るい
}


def allowed_pcs(tonic_pc, scale):
    return sorted({(tonic_pc + i) % 12 for i in SCALES[scale]})


def map_note(n, tonic_pc, scale, tie='up'):
    """音高を音階内の最も近い音へ寄せる。等距離のときは tie で決める。"""
    pcs = allowed_pcs(tonic_pc, scale)
    best, bestd = None, 99
    for cand in pcs:
        for off in (-12, 0, 12):
            d = (cand + off) - (n % 12)
            if abs(d) < abs(bestd) or (abs(d) == abs(bestd) and
                                       ((d > 0) if tie == 'up' else (d < 0))):
                bestd, best = d, cand
    return n + bestd


def step_up(n, tonic_pc, scale):
    """音階上でひとつ上の音。"""
    pcs = allowed_pcs(tonic_pc, scale)
    for k in range(1, 13):
        if (n + k) % 12 in pcs:
            return n + k
    return n + 12


def transform(notes, tonic_pc, scale, tie='up'):
    """(開始, 長さ, 音高, ベロシティ, トラック) の列を写像し、直後の同音を1段上げる。"""
    out = []
    prev_pitch, prev_t = None, -9.0
    for t, d, n, v, tr in notes:
        m = map_note(n, tonic_pc, scale, tie)
        if d < 0.4 and prev_pitch == m and 0 < t - prev_t < 0.5:
            m = step_up(m, tonic_pc, scale)
        if d < 0.4:
            prev_pitch, prev_t = m, t
        out.append((t, d, m, v, tr))
    return out
