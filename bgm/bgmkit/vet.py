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

# ★★虫・蝉の巻では「音程あり」で落としてはいけない（2026年8月25日、SOJ02の準備で判明）。
#   雨にとって音程は不純物の証拠だが、この題材では**音程そのものが主題**。
#   手元の虫3本を雨の物差しで測ると 2.0倍 / 4.0倍 / 7.2倍 で、合格線4.0倍では
#   まともな素材まで落ちる。→ `--insect` では音程での足切りをやめ、
#   代わりに種を見分けるための指紋（脈・主帯・響き・山の動き）を測って出す。
#
# ★★合否には使わない。 memo にある見分けの目印（ヒグラシ=毎秒10〜15回の脈／
#   ミンミン=3〜4Hz／ツクツクボウシ=加速する句／アブラ=脈なし）を数字にしただけで、
#   最後は耳で決める。数字は「15本を聴く順番を決める」ために使う。
INSECT_BAND = (2000, 9000)   # 日本の蝉が鳴く帯
INSECT_CAP = 240.0           # 指紋は先頭4分だけ見る（25分の素材で待たされないため）
MOD_BAND = (2.0, 25.0)       # 脈として読む範囲（Hz）
# ★変動の上限は雨の4.0では厳しい可能性がある。蝉の合唱は雨より波打つ。
#   ★★この 6.0 は仮の値。 雨で 2.5→4.0 に当て直したのと同じことを、
#     実素材を10本以上測ってから必ずやり直すこと。
INSECT_VAR = 6.0
# ★尺の下限は雨の60秒ではなくモザイクの成立条件で決まる（2026年8月25日）。
#   継ぎ目の無いループを作るのに重ね幅の3倍（4.0秒×3＝12秒）が要る。それが物理的な下限。
#   ただし「片」より短い素材は片の中で何周もするので、12秒を通ったから使えるという意味ではない。
#   そこは audio 側の `_mosaic` が周回数を警告に出す。ここは**測って並べるための下限**。
INSECT_DUR = 12.0

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


