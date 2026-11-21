"""IRO25 の投稿文一式を作る（Claude 2026-11-21。iro24_投稿文を作る.py の形・IRO01 のポモドーロの章立てを写した）。

章は作業と休憩の始まり12か所（IRO01 と同じ）。時刻は扉ムービーの分（長さ＋間）を足して、秒を切り上げる（0:00 は扉から）。
貼り付け用は iro/IRO25_雪が積もるまで集中する_貼り付け用/ と Mac の 投稿用/ に同じものを置く。
★説明文の楽器名は Suno の指定どおり。判定器で確かめられたのはフルート・ヴァイオリンだけ（本人の通し視聴で確認）。
★効能（集中力が上がる等）は書かない。「受験」は利用場面として説明文に1回だけ。
"""
import math, shutil, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT / 'IRO25_雪が積もるまで集中する_貼り付け用'; KIT.mkdir(exist_ok=True)
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Study/25_雪が積もるまで集中する/投稿用')
spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
SHIFT = door.dur(door.MOVIE) + door.BREATH        # 本編の 0秒が扉入りで何秒目か
FOCUS, BREAK, BLOCKS = 1500, 300, 6


def ts(s):
    s = int(math.ceil(s)); h, m, x = s // 3600, s % 3600 // 60, s % 60
    return f'{h}:{m:02d}:{x:02d}' if h else f'{m}:{x:02d}'


ch_ja, ch_en = [], []
for b in range(BLOCKS):
    t0 = b * (FOCUS + BREAK)
    ch_ja += [f'{"0:00" if b == 0 else ts(SHIFT + t0)} 作業 {b + 1}／{BLOCKS}', f'{ts(SHIFT + t0 + FOCUS)} 休憩 {b + 1}']
    ch_en += [f'{"0:00" if b == 0 else ts(SHIFT + t0)} Focus {b + 1}/{BLOCKS}', f'{ts(SHIFT + t0 + FOCUS)} Break {b + 1}']

title_ja = '雪が積もるまで、集中する。｜ポモドーロタイマー 3時間 25分×6 勉強用BGM 冬 Lo-fi'
title_en = '3 Hour Pomodoro Timer 25/5 ×6 | Winter Study Lo-fi | Focus Until the Snow Settles'
assert len(title_ja) <= 100 and len(title_en) <= 100
tags_hash = '#勉強用BGM #作業用BGM #集中BGM'
desc_ja = ('25分の作業と5分の休憩を6回。3時間ぶんのポモドーロです。\n'
           '冬の午後、こたつで勉強をはじめて、窓の外に雪が積もるまで。\n\n'
           '画面の右上に残り時間を出しています。\n'
           '作業の25分はLo-fiのビート、休憩の5分はビートのない静かな曲に変わります。\n'
           '切り替わりには小さなチャイムが鳴ります（休憩へは下がる2音、作業へは上がる2音）。\n\n'
           'マリンバ、フルート、アコースティックギター、カリンバ、シンセ、ヴァイオリン。\n'
           '主役の楽器が違う曲を7曲ずつ入れ替えながら流します。休憩はグラスハープとタングドラムです。\n'
           '3時間のあいだ、同じ曲は二度出てきません。歌や人の声は入っていません。\n\n'
           '1回終わるごとに、外は少しずつ暗くなり、雪が積もっていきます。\n'
           'となりでは、ゴールデンレトリバーがこたつにもぐって眠っています。\n'
           '冬の勉強や受験の追い込み、読書や作業のおともにどうぞ。\n\n'
           '── 章 ──\n' + '\n'.join(ch_ja) + '\n\n' + tags_hash)
