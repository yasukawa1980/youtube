"""完成本編の出来事の頭から15秒、4種類の音源で縦ショートを作る。"""
from pathlib import Path
import argparse
import json
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / 'iro/volumes/iro20.yaml').read_text())
BASE = Path(CFG['dir']); WORK = BASE / '_work/ショート_v01'; OUT = BASE / '投稿用'
MAIN = OUT / 'iro20_しおりを挟むにはまだ早い_本編_扉入り.mp4'
PLAN = BASE / '_work/映像_v01/構成.json'
JP = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'; AV = '/System/Library/Fonts/Avenir Next.ttc'
SCENES = [('A', 760, ['物語の外にも、', '灯りがある。'], 'iro20_A-01b.wav'),
          ('B', 800, ['先に眠った、', '読書仲間。'], 'iro20_C-01a.wav'),
          ('C', 1040, ['この一冊は、', '夢で読む。'], 'iro20_D-01b.wav'),
          ('D', 1040, ['まだ読んでる？', 'おやすみ。'], 'iro20_E-01b.wav')]


def ff(args):
    subprocess.run(['ffmpeg', '-v', 'error', *map(str, args)], check=True)


def overlay(tag, lines, lead='本編2時間はチャンネルから', suffix=''):
    top = 1430 if tag in 'AB' else 170
    y = np.arange(1920)
    alpha = np.clip(np.minimum(y - (top - 140), (top + 470) - y) / 140, 0, 1) * 178
    band = Image.new('RGBA', (1080, 1920), (33, 21, 35, 0))
    band.putalpha(Image.fromarray(np.repeat(alpha[:, None], 1080, axis=1).astype('uint8')))
    text = Image.new('RGBA', band.size); d = ImageDraw.Draw(text)
    d.rounded_rectangle((66, top, 750, top + 56), 28, fill=(87, 56, 83, 255))
    d.text((90, top + 6), 'PLUM  |  Chamber Chill', font=ImageFont.truetype(AV, 34, index=2), fill='white')
    for i, line in enumerate(lines):
        d.text((65, top + 85 + i * 105), line, font=ImageFont.truetype(JP, 84), fill='white')
    d.text((70, top + 328), f'読書BGM・{lead}',
           font=ImageFont.truetype(JP, 32), fill=(255, 221, 111, 255))
    shade = Image.new('RGBA', band.size, (0, 0, 0, 0))
    shade.putalpha(text.getchannel('A').filter(ImageFilter.GaussianBlur(7)))
    dest = WORK / f'{tag}_文字{suffix}.png'
    Image.alpha_composite(Image.alpha_composite(band, shade), text).save(dest)
    return dest


def measure(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-vn',
                        '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True, check=True)
    return {'lufs': float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1]),
            'true_peak_dbtp': float(re.findall(r'Peak:\s+(-?[\d.]+)', r.stderr)[-1])}


