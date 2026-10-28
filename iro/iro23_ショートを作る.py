"""IRO23 ショート4本（各15秒・1080×1920）を場面の30秒の部品から切り出す（IRO22 の ショートを作る.py を写した・Claude 2026-10-28）。

Kling が無いので、動きは湯気・灯りのゆらぎと、15秒で3%のごくゆっくりした寄り。
★IRO21 の本人指摘（同じ切り抜きだと絵がほぼ同じ）→ 4本とも場面と寄り引きを変える：
  A＝S2 雨の窓とマグを持つ女性（608×1080）／B＝S3 手元の寄りと湯気（608×1080）／C＝S4 撫でられて眠る犬の寄り（456×810）／D＝S5 夜の窓越し（540×960）
音は4本とも別の楽器の曲の30秒目から15秒。
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

MAC = Path('/Users/ryo/Desktop/BGM/IRO/Cafe/23_雨やどりのつもりだった'); SSD = Path('/Volumes/ESD-02/IRO/IRO23_素材_雨やどりのカフェ2時間')
LOOPS = SSD / '_映像作業/loops'; OUT = MAC / '投稿用'; W = MAC / '_work'; SONGS = Path('/Volumes/ESD-02/Suno書き出し/IRO23_全48曲/wav')
JP = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'; AV = '/System/Library/Fonts/Avenir Next.ttc'
#   場面・切り抜き (x, y, 幅, 高さ)・字の位置・題（2行）・曲（選曲と時刻.json で本編に使った曲から各種1曲）
SC = [('A', 'S2', (740, 0, 608, 1080), 'bottom', ['雨が上がるまで、', 'あと一杯。'], 'A'),
      ('B', 'S3', (1076, 0, 608, 1080), 'bottom', ['ページをめくる', '音だけ。'], 'C'),
      ('C', 'S4', (790, 270, 456, 810), 'top', ['となりの寝息が、', 'いちばん落ち着く。'], 'B'),
      ('D', 'S5', (790, 60, 540, 960), 'bottom', ['気づけば、', '灯りがついていた。'], 'D')]


def run(a): subprocess.run(['ffmpeg', '-y', '-v', 'error', *map(str, a)], check=True)


def overlay(tag, where, lines):
    top = 1430 if where == 'bottom' else 110
    y = np.arange(1920); a = np.clip(np.minimum(y - (top - 140), (top + 470) - y) / 140, 0, 1) * 165
    band = Image.new('RGBA', (1080, 1920), (24, 14, 10, 0)); band.putalpha(Image.fromarray(np.repeat(a[:, None], 1080, axis=1).astype('uint8')))
    lay = Image.new('RGBA', band.size); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((66, top, 560, top + 56), 28, fill=(123, 91, 69, 255))
    d.text((90, top + 6), 'MOCHA  |  Café Jazz Lo-fi', font=ImageFont.truetype(AV, 34, index=2), fill='white')
    for i, t in enumerate(lines): d.text((65, top + 85 + i * 105), t, font=ImageFont.truetype(JP, 84), fill='white')
    d.text((70, top + 328), 'カフェBGM 2時間・本編は関連動画から', font=ImageFont.truetype(JP, 34), fill=(255, 215, 90, 255))
    shade = Image.new('RGBA', band.size, (0, 8, 8, 0)); shade.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(7)))
    p = W / f'short_{tag}_文字.png'; Image.alpha_composite(Image.alpha_composite(band, shade), lay).save(p); return p


def song_for(kind):
    used = [t['name'] for t in json.loads((SSD / '選曲と時刻.json').read_text())['tracks']]
    return next(n for n in used if n.startswith(kind))


if __name__ == '__main__':
    W.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True); info = []
    for tag, scene, (x, y, w, h), where, lines, kind in SC:
        ov = overlay(tag, where, lines); v = W / f'short_{tag}_映像.mp4'; a = W / f'short_{tag}_音声.wav'; fin = OUT / f'iro23_ショート_{tag}.mp4'
        song = song_for(kind)
        # 2倍に拡大してから zoompan で 15秒かけて 1.00→1.03 倍（整数の丸めでがたつかないように）
        z = "1+0.03*on/359"
        run(['-t', 15, '-i', LOOPS / f'{scene}.mp4', '-i', ov, '-filter_complex',
             f'[0:v]crop={w}:{h}:{x}:{y},scale=2160:3840:flags=lanczos,zoompan=z=\'{z}\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d=1:s=1080x1920:fps=24[b];'
             f'[b][1:v]overlay=0:0,format=yuv420p[v]',
             '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-frames:v', 360, v])
        run(['-ss', 30, '-t', 15, '-i', SONGS / f'iro23_{song}.wav', '-af', 'loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,afade=t=in:d=0.4,afade=t=out:st=13.8:d=1.2', '-c:a', 'pcm_s24le', a])
        run(['-i', v, '-i', a, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', 'aresample=192000,alimiter=limit=0.60:attack=1:release=60:level=false,aresample=48000',
             '-c:a', 'aac_at', '-b:a', '256k', '-t', 15, '-movflags', '+faststart', fin])
        m = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(fin), '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
        I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', m)[-1]); TP = float(re.findall(r'Peak:\s+(-?[\d.]+)', m)[-1])
        yavg = subprocess.run(f"ffmpeg -v error -i '{fin}' -vf fps=1,signalstats,metadata=print:file=- -f null - | awk -F= '/YAVG/{{s+=$2;n++}} END{{print s/n}}'",
                              shell=True, capture_output=True, text=True).stdout.strip()
        info.append({'tag': tag, 'scene': scene, 'crop': [x, y, w, h], 'title': ''.join(lines), 'song': song, 'LUFS': I, 'TP': TP, '平均輝度': float(yavg)})
        print(info[-1], flush=True)
    (W / 'ショート設定.json').write_text(json.dumps(info, ensure_ascii=False, indent=1))
