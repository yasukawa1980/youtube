"""EOJL01（EOJ総集編・約8時間47分）の音と manifest を、公開済み9巻からつなぐ。

★★音は作り直さない。 各巻の `_work/music_bed.wav`（公開版と同じ整音済み）を
  巻の境で8秒の等電力クロスフェード（各巻の中の曲間と同じ長さ）で重ねるだけ。
  巻の終わりは自然減衰で −48dB まで落ちて終わる（EOJ10で実測）ので、そのまま重ねてよい。
★★WAVは4GBを超える（16bit/48k/2chで約6.1GB）→ RF64 で書く。ffmpeg はそのまま読める。
★manifest は「場面（画の切替）」の単位で36本にする（9巻×4場面）。
  EOJ02・03 の manifest は曲単位の8本なので、2本おきに拾って場面にそろえる。

使い方：python3 bgm/EOJL01_つなぐ.py        （音と manifest を作って測る）
"""
import glob
import json
import os
import subprocess
import sys

BGM = os.path.dirname(os.path.abspath(__file__))
SRC = "/Volumes/ESD-02/BGM/5_Echoes of Old Japan"
OUT = os.path.join(SRC, "EOJL01_素材_8時間")
XF = 8.0

# 並び順（子守歌で始め、夜の中ほどにゴルトベルク、朝のアヴェ・マリアで終わる）
ORDER = [
    ("eoj13", "EOJ13_素材_子守歌", "Lullabies"),
    ("eoj03", "EOJ03_素材_ジムノペディ", "Gymnopédies"),
    ("eoj02", "EOJ02_素材_グノシエンヌ", "Gnossiennes"),
    ("eoj04", "EOJ04_素材_ノクターン", "Nocturnes"),
    ("eoj11", "EOJ11_素材_ゴルトベルク", "Goldberg Variations"),
    ("eoj08", "EOJ08_素材_雨だれ", "Raindrop Prelude"),
    ("eoj09", "EOJ09_素材_緩徐楽章", "Pathétique & Appassionata"),
    ("eoj10", "EOJ10_素材_トロイメライ", "Träumerei"),
    ("eoj12", "EOJ12_素材_アヴェマリア_シューベルト", "Ave Maria"),
]


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", p], capture_output=True, text=True, check=True)
    return float(r.stdout)


def scenes(slug):
    """その巻の manifest から、画の切替4か所の開始秒と名前を返す。"""
    m = json.load(open(glob.glob(os.path.join(BGM, slug.upper() + "_*", "_work", "manifest.json"))[0]))
    t = m["tracks"]
    per = len(t) // 4
    return [(t[i * per]["start"], t[i * per]["name"]) for i in range(4)]


def main():
    os.makedirs(os.path.join(OUT, "_work"), exist_ok=True)
    beds = [os.path.join(SRC, d, "_work", "music_bed.wav") for _, d, _ in ORDER]
    for b in beds:
        if not os.path.exists(b):
            sys.exit(f"音がありません: {b}")
    ds = [dur(b) for b in beds]

    tracks, chapters, off = [], [], 0.0
    for k, ((slug, _, name), d) in enumerate(zip(ORDER, ds)):
        chapters.append((off, slug, name))
        for s, n in scenes(slug):
            tracks.append({"start": round(off + s, 3), "name": f"{slug} {n}"})
        off += d - XF
    total = off + XF

    # 9本を順に acrossfade（等電力 qsin）。 各巻の曲間の重ねと同じ8秒
    ins, f, prev = [], [], "0:a"
    for b in beds:
        ins += ["-i", b]
    for i in range(1, len(beds)):
        o = f"x{i}"
        f.append(f"[{prev}][{i}:a]acrossfade=d={XF}:c1=qsin:c2=qsin[{o}]")
        prev = o
    wav = os.path.join(OUT, "_work", "music_bed.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", ";".join(f),
                    "-map", f"[{prev}]", "-c:a", "pcm_s16le", "-ar", "48000", "-rf64", "auto", wav],
                   check=True)

    man = {"total": round(dur(wav), 4), "xf": XF, "tracks": tracks}
    json.dump(man, open(os.path.join(OUT, "_work", "manifest.json"), "w"), ensure_ascii=False, indent=1)
    print(f"計算上の尺 {total:.1f}秒 / 実測 {man['total']:.1f}秒")
    for o, slug, name in chapters:
        h, r = divmod(int(round(o)), 3600)
        print(f"  {h}:{r // 60:02d}:{r % 60:02d} {name}（{slug}）")


if __name__ == "__main__":
    main()
