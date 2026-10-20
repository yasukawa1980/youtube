"""v03: subpixel camera motion, female Japanese narration and +3 dB BGM.

Environment: WOM_EPISODE_ROOT (new output), WOM_PREVIOUS_ROOT (v02).
Never overwrites v02. The English timeline stays fixed; subtitle replacement is deferred.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from wom01_multilingual_render import ff, read, save, sha, probe, measure, make_audio

FPS, SR = 30, 24000


def prepare(root, previous):
    assert root != previous
    for d in ('records', 'deliverables', 'review', 'audio/en', 'audio/ja', '_work/render'):
        (root / d).mkdir(parents=True, exist_ok=True)
    for name in ('content.json', 'content_en.json', 'master_timeline.json', 'visual_manifest.json',
                 'narration_timeline_en.json', 'narration_segments_en.json'):
        dst = root / 'records' / name
        if not dst.exists():
            shutil.copy2(previous / 'records' / name, dst)
    for name in ('assets/composed_en',):
        if not (root / name).exists():
            shutil.copytree(previous / name, root / name)
    dry = root / 'audio/en/narration.wav'
    if not dry.exists():
        shutil.copy2(previous / 'audio/en/narration.wav', dry)
    save(root / 'records/revision_request.json', {
        'version': 'v03', 'source_root': str(previous), 'duration_seconds': 666.2,
        'voice_en': 'Kokoro: af_heart (B), existing narration unchanged',
        'voice_ja': 'VOICEVOX:冥鳴ひまり', 'style_id': 14, 'model': '1.vvm',
        'ja_speed': 1.0, 'bgm_change_db': 3, 'target_bgm_under_narration_dbfs': -33.5,
        'video': '1080p30, fractional-coordinate cubic perspective zoom; fixed header/footer',
        'subtitles_burned_in': False, 'external_subtitle_update': 'deferred at owner request',
        'voice_terms': ['https://www.meimeihimari.com/terms-of-use', 'https://voicevox.hiroshiba.jp/term/'],
        'model_source': 'https://github.com/VOICEVOX/voicevox_vvm/releases/download/0.16.4/1.vvm',
        'model_sha256': '8df20815be9a84a4b4723b9e778d2ef6a4df277e4872fe9efe29676a60e02774',
        'human_full_listening': False, 'paid_services': False, 'publication': False,
    })


def fit_japanese(root):
    """Re-synthesize only sentences whose new voice would overrun a v02 slot."""
    master = read(root / 'records/master_timeline.json')
    for attempt in range(4):
        narr = read(root / 'records/narration_segments_ja.json')
        pacing = {s['id']: s['native_speed'] for s in narr['segments']}
        overflow = []
        for common, seg in zip(master['segments'], narr['segments']):
            available = common['end'] - common['start'] - common['gap_min_seconds']
            if seg['duration_seconds'] > available:
                speed = round(seg['native_speed'] * seg['duration_seconds'] / (available-.35), 4)
                assert speed <= 1.2, (seg['id'], speed)
                pacing[seg['id']] = speed
                overflow.append((seg['id'], speed))
        if not overflow:
            print('All female segments fit the unchanged English timeline', flush=True)
            return
        if attempt == 3:
            raise RuntimeError(f'Japanese timing still overflows: {overflow}')
        print('Adjusting long Japanese segments:', overflow, flush=True)
        save(root / 'records/japanese_pacing.json', pacing)
        subprocess.run([sys.executable, str(Path(__file__).with_name('wom01_multilingual_narration.py'))], check=True)
    raise RuntimeError('Japanese timing still overflows')


def align_japanese(root):
    master = read(root / 'records/master_timeline.json')
    narr = read(root / 'records/narration_segments_ja.json')
    assert [s['id'] for s in narr['segments']] == [s['id'] for s in master['segments']]
    track = np.zeros(round(master['duration_seconds'] * SR), np.float32)
    aligned = []
    for common, seg in zip(master['segments'], narr['segments']):
        audio, sr = sf.read(root / seg['audio_file'], dtype='float32')
        assert sr == SR
        available = common['end'] - common['start'] - common['gap_min_seconds']
        assert len(audio)/SR <= available, (seg['id'], len(audio)/SR, available)
        start = round(common['start'] * SR)
        track[start:start+len(audio)] = audio
        cues = [{**c, 'start': c['start']+common['start'], 'end': c['end']+common['start']} for c in seg['cues']]
        aligned.append({**seg, 'start': common['start'], 'end': common['end'], 'cues': cues})
        common['speech_seconds']['ja'] = len(audio)/SR
        common['padding_seconds']['ja'] = common['end']-common['start']-len(audio)/SR
        common['speech_end'] = common['start']+max(common['speech_seconds'].values())
    sf.write(root / 'audio/ja/narration.wav', track, SR, subtype='PCM_16')
    save(root / 'records/master_timeline.json', master)
    save(root / 'records/narration_timeline_ja.json', {**narr, 'duration_seconds': master['duration_seconds'], 'segments': aligned})
    print('Japanese aligned without changing English segment times', flush=True)


def camera_filter(count):
    # Perspective uses fractional coordinates; zoompan rounds crop origins to pixels.
    # Animate only the illustration band; keep heading/source text steady.
    z = f'(1+0.025*on/{max(count-1,1)})'
    x, y = f'(W-W/{z})/2', f'(H-H/{z})/2'
    perspective = (f"perspective=x0='{x}':y0='{y}':x1='W-{x}':y1='{y}':"
                   f"x2='{x}':y2='H-{y}':x3='W-{x}':y3='H-{y}':"
                   "sense=source:eval=frame:interpolation=cubic")
    return ("[0:v]split=2[base][art];[art]crop=1920:806:0:164,format=yuv444p,"
            + perspective + "[moving];[base][moving]overlay=0:164:format=yuv444,format=yuv420p[v]")


def pictures(root, limit=0):
    master = read(root / 'records/master_timeline.json')
    manifest = read(root / 'records/visual_manifest.json')
    work = root / '_work/render'
    parts, shots = [], []
    for i, seg in enumerate(master['segments']):
        images = [s for s in manifest['shots'] if s['segment_id'] == seg['id']]
        first = 0 if i == 0 else round(seg['start']*FPS)
        last = round(seg['end']*FPS)
        bounds = np.linspace(first, last, len(images)+1).round().astype(int)
        for j, image in enumerate(images):
            count = int(bounds[j+1]-bounds[j])
            path = work / f'{seg["id"]}_{j:02}_subpixel_v03.mp4'
            picture = root / image['file']
            expected = {'image_sha256':sha(picture), 'frames':count, 'filter':camera_filter(count), 'crf':20}
            stamp=path.with_suffix('.json')
            if not path.exists() or not stamp.exists() or read(stamp)!=expected:
                ff(['-loop', 1, '-framerate', FPS, '-i', picture, '-filter_complex_threads', 2,
                    '-filter_complex', camera_filter(count), '-map', '[v]', '-frames:v', count,
                    '-an', '-c:v', 'libx264', '-threads', 4, '-preset', 'veryfast', '-crf', 20,
                    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', path])
                save(stamp,expected)
            assert abs(float(probe(path)['format']['duration'])-count/FPS) < 1/FPS
            parts.append(path)
            shots.append({**image,'start':int(bounds[j])/FPS,'end':int(bounds[j+1])/FPS,
                          'frames':count,'encoded_file':str(path.relative_to(root))})
            print('PICTURE',seg['id'],j,'frames',count,flush=True)
            if limit and len(parts)>=limit:
                return
    concat = work / 'concat.txt'
    concat.write_text(''.join(f"file '{p}'\n" for p in parts))
    ff(['-f','concat','-safe',0,'-i',concat,'-c','copy','-movflags','+faststart',root/'_work/picture_master.mp4'])
    save(root/'records/render_shots.json',shots)


def package(root):
    source_picture=root/'_work/picture_master.mp4'
    assert probe(source_picture)['streams'][0]['time_base']=='1/15360'
    # MP4 concatenation rounds segment durations to microseconds. Snap PTS/DTS
    # back to the 512-tick (1/30 s) grid without re-encoding any pictures.
    picture=root/'_work/picture_cfr.mp4'
    ff(['-i',source_picture,'-map','0:v:0','-c','copy','-bsf:v',
        'setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512',
        '-movflags','+faststart',picture])
    total=read(root/'records/master_timeline.json')['duration_seconds']
    files=[]
    for lang in ['en','ja']:
        out=root/f'deliverables/EP001_Anubis_{lang}_v03_1080p30.mp4'
        ff(['-i',picture,'-i',root/f'deliverables/EP001_audio_{lang}.m4a',
            '-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0',
            'language='+('eng' if lang=='en' else 'jpn'),'-metadata','comment='+('English narration: Kokoro / af_heart' if lang=='en' else 'Japanese narration: VOICEVOX:冥鳴ひまり'),'-movflags','+faststart',out])
        files.append(out)
        short=root/f'deliverables/EP001_{lang}_v03_first90s.mp4'
        ff(['-i',out,'-t',90,'-map','0','-c','copy','-movflags','+faststart',short])
    report={'version':'v03','duration_seconds':total,'fps':FPS,'human_full_listening':False,
            'subtitles_burned_in':False,'external_subtitles':'deferred','files':[]}
    for path in files:
        ff(['-i',path,'-f','null','-'])
        info=probe(path);levels=measure(path)
        assert abs(float(info['format']['duration'])-total)<1/FPS
        assert [s['codec_type'] for s in info['streams']]==['video','audio']
        assert info['streams'][0]['avg_frame_rate']=='30/1'
        assert abs(float(levels['input_i'])+16)<.5 and float(levels['input_tp'])<=-2
        video_hash=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:v:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
        report['files'].append({'file':path.name,'bytes':path.stat().st_size,'sha256':sha(path),
                               'video_stream_hash':video_hash,'full_decode':'pass','levels':levels,'probe':info})
        print('QC',path.name,levels['input_i'],levels['input_tp'],flush=True)
    assert report['files'][0]['video_stream_hash']==report['files'][1]['video_stream_hash']
    save(root/'records/qc_v03.json',report)
    (root/'deliverables/SHA256SUMS.txt').write_text(''.join(f'{sha(p)}  {p.name}\n' for p in sorted((root/'deliverables').iterdir()) if p.suffix in ['.mp4','.wav','.m4a']))
    (root/'deliverables/音声クレジット.txt').write_text('English: Kokoro / af_heart (B)\n日本語音声：VOICEVOX:冥鳴ひまり\nhttps://www.meimeihimari.com/terms-of-use\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','fit','align','audio','pictures','picture-test','package'])
    args=p.parse_args();root=Path(os.environ['WOM_EPISODE_ROOT']);previous=Path(os.environ['WOM_PREVIOUS_ROOT'])
    if args.stage=='prepare':prepare(root,previous)
    elif args.stage=='fit':fit_japanese(root)
    elif args.stage=='align':align_japanese(root)
    elif args.stage=='audio':make_audio(root)
    elif args.stage in ('pictures','picture-test'):pictures(root,1 if args.stage=='picture-test' else 0)
    elif args.stage=='package':package(root)

if __name__=='__main__':main()
