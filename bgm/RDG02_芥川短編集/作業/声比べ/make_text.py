"""声の聞き比べ用：蜘蛛の糸の題と冒頭3段落の前半を、読み上げ用の文に分ける。"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / 'RDG01_夢十夜/作業'))
from prep_text import to_spoken  # noqa: E402

SRC = HERE.parents[1] / '素材/kumono_ito_utf8.txt'
FIXES = [['陀多', 'カンダタ'], ['御歩き', 'おあるき'], ['御眼', 'おめ'], ['丁度', 'ちょうど'],
         ['居ります', 'おります'], ['御覧', 'ごらん'], ['一しょ', 'いっしょ'], ['大泥坊', 'おおどろぼう'], ['御釈迦様', 'おしゃかさま'], ['透き徹して', 'すきとおして']]

lines = SRC.read_text().replace('すいしよう', 'すいしょう').splitlines()
start = lines.index('［＃８字下げ］一［＃「一」は中見出し］') + 2
paras = [l for l in lines[start:start + 4] if l.strip()][:3]
sents = ['くものいと。']
for p in paras:
    sents += [s for s in re.split(r'(?<=。)', to_spoken(p, FIXES)) if s.strip('、。 ')]
sents = sents[:8]   # 約1分半
(HERE / 'sentences.json').write_text(json.dumps(sents, ensure_ascii=False, indent=1))
print(len(sents), sum(map(len, sents)))
print('\n'.join(sents))
