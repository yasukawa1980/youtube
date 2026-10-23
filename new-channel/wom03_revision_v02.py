"""EP003 v02: append one M18 sentence and use the shared 10-second end card.

Run with the existing requirements_wom03 Python environment. Stages:
prepare, narrate, brand, timeline, audio, pictures, package, reviews, verify,
docs, share, export. v01 and other episodes are read-only inputs.
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
BASE = Path('/Users/ryo/Desktop/新チャンネル')
OLD = BASE / 'EP003_Medusa/確認版_v01_20261023'
ROOT = BASE / 'EP003_Medusa/確認版_v02_20261023'
BRAND = BASE / 'ブランド素材/エンドカード_共通版_v02_20261023'
GUIDE = REPO / 'new-channel/wom03_確認版_v02_20261023'
BGUIDE = REPO / 'new-channel/branding/20261023_エンドカード共通版_v02'
GH = 'yasukawa1980/youtube'
TAG = 'wom03-medusa-v02-20261023'
os.environ['WOM03_ROOT'] = str(ROOT)
from wom01_multilingual_render import read, save, sha, ff, probe, measure, rms
from wom01_subtitles import pages, to_srt
from wom01_quiet_origins import stream_hash
from wom03_render import camera

SR = 24000
AR = 48000
FPS = 30


def out(lang, review=False):
    return ROOT / f'deliverables/EP003_Medusa_{lang}_v02{"_subtitled_review" if review else ""}_1080p30.mp4'


def oldvideo(lang, review=False):
    return OLD / f'deliverables/EP003_Medusa_{lang}_v01{"_subtitled_review" if review else ""}_1080p30.mp4'


def packets(path, kind):
    return json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-select_streams', kind + ':0',
        '-show_packets', '-show_data_hash', 'sha256', '-of', 'json', str(path)
    ]))['packets']


def prepare():
    for root in [ROOT, BRAND]:
        for folder in ['records', 'deliverables', 'review', '_work']:
            (root / folder).mkdir(parents=True, exist_ok=True)
    for folder in ['assets', '_work/render', 'audio/en/sentences', 'audio/ja/sentences']:
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    for lang in ['en', 'ja']:
        name = 'content_en.json' if lang == 'en' else 'content.json'
        src = REPO / 'new-channel/episodes/EP003_Medusa/records' / name
        target = ROOT / 'records' / name
        if target.exists():
            assert sha(target) == sha(src), 'Use a new version for a changed script'
        else:
            shutil.copy2(src, target)
        before, after = read(OLD / 'records' / name), read(target)
        assert before['segments'][:17] == after['segments'][:17]
        assert 'v04' in after['script_version']
        for i in range(1, 6):
            source_i = 4 if i == 5 else i
            if i == 4:
                continue
            for suffix in ['.wav', '.json']:
                source = OLD / f'audio/{lang}/sentences/M18-{source_i:02}{suffix}'
                shutil.copy2(source, ROOT / f'audio/{lang}/sentences/M18-{i:02}{suffix}')
    for name in ['visual_manifest.json', 'source_assets.json', 'ai_images.json', 'ai_videos.json',
                 'reading_replacements.json', 'pronunciation_locations.json', 'chapters.json']:
        shutil.copy2(OLD / 'records' / name, ROOT / 'records' / name)
    shutil.copy2(OLD / 'assets/M18_01_credits.png', ROOT / 'assets/M18_01_credits.png')
    for key in ['A24', 'A04']:
        shutil.copy2(OLD / f'deliverables/EP003_thumbnail_{key}.jpg',
                     ROOT / f'deliverables/EP003_thumbnail_{key}.jpg')
    save(ROOT / 'records/revision_request.json', {
        'source_root': str(OLD), 'source_release_id': 421292434,
        'claude_commit': '0fbd21c', 'script_version': 'v04',
        'changes': ['M18: one calm like/subscribe sentence before thanks',
                    'Shared end card v02: 10 seconds; retain layout and natural ending'],
        'M01_M17_unchanged_required': True, 'new_paid_services': False,
        'youtube_posted': False, 'human_auditory_review_completed': False,
        'input_script_sha256': {n: sha(ROOT / 'records' / n)
                                for n in ['content.json', 'content_en.json']},
    })
    print('PREPARED', ROOT, flush=True)


def narrate():
    import wom03_produce as synthesis
    real_content = synthesis.content
    synthesis.content = lambda lang: {'segments': [real_content(lang)['segments'][-1]]}
    for lang in ['en', 'ja']:
        synthesis.narrate(lang)
        updated = read(ROOT / f'records/narration_segments_{lang}.json')
        before = read(OLD / f'records/narration_segments_{lang}.json')
        updated['segments'] = before['segments'][:17] + updated['segments']
        save(ROOT / f'records/narration_segments_{lang}.json', updated)
    print('M18 SYNTHESIZED; only new sentence M18-04 generated in each language', flush=True)


def brand():
    source = Path(read(OLD / 'records/request.json')['endcard'])
    source_wav = source.with_suffix('.wav')
    assert source_wav.exists()
    wav = BRAND / 'deliverables/Quiet_Origins_endcard_v02.wav'
    src_audio, sr = sf.read(source_wav, dtype='float32', always_2d=True)
    assert sr == AR and len(src_audio) == 20 * AR
    # Preserve the original attack, then crossfade into its complete five-second ending.
    # The last 4.7 seconds, including the final second, remain sample-identical.
    nfade = round(.3 * AR)
    a, b = src_audio[:round(5.3 * AR)].copy(), src_audio[15 * AR:].copy()
    ramp = np.linspace(0, 1, nfade, dtype=np.float32)[:, None]
    audio = np.concatenate([a[:-nfade], a[-nfade:] * (1-ramp) + b[:nfade] * ramp,
                            b[nfade:]])
    assert len(audio) == 10 * AR
    sf.write(wav, audio, AR, subtype='PCM_24')
    assert np.array_equal(sf.read(wav, dtype='int32')[0][-AR:],
                          sf.read(source_wav, dtype='int32')[0][-AR:])
    picture = BRAND / '_work/endcard_picture_v02.mp4'
    # Compress only the subtle background-light motion before t=19. The old final
    # 30 pictures play at the original rate; lettering/layout never change.
    selection = r"select='if(lt(n,570),gt(floor(n*270/570),floor((n-1)*270/570)),1)',setpts=N/(30*TB)"
    ff(['-i', source, '-vf', selection, '-frames:v', 300, '-an', '-c:v', 'libx264',
        '-preset', 'veryfast', '-crf', 18, '-threads', 4, '-pix_fmt', 'yuv420p',
        '-video_track_timescale', 15360, '-color_primaries', 'bt709',
        '-color_trc', 'bt709', '-colorspace', 'bt709', picture])
    final = BRAND / 'deliverables/Quiet_Origins_endcard_v02.mp4'
    ff(['-i', picture, '-i', wav, '-map', '0:v:0', '-map', '1:a:0', '-c:v', 'copy',
        '-c:a', 'aac', '-b:a', '192k', '-ar', AR, '-movie_timescale', AR,
        '-movflags', '+faststart', final])
    v = next(s for s in probe(final)['streams'] if s['codec_type'] == 'video')
    assert int(v['nb_frames']) == 300
    imgs = []
    for name, frame in [('first', 0), ('last', 299), ('before_final_second', 270)]:
        target = BRAND / f'review/endcard_v02_{name}.jpg'
        ff(['-i', final, '-vf', f'select=eq(n\\,{frame}),scale=1280:720',
            '-frames:v', 1, '-q:v', 3, target])
        shutil.copy2(target, ROOT / 'review' / target.name)
        imgs.append({'file': target.name, 'frame': frame, 'sha256': sha(target)})
    envelope = []
    for start in [0, 4.8, 5, 5.3, 8, 9, 9.8, 9.9]:
        envelope.append({'start': start, 'window_seconds': .1,
                         'rms_dbfs': rms(audio[round(start*AR):round((start+.1)*AR)])})
    report = {
        'passed': True, 'source': str(source), 'source_sha256': sha(source),
        'source_wav': str(source_wav), 'source_wav_sha256': sha(source_wav),
        'output': str(final), 'sha256': sha(final),
        'video_stream_sha256': stream_hash(final, 'v'),
        'audio_stream_sha256': stream_hash(final, 'a'), 'wav_sha256': sha(wav),
        'duration_seconds': 10, 'frames': 300, 'audio_samples': len(audio),
        'layout_and_left_element_space': 'Unchanged: source pictures retimed only',
        'video_mapping': '270 frames sampled from source frames 0..569, followed by source 570..599 at native 30fps; re-encoded',
        'audio_mapping': 'source 0..5.3s plus 15..20s, 0.3s linear crossfade; native pitch/rate; final 4.7s unchanged',
        'final_second_wav_samples_identical': True,
        'ending': 'Source video has no visual fade; fixed logo/title continue. Original five-second audio fade retained; no new visual fade.',
        'envelope': envelope, 'loudness': measure(final), 'images': imgs,
        'human_listening': False, 'EP001_EP002_modified': False,
    }
    save(BRAND / 'records/endcard_v02.json', report)
    save(ROOT / 'records/endcard_v02.json', report)
    for p in (BRAND / 'deliverables').iterdir():
        shutil.copy2(p, ROOT / 'deliverables' / p.name)
    print('BRAND', report['loudness']['input_i'], envelope[-1], flush=True)


def make_subtitles(lang, segment, start, endcard):
    sub = copy.deepcopy(read(OLD / f'records/subtitle_cues_{lang}.json')['cues'])
    sub = [c for c in sub if not c['sentence_id'].startswith('M18-')]
    for c in segment['cues']:
        chunks = pages(c['text'], lang)
        weights = np.array([len(x.replace('\n', '')) for x in chunks], dtype=float)
        span = c['end'] - c['start']
        durations = span * weights / weights.sum()
        if len(chunks) > 1:
            assert span >= 1.4 * len(chunks)
            fixed = np.zeros(len(chunks), bool)
            while np.any(durations < 1.4 - 1e-9):
                fixed |= durations < 1.4
                durations[fixed] = 1.4
                durations[~fixed] = (span - 1.4 * fixed.sum()) * weights[~fixed] / weights[~fixed].sum()
        pos = start + c['start']
        for i, chunk in enumerate(chunks):
            stop = start + c['end'] if i == len(chunks)-1 else pos + float(durations[i])
            sub.append({'sentence_id': c['id'], 'start': pos, 'end': stop, 'text': chunk})
            pos = stop
    for i, c in enumerate(sub):
        if c['end']-c['start'] < 1.4-1e-6:
            cap = sub[i+1]['start']-.01 if i+1 < len(sub) else endcard-.05
            assert c['start']+1.4 <= cap
            c['end'] = c['start']+1.4
    text = read(ROOT / 'records' / ('content_en.json' if lang == 'en' else 'content.json'))
    clean = lambda x: re.sub(r'\s+', '', x)
    assert clean(''.join(c['text'] for c in sub)) == clean(''.join(s['text'] for s in text['segments']))
    assert all(len(c['text'].splitlines()) <= 2 and max(map(len, c['text'].splitlines())) <= (42 if lang == 'en' else 23) for c in sub)
    assert all(c['end']-c['start'] >= 1.4-1e-6 for c in sub)
    assert all(a['end'] <= b['start'] for a, b in zip(sub, sub[1:]))
    previous = read(OLD / f'records/subtitle_cues_{lang}.json')['cues']
    assert [c for c in sub if not c['sentence_id'].startswith('M18-')] == [c for c in previous if not c['sentence_id'].startswith('M18-')]
    srt = ROOT / f'deliverables/EP003_Medusa_{lang}_v02_1080p30.srt'
    srt.write_text(to_srt(sub))
    save(ROOT / f'records/subtitle_cues_{lang}.json', {'count': len(sub), 'cues': sub,
         'M01_M17_identical': True, 'script_matches_ignoring_layout_whitespace': True})
    return {'count': len(sub), 'min_seconds': min(c['end']-c['start'] for c in sub),
            'max_line_chars': max(len(line) for c in sub for line in c['text'].splitlines()),
            'M01_M17_identical': True, 'script_matches': True}


def timeline():
    m = read(OLD / 'records/master_timeline.json')
    original_duration = m['duration_seconds']
    original_m18_end = m['segments'][-1]['end']
    last = {l: read(ROOT / f'records/narration_segments_{l}.json')['segments'][-1] for l in ['en', 'ja']}
    start = m['segments'][-1]['start']
    end = math.ceil((start + max(s['duration_seconds'] for s in last.values()) + 1.2) * FPS) / FPS
    m['segments'][-1].update(speech_end=start+max(s['duration_seconds'] for s in last.values()),
        end=end, speech_seconds={l: s['duration_seconds'] for l, s in last.items()})
    m['brand_intervals']['endcard'] = [end, end+10]
    m['duration_seconds'] = end+10
    m['revision'] = {'v01_duration': original_duration, 'M18_extension_seconds': end-original_m18_end,
                     'formula': 'v01 - 10 + M18 extension', 'version': 'v02'}
    assert abs(m['duration_seconds'] - (original_duration-10+end-original_m18_end)) < 1e-8
    save(ROOT / 'records/master_timeline.json', m)
    checks = {}
    for lang in ['en', 'ja']:
        tl = read(OLD / f'records/narration_timeline_{lang}.json')
        seg = copy.deepcopy(last[lang])
        seg.update(m['segments'][-1])
        seg['cues'] = [{**c, 'start': c['start']+start, 'end': c['end']+start} for c in last[lang]['cues']]
        tl['segments'][-1] = seg
        tl['duration_seconds'] = m['duration_seconds']
        save(ROOT / f'records/narration_timeline_{lang}.json', tl)
        checks[lang] = make_subtitles(lang, last[lang], start, end)
        dry = np.zeros(round(m['duration_seconds']*SR), np.float32)
        old, sr = sf.read(OLD / f'audio/{lang}/narration.wav', dtype='float32')
        cut = round(start*SR)
        dry[:cut] = old[:cut]
        x, sr = sf.read(ROOT / f'audio/{lang}/M18.wav', dtype='float32')
        dry[cut:cut+len(x)] = x
        sf.write(ROOT / f'audio/{lang}/narration.wav', dry, SR, subtype='PCM_16')
    save(ROOT / 'records/subtitle_validation.json', checks)
    print('TIMELINE', m['duration_seconds'], 'frames', round(m['duration_seconds']*FPS),
          'endcard', m['brand_intervals']['endcard'], checks, flush=True)


def adts_frames(data):
    frames = []
    i = 0
    while i < len(data):
        assert data[i] == 255 and data[i+1] & 0xF6 == 0xF0
        size = ((data[i+3] & 3) << 11) | (data[i+4] << 3) | (data[i+5] >> 5)
        frames.append(data[i:i+size])
        i += size
    assert i == len(data)
    return frames


def preserve_aac_prefix(lang, wav, total_samples, boundary):
    """Copy original AAC frames before M18; encode only a packet-aligned suffix.

    Include the old encoder's priming frame once. Drop the new suffix's priming
    frame. Explicit PTS/duration recreates one MP4 edit list and an exact last
    packet duration. Verification compares both packet data and decoded PCM.
    """
    folder = ROOT / '_work'
    source = OLD / f'deliverables/EP003_audio_{lang}.m4a'
    old_adts = folder / f'{lang}_old.aac'
    ff(['-i', source, '-c:a', 'copy', '-f', 'adts', old_adts])
    old_frames = adts_frames(old_adts.read_bytes())
    old_packets = packets(source, 'a')
    assert len(old_frames) == len(old_packets)
    assert int(old_packets[0]['pts']) == -1024
    splice = math.ceil(boundary/1024)*1024
    kept = [f for f, p in zip(old_frames, old_packets) if int(p['pts']) < splice]
    suffix = folder / f'{lang}_suffix.m4a'
    ff(['-i', wav, '-af', f'atrim=start_sample={splice},asetpts=PTS-STARTPTS',
        '-ar', AR, '-c:a', 'aac', '-b:a', '192k', '-movie_timescale', AR, suffix])
    suffix_adts = folder / f'{lang}_suffix.aac'
    ff(['-i', suffix, '-c:a', 'copy', '-f', 'adts', suffix_adts])
    new_frames = adts_frames(suffix_adts.read_bytes())
    assert int(packets(suffix, 'a')[0]['pts']) == -1024
    combined = kept + new_frames[1:]
    # AAC includes exactly one encoder-delay packet, followed by ceil(n/1024).
    count = math.ceil(total_samples/1024)+1
    assert len(combined) >= count
    combined = combined[:count]
    path = folder / f'{lang}_joined.aac'
    path.write_bytes(b''.join(combined))
    last_duration = total_samples - (count-2)*1024
    bsf = f'setts=time_base=1/48000:prescale=1:pts=N*1024-1024:dts=N*1024-1024:duration=if(eq(N\\,{count-1})\\,{last_duration}\\,1024)'
    final = ROOT / f'deliverables/EP003_audio_{lang}.m4a'
    ff(['-i', path, '-map', '0:a:0', '-c:a', 'copy', '-bsf:a', bsf,
        '-movie_timescale', AR, '-movflags', '+faststart', final])
    actual = packets(final, 'a')
    assert int(next(s for s in probe(final)['streams'] if s['codec_type']=='audio')['duration_ts']) == total_samples
    a = [p['data_hash'] for p in old_packets if int(p['pts']) < splice]
    b = [p['data_hash'] for p in actual[:len(a)]]
    assert a == b
    return {'splice_sample': splice, 'splice_seconds': splice/AR,
            'preserved_packets_including_priming': len(a),
            'packet_data_sha256': hashlib.sha256(''.join(a).encode()).hexdigest(),
            'prefix_aac_packet_data_identical': True, 'final_duration_samples': total_samples}


def audio():
    m = read(ROOT / 'records/master_timeline.json')
    duration = m['duration_seconds']
    n = round(duration*SR)
    cut = round(m['segments'][-1]['start']*SR)
    endcard = m['brand_intervals']['endcard'][0]
    t = np.arange(n)/SR
    base = .006*np.sin(2*np.pi*146.832384*t)*(.66+.34*np.sin(2*np.pi*t/53)**2)+.003*np.sin(2*np.pi*220*t+.5)
    notes = np.array([293.664768,349.228231,440.,391.995436,293.664768,523.251131])
    local = t % 14
    pitch = notes[np.floor(t/14).astype(int) % len(notes)]
    pluck = .018*np.sin(2*np.pi*pitch*local)*np.exp(-local/2.1)*(1-np.exp(-local/.045))
    music = np.stack([base+pluck,base+.92*pluck+.0017*np.sin(2*np.pi*293.664768*t+.45)],axis=1).astype(np.float32)
    mask = np.zeros(n, bool)
    duck = np.ones(n, np.float32)
    for s in m['segments']:
        a, b = s['start'], s['speech_end']
        mask[round(a*SR):round(b*SR)] = True
        duck = np.minimum(duck, 1-np.minimum(np.clip((t-(a-.18))/.18,0,1),np.clip((b+.4-t)/.4,0,1)))
    # Use the v01 calibration constant, never renormalize the complete music bed.
    oldm = read(OLD / 'records/master_timeline.json')
    oldn = round(oldm['duration_seconds']*SR)
    oldt = np.arange(oldn)/SR
    oldbase = .006*np.sin(2*np.pi*146.832384*oldt)*(.66+.34*np.sin(2*np.pi*oldt/53)**2)+.003*np.sin(2*np.pi*220*oldt+.5)
    oldlocal = oldt % 14
    oldpitch = notes[np.floor(oldt/14).astype(int) % len(notes)]
    oldpluck = .018*np.sin(2*np.pi*oldpitch*oldlocal)*np.exp(-oldlocal/2.1)*(1-np.exp(-oldlocal/.045))
    oldraw = np.stack([oldbase+oldpluck,oldbase+.92*oldpluck+.0017*np.sin(2*np.pi*293.664768*oldt+.45)],axis=1).astype(np.float32)
    oldmask = np.zeros(oldn, bool)
    for s in oldm['segments']:
        oldmask[round(s['start']*SR):round(s['speech_end']*SR)] = True
    calibration = -33.5-rms(oldraw[oldmask])
    music *= 10**(calibration/20)
    music *= 10**((4*duck)/20)[:,None]
    music *= np.clip(t/.7,0,1)[:,None]
    oldmusic, sr = sf.read(OLD / 'audio/common_bgm_and_brand.wav',dtype='float32')
    music[:cut] = oldmusic[:cut]
    i = round(endcard*SR)
    fade = round(.2*SR)
    music[i-fade:i] *= np.linspace(1,0,fade)[:,None]
    brand_wav = ROOT / '_work/endcard_24k.wav'
    ff(['-i', BRAND / 'deliverables/Quiet_Origins_endcard_v02.wav', '-ar', SR,
        '-c:a', 'pcm_f32le', brand_wav])
    brand_audio, sr = sf.read(brand_wav,dtype='float32')
    music[i:] = brand_audio[:n-i]
    sf.write(ROOT / 'audio/common_bgm_and_brand.wav',music,SR,subtype='FLOAT')
    checks = {'bgm_calibration_gain_db': calibration, 'pause_boost_db': 4,
              'bgm_prefix_sample_identical': np.array_equal(music[:cut],oldmusic[:cut]),
              'languages': {}}
    for lang in ['en', 'ja']:
        olddry, sr = sf.read(OLD / f'audio/{lang}/narration.wav',dtype='float32')
        oldnormal, sr = sf.read(OLD / f'audio/{lang}/normalized.wav',dtype='float32')
        nonzero = np.abs(olddry)>1e-3
        norm_gain = float(np.median(oldnormal[nonzero]/olddry[nonzero]))
        oldmix, sr = sf.read(OLD / f'audio/{lang}/mix.wav',dtype='float32')
        eligible = np.abs(oldnormal[:cut])>1e-3
        final_gain = float(np.median((oldmix[:cut,0]-oldmusic[:cut,0])[eligible]/oldnormal[:cut][eligible]))
        dry, sr = sf.read(ROOT / f'audio/{lang}/narration.wav',dtype='float32')
        old_voice_path=ROOT/f'_work/{lang}_old_M18_voice.wav'
        new_voice_path=ROOT/f'_work/{lang}_new_M18_voice.wav'
        old_speech_end=round(oldm['segments'][-1]['speech_end']*SR)
        sf.write(old_voice_path,(oldmix-oldmusic)[cut:old_speech_end],SR,subtype='FLOAT')
        new_speech_end=round(m['segments'][-1]['speech_end']*SR)
        sf.write(new_voice_path,np.repeat(dry[cut:new_speech_end,None],2,axis=1),SR,subtype='FLOAT')
        old_levels,new_levels=measure(old_voice_path),measure(new_voice_path)
        gain_db=min(float(old_levels['input_i'])-float(new_levels['input_i']),
                    -3-float(new_levels['input_tp']))
        mix = dry[:,None]*10**(gain_db/20)+music
        mix[:cut] = oldmix[:cut]
        # No whole-program normalization: earlier samples must remain identical.
        mix_path = ROOT / f'audio/{lang}/mix.wav'
        sf.write(mix_path,mix,SR,subtype='FLOAT')
        wav = ROOT / f'deliverables/EP003_audio_{lang}.wav'
        total = round(duration*AR)
        ff(['-i',mix_path,'-af',f'aresample=48000,apad=whole_len={total},atrim=end_sample={total}',
            '-ar',AR,'-c:a','pcm_s24le',wav])
        # Avoid the resampling filter boundary's few samples at the edit. The
        # archived 48kHz master prefix is copied byte-for-byte into the new WAV.
        prefix = round(m['segments'][-1]['start']*AR)
        oldpcm = sf.read(OLD / f'deliverables/EP003_audio_{lang}.wav',dtype='int32')[0][:prefix]
        fullpcm = sf.read(wav,dtype='int32')[0]
        fullpcm[:prefix] = oldpcm
        sf.write(wav,fullpcm,AR,subtype='PCM_24')
        newpcm = sf.read(wav,dtype='int32')[0][:prefix]
        assert np.array_equal(oldpcm,newpcm)
        aac = preserve_aac_prefix(lang,wav,total,prefix)
        levels = measure(ROOT / f'deliverables/EP003_audio_{lang}.m4a')
        assert abs(float(levels['input_i'])+16)<.3 and float(levels['input_tp'])<=-1
        checks['languages'][lang] = {'loudness': levels, 'v01_narration_median_gain_for_reference':norm_gain,
            'v01_mix_voice_gain':final_gain, 'M01_M17_float_mix_identical': True,
            'M18_gain_db':gain_db,'M18_reference_voice_loudness':old_levels,'M18_raw_voice_loudness':new_levels,
            'M01_M17_WAV_PCM_identical': True,'WAV_prefix_PCM_SHA256':hashlib.sha256(newpcm.tobytes()).hexdigest(),
            'prefix_samples_48k':prefix,'aac':aac,'wav_samples':total,'wav_sha256':sha(wav)}
        print('AUDIO',lang,levels['input_i'],levels['input_tp'],aac,flush=True)
    save(ROOT / 'records/audio_revision_v02.json',checks)


def pictures():
    m = read(ROOT / 'records/master_timeline.json')
    shots = copy.deepcopy(read(OLD / 'records/render_shots.json'))
    parts = []
    for s in shots[:-2]:
        source = OLD / s['encoded_file']
        parts.append(source)
        s['encoded_file'] = str(source)
        s['source_v01_sha256'] = sha(source)
    last = shots[-2]
    assert last['segment_id']=='M18'
    a,b = m['segments'][-1]['start'],m['segments'][-1]['end']
    frames = round((b-a)*FPS)
    image = ROOT / 'assets/M18_01_credits.png'
    target = ROOT / '_work/render/M18_01_credits.mp4'
    ff(['-loop',1,'-framerate',FPS,'-i',image,'-filter_complex_threads',2,
        '-filter_complex',camera(frames,last['camera_band']),'-map','[v]',
        '-frames:v',frames,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,
        '-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',target])
    last.update(start=a,end=b,frames=frames,encoded_file=str(target),file=str(image))
    parts.append(target)
    last = shots[-1]
    source = BRAND / 'deliverables/Quiet_Origins_endcard_v02.mp4'
    target = ROOT / '_work/render/endcard.mp4'
    ff(['-i',source,'-map','0:v:0','-c','copy',target])
    last.update(start=b,end=b+10,frames=300,encoded_file=str(target),approved_brand_source=str(source),
                source_sha256=sha(source))
    parts.append(target)
    listing = ROOT / '_work/concat.txt'
    listing.write_text(''.join(f"file '{p}'\nduration {s['frames']/30:.9f}\n" for p,s in zip(parts,shots)))
    raw = ROOT / '_work/picture_concat.mp4'
    ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw])
    final = ROOT / '_work/picture_master.mp4'
    ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v',
        'setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512',
        '-movie_timescale',AR,'-movflags','+faststart',final])
    assert sum(s['frames'] for s in shots)==round(m['duration_seconds']*FPS)
    save(ROOT / 'records/render_shots.json',shots)
    print('PICTURES',len(shots),flush=True)


def package():
    for lang in ['en','ja']:
        ff(['-i',ROOT/'_work/picture_master.mp4','-i',ROOT/f'deliverables/EP003_audio_{lang}.m4a',
            '-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0',
            'language='+('eng' if lang=='en' else 'jpn'),'-metadata','title=Quiet Origins / Medusa v02',
            '-movie_timescale',AR,'-movflags','+faststart',out(lang)])
        print('PACKAGED',lang,flush=True)


def reviews():
    import imageio_ffmpeg
    for lang in ['en','ja']:
        srt = ROOT / f'_work/{lang}.srt'
        shutil.copy2(out(lang).with_suffix('.srt'),srt)
        vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(out(lang)),
            '-vf',vf,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',
            '-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy',
            '-movie_timescale','48000','-movflags','+faststart','-progress',str(ROOT/f'_work/review_{lang}.txt'),str(out(lang,True))],check=True)
        assert stream_hash(out(lang),'a')==stream_hash(out(lang,True),'a')
        print('REVIEW',lang,flush=True)


def decoded_audio_hash(path, samples):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0',
        '-af',f'atrim=end_sample={samples}','-c:a','pcm_f32le','-f','hash','-hash','sha256','-'],text=True).strip()


def check_layout():
    import imageio_ffmpeg
    binary=imageio_ffmpeg.get_ffmpeg_exe()
    records=[]
    maxbottom=602  # Unchanged credits composition; maximum under the 3% camera checked below.
    shot=read(ROOT/'records/render_shots.json')[-2]
    center=sum(shot['camera_band'])/2
    maxbottom=max(max(t['bbox'][3],center+1.03*(t['bbox'][3]-center)) for t in shot['texts'])
    assert maxbottom<=700
    for lang in ['en','ja']:
        cues=[c for c in read(ROOT/f'records/subtitle_cues_{lang}.json')['cues'] if c['sentence_id'].startswith('M18-')]
        test=[{**c,'start':i+.1,'end':i+.9} for i,c in enumerate(cues)]
        srt=ROOT/f'_work/layout_{lang}.srt';srt.write_text(to_srt(test))
        for size in [14,26]:
            folder=ROOT/f'_work/layout_{lang}_{size}';folder.mkdir(exist_ok=True)
            vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize={size},BorderStyle=3,MarginV=12',select='mod(n,2)'"
            subprocess.run([binary,'-nostdin','-y','-v','error','-f','lavfi','-i',
                f'color=c=black:s=1920x1080:r=2:d={len(cues)}','-vf',vf,'-frames:v',str(len(cues)),
                '-fps_mode','passthrough',str(folder/'%04d.png')],check=True)
            boxes=[]
            for i,c in enumerate(cues,1):
                im=np.array(Image.open(folder/f'{i:04d}.png').convert('RGB'))
                ys,xs=np.where(im.max(axis=2)>100)
                box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
                assert box[1]>700
                boxes.append({'sentence_id':c['sentence_id'],'text':c['text'],'bbox':box})
            records.append({'language':lang,'font_size':size,'all_nonoverlapping':True,'boxes':boxes})
    save(ROOT/'records/subtitle_layout_v02.json',{'passed':True,'M01_M17':'v01 unchanged, prior 350 raster checks retained',
        'M18_content_bottom_with_zoom':maxbottom,'M18_checks':records})


def verify():
    m=read(ROOT/'records/master_timeline.json')
    frames=round(m['duration_seconds']*FPS);samples=frames*1600
    boundary=m['segments'][-1]['start'];prefix_frames=round(boundary*FPS);prefix_samples=prefix_frames*1600
    assert frames==11987 and samples==19179200
    assert round((m['duration_seconds']-m['brand_intervals']['endcard'][0])*FPS)==300
    files=[];preservation=[]
    for f in read(OLD/'records/qc_v01.json')['files']:
        assert sha(OLD/'deliverables'/f['name'])==f['sha256']
    for lang in ['en','ja']:
        oldpack=packets(oldvideo(lang),'a')
        for review in [False,True]:
            path=out(lang,review)
            ff(['-i',path,'-f','null','-'])
            p=probe(path);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
            assert [v['width'],v['height']]==[1920,1080] and v['avg_frame_rate']=='30/1'
            assert int(v['nb_frames'])==frames and int(v['duration_ts'])==frames*512
            assert a['time_base']=='1/48000' and int(a['duration_ts'])==samples
            pts=sorted(int(p['pts']) for p in packets(path,'v'))
            assert pts==list(range(0,frames*512,512))
            levels=measure(path)
            assert abs(float(levels['input_i'])+16)<.3 and float(levels['input_tp'])<=-1
            silence=subprocess.run(['ffmpeg','-hide_banner','-i',str(path),'-af','silencedetect=noise=-60dB:d=1',
                '-f','null','-'],capture_output=True,text=True,check=True).stderr
            silent=[float(x) for x in re.findall(r'silence_duration: ([\d.]+)',silence)]
            assert not silent
            files.append({'name':path.name,'bytes':path.stat().st_size,'sha256':sha(path),
                'video_stream_sha256':stream_hash(path,'v'),'audio_stream_sha256':stream_hash(path,'a'),
                'frames':frames,'duration_seconds':float(p['format']['duration']),'full_decode':True,
                'exact_30fps_pts':True,'audio_samples':samples,'loudness':levels,'silence_over_1s_at_minus60dB':silent})
            print('VERIFIED',path.name,levels['input_i'],levels['input_tp'],flush=True)
        a=[p for p in oldpack if int(p['pts'])<prefix_samples]
        b=[p for p in packets(out(lang),'a') if int(p['pts'])<prefix_samples]
        assert [(p['pts'],p['data_hash']) for p in a]==[(p['pts'],p['data_hash']) for p in b]
        av=[p for p in packets(oldvideo(lang),'v') if int(p['pts'])<prefix_frames*512]
        bv=[p for p in packets(out(lang),'v') if int(p['pts'])<prefix_frames*512]
        assert [(p['pts'],p['dts'],p['data_hash']) for p in av]==[(p['pts'],p['dts'],p['data_hash']) for p in bv]
        h1,h2=decoded_audio_hash(oldvideo(lang),prefix_samples),decoded_audio_hash(out(lang),prefix_samples)
        assert h1==h2
        info=sf.info(ROOT/f'deliverables/EP003_audio_{lang}.wav')
        assert info.samplerate==AR and info.frames==samples and info.subtype=='PCM_24'
        for key in ['A24','A04']:
            assert sha(ROOT/f'deliverables/EP003_thumbnail_{key}.jpg')==sha(OLD/f'deliverables/EP003_thumbnail_{key}.jpg')
        preservation.append({'language':lang,'range_seconds':[0,boundary],'frames':prefix_frames,'samples_48k':prefix_samples,
            'aac_packets':len(a),'video_packets':len(av),'encoded_audio_packets_identical':True,
            'encoded_video_packets_identical':True,'decoded_PCM_float32_SHA256':h1,'decoded_PCM_difference':0,
            'video_packet_SHA256':hashlib.sha256(''.join(p['data_hash'] for p in av).encode()).hexdigest(),
            'audio_packet_SHA256':hashlib.sha256(''.join(p['data_hash'] for p in a).encode()).hexdigest(),
            'WAV_samples':info.frames,'WAV_sha256':sha(ROOT/f'deliverables/EP003_audio_{lang}.wav')})
        newc=read(ROOT/f'records/narration_segments_{lang}.json')['segments'][-1]['cues']
        oldc=read(OLD/f'records/narration_segments_{lang}.json')['segments'][-1]['cues']
        assert [sha(ROOT/c['audio_file']) for c in newc[:3]+newc[-1:]]==[sha(OLD/c['audio_file']) for c in oldc]
        assert stream_hash(out(lang),'a')==stream_hash(out(lang,True),'a')
    assert stream_hash(out('en'),'v')==stream_hash(out('ja'),'v')
    # The opening is within the unchanged prefix. Match all 300 end-card frames
    # against the new common version, independently of the assembly manifest.
    start=m['brand_intervals']['endcard'][0]
    def framehash(path,start_frame,end_frame):
        raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-an','-vf',
            f'trim=start_frame={start_frame}:end_frame={end_frame},setpts=PTS-STARTPTS',
            '-f','framemd5','-'],text=True)
        return [line.split(',')[-1].strip() for line in raw.splitlines() if line and not line.startswith('#')]
    h1=framehash(out('en'),round(start*FPS),frames)
    h2=framehash(BRAND/'deliverables/Quiet_Origins_endcard_v02.mp4',0,300)
    assert h1==h2 and len(h1)==300
    check_layout()
    from wom03_motion import roi,motion_stats
    motion=read(OLD/'records/motion_v01.json')
    shot=read(ROOT/'records/render_shots.json')[-2]
    q=motion_stats(Path(shot['encoded_file']),roi(shot))
    assert q['frame_pairs']==shot['frames']-1 and q['p95_over_median']<=2.5
    motion['shots'][-1]={'segment_id':'M18','key':'credits','start':shot['start'],'end':shot['end'],
        'encoded_sha256':sha(Path(shot['encoded_file'])),'measurement':q,'passed':True}
    motion['unchanged_M01_M17']='Measurements inherited from identical encoded source files in v01'
    for oldshot,newshot in zip(motion['shots'][:-1],[s for s in read(ROOT/'records/render_shots.json') if s['segment_id'] not in ['M18','BRAND']]):
        assert oldshot['encoded_sha256']==sha(Path(newshot['encoded_file']))
    save(ROOT/'records/motion_v02.json',motion)
    save(ROOT/'records/qc_v02.json',{'passed':True,'duration_seconds':m['duration_seconds'],'frames':frames,
        'samples_48k':samples,'endcard_exact_last_10_seconds':True,'endcard_start':start,
        'endcard_300_decoded_frames_identical_to_common_v02':True,'M01_M17_preservation':preservation,
        'shared_regular_video_stream':True,'subtitle_review_audio_unchanged':True,'files':files,
        'M01_M17_SRT':'Exact cue records retained; SRT byte-prefix comparison in documentation stage',
        'M18_existing_four_sentences_reused':True,'v01_all_four_MP4_file_hashes_unchanged':True,
        'M18_motion_p95_over_median':q['p95_over_median'],
        'human_full_listening':False})
    print('QC PASSED',frames,samples,flush=True)


def mm(seconds):
    return f'{int(seconds)//60:02d}:{int(seconds)%60:02d}'


def docs():
    assert read(ROOT/'records/qc_v02.json')['passed']
    m=read(ROOT/'records/master_timeline.json');start=m['segments'][-1]['start'];duration=m['duration_seconds']
    srt_checks={}
    for lang in ['en','ja']:
        srt=out(lang).with_suffix('.srt');old=oldvideo(lang).with_suffix('.srt')
        oldc=read(OLD/f'records/subtitle_cues_{lang}.json')['cues']
        count=sum(not c['sentence_id'].startswith('M18-') for c in oldc)
        split=lambda p:p.read_text().strip().split('\n\n')
        before='\n\n'.join(split(old)[:count]);after='\n\n'.join(split(srt)[:count]);assert before==after
        srt_checks[lang]={'prefix_cues':count,'SRT_prefix_identical':True,'SHA256':hashlib.sha256(after.encode()).hexdigest()}
        p=ROOT/f'deliverables/EP003_upload_info_{lang}.md'
        text=(OLD/f'deliverables/EP003_upload_info_{lang}.md').read_text()
        text=text.replace('確認版v01。','確認版v02。').replace('台本v03。共通尺 403.666667秒。エンドカード開始 383.666667秒。',
            f'台本v04。共通尺 {duration:.6f}秒。エンドカード開始 {m["brand_intervals"]["endcard"][0]:.6f}秒（最後の10秒）。')
        text=text.replace('各19,376,000サンプル',f'各{round(duration*AR):,}サンプル')
        p.write_text(text)
        body=text.split('## Description\n\n',1)[1].split('\n## 制作・確認メモ',1)[0]
        assert len(body)<=5000
        # A short native-rate excerpt makes the two requested changes easy to hear.
        excerpt=ROOT/f'deliverables/EP003_M18_endcard_{lang}_v02.mp4'
        ff(['-ss',start,'-i',out(lang,True),'-map','0:v:0','-map','0:a:0','-c:v','libx264',
            '-preset','veryfast','-crf',18,'-threads',4,'-c:a','aac','-b:a','192k',
            '-ar',AR,'-video_track_timescale',15360,'-movie_timescale',AR,'-movflags','+faststart',excerpt])
    save(ROOT/'records/srt_prefix_preservation.json',srt_checks)
    for name in ['EP003_source_credits.md','EP003_pronunciation_en.m4a','EP003_pronunciation_en.txt',
                 'EP003_pronunciation_ja.m4a','EP003_pronunciation_ja.txt']:
        shutil.copy2(OLD/'deliverables'/name,ROOT/'deliverables'/name)
    # All new cue midpoints from actual subtitle-review videos, plus transition frames.
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
    for lang in ['en','ja']:
        cues=[c for c in read(ROOT/f'records/subtitle_cues_{lang}.json')['cues'] if c['sentence_id'].startswith('M18-')]
        sheet=Image.new('RGB',(1280,math.ceil(len(cues)/3)*260),'#0c1820');draw=ImageDraw.Draw(sheet)
        for i,c in enumerate(cues):
            t=(c['start']+c['end'])/2;p=ROOT/f'_work/cue_{lang}_{i:02d}.jpg'
            ff(['-ss',t,'-i',out(lang,True),'-frames:v',1,'-vf','scale=426:240','-q:v',3,p])
            sheet.paste(Image.open(p),(i%3*426,i//3*260))
            draw.text((i%3*426+5,i//3*260+242),f"{lang} {c['sentence_id']} {t:.2f}s",font=font,fill='#f4efdf')
        sheet.thumbnail((1280,1280));sheet.save(ROOT/f'review/M18_subtitles_{lang}_v02.jpg',quality=88,optimize=True)
    cards=''
    for lang,label in [('en','English'),('ja','日本語')]:
        cards+=f'<section><h2>{label}：変更箇所</h2><video controls preload="metadata" src="EP003_M18_endcard_{lang}_v02.mp4"></video><h3>全編</h3><video controls preload="metadata" src="{out(lang,True).name}"></video><p><a href="{out(lang).name}">通常版</a> / <a href="{out(lang).with_suffix(".srt").name}">SRT</a> / <a href="EP003_audio_{lang}.wav">投稿用WAV</a></p></section>'
    (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Medusa v02</title><style>body{max-width:1100px;margin:32px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}a,h1{color:#d8b575}video{width:100%;max-height:70vh}section{margin:40px 0}</style><h1>Quiet Origins / Medusa v02</h1><p>6分39.57秒。M18のお願いの読み方と、10秒エンドカードの終わり方をご確認ください。</p>'+cards+'<script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})))</script></html>')
    usage=copy.deepcopy(read(OLD/'records/asset_usage_v01.json'))
    usage[-1]['end']=m['segments'][-1]['end']
    with (ROOT/'deliverables/EP003_asset_usage_v02.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(usage[0]),lineterminator='\n');w.writeheader();w.writerows(usage)
    save(ROOT/'records/asset_usage_v02.json',usage)
    print('DOCS READY',flush=True)


def api(args,data=None):
    p=subprocess.run(['gh','api',*args],input=json.dumps(data) if data is not None else None,
        capture_output=True,text=True,check=True)
    return json.loads(p.stdout)


def share():
    qc=read(ROOT/'records/qc_v02.json');assert qc['passed']
    visual=read(ROOT/'records/visual_review_v02.json');assert visual['passed']
    assert all(sha(out(l,True))==visual['video_sha256'][l] for l in ['en','ja'])
    for f in qc['files']:assert sha(ROOT/'deliverables'/f['name'])==f['sha256']
    for p in (ROOT/'records').glob('*.json'):
        if p.name!='sharing.json':shutil.copy2(p,ROOT/'deliverables'/p.name)
    with zipfile.ZipFile(ROOT/'deliverables/EP003_review_frames_v02.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT/'review').glob('*.jpg')):z.write(p,p.name)
    files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.name!='SHA256SUMS_shared.txt')
    sums=ROOT/'deliverables/SHA256SUMS_shared.txt';sums.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(sums)
    state=ROOT/'records/sharing.json'
    r=api([f'repos/{GH}/releases/{read(state)["release_id"]}']) if state.exists() else next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
    if r is None:
        r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],{
            'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins：第3話 メドゥーサ v02（M18追加・10秒エンドカード）',
            'body':'Claude依頼0fbd21c・台本v04。399.566667秒・11987フレーム・19179200サンプル。M01〜M17の映像/AACパケット・デコード音声がv01と一致。M18に落ち着いたお願いを一文、エンドカードは10秒の共通版v02。英日通常版・字幕入り確認版・変更箇所抜粋・SRT・M4A・WAV・サムネ・技術検査記録。本人試聴待ち。非公開Draftを維持。原寸AI素材等はv01 Release 421292434を参照。',
            'draft':True})
    assert r['draft']
    save(state,{'release_id':r['id'],'draft':True,'status':'uploading','release_url':r['html_url']})
    for p in files:
        old=next((a for a in r['assets'] if a['name']==p.name),None)
        if old:assert old['state']=='uploaded' and old['digest']=='sha256:'+sha(p)
        else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
        print('UPLOADED',p.name,flush=True)
    r=api([f'repos/{GH}/releases/{r["id"]}']);assert r['draft'] and len(r['assets'])==len(files)
    checks=[]
    for p in files:
        a=next(a for a in r['assets'] if a['name']==p.name)
        proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE)
        h=hashlib.sha256();count=0
        for block in iter(lambda:proc.stdout.read(1048576),b''):h.update(block);count+=len(block)
        assert proc.wait()==0 and h.hexdigest()==sha(p) and count==p.stat().st_size
        assert a['digest']=='sha256:'+h.hexdigest()
        checks.append({'name':p.name,'asset_id':a['id'],'bytes':count,'sha256':h.hexdigest(),'REST_download_verified':True})
        print('REST VERIFIED',p.name,flush=True)
    save(state,{'release_id':r['id'],'draft':True,'status':'verified','release_url':r['html_url'],'assets':checks})
    print('SHARED',r['id'],len(checks),flush=True)


def export():
    shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified'
    for folder in ['records','frames','deliverables']:(GUIDE/folder).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,GUIDE/'records'/p.name)
    for p in (ROOT/'review').glob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        shutil.copy2(p,GUIDE/'frames'/p.name)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.srt','.md','.txt','.html','.csv']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
    # Delta production deliberately leaves unchanged high-resolution images and
    # sentence WAVs in v01. Document how inherited relative paths resolve.
    references=[]
    for lang in ['en','ja']:
        for name in [f'narration_segments_{lang}.json',f'narration_timeline_{lang}.json']:
            for segment in read(ROOT/'records'/name)['segments']:
                base=ROOT if segment['id']=='M18' else OLD
                for entry in [segment,*segment['cues']]:
                    path=base/entry['audio_file'];assert path.is_file()
                    references.append({'record':name,'id':entry['id'],'relative':entry['audio_file'],
                        'resolved_path':str(path),'sha256':sha(path)})
    for shot in read(ROOT/'records/visual_manifest.json')['shots']:
        base=ROOT if shot['segment_id']=='M18' else OLD
        path=base/shot['file'];assert path.is_file()
        references.append({'record':'visual_manifest.json','id':shot['key'],'relative':shot['file'],
            'resolved_path':str(path),'sha256':sha(path)})
    save(GUIDE/'records/source_path_resolution.json',{'passed':True,'v01_root':str(OLD),
        'v02_root':str(ROOT),'rule':'Inherited M01..M17 relative source paths use v01; M18 uses v02. Render-shot encoded_file values are absolute.',
        'references':references})
    for folder in ['records','frames']:(BGUIDE/folder).mkdir(parents=True,exist_ok=True)
    shutil.copy2(BRAND/'records/endcard_v02.json',BGUIDE/'records/endcard_v02.json')
    for p in (BRAND/'review').glob('*.jpg'):shutil.copy2(p,BGUIDE/'frames'/p.name)
    selected=[a for a in shared['assets'] if a['name'].startswith('Quiet_Origins_endcard_v02')]
    save(BGUIDE/'records/sharing.json',{'release_id':shared['release_id'],'draft':True,
        'release_url':shared['release_url'],'assets':selected})
    (BGUIDE/'README.md').write_text(f'''# Quiet Origins エンドカード共通版v02（第3話以降）

10秒・300フレーム・480,000サンプル。ロゴ・文字・色・模様・左側の終了画面用の余白はv01のまま。
背景の光だけを時間短縮し、旧版の最後30フレームを元の速さで再生。元の画面には映像フェードがないため追加していない。
音は冒頭5.3秒から元の15〜20秒へ0.3秒でクロスフェード。元の5秒間の音のフェードを保ち、最後4.7秒のWAVサンプルは同一。ピッチ・再生速度変更なし。

[映像・音声SHA-256と作り方](records/endcard_v02.json)／[最初](frames/endcard_v02_first.jpg)／[最後](frames/endcard_v02_last.jpg)。

Mac：`{BRAND}`。第1話・第2話は変更していない。
取得：非公開Draft Release ID **{shared['release_id']}**。[添付ID・照合済みハッシュ](records/sharing.json)。
''')
    table='\n'.join(f'| {a["name"]} | {a["asset_id"]} | {a["bytes"]:,} |' for a in shared['assets'])
    (GUIDE/'README.md').write_text(f'''# メドゥーサ確認版v02（台本v04）

399.566667秒・11,987フレーム・19,179,200サンプル。Mac：`{ROOT}`。`deliverables/preview.html`から全編と変更箇所を再生できます。

M01〜M17はv01と映像・AACパケット一致、デコード音声差分0、SRT一致。M18に一文を追加。共通版v02のエンドカードは389.566667秒から最後の10秒。サムネ2案はv01と同一。

[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付をRelease ID指定RESTで再取得してサイズ・SHA-256一致。

```sh
gh api repos/{GH}/releases/{shared['release_id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{GH}/releases/assets/ASSET_ID > FILE_NAME
```

別環境では全添付を同じフォルダへ保存しpreview.htmlを開いてください。Git内には動画・音声を置いていません。原寸AI素材・v01全検査はRelease **421292434**に保全。

制作記録のM01〜M17の素材・文別WAVの相対参照はv01フォルダ、M18はv02フォルダが基準です。[実在確認済みの参照先とSHA-256](records/source_path_resolution.json)。

[技術検査](records/qc_v02.json)／[M01〜M17のSRT照合](records/srt_prefix_preservation.json)／[共通エンドカードの作り方とSHA-256](records/endcard_v02.json)。

本人試聴：M18の英日のお願い、10秒エンドカードの終わり方。未確認の固有名詞・神統記・M12の調子も引き続き確認対象。
再現：既存環境で `wom03_revision_v02.py prepare → narrate → brand → timeline → audio → pictures → package → reviews → verify → docs`、目視確認記録後 `share → export`。v01を読取専用入力として使用。

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}
''')
    qc=read(ROOT/'records/qc_v02.json');audio=read(ROOT/'records/audio_revision_v02.json');sub=read(ROOT/'records/subtitle_validation.json')
    (REPO/'new-channel/wom03_制作結果_v02_20261023.md').write_text(f'''# 第3話「メドゥーサ」確認版v02 制作結果（2026-10-23）

**Claudeの修正依頼 `0fbd21c`・台本v04を反映。英日399.566667秒（6分39.57秒）、11,987フレーム、1080p30。** [再生・取得案内](wom03_確認版_v02_20261023/README.md)。

## 修正した2点

- M18に英日それぞれ、承認済みの高評価・チャンネル登録のお願いを一文追加。既存と同じHeart速度0.82／冥鳴ひまりC設定。新規合成は追加した各一文のみで、M18の既存4文も再利用。強調・効果音・画面文字追加なし。
- [エンドカード共通版v02](branding/20261023_エンドカード共通版_v02/README.md)を10秒で制作。元と同じ配置・文字・色・線の模様・左側の余白。背景の光の時間だけ短縮し、元の最後1秒を元の速さで再生。映像は元々フェードしないので、その終わり方を維持。音は元の最後5秒のフェードを保つ接続とし、最後4.7秒のWAVは元とサンプル一致。第1話・第2話は変更していない。

総尺は **403.666667 − 10 ＋ 5.9 ＝ 399.566667秒**。M18のクレジットを20.1秒→26秒へ延長。エンドカード開始は **389.566667秒**、終了まで正確に10秒。YouTube終了画面はこの区間に配置する（未投稿・未設定）。

![共通版v02の最初](wom03_確認版_v02_20261023/frames/endcard_v02_first.jpg)
![共通版v02の最後](wom03_確認版_v02_20261023/frames/endcard_v02_last.jpg)

## 実測検査

| 項目 | 結果 |
|---|---|
| 総尺 | 11,987フレーム×1,600＝**19,179,200サンプル**。MP4・M4A・48kHz/24bit WAVが同尺 |
| M01〜M17 | 0〜363.566667秒の英日通常版の圧縮映像・AACパケットがv01と一致。最初10,907映像フレーム、17,451,200音声サンプル。完成MP4のデコード音声差分0。WAV PCMも一致 |
| 字幕の保全 | M01〜M17のSRT本文・時刻・連番が一致。M18のみ更新。英{sub['en']['count']}件・日{sub['ja']['count']}件、全台本と空白以外一致、最短1.4秒以上、英42字／日23字以内、2行以内 |
| 字幕配置 | M18全字幕をFontSize14／26で描画し、文字y≤700との重なりなし。既存区間はv01の検査を引き継ぐ |
| 音量・ピーク | 英語 {audio['languages']['en']['loudness']['input_i']} LUFS / {audio['languages']['en']['loudness']['input_tp']} dBTP、日本語 {audio['languages']['ja']['loudness']['input_i']} LUFS / {audio['languages']['ja']['loudness']['input_tp']} dBTP |
| BGM | v01の音量補正値・間の+4dB設定を維持。既存区間の全サンプルを保全し、M18だけ同じ設定で延長。全編の再正規化なし |
| 動画4本 | 全編デコード・正確な1/30秒PTS。英日通常版は同一映像ストリーム。字幕入り版の音声は通常版と同一 |
| エンドカード | 完成MP4最後300フレームが共通版v02と全画素一致 |
| 無音 | −60dB基準で1秒以上0件 |
| サムネ | A24・A04の両案をv01から保全。Claude推奨はA24、本人最終判断待ち |

[映像・音声・保全ハッシュ](wom03_確認版_v02_20261023/records/qc_v02.json)／[音声接続記録](wom03_確認版_v02_20261023/records/audio_revision_v02.json)／[共通版の映像・音声SHA-256と変更内容](wom03_確認版_v02_20261023/records/endcard_v02.json)。字幕焼き込み版は確認用の再エンコードで、既存区間の圧縮映像一致検査は通常版に対して実施。

## 保存・共有と本人確認

Mac：`{ROOT}`。v01の制作物・Releaseは保全。

新規[非公開Draft Release]({shared['release_url']})、Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付、{sum(a['bytes'] for a in shared['assets']):,}bytesをRelease ID指定RESTで再取得し、サイズ・SHA-256を照合。[添付一覧](wom03_確認版_v02_20261023/README.md)。資料・スクリプトは `bgm/production` に本報告と同じコミットで共有。

M18の全字幕中点・共通版の最初と最後の画像は目視確認済み。本人による試聴は未実施：**M18のお願いの読み方（英日）、10秒エンドカードの終わり方**。v01から未確認の英語固有名詞・日本語の神統記・M12の調子も確認対象。音を聴いた／全編視聴済みとはしていない。

YouTubeへの投稿・予約・公開、Release公開、追加契約・購入は未実施。
''')
    canonical=REPO/'new-channel/episodes/EP003_Medusa/records'
    for name in ['qc_v02.json','sharing.json','master_timeline.json','chapters.json']:
        shutil.copy2(ROOT/'records'/name,canonical/name)
    handoff=REPO/'new-channel/Claude引き継ぎ_次のセッション.md'
    text=handoff.read_text()
    lines=text.splitlines()
    for i,line in enumerate(lines):
        if line.startswith('| 第3話 メドゥーサ（wom03） |'):
            lines[i]=f'| 第3話 メドゥーサ（wom03） | **確認版v02完成**（Release `{shared["release_id"]}`、399.567秒、台本v04）。M18にお願いを一文、エンドカードは10秒の共通版v02。M01〜M17は圧縮映像・AACパケット一致、デコード音声差分0。Claude確認→本人のM18・終わり方の試聴待ち。v01は本人「概ねいい」。サムネA24案をClaude推奨 | `wom03_制作結果_v02_20261023.md`、`wom03_修正依頼_v02_20261023.md`、`branding/20261023_エンドカード共通版_v02/README.md` |'
    if lines[0].startswith('# 次のClaudeセッションへの引き継ぎ'):
        lines[0]='# 次のClaudeセッションへの引き継ぎ（2026-10-23 第3話v02完成 更新）'
    handoff.write_text('\n'.join(lines)+'\n')
    print('EXPORTED',GUIDE,flush=True)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['prepare','narrate','brand','timeline','audio','pictures','package','reviews','verify','docs','share','export'])
    args=parser.parse_args()
    globals()[args.stage]()
