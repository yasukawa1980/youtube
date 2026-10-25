"""最終ファイルの4秒コマと土台の顔を一枚にまとめる。"""
from pathlib import Path
from io import BytesIO
import json
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / 'iro/volumes/iro20.yaml').read_text())
BASE = Path(CFG['dir'])
OUT = BASE / '投稿用'
FONT = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'


def frame(path, seconds):
    data = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', str(seconds), '-threads', '2',
        '-i', str(path), '-frames:v', '1', '-f', 'image2pipe', '-vcodec', 'png', '-threads', '2', '-'])
    return Image.open(BytesIO(data)).convert('RGB')


def main():
    dest = ROOT / 'iro/iro20_検品/Claude検品用_見本.jpg'
    old = ROOT / 'iro/_work/iro20/Claude見本_旧サムネ案.jpg'
    if dest.exists() and not old.exists():
        shutil.copy2(dest, old)
    canvas = Image.new('RGB', (1280, 1900), '#18151d')
    draw = ImageDraw.Draw(canvas)
    def label(x, y, text, size=22):
        draw.text((x, y), text, font=ImageFont.truetype(FONT, size), fill='white')
    def paste(image, x, y, size):
        image = image.copy(); image.thumbnail(size); canvas.paste(image, (x, y))
    label(14, 8, 'IRO20 / 開始画像・サムネ・完成ショート・女性の顔')
    paste(Image.open(BASE / '開始画像/iro20_start_v03.png'), 0, 44, (640, 360))
    paste(Image.open(OUT / 'iro20_サムネ.jpg'), 640, 44, (640, 360))
    label(10, 410, '168pxサムネを2倍表示')
    thumb = Image.open(OUT / 'iro20_サムネ.jpg').resize((168, 95), Image.Resampling.LANCZOS)
    canvas.paste(thumb.resize((336, 190)), (0, 446))
    label(360, 410, 'あくびの山 / ショートC 2.3秒')
    paste(frame(OUT / 'iro20_ショート_C.mp4', 2.3).crop((100, 700, 1040, 1300)), 360, 446, (360, 220))
    label(754, 410, '本編・終端カード')
    paste(Image.open(BASE / '_work/映像_v01/エンドカード.png'), 754, 446, (520, 220))
    label(10, 674, '完成ショート A / B / C / D：各4.000秒')
    for i, tag in enumerate('ABCD'):
        paste(frame(Path(CFG['shorts']['files'][tag]), 4), i * 320, 710, (320, 569))
    for row, tag in enumerate(['B1', 'B2']):
        y = 1292 + row * 290
        label(10, y, f'{tag} 女性の顔：0〜7.667秒 / 3fps / 頭の時間は未変更', 19)
        part = BASE / f'_work/映像_v01/parts/{tag}.mp4'
        for i in range(24):
            face = frame(part, i / 3).crop((970, 270, 1195, 495)).resize((104, 104))
            x = (i % 12) * 106; yy = y + 32 + (i // 12) * 124
            canvas.paste(face, (x, yy))
            label(x + 3, yy + 105, f'{i/3:.2f}s', 12)
    label(12, 1873, '映像の見本。音声の直接聴取は未実施。', 17)
    canvas.save(dest, quality=88, optimize=True)
    print(dest, dest.stat().st_size, flush=True)


if __name__ == '__main__':
    main()
