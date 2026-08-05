"""確定した曲順から音声トラックを組む。

旧 prep_audio*.py。曲ごとに
  頭尾の無音をトリム → loudnorm 2パスで -14 LUFS に統一 → クロスフェードで連結。

ラウドネスの統一は必須。Sunoの生成物は曲ごとに -13〜-16 LUFS と3LUほど開いていて、
そのまま並べると曲が変わるたびに音量が動く。
"""
import os

from .ffutil import duration, ff, measure_loudness, mmss, save_json, silence_bounds


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
    return bed
