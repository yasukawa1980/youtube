"""映像トラックを組む。旧 build_vol*.py。

守っている決めごと:

1. ケンバーンズに zoompan を使わない。
   zoompan は切り出し位置を整数ピクセルでしか指定できず、動きが遅いほど
   「4秒に1回1〜2pxカクッと飛ぶ」症状が出る（Vol.4で実測、動いていたフレームは1.7%）。
   perspective なら4隅を小数の式で置けるので、段差が 1.4〜2.0px → 0.001〜0.010px になる。
   eval=frame が必須。4隅の順序は 左上・右上・左下・右下。

2. 画像の尺を等分しない。
   等分すると曲の長さのばらつきぶん映像と音の変わり目が離れ、Vol.6では最大32秒ずれた。
   音のクロスフェードの中心と映像のクロスフェードの中心を合わせる：
     映像の切替開始 = 曲i+1の頭 + (音XF - 映像XF) / 2

3. エンドカードは本編の後ろに足さない。
   最後の場面からクロスフェードでカードへ入り、カードの上で音楽を消す。
   xfade は「1本目の供給長 ≧ offset + duration」でないと出力が offset で打ち切られる。
"""
import os

from .ffutil import ff, load_json, measure_loudness, mmss


def _kenburns(cfg, dirn, pan, nframes, skip=0):
    v = cfg["video"]
    W, H = v["supersample"]
    z0 = v["zoom_max"]
    t = f"((on+{skip})/{nframes})" if skip else f"(on/{nframes})"
    z = (f"(1+{z0 - 1:.6f}*{t})" if dirn == "in" else f"({z0:.6f}-{z0 - 1:.6f}*{t})")
    w, h = f"({W}/{z})", f"({H}/{z})"
    room = f"(({W}-{w})/2)"
    px = room if pan == "c" else (f"({room}*(1+{t}))" if pan == "r" else f"({room}*(1-{t}))")
    py = f"(({H}-{h})/2)"
    return (f"perspective=x0='{px}':y0='{py}':x1='{px}+{w}':y1='{py}':"
            f"x2='{px}':y2='{py}+{h}':x3='{px}+{w}':y3='{py}+{h}':"
            f"interpolation=cubic:sense=source:eval=frame")


def default_moves(n):
    """寄る/引くを交互、中央/左/右を巡回。最後の2枚は両方「引き」で拡大率を揃える。

    クライマックス→夜明けのように連続した場面では、9=(in,c) で寄り切って
    10=(out,c) で同じズーム量から引くと、クロスフェードの前後で拡大率が一致して
    絵が動かないまま時間だけが進んで見える。
    """
    pans = ["c", "l", "r"]
    mv = [("in" if i % 2 == 0 else "out", pans[i % 3]) for i in range(n)]
    if n >= 2:
        mv[-2] = ("in", "c")
        mv[-1] = ("out", "c")
    return mv


