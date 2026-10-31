"""朗読（narration.wav）とBGM床（WAVE10の自前合成）を混ぜ、静止画5場面で本編を書き出す。

- 場面は2話ごとに切り替える。転換は次の話の題の4秒前を中心に6秒（題の前の8秒の無音の中）
- 字幕を下中央に焼く（subtitles.py）。各話の頭の「第一夜」などの札と、1:00の登録のお願いは左上
- BGMは0秒から2秒で入る（冒頭を無音にしない）。末尾6秒で黒へ
- 絵は第一夜の庭（画像プロンプト/）。夕べ→月夜→星→霧→暁
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BGM = HERE.parents[1]
sys.path.insert(0, str(BGM))
from bgmkit.config import CTA_TEXT                                    # noqa: E402
from bgmkit.video import CTA_DEFAULT, LABEL_DEFAULT, _fade_over, _text_png  # noqa: E402

FPS = 30
SIZE = (1920, 1080)
IMAGES = [HERE.parent / '画像' / f'rdg01_0{n}.png' for n in range(1, 6)]   # 夕べ・月夜・星・霧・暁
BED = BGM / 'WAVE10_時雨の山寺/本編音声v2/wave10_3時間_自前合成_v2.flac'
VOICE_LUFS = -20.0    # 左右に振ると約3dB上がる。完成で約-16 LUFS
BED_LUFS = -39.0       # 声より19dB下。無音の間に聞こえるのはこちら
TRANSITION = 6.0
END_FADE = 6.0
OPENING_LABEL = (0.5, '夏目漱石　夢十夜')
# ★下中央に字幕を焼くので、札と登録のお願いは左上へ逃がす（見た目は bgmkit と同じ）
LABEL = dict(LABEL_DEFAULT, y=70)
OPENING = dict(LABEL, hold=4.0)    # 第一夜の札（約8秒）と重ならないように短く
CTA = dict(CTA_DEFAULT, y=88)
OUT = HERE.parent / '完成' / 'RDG01_夢十夜_朗読.mp4'
PREVIEW = float(sys.argv[1]) if len(sys.argv) > 1 else None   # 秒。頭だけ試しに書き出す


class _TextCfg(dict):
    images_dir = ''


def lufs(path, seconds=None):
    args = ['ffmpeg', '-hide_banner', '-nostats']
    if seconds:
        args += ['-t', str(seconds)]
    args += ['-i', str(path), '-af', 'ebur128', '-f', 'null', '-']
    err = subprocess.run(args, capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', err)[-1])


def duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                          '-of', 'csv=p=0', str(path)], capture_output=True, text=True).stdout
    return float(out)


def label_png(text, scene, name, st):
    cfg = _TextCfg(video={'output': list(SIZE)}, images=[str(IMAGES[scene])])
    out = HERE / 'labels' / f'{name}.png'
    out.parent.mkdir(exist_ok=True)
    return Path(_text_png(cfg, 0, text, st, str(out), name))


def mix(total):
    voice = HERE / 'narration.wav'
    gv = VOICE_LUFS - lufs(voice)
    gb = BED_LUFS - lufs(BED, 600)
    out = HERE / 'mix.wav'
    fc = (f'[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume={gv:.2f}dB[v];'
          f'[1:a]atrim=0:{total:.3f},asetpts=N/SR/TB,volume={gb:.2f}dB,'
          f'afade=t=in:d=2,afade=t=out:st={total - END_FADE - 4:.3f}:d={END_FADE + 4}[b];'
          f'[v][b]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.89[a]')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(voice),
                    '-i', str(BED), '-filter_complex', fc, '-map', '[a]', '-t', f'{total:.3f}',
                    '-c:a', 'pcm_s24le', str(out)], check=True)
    print(f'声 {gv:+.1f}dB・床 {gb:+.1f}dB → 完成 {lufs(out):.1f} LUFS')
    return out


def main():
    chapters = json.loads((HERE / 'chapters.json').read_text())
    total = duration(HERE / 'narration.wav')
    # 場面 k は第(2k+1)夜から。転換は題の4秒前を中心に
    cuts = [chapters[2 * k][0] - 4.0 for k in range(1, 5)]
    starts = [0.0] + cuts
    ends = cuts + [total]
    lens = [e - s + (TRANSITION / 2 if i else 0) + (TRANSITION / 2 if i < 4 else 0)
            for i, (s, e) in enumerate(zip(starts, ends))]

    overlays = [(OPENING_LABEL[0], label_png(OPENING_LABEL[1], 0, 'opening', OPENING),
                 OPENING)]
    for n, (t, name) in enumerate(chapters):
        overlays.append((t + 1.0, label_png(name, n // 2, f'night{n + 1:02d}', LABEL),
                         LABEL))
    overlays.append((CTA['at'], label_png(CTA_TEXT['video'], 0, 'cta', CTA), CTA))

    audio = mix(total)
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    for img, sec in zip(IMAGES, lens):
        args += ['-loop', '1', '-framerate', str(FPS), '-t', f'{sec:.3f}', '-i', str(img)]
    for at, png, st in overlays:
        # 出す時刻まで入力ごと遅らせ、出している間だけ読む（80分ぶん重ね続けない）
        args += ['-loop', '1', '-framerate', str(FPS), '-itsoffset', f'{at - 0.5:.3f}',
                 '-t', f'{2 * st["fade"] + st["hold"] + 1:.2f}', '-i', str(png)]
    subs = 5 + len(overlays)          # 字幕（subtitles.py が作る画像列）
    args += ['-f', 'concat', '-safe', '0', '-i', str(HERE / 'subs.txt'), '-i', str(audio)]

    f = [f'[{i}:v]scale={SIZE[0]}:{SIZE[1]}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p[s{i}]'
         for i in range(5)]
    prev, offset = '[s0]', 0.0
    for i in range(1, 5):
        offset += lens[i - 1] - TRANSITION
        f.append(f'{prev}[s{i}]xfade=transition=fade:duration={TRANSITION}:offset={offset:.3f}[x{i}]')
        prev = f'[x{i}]'
    f.append(f'[{subs}:v]format=rgba[sub];{prev}[sub]overlay=0:0:eof_action=pass[st]')
    base = 'st'
    for j, (at, _, st) in enumerate(overlays):
        idx = 5 + j
        f.append(_fade_over(idx, at, st['fade'], st['hold'], base, f'o{j}',
                            ov=':eof_action=pass') + f'[c{j}]')
        base = f'c{j}'
    f.append(f'[{base}]fade=t=out:st={total - END_FADE:.3f}:d={END_FADE}[v]')
    OUT.parent.mkdir(exist_ok=True)
    args += ['-filter_complex', ';'.join(f), '-map', '[v]', '-map', f'{subs + 1}:a',
             '-t', f'{PREVIEW or total:.3f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
             '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-g', str(FPS * 10),
             '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(OUT)]
    if PREVIEW:
        args[-1] = str(HERE / '検品' / '冒頭の試し.mp4')
    subprocess.run(args, check=True)
    print(args[-1] if PREVIEW else OUT, f'{duration(OUT) / 60:.1f}分')


if __name__ == '__main__':
    main()
