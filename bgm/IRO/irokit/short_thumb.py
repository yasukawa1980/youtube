"""IRO ショートの縦サムネを1本ずつ作る（Claude 2026-10-30）。

10/30 本人「直近のショートが全部同じ画面」→ 巻ごとに4本共通だった縦サムネをやめ、
そのショート自身の場面（字の入っていない元のコマ）に、最大の白い用途＋そのショートの一言（淡い黄）を置く。
チャンネルのショート一覧で同じ絵が並ばないようにする。字は顔にかからない側（top / bottom）へ。
YouTube が一覧で下の方に題と回数を重ねるので、bottom でも下端から約22%は空ける。

使い方：frame = clean_frame(動画, 秒, (x, y, 幅, 高さ)); make(frame, '読書BGM', ['先に眠った、', '読書仲間。'], 'bottom', 出力.jpg)
"""
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

F = '/System/Library/Fonts/'
HEAVY, BOLD = F + 'ヒラギノ角ゴシック W9.ttc', F + 'ヒラギノ角ゴシック W8.ttc'
WHITE, YELLOW = (255, 255, 255), (255, 244, 168)
W, H = 1080, 1920


def clean_frame(video, sec, crop):
    """動画の sec 秒のコマを crop (x, y, 幅, 高さ) で切り、1080×1920 にする。"""
    x, y, w, h = crop
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'f.png'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(sec), '-i', str(video), '-frames:v', '1',
                        '-vf', f'crop={w}:{h}:{x}:{y},scale={W}:{H}:flags=lanczos', str(p)], check=True)
        return Image.open(p).convert('RGB')


def _fit(text, font, px, limit=940):
    """横幅 limit に収まるまで字を縮める（「ドライブBGM」は156pxだと幅を超える）。"""
    while ImageFont.truetype(font, px).getlength(text) > limit:
        px -= 2
    return px


def _lines(use, phrase):
    return [(use, HEAVY, _fit(use, HEAVY, 156), WHITE, 34)] + [(t, BOLD, _fit(t, BOLD, 84), YELLOW, 18) for t in phrase]


def _draw(img, lines, y):
    d = ImageDraw.Draw(img); boxes = []
    for text, font, px, col, gap in lines:
        f = ImageFont.truetype(font, px)
        l, t, r, b = d.textbbox((0, 0), text, font=f)
        x = (W - (r - l)) // 2 - l
        for off in (6, 4):  # 柔らかい影
            d.text((x + off, y - t + off), text, font=f, fill=(20, 8, 14))
        d.text((x, y - t), text, font=f, fill=col)
        boxes.append((x, y, x + r - l, y + b - t)); y += (b - t) + gap
    return boxes, y


def make(frame, use, phrase, where, out, y=None):
    """frame（1080×1920）に用途と一言を置いて out へ JPG で保存する。y で字の上端を指定できる。"""
    lines = _lines(use, phrase)
    _, end = _draw(Image.new('RGB', (W, H)), lines, 0)
    if y is None:
        y = 150 if where == 'top' else round(H * 0.78) - end
    boxes, _ = _draw(Image.new('RGB', (W, H)), lines, y)
    x0 = min(b[0] for b in boxes) - 70; y0 = min(b[1] for b in boxes) - 50
    x1 = max(b[2] for b in boxes) + 70; y1 = max(b[3] for b in boxes) + 50
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((x0, y0, x1, y1), 60, fill=150)
    img = Image.composite(Image.new('RGB', (W, H), (30, 10, 20)), frame, m.filter(ImageFilter.GaussianBlur(60)))
    _draw(img, lines, y)
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, quality=90)
    return out
