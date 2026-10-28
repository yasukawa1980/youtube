"""Music band analysis and equal-loudness narration auditions; no perceptual pass claim."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from scipy.signal import welch

SR = 48000

def decode(path, duration=None, filters=None):
    cmd = ['ffmpeg', '-v', 'error', '-i', str(path)]
    if duration is not None:
        cmd += ['-t', str(duration)]
    if filters:
        cmd += ['-af', filters]
    cmd += ['-ar', str(SR), '-ac', '2', '-f', 'f32le', '-']
    return np.frombuffer(subprocess.check_output(cmd), '<f4').reshape(-1, 2).copy()

def write_wav(path, audio):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR),
                    '-ac', '2', '-i', '-', '-c:a', 'pcm_s24le', str(path)],
                   input=audio.astype('<f4').tobytes(), check=True)

def loudness(path):
    cmd = ['ffmpeg', '-hide_banner', '-nostats', '-i', str(path),
           '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-']
    s = subprocess.run(cmd, capture_output=True, text=True, check=True).stderr
    return json.loads(re.findall(r'\{[^{}]*"input_i"[^{}]*\}', s)[-1])

def normalize(src, dst):
    m = loudness(src)
    f = (f'loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={m["input_i"]}:'
         f'measured_TP={m["input_tp"]}:measured_LRA={m["input_lra"]}:'
         f'measured_thresh={m["input_thresh"]}:offset={m["target_offset"]}:linear=true')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-af', f,
                    '-ar', str(SR), '-c:a', 'pcm_s24le', str(dst)], check=True)
    return loudness(dst)

def db(x):
    return float(20 * np.log10(np.sqrt(np.mean(np.asarray(x, dtype=np.float64)**2)) + 1e-15))

def bands(y):
    f, p = welch(y, SR, nperseg=4096, axis=0)
    p = p.sum(axis=1)
    total = p.sum()
    spans = {'below_200': (0, 200), '200_to_2000': (200, 2000),
             'above_2000': (2000, 24001), '500_to_4000': (500, 4000),
             '2000_to_4000': (2000, 4000)}
    return {k: round(float(p[(f >= lo) & (f < hi)].sum()/total), 6)
            for k, (lo, hi) in spans.items()}, f, p

def analyze(path, out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    y = decode(path)
    duration = len(y)/SR
    fractions, f, p = bands(y)
    step = SR//4
    power = np.mean(y[:len(y)//step*step].reshape(-1, step, 2)**2, axis=(1,2))
    rms = 10*np.log10(power+1e-15)
    # Stable 30-second interior window; avoid fades and large crescendos.
    choices = [(float(power[i:i+120].mean()), i) for i in range(40, len(power)-160)
               if np.min(rms[i:i+120]) > -45
               and np.percentile(rms[i:i+120],90)-np.percentile(rms[i:i+120],10) <= 6]
    if not choices:
        raise ValueError(f'No continuous non-silent 30-second interior window: {path}')
    _, q = min(choices)
    start, end = q/4, q/4+30
    m = loudness(path)
    fig, ax = plt.subplots(3, 1, figsize=(12, 8), constrained_layout=True)
    ax[0].plot(np.arange(len(y[::240]))/200, y[::240,0], linewidth=.35)
    ax[0].axvspan(start, end, alpha=.2, color='green')
    ax[0].set(title=path.stem+' — waveform / candidate quiet window', xlabel='Seconds', ylabel='Amplitude')
    ax[1].plot(np.arange(len(rms))*.25, rms, linewidth=.8)
    ax[1].set(xlabel='Seconds', ylabel='250 ms RMS dBFS', ylim=(-65, 0))
    ax[2].semilogx(f[1:], 10*np.log10(p[1:]+1e-20))
    ax[2].axvspan(500, 4000, alpha=.15, color='orange')
    ax[2].set(xlim=(30, 16000), xlabel='Hz', ylabel='PSD dB/Hz')
    fig.savefig(out/(path.stem+'_analysis.jpg'), dpi=100)
    plt.close(fig)
    return {'file': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'duration_seconds': duration, 'lufs': float(m['input_i']),
            'true_peak_dbtp': float(m['input_tp']), 'energy_fractions': fractions,
            'quiet_window_candidate': {'start': start, 'end': end, 'rms_dbfs': db(y[int(start*SR):int(end*SR)]),
                                       'p90_minus_p10_db': float(np.percentile(rms[q:q+120],90)-np.percentile(rms[q:q+120],10))},
            'loop_candidate': {'start': start, 'end': end, 'crossfade_seconds': 3,
                               'status': 'numerical candidate; listening approval pending'},
            'direct_listening': 'not_performed'}

def audition(path, narration, old_bgm, timeline, duration, out):
    n = decode(narration, duration)
    length = len(n)
    # 10 ms voice energy, hold 150 ms on both sides; ramp gain over 200 ms.
    hop = SR//100
    p = np.mean(n[:length//hop*hop].reshape(-1, hop, 2)**2, axis=(1,2))
    gate = maximum_filter1d(p > 10**(-45/10), size=31).astype(float)
    mask = np.repeat(gate, hop)
    mask = np.pad(mask, (0, length-len(mask)), mode='edge') > .5
    env = np.repeat(uniform_filter1d(gate, size=21), hop)
    env = np.pad(env, (0, length-len(env)), mode='edge')
    vdb = db(n[mask])
    y = decode(path, duration, 'highpass=f=100,equalizer=f=2828:t=o:w=1:g=-3.5')
    if len(y) < length:
        raise ValueError('Source music shorter than demo')
    y = y[:length]
    gain = 10**((vdb-18-db(y[mask]))/20)
    music = y*gain*(10**((6*(1-env))/20))[:,None]
    music[:SR//2] *= np.linspace(0,1,SR//2)[:,None]
    music[-SR//2:] *= np.linspace(1,0,SR//2)[:,None]
    # Retain the common four-second logo sound from the existing master.
    original = decode(old_bgm, duration)
    brand = np.zeros_like(n)
    a,b = timeline['brand_intervals']['opening']
    a,b = int(a*SR), min(length,int(b*SR))
    brand[a:b] = original[a:b]
    raw = out/'_work'/(path.stem+'_raw.wav')
    write_wav(raw, n+music+brand)
    dest = out/(path.stem+'_EP006_demo.wav')
    measured = normalize(raw, dest)
    mp3 = dest.with_suffix('.mp3')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(dest), '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)], check=True)
    encoded = loudness(mp3)
    if float(encoded['input_tp']) > -1:
        # Leave extra headroom for lossy encoding; remeasure the deliverable.
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(dest), '-af', 'volume=-0.5dB',
                        '-c:a', 'libmp3lame', '-b:a', '192k', str(mp3)], check=True)
        encoded = loudness(mp3)
    return {'wav':str(dest), 'mp3':str(mp3), 'duration_seconds':length/SR,
            'voice_active_dbfs':vdb, 'music_during_voice_dbfs':db(music[mask]),
            'music_between_voice_dbfs':db(music[~mask]), 'relative_voice_db':db(music[mask])-vdb,
            'gap_boost_db':6, 'opening_original_preserved':[a/SR,b/SR],
            'music_eq':'highpass100Hz + octave-wide -3.5dB EQ centered2828Hz',
            'wav_loudness':measured,'mp3_loudness':encoded,
            'wav_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
            'mp3_sha256':hashlib.sha256(mp3.read_bytes()).hexdigest()}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--narration', type=Path, required=True)
    ap.add_argument('--old-bgm', type=Path, required=True)
    ap.add_argument('--old-mix', type=Path, required=True)
    ap.add_argument('--timeline', type=Path, required=True)
    ap.add_argument('--duration', type=float, default=64.533333333)
    ap.add_argument('files', type=Path, nargs='+')
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True); (args.out/'_work').mkdir(exist_ok=True)
    timeline=json.loads(args.timeline.read_text())
    report={'method':'Welch PSD summed over stereo channels; energy ratios on original WAV; 30s interior candidate with RMS p90-p10 <=6dB and every 250ms bin above -45dBFS.',
            'limitation':'Automatic screening; direct listening and final user selection pending.', 'files':{},'demos':{}}
    report_path=args.out/'audio_analysis.json'
    if report_path.exists():
        report=json.loads(report_path.read_text())
    for path in args.files:
        report['files'][path.stem]=analyze(path,args.out)
        report['demos'][path.stem]=audition(path,args.narration,args.old_bgm,timeline,args.duration,args.out)
        (args.out/'audio_analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(path.stem,report['files'][path.stem]['energy_fractions'],flush=True)
    raw=args.out/'_work'/'baseline.wav'
    write_wav(raw,decode(args.old_mix,args.duration))
    dest=args.out/'QO_BASELINE_OLD_EP006_demo.wav'
    m=normalize(raw,dest)
    mp3=dest.with_suffix('.mp3')
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(dest),'-c:a','libmp3lame','-b:a','192k',str(mp3)],check=True)
    report['baseline']={'wav':str(dest),'mp3':str(mp3),'wav_loudness':m,'mp3_loudness':loudness(mp3),
                        'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
    report['baseline_music_energy']=bands(decode(args.old_bgm,args.duration))[0]
    (args.out/'audio_analysis.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':
    main()
