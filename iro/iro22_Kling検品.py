"""IRO22 Kling素材の検品：カメラのずれ（背景の位相相関）・頭↔尻の差・動いた範囲・コマ見本。
使い方: iro22_Kling検品.py <Kling素材フォルダ> <出力フォルダ>"""
import json, pathlib, subprocess, sys, numpy as np
from PIL import Image
SRC, OUT = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
W, H = 480, 270
def frames(p):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(p), '-vf', f'scale={W}:{H}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32)
def shift(a, b):
    F = np.fft.fft2(a) * np.conj(np.fft.fft2(b)); r = np.fft.ifft2(F / (np.abs(F) + 1e-6)).real
    y, x = np.unravel_index(r.argmax(), r.shape); y = y - H if y > H // 2 else y; x = x - W if x > W // 2 else x
    return float(np.hypot(x, y)) * 4  # 1920基準
out = {}
for p in sorted(SRC.glob('iro22_*_raw.mp4')):
    f = frames(p); g = f.mean(3); n = len(f)
    # 背景＝右の本棚の上（人物・犬から離れた所）
    bg = g[:, 10:110, 380:470]
    drift = max(shift(np.pad(bg[i], 0), np.pad(bg[0], 0)) for i in range(0, n, 6))
    d = np.abs(np.diff(g, axis=0)).mean((1, 2))
    seam = float(np.abs(g[-1] - g[0]).mean())
    mot = np.abs(g - g[0]).max(0) > 12
    ys, xs = np.nonzero(mot)
    box = [int(xs.min() * 4), int(ys.min() * 4), int(xs.max() * 4), int(ys.max() * 4)] if len(xs) else None
    out[p.stem] = {'コマ数': n, 'カメラずれpx最大': round(drift, 2), 'コマ間差の中央': round(float(np.median(d)), 3),
                   'コマ間差の最大': round(float(d.max()), 3), '尻→頭の差': round(seam, 3), '動いた範囲1920': box,
                   '動いた画素の割合%': round(float(mot.mean() * 100), 2)}
    idx = np.linspace(0, n - 1, 9).astype(int)
    sheet = Image.new('RGB', (W * 3, H * 3))
    for k, i in enumerate(idx): sheet.paste(Image.fromarray(f[i].astype(np.uint8)), ((k % 3) * W, (k // 3) * H))
    sheet.save(OUT / f'{p.stem}_見本.jpg', quality=82)
    print(p.stem, out[p.stem], flush=True)
(OUT / 'Kling検品.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
