"""SOJ09 のショート3本を、水が動く本編から切り出す（SOJ08 の同名スクリプトを写したもの）。

  python3 SOJ09_制作/ショートを作る.py [--audio 音_完成/xxx.wav] [--only A B]

★bgmkit の `short` は静止画からしか組めない（`-loop 1 -i img`）。YKL01 と同じく、
  文字の描画（`_overlay`）・縦のケンバーンズ・音の整音は bgmkit のものをそのまま使い、
  **映像の入力だけ本編（無音・水の動き付き）に差し替える**。文字の位置も音量の作り方も既刊と同じになる。
★場面3（宿の縁側）は作らない。縦に切ると縁側と行灯（左端）か海（右）のどちらかしか残らない。
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from bgmkit import config  # noqa: E402
from bgmkit.ffutil import ff, measure_loudness  # noqa: E402
from bgmkit.short import _head_check, _hms, _kenburns_v, _overlay  # noqa: E402

VIDEO = ROOT / "映像_本編" / "SOJ09_晩秋の浜辺_3608秒_無音.mp4"
IMAGES = ROOT / "画像"

# 出す順：A（女性と舟＝いちばん掴む）→ B（昼の波打ち際）→ C（月夜）
# anchor は 9:16 の切り出し位置（0＝左端・1＝右端）。★A は 0.84 だと縦のケンバーンズで女性が左端で切れた→0.60
SHORTS = [
    dict(tag="A", at="0:26:00", image="02_漁村の浜_夕方.png", anchor=0.60, move="out",
         scrim=dict(opacity=0.88, top=900, full=1500),
         title="晩秋の浜辺", sub=["夕暮れの漁村", "1時間版はチャンネルに"]),
    dict(tag="B", at="0:08:00", image="01_波打ち際_昼下がり.png", anchor=0.45, move="in",
         scrim=dict(opacity=0.88, top=900, full=1500),
         title="晩秋の浜辺", sub=["昼下がりの波打ち際", "1時間版はチャンネルに"]),
    # ★C は月夜で平均39.9（SOJのショートの目安50以上を切る）。SOJ08 と同じく暗部を持ち上げる
    dict(tag="C", at="0:53:00", image="04_月夜の海_夜.png", anchor=0.80, move="in", pre="eq=gamma=1.18",
         scrim=dict(opacity=0.88, top=900, full=1500),  # ★副題が月の道と白い波に乗って沈んだ
         title="晩秋の浜辺", sub=["月夜の海、遠い波の音", "1時間版はチャンネルに"]),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", default=str(ROOT / "音_完成" / "SOJ09_原音_xf15_s4-1.2.wav"))
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    cfg = config.load("soj09")
    s = cfg["short"]
    W, H = s["size"]
    SW, SH = s["supersample"]
    fps = s["fps"]
    bed = a.audio
    outdir = ROOT / "ショート"
    outdir.mkdir(exist_ok=True)
    tmp = str(outdir / "_overlay.png")
    for spec in SHORTS:
        if a.only and spec["tag"] not in a.only:
            continue
        dur = float(s["seconds"])
        start = _hms(spec["at"])
        h, b, gap = _head_check(bed, start, dur)
        print(f"{spec['tag']}  {spec['at']}から{dur:.0f}秒  頭{h:.1f}/本体{b:.1f}dB"
              + ("  ★頭が静か" if gap < -8 else ""))
        # 文字の見え方（地の明るさ）は元の静止画で測る。映像と同じ絵なので結果は一致する
        _overlay(cfg, spec, tmp, str(IMAGES / spec["image"]))
        nf = int(round(dur * fps))
        pre = spec.get("pre")
        vf = (f"[0:v]{pre + ',' if pre else ''}scale=-1:{SH}:flags=lanczos,"
              f"crop={SW}:{SH}:'(iw-{SW})*{spec['anchor']}':0,setsar=1,format=yuv420p,fps={fps},"
              f"{_kenburns_v(cfg, spec['move'], nf)},"
              f"scale={W}:{H}:flags=lanczos,{s['unsharp']}[v];"
              f"[v][1:v]overlay=0:0[vo]")
        au = dict(cfg["audio"])
        au["target_lufs"] = s.get("target_lufs", au["target_lufs"])
        au["true_peak"] = s.get("true_peak", au["true_peak"])
        m = measure_loudness(bed, au, ss=start, t=dur)
        fade = s["audio_fade"]
        af = (f"loudnorm=I={au['target_lufs']}:TP={au['true_peak']}:LRA={au['lra']}"
              f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
              f":measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}"
              f":offset={m['target_offset']}:linear=true,"
              f"afade=t=in:st=0:d={fade},afade=t=out:st={dur - fade:.2f}:d={fade}")
        out = str(outdir / f"soj09_ショート_{spec['tag']}.mp4")
        e = s["encode"]
        ff(["-ss", f"{start}", "-t", f"{dur}", "-i", str(VIDEO), "-i", tmp,
            "-ss", f"{start}", "-t", f"{dur}", "-i", bed,
            "-filter_complex", vf, "-map", "[vo]", "-map", "2:a", "-af", af,
            "-frames:v", str(nf),
            "-c:v", e["vcodec"], "-preset", e["preset"], "-crf", str(e["crf"]),
            "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", au.get("bitrate", "320k"), "-ar", "48000",
            "-movflags", "+faststart", out])
        print(f"    → {out}")
    os.remove(tmp) if os.path.exists(tmp) else None


if __name__ == "__main__":
    main()
