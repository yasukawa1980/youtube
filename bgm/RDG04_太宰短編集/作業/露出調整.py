"""生成直後の絵を暗くし、話の進みに合わせて平均輝度を下げる。

RDG04の絵は平均85〜131と明るく、線形倍率だけで下げると窓あかり・街灯まで鈍って雪が灰色にくすんだ（11/8）。
線形RGBにガンマ1.5を掛けてから倍率で下げる＝明るい所を残して暗部を沈める。
"""
import json
import shutil
from pathlib import Path

import numpy as np
from PIL import Image

IMG = Path(__file__).resolve().parent.parent / '画像'
BEFORE = Path('/Volumes/ESD-EPB/BGM/9_朗読/RDG04_素材_太宰短編集/画像_露出前')   # Macの空きが少ないのでSSDへ
TARGET = {'01': 55, '02': 52, '03': 50, '04': 48, '05': 46, '06': 46, '07': 46, '08': 42}
GAMMA = {'02': 1.0, '05': 1.0}   # 02・05は夜の絵として作り直し、元が平均約68と暗いので線形倍率だけ（ほかは1.5）
ONLY = set(__import__('sys').argv[1:])   # 番号を渡すとその場面だけ


def lin(a):
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def srgb(a):
    return np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(np.maximum(a, 1e-9), 1 / 2.4) - 0.055)


def luma(rgb255):
    return 0.2126 * rgb255[..., 0] + 0.7152 * rgb255[..., 1] + 0.0722 * rgb255[..., 2]


def main():
    BEFORE.mkdir(exist_ok=True)
    path = IMG / '露出調整.json'
    log = json.loads(path.read_text()) if path.exists() else {}
    for n, target in TARGET.items():
        if ONLY and n not in ONLY:
            continue
        name = f'rdg04_{n}.png'
        if not (IMG / name).exists() and not (BEFORE / name).exists():
            continue
        if not (BEFORE / name).exists():
            shutil.copy2(IMG / name, BEFORE / name)
        linear = lin(np.asarray(Image.open(BEFORE / name).convert('RGB'), dtype='float64') / 255) ** GAMMA.get(n, 1.5)
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
        log[name] = {'gamma': GAMMA.get(n, 1.5), 'linear_rgb_scale': round(k, 4), 'mean': round(float(y.mean()), 1),
                     'under16_pct': round(float((y < 16).mean() * 100), 1)}
        print(name, log[name])
    path.write_text(json.dumps(log, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
