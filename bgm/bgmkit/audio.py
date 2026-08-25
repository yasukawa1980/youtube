"""確定した曲順から音声トラックを組む。

旧 prep_audio*.py。曲ごとに
  頭尾の無音をトリム → loudnorm 2パスで -14 LUFS に統一 → クロスフェードで連結。

ラウドネスの統一は必須。Sunoの生成物は曲ごとに -13〜-16 LUFS と3LUほど開いていて、
そのまま並べると曲が変わるたびに音量が動く。

★★`track_target_lufs` … 1本ずつを揃えるときの目標。既定は target_lufs と同じ。
  ピーク対平均の高い素材（雨）では -14 を狙うと**トラックごとに違う量のリミッタが掛かり**、
  到達点がばらついて段差になる。実測（4本）：
    目標 -14 → -17.6 / -16.7 / -14.0 / -14.2  ばらつき **3.6 LU**（＝聞こえる段差）
    目標 -18 → -18.2 / -18.4 / -18.0 / -18.0  ばらつき **0.4 LU**（＝揃う）
  **1本ずつは全部が無理なく届く低い目標で揃え、持ち上げは最後に全体へ一度だけ掛ける。**
  そうすればリミッタが掛かるとしても全トラックに同じだけ掛かるので段差にならない
  （`final_normalize` と対で使う）。

★★loudnorm が目標に届かないことがある。届いたかを必ず確かめる（2026年8月23日）。
  ピークに対して平均が低すぎる素材は、-14 LUFS まで上げるとクリップするため、
  loudnorm が Dynamic に落ちて**目標に届かないまま黙って通る**。
  実測：`rain-on-umbrella`（入力 -40.7 LUFS / TP -6.2）は **-22.5 LUFS までしか上がらず**、
  隣のトラックより8.5dB低いまま8分間鳴っていた。継ぎ目の落ち込みに見えていたものの正体はこれで、
  クロスフェードではなく**段差**だった。
  Sunoの曲は -13〜-16 LUFS に収まるので、この問題は環境音の巻で初めて出る。
  → 2パス目の summary から Output Integrated を読み、1.5LU以上ずれていたら表に出す。

★★クロスフェードの曲線は素材で使い分ける（2026年8月23日、雨で実測）。
  既定の `tri`（直線＝等ゲイン）は**相関のある音**向け。無相関の音を重ねると
  中点で理論値どおり -3dB 落ちる。**雨で実測すると継ぎ目が 2.8〜4.8dB へこんだ。**
  3時間で21回へこむので、睡眠用では致命的（起こしてしまう）。
  環境音では `xfade_curve: qsin`（四分正弦＝等パワー）にする。中点の合成が 0dB になる。
  **既定は `tri` のまま**。公開済みの巻を作り直したときに音が変わらないようにするため。

★`final_normalize: true` を書くと、連結したあとに全体をもう一度 -14 LUFS / TP に測り直す。
  環境音の巻では素材ごとの元ラウドネスが -20〜-42 と20LU以上ばらつき、
  連結後のトゥルーピークが目標を大きく超える（雨で実測 **-0.39dBTP**。目標は -1.5）。
  Vol.14 は AAC 段で 0.4dB 上がって -1.1 まで来ているので、この余裕は要る。
  **既定は false**。公開済みの巻の再現性を壊さないため（`ambient` を敷く巻は
  `_lay_ambient` の中で従来どおり測り直している）。

★`track_trim_edges` を書くと、各トラックの頭と尻をその割合だけ落としてから使う。
  配布されている環境音はたいてい端がフェードしていて、そのままループにすると
  周回ごとに音量の谷が来る（実測：レベル変動15.9dB → 端を1割落として0.9dB）。
  `vet` も同じ割合で落として測るので、検品した音とここで鳴る音が一致する。
  **曲では絶対に使わない**（頭と終わりを切り落とすことになる）。既定は0。

★`track_seconds` を書くと、各トラックを継ぎ目の聞こえないまま その秒数まで伸ばす。
  Vol.16（雨だけで3時間）のように、素材そのものが短い環境音で場面を埋める巻で使う。
  曲は必要な長さを持っているので、音楽の巻では書かない（書かなければ従来どおり）。

★環境音（`ambient`）を設定すると、連結後の music_bed.wav の上に1枚重ねる。
  濃さの基準は公開済みのVol.5「蛍の川」の実測で、**-18dB でVol.5と同じ**になる
  （4〜8kHz帯の変動係数が 0.52 で一致。詳細はメモリ vol1-has-no-nature-sounds）。
  素材は必ず**継ぎ目の無いループに作り直してから**敷く。9分の素材を60分に単純に
  繰り返すと、6回ある折り返しでプツッと切り替わるのが聞こえる。
"""
import os
import re

