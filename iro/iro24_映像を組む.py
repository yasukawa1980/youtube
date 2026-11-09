"""IRO24 の映像を組む（Claude 2026-11-09。iro23_映像を組む.py を下敷きにした）。

Kling は使わない。場面の静止画6枚（S1〜S6）を30分ずつ並べ、境目は8秒の溶かし。
動きは計算で足す：窓の外の雪（S2・S4、S5 は画面全体。S1 はまだ降らず、S6 はやんでいる）、
ツリーの電球のまたたき（S4・S5・S6）、ココアの湯気（S3・S6）。
どれも30秒で一周する式で作り、30秒の部品（無劣化 -qp 0）を繰り返す（継ぎ目なし）。

  python iro24_映像を組む.py prep            # 1672→1920 に拡大、夜の絵は暗部を少し持ち上げる（ESD-02 の _映像作業/）
  python iro24_映像を組む.py bulbs           # 電球の位置を検出して見本に印を付ける（確認用）
  python iro24_映像を組む.py loops           # 場面ごとの30秒の部品
  python iro24_映像を組む.py check           # 部品から見本の静止画と継ぎ目の差
  python iro24_映像を組む.py card            # 終了カード
  python iro24_映像を組む.py final [秒] [開始秒]  # 扉なしの本編。秒を付けると見本
  python iro24_映像を組む.py door [gain]     # 扉ムービーを入れ、音を aac_at で作り直して差し替える
"""
import sys, json, subprocess, importlib.util
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Seasonal/24_今年もツリーを出した')
SSD = Path('/Volumes/ESD-02/IRO/IRO24_素材_クリスマス3時間')
SRC = MAC / '開始画像'; WORK = SSD / '_映像作業'; LOOPS = WORK / 'loops'
BED = SSD / 'music_bed.wav'
OUT = MAC / '投稿用'; MAIN0 = SSD / 'iro24_完成_扉なし.mov'
MAIN = OUT / 'iro24_今年もツリーを出した_本編_扉入り.mp4'
CARD_PNG = MAC / '_work/iro_エンドカード_IRO24.png'
FPS = 24; LOOP = 30; NF = FPS * LOOP
OPEN = 4.2
T = 10800
SCENES = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
FILES = {'S1': 'iro24_S1_案1.png', 'S2': 'iro24_S2.png', 'S3': 'iro24_S3.png', 'S4': 'iro24_S4.png', 'S5': 'iro24_S5.png', 'S6': 'iro24_S6.png'}
XF = 8
CARD_LEN, CARD_XF = 15, 2

# 湯気：液面の中心（1920基準）・縁の幅・立ちのぼる高さ・濃さ
STEAM = {
    'S3': [dict(x=580, y=588, w=150, h=280, a=0.60, base=0.04)],   # 床のトレイのココア。背景は灰色の敷物
    'S6': [dict(x=307, y=505, w=44, h=95, a=0.50)],                # 両手で包んだマグ。顔の前なので低く
}
# 窓ガラス（1920基準）：桟と、手前にかかるツリー・花瓶を除く
WIN = dict(x0=1330, x1=1782, y0=55, y1=585,
           holes=[(1541, 0, 1563, 1080), (0, 294, 1920, 328), (0, 420, 1378, 1080), (1762, 455, 1920, 1080)])
# 雪：数・大きさ（半径px）・30秒で何回落ちきるか・濃さ。 full=True は画面全体（外から見た S5）
SNOW = {
    'S2': dict(n=90, r=(1.4, 3.0), k=(2, 3), a=(0.85, 1.0), col=(255, 255, 255)),   # 降り始め。★初版 n55・r1.0〜2.2・a0.55〜0.85 は明るい灰色の空に溶けて見えなかった
    'S4': dict(n=150, r=(1.0, 2.6), k=(2, 4), a=(0.55, 0.9)),
    'S5': dict(n=260, r=(1.3, 4.2), k=(2, 4), a=(0.45, 0.9), full=True),
}
# 電球を探す範囲（1920基準）
TREE = {'S4': (850, 60, 1385, 715), 'S6': (850, 60, 1385, 715), 'S5': (1380, 120, 1700, 640)}
# 電球の検出から外す範囲（S4 左下の本のページ）
NOBULB = {'S4': [(850, 620, 925, 715)], 'S6': [(850, 620, 925, 715)]}
BULB_DEPTH = {'S4': 0.28, 'S5': 0.22, 'S6': 0.30}
DARK_TARGET = 4.0   # 16未満の画素の割合（%）をこれ以下へ。持ち上げは黒で最大12段階まで


