"""FAILED v03 approach, retained for audit and reusable hash/probe helpers.

v02 stream-copied a lossless High 4:4:4 Predictive segment into a High
profile track. Decode the complete v02 and encode one delivery stream.
This baked the defective sequential decode into the output. Use v04 instead.
Never overwrite the approved source or delete the existing private upload.
"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

BASE = Path('/Users/ryo/Desktop/新チャンネル/EP005_Tengu')
SOURCE = BASE / '確認版_v02_20261024'
ROOT = BASE / '修正版_v03_20261025'

def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, **kwargs)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe', '-v', 'error',
        '-show_streams', '-show_format', '-of', 'json', str(path)]))

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()

def stream_hash(path, selector):
    return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
        '-map', selector, '-c', 'copy', '-f', 'streamhash', '-hash', 'sha256', '-'],
        text=True).strip()

def main():
    raise RuntimeError('v03 failed visual verification; use wom05_repair_encoding_v04.py')
    for folder in ['deliverables', 'records', '_work', 'review']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    source_en = SOURCE / 'deliverables/EP005_Tengu_en_v02_1080p30.mp4'
    out_en = ROOT / 'deliverables/EP005_Tengu_en_v03_1080p30.mp4'
    assert not out_en.exists(), 'Do not overwrite an existing repair'
    args = ['ffmpeg', '-nostdin', '-n', '-hide_banner', '-v', 'warning',
        '-i', source_en, '-map', '0:v:0', '-map', '0:a:0', '-map_metadata', '0',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-threads', '6',
        '-profile:v', 'high', '-level:v', '4.1', '-pix_fmt', 'yuv420p',
        '-g', '60', '-keyint_min', '30', '-bf', '2', '-maxrate', '20M',
        '-bufsize', '30M', '-fps_mode', 'passthrough',
        '-video_track_timescale', '15360', '-movie_timescale', '48000',
        '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
        '-c:a', 'copy', '-movflags', '+faststart',
        '-progress', ROOT / '_work/encode_progress.txt', out_en]
    with (ROOT / 'records/encode.log').open('w') as log:
        run(args, stderr=log)
    results = []
    for lang in ['en', 'ja']:
        src = SOURCE / f'deliverables/EP005_Tengu_{lang}_v02_1080p30.mp4'
        dst = ROOT / f'deliverables/EP005_Tengu_{lang}_v03_1080p30.mp4'
        if lang == 'ja':
            run(['ffmpeg', '-nostdin', '-n', '-v', 'error', '-i', out_en,
                '-i', src, '-map', '0:v:0', '-map', '1:a:0', '-map_metadata', '1',
                '-c', 'copy', '-movie_timescale', '48000', '-movflags', '+faststart', dst])
        a, b = probe(src), probe(dst)
        assert a['streams'][0]['nb_frames'] == b['streams'][0]['nb_frames'] == '11065'
        assert b['streams'][0]['profile'] == 'High'
        assert b['streams'][0]['pix_fmt'] == 'yuv420p'
        assert b['streams'][0]['r_frame_rate'] == '30/1'
        assert a['format']['duration'] == b['format']['duration']
        assert stream_hash(src, '0:a:0') == stream_hash(dst, '0:a:0')
        results.append({'file': dst.name, 'sha256': sha(dst), 'bytes': dst.stat().st_size,
            'source_sha256': sha(src), 'frames': 11065, 'duration': b['format']['duration'],
            'audio_encoded_stream_identical': True, 'profile': b['streams'][0]['profile']})
        shutil.copy2(src.with_suffix('.srt'), dst.with_suffix('.srt'))
    for name in ['EP005_audio_ja.wav', 'EP005_thumbnail_met_24145.jpg']:
        shutil.copy2(SOURCE / 'deliverables' / name, ROOT / 'deliverables' / name)
    (ROOT / 'records/repair.json').write_text(json.dumps({
        'reason': 'v02 contains High and lossless High 4:4:4 Predictive profiles in one stream',
        'command': list(map(str, args)), 'files': results,
        'edit_timing_narration_subtitles_unchanged': True,
        'youtube_verification': 'pending'}, ensure_ascii=False, indent=2) + '\n')
    files = sorted((ROOT / 'deliverables').iterdir())
    (ROOT / 'deliverables/SHA256SUMS_shared.txt').write_text(''.join(
        f'{sha(p)}  {p.name}\n' for p in files))
    print(json.dumps(results, ensure_ascii=False, indent=2), flush=True)

if __name__ == '__main__':
    main()
