"""短い動画の実測と目視用コマ一覧。合否や実視聴は自動で宣言しない。

python -m bgmkit.clip_qc clip.mp4 --out /path/to/_work/qc --seconds 8 
    --face 950,260,230,240 --camera 300,100,240,180

box は元映像の x,y,width,height。既存出力は上書きせず別フォルダを使う。
"""
from __future__ import annotations

import argparse
import json
import subprocess
from fractions import Fraction
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def box_arg(text):
    values = tuple(map(int, text.split(',')))
    if len(values) != 4 or min(values[:2]) < 0 or min(values[2:]) <= 0:
        raise argparse.ArgumentTypeError('x,y,width,height を指定してください')
    return values


def phase_shift(a, b):
    """固定背景の位相相関。3点放物線補間、単位は元画像px。

    絵の変形・照明変化も相関へ影響するので、カメラ動作の断定には使わない。
    """
    window = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    fa = np.fft.fft2((a - a.mean()) * window)
    fb = np.fft.fft2((b - b.mean()) * window)
    cross = fa * np.conj(fb)
    corr = np.fft.ifft2(cross / np.maximum(np.abs(cross), 1e-12)).real
    py, px = np.unravel_index(np.argmax(corr), corr.shape)
    values = []
    for p, n, line in ((px, a.shape[1], corr[py, :]), (py, a.shape[0], corr[:, px])):
        left, center, right = line[(p - 1) % n], line[p], line[(p + 1) % n]
        den = left - 2 * center + right
        sub = .5 * (left - right) / den if abs(den) > 1e-12 else 0.
        values.append(float((p if p <= n / 2 else p - n) + sub))
    return values


def sheet(frames, out, columns, cell_size):
    cw, ch = cell_size
    canvas = Image.new('RGB', (cw * columns, (ch + 24) * ((len(frames) + columns - 1) // columns)), '#202020')
    draw = ImageDraw.Draw(canvas)
    for i, (t, im) in enumerate(frames):
        im = im.copy(); im.thumbnail((cw, ch), Image.Resampling.LANCZOS)
        x, y = (i % columns) * cw, (i // columns) * (ch + 24)
        canvas.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
        draw.text((x + 6, y + ch + 4), f'{t:.3f}s', fill='white')
    canvas.save(out, quality=90)


def inspect(path, out, seconds, face=None, camera=None):
    metadata = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)]))
    stream = next(s for s in metadata['streams'] if s['codec_type'] == 'video')
    w, h = stream['width'], stream['height']
    fps = float(Fraction(stream['avg_frame_rate']))
    for box in (face, camera):
        if box and (box[0] + box[2] > w or box[1] + box[3] > h):
            raise ValueError('crop box が映像の外に出ています')
    if out.exists() and any(out.iterdir()):
        raise FileExistsError(f'検品結果を保全するため空の保存先を指定してください: {out}')
    out.mkdir(parents=True, exist_ok=True)
    args = ['ffmpeg', '-v', 'error', '-i', str(path)]
    if seconds:
        args += ['-t', str(seconds)]
    args += ['-map', '0:v:0', '-pix_fmt', 'rgb24', '-f', 'rawvideo', '-']
    steps, motion, drift, exposures, shots, faces = [], [], [], [], [], []
    previous = first = camera_first = None
    index, next_sample = 0, 0.
    with (out / 'decode.log').open('w') as log:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=log)
        try:
            while True:
                raw = p.stdout.read(w * h * 3)
                if not raw:
                    break
                if len(raw) != w * h * 3:
                    raise RuntimeError('不完全な映像フレーム')
                rgb = np.frombuffer(raw, np.uint8).reshape(h, w, 3)
                im = Image.fromarray(rgb)
                small = np.asarray(im.resize((480, round(h * 480 / w))).convert('L'), dtype=np.float32)
                if first is None:
                    first = small.copy()
                if previous is not None:
                    diff = np.abs(small - previous)
                    steps.append(float(diff.mean()))
                    motion.append(float((diff > 12).mean() * 100))
                previous = small
                if camera:
                    x, y, bw, bh = camera
                    gray = np.asarray(im.crop((x, y, x + bw, y + bh)).convert('L'), dtype=np.float32)
                    if camera_first is None:
                        camera_first = gray.copy()
                    drift.append(phase_shift(camera_first, gray))
                t = index / fps
                if t + .5 / fps >= next_sample:
                    shots.append((t, im.copy()))
                    if face:
                        x, y, bw, bh = face
                        faces.append((t, im.crop((x, y, x + bw, y + bh))))
                    gray = np.asarray(im.convert('L'))
                    exposures.append({'seconds': t, 'dark_lt16_pct': float((gray < 16).mean() * 100),
                                      'bright_ge250_pct': float((gray >= 250).mean() * 100)})
                    next_sample += 1 / 3
                index += 1
        finally:
            p.stdout.close()
            code = p.wait()
    if code or not index:
        raise RuntimeError(f'映像デコード失敗 code={code}: {out / "decode.log"}')
    seam = float(np.abs(previous - first).mean())
    median = float(np.median(steps)) if steps else 0
    report = {'source': str(path.resolve()), 'width': w, 'height': h, 'fps': fps,
              'container_seconds': float(metadata['format']['duration']), 'decoded_frames': index,
              'analyzed_seconds': index / fps, 'requested_limit_seconds': seconds,
              'decode_exit': code, 'audio_streams': sum(s['codec_type'] == 'audio' for s in metadata['streams']),
              'luma_analysis_width': 480, 'adjacent_mae_median': median,
              'adjacent_mae_max': max(steps, default=0), 'end_to_start_mae': seam,
              'seam_over_median': seam / median if median else None,
              'adjacent_changed_gt12_pct_max': max(motion, default=0), 'exposure_3fps': exposures,
              'camera_box': camera, 'phase_shift_method': 'Hann window, phase correlation, parabolic subpixel; distortion also affects result',
              'camera_abs_shift_max_px': np.max(np.abs(drift), axis=0).tolist() if drift else None,
              'face_box': face, 'sample_fps': 3, 'visual_review': 'pending', 'audio_listening': 'not_performed',
              'all_frame_adjacent_mae': steps, 'camera_phase_shift_by_frame': drift}
    sheet(shots, out / '全景_3fps.jpg', 6, (320, 180))
    if faces:
        sheet(faces, out / '顔_3fps.jpg', 6, (200, 200))
    (out / 'metrics.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return {k: report[k] for k in ('decoded_frames', 'analyzed_seconds', 'adjacent_mae_median', 'end_to_start_mae', 'seam_over_median', 'camera_abs_shift_max_px')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=8)
    parser.add_argument('--face', type=box_arg)
    parser.add_argument('--camera', type=box_arg)
    args = parser.parse_args()
    if not 0 < args.seconds <= 60:
        parser.error('--seconds は0超〜60秒（長尺の検品は連続デコードを別途実行）')
    print(json.dumps(inspect(args.video, args.out, args.seconds, args.face, args.camera), ensure_ascii=False))


if __name__ == '__main__':
    main()
