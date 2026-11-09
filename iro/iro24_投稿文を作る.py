"""IRO24 の投稿文一式を作る（Claude 2026-11-10。iro23_投稿文を作る.py の形を写した）。

章は場面の切り替わり6か所（30分ごと・溶かしの中央）。時刻は扉ムービーの分（長さ＋間）を足して、秒を切り上げる。
貼り付け用は iro/IRO24_今年もツリーを出した_貼り付け用/ と Mac の 投稿用/ に同じものを置く。
★説明文の楽器名は Suno の指定どおり。判定器では主役を確かめきれていない（本人の通し視聴で確認）。
"""
import math, shutil, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT / 'IRO24_今年もツリーを出した_貼り付け用'; KIT.mkdir(exist_ok=True)
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Seasonal/24_今年もツリーを出した/投稿用')
spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
SHIFT = door.dur(door.MOVIE) + door.BREATH        # 本編の 0秒が扉入りで何秒目か
SCENE = 1800


def ts(s):
    s = int(math.ceil(s)); h, m, x = s // 3600, s % 3600 // 60, s % 60
    return f'{h}:{m:02d}:{x:02d}' if h else f'{m}:{x:02d}'


NAMES = [('ツリーを出す', 'Taking out the tree'), ('雪が降りはじめる', 'The first snow'), ('手元で、ひと休み', 'Cocoa and ornaments'),
         ('灯りがともる', 'The lights come on'), ('窓の外から', 'From the snowy street'), ('灯りだけの夜', 'Only the tree lights')]
ch_ja = [f'{"0:00" if i == 0 else ts(SHIFT + i * SCENE)} {ja}' for i, (ja, en) in enumerate(NAMES)]
ch_en = [f'{"0:00" if i == 0 else ts(SHIFT + i * SCENE)} {en}' for i, (ja, en) in enumerate(NAMES)]

title_ja = '今年も、ツリーを出した。｜クリスマスジャズ 3時間 雪の夜 作業用・勉強用・読書用BGM'
title_en = 'The Tree Is Up Again This Year | Cozy Christmas Jazz 3 Hours'
assert len(title_ja) <= 100 and len(title_en) <= 100
tags_hash = '#クリスマスBGM #クリスマスジャズ #作業用BGM'
desc_ja = ('12月の午後、押し入れから箱を出して、今年もツリーを飾る。\n'
           '雪が降りはじめ、灯りがともり、夜が深くなるまで。\n\n'
           '冬の部屋で過ごす3時間の、クリスマスジャズです。\n\n'
           'ピアノトリオ、ビブラフォン、テナーサックス、チェロ、グロッケンシュピール、フレンチホルン。\n'
           'ブラシのドラムとウッドベースの上で、主役の楽器が違う曲を入れ替えながら流します。\n'
           '曲はすべてこの動画のためのオリジナルで、定番のクリスマスソングは入っていません。\n'
           '3時間のあいだ、同じ曲は二度出てきません。歌や人の声は入っていません。\n\n'
           'となりでは、ゴールデンレトリバーがずっと眠っています。\n\n'
           '── 章 ──\n' + '\n'.join(ch_ja) + '\n\n' + tags_hash)
desc_en = ('A December afternoon: the boxes come out, and the tree goes up again.\n'
           'Then the first snow, the lights coming on, and a long, quiet night.\n\n'
           'Three hours of cozy Christmas jazz in a warm winter room.\n\n'
           'Piano trio, vibraphone, tenor saxophone, cello, glockenspiel and French horn,\n'
           'over soft brushed drums and upright bass — the tracks rotate between different lead instruments.\n'
           'All tracks are original pieces made for this video (no classic Christmas songs).\n'
           'No track repeats in the full three hours. No vocals.\n\n'
           'Beside her, a golden retriever sleeps the whole time.\n\n'
           '── Chapters ──\n' + '\n'.join(ch_en))

S = {'A': ('今年も、この季節が来た。', '窓の外に、今年はじめての雪。ツリーの飾りつけは、まだ途中。', 'This season has come around again.'),
     'B': ('ココアが冷めるまで、もう少し。', 'オーナメントの箱をあけて、ひと休み。マグから湯気がのぼる。', 'A little longer, until the cocoa cools.'),
     'C': ('灯りの下で、となりは寝息。', 'ツリーの灯りのそばで本を読む。となりで眠る相棒に、そっと手をのせて。', 'Under the lights, my friend is fast asleep.'),
     'D': ('外は雪。部屋だけ、あたたかい。', '雪の夜、通りから見た窓。ツリーの灯りと、本を読む人と犬。', 'Snow outside. Only the room is warm.')}
short = {t: f'【タイトル】\n{a}🎄 クリスマスジャズ #shorts\n\n【説明】\n{b}\n{c}\n\n雪の夜のクリスマスジャズ3時間の本編は、関連動画からどうぞ。\n\n#クリスマスBGM #クリスマスジャズ #shorts\n\n【関連動画】本編 IRO24 を公開後に設定'
         for t, (a, b, c) in S.items()}

files = {
    '01_タイトル_日本語.txt': title_ja,
    '02_タイトル_英語.txt': title_en,
    '05_説明文_日本語.txt': desc_ja,
    '06_説明文_英語.txt': desc_en,
    '07_ハッシュタグ.txt': tags_hash,
    '08_タグ.txt': 'クリスマスBGM, クリスマスジャズ, 作業用BGM, 勉強用BGM, 読書用BGM, ジャズ, ピアノ, クリスマス, 冬, 雪, 夜, ツリー, 犬, ゴールデンレトリバー, 3時間, christmas jazz, christmas music, cozy christmas, winter jazz, christmas ambience, study music, reading music, 3 hours, IRO Sounds',
    '09_再生リスト_タイトル.txt': '🎄 Christmas｜クリスマスBGM（新規作成）',
    '10_英語ローカライズ_説明文.txt': title_en + '\n\n' + desc_en,
    '11_チャプター.txt': '\n'.join(ch_ja) + '\n\n' + '\n'.join(ch_en),
    '13_ショートA_初雪の窓.txt': short['A'], '14_ショートB_ココア.txt': short['B'], '15_ショートC_犬.txt': short['C'], '16_ショートD_窓越しの夜.txt': short['D'],
}
files['00_説明文_これを貼る.txt'] = desc_ja + '\n\n── English ──\n\n' + desc_en
files['00_使い方.txt'] = ('本人の通し視聴の後に予約する。本編・ショート4本・サムネ（本編用と、ショート1本ずつの縦）は Mac の 投稿用 フォルダ。\n'
                        'IRO Sounds の既定説明文を残し、その上に 00 の本文を挿入（日本語→英語）。\n再生リストは 09（新規。クリスマスの巻はここへ）。公開は11/22〜28ごろ。本編は10時公開・ショートは12時／21時（10/25〜の方針）。\n'
                        'IRO の公開は本編＋ショートで1日3本まで・ショートは1日2本まで。')
for k, v in files.items():
    (KIT / k).write_text(v + '\n')
    if MAC.exists(): shutil.copy2(KIT / k, MAC / k)
print(len(files), '件', '題', len(title_ja), len(title_en), '字'); print('\n'.join(ch_ja))
