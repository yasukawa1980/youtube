"""短い動画の目元だけを追跡修正し、頭・呼吸・手の時間を保つ。設定はJSON。"""
import argparse
import json
import subprocess
from pathlib import Path

import cv2
import numpy as np


def correct(source, output, config):
    if output.exists():
        raise FileExistsError(f'修正版を上書きしません: {output}')
    x, y, w, h = config['face_box']
    cap = cv2.VideoCapture(str(source))
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    faces = []
    for i in range(config.get('frames', 192)):
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f'素材が短い: {i}')
        faces.append(frame[y:y+h, x:x+w].copy())
    cap.release()
    gray = [cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in faces]
    mask = np.zeros((h, w), np.float32)
    for ex, ey, ew, eh, angle in config['eyes']:
        cv2.ellipse(mask, (ex, ey), (ew, eh), angle, 0, 360, 1, -1)
    core = mask.copy()
    mask = cv2.GaussianBlur(mask, (9, 9), 1.5) * core
    anchors = np.zeros((h, w), np.uint8)
    ax, ay, aw, ah = config['anchors']
    cv2.ellipse(anchors, (ax, ay), (aw, ah), 0, 0, 360, 255, -1)
    anchors[cv2.dilate(core, np.ones((7, 7), np.uint8)) > 0] = 0
    points = cv2.goodFeaturesToTrack(gray[0], 180, .01, 3, mask=anchors)
    if points is None or len(points) < 12:
        raise RuntimeError('追跡点が足りません')
    matrices, errors = [], []
    for i, g in enumerate(gray):
        target, status, err = cv2.calcOpticalFlowPyrLK(gray[0], g, points, None,
            winSize=(21, 21), maxLevel=3,
            criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, .001))
        good = (status[:, 0] == 1) & (err[:, 0] < 30)
        if good.sum() < 12:
            raise RuntimeError(f'追跡失敗: {i}')
        matrix, inliers = cv2.estimateAffinePartial2D(points[good], target[good],
            method=cv2.RANSAC, ransacReprojThreshold=1.5)
        if matrix is None or np.count_nonzero(inliers) < 8:
            raise RuntimeError(f'追跡行列失敗: {i}')
        matrices.append(matrix)
        errors.append(float(np.median(np.linalg.norm(cv2.transform(points[good], matrix) - target[good], axis=2))))
    output.parent.mkdir(parents=True, exist_ok=True)
    process = subprocess.Popen(['ffmpeg', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
        '-s', f'{width}x{height}', '-r', str(fps), '-i', '-', '-an', '-c:v', 'libx264',
        '-crf', '12', '-preset', 'fast', '-pix_fmt', 'yuv420p', str(output)], stdin=subprocess.PIPE)
    cap = cv2.VideoCapture(str(source))
    changed, max_outside = [], 0
    start, end = config['interval']
    donor = faces[0]
    try:
        for i, matrix in enumerate(matrices):
            ok, frame = cap.read()
            if not ok:
                raise RuntimeError('再読失敗')
            original = frame[y:y+h, x:x+w].copy()
            weight = min(float(np.clip((i - start + 3) / 3, 0, 1)),
                         1 - float(np.clip((i - end) / 3, 0, 1)))
            for center in config['blink_centers']:
                weight *= float(np.clip((abs(i - center) - 2) / 2, 0, 1))
            mapped = cv2.warpAffine(donor, matrix, (w, h), flags=cv2.INTER_CUBIC)
            alpha = cv2.warpAffine(mask, matrix, (w, h), flags=cv2.INTER_LINEAR) * weight
            patch = np.rint(original * (1 - alpha[..., None]) + mapped * alpha[..., None]).clip(0, 255).astype(np.uint8)
            difference = np.abs(patch.astype(int) - original.astype(int))
            max_outside = max(max_outside, int(difference[alpha == 0].max(initial=0)))
            changed.append(int(np.any(patch != original, axis=2).sum()))
            frame[y:y+h, x:x+w] = patch
            process.stdin.write(frame.tobytes())
    finally:
        cap.release(); process.stdin.close()
    if process.wait():
        raise RuntimeError('目元修正版のエンコード失敗')
    report = {'source': str(source), 'output': str(output), 'config': config, 'frames': len(faces),
              'head_retiming': False, 'outside_eye_mask_difference_before_encoding': max_outside,
              'tracking_median_error_px': float(np.median(errors)), 'tracking_max_error_px': max(errors),
              'changed_pixels_by_frame': changed, 'visual_review': 'pending'}
    output.with_suffix('.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: report[k] for k in ('frames', 'outside_eye_mask_difference_before_encoding', 'tracking_max_error_px')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    correct(args.source, args.output, json.loads(args.config.read_text()))
