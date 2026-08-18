"""確定した曲順から音声トラックを組む。

旧 prep_audio*.py。曲ごとに
  頭尾の無音をトリム → loudnorm 2パスで -14 LUFS に統一 → クロスフェードで連結。

ラウドネスの統一は必須。Sunoの生成物は曲ごとに -13〜-16 LUFS と3LUほど開いていて、
そのまま並べると曲が変わるたびに音量が動く。

★環境音（`ambient`）を設定すると、連結後の music_bed.wav の上に1枚重ねる。
  濃さの基準は公開済みのVol.5「蛍の川」の実測で、**-18dB でVol.5と同じ**になる
  （4〜8kHz帯の変動係数が 0.52 で一致。詳細はメモリ vol1-has-no-nature-sounds）。
  素材は必ず**継ぎ目の無いループに作り直してから**敷く。9分の素材を60分に単純に
  繰り返すと、6回ある折り返しでプツッと切り替わるのが聞こえる。
"""
import os

from .ffutil import (duration, ff, measure_loudness, mmss, pcm_mono, save_json,
                     silence_bounds)


def build(cfg, order):
    acfg = cfg["audio"]
    xf = acfg["crossfade"]
    src = cfg.tracks_dir
    out = cfg.wpath("norm")
    os.makedirs(out, exist_ok=True)

    man = []
    for i, name in enumerate(order, 1):
        p = os.path.join(src, name)
        d = duration(p)
        h, t = silence_bounds(p, d, acfg)
        seg = t - h
        m = measure_loudness(p, acfg, ss=h, t=seg)
        dst = os.path.join(out, f"{i:02d}.wav")
        ln = (f"loudnorm=I={acfg['target_lufs']}:TP={acfg['true_peak']}:LRA={acfg['lra']}"
              f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
              f":offset={m['target_offset']}:linear=true:print_format=summary")
        ff(["-ss", f"{h}", "-t", f"{seg}", "-i", p, "-af", ln,
            "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", dst])
        od = duration(dst)
        man.append(dict(idx=i, name=name, dur=round(od, 3), in_i=m["input_i"]))
        print(f"{i:02d} {name:38s} trim {h:5.2f}-{t:6.2f}  {od:7.2f}s  "
              f"in_I={m['input_i']:>6s} → {acfg['target_lufs']}")

    ins, parts, prev = [], [], "[0:a]"
    for i in range(len(order)):
        ins += ["-i", os.path.join(out, f"{i + 1:02d}.wav")]
    for i in range(1, len(order)):
        tag = f"[a{i}]"
        parts.append(f"{prev}[{i}:a]acrossfade=d={xf}:c1=tri:c2=tri{tag}")
        prev = tag

    bed = cfg.wpath("music_bed.wav")
    ff([*ins, "-filter_complex", ";".join(parts), "-map", prev,
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", bed])

    total = duration(bed)
    starts, acc = [0.0], 0.0
    for e in man[:-1]:
        acc += e["dur"] - xf
        starts.append(round(acc, 3))
    for e, s in zip(man, starts):
        e["start"] = s
    save_json(cfg.wpath("manifest.json"),
              dict(tracks=man, total=round(total, 3), xf=xf))

    print(f"\n連結後 {total:.2f}s = {int(total // 60)}分{int(total % 60):02d}秒")
    print("\n曲頭の時刻（チャプター用）")
    for e in man:
        print(f"  {mmss(e['start'])}  {e['name']}")

    # ジャンル側に既定（濃さ・フェード）だけ置いてあるので、`file` を書いた巻だけ敷く。
    if (cfg.get("ambient") or {}).get("file"):
        # 変わり目の中心。映像の切り替えも同じ時刻に揃っている（video.py の cuts）。
        seams = [st + xf / 2 for st in starts[1:]]
        bed = _lay_ambient(cfg, bed, total, seams)
    return bed


def _env(amb, gain, seams):
    """環境音の音量。`duck_db` を書くと「曲の変わり目で持ち上がる」envelope になる。

    ★本人の要望（2026年8月17日）：「常にバックで流れているより、曲と映像の
      変わり目に聞こえるようにしたい」。**完全に消してから出すのはやらない** ——
      虫は鳴き始めたり止んだりしないので、出入りが聞こえると作り物になる。
      **底を敷いたまま変わり目だけ山にする**（音楽が薄くなると気づく、という形）。

    底＝gain_db + duck_db。既定の -18 + -12 = -30dB は 3〜5kHz を +7.6dB 上げるだけで、
    山の -18dB は +17.7dB（いずれも実測。効き方の表は ambient-layer-pipeline を参照）。

    山は三角。`swell` は全幅なので、片側は swell/2。曲は最短でも2分あるので
    swell が数十秒でも山どうしは重ならないが、念のため min(1,…) で頭を押さえる。
    duck_db が無ければ従来どおり通しで一定。
    """
    duck = amb.get("duck_db")
    if not duck:
        return f"volume={gain}dB"
    w = amb.get("swell", 12.0) / 2
    peak, floor = 10 ** (gain / 20), 10 ** ((gain + duck) / 20)
    tri = "+".join(f"max(0\\,1-abs(t-{s:.3f})/{w:g})" for s in seams)
    expr = f"{floor:.6f}+{peak - floor:.6f}*min(1\\,{tri})"
    return f"volume=volume='{expr}':eval=frame"


def _seamless_loop(cfg, src, xf):
    """素材を「終わりと頭が繋がるループ」に作り直す。

    長さLの素材の末尾 xf 秒を、先頭 xf 秒の上にクロスフェードで重ねる。
    出来上がりは L-xf 秒で、その最後は素材の L-xf 地点、頭も同じ素材の
    L-xf 地点から始まるので、単純に繰り返しても折り返しが聞こえない。
    """
    L = duration(src)
    if L <= xf * 3:
        raise SystemExit(f"環境音の素材が短すぎます（{L:.1f}秒）。ループの重ね幅の3倍は要ります。")
    out = cfg.wpath("ambient_loop.wav")
    fc = (f"[0:a]atrim=0:{L - xf},asetpts=N/SR/TB,afade=t=in:d={xf}[a];"
          f"[0:a]atrim={L - xf}:{L},asetpts=N/SR/TB,afade=t=out:d={xf},"
          f"apad=whole_dur={L - xf}[b];"
          f"[a][b]amix=inputs=2:duration=first:normalize=0[o]")
    ff(["-i", src, "-filter_complex", fc, "-map", "[o]",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", out])
    return out, L - xf


def _lay_ambient(cfg, bed, total, seams):
    """連結済みの音楽の上に環境音を1枚敷き、-14 LUFS に測り直す。"""
    acfg, amb = cfg["audio"], cfg["ambient"]
    src = os.path.expanduser(amb["file"])
    if not os.path.exists(src):
        raise SystemExit(f"環境音の素材が見つかりません: {src}")
    gain = amb.get("gain_db", -18.0)
    fi, fo = amb.get("fade_in", 8.0), amb.get("fade_out", acfg["fade_out"])

    # ★環境音を敷いた結果は music_bed.wav に上書きするので、敷く前を先に退避する。
    #   同じパスのまま _ambient_check に渡すと、自分自身と比べて必ず 0dB になる。
    dry = cfg.wpath("music_bed_dry.wav")
    os.replace(bed, dry)

    loop, loop_len = _seamless_loop(cfg, src, amb.get("loop_xfade", 4.0))
    duck = amb.get("duck_db")
    how = (f"{gain}dB 通し" if not duck else
           f"底{gain + duck}dB → 変わり目{len(seams)}箇所で{gain}dB "
           f"（山の全幅{amb.get('swell', 12.0):g}秒）")
    print(f"\n環境音 {os.path.basename(src)} → ループ {loop_len:.1f}秒 × "
          f"{total / loop_len:.1f}回 / {how}")

    mixed = cfg.wpath("music_bed_ambient.wav")
    fc = (f"[0:a]atrim=0:{total},asetpts=N/SR/TB,{_env(amb, gain, seams)},"
          f"afade=t=in:d={fi},afade=t=out:st={total - fo}:d={fo}[amb];"
          f"[1:a][amb]amix=inputs=2:duration=first:normalize=0[o]")
    ff(["-stream_loop", "-1", "-i", loop, "-i", dry,
        "-filter_complex", fc, "-map", "[o]",
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", mixed])

    # 重ねたぶん上がるので測り直す。-18dB なら 0.1LU 程度だが、
    # トゥルーピークは Vol.14 で AAC 段の 0.4dB に泣いているので必ず見る。
    m = measure_loudness(mixed, acfg)
    out = cfg.wpath("music_bed.wav")
    ln = (f"loudnorm=I={acfg['target_lufs']}:TP={acfg['true_peak']}:LRA={acfg['lra']}"
          f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
          f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
          f":offset={m['target_offset']}:linear=true:print_format=summary")
    tmp = cfg.wpath("music_bed_final.wav")
    ff(["-i", mixed, "-af", ln, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", tmp])
    os.replace(tmp, out)
    print(f"環境音を重ねて測り直し: {m['input_i']} LUFS / TP {m['input_tp']} "
          f"→ {acfg['target_lufs']} LUFS")
    print(_ambient_check(dry, out, seams if amb.get("duck_db") else None))
    return out


def _ambient_check(before, after, seams=None,
                   bands=((500, 1500), (1500, 3000), (3000, 5000), (5000, 8000))):
    """環境音が「静かなところの底」を何dB持ち上げたかを帯域ごとに出す。

    ★固定帯の変動係数では測れない（Vol.5の水で合わせた 4〜8kHz の物差しを
      虫の音に当てると、虫は3〜5kHzにしか居ないので「敷けていない」と誤判定する）。
      素材が何であっても効くのは「敷く前と後の差」なので、そちらを見る。

    実測の目安（2026年8月17日、在庫の尺八→ピアノの継ぎ目で測定）：
      水を -22dB 通し … 1.5-3k +22.7dB / 3-5k +31.8dB / 5-8k +36.4dB（全帯を洗う）
      虫を -22dB 通し … 3-5k +14.1dB、他はほぼ0（狭い帯だけを埋める）
      虫を -18dB 通し … 3-5k +17.7dB
    **同じdBでも素材が違えば効き方は全く違う。** 数字を巻をまたいで流用しないこと。

    seams を渡すと「変わり目」と「山の外」を分けて測る。通しで測ると、
    山は全体のごく一部なので底の数字に埋もれて山が見えない。
    """
    import numpy as np

    def floors(path, windows=None):
        x = pcm_mono(path, 22050)
        n = 1024
        S = np.abs(np.fft.rfft(x[:len(x) // n * n].reshape(-1, n) * np.hanning(n), axis=1))
        fr = np.fft.rfftfreq(n, 1 / 22050)
        rate = 22050 / n
        if windows is not None:
            keep = np.zeros(len(S), bool)
            for a, b in windows:
                keep[max(0, int(a * rate)):int(b * rate)] = True
            S = S[keep] if keep.any() else S
        return [20 * np.log10(np.percentile(
            S[:, (fr >= lo) & (fr < hi)].mean(axis=1), 10) + 1e-12) for lo, hi in bands]

    def line(tag, windows):
        b, a = floors(before, windows), floors(after, windows)
        cols = "  ".join(f"{lo // 100 / 10}-{hi // 100 / 10}k {x - y:+.1f}dB"
                         for (lo, hi), y, x in zip(bands, b, a))
        return f"  {tag:12s}{cols}", max(x - y for y, x in zip(b, a))

    out = ["環境音の効き（静かなところの底の持ち上がり）"]
    if not seams:
        txt, top = line("通し", None)
        out.append(txt)
    else:
        at = [(s - 2.0, s + 2.0) for s in seams]
        away = [(s + 12.0, e - 12.0) for s, e in zip([0.0] + list(seams), list(seams) + [1e9])
                if e - s > 30.0]
        t1, m1 = line("変わり目", at)
        t2, m2 = line("山の外", away)
        out += [t1, t2]
        top = m1
    out.append("  → " + ("✓ 敷けている" if top >= 6 else "✗ ほぼ効いていない（濃さを見直す）"))
    return "\n".join(out)
