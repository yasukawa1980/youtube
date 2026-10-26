"""IRO22 の映像を組む（Claude 2026-10-27。IRO21 の 映像を組む.py・IRO14 の 画面とサムネを作る.py を下敷きにした）。

背景は開始画像で固定し、女性と犬の範囲だけ Kling 素材を重ねる（8秒＝192コマの部品6種）。部品を900個並べて2時間にする。
出来事はタイマーに合わせる：作業 4:00 ひと口・11:00 あくび・18:00 ひと口／25:00 直前に伸び（チャイムと同時）・27:00 撫でる。
「日が暮れるまで」は計算で足す：30分目から全体を少しずつ青く暗く（eq の時刻の式）、窓は群青へ、ランプの灯りは60分目から点く。

  python iro22_映像を組む.py cache          # Kling 6本を npy に展開（ESD-02）
  python iro22_映像を組む.py parts          # 部品6種
  python iro22_映像を組む.py masks          # 重ねる範囲の確認画像
  python iro22_映像を組む.py layers         # 窓の群青・ランプの灯り（RGBA の PNG）
  python iro22_映像を組む.py timer          # タイマーの PNG（1秒1枚・7200枚）
  python iro22_映像を組む.py tcheck         # タイマーと夕暮れの見本（0・45・75・115分）
  python iro22_映像を組む.py card           # 終了カード
  python iro22_映像を組む.py final [秒] [開始秒]  # 扉なしの本編（頭 OPEN 秒は本編の最初のコマで止める）。秒を付けると見本
  python iro22_映像を組む.py door           # 扉ムービーを入れ、音を aac_at で作り直して差し替える
"""
import sys, json, random, subprocess, importlib.util, os
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Study/22_日が暮れるまで集中する')
SSD = Path('/Volumes/ESD-02/IRO/IRO22_素材_夕方のポモドーロ2時間')
KL = MAC / 'Kling素材'; WORK = SSD / '_映像作業'; PARTS = WORK / 'parts'; TDIR = WORK / 'timer'
REF = MAC / '開始画像/iro22_start_1920.png'
BED = SSD / 'music_bed.wav'
OUT = MAC / '投稿用'; MAIN0 = SSD / 'iro22_完成_扉なし.mp4'; MAIN = Path('/Volumes/ESD-02/BGM/IRO/Study/22_日が暮れるまで集中する/投稿用/iro22_日が暮れるまで集中する_本編_扉入り.mp4')
CARD_PNG = MAC / '_work/iro_エンドカード_IRO22.png'
LAYER_WIN = WORK / '窓の群青.png'; LAYER_LAMP = WORK / 'ランプの灯り.png'
FPS = 24; N = 192; EDGE = 8
OPEN = 4.2
FOCUS, BREAK, BLOCKS = 1500, 300, 4
T = BLOCKS * (FOCUS + BREAK)
CARD_LEN, CARD_XF = 15, 2
AV = '/System/Library/Fonts/Avenir Next.ttc'

# 重ねる範囲：女性（伸びの腕が上端まで届く）と足元の犬
WOMAN = ((760, 0), (1640, 880))
DOG = ((1070, 830), (390, 200))
# 窓（空と家並み）：夕暮れで群青に寄せる範囲
WINDOW = [(0, 0), (800, 0), (800, 470), (210, 470), (0, 420)]
LAMP = (1480, 315)          # ランプの笠の中心
# タイマーの板（x, y, 幅, 高さ）：窓の空の中。太陽（約 312,279）には掛けない
TBOX = (330, 36, 430, 230)
# 夕暮れの版（静止の色調整）。本編では30分目から120分目へ透明度を 0→1 にして重ねる
DUSK = 'eq=brightness=-0.11:saturation=0.80,colorchannelmixer=rr=0.78:gg=0.86:bb=1.06'


def run(a): subprocess.run(['ffmpeg', '-y', '-v', 'error', *map(str, a)], check=True)


def dur(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)],
                                capture_output=True, text=True).stdout)


def soft_rect(a, b, blur=30):
    m = np.zeros((1080, 1920), np.float32); cv2.rectangle(m, a, b, 1, -1)
    return cv2.GaussianBlur(m, (0, 0), blur)[:, :, None]


