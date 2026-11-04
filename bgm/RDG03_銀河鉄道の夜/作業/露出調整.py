"""生成直後の絵を線形RGB倍率で暗くし、話の進みに合わせて平均輝度を下げる（RDG02と同じ方法）。"""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

IMG = Path(__file__).resolve().parent.parent / '画像'
BEFORE = IMG / '露出前'
TARGET = {'01': 55, '02': 48, '03': 46, '04': 44, '05': 44, '06': 44, '07': 42, '08': 40, '09': 38, '10': 35}


def lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def srgb(a):
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.maximum(a, 1e-9), 1 / 2.4) - 0.055)


def luma(rgb255):
    return 0.2126 * rgb255[..., 0] + 0.7152 * rgb255[..., 1] + 0.0722 * rgb255[..., 2]


def main():
    BEFORE.mkdir(exist_ok=True)
    log = {}
    for n, target in TARGET.items():
        name = f'rdg03_{n}.png'
        if not (BEFORE / name).exists():
            shutil.copy2(IMG / name, BEFORE / name)
        linear = lin(np.asarray(Image.open(BEFORE / name).convert('RGB'), dtype='float64') / 255)
        lo, hi = 0.0, 1.0
        for _ in range(30):
            k = (lo + hi) / 2
            if luma(srgb(linear * k) * 255).mean() > target:
                hi = k
            else:
                lo = k
        out = np.clip(srgb(linear * k) * 255 + 0.5, 0, 255).astype('uint8')
        Image.fromarray(out).save(IMG / name)
        y = luma(out.astype('float64'))
        log[name] = {'linear_rgb_scale': round(k, 4), 'mean': round(float(y.mean()), 1),
                     'under16_pct': round(float((y < 16).mean() * 100), 1)}
        print(name, log[name])
    (IMG / '露出調整.json').write_text(json.dumps(log, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
