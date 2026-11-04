"""青空文庫『銀河鉄道の夜』を、読み上げ用の文の並びにする。

RDG02の prep_text.py と同じ考え方：ルビ《》は読み方としてそのまま使い、
画面用の表記（display）と、合成に渡す読み（spoken）を分けて持つ。
章題は読み上げる（kind='title'）。未定稿の亀甲注記は設計メモの扱いに従う：
標札の文字は括弧だけ外し、空白は読まずに短い間、原稿の欠落は長めの間（gap_after）。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / '素材' / 'gingatetsudo_utf8.txt'
OUT = HERE / 'sentences.json'
FIX = HERE / 'reading_fixes.json'   # ルビの無い語の読み直し（検品で足す）

KANJI = r'[一-鿿々〆ヶ※]'
MISSING = '〔以下原稿一枚？なし〕'
CHAP_KANA = {'一': 'いち', '二': 'に', '三': 'さん', '四': 'よん', '五': 'ご',
             '六': 'ろく', '七': 'なな', '八': 'はち', '九': 'きゅう'}


def strip_notes(s):
    return re.sub(r'［＃[^］]*］', '', s)


def bracket_notes(s, blank):
    """亀甲注記：標札の文字は残し、空白の注記は blank に置き換える。"""
    s = s.replace(MISSING, '').replace('〔以下数文字分空白〕', '')
    s = re.sub(r'〔[^〕]*空白〕', blank, s)
    return re.sub(r'〔([^〕]*)〕', r'\1', s)


def to_display(s):
    s = bracket_notes(strip_notes(s), '　').replace('｜', '')
    return re.sub(r'《[^》]*》', '', s)


def to_spoken(s, fixes):
    s = bracket_notes(strip_notes(s), '、')
    def kata(m):
        r = m.group(1)
        if re.search('[ゃゅょ]', r):   # 拗音をカタカナにすると「ヤ」と読まれる
            return r
        return ''.join(chr(ord(c) + 96) if 'ぁ' <= c <= 'ゖ' else c for c in r)
    s = re.sub(r'｜[^《]+《([^》]+)》', kata, s)
    s = re.sub(rf'{KANJI}+《([^》]+)》', kata, s)
    for a, b in fixes:
        s = s.replace(a, b)
    return flat(s)


def flat(s):
    s = s.replace('「', '').replace('」', '。').replace('（', '').replace('）', '。')
    return re.sub(r'、+', '、', re.sub(r'。+', '。', s)).strip('　 、')


def split(s):
    return [p.strip('、　') for p in re.split(r'(?<=。)', s) if p.strip('、。　 ')]


def main():
    fixes = json.loads(FIX.read_text()) if FIX.exists() else []
    text = SRC.read_text().replace('※［＃小書き平仮名ん、168-12］', 'ん')
    lines = text.splitlines()
    body = lines[[i for i, l in enumerate(lines) if l.startswith('-----')][1] + 1:]
    body = body[:next(i for i, l in enumerate(body) if l.startswith('底本：'))]
    out, para = [], 0
    for raw in body:
        raw = raw.rstrip()
        if not raw.strip():
            continue
        if '中見出し' in raw:
            shown = to_display(raw).strip('　 ')
            num, name = shown.split('、', 1)
            spoken = to_spoken(strip_notes(raw).strip('　 ').split('、', 1)[1], fixes).strip('。')
            out.append({'kind': 'title', 'para': 0, 'display': shown,
                        'spoken': f'{CHAP_KANA[num]}、{spoken}。'})
            continue
        para += 1
        disp = to_display(raw).strip('　 ')
        s_parts = split(to_spoken(raw, fixes))
        d_sent = split(flat(disp))
        assert len(d_sent) == len(s_parts), (disp, s_parts)
        o = {'kind': 'para', 'para': para, 'display': disp,
             'sentences': s_parts, 'display_sentences': d_sent}
        if MISSING in raw:
            o['gap_after'] = 'missing'
        out.append(o)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    ps = [o for o in out if o['kind'] == 'para']
    print(f'章 {len(out) - len(ps)}・段落 {len(ps)}・文 {sum(len(o["sentences"]) for o in ps)}'
          f'・欠落の間 {sum("gap_after" in o for o in ps)}')
    left = [s for o in ps for s in o['sentences'] if re.search(r'[〔〕［］《》｜※]', s)]
    print('注記の残り', left)


if __name__ == '__main__':
    main()
