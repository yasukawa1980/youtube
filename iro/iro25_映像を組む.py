"""IRO25 の映像を組む（Claude 2026-11-21。iro24_映像を組む.py の場面と雪・湯気に、iro22_映像を組む.py のタイマーを足した）。

Kling は使わない。場面の静止画6枚（S1〜S6）を1回のポモドーロ（30分）に1枚ずつ。
境目は8秒の溶かしで、休憩の最後の8秒に溶け終わる（作業中は絵を変えない）。
動きは計算で足す：窓の外の雪（S2・S3・S4・S5。S1 はまだ降らず、S6 はやんで積もっている）、湯気（S3・S6 の2杯目）、タイマー。
ランプの揺らぎは入れない（電気スタンドが揺れると故障に見える。設計から外した）。
どれも30秒で一周する式で作り、30秒の部品（無劣化 -qp 0）を繰り返す（継ぎ目なし）。

  python iro25_映像を組む.py prep            # 1672→1920 に拡大。S6 は周辺を落とし、暗部が多ければ持ち上げる（ESD-02 の _映像作業/）
  python iro25_映像を組む.py loops           # 場面ごとの30秒の部品
  python iro25_映像を組む.py check           # 部品から見本の静止画と継ぎ目の差
  python iro25_映像を組む.py timer           # タイマーの PNG（1秒1枚・10800枚）
  python iro25_映像を組む.py tcheck          # 各場面にタイマーを重ねた見本
  python iro25_映像を組む.py card            # 終了カード
  python iro25_映像を組む.py final [秒] [開始秒]  # 扉なしの本編。秒を付けると見本
  python iro25_映像を組む.py door [gain]     # 扉ムービーを入れ、音を aac_at で作り直して差し替える
"""
import sys, json, subprocess, importlib.util
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageFilter, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Study/25_雪が積もるまで集中する')
SSD = Path('/Volumes/ESD-02/IRO/IRO25_素材_冬のポモドーロ3時間')
SRC = MAC / '開始画像'; WORK = SSD / '_映像作業'; LOOPS = WORK / 'loops'; TDIR = WORK / 'timer'
BED = SSD / 'music_bed.wav'
OUT = MAC / '投稿用'; MAIN0 = SSD / 'iro25_完成_扉なし.mov'
MAIN = OUT / 'iro25_雪が積もるまで集中する_本編_扉入り.mp4'
CARD_PNG = MAC / '_work/iro_エンドカード_IRO25.png'
FPS = 24; LOOP = 30; NF = FPS * LOOP
OPEN = 4.2
FOCUS, BREAK, BLOCKS = 1500, 300, 6
T = BLOCKS * (FOCUS + BREAK)
SCENES = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
FILES = {'S1': 'iro25_S1_案1.png', 'S2': 'iro25_S2.png', 'S3': 'iro25_S3.png', 'S4': 'iro25_S4.png', 'S5': 'iro25_S5.png', 'S6': 'iro25_S6.png'}
XF = 8
CARD_LEN, CARD_XF = 15, 2
AV = '/System/Library/Fonts/Avenir Next.ttc'

# タイマーの板（x, y, 幅, 高さ・1920基準）：6場面とも右上の壁。S1/S6 のランプの笠（約1493〜1587, 360〜453）より上
TBOX = (1400, 60, 430, 230)
# 板の色：回ごとに午後の灰青 → 夜の群青
PANEL = [(66, 76, 92), (60, 70, 88), (54, 62, 82), (44, 52, 76), (36, 44, 70), (30, 36, 62)]

# 湯気：液面の中心（1920基準）・縁の幅・立ちのぼる高さ・濃さ
STEAM = {
    'S3': [dict(x=1600, y=418, w=150, h=300, a=0.55, base=0.04)],   # 手元の寄りのマグ。背景は灰色の壁
    'S6': [dict(x=1493, y=566, w=62, h=90, a=0.50)],                # 2杯目（右のマグ）。上にランプの笠があるので低く
}
# 窓ガラス（1920基準）と、雪を降らせない所（桟・手前の鉢植え・ランプ）
WIN_ROOM = dict(x0=123, x1=742, y0=86, y1=502,
                holes=[(444, 0, 461, 1080), (0, 295, 1920, 314), (30, 405, 385, 1080)])
