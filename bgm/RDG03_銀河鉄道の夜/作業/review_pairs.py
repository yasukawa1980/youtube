"""kana_review.txt から「漢字のかたまり → 読み」を文ごとに対応づけ、重複を除いて一覧にする。
助詞の発音（は→ワ等）と長音（う→オ等）を許して、かなを手がかりに合わせる。"""
import collections
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ALT = {'ハ': 'ハワ', 'ヘ': 'ヘエ', 'ヲ': 'ヲオ', 'ウ': 'ウオ', 'オ': 'オウ', 'エ': 'エイ', 'イ': 'イエ',
       'ヅ': 'ヅズ', 'ヂ': 'ヂジ', 'ー': 'ーアイウエオ'}
KANJI = r'[一-鿿々〆ヶ]+'


def kata(s):
    return ''.join(chr(ord(c) + 96) if 'ぁ' <= c <= 'ゖ' else c for c in s)


def pattern(spoken):
    out, runs = '', []
    for tok in re.findall(rf'{KANJI}|[^一-鿿々〆ヶ]', kata(spoken)):
        if re.fullmatch(KANJI, tok):
            out += '(.+?)'
            runs.append(tok)
        elif re.fullmatch(r'[ァ-ヶー]', tok):
            alts = ALT.get(tok, tok)
            out += f'[{alts}]?' if tok in 'ウオーッ' else f'[{alts}]'
        # 記号は読みに出ないので飛ばす
    return re.compile('^' + out + '$'), runs


pairs = collections.defaultdict(list)
fail = []
for row in (HERE / 'kana_review.txt').read_text().splitlines():
    n, rest = row.split(': ', 1)
    spoken, kana = rest.rsplit(' ｜ ', 1)
    kana = re.sub(r'[、。？！]', '', kana)
    pat, runs = pattern(spoken)
    m = pat.match(kana) if runs else None
    if runs and not m:
        fail.append(row)
    elif m:
        for r, k in zip(runs, m.groups()):
            pairs[(r, k)].append(int(n))
lines = [f'{r}={k} ×{len(v)} #{v[0]}' for (r, k), v in sorted(pairs.items(), key=lambda x: x[0][0])]
(HERE / 'pairs.txt').write_text('\n'.join(lines))
(HERE / 'pairs_fail.txt').write_text('\n'.join(fail))
print(len(lines), 'ペア・合わなかった文', len(fail))