def main():
    if not MAIN.exists():
        raise FileNotFoundError(MAIN)
    WORK.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text()); rows = []
    for tag, crop_x, lines, song in SCENES:
        dest = OUT / f'iro20_ショート_{tag}.mp4'
        if dest.exists():
            raise FileExistsError(f'既存の完成候補を保全: {dest}')
        start = plan['first_events'][tag]['seconds']; text = overlay(tag, lines)
        video = WORK / f'{tag}_映像.mp4'; audio = WORK / f'{tag}_音声.wav'
        if not video.exists():
            ff(['-ss', start, '-t', 15, '-i', MAIN, '-i', text, '-filter_complex',
                f'[0:v]crop=608:1080:{crop_x}:0,scale=1080:1920:flags=lanczos[b];[b][1:v]overlay=0:0,format=yuv420p[v]',
                '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', 18, '-preset', 'fast', '-threads', 4,
                '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                '-colorspace', 'bt709', '-color_range', 'tv', '-r', 24, '-frames:v', 360, video])
        if not audio.exists():
            ff(['-ss', 30, '-t', 15, '-i', BASE / '楽曲' / song, '-af',
                'loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,afade=t=in:d=0.3,afade=t=out:st=13.8:d=1.2',
                '-ac', 2, '-c:a', 'pcm_s24le', audio])
        ff(['-i', video, '-i', audio, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af',
            'aresample=192000,alimiter=limit=0.60:attack=1:release=60:level=false,aresample=48000',
            '-c:a', 'aac_at', '-b:a', '256k', '-t', 15, '-movflags', '+faststart', dest])
        rows.append({'tag': tag, 'source_main_start': start, 'crop': [crop_x, 0, 608, 1080],
                     'title': ''.join(lines), 'song': song, 'source_audio_start': 30,
                     'file': str(dest), 'bytes': dest.stat().st_size, **measure(dest),
                     'direct_listening': 'not_performed'})
        (ROOT / 'iro/iro20_ショート検品.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
        print(tag, rows[-1], flush=True)


def repair_levels():
    """初稿を保全し、A/Bだけ測定値に基づくゲインで別版にする。"""
    report = ROOT / 'iro/iro20_ショート検品.json'
    rows = json.loads(report.read_text())
    cfg = yaml.safe_load((ROOT / 'iro/volumes/iro20.yaml').read_text())
    files = {tag: str(OUT / f'iro20_ショート_{tag}.mp4') for tag in 'ABCD'}
    for row in rows:
        tag = row['tag']
        if tag not in 'AB':
            continue
        dest = OUT / f'iro20_ショート_{tag}_v02.mp4'
        if dest.exists():
            raise FileExistsError(dest)
        gain = -14 - row['lufs']
        ff(['-i', WORK / f'{tag}_映像.mp4', '-i', WORK / f'{tag}_音声.wav',
            '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af',
            f'volume={gain:.3f}dB,aresample=192000,alimiter=limit=0.70:attack=1:release=60:level=false,aresample=48000',
            '-c:a', 'aac_at', '-b:a', '256k', '-t', 15, '-movflags', '+faststart', dest])
        row['previous_version'] = dict(file=row['file'], lufs=row['lufs'], true_peak_dbtp=row['true_peak_dbtp'])
        row.update(file=str(dest), bytes=dest.stat().st_size, level_repair_gain_db=gain, **measure(dest))
        files[tag] = str(dest)
        print('repaired', tag, row['lufs'], row['true_peak_dbtp'], flush=True)
    cfg['shorts']['files'] = files
    (ROOT / 'iro/volumes/iro20.yaml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    report.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')


def retext():
    """誘導文を説明文と同じ「関連動画から」にしたv03。音声は投稿用と同じ処理で作り直す。"""
    report = ROOT / 'iro/iro20_ショート検品.json'
    rows = {r['tag']: r for r in json.loads(report.read_text())}
    cfg = yaml.safe_load((ROOT / 'iro/volumes/iro20.yaml').read_text())
    files = {}
    for tag, crop_x, lines, song in SCENES:
        row = rows[tag]
        dest = OUT / f'iro20_ショート_{tag}_v03.mp4'
        if dest.exists():
            raise FileExistsError(dest)
        text = overlay(tag, lines, '本編2時間は関連動画から', '_v03')
        video = WORK / f'{tag}_映像_v03.mp4'
        ff(['-ss', row['source_main_start'], '-t', 15, '-i', MAIN, '-i', text, '-filter_complex',
            f'[0:v]crop=608:1080:{crop_x}:0,scale=1080:1920:flags=lanczos[b];[b][1:v]overlay=0:0,format=yuv420p[v]',
            '-map', '[v]', '-an', '-c:v', 'libx264', '-crf', 18, '-preset', 'fast', '-threads', 4,
            '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709',
            '-colorspace', 'bt709', '-color_range', 'tv', '-r', 24, '-frames:v', 360, video])
        gain = row.get('level_repair_gain_db')
        chain = (f'volume={gain:.3f}dB,aresample=192000,alimiter=limit=0.70:attack=1:release=60:level=false,aresample=48000'
                 if gain is not None else
                 'aresample=192000,alimiter=limit=0.60:attack=1:release=60:level=false,aresample=48000')
        ff(['-i', video, '-i', WORK / f'{tag}_音声.wav', '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
            '-af', chain, '-c:a', 'aac_at', '-b:a', '256k', '-t', 15, '-movflags', '+faststart', dest])
        row['text_v02'] = dict(file=row['file'], lufs=row['lufs'], true_peak_dbtp=row['true_peak_dbtp'])
        row.update(file=str(dest), bytes=dest.stat().st_size, lead_text='読書BGM・本編2時間は関連動画から', **measure(dest))
        files[tag] = str(dest)
        print('retext', tag, row['lufs'], row['true_peak_dbtp'], flush=True)
    cfg['shorts']['files'] = files
    cfg['final']['shorts'] = files
    (ROOT / 'iro/volumes/iro20.yaml').write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    report.write_text(json.dumps(list(rows.values()), ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repair-levels', action='store_true')
    parser.add_argument('--retext', action='store_true')
    args = parser.parse_args()
    retext() if args.retext else repair_levels() if args.repair_levels else main()
