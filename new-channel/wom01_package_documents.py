# English-primary v02 entry point. The legacy v01 path below remains available.
import os as _wom_os
if _wom_os.environ.get('WOM_MULTILINGUAL') == '1':
    from wom01_multilingual_documents import main as _wom_main
    _wom_main()
    raise SystemExit(0)

"""Create the source-linked script, rights register and reviewable handoff."""
import json, hashlib, csv
from pathlib import Path
import os

R=Path(os.environ['WOM_EPISODE_ROOT']).expanduser().resolve()
D=R/'deliverables'
C=json.loads((R/'records/content.json').read_text())
T=json.loads((R/'records/narration_timeline.json').read_text())
A=json.loads((R/'records/museum_assets.json').read_text())
S={s['id']:s for s in C['sources']}
times={s['id']:s for s in T['segments']}
def ts(v):
    n=int(v);return f'{n//60:02}:{n%60:02}'
classes={'historical_fact':'史料・博物館解説に基づく記述','myth_variant':'信仰・図像の内容（現実の出来事としては扱わない）','scholarly_interpretation':'博物館の解釈・不確実性を明示','editorial_question':'編集上の問い','production_method':'制作上の説明','editorial_interpretation':'編集上の読み解き','editorial_summary':'史料に基づく編集上のまとめ','production_disclosure':'制作方法の開示'}
lines=['# EP001 アヌビス：出典付き完成台本','',f'尺：{ts(T["duration_seconds"])}／日本語／ナレーション：{C["voice_credit"]}','', 'この台本は実際に生成したナレーションと対応する。言語と声は試作用の選択。時刻は生成音声の文単位の境界に基づく。歴史・宗教の紹介であり、死後世界の実在を主張しない。','']
chapter=None
for seg in C['segments']:
    if chapter!=seg['chapter']:
        chapter=seg['chapter'];name=next(x['title'] for x in C['chapters'] if x['id']==chapter)
        lines.extend([f'## {ts(times[seg["id"]]["start"])} {name}',''])
    lines.extend([f'### {seg["id"]} {seg["heading"]}', '',f'区分：{classes[seg["classification"]]}。画面：{", ".join(seg["visuals"])}。','',seg['text'],''])
    if seg['sources']:
        lines.append('根拠：'+'、'.join(f'[{sid}: {S[sid]["title"]}]({S[sid]["url"]})' for sid in seg['sources'])+'。')
        for sid in seg['sources']:lines.append(f'- {sid} 確認位置：{S[sid]["locator"]}')
    else:lines.append('根拠：制作記録または編集上の説明。新たな歴史的事実の断定は含めない。')
    lines.append('')
lines.extend(['## 説明上の注意','', '- N04の「見張っているよう」は姿からの編集上の印象。墓地との関係はN05で博物館の解釈と区別した。','- N07・N10・N20・N25・N27・N28の説明には、出典に基づく事実と編集上の読み解きが含まれる。全語句が史料の直訳ではない。','- N16／MET 557830は現代の紙上の模写。カタログの古代の年代は原壁画の年代で、模写の制作年としない。','- N06／MET 590939とN24／MET 547871は神の同定に留保がある。確定的な名称に変更しない。','- マアトは資料によって羽根や女神像で表される。図解は説明用の概念図。','- N09／ネジェムアンクの棺は2019年に盗掘品としてエジプトへ返還済み（S12）。Metの現所蔵品として紹介しない。棺の画像は使っていない。','- N26は、N03と内容が重なるためv02で削除（IDは音声キャッシュのため詰めない）。','- アメミト、ナウニ、ナクトアメン、イミウト、ネジェムアンク等の読みは公開前に通しで聴いて確認する。','', '確認日：2026-10-15。主な根拠はMetの収蔵品・学芸解説であり、主要な役割はKelsey Museumの公式解説でも補足照合した（records/補足照合.md）。個別作品の年代・同定の別機関照合は未完了。専門家による査読済みとは表示しない。',''])
(D/'EP001_出典付き台本.md').write_text('\n'.join(lines))

g=json.loads((R/'records/generated_assets.json').read_text())
for item in g:item['sha256']=hashlib.sha256((R/item['path']).read_bytes()).hexdigest()
(R/'records/generated_assets.json').write_text(json.dumps(g,ensure_ascii=False,indent=2)+'\n')
rights=['# 素材・出典・利用条件台帳','', '確認日：2026-10-15。素材の実際の使用は本編とサムネイルの範囲。権利判断の根拠を保存した制作台帳であり、第三者による法務審査ではない。','', '## 博物館の画像','', '[Met Open Access方針](https://www.metmuseum.org/hubs/open-access)に基づき、公式APIで `isPublicDomain=true` の画像のみ採用。全10点はCC0。トリミング・明暗調整・枠組みを行った。原寸画像・APIメタデータ・取得先URL・SHA-256を `records/museum_assets.json` と `records/met_*.json` に保存。','']
for a in A:
    rights.extend([f'### MET-{a["object_id"]}: {a["title"]}','',f'- 作品番号：{a["object_number"]}／年代表示：{a["object_date"]}',f'- 所蔵：The Metropolitan Museum of Art。利用条件：{a["license"]}',f'- クレジット：{a["credit_line"]}',f'- 作品ページ：[公式カタログ]({a["url"]})',f'- ファイル：`{a["file"]}`',''])
