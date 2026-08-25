"""環境音の素材を検品する。

Vol.15（虫の音）では候補を1本ずつ手で測って `出典とライセンス.md` に書き留めていた。
Vol.16 は雨だけで3時間を組むため素材が18本必要になり、手作業では回らない。

  python3 -m bgmkit vet <ファイル…|フォルダ>

★★突発音は「粒」と「衝撃」に分けて見る（2026年8月22日、雨17本を実測して分けた）。
  中央値より 9〜18dB 大きいフレームは**軒の雨だれの粒**で、これは落としてはいけない
  （第二幕はそれが主題）。**18dB を超えるものだけが雷・扉・落下音**にあたる。
  分ける前は「雨樋の滴り」が突発音37.9%で不合格になっていた。中身は全部が滴なのだから当然で、
  虫の音（定常な地）で作った物差しをそのまま当てたのが誤りだった。
  実測では18dB超えを持つのは17本中2本だけで、境目はきれいに割れている。

★★「音程のあるもの」が混ざっていないかを見る（2026年8月22日、鳥入りの雨で追加）。
  Pixabayの `rain` には**鳥・虫・人声・音楽**が乗っている素材が普通に混ざる。
  粒の数だけでは水滴と鳥を区別できず、実際に鳥入りの1本を「軒の雨だれ向き」と推薦してしまった。
  **1.5〜8kHzのスペクトル平坦度が、最も音程的な瞬間に中央値の何分の1まで落ちるか**で見る。
  実測：鳥入り **45倍** ／ 雨だけの素材はどれも 1.7倍以内。境目は桁で開いている。
  ★絶対値では判定できない。 暗くこもった雨（`balkan-street-rain-echo`）は平坦度が
  通して0.06と低いが、これは高域が無いだけで音程ではない。**中央値との比で見ること。**

★★測る前に両端を落とす。 配布されている環境音はたいてい頭と尻がフェードしていて、
  そのまま測るとレベル変動が実態よりはるかに大きく出る（実測：15.9dB → 端を1割落として0.9dB）。
  ループにして3時間敷くので、どのみち端は使わない。`audio` 側も同じ割合で落とす
  （`audio.track_trim_edges`）ので、ここで測る音と実際に鳴る音が一致する。

★低域の足切りは 200Hz ではなく **120Hz未満**で見る。 交通のゴロゴロとマイクの吹かれは
  120Hz より下に居るが、雨そのものにも 120〜200Hz の胴回りがあり、200Hz で切ると
  健全な雨まで落ちる（ピンクノイズで試して分かった）。

★「こもり」は素材を三幕に割り振るための指標。 高域/低域のエネルギー比(dB)で、
  高いほど近くて開けた雨（石畳・傘）、低いほど遠い雨や屋内の雨になる。
  Vol.16 は幕が進むほど音がこもっていく設計なので、この順に並べる。
"""
import os
import subprocess
import sys

import numpy as np

from .ffutil import duration, run

SR = 22050
HOP = 0.25                       # レベルを測る窓（秒）
# ★2026年8月22日、雨17本で当て直した値。
#   var は 2.5（虫の音の実測1.4に合わせた値）では雨に厳しすぎた。端を落として測れば
#   良い素材は 0.8〜2.6 に収まり、4.0 を超えるのは滴りものと本当に波打つ素材だけになる。
LIMITS = dict(shock=0.0, var=4.0, low=20.0, dur=60.0, corr=0.95, tonal=4.0)
SHOCK_DB = 18.0          # これを超える突出＝雷・扉・落下音
GRAIN_DB = 9.0           # 9〜18dB は軒の雨だれの「粒」。落とさない
TONAL_BAND = (1500, 8000)
TRIM = 0.10              # 測る前に両端をこれだけ落とす
TRIM_CAP = 20.0          # ただし片側20秒まで
EXT = (".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".aiff", ".aif")


def _pcm_stereo(path):
    """ステレオf32でデコードして (2, N) を返す。"""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "2",
                        "-ar", str(SR), "-f", "f32le", "-"], capture_output=True)
    x = np.frombuffer(r.stdout, dtype=np.float32)
    return x.reshape(-1, 2).T if x.size else np.zeros((2, 0), np.float32)


