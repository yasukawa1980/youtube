"""完成本編から導入・出来事4種・終端を抜粋した110秒の確認用動画。"""
from pathlib import Path
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(yaml.safe_load((ROOT / 'iro/volumes/iro20.yaml').read_text())['dir'])
OUT = BASE / '投稿用'
WORK = BASE / '_work/抜粋確認_v01'
MAIN = OUT / 'iro20_しおりを挟むにはまだ早い_本編_扉入り.mp4'
DEST = OUT / 'iro20_完成確認_抜粋110秒.mp4'


def main():
    if DEST.exists():
        raise FileExistsError(DEST)
    WORK.mkdir(parents=True, exist_ok=True)
    plan = json.loads((BASE / '_work/映像_v01/構成.json').read_text())
    total = plan['total_frames'] / 24
    scenes = [('導入・本編への接続', 0, 30)]
    scenes += [(f'出来事 {tag}', plan['first_events'][tag]['seconds'], 15) for tag in 'ABCD']
    scenes += [('最後20秒・エンドカード', total - 20, 20)]
    files = []
    for i, (name, start, duration) in enumerate(scenes):
        image = Image.new('RGBA', (1280, 720))
        d = ImageDraw.Draw(image)
        d.rectangle((0, 0, 1280, 57), fill=(20, 15, 25, 215))
        d.text((20, 12), f'抜粋確認 / {name} / 本編 {start:.3f}秒から',
               font=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc', 24), fill='white')
        overlay = WORK / f'{i}_表示.png'; image.save(overlay)
        dest = WORK / f'{i}.mp4'; files.append(dest)
        if dest.exists():
            continue
        subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(start), '-t', str(duration),
            '-i', str(MAIN), '-i', str(overlay), '-filter_complex',
            '[0:v]scale=1280:720[b];[b][1:v]overlay=0:0,format=yuv420p[v]',
            '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-crf', '22', '-preset', 'fast',
            '-threads', '4', '-r', '24', '-c:a', 'aac_at', '-b:a', '192k', str(dest)], check=True)
    listing = WORK / '連結.txt'
    listing.write_text(''.join(f"file '{p}'\n" for p in files))
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', str(listing),
                    '-c', 'copy', '-movflags', '+faststart', str(DEST)], check=True)
    (ROOT / 'iro/iro20_確認用抜粋.json').write_text(json.dumps({'file': str(DEST),
        'purpose': '映像構成の抜粋確認。本編の通し視聴・聴感検品を代替しない。',
        'scenes': scenes, 'bytes': DEST.stat().st_size}, ensure_ascii=False, indent=2) + '\n')
    print(DEST, flush=True)


if __name__ == '__main__':
    main()
