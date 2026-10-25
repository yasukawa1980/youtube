"""IRO20: 共通背景、動く人物と犬、扉v5、15秒カード、4ショート。"""
from pathlib import Path
import argparse
import importlib.util
import json
import math
import random
import shutil
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import yaml

ROOT = Path(__file__).resolve().parents[1]
BASE = Path(yaml.safe_load((ROOT / 'iro/volumes/iro20.yaml').read_text())['dir'])
WORK = BASE / '_work/映像_v01'
PARTS = WORK / 'parts'
OUT = BASE / '投稿用'
MAIN = OUT / 'iro20_しおりを挟むにはまだ早い_本編_扉入り.mp4'
FPS, N, T = 24, 192, 7200
JP = '/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
AV = '/System/Library/Fonts/Avenir Next.ttc'
ENC = ['-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-threads', '4',
       '-profile:v', 'high', '-level:v', '4.2', '-bf', '0',
       '-x264-params', 'keyint=480:min-keyint=240:scenecut=0:open-gop=0',
       '-r', '24', '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709',
       '-color_trc', 'bt709', '-colorspace', 'bt709', '-color_range', 'tv']
WOMAN = [(980, 265), (1138, 268), (1192, 315), (1210, 390), (1195, 510),
         (1175, 593), (1080, 615), (1010, 580), (858, 555), (844, 482), (908, 424), (966, 366)]
DOG = [(1120, 490), (1140, 435), (1240, 420), (1390, 440), (1558, 485),
       (1558, 645), (1450, 660), (1175, 635), (1120, 590)]
COMBOS = {'B1': ('B1', 'B1'), 'B2': ('B2', 'B2'), 'A': ('A', 'B1'), 'B': ('B', 'B1'),
          'B1C': ('B1', 'C'), 'B2C': ('B2', 'C'), 'B1D': ('B1', 'D'), 'B2D': ('B2', 'D')}
spec = importlib.util.spec_from_file_location('door', ROOT / 'bgm/IRO/irokit/扉ムービーを入れる.py')
door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
M = door.dur(door.MOVIE)
PREFIX = round((5 + M + door.BREATH - door.SKIP) * FPS)
TOTAL = round((T + M + door.BREATH - door.SKIP) * FPS)
BODY = TOTAL - PREFIX
cv2.setNumThreads(2)


def ff(args):
    subprocess.run(['ffmpeg', '-v', 'error', *map(str, args)], check=True)


def frame_count(path):
    return int(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=nb_frames', '-of', 'csv=p=0', str(path)], text=True).strip())


def source(name, eyes=False):
    if name == 'B1' and eyes:
        return ROOT / 'iro/_work/iro20/iro20_B1_eye_v01.mp4'
    return BASE / f'Kling素材/iro20_{name}_raw.mp4'


def fixed():
    cap = cv2.VideoCapture(str(source('B1'))); ok, frame = cap.read(); cap.release()
    if not ok:
        raise RuntimeError('B1基準コマを読めません')
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).astype(np.float32)


def mask(points, blur):
    m = np.zeros((1080, 1920), np.float32)
    cv2.fillPoly(m, [np.asarray(points, np.int32)], 1)
    return (cv2.GaussianBlur(m, (0, 0), blur) * (m > 0))[:, :, None]


def reader(name, eyes=False, offset=0):
    cap = cv2.VideoCapture(str(source(name, eyes)))
    if offset:
        cap.set(cv2.CAP_PROP_POS_FRAMES, offset)
    fallback = None
    try:
        for k in range(N):
            active = cap
            if k + offset >= N:
                if fallback is None:
                    fallback = cv2.VideoCapture(str(source('B1')))
                active = fallback
            ok, frame = active.read()
            if not ok or frame.shape[:2] != (1080, 1920):
                raise RuntimeError(f'読込失敗 {name} {k}')
            yield cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    finally:
        cap.release()
        if fallback:
            fallback.release()


