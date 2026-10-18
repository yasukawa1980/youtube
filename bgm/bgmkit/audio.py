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
  ★`ambient.no_loop: true` を書くとループ化しない。**素材が最初から全長ぶんあって、
  しかも時間とともに変化している**場合（Waves of Japan のビート層）に使う。
  ループ化は末尾を先頭に重ねる処理なので、そういう素材では頭と尻が混ざって壊れる。
"""
import math
import os
import random
import re
import shutil
import subprocess

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
        tgt = _target_len(cfg, i, len(order))
        if isinstance(name, (list, tuple)):
            # ★曲順の1項目が「複数の素材」なら、その場面はモザイクで組む。
            if not tgt:
                raise SystemExit(
                    f"{i:02d} 番はモザイク指定だが track_seconds が無い。"
                    "何秒に敷き詰めるか決まらないと組めない。")
            p = _mosaic(cfg, list(name), tgt, acfg, tt, i)
            d = duration(p)
            # 片ごとに揃えて継いであるので、無音検出も端落としも掛けない。
            h, t = 0.0, d
            name = "＋".join(os.path.splitext(x)[0][:12] for x in name)[:37]
        else:
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


def _corr(path):
    """左右の相関。1.00に近いほど実質モノラル。"""
    import numpy as np
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2",
                        "-ar", "8000", "-f", "f32le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, dtype=np.float32)
    if x.size < 16000:
        return 1.0
    l, r_ = x.reshape(-1, 2).T
    # ★ここは相関だけを見るので8kHzで足りる（帯域の中身は測っていない）。
    return float(abs(np.corrcoef(l, r_)[0, 1])) if l.std() and r_.std() else 1.0


def _mosaic(cfg, names, target, acfg, tt, tag):
    """複数の短尺素材から、1場面ぶんの床を継ぎ合わせて作る。

    ★★1本を繰り返すと折り返しが聞こえる題材のための敷き方（2026年8月25日、蝉の巻で追加）。
      雨は音程も位相も持たないので、1本を8分ループしても誰にも分からなかった。
      蝉は違う。個々の鳴き声が聞き分けられるので、同じ30秒が16回来れば必ず気づかれる。
      無料ストックに日本の蝉の長尺が存在しないことが分かったので、
      **短い素材を何本かまとめて渡し、順を変えた「片」を継いでいく**形にした。

    ★★1片ごとに 速さ・左右・音量 を散らす。 これが要。順を変えるだけでは、
      同じ素材が再び来たときに「さっきのあれ」と分かってしまう。
        速さ ±3%  … 虫の音では音程の違いに聞こえない（個体差の範囲に収まる）。
                    素材の自己相関を完全に崩すので、重ねても櫛形の干渉が出ない。
        左右入替  … 全く聞こえないのに、ステレオ像だけが入れ替わる。最も安いごまかし。
        音量 ±dB  … 遠近が動いたように聞こえる。合唱は元々ゆっくり上下している。

    ★片の長さもばらす（既定40〜70秒）。 固定だと切り替わりが等間隔に来て、
      それ自体が拍になって聞こえる。

    ★素材は先に1本ずつ tt へ揃え、継ぎ目の無いループに作り直してから片にする。
      揃えずに継ぐと片が変わるたびに音量が動く（それは折り返しより目立つ）。

    ★★1片は1本ではなく2〜3本を**重ねる**（2026年8月25日、蝉の実素材16本を見て変更）。
      横に並べるだけでは、素材1本ずつの弱点がそのまま床に出る。実素材はこうだった：
        ・16本中9本が実質モノラル（L/R 1.00）。効果音サイトの素材なので当然
        ・単独個体の録音は音量が7〜9dB振れる（鳴き始めと鳴き終わりがそのまま出る）
        ・全部で8.7分しかない。3時間だと同じ音を20回聴かせることになる
      重ねると4つとも同時に解ける：
        ・**モノラルが広がる**。同じ素材でも速さを0.6%ずらして左右に振れば別個体に聞こえる
          （実際の合唱は個体ごとに音程が違う。物理的にも正しい）
        ・**振れが均される**。1本が鳴き止んでも他が鳴いている
        ・**組み合わせが爆発する**。16本から2本選ぶだけで120通り、ずらし位置を含めれば無限
        ・**単独個体の効果音が「森」になる**。1本では素材、重ねると情景
      ★重ねてよいのは蝉どうしだけ。 シリーズの約束は「一つの音だけ」なので、
        蝉に別の音を足すのは禁じ手。同じ幕の中の蝉を重ねるのは合唱そのもの。
      ★幕をまたいで重ねないこと。 三幕は種の移ろいで作るので、
        明け方のヒグラシに真昼のアブラゼミを重ねると設計が壊れる。
        重なる範囲は order_tracks の1項目に何を並べるかで決まる（＝人が決める）。
    """
    src = cfg.tracks_dir
    m = acfg.get("mosaic") or {}
    lo, hi = m.get("cell", [40.0, 70.0])
    rates = m.get("rates", [0.97, 0.985, 1.0, 1.015, 1.03])
    gdb = float(m.get("gain_db", 0.7))
    swap = m.get("swap_lr", True)
    # ★既定を2本以上にしてある。 1本だと実質モノラルの素材が中央の点になってしまう。
    lay_lo, lay_hi = m.get("layers", [2, 3])
    detune = float(m.get("detune", 0.006))   # 重ねる同士の速さの差＝個体差
    spread = float(m.get("spread", 0.7))     # 左右にどこまで振るか
    xf = float(m.get("xfade", acfg.get("track_loop_xfade", 4.0)))
    # ★種は場面ごとに変える。 全場面が同じ並びだと、場面をまたいだ繰り返しが出る。
    rng = random.Random(int(m.get("seed", 1)) * 1000 + tag)

    work = cfg.wpath(f"mosaic/{tag:02d}")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    pcm = ["-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le"]
    tcfg = dict(acfg, target_lufs=tt)

    loops, pens, lras = [], [], []
    for k, n in enumerate(names):
        sp = os.path.join(src, n)
        d = duration(sp)
        h, t = silence_bounds(sp, d, acfg)
        edge = acfg.get("track_trim_edges", 0) or 0
        if edge:
            cut = min((t - h) * edge, acfg.get("track_trim_cap", 20.0))
            if (t - h) - 2 * cut > 4.0:
                h, t = h + cut, t - cut
        seg = t - h
        # ★重ね幅は素材ごとに決める（2026年8月25日）。 効果音サイトの素材には
        #   10秒前後のものが普通にあり、固定4秒だとループが作れずに止まる。
        #   短い素材は重ね幅も詰めてよい。どうせ単独で床にはせず、
        #   合唱の中の1個体として他の層に埋もれる使い方になる。
        xfc = min(xf, seg / 4.0)
        if seg <= 2.0:
            raise SystemExit(f"{n} は使えるところが {seg:.1f}秒しかない。短すぎる。")
        if xfc < xf:
            print(f"   {n} は {seg:.0f}秒。ループの重ね幅を {xfc:.1f}秒に詰めた")
        # ★1片の中で素材が何周するか。 短い素材ほど片の中の繰り返しが聞こえる。
        if seg < lo:
            print(f"   ★{n} は {seg:.0f}秒。1片({lo:.0f}〜{hi:.0f}秒)の中で"
                  f"最大{hi / seg:.1f}周する。近い繰り返しは散らしても隠れない")
        lv = os.path.join(work, f"src{k:02d}.wav")
        mm = measure_loudness(sp, tcfg, ss=h, t=seg)
        ff(["-ss", f"{h}", "-t", f"{seg}", "-i", sp, "-af",
            f"loudnorm=I={tt}:TP={acfg['true_peak']}:LRA={acfg['lra']}"
            f":measured_I={mm['input_i']}:measured_TP={mm['input_tp']}"
            f":measured_LRA={mm['input_lra']}:measured_thresh={mm['input_thresh']}"
            f":offset={mm['target_offset']}:linear=true", *pcm, lv])
        # ★★振れの大きい素材は層として下げる（2026年8月25日、蝉の実素材で判明）。
        #   単独個体の効果音は鳴き始めと鳴き終わりがそのまま入っていて、
        #   実測で 7〜10dB 振れる。これを対等な層として重ねると床全体がうねる
        #   （5本重ねの実測で 0.8dB → 4.7dB に悪化した）。
        #   かといって捨てると素材が足りない。**遠くの一匹として小さく入れる**のが正解で、
        #   これは情景としても正しい（近くで1匹だけ大きく鳴くほうが不自然）。
        #   振れの目安は loudnorm が既に測っている LRA を使う（測り直しは要らない）。
        try:
            lra = float(mm["input_lra"])
        except (TypeError, ValueError):
            lra = 0.0
        # accent_db を 0 にすると減衰しない（効いているかを確かめるためのつまみ）
        pen = -min(float(m.get("accent_db", 6.0)), max(0.0, lra - 3.0))
        if pen < -0.05:
            print(f"   {n} は LRA {lra:.1f}。層として {pen:.1f}dB 下げる（遠くの一匹にする）")
        pens.append(pen)
        lras.append(lra)
        # ★★実質モノラルの素材を「床」に使うと、場面全体のステレオ像が狭くなる
        #   （2026年8月25日、蝉の午後で実測）。重ねれば広がるとはいえ、それは
        #   点景（-6dB）の話。床は全重量で鳴り続けるので像を引き締めてしまう。
        #   実測：モノラル1本を床に含む3本版 L/R 0.27〜0.49、外した2本版 0.07〜0.09。
        #   ★捨てろという意味ではない。 素材が少ないときは繰り返しのほうが害が大きい
        #   （2本版は自己相関 0.079→0.102 と少し悪化した）。天秤に掛けるための警告。
        if lra <= float(m.get("bed_lra", 6.0)) and _corr(lv) > 0.95:
            print(f"   ★{n} は実質モノラルなのに床に使われる。"
                  f"場面全体のステレオ像が狭くなる")
        # _seamless_loop は (パス, 長さ) を返す。パスだけ使う。
        lp, _ = _seamless_loop(cfg, lv, xfc, os.path.join(work, f"loop{k:02d}.wav"))
        loops.append(lp)

    lens = [duration(l) for l in loops]
    # ★★片には必ず「床」を入れる（2026年8月25日、実測で追い込んだ）。
    #   層を下げるだけでは足りなかった。振れの大きい素材どうしが同じ片に入ると、
    #   片ごとのラウドネス合わせが**その揺れごと持ち上げる**ので、
    #   15秒ならしても 3.7dB のうねりが残る（睡眠用では通せない値）。
    #   LRA の小さい素材＝定常な地を床とし、振れる素材はその上の点景に限る。
    bed = [x for x in range(len(loops)) if lras[x] <= float(m.get("bed_lra", 6.0))]
    acc_only = [x for x in range(len(loops)) if x not in bed]
    if not bed:
        raise SystemExit(
            "床にできる素材が1本も無い（全部 LRA が大きい＝鳴き始めと鳴き終わりが"
            "そのまま入っている）。定常に鳴き続けている録音が最低1本要る。")
    if acc_only:
        print(f"   床 {len(bed)}本 / 点景 {len(acc_only)}本"
              f"（点景は必ず床の上にだけ乗せる）")

    lens_ = lens
    cells, acc, prev = [], 0.0, []
    while acc < target + hi:
        cell = rng.uniform(lo, hi)
        k = min(rng.randint(lay_lo, lay_hi), max(1, len(loops)))
        # ★床を先に取る。 残りの枠にだけ点景を混ぜる。
        bpool = [x for x in bed if x not in prev] or bed
        nbed = max(1, k - 1) if acc_only else k
        pick = rng.sample(bpool, min(nbed, len(bpool)))
        while len(pick) < nbed:
            pick.append(rng.choice(bed))
        rest = [x for x in (acc_only or bed) if x not in pick]
        while len(pick) < k:
            pick.append(rng.choice(rest or (acc_only or bed)))
        rng.shuffle(pick)
        prev = pick[:]

        ins, chains, tags = [], [], []
        # 無相関な音を k 本重ねると出力は 10log10(k) dB 上がる。そのぶん下げておく。
        base = -10.0 * math.log10(k)
        for q, j in enumerate(pick):
            ins += ["-stream_loop", "-1", "-i", loops[j]]
            # ★重ねる同士は必ず速さをずらす。 同じ素材を同じ速さで重ねると
            #   ただ音量が上がるだけで、個体が増えたようには聞こえない。
            rate = rng.choice(rates) * (1.0 + detune * (q - (k - 1) / 2.0))
            # ★開始位置もずらす。 ループは継ぎ目が無いので、どこから始めてもよい。
            off = rng.uniform(0, max(0.1, lens[j] - 0.1))
            # 左右の定位を k 本で振り分ける（等パワー）
            pos = 0.0 if k == 1 else spread * (2.0 * q / (k - 1) - 1.0)
            la = math.sqrt(max(0.0, 1.0 - pos)) 
            ra = math.sqrt(max(0.0, 1.0 + pos))
            if swap and rng.random() < 0.5:
                la, ra = ra, la
            g = base + pens[j] + rng.uniform(-gdb, gdb)
            # ★引数の tag（場面番号）を踏まないこと。 ltag は層のラベル。
            ltag = f"[l{q}]"
            chains.append(
                f"[{q}:a]atrim=start={off:.3f},asetpts=N/SR/TB,"
                f"asetrate=48000*{rate:.5f},aresample=48000,"
                f"pan=stereo|c0={la:.4f}*c0|c1={ra:.4f}*c1,"
                f"volume={g:.2f}dB{ltag}")
            tags.append(ltag)
        if k == 1:
            chains.append(f"{tags[0]}anull[o]")
        else:
            chains.append(f"{''.join(tags)}amix=inputs={k}"
                          f":duration=longest:normalize=0[o]")
        cp = os.path.join(work, f"cell{len(cells):03d}.wav")
        # ★-t は出力側に置く。 入力側だと asetrate で伸び縮みする前の長さで切れる。
        ff([*ins, "-filter_complex", ";".join(chains), "-map", "[o]",
            "-t", f"{cell}", *pcm, cp])
        # ★★片ごとにラウドネスを揃える（2026年8月25日）。
        #   本数で割るだけでは揃わない。片ごとに顔ぶれが違うので、
        #   静かな素材2本の片と賑やかな素材3本の片で高さが変わり、
        #   それが切り替わるたびの段差になる（実測4.7dB）。
        #   ★リミッタは使わずゲインだけで合わせる。 この形式は「うねりを平らにしない」
        #     ことが値打ちなので、片ごとに圧縮を掛けたら意味が無くなる。
        cm = measure_loudness(cp, tcfg) if m.get("level_cells", True) else None
        try:
            gain = max(-9.0, min(9.0, tt - float(cm["input_i"]))) if cm else 0.0
        except (TypeError, ValueError):
            gain = 0.0
        if abs(gain) > 0.05:
            fx = cp + ".lv.wav"
            ff(["-i", cp, "-af", f"volume={gain:.2f}dB", *pcm, fx])
            os.replace(fx, cp)
        cells.append(cp)
        acc += cell - xf

    out = cfg.wpath(f"mosaic_{tag:02d}.wav")
    if len(cells) == 1:
        shutil.copyfile(cells[0], out)
    else:
        ins, parts, prevtag = [], [], "[0:a]"
        for c in cells:
            ins += ["-i", c]
        for k in range(1, len(cells)):
            tg = f"[m{k}]"
            parts.append(f"{prevtag}[{k}:a]acrossfade=d={xf}"
                         f":c1={acfg.get('xfade_curve', 'tri')}"
                         f":c2={acfg.get('xfade_curve', 'tri')}{tg}")
            prevtag = tg
        ff([*ins, "-filter_complex", ";".join(parts), "-map", prevtag,
            "-t", f"{target}", *pcm, out])
    # 片は1場面で数百MBになる。使い終わったら消す（3時間だと全場面で数GB）。
    shutil.rmtree(work, ignore_errors=True)
    print(f"   モザイク {len(cells)}片（{lay_lo}〜{lay_hi}重ね） / 素材{len(names)}本 "
          f"→ {duration(out):.1f}s")
    return out


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


def _sprinkle(cfg, spec, total):
    """短い音を、間隔を空けてまばらに置いた層を作る（風鈴の打音など）。

    ★★「敷く」ではなく「点で置く」ための仕組み（2026年8月26日、風鈴で必要になった）。
      雨・蝉・虫は通して鳴り続けるので `_seamless_loop` で敷けばよかった。
      **風鈴は風が吹いたときだけ鳴る間欠音**で、実際の縁側では数十秒の沈黙をはさむ。
      敷くと鳴りっぱなしになり、53分では消耗する。

    ★実測がそれを裏づけた。 落とした長尺2本（155秒・60秒）は打音の間隔の
      **76〜85%が0.5秒未満**、最大でも3秒だった。強い風で鳴り続けている録音で、
      「風が来ては去る縁側」ではない。**使わない。**
      代わりに短尺5本（5.7〜6.8秒・孤立した打音・地が-61〜-74dB）を点として置く。

    ★1打ごとに 左右・速さ・音量 を散らす。 素材が4本ともモノラルなので、
      振らないと全部が同じ位置で鳴る。速さは±1.5%（風鈴は個体で音程が違うので自然）。
    """
    files = [os.path.expanduser(f) for f in spec["files"]]
    for f in files:
        if not os.path.exists(f):
            raise SystemExit(f"風鈴の素材が見つかりません: {f}")
    lo, hi = spec.get("every", [25.0, 70.0])
    spread = float(spec.get("spread", 0.6))
    rates = spec.get("rates", [0.985, 0.995, 1.0, 1.005, 1.015])
    gdb = float(spec.get("gain_jitter_db", 2.0))
    rng = random.Random(int(spec.get("seed", 1)))

    work = cfg.wpath("sprinkle")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    pcm = ["-ar", "48000", "-ac", "2", "-c:a", "pcm_s24le"]

    parts, t, k, prev = [], 0.0, 0, -1
    while t < total:
        gap = rng.uniform(lo, hi)
        pool = [x for x in range(len(files)) if x != prev] or [0]
        j = rng.choice(pool)
        prev = j
        pos = rng.uniform(-spread, spread)
        la, ra = math.sqrt(max(0.0, 1.0 - pos)), math.sqrt(max(0.0, 1.0 + pos))
        rate = rng.choice(rates)
        af = [f"asetrate=48000*{rate:.4f}", "aresample=48000",
              f"pan=stereo|c0={la:.4f}*c0|c1={ra:.4f}*c1",
              f"volume={rng.uniform(-gdb, gdb):.2f}dB"]
        g = os.path.join(work, f"g{k:04d}.wav")
        c = os.path.join(work, f"c{k:04d}.wav")
        # 沈黙 → 打音 の順に並べ、あとで一本に繋ぐ
        ff(["-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo", "-t", f"{gap:.3f}", *pcm, g])
        ff(["-i", files[j], "-af", ",".join(af), *pcm, c])
        parts += [g, c]
        t += gap + duration(c)
        k += 1

    lst = os.path.join(work, "list.txt")
    with open(lst, "w") as fh:
        for p_ in parts:
            fh.write("file '" + p_.replace("'", "'\\''") + "'\n")
    out = cfg.wpath("ambient_sprinkle.wav")
    ff(["-f", "concat", "-safe", "0", "-i", lst, "-t", f"{total}", *pcm, out])
    print(f"風鈴 {k}打 / {total / 60:.0f}分（平均 {total / max(k, 1):.0f}秒に1回）"
          f" 素材{len(files)}本")
    return out


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

    # ★★`no_loop` を書いた巻はループ化しない。
    #   `_seamless_loop` は末尾を先頭の上に重ねる処理なので、**素材が最初から
    #   全長ぶんあって、しかも時間とともに変化している**場合には壊れる。
    #   Waves of Japan のビート層（3時間かけて うなり が 12Hz→8Hz へ落ちる）に掛けると
    #   尻の8Hzが頭の12Hzに重なり、さらに出来上がりが total-xf に縮むので
    #   末尾に頭の12Hzが戻ってくる。3時間ぶんのループ化に数分かかる無駄も省ける。
    if amb.get("no_loop"):
        loop_len = duration(src)
        if loop_len < total:
            raise SystemExit(
                f"no_loop の環境音が本編より短いです（{loop_len:.1f}秒 < {total:.1f}秒）。"
                "全長ぶん用意するか no_loop を外してください。")
        loop = src
    else:
        loop, loop_len = _seamless_loop(cfg, src, amb.get("loop_xfade", 4.0))
    duck = amb.get("duck_db")
    how = (f"{gain}dB 通し" if not duck else
           f"底{gain + duck}dB → 変わり目{len(seams)}箇所で{gain}dB "
           f"（山の全幅{amb.get('swell', 12.0):g}秒）")
    if amb.get("no_loop"):
        print(f"\n環境音 {os.path.basename(src)} → ループ化せず全長 {loop_len:.1f}秒 "
              f"をそのまま使う / {how}")
    else:
        print(f"\n環境音 {os.path.basename(src)} → ループ {loop_len:.1f}秒 × "
              f"{total / loop_len:.1f}回 / {how}")

    # ★★点で置く層（風鈴など）。 書かなければ従来どおり地の1枚だけ。
    spec = amb.get("sprinkle")
    spr = _sprinkle(cfg, spec, total) if spec else None

    mixed = cfg.wpath("music_bed_ambient.wav")
    fc = (f"[0:a]atrim=0:{total},asetpts=N/SR/TB,{_env(amb, gain, seams)},"
          f"afade=t=in:d={fi},afade=t=out:st={total - fo}:d={fo}[amb];")
    ins = ["-stream_loop", "-1", "-i", loop, "-i", dry]
    if spr:
        sg = float(spec.get("gain_db", -12.0))
        ins += ["-i", spr]
        fc += (f"[2:a]volume={sg}dB,afade=t=in:d={fi},"
               f"afade=t=out:st={total - fo}:d={fo}[spr];"
               f"[1:a][amb][spr]amix=inputs=3:duration=first:normalize=0[o]")
    else:
        fc += "[1:a][amb]amix=inputs=2:duration=first:normalize=0[o]"
    ff([*ins, "-filter_complex", fc, "-map", "[o]",
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
