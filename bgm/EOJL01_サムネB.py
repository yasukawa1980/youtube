"""EOJL01 サムネB案：A案（`bgmkit thumb eojl01`）に、バッハ・ショパン・シューベルトの丸窓を足す。

★肖像は Wikimedia Commons のパブリックドメインの絵（AIで描かせていない＝合成の申告は不要）。
  バッハ：Elias Gottlob Haussmann 1748 ／ ショパン：Ary Scheffer 1847（Dordrechts Museum）／
  シューベルト：Wilhelm August Rieder 1875。 960px版を `EOJL01_素材_8時間/肖像/` に置いた。
★置き場所は題字の下の暗い幹（x 96〜、y 600〜）。 暗い地のほうが顔が立ち、右の空と梅を隠さない。
★新版画の地になじませるため、彩度を落として少し温める（顔の判別は落とさない程度）。
★3人までにした。 168px（関連動画欄）では1人あたり約22pxで、4人以上は点になる。

使い方：/usr/bin/python3 bgm/EOJL01_サムネB.py（-I を付けるとユーザー領域の Pillow が読めない）
"""
import os

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

D = "/Volumes/ESD-02/BGM/5_Echoes of Old Japan/EOJL01_素材_8時間"
A = os.path.join(D, "eojl01_サムネA_16x9.png")
OUT = os.path.join(D, "eojl01_サムネB_16x9.png")

# (ファイル, 顔の中心x, 中心y, 半径) —— 960px幅の原画での座標
FACES = [
    ("bach.jpg", 436, 290, 220),
    ("chopin.jpg", 481, 410, 235),
    ("schubert.jpg", 470, 285, 165),
]
DIAM, GAP, X0, Y0 = 250, 26, 96, 640
GOLD = (247, 216, 143)
RING = 5


def medallion(name, cx, cy, r):
    im = Image.open(os.path.join(D, "肖像", name)).convert("RGB")
    im = im.crop((cx - r, cy - r, cx + r, cy + r)).resize((DIAM, DIAM), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.75)
    warm = Image.new("RGB", im.size, (120, 90, 50))
    im = Image.blend(im, warm, 0.08)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    return im


def main():
    base = Image.open(A).convert("RGB")
    # 丸窓の下に薄い影を落として幹から浮かせる
    shadow = Image.new("L", base.size, 0)
    sd = ImageDraw.Draw(shadow)
    mask = Image.new("L", (DIAM, DIAM), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, DIAM - 1, DIAM - 1), fill=255)
    mask = mask.resize((DIAM * 4, DIAM * 4)).filter(ImageFilter.GaussianBlur(2)).resize((DIAM, DIAM), Image.LANCZOS)
    for i in range(len(FACES)):
        x = X0 + i * (DIAM + GAP)
        sd.ellipse((x - 6, Y0 + 4, x + DIAM + 6, Y0 + DIAM + 14), fill=150)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    base = Image.composite(Image.new("RGB", base.size, (0, 0, 0)), base, shadow)

    d = ImageDraw.Draw(base)
    for i, (name, cx, cy, r) in enumerate(FACES):
        x = X0 + i * (DIAM + GAP)
        base.paste(medallion(name, cx, cy, r), (x, Y0), mask)
        d.ellipse((x - RING // 2, Y0 - RING // 2, x + DIAM + RING // 2, Y0 + DIAM + RING // 2),
                  outline=GOLD, width=RING)
    base.save(OUT)
    print("書き出し:", OUT, base.size)


if __name__ == "__main__":
    main()
