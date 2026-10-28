"""IRO23 のサムネを（IRO22 の 用途中心サムネを作る.py を写した）、10/18 に全巻へ入れた「用途中心」の形で組む（本編16:9・ショート9:16）。

形（IRO01〜17 と同じ順）：最大の白い用途 → 淡い黄の場面 → 白のジャンル｜尺 → 小さな作品名。
字の後ろだけ暗くする。絵は S2（雨が強まる：右にマグを両手で持つ女性、足元に眠る犬、左の窓に雨の町）。
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = Path('/Volumes/ESD-02/IRO/IRO23_素材_雨やどりのカフェ2時間/_映像作業/S2.png')
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/Users/ryo/Desktop/BGM/IRO/Cafe/23_雨やどりのつもりだった/_work/用途中心サムネ')
F = '/System/Library/Fonts/'
HEAVY, BOLD, MID, MIN = F + 'ヒラギノ角ゴシック W9.ttc', F + 'ヒラギノ角ゴシック W8.ttc', F + 'ヒラギノ角ゴシック W6.ttc', F + 'ヒラギノ明朝 ProN.ttc'
WHITE, YELLOW = (255, 255, 255), (255, 244, 168)

LINES = [  # 文字・書体・大きさ（高さ720基準）・色・次の行までの間
    ('カフェBGM', HEAVY, 104, WHITE, 16),
    ('雨の午後から、夜まで', BOLD, 54, YELLOW, 30),
    ('Jazz・Lo-fi｜2時間', MID, 40, WHITE, 26),
    ('雨やどりの、つもりだった。', MIN, 30, WHITE, 0),
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
    # 本編 1280×720：字は左上、窓の雨空に置き、女性（右）と犬（下）にかけない
    # 右を切って少し寄せ、女性を右へ逃がす（顔が x≈770 になる）
    main_img = compose(src.crop((0, 0, 1792, 1008)).resize((1280, 720), Image.LANCZOS), LINES, 52, 62, 1.0)
    main_img.save(OUT / 'iro23_サムネ.png')
    main_img.save(OUT / 'iro23_サムネ.jpg', quality=92)
    main_img.resize((168, 95), Image.LANCZOS).resize((336, 190), Image.NEAREST).save(OUT / 'iro23_サムネ_168px.png')
    # ショート 720×1280：マグを持つ女性と足元の犬の頭が入る縦の切り抜き
    crop = src.crop((800, 0, 1408, 1080)).resize((720, 1280), Image.LANCZOS)
    # 顔（y≈250〜390）にかけないよう、字は上の壁と窓の中だけに収める（3行目は入れない）
    short_lines = [('カフェBGM', HEAVY, 92, WHITE, 12), ('雨の午後から夜まで', BOLD, 46, YELLOW, 0)]
    short = compose(crop, short_lines, 0, 44, 1.0, center=True, strength=140)
    short = compose(short, [('雨やどりの、つもりだった。', MIN, 32, WHITE, 0)], 0, 1170, 1.0, center=True, strength=120)
    short.save(OUT / 'iro23_ショート_サムネ.png')
    short.save(OUT / 'iro23_ショート_サムネ.jpg', quality=92)
    for p in sorted(OUT.glob('*.jpg')):
        print(p.name, Image.open(p).size, p.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
