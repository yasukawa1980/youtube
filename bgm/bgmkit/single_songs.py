#!/usr/bin/env python3
"""Configurable single-song videos. Requires FFmpeg, ffprobe and PyYAML.

Run from the repository root: python3 -m bgm.bgmkit.single_songs --check
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SR = 48000
FPS = 30
IMAGES = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}


def run(args):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-6000:] or result.stdout[-6000:])
    return result


def ff(*args):
    return run(['ffmpeg', '-hide_banner', '-nostdin', '-nostats', '-y', *args])


def probe(path):
    return json.loads(run(['ffprobe', '-v', 'error', '-show_format',
                           '-show_streams', '-of', 'json', path]).stdout)


def seconds(value):
    if isinstance(value, bool):
        raise ValueError('時刻に true/false は使えません')
    parts = str(value).split(':')
    if not 1 <= len(parts) <= 3:
        raise ValueError(f'不正な時刻: {value}')
    nums = [float(p) for p in parts]
    if any(not math.isfinite(n) or n < 0 for n in nums):
        raise ValueError(f'不正な時刻: {value}')
    if len(nums) > 1 and any(n >= 60 for n in nums[1:]):
        raise ValueError(f'秒・分は60未満にしてください: {value}')
    total = 0.0
    for n in nums:
        total = total * 60 + n
    return total


def resolve(base, path):
    return (base / Path(path).expanduser()).resolve()


def take_info(base, take):
    path = resolve(base, take['path'])
    if not path.is_file():
        raise ValueError(f'音源がありません: {path}')
    info = probe(path)
    streams = [s for s in info['streams'] if s['codec_type'] == 'audio']
    if not streams:
        raise ValueError(f'音声トラックがありません: {path}')
    duration = float(streams[0].get('duration', info['format'].get('duration', 0)))
    start = seconds(take.get('start', 0))
    end = seconds(take.get('end', duration))
    if not 0 <= start < end <= duration + 0.001:
        raise ValueError(f'切り出し範囲が不正: {path}: {start}〜{end} / {duration}秒')
    return dict(path=str(path), start=start, end=min(end, duration),
                duration=min(end, duration) - start, name=take.get('name', path.stem))


def sequence(durations, target, crossfade, repeats=None):
    """Round-robin indices and overlap start times; include enough complete takes."""
    if any(d <= 2 * crossfade for d in durations):
        raise ValueError('各音源はクロスフェードの2倍より長くしてください')
    indices, joins, total = [0], [], durations[0]
    while (len(indices) < repeats if repeats is not None else total < target):
        i = len(indices) % len(durations)
        joins.append(total - crossfade)
        total += durations[i] - crossfade
        indices.append(i)
        if len(indices) > 1000:
            raise ValueError('ループ回数が1000を超えます。長い音源を指定してください')
    return indices, joins, total if repeats is not None else target


def norm_stats(path, lufs, peak, lra):
    result = ff('-i', path, '-vn', '-af',
                f'loudnorm=I={lufs}:TP={peak}:LRA={lra}:print_format=json', '-f', 'null', '-')
    matches = re.findall(r'\{[^{}]*"input_i"[^{}]*\}', result.stderr, re.S)
    if not matches:
        raise ValueError(f'音量測定に失敗しました: {path}')
    stats = json.loads(matches[-1])
    if any(not math.isfinite(float(stats[k])) for k in
           ('input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset')):
        raise ValueError(f'無音などの理由で音量を正規化できません: {path}')
    return stats


def normalize(src, dst, settings):
    lufs, peak, lra = (settings[k] for k in ('lufs', 'true_peak', 'lra'))
    stats = norm_stats(src, lufs, peak, lra)
    filt = (f'loudnorm=I={lufs}:TP={peak}:LRA={lra}:linear=true:'
            f'measured_I={stats["input_i"]}:measured_TP={stats["input_tp"]}:'
            f'measured_LRA={stats["input_lra"]}:measured_thresh={stats["input_thresh"]}:'
            f'offset={stats["target_offset"]}')
    codec = ['-c:a', 'aac', '-b:a', '192k'] if dst.suffix == '.m4a' else ['-c:a', 'pcm_f32le']
    ff('-i', src, '-vn', '-af', filt, '-ar', str(SR), '-ac', '2', *codec, dst)


def mix_audio(takes, indices, duration, crossfade, fade, dst):
    inputs, filters = [], []
    for n, i in enumerate(indices):
        inputs += ['-i', takes[i]]
        filters.append(f'[{n}:a]asetpts=PTS-STARTPTS[a{n}]')
    prev = 'a0'
    for n in range(1, len(indices)):
        filters.append(f'[{prev}][a{n}]acrossfade=d={crossfade}:c1=tri:c2=tri[x{n}]')
        prev = f'x{n}'
    filters.append(f'[{prev}]atrim=duration={duration},asetpts=PTS-STARTPTS,'
                   f'afade=t=in:d={fade},afade=t=out:st={duration-fade}:d={fade}[out]')
    ff(*inputs, '-filter_complex', ';'.join(filters), '-map', '[out]',
       '-ar', str(SR), '-ac', '2', '-c:a', 'pcm_f32le', dst)


def video_options(settings):
    return ['-an', '-c:v', 'libx264', '-preset', settings['preset'], '-crf', str(settings['crf']),
            '-pix_fmt', 'yuv420p', '-r', str(FPS), '-g', str(FPS),
            '-keyint_min', str(FPS), '-sc_threshold', '0', '-bf', '0', '-threads', '4',
            '-video_track_timescale', '15360']


def make_video(visual, audio, duration, fade, settings, work, output):
    scale = ('scale=1920:1080:force_original_aspect_ratio=decrease,'
             'pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1')
    frames = math.ceil(duration * FPS - 1e-7)
    if visual.suffix.lower() in IMAGES:
        # Only encode fades and a one-second still. Copy the still for the long middle.
        for name, length, extra in [('intro', fade, f',fade=t=in:d={fade}'),
                                    ('hold', 1, ''), ('outro', fade, f',fade=t=out:d={fade}')]:
            path = work / f'{name}.mp4'
            if not path.exists():
                ff('-loop', '1', '-framerate', str(FPS), '-i', visual,
                   '-vf', scale + extra, '-frames:v', str(round(length * FPS)),
                   *video_options(settings), path)
        middle_frames = frames - 2 * round(fade * FPS)
        ff('-stream_loop', '-1', '-i', work / 'hold.mp4', '-map', '0:v:0',
           '-frames:v', str(middle_frames), '-c:v', 'copy', work / 'middle.mp4')
        listing = work / 'video.ffconcat'
        listing.write_text("file 'intro.mp4'\nfile 'middle.mp4'\nfile 'outro.mp4'\n")
        ff('-f', 'concat', '-safe', '0', '-i', listing, '-i', audio,
           '-map', '0:v:0', '-map', '1:a:0', '-c', 'copy', '-t', str(duration),
           '-movflags', '+faststart', output)
    else:
        ff('-stream_loop', '-1', '-i', visual, '-i', audio,
           '-map', '0:v:0', '-map', '1:a:0', '-vf',
           scale + f',fps={FPS},fade=t=in:d={fade},fade=t=out:st={duration-fade}:d={fade}',
           # video_options includes -an, so supply audio mapping/codec after it.
           *[x for x in video_options(settings) if x != '-an'],
           '-c:a', 'copy', '-t', str(duration), '-movflags', '+faststart', output)


def verify(path, duration, settings):
    info = probe(path)
    v = next(s for s in info['streams'] if s['codec_type'] == 'video')
    a = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    if (v['codec_name'], v['width'], v['height'], v['pix_fmt'], a['codec_name']) != (
            'h264', 1920, 1080, 'yuv420p', 'aac'):
        raise ValueError('出力形式の検証に失敗しました')
    for s in (v, a):
        if abs(float(s['duration']) - duration) > 0.12:
            raise ValueError(f'出力尺が一致しません: {s["codec_type"]} {s["duration"]} / {duration}')
    # Decode every frame and audio packet, not just the container header.
    result = ff('-v', 'error', '-xerror', '-i', path, '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-')
    if result.stderr.strip():
        raise ValueError(f'デコード警告: {result.stderr}')
    measured = norm_stats(path, settings['lufs'], settings['true_peak'], settings['lra'])
    warnings = []
    if abs(float(measured['input_i']) - settings['lufs']) > 1.0:
        warnings.append('目標LUFSとの差が1 LUを超えています。確認してください。')
    if float(measured['input_tp']) > -1.0:
        warnings.append('AACのTrue Peakが-1 dBTPを超えています。確認してください。')
    return dict(duration=float(info['format']['duration']), video=v['codec_name'],
                width=v['width'], height=v['height'], audio=a['codec_name'],
                lufs=float(measured['input_i']), true_peak=float(measured['input_tp']),
                full_decode='passed', warnings=warnings)


def metadata(song, channel, version, duration):
    label = f'{int(duration)//60}分{round(duration)%60:02d}秒' if version == 'short' else version
    purpose = '子守唄・寝かしつけ・作業用' if version == '30分' else '子守唄・寝かしつけ'
    title = f'{song["name"]}｜{channel}｜{purpose} {label}'
    description = (f'「{song["name"]}」を、{label}ゆっくりお楽しみいただける単曲版です。\n'
                   f'{song.get("description", "")}\n'
                   'おやすみ前や、静かに過ごしたい時間のおともに。\n\n'
                   f'制作：{channel}\n')
    tags = list(dict.fromkeys([song['name'], channel, '童謡', '子守唄', '寝かしつけ',
                              'リラックス', '作業用BGM', *song.get('tags', [])]))
    return f'【タイトル案】\n{title}\n\n【説明文案】\n{description}\n【タグ案】\n' + ', '.join(tags) + '\n'


def prepare(config, selected, selected_versions=None):
    base = config.parent
    data = yaml.safe_load(config.read_text(encoding='utf-8'))
    settings = dict(crossfade=1.5, fade=4.0, lufs=-14.0, true_peak=-2.0,
                    lra=11.0, preset='veryfast', crf=20)
    settings.update(data.get('settings', {}))
    for k in ('crossfade', 'fade', 'lufs', 'true_peak', 'lra', 'crf'):
        settings[k] = float(settings[k])
        if not math.isfinite(settings[k]):
            raise ValueError(f'{k}は有限の数値にしてください')
    if not 1 <= settings['crossfade'] <= 2 or not 3 <= settings['fade'] <= 5:
        raise ValueError('crossfadeは1〜2秒、fadeは3〜5秒です')
    settings['fade'] = round(settings['fade'] * FPS) / FPS
    if not (-70 <= settings['lufs'] <= -5 and -9 <= settings['true_peak'] <= 0
            and 1 <= settings['lra'] <= 50 and 0 <= settings['crf'] <= 51):
        raise ValueError('lufs / true_peak / lra / crf の範囲が不正です')
    jobs, seen = [], set()
    for song in data['songs']:
        if not song.get('enabled', True) or (selected and song['id'] not in selected):
            continue
        sid = song['id']
        if not re.fullmatch(r'[A-Za-z0-9_-]+', sid) or sid in seen:
            raise ValueError(f'idは重複のない英数字・ハイフン・下線にしてください: {sid}')
        seen.add(sid)
        visual = resolve(base, song['visual'])
        if not visual.is_file() or not any(s['codec_type'] == 'video' for s in probe(visual)['streams']):
            raise ValueError(f'映像・画像を読み込めません: {visual}')
        primary = take_info(base, song['audio'])
        short_cfg = song.get('short', {})
        short = take_info(base, short_cfg['audio']) if 'audio' in short_cfg else primary
        repeats = short_cfg.get('repeats')
        if repeats is None:
            repeats = min((1, 2), key=lambda n: abs(n * short['duration'] - (n-1) * settings['crossfade'] - 240))
        if isinstance(repeats, bool) or repeats not in (1, 2):
            raise ValueError('short.repeatsは1か2にしてください')
        long_takes = [primary] + [take_info(base, t) for t in song.get('alternates', [])]
        versions = [('short', [short], None, repeats), ('10分', [primary], 600, None),
                    ('30分', long_takes, 1800, None)]
        plans = []
        for version, takes, target, count in versions:
            if selected_versions and version not in selected_versions:
                continue
            indices, joins, duration = sequence([t['duration'] for t in takes], target,
                                                 settings['crossfade'], count)
            if duration <= 2 * settings['fade']:
                raise ValueError('動画はフェード時間の2倍より長くしてください')
            plans.append(dict(version=version, takes=takes, indices=indices,
                              joins=joins, duration=duration))
        jobs.append((song, visual, plans))
    if not jobs or (selected and set(selected) - seen):
        raise ValueError('指定した有効な曲が見つかりません')
    return data, settings, resolve(base, data.get('output_dir', 'output')), jobs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path(__file__).resolve().parents[1] / 'volumes' / 'doyo03.yaml')
    parser.add_argument('--song', action='append', help='曲id。複数指定可')
    parser.add_argument('--version', action='append', choices=['short', '10min', '30min'],
                        help='生成する長さ。複数指定可。省略すると3種類すべて')
    parser.add_argument('--check', action='store_true', help='入力素材と出力予定を検証するだけ')
    parser.add_argument('--overwrite', action='store_true', help='同名の完成動画・投稿文・検証結果を置換')
    args = parser.parse_args()
    for command in ('ffmpeg', 'ffprobe'):
        if not shutil.which(command):
            raise ValueError(f'{command}をインストールしてください')
    versions = {'short': 'short', '10min': '10分', '30min': '30分'}
    selected_versions = [versions[v] for v in args.version] if args.version else None
    data, settings, out, jobs = prepare(args.config.resolve(), args.song, selected_versions)
    for song, _, plans in jobs:
        for plan in plans:
            print(f'{song["name"]} {plan["version"]}: {plan["duration"]:.3f}秒 / '
                  f'{len(plan["indices"])}音源、接続{len(plan["joins"])}箇所', flush=True)
            stem = f'{song["id"]}_{plan["version"]}'
            for suffix in ('.mp4', '.txt', '.json'):
                if not args.check and (out / (stem + suffix)).exists() and not args.overwrite:
                    raise ValueError(f'既存ファイルがあります: {out / (stem + suffix)}。再生成は --overwrite')
    if args.check:
        return
    out.mkdir(parents=True, exist_ok=True)
    for song, visual, plans in jobs:
        # Per-run files and atomic publication keep failed runs away from finished videos.
        with tempfile.TemporaryDirectory(prefix=f'.{song["id"]}-', dir=out) as temporary:
            work = Path(temporary)
            normalized = {}
            for plan in plans:
                version, duration = plan['version'], plan['duration']
                print(f'作成中: {song["name"]} {version} — 音声', flush=True)
                paths = []
                for take in plan['takes']:
                    key = (take['path'], take['start'], take['end'])
                    if key not in normalized:
                        raw, norm = work / 'extract.wav', work / f'take{len(normalized)}.wav'
                        ff('-ss', str(take['start']), '-i', take['path'], '-t', str(take['duration']),
                           '-map', '0:a:0', '-vn', '-ar', str(SR), '-ac', '2', '-c:a', 'pcm_f32le', raw)
                        normalize(raw, norm, settings)
                        normalized[key] = norm
                    paths.append(normalized[key])
                mix_audio(paths, plan['indices'], duration, settings['crossfade'], settings['fade'], work / 'mix.wav')
                normalize(work / 'mix.wav', work / 'audio.m4a', settings)
                print(f'作成中: {song["name"]} {version} — 映像', flush=True)
                make_video(visual, work / 'audio.m4a', duration, settings['fade'], settings, work, work / 'result.mp4')
                print(f'検証中: {song["name"]} {version} — 全編デコード・音量測定', flush=True)
                report = verify(work / 'result.mp4', duration, settings)
                report.update(song=song['name'], settings=settings, plan=plan,
                              visual=str(visual), subjective_listening='not performed by script')
                stem = f'{song["id"]}_{version}'
                (work / 'result.txt').write_text(metadata(song, data.get('channel', 'ウィスパーズ'), version, duration), encoding='utf-8')
                (work / 'result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
                for suffix in ('.mp4', '.txt', '.json'):
                    (work / ('result' + suffix)).replace(out / (stem + suffix))
                print(f'完了: {out / (stem + ".mp4")} / {report["lufs"]} LUFS', flush=True)
                for warning in report['warnings']:
                    print(f'注意: {warning}', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, RuntimeError, yaml.YAMLError) as exc:
        print(f'エラー: {exc}', file=sys.stderr)
        sys.exit(1)
