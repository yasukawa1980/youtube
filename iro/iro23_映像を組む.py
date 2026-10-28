"""IRO23 の映像を組む（Claude 2026-10-28。IRO22 の 映像を組む.py を下敷きにした）。

Kling は使わない。場面の静止画6枚（S1〜S6）を約20分ずつ並べ、境目は8秒の溶かし。
動きは計算で足す：マグの湯気（S2・S3・S4・S6）と、灯りのゆらぎ（S4・S5・S6。S1・S2 はランプがうっすらなので足さない）。
湯気もゆらぎも30秒で一周する式で作り、30秒の部品を繰り返して20分にする（継ぎ目なし）。
★部品は無劣化（-qp 0・1周に I フレーム1枚）。10/28 初版の crf10・-g 240 は10秒ごとのキーフレームで画が平均0.47段跳ね、
  全コマ I（-g 1）にするとコマごとの圧縮のざらつきで差が約1.0に増え、頭のコマも1.6跳ねた。

  python iro23_映像を組む.py prep            # 1672→1920 に拡大、夜の絵は暗部を少し持ち上げる（ESD-02 の _映像作業/）
  python iro23_映像を組む.py loops           # 場面ごとの30秒の部品（湯気・灯り入り）
  python iro23_映像を組む.py check           # 部品から見本の静止画（湯気の濃い瞬間）と暗部の割合
  python iro23_映像を組む.py card            # 終了カード
  python iro23_映像を組む.py final [秒] [開始秒]  # 扉なしの本編（頭 OPEN 秒は最初のコマで止める）。秒を付けると見本
  python iro23_映像を組む.py door            # 扉ムービーを入れ、音を aac_at で作り直して差し替える
"""
import sys, json, subprocess, importlib.util
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Cafe/23_雨やどりのつもりだった')
SSD = Path('/Volumes/ESD-02/IRO/IRO23_素材_雨やどりのカフェ2時間')
SRC = MAC / '開始画像'; WORK = SSD / '_映像作業'; LOOPS = WORK / 'loops'
BED = SSD / 'music_bed.wav'
OUT = MAC / '投稿用'; MAIN0 = SSD / 'iro23_完成_扉なし.mov'
MAIN = OUT / 'iro23_雨やどりのつもりだった_本編_扉入り.mp4'
CARD_PNG = MAC / '_work/iro_エンドカード_IRO23.png'
FPS = 24; LOOP = 30; NF = FPS * LOOP
OPEN = 4.2
T = 7200
SCENES = ['S1', 'S2', 'S3', 'S4', 'S5', 'S6']
FILES = {'S1': 'iro23_S1_案2.png', 'S2': 'iro23_S2.png', 'S3': 'iro23_S3.png', 'S4': 'iro23_S4.png', 'S5': 'iro23_S5.png', 'S6': 'iro23_S6.png'}
XF = 8
CARD_LEN, CARD_XF = 15, 2

# 湯気：マグの液面の中心（1920基準）・縁の幅・立ちのぼる高さ・濃さ
STEAM = {
    'S2': [dict(x=1045, y=306, w=51, h=70, a=0.35)],     # 顔の前なので低く薄く
    'S3': [dict(x=1380, y=482, w=250, h=360, a=0.70, base=0.04)],   # 明るい雨の町が背景なので濃いめ。液面の奥（y≈482）から立てる
    'S4': [dict(x=880, y=432, w=51, h=120, a=0.50)],
    'S6': [dict(x=969, y=434, w=50, h=115, a=0.50)],     # 手前の2杯目だけ（左の1杯目は冷めている）
    # ★10/28 初版は a=0.16〜0.20・筋の幅 0.07〜0.23w・ぼかし 0.035w で、背景に溶けて見えなかった
}
# 灯り：中心（1920基準）・半径・ゆらぎの深さ
LAMPS = {
    'S4': [(1200, 60, 120, .035), (1562, 100, 120, .035), (1613, 362, 150, .03)],
    'S5': [(1045, 220, 90, .035), (1148, 258, 90, .035), (1255, 427, 90, .03),
           (287, 150, 110, .05), (322, 333, 70, .05), (365, 396, 55, .05), (471, 434, 45, .05)],
    'S6': [(1200, 60, 120, .035), (1562, 100, 120, .035), (1613, 362, 150, .03)],
}
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


