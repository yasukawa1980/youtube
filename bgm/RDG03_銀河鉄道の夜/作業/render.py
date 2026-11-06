"""朗読（narration.wav）とBGM床（WAVE12の自前合成）を混ぜ、静止画10場面で本編を書き出す。

RDG02の render.py を直したもの。
- 場面は章と九章の区切りで切り替える（SCENES）。転換は区切りの無音の真ん中を中心に6秒
- 字幕を下中央に焼く（subtitles.py）。章題の札と、1:00の登録のお願いは左上
- BGMは0秒から2秒で入る（冒頭を無音にしない）。末尾6秒で黒へ
- Mac本体の空きが少ないので、混ぜた音と完成はESD-EPBに書く
"""
from __future__ import annotations

import json
import os
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
IMG = HERE.parent / '画像'
# (切り替わる語りの位置[秒], その前の無音の長さ[秒], 絵)。時刻は narration.srt の実測
SCENES = [(0.0, 0.0, 'rdg03_01.png'),        # 夕暮れの坂の町（一〜三章）
          (895.7, 3.0, 'rdg03_02.png'),      # ケンタウル祭の夜（四章）
          (1416.2, 3.0, 'rdg03_03.png'),     # 天気輪の柱の丘（五章）
          (1605.3, 3.0, 'rdg03_04.png'),     # 銀河ステーション（六章）
          (2136.4, 3.0, 'rdg03_05.png'),     # 北十字とプリオシン海岸（七章）
          (2934.8, 3.0, 'rdg03_06.png'),     # 鷺の降る河原（八章）
          (3725.3, 3.0, 'rdg03_07.png'),     # 夜の車内と苹果（九章）
          (5118.6, 1.6, 'rdg03_08.png'),     # 孔雀の森と蝎の火（「あ孔雀が居るよ」）
          (6304.2, 1.6, 'rdg03_09.png'),     # サウザンクロスと石炭袋（「もうじきサウザンクロスです」）
          (6839.1, 1.6, 'rdg03_10.png')]     # 銀河の映る川（「ジョバンニは眼をひらきました」）
BED = Path('/Volumes/ESD-02/BGM/4_Waves of Japan/WAVE12_素材_川霧の渡し場/本編音声v2/wave12_3時間_自前合成_v2_整音.flac')
VOICE_LUFS = -20.0    # 左右に振ると約3dB上がる。完成で約-16 LUFS
BED_LUFS = -39.0       # 声より19dB下。無音の間に聞こえるのはこちら
TRANSITION = 6.0
END_FADE = 6.0
OPENING_LABEL = (0.5, '宮沢賢治　銀河鉄道の夜')
LABEL = dict(LABEL_DEFAULT, y=70)
OPENING = dict(LABEL, hold=4.0)    # 「一、午后の授業」の札（約9秒）と重ならないように短く
CTA = dict(CTA_DEFAULT, y=88)
SSD = Path('/Volumes/ESD-EPB/BGM/9_朗読/RDG03_素材_銀河鉄道の夜')
VOICE = os.environ.get('RDG_VOICE', '')   # 'satomi' で ElevenLabs v4・Satomi 版（11/6 本人決定）
SUF = f'_{VOICE}' if VOICE else ''
WORK = SSD / f'_work{SUF}'
MIX = WORK / 'mix.wav'
OUT = SSD / '完成' / f'RDG03_銀河鉄道の夜_朗読{SUF}.mp4'


def _starts(name):
    return [float(h) * 3600 + float(m) * 60 + float(sec.replace(',', '.'))
            for h, m, sec in re.findall(r'^(\d+):(\d+):([\d,]+) -->', (HERE / name).read_text(), re.M)]


if VOICE:   # 場面の切り替えを、冥鳴ひまり版と同じ字幕番号の位置へ移す
    _old, _new = _starts('narration.srt'), _starts(f'narration{SUF}.srt')
    assert len(_old) == len(_new)
    SCENES = [(0.0, g, img) if s == 0 else
              (_new[min(range(len(_old)), key=lambda i: abs(_old[i] - s))], g, img) for s, g, img in SCENES]
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


def label_png(text, image, name, st):
    cfg = _TextCfg(video={'output': list(SIZE)}, images=[str(IMG / image)])
    out = HERE / 'labels' / f'{name}.png'
    out.parent.mkdir(exist_ok=True)
    return Path(_text_png(cfg, 0, text, st, str(out), name))