def parts(only=None):
    PARTS.mkdir(parents=True, exist_ok=True)
    r, wm, dm = fixed(), mask(WOMAN, 10), mask(DOG, 9)
    Image.fromarray(np.uint8(wm[:, :, 0] * 255)).save(WORK / '人物マスク.png')
    Image.fromarray(np.uint8(dm[:, :, 0] * 255)).save(WORK / '犬マスク.png')
    yy, xx = np.nonzero((wm[:, :, 0] > 0) | (dm[:, :, 0] > 0))
    x0, x1, y0, y1 = int(xx.min()), int(xx.max()) + 1, int(yy.min()), int(yy.max()) + 1
    r8 = r.astype(np.uint8)
    r = r[y0:y1, x0:x1].copy()
    wm, dm = wm[y0:y1, x0:x1], dm[y0:y1, x0:x1]
    for key, (woman, dog) in COMBOS.items():
        if only and key not in only:
            continue
        dest = PARTS / f'{key}.mp4'
        if dest.exists():
            if frame_count(dest) != N:
                raise RuntimeError(f'不完全な部品を保全しています: {dest}')
            continue
        wr = reader(woman, eyes=True)
        # Cの静止待ち3秒を除き、頭を上げる直前から8秒単位を組み直す。
        dr = reader(dog, offset=72 if dog == 'C' else 0)
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
            '-s', '1920x1080', '-r', '24', '-i', '-', '-an', '-vf',
            'scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p',
            *ENC, str(dest)], stdin=subprocess.PIPE)
        try:
            for k, (w, d) in enumerate(zip(wr, dr)):
                w = w[y0:y1, x0:x1].astype(np.float32)
                d = d[y0:y1, x0:x1].astype(np.float32)
                a = min(1., k / 10, (N - 1 - k) / 10)
                a = a * a * (3 - 2 * a)
                img = r * (1 - wm * a) + w * (wm * a)
                img = img * (1 - dm * a) + d * (dm * a)
                frame = r8.copy()
                frame[y0:y1, x0:x1] = np.uint8(np.clip(img + .5, 0, 255))
                p.stdin.write(frame.tobytes())
        finally:
            p.stdin.close(); wr.close(); dr.close()
        if p.wait() or frame_count(dest) != N:
            raise RuntimeError(f'部品エンコード失敗 {key}')
        print('part', key, dest.stat().st_size, flush=True)
    (WORK / '部品設計.json').write_text(json.dumps({'woman_polygon': WOMAN, 'dog_polygon': DOG,
        'mask_blur_sigma': [10, 9], 'mask_clipped_after_blur': True, 'edge_blend_frames': 10,
        'C_source_offset_frames': 72, 'C_fallback': 'B1', 'background': 'B1 first frame',
        'combos': COMBOS, 'encode': ENC}, ensure_ascii=False, indent=2) + '\n')


