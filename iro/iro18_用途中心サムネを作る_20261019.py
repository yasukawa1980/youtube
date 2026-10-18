"""IRO18 のサムネを、10/18 に全巻へ入れた「用途中心」の形で組む（本編16:9・ショート9:16）。

形（IRO01〜17 と同じ順）：最大の白い用途 → 淡い黄の場面 → 白のジャンル｜尺 → 小さな作品名。
字の後ろだけ暗くする。絵は手直し後の開始画像（編む女性＋犬1.4倍）。
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = Path('/Volumes/ESD-02/BGM/IRO/Chill/18_毛糸の季節がやってきた/手直し_20261018/18_start_編む手元_犬1.4倍.png')
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / '_work/用途中心サムネ'
F = '/System/Library/Fonts/'
HEAVY, BOLD, MID, MIN = F + 'ヒラギノ角ゴシック W9.ttc', F + 'ヒラギノ角ゴシック W8.ttc', F + 'ヒラギノ角ゴシック W6.ttc', F + 'ヒラギノ明朝 ProN.ttc'
WHITE, YELLOW = (255, 255, 255), (255, 244, 168)

LINES = [  # 文字・書体・大きさ（高さ720基準）・色・次の行までの間
    ('編み物BGM', HEAVY, 118, WHITE, 18),
    ('秋冬の手しごとに', BOLD, 64, YELLOW, 34),
    ('アコースティック・チル', MID, 40, WHITE, 8),
    ('｜2時間', MID, 40, WHITE, 30),
    ('毛糸の季節が、やってきた。', MIN, 30, WHITE, 0),
]


def shade(size, box, strength):
    """字の箱のまわりだけを暗くする（縁はぼかす）。"""
    m = Image.new('L', size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, 40, fill=strength)
    return m.filter(ImageFilter.GaussianBlur(45))


def draw_lines(img, lines, x, y, scale, center=False):
    d = ImageDraw.Draw(img)
    boxes = []
    for text, font, px, col, gap in lines:
        f = ImageFont.truetype(font, round(px * scale))
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        xx = (img.width - (r - l)) // 2 - l if center else x - l
        for off in (4, 3):  # 柔らかい影
            d.text((xx + off * scale / 2, y - t + off * scale / 2), text, font=f, fill=(20, 8, 14))
        d.text((xx, y - t), text, font=f, fill=col)
        boxes.append((xx, y, xx + r - l, y + b - t))
        y += (b - t) + round(gap * scale)
    return boxes


def compose(base, lines, x, y, scale, center=False, strength=150):
    trial = Image.new('RGB', base.size)
    boxes = draw_lines(trial, lines, x, y, scale, center)
    x0 = min(b[0] for b in boxes) - 40 * scale; y0 = min(b[1] for b in boxes) - 30 * scale
    x1 = max(b[2] for b in boxes) + 40 * scale; y1 = max(b[3] for b in boxes) + 30 * scale
    dark = Image.new('RGB', base.size, (30, 10, 20))
    out = Image.composite(dark, base, shade(base.size, (x0, y0, x1, y1), strength))
    draw_lines(out, lines, x, y, scale, center)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert('RGB')
    # 本編 1280×720：字は左上、犬（左下）と女性（右）にかけない
    main_img = compose(src.resize((1280, 720), Image.LANCZOS), LINES, 52, 62, 1.0)
    main_img.save(OUT / 'iro18_サムネ.png')
    main_img.save(OUT / 'iro18_サムネ.jpg', quality=92)
    main_img.resize((168, 95), Image.LANCZOS).resize((336, 190), Image.NEAREST).save(OUT / 'iro18_サムネ_168px.png')
    # ショート 720×1280：編む女性を中心にした縦の切り抜き（幅608では犬までは入らない）
    crop = src.crop((900, 0, 1508, 1080)).resize((720, 1280), Image.LANCZOS)
    short_lines = [('編み物BGM', HEAVY, 118, WHITE, 14), ('秋冬の手しごとに', BOLD, 62, YELLOW, 22),
                   ('音楽のショート試聴', MID, 40, WHITE, 0)]
    short = compose(crop, short_lines, 0, 70, 1.0, center=True, strength=140)
    short = compose(short, [('毛糸の季節が、やってきた。', MIN, 32, WHITE, 0)], 0, 1170, 1.0, center=True, strength=120)
    short.save(OUT / 'iro18_ショート_サムネ.png')
    short.save(OUT / 'iro18_ショート_サムネ.jpg', quality=92)
    for p in sorted(OUT.glob('*.jpg')):
        print(p.name, Image.open(p).size, p.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
