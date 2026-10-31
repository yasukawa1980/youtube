"""青空文庫の本文を、読み上げ用の文の並びにする。

ルビ《》は読み方としてそのまま使う（親字を読み仮名に置き換える）。
画面用の表記（display）と、合成に渡す読み（spoken）を分けて持つ。
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / '素材/yume_juya_utf8.txt'
OUT = HERE / 'sentences.json'
FIX = HERE / 'reading_fixes.json'   # ルビの無い語の読み直し（検品で足す）

TITLES = dict(zip([f'第{n}夜' for n in '一二三四五六七八九十'],
                  ['だいいちや', 'だいにや', 'だいさんや', 'だいよや', 'だいごや',
                   'だいろくや', 'だいななや', 'だいはちや', 'だいくや', 'だいじゅうや']))
KANJI = r'[一-鿿々〆ヶ※]'


def strip_notes(s):
    return re.sub(r'［＃[^］]*］', '', s)


GAIJI = {'目＋爭': '睜', '楫のつくり＋戈': '戢'}


def to_display(s):
    s = re.sub(r'※［＃「([^」]+)」[^］]*］', lambda m: GAIJI[m.group(1)], s)
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
    s = s.replace('※', '')
    for a, b in fixes:
        s = s.replace(a, b)
    s = s.replace('——', '、').replace('「', '').replace('」', '。')
    s = re.sub(r'。+', '。', s)
    s = re.sub(r'、+', '、', s)
    return s.strip('　 、')


def main():
    fixes = json.loads(FIX.read_text()) if FIX.exists() else []
    lines = SRC.read_text().splitlines()
    body = lines[lines.index('［＃５字下げ］第一夜［＃「第一夜」は中見出し］'):]
    body = body[:next(i for i, l in enumerate(body) if l.startswith('底本：'))]
    out, night, para = [], None, 0
    for raw in body:
        raw = raw.rstrip()
        if not raw.strip():
            continue
        m = re.search(r'(第.夜)［＃「', raw)
        if m:
            night, para = m.group(1), 0
            out.append({'night': night, 'kind': 'title', 'para': 0,
                        'display': night, 'spoken': TITLES[night]})
            continue
        para += 1
        disp = to_display(raw).strip('　 ')
        spk = to_spoken(raw, fixes)
        # 文に分ける（」の直後も区切る）
        d_parts = re.findall(r'[^。」]+(?:。」|」|。)?', disp)
        s_parts = [p.strip('、') for p in re.split(r'(?<=。)', spk) if p.strip('、。 ')]
        d_src = disp.replace('——', '、').replace('「', '').replace('」', '。')
        d_src = re.sub(r'、+', '、', re.sub(r'。+', '。', d_src)).strip('、')
        d_sent = [p.strip('、') for p in re.split(r'(?<=。)', d_src) if p.strip('、。 ')]
        assert len(d_sent) == len(s_parts), (disp, spk)
        out.append({'night': night, 'kind': 'para', 'para': para,
                    'display': disp, 'sentences': s_parts, 'display_sentences': d_sent})
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    n = sum(len(o.get('sentences', [])) for o in out)
    chars = sum(len(o['display']) for o in out)
    print(f'段落 {sum(o["kind"] == "para" for o in out)}・文 {n}・表示字数 {chars}')


if __name__ == '__main__':
    main()
