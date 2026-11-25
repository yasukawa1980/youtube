"""青空文庫の新美南吉4編（手袋を買いに・ごん狐・おじいさんのランプ・狐）を、読み上げ用の文の並びにする。

RDG04の prep_text.py を流用。違い：ごん狐の章見出し（一〜六）は読まず kind='break'（間だけ）。
手袋を買いにの子守唄（字下げの4行）は1段落にまとめる。傍点の注記は消す。

RDG02の prep_text.py と同じ考え方：ルビ《》は読み方としてそのまま使い、
画面用の表記（display）と、合成に渡す読み（spoken）を分けて持つ。
作品名は読み上げる（kind='title'）。末尾の出典注記（古伝説と…／初出誌）は読まない。
本文中の丸括弧の注（姪・トランプ遊戯の一種 等）は、読みでは読点で挟む。
短い引用「カナリヤのお食事」みたいに 等は、読みでは括弧を外して文を切らない。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / '素材'
OUT = HERE / 'sentences.json'
FIX = HERE / 'reading_fixes.json'   # ルビの無い語の読み直し（検品で足す）

WORKS = [('手袋を買いに', 'てぶくろをかいに', 'tebukuro_utf8.txt'),
         ('ごん狐', 'ごんぎつね', 'gongitsune_utf8.txt'),
         ('おじいさんのランプ', 'おじいさんのランプ', 'ojiisan_no_lamp_utf8.txt'),
         ('狐', 'きつね', 'kitsune_utf8.txt')]
KANJI = r'[一-鿿々〆ヶ※]'


def strip_notes(s):
    return re.sub(r'［＃[^］]*］', '', s)


def inline_quotes(s):
    """文の途中の短い引用（後ろが「と」「、」「。」以外に続くもの）は括弧を外す。"""
    return re.sub(r'「([^「」。]{1,20})」(?=[みな])', r'\1', s)


def to_display(s):
    s = strip_notes(s).replace('｜', '')
    return re.sub(r'《[^》]*》', '', s)


def to_spoken(s, fixes):
    s = strip_notes(s)
    def kata(m):
        r = m.group(1)
        if re.search('[ゃゅょ]', r):   # 拗音をカタカナにすると「ヤ」と読まれる
            return r
        return ''.join(chr(ord(c) + 96) if 'ぁ' <= c <= 'ゖ' else c for c in r)
    s = re.sub(r'｜[^《]+《([^》]+)》', kata, s)
    s = re.sub(rf'{KANJI}+《([^》]+)》', kata, s)
    for a, b in fixes:
        s = s.replace(a, b)
    s = re.sub(r'（([^）]*)）', r'、\1、', s)
    return flat(s)


def flat(s):
    s = inline_quotes(s)
    s = s.replace('——', '、').replace('―', '').replace('「', '').replace('」', '。')
    return re.sub(r'、+', '、', re.sub(r'。+', '。', s)).strip('　 、')


def split(s):
    return [p.strip('、　') for p in re.split(r'(?<=。)', s) if p.strip('、。　 ')]


def clean_disp(d):
    d = re.sub(r'([、？！])。$', lambda m: '。' if m.group(1) == '、' else m.group(1), d)
    return d   # 字幕に「さあ、。」「？。」を出さない


def main():
    fixes = json.loads(FIX.read_text()) if FIX.exists() else []
    out = []
    for work, kana, name in WORKS:
        lines = (SRC / name).read_text().splitlines()
        body = lines[[i for i, l in enumerate(lines) if l.startswith('-----')][1] + 1:]
        body = body[:next(i for i, l in enumerate(body) if l.startswith('底本：'))]
        out.append({'work': work, 'kind': 'title', 'para': 0, 'display': work, 'spoken': kana + '。'})
        para = 0
        merged, buf, inblock = [], [], False
        for raw in body:
            raw = raw.rstrip()
            if '［＃ここから' in raw:
                inblock = True; continue
            if '［＃ここで字下げ終わり］' in raw:
                inblock = False; merged.append('　'.join(buf)); buf = []; continue
            if inblock:
                buf.append(raw.strip('　')); continue
            merged.append(raw)
        for raw in merged:
            if '中見出し' in raw:
                out.append({'work': work, 'kind': 'break', 'para': para,
                            'display': strip_notes(raw).strip('　 ')})
                continue
            if not raw.strip() or re.fullmatch(r'［＃[^］]*］', raw.strip('　')):
                continue
            para += 1
            disp = to_display(raw).strip('　 ')
            s_parts = [p if re.search(r'[ぁ-んァ-ヶ一-鿿]', p) else ''
                       for p in split(to_spoken(raw, fixes))]
            d_sent = [clean_disp(d) for d in split(flat(disp))]
            assert len(d_sent) == len(s_parts), (disp, s_parts, d_sent)
            out.append({'work': work, 'kind': 'para', 'para': para, 'display': disp,
                        'sentences': s_parts, 'display_sentences': d_sent})
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for work, *_ in WORKS:
        ws = [o for o in out if o['work'] == work and o['kind'] == 'para']
        print(f'{work}：段落 {len(ws)}・文 {sum(len(o["sentences"]) for o in ws)}'
              f'・読み字数 {sum(len(s) for o in ws for s in o["sentences"])}')
    left = [s for o in out if o['kind'] == 'para' for s in o['sentences']
            if re.search(r'[〔〕［］《》｜※（）「」]', s)]
    print('記号の残り', left)


if __name__ == '__main__':
    main()
