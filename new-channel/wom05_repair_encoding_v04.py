"""Rebuild from independent shot decoders: mixed-profile v02 cannot be input.

Each intermediate shot is opened in a fresh decoder. Raw yuv420p frames go
to one encoder, so decoder state never crosses shot boundaries. The v02
MP4 is used only for its unchanged compressed audio and metadata.
"""
import json
import shutil
import subprocess
from wom05_repair_encoding_v03 import BASE, SOURCE, probe, sha, stream_hash

ROOT = BASE / '修正版_v04_20261025'

def main():
    for folder in ['deliverables', 'records', '_work', 'review']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    shots = json.loads((SOURCE/'records/render_shots.json').read_text())
    assert sum(x['frames'] for x in shots) == 11065
    src_en = SOURCE/'deliverables/EP005_Tengu_en_v02_1080p30.mp4'
    out_en = ROOT/'deliverables/EP005_Tengu_en_v04_1080p30.mp4'
    assert not out_en.exists()
    args = ['ffmpeg','-nostdin','-n','-hide_banner','-v','warning',
        '-f','rawvideo','-pixel_format','yuv420p','-video_size','1920x1080',
        '-framerate','30','-i','pipe:0','-i',str(src_en),
        '-map','0:v:0','-map','1:a:0','-map_metadata','1',
        '-c:v','libx264','-preset','medium','-crf','16','-threads','6',
        '-profile:v','high','-level:v','4.1','-pix_fmt','yuv420p',
        '-g','60','-keyint_min','30','-bf','2','-maxrate','20M','-bufsize','30M',
        '-fps_mode','passthrough','-video_track_timescale','15360',
        '-movie_timescale','48000','-color_primaries','bt709','-color_trc','bt709',
        '-colorspace','bt709','-c:a','copy','-movflags','+faststart',
        '-progress',str(ROOT/'_work/encode_progress.txt'),str(out_en)]
    records = []
    with (ROOT/'records/encode.log').open('w') as log:
        enc = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=log)
        try:
            for shot in shots:
                src = shot['encoded_file']
                info = probe(src)['streams'][0]
                assert int(info['nb_frames']) == shot['frames']
                assert (info['width'],info['height']) == (1920,1080)
                subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','3',
                    '-i',src,'-map','0:v:0','-an','-pix_fmt','yuv420p',
                    '-fps_mode','passthrough','-f','rawvideo','pipe:1'],
                    stdout=enc.stdin, stderr=log, check=True)
                records.append({'key':shot['key'],'file':src,'frames':shot['frames'],
                    'profile':info['profile']})
                print('DECODED',shot['key'],shot['frames'],flush=True)
            enc.stdin.close()
            assert enc.wait() == 0
        except BaseException:
            enc.kill()
            enc.wait()
            raise
    results = []
    for lang in ['en','ja']:
        src = SOURCE/f'deliverables/EP005_Tengu_{lang}_v02_1080p30.mp4'
        dst = ROOT/f'deliverables/EP005_Tengu_{lang}_v04_1080p30.mp4'
        if lang == 'ja':
            subprocess.run(['ffmpeg','-nostdin','-n','-v','error','-i',str(out_en),
                '-i',str(src),'-map','0:v:0','-map','1:a:0','-map_metadata','1',
                '-c','copy','-movie_timescale','48000','-movflags','+faststart',str(dst)],check=True)
        a,b = probe(src),probe(dst)
        assert a['streams'][0]['nb_frames']==b['streams'][0]['nb_frames']=='11065'
        assert a['format']['duration']==b['format']['duration']
        assert b['streams'][0]['profile']=='High'
        assert stream_hash(src,'0:a:0')==stream_hash(dst,'0:a:0')
        results.append({'file':dst.name,'sha256':sha(dst),'bytes':dst.stat().st_size,
            'frames':11065,'duration':b['format']['duration'],'audio_encoded_stream_identical':True})
        shutil.copy2(src.with_suffix('.srt'),dst.with_suffix('.srt'))
    for name in ['EP005_audio_ja.wav','EP005_thumbnail_met_24145.jpg']:
        shutil.copy2(SOURCE/'deliverables'/name,ROOT/'deliverables'/name)
    (ROOT/'records/repair.json').write_text(json.dumps({'files':results,
        'shots':records,'command':args,'method':'Independent shot decoders feeding one raw-video encoder',
        'youtube_verification':'pending'},ensure_ascii=False,indent=2)+'\n')
    files=sorted((ROOT/'deliverables').iterdir())
    (ROOT/'deliverables/SHA256SUMS_shared.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files))
    print(json.dumps(results,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':main()
