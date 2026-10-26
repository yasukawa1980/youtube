"""IRO21 の投稿文一式を作る（Claude 2026-10-26。IRO19 の 投稿文を作る.py を下敷きに、IRO20 の添削で決めた形にそろえた）。

章は 構成.json の出来事4種（A 街の灯り・B 犬へ微笑む・C あくび・D 見上げる）の全回。時刻は部品の頭＋動き出し（Kling 素材で実測）を秒へ切り捨て。
貼り付け用は iro/IRO21_遠回りして帰ろうか_貼り付け用/ と Mac の 投稿用/ に同じものを置く。
"""
import json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
KIT = ROOT / 'IRO21_遠回りして帰ろうか_貼り付け用'; KIT.mkdir(exist_ok=True)
MAC = Path('/Users/ryo/Desktop/BGM/IRO/Drive/21_遠回りして帰ろうか/投稿用')
data = json.loads(Path('/Volumes/ESD-02/IRO/IRO21_素材_ドライブ2時間/_映像作業/構成.json').read_text())
P, N, FPS = data['prefix_frames'], 192, 24
ONSET = {'A': 1.25, 'B': 1.25, 'C': 3.0, 'D': 1.42}  # 8秒の素材の中で動き出す秒（iro21 の Kling 素材を範囲の差で実測）


def ts(s):
    s = int(s); h, m, x = s // 3600, s % 3600 // 60, s % 60
    return f'{h}:{m:02d}:{x:02d}' if h else f'{m}:{x:02d}'


JA_KIND = {'A': '🌃 遠くの灯りに', 'B': '🐕 助手席に微笑んで', 'C': '🐕 大きなあくび', 'D': '🐕 まだ着かないの？'}
EN_KIND = {'A': '🌃 Lights across the bay', 'B': '🐕 A smile for the co-pilot', 'C': '🐕 One big yawn', 'D': '🐕 Are we there yet?'}
ev = [((P + i * N) / FPS + ONSET[s[-1]], s[-1]) for i, s in enumerate(data['parts']) if s not in ('B1', 'B2')]
ch_ja = ['0:00 はじまり'] + [f'{ts(t)} {JA_KIND[k]}' for t, k in ev]
ch_en = ['0:00 Beginning'] + [f'{ts(t)} {EN_KIND[k]}' for t, k in ev]

title_ja = '遠回りして、帰ろうか。｜夜のドライブBGM 2時間 ナイトドライブ・チル 作業用・リラックス'
title_en = 'Taking the Long Way Home | 2 Hours of Night Drive Chill Music'
assert len(title_ja) <= 100 and len(title_en) <= 100
tags_hash = '#ドライブBGM #夜ドライブ #ChillMusic'
desc_ja = ('湾の向こうに、街の灯り。助手席では、大きな犬がひと足先に夢の中。\n'
           'まっすぐ帰るには、まだ少し惜しい夜の2時間。\n\n'
           'ペダルスチール、クラリネット、スティールパン、フレットレスベース、オーボエ、ハモンドオルガン。\n'
           '6つの音色をゆったりしたビートでつなぐ、ナイトドライブ・チルです。\n\n'
           '夜のドライブや帰り道、静かな作業のおともに。タイマーのない時間を、あなたのペースで。\n\n' + tags_hash)
desc_en = ('City lights across the bay. In the passenger seat, a big golden retriever has already drifted off.\n'
           'Two hours for a night that is a little too nice to head straight home.\n\n'
           'Pedal steel, clarinet, steel pan, fretless bass, oboe and Hammond organ drift over an easy, unhurried groove.\n\n'
           'A quiet companion for night drives, the way home and calm work, without a timer.')

S = {'A': ('遠くの灯りに、ちょっと寄り道。', '運転の合間に、湾の向こうの灯りへちらり。まっすぐ帰るのは、もう少しあとで。', 'A quick look at the lights across the bay.'),
     'B': ('助手席の寝息を、聞きながら。', '隣で眠る大きな相棒に、そっと微笑んで。夜の道は、まだ続きます。', 'Driving on, with a sleepy co-pilot beside me.'),
     'C': ('助手席で、大きなあくび。', '揺れる車内で、眠る犬が大きなあくび。またすぐ、夢のつづきへ。', 'One big yawn from the passenger seat.'),
     'D': ('まだ着かないの？　おやすみ。', '目を開けて運転席を見上げたら、また顎を前足に。おやすみ。', 'Are we there yet? Never mind, back to sleep.')}
short = {t: f'{a}🚗 ドライブBGM #shorts\n\n{b}\n{c}\n\n2時間の本編は、関連動画からどうぞ。\n\n#ドライブBGM #夜ドライブ #shorts' for t, (a, b, c) in S.items()}

files = {
    '01_タイトル_日本語.txt': title_ja,
    '02_タイトル_英語.txt': title_en,
    '05_説明文_日本語.txt': desc_ja + '\n\n── 動くところ ──\n' + '\n'.join(ch_ja),
    '06_説明文_英語.txt': desc_en,
    '07_ハッシュタグ.txt': tags_hash,
    '08_タグ.txt': 'ドライブBGM,夜ドライブ,ナイトドライブ,チルBGM,作業用BGM,リラックスBGM,夜BGM,秋BGM,night drive music,chill music,lofi drive,relaxing instrumental,IRO Sounds',
    '09_再生リスト_タイトル.txt': '🚗 Drive｜ドライブBGM\n🌙 Relax / Night｜夜・リラックスBGM',
    '10_英語ローカライズ_説明文.txt': title_en + '\n\n' + desc_en + '\n\n── When they move ──\n' + '\n'.join(ch_en),
    '11_チャプター.txt': '\n'.join(ch_ja) + '\n\n' + '\n'.join(ch_en),
    '13_ショートA.txt': short['A'], '14_ショートB.txt': short['B'], '15_ショートC.txt': short['C'], '16_ショートD.txt': short['D'],
}
files['00_説明文_これを貼る.txt'] = files['05_説明文_日本語.txt'] + '\n\n── English ──\n\n' + desc_en + '\n\n── When they move ──\n' + '\n'.join(ch_en)
files['00_使い方.txt'] = ('未投稿。本人の通し視聴の後に投稿・予約。\n本編・ショート4本・サムネ（本編用と、ショート4本共通の縦）は Mac の 投稿用 フォルダ。\n'
                        'IRO Sounds の既定説明文を残し、その上に 00 の本文を挿入（日本語→英語）。\n再生リストは 09 の2つ。本編は10時公開・ショートは21時（10/18〜の方針）。\n'
                        'IRO の公開は本編＋ショートで1日3本まで・ショートは1日2本まで。')
for k, v in files.items():
    (KIT / k).write_text(v + '\n')
    if MAC.exists(): shutil.copy2(KIT / k, MAC / k)
print(len(files), '件', '章', len(ch_ja), '件', '題', len(title_ja), len(title_en), '字')
