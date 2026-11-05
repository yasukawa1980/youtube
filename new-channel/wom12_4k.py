#!/usr/bin/env python3
"""第12話の完成版を4Kへ拡大する。QT-Cと同じ設定。元の1080p版は変更しない。

使い方: python3 wom12_4k.py [v01] [en]
"""
import hashlib, json, subprocess, sys, fcntl, shutil
from pathlib import Path

BASE = Path('/Volumes/ESD-02/新チャンネル/EP012_SantaClaus')
FOLDERS = {'v01': '確認版_v01_20261105', 'v02': '確認版_v02_20261105'}
VF = 'scale=3840:2160:flags=lanczos'
ENCODE = ['-c:v', 'libx264', '-preset', 'veryfast', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
          '-b:v', '40M', '-maxrate', '45M', '-bufsize', '80M', '-g', '15', '-bf', '2',
          '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709']


def run(*args):
    return subprocess.run(args, check=True, capture_output=True, text=True).stdout


def probe(path):
    return json.loads(run('ffprobe', '-v', 'error', '-count_frames', '-show_entries',
                          'format=duration,size,bit_rate:stream=codec_type,codec_name,profile,pix_fmt,width,height,avg_frame_rate,nb_read_frames',
                          '-of', 'json', str(path)))


def audio_sha(path):
    data = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-c', 'copy', '-f', 'adts', '-'],
                          check=True, capture_output=True).stdout
    return hashlib.sha256(data).hexdigest()


def video_stream(info):
    return next(s for s in info['streams'] if s['codec_type'] == 'video')


def convert(version, language):
    root = BASE / FOLDERS[version]
    src = root / f'deliverables/EP012_SantaClaus_{language}_{version}_1080p30.mp4'
    # Preserve the encoded 1080p source while the review muxes undergo timing checks.
    source_file = src
    src = root / '_work' / 'immutable_4k_input.mp4'
    shutil.copy2(source_file, src)
    out = root / f'deliverables_4k/EP012_SantaClaus_{language}_{version}_2160p30.mp4'
    out.parent.mkdir(exist_ok=True)
    run('ffmpeg', '-nostdin', '-y', '-v', 'error', '-i', str(src), '-map', '0:v:0', '-map', '0:a:0', '-vf', VF, *ENCODE,
        '-threads', '4', '-progress', str(root / '_work/4k_progress.txt'), '-c:a', 'copy', '-movflags', '+faststart', str(out))
    decoded = subprocess.run(['ffmpeg','-nostdin','-v','warning','-xerror','-i',str(out),'-map','0:v:0','-f','null','-'],check=True,capture_output=True,text=True)
    assert not decoded.stderr.strip(), decoded.stderr
    before, after = probe(src), probe(out)
    v0, v1 = video_stream(before), video_stream(after)
    assert [v1['width'], v1['height'], v1['avg_frame_rate']] == [3840, 2160, '30/1']
    assert v1['nb_read_frames'] == v0['nb_read_frames']
    assert [v1['profile'],v1['pix_fmt']] == ['High','yuv420p']
    assert audio_sha(src) == audio_sha(out)
    record = {'language': language, 'source': source_file.name, 'output': out.name, 'frames': int(v1['nb_read_frames']),
              'duration': float(after['format']['duration']), 'bytes': int(after['format']['size']),
              'bit_rate': int(after['format']['bit_rate']), 'audio_same': True, 'decode_warnings': 0, 'source_sha256': hashlib.file_digest(src.open('rb'),'sha256').hexdigest(), 'output_sha256': hashlib.file_digest(out.open('rb'),'sha256').hexdigest()}
    print(json.dumps(record, ensure_ascii=False), flush=True)
    return record


if __name__ == '__main__':
    version = sys.argv[1] if len(sys.argv) > 1 else 'v01'
    languages = sys.argv[2:] or ['en']
    root = BASE / FOLDERS[version]
    with (root / '_work/4k.lock').open('a') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state = root / 'deliverables_4k/encoding.json'
        cached = json.loads(state.read_text()) if state.exists() else None
        valid = cached is not None and [x['language'] for x in cached['files']] == languages
        if valid:
            for item in cached['files']:
                src = root / 'deliverables' / item['source']; dst = root / 'deliverables_4k' / item['output']
                valid = valid and dst.exists() and hashlib.file_digest(src.open('rb'),'sha256').hexdigest() == item['source_sha256'] and hashlib.file_digest(dst.open('rb'),'sha256').hexdigest() == item['output_sha256']
        if valid:
            print('4K CACHE VERIFIED', state, flush=True)
        else:
            records = [convert(version, language) for language in languages]
            state.write_text(json.dumps({'vf': VF, 'encode': ENCODE, 'files': records}, indent=2))