WIN = {
    'S2': WIN_ROOM, 'S4': WIN_ROOM,
    'S3': dict(x0=100, x1=868, y0=0, y1=274, holes=[(486, 0, 514, 1080), (0, 105, 382, 1080)]),
    'S5': dict(x0=447, x1=1008, y0=0, y1=314, holes=[(699, 0, 717, 1080), (0, 86, 1920, 108), (438, 198, 742, 1080), (0, 0, 492, 122)]),
}
# 雪：数・大きさ（半径px）・30秒で何回落ちきるか・濃さ・ぼかし
SNOW = {
    'S2': dict(n=80, r=(1.4, 3.0), k=(2, 3), a=(0.85, 1.0), col=(255, 255, 255)),   # 降り始め。明るい灰色の空でも見える濃さ（IRO24 S2 の教訓）
    'S3': dict(n=120, r=(2.4, 4.6), k=(2, 3), a=(0.8, 1.0), col=(255, 255, 255), blur=1.6),  # 奥の窓・ピントの外。★初版 n70・a0.55〜0.85・blur2.2 は明るい空に溶けて見えなかった
    'S4': dict(n=150, r=(1.0, 2.6), k=(2, 4), a=(0.55, 0.9)),
    'S5': dict(n=110, r=(1.6, 3.6), k=(2, 4), a=(0.5, 0.85), blur=1.4),             # 犬の寄りの奥の窓
}
DARK_TARGET = 4.0   # 16未満の画素の割合（%）をこれ以下へ
VIGNETTE = {'S6': dict(cx=1350, cy=470, r=1150, depth=0.30)}   # S6 はランプ以外を少し暗く（絵は壁が明るめに描かれた）


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
        d0 = dark(im)
        if s in VIGNETTE:
            v = VIGNETTE[s]; yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
            r = np.sqrt((xx - v['cx']) ** 2 + (yy - v['cy']) ** 2) / v['r']
            g = 1 - v['depth'] * np.clip(r, 0, 1) ** 1.6
            im = np.uint8(np.clip(im * g[:, :, None] + .5, 0, 255))
        L = 0
        while dark(np.uint8(toe(L)[im] + .5)) > DARK_TARGET and L < 12: L += 1
        out = np.uint8(toe(L)[im] + .5) if L else im
        Image.fromarray(out).save(WORK / f'{s}.png')
        rep[s] = dict(暗部_元=round(d0, 2), 周辺減光=s in VIGNETTE, 持ち上げ=L, 暗部_後=round(dark(out), 2))
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
    up = 1 - yy / h
    env = np.clip(up / sp.get('base', 0.12), 0, 1) * np.clip((1 - up) / 0.55, 0, 1) ** 1.3
    a = np.zeros((h, bw), np.float32); rng = np.random.default_rng(rng_seed)
    for j in range(3):
        P = LOOP / rng.choice([4, 5, 6])
        lam = h * rng.uniform(0.45, 0.7); ph = rng.uniform(0, 2 * np.pi)
        sway = periodic(rng, t, 1, 3) * w * 0.12
        cx = bw / 2 + (j - 1) * w * 0.22 + sway * up + np.sin(2 * np.pi * (yy / lam - t / P) + ph) * w * 0.18 * up ** 0.8
        width = w * (0.04 + 0.10 * up)
        dens = 0.55 + 0.45 * np.sin(2 * np.pi * (yy / (lam * 1.7) - t / P) + ph * 1.3)
        a += np.exp(-((xx - cx) / width) ** 2) * dens
    a = cv2.GaussianBlur(a * env, (0, 0), max(1.0, w * 0.02))
    return x0, y0, np.clip(a, 0, 1)


def snow_layer(s, t, flakes, W, H):
    lay = np.zeros((H, W), np.float32)
    for f in flakes:
        y = (f['y0'] + f['k'] * (H + 20) * t / LOOP) % (H + 20) - 10
        x = (f['x0'] + f['sw'] * np.sin(2 * np.pi * f['ks'] * t / LOOP + f['ph'])) % W
        cv2.circle(lay, (int(x * 4), int(y * 4)), max(1, int(f['r'] * 4)), float(f['a']), -1, cv2.LINE_AA, shift=2)
    return cv2.GaussianBlur(lay, (0, 0), SNOW[s].get('blur', 0.8))


