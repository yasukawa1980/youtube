#!/usr/bin/env python3
"""馬の鼻息のように聞こえた衣擦れ音だけを本編・ショートから除去する。

実行: bgm/.venv-audio-qc/bin/python iro/irostory01_音修正_20261031.py
対象は本人が指定したショート9〜10秒＝本編34.3秒の合成衣擦れ。
映像ストリームはコピー。音声は該当区間をゼロ化してAACへ再符号化。
元動画・元音源は保持し、新しい版名で保存する。
"""
from pathlib import Path
import hashlib
import json
import subprocess

import numpy as np
from scipy.io import wavfile

REPO = Path(__file__).resolve().parents[1]
BASE = Path('/Volumes/ESD-EPB/BGM/IRO/Stories/01_あと一ページのはずだった')
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Stories/01_あと一ページのはずだった')
OUT = BASE/'投稿用'
WORK = BASE/'_work/audio_fix_20261031'
JOBS = [
    dict(kind='本編', old='irostory01_あと一ページのはずだった_完成v2.mp4',
         new='irostory01_あと一ページのはずだった_完成v3.mp4',
         wav_old='irostory01_生活音_仕上げv2.wav', wav_new='irostory01_生活音_仕上げv3.wav',
         start=34.2, end=34.85, event=34.3, duration=90, width=1920, height=1080),
    dict(kind='ショート', old='irostory01_ショート_あと一ページのはずだった_v1.mp4',
         new='irostory01_ショート_あと一ページのはずだった_v2.mp4',
         wav_old='irostory01_ショート_生活音_v1.wav', wav_new='irostory01_ショート_生活音_v2.wav',
         start=9.2, end=9.85, event=9.3, duration=36, width=1080, height=1920),
]


def run(args):
    return subprocess.run(list(map(str,args)),check=True,capture_output=True,text=True)


def video_hash(path):
    return run(['ffmpeg','-v','error','-i',path,'-map','0:v:0','-c','copy',
                '-f','hash','-hash','sha256','-']).stdout.strip()


def process(job):
    old,new = OUT/job['old'],OUT/job['new']
    old_wav,new_wav = BASE/'音源'/job['wav_old'],BASE/'音源'/job['wav_new']
    assert old.is_file() and old_wav.is_file()
    if new.exists() or new_wav.exists():
        raise FileExistsError('修正版が既に存在するため上書きしません')
    sr,original = wavfile.read(old_wav)
    assert sr==48000 and original.shape==(job['duration']*sr,2)
    a,b = round(job['start']*sr),round(job['end']*sr)
    fixed = original.copy()
    fixed[a:b]=0
    # Both bounds sit in silence, outside the 0.45-second synthetic rustle.
    assert not np.any(original[a:a+int(.05*sr)])
    assert not np.any(original[b-int(.05*sr):b])
    assert np.array_equal(original[:a],fixed[:a]) and np.array_equal(original[b:],fixed[b:])
    assert np.any(original[a:b]) and not np.any(fixed[a:b])
    wavfile.write(new_wav,sr,fixed)
    af=f"volume=0:enable='between(t,{job['start']},{job['end']})'"
    run(['ffmpeg','-n','-v','error','-i',old,'-map','0:v:0','-map','0:a:0',
         '-c:v','copy','-af',af,'-c:a','aac','-b:a','256k','-ar',48000,
         '-t',job['duration'],'-movflags','+faststart',new])
    data=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',new]).stdout)
    dec=run(['ffmpeg','-v','error','-i',new,'-f','null','-'])
    loud=run(['ffmpeg','-hide_banner','-i',new,'-vn','-af',
              'loudnorm=I=-24:TP=-3:LRA=20:print_format=json','-f','null','-']).stderr
    ld=json.loads(loud[loud.rfind('{'):loud.rfind('}')+1])
    vs=next(s for s in data['streams'] if s['codec_type']=='video')
    old_vhash,new_vhash=video_hash(old),video_hash(new)
    assert old_vhash==new_vhash
    assert float(data['format']['duration'])==job['duration']
    assert (vs['width'],vs['height'])==(job['width'],job['height']) and vs['avg_frame_rate']=='24/1'
    assert not dec.stderr.strip() and float(ld['input_tp'])<-2.5
    # Inspect the actual final AAC after decoding, not only the source WAV.
    pcm=WORK/(job['kind']+'_検品.wav')
    run(['ffmpeg','-n','-v','error','-i',new,'-vn','-c:a','pcm_s16le',pcm])
    rate,decoded=wavfile.read(pcm)
    silence=decoded[round((job['start']+.05)*rate):round((job['end']-.05)*rate)]
    peak=int(np.max(np.abs(silence.astype(np.int32))))
    assert peak<=1, f'削除区間に音が残っています: {peak}'
    record={**job,'sample_rate':sr,'size_bytes':new.stat().st_size,
            'sha256':hashlib.sha256(new.read_bytes()).hexdigest(),
            'video_stream_unchanged':True,'video_stream_hash':new_vhash,
            'raw_audio_unchanged_outside_interval':True,
            'removed_source_nonzero_samples':int(np.count_nonzero(original[a:b])),
            'decoded_removed_interval_peak_pcm16':peak,
            'integrated_lufs':float(ld['input_i']),'true_peak_dbtp':float(ld['input_tp']),
            'full_decode_errors':dec.stderr.strip()}
    print(json.dumps(record,ensure_ascii=False),flush=True)
    return record


if __name__=='__main__':
    WORK.mkdir(parents=True,exist_ok=True)
    records=[process(job) for job in JOBS]
    report={'date':'2026-10-31','request':'馬の鼻息のようなブルルン音を本編・ショートとも除去',
            'user_identified_short_seconds':'9〜10秒・女性が犬を見る場面',
            'identified_source':'本編34.3秒の紙／衣擦れ（合成）、長さ0.45秒',
            'method':'既存AACの対象区間をゼロ化して再符号化。映像ストリームはコピー。元WAVも同じ区間だけゼロ化。',
            'subjective_audio_review':'直接聴取は未実施。本人指定時刻と制作記録を照合し、音の除去をPCMで確認。',
            'new_generation_credits':0,'files':records}
    (REPO/'iro/irostory01_音修正_検品_20261031.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
