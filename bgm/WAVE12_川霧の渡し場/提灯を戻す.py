#!/usr/bin/env python3
"""第5場面の提灯が編集で小さくなったので、基準（第3場面）の提灯を同じ位置に戻して暗くする。

提灯の外形だけを取り、線形RGBで暗くして重ねる。小さい提灯は基準の外形の内側に収まるので消える。
元の版は 画像/生成直後/wave12_05_未明の水面_提灯が小さい版.png。
"""
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent / "画像"
BASE = HERE / "wave12_03_霧の立つ夜.png"
SOURCE = HERE / "生成直後" / "wave12_05_未明の水面_提灯が小さい版.png"
OUT = HERE / "wave12_05_未明の水面.png"
BOX = (1270, 240, 1390, 380)   # x0, y0, x1, y1
GAIN = 0.34                    # 提灯の線形倍率（04より暗く、05の「低い灯り」に合わせる）


def to_linear(v):
    return np.power(v / 255.0, 2.2)


def to_srgb(v):
    return np.clip(np.power(np.clip(v, 0, 1), 1 / 2.2) * 255.0, 0, 255)


base = cv2.imread(str(BASE)).astype(np.float32)
scene = cv2.imread(str(SOURCE)).astype(np.float32)
x0, y0, x1, y1 = BOX
gray = cv2.cvtColor(base[y0:y1, x0:x1].astype(np.uint8), cv2.COLOR_BGR2GRAY)
_, body = cv2.threshold(gray, 95, 255, cv2.THRESH_BINARY)
count, labels, stats, _ = cv2.connectedComponentsWithStats(body)
largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
left, top, width, height = stats[largest][:4]
mask = (labels == largest).astype(np.uint8) * 255
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
# 上下の黒い口輪も提灯の一部として含める
cap = int(round(height * 0.09))
inset = int(round(width * 0.22))
mask[max(top - cap, 0):top + 2, left + inset:left + width - inset] = 255
mask[top + height - 2:top + height + cap, left + inset:left + width - inset] = 255
alpha = cv2.GaussianBlur(mask.astype(np.float32) / 255.0, (0, 0), 0.9)[..., None]

lantern = to_srgb(to_linear(base[y0:y1, x0:x1]) * GAIN)
scene[y0:y1, x0:x1] = lantern * alpha + scene[y0:y1, x0:x1] * (1 - alpha)
cv2.imwrite(str(OUT), np.clip(scene, 0, 255).astype(np.uint8))
print("提灯の外形", left + x0, top + y0, width, height)
