"""narration.srt から、画面に焼く字幕の画像列（subs/）と ffmpeg の concat 一覧を作る。

ffmpeg に libass が入っていないので、1画面ずつ透明PNGにして1本の入力として重ねる。
- 位置は下中央（縁側の床の暗い帯の上）。札と登録のお願いは左上へ逃がした
- 1行30字まで・1画面2行まで。長い文は画面を分け、時間は字数で割る
- 文と文の間が1秒未満なら前の字幕を残す（ちらつかせない）
- 冒頭の題と「第一夜」などは札が出すので字幕にしない
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / 'subs'
SIZE = (1920, 1080)
FONT = ImageFont.truetype('/System/Library/Fonts/ヒラギノ明朝 ProN.ttc', 46, index=0)
INK = (238, 232, 218, 255)      # 生成り。真っ白にしない（寝る前の画面）
HALO = (6, 10, 22)
LINE_CHARS = 30
LINE_GAP = 1.55                 # 行送り（字の大きさの倍）
BOTTOM = 1018                   # 2行目の下端
HOLD_GAP = 1.0


def sec(t):
    h, m, s = t.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def wrap(text):
    """30字以内で、なるべく読点の直後で折る。"""
    lines = []
    while len(text) > LINE_CHARS:
        cut = text.rfind('、', 0, LINE_CHARS) + 1
        if cut < LINE_CHARS * 0.5:
            cut = LINE_CHARS
        lines.append(text[:cut])
        text = text[cut:]
    return lines + [text] if text else lines


def page_png(lines, path):
    img = Image.new('RGBA', SIZE, (0, 0, 0, 0))
    halo = Image.new('L', SIZE, 0)
    hd, d = ImageDraw.Draw(halo), ImageDraw.Draw(img)
    step = FONT.size * LINE_GAP
    top = BOTTOM - FONT.size - step * (len(lines) - 1)
    for k, line in enumerate(lines):
        w = d.textlength(line, font=FONT)
        xy = ((SIZE[0] - w) / 2, top + step * k)
        hd.text(xy, line, font=FONT, fill=235)
        d.text(xy, line, font=FONT, fill=INK)
    halo = halo.filter(ImageFilter.GaussianBlur(FONT.size * 0.18))
    base = Image.new('RGBA', SIZE, (0, 0, 0, 0))
    base.paste(Image.new('RGBA', SIZE, (*HALO, 200)), (0, 0), halo)
    Image.alpha_composite(base, img).save(path)


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob('*.png'):
        old.unlink()
    cues = []
    for block in (HERE / 'narration.srt').read_text().strip().split('\n\n'):
        _, span, text = block.split('\n', 2)
        a, b = span.split(' --> ')
        cues.append((sec(a), sec(b), text.replace('\n', '')))
    cues = [c for c in cues if not re.fullmatch(r'第.夜|夏目漱石『夢十夜』', c[2])]

    blank = OUT / 'blank.png'
    Image.new('RGBA', SIZE, (0, 0, 0, 0)).save(blank)
    pages, t = [], 0.0          # (png, 長さ)
    for n, (a, b, text) in enumerate(cues):
        if a > t:
            pages.append((blank, a - t))
        nxt = cues[n + 1][0] if n + 1 < len(cues) else b + 3.0
        end = nxt if nxt - b < HOLD_GAP else b + 0.3
        lines = wrap(text)
        chunks = [lines[k:k + 2] for k in range(0, len(lines), 2)]
        total = sum(len(''.join(c)) for c in chunks)
        start = a
        for j, chunk in enumerate(chunks):
            stop = end if j == len(chunks) - 1 else start + (b - a) * len(''.join(chunk)) / total
            path = OUT / f'{n:04d}_{j}.png'
            page_png(chunk, path)
            pages.append((path, stop - start))
            start = stop
        t = end
    pages.append((blank, 1.0))
    # concat demuxer：最後の画像は duration が効かないので、もう一度書く
    body = ''.join(f"file '{p}'\nduration {d:.3f}\n" for p, d in pages) + f"file '{blank}'\n"
    (HERE / 'subs.txt').write_text(body)
    print(f'字幕の画面 {sum(p != blank for p, _ in pages)}・合計 {sum(d for _, d in pages) / 60:.1f}分')


if __name__ == '__main__':
    main()
