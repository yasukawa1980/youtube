"""SOJ09本編用の4場面水域マスクとWAVE08準拠CTA画像を作る。"""

from __future__ import annotations

from pathlib import Path
import sys
import json
import hashlib

import cv2
import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
IMAGES = ROOT / "画像"
W, H = 1920, 1080


def polygon_mask(points: list[tuple[int, int]]) -> np.ndarray:
    mask = np.zeros((H, W), np.uint8)
    cv2.fillPoly(mask, [np.array(points, np.int32)], 255)
    return mask


def color_water(
    image: np.ndarray,
    corridor: np.ndarray,
    density_cut: int,
    include_bluish: bool = True,
    value_floor: int = 60,
    foam_floor: int = 132,
    blue_delta: int = 7,
) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    blue, green, red = cv2.split(image)
    _, saturation, value = cv2.split(hsv)
    foam = (value > foam_floor) & (saturation < 118)
    bluish = (value > value_floor) & (blue.astype(np.int16) > red.astype(np.int16) + blue_delta)
    selected = foam | bluish if include_bluish else foam
    candidate = (selected.astype(np.uint8) * 255)
    candidate = cv2.bitwise_and(candidate, corridor)
    density = cv2.GaussianBlur(candidate, (25, 25), 0)
    candidate[density < density_cut] = 0
    candidate = cv2.morphologyEx(
        candidate, cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 7)),
    )
    candidate = cv2.dilate(
        candidate, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
    )
    blurred = cv2.GaussianBlur(candidate, (11, 11), 0)
    # 膨張・ぼかしが陸側へ漏れないよう、水域内の距離でフェザーを制限。
    distance = cv2.distanceTransform(corridor, cv2.DIST_L2, 5)
    return np.rint(blurred * np.clip(distance / 6.0, 0, 1)).astype(np.uint8)


def subtract_ellipses(mask: np.ndarray, ellipses: list[tuple]) -> np.ndarray:
    protect = np.zeros_like(mask)
    for center, axes, angle in ellipses:
        cv2.ellipse(protect, center, axes, angle, 0, 360, 255, -1)
    soft = cv2.GaussianBlur(protect, (15, 15), 0).astype(np.float32) / 255.0
    return np.clip(mask.astype(np.float32) * (1.0 - soft), 0, 255).astype(np.uint8)


