"""IRO21 の映像を組む（Claude 2026-10-26。IRO19 の 映像を組む.py・本編を仕上げる.py を下敷きにした）。

背景は開始画像で固定し、女性と犬の範囲だけ Kling 素材を重ねる（窓の外は Kling でも止まっていたが、範囲の外は開始画像のまま）。
走っている感じは「街灯が通り過ぎる光」を計算で足す：橙の光の帯が前（上）から後ろ（下）へ車内をなでる。
60秒の輪（1440コマ）に3〜7秒おき・不規則に入れ、本編ではこれを繰り返して加算で重ねる。

  python iro21_映像を組む.py cache    # Kling 6本を npy に展開（ESD-02）
  python iro21_映像を組む.py parts    # 女性・犬の部品8種
  python iro21_映像を組む.py sweep    # 街灯の光の輪
  python iro21_映像を組む.py card     # 終了カード
  python iro21_映像を組む.py video [秒]  # 本編（秒を付けると頭から見本だけ）
  python iro21_映像を組む.py audio    # 配信用音声
  python iro21_映像を組む.py mux      # 映像＋音声
"""
import sys, json, random, subprocess, importlib.util
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Drive/21_遠回りして帰ろうか')
SSD = Path('/Volumes/ESD-02/IRO/IRO21_素材_ドライブ2時間')
KL = MAC / 'Kling素材'; WORK = SSD / '_映像作業'; PARTS = WORK / 'parts'
REF = MAC / '開始画像/iro21_start_1920.png'
OUT = MAC / '投稿用'; MAIN = OUT / 'iro21_遠回りして帰ろうか_本編_扉入り.mp4'
CARD_PNG = MAC / '_work/iro_エンドカード_IRO21.png'
FPS = 24; T = 7200; CARD = 15 * FPS; N = 192; EDGE = 8; SWEEP = 60 * FPS

WOMAN = [(1080, 420), (1380, 60), (1920, 60), (1920, 1080), (1100, 1080), (1060, 700)]
DOG = ((490, 720), (380, 220))
WINDOW = ((800, 260), (620, 220))   # フロントガラスの外：光は弱く当てる

spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
M = door.dur(door.MOVIE)
PREFIX = round((5 + M + door.BREATH - door.SKIP) * FPS)  # IRO18・19 と同じ式（扉＋間で本編の頭までのコマ数）
TOTAL = round((T + M + door.BREATH - door.SKIP) * FPS)
BODY = TOTAL - PREFIX
ENC = ['-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-profile:v', 'high', '-x264-params', 'keyint=480:min-keyint=240', '-r', str(FPS),
       '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']


def run(a): subprocess.run(['ffmpeg', '-y', '-v', 'error', *map(str, a)], check=True)


def mask_poly(pts, blur=20):
    m = np.zeros((1080, 1920), np.float32); cv2.fillPoly(m, [np.array(pts, np.int32)], 1)
    return cv2.GaussianBlur(m, (0, 0), blur)[:, :, None]


def mask_ell(c, ax, blur=20):
    m = np.zeros((1080, 1920), np.float32); cv2.ellipse(m, c, ax, 0, 0, 360, 1, -1)
    return cv2.GaussianBlur(m, (0, 0), blur)[:, :, None]


def enc(path, rgb=False):
    # 部品は中間物：ほぼ劣化なし（crf 8）で作り、本編で1回だけ圧縮する
    v = ['-c:v', 'libx264rgb', '-crf', '6', '-preset', 'fast'] if rgb else \
        ['-c:v', 'libx264', '-crf', '8', '-preset', 'fast', '-g', '192', '-bf', '0', '-pix_fmt', 'yuv420p',
         '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']
    return subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '24', '-i', '-', '-an', *v, str(path)],
                            stdin=subprocess.PIPE)


def clip(n):
    p = WORK / f'{n}.npy'
    if not p.exists():
        a = np.lib.format.open_memmap(p, mode='w+', dtype=np.uint8, shape=(N, 1080, 1920, 3)); c = cv2.VideoCapture(str(KL / f'iro21_{n}_raw.mp4'))
        for k in range(N):
            ok, b = c.read(); assert ok, (n, k)
            a[k] = cv2.cvtColor(b, cv2.COLOR_BGR2RGB)
        a.flush(); c.release()
    return np.load(p, mmap_mode='r')


def ref():
    return np.array(Image.open(REF).convert('RGB')).astype(np.float32)


def ramp(k):
    a = min(1.0, k / EDGE, (N - 1 - k) / EDGE)
    return a * a * (3 - 2 * a)