def run(a): subprocess.run(['ffmpeg', '-y', '-v', 'error', *map(str, a)], check=True)


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                capture_output=True, text=True).stdout)


def dark(a): return float((a.astype(np.float32) @ [0.299, 0.587, 0.114] < 16).mean() * 100)


def toe(L):
    x = np.arange(256, dtype=np.float32)
    return np.clip(x + L * np.clip(1 - x / 64, 0, 1) ** 2, 0, 255)


def prep():
    WORK.mkdir(parents=True, exist_ok=True); rep = {}
    for s in SCENES:
        im = np.array(Image.open(SRC / FILES[s]).convert('RGB').resize((1920, 1080), Image.LANCZOS))
        d0 = dark(im); L = 0
        while dark(np.uint8(toe(L)[im] + .5)) > DARK_TARGET and L < 12: L += 1
        out = np.uint8(toe(L)[im] + .5) if L else im
        Image.fromarray(out).save(WORK / f'{s}.png')
        rep[s] = dict(暗部_元=round(d0, 2), 持ち上げ=L, 暗部_後=round(dark(out), 2))
        print(s, rep[s], flush=True)
    (WORK / '暗部.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1))


def periodic(rng, t, kmin, kmax, n=4):
    """30秒で一周するなめらかな揺れ（-1〜1 程度）"""
    v = 0
    for _ in range(n):
        k = rng.integers(kmin, kmax + 1); v = v + np.sin(2 * np.pi * k * t / LOOP + rng.uniform(0, 2 * np.pi)) / n
    return v


def steam_field(sp, t, rng_seed):
    """縁の上の箱に、上へ流れる細い筋を3本描く（アルファ 0〜1）。返り値：(x0, y0, alpha)"""
    w, h = sp['w'], sp['h']; bw = int(w * 1.8); x0 = int(sp['x'] - bw / 2); y0 = int(sp['y'] - h)
    yy, xx = np.mgrid[0:h, 0:bw].astype(np.float32)
    up = 1 - yy / h                                   # 0（縁）→1（上端）
    env = np.clip(up / sp.get('base', 0.12), 0, 1) * np.clip((1 - up) / 0.55, 0, 1) ** 1.3
    a = np.zeros((h, bw), np.float32); rng = np.random.default_rng(rng_seed)
    for j in range(3):
        P = LOOP / rng.choice([4, 5, 6])              # 筋の周期（30秒を割り切る）
        lam = h * rng.uniform(0.45, 0.7); ph = rng.uniform(0, 2 * np.pi)
        sway = periodic(rng, t, 1, 3) * w * 0.12
        cx = bw / 2 + (j - 1) * w * 0.22 + sway * up + np.sin(2 * np.pi * (yy / lam - t / P) + ph) * w * 0.18 * up ** 0.8
        width = w * (0.04 + 0.10 * up)
        dens = 0.55 + 0.45 * np.sin(2 * np.pi * (yy / (lam * 1.7) - t / P) + ph * 1.3)
        a += np.exp(-((xx - cx) / width) ** 2) * dens
    a = cv2.GaussianBlur(a * env, (0, 0), max(1.0, w * 0.02))
    return x0, y0, np.clip(a, 0, 1)


def find_bulbs(s, img):
    x0, y0, x1, y1 = TREE[s]; a = img[y0:y1, x0:x1].astype(np.float32)
    L = a @ [0.299, 0.587, 0.114]; warm = (a[..., 0] >= a[..., 2] + 25)
    m = ((L > 205) & warm).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    pts = [(cx + x0, cy + y0) for (cx, cy), (_, _, w, h, ar) in zip(cen[1:], st[1:]) if 1 <= ar <= 60 and w <= 12 and h <= 12]
    for bx0, by0, bx1, by1 in NOBULB.get(s, []):
        pts = [(x, y) for x, y in pts if not (bx0 <= x < bx1 and by0 <= y < by1)]
    return pts


def bulbs():
    (MAC / '_work').mkdir(parents=True, exist_ok=True)
    for s in TREE:
        img = np.array(Image.open(WORK / f'{s}.png').convert('RGB')); pts = find_bulbs(s, img); v = img.copy()
        for x, y in pts: cv2.circle(v, (int(x), int(y)), 6, (0, 255, 255), 1)
        x0, y0, x1, y1 = TREE[s]
        Image.fromarray(v[y0:y1, x0:x1]).save(MAC / f'_work/電球_{s}.png'); print(s, '電球', len(pts), flush=True)


def snow_layer(s, t, flakes, W, H):
    lay = np.zeros((H, W), np.float32)
    for f in flakes:
        y = (f['y0'] + f['k'] * (H + 20) * t / LOOP) % (H + 20) - 10
        x = (f['x0'] + f['sw'] * np.sin(2 * np.pi * f['ks'] * t / LOOP + f['ph'])) % W
        cv2.circle(lay, (int(x * 4), int(y * 4)), max(1, int(f['r'] * 4)), float(f['a']), -1, cv2.LINE_AA, shift=2)
    return cv2.GaussianBlur(lay, (0, 0), 0.8)


def make_flakes(s, W, H):
    c = SNOW[s]; rng = np.random.default_rng(2400 + SCENES.index(s)); fl = []
    for _ in range(c['n']):
        r = rng.uniform(*c['r']); q = (r - c['r'][0]) / (c['r'][1] - c['r'][0])     # 大きい＝手前＝速い
        k = int(round(c['k'][0] + q * (c['k'][1] - c['k'][0]) + rng.uniform(-0.5, 0.5))); k = max(c['k'][0], min(c['k'][1], k))
        fl.append(dict(x0=rng.uniform(0, W), y0=rng.uniform(0, H + 20), k=k, r=r, a=rng.uniform(*c['a']) * (0.7 + 0.3 * q),
                       sw=rng.uniform(4, 14) * (0.5 + q), ks=int(rng.integers(1, 4)), ph=rng.uniform(0, 2 * np.pi)))
    return fl


def loops():
    LOOPS.mkdir(parents=True, exist_ok=True)
    for s in SCENES:
        out = LOOPS / f'{s}.mp4'
        if out.exists(): continue
        base = np.array(Image.open(WORK / f'{s}.png').convert('RGB')).astype(np.float32)
        if s not in STEAM and s not in SNOW and s not in TREE:
            run(['-loop', 1, '-framerate', FPS, '-i', WORK / f'{s}.png', '-t', LOOP, '-c:v', 'libx264', '-qp', 0, '-preset', 'veryfast',
                 '-g', NF, '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', out])
            print('部品', s, '（静止）', flush=True); continue
        rng = np.random.default_rng(2410 + SCENES.index(s))
        # 電球：5組に分け、組ごとに30秒で整数回まわる揺れ
        groups = []
        if s in TREE:
            pts = find_bulbs(s, base.astype(np.uint8)); x0, y0, x1, y1 = TREE[s]
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32); gm = [np.zeros_like(xx) for _ in range(5)]
            for i, (px, py) in enumerate(pts):
                gm[int(rng.integers(0, 5))] += np.exp(-((xx - px) ** 2 + (yy - py) ** 2) / (2 * 3.2 ** 2))
            for g in gm:
                groups.append((np.clip(g, 0, 1), [int(rng.integers(1, 6)) for _ in range(2)], rng.uniform(0, 2 * np.pi, 2)))
            print(s, '電球', len(pts), flush=True)
        # 雪
        if s in SNOW:
            if SNOW[s].get('full'): sx0, sy0, W, H = 0, 0, 1920, 1080; mask = np.ones((1080, 1920), np.float32)
            else:
                sx0, sy0, W, H = WIN['x0'], WIN['y0'], WIN['x1'] - WIN['x0'], WIN['y1'] - WIN['y0']
                mask = np.ones((H, W), np.float32)
                for hx0, hy0, hx1, hy1 in WIN['holes']:
                    mask[max(0, hy0 - sy0):max(0, hy1 - sy0), max(0, hx0 - sx0):max(0, hx1 - sx0)] = 0
                mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
            flakes = make_flakes(s, W, H)
            col = np.array(SNOW[s].get('col', (238, 242, 250)), np.float32)
        e = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(FPS), '-i', '-', '-an',
                              '-c:v', 'libx264', '-qp', '0', '-preset', 'veryfast', '-g', str(NF), '-pix_fmt', 'yuv420p',
                              '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', str(out)], stdin=subprocess.PIPE)
        for k in range(NF):
            t = k / FPS; img = base.copy()
            if groups:
                x0, y0, x1, y1 = TREE[s]; mod = np.zeros((y1 - y0, x1 - x0), np.float32)
                for g, ks, phs in groups:
                    v = (np.sin(2 * np.pi * ks[0] * t / LOOP + phs[0]) + np.sin(2 * np.pi * ks[1] * t / LOOP + phs[1])) / 2
                    mod += g * v
                img[y0:y1, x0:x1] *= (1 + BULB_DEPTH[s] * mod)[:, :, None]
            for i, sp in enumerate(STEAM.get(s, [])):
                x0, y0, a = steam_field(sp, t, 77 + i); h, w = a.shape
                roi = img[y0:y0 + h, x0:x0 + w]; aa = (a * sp['a'])[:, :, None]
                roi[:] = roi * (1 - aa) + np.array([244, 238, 228], np.float32) * aa
            if s in SNOW:
                lay = (snow_layer(s, t, flakes, W, H) * mask)[:, :, None]
                roi = img[sy0:sy0 + H, sx0:sx0 + W]; roi[:] = roi * (1 - lay) + col * lay
            e.stdin.write(np.uint8(np.clip(img + .5, 0, 255)).tobytes())
        e.stdin.close(); assert e.wait() == 0
        print('部品', s, flush=True)


