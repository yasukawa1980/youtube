"""IRO24 のサムネ（IRO23 の 用途中心サムネを作る.py を写した）。「用途中心」の形で組む（本編16:9・ショート9:16）。

形：最大の白い用途 → 淡い黄の場面 → 白のジャンル｜尺 → 小さな作品名。
絵は S4（夜：灯りのついたツリー、ソファにもたれて読む女性、寄りそって眠る犬、右の窓に雪の町）。
★字の後ろの暗がりは行ごとに付ける（全体の箱だと左下の女性の頭まで暗くなる）。
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = Path('/Volumes/ESD-02/IRO/IRO24_素材_クリスマス3時間/_映像作業/S4.png')
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/Users/ryo/Desktop/BGM/IRO/Seasonal/24_今年もツリーを出した/_work/用途中心サムネ')
F = '/System/Library/Fonts/'
HEAVY, BOLD, MID, MIN = F + 'ヒラギノ角ゴシック W9.ttc', F + 'ヒラギノ角ゴシック W8.ttc', F + 'ヒラギノ角ゴシック W6.ttc', F + 'ヒラギノ明朝 ProN.ttc'
WHITE, YELLOW = (255, 255, 255), (255, 244, 168)

LINES = [  # 文字・書体・大きさ（高さ720基準）・色・次の行までの間
    ('クリスマスジャズ', HEAVY, 92, WHITE, 16),
    ('雪の夜、ツリーの灯りと', BOLD, 50, YELLOW, 28),
    ('Jazz・Piano｜3時間', MID, 38, WHITE, 24),
    ('今年も、ツリーを出した。', MIN, 28, WHITE, 0),
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
    m = Image.new('L', base.size, 0); d = ImageDraw.Draw(m)
    for bx0, by0, bx1, by1 in boxes:
        d.rounded_rectangle((bx0 - 34 * scale, by0 - 18 * scale, bx1 + 34 * scale, by1 + 18 * scale), 30, fill=strength)
    m = m.filter(ImageFilter.GaussianBlur(32))
    dark = Image.new('RGB', base.size, (12, 22, 20))
    out = Image.composite(dark, base, m)
    draw_lines(out, lines, x, y, scale, center)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    src = Image.open(SRC).convert('RGB')
    # 本編 1280×720：字は左上、窓の雨空に置き、女性（右）と犬（下）にかけない
    # 右を切って少し寄せ、女性を右へ逃がす（顔が x≈770 になる）
    main_img = compose(src.resize((1280, 720), Image.LANCZOS), LINES, 44, 40, 1.0)
    main_img.save(OUT / 'iro24_サムネ.png')
    main_img.save(OUT / 'iro24_サムネ.jpg', quality=92)
    main_img.resize((168, 95), Image.LANCZOS).resize((336, 190), Image.NEAREST).save(OUT / 'iro24_サムネ_168px.png')
    # ショート 720×1280：読む女性とツリーが入る縦の切り抜き
    crop = src.crop((560, 0, 1168, 1080)).resize((720, 1280), Image.LANCZOS)
    short_lines = [('クリスマスジャズ', HEAVY, 80, WHITE, 12), ('雪の夜、ツリーの灯りと', BOLD, 44, YELLOW, 0)]
    short = compose(crop, short_lines, 0, 44, 1.0, center=True, strength=140)
    short = compose(short, [('今年も、ツリーを出した。', MIN, 32, WHITE, 0)], 0, 1170, 1.0, center=True, strength=120)
    short.save(OUT / 'iro24_ショート_サムネ.png')
    short.save(OUT / 'iro24_ショート_サムネ.jpg', quality=92)
    for p in sorted(OUT.glob('*.jpg')):
        print(p.name, Image.open(p).size, p.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