rights.extend(['MET 557830の年代表示は原壁画を指す。使用画像はNina de Garis Daviesによる紙上の模写。作品の確実な同定がない場合は、その留保を本編にも反映した。','', '## AI再現画・図解・音楽','', '- AI再現画4枚はこの作品用に生成。歴史的な証拠として用いない。プロンプトと元画像のハッシュは `records/generated_assets.json`。追加の有料API呼び出しや契約は行っていない。','- 図解6枚と画面の組版は制作スクリプトによるオリジナル。実物画像に文字を描き足した擬似史料は作っていない。','- BGMは `new-channel/wom01_render_episode.py` で合成したオリジナルの静かな音。SunoやDistroKidの既存楽曲・原盤は使用していない。古代音楽の復元ではない。','- AI出力の権利の独占性やContent ID適格性は保証しない。今回の音・画像をContent IDに登録する作業は実施していない。','- システムの日本語フォントで文字を画像・字幕に焼き込み。フォントファイルを納品・再配布していない。','', '## 音声','', '- 使用音声：**VOICEVOX:雀松朱司**。声の利用条件に商用・非商用利用とクレジット条件を確認。動画末尾・概要欄案・制作台帳に記載。','- [VOICEVOX利用規約](https://voicevox.hiroshiba.jp/term/)／[VirVox ProjectのVOICEVOXキャラクター利用規約](https://www.virvoxproject.com/voicevox%E3%81%AE%E5%88%A9%E7%94%A8%E8%A6%8F%E7%B4%84)','- ナレーションはローカルの公式VOICEVOX Coreと音声モデルで生成。利用条件・モデル情報は `records/voice_license.json` と `records/narration_timeline.json`。','- 実在人物の声の模倣・クローン音声は使っていない。歴史の紹介を目的とし、信仰への勧誘・否定を目的にしていない。','', '## 公開前に残る確認','', '- 人による全編視聴、読みと音声の聞き取り、史料と画面の対応を確認する。','- チャンネル言語・声・名称と公開方針を決める。','- [YouTubeのAI使用開示方針](https://support.google.com/youtube/answer/14328491?hl=ja)とアップロード画面の質問を確認し、該当する開示を設定する。説明欄だけで設定を代替しない。',''])
(D/'EP001_素材と権利台帳.md').write_text('\n'.join(rights))

chap=[]
for ch in C['chapters']:
    seg=next(s for s in T['segments'] if s['chapter']==ch['id']);chap.append(f'{ts(seg["start"])} {ch["title"]}')
desc=['# 投稿用情報（下書き・未投稿）','', '## タイトル','', C['title'],'','## 概要欄案（ここからコピー）','', '犬科の頭を持つ古代エジプトの神アヌビス。心臓を量る姿だけでなく、墓や身体を守る役割を、メトロポリタン美術館の公開資料から読み解きます。','', '博物館資料の写真、現代の壁画模写、説明用の図解、AIによる再現画を区別して紹介しています。神話・宗教的信仰の内容を、現実に起きた出来事として断定するものではありません。','', 'ナレーション：VOICEVOX:雀松朱司','制作：台本・編集・一部の再現画にAIを使用。音楽は本作品用のオリジナル合成音。','', 'チャプター',*chap,'', '参考資料：The Metropolitan Museum of Art（公式カタログ・学芸解説）']
for s in C['sources']:desc.extend([f'{s["id"]} {s["title"]}',s['url']])
desc.extend(['', '画像：The Metropolitan Museum of Art, Open Access / CC0。使用作品ID：'+', '.join(str(a['object_id']) for a in A), 'https://www.metmuseum.org/hubs/open-access','', '主な注意：MET 557830はNina de Garis Daviesによる壁画の模写。MET 590939、547871の神の同定には不確実性があります。','', '#古代エジプト #アヌビス #神話','', '## 投稿画面での確認メモ','', '- 公開状態、日時、チャンネルIDは未設定。アップロード・予約・新チャンネル開設は行っていない。','- 概要欄のAI説明に加え、YouTube Studioの「AIの使用」（表記は画面による）の質問を確認する。史実の実写と誤認され得る再現画があるため、今回の試作では開示する運用を推奨。','- 字幕焼き込み版を納品。SRTを追加する場合、表示の重なりとCCボタンの挙動をプレビューで確認する。','- サムネイルは1920×1080のJPEG。文字と史料画像の識別は縮小画像でも確認済み。','- 公開前に通しで試聴し、固有名詞の読み、声、章のつながりを確定する。',''])
(D/'EP001_投稿用情報.md').write_text('\n'.join(desc))

with (R/'records/claims.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['segment_id','start_seconds','classification','sources','source_locations','claim_text','review_status'])
    for s in C['segments']:
        writer.writerow([s['id'],round(times[s['id']]['start'],3),s['classification'],';'.join(s['sources']),';'.join(S[x]['locator'] for x in s['sources']),s['text'],'source-linked; independent expert review not completed'])
print('Documents packaged')