def check():
    (MAC / '_work').mkdir(parents=True, exist_ok=True)
    for s in SCENES:
        p = LOOPS / f'{s}.mp4'
        for t in (0, 11.5, 22.0):
            run(['-ss', t, '-i', p, '-frames:v', 1, '-q:v', 2, MAC / f'_work/見本_{s}_{t:04.1f}秒.jpg'])
        # 頭と尻の差（ループの継ぎ目）
        # ★全コマを持つと約9GB（11/9 に8GBのMacで強制終了）→ 1コマずつ読み、最初・直前・最後だけ持つ
        c = cv2.VideoCapture(str(p)); first = prev = None; n = 0; steps = []
        while True:
            ok, b = c.read()
            if not ok: break
            b = b.astype(np.int16)
            if first is None: first = b
            elif n % 30 == 0: steps.append(np.abs(b - prev).mean())
            prev = b; n += 1
        seam = np.abs(prev - first).mean()
        print(s, f'コマ数{n} 継ぎ目の差{seam:.3f} ふだんのコマ間{np.mean(steps):.3f}', flush=True)


def card():
    sys.path.insert(0, str(ROOT.parent / 'bgm/IRO/irokit')); import endcard as ec
    bg = np.asarray(Image.open(WORK / 'S6.png').convert('RGB').filter(ImageFilter.GaussianBlur(28))).astype(np.float32) * .62
    ec.build(bg, str(CARD_PNG), greet_ja='あたたかい夜を。', greet_en='Have a cozy Christmas night.')
    ec.check(str(CARD_PNG), str(MAC / '_work/エンドカード_位置検証.png')); print('card ok')


