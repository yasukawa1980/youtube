"""Measure all adjacent frames in seven painting shots of the final delivery."""
import os
import subprocess
import numpy as np
from pnt02_produce import ROOT, read, save, sha


def main():
    lang = os.environ['PNT02_LANG']
    scale = int(os.environ.get('PNT02_SCALE', '1'))
    suffix = '_4k' if scale == 2 else ''
    shots = read(ROOT / f'records/render_shots{suffix}.json')
    geometry = read(ROOT / f'records/art_scales{suffix}.json')
    src = ROOT / f'deliverables/PNT02_WashingtonCrossing_{lang}_v01_{1080*scale}p30.mp4'
    checks = []
    for shot in shots:
        if not shot.get('moving'):
            continue
        key = shot['key']
        left, top, right, bottom = geometry[key]['pasted_box']
        # Keep the ROI inside artwork and outside the fixed header and rail.
        left, right = left + (right-left)*.15, right - (right-left)*.15
        top, bottom = max(top, 120), min(bottom, 900)
        top, bottom = top+(bottom-top)*.15, bottom-(bottom-top)*.15
        x, y = round(left*scale), round(top*scale)
        w, h = round((right-left)*scale), round((bottom-top)*scale)
        cmd = ['ffmpeg', '-nostdin', '-v', 'error', '-threads', '1',
               '-ss', str(shot['start']), '-i', str(src), '-an',
               '-frames:v', str(shot['frames']), '-filter_threads', '1',
               '-vf', f'format=gray,crop={w}:{h}:{x}:{y}:exact=1',
               '-threads', '1', '-pix_fmt', 'gray', '-fps_mode', 'passthrough',
               '-f', 'rawvideo', '-']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        previous = None
        differences = []
        for _ in range(shot['frames']):
            data = process.stdout.read(w*h)
            assert len(data) == w*h, (key, len(data))
            current = np.frombuffer(data, np.uint8).astype(np.int16)
            if previous is not None:
                differences.append(float(np.abs(current-previous).mean()))
            previous = current
        assert process.wait() == 0
        median, p95 = float(np.median(differences)), float(np.percentile(differences, 95))
        ratio = p95/median if median else None
        checks.append(dict(shot=key, roi=[x,y,w,h], adjacent_pairs=len(differences),
                           median=median, p95=p95, ratio=ratio,
                           passed=ratio is not None and ratio <= 2.5))
        print('MOTION', lang, scale, key, ratio, flush=True)
    assert len(checks) == 7
    save(ROOT / f'records/final_video_motion{suffix}.json', dict(
        passed=all(row['passed'] for row in checks), video_sha256=sha(src),
        method='Every adjacent decoded frame in each moving artwork shot; inner artwork ROI excludes fixed labels and chronology. Static cards and common brand clips excluded.',
        checks=checks))


if __name__ == '__main__':
    main()