def save(name: str, image: np.ndarray, mask: np.ndarray) -> None:
    mask_path = HERE / f"{name}_水域マスク.png"
    preview_path = HERE / f"{name}_水域マスク確認.jpg"
    cv2.imwrite(str(mask_path), mask)
    cyan = np.zeros_like(image)
    cyan[:, :, 0] = 255
    cyan[:, :, 1] = 210
    alpha = (mask.astype(np.float32) / 255.0 * 0.62)[:, :, None]
    preview = np.clip(image * (1.0 - alpha) + cyan * alpha, 0, 255).astype(np.uint8)
    cv2.imwrite(str(preview_path), preview, [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(mask_path)
    print(f"  nonzero={np.count_nonzero(mask) / mask.size:.5f}, strong={np.count_nonzero(mask >= 128) / mask.size:.5f}")


# 生成プレビュー（1672×941）上で目視採点した水陸境界。
# 座標は最終1920×1080へ変換。元画像を差し替えた場合は必ず再採点する。
REFERENCE_SIZE = (1672, 941)
SCENES = [
    {
        "stem": "01_波打ち際_昼下がり", "seconds": 1130, "interval": [0, 1130],
        "corridor": [
            (943, 301), (1671, 301), (1671, 940), (1425, 940),
            (1300, 913), (1160, 874), (1064, 836), (982, 803),
            (933, 769), (900, 743), (825, 712), (799, 689),
            (757, 666), (683, 636), (685, 618), (647, 594),
            (626, 567), (592, 550), (597, 535), (554, 514),
            (556, 495), (513, 477), (496, 455), (550, 434),
            (518, 406), (445, 377), (392, 354), (280, 339),
            (370, 331), (490, 320), (620, 312), (760, 307),
        ],
        "protect": [],
        "color": {"density_cut": 35, "value_floor": 45, "foam_floor": 115, "blue_delta": 5},
    },
    {
        "stem": "02_漁村の浜_夕方", "seconds": 1125, "interval": [1115, 2240],
        "corridor": [
            (980, 342), (1671, 340), (1671, 675), (1440, 647),
            (1230, 618), (1070, 587), (915, 567), (884, 547),
            (795, 536), (793, 520), (815, 518), (824, 498),
            (850, 489), (876, 507), (895, 519), (903, 510),
            (876, 486), (807, 481), (775, 482), (706, 470),
            (672, 445), (641, 430), (605, 419), (579, 399),
            (535, 391), (602, 384), (661, 379), (740, 373),
            (856, 365), (877, 359), (956, 356),
        ],
        "protect": [
            # 女性の髪から足先まで余白付き保護。水面の背後部分も固定。
            [(958, 376), (1028, 375), (1044, 442), (1063, 462),
             (1077, 511), (1072, 616), (1061, 661), (1062, 796),
             (940, 796), (935, 650), (918, 601), (919, 501),
             (932, 462), (948, 442)],
            # 手前の岩、奥の舟の舳先。
            [(783, 487), (810, 487), (826, 525), (800, 540), (780, 522)],
            [(817, 492), (842, 480), (864, 486), (884, 502),
             (891, 520), (878, 532), (840, 533), (816, 520)],
        ],
        "color": {"density_cut": 26, "value_floor": 38, "foam_floor": 110, "blue_delta": 2},
    },
    {
        "stem": "03_宿の縁側から_薄暮", "seconds": 560, "interval": [2225, 2785],
        "corridor": [
            (540, 433), (1671, 432), (1671, 541), (1615, 542),
            (1580, 576), (1535, 602), (1480, 619), (1340, 613),
            (1170, 602), (1005, 586), (950, 575), (915, 560),
            (835, 548), (795, 542), (755, 526), (722, 511),
            (693, 497), (636, 489), (593, 473), (540, 466),
        ],
        "protect": [
            # 縁側の外に見える松と海岸の岩を保護。
            [(470, 466), (540, 465), (590, 475), (628, 480),
             (660, 501), (689, 504), (724, 517), (724, 540),
             (683, 562), (610, 550), (485, 520)],
            [(723, 548), (757, 548), (790, 581), (780, 603), (710, 590)],
            [(804, 570), (845, 559), (861, 579), (906, 579),
             (919, 602), (810, 600)],
        ],
        "color": {"density_cut": 30, "value_floor": 30, "foam_floor": 92, "blue_delta": 4},
    },
    {
        "stem": "04_月夜の海_夜", "seconds": 838, "interval": [2770, 3608],
        "corridor": [
            (748, 386), (1671, 386), (1671, 422), (1600, 423),
            (1560, 451), (1517, 474), (1525, 513), (1540, 538),
            (1495, 565), (1534, 613), (1590, 640), (1655, 640),
            (1660, 655), (1560, 668), (1500, 675), (1470, 706),
            (1430, 710), (1405, 680), (1385, 681), (1367, 711),
            (1337, 725), (1320, 737), (1288, 760), (1283, 793),
            (1180, 767), (1080, 743), (980, 720), (875, 691),
            (780, 665), (690, 638), (610, 610), (535, 585),
            (477, 563), (423, 543), (387, 528), (352, 516),
            (365, 498), (405, 488), (434, 481), (471, 478),
            (505, 475), (542, 467), (565, 461), (618, 461),
            (655, 458), (695, 453), (668, 446), (652, 436),
            (590, 438), (578, 427), (540, 424), (531, 407),
            (535, 394), (651, 391),
        ],
        "protect": [
            [(551, 437), (579, 431), (600, 445), (603, 462), (551, 464)],
            [(620, 439), (648, 439), (664, 455), (615, 462)],
            [(1360, 725), (1360, 695), (1375, 681), (1385, 658),
             (1408, 660), (1423, 685), (1430, 709), (1452, 722),
             (1470, 735), (1440, 765), (1390, 766)],
        ],
        "color": {"density_cut": 24, "value_floor": 22, "foam_floor": 85, "blue_delta": 3},
    },
]


def reference_polygon(points: list[tuple[int, int]]) -> np.ndarray:
    return polygon_mask([
        (round(x * W / REFERENCE_SIZE[0]), round(y * H / REFERENCE_SIZE[1]))
        for x, y in points
    ])


def main() -> None:
    records = []
    for scene in SCENES:
        stem = scene["stem"]
        path = IMAGES / f"{stem}.png"
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None or image.shape[:2] != (H, W):
            raise RuntimeError(f"bad image: {path}: {None if image is None else image.shape}")
        corridor = reference_polygon(scene["corridor"])
        protected = np.zeros((H, W), np.uint8)
        for points in scene["protect"]:
            protected = cv2.bitwise_or(protected, reference_polygon(points))
        corridor[protected > 0] = 0
        mask = color_water(image, corridor, **scene["color"])
        if not np.any(mask >= 128):
            raise RuntimeError(f"empty strong water mask: {stem}")
        if np.any(mask[corridor == 0]):
            raise RuntimeError(f"mask leaks outside allowed water: {stem}")
        save(stem, image, mask)
        ys, xs = np.nonzero(mask)
        records.append({
            "file": f"{stem}_水域マスク.png",
            "source_file": f"../画像/{stem}.png",
            "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size": [W, H],
            "scene_seconds": scene["seconds"], "timeline_interval": scene["interval"],
            "nonzero_area_percent": round(float(np.count_nonzero(mask) / mask.size * 100), 4),
            "strong_area_percent": round(float(np.count_nonzero(mask >= 128) / mask.size * 100), 4),
            "alpha_weighted_area_percent": round(float(mask.mean() / 255 * 100), 4),
            "bounding_box_xyxy_exclusive": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
            "pixels_outside_corridor": int(np.count_nonzero(mask[corridor == 0])),
            "pixels_on_explicit_protected_regions": int(np.count_nonzero(mask[protected > 0])),
        })

    # SOJ08 と同一の bgmkit 関数・既定値で透明CTAを作成。
    sys.path.insert(0, str(ROOT.parent))
    from bgmkit.config import CTA_TEXT
    from bgmkit.video import CTA_DEFAULT, _text_png

    class TextCfg(dict):
        images_dir = ""

    cfg = TextCfg(video={"output": [W, H]}, images=[str(IMAGES / f"{SCENES[0]['stem']}.png")])
    _text_png(cfg, 0, CTA_TEXT["video"], dict(CTA_DEFAULT), str(HERE / "_cta.png"), "登録のお願い")
    cta = cv2.imread(str(HERE / "_cta.png"), cv2.IMREAD_UNCHANGED)
    if cta is None or cta.shape != (H, W, 4) or not np.any(cta[:, :, 3]):
        raise RuntimeError("CTA must be a nonempty 1920x1080 RGBA overlay")
    report = {
        "method": "SOJ08 polygon corridor + HSV/blue/foam selection + density + close/dilate + Gaussian feather; SOJ09 clamps feather inside water corridor",
        "mask_area_definition": "strong: mask>=128; nonzero: mask>0; weighted: sum(mask/255)/(1920*1080)",
        "total_timeline_seconds": 3608,
        "crossfade_seconds": 15,
        "masks": records,
        "cta": {"file": "_cta.png", "size": [W, H], "mode": "RGBA", "text": CTA_TEXT["video"], "same_defaults_as_soj08": True},
        "checks": {
            "all_masks_1920x1080_grayscale": True,
            "all_masks_nonempty": True,
            "all_masks_zero_outside_water_corridors": True,
            "all_masks_zero_on_explicit_protected_regions": True,
            "cta_rgba_nonempty": True,
        },
        "notes": [
            "マスクは水だけを選択。境界の安全余白のため、泡の最外縁・人物の背後・松の際などの水面には固定部分が残る。",
            "マスク確認JPGの水色が可動域。静止画で検品済み。動き試作・本編書き出しは今回の作業対象外。",
            "色条件を晩秋の暗い海に合わせて調整。SOJ08の試作マスクへの依存はなく、4枚とも本スクリプトで再生成できる。",
        ],
    }
    (HERE / "素材検品結果.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(HERE / "_cta.png")


if __name__ == "__main__":
    main()
