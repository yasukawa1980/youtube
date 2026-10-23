#!/usr/bin/env python3
"""Mac内蔵・SSD(ESD-02)の容量整理（2026-10-23 本人方針B）。

python3 bgm/容量整理_20261023.py plan      消す候補を数えて一覧にする（何も消さない）
python3 bgm/容量整理_20261023.py execute   plan の一覧どおりに消す（本人確認後だけ）

一覧は ~/Desktop/容量整理_一覧_20261023.tsv、要約は ~/Desktop/容量整理_要約_20261023.txt。
execute は一覧を読み直し、大きさが一覧と同じ時だけ消す。G1は直前にSSD側も照合する。

G1 Mac BGM：SSDの同じ場所に同じファイル（大きさと先頭・末尾1MBが一致）があるものをMacから消す。_共通は対象外。
G2 新チャンネル：投稿済みの回の古い確認版。完成版・ショートの材料・v02が参照するv01は残す。
G3 Downloads：iroの素材zip。
G4 SSD：10/8以前に更新が止まった回の _work・動画・zip。音源・画像・資料は残す（方針B）。
"""
import argparse
import hashlib
import os
import shutil
import sys
import time
from pathlib import Path

HOME = Path.home()
MAC_BGM = HOME / 'Desktop/BGM'
NEW = HOME / 'Desktop/新チャンネル'
SSD_BGM = Path('/Volumes/ESD-02/BGM')
LIST = HOME / 'Desktop/容量整理_一覧_20261023.tsv'
SUMMARY = HOME / 'Desktop/容量整理_要約_20261023.txt'
CUTOFF = time.mktime((2026, 10, 9, 0, 0, 0, 0, 0, -1))  # 10/8までに更新が止まった回だけ
VIDEO = {'.mp4', '.mov', '.m4v', '.mkv', '.webm', '.avi', '.zip'}
G1_SKIP = {'_共通'}
G2_DIRS = [
    'EP001_Anubis/英語メイン版_v02_20261020',
    'EP001_Anubis/映像音声調整_v03_20261021',
    'EP001_Anubis/C採用_はかり修正_v04_20261021',
    'EP001_Anubis/Quiet_Origins_v05_20261021',
    'EP001_Anubis/Quiet_Origins_v06_20261021',
    'EP001_Anubis/Quiet_Origins_v07_20261021',
    'EP001_Anubis/確認用_v01_20261020',
    'EP001_Anubis/英語声試聴_20261020',
    'EP001_Anubis/日本語自然さ試聴_20261021',
    'EP001_Anubis/字幕入り確認用_v05_20261021',
    'EP002_Halloween/確認版_v02_20261022',
    'EP002_Halloween/確認版_v03_20261022',
]
G4_SKIP = {'_共通', 'コンピ', '20260908_修正版案内', '_整理待ち'}


def files(root):
    for d, dirs, names in os.walk(root):
        for n in names:
            p = Path(d) / n
            if not p.is_symlink() and p.is_file():
                yield p


def edges(path):
    """先頭と末尾1MBのハッシュ。大きな動画を全部読まずに同一性を確かめる。"""
    h = hashlib.sha256()
    size = path.stat().st_size
    with path.open('rb') as f:
        h.update(f.read(1 << 20))
        if size > 2 << 20:
            f.seek(-(1 << 20), 2)
            h.update(f.read())
    return h.hexdigest()


def same_on_ssd(mac_file):
    twin = SSD_BGM / mac_file.relative_to(MAC_BGM)
    return twin.is_file() and twin.stat().st_size == mac_file.stat().st_size and edges(twin) == edges(mac_file)


def g4_units():
    for top in sorted(SSD_BGM.iterdir()):
        if not top.is_dir() or top.name in G4_SKIP:
            continue
        if top.name == 'IRO':
            yield from (u for g in sorted(top.iterdir()) if g.is_dir() for u in sorted(g.iterdir()) if u.is_dir())
        elif top.name[0].isdigit():
            yield from (u for u in sorted(top.iterdir()) if u.is_dir())
        else:
            yield top