from .ffutil import (duration, ff, measure_loudness, mmss, pcm_mono, save_json,
                     silence_bounds)


def build(cfg, order):
    acfg = cfg["audio"]
    xf = acfg["crossfade"]
    src = cfg.tracks_dir
    out = cfg.wpath("norm")
    os.makedirs(out, exist_ok=True)

    # 1本ずつを揃える目標。既定は最終目標と同じ（音楽の巻は従来どおり）。
    tt = acfg.get("track_target_lufs", acfg["target_lufs"])
    tcfg = dict(acfg, target_lufs=tt)

    man, shortfalls = [], []
    for i, name in enumerate(order, 1):
        p = os.path.join(src, name)
        d = duration(p)
        h, t = silence_bounds(p, d, acfg)
        # ★端のフェードを落とす（環境音の巻だけ。既定0なので曲の巻は素通り）。
        edge = acfg.get("track_trim_edges", 0) or 0
        if edge:
            cut = min((t - h) * edge, acfg.get("track_trim_cap", 20.0))
            if (t - h) - 2 * cut > 4.0:
                h, t = h + cut, t - cut
        seg = t - h
        m = measure_loudness(p, tcfg, ss=h, t=seg)
        dst = os.path.join(out, f"{i:02d}.wav")
        ln = (f"loudnorm=I={tt}:TP={acfg['true_peak']}:LRA={acfg['lra']}"
              f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
              f":offset={m['target_offset']}:linear=true:print_format=summary")
        # loglevel="info" が要る。既定の warning では loudnorm の summary が出ず、
        # 目標に届いたかどうかを読み取れない（一度これで検査が空振りした）。
        r = ff(["-ss", f"{h}", "-t", f"{seg}", "-i", p, "-af", ln,
                "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", dst],
               loglevel="info")
        got = _achieved(r, tt)
        tgt = _target_len(cfg, i, len(order))
        if tgt:
            _extend(cfg, dst, tgt, acfg.get("track_loop_xfade", 4.0))
        od = duration(dst)
        man.append(dict(idx=i, name=name, dur=round(od, 3), in_i=m["input_i"]))
        grew = f" ←{seg:.0f}s を伸長" if tgt and seg < tgt - 0.5 else ""
        short = "" if got is None else f" ★{got:+.1f}LU 届いていない"
        if short:
            shortfalls.append((i, name, got))
        print(f"{i:02d} {name:38s} trim {h:5.2f}-{t:6.2f}  {od:7.2f}s  "
              f"in_I={m['input_i']:>6s} → {tt}{grew}{short}")

    curve = acfg.get("xfade_curve", "tri")
    ins, parts, prev = [], [], "[0:a]"
    for i in range(len(order)):
        ins += ["-i", os.path.join(out, f"{i + 1:02d}.wav")]
    for i in range(1, len(order)):
        tag = f"[a{i}]"
        parts.append(f"{prev}[{i}:a]acrossfade=d={xf}:c1={curve}:c2={curve}{tag}")
        prev = tag

    bed = cfg.wpath("music_bed.wav")
    ff([*ins, "-filter_complex", ";".join(parts), "-map", prev,
        "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", bed])

    if acfg.get("final_normalize"):
        bed = _renormalize(cfg, bed)

    total = duration(bed)
    starts, acc = [0.0], 0.0
    for e in man[:-1]:
        acc += e["dur"] - xf
        starts.append(round(acc, 3))
    for e, s in zip(man, starts):
        e["start"] = s
    save_json(cfg.wpath("manifest.json"),
              dict(tracks=man, total=round(total, 3), xf=xf))

    if shortfalls:
        print(f"\n★ {tt} LUFS に届いていないトラックがある。隣との段差になって聞こえる。")
        print("  ピークに対して平均が低い素材は、上げるとクリップするので上げきれない。")
        for i, name, d in shortfalls:
            print(f"  {i:02d} {name}  {d:+.1f} LU")
        print("  → 差し替えるのが早い。圧縮で持ち上げると音の性格が変わる。")

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