def mix(total):
    voice = SSD / f'narration{SUF}.wav'
    gv = VOICE_LUFS - lufs(voice)
    gb = BED_LUFS - lufs(BED, 600)
    MIX.parent.mkdir(parents=True, exist_ok=True)
    fc = (f'[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,volume={gv:.2f}dB[v];'
          f'[1:a]atrim=0:{total:.3f},asetpts=N/SR/TB,volume={gb:.2f}dB,'
          f'afade=t=in:d=2,afade=t=out:st={total - END_FADE - 4:.3f}:d={END_FADE + 4}[b];'
          f'[v][b]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.89[a]')
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(voice),
                    '-i', str(BED), '-filter_complex', fc, '-map', '[a]', '-t', f'{total:.3f}',
                    '-c:a', 'pcm_s24le', str(MIX)], check=True)
    print(f'声 {gv:+.1f}dB・床 {gb:+.1f}dB → 完成 {lufs(MIX):.1f} LUFS')
    return MIX


def scene_of(t):
    return max(i for i, (s, gap, _) in enumerate(SCENES) if s - gap / 2 <= t)


def main():
    chapters = json.loads((HERE / f'chapters{SUF}.json').read_text())   # 章題の位置
    total = duration(SSD / f'narration{SUF}.wav')
    cuts = [s - gap / 2 for s, gap, _ in SCENES[1:]]     # 転換の中心＝区切りの無音の真ん中
    starts = [0.0] + cuts
    ends = cuts + [total]
    n = len(SCENES)
    lens = [e - s + (TRANSITION / 2 if i else 0) + (TRANSITION / 2 if i < n - 1 else 0)
            for i, (s, e) in enumerate(zip(starts, ends))]

    overlays = [(OPENING_LABEL[0], label_png(OPENING_LABEL[1], SCENES[0][2], 'opening', OPENING),
                 OPENING)]
    for k, (t, name) in enumerate(chapters):
        overlays.append((t + 1.0, label_png(name, SCENES[scene_of(t + 1.0)][2], f'chap{k + 1}', LABEL),
                         LABEL))
    overlays.append((CTA['at'], label_png(CTA_TEXT['video'], SCENES[scene_of(CTA['at'])][2], 'cta', CTA),
                     CTA))

    audio = mix(total)
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y']
    for (_, _, img), sec in zip(SCENES, lens):
        args += ['-loop', '1', '-framerate', str(FPS), '-t', f'{sec:.3f}', '-i', str(IMG / img)]
    for at, png, st in overlays:
        # 出す時刻まで入力ごと遅らせ、出している間だけ読む（1時間ぶん重ね続けない）
        args += ['-loop', '1', '-framerate', str(FPS), '-itsoffset', f'{at - 0.5:.3f}',
                 '-t', f'{2 * st["fade"] + st["hold"] + 1:.2f}', '-i', str(png)]
    subs = n + len(overlays)          # 字幕（subtitles.py が作る画像列）
    args += ['-f', 'concat', '-safe', '0', '-i', str(WORK / 'subs.txt'), '-i', str(audio)]

    f = [f'[{i}:v]scale={SIZE[0]}:{SIZE[1]}:flags=lanczos,setsar=1,fps={FPS},format=yuv420p[s{i}]'
         for i in range(n)]
    prev, offset = '[s0]', 0.0
    for i in range(1, n):
        offset += lens[i - 1] - TRANSITION
        f.append(f'{prev}[s{i}]xfade=transition=fade:duration={TRANSITION}:offset={offset:.3f}[x{i}]')
        prev = f'[x{i}]'
    f.append(f'[{subs}:v]format=rgba[sub];{prev}[sub]overlay=0:0:eof_action=pass[st]')
    base = 'st'
    for j, (at, _, st) in enumerate(overlays):
        idx = n + j
        f.append(_fade_over(idx, at, st['fade'], st['hold'], base, f'o{j}',
                            ov=':eof_action=pass') + f'[c{j}]')
        base = f'c{j}'
    f.append(f'[{base}]fade=t=out:st={total - END_FADE:.3f}:d={END_FADE}[v]')
    out = WORK / '冒頭の試し.mp4' if PREVIEW else OUT
    out.parent.mkdir(parents=True, exist_ok=True)
    args += ['-filter_complex', ';'.join(f), '-map', '[v]', '-map', f'{subs + 1}:a',
             '-t', f'{PREVIEW or total:.3f}', '-c:v', 'libx264', '-preset', 'medium', '-crf', '20',
             '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-g', str(FPS * 10),
             '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', str(out)]
    subprocess.run(args, check=True, stdin=subprocess.DEVNULL)
    print(out, f'{duration(out) / 60:.1f}分')


if __name__ == '__main__':
    main()
