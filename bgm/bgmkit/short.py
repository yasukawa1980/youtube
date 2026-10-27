"""縦型ショート（1080x1920）を作る。

本編の画像1枚と、音声の任意の位置45秒から組む。
巻ごとに手で作っていたものを道具にした（Vol.15は手作業）。

★レイアウトは公開済みのVol.15のショートを実測して合わせてある。
  文字の位置（1080x1920のフレーム内）：
    WHISPERS OF JAPAN  y1238 高さ24  x85〜
    作品名              y1330 高さ76
    サブ1               y1462 高さ31
    サブ2               y1520 高さ31
  左の余白は88px。

★★出だしが静かな位置から切らないこと。
  Vol.15のショートCは本編00:00から採ったため、曲のフェードインをそのまま拾って
  **最初の1秒が本体より19dB低かった**（A・Bは0〜5dB差）。
  ショートのフィードは1秒未満でスワイプされるので、無音に近い出だしは離脱を招く。
  → 切り出した音の頭と本体を比べて、離れていたら警告を出す。

★文字は縮小後に重ねる。 先に重ねてから縮めると字が滲む。
"""
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .ffutil import ff, measure_loudness

# ★測るときの標本化周波数。8000では蝉・虫の主帯(4〜9kHz)が帯域外になる。
HEAD_SR = 22050


def _font(path, size, index=0):
    return ImageFont.truetype(os.path.expanduser(path), size, index=index)


def _tracked(d, xy, text, f, tr, fill):
    x, y = xy
    for c in text:
        d.text((x, y), c, font=f, fill=fill)
        x += d.textlength(c, font=f) + tr
    return x - tr


def _overlay(cfg, spec, path):
    """文字だけを描いた透過PNGを作る。"""
    s = cfg["short"]
    W, H = s["size"]
    lay, sz = s["layout"], s["sizes"]
    col = {k: tuple(v) for k, v in cfg["thumb"]["colors"].items()}
    f_brand = _font(s["fonts"]["latin"], sz["brand"], s["font_index"]["latin"])
    f_title = _font(s["fonts"]["jp"], sz["title"], s["font_index"]["jp"])
    f_sub = _font(s["fonts"]["jp"], sz["sub"], s["font_index"]["jp"])

    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # ★★下側にグラデーションのスクリムを敷く（2026年8月25日に追加）。
    #   Vol.15のショートは下が元から暗かったので無くても読めたが、
    #   明るい石畳や砂利が下に来る絵では文字が沈む（Long Nights 3 の場面28で実際に沈んだ）。
    #   サムネと同じ考え方。絵を殺さないよう、上端から緩やかに立ち上げる。
    sc = s.get("scrim")
    if sc:
        y0, y1 = sc["top"], sc.get("full", H)
        a = np.zeros((H, 1), dtype=np.float64)
        ramp = np.clip((np.arange(H) - y0) / max(1, y1 - y0), 0, 1)
        a[:, 0] = (ramp ** sc.get("gamma", 1.6)) * sc["opacity"] * 255
        layer = np.zeros((H, W, 4), dtype=np.uint8)
        layer[:, :, 0], layer[:, :, 1], layer[:, :, 2] = sc["color"]
        layer[:, :, 3] = np.repeat(a.astype(np.uint8), W, axis=1)
        im.alpha_composite(Image.fromarray(layer, "RGBA"))
    d = ImageDraw.Draw(im)
    X, tr = lay["x"], s["tracking"]

    # ★暗いハローを敷く。縮小して見るので、これが無いと背景と混ざって潰れる（thumb と同じ理屈）
    def halo(xy, text, f, track=0):
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)):
            if track:
                _tracked(d, (xy[0] + dx, xy[1] + dy), text, f, track, (0, 0, 0, 170))
            else:
                d.text((xy[0] + dx, xy[1] + dy), text, font=f, fill=(0, 0, 0, 170))

    halo((X, lay["brand"]), cfg["brand"], f_brand, tr)
    end = _tracked(d, (X, lay["brand"]), cfg["brand"], f_brand, tr, col["gold"] + (255,))
    d.line([(X, lay["brand"] + sz["brand"] + 14), (end, lay["brand"] + sz["brand"] + 14)],
           fill=col["gold"] + (200,), width=2)

    halo((X, lay["title"]), spec["title"], f_title)
    d.text((X, lay["title"]), spec["title"], font=f_title, fill=col["cream"] + (255,))

    for i, line in enumerate(spec.get("sub", [])[:2]):
        y = lay["sub1"] if i == 0 else lay["sub2"]
        halo((X, y), line, f_sub)
        d.text((X, y), line, font=f_sub, fill=col["cream"] + (225,))

    im.save(path)
    return path


def _kenburns_v(cfg, dirn, nframes):
    """縦版のケンバーンズ。中央固定で寄る/引くだけにする（横に振ると縦画面では酔う）。"""
    s = cfg["short"]
    W, H = s["supersample"]
    z0 = s["zoom_max"]
    t = f"(on/{nframes})"
    z = f"(1+{z0 - 1:.6f}*{t})" if dirn == "in" else f"({z0:.6f}-{z0 - 1:.6f}*{t})"
    w, h = f"({W}/{z})", f"({H}/{z})"
    px, py = f"(({W}-{w})/2)", f"(({H}-{h})/2)"
    return (f"perspective=x0='{px}':y0='{py}':x1='{px}+{w}':y1='{py}':"
            f"x2='{px}':y2='{py}+{h}':x3='{px}+{w}':y3='{py}+{h}':"
            f"interpolation=cubic:sense=source:eval=frame")


