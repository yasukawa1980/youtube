"""IRO22 の投稿文一式を作る（Claude 2026-10-27。IRO21 の 投稿文を作る.py の形に、IRO14 のポモドーロの文面を合わせた）。

章は作業と休憩の切り替わり8か所（IRO14 と同じ）。時刻は扉ムービーの分（長さ＋間）を足して、秒を切り上げる（切り替わりより前に章が始まらないように）。
貼り付け用は iro/IRO22_日が暮れるまで集中する_貼り付け用/ と Mac の 投稿用/ に同じものを置く。
"""
import math, shutil, importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT / 'IRO22_日が暮れるまで集中する_貼り付け用'; KIT.mkdir(exist_ok=True)
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Study/22_日が暮れるまで集中する/投稿用')
spec = importlib.util.spec_from_file_location('door', ROOT.parent / 'bgm/IRO/irokit/扉ムービーを入れる.py'); door = importlib.util.module_from_spec(spec); spec.loader.exec_module(door)
SHIFT = door.dur(door.MOVIE) + door.BREATH        # 本編の 0秒（25:00 が動き出す所）が扉入りで何秒目か
FOCUS, BREAK = 1500, 300


def ts(s):
    s = int(math.ceil(s)); h, m, x = s // 3600, s % 3600 // 60, s % 60
    return f'{h}:{m:02d}:{x:02d}' if h else f'{m}:{x:02d}'


ch_ja, ch_en = [], []
for b in range(4):
    t = SHIFT + b * (FOCUS + BREAK)
    ch_ja += [f'{"0:00" if b == 0 else ts(t)} 作業 {b + 1}／4', f'{ts(t + FOCUS)} 休憩 {b + 1}']
    ch_en += [f'{"0:00" if b == 0 else ts(t)} Focus {b + 1}/4', f'{ts(t + FOCUS)} Break {b + 1}']

title_ja = '日が暮れるまで、集中する。｜ポモドーロタイマー 2時間 25分×4 勉強用BGM 夕方 Lo-fi'
title_en = 'Focus Until Sundown | Pomodoro Timer 2 Hours 25/5 ×4 Study Lo-fi'
assert len(title_ja) <= 100 and len(title_en) <= 100
tags_hash = '#勉強用BGM #作業用BGM #集中BGM'
desc_ja = ('25分の作業と5分の休憩を4回。2時間ぶんのポモドーロです。\n\n'
           '画面の左上に残り時間を出しています。\n'
           '作業の25分はやわらかいビートのLo-fi、休憩の5分はビートのない静かな曲に変わります。\n'
           '切り替わりには小さなチャイムが鳴ります（休憩へは下がる2音、作業へは上がる2音）。\n\n'
           'ローズ（電気ピアノ）、ジャズギター、フリューゲルホルン、チェンバロ、ウッドベース、メロディカ。\n'
           '主役の楽器が違う曲を入れ替えながら流します。休憩はライアーとシンギングボウル。\n'
           '2時間のあいだ、同じ曲は二度出てきません。歌や人の声は入っていません。\n\n'
           '晩秋の夕方、窓辺の机でノートに向かう女性と、足元で眠るゴールデンレトリバー。\n'
           '休憩になると、大きく伸びをして、眠る相棒をひと撫で。\n'
           '窓の外はゆっくり日が暮れていき、最後の休憩のころには机のランプが灯ります。\n\n'
           '── 章 ──\n' + '\n'.join(ch_ja) + '\n\n' + tags_hash)