def plan():
    WORK.mkdir(parents=True, exist_ok=True)
    rng = random.Random(202620); seq = []
    events = {12: 'A', 30: 'C', 48: 'B', 65: 'D'}
    last_bases = []
    for i in range(math.ceil(BODY / N)):
        b = rng.choice(['B1', 'B2'])
        if len(last_bases) >= 2 and last_bases[-1] == last_bases[-2] == b:
            b = 'B2' if b == 'B1' else 'B1'
        last_bases.append(b)
        event = events.get(i % 75) if (i + 1) * N < BODY - 15 * FPS else None
        seq.append((event if event in ('A', 'B') else b + event) if event else b)
    first = {tag: next(i for i, p in enumerate(seq) if p.endswith(tag)) for tag in 'ABCD'}
    data = {'fps': FPS, 'prefix_frames': PREFIX, 'total_frames': TOTAL, 'body_frames': BODY,
            'music_seconds': T, 'parts': seq,
            'first_events': {tag: {'part': i, 'seconds': (PREFIX + i * N) / FPS} for tag, i in first.items()},
            'events': [{'part': i, 'kind': p[-1], 'seconds': (PREFIX + i * N) / FPS}
                       for i, p in enumerate(seq) if p[-1] in 'ABCD']}
    (WORK / '構成.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    return data


def card():
    sys.path.insert(0, str(ROOT / 'bgm/IRO/irokit'))
    import endcard
    WORK.mkdir(parents=True, exist_ok=True)
    bg = np.asarray(Image.open(BASE / '開始画像/iro20_start_1920.png').convert('RGB').filter(ImageFilter.GaussianBlur(28))) * .58
    endcard.build(bg, str(WORK / 'エンドカード.png'), 'また、次のページで。', 'See you on the next page.')
    endcard.check(str(WORK / 'エンドカード.png'), str(WORK / 'エンドカード_位置検証.png'))


def prefix():
    lead = WORK / '導入19コマ.mp4'
    if not lead.exists():
        ff(['-ss', 173 / FPS, '-i', PARTS / 'B1.mp4', '-an', '-frames:v', 19, *ENC, lead])
    dest = WORK / '扉と間.mp4'
    if not dest.exists():
        fc = ('[0:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS[a];'
              '[1:v]fps=24,format=yuv420p,setpts=PTS-STARTPTS,tpad=start_duration=2.5:start_mode=clone[b];'
              '[a][b]xfade=transition=fade:duration=1:offset=19.333333,format=yuv420p[v]')
        ff(['-i', door.MOVIE, '-i', lead, '-filter_complex', fc, '-map', '[v]', '-an', '-frames:v', PREFIX, *ENC, dest])
    if frame_count(dest) != PREFIX:
        raise RuntimeError('扉のコマ数が合いません')


def finish_video():
    data = plan(); card(); prefix()
    listing = WORK / '本編全体_参照一覧.txt'
    listing.write_text(''.join(f"file '{PARTS / (p + '.mp4')}'\nduration 8.000000\n" for p in data['parts']))
    pre_card = BODY - 15 * FPS
    full, remaining = divmod(pre_card, N)
    files = [WORK / '扉と間.mp4'] + [PARTS / (p + '.mp4') for p in data['parts'][:full]]
    if remaining:
        partial = WORK / 'カード直前.mp4'
        if not partial.exists():
            ff(['-i', PARTS / (data['parts'][full] + '.mp4'), '-an', '-frames:v', remaining, *ENC, partial])
        files.append(partial)
    end = WORK / '最後15秒.mp4'
    if not end.exists():
        fc = ('[0:v]setpts=PTS-STARTPTS[b];[1:v]format=rgba,fade=t=in:st=0:d=2:alpha=1[c];'
              '[b][c]overlay=0:0:shortest=1,format=yuv420p[v]')
        ff(['-ss', pre_card / FPS, '-f', 'concat', '-safe', 0, '-i', listing,
            '-loop', 1, '-framerate', FPS, '-i', WORK / 'エンドカード.png',
            '-filter_complex', fc, '-map', '[v]', '-an', '-frames:v', 15 * FPS, *ENC, end])
    if frame_count(end) != 15 * FPS:
        raise RuntimeError('エンドカードのコマ数が合いません')
    files.append(end)
    (WORK / '完成映像_連結.txt').write_text(''.join(f"file '{p}'\n" for p in files))
    print('video structure', PREFIX, BODY, TOTAL, flush=True)


def audio():
    dest = WORK / '配信用音声.m4a'
    if dest.exists():
        raise FileExistsError(dest)
    fc = (f'[0:a]volume={door.GAIN}dB,aformat=sample_rates=48000:channel_layouts=stereo,apad=whole_dur={M + door.BREATH:.6f}[ma];'
          f'[1:a]asetpts=PTS-STARTPTS,aresample=192000,alimiter=limit=0.56:attack=1:release=60:level=false,'
          f'alimiter=limit=0.56:attack=1:release=60:level=false,aresample=48000,aformat=channel_layouts=stereo,'
          f'afade=t=in:d={door.FADE_IN},afade=t=out:st={T - door.SKIP - 10:.6f}:d=10[ba];'
          '[ma][ba]concat=n=2:v=0:a=1[pre];[pre]volume=-0.2dB[a]')
    ff(['-i', door.MOVIE, '-ss', door.SKIP, '-t', T - door.SKIP, '-i', BASE / '_work/music_bed.wav',
        '-filter_complex', fc, '-map', '[a]', '-c:a', 'aac_at', '-b:a', '320k', dest])


def mux():
    if MAIN.exists():
        raise FileExistsError(MAIN)
    ff(['-f', 'concat', '-safe', 0, '-i', WORK / '完成映像_連結.txt', '-i', WORK / '配信用音声.m4a',
        '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-movflags', '+faststart', MAIN])
    if frame_count(MAIN) != TOTAL:
        raise RuntimeError('本編のコマ数が合いません')
    print(MAIN, MAIN.stat().st_size, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['parts', 'card', 'plan', 'video', 'audio', 'mux'])
    parser.add_argument('--only')
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True); OUT.mkdir(exist_ok=True)
    if args.step == 'parts':
        parts(args.only.split(',') if args.only else None)
    else:
        {'card': card, 'plan': plan, 'video': finish_video, 'audio': audio, 'mux': mux}[args.step]()
