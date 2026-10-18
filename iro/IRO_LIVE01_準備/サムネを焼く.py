"""IRO LIVE01 のサムネ：IRO12 のサムネ（画面とサムネを作る.py thumb）に「8時間ライブ」を足す。

IRO12 との違い：
- 「SKY | Study」の札の右に、赤い「● 8時間ライブ」の札
- 黄色の行「ポモドーロ 2時間」→「ポモドーロ 8時間」、下の行「25分 × 4」→「25分 × 16」
"""
import os, importlib.util
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("iro12", os.path.join(HERE, "../IRO12_よく晴れた日に集中する/画面とサムネを作る.py"))
m = importlib.util.module_from_spec(s); s.loader.exec_module(m)


def live_badge(d, lay, x, cy, txt, size=34):
    f = ImageFont.truetype(m.JP, size)
    tw = d.textlength(txt, font=f); h = int(size * 1.7); r = int(size * 0.28)
    w = int(tw + 58 + r * 2 + 14)
    d.rounded_rectangle((x, cy, x + w, cy + h), h // 2, fill=(228, 38, 50, 255))
    cx0 = x + 29 + r; cy0 = cy + h / 2
    d.ellipse((cx0 - r, cy0 - r, cx0 + r, cy0 + r), fill=(255, 255, 255, 255))
    d.text((cx0 + r + 14, cy0), txt, font=f, fill=(255, 255, 255, 255), anchor="lm")


def main():
    st = cv2.resize(m.still(), (1280, 720), interpolation=cv2.INTER_AREA).astype(np.float32)
    g = np.clip((np.arange(1280) / 1280 - 0.05) / 0.55, 0, 1)
    st *= (0.62 + 0.38 * g ** 1.5)[None, :, None]
    im = Image.fromarray(st.clip(0, 255).astype(np.uint8)).convert("RGBA")
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); X = 64
    m.chip(d, lay, X, 96, m.CHIP)
    cw = int(d.textlength(m.CHIP, font=ImageFont.truetype(m.AV, 34, index=2)) + 58)
    live_badge(d, lay, X + cw + 16, 96, "8時間ライブ")
    tf = ImageFont.truetype(m.JP, 84); y = 182
    for line in ("よく晴れた日に、", "集中する。"):
        d.text((X - 4, y), line, font=tf, fill=(255, 255, 255, 255)); y += 104
    d.text((X - 2, y + 18), "ポモドーロ 8時間", font=ImageFont.truetype(m.JP, 60), fill=(255, 238, 160, 255))
    d.text((X, y + 96), "25分 × 16・タイマー付き", font=ImageFont.truetype(m.JP_M, 36), fill=(232, 244, 255, 250))
    out = m.shadowed(im, lay).convert("RGB")
    p = os.path.join(HERE, "live01_サムネ.png"); out.save(p, optimize=True)
    out.resize((168, 94), Image.LANCZOS).save(os.path.join(HERE, "live01_サムネ_168px.png"))
    print(p, os.path.getsize(p) // 1024, "KB")


main()
