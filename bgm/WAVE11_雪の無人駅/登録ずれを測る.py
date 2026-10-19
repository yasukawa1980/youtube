#!/usr/bin/env python3
"""WAVE11 の5場面（WAVE10版を写した）が基準画像（第3場面）と同じ位置にあるかを測る。

ディゾルブは物を動かさず重ねるだけなので、ホームの灯りと待合室の窓（小さく明るい孤立物）が
ずれると10秒間「灯りが2つ」に見える（WAVE07の月の教訓）。

1. 全体：輪郭（勾配の強さ）どうしの位相相関で、画面全体の平行移動を出す
2. 局所：石段・山門・灯籠の周りの小窓ごとに同じことをして、部分的な歪みを出す
3. 火袋：基準の火袋の周り 90×90 で、場面側の明るい塊の重心を比べる
4. 明るさ：平均輝度・16未満・250以上・最大の黒塊・局所std
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
IMAGES = HERE / "画像"
REFERENCE = "wave11_03_雪の止んだ夜.png"
SCENES = ("wave11_01_暮れ方の雪.png", "wave11_02_灯のともる駅.png", REFERENCE,
          "wave11_04_夜更けの雪明かり.png", "wave11_05_未明の青.png")
# 基準画像で見たホームの灯り・待合室の窓のおおよその中心（1920×1080）。基準の上で重心を取り直して使う
LANTERNS = ((1158, 340), (1575, 522))
# 局所の小窓（x, y, 幅, 高さ）：ホームの縁・待合室・灯りの柱・線路・左の杉
WINDOWS = {"ホームの縁": (800, 640, 1100, 300), "待合室": (1250, 300, 520, 380),
           "灯りの柱": (1110, 260, 140, 420), "線路": (580, 640, 600, 400),
           "左の杉と土手": (100, 150, 600, 700)}


def gray(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f"読めません: {path}")
    if image.shape[:2] != (1080, 1920):
        raise SystemExit(f"1920×1080ではありません: {path.name} {image.shape[1]}×{image.shape[0]}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)


def edges(g: np.ndarray) -> np.ndarray:
    # ★明るさの違う場面どうしを比べるので、輝度でなく正規化した輪郭で比べる
    g = cv2.GaussianBlur(g, (0, 0), 1.2)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
    m = np.sqrt(gx * gx + gy * gy)
    return (m - m.mean()) / (m.std() + 1e-6)


def shift(a: np.ndarray, b: np.ndarray) -> tuple[float, float, float]:
    window = cv2.createHanningWindow(a.shape[::-1], cv2.CV_32F)
    (dx, dy), response = cv2.phaseCorrelate(a, b, window)
    return round(float(dx), 2), round(float(dy), 2), round(float(response), 3)


def lantern_centres(g: np.ndarray, guesses) -> list[tuple[float, float]]:
    out = []
    for x, y in guesses:
        patch = g[y - 45:y + 45, x - 45:x + 45]
        top = np.percentile(patch, 97)
        mask = patch >= top
        ys, xs = np.nonzero(mask)
        weights = patch[mask]
        out.append((x - 45 + float((xs * weights).sum() / weights.sum()),
                    y - 45 + float((ys * weights).sum() / weights.sum())))
    return out


def levels(path: Path) -> dict:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    rgb = image[:, :, ::-1].astype(np.float32)
    y = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
    dark = (y <= 8).astype(np.uint8)
    count, _, stats, _ = cv2.connectedComponentsWithStats(dark, connectivity=8)
    biggest = int(stats[1:, cv2.CC_STAT_AREA].max()) if count > 1 else 0
    small = cv2.resize(y, (480, 270), interpolation=cv2.INTER_AREA)
    mean = cv2.blur(small, (9, 9))
    sq = cv2.blur(small * small, (9, 9))
    local = np.sqrt(np.maximum(sq - mean * mean, 0))
    return {"mean": round(float(y.mean()), 2),
            "under16_pct": round(float((y < 16).mean() * 100), 2),
            "over250_pct": round(float((y >= 250).mean() * 100), 3),
            "largest_black_blob_pct": round(biggest / y.size * 100, 2),
            "local_std_median": round(float(np.median(local)), 2)}


def main() -> None:
    names = sys.argv[1:] or SCENES
    ref = gray(IMAGES / REFERENCE)
    ref_edges = edges(ref)
    ref_lanterns = lantern_centres(ref, LANTERNS)
    report = {"reference": REFERENCE,
              "reference_lanterns": [[round(x, 1), round(y, 1)] for x, y in ref_lanterns],
              "scenes": {}}
    for name in names:
        path = IMAGES / name
        if not path.exists():
            report["scenes"][name] = "なし"
            continue
        g = gray(path)
        e = edges(g)
        row = {"global_shift": shift(ref_edges, e), "windows": {}, "lanterns": []}
        for label, (x, y, w, h) in WINDOWS.items():
            row["windows"][label] = shift(ref_edges[y:y + h, x:x + w], e[y:y + h, x:x + w])
        for (rx, ry), (sx, sy) in zip(ref_lanterns, lantern_centres(g, LANTERNS)):
            row["lanterns"].append(round(float(np.hypot(sx - rx, sy - ry)), 1))
        row["levels"] = levels(path)
        row["md5"] = __import__("hashlib").md5(path.read_bytes()).hexdigest()
        report["scenes"][name] = row
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    (HERE / "検品").mkdir(exist_ok=True)
    (HERE / "検品" / "登録ずれ.json").write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