def parts():
    """頭と終わりの8コマで開始画像へなじませ、8秒ごとの明るさの跳ねを消す（IRO19 と同じ）。"""
    PARTS.mkdir(parents=True, exist_ok=True); R = ref()
    mw = mask_poly(WOMAN); md = mask_ell(*DOG)
    combos = {'B1': ('B1', 'B1'), 'B2': ('B2', 'B2'), 'A': ('A', 'A'), 'B': ('B', 'B'),
              'B1C': ('B1', 'C'), 'B2C': ('B2', 'C'), 'B1D': ('B1', 'D'), 'B2D': ('B2', 'D')}
    for key, (w, d) in combos.items():
        out = PARTS / f'{key}.mp4'
        if out.exists(): continue
        W, Dg = clip(w), clip(d); e = enc(out)
        for k in range(N):
            a = ramp(k); img = R.copy()
            img = img * (1 - mw * a) + W[k] * (mw * a)
            img = img * (1 - md * a) + Dg[k] * (md * a)
            e.stdin.write(np.uint8(np.clip(img + .5, 0, 255)).tobytes())
        e.stdin.close(); assert e.wait() == 0
        print('部品', key, flush=True)


def sweep():
    """街灯の光の輪（60秒）。黒が「何も足さない」。本編へは加算で重ねる。"""
    rng = random.Random(21202610); t, starts = 1.0, []
    while t + 1.6 < SWEEP / FPS - 0.2:
        starts.append(t); t += rng.uniform(3.0, 7.0)
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    u = yy + 0.3 * np.abs(xx - 960)                       # 上（前）から下と外（後ろ）へ流れる座標
    wmask = 1 - 0.65 * mask_ell(*WINDOW, blur=60)[:, :, 0]  # 窓の外には弱く
    col = np.array([42, 27, 12], np.float32)               # 橙（8bit で足す量の最大）
    dur, sig = 1.4, 260.0
    e = enc(WORK / '街灯の輪.mp4', rgb=True)
    for k in range(SWEEP):
        s = k / FPS; I = np.zeros((1080, 1920), np.float32)
        for st in starts:
            p = (s - st) / dur
            if 0 <= p <= 1:
                env = np.sin(np.pi * p) ** 1.5                   # 現れて消える
                I += env * np.exp(-((u - (-300 + 1800 * p)) ** 2) / (2 * sig ** 2))
        img = (I * wmask)[:, :, None] * col
        e.stdin.write(np.uint8(np.clip(img + .5, 0, 255)).tobytes())
    e.stdin.close(); assert e.wait() == 0
    (WORK / '街灯の輪.json').write_text(json.dumps({'starts_sec': [round(x, 2) for x in starts], 'duration': dur, 'peak_rgb_add': col.tolist()}))
    print('街灯の輪', len(starts), '回／60秒', flush=True)


