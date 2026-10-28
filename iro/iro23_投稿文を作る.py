"""IRO23 の投稿文一式を作る（Claude 2026-10-28。IRO22 の 投稿文を作る.py の形を、区切りのないカフェの巻に合わせた）。

章は場面の切り替わり6か所（20分ごと・溶かしの中央）。時刻は扉ムービーの分（長さ＋間）を足して、秒を切り上げる。
貼り付け用は iro/IRO23_雨やどりのつもりだった_貼り付け用/ と Mac の 投稿用/ に同じものを置く。
★説明文の楽器名は Suno の指定どおり。判定器では主役を確かめきれていない（本人の通し視聴で確認）。
"""
import math, shutil, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT / 'IRO23_雨やどりのつもりだった_貼り付け用'; KIT.mkdir(exist_ok=True)
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Cafe/23_雨やどりのつもりだった/投稿用')
spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
SHIFT = door.dur(door.MOVIE) + door.BREATH        # 本編の 0秒が扉入りで何秒目か
SCENE = 1200


def ts(s):
    s = int(math.ceil(s)); h, m, x = s // 3600, s % 3600 // 60, s % 60
    return f'{h}:{m:02d}:{x:02d}' if h else f'{m}:{x:02d}'


NAMES = [('雨やどり', 'Coming in from the rain'), ('雨が強くなる', 'The rain gets heavier'), ('手元で、ひと休み', 'A book and a warm cup'),
         ('雨上がりの夕方', 'Evening after the rain'), ('窓の外から', 'From the street outside'), ('閉店まで', 'Until closing time')]
ch_ja = [f'{"0:00" if i == 0 else ts(SHIFT + i * SCENE)} {ja}' for i, (ja, en) in enumerate(NAMES)]
ch_en = [f'{"0:00" if i == 0 else ts(SHIFT + i * SCENE)} {en}' for i, (ja, en) in enumerate(NAMES)]

title_ja = '雨やどりの、つもりだった。｜カフェBGM 2時間 雨の午後から夜まで ジャズ Lo-fi 作業用・読書用'
title_en = 'I Only Meant to Wait Out the Rain | Café Jazz Lo-fi 2 Hours'
assert len(title_ja) <= 100 and len(title_en) <= 100
tags_hash = '#カフェBGM #作業用BGM #読書用BGM'
desc_ja = ('急な雨に、通りの小さな喫茶店へ。\n少しだけのつもりが、気づけば閉店まで。\n\n'
           '雨の午後から、雨上がりの夕方、灯りのともる夜まで。\n'
           '窓辺の席で過ごす2時間の、カフェのジャズ Lo-fi です。\n\n'
           'アコーディオン、ウクレレ、オルゴール、バンドネオン、チャランゴ、アルトリコーダー。\n'
           'ブラシのドラムとウッドベースの上で、主役の楽器が違う曲を入れ替えながら流します。\n'
           '2時間のあいだ、同じ曲は二度出てきません。歌や人の声、雨の音は入っていません。\n\n'
           '足元では、ゴールデンレトリバーがずっと眠っています。\n\n'
           '── 章 ──\n' + '\n'.join(ch_ja) + '\n\n' + tags_hash)
desc_en = ('A sudden shower, and a small café on the corner.\nShe only meant to stay a little while — and stayed until closing.\n\n'
           'From a rainy afternoon, through the evening after the rain, into the lamp-lit night:\n'
           'two hours of café jazz lo-fi at a seat by the window.\n\n'
           'Accordion, ukulele, music box, bandoneon, charango and alto recorder,\n'
           'over soft brushed drums and upright bass — the tracks rotate between different lead instruments.\n'
           'No track repeats in the full two hours. No vocals, no rain sounds.\n\n'
           'At her feet, a golden retriever sleeps the whole time.\n\n'
           '── Chapters ──\n' + '\n'.join(ch_en))

S = {'A': ('雨が上がるまで、あと一杯。', '窓の外は強い雨。両手で包んだマグが、まだあたたかい。', 'One more cup until the rain stops.'),
     'B': ('ページをめくる音だけ。', '雨の窓辺で、本とコーヒー。湯気の向こうに、ぬれた町。', 'Just the sound of turning pages.'),
     'C': ('となりの寝息が、いちばん落ち着く。', '本を読みながら、足元で眠る相棒にそっと手をのせて。', 'The calmest sound is my friend sleeping beside me.'),
     'D': ('気づけば、灯りがついていた。', '雨上がりの夜、通りから見た喫茶店の窓。', 'Before I knew it, the lights were on.')}
short = {t: f'【タイトル】\n{a}☕ カフェBGM #shorts\n\n【説明】\n{b}\n{c}\n\n雨の午後から夜までの2時間の本編は、関連動画からどうぞ。\n\n#カフェBGM #作業用BGM #shorts\n\n【関連動画】本編 IRO23 を公開後に設定'
         for t, (a, b, c) in S.items()}

files = {
    '01_タイトル_日本語.txt': title_ja,
    '02_タイトル_英語.txt': title_en,
    '05_説明文_日本語.txt': desc_ja,
    '06_説明文_英語.txt': desc_en,
    '07_ハッシュタグ.txt': tags_hash,
    '08_タグ.txt': 'カフェBGM, 作業用BGM, 読書用BGM, 雨の日BGM, カフェミュージック, ジャズ, Lo-fi, ローファイ, 喫茶店, 雨, 夜, 犬, ゴールデンレトリバー, 2時間, cafe music, coffee shop music, cafe jazz, lofi jazz, rainy cafe, rainy day music, study music, reading music, 2 hours, IRO Sounds',
    '09_再生リスト_タイトル.txt': '☕ Café / Chill｜カフェ・チルBGM',
    '10_英語ローカライズ_説明文.txt': title_en + '\n\n' + desc_en,
    '11_チャプター.txt': '\n'.join(ch_ja) + '\n\n' + '\n'.join(ch_en),
    '13_ショートA_雨の窓.txt': short['A'], '14_ショートB_手元.txt': short['B'], '15_ショートC_犬.txt': short['C'], '16_ショートD_窓越しの夜.txt': short['D'],
}
files['00_説明文_これを貼る.txt'] = desc_ja + '\n\n── English ──\n\n' + desc_en
files['00_使い方.txt'] = ('本人の通し視聴の後に予約する。本編・ショート4本・サムネ（本編用と、ショート4本共通の縦）は Mac の 投稿用 フォルダ。\n'
                        'IRO Sounds の既定説明文を残し、その上に 00 の本文を挿入（日本語→英語）。\n再生リストは 09（既存）。本編は10時公開・ショートは12時／21時（10/25〜の方針）。\n'
                        'IRO の公開は本編＋ショートで1日3本まで・ショートは1日2本まで。')
for k, v in files.items():
    (KIT / k).write_text(v + '\n')
    if MAC.exists(): shutil.copy2(KIT / k, MAC / k)
print(len(files), '件', '題', len(title_ja), len(title_en), '字'); print('\n'.join(ch_ja))