def soft_ell(c, ax, blur=24):
    m = np.zeros((1080, 1920), np.float32); cv2.ellipse(m, c, ax, 0, 0, 360, 1, -1)
    return cv2.GaussianBlur(m, (0, 0), blur)[:, :, None]


def mask():
    return np.maximum(soft_rect(*WOMAN), soft_ell(*DOG))


def enc(path):
    # 部品は中間物：ほぼ劣化なし（crf 8）で作り、本編で1回だけ圧縮する
    v = ['-c:v', 'libx264', '-crf', '8', '-preset', 'fast', '-g', '192', '-bf', '0', '-pix_fmt', 'yuv420p',
         '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']
    return subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1920x1080', '-r', '24', '-i', '-', '-an', *v, str(path)],
                            stdin=subprocess.PIPE)


def clip(n):
    p = WORK / f'{n}.npy'
    if not p.exists():
        a = np.lib.format.open_memmap(p, mode='w+', dtype=np.uint8, shape=(N, 1080, 1920, 3)); c = cv2.VideoCapture(str(KL / f'iro22_{n}_raw.mp4'))
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
    """頭と終わりの8コマで開始画像へなじませ、8秒ごとの明るさの跳ねを消す（IRO19・21 と同じ）。"""
    PARTS.mkdir(parents=True, exist_ok=True); R = ref(); m = mask()
    for key in ['B1', 'B2', 'A', 'B', 'C', 'D']:
        out = PARTS / f'{key}.mp4'
        if out.exists(): continue
        C = clip(key); e = enc(out)
        for k in range(N):
            a = m * ramp(k)
            img = R * (1 - a) + C[k] * a
            e.stdin.write(np.uint8(np.clip(img + .5, 0, 255)).tobytes())
        e.stdin.close(); assert e.wait() == 0
        print('部品', key, flush=True)


def masks():
    R = ref(); m = mask()
    show = R * (0.45 + 0.55 * m)
    cv2.imwrite(str(MAC / '_work/重ねる範囲.jpg'), cv2.cvtColor(np.uint8(show), cv2.COLOR_RGB2BGR))
    # Kling の動いた範囲がはみ出していないか：素材ごとに「動いた画素のうち範囲の外にある割合」
    res = {}
    for key in ['B1', 'B2', 'A', 'B', 'C', 'D']:
        C = clip(key); mv = np.zeros((1080, 1920), bool)
        for k in range(0, N, 4): mv |= np.abs(C[k].astype(np.int16) - C[0]).max(2) > 18
        res[key] = round(float((mv & (m[:, :, 0] < 0.5)).sum() / max(1, mv.sum()) * 100), 2)
    print('動いた画素のうち範囲の外（%）', res)


def layers():
    """窓の群青（窓の中を濃い青で覆う）・ランプの灯り（笠のまわりの暖かい光）。どちらも RGBA。"""
    WORK.mkdir(parents=True, exist_ok=True)
    m = np.zeros((1080, 1920), np.float32); cv2.fillPoly(m, [np.array(WINDOW, np.int32)], 1)
    m = cv2.GaussianBlur(m, (0, 0), 18)
    win = np.zeros((1080, 1920, 4), np.uint8); win[..., :3] = (30, 42, 96); win[..., 3] = np.uint8(m * 175)
    Image.fromarray(win, 'RGBA').save(LAYER_WIN)
    yy, xx = np.mgrid[0:1080, 0:1920].astype(np.float32)
    d = np.hypot((xx - LAMP[0]) / 1.0, (yy - LAMP[1]) / 0.8)
    g = np.exp(-(d / 110) ** 2) * 0.9 + np.exp(-(d / 300) ** 2) * 0.28
    lamp = np.zeros((1080, 1920, 4), np.uint8); lamp[..., :3] = (255, 184, 104); lamp[..., 3] = np.uint8(np.clip(g, 0, 1) * 170)
    Image.fromarray(lamp, 'RGBA').save(LAYER_LAMP)
    print('layers ok')


