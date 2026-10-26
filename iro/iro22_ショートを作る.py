"""IRO22 ショート4本（各15秒・1080×1920）を完成本編から切り出す（IRO21 の ショートを作る.py を写した・Claude 2026-10-27）。

映像は本編の最初の30分の出来事の頭から15秒（夕暮れの色はまだ掛かっていない・タイマーは切り抜きの外）。
★IRO21 の本人指摘（同じ切り抜きだと出来事が違っても絵がほぼ同じ）→ 4本とも場面と寄り引きを変える：
  A 伸び＝女性の全身（608×1080）／B 撫でる＝女性と犬の頭の引き（608×1080）／C ひと口＝女性とマグの寄り（540×960）／D あくび＝犬の顔の寄り（456×810）
音は4本とも別の楽器の曲の30秒目から15秒（ローズ・ジャズギター・フリューゲル・メロディカ）。
"""
import json, re, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MAC = Path('/Users/ryo/Desktop/BGM/IRO/Study/22_日が暮れるまで集中する'); SSD = Path('/Volumes/ESD-02/IRO/IRO22_素材_夕方のポモドーロ2時間')
MAIN = MAC / '投稿用/iro22_日が暮れるまで集中する_本編_扉入り.mp4'
OUT = MAC / '投稿用'; W = MAC / '_work'; SONGS = Path('/Volumes/ESD-02/Suno書き出し/IRO22_全56曲')
JP = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'; AV = '/System/Library/Fonts/Avenir Next.ttc'
data = json.loads((SSD / '_映像作業/構成.json').read_text())
# 扉入りの本編で、扉ムービーの分だけ本編が後ろへずれる：扉の長さ＋間 − 本編の頭の OPEN
import importlib.util
spec = importlib.util.spec_from_file_location('door', '/Users/ryo/youtube/bgm/IRO/irokit/扉ムービーを入れる.py'); door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
SHIFT = door.dur(door.MOVIE) + door.BREATH - door.SKIP
OPEN = 4.2
first = {k: next(i for i, s in enumerate(data['parts']) if s == k) for k in 'ABCD'}
#   切り抜きは (x, y, 幅, 高さ)・字の位置（top / bottom）
SC = [('A', (920, 0, 608, 1080), 'bottom', ['西日の中で、', 'のびをひとつ。'], 'iro22_A-01b.wav'),
      ('B', (700, 0, 608, 1080), 'top', ['休憩の合図は、', 'この手のひら。'], 'iro22_B-02a.wav'),
      ('C', (780, 40, 540, 960), 'bottom', ['冷めないうちに、', 'ひと口。'], 'iro22_C-01b.wav'),
      ('D', (650, 270, 456, 810), 'top', ['夕焼けにつられて、', '大あくび。'], 'iro22_F-01b.wav')]


def run(a): subprocess.run(['ffmpeg', '-y', '-v', 'error', *map(str, a)], check=True)


def overlay(tag, where, lines):
    top = 1430 if where == 'bottom' else 110
    y = np.arange(1920); a = np.clip(np.minimum(y - (top - 140), (top + 470) - y) / 140, 0, 1) * 165
    band = Image.new('RGBA', (1080, 1920), (24, 14, 10, 0)); band.putalpha(Image.fromarray(np.repeat(a[:, None], 1080, axis=1).astype('uint8')))
    lay = Image.new('RGBA', band.size); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((66, top, 560, top + 56), 28, fill=(192, 138, 62, 255))
    d.text((90, top + 6), 'OCHRE  |  Study Lo-fi', font=ImageFont.truetype(AV, 34, index=2), fill='white')
    for i, t in enumerate(lines): d.text((65, top + 85 + i * 105), t, font=ImageFont.truetype(JP, 84), fill='white')
    d.text((70, top + 328), 'ポモドーロ2時間・本編は関連動画から', font=ImageFont.truetype(JP, 34), fill=(255, 215, 90, 255))
    shade = Image.new('RGBA', band.size, (0, 8, 8, 0)); shade.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(7)))
    p = W / f'short_{tag}_文字.png'; Image.alpha_composite(Image.alpha_composite(band, shade), lay).save(p); return p


info = []
for tag, x, where, lines, song in SC:
    start = SHIFT + OPEN + first[tag] * 192 / 24
    ov = overlay(tag, where, lines); v = W / f'short_{tag}_映像.mp4'; a = W / f'short_{tag}_音声.wav'; fin = OUT / f'iro22_ショート_{tag}.mp4'
    run(['-ss', start, '-t', 15, '-i', MAIN, '-i', ov, '-filter_complex', f'[0:v]crop={x[2]}:{x[3]}:{x[0]}:{x[1]},scale=1080:1920:flags=lanczos[b];[b][1:v]overlay=0:0,format=yuv420p[v]',
         '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-frames:v', 360, v])
    run(['-ss', 30, '-t', 15, '-i', SONGS / song, '-af', 'loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,afade=t=in:d=0.4,afade=t=out:st=13.8:d=1.2', '-c:a', 'pcm_s24le', a])
    run(['-i', v, '-i', a, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'aresample=192000,alimiter=limit=0.60:attack=1:release=60:level=false,aresample=48000',
         '-c:a', 'aac_at', '-b:a', '256k', '-t', 15, '-movflags', '+faststart', fin])
    m = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(fin), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', m)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+)', m)[-1])
    info.append({'tag': tag, 'start_in_main': start, 'crop_x': x, 'title': ''.join(lines), 'song': song, 'LUFS': I, 'TP': TP})
    print(tag, round(start, 2), I, TP, flush=True)
(W / 'ショート設定.json').write_text(json.dumps(info, ensure_ascii=False, indent=1))