def plan():
    if not SSD_BGM.is_dir():
        sys.exit(f'SSDが見つかりません: {SSD_BGM}（ESD-02を接続してから実行）')
    rows, held = [], []
    for p in files(MAC_BGM):
        rel = p.relative_to(MAC_BGM)
        if rel.parts[0] not in G1_SKIP and same_on_ssd(p):
            rows.append(('G1', '/'.join(rel.parts[:2]), p))
    for d in G2_DIRS:
        if (NEW / d).is_dir():
            rows += [('G2', d, p) for p in files(NEW / d)]
    rows += [('G3', 'Downloads', p) for p in sorted((HOME / 'Downloads').glob('iro*.zip'))]
    for unit in g4_units():
        all_files = [p for p in files(unit) if p.name != '.DS_Store']
        if not all_files:
            continue
        unit_rel = str(unit.relative_to(SSD_BGM))
        newest = max(p.stat().st_mtime for p in all_files)
        if newest >= CUTOFF:
            held.append(f'{unit_rel}（最終更新 {time.strftime("%Y-%m-%d", time.localtime(newest))}）')
            continue
        rows += [('G4', unit_rel, p) for p in all_files
                 if '_work' in p.relative_to(unit).parts or p.suffix.lower() in VIDEO]

    with LIST.open('w', encoding='utf-8') as f:
        for g, unit, p in rows:
            f.write(f'{g}\t{p.stat().st_size}\t{unit}\t{p}\n')
    totals = {}
    for g, unit, p in rows:
        totals.setdefault((g, unit), [0, 0])
        totals[(g, unit)][0] += p.stat().st_size
        totals[(g, unit)][1] += 1
    gb = lambda n: f'{n / 1024 ** 3:.2f}G'
    lines = [f'容量整理の候補（{time.strftime("%Y-%m-%d %H:%M")}、まだ何も消していません）', '']
    for g, title in [('G1', 'Mac BGM：SSDに同じものがある'), ('G2', '新チャンネル：古い確認版'),
                     ('G3', 'Downloads：iro素材zip'), ('G4', 'SSD：10/8以前の回の_work・動画・zip')]:
        part = {u: v for (gg, u), v in totals.items() if gg == g}
        lines.append(f'== {g} {title}　計 {gb(sum(v[0] for v in part.values()))}')
        lines += [f'  {gb(v[0]):>7}  {v[1]:>5}件  {u}' for u, v in sorted(part.items(), key=lambda x: -x[1][0])]
        lines.append('')
    lines.append('== G4で保留（10/9以降に更新があるため対象外）')
    lines += [f'  {h}' for h in held]
    lines += ['', f'合計 Mac {gb(sum(v[0] for (g, _), v in totals.items() if g != "G4"))}'
                  f' / SSD {gb(sum(v[0] for (g, _), v in totals.items() if g == "G4"))}']
    SUMMARY.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(SUMMARY.read_text(encoding='utf-8'))
    print(f'一覧: {LIST}')


def execute():
    if not LIST.is_file():
        sys.exit('先に plan を実行してください')
    freed, skipped, roots = 0, [], set()
    for line in LIST.read_text(encoding='utf-8').splitlines():
        g, size, unit, path = line.split('\t')
        p = Path(path)
        if not p.is_file() or p.stat().st_size != int(size) or (g == 'G1' and not same_on_ssd(p)):
            skipped.append(path)
            continue
        p.unlink()
        freed += int(size)
        roots.add(p.parent)
    # 中身が空になったフォルダだけ片付ける。シリーズ直下（1_Whispers of Japan 等）は構成として残す
    keep = {MAC_BGM, NEW, SSD_BGM, HOME / 'Downloads'}
    keep |= {p for r in (MAC_BGM, SSD_BGM) if r.is_dir() for p in r.iterdir()}
    keep |= {p for r in (MAC_BGM, SSD_BGM) if (r / 'IRO').is_dir() for p in (r / 'IRO').iterdir()}
    for d in sorted(roots, key=lambda x: -len(x.parts)):
        while d not in keep and d.is_dir():
            leftovers = [x for x in d.iterdir() if x.name != '.DS_Store']
            if leftovers:
                break
            shutil.rmtree(d)
            d = d.parent
    print(f'削除 {freed / 1024 ** 3:.2f}G、照合が合わず残したもの {len(skipped)}件')
    for s in skipped[:50]:
        print('  残した:', s)
    os.system('df -h /System/Volumes/Data /Volumes/ESD-02')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('command', choices=['plan', 'execute'])
    {'plan': plan, 'execute': execute}[ap.parse_args().command]()
