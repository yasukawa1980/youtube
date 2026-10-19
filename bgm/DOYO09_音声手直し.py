#!/usr/bin/env python3
"""DOYO09 月の沙漠：AACのTrue Peak（−0.66 dBTP）を −1.5 dBTP 以下へ。DOYO05紅葉と同じ手順。

python3 bgm/DOYO09_音声手直し.py
原音源から2パスloudnorm（TP −1.5）で整音し、リミッター付きでAACを焼いて実測。
映像は書き出し済みH.264をビットストリームコピーし、音声だけ差し替える。
差し替え前の動画と測定JSONは同じ曲フォルダの `_修正前_20261019_TP/` へ移す（この巻で作ったばかりの未公開ファイル）。
"""
import hashlib
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bgmkit import single_songs as ss

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    cfg = yaml.safe_load((ROOT / 'bgm/volumes/doyo09.yaml').read_text())
    song = cfg['songs'][0]
    original = Path(cfg['artifacts']['video'])
    folder = original.parent
    work = folder.parent / '_work' / '修正_20261019_doyo09'
    work.mkdir(parents=True, exist_ok=True)
    take = ss.take_info(ROOT / 'bgm/volumes', song['short']['audio'])
    duration = take['duration']
    settings = dict(cfg['settings'], true_peak=-1.5)
    raw, normalized, mixed, master = [work / n for n in ('extract.wav', 'take.wav', 'mix.wav', 'master.wav')]
    ss.ff('-ss', str(take['start']), '-i', take['path'], '-t', str(duration),
          '-vn', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_f32le', raw)
    ss.normalize(raw, normalized, settings)
    ss.mix_audio([normalized], [0], duration, settings['crossfade'], settings['fade'], mixed)
    ss.normalize(mixed, master, settings)
    ceiling, attempts = -2.5, []
    encoded = work / 'master.m4a'
    for attempt in range(4):
        limit = 10 ** (ceiling / 20)
        guard = f'aresample=192000,alimiter=limit={limit}:level=false:attack=5:release=50:latency=true,aresample=48000'
        ss.ff('-i', master, '-af', guard, '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', encoded)
        stats = ss.norm_stats(encoded, -14, -1.5, settings['lra'])
        peak, lufs = float(stats['input_tp']), float(stats['input_i'])
        attempts.append(dict(limiter_ceiling_db=ceiling, lufs=lufs, true_peak=peak))
        print(f'AAC {attempt+1}: {lufs} LUFS / {peak} dBTP', flush=True)
        if peak <= -1.5 and abs(lufs + 14) <= 1:
            break
        if peak <= -1.5:
            raise ValueError('目標LUFSとの差が1 LUを超えます。自動適用せず要確認')
        ceiling -= peak + 1.5 + 0.2
    else:
        raise ValueError('4回のAAC検証でピーク基準に到達しませんでした')
    result = work / original.name
    ss.ff('-i', original, '-i', encoded, '-map', '0:v:0', '-map', '1:a:0',
          '-c', 'copy', '-t', str(duration), '-movflags', '+faststart', result)
    report = ss.verify(result, duration, settings)
    assert report['true_peak'] <= -1.5 and report['full_decode'] == 'passed'
    video_hashes = [ss.ff('-v', 'error', '-i', p, '-map', '0:v:0', '-c:v', 'copy',
                         '-bsf:v', 'h264_mp4toannexb', '-f', 'hash', '-hash', 'sha256', '-').stdout.strip()
                    for p in (original, result)]
    assert video_hashes[0] == video_hashes[1], '映像ビットストリームが変化しました'
    old_report = folder / (original.stem + '.json')
    backup = folder / '_修正前_20261019_TP'
    backup.mkdir(exist_ok=True)
    report.update(song=song['name'], source_audio=str(take['path']), original_video_sha256=sha(original),
                  loudnorm_target_tp=-1.5, limiter_attempts=attempts, video_stream_copy=True,
                  video_hashes=video_hashes, target_duration=duration, fade_seconds=settings['fade'],
                  previous=json.loads(old_report.read_text()) if old_report.exists() else None)
    original.replace(backup / original.name)
    if old_report.exists():
        old_report.replace(backup / old_report.name)
    result.replace(original)
    report.update(output=str(original), output_sha256=sha(original), backup=str(backup))
    old_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('duration', 'lufs', 'true_peak', 'full_decode', 'warnings')},
                     ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
