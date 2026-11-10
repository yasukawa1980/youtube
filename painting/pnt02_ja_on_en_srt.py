"""絵画02：日本語字幕（本文はv01のまま）を英語版の時間割に載せ替える。
区間（P01〜P14）ごとに、日本語の語りの範囲を英語の語りの範囲へ線形に写す。
使い方: python3 -I wom13_ja_on_en_srt.py <確認版_v01フォルダ> <出力SRT>
"""
import json, sys, re
D, OUT = sys.argv[1], sys.argv[2]
MIN = 1.4

def seg_ranges(lang):
    d = json.load(open(f"{D}/{lang}/records/narration_timeline_{lang}.json"))
    r = {}
    for s in d["segments"]:
        r[s["id"]] = (s["cues"][0]["start"], s["cues"][-1]["end"])
    return r, d["duration_seconds"]

en, en_dur = seg_ranges("en")
ja, _ = seg_ranges("ja")
assert list(en) == list(ja), "区間IDが英日で違う"
cues = json.load(open(f"{D}/ja/records/subtitle_cues_ja.json"))["cues"]

out = []
for c in cues:
    sid = c["sentence_id"].split("-")[0]
    (js, je), (es, ee) = ja[sid], en[sid]
    f = lambda t: es + (t - js) * (ee - es) / (je - js)
    out.append([f(c["start"]), f(c["end"]), c["text"], sid])

# 最短1.4秒：短いものは次の字幕の手前（無ければ区間の終わり+余裕）まで延ばす
for i, o in enumerate(out):
    if o[1] - o[0] < MIN:
        nxt = out[i + 1][0] if i + 1 < len(out) else en_dur
        o[1] = min(o[0] + MIN, nxt - 0.05)
    if o[1] - o[0] < MIN:  # まだ短ければ、前の字幕との空きへ始まりを早める
        prv = out[i - 1][1] if i else 0.0
        o[0] = max(o[1] - MIN, prv + 0.05)

def ts(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

with open(OUT, "w", encoding="utf-8") as fh:
    for i, (s, e, t, _) in enumerate(out, 1):
        fh.write(f"{i}\n{ts(s)} --> {ts(e)}\n{t}\n\n")

durs = [e - s for s, e, _, _ in out]
ov = sum(1 for a, b in zip(out, out[1:]) if b[0] < a[1])
print(json.dumps({"count": len(out), "min_dur": round(min(durs), 3), "overlaps": ov,
                  "last_end": round(out[-1][1], 3), "en_duration": en_dur,
                  "below_min": sum(d < MIN - 1e-6 for d in durs)}, ensure_ascii=False))