def lengths():
    n = len(SCENES); L = [T / n + XF] * n; L[0] -= XF / 2; L[-1] -= XF / 2
    return L


def final(preview=None, start=0.0):
    L = lengths(); assert abs(sum(L) - (len(L) - 1) * XF - T) < 1e-6
    total = T + OPEN
    a = []
    for s, l in zip(SCENES, L):
        a += ['-stream_loop', -1, '-t', f'{l:.3f}', '-i', LOOPS / f'{s}.mp4']
    fc = ''; prev = '[0:v]'; acc = L[0]
    for i in range(1, len(L)):
        fc += f'{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={acc - XF:.3f}[x{i}];'; prev = f'[x{i}]'; acc += L[i] - XF
    ci = len(L)
    fc += (f'{prev}tpad=start_duration={OPEN}:start_mode=clone,setpts=PTS-STARTPTS,format=yuv420p[v0];'
           f'[{ci}:v]format=rgba,fade=t=in:st={total - CARD_LEN}:d={CARD_XF}:alpha=1[cd];'
           f'[v0][cd]overlay=0:0:enable=gte(t\\,{total - CARD_LEN}),format=yuv420p[v]')
    a += ['-loop', 1, '-framerate', FPS, '-t', total, '-i', CARD_PNG, '-i', BED,
          '-filter_complex', fc, '-map', '[v]', '-map', f'{ci + 1}:a',
          '-c:v', 'libx264', '-crf', 16, '-preset', 'medium', '-g', 240, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', FPS, '-c:a', 'pcm_s24le',
          '-threads', 4, '-filter_complex_threads', 2]   # ★8GBのMacが固まらないよう絞る
    out = WORK / f'見本_{int(start)}秒から.mov' if preview else MAIN0
    if preview: a += ['-ss', start, '-t', preview]
    else: a += ['-t', f'{total:.3f}']
    run(a + [out]); print('final', out)