def make_flakes(s, W, H):
    c = SNOW[s]; rng = np.random.default_rng(2500 + SCENES.index(s)); fl = []
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
        if s not in STEAM and s not in SNOW:
            run(['-loop', 1, '-framerate', FPS, '-i', WORK / f'{s}.png', '-t', LOOP, '-c:v', 'libx264', '-qp', 0, '-preset', 'veryfast',
                 '-g', NF, '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', out])
            print('部品', s, '（静止）', flush=True); continue
        if s in SNOW:
            w = WIN[s]; sx0, sy0, W, H = w['x0'], w['y0'], w['x1'] - w['x0'], w['y1'] - w['y0']
            mask = np.ones((H, W), np.float32)
            for hx0, hy0, hx1, hy1 in w['holes']:
                mask[max(0, hy0 - sy0):max(0, hy1 - sy0), max(0, hx0 - sx0):max(0, hx1 - sx0)] = 0
            mask = cv2.GaussianBlur(mask, (0, 0), 1.0)
            flakes = make_flakes(s, W, H)
            col = np.array(SNOW[s].get('col', (238, 242, 250)), np.float32)
        e = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(FPS), '-i', '-', '-an',
                              '-c:v', 'libx264', '-qp', '0', '-preset', 'veryfast', '-g', str(NF), '-pix_fmt', 'yuv420p',
                              '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', str(out)], stdin=subprocess.PIPE)
        for k in range(NF):
            t = k / FPS; img = base.copy()
            for i, sp in enumerate(STEAM.get(s, [])):
                x0, y0, a = steam_field(sp, t, 77 + i); h, w_ = a.shape
                roi = img[y0:y0 + h, x0:x0 + w_]; aa = (a * sp['a'])[:, :, None]
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
        # ★全コマを持つと約9GB → 1コマずつ読み、最初・直前・最後だけ持つ
        c = cv2.VideoCapture(str(p)); first = prev = None; n = 0; steps = []
        while True:
            ok, b = c.read()
            if not ok: break
            b = b.astype(np.int16)
            if first is None: first = b
            elif n % 30 == 0: steps.append(np.abs(b - prev).mean())
            prev = b; n += 1
        seam = np.abs(prev - first).mean()
        print(s, f'コマ数{n} 継ぎ目の差{seam:.3f} ふだんのコマ間{np.mean(steps) if steps else 0:.3f}', flush=True)