# ---- タイマー（IRO14 の描き方。板は夕方の部屋に合わせて焦げ茶） ----
def timer_png(label, remain, frac):
    bw, bh = TBOX[2], TBOX[3]
    im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0))
    pm = Image.new('L', (bw, bh), 0); ImageDraw.Draw(pm).rounded_rectangle((0, 0, bw - 1, bh - 1), 26, fill=255)
    panel = Image.new('RGBA', (bw, bh), (52, 34, 26, 0)); panel.putalpha(pm.point(lambda v: int(v * 0.5)))
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
            yield f'FOCUS  {b + 1} / {BLOCKS}', FOCUS - s, s / FOCUS
        for s in range(BREAK):
            yield 'BREAK', BREAK - s, s / BREAK


def timer():
    TDIR.mkdir(parents=True, exist_ok=True)
    for n, (lab, rem, fr) in enumerate(timer_seq()):
        p = TDIR / f'{n:05d}.png'
        if not p.exists(): timer_png(lab, rem, fr).save(p, compress_level=1)
    print('タイマー', n + 1, '枚', flush=True)


def plan():
    """30分の輪ごとに出来事を置き、土台は B1 を主に B2 を不規則に混ぜる（B2 は 4〜5秒目に約1秒目を閉じるので少なめ）。"""
    rng = random.Random(22102720); n = -(-(T + 1) * FPS // N); seq = []
    U = (FOCUS + BREAK) // 8   # 225部品＝30分
    ev = {30: 'C', 82: 'D', 135: 'C', 187: 'A', 202: 'B'}   # 4:00・10:56・18:00・24:56（伸びの腕が上がるのが約25:00）・26:56
    for i in range(n):
        base = 'B2' if rng.random() < 0.3 else 'B1'
        if seq and seq[-1] == 'B2' == base: base = 'B1'
        e = ev.get(i % U)
        last = (i * N + N) / FPS > T - CARD_LEN
        seq.append(e if e and not last else base)
    data = {'parts': seq, 'events_sec_in_unit': {k: v * 8 for v, k in ev.items()}}
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / '構成.json').write_text(json.dumps(data, ensure_ascii=False, indent=1)); return seq


def tcheck():
    """タイマーと夕暮れの見本：0・45・75・115分の静止画を ffmpeg の本番と同じ式で作る。"""
    for mi in (0, 45, 75, 115):
        t = mi * 60; k = min(1, max(0, (t - 1800) / 5400)); kl = min(1, max(0, (t - 3600) / 1800))
        out = MAC / f'_work/夕暮れ見本_{mi:03d}分.jpg'
        fc = (f'[0:v]format=yuv420p,split[b0][d0];[d0]{DUSK},format=rgba,colorchannelmixer=aa={k:.4f}[dk];[b0][dk]overlay=0:0[g];'
              f'[1:v]format=rgba,colorchannelmixer=aa={k:.4f}[w];[g][w]overlay=0:0[g2];'
              f'[2:v]format=rgba,colorchannelmixer=aa={kl:.4f}[l];[g2][l]overlay=0:0[g3];'
              f'[3:v]format=rgba[tm];[g3][tm]overlay={TBOX[0]}:{TBOX[1]}')
        tp = TDIR / f'{min(t, T - 1):05d}.png'
        run(['-i', REF, '-i', LAYER_WIN, '-i', LAYER_LAMP, '-i', tp, '-filter_complex', fc, '-frames:v', 1, '-q:v', 3, out])
        print(out)


def card():
    sys.path.insert(0, str(ROOT.parent / 'bgm/IRO/irokit')); import endcard as ec
    bg = np.asarray(Image.open(REF).convert('RGB').filter(ImageFilter.GaussianBlur(28))).astype(np.float32) * .62
    bg[..., 2] *= 1.08
    ec.build(bg, str(CARD_PNG), greet_ja='今日も、よくがんばりました。', greet_en='You did great today.')
    ec.check(str(CARD_PNG), str(MAC / '_work/エンドカード_位置検証.png')); print('card ok')