def plan():
    """10分（75部品）ごとに A 街の灯り・C あくび・B 犬へ微笑む・D 犬が見上げる。土台は B1/B2 を不規則に（同じのは2回まで）。"""
    rng = random.Random(21192026); n = -(-BODY // N); seq = []
    ev = {12: 'A', 28: 'C', 45: 'B', 60: 'D'}
    for i in range(n):
        base = rng.choice(['B1', 'B2'])
        if len(seq) >= 2 and seq[-1][:2] == seq[-2][:2] == base: base = 'B2' if base == 'B1' else 'B1'
        e = ev.get(i % 75)
        last = i * N + N > BODY - CARD
        if e and not last: seq.append(e if e in 'AB' else base + e)
        else: seq.append(base)
    chapters = [(i, s[-1]) for i, s in enumerate(seq) if s.endswith(('C', 'D'))]
    data = {'prefix_frames': PREFIX, 'total_frames': TOTAL, 'body_frames': BODY, 'parts': seq,
            'chapters': [{'part': i, 'kind': k, 'seconds': (PREFIX + i * N) / FPS} for i, k in chapters]}
    (WORK / '構成.json').write_text(json.dumps(data, ensure_ascii=False, indent=1)); return data


def card():
    sys.path.insert(0, str(ROOT.parent / 'bgm/IRO/irokit')); import endcard as ec
    bg = np.asarray(Image.open(REF).convert('RGB').filter(ImageFilter.GaussianBlur(28))) * .72
    ec.build(bg, str(CARD_PNG), greet_ja='遠回りも、悪くなかったね。', greet_en='The long way was worth it.')
    ec.check(str(CARD_PNG), str(MAC / '_work/エンドカード_位置検証.png')); print('card ok')


SWEEP_FC = '[{b}]format=gbrp[bb];[{s}]format=gbrp[ss];[bb][ss]blend=all_mode=addition,format=yuv420p'


def video(preview=None):
    data = plan(); frames = BODY if not preview else int(preview * FPS)
    lst = WORK / '本編_連結.txt'; lst.write_text(''.join(f"file '{PARTS / (k + '.mp4')}'\n" for k in data['parts']))
    body = WORK / ('本編_見本.mp4' if preview else '本編.mp4')
    st = (BODY - CARD) / FPS
    fc = ('[0:v]setpts=PTS-STARTPTS[b0];[1:v]setpts=PTS-STARTPTS[s0];' + SWEEP_FC.format(b='b0', s='s0') + '[x];'
          f'[2:v]setpts=PTS-STARTPTS,format=rgba,fade=t=in:st={st:.6f}:d=2:alpha=1[c];[x][c]overlay=0:0:enable=gte(t\\,{st:.6f}),format=yuv420p[v]')
    run(['-f', 'concat', '-safe', '0', '-i', lst, '-stream_loop', '-1', '-i', WORK / '街灯の輪.mp4',
         '-loop', '1', '-framerate', FPS, '-i', CARD_PNG, '-filter_complex', fc, '-map', '[v]', '-an',
         '-frames:v', frames, *ENC, body])
    if preview: print('見本', body); return
    # 扉：本編の頭へ溶ける「導入19コマ」は B1 部品の最後19コマに街灯の輪の最後19コマを足したもの（輪の頭へつながる）
    lead = WORK / '導入19コマ.mp4'
    run(['-ss', 173 / FPS, '-i', PARTS / 'B1.mp4', '-ss', (SWEEP - 19) / FPS, '-i', WORK / '街灯の輪.mp4',
         '-filter_complex', '[0:v]setpts=PTS-STARTPTS[b0];[1:v]setpts=PTS-STARTPTS[s0];' + SWEEP_FC.format(b='b0', s='s0') + '[v]',
         '-map', '[v]', '-frames:v', 19, *ENC, lead])
    prefix = WORK / '扉と間.mp4'
    fc = ('[0:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS[a];[1:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS,'
          'tpad=start_duration=2.5:start_mode=clone[b];[a][b]xfade=transition=fade:duration=1:offset=19.333333,format=yuv420p[v]')
    run(['-i', door.MOVIE, '-i', lead, '-filter_complex', fc, '-map', '[v]', '-an', '-frames:v', PREFIX, *ENC, prefix])
    (WORK / '完成映像_連結.txt').write_text(f"file '{prefix}'\nfile '{body}'\n")
    print('video ok', PREFIX, BODY, TOTAL)


def audio():
    bed = MAC / '_work/music_bed.wav'; out = WORK / '配信用音声.m4a'
    fc = (f'[0:a]volume={door.GAIN}dB,aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={M + door.BREATH:.6f}[ma];'
          f'[1:a]asetpts=PTS-STARTPTS,aresample=192000,alimiter=limit=0.56:attack=1:release=60:level=false,alimiter=limit=0.56:attack=1:release=60:level=false,aresample=48000,'
          f'aformat=channel_layouts=stereo,afade=t=in:d={door.FADE_IN},afade=t=out:st={T - door.SKIP - 10:.6f}:d=10[ba];[ma][ba]concat=n=2:v=0:a=1[pre];[pre]volume=-0.2dB[a]')
    run(['-i', door.MOVIE, '-ss', door.SKIP, '-t', T - door.SKIP, '-i', bed, '-filter_complex', fc, '-map', '[a]', '-c:a', 'aac_at', '-b:a', '320k', out])
    print('audio ok', out)


def mux():
    OUT.mkdir(parents=True, exist_ok=True)
    run(['-f', 'concat', '-safe', '0', '-i', WORK / '完成映像_連結.txt', '-i', WORK / '配信用音声.m4a', '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', MAIN])
    print('MAIN', MAIN)


if __name__ == '__main__':
    WORK.mkdir(parents=True, exist_ok=True)
    s = sys.argv[1]
    if s == 'cache':
        for n in ['B1', 'B2', 'A', 'B', 'C', 'D']: clip(n); print('展開', n, flush=True)
    elif s == 'video': video(float(sys.argv[2]) if len(sys.argv) > 2 else None)
    else: {'parts': parts, 'sweep': sweep, 'card': card, 'audio': audio, 'mux': mux, 'plan': lambda: print(json.dumps(plan()['chapters'][:4]))}[s]()
