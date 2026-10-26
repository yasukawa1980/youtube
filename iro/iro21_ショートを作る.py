"""IRO21 ショート4本（IRO19 の ショートを作る.py を写した）（各15秒・1080×1920）を完成本編から切り出す（Claude 2026-10-21）。

A 街の灯り・B 犬へ微笑む＝運転する女性の切り抜き（字は下）／C あくび・D 見上げる＝犬の切り抜き（字は上）。
映像は本編の出来事の頭から15秒（街灯の光は本編で重ね済み）。犬は幅608に尾の先まで入らない（本人了承）。音は系統ごとの曲の30秒目から15秒。
"""
import json, re, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MAC = Path('/Users/ryo/Desktop/BGM/IRO/Drive/21_遠回りして帰ろうか'); SSD = Path('/Volumes/ESD-02/IRO/IRO21_素材_ドライブ2時間')
MAIN = MAC / '投稿用/iro21_遠回りして帰ろうか_本編_扉入り.mp4'
OUT = MAC / '投稿用'; W = MAC / '_work'; SONGS = MAC / '楽曲/wav'
JP = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'; AV = '/System/Library/Fonts/Avenir Next.ttc'
data = json.loads((SSD / '_映像作業/構成.json').read_text()); P = data['prefix_frames']
first = {k: next(i for i, s in enumerate(data['parts']) if s.endswith(k)) for k in 'ABCD'}
# 10/27 本人「同じスタートの動画が2本ずつ」→ v02：同じ絵が続かないよう切り抜きを4本とも変えた（v01 は残置）
#   A＝フロントガラスの湾と橋の灯り／B＝運転する女性／C＝犬の引き／D＝犬の顔の寄り（456×810を拡大）
#   切り抜きは (x, y, 幅, 高さ)
SC = [('A', (780, 0, 608, 1080), ['遠くの灯りに、', 'ちょっと寄り道。'], 'iro21_A-03a.wav'),
      ('B', (1290, 0, 608, 1080), ['助手席の寝息を、', '聞きながら。'], 'iro21_B-01a.wav'),
      ('C', (150, 0, 608, 1080), ['助手席で、', '大きなあくび。'], 'iro21_C-01b.wav'),
      ('D', (152, 270, 456, 810), ['まだ着かないの？', 'おやすみ。'], 'iro21_F-02b.wav')]


def run(a): subprocess.run(['ffmpeg', '-y', '-v', 'error', *map(str, a)], check=True)


def overlay(tag, lines):
    top = 1430 if tag in 'AB' else 170
    y = np.arange(1920); a = np.clip(np.minimum(y - (top - 140), (top + 470) - y) / 140, 0, 1) * 165
    band = Image.new('RGBA', (1080, 1920), (24, 14, 10, 0)); band.putalpha(Image.fromarray(np.repeat(a[:, None], 1080, axis=1).astype('uint8')))
    lay = Image.new('RGBA', band.size); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((66, top, 700, top + 56), 28, fill=(156, 74, 46, 255))
    d.text((90, top + 6), 'RUST  |  Night Drive Chill', font=ImageFont.truetype(AV, 34, index=2), fill='white')
    for i, t in enumerate(lines): d.text((65, top + 85 + i * 105), t, font=ImageFont.truetype(JP, 84), fill='white')
    d.text((70, top + 328), 'ドライブBGM 2時間・本編は関連動画から', font=ImageFont.truetype(JP, 34), fill=(255, 215, 90, 255))
    shade = Image.new('RGBA', band.size, (0, 8, 8, 0)); shade.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(7)))
    p = W / f'short_{tag}_文字.png'; Image.alpha_composite(Image.alpha_composite(band, shade), lay).save(p); return p


info = []
for tag, x, lines, song in SC:
    start = (P + first[tag] * 192) / 24
    ov = overlay(tag, lines); v = W / f'short_{tag}_映像.mp4'; a = W / f'short_{tag}_音声.wav'; fin = OUT / f'iro21_ショート_{tag}_v02.mp4'
    run(['-ss', start, '-t', 15, '-i', MAIN, '-i', ov, '-filter_complex', f'[0:v]crop={x[2]}:{x[3]}:{x[0]}:{x[1]},scale=1080:1920:flags=lanczos[b];[b][1:v]overlay=0:0,format=yuv420p[v]',
         '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-frames:v', 360, v])
    run(['-ss', 30, '-t', 15, '-i', SONGS / song, '-af', 'loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,afade=t=in:d=0.4,afade=t=out:st=13.8:d=1.2', '-c:a', 'pcm_s24le', a])
    run(['-i', v, '-i', a, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'aresample=192000,alimiter=limit=0.60:attack=1:release=60:level=false,aresample=48000',
         '-c:a', 'aac_at', '-b:a', '256k', '-t', 15, '-movflags', '+faststart', fin])
    m = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(fin), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', m)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+)', m)[-1])
    info.append({'tag': tag, 'start_in_main': start, 'crop_x': x, 'title': ''.join(lines), 'song': song, 'LUFS': I, 'TP': TP})
    print(tag, round(start, 2), I, TP, flush=True)
(W / 'ショート設定_v02.json').write_text(json.dumps(info, ensure_ascii=False, indent=1))
