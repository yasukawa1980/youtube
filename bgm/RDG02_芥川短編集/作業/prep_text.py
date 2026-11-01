"""青空文庫の3作（蜘蛛の糸・トロッコ・杜子春）を、読み上げ用の文の並びにする。

RDG01の prep_text.py と同じ考え方：ルビ《》は読み方としてそのまま使い、
画面用の表記（display）と、合成に渡す読み（spoken）を分けて持つ。
作品名は読み上げ、章番号（一、二…）は読まずに間だけ取る（kind='chap'）。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / '素材'
OUT = HERE / 'sentences.json'
FIX = HERE / 'reading_fixes.json'   # ルビの無い語の読み直し（検品で足す）

WORKS = [('蜘蛛の糸', 'くものいと', 'kumono_ito_utf8.txt'),
         ('トロッコ', 'とろっこ', 'torokko_utf8.txt'),
         ('杜子春', 'とししゅん', 'toshishun_shin_utf8.txt')]   # 新字新仮名版（card43015）
KANJI = r'[一-鿿々〆ヶ※]'
GAIJI = {'特のへん＋廴＋聿': '犍', '均のつくり': '匂'}
RUBY_FIX = {'すいしよう': 'すいしょう'}   # 青空文庫の入力で小書きになっていないルビ


def strip_notes(s):
    return re.sub(r'［＃[^］]*］', '', s)


def gaiji(s):
    return re.sub(r'※［＃「([^」]+)」[^］]*］', lambda m: GAIJI[m.group(1)], s)


def to_display(s):
    s = strip_notes(s).replace('｜', '')
    return re.sub(r'《[^》]*》', '', s)


def to_spoken(s, fixes):
    s = strip_notes(s)
    def kata(m):
        r = RUBY_FIX.get(m.group(1), m.group(1))
        if re.search('[ゃゅょ]', r):   # 拗音をカタカナにすると「ヤ」と読まれる
            return r
        return ''.join(chr(ord(c) + 96) if 'ぁ' <= c <= 'ゖ' else c for c in r)
    s = re.sub(r'｜[^《]+《([^》]+)》', kata, s)
    s = re.sub(rf'{KANJI}+《([^》]+)》', kata, s)
    for a, b in fixes:
        s = s.replace(a, b)
    s = s.replace('——', '、').replace('「', '').replace('」', '。')
    s = re.sub(r'。+', '。', s)
    s = re.sub(r'、+', '、', s)
    return s.strip('　 、')


def flat(s):
    s = s.replace('——', '、').replace('「', '').replace('」', '。')
    return re.sub(r'、+', '、', re.sub(r'。+', '。', s)).strip('、')


def split(s):
    return [p.strip('、') for p in re.split(r'(?<=。)', s) if p.strip('、。 ')]


def main():
    fixes = json.loads(FIX.read_text()) if FIX.exists() else []
    out = []
    for work, kana, name in WORKS:
        lines = gaiji((SRC / name).read_text()).splitlines()
        body = lines[[i for i, l in enumerate(lines) if l.startswith('-----')][1] + 1:]
        body = body[:next(i for i, l in enumerate(body) if l.startswith('底本：'))]
        out.append({'work': work, 'kind': 'title', 'para': 0, 'display': work, 'spoken': kana})
        para = 0
        for raw in body:
            raw = raw.rstrip()
            if not raw.strip() or re.fullmatch(r'［＃[^］]*］', raw.strip('　')):
                continue
            if re.fullmatch(r'（[^）]*年[^）]*）', strip_notes(raw).strip('　 ')):
                continue   # 末尾の執筆日は読まない
            m = re.search(r'([一二三四五六七八九十]+)［＃「.」は中見出し］', raw)
            if m:
                out.append({'work': work, 'kind': 'chap', 'para': 0, 'display': m.group(1)})
                continue
            para += 1
            disp = to_display(raw).strip('　 ')
            # 「…………」だけの文は読まずに間にする（spoken を空にする）
            s_parts = [p if re.search(r'[ぁ-んァ-ヶ一-鿿]', p) else ''
                       for p in split(to_spoken(raw, fixes))]
            d_sent = split(flat(disp))
            assert len(d_sent) == len(s_parts), (disp, s_parts)
            out.append({'work': work, 'kind': 'para', 'para': para, 'display': disp,
                        'sentences': s_parts, 'display_sentences': d_sent})
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for work, *_ in WORKS:
        ws = [o for o in out if o['work'] == work and o['kind'] == 'para']
        print(f'{work}：段落 {len(ws)}・文 {sum(len(o["sentences"]) for o in ws)}'
              f'・表示字数 {sum(len(o["display"]) for o in ws)}')


if __name__ == '__main__':
    main()