def _bands(mono):
    """帯域ごとのエネルギー比(%)と、こもり具合(dB)を返す。"""
    n = 8192
    nf = max(1, len(mono) // n)
    S = np.zeros(n // 2 + 1)
    w = np.hanning(n)
    for i in range(nf):
        seg = mono[i * n:(i + 1) * n]
        if len(seg) < n:
            break
        S += np.abs(np.fft.rfft(seg * w)) ** 2
    f = np.fft.rfftfreq(n, 1 / SR)
    tot = S.sum() + 1e-30

    def share(lo, hi):
        return 100.0 * S[(f >= lo) & (f < hi)].sum() / tot

    def energy(lo, hi):
        return S[(f >= lo) & (f < hi)].sum() + 1e-30

    return dict(
        low=share(0, 120),
        b1=share(500, 1500), b2=share(1500, 3000),
        b3=share(3000, 5000), b4=share(5000, 8000),
        peak=float(f[np.argmax(S)]),
        # ★こもり具合。高いほど近くて開けた雨、低いほど遠い雨・屋内の雨。
        muffle=10 * np.log10(energy(2000, 8000) / energy(200, 800)),
    )


def _tonal(mono, off):
    """音程のあるものが混ざっていないか。中央値と「最も音程的な瞬間」の比で返す。"""
    n, hop = 2048, 1024
    f = np.fft.rfftfreq(n, 1 / SR)
    ok = (f > TONAL_BAND[0]) & (f < TONAL_BAND[1])
    w = np.hanning(n)
    nf = (len(mono) - n) // hop
    if nf < 12:
        return dict(tonal=1.0, tonal_at=[])
    idx = range(0, nf, 3)
    fl = np.array([_flat(np.abs(np.fft.rfft(mono[i * hop:i * hop + n] * w)) ** 2, ok)
                   for i in idx])
    med = float(np.median(fl))
    lo = float(np.percentile(fl, 5))
    worst = np.argsort(fl)[:6]
    return dict(
        tonal=med / max(lo, 1e-9),
        tonal_at=sorted(round(off + list(idx)[i] * hop / SR, 1) for i in worst),
    )


def _flat(power, ok):
    b = power[ok] + 1e-20
    return float(np.exp(np.log(b).mean()) / b.mean())


def _levels(mono, off):
    """フレームごとのRMS(dB)から、変動・粒・衝撃・欠落を出す。

    off は端を落とした秒数。表示する時刻を元ファイルの時刻に戻すために使う。
    """
    n = int(SR * HOP)
    nf = len(mono) // n
    if nf < 4:
        return dict(var=99.0, grain=0.0, shock=100.0, shock_at=[], gap=100.0)
    rms = np.sqrt((mono[:nf * n].reshape(nf, n) ** 2).mean(axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    ex = db - np.median(db)
    shock = np.flatnonzero(ex > SHOCK_DB)
    return dict(
        var=float(db.std()),
        # 9〜18dB＝軒の雨だれの粒。落とさずに出すだけ
        grain=100.0 * float(((ex > GRAIN_DB) & (ex <= SHOCK_DB)).mean()),
        shock=100.0 * len(shock) / nf,
        # ★どこで鳴っているかを出す。合否だけでは聴きに行けない
        shock_at=[round(off + i * HOP, 1) for i in shock[:6]],
        # 中央値より25dB以上小さいフレーム＝途中で切れている（端のフェードは落とし済み）
        gap=100.0 * float((ex < -25).mean()),
    )


def measure(path):
    x = _pcm_stereo(path)
    if x.shape[1] < SR:
        raise ValueError("デコードできないか短すぎます")
    d = dict(name=os.path.basename(path), path=path, dur=duration(path))

    # ★端のフェードを落としてから測る。audio 側も同じ割合で落とすので実際に鳴る音と一致する。
    cut = int(min(x.shape[1] * TRIM, TRIM_CAP * SR))
    if x.shape[1] - 2 * cut > SR * 4:
        head = x[:, :cut].mean(axis=0)
        body = x[:, cut:x.shape[1] - cut]
        d["faded"] = bool(len(head) and
                          head.std() < body.mean(axis=0).std() * 0.6)
        x = body
    d["trim"] = round(cut / SR, 1)
    mono = x.mean(axis=0)
    d.update(_levels(mono, d["trim"]))
    d.update(_tonal(mono, d["trim"]))
    d.update(_bands(mono))
    l, r = x[0], x[1]
    d["corr"] = float(abs(np.corrcoef(l, r)[0, 1])) if l.std() and r.std() else 1.0
    d["clip"] = 100.0 * float((np.abs(mono) >= 0.999).mean())
    return d


def _verdict(d):
    """落ちた理由を並べて返す。空なら合格。"""
    bad = []
    if d["shock"] > LIMITS["shock"]:
        at = "・".join(f"{t:.0f}s" for t in d["shock_at"])
        bad.append(f"衝撃音{d['shock']:.1f}%（{at} を聴く）")
    if d["var"] > LIMITS["var"]:
        bad.append(f"レベル変動{d['var']:.1f}dB")
    if d["low"] > LIMITS["low"]:
        bad.append(f"120Hz未満{d['low']:.0f}%（交通・吹かれ）")
    if d["dur"] < LIMITS["dur"]:
        bad.append(f"尺{d['dur']:.0f}秒")
    if d["tonal"] > LIMITS["tonal"]:
        at = "・".join(f"{t:.0f}s" for t in d["tonal_at"][:4])
        bad.append(f"音程あり{d['tonal']:.0f}倍（鳥・虫・人声・音楽。{at} を聴く）")
    if d["corr"] > LIMITS["corr"]:
        bad.append(f"左右相関{d['corr']:.2f}（実質モノラル）")
    if d["gap"] > 0.5:
        bad.append(f"途中で欠落{d['gap']:.1f}%")
    if d["clip"] > 0.01:
        bad.append(f"クリップ{d['clip']:.2f}%")
    return bad


def _collect(paths):
    out = []
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.isdir(p):
            out += [os.path.join(p, f) for f in sorted(os.listdir(p))
                    if f.lower().endswith(EXT) and not f.startswith(".")]
        elif os.path.exists(p):
            out.append(p)
        else:
            sys.stderr.write(f"見つかりません: {p}\n")
    return out


def run_vet(paths):
    files = _collect(paths)
    if not files:
        raise SystemExit("検品するファイルがありません。")

    rows = []
    for p in files:
        try:
            rows.append(measure(p))
        except Exception as e:                                   # noqa: BLE001
            sys.stderr.write(f"読めません {os.path.basename(p)}: {e}\n")

    # こもりの大きい順＝近くて開けた雨が上。三幕への割り振りはこの順で読む。
    rows.sort(key=lambda d: -d["muffle"])

    print(f"\n{'素材':38s} {'尺':>7s} {'変動':>5s} {'粒':>5s} {'衝撃':>5s} {'<120':>5s} "
          f"{'L/R':>5s} {'音程':>5s} {'こもり':>6s}  判定")
    print("-" * 120)
    ok = []
    for d in rows:
        bad = _verdict(d)
        name = d["name"][:37]
        print(f"{name:38s} {d['dur']:6.0f}s {d['var']:5.1f} {d['grain']:4.1f}% "
              f"{d['shock']:4.1f}% {d['low']:4.0f}% {d['corr']:5.2f} "
              f"{d['tonal']:4.1f}x {d['muffle']:+6.1f}  "
              + ("合格" if not bad else "／".join(bad)))
        if not bad:
            ok.append(d)

    faded = [d for d in rows if d.get("faded")]
    print(f"\n合格 {len(ok)} / {len(rows)} 本"
          + (f"　※両端を{TRIM:.0%}落として測っている"
             f"（{len(faded)}本は端がフェードしていた）" if faded else ""))
    grainy = [d for d in ok if d["grain"] > 1.0]
    if grainy:
        print("「粒」が立っている＝軒の雨だれ向き： "
              + "／".join(d["name"][:24] for d in grainy))
    if ok:
        print("\n帯域の内訳（%）  ※三幕への割り振りはこもりの順に読む")
        print(f"{'素材':38s} {'0.5-1.5k':>9s} {'1.5-3k':>8s} {'3-5k':>7s} {'5-8k':>7s}")
        for d in ok:
            print(f"{d['name'][:37]:38s} {d['b1']:8.1f}% {d['b2']:7.1f}% "
                  f"{d['b3']:6.1f}% {d['b4']:6.1f}%")
        print("\nこもりが大きい（＝近くて開けた雨）ほど上。第一幕から順に当てる。")
    return ok
