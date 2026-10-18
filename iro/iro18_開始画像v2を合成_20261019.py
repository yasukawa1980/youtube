"""画像生成済みの手元を既存マスクで合成し、保存PNGのマスク外を検証する。"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SOURCE = Path('/Volumes/ESD-02/BGM/IRO/Chill/18_毛糸の季節がやってきた/手直し_20261018')
REVIEW = Path(__file__).resolve().parent / 'iro18_手直し_20261018'
SIZE = (1920, 1080)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measure(actual, baseline, outside):
    delta = np.abs(np.asarray(actual).astype(np.int16) - np.asarray(baseline).astype(np.int16))
    return {
        'outside_pixels': int(outside.sum()),
        'outside_changed_pixels': int(np.count_nonzero(np.any(delta != 0, axis=2) & outside)),
        'outside_max_channel_difference': int(delta[outside].max()),
        'outside_absolute_difference_sum': int(delta[outside].sum()),
        'total_changed_pixels': int(np.any(delta != 0, axis=2).sum()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--generated', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    original_path = SOURCE / '18_start_旧_1920.png'
    mask_path = SOURCE / '手元変更マスク_1672.png'
    original = Image.open(original_path).convert('RGB')
    assert original.size == SIZE
    generated = Image.open(args.generated).convert('RGB').resize(SIZE, Image.Resampling.LANCZOS)
    old_mask = Image.open(mask_path).convert('L')
    support = np.asarray(old_mask.resize(SIZE, Image.Resampling.NEAREST)) > 0
    alpha = np.array(old_mask.resize(SIZE, Image.Resampling.BILINEAR))
    alpha[~support] = 0
    mask = Image.fromarray(alpha)
    merged = Image.composite(generated, original, mask)
    # 合成後はリサイズしない。保存する1920x1080の画素で外側を完全固定。
    main_path = args.out / '18_start_編む手元v2_Kling用.png'
    dog_path = args.out / '18_start_編む手元v2_犬1.4倍.png'
    for path in (main_path, dog_path):
        if path.exists():
            raise FileExistsError(path)
    merged.save(main_path)
    dog_mask = Image.open(SOURCE / '犬1.4倍_合成マスク.png').convert('L')
    assert dog_mask.size == SIZE
    zoom = original.resize((2688, 1512), Image.Resampling.LANCZOS).crop((164, 400, 2084, 1480))
    dog_baseline = Image.composite(zoom, original, dog_mask)
    # 犬の1.4倍拡大は前回と同じマスク・補間・位置。手元とは重ならない。
    assert not np.any((np.asarray(dog_mask) > 0) & support)
    dog_final = Image.fromarray(np.where(support[..., None], np.asarray(merged), np.asarray(dog_baseline)).astype(np.uint8))
    dog_final.save(dog_path)
    saved = Image.open(main_path).convert('RGB')
    dog_saved = Image.open(dog_path).convert('RGB')
    metrics = measure(saved, original, ~support)
    dog_metrics = measure(dog_saved, dog_baseline, ~support)
    union_metrics = measure(dog_saved, original, ~(support | (np.asarray(dog_mask) > 0)))
    for result in (metrics, dog_metrics, union_metrics):
        assert result['outside_changed_pixels'] == 0
        assert result['outside_max_channel_difference'] == 0
    mask.save(args.out / '開始画像v2_手元変更マスク_1920.png')

    previous = Image.open(SOURCE / '18_start_編む手元_Kling用.png').convert('RGB')
    sheet = Image.new('RGB', (1280, 910), '#f7f1e8')
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', 22)
    small = ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc', 18)
    for x, im, title in [(16, previous, '旧：前回の編む手元'), (648, saved, '新：編む手元 v2')]:
        draw.text((x, 14), title, font=font, fill='#392a28')
        sheet.paste(im.resize((616, 347), Image.Resampling.LANCZOS), (x, 52))
        draw.text((x, 416), '手元拡大', font=font, fill='#392a28')
        crop = im.crop((955, 450, 1510, 820))
        sheet.paste(crop.resize((616, 411), Image.Resampling.LANCZOS), (x, 452))
    draw.text((16, 878), '元画像：18_start_旧_1920.png ／ 手元マスク外の変更 0画素・RGB最大差 0', font=small, fill='#392a28')
    REVIEW.mkdir(parents=True, exist_ok=True)
    compare_path = REVIEW / '開始画像v2_比較.jpg'
    sheet.save(compare_path, quality=91, subsampling=0)
    report = {
        'source': str(original_path), 'source_sha256': sha(original_path),
        'source_mask': str(mask_path), 'source_mask_sha256': sha(mask_path),
        'generated': str(args.generated), 'generated_sha256': sha(args.generated),
        'method': 'built-in image_gen / 2 edits; final-size mask composite; no post-composite resizing',
        'mask_scaling': 'support=NEAREST>0; alpha=BILINEAR clipped to support; original mask unchanged',
        'size': list(SIZE), 'main_vs_original': metrics,
        'dog_vs_original_with_same_1_4x_dog': dog_metrics,
        'dog_vs_original_outside_hand_and_dog_masks': union_metrics,
        'dog_scale': 1.4, 'dog_crop_offset': [164, 400],
        'dog_note': '犬拡大版は犬も変わるため、手元マスク外0は同じ犬拡大を施した旧画像との比較。元画像に対しては手元＋犬マスクの外側が0。',
        'outputs': [{'path': str(SOURCE / p.name), 'sha256': sha(p), 'bytes': p.stat().st_size} for p in (main_path, dog_path)],
        'comparison': {'path': str(compare_path), 'size': list(sheet.size), 'bytes': compare_path.stat().st_size},
        'kling_invoked': False, 'posted': False, 'scheduled': False,
    }
    (REVIEW / '開始画像v2_検証.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
