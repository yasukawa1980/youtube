"""完成AACを区切らず測り、全映像・全音声を厳密にデコードする。"""
from pathlib import Path
from fractions import Fraction
import argparse
import hashlib
import json
import re
import subprocess
import time

import yaml

ROOT = Path(__file__).resolve().parents[1]
CFG = yaml.safe_load((ROOT / 'iro/volumes/iro20.yaml').read_text())
BASE = Path(CFG['dir']); OUT = BASE / '投稿用'; WORK = BASE / '_work/完成検品_v01'
REPORT = ROOT / 'iro/iro20_完成検品.json'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def inspect(tag, path, expected):
    start = time.monotonic()
    metadata = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams',
        '-show_format', '-of', 'json', str(path)]))
    video = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
    sound = next(s for s in metadata['streams'] if s['codec_type'] == 'audio')
    command = ['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-map', '0:a:0', '-vn',
        '-af', 'loudnorm=I=-14:TP=-2:LRA=11:print_format=json', '-f', 'null', '-']
    measured = subprocess.run(command, capture_output=True, text=True, check=True)
    (WORK / f'{tag}_AAC全体測定.log').write_text(measured.stderr)
    match = re.search(r'\{[^{}]*input_i[^{}]*\}', measured.stderr, re.S)
    if not match:
        raise RuntimeError(f'AAC測定値がありません: {tag}')
    meter = json.loads(match.group(0))
    decode_command = ['ffmpeg', '-v', 'error', '-xerror', '-threads', '4', '-i', str(path),
                      '-map', '0:v:0', '-map', '0:a:0', '-f', 'null', '-']
    with (WORK / f'{tag}_全編デコード.log').open('w') as log:
        decoded = subprocess.run(decode_command, stdout=subprocess.DEVNULL, stderr=log)
    errors = (WORK / f'{tag}_全編デコード.log').read_text()
    flags = []
    frames = int(video['nb_frames']); seconds = float(metadata['format']['duration'])
    fps = float(Fraction(video['avg_frame_rate']))
    dims = [video['width'], video['height']]
    if dims != expected['dimensions'] or frames != expected['frames'] or abs(fps - 24) > .0001:
        flags.append('映像の寸法・コマ数・fpsが不一致')
    if abs(seconds - expected['frames'] / 24) > .05:
        flags.append('実尺が予定から0.05秒超ずれる')
    lufs, peak = float(meter['input_i']), float(meter['input_tp'])
    if not -14.5 <= lufs <= -13.5:
        flags.append('LUFSが-14±0.5の外')
    if peak > -2:
        flags.append('AAC True Peakが-2.0dBTPを超える')
    if decoded.returncode or errors.strip():
        flags.append('全編デコードにエラー')
    if sound['codec_name'] != 'aac' or sound['sample_rate'] != '48000' or sound['channels'] != 2:
        flags.append('音声形式が不一致')
    row = {'tag': tag, 'file': str(path), 'bytes': path.stat().st_size, 'file_sha256': digest(path),
           'duration_seconds': seconds, 'dimensions': dims, 'frames': frames, 'fps': fps,
           'video_codec': video['codec_name'], 'video_bitrate_bps': int(video.get('bit_rate', 0)),
           'video_profile': video.get('profile'), 'color_space': video.get('color_space'),
           'color_range': video.get('color_range'), 'audio_codec': sound['codec_name'],
           'audio_sample_rate': 48000, 'audio_channels': 2,
           'lufs': lufs, 'true_peak_dbtp': peak, 'lra': float(meter['input_lra']),
           'whole_aac_measured_continuously': True, 'measurement_command': command,
           'full_av_decode_exit_code': decoded.returncode, 'decode_error_bytes': len(errors.encode()),
           'decode_command': decode_command, 'expected': expected, 'flags': flags,
           'technical_pass': not flags, 'visual_review': 'pending', 'direct_listening': 'not_performed',
           'elapsed_seconds': round(time.monotonic() - start, 1)}
    print(tag, {k: row[k] for k in ('duration_seconds', 'lufs', 'true_peak_dbtp', 'flags')}, flush=True)
    return row


def main():
    global WORK
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only', choices=['main', 'shorts'])
    parser.add_argument('--revision', default='v01', help='ログ保存先の版。例: v03')
    args = parser.parse_args()
    if not re.fullmatch(r'v\d+', args.revision):
        parser.error('--revision は v03 のような形式で指定してください')
    WORK = BASE / f'_work/完成検品_{args.revision}'
    WORK.mkdir(parents=True, exist_ok=True)
    plan = json.loads((BASE / '_work/映像_v01/構成.json').read_text())
    targets = [('main', OUT / 'iro20_しおりを挟むにはまだ早い_本編_扉入り.mp4',
                {'dimensions': [1920, 1080], 'frames': plan['total_frames']})]
    targets += [(tag, Path(CFG.get('shorts', {}).get('files', {}).get(tag, str(OUT / f'iro20_ショート_{tag}.mp4'))),
                 {'dimensions': [1080, 1920], 'frames': 360}) for tag in 'ABCD']
    report = json.loads(REPORT.read_text()) if REPORT.exists() else {'checks': {}}
    for tag, path, expected in targets:
        if args.only == 'main' and tag != 'main' or args.only == 'shorts' and tag == 'main':
            continue
        if not path.is_file():
            raise FileNotFoundError(path)
        row = inspect(tag, path, expected)
        # 本編とショートを別プロセスで検品しても先行結果を保つ。
        report = json.loads(REPORT.read_text()) if REPORT.exists() else {'checks': {}}
        report['checks'][tag] = row
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    main()
