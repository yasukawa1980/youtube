"""IRO25 のサムネ（iro25_用途中心サムネを作る.py を写した・Claude 2026-11-21）。「用途中心」の形で組む（本編16:9・ショート9:16）。

形：最大の白い用途 → 淡い黄の場面 → 白のジャンル｜尺 → 小さな作品名。
絵は S4（夕暮れ：ランプの灯り、こたつで参考書を読みながら犬の頭に手をのせる女性、左の窓に雪の屋根）。
字は左上の窓（群青の空と雪の屋根）に置き、女性の顔（x≈690〜870）と犬にかけない。
★字の後ろの暗がりは行ごとに付ける（全体の箱だと左下の女性の頭まで暗くなる）。
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = Path('/Volumes/ESD-02/IRO/IRO25_素材_冬のポモドーロ3時間/_映像作業/S4.png')
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/Users/ryo/Desktop/BGM/IRO/Study/25_雪が積もるまで集中する/_work/用途中心サムネ')
F = '/System/Library/Fonts/'
HEAVY, BOLD, MID, MIN = F + 'ヒラギノ角ゴシック W9.ttc', F + 'ヒラギノ角ゴシック W8.ttc', F + 'ヒラギノ角ゴシック W6.ttc', F + 'ヒラギノ明朝 ProN.ttc'
WHITE, YELLOW = (255, 255, 255), (255, 244, 168)

LINES = [  # 文字・書体・大きさ（高さ720基準）・色・次の行までの間
    ('ポモドーロ', HEAVY, 100, WHITE, 16),
    ('冬の勉強に、3時間', BOLD, 50, YELLOW, 28),
    ('Lo-fi・25分×6｜3時間', MID, 38, WHITE, 24),
    ('雪が積もるまで、集中する。', MIN, 28, WHITE, 0),
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
    # 本編 1280×720：字は左上の窓、女性（中央右）と犬（左下）にかけない
    main_img = compose(src.resize((1280, 720), Image.LANCZOS), LINES, 44, 40, 1.0)
    main_img.save(OUT / 'iro25_サムネ.png')
    main_img.save(OUT / 'iro25_サムネ.jpg', quality=92)
    main_img.resize((168, 95), Image.LANCZOS).resize((336, 190), Image.NEAREST).save(OUT / 'iro25_サムネ_168px.png')
    # ショート 720×1280：ランプの灯りで読む女性と犬に触れる手が入る縦の切り抜き
    crop = src.crop((900, 0, 1508, 1080)).resize((720, 1280), Image.LANCZOS)
    short_lines = [('ポモドーロ', HEAVY, 88, WHITE, 12), ('冬の勉強に、3時間', BOLD, 44, YELLOW, 0)]
    short = compose(crop, short_lines, 0, 44, 1.0, center=True, strength=140)
    short = compose(short, [('雪が積もるまで、集中する。', MIN, 32, WHITE, 0)], 0, 1170, 1.0, center=True, strength=120)
    short.save(OUT / 'iro25_ショート_サムネ.png')
    short.save(OUT / 'iro25_ショート_サムネ.jpg', quality=92)
    for p in sorted(OUT.glob('*.jpg')):
        print(p.name, Image.open(p).size, p.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