def loops():
    LOOPS.mkdir(parents=True, exist_ok=True)
    for s in SCENES:
        out = LOOPS / f'{s}.mp4'
        if out.exists(): continue
        base = np.array(Image.open(WORK / f'{s}.png').convert('RGB')).astype(np.float32)
        if s not in STEAM and s not in LAMPS:
            run(['-loop', 1, '-framerate', FPS, '-i', WORK / f'{s}.png', '-t', LOOP, '-c:v', 'libx264', '-qp', 0, '-preset', 'veryfast',
                 '-g', NF, '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', out])
            print('部品', s, '（静止）', flush=True); continue
        yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
        glows = [(np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)), dep) for cx, cy, r, dep in LAMPS.get(s, [])]
        rng = np.random.default_rng(2310 + SCENES.index(s))
        fl = [(g, dep, [rng.integers(2, 9) for _ in range(4)], rng.uniform(0, 2 * np.pi, 4)) for g, dep in glows]
        e = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', str(FPS), '-i', '-', '-an',
                              '-c:v', 'libx264', '-qp', '0', '-preset', 'veryfast', '-g', str(NF), '-pix_fmt', 'yuv420p',
                              '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', str(out)], stdin=subprocess.PIPE)
        for k in range(NF):
            t = k / FPS; img = base.copy()
            for g, dep, ks, phs in fl:
                v = sum(np.sin(2 * np.pi * kk * t / LOOP + p) for kk, p in zip(ks, phs)) / 4
                img *= (1 + dep * v * g)[:, :, None]
            for i, sp in enumerate(STEAM.get(s, [])):
                x0, y0, a = steam_field(sp, t, 77 + i); h, w = a.shape
                roi = img[y0:y0 + h, x0:x0 + w]; aa = (a * sp['a'])[:, :, None]
                roi[:] = roi * (1 - aa) + np.array([244, 238, 228], np.float32) * aa
            e.stdin.write(np.uint8(np.clip(img + .5, 0, 255)).tobytes())
        e.stdin.close(); assert e.wait() == 0
        print('部品', s, flush=True)


def check():
    (MAC / '_work').mkdir(parents=True, exist_ok=True)
    for s in SCENES:
        p = LOOPS / f'{s}.mp4'
        for t in (0, 11.5):
            run(['-ss', t, '-i', p, '-frames:v', 1, '-q:v', 2, MAC / f'_work/見本_{s}_{t:04.1f}秒.jpg'])
        # 頭と尻の差（ループの継ぎ目）
        c = cv2.VideoCapture(str(p)); fr = []
        while True:
            ok, b = c.read()
            if not ok: break
            fr.append(b.astype(np.int16))
        seam = np.abs(fr[-1] - fr[0]).mean(); step = np.mean([np.abs(fr[i + 1] - fr[i]).mean() for i in range(0, len(fr) - 1, 30)])
        print(s, f'コマ数{len(fr)} 継ぎ目の差{seam:.3f} ふだんのコマ間{step:.3f}', flush=True)


def card():
    sys.path.insert(0, str(ROOT.parent / 'bgm/IRO/irokit')); import endcard as ec
    bg = np.asarray(Image.open(WORK / 'S6.png').convert('RGB').filter(ImageFilter.GaussianBlur(28))).astype(np.float32) * .62
    ec.build(bg, str(CARD_PNG), greet_ja='ゆっくり、できましたか。', greet_en='Hope you had a cozy time.')
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
          '-c:v', 'libx264', '-crf', 16, '-preset', 'medium', '-g', 240, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', FPS, '-c:a', 'pcm_s24le']
    out = WORK / f'見本_{int(start)}秒から.mov' if preview else MAIN0
    if preview: a += ['-ss', start, '-t', preview]
    else: a += ['-t', f'{total:.3f}']
    run(a + [out]); print('final', out)


def door():
    """扉ムービーを入れる（映像）→ 音は IRO22 と同じ式で aac_at に作り直して差し替える（天井0.63・本編部分を測ってから GAIN を決める）。"""
    spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
    tmp = SSD / 'iro23_扉入り_仮.mp4'
    if not tmp.exists(): d.main(str(MAIN0), str(tmp))
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
    else: {'prep': prep, 'loops': loops, 'check': check, 'card': card, 'door': door}[s]()
