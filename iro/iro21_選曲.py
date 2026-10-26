"""IRO21 の選曲：自動検品の結果から各種5曲（Aだけ6曲）を選び、A→B→C→D→E→F の順に並べて iro/volumes/iro21.yaml に書く。

除外：人声の最大>0.03／途中の無音2秒以上／最後1秒が−25dBより大きい（尾の切れ）。
順位：尾の弱い減衰（最後1秒>−36dB）が無いもの → 主役ラベル（Aのみ有効）→ 音量が−15.5 LUFS に近いもの。
"""
import json, pathlib, yaml
D = pathlib.Path('/Users/ryo/Desktop/BGM/IRO/Drive/21_遠回りして帰ろうか')
AST = json.loads((D / '_work/候補_自動検品.json').read_text()); QC = json.loads((D / '_work/全50曲_検品.json').read_text())
NAME = {'A': 'Aペダルスチール', 'B': 'Bクラリネット', 'C': 'Cスティールパン', 'D': 'Dフレットレスベース', 'E': 'Eオーボエ', 'F': 'Fハモンドオルガン'}
WANT = {'A': 6, 'B': 5, 'C': 5, 'D': 5, 'E': 5, 'F': 5}
missing = sorted(set(QC) - set(AST)); assert not missing, f'人声の検品が未了: {missing}'
excl, pool = {}, {k: [] for k in NAME}
for n, q in QC.items():
    a = AST[n]; why = []
    if a['人声の最大'] > 0.03: why.append(f"人声{a['人声の最大']}")
    if q['途中無音秒'] >= 2: why.append(f"途中無音{q['途中無音秒']}秒")
    if q['最後1秒dB'] > -25: why.append(f"尾の切れ{q['最後1秒dB']}dB")
    if why: excl[n] = '・'.join(why); continue
    lead = max(a['主役ラベル'].values()) if a['主役ラベル'] else 0
    pool[n.split('_')[1][0]].append((q['最後1秒dB'] > -36, -lead if n.split('_')[1][0] == 'A' else 0, abs(q['LUFS'] + 15.5), n))
pick = {k: [x[3] for x in sorted(v)[:WANT[k]]] for k, v in pool.items()}
for k in pick: assert len(pick[k]) == WANT[k], (k, pick[k])
order = []
for r in range(6):
    for k in 'ABCDEF':
        if r < len(pick[k]): order.append(pick[k][r])
# A の6曲目は最後（31曲目）。最後は2時間の手前で10秒フェードするので尾の弱いものでもよい
order = [n for n in order if n != pick['A'][5]] + [pick['A'][5]]
p = pathlib.Path(__file__).resolve().parent / 'volumes/iro21.yaml'
cfg = yaml.safe_load(p.read_text()) if p.exists() else {}
cfg.update({'kinds': {n: NAME[n.split('_')[1][0]] for n in order}, 'picked': [n + '.wav' for n in order],
            'order_tracks': [n + '.wav' for n in order], 'exclude': excl})
p.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
print(len(order), '曲'); print('\n'.join(order)); print('除外', excl)
