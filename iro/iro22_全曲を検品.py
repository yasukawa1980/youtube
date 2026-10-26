"""IRO22 全候補の検品：途中の無音・頭と尾の音量（尾の切れ）・音量(LUFS/TP)・高域比。人声と主役は iro22_試作を自動検品.py の結果を使う。
使い方: iro22_全曲を検品.py <WAVのフォルダ> <出力JSON>"""
import json, pathlib, subprocess, re, sys, numpy as np
SRC, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out = {}
for p in sorted(SRC.glob('*.wav')):
    y = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(p), '-ac', '1', '-ar', '16000', '-f', 'f32le', '-']), '<f4')
    sec = y[:len(y) // 16000 * 16000].reshape(-1, 16000); db = 20 * np.log10(np.sqrt((sec ** 2).mean(1)) + 1e-9)
    runs = cur = 0
    for v in db[3:-3]:
        cur = cur + 1 if v < -50 else 0; runs = max(runs, cur)
    lu = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(p), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', lu)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+)', lu)[-1])
    yy = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', '60', '-t', '60', '-i', str(p), '-ac', '1', '-ar', '44100', '-f', 'f32le', '-']), '<f4')
    S = np.abs(np.fft.rfft(yy)) ** 2; fq = np.fft.rfftfreq(len(yy), 1 / 44100)
    out[p.stem] = {'秒': round(len(y) / 16000, 2), '途中無音秒': int(runs), '最初1秒dB': round(float(db[0]), 1), '最後1秒dB': round(float(db[-1]), 1),
                   '最後5秒の中央dB': round(float(np.median(db[-5:])), 1), '本体の中央dB': round(float(np.median(db)), 1),
                   'LUFS': I, 'TP': TP, '高域比': round(float(S[fq > 8000].sum() / S.sum()), 4)}
    print(p.stem, out[p.stem], flush=True)
OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