desc_en = ('Four rounds of 25 minutes of focus and 5 minutes of rest — a 2-hour Pomodoro session for a late-autumn afternoon.\n\n'
           'A countdown timer sits in the top-left corner of the screen.\n'
           'The 25-minute focus blocks are soft lo-fi beats; the 5-minute breaks switch to quiet, beatless music.\n'
           'A soft chime marks each change (two falling notes into a break, two rising notes back to focus).\n\n'
           'Rhodes electric piano, jazz guitar, flugelhorn, harpsichord, upright bass and melodica —\n'
           'the blocks rotate tracks led by different instruments. The breaks are lyre and singing bowls.\n'
           'No track repeats in the full two hours. No vocals.\n\n'
           'By a window desk, a woman works through her notes while a golden retriever sleeps at her feet.\n'
           'When the break comes, she stretches and gives her sleepy friend a gentle pat.\n'
           'Outside, the sun slowly sets, and by the last break her desk lamp is glowing.\n\n'
           '── Chapters ──\n' + '\n'.join(ch_en))

S = {'A': ('西日の中で、のびをひとつ。', '休憩のチャイムが鳴ったら、西日の窓辺で両腕をうんと伸ばして。', 'A big stretch in the afternoon sun.'),
     'B': ('休憩の合図は、この手のひら。', '休憩のあいだに、足元で眠る相棒をそっとひと撫で。犬は寝たまま、うれしそう。', 'Break time means a gentle pat for my sleepy friend.'),
     'C': ('冷めないうちに、ひと口。', 'ノートから顔を上げて、マグからひと口。また、もうひと頑張り。', 'One sip before it gets cold.'),
     'D': ('夕焼けにつられて、大あくび。', '夕日の差す敷物の上で、眠る犬が大きなあくび。またすぐ、夢のつづきへ。', 'One big yawn in the sunset glow.')}
short = {t: f'【タイトル】\n{a}📚 勉強用BGM #shorts\n\n【説明】\n{b}\n{c}\n\n25分×4のポモドーロ（2時間）の本編は、関連動画からどうぞ。\n\n#勉強用BGM #ポモドーロ #shorts\n\n【関連動画】本編 IRO22 を公開後に設定'
         for t, (a, b, c) in S.items()}

files = {
    '01_タイトル_日本語.txt': title_ja,
    '02_タイトル_英語.txt': title_en,
    '05_説明文_日本語.txt': desc_ja,
    '06_説明文_英語.txt': desc_en,
    '07_ハッシュタグ.txt': tags_hash,
    '08_タグ.txt': '勉強用BGM, 作業用BGM, 集中BGM, ポモドーロ, ポモドーロタイマー, ポモドーロタイマー 2時間, タイマー付き, 2時間, 夕方, Lo-fi, ローファイ, study music, pomodoro, pomodoro timer, pomodoro 2 hours, focus music, study with me, lofi study, 2 hours, IRO Sounds',
    '09_再生リスト_タイトル.txt': '📚 Study / Focus｜勉強・作業用BGM',
    '10_英語ローカライズ_説明文.txt': title_en + '\n\n' + desc_en,
    '11_チャプター.txt': '\n'.join(ch_ja) + '\n\n' + '\n'.join(ch_en),
    '13_ショートA_伸び.txt': short['A'], '14_ショートB_撫でる.txt': short['B'], '15_ショートC_ひと口.txt': short['C'], '16_ショートD_あくび.txt': short['D'],
}
files['00_説明文_これを貼る.txt'] = desc_ja + '\n\n── English ──\n\n' + desc_en
files['00_使い方.txt'] = ('本人の通し視聴の後に予約する。本編・ショート4本・サムネ（本編用と、ショート4本共通の縦）は Mac の 投稿用 フォルダ。\n'
                        'IRO Sounds の既定説明文を残し、その上に 00 の本文を挿入（日本語→英語）。\n再生リストは 09（既存）。本編は10時公開・ショートは12時／21時（10/25〜の方針）。\n'
                        'IRO の公開は本編＋ショートで1日3本まで・ショートは1日2本まで。')
for k, v in files.items():
    (KIT / k).write_text(v + '\n')
    if MAC.exists(): shutil.copy2(KIT / k, MAC / k)
print(len(files), '件', '題', len(title_ja), len(title_en), '字'); print('\n'.join(ch_ja))