def door():
    """扉ムービーを入れる（映像）→ 音は IRO22 と同じ式で aac_at に作り直して差し替える（天井0.63・本編部分を測ってから GAIN を決める）。"""
    spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
    tmp = SSD / 'iro24_扉入り_仮.mp4'
    if not tmp.exists():
        # 映像のつなぎ方は 扉ムービーを入れる.py の main と同じ。圧縮だけ libx264 crf16（共通の videotoolbox q85 は静止画中心でも約9.5Mbps になる）
        m = d.dur(d.MOVIE); hold = d.XF + d.BREATH
        fc = (f'[0:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS[a];'
              f'[1:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS,tpad=start_duration={hold}:start_mode=clone[b];'
              f'[a][b]xfade=transition=fade:duration={d.XF}:offset={m - d.XF:.3f}[v]')
        run(['-i', d.MOVIE, '-ss', d.SKIP, '-i', MAIN0, '-filter_complex', fc, '-map', '[v]', '-an',
             '-c:v', 'libx264', '-crf', 16, '-preset', 'medium', '-g', 240, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', 24, '-movflags', '+faststart', tmp])
    M = d.dur(d.MOVIE); au = SSD / '配信用音声.m4a'
    gain = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    fc = (f'[0:a]volume={d.GAIN}dB,aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={M + d.BREATH:.6f}[ma];'
          f'[1:a]asetpts=PTS-STARTPTS,volume={gain}dB,aresample=192000,alimiter=limit=0.63:attack=1:release=60:level=false,alimiter=limit=0.63:attack=1:release=60:level=false,aresample=48000,'
          f'aformat=channel_layouts=stereo,afade=t=in:d={d.FADE_IN}[ba];[ma][ba]concat=n=2:v=0:a=1[pre];[pre]volume=-0.2dB[a]')
    run(['-i', d.MOVIE, '-ss', d.SKIP, '-i', BED, '-filter_complex', fc, '-map', '[a]', '-c:a', 'aac_at', '-b:a', '320k', au])
    OUT.mkdir(parents=True, exist_ok=True)
    run(['-i', tmp, '-i', au, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-shortest', '-movflags', '+faststart', MAIN])
    print('MAIN', MAIN)


if __name__ == '__main__':
    WORK.mkdir(parents=True, exist_ok=True)
    s = sys.argv[1]
    if s == 'final': final(float(sys.argv[2]) if len(sys.argv) > 2 else None, float(sys.argv[3]) if len(sys.argv) > 3 else 0.0)
    else: {'prep': prep, 'bulbs': bulbs, 'loops': loops, 'check': check, 'card': card, 'door': door}[s]()