# ---- タイマー（IRO14・22 の描き方。板は回ごとに灰青→群青） ----
def timer_png(label, remain, frac, b):
    bw, bh = TBOX[2], TBOX[3]
    im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    pm = Image.new('L', (bw, bh), 0); ImageDraw.Draw(pm).rounded_rectangle((0, 0, bw - 1, bh - 1), 26, fill=255)
    panel = Image.new('RGBA', (bw, bh), PANEL[b] + (0,)); panel.putalpha(pm.point(lambda v: int(v * 0.5)))
    im = Image.alpha_composite(im, panel)
    d = ImageDraw.Draw(im)
    fb = ImageFont.truetype(AV, 116, index=5); fl = ImageFont.truetype(AV, 26, index=2)

    def sp(y, t, f, tr):
        w = sum(d.textlength(c, font=f) for c in t) + tr * (len(t) - 1); x = (bw - w) / 2
        for c in t:
            d.text((x, y), c, font=f, fill=(255, 255, 255, 250)); x += d.textlength(c, font=f) + tr
    sp(24, label, fl, 10)
    sp(52, '%02d:%02d' % (remain // 60, remain % 60), fb, 4)
    barw = 300; x0 = (bw - barw) // 2; y = 196
    d.rounded_rectangle((x0, y, x0 + barw, y + 5), 2, fill=(255, 255, 255, 55))
    if frac > 0:
        d.rounded_rectangle((x0, y, x0 + max(5, int(barw * frac)), y + 5), 2, fill=(255, 255, 255, 240))
    return im


def timer_seq():
    for b in range(BLOCKS):
        for s in range(FOCUS):
            yield f'FOCUS  {b + 1} / {BLOCKS}', FOCUS - s, s / FOCUS, b
        for s in range(BREAK):
            yield 'BREAK', BREAK - s, s / BREAK, b


def timer():
    TDIR.mkdir(parents=True, exist_ok=True)
    for n, (lab, rem, fr, b) in enumerate(timer_seq()):
        p = TDIR / f'{n:05d}.png'
        if not p.exists(): timer_png(lab, rem, fr, b).save(p, compress_level=1)
    print('タイマー', n + 1, '枚', flush=True)


def tcheck():
    """各場面の見本（作業の始め・休憩中）にタイマーを重ねる。"""
    (MAC / '_work').mkdir(parents=True, exist_ok=True)
    for b, s in enumerate(SCENES):
        for sec, tag in ((b * 1800 + 60, '作業'), (b * 1800 + 1620, '休憩')):
            out = MAC / f'_work/タイマー見本_{s}_{tag}.jpg'
            run(['-i', WORK / f'{s}.png', '-i', TDIR / f'{sec:05d}.png', '-filter_complex', f'[0:v][1:v]overlay={TBOX[0]}:{TBOX[1]}',
                 '-frames:v', 1, '-q:v', 3, out])
        print(s, flush=True)


def card():
    sys.path.insert(0, str(ROOT.parent / 'bgm/IRO/irokit')); import endcard as ec
    bg = np.asarray(Image.open(WORK / 'S6.png').convert('RGB').filter(ImageFilter.GaussianBlur(28))).astype(np.float32) * .62
    bg[..., 2] *= 1.06
    ec.build(bg, str(CARD_PNG), greet_ja='雪の夜に、おつかれさま。', greet_en='You did great tonight.')
    ec.check(str(CARD_PNG), str(MAC / '_work/エンドカード_位置検証.png')); print('card ok')


def lengths():
    """1枚目は30分、2枚目以降は 30分＋溶かし。溶かしは各回の休憩の最後の8秒（本編の 1792〜1800秒など）。"""
    L = [1800.0] + [1800.0 + XF] * (len(SCENES) - 1)
    assert abs(sum(L) - (len(L) - 1) * XF - T) < 1e-6
    return L


def final(preview=None, start=0.0):
    L = lengths(); total = T + OPEN
    a = []
    for s, l in zip(SCENES, L):
        a += ['-stream_loop', -1, '-t', f'{l:.3f}', '-i', LOOPS / f'{s}.mp4']
    fc = ''; prev = '[0:v]'; acc = L[0]
    for i in range(1, len(L)):
        fc += f'{prev}[{i}:v]xfade=transition=fade:duration={XF}:offset={acc - XF:.3f}[x{i}];'; prev = f'[x{i}]'; acc += L[i] - XF
    ti, ci, ai = len(L), len(L) + 1, len(L) + 2
    fc += (f'{prev}tpad=start_duration={OPEN}:start_mode=clone,setpts=PTS-STARTPTS,format=yuv420p[v0];'
           f'[{ti}:v]fps={FPS},format=rgba[tm];[v0][tm]overlay={TBOX[0]}:{TBOX[1]}:eof_action=pass[v1];'
           f'[{ci}:v]format=rgba,fade=t=in:st={total - CARD_LEN}:d={CARD_XF}:alpha=1[cd];'
           f'[v1][cd]overlay=0:0:enable=gte(t\\,{total - CARD_LEN}),format=yuv420p[v]')
    a += ['-itsoffset', OPEN, '-framerate', 1, '-i', TDIR / '%05d.png',
          '-loop', 1, '-framerate', FPS, '-t', total, '-i', CARD_PNG, '-i', BED,
          '-filter_complex', fc, '-map', '[v]', '-map', f'{ai}:a',
          '-c:v', 'libx264', '-crf', 16, '-preset', 'medium', '-g', 240, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', FPS, '-c:a', 'pcm_s24le',
          '-threads', 4, '-filter_complex_threads', 2]   # ★8GBのMacが固まらないよう絞る
    out = WORK / f'見本_{int(start)}秒から.mov' if preview else MAIN0
    if preview: a += ['-ss', start, '-t', preview]
    else: a += ['-t', f'{total:.3f}']
    run(a + [out]); print('final', out)


def door():
    """扉ムービーを入れる（映像）→ 音は IRO22・24 と同じ式で aac_at に作り直して差し替える（天井0.63・本編部分を測ってから GAIN を決める）。"""
    spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
    tmp = SSD / 'iro25_扉入り_仮.mp4'
    if not tmp.exists():
        m = d.dur(d.MOVIE); hold = d.XF + d.BREATH
        fc = (f'[0:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS[a];'
              f'[1:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS,tpad=start_duration={hold}:start_mode=clone[b];'
              f'[a][b]xfade=transition=fade:duration={d.XF}:offset={m - d.XF:.3f}[v]')
        run(['-i', d.MOVIE, '-ss', d.SKIP, '-i', MAIN0, '-filter_complex', fc, '-map', '[v]', '-an',
             '-c:v', 'libx264', '-crf', 16, '-preset', 'medium', '-g', 240, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', 24, '-movflags', '+faststart',
             '-threads', 4, tmp])
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
    else: {'prep': prep, 'loops': loops, 'check': check, 'timer': timer, 'tcheck': tcheck, 'card': card, 'door': door}[s]()