def final(preview=None, start=0.0):
    seq = plan()
    lst = WORK / '本編_連結.txt'; lst.write_text(''.join(f"file '{PARTS / (k + '.mp4')}'\n" for k in seq))
    total = T + OPEN
    out = WORK / f'見本_{int(start)}秒から.mp4' if preview else MAIN0
    # 本編の時刻 t は OPEN を含む。夕暮れの式・タイマーは本編の 0 秒＝OPEN 後から数える
    fc = (f'[0:v]tpad=start_duration={OPEN}:start_mode=clone,setpts=PTS-STARTPTS,format=yuv420p,split[b0][d0];'
          f'[d0]{DUSK},format=rgba,fade=t=in:st={OPEN + 1800}:d=5400:alpha=1[dk];[b0][dk]overlay=0:0[g];'
          f'[1:v]format=rgba,fade=t=in:st={OPEN + 1800}:d=5400:alpha=1[w];[g][w]overlay=0:0:shortest=0[g2];'
          f'[2:v]format=rgba,fade=t=in:st={OPEN + 3600}:d=1800:alpha=1[l];[g2][l]overlay=0:0[g3];'
          f'[3:v]fps={FPS},format=rgba[tm];[g3][tm]overlay={TBOX[0]}:{TBOX[1]}:eof_action=pass[v1];'
          f'[4:v]format=rgba,fade=t=in:st={total - CARD_LEN}:d={CARD_XF}:alpha=1[cd];'
          f'[v1][cd]overlay=0:0:enable=gte(t\\,{total - CARD_LEN}),format=yuv420p[v]')
    a = ['-f', 'concat', '-safe', '0', '-i', lst,
         '-loop', 1, '-framerate', FPS, '-t', total, '-i', LAYER_WIN,
         '-loop', 1, '-framerate', FPS, '-t', total, '-i', LAYER_LAMP,
         '-itsoffset', OPEN, '-framerate', 1, '-i', TDIR / '%05d.png',
         '-loop', 1, '-framerate', FPS, '-t', total, '-i', CARD_PNG,
         '-i', BED,
         '-filter_complex', fc, '-map', '[v]', '-map', '5:a',
         '-c:v', 'h264_videotoolbox', '-q:v', 85, '-profile:v', 'high', '-r', FPS,
         '-c:a', 'pcm_s24le']
    if preview: a += ['-ss', start, '-t', preview]
    else: a += ['-t', f'{total:.3f}']
    out = out.with_suffix('.mov')
    run(a + [out]); print('final', out)


def door():
    """扉ムービーを入れる（映像）→ 音は IRO21 と同じ式で aac_at に作り直して差し替える。
    ★10/27 1回目は本編の部分が −14.9 LUFS・TP −4.7（IRO21 の天井 0.56 のまま）→ +0.9dB・天井 0.63 にした"""
    spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)
    tmp = SSD / 'iro22_扉入り_仮.mp4'
    if not tmp.exists(): d.main(str(MAIN0.with_suffix('.mov')), str(tmp))   # 映像はできていれば使い回し、音だけ作り直す
    M = d.dur(d.MOVIE); au = SSD / '配信用音声.m4a'
    fc = (f'[0:a]volume={d.GAIN}dB,aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={M + d.BREATH:.6f}[ma];'
          f'[1:a]asetpts=PTS-STARTPTS,volume=0.9dB,aresample=192000,alimiter=limit=0.63:attack=1:release=60:level=false,alimiter=limit=0.63:attack=1:release=60:level=false,aresample=48000,'
          f'aformat=channel_layouts=stereo,afade=t=in:d={d.FADE_IN}[ba];[ma][ba]concat=n=2:v=0:a=1[pre];[pre]volume=-0.2dB[a]')
    run(['-i', d.MOVIE, '-ss', d.SKIP, '-i', BED, '-filter_complex', fc, '-map', '[a]', '-c:a', 'aac_at', '-b:a', '320k', au])
    OUT.mkdir(parents=True, exist_ok=True)
    run(['-i', tmp, '-i', au, '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-shortest', '-movflags', '+faststart', MAIN])
    print('MAIN', MAIN)


if __name__ == '__main__':
    WORK.mkdir(parents=True, exist_ok=True)
    s = sys.argv[1]
    if s == 'cache':
        for n in ['B1', 'B2', 'A', 'B', 'C', 'D']: clip(n); print('展開', n, flush=True)
    elif s == 'final': final(float(sys.argv[2]) if len(sys.argv) > 2 else None, float(sys.argv[3]) if len(sys.argv) > 3 else 0.0)
    else: {'parts': parts, 'masks': masks, 'layers': layers, 'timer': timer, 'tcheck': tcheck, 'card': card, 'door': door,
           'plan': lambda: print(len(plan()))}[s]()
