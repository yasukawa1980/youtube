#!/usr/bin/env python3
"""Waves of Japan 用の3時間BGM生成器 v2（2026-09-20）。

**v1（WAVE05・WAVE06）が単調だった理由を構造から直したもの。**

v1は188秒の同じ形の区間を60個作ってクロスフェードで並べていた。実測すると
音量包絡の自己相関が **15秒で +0.48、180秒で +0.58〜0.62** あり、
「和音が15.0秒ちょうどの格子で替わる」「3分ごとに同じ形が戻る」が数字に出ていた。
さらに3時間かけての変化が **2dB** しかなかった。

v2は次を変える。

1. **3時間を1本の連続した時間軸として作る。** 区間もクロスフェードも無い。
   重なり（lookbehind）付きで部分ごとに書き出し、そのまま連結するだけなので継ぎ目が存在しない
2. **和音の長さが不規則**（8〜32秒）。さらに「詰まる時間帯／伸びる時間帯」が
   17分・29分周期で動くので、格子にならない
3. **調の中心が数十分かけて移ろう**（Am / C / F / Dm / Em / G）。
   すべてAナチュラルマイナーの内側なので、主音Aは常に鳴っていてよく、
   左右信号の中心（WAVE06は220Hz＝A3）との整合が崩れない
4. **音域・密度・明るさ・音量が、3時間で一巡しない周期の重ね合わせで動く**
   （7.3分・11.9分・17.3分・23.7分など素な周期）
5. **息継ぎ（点で鳴る音が数十秒止まる区間）を不規則に置く**

外部音源・第三者楽曲・サンプルは使わない。すべて数式合成。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import zlib
import sys
import time

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, sosfilt

RATE = 48_000
TOTAL = 10_800.0
CHUNK = 300.0          # 書き出しの単位
LOOKBEHIND = 48.0      # 直前から鳴り続けている音を作り直すための助走
MAX_TAIL = 26.0        # いちばん長い音（パッド）の全長

# ---------------------------------------------------------------- 巻の設定

VOLUMES = {
    "wave11": {
        "title": "WAVE11 雪の無人駅",
        "dir": "WAVE11_雪の無人駅",
        "seed": 111_111,
        "target_lufs": -16.5,
        "true_peak": -2.5,
        # 左右信号：中心146.83Hz（D3・2巡目）、差3→1Hzの下降（δの中で深く降りる）。
        # ★D3はCHORD_LIBRARYの6種すべてに馴染む（WAVE08で使用済み）。
        # ★終盤は差1Hz＝左右の音が床のD3から0.5Hzしか離れない。
        #   WAVE09（差1Hz一定）と同じ±0.22Hz・80秒を当てて床を拾わないようにする。
        "beat": {"center": 146.83, "start": 3.0, "end": 1.0, "gain_db": -41.0},
        "search_hz": 0.22,
        "window_seconds": 80.0,
        # 点で鳴る音は E F A B D の5音（都節 E F A B C の C を D に替えた陰の型）。
        # ★Aナチュラルマイナー内で未使用の組。半音 E-F を持ち、冬の夜の冷たい側に寄る。
        #   主音側にDを持つので左右信号の中心D3とも整合する。
        "melody_classes": (4, 5, 9, 11, 2),
        # 眠りへ降りる巻なので密度は未明へ向けて下げ続ける（WAVE10よりさらに薄く終える）
        "scenes": ((0.0, "暮れ方の雪", 0.94), (1920.0, "灯のともる駅", 0.88),
                   (3960.0, "雪の止んだ夜", 0.80), (6120.0, "夜更けの雪明かり", 0.74),
                   (8400.0, "未明の青", 0.68)),
    },
    "wave10": {
        "title": "WAVE10 時雨の山寺",
        "dir": "WAVE10_時雨の山寺",
        "seed": 101_010,
        "target_lufs": -16.5,
        "true_peak": -2.5,
        # 左右信号：中心220Hz（A3）、差7→3Hzの下降（θ→δの入口）。中心は2巡目に入った。
        # ★A3はCHORD_LIBRARYの主音なので、6種すべての和音の中で濁らない。
        # ★終盤は左右の音が床のA3から1.5Hzまで近づく。WAVE07（床から1Hz）の
        #   ±0.45Hz・40秒を当てて、床を拾わないようにしておく。
        "beat": {"center": 220.0, "start": 7.0, "end": 3.0, "gain_db": -41.0},
        "search_hz": 0.45,
        "window_seconds": 40.0,
        # 点で鳴る音は都節 E F A B C（WAVE07の陰旋と同じ5音）。
        # ★Aナチュラルマイナーの内側の半音なし5音はWAVE06・08・09で使い切ったので、
        #   半音を持つ組（寺と雨に合う暗い側）を2巡目として使う。
        "melody_classes": (4, 5, 9, 11, 0),
        # 眠りへ降りる巻なので密度は未明へ向けて下げ続ける
        "scenes": ((0.0, "夕暮れの時雨", 0.96), (1920.0, "灯ともし頃", 0.90),
                   (3960.0, "雨上がりの山門", 0.82), (6120.0, "夜更けの霧", 0.75),
                   (8400.0, "未明の静けさ", 0.70)),
    },
    "wave09": {
        "title": "WAVE09 天の川の高原",
        "dir": "WAVE09_天の川の高原",
        "seed": 90_909,
        "target_lufs": -16.5,
        "true_peak": -2.5,
        # 左右信号：中心130.81Hz（C3）、差1Hz一定のδ。既刊でいちばん深い一定。
        # ★C3はCHORD_LIBRARYのAm（3度）・C（根音）・F（5度）・Dm（7度）に入る。
        # ★差1Hzなので左右の音は床のC3から0.5Hzしか離れていない（WAVE07の半分）。
        #   探索を±0.22Hzに絞り、抜き出しを80秒に伸ばして分解能を取り戻す。
        "beat": {"center": 130.81, "start": 1.0, "end": 1.0, "gain_db": -41.0},
        "search_hz": 0.22,
        "window_seconds": 80.0,
        # 点で鳴る音はD民謡音階 D F G A C の5音だけ（半音を持たない・既刊のどれとも別の組）。
        # WAVE08のヨナ抜き C D E G A とは E→F の1音違いで、夜の暗い側に寄る。
        "melody_classes": (2, 5, 7, 9, 0),
        # δの最深部なので密度は夜半へ向けて下げ、薄明でわずかに戻す
        "scenes": ((0.0, "宵の天の川", 0.90), (1920.0, "夜半の高原", 0.84),
                   (3960.0, "満天", 0.76), (6120.0, "未明の静けさ", 0.70),
                   (8400.0, "薄明", 0.76)),
    },
    "wave08": {
        "title": "WAVE08 朝顔の垣根",
        "dir": "WAVE08_朝顔の垣根",
        "seed": 80_808,
        "target_lufs": -16.5,
        "true_peak": -2.5,
        # 左右信号：中心146.83Hz（D3）、差5→10Hzの上昇（θ→α）。未明から朝へ。
        # ★D3はCHORD_LIBRARYの6種すべてに馴染む（Am=4度・C=9度・F=6度・Dm=根音・Em=7度・G=5度）。
        #   左右は床のD3から2.5〜5Hz離れるので、探索幅は既定の±0.8Hzのままでよい。
        "beat": {"center": 146.83, "start": 5.0, "end": 10.0, "gain_db": -41.0},
        # 点で鳴る音はヨナ抜き長音階 C D E G A の5音だけ（半音を持たない明るい側）。
        # WAVE06の律 A B D E G とは B→C の1音違い、WAVE07の陰旋とは3音違い。
        "melody_classes": (0, 2, 4, 7, 9),
        # 目覚めの巻なので密度は朝へ向けて上げ、最後だけわずかに落ち着かせる
        "scenes": ((0.0, "未明の藍", 0.78), (1920.0, "蕾の垣根", 0.86),
                   (3960.0, "ほどける花", 0.95), (6120.0, "朝露", 1.04),
                   (8400.0, "朝の光", 0.98)),
    },
    "wave07": {
        "title": "WAVE07 月夜の芒原",
        "dir": "WAVE07_月夜の芒原",
        "seed": 70_707,
        "target_lufs": -16.5,
        "true_peak": -2.5,
        # 左右信号：中心164.81Hz（E3）、差2Hz一定のδ。
        # ★E3はAナチュラルマイナーの属音なので、CHORD_LIBRARYの6種すべてに馴染む
        #   （Am=5度・C=3度・F=7度・Dm=9度・Em=根音・G=6度）。
        # ★差が2Hzしかないので、左右の音は床のE3から1Hzしか離れていない。
        #   既刊（8〜12Hz離れていた）と違って探索幅0.8Hzでは床に届いてしまうため、
        #   この巻だけ探索を±0.45Hzに絞り、抜き出しを40秒に伸ばして分解能を上げる。
        "beat": {"center": 164.81, "start": 2.0, "end": 2.0, "gain_db": -41.0},
        "search_hz": 0.45,
        "window_seconds": 40.0,
        # 点で鳴る音は陰旋（ヨナ抜き短音階）A B C E F の5音だけ。
        # WAVE06の律 A B D E G と分ける（秋とδに合う暗い側）。
        "melody_classes": (9, 11, 0, 4, 5),
        "scenes": ((0.0, "月の出", 0.95), (1920.0, "宵の芒原", 1.00),
                   (3960.0, "夜半の月", 0.86), (6120.0, "未明前の風", 0.74),
                   (8400.0, "薄明の露", 0.80)),
    },
    "wave06": {
        "title": "WAVE06 花明かりの丘",
        "dir": "WAVE06_花明かりの丘",
        "seed": 60_606,
        "target_lufs": -16.5,
        "true_peak": -2.5,
        # 左右信号：中心220Hz（A3）、差4→8Hzの上昇
        "beat": {"center": 220.0, "start": 4.0, "end": 8.0, "gain_db": -41.0},
        # 点で鳴る音は律音階 A B D E G の5音だけ
        "melody_classes": (9, 11, 2, 4, 7),
        "scenes": ((0.0, "宵の花明かり", 1.00), (1920.0, "花の帳", 0.94),
                   (3960.0, "深夜の風", 0.84), (6120.0, "花散らしの静けさ", 0.78),
                   (8400.0, "未明の薄青", 0.88)),
    },
    "wave05": {
        "title": "WAVE05 雪明かりの書院",
        "dir": "WAVE05_雪明かりの書院",
        "seed": 50_505,
        "target_lufs": -16.5,
        "true_peak": -2.5,
        # 既刊の説明文に合わせ、左180Hz／右190Hzの10Hz一定を維持する
        "beat": {"center": 185.0, "start": 10.0, "end": 10.0, "gain_db": -41.0},
        # D major / B minor。ヨナ抜き長音階 D E F# A B
        "melody_classes": (2, 4, 6, 9, 11),
        "scenes": ((0.0, "深雪の夜", 0.88), (1920.0, "雪降る書院", 1.00),
                   (3960.0, "雪明かり", 1.08), (6120.0, "東雲", 1.02),
                   (8400.0, "朝白", 0.86)),
    },
}

# Aナチュラルマイナーの内側に収めた和音。どれもAが濁らない。
# (根音の度数ラベル, 5声の音程) — 音程はMIDI番号。
CHORD_LIBRARY = {
    "Am": ((33, 40, 45, 48, 55), (33, 40, 45, 47, 52), (28, 40, 45, 52, 57),
           (33, 45, 52, 57, 60), (21, 33, 40, 45, 52)),
    "C":  ((36, 43, 48, 52, 55), (36, 43, 47, 52, 59), (31, 43, 48, 55, 60),
           (36, 48, 55, 59, 64), (24, 36, 43, 48, 55)),
    "F":  ((29, 36, 41, 45, 52), (29, 36, 45, 48, 53), (33, 41, 48, 53, 57),
           (29, 41, 48, 53, 60), (17, 29, 36, 45, 48)),
    "Dm": ((26, 33, 38, 45, 48), (26, 38, 45, 50, 57), (33, 38, 45, 50, 53),
           (26, 33, 45, 48, 57), (14, 26, 33, 38, 45)),
    "Em": ((28, 35, 40, 47, 50), (28, 35, 42, 47, 52), (31, 40, 47, 52, 59),
           (28, 40, 47, 55, 59), (16, 28, 35, 40, 47)),
    "G":  ((31, 38, 43, 47, 52), (31, 38, 45, 50, 55), (35, 43, 50, 55, 59),
           (31, 43, 50, 55, 62), (19, 31, 38, 43, 50)),
}
ROOTS = ("Am", "C", "F", "Dm", "Em", "G")


# ★★正弦波を使わない。正弦波は周期を持つので、ゆっくりしたうねりを足すと
# その周期に自己相関の山が立つ（実測：5.1分の成分を入れたら300秒に +0.102 の山）。
# 代わりに「不規則な節を平滑化した曲線」を使う。これには周期が存在しない。
_CURVES: dict = {}


def _curve(cfg: dict, name: str, minutes: float):
    key = (cfg["seed"], name, minutes)
    if key not in _CURVES:
        salt = zlib.crc32(name.encode("utf-8"))
        rng = np.random.default_rng(cfg["seed"] + salt)
        span = TOTAL + 400.0
        knots = [-200.0]
        while knots[-1] < span:
            knots.append(knots[-1] + float(rng.uniform(0.55, 1.7)) * minutes * 30.0)
        values = rng.normal(0.0, 1.0, len(knots))
        grid = np.arange(-200.0, span, 1.0)
        curve = np.interp(grid, knots, values)
        sigma = max(2.0, minutes * 15.0)
        half = int(sigma * 3)
        window = np.exp(-0.5 * (np.arange(-half, half + 1) / sigma) ** 2)
        window /= window.sum()
        curve = np.convolve(curve, window, mode="same")
        curve /= float(curve.std() + 1e-9)
        _CURVES[key] = (grid, np.clip(curve, -2.6, 2.6))
    return _CURVES[key]


def slow(cfg: dict, name: str, minutes: float, t):
    """-1〜+1 前後の、周期を持たないゆっくりした揺れ。"""
    grid, curve = _curve(cfg, name, minutes)
    return np.interp(t, grid, curve)


def scene_value(cfg: dict, t: float) -> tuple[str, float]:
    """場面の名前と密度。境界は60秒かけて混ぜる（音は絵より早く移ってよい）。"""
    scenes = cfg["scenes"]
    index = 0
    for i, (start, _, _) in enumerate(scenes):
        if t >= start:
            index = i
    name, density = scenes[index][1], scenes[index][2]
    if index + 1 < len(scenes):
        nxt = scenes[index + 1][0]
        if t > nxt - 60.0:
            ratio = (t - (nxt - 60.0)) / 60.0
            density = density * (1 - ratio) + scenes[index + 1][2] * ratio
    return name, density


# ---------------------------------------------------------------- 時間軸

def chord_timeline(cfg: dict) -> list[tuple[float, float, tuple[int, ...], float]]:
    """(開始, 長さ, 5声, 明るさ) の並び。長さは不規則で、格子にならない。"""
    rng = np.random.default_rng(cfg["seed"] + 11)
    out = []
    t = -LOOKBEHIND - MAX_TAIL
    previous_root = None
    while t < TOTAL + MAX_TAIL:
        # 「詰まる時間帯」と「伸びる時間帯」。17分と29分は3時間で一巡しない
        stretch = 1.0 + 0.40 * float(slow(cfg, 'stretch', 17.0, t))
        duration = float(rng.uniform(8.0, 24.0)) * max(0.55, stretch)

        # 調の中心の移ろい。11.9分と23.7分の重ね合わせで根音を選ぶ
        drift = 0.5 + 0.34 * float(slow(cfg, 'tonal', 21.0, t))
        favour = ROOTS[min(len(ROOTS) - 1, int(drift * len(ROOTS)))]
        if previous_root == favour and rng.random() < 0.55:
            favour = ROOTS[int(rng.integers(0, len(ROOTS)))]
        previous_root = favour

        # 音域。低い声部を選ぶか高い声部を選ぶかも、ゆっくり動く
        register = 0.5 + 0.34 * float(slow(cfg, 'register', 12.0, t))
        voicings = CHORD_LIBRARY[favour]
        pick = min(len(voicings) - 1, int(register * len(voicings)))
        if rng.random() < 0.3:
            pick = int(rng.integers(0, len(voicings)))

        brightness = 0.5 + 0.34 * float(slow(cfg, 'brightness', 18.0, t))
        out.append((t, duration, voicings[pick], brightness))
        t += duration
    return out


def point_events(cfg: dict, chords: list) -> dict[str, list[tuple]]:
    """ピアノ・プラック・点景音。速さは複数のゆっくりした波の重ね合わせ。"""
    rng = np.random.default_rng(cfg["seed"] + 23)
    classes = cfg["melody_classes"]
    notes = [n for n in range(45, 93) if n % 12 in classes]

    def chord_at(t: float) -> tuple[int, ...]:
        for start, duration, voicing, _ in chords:
            if start <= t < start + duration:
                return voicing
        return chords[0][2]

    def pick(t: float, low: int, high: int) -> int:
        chord = chord_at(t)
        cands = [n for n in notes if low <= n <= high]
        classes_in = {n % 12 for n in chord}
        weights = np.array([2.4 if n % 12 in classes_in else 1.0 for n in cands])
        weights /= weights.sum()
        return int(rng.choice(cands, p=weights))

    # 息継ぎ：点で鳴る音が止まる区間を不規則に置く
    rests = []
    t = float(rng.uniform(120.0, 400.0))
    while t < TOTAL:
        length = float(rng.uniform(35.0, 95.0))
        rests.append((t, t + length))
        t += float(rng.uniform(300.0, 900.0))

    def resting(t: float) -> bool:
        return any(a <= t < b for a, b in rests)

    piano, pluck, point = [], [], []

    t = -LOOKBEHIND
    while t < TOTAL:
        _, density = scene_value(cfg, max(t, 0.0))
        rate = 0.72 + 0.38 * float(slow(cfg, 'piano_rate', 9.0, t))
        gap = float(rng.uniform(7.0, 17.0)) / max(0.35, rate * density)
        t += gap
        if t >= TOTAL or resting(t):
            continue
        low = 55 + int(8 * (0.5 + 0.34 * float(slow(cfg, 'register', 12.0, t))))
        piano.append((t, pick(t, low, low + 20),
                      float(rng.uniform(0.48, 0.92) * density),
                      float(rng.uniform(0.32, 0.68))))

    # プラックは活動する時間帯と、まったく鳴らない時間帯に分かれる
    t = -LOOKBEHIND
    while t < TOTAL:
        wave = 0.5 + 0.34 * float(slow(cfg, 'pluck_wave', 11.0, t))
        if wave < 0.42 or resting(t):
            t += float(rng.uniform(12.0, 30.0))
            continue
        _, density = scene_value(cfg, max(t, 0.0))
        t += float(rng.uniform(4.5, 11.0)) / max(0.4, wave * density)
        if t >= TOTAL:
            break
        pluck.append((t, pick(t, 69, 90),
                      float(rng.uniform(0.40, 0.76) * density * wave),
                      float(rng.uniform(0.22, 0.78))))

    t = -LOOKBEHIND
    while t < TOTAL:
        t += float(rng.uniform(18.0, 46.0)) * (1.2 - 0.4 * (0.5 + 0.34 * float(slow(cfg, 'point_rate', 24.0, t))))
        if t >= TOTAL or resting(t):
            continue
        point.append((t, pick(t, 60, 81), float(rng.uniform(0.7, 1.15))))

    return {"piano": piano, "pluck": pluck, "point": point, "rests": rests}


# ---------------------------------------------------------------- 楽器

def midi_hz(note: float) -> float:
    return 440.0 * (2.0 ** ((note - 69) / 12.0))


def equal_power(length: int, attack: float, release: float) -> np.ndarray:
    env = np.ones(length, dtype=np.float32)
    a = min(int(attack * RATE), length // 2)
    r = min(int(release * RATE), length // 2)
    if a > 0:
        env[:a] = np.sin(np.linspace(0, math.pi / 2, a, dtype=np.float32)) ** 2
    if r > 0:
        env[-r:] = np.cos(np.linspace(0, math.pi / 2, r, dtype=np.float32)) ** 2
    return env


def add_pad(left, right, offset, note, duration, gain, voice, brightness):
    i0 = max(0, int(round(offset * RATE)))
    i1 = min(len(left), i0 + int(round(duration * RATE)))
    if i1 <= i0:
        return
    n = i1 - i0
    t = np.arange(n, dtype=np.float32) / RATE
    base = midi_hz(note)
    detune = 2.0 ** ((0.16 + (voice % 3) * 0.035) / 1200.0)
    drift = 0.008 * np.sin(2.0 * np.pi * t / (17.0 + voice * 1.7) + voice)
    pl = 2.0 * np.pi * (base / detune) * t + drift
    pr = 2.0 * np.pi * (base * detune) * t - drift
    # brightness で上の倍音が増減する＝3時間かけて音色が動く
    h2 = 0.065 + 0.075 * brightness
    h3 = 0.018 + 0.030 * brightness
    cl = np.sin(pl) + h2 * np.sin(2.0 * pl + 0.7) + h3 * np.sin(3.0 * pl + 1.9)
    cr = np.sin(pr + 0.08) + h2 * np.sin(2.0 * pr + 1.0) + h3 * np.sin(3.0 * pr + 2.2)
    # ★★包絡は「音符の本来の長さ」で作ってから切る。
    # 切られた長さに対して余韻を付けると、バッファの端をまたぐ音が
    # そこで消えてしまう（書き出しの単位＝300秒ごとに音が沈み、
    # 自己相関に300秒の山が立った。2026-09-21に発見）。
    full = max(n, int(round(duration * RATE)))
    env = equal_power(full, 5.5, 7.0)[:n]
    breath = 0.94 + 0.06 * np.sin(2.0 * np.pi * t / (11.0 + voice))
    scale = gain * env * breath
    left[i0:i1] += (cl * scale).astype(np.float32)
    right[i0:i1] += (cr * scale).astype(np.float32)


def add_piano(left, right, offset, note, strength, pan, index):
    duration = 9.5
    i0 = int(round(offset * RATE))
    i1 = min(len(left), i0 + int(round(duration * RATE)))
    if i1 <= max(i0, 0):
        return
    i0 = max(i0, 0)
    n = i1 - i0
    t = np.arange(n, dtype=np.float32) / RATE
    f = midi_hz(note)
    p = 2.0 * np.pi * f * t
    tone = np.sin(p) + 0.20 * np.sin(2.01 * p + 0.3) + 0.065 * np.sin(3.98 * p + 1.1)
    env = (1.0 - np.exp(-t / 0.020)) * (0.78 * np.exp(-t / 2.8) + 0.22 * np.exp(-t / 7.8))
    rng = np.random.default_rng(1_000 + index)
    hammer = rng.standard_normal(n).astype(np.float32)
    hammer = sosfilt(butter(2, 1_900.0, btype="lowpass", fs=RATE, output="sos"), hammer)
    hammer = hammer.astype(np.float32) * np.exp(-t / 0.030) * 0.035
    sound = (tone * env + hammer) * (0.047 * strength)
    left[i0:i1] += (sound * math.sqrt(1.0 - pan)).astype(np.float32)
    right[i0:i1] += (sound * math.sqrt(pan)).astype(np.float32)


def add_pluck(left, right, offset, note, strength, pan, index):
    duration = 7.0
    i0 = int(round(offset * RATE))
    i1 = min(len(left), i0 + int(round(duration * RATE)))
    if i1 <= max(i0, 0):
        return
    i0 = max(i0, 0)
    n = i1 - i0
    t = np.arange(n, dtype=np.float32) / RATE
    f = midi_hz(note)
    p = 2.0 * np.pi * f * t
    tone = np.sin(p) + 0.22 * np.sin(2.004 * p + 0.8) + 0.085 * np.sin(3.01 * p + 1.6)
    env = (1.0 - np.exp(-t / 0.006)) * (0.72 * np.exp(-t / 1.45) + 0.28 * np.exp(-t / 4.6))
    rng = np.random.default_rng(2_000 + index)
    pick = rng.standard_normal(n).astype(np.float32)
    pick = sosfilt(butter(2, (650.0, 4_800.0), btype="bandpass", fs=RATE, output="sos"), pick)
    pick = pick.astype(np.float32) * np.exp(-t / 0.012) * 0.020
    sound = (tone * env + pick) * (0.036 * strength)
    left[i0:i1] += (sound * math.sqrt(1.0 - pan)).astype(np.float32)
    right[i0:i1] += (sound * math.sqrt(pan)).astype(np.float32)


def add_point(left, right, offset, note, strength, index):
    duration = 15.0
    i0 = int(round(offset * RATE))
    i1 = min(len(left), i0 + int(round(duration * RATE)))
    if i1 <= max(i0, 0):
        return
    i0 = max(i0, 0)
    n = i1 - i0
    t = np.arange(n, dtype=np.float32) / RATE
    f = midi_hz(note)
    p = 2.0 * np.pi * f * t
    tone = np.sin(p) + 0.07 * np.sin(2.0 * p + 0.4)
    full = max(n, int(round(duration * RATE)))
    env = (1.0 - np.exp(-t / 1.8)) * np.exp(-t / 7.2) * equal_power(full, 1.2, 3.0)[:n]
    pan = 0.30 + 0.40 * ((index * 0.61803398875) % 1.0)
    gain = 0.014 * strength
    left[i0:i1] += (tone * env * gain * math.sqrt(1.0 - pan)).astype(np.float32)
    right[i0:i1] += (tone * env * gain * math.sqrt(pan)).astype(np.float32)


# ---------------------------------------------------------------- 描画

def render_range(cfg: dict, chords: list, events: dict,
                 start: float, end: float) -> np.ndarray:
    """[start-LOOKBEHIND, end) を作り、[start, end) を返す。継ぎ目は存在しない。"""
    origin = start - LOOKBEHIND
    frames = int(round((end - origin) * RATE))
    left = np.zeros(frames, dtype=np.float32)
    right = np.zeros(frames, dtype=np.float32)

    for index, (at, duration, voicing, brightness) in enumerate(chords):
        if at + duration + MAX_TAIL < origin or at >= end:
            continue
        gains = (0.027, 0.023, 0.019, 0.016, 0.012)
        for voice, note in enumerate(voicing):
            add_pad(left, right, at - origin, note, duration + 8.0,
                    gains[voice], voice + index, brightness)

    for index, (at, note, strength, pan) in enumerate(events["piano"]):
        if at + 10.0 < origin or at >= end:
            continue
        add_piano(left, right, at - origin, note, strength, pan, index)
    for index, (at, note, strength, pan) in enumerate(events["pluck"]):
        if at + 7.5 < origin or at >= end:
            continue
        add_pluck(left, right, at - origin, note, strength, pan, index)
    for index, (at, note, strength) in enumerate(events["point"]):
        if at + 15.5 < origin or at >= end:
            continue
        add_point(left, right, at - origin, note, strength, index)

    # 空気の層。両端を0.75秒で出し入れするので、連結しても段差にならない
    rng = np.random.default_rng(cfg["seed"] + int(origin))
    noise = rng.standard_normal(frames).astype(np.float32)
    noise = sosfilt(butter(2, 1_500.0, btype="lowpass", fs=RATE, output="sos"), noise)
    noise = sosfilt(butter(1, 70.0, btype="highpass", fs=RATE, output="sos"), noise)
    noise = noise.astype(np.float32)
    noise /= float(np.std(noise) + 1e-12)
    noise *= equal_power(frames, 0.75, 0.75)
    t_abs = origin + np.arange(frames, dtype=np.float64) / RATE
    air = 0.0013 * (0.76 + 0.24 * np.sin(2.0 * np.pi * t_abs / 47.0))
    left += (noise * air).astype(np.float32)
    delay = int(0.019 * RATE)
    right[delay:] += (noise[:-delay] * air[delay:]).astype(np.float32)

    # 音量の大きなうねり。5.1分・8.9分・14.7分を重ね、3時間で一巡しない
    # ★3時間かけての変化。速い揺れと遅い揺れを重ねるが、どちらも周期を持たない。
    # v1はここが2dBしか動かず「始まりと終わりで何も変わらない」曲になっていた。
    arc_db = (1.30 * slow(cfg, "swell_slow", 34.0, t_abs)
              + 0.85 * slow(cfg, "swell_mid", 13.0, t_abs)
              + 0.45 * slow(cfg, "swell_fast", 5.5, t_abs))
    arc = (10.0 ** (np.clip(arc_db, -5.0, 4.0) / 20.0)).astype(np.float32)
    left *= arc
    right *= arc

    dry_l, dry_r = left.copy(), right.copy()
    for seconds, gain in ((0.21, 0.17), (0.47, 0.115), (0.83, 0.075),
                          (1.37, 0.048), (2.11, 0.030)):
        d = int(round(seconds * RATE))
        left[d:] += dry_r[:-d] * gain
        right[d:] += dry_l[:-d] * gain
    del dry_l, dry_r, noise

    band = butter(3, (28.0, 8_500.0), btype="bandpass", fs=RATE, output="sos")
    left = sosfilt(band, left).astype(np.float32)
    right = sosfilt(band, right).astype(np.float32)

    cut = int(round(LOOKBEHIND * RATE))
    stereo = np.column_stack((left[cut:], right[cut:])).astype(np.float32)
    # ★チャンクごとにピークで正規化しない。片方だけ縮むと境界に段差ができる。
    # 全体の音量は仕上げで一度だけ当てる。
    return stereo


# ---------------------------------------------------------------- 検査

def envelope_metrics(samples: np.ndarray, rate: int = RATE) -> dict:
    """★単調さを数字で見る。ここが v1 で見落とした指標。"""
    mono = samples.mean(axis=1)
    step = rate // 4
    n = len(mono) // step
    rms = np.sqrt((mono[:n * step].reshape(n, step) ** 2).mean(axis=1)) + 1e-9
    e = 20.0 * np.log10(rms)
    e = e - e.mean()
    ac = np.correlate(e, e, mode="full")[len(e) - 1:]
    ac /= ac[0]
    per_second = rate / step
    # ★「なだらかに高い」のと「特定の遅れに山が立つ」のは別物。
    # 後者だけが単調さ（＝同じ形の繰り返し）なので、滑らかな土台を引いて山を探す。
    # ★探索は素材の長さの1/10まで。それより長い遅れは独立な標本が足りず、
    #   数字が暴れる（1時間の素材で600秒の山を見ると偽の山が出る）。
    # ★端の処理に convolve(mode="same") を使うと、配列の端で土台が低く出て
    #   そこに偽の山が立つ。uniform_filter1d(mode="nearest") を使う。
    limit = int(min(600.0, (len(e) / per_second) / 10.0) * per_second)
    limit = max(limit, int(60 * per_second))
    baseline = uniform_filter1d(ac[:limit], size=int(20 * per_second) | 1, mode="nearest")
    residual = ac[:limit] - baseline
    lags = {}
    for seconds in (15, 30, 60, 180, 300):
        index = int(seconds * per_second)
        if index < limit:
            lags[f"{seconds}s"] = round(float(ac[index]), 3)
    low = int(10 * per_second)
    search = residual[low:]
    peak_index = int(search.argmax()) + low
    worst_lag = round(peak_index / per_second, 1)
    worst = float(residual[peak_index])
    blocks = []
    per_block = int(600 * per_second)
    for i in range(len(e) // per_block):
        blocks.append(float(e[i * per_block:(i + 1) * per_block].mean()))
    return {
        "envelope_std_db": round(float(e.std()), 2),
        "autocorrelation": lags,
        "search_limit_seconds": round(limit / per_second, 1),
        "strongest_period_seconds": worst_lag,
        "strongest_period_height": round(worst, 3),
        "ten_minute_block_spread_db": round(max(blocks) - min(blocks), 2) if len(blocks) > 1 else None,
        "ten_minute_blocks": len(blocks),
    }


def run(args, capture=False):
    return subprocess.run(args, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None,
                          stderr=subprocess.PIPE if capture else None)


def probe(path: Path) -> dict:
    result = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_name,sample_rate,channels",
        "-of", "json", str(path),
    ], capture=True)
    return json.loads(result.stdout)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------- 左右信号

def beat_expression(cfg: dict) -> str:
    b = cfg["beat"]
    left_base = b["center"] - b["start"] / 2.0
    right_base = b["center"] + b["start"] / 2.0
    # ★t²の係数は (差の変化量)/(4×全長)。半分を全長で割ると2倍になる
    coefficient = (b["end"] - b["start"]) / (4.0 * TOTAL)
    gain = 10.0 ** (b["gain_db"] / 20.0)
    sign = "-" if coefficient >= 0 else "+"
    c = abs(coefficient)
    return (
        f"aevalsrc={gain:.12f}*sin(2*PI*({left_base:.6f}*t{sign}{c:.12f}*t*t))|"
        f"{gain:.12f}*sin(2*PI*({right_base:.6f}*t{'+' if sign == '-' else '-'}{c:.12f}*t*t))"
        f":s={RATE}:d={TOTAL}"
    )


def beat_frequencies(cfg: dict, seconds: float) -> tuple[float, float]:
    b = cfg["beat"]
    difference = b["start"] + (b["end"] - b["start"]) * seconds / TOTAL
    return b["center"] - difference / 2.0, b["center"] + difference / 2.0


# ---------------------------------------------------------------- 実行

def synthesize(cfg: dict, out_dir: Path, seconds: float, *, label: str) -> Path:
    """★中間ファイルを作らず、1本のffmpegへ直接流し込む。

    以前は区間ごとにFLACを書いて `-f concat -c copy` でつないでいたが、
    **FLACのフレームの継ぎ目が壊れ、300秒ごとに0.25秒ほどの欠落が入っていた**
    （dtsが単調増加でないという警告が22万件出ていたのがその正体。2026-09-21に発見）。
    生のPCMを直接渡せば、連結という工程自体が無くなる。
    """
    chords = chord_timeline(cfg)
    events = point_events(cfg, chords)
    out_dir.mkdir(parents=True, exist_ok=True)
    joined = out_dir / f"_{label}_連結.flac"
    if joined.exists():
        probed = float(probe(joined)["format"]["duration"])
        if abs(probed - seconds) < 0.5:
            print(f"  連結済みを再利用（{probed:.1f}秒）", flush=True)
            return joined

    process = subprocess.Popen([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-f", "f32le", "-ar", str(RATE), "-ac", "2", "-i", "pipe:0",
        "-c:a", "flac", "-compression_level", "6", "-sample_fmt", "s32", str(joined),
    ], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdin is not None
    written = 0
    start = 0.0
    while start < seconds:
        end = min(seconds, start + CHUNK)
        began = time.time()
        block = render_range(cfg, chords, events, start, end)
        try:
            process.stdin.write(block.tobytes())
        except BrokenPipeError as error:      # ffmpegが落ちた理由を必ず出す
            process.stdin = None
            _, stderr = process.communicate()
            raise RuntimeError(
                f"ffmpegが{start:.0f}秒の書き込み中に終了しました: "
                f"{stderr.decode('utf-8', 'replace')[-600:]}") from error
        written += len(block)
        print(f"  {start:7.0f}〜{end:7.0f}秒  {time.time() - began:5.1f}s", flush=True)
        start = end
    # ★stdinを自分で閉じてから communicate() を呼ぶと
    # 「flush of closed file」で落ちる。communicate() に任せる。
    _, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError("FLACの書き出しに失敗しました: "
                           + stderr.decode("utf-8", "replace")[-600:])
    expected = int(round(seconds * RATE))
    if written != expected:
        raise RuntimeError(f"標本数が合いません: {written} != {expected}")
    return joined


def measure(path: Path, rate: int = 2_000) -> dict:
    """★2kHzモノラルで読む。

    単調さの指標は0.25秒ごとの音量しか使わないので原寸で読む必要がない。
    48kHzステレオで3時間を読むと4.15GBをメモリに載せることになり、そこで落ちた。
    """
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
                          "-ar", str(rate), "-f", "f32le", "-acodec", "pcm_f32le", "-"],
                         check=True, stdout=subprocess.PIPE).stdout
    samples = np.frombuffer(raw, dtype="<f4").reshape(-1, 1)
    return envelope_metrics(samples, rate)


def loudness(path: Path, cfg: dict) -> dict:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
         f"loudnorm=I={cfg['target_lufs']}:TP={cfg['true_peak']}:LRA=7:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True, check=True)
    return json.loads(re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, re.S)[-1])


def master(cfg: dict, joined: Path, final: Path) -> dict:
    """左右信号を重ね、**静的なゲインだけ**で音量を合わせる。

    ★loudnorm をそのまま使うと Normalization Type が Dynamic になり、
    3時間かけての大きなうねりを圧縮して平らに戻してしまう（v1がこれだった）。
    測るのには使い、当てるのは volume フィルタの一定値にする。
    """
    mix = (f"[0:a][1:a]amix=inputs=2:duration=first:normalize=0,"
           f"afade=t=in:st=0:d=3,afade=t=out:st={TOTAL - 10}:d=10[m]")
    probe_args = ["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(joined),
                  "-f", "lavfi", "-i", beat_expression(cfg),
                  "-filter_complex", mix + f";[m]loudnorm=I={cfg['target_lufs']}:"
                  f"TP={cfg['true_peak']}:LRA=7:print_format=json[out]",
                  "-map", "[out]", "-f", "null", "-"]
    result = subprocess.run(probe_args, capture_output=True, text=True, check=True)
    measured = json.loads(re.findall(r"\{\s*\"input_i\".*?\}", result.stderr, re.S)[-1])
    gain = cfg["target_lufs"] - float(measured["input_i"])
    headroom = cfg["true_peak"] - (float(measured["input_tp"]) + gain)
    if headroom < 0:
        gain += headroom
        print(f"  トゥルーピークに当たるので {headroom:+.2f} dB 引きます", flush=True)
    print(f"  測定 {measured['input_i']} LUFS / TP {measured['input_tp']} "
          f"→ 静的ゲイン {gain:+.2f} dB", flush=True)
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(joined),
         "-f", "lavfi", "-i", beat_expression(cfg),
         "-filter_complex", mix + f";[m]volume={gain:.3f}dB[out]",
         "-map", "[out]", "-ar", str(RATE), "-ac", "2", "-c:a", "flac",
         "-compression_level", "8", "-sample_fmt", "s32", str(final)])
    after = loudness(final, cfg)
    return {"static_gain_db": round(gain, 3), "before": measured, "after": after}


def verify_beat(cfg: dict, path: Path) -> list[dict]:
    """★設計値の周りを0.005Hz刻みで探索し、実測周波数そのものを出す。

    ★探索幅は床の主音を拾わない範囲に留める。既定は±0.8Hz（差が8Hz以上ある巻）。
    **うなりが小さい巻は左右の音が床の主音に近づく**ので、巻ごとに `search_hz` で
    狭める（WAVE07は差2Hz＝床のE3から1Hzしか離れていないため±0.45Hz）。
    狭めたぶんの分解能は `window_seconds` を伸ばして取り戻す。
    """
    findings = []
    span = float(cfg.get("search_hz", 0.8))
    window = float(cfg.get("window_seconds", 20.0))
    for position in (300.0, 2_700.0, 5_400.0, 8_100.0, 10_500.0):
        raw = subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(position),
             "-t", str(window), "-i", str(path), "-f", "f32le", "-acodec", "pcm_f32le", "-"],
            check=True, stdout=subprocess.PIPE).stdout
        audio = np.frombuffer(raw, dtype="<f4").reshape(-1, 2)
        t = np.arange(len(audio), dtype=np.float64) / RATE
        design = beat_frequencies(cfg, position + window / 2.0)
        row = {"position_seconds": position}
        seen = []
        for channel, name, target in ((0, "left", design[0]), (1, "right", design[1])):
            grid = np.arange(target - span, target + span + 1e-9, 0.005)
            levels = np.array([abs(np.vdot(audio[:, channel], np.exp(-2j * np.pi * f * t)))
                               * 2.0 / len(audio) for f in grid])
            best = int(levels.argmax())
            other = abs(np.vdot(audio[:, 1 - channel],
                                np.exp(-2j * np.pi * grid[best] * t))) * 2.0 / len(audio)
            seen.append(float(grid[best]))
            row[f"{name}_design_hz"] = round(target, 4)
            row[f"{name}_measured_hz"] = round(float(grid[best]), 4)
            row[f"{name}_error_hz"] = round(float(grid[best]) - target, 4)
            row[f"{name}_dbfs"] = round(float(20 * np.log10(levels[best] + 1e-15)), 1)
            row[f"{name}_separation_db"] = round(
                float(20 * np.log10((levels[best] + 1e-15) / (other + 1e-15))), 1)
        row["measured_difference_hz"] = round(seen[1] - seen[0], 4)
        findings.append(row)
    return findings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("volume", choices=sorted(VOLUMES))
    parser.add_argument("--minutes", type=float, default=30.0,
                        help="試験用に作る長さ（分）")
    parser.add_argument("--full", action="store_true", help="3時間を作る")
    parser.add_argument("--out", type=Path)
    arguments = parser.parse_args()
    cfg = VOLUMES[arguments.volume]
    seconds = TOTAL if arguments.full else arguments.minutes * 60.0
    out_dir = arguments.out or (Path(__file__).resolve().parent.parent /
                                cfg["dir"] / "本編音声v2")
    label = "full" if arguments.full else f"{int(arguments.minutes)}min"
    print(f"{cfg['title']}  {seconds / 60:.0f}分ぶんを作ります", flush=True)
    began = time.time()
    joined = synthesize(cfg, out_dir, seconds, label=label)
    metrics = measure(joined)
    if arguments.full:
        final = out_dir / f"{arguments.volume}_3時間_自前合成_v2.flac"
        print("仕上げ（左右信号と静的ゲイン）", flush=True)
        mastering = master(cfg, joined, final)
        beat = verify_beat(cfg, final)
        joined.unlink()
        report = out_dir / f"{arguments.volume}_v2_検品.json"
        report.write_text(json.dumps({
            "volume": cfg["title"], "file": str(final),
            "bytes": final.stat().st_size, "sha256": sha256(final),
            "monotony": metrics, "mastering": mastering, "beat": beat,
            "elapsed_seconds": round(time.time() - began, 1),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"final": str(final),
                          "lufs": mastering["after"]["input_i"],
                          "true_peak": mastering["after"]["input_tp"],
                          "lra": mastering["after"]["input_lra"],
                          "monotony": metrics}, ensure_ascii=False, indent=2))
        print(report)
        return
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    report = out_dir / f"{label}_単調さ検査.json"
    report.write_text(json.dumps({
        "volume": cfg["title"], "seconds": seconds,
        "file": str(joined), "metrics": metrics,
        "targets": {"strongest_period_height": "< 0.08（特定の周期に山が立たないこと）",
                    "ten_minute_block_spread_db": "> 3.0"},
        "elapsed_seconds": round(time.time() - began, 1),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