def _insect(mono, off):
    """蝉・虫の指紋を返す。脈(Hz)・脈の強さ・主帯(Hz)・響き・山の動き。

    脈       … 振幅の揺れをもう一度フーリエに掛けて出す。種ごとに違う。
    脈の強さ … その山が地面より何倍高いか。アブラゼミのような連続音は小さい。
    主帯     … 2〜9kHz でいちばんエネルギーのある周波数。
    響き     … 主帯の中の平坦度。低いほど「カナカナ」の鳴り、高いほど「ジー」の雑音。
    山の動き … 最も強い山の周波数が時間でどれだけ動くか(Hz)。
               ★これが鳥・人声の見張り役。 蝉の山は動かないが、鳥はうねる。
               音程の足切りを外した穴をここで埋めている。
    """
    n, hop = 1024, 256
    if len(mono) > int(SR * INSECT_CAP):
        mono = mono[:int(SR * INSECT_CAP)]
    nf = (len(mono) - n) // hop
    if nf < 200:
        return dict(pulse=0.0, pulse_str=0.0, carrier=0.0,
                    ring=1.0, wander=0.0, wander_at=[])

    f = np.fft.rfftfreq(n, 1 / SR)
    band = (f >= INSECT_BAND[0]) & (f < INSECT_BAND[1])
    hi = (f >= 1500) & (f < 9000)
    fh = f[hi]
    w = np.hanning(n).astype(np.float32)
    sw = np.lib.stride_tricks.sliding_window_view(mono, n)
    idx = np.arange(nf) * hop

    # ★まとめてFFTすると4分でも数百MB積む。2048フレームずつ畳んで必要な3つだけ残す。
    env = np.empty(nf)          # 帯のエネルギーの時間変化
    pk = np.empty(nf)           # そのフレームで最も強い山の周波数
    mean = np.zeros(n // 2 + 1)
    for a in range(0, nf, 2048):
        b = min(a + 2048, nf)
        P = np.abs(np.fft.rfft(sw[idx[a:b]] * w, axis=1)) ** 2
        mean += P.sum(axis=0)
        env[a:b] = P[:, band].sum(axis=1)
        pk[a:b] = fh[np.argmax(P[:, hi], axis=1)]
    mean /= nf

    carrier = float(f[band][np.argmax(mean[band])])
    ring = _flat(mean, band)

    # 脈：帯のエネルギーの時間変化を8秒窓でフーリエに掛け、2〜25Hzの山を拾う
    fs = SR / hop
    win = int(min(fs * 8, nf))
    ww = np.hanning(win)
    acc, cnt = None, 0
    for i in range(0, nf - win + 1, max(1, win // 2)):
        seg = env[i:i + win]
        seg = seg / (seg.mean() + 1e-30) - 1.0
        S = np.abs(np.fft.rfft(seg * ww)) ** 2
        acc = S if acc is None else acc + S
        cnt += 1
    mf = np.fft.rfftfreq(win, 1 / fs)
    ok = (mf >= MOD_BAND[0]) & (mf <= MOD_BAND[1])
    # ★★argmax では駄目。 揺れの成分は 1/f の右下がりを持つので、山が無い素材でも
    #   必ず下端(2.0Hz)が最大になり、アブラゼミが「ミンミン」に化ける（実測で確認）。
    #   **両隣より高い点＝本物の山**だけを候補にする。1つも無ければ「脈なし」。
    pulse, pstr = 0.0, 0.0
    if cnt and ok.sum() >= 3:
        S = acc[ok]
        fq = mf[ok]
        top = np.flatnonzero((S[1:-1] > S[:-2]) & (S[1:-1] > S[2:])) + 1
        if len(top):
            k = int(top[np.argmax(S[top])])
            pulse = float(fq[k])
            pstr = float(S[k] / (np.median(S) + 1e-30))

    # 山の動き：静かなフレームは雑音で山が飛ぶので、鳴っている側だけで見る
    loud = env > np.median(env)
    p = pk[loud] if loud.any() else pk
    med = float(np.median(p))
    far = np.argsort(-np.abs(pk - med))[:6]
    return dict(
        pulse=pulse, pulse_str=pstr, carrier=carrier, ring=ring,
        wander=float(np.percentile(p, 90) - np.percentile(p, 10)),
        wander_at=sorted(round(off + int(i) * hop / SR, 1) for i in far),
    )


def _guess(d):
    """指紋から種の当たりをつける。★聴く順番を決めるための当て推量。最後は耳。

    ★★2026年8月25日、種名の付いた実素材16本で当て直した。
      それ以前の版は memo の「ヒグラシ＝毎秒10〜15回の脈」を鵜呑みにしていたが、
      **10〜15Hz はアブラゼミだった**。実測でこう割れる：
        ヒグラシ   脈 6.9〜8.5Hz  主帯 4156〜4457Hz
        アブラゼミ 脈 13.1〜14.9Hz 主帯 5749〜6266Hz
      この取り違えは実害が出る。3時間浴びると疲れるので主役にしないと決めた種を、
      「ヒグラシらしい」と表示して第一幕に据えてしまう。

    ★ニイニイゼミは主帯で一発で分かる。 8140〜8635Hz と飛び抜けて高く、
      響きが 0.00＝ほぼ純音（「チーーー」という連続音そのもの）。

    ★★ミンミンとツクツクは、いまの指標では割れない。 脈が 2.8 と 2.9 で重なり、
      響きも 0.39 が両方に出る（ミンミン 0.13/0.39、ツクツク 0.88/0.39/0.71）。
      **割れないものを割れたふりで出さない。** 確信ありげな誤ラベルは、
      第三幕に別の種を据える事故になる。ここは連名で出して耳に回す。
      ツクツクボウシの本当の目印は「加速する句」で、いまの脈は句の繰り返し周期しか
      見ていない。加速を測る指標を足せば割れるはずだが、未対応。
    """
    c, p, st, r = d["carrier"], d["pulse"], d["pulse_str"], d["ring"]
    if c >= 7000 and r < 0.10:
        return "ニイニイゼミ（高い連続音）"
    if st < 2.0:
        return "脈が立たない＝連続音。外国種の唸りも疑う"
    if c < 3200:
        return "主帯が低い。外国種か、遠すぎる録音を疑う"
    if 11.0 <= p <= 18.0 and c >= 5200:
        return "アブラゼミ（★主役にしない種）"
    if 6.0 <= p <= 10.5 and 3800 <= c <= 5200:
        return "ヒグラシらしい"
    if 2.2 <= p <= 4.5:
        return "ミンミンかツクツクボウシ（割れない。耳で）"
    return "不明"


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


def measure(path, insect=False):
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
    if insect:
        d.update(_insect(mono, d["trim"]))
    l, r = x[0], x[1]
    d["corr"] = float(abs(np.corrcoef(l, r)[0, 1])) if l.std() and r.std() else 1.0
    d["clip"] = 100.0 * float((np.abs(mono) >= 0.999).mean())
    return d


def _verdict(d, insect=False):
    """落ちた理由を並べて返す。空なら合格。"""
    bad = []
    if d["shock"] > LIMITS["shock"]:
        at = "・".join(f"{t:.0f}s" for t in d["shock_at"])
        bad.append(f"衝撃音{d['shock']:.1f}%（{at} を聴く）")
    if d["var"] > (INSECT_VAR if insect else LIMITS["var"]):
        bad.append(f"レベル変動{d['var']:.1f}dB")
    if d["low"] > LIMITS["low"]:
        bad.append(f"120Hz未満{d['low']:.0f}%（交通・吹かれ）")
    if d["dur"] < (INSECT_DUR if insect else LIMITS["dur"]):
        bad.append(f"尺{d['dur']:.0f}秒")
    # ★虫・蝉の巻では音程で落とさない（音程が主題）。見張りは「山の動き」に任せる。
    if not insect and d["tonal"] > LIMITS["tonal"]:
        at = "・".join(f"{t:.0f}s" for t in d["tonal_at"][:4])
        bad.append(f"音程あり{d['tonal']:.0f}倍（鳥・虫・人声・音楽。{at} を聴く）")
    # ★虫・蝉の巻ではモノラルで落とさない（2026年8月25日）。
    #   効果音サイトの素材は16本中9本がモノラルで、これで落とすと素材が半分になる。
    #   モザイクは同じ素材を速さをずらして左右に振るので、重ねた時点で広がる
    #   （実測：モノラルを含む5本の重ねで L/R 0.15。当たり素材1本の素直ループは0.32）。
    #   ★ただし1本だけで床にするなら従来どおり失格。 判定は「重ねる前提か」で変わる。
    if not insect and d["corr"] > LIMITS["corr"]:
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


def run_vet(paths, insect=False):
    files = _collect(paths)
    if not files:
        raise SystemExit("検品するファイルがありません。")

    rows = []
    for p in files:
        try:
            rows.append(measure(p, insect=insect))
        except Exception as e:                                   # noqa: BLE001
            sys.stderr.write(f"読めません {os.path.basename(p)}: {e}\n")

    if insect:
        return _report_insect(rows)

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


def _report_insect(rows):
    """蝉・虫の巻の検品。合否（衛生）と指紋（種の見分け）を分けて出す。

    ★★合否の表に種は出てこない。 種は指紋の表で当たりをつけ、最後は耳で決める。
      雨のときは「こもり」1つで三幕に割り振れたが、蝉は
      「一日の移ろい」＝種の並びで幕を作るので、並べ替えの軸が指紋のほうになる。
    """
    rows.sort(key=lambda d: -d.get("pulse", 0.0))

    print(f"\n{'素材':38s} {'尺':>7s} {'変動':>5s} {'衝撃':>5s} {'<120':>5s} "
          f"{'L/R':>5s}  判定")
    print("-" * 108)
    ok = []
    for d in rows:
        bad = _verdict(d, insect=True)
        print(f"{d['name'][:37]:38s} {d['dur']:6.0f}s {d['var']:5.1f} "
              f"{d['shock']:4.1f}% {d['low']:4.0f}% {d['corr']:5.2f}  "
              + ("合格" if not bad else "／".join(bad)))
        if not bad:
            ok.append(d)
    print(f"\n合格 {len(ok)} / {len(rows)} 本"
          f"　※両端を{TRIM:.0%}落として測っている／変動の上限は仮の{INSECT_VAR}dB"
        f"／モノラルでは落としていない（重ねて広げる前提）")

    if not ok:
        return ok

    print("\n蝉の指紋　※合否ではない。聴く順番を決めるための当て推量")
    print(f"{'素材':38s} {'脈Hz':>6s} {'強さ':>6s} {'主帯Hz':>7s} {'響き':>6s} "
          f"{'L/R':>5s} {'こもり':>6s}  見立て")
    print("-" * 130)
    for d in ok:
        # 強さは中央値との比なので、地の静かな素材では桁が飛ぶ。表では999で頭打ちにする。
        print(f"{d['name'][:37]:38s} {d['pulse']:6.1f} {min(d['pulse_str'], 999.0):6.1f} "
              f"{d['carrier']:7.0f} {d['ring']:6.2f} {d['corr']:5.2f} "
              f"{d['muffle']:+6.1f}  {_guess(d)}")

    # ★響きの薄い（＝山を持たない）雑音的な素材では山の動きに意味が無い。
    #   帯域雑音を測ると山が毎フレーム飛んで 2.5kHz 出る（合成音で確認）。
    #   鳴りを持つ素材に限って見張る。
    wide = [d for d in ok if d["wander"] > 1500 and d["ring"] < 0.40]
    if wide:
        print("\n★山が動いている＝鳥・人声が乗っている疑い。必ずこの時刻を聴くこと：")
        for d in wide:
            at = "・".join(f"{t:.0f}s" for t in d["wander_at"][:4])
            print(f"  {d['name'][:44]:45s} {d['wander']:.0f}Hz　{at}")
    print("\n★人声はどの数字にも出ない。 通しで一度は耳を通すこと（雨の巻で1本取り逃がしている）。")
    return ok