def build(cfg):
    v = cfg["video"]
    man = load_json(cfg.wpath("manifest.json"))
    T = man["total"]
    axf = man["xf"]
    xf = v["xfade"]
    fps = v["fps"]
    SS_W, SS_H = v["supersample"]
    OW, OH = v["output"]

    images = cfg.get("images")
    if not images:
        d = cfg.images_dir
        images = sorted(f for f in os.listdir(d) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    paths = [p if os.path.isabs(p) else os.path.join(cfg.images_dir, p) for p in images]
    for p in paths:
        if not os.path.exists(p):
            raise SystemExit(f"画像がありません: {p}")
    n = len(paths)
    if n != len(man["tracks"]):
        raise SystemExit(f"画像{n}枚に対して曲は{len(man['tracks'])}本です。数を揃えてください。")

    starts = [t["start"] for t in man["tracks"]]
    cuts = [starts[i] + (axf - xf) / 2 for i in range(1, n)]
    seg = [cuts[0] + xf]
    for i in range(1, len(cuts)):
        seg.append(cuts[i] - cuts[i - 1] + xf)
    seg.append(T - cuts[-1])

    moves = cfg.get("moves") or default_moves(n)
    moves = [tuple(m) for m in moves]

    parts, inputs = [], []
    for i, p in enumerate(paths):
        L = seg[i]
        inputs += ["-loop", "1", "-t", f"{L:.6f}", "-i", p]
        dirn, pan = moves[i]
        parts.append(
            f"[{i}:v]scale={SS_W}:{SS_H}:flags=lanczos,setsar=1,format=yuv420p,fps={fps},"
            f"{_kenburns(cfg, dirn, pan, int(round(L * fps)))},"
            f"scale={OW}:{OH}:flags=lanczos,{v['unsharp']},"
            f"trim=duration={L:.6f},setpts=PTS-STARTPTS[s{i}]")

    prev = "[s0]"
    for i in range(1, n):
        parts.append(f"{prev}[s{i}]xfade=transition=fade:duration={xf}"
                     f":offset={cuts[i - 1]:.6f}[v{i}]")
        prev = f"[v{i}]"

    card = v.get("card")
    if card:
        clen, cxf = v["card_len"], v["card_xfade"]
        inputs += ["-loop", "1", "-t", f"{clen}", "-i", card]
        parts.append(f"[{n}:v]{v['card_filter']},setsar=1,format=yuv420p,fps={fps},"
                     f"trim=duration={clen},setpts=PTS-STARTPTS[card]")
        parts.append(f"{prev}[card]xfade=transition=fade:duration={cxf}"
                     f":offset={T - clen:.6f}[vout]")
        prev = "[vout]"

    print("切替の照合（曲の中心 / 映像の中心）")
    for i, c in enumerate(cuts, 1):
        am, vm = starts[i] + axf / 2, c + xf / 2
        print(f"  {i}: 曲 {mmss(am)}.{int(am % 1 * 100):02d} / "
              f"映像 {mmss(vm)}.{int(vm % 1 * 100):02d}  差 {vm - am:+.2f}s"
              f"   画像{i}の尺 {seg[i - 1]:.1f}s")
    print(f"  {n}枚目 {seg[-1]:.1f}s / 合計 {sum(seg) - xf * (n - 1):.2f}s（音声 {T:.2f}s）")

    e = v["encode"]
    out = cfg.wpath("video.mp4")
    ff([*inputs, "-filter_complex", ";".join(parts), "-map", prev, "-t", f"{T:.6f}",
        "-c:v", e["vcodec"], "-preset", e["preset"], "-crf", str(e["crf"]),
        "-pix_fmt", "yuv420p", "-r", str(fps), "-g", str(fps * 10), out])
    print(f"\n書き出し: {out}")
    return out


def mux(cfg):
    """映像と音声を合わせて最終MP4にする。

    これまで巻ごとに手打ちしていた工程。afade の尻はエンドカードの上で消える位置に置く。
    映像は再エンコードしない（-c:v copy）ので、音だけ差し替えても画は1ビットも変わらない。
    """
    v, a = cfg["video"], cfg["audio"]
    man = load_json(cfg.wpath("manifest.json"))
    T = man["total"]
    fi, fo = a["fade_in"], a["fade_out"]
    out = os.path.join(cfg["dir"], f"{cfg.slug}_完成.mp4")
    ff(["-i", cfg.wpath("video.mp4"), "-i", cfg.wpath("music_bed.wav"),
        "-map", "0:v", "-map", "1:a",
        "-af", f"afade=t=in:st=0:d={fi},afade=t=out:st={T - fo:.3f}:d={fo}",
        "-c:v", "copy", "-c:a", "aac", "-b:a", a.get("bitrate", "320k"),
        "-ar", "48000", "-movflags", "+faststart", out])
    print(f"完成: {out}  ({int(T // 60)}分{int(T % 60):02d}秒)")
    _check_peak(cfg, out)
    return out


def _check_peak(cfg, path):
    """完成MP4のラウドネスとトゥルーピークを測る。

    ★AAC段でトゥルーピークが上がる。music_bed.wav では狙いどおりでも、
      完成品では超えていることがある（Vol.14は -1.5狙いで **-1.1**、Vol.15は -1.3）。
      Vol.14の申し送り「mux 後にトゥルーピークを検査する工程が無い」への対応
      （2026年8月19日に追加）。
      YouTubeの推奨上限は -1.0 dBTP なので、それを超えたときだけ警告する。
    """
    a = cfg["audio"]
    m = measure_loudness(path, a)
    i, tp = float(m["input_i"]), float(m["input_tp"])
    note = ""
    if tp > -1.0:
        note = "  ⚠ YouTubeの推奨上限 -1.0 dBTP を超えています"
    elif tp > a["true_peak"]:
        note = f"  （狙いの {a['true_peak']} からAAC段で {tp - a['true_peak']:+.1f}dB。範囲内）"
    print(f"完成品の実測: {i:.1f} LUFS / トゥルーピーク {tp:.1f} dBTP{note}")
