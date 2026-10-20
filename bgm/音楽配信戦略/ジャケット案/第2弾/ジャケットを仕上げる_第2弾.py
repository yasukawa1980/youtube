# 第2弾：生成画像（1254px）に文字を載せ、3000×3000 JPG に仕上げる（初回の ../ジャケットを仕上げる.py と同じ書体・色）。
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
SRC, OUT = HERE / "生成", HERE / "仕上げ"
OUT.mkdir(exist_ok=True)
MIN = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
G6 = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
G3 = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
S = 3000


def base(name):
    im = Image.open(SRC / f"{name}.png").convert("RGB").resize((S, S), Image.LANCZOS)
    return im.filter(ImageFilter.UnsharpMask(radius=2, percent=40, threshold=2)).convert("RGBA")


def track(d, xy, text, font, fill, sp):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += d.textlength(ch, font=font) + sp
    return x - sp


def whispers(name):
    im = base(name)
    d = ImageDraw.Draw(im)
    gold, cream = (232, 200, 120), (252, 249, 243)
    # 月が上部（y≈330〜430）にあるので、文字の塊は月の下に置く
    x = track(d, (220, 500), "WHISPERS OF JAPAN", ImageFont.truetype(MIN, 88), gold, 28)
    d.line([(220, 635), (x, 635)], fill=gold, width=6)
    d.text((200, 690), "Falling Leaves at Night", font=ImageFont.truetype(MIN, 215), fill=cream)
    track(d, (224, 985), "落葉の夜", ImageFont.truetype(MIN, 128), cream, 20)
    return im


def iro(name):
    im = base(name)
    d = ImageDraw.Draw(im)
    white = (255, 255, 255)
    track(d, (200, 220), "IRO SOUNDS", ImageFont.truetype(G6, 80), white, 20)
    f = ImageFont.truetype(G6, 205)
    d.text((184, 360), "今日はもう、", font=f, fill=white)
    d.text((184, 610), "ゆるくていい。", font=f, fill=white)
    track(d, (200, 900), "Take It Easy Today", ImageFont.truetype(G3, 96), white, 4)
    return im


if __name__ == "__main__":
    for i in (1, 2, 3):
        whispers(f"Whispers2_{i}").convert("RGB").save(OUT / f"Whispers2_{i}_3000.jpg", quality=95)
        iro(f"IRO2_{i}").convert("RGB").save(OUT / f"IRO2_{i}_3000.jpg", quality=95)
    # 比較：各案の大・160px・60px
    tiles = []
    for n in [f"Whispers2_{i}" for i in (1, 2, 3)] + [f"IRO2_{i}" for i in (1, 2, 3)]:
        im = Image.open(OUT / f"{n}_3000.jpg")
        t = Image.new("RGB", (700, 500), (40, 40, 40))
        t.paste(im.resize((480, 480)), (10, 10)); t.paste(im.resize((160, 160)), (500, 10)); t.paste(im.resize((60, 60)), (500, 190))
        ImageDraw.Draw(t).text((500, 270), n, fill=(255, 140, 140), font=ImageFont.truetype(G3, 20))
        tiles.append(t)
    sheet = Image.new("RGB", (2100, 1000), (40, 40, 40))
    for k, t in enumerate(tiles):
        sheet.paste(t, ((k % 3) * 700, (k // 3) * 500))
    sheet.save(OUT / "_6案の比較.jpg", quality=90)
    print("ok")
