"""SOJ09：波の実録に「水以外の音」が混ざっていないかを全編走査する。

Nothing but a Mountain Stream を名乗るので、鳥・虫・蛙・人声・車・飛行機・犬・風・雨が
混ざった素材は床にできない。沢の実録で最も多い混入は鳥（タグに無くても入っている）。

  python3 SOJ08_制作/混入走査.py 出力.json ファイル…

10秒窓・5秒刻みで全サンプルを見る（bgmkit/vocalcheck.py と同じ窓）。
★点数は証拠であって保証ではない。最後は該当秒を耳で聴く。
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

MODEL = Path(__file__).resolve().parent.parent / ".models" / "ast-audioset"

# 混入として数えるもの（AudioSetのラベル名に含まれる語）
DIRT = {
    "鳥": ("Bird", "Chirp, tweet", "Pigeon", "Crow", "Caw", "Owl", "Coo", "Squawk", "Bird vocalization, bird call, bird song", "Hoot"),
    "虫": ("Insect", "Cricket", "Mosquito", "Fly, housefly", "Bee, wasp", "Buzz"),
    "蛙": ("Frog", "Croak"),
    "人": ("Speech", "Conversation", "Laughter", "Shout", "Child", "Whistling",
          "Footsteps", "Walk, footsteps", "Children playing", "Children shouting", "Child speech, kid speaking"),
    "車": ("Vehicle", "Car", "Motor vehicle", "Traffic", "Engine", "Truck",
          "Motorcycle", "Train", "Aircraft", "Airplane", "Helicopter", "Jet engine"),
    "船": ("Boat, Water vehicle", "Motorboat, speedboat", "Ship", "Foghorn", "Sailboat, sailing ship", "Rowboat, canoe, kayak"),
    "犬": ("Dog", "Bark"),
    "風": ("Wind", "Wind noise (microphone)", "Rustling leaves"),
    "雨": ("Rain", "Raindrop", "Rain on surface", "Thunder", "Thunderstorm"),
    "音楽": ("Music", "Musical instrument", "Bell", "Chime"),
}
WATER = ("Stream", "Waterfall", "Water", "Gurgling", "Pour", "Trickle, dribble",
         "Splash, splatter", "Ocean", "Waves, surf")
HIT = 0.10       # これを超えた窓を「疑い」として数える


def main():
    import torch
    from transformers import ASTFeatureExtractor, ASTForAudioClassification
    out = Path(sys.argv[1])
    files = sys.argv[2:]
    torch.set_num_threads(8)
    ext = ASTFeatureExtractor.from_pretrained(MODEL, local_files_only=True)
    model = ASTForAudioClassification.from_pretrained(MODEL, local_files_only=True).eval()
    labels = model.config.id2label
    idx = {k: [i for i, n in labels.items() if n in v] for k, v in DIRT.items()}
    widx = [i for i, n in labels.items() if n in WATER]
    res = json.loads(out.read_text()) if out.exists() else {}
    for f in files:
        name = Path(f).name
        if name in res:
            continue
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000",
                              "-f", "f32le", "-"], check=True, capture_output=True).stdout
        x = np.frombuffer(raw, dtype="<f4")
        W, S = 160000, int(16000 * float(__import__("os").environ.get("STRIDE", "5")))
        starts = list(range(0, max(1, len(x) - W + 1), S))
        rows = []
        for st in range(0, len(starts), 16):
            batch = [x[s:s + W] for s in starts[st:st + 16]]
            batch = [np.pad(b, (0, W - len(b))) for b in batch]
            inp = ext(batch, sampling_rate=16000, return_tensors="pt")
            with torch.inference_mode():
                sc = model(**inp).logits.sigmoid().numpy()
            for s, r in zip(starts[st:st + 16], sc):
                rows.append(dict(t=s / 16000,
                                 dirt={k: float(r[v].max()) if v else 0.0 for k, v in idx.items()},
                                 water=float(r[widx].max()),
                                 top=labels[int(r.argmax())]))
        summ = {}
        for k in DIRT:
            v = np.array([r["dirt"][k] for r in rows])
            at = [round(r["t"]) for r in rows if r["dirt"][k] > HIT]
            summ[k] = dict(max=round(float(v.max()), 3), share=round(100 * len(at) / len(rows), 1),
                           at=at[:12])
        res[name] = dict(dur=len(x) / 16000, windows=len(rows), summary=summ,
                         water_min=round(min(r["water"] for r in rows), 3),
                         rows=rows)
        out.write_text(json.dumps(res, ensure_ascii=False))
        worst = sorted(summ.items(), key=lambda kv: -kv[1]["share"])[:4]
        print(f"{name:28s} {len(x)/16000/60:5.1f}分 水の最低{res[name]['water_min']:.2f}  "
              + "  ".join(f"{k}{v['share']:.0f}%(max{v['max']:.2f})" for k, v in worst), flush=True)


if __name__ == "__main__":
    main()
