"""IRO22 Suno候補の自動検品：AST（AudioSet）で10秒ごとに分類し、人声の最大値・主役らしいラベル・強いラベル上位を出す。
使い方: iro22_試作を自動検品.py <WAVのフォルダ> <出力JSON>"""
import json, pathlib, subprocess, sys, numpy as np, torch
from transformers import ASTFeatureExtractor, ASTForAudioClassification
MODEL = pathlib.Path(__file__).resolve().parent.parent / 'bgm' / '.models' / 'ast-audioset'
SRC, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
dev = 'mps' if torch.backends.mps.is_available() else 'cpu'
ex = ASTFeatureExtractor.from_pretrained(MODEL, local_files_only=True)
m = ASTForAudioClassification.from_pretrained(MODEL, local_files_only=True).to(dev).eval()
lab = m.config.id2label
voc = [i for i, n in lab.items() if any(t in n.lower() for t in ('speech', 'singing', 'choir', 'chant', 'humming', 'whisper', 'vocal', 'rapping')) and n not in ('Singing bowl', 'Whale vocalization')]
# 種類ごとに主役として期待するラベル
LEAD = {'A': ['Electric piano', 'Rhodes piano', 'Piano'], 'B': ['Electric guitar', 'Guitar'], 'C': ['Trumpet', 'Brass instrument', 'French horn'],
        'D': ['Harpsichord', 'Piano'], 'E': ['Double bass', 'Bass guitar'], 'F': ['Harmonica', 'Accordion', 'Wind instrument, woodwind instrument'],
        'G': ['Harp', 'Plucked string instrument'], 'H': ['Singing bowl', 'Bell']}
DRUM = ['Drum', 'Drum kit', 'Snare drum', 'Bass drum', 'Hi-hat', 'Percussion']
idx = {n: i for i, n in lab.items()}
skip = {'Music', 'Musical instrument'}
out = json.loads(OUT.read_text()) if OUT.exists() else {}
for p in sorted(SRC.glob('*.wav')):
    if p.stem in out: continue
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(p), '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'])
    y = np.frombuffer(raw, '<f4'); wins = [y[s:s + 160000] for s in range(0, len(y) - 160000 + 1, 160000)]
    probs = []
    for k in range(0, len(wins), 6):
        f = ex([w for w in wins[k:k + 6]], sampling_rate=16000, return_tensors='pt').to(dev)
        with torch.no_grad(): probs.append(torch.sigmoid(m(**f).logits).cpu().numpy())
    P = np.concatenate(probs); mean = P.mean(0)
    kind = p.stem.split('_')[1][0]
    lead = {n: round(float(mean[idx[n]]), 3) for n in LEAD[kind] if n in idx}
    top = [(lab[i], round(float(mean[i]), 3)) for i in np.argsort(-mean) if lab[i] not in skip][:6]
    drum = round(float(max(mean[idx[n]] for n in DRUM if n in idx)), 3)
    # 尾：最後の1秒のRMS(dB)
    tail = round(float(20 * np.log10(np.sqrt(np.mean(y[-16000:] ** 2)) + 1e-9)), 1)
    out[p.stem] = {'人声の最大': round(float(P[:, voc].max()), 3), '主役ラベル': lead, '打楽器': drum, '尾dB': tail, '上位': top}
    print(p.stem, out[p.stem]['人声の最大'], drum, tail, lead, top[:4], flush=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
