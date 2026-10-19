"""IRO LIVE02 のサムネ：IRO11 の用途中心サムネ（10/18）と同じ並びで、ライブ用に作り直す。

- 絵：IRO11 の開始画像（CORAL の色寄せ）＝画面とサムネを作る.py の still()
- 字：「ローファイ」（白・最大）／「夜の作業用BGM」（黄）／「8時間ライブ・歌なし」（白）／作品名（小）
- 左上に赤い「● LIVE」の札
"""
import os, importlib.util
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("iro11", os.path.join(HERE, "../IRO11_もう少しだけ起きていよう/画面とサムネを作る.py"))
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
JP_B = "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc"


def live_badge(d, x, y, txt="LIVE", size=40):
    f = ImageFont.truetype(m.AV, size, index=2)
    tw = d.textlength(txt, font=f); h = int(size * 1.6); r = int(size * 0.26)
    w = int(tw + 40 + r * 2 + 14)
    d.rounded_rectangle((x, y, x + w, y + h), 10, fill=(228, 38, 50, 255))
    cx0 = x + 22 + r; cy0 = y + h / 2
    d.ellipse((cx0 - r, cy0 - r, cx0 + r, cy0 + r), fill=(255, 255, 255, 255))
    d.text((cx0 + r + 14, cy0), txt, font=f, fill=(255, 255, 255, 255), anchor="lm")


def main():
    st = cv2.resize(m.still(), (1280, 720), interpolation=cv2.INTER_AREA).astype(np.float32)
    g = np.clip((np.arange(1280) / 1280 - 0.05) / 0.55, 0, 1)
    st *= (0.55 + 0.45 * g ** 1.5)[None, :, None]
    im = Image.fromarray(st.clip(0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); X = 62
    live_badge(d, X, 52)
    d.text((X - 4, 128), "ローファイ", font=ImageFont.truetype(JP_B, 132), fill=(255, 255, 255, 255))
    d.text((X - 2, 296), "夜の作業用BGM", font=ImageFont.truetype(m.JP, 84), fill=(255, 238, 140, 255))
    d.text((X, 410), "8時間ライブ・歌なし", font=ImageFont.truetype(m.JP, 58), fill=(255, 255, 255, 255))
    d.text((X, 566), "もう少しだけ、起きていよう。", font=ImageFont.truetype(m.JP_M, 32), fill=(255, 255, 255, 245))
    out = m.shadowed(im, lay, k=0.75, r=8).convert("RGB")
    p = os.path.join(HERE, "live02_サムネ.png"); out.save(p, optimize=True)
    out.save(os.path.join(HERE, "live02_サムネ.jpg"), quality=90)
    out.resize((168, 94), Image.LANCZOS).save(os.path.join(HERE, "live02_サムネ_168px.png"))
    print(p, os.path.getsize(p) // 1024, "KB")


main()
