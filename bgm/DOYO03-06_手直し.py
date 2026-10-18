#!/usr/bin/env python3
"""DOYO03–06の承認済み文字修正とDOYO05のAACピーク再書き出し。

python3 bgm/DOYO03-06_手直し.py thumbnails
python3 bgm/DOYO03-06_手直し.py audio
出力はMac BGM内の_work。原本への反映は目視確認後に別途コピーする。
"""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

import cv2
import numpy as np
import yaml
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bgmkit import single_songs as ss

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = Path('/Users/ryo/Desktop/BGM/1_Whispers of Japan/童謡単曲')
WORK = MATERIALS / '_work' / '修正_20261018'
GOLD = (247, 216, 143)
BRAND = 'WHISPERS OF JAPAN'
COCHIN = '/System/Library/Fonts/Supplemental/Cochin.ttc'
MINCHO = '/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
SPECS = [
    (3, '01_夕焼け小焼け', 'yuuyake', (62, 746, 440, 831)),
    (4, '02_赤とんぼ', 'akatombo', (62, 642, 440, 720)),
    (5, '03_紅葉', 'momiji', (62, 672, 440, 747)),
    (6, '04_七つの子', 'nanatsunoko', (62, 659, 440, 733)),
]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def thumbnails():
    out = WORK / 'thumbnails'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for no, folder, key, box in SPECS:
        source = MATERIALS / folder / (key + '_thumbnail.png')
        backup_source = source.parent / '_修正前_20261018_英字ブランド' / source.name
        if backup_source.exists():
            source = backup_source
        image = Image.open(source).convert('RGB')
        if image.size != (1672, 941):
            raise ValueError(f'座標の再確認が必要: {source}, {image.size}')
        before = np.asarray(image).copy()
        mask = np.zeros(before.shape[:2], np.uint8)
        x0, y0, x1, y1 = box
        roi = before[y0:y1, x0:x1].astype(np.int16)
        white = (roi.min(axis=2) > 165) & ((roi.max(axis=2) - roi.min(axis=2)) < 45)
        mask[y0:y1, x0:x1] = white.astype(np.uint8) * 255
        mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
        image = Image.fromarray(cv2.inpaint(before, mask, 5, cv2.INPAINT_TELEA))
        # 4枚共通の座標。Cochin Bold、1920幅換算38px／字間8px。
        factor = image.width / 1920
        font = ImageFont.truetype(COCHIN, round(38 * factor), index=1)
        spacing = 8 * factor
        layer = Image.new('RGBA', image.size)
        draw = ImageDraw.Draw(layer)
        x, y = 72.0, 758.0
        for char in BRAND:
            draw.text((x, y), char, font=font, fill=GOLD + (255,), anchor='lt')
            x += draw.textlength(char, font=font) + spacing
        if no == 5:
            ruby = ImageFont.truetype(MINCHO, 68, index=2)
            # 題字の右側、字面下端590pxにそろえる。約1/4の大きさ。
            draw.text((652, 590), 'もみじ', font=ruby, fill=GOLD + (255,), anchor='lb')
        # 影を2回重ね、明るい岩の上でも「じ」の濁点を読みやすくする。
        shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
        shadow.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(2)))
        image = Image.alpha_composite(image.convert('RGBA'), shadow)
        image = Image.alpha_composite(image, shadow)
        image = Image.alpha_composite(image, layer).convert('RGB')
        png = out / (key + '_thumbnail.png')
        jpg = out / (key + '_short_thumbnail.jpg')
        small = out / f'doyo{no:02d}_168.jpg'
        image.save(png)
        image.resize((1280, 720), Image.Resampling.LANCZOS).save(jpg, quality=90)
        image.resize((168, 95), Image.Resampling.LANCZOS).save(small, quality=95)
        # 画面の変更は指定した旧ブランド領域、新ブランド領域、ふりがなに限定。
        allowed = mask > 0
        allowed[748:830, 62:900] = True
        if no == 5:
            allowed[500:605, 640:875] = True
        delta = np.any(np.asarray(image) != before, axis=2)
        outside = int(np.count_nonzero(delta & ~allowed))
        if outside:
            raise ValueError(f'指定箇所以外が変化: {key}: {outside}px')
        assert jpg.stat().st_size < 1_000_000
        rows.append(dict(id=f'doyo{no:02d}', source=str(source), source_sha256=sha(source),
                         png=str(png), jpeg=str(jpg), preview_168=str(small),
                         jpeg_bytes=jpg.stat().st_size, dimensions=[1280, 720],
                         brand_xy=[72, 758], brand_font_px=font.size,
                         tracking=spacing, removed_mask_pixels=int(np.count_nonzero(mask)),
                         pixels_changed_outside_allowed=outside))
        print(f'doyo{no:02d}: JPG {jpg.stat().st_size} bytes、指定箇所以外の変化 {outside}px', flush=True)
    (WORK / 'thumbnails.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))


def audio():
    work = WORK / 'audio'
    work.mkdir(parents=True, exist_ok=True)
    cfg = yaml.safe_load((ROOT / 'bgm/volumes/doyo05.yaml').read_text())
    song = cfg['songs'][0]
    take = ss.take_info(ROOT / 'bgm/volumes', song['short']['audio'])
    duration = take['duration']
    settings = dict(cfg['settings'], true_peak=-1.5)
    raw, normalized, mixed, master = [work / n for n in ('extract.wav', 'take.wav', 'mix.wav', 'master.wav')]
    ss.ff('-ss', str(take['start']), '-i', take['path'], '-t', str(duration),
          '-vn', '-ar', '48000', '-ac', '2', '-c:a', 'pcm_f32le', raw)
    print('原音源から2パスloudnorm TP=-1.5で整音', flush=True)
    ss.normalize(raw, normalized, settings)
    ss.mix_audio([normalized], [0], duration, settings['crossfade'], settings['fade'], mixed)
    ss.normalize(mixed, master, settings)
    # 最終AACを実測しながら余裕を調整。毎回、非圧縮マスターから再エンコード。
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
    original = Path(cfg['artifacts']['video'])
    result = work / original.name
    # 映像は承認済みH.264をビットストリームコピー。音声のみ差し替える。
    ss.ff('-i', original, '-i', encoded, '-map', '0:v:0', '-map', '1:a:0',
          '-c', 'copy', '-t', str(duration), '-movflags', '+faststart', result)
    report = ss.verify(result, duration, settings)
    assert report['true_peak'] <= -1.5
    video_hashes = [ss.ff('-v', 'error', '-i', path, '-map', '0:v:0', '-c:v', 'copy',
                         '-bsf:v', 'h264_mp4toannexb', '-f', 'hash', '-hash', 'sha256', '-').stdout.strip()
                    for path in (original, result)]
    assert video_hashes[0] == video_hashes[1], '映像ビットストリームが変化しました'
    report.update(source_audio=str(take['path']), source_video=str(original),
                  original_video_sha256=sha(original), output=str(result),
                  output_sha256=sha(result), loudnorm_target_tp=-1.5,
                  limiter_attempts=attempts, video_stream_copy=True, video_hashes=video_hashes,
                  target_duration=duration, fade_seconds=settings['fade'])
    (WORK / 'audio.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


def install():
    """目視検品後だけ実行。移動せず修正前を複製保存し、同じパスへ差し替える。"""
    ssd = Path('/Volumes/ESD-02/BGM/1_Whispers of Japan/童謡単曲')
    if not Path('/Volumes/ESD-02').is_mount() or not ssd.is_dir():
        raise ValueError('指定SSD ESD-02が未接続。別ボリュームには書き込みません')
    thumbs = json.loads((WORK / 'thumbnails.json').read_text())
    audio_report = json.loads((WORK / 'audio.json').read_text())
    assert audio_report['true_peak'] <= -1.5 and audio_report['full_decode'] == 'passed'
    copies = []
    for row, (_, folder, key, _) in zip(thumbs, SPECS):
        assert sha(row['source']) == row['source_sha256'], '検品後に原本が更新されています'
        for source in (Path(row['png']), Path(row['jpeg'])):
            for root in (MATERIALS, ssd):
                copies.append((source, root / folder / source.name))
    original = Path(audio_report['source_video'])
    assert sha(original) == audio_report['original_video_sha256']
    for root in (MATERIALS, ssd):
        copies.append((Path(audio_report['output']), root / '03_紅葉' / original.name))
    # 全対象の実在とバックアップ衝突を先に確認。
    for source, dest in copies:
        assert source.is_file() and dest.is_file(), f'ファイル未確認: {source} / {dest}'
        backup = dest.parent / '_修正前_20261018_英字ブランド' / dest.name
        if backup.exists() and sha(backup) != sha(dest) and sha(dest) != sha(source):
            raise ValueError(f'既存バックアップと現行ファイルが異なります: {backup}')
    records = []
    for source, dest in copies:
        backup = dest.parent / '_修正前_20261018_英字ブランド' / dest.name
        backup.parent.mkdir(exist_ok=True)
        if backup.exists() and sha(dest) == sha(source):
            records.append(dict(path=str(dest), backup=str(backup), old_sha256=sha(backup),
                                sha256=sha(dest), exists=True))
            continue
        old_hash = sha(dest)
        if not backup.exists():
            shutil.copy2(dest, backup)
        assert sha(backup) == old_hash
        temp = dest.with_name(dest.name + '.replacing')
        shutil.copy2(source, temp)
        assert sha(temp) == sha(source)
        temp.replace(dest)
        records.append(dict(path=str(dest), backup=str(backup), old_sha256=old_hash,
                            sha256=sha(dest), exists=dest.is_file()))
    for row in thumbs:
        dest = ROOT / 'サムネ確認用/童謡単曲' / (row['id'] + '_サムネ.jpg')
        shutil.copy2(row['jpeg'], dest)
        assert sha(dest) == sha(row['jpeg'])
        row['review_path'] = str(dest.relative_to(ROOT))
    result = dict(date='2026-10-18', tool='Pillow + OpenCV; image generation not used',
                  thumbnails=thumbs, audio=audio_report, copies=records,
                  copy_count=len(records), all_current_paths_exist=all(r['exists'] for r in records),
                  backups_verified=True, ssd='ESD-02', playback='pending')
    report_path = ROOT / 'bgm/DOYO03-06_手直し結果_20261018.json'
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f'Mac/SSD {len(records)}件、確認用JPG 4件を反映。全コピーSHA-256一致。', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['thumbnails', 'audio', 'install'])
    args = parser.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    {'thumbnails': thumbnails, 'audio': audio, 'install': install}[args.stage]()
