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

4. ★★長い巻は `segmented: true` にして場面ごとに書き出す（2026年8月24日、Vol.16で追加）。
   既定の作りは**全場面を1本の ffmpeg コマンド**で処理する。xfade を数珠つなぎにするため、
   最後の場面のフィルタも t=0 から動き続け、**全入力ぶんのフレームを同時に抱える**。
   2880x1620 の yuv420p は1フレーム7MBなので、22枚＋カードで8GBの機械に載らない。
   Vol.16（3時間）は空きメモリ69MB・圧縮に3.4GBという状態になり、
   **10.3時間かけて28〜37%しか進まなかった**（CPUは回っているのに前に進まない）。
   60分では起きず、尺が3倍になって初めて出た。同時進行の本数が尺に比例して増えるため。

   分割版は「場面の本体」と「継ぎ目」を別々の小さなコマンドで書き出し、最後に連結する。
   ・メモリは1〜2入力ぶんで済む（画質の設定は一切落とさない）
   ・**途中で落ちても1片ぶんしか失わない**（`.done` を見て再開する）
   ・`jobs` で並列に回せる
   ★既定は false。 公開済みの巻を作り直したときに1ビットも変わらないようにするため。
"""
import os
from concurrent.futures import ThreadPoolExecutor

from .ffutil import duration, ff, load_json, measure_loudness, mmss


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
    nt = len(man["tracks"])
    # ★★画像は曲数の約数でよい（2026年8月26日）。 従来は「枚数＝曲数」しか通らなかった。
    #   22曲なら22枚が要り、**1枚に手をかける作りと正面から衝突する**
    #   （伸びているBGM動画は3時間でも場面が3〜5回しか変わらない）。
    #   20曲＝5枚なら4曲ごとに切り替わる。旧 build_comp.py には同じ仕様があったが
    #   bgmkit に引き継がれていなかった。
    #   ★切り替えは必ず曲の変わり目に置く。 曲の途中で絵が変わると、
    #     音と映像の継ぎ目が別々の場所に来て気持ちが悪い。
    if nt % n:
        raise SystemExit(
            f"画像{n}枚に対して曲は{nt}本です。**枚数は曲数の約数**にしてください"
            f"（{nt}本なら " + "・".join(str(d) for d in range(1, nt + 1) if nt % d == 0)
            + " 枚のいずれか）。")
    per = nt // n
    if per > 1:
        print(f"画像1枚が{per}曲ぶん（{n}枚 / {nt}曲）")

    starts = [man["tracks"][i * per]["start"] for i in range(n)]
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

    if v.get("segmented"):
        return _segmented(cfg, paths, seg, cuts, moves, T)

    e = v["encode"]
    out = cfg.wpath("video.mp4")
    ff([*inputs, "-filter_complex", ";".join(parts), "-map", prev, "-t", f"{T:.6f}",
        "-c:v", e["vcodec"], "-preset", e["preset"], "-crf", str(e["crf"]),
        "-pix_fmt", "yuv420p", "-r", str(fps), "-g", str(fps * 10), out])
    print(f"\n書き出し: {out}")
    return out


def _chain(cfg, i, moves, nframes, skip):
    """1枚ぶんのフィルタ列。1本版と同じものを使う（画質を変えないため）。"""
    v = cfg["video"]
    SS_W, SS_H = v["supersample"]
    OW, OH = v["output"]
    dirn, pan = moves[i]
    return (f"scale={SS_W}:{SS_H}:flags=lanczos,setsar=1,format=yuv420p,fps={v['fps']},"
            f"{_kenburns(cfg, dirn, pan, nframes, skip)},"
            f"scale={OW}:{OH}:flags=lanczos,{v['unsharp']}")


def _enc(cfg):
    e = cfg["video"]["encode"]
    return ["-c:v", e["vcodec"], "-preset", e["preset"], "-crf", str(e["crf"]),
            "-pix_fmt", "yuv420p", "-r", str(cfg["video"]["fps"])]


def _plan(cfg, paths, seg, cuts, moves, T):
    """出力を「場面の本体」と「継ぎ目」に切り分ける。すべてフレーム数で持つ。

    場面 i のクリップの先頭は、出力の origin[i] フレーム目に置かれる。
    ケンバーンズは **クリップ全体の長さ** に対して計算し、途中から描くときは skip で送る。
    こうすると1本版と同じ動きになる。
    """
    v = cfg["video"]
    fps = v["fps"]
    n = len(paths)
    F = lambda x: int(round(x * fps))                            # noqa: E731
    xff = F(v["xfade"])
    cutf = [F(c) for c in cuts]
    segf = [F(s) for s in seg]
    origin = [0] + cutf
    endf = F(T)
    card = v.get("card")
    cardf = F(T - v["card_len"]) if card else endf
    cxff = F(v["card_xfade"]) if card else 0

    pieces = []
    for i in range(n):
        head = origin[i] + (xff if i else 0)                     # この場面の本体が始まる出力位置
        tail = cutf[i] if i < n - 1 else cardf                   # 次の継ぎ目が始まる出力位置
        if tail > head:
            pieces.append(dict(kind="body", i=i, skip=head - origin[i],
                               nframes=segf[i], count=tail - head))
        if i < n - 1:
            # 次の場面のクリップは先頭(skip=0)から。ケンバーンズはそれぞれの全長で計算する。
            pieces.append(dict(kind="trans", i=i, skip=cutf[i] - origin[i],
                               nframes=segf[i], n2=segf[i + 1], count=xff))
    if card:
        pieces.append(dict(kind="card_in", i=n - 1, skip=cardf - origin[n - 1],
                           nframes=segf[n - 1], count=cxff))
        pieces.append(dict(kind="card", count=endf - cardf - cxff))
    return pieces, endf


def _render(cfg, pc, paths, moves, out):
    v = cfg["video"]
    xf, cxf = v["xfade"], v.get("card_xfade")
    if pc["kind"] == "body":
        ff(["-loop", "1", "-i", paths[pc["i"]],
            "-vf", _chain(cfg, pc["i"], moves, pc["nframes"], pc["skip"]),
            "-frames:v", str(pc["count"]), *_enc(cfg), "-f", "mpegts", out])
    elif pc["kind"] == "card":
        ff(["-loop", "1", "-i", v["card"],
            "-vf", f"{v['card_filter']},setsar=1,format=yuv420p,fps={v['fps']}",
            "-frames:v", str(pc["count"]), *_enc(cfg), "-f", "mpegts", out])
    else:
        i = pc["i"]
        a = _chain(cfg, i, moves, pc["nframes"], pc["skip"])
        if pc["kind"] == "trans":
            # 次の場面のクリップは先頭から入る。動きは自分の全長で計算する。
            second = paths[i + 1]
            b = _chain(cfg, i + 1, moves, pc["n2"], 0)
            d = xf
        else:
            second = v["card"]
            b = f"{v['card_filter']},setsar=1,format=yuv420p,fps={v['fps']}"
            d = cxf
        fc = (f"[0:v]{a}[a];[1:v]{b}[b];"
              f"[a][b]xfade=transition=fade:duration={d}:offset=0[o]")
        ff(["-loop", "1", "-i", paths[i], "-loop", "1", "-i", second,
            "-filter_complex", fc, "-map", "[o]",
            "-frames:v", str(pc["count"]), *_enc(cfg), "-f", "mpegts", out])


def _segmented(cfg, paths, seg, cuts, moves, T):
    v = cfg["video"]
    pieces, endf = _plan(cfg, paths, seg, cuts, moves, T)
    d = cfg.wpath("seg")
    os.makedirs(d, exist_ok=True)

    total = sum(p["count"] for p in pieces)
    print(f"\n分割書き出し {len(pieces)}片 / 合計 {total}フレーム "
          f"= {total / v['fps']:.2f}秒（狙い {T:.2f}秒）")
    if total != endf:
        raise SystemExit(f"フレーム数が合いません: {total} ≠ {endf}")

    todo = []
    for k, pc in enumerate(pieces):
        pc["out"] = os.path.join(d, f"{k:03d}.ts")
        pc["done"] = pc["out"] + ".done"
        if not os.path.exists(pc["done"]):
            todo.append((k, pc))
    print(f"  済み {len(pieces) - len(todo)}片 / これから {len(todo)}片")

    def work(item):
        k, pc = item
        _render(cfg, pc, paths, moves, pc["out"])
        open(pc["done"], "w").write(str(pc["count"]))
        print(f"  {k:03d} {pc['kind']:8s} {pc['count']:6d}フレーム 完了", flush=True)

    jobs = int(v.get("jobs", 2))
    with ThreadPoolExecutor(max_workers=jobs) as ex:
        list(ex.map(work, todo))

    lst = cfg.wpath("seg_list.txt")
    with open(lst, "w") as f:
        for pc in pieces:
            f.write(f"file '{pc['out']}'\n")
    out = cfg.wpath("video.mp4")
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    got = duration(out)
    print(f"\n連結: {out}  {got:.2f}秒（狙い {T:.2f}秒 / 差 {got - T:+.2f}秒）")
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
    # ★AAC段の持ち上がりを吸収するための素直なゲイン。圧縮ではないので質感は変わらない。
    g = a.get("mux_gain_db", 0) or 0
    af = f"afade=t=in:st=0:d={fi},afade=t=out:st={T - fo:.3f}:d={fo}"
    if g:
        af = f"volume={g}dB,{af}"
        print(f"mux前に {g:+.1f}dB（AAC段の持ち上がりぶん）")
    ff(["-i", cfg.wpath("video.mp4"), "-i", cfg.music_bed,
        "-map", "0:v", "-map", "1:a",
        "-af", af,
        "-c:v", "copy", "-c:a", "aac", "-b:a", a.get("bitrate", "320k"),
        "-ar", "48000", "-movflags", "+faststart", out])
    print(f"完成: {out}  ({int(T // 60)}分{int(T % 60):02d}秒)")
    _check_peak(cfg, out)
    return out


def _check_peak(cfg, path):
    """完成MP4のラウドネスとトゥルーピークを測る。

    ★AAC段でトゥルーピークが上がる。music_bed.wav では狙いどおりでも、
      完成品では超えていることがある（Vol.14は -1.5狙いで **-1.1**、Vol.15は -1.3）。
      ★★雨のような広帯域のノイズは持ち上がりが大きい。 Vol.16 は **+1.0dB** 上がって
        -0.2 dBTP まで来た（音楽は +0.2〜0.4dB）。環境音の巻では `mux_gain_db` で
        素直に下げること。リミッタを強めると雨のうねりが平らになる。
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