def _achieved(r, target, tol=1.5):
    """loudnorm 2パス目の summary から、実際に到達したラウドネスのずれを返す。

    届いていれば None。ピークに余裕が無い素材では Dynamic に落ちて届かないことがある。
    """
    m = re.search(r"Output Integrated:\s*(-?[\d.]+)", r.stderr or "")
    if not m:
        return None
    d = float(m.group(1)) - target
    return d if abs(d) > tol else None


def _renormalize(cfg, bed):
    """連結後の全体をもう一度 -14 LUFS / TP に測り直す。

    素材ごとの元ラウドネスが大きくばらつく環境音の巻で要る。個々のトラックを
    -14 に揃えても、クロスフェードで重なるぶんトゥルーピークが目標を超える。
    """
    acfg = cfg["audio"]
    m = measure_loudness(bed, acfg)
    ln = (f"loudnorm=I={acfg['target_lufs']}:TP={acfg['true_peak']}:LRA={acfg['lra']}"
          f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
          f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
          f":offset={m['target_offset']}:linear=true:print_format=summary")
    tmp = cfg.wpath("music_bed_norm.wav")
    ff(["-i", bed, "-af", ln, "-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le", tmp])
    os.replace(tmp, bed)
    print(f"\n連結後に測り直し: {m['input_i']} LUFS / TP {m['input_tp']} dBTP "
          f"→ {acfg['target_lufs']} / {acfg['true_peak']}")
    return bed


def _target_len(cfg, i, n):
    """i 番目（1始まり）のトラックを何秒にするか。書いていなければ None。

    スカラなら全トラック同じ長さ、リストなら曲順と1対1に対応する。
    """
    t = cfg.get("track_seconds")
    if not t:
        return None
    if isinstance(t, (int, float)):
        return float(t)
    if len(t) != n:
        raise SystemExit(f"track_seconds が {len(t)} 個ですが、トラックは {n} 本です。")
    return float(t[i - 1])


def _extend(cfg, path, target, xf):
    """素材を target 秒ちょうどに揃える（足りなければ継ぎ目なく伸ばす）。path を上書きする。

    ★単純な繰り返しでは折り返しが聞こえる。 いったん「終わりと頭が繋がるループ」に
      作り直してから敷き詰めるので、何周しても切り替わりが分からない。
    """
    L = duration(path)
    tmp = cfg.wpath("track_long.wav")
    pcm = ["-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le"]
    if L >= target:
        ff(["-i", path, "-t", f"{target}", *pcm, tmp])
    else:
        loop, _ = _seamless_loop(cfg, path, xf, cfg.wpath("track_loop.wav"))
        ff(["-stream_loop", "-1", "-i", loop, "-t", f"{target}", *pcm, tmp])
    os.replace(tmp, path)
    return path


def _seamless_loop(cfg, src, xf, out=None):
    """素材を「終わりと頭が繋がるループ」に作り直す。

    長さLの素材の末尾 xf 秒を、先頭 xf 秒の上にクロスフェードで重ねる。
    出来上がりは L-xf 秒で、その最後は素材の L-xf 地点、頭も同じ素材の
    L-xf 地点から始まるので、単純に繰り返しても折り返しが聞こえない。
    """
    L = duration(src)
    if L <= xf * 3:
        raise SystemExit(f"環境音の素材が短すぎます（{L:.1f}秒）。ループの重ね幅の3倍は要ります。")
    out = out or cfg.wpath("ambient_loop.wav")
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
