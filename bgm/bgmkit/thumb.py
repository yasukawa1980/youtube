"""サムネイル生成。旧 make_thumbnail_vol*.py。

設計の根拠（Vol.3で検証）:
  - 実表示は スマホのフィード=360px / PCの関連動画欄=168px。
    168pxで読めない文字は無いのと同じ。作品名を最大にする。
  - 金色の細い文字は縮小すると背景に溶ける。尺は「金地に濃紺の文字」のバッジで反転させる。
  - 全文字に暗いハローを敷かないと、縮小時に背景と混ざって潰れる。
  - 右下はYouTubeが尺バッジを自動で重ねるので空けておく。

★2026年8月12日、Vol.14から「B案」に変更（Vol.1〜13は旧レイアウトで作ってある）:
  - タグライン `RELAX · READ · FOCUS` と `VOL. n` を描かなくなった。
    168pxでは両方とも読めず、読めない要素が下段の面積を占有していた。
    デバイスはPC45.7%で流入の91.5%が「次の動画」なので、関連動画欄の168pxが主戦場。
  - 空いたぶんタイトルを 140→172 に拡大し、スクリムを 1060→880 に狭めて絵を広く残す
    （Vol.10の畳の間は暗すぎて168pxで被写体を判別できなかった）。
  - `WHISPERS OF JAPAN` と金バッジの尺は残す。前者を消すとシリーズ物に見えなくなり、
    後者は金地に濃紺で反転しているので小さくても読める。
★この変更はまだ実証されていない。 CTRは母数不足で優劣を判定できなかった
  （信頼できるのはVol.6の9,963回＝1.9%だけで、他は1〜4クリック）。
  次にどれかが伸び始めたら、その日のうちにYouTubeのサムネイルA/Bテストで確かめること。
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

    # ★★2026年8月25日、シンプル化に対応（本人の提案）。
    #   ・題字は英語2行固定ではなく **任意の行数**。日本語1行も置ける
    #   ・**尺バッジを省ける**（`thumb.pill: false`）。YouTubeが右下に尺を必ず重ねるので、
    #     自分で描くと同じ情報を二度出すことになる。上の設計メモにも
    #     「右下はYouTubeが尺バッジを自動で重ねる」と書いてある
    #   ・題字に日本語フォントを選べる（`thumb.title_family: jp`）
    #   ★既定は従来のまま。 書かなければ英語2行＋尺バッジで、公開済みの巻は1画素も変わらない。
    fam = t.get("title_family", "serif")
    f_brand = f_of("brand", "serif")

    brand = cfg["brand"]
    lines = cfg["title_lines"]
    if isinstance(lines, str):
        lines = [lines]
    tsize = t["sizes"]["title"]
    trk = (t.get("tracking") or {}).get("title", 4)

    # ★★`title_fit` を書くと、その幅に収まる最大の級数を自分で選ぶ（2026年8月25日）。
    #   日本語に切り替えたら題字の字数が3〜8字とばらつき、巻ごとに手で級数を決めるのは
    #   16本ぶんとなると現実的でない。**幅を決めて級数を機械に選ばせる**ほうが早くて確実。
    #   ★上限を切ること。 短い題字（蝉時雨＝3字）が青天井に大きくなると、
    #     同じ棚に並んだとき級数がばらついて見える。
    fit = t.get("title_fit")
    if fit:
        lo, hi = t.get("title_min", 90), tsize
        probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
        while lo < hi:
            mid = (lo + hi + 1) // 2
            f = _font(fonts[fam], mid, idx["title"])
            if max(_tw(probe, ln, f, trk) for ln in lines) <= fit:
                lo = mid
            else:
                hi = mid - 1
        tsize = lo
    f_title = _font(fonts[fam], tsize, idx["title"])
    # ★`line_gap: auto` で行間を級数に比例させる。 自動級数と組み合わせるときに要る
    #   （級数が巻ごとに変わるので、行間を固定値で書けない）。
    #   172×1.12=192.6→192 で、従来の t1=336/t2=528 と一致する。
    gap = lay.get("line_gap", lay.get("t2", lay["t1"]) - lay["t1"])
    if gap == "auto":
        gap = int(tsize * 1.12)
    ys = [lay["t1"] + i * gap for i in range(len(lines))]

    show_pill = t.get("pill", True) and cfg.get("runtime")

    # ★帯の字間も巻ごとに詰められる。 背景の主役が右上にいる巻では、既定の16だと
    #   帯が主役に食い込む（SOJ02は麦わら帽子に「OLD JAPAN」が乗った）。
    #   ★文字を小さくするのではなく字間で逃がすこと。 小さくすると読めなくなる。
    btrk = (t.get("tracking") or {}).get("brand", 16)
    items = [(brand, f_brand, btrk, lay["brand"])]
    items += [(ln, f_title, trk, y) for ln, y in zip(lines, ys)]

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for text, f, tr, y in items:
        _draw_tracked(gd, (X, y), text, f, tr, (0, 0, 0, 225))
    img = Image.alpha_composite(img.convert("RGBA"),
                                glow.filter(ImageFilter.GaussianBlur(16))).convert("RGB")
    d = ImageDraw.Draw(img)

    _draw_tracked(d, (X, lay["brand"]), brand, f_brand, btrk, col["gold"])
    d.line([(X, lay["brand"] + 76), (X + _tw(d, brand, f_brand, btrk), lay["brand"] + 84)],
           fill=col["gold"], width=3)

    for ln, y in zip(lines, ys):
        _draw_tracked(d, (X, y), ln, f_title, trk, col["cream"])
    # ★下線の位置は題字の大きさに比例させる。 従来は172px前提の固定値(157/168)だった。
    #   172×0.913=157.0、172×0.977=168.0 なので **題字172pxの巻は1画素も変わらない**
    #   （Vol.14・15で実測して確認済み。公開済みの巻はすべて172）。
    #   ★題字を落としている巻だけ下線が動く。 SOJ01（150px）は21px上がる。
    #     こちらが正しい位置で、固定値のままだと題字が小さいほど下線が離れていた。
    #     SOJ01は未公開なので作り直して差し支えない。
    if t.get("title_rule", True):
        yl = ys[-1]
        d.line([(X, yl + int(tsize * 0.913)),
                (X + _tw(d, lines[-1], f_title, trk), yl + int(tsize * 0.977))],
               fill=col["gold"], width=3)

    # ★題字の下に小さく1行置ける（`thumb_sub`）。日本語の題字に英語の添え書きを付ける用途。
    #   ショートの見出しが「帯＋題字＋小さい2行」なので、それに寄せるための枠。
    sub = cfg.get("thumb_sub")
    if sub:
        f_sub = f_of("sub", t.get("sub_family", "serif"))
        _draw_tracked(d, (X, lay["sub"]), sub, f_sub,
                      (t.get("tracking") or {}).get("sub", 8), col["gold"])

    if show_pill:
        f_pill = f_of("pill", "sans")
        runtime = cfg["runtime"]
        pw = _tw(d, runtime, f_pill, 6) + 64
        d.rounded_rectangle([X, lay["row"], X + pw, lay["row"] + 92],
                            radius=12, fill=col["gold"])
        _draw_tracked(d, (X + 32, lay["row"] + 14), runtime, f_pill, 6, col["navy"])

    img.save(out)
    print(f"書き出し: {out} {img.size}")
    return out


def check_runtime(cfg):
    """サムネの尺表記が本編の実尺と合っているかを確かめる。

    ★「3 HOURS」のように時間で書く巻がある（Long Nights の3時間版）。
      分で書いた巻と同じ物差しで測ると 180 と 3 を比べることになるので、単位を見て分ける。
      時間表記の許容は ±3分（"3 Hours" が 2時間31分でも通ってしまうのを防ぐ）。
    """
    import re

    from .ffutil import load_json
    # ★中間生成物が無い巻でも落ちない（2026年8月25日）。
    #   bgmkit 以前に作った巻（Vol.3〜9）はサムネだけ作り直すので manifest が無い。
    #   照合できないことを言うだけにして、サムネの生成そのものは通す。
    # ★runtime は任意（pill: false の巻ではサムネに描かないため）。無ければ照合しない。
    if not cfg.get("runtime"):
        return
    mp = cfg.wpath("manifest.json")
    if not os.path.exists(mp):
        print(f"※ manifest が無いので尺の照合を飛ばした（{cfg.get('runtime','-')}）")
        return
    man = load_json(mp)
    m = re.search(r"(\d+)", cfg["runtime"])
    if not m:
        return True
    said = int(m.group(1))

    if re.search(r"hour", cfg["runtime"], re.I):
        real = man["total"] / 3600
        if abs(real - said) > 0.05:
            h, mi = int(man["total"] // 3600), int(man["total"] % 3600 // 60)
            print(f"⚠ サムネの尺 '{cfg['runtime']}' が実尺 {h}時間{mi}分 と違います。"
                  f"volumes の runtime を直してください。")
            return False
        return True

    real = int(round(man["total"] / 60))
    if said != real:
        print(f"⚠ サムネの尺 '{cfg['runtime']}' が実尺 {real} 分と違います。"
              f"volumes の runtime を直してください。")
        return False
    return True