desc_en = ('Six rounds of 25 minutes of focus and 5 minutes of rest — a three-hour Pomodoro session.\n'
           'A winter afternoon at the kotatsu, studying until the snow settles outside the window.\n\n'
           'A countdown timer is shown in the upper right.\n'
           'Focus rounds play lo-fi beats; breaks switch to quiet, beatless music.\n'
           'A soft chime marks each change (two falling notes into a break, two rising notes back to focus).\n\n'
           'Marimba, flute, acoustic guitar, kalimba, synth and violin — the tracks rotate between different lead instruments.\n'
           'Breaks feature glass harp and tongue drum.\n'
           'No track repeats in the full three hours. No vocals.\n\n'
           'With each round, the sky grows darker and the snow piles up.\n'
           'Beside her, a golden retriever sleeps half under the kotatsu quilt.\n\n'
           '── Chapters ──\n' + '\n'.join(ch_en))

S = {'A': ('雪が降ってきた。あと4回。', '2回目の作業。窓の外に、今年はじめての雪。', 'It started snowing. Four rounds to go.'),
     'B': ('単語カード、もう1周だけ。', '手元の単語カードをめくる。奥の窓では、雪が降りつづける。', 'One more round of flashcards.'),
     'C': ('勉強の横で、ずっと寝てる。', 'こたつのそばで丸くなって眠る相棒。ランプの灯りがあたたかい。', 'Fast asleep right beside my study desk.'),
     'D': ('2杯目と、最後の25分。', '外はすっかり雪の夜。2杯目のお茶をいれて、最後の作業。', 'A second cup, and the last 25 minutes.')}
short = {t: f'【タイトル】\n{a}❄️ ポモドーロ #shorts\n\n【説明】\n{b}\n{c}\n\n冬の勉強用BGM（ポモドーロ 25分×6・3時間）の本編は、関連動画からどうぞ。\n\n#勉強用BGM #ポモドーロ #shorts\n\n【関連動画】本編 IRO25 を公開後に設定'
         for t, (a, b, c) in S.items()}

files = {
    '01_タイトル_日本語.txt': title_ja,
    '02_タイトル_英語.txt': title_en,
    '03_章立て_日本語.txt': '\n'.join(ch_ja),
    '04_章立て_英語.txt': '\n'.join(ch_en),
    '05_説明文_日本語.txt': desc_ja,
    '06_説明文_英語.txt': desc_en,
    '07_ハッシュタグ.txt': tags_hash,
    '08_タグ.txt': '勉強用BGM, 作業用BGM, 集中BGM, ポモドーロ, ポモドーロタイマー, タイマー付き, 3時間, Lo-fi, ローファイ, 冬, 雪, こたつ, 受験勉強, 犬, ゴールデンレトリバー, pomodoro timer, pomodoro 25/5, study timer, 3 hour timer, study with me, lofi study, winter lofi, focus music, IRO Sounds',
    '09_再生リスト_タイトル.txt': '📚 Study / Focus｜勉強・作業用BGM（既存）',
    '10_英語ローカライズ_説明文.txt': title_en + '\n\n' + desc_en,
    '13_ショートA_雪の窓.txt': short['A'], '14_ショートB_単語カード.txt': short['B'], '15_ショートC_犬.txt': short['C'], '16_ショートD_2杯目.txt': short['D'],
}
files['00_説明文_これを貼る.txt'] = desc_ja + '\n\n── English ──\n\n' + desc_en
files['00_使い方.txt'] = ('本人の通し視聴の後に予約する。本編・ショート4本・サムネ（本編用と、ショート1本ずつの縦）は Mac の 投稿用 フォルダ。\n'
                        'IRO Sounds の既定説明文を残し、その上に 00 の本文を挿入（日本語→英語）。\n再生リストは 09（既存）。公開は12月上旬の10時・ショートは本編の翌日以降の12時／21時。\n'
                        'IRO の公開は本編＋ショートで1日3本まで・ショートは1日2本まで。予約前にその日の IRO Sounds の本数を合算して照合する。')
for k, v in files.items():
    (KIT / k).write_text(v + '\n')
    if MAC.exists(): shutil.copy2(KIT / k, MAC / k)
print(len(files), '件', '題', len(title_ja), len(title_en), '字'); print('\n'.join(ch_ja))
