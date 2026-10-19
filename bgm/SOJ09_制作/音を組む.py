"""SOJ09「晩秋の浜辺」：4本の波の実録を、それぞれ一度だけ・ループなしで継いで1時間にする。

  python3 SOJ09_制作/音を組む.py [--src 試聴|原音] [--xf 15] [--s4 -1.2] [--ceil -2.5] [--out 名前]

SOJ08 の `音を組む.py` を写したもの。違いは「波頭の手フェーダー」だけ。
  ★波は砕けるたびに平均より 13〜19dB 飛び出す。−17.6 LUFS に揃えると、場面1・2で
    合わせて十数秒だけ標本ピークが上限（−2.5dBFS）を超えた（どれも 1〜3秒続く本物の大波で、
    周波数の形は平常と同じ。クリックではない）。
  ★リミッタ・コンプは使わない（シリーズの約束）。代わりに、超える秒だけ「必要な dB だけ」
    1秒の上げ下げで滑らかに下げる。人がフェーダーで大波を少し抑えるのと同じ。
    波の大きさは元々 10dB 以上ばらつくので、2〜3dB 小さい波として聞こえるだけ。

手順：
  1. 各素材から区間を切り出し、−18 LUFS に揃える（ゲインのみ）。場面4 だけ s4 dB 下げる
  2. qsin（等パワー）15秒で継ぐ
  3. 全体を1回だけゲインで −17.6 へ。末尾12秒でフェードアウト
  4. 波頭の手フェーダー（上限 ceil dBFS）→ もう一度だけ全体ゲインで −17.6 に戻す
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SR = 48000

# 場面：(名前, 素材ID, 使う区間の頭[秒], 長さ[秒], 追加フィルタ)
# ★区間は検品で避けるべき秒を外して選んだ（テーマ設計 §2・§3）
# ★★ピークで選び直した（2026-09-30）。−17.6 LUFS に揃えたとき標本ピークが −2.5dBFS を
#   超えない素材だけを使う（AAC段の持ち上がりを見込んで TP −1.5 に収めるため）。
#   730828（しぶきが75秒ぶん上限超え・最大+6.9）と 511349（43秒ぶん・+1.5）は外した。
#   リミッタで潰すと粒立ちが消える。平均より20dB飛び出すしぶきは睡眠用では起こす音でもある。
SCENES = [
    ("波打ち際", "436409", 95.0, 1130.0, ""),      # incoming tide。重心1533Hz・最も近い。−18で最大−2.2（95〜1135）
    ("漁村の浜", "449983", 170.0, 1125.0, ""),     # Wrightsville。908Hz・周期11秒で規則的。大波が12秒ぶん上限超え（最大+0.1）
    ("宿の縁側", "261204", 0.0, 560.0, ""),        # 629Hz・左右相関0.94＝狭い音（屋内から聞く）。560秒以降に人の反応0.28→使わない
    ("月夜の海", "860010", 20.0, 838.0, ""),       # 297Hz・左右相関0.05＝最も暗く広い。衝撃音ゼロ・超過ゼロ
]
TRACK_LUFS = -18.0
FINAL_LUFS = -17.6
FADE = 12.0


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def src_path(kind, sid):
    if kind == "試聴":
        return ROOT / "候補試聴" / f"prev_{sid}.mp3"
    hits = sorted((ROOT / "原音").glob(f"{sid}_*")) + sorted((ROOT / "原音").glob(f"{sid}.*"))
    if not hits:
        raise SystemExit(f"原音がありません: 原音/{sid}_*")
    return hits[0]


def loudness(path, ss=None, t=None, extra=""):
    cmd = ["ffmpeg", "-hide_banner", "-nostats"]
    if ss is not None:
        cmd += ["-ss", str(ss), "-t", str(t)]
    af = (extra + "," if extra else "") + "loudnorm=print_format=json"
    cmd += ["-i", str(path), "-af", af, "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    return json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err, re.S).group(0))


def ebur128(path):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af",
                          "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    tail = err[err.rfind("Summary:"):]
    g = lambda k: float(re.search(k + r":\s+(-?[\d.]+)", tail).group(1))  # noqa: E731
    return dict(I=g("I"), LRA=g("LRA"), TP=g("Peak"))


def fader(path, ceil):
    """波頭の手フェーダー：標本ピークが ceil を超える所だけ、必要な dB を 1秒の上げ下げで下げる。"""
    import numpy as np
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, "<f4").reshape(-1, 2).astype(np.float64)
    hop = SR // 100                                   # 10ms
    n = len(x) // hop
    pk = np.abs(x[: n * hop]).max(1).reshape(n, hop).max(1)
    need = np.maximum(0.0, 20 * np.log10(pk + 1e-12) - ceil) + np.where(pk > 10 ** (ceil / 20), 0.1, 0)
    # 前後0.5秒の最大を取ってから0.5秒ならす（ならしで必要量を下回らないよう、先に広げる）
    w = 50
    padded = np.pad(need, w)
    wide = np.max(np.lib.stride_tricks.sliding_window_view(padded, 2 * w + 1), axis=1)
    k = np.hanning(2 * w + 1); k /= k.sum()
    sm = np.maximum(np.convolve(wide, k, "same"), need)
    g = 10 ** (-np.repeat(sm, hop) / 20)
    g = np.concatenate([g, np.full(len(x) - len(g), g[-1] if len(g) else 1.0)])
    y = (x * g[:, None]).astype("<f4")
    secs = sorted(set((np.where(need > 0)[0] // 100).tolist()))
    tmp = Path(path).with_name("_fader.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s24le", str(tmp)], input=y.tobytes(), check=True)
    tmp.replace(path)
    print(f"波頭の手フェーダー：{len(secs)}秒ぶん・最大 {need.max():.1f}dB 下げた  {secs[:30]}")
    return dict(ceil=ceil, seconds=secs, max_db=round(float(need.max()), 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="試聴", choices=["試聴", "原音"])
    ap.add_argument("--xf", type=float, default=15.0)
    ap.add_argument("--s4", type=float, default=-1.2)
    ap.add_argument("--out", default=None)
    ap.add_argument("--ceil", type=float, default=-2.5)
    a = ap.parse_args()

    work = ROOT / "音_作業" / a.src
    work.mkdir(parents=True, exist_ok=True)
    parts = []
    log = dict(src=a.src, xf=a.xf, s4_db=a.s4, scenes=[])
    for i, (name, sid, ss, dur, flt) in enumerate(SCENES):
        p = src_path(a.src, sid)
        m = loudness(p, ss, dur, flt)
        gain = TRACK_LUFS - float(m["input_i"]) + (a.s4 if i == 3 else 0.0)
        dst = work / f"{i + 1:02d}_{name}.wav"
        run(["ffmpeg", "-y", "-v", "error", "-ss", str(ss), "-t", str(dur), "-i", str(p),
             "-af", (flt + "," if flt else "") + f"volume={gain:.3f}dB", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", str(dst)])
        parts.append(dst)
        log["scenes"].append(dict(name=name, id=sid, ss=ss, dur=dur, filter=flt, file=p.name,
                                  in_I=float(m["input_i"]), in_TP=float(m["input_tp"]),
                                  gain_db=round(gain, 2)))
        print(f"{i + 1} {name:6s} {sid}  {ss:6.0f}s〜{ss + dur:6.0f}s  in {m['input_i']:>6s} LUFS"
              f" / TP {m['input_tp']:>6s}  → {gain:+.2f}dB")

    # qsin で継ぐ
    ins = sum((["-i", str(p)] for p in parts), [])
    fc, prev = [], "[0:a]"
    for i in range(1, len(parts)):
        fc.append(f"{prev}[{i}:a]acrossfade=d={a.xf}:c1=qsin:c2=qsin[a{i}]")
        prev = f"[a{i}]"
    bed = work / "連結.wav"
    run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fc), "-map", prev,
         "-c:a", "pcm_s24le", str(bed)])

    total = sum(sc[3] for sc in SCENES) - a.xf * (len(SCENES) - 1)
    m = ebur128(bed)
    g = FINAL_LUFS - m["I"]
    out = ROOT / "音_完成" / (a.out or f"SOJ09_{a.src}_xf{a.xf:g}_s4{a.s4:g}.wav")
    out.parent.mkdir(exist_ok=True)
    run(["ffmpeg", "-y", "-v", "error", "-i", str(bed), "-af",
         f"volume={g:.3f}dB,afade=t=in:d=3,afade=t=out:st={total - FADE}:d={FADE}",
         "-c:a", "pcm_s24le", str(out)])
    nfix = fader(out, a.ceil)
    fin = ebur128(out)
    if abs(fin["I"] - FINAL_LUFS) > 0.05:
        tmp = out.with_name("_tmp.wav")
        run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-af", f"volume={FINAL_LUFS - fin['I']:.3f}dB",
             "-c:a", "pcm_s24le", str(tmp)])
        tmp.replace(out)
        fin = ebur128(out)
    log["fader"] = nfix

    starts, acc = [], 0.0
    for *_, d, _f in SCENES:
        starts.append(acc)
        acc += d - a.xf
    log.update(total=total, final=fin, final_gain_db=round(g, 2), out=out.name,
               chapters=[dict(t=round(s, 1), name=n) for s, (n, *_) in zip(starts, SCENES)])
    (out.with_suffix(".json")).write_text(json.dumps(log, ensure_ascii=False, indent=2))
    mm = lambda s: f"{int(s // 60)}:{int(s % 60):02d}"  # noqa: E731
    print(f"\n{out.name}  {mm(total)}（{total:.1f}秒）  I {fin['I']} / LRA {fin['LRA']} / TP {fin['TP']}")
    print("章：" + "  ".join(f"{mm(s)} {n}" for s, (n, *_) in zip(starts, SCENES)))


if __name__ == "__main__":
    main()
