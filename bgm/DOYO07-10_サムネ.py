#!/usr/bin/env python3
"""DOYO07–10（童謡単曲 第2弾）のサムネ。文字のない絵に、第1弾と同じ型の文字を後から重ねる。

python3 bgm/DOYO07-10_サムネ.py --out <確認用フォルダ>   # 試し焼き
python3 bgm/DOYO07-10_サムネ.py                          # yaml の artifacts へ書く（既存があれば止まる）

第1弾（DOYO03-06_サムネ手直し.md）の型：上に帯「和楽器で聴く童謡」と金の罫、白い明朝の題字、
下に金の罫と WHISPERS OF JAPAN（Cochin Bold・1920幅換算38px／字間8px・1672原本で(72,758)）。
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / 'サムネ確認用' / '童謡単曲'
GOLD = (247, 216, 143)
WHITE = (250, 248, 242)
COCHIN = '/System/Library/Fonts/Supplemental/Cochin.ttc'
MINCHO = '/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
# 題字の改行。1行の字数は左の暗がり（1280幅で x≈510 まで）に収まる数にする。
# shift：帯と上の罫を下げる量（月に重ならないように）。moon：暗がりをかけない月の中心と半径（実測）。
SPECS = [
    ('doyo07', ['虫の', 'こえ'], 0, None),
    ('doyo08', ['十五夜', 'お月さん'], 70, (536, 166, 48)),
    ('doyo09', ['月の', '沙漠'], 0, None),
    ('doyo10', ['浜千鳥'], 130, (552, 246, 45)),
]
X0 = 72            # 左端（1672原本の座標）
TEXT_RIGHT = 660   # 題字の右端の上限（1280幅で約505px）


def tracked(draw, xy, text, font, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill, anchor='ls')
        x += draw.textlength(ch, font=font) + spacing
    return x - spacing


def width(draw, text, font, spacing=0):
    return sum(draw.textlength(c, font=font) for c in text) + spacing * (len(text) - 1)


def compose(visual, lines, shift=0, moon=None):
    base = Image.open(visual).convert('RGB')
    if base.size != (1672, 941):
        raise ValueError(f'座標の再確認が必要: {visual}, {base.size}')
    W, H = base.size
    # 左の暗がり：左端で濃く、x≈900で消える。絵の明るさに合わせて濃さを決める。
    arr = np.asarray(base).astype(np.float32)
    lum = (arr[:, :700] @ [0.299, 0.587, 0.114]).mean()
    peak = float(np.clip(0.72 + (lum - 60) / 250, 0.72, 0.88))
    x = np.linspace(0, 1, W)
    ramp = np.tile(np.clip(1 - x / 0.6, 0, 1) ** 1.1 * peak, (H, 1))
    if moon:
        mx, my, r = moon
        yy, xx = np.mgrid[0:H, 0:W]
        dist = np.hypot(xx - mx, yy - my)
        ramp *= np.clip((dist - r * 1.2) / (r * 1.6), 0, 1)
    arr *= (1 - ramp)[:, :, None]
    image = Image.fromarray(arr.clip(0, 255).astype(np.uint8)).convert('RGBA')

    layer = Image.new('RGBA', image.size)
    d = ImageDraw.Draw(layer)
    band = ImageFont.truetype(MINCHO, 58, index=2)
    tracked(d, (X0, 224 + shift), '和楽器で聴く童謡', band, GOLD + (255,), 9)
    d.line([(X0, 252 + shift), (TEXT_RIGHT, 252 + shift)], fill=GOLD + (200,), width=2)

    # 題字：行数に応じて、いちばん長い行が TEXT_RIGHT に収まる最大の大きさ（上限200px）。
    size = 200
    while size > 80:
        font = ImageFont.truetype(MINCHO, size, index=2)
        if max(width(d, s, font) for s in lines) <= TEXT_RIGHT - X0:
            break
        size -= 2
    top, bottom = 290 + shift, 712
    lead = size * 1.08
    block = lead * (len(lines) - 1) + size * 0.88
    y = top + (bottom - top - block) / 2 + size * 0.88
    for s in lines:
        d.text((X0 - 6, y), s, font=font, fill=WHITE + (255,), anchor='ls')
        y += lead

    d.line([(X0, 735), (TEXT_RIGHT, 735)], fill=GOLD + (200,), width=2)
    factor = W / 1920
    brand = ImageFont.truetype(COCHIN, round(38 * factor), index=1)
    bx, by = float(X0), 758.0
    for ch in 'WHISPERS OF JAPAN':
        d.text((bx, by), ch, font=brand, fill=GOLD + (255,), anchor='lt')
        bx += d.textlength(ch, font=brand) + 8 * factor

    shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
    shadow.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(3)))
    image = Image.alpha_composite(image, shadow)
    image = Image.alpha_composite(image, shadow)
    image = Image.alpha_composite(image, layer).convert('RGB')
    return image, dict(scrim_peak=round(peak, 3), shift=shift, moon_protected=moon, title_px=size, title_lines=lines,
                       brand_right_1280=round(bx * 1280 / W, 1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, help='試し焼きの出力先（省略すると yaml の artifacts と確認用JPG）')
    p.add_argument('--overwrite', action='store_true')
    a = p.parse_args()
    rows = []
    sheet = Image.new('RGB', (168 * 2 + 12, 95 * 2 + 12), (255, 255, 255))
    for i, (slug, lines, shift, moon) in enumerate(SPECS):
        cfg = yaml.safe_load((ROOT / 'bgm' / 'volumes' / f'{slug}.yaml').read_text(encoding='utf-8'))
        art = cfg['artifacts']
        image, info = compose(cfg['songs'][0]['visual'], lines, shift, moon)
        if a.out:
            a.out.mkdir(parents=True, exist_ok=True)
            png, jpg = a.out / f'{slug}_thumbnail.png', a.out / f'{slug}_short_thumbnail.jpg'
            review = a.out / f'{slug}_サムネ.jpg'
        else:
            png, jpg = Path(art['thumbnail_original']), Path(art['thumbnail'])
            review = (ROOT / 'bgm' / 'volumes' / art['thumbnail_review']).resolve()
        for f in (png, jpg, review):
            if f.exists() and not a.overwrite:
                raise SystemExit(f'既存ファイルがあります: {f}')
        image.save(png)
        small = image.resize((1280, 720), Image.Resampling.LANCZOS)
        small.save(jpg, quality=90)
        review.parent.mkdir(parents=True, exist_ok=True)
        small.save(review, quality=90)
        if jpg.stat().st_size >= 1_000_000 or review.stat().st_size >= 1_000_000:
            raise SystemExit(f'1MBを超えた: {jpg}')
        sheet.paste(image.resize((168, 95), Image.Resampling.LANCZOS), (4 + (i % 2) * 172, 4 + (i // 2) * 99))
        rows.append(dict(slug=slug, visual=cfg['songs'][0]['visual'], png=str(png), jpeg=str(jpg),
                         review=str(review), jpeg_bytes=jpg.stat().st_size, **info))
        print(slug, info, jpg.stat().st_size, 'bytes')
    sheet_path = (a.out or REVIEW) / 'doyo07-10_168px確認.jpg'
    sheet.save(sheet_path, quality=95)
    print(json.dumps(rows, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    sys.exit(main())
