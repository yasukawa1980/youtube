"""全編の自動検査と重複確認に基づく31曲選定・4秒の連結。聴感合格は宣言しない。"""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bgm'))
from bgmkit import audio, config
from bgmkit.ffutil import audio_md5, duration

YAML = ROOT / 'iro/volumes/iro20.yaml'
NAMES = {'A': 'ハープ', 'B': 'ファゴット', 'C': 'チェレスタ',
         'D': 'マンドリン', 'E': 'トロンボーン', 'F': 'ハーモニウム'}
COUNTS = {'A': 6, 'B': 5, 'C': 6, 'D': 5, 'E': 6, 'F': 3}


def ordered_tags():
    family = {'A': 'plucked', 'B': 'wind', 'C': 'keyboard',
              'D': 'plucked', 'E': 'wind', 'F': 'keyboard'}
    used = dict.fromkeys(COUNTS, 0)
    rare_slots = {5, 16, 27}
    def visit(sequence):
        i = len(sequence)
        if i == 31:
            return sequence
        options = ['F'] if i in rare_slots else list('ABCDE')
        options = [t for t in options if used[t] < COUNTS[t] and t not in sequence[-2:]]
        def priority(t):
            value = (i + 1) * COUNTS[t] / 31 - used[t]
            for back, penalty in [(1, .4), (2, .15)]:
                if len(sequence) >= back and family[t] == family[sequence[-back]]:
                    value -= penalty
            return (-value, t)
        for tag in sorted(options, key=priority):
            used[tag] += 1
            result = visit(sequence + [tag])
            if result is not None:
                return result
            used[tag] -= 1
        return None
    result = visit([])
    if result is None:
        raise RuntimeError('種類分散の曲順を作れません')
    return result


def select():
    cfg = yaml.safe_load(YAML.read_text()); base = Path(cfg['dir'])
    report = json.loads((ROOT / 'iro/iro20_音源検品.json').read_text())['files']
    pool = {tag: [] for tag in NAMES}; excluded = {}
    for path in sorted((base / '楽曲').glob('*.wav')):
        tag = path.stem.split('_')[1][0]
        if path.stem not in report:
            raise RuntimeError(f'全編検査未完了: {path.name}')
        row = report[path.stem]
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['file_sha256']:
            raise RuntimeError(f'検査後に音源が変化: {path.name}')
        if tag == 'F' and int(path.stem.split('-')[1][:2]) < 4:
            excluded[path.name] = '音色の同定を保留（弦系分類が続いたため再試作を優先）'
        elif tag == 'F' and 'Organ' not in row['class_mean_top']:
            excluded[path.name] = '目的の鍵盤・オルガン系を自動分類で確認しにくいため採用保留'
        elif row['flags']:
            excluded[path.name] = '自動検査の要確認: ' + ', '.join(row['flags'])
        else:
            pool[tag].append(path.name)
    chosen = {}
    for tag, songs in pool.items():
        need = COUNTS[tag]
        if len(songs) < need:
            raise RuntimeError(f'{tag} の検査済み候補が不足: {len(songs)} / {need}')
        ranked = sorted(songs, key=lambda name: (report[Path(name).stem]['voice_max'],
                        abs(report[Path(name).stem]['lufs'] + 16.5), name))
        chosen[tag] = ranked[:need]
        for name in ranked[need:]:
            excluded[name] = '必要尺を満たす31曲へ自動検査値に基づき絞り込み（不採用判定ではない）'
    tags = ordered_tags(); used = dict.fromkeys(COUNTS, 0); order = []
    for tag in tags:
        order.append(chosen[tag][used[tag]]); used[tag] += 1
    if len(order) != 31 or len(set(order)) != 31:
        raise RuntimeError('31曲の固有性が成立しません')
    kinds = [name.split('_')[1][0] for name in order]
    for i, tag in enumerate(kinds):
        if (i > 0 and tag == kinds[i - 1]) or (i > 1 and tag == kinds[i - 2]):
            raise RuntimeError('同系統が隣接または1曲おきです')
    hashes = {}
    for name in order:
        digest = audio_md5(str(base / '楽曲' / name))
        if not digest:
            raise RuntimeError(f'PCMハッシュ測定失敗: {name}')
        if digest in hashes.values():
            raise RuntimeError(f'PCM重複: {name}')
        hashes[name] = digest
    estimated = sum(report[Path(name).stem]['usable_seconds'] for name in order) - 4 * (len(order) - 1)
    if estimated < 7200:
        raise RuntimeError(f'2時間に足りません: {estimated}')
    cfg['kinds'] = {Path(name).stem: name.split('_')[1][0] + NAMES[name.split('_')[1][0]] for name in order}
    cfg['picked'] = order; cfg['order_tracks'] = order; cfg['exclude'] = [Path(n).stem for n in excluded]
    cfg['status'] = 'editing_audio'
    cfg['instrument_verification'] = '生成指示と自動分類。直接聴取・厳密な楽器同定は未実施。'
    YAML.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    result = {'selected_count': len(order), 'kind_counts': {t: len(chosen[t]) for t in NAMES},
              'order': order, 'pcm_md5': hashes, 'unique_decoded_pcm': True,
              'estimated_seconds_after_crossfades': estimated, 'crossfade_seconds': 4,
              'same_kind_adjacent': False, 'same_kind_skip1': False,
              'unused_candidates': excluded, 'direct_listening': 'not_performed',
              'selection_basis': '自動検査の衛生指標・必要尺・種類分散。聴感評価ではない。',
              'last_track': '本編2時間到達時に10秒のフェードで閉じる'}
    (ROOT / 'iro/iro20_選曲結果.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('selected', len(order), 'unique PCM', len(hashes), 'estimate', estimated, flush=True)


def build():
    cfg = config.load(str(YAML))
    if len(cfg.get('order_tracks', [])) != 31:
        raise RuntimeError('31曲の選曲が確定していません')
    if Path(cfg.wpath('music_bed.wav')).exists():
        raise FileExistsError('既存の音楽床を保全。別版として書き出してください')
    bed = audio.build(cfg, cfg['order_tracks'])
    seconds = duration(bed)
    if seconds < 7200:
        raise RuntimeError(f'組み上げた音楽床が2時間未満: {seconds}')
    manifest = json.loads(Path(cfg.wpath('manifest.json')).read_text())
    manifest.update(music_bed=str(bed), measured_seconds=seconds, direct_listening='not_performed')
    (ROOT / 'iro/iro20_音楽構成.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print('music bed', bed, seconds, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['select', 'build'])
    args = parser.parse_args()
    {'select': select, 'build': build}[args.step]()
