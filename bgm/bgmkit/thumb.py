"""サムネイル生成。旧 make_thumbnail_vol*.py。

設計の根拠（Vol.3で検証）:
  - 実表示は スマホのフィード=360px / PCの関連動画欄=168px。
    168pxで読めない文字は無いのと同じ。作品名を最大にする。
  - 金色の細い文字は縮小すると背景に溶ける。尺は「金地に濃紺の文字」のバッジで反転させる。
  - 全文字に暗いハローを敷かないと、縮小時に背景と混ざって潰れる。
  - 右下はYouTubeが尺バッジを自動で重ねるので空けておく。
  - タグラインに実体と違う語（SLEEP や環境音系）を置かない。
    期待外れの離脱がそのまま平均視聴時間を下げる。
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)


def _tw(d, text, f, tr):
    return sum(d.textlength(c, font=f) + tr for c in text) - tr if text else 0


def _draw_tracked(d, xy, text, f, tr, fill):
    x, y = xy
    for c in text:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tr


def build(cfg):
    t = cfg["thumb"]
    W, H = t["size"]
    lay = dict(t["layout"])
    lay.update(cfg.get("thumb_layout", {}))      # 巻ごとに文字位置をずらす場合
    col = {k: tuple(v) for k, v in t["colors"].items()}
    fonts = t["fonts"]

    src = cfg["background"]
    out = cfg.get("thumb_out") or os.path.join(cfg["dir"], f"{cfg.slug}_サムネ_16x9.png")

    img = Image.open(src).convert("RGB")
    iw, ih = img.size
    ch = int(iw * H / W)
    top = max(0, int((ih - ch) * t["crop_y"]))
    img = img.crop((0, top, iw, top + min(ch, ih))).resize((W, H), Image.LANCZOS)

    # 左側だけを暗く落として文字を乗せる場所を作る
    s = t["scrim"]
    scrim = Image.new("L", (W, 1), 0)
    for x in range(W):
        u = min(max((x - s["start"]) / float(s["width"]), 0.0), 1.0)
        scrim.putpixel((x, 0), int(255 * (s["opacity"] * (1 - u) ** s["gamma"])))
    img = Image.composite(Image.new("RGB", (W, H), tuple(s["color"])), img,
                          scrim.resize((W, H)))

    d = ImageDraw.Draw(img)
    X = lay["x"]

    # .ttc は1ファイルに複数のウェイトが入っている。役割ごとに使う番号が違うので
    # まとめて指定しない（Optima の 1 と 4 を取り違えると尺バッジとタグラインだけ字面が変わる）。
    idx = t["font_index"]

    def f_of(role, family):
        return _font(fonts[family], t["sizes"][role], idx[role])

    f_brand = f_of("brand", "serif")
    f_title = f_of("title", "serif")
    f_pill = f_of("pill", "sans")
    f_vol = f_of("vol", "sans")
    f_use = f_of("tagline", "sans")

    brand = cfg["brand"]
    t1, t2 = cfg["title_lines"]
    volume = cfg.get("volume_label") or f"VOL. {cfg['volume']}"
    runtime = cfg["runtime"]
    tagline = t["tagline"]

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for text, f, tr, y in [(brand, f_brand, 16, lay["brand"]),
                           (t1, f_title, 4, lay["t1"]),
                           (t2, f_title, 4, lay["t2"]),
                           (tagline, f_use, 5, lay["use"])]:
        _draw_tracked(gd, (X, y), text, f, tr, (0, 0, 0, 225))
    img = Image.alpha_composite(img.convert("RGBA"),
                                glow.filter(ImageFilter.GaussianBlur(16))).convert("RGB")
    d = ImageDraw.Draw(img)

    _draw_tracked(d, (X, lay["brand"]), brand, f_brand, 16, col["gold"])
    d.line([(X, lay["brand"] + 76), (X + _tw(d, brand, f_brand, 16), lay["brand"] + 84)],
           fill=col["gold"], width=3)

    _draw_tracked(d, (X, lay["t1"]), t1, f_title, 4, col["cream"])
    _draw_tracked(d, (X, lay["t2"]), t2, f_title, 4, col["cream"])
    d.line([(X, lay["t2"] + 157), (X + _tw(d, t2, f_title, 4), lay["t2"] + 168)],
           fill=col["gold"], width=3)

    pw = _tw(d, runtime, f_pill, 6) + 64
    d.rounded_rectangle([X, lay["row"], X + pw, lay["row"] + 92], radius=12, fill=col["gold"])
    _draw_tracked(d, (X + 32, lay["row"] + 14), runtime, f_pill, 6, col["navy"])
    _draw_tracked(d, (X + pw + 40, lay["row"] + 18), volume, f_vol, 8, col["gold"])

    _draw_tracked(d, (X, lay["use"]), tagline, f_use, 5, col["cream"])

    img.save(out)
    print(f"書き出し: {out} {img.size}")
    return out


def check_runtime(cfg):
    """サムネの尺表記が本編の実尺と合っているかを確かめる。"""
    import re

    from .ffutil import load_json
    man = load_json(cfg.wpath("manifest.json"))
    real = int(round(man["total"] / 60))
    m = re.search(r"(\d+)", cfg["runtime"])
    if m and int(m.group(1)) != real:
        print(f"⚠ サムネの尺 '{cfg['runtime']}' が実尺 {real} 分と違います。"
              f"volumes の runtime を直してください。")
        return False
    return True
