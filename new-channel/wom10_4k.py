#!/usr/bin/env python3
"""第10話の完成版を4Kへ拡大する。QT-Cと同じ設定。元の1080p版は変更しない。

使い方: python3 wom10_4k.py [v01] [en ja]
"""
import hashlib, json, subprocess, sys
from pathlib import Path

BASE = Path('/Volumes/ESD-02/新チャンネル/EP010_Krampus')
FOLDERS = {'v01': '確認版_v01_20261102', 'v02': '確認版_v02_20261103'}
VF = 'scale=3840:2160:flags=lanczos'
ENCODE = ['-c:v', 'libx264', '-preset', 'veryfast', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
          '-b:v', '40M', '-maxrate', '45M', '-bufsize', '80M', '-g', '15', '-bf', '2',
          '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709']


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def probe(path):
    return json.loads(run('ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                          'format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,avg_frame_rate,nb_read_frames',
                          '-of', 'json', str(path)))


def audio_sha(path):
    data = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-c', 'copy', '-f', 'adts', '-'],
                          check=True, capture_output=True).stdout
    return hashlib.sha256(data).hexdigest()


def video_stream(info):
    return next(s for s in info['streams'] if s['codec_type'] == 'video')


def convert(version, language):
    root = BASE / FOLDERS[version]
    src = root / f'deliverables/EP010_Krampus_{language}_{version}_1080p30.mp4'
    out = root / f'deliverables_4k/EP010_Krampus_{language}_{version}_2160p30.mp4'
    out.parent.mkdir(exist_ok=True)
    run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', str(src), '-map', '0:v:0', '-map', '0:a:0', '-vf', VF, *ENCODE,
        '-c:a', 'copy', '-movflags', '+faststart', str(out))
    run('ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(out), '-map', '0:v:0', '-f', 'null', '-')
    before, after = probe(src), probe(out)
    v0, v1 = video_stream(before), video_stream(after)
    assert [v1['width'], v1['height'], v1['avg_frame_rate']] == [3840, 2160, '30/1']
    assert v1['nb_read_frames'] == v0['nb_read_frames']
    assert audio_sha(src) == audio_sha(out)
    record = {'language': language, 'source': src.name, 'output': out.name, 'frames': int(v1['nb_read_frames']),
              'duration': float(after['format']['duration']), 'bytes': int(after['format']['size']),
              'bit_rate': int(after['format']['bit_rate']), 'audio_same': True}
    print(json.dumps(record, ensure_ascii=False), flush=True)
    return record


if __name__ == '__main__':
    version = sys.argv[1] if len(sys.argv) > 1 else 'v01'
    languages = sys.argv[2:] or ['en']
    records = [convert(version, language) for language in languages]
    state = BASE / FOLDERS[version] / 'deliverables_4k/encoding.json'
    state.write_text(json.dumps({'vf': VF, 'encode': ENCODE, 'files': records}, ensure_ascii=False, indent=2))
