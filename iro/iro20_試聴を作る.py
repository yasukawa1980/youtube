"""自動検査済み試作6種を20秒ずつ、2分の確認版へ。音色名は生成時の指定。"""
from pathlib import Path
import json
import subprocess

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / 'iro/volumes/iro20.yaml').read_text())
BASE = Path(CFG['dir'])
WORK = BASE / '_work/試聴_v01'
OUT = BASE / '投稿用/iro20_試作6種_2分.mp4'
NAMES = [('A', 'ハープ'), ('B', 'ファゴット'), ('C', 'チェレスタ'),
         ('D', 'マンドリン'), ('E', 'トロンボーン'), ('F', 'ハーモニウム')]
FONT = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'


def ff(args):
    subprocess.run(['ffmpeg', '-v', 'error', *map(str, args)], check=True)


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    WORK.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (tag, name) in enumerate(NAMES):
        source = BASE / f'楽曲/iro20_{tag}-01a.wav'
        audio = WORK / f'{tag}.wav'
        if not audio.exists():
            ff(['-ss', 30, '-t', 20, '-i', source, '-af',
                'loudnorm=I=-14:TP=-2.5:LRA=11,aresample=48000,afade=t=in:d=0.3,afade=t=out:st=18.8:d=1.2',
                '-ac', 2, '-c:a', 'pcm_s24le', audio])
        text = WORK / f'{tag}.txt'
        text.write_text(f'{tag}  {name}指定\n自動検査済み・聴感未確認', encoding='utf-8')
        rows.append({'tag': tag, 'instrument_prompt': name, 'seconds': i * 20,
                     'source': str(source), 'source_start': 30, 'sample_seconds': 20})
    listing = WORK / '音源一覧.txt'
    listing.write_text(''.join(f"file '{WORK / (tag + '.wav')}'\n" for tag, name in NAMES))
    mix = WORK / '試聴6種.m4a'
    if not mix.exists():
        ff(['-f', 'concat', '-safe', 0, '-i', listing, '-af',
            'aresample=192000,alimiter=limit=0.58:attack=1:release=60:level=false,aresample=48000',
            '-c:a', 'aac_at', '-b:a', '256k', '-t', 120, mix])
    picture_list = []
    for i, (tag, name) in enumerate(NAMES):
        image = Image.open(BASE / '開始画像/iro20_start_1920.png').convert('RGBA')
        overlay = Image.new('RGBA', image.size)
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle((45, 35, 505, 135), 14, fill=(40, 24, 42, 220))
        draw.text((65, 50), '試作6種／2分', font=ImageFont.truetype(FONT, 46), fill='white')
        draw.rounded_rectangle((45, 870, 1040, 1055), 14, fill=(40, 24, 42, 220))
        draw.text((65, 895), f'{tag}  {name}指定', font=ImageFont.truetype(FONT, 48), fill='white')
        draw.text((65, 975), '自動検査済み・聴感未確認', font=ImageFont.truetype(FONT, 38), fill=(255, 224, 129))
        picture = WORK / f'{tag}_caption.png'
        Image.alpha_composite(image, overlay).convert('RGB').save(picture)
        picture_list.append(f"file '{picture}'\nduration 20\n")
    pictures = WORK / '映像一覧.txt'
    pictures.write_text(''.join(picture_list) + f"file '{picture}'\n")
    ff(['-f', 'concat', '-safe', 0, '-i', pictures, '-i', mix,
        '-r', 24, '-c:v', 'libx264', '-crf', 19, '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
        '-c:a', 'copy', '-t', 120, '-movflags', '+faststart', OUT])
    (ROOT / 'iro/iro20_試聴6種_目次.json').write_text(json.dumps({
        'file': str(OUT), 'duration_seconds': 120, 'direct_listening': 'not_performed', 'samples': rows
    }, ensure_ascii=False, indent=2) + '\n')
    print(OUT)


if __name__ == '__main__':
    main()