def _hms(v):
    if isinstance(v, (int, float)):
        return float(v)
    p = [float(x) for x in str(v).split(":")]
    return sum(x * 60 ** i for i, x in enumerate(reversed(p)))


def _head_check(path, start, dur):
    """切り出す位置の頭が本体より静かでないか。静かならフィードで離脱する。

    ★★8000Hz でデコードしてはいけない（2026年8月25日、蝉の巻で判明）。
      ナイキストが4kHzになる。ニイニイゼミ（主帯7343〜8635Hz・ほぼ純音）を測ると
      **エネルギーが丸ごと帯域外に出て -80dB** と出た。音は正常で、測定器が
      聞こえていなかっただけ。素材の主帯より上まで取れる標本化周波数で測ること。
      同じ罠は vet の検証でも踏んだ。**環境音を扱う測定は毎回ここを疑う。**
    """
    def rms(ss, t):
        r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{ss}", "-t", f"{t}",
                            "-i", path, "-ac", "1", "-ar", str(HEAD_SR),
                            "-f", "f32le", "-"], capture_output=True)
        x = np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)
        return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12) if len(x) else -99.0

    head = rms(start, 1.0)
    body = rms(start + dur / 2 - 1.5, 3.0)
    return head, body, head - body


def build(cfg, only=None):
    specs = cfg.get("shorts")
    if not specs:
        raise SystemExit("巻のYAMLに `shorts:` がありません。")
    s = cfg["short"]
    W, H = s["size"]
    SW, SH = s["supersample"]
    fps = s["fps"]
    bed = cfg.music_bed
    if not os.path.exists(bed):
        raise SystemExit(f"音声がありません: {bed}")
    outdir = os.path.join(cfg["dir"], "ショート")
    os.makedirs(outdir, exist_ok=True)
    tmp = cfg.wpath("short_overlay.png")
    made = []

    for i, spec in enumerate(specs, 1):
        tag = spec.get("tag") or chr(64 + i)
        if only and tag not in only:
            continue
        dur = float(spec.get("seconds", s["seconds"]))
        start = _hms(spec["at"])
        img = spec["image"]
        img = img if os.path.isabs(str(img)) else os.path.join(
            cfg.images_dir, img if isinstance(img, str) else cfg["images"][int(img) - 1])

        h, b, gap = _head_check(bed, start, dur)
        note = ""
        if gap < -8:
            note = (f"  ★頭が本体より{-gap:.0f}dB静か。フィードで離脱する。"
                    f"開始位置をずらすこと")
        print(f"{tag}  {spec['title']}  {int(start)//60:02d}:{int(start)%60:02d}から{dur:.0f}秒"
              f"  頭{h:.1f}/本体{b:.1f}dB{note}")

        _overlay(cfg, spec, tmp)
        nf = int(round(dur * fps))
        anchor = float(spec.get("anchor", 0.5))
        vf = (f"[0:v]scale=-1:{SH}:flags=lanczos,"
              f"crop={SW}:{SH}:'(iw-{SW})*{anchor}':0,setsar=1,format=yuv420p,fps={fps},"
              f"{_kenburns_v(cfg, spec.get('move', 'in'), nf)},"
              f"scale={W}:{H}:flags=lanczos,{s['unsharp']}[v];"
              f"[v][1:v]overlay=0:0[vo]")
        # ★ショートは本編と音量を分けられる。 本編を控えめにした巻（環境音など）でも、
        #   フィードでは周りと同じ高さでないと埋もれる。書かなければ本編と同じ。
        a = dict(cfg["audio"])
        a["target_lufs"] = s.get("target_lufs", a["target_lufs"])
        a["true_peak"] = s.get("true_peak", a["true_peak"])
        m = measure_loudness(bed, a, ss=start, t=dur)
        fade = s["audio_fade"]
        af = (f"loudnorm=I={a['target_lufs']}:TP={a['true_peak']}:LRA={a['lra']}"
              f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
              f":offset={m['target_offset']}:linear=true,"
              f"afade=t=in:st=0:d={fade},afade=t=out:st={dur - fade:.2f}:d={fade}")
        out = os.path.join(outdir, f"{cfg.slug}_ショート_{tag}.mp4")
        e = s["encode"]
        ff(["-loop", "1", "-i", img, "-i", tmp, "-ss", f"{start}", "-t", f"{dur}", "-i", bed,
            "-filter_complex", vf, "-map", "[vo]", "-map", "2:a", "-af", af,
            "-frames:v", str(nf),
            "-c:v", e["vcodec"], "-preset", e["preset"], "-crf", str(e["crf"]),
            "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", a.get("bitrate", "320k"), "-ar", "48000",
            "-movflags", "+faststart", out])
        made.append(out)
        print(f"    → {out}")
    return made
