"""Publish review records in the repository after verified private draft upload."""
import shutil,csv
from pathlib import Path
from wom_shorts_remake_v02 import ROOT,read,save
REPO=Path(__file__).resolve().parent.parent
def main():
 share=read(ROOT/'records/github_draft_release.json');assert share['status']=='verified' and len(share['assets'])==6
 qc={r['id']:r for r in read(ROOT/'records/final_qc.json')};motion=read(ROOT/'records/final_pixel_motion.json');assert motion['passed']
 target=REPO/'new-channel/research/wom_ショート作り直し_v02_20261102';target.mkdir(exist_ok=True,parents=True)
 for p in ROOT.glob('records/*.json'):shutil.copy2(p,target/p.name)
 photos=REPO/'new-channel/サムネ確認用/shorts_remake_v02';photos.mkdir(exist_ok=True,parents=True)
 for p in ROOT.glob('review/*.jpg'):shutil.copy2(p,photos/p.name)
 rows=[dict(id=sid,**r) for sid in ['A1R','M1R','P1R','T1R','A3R'] for r in qc[sid]['caption_rows']]
 with (target/'caption_rows.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 text='''# 旧型ショート5本 v02 修正結果

2026-11-02制作開始、11-03完了。5本ともClaude確認・本人試聴待ち。A1Rは先行コミット `fce63d1` で共有済み、その完成MP4は変更していない。

台本・音声・話速・尺はv01から変更なし。5本すべて音声ストリームSHA256一致。P1Rは本人許可済み24.733333秒・49語を維持し、41語短縮案は使用していない。YouTube投稿・予約は未実施。

## 取得

'''
 text+=f"[非公開Draft Release]({share['release_url']})、Release ID `{share['release_id']}`。5本のMP4と `remakes_review_v02.zip` の全6ファイルをRESTで再取得し、バイト数・SHA256一致、匿名取得404を確認。\n\n保存先：`{ROOT}/deliverables/`。\n\n"
 text+='''## 実測

| ID | 秒 | LUFS | dBTP | 最低字幕コントラスト | 動き p95/中央値の最大 |
|---|---:|---:|---:|---:|---:|
'''
 for sid in ['A1R','M1R','P1R','T1R','A3R']:
  r=qc[sid];mx=max(x['ratio'] for x in motion['checks'] if x['id']==sid and x['ratio'] is not None);text+=f"| {sid} | {r['video_duration']:.6f} | {r['audio']['input_i']} | {r['audio']['input_tp']} | {r['minimum_contrast']:.3f} | {mx:.3f} |\n"
 text+='''
全5本1080×1920・30fps・H.264 High・yuv420p。全編連続デコード警告0。案内は語りの後2.5秒、字高84px/56px、横圧縮なし。13素材・重複0・AI素材0。

動きは完成動画の全隣接フレームをグレースケールで比較し、各キーフレームの表示枠に共通する原典内部を固定領域として測定。字幕・案内・見出しの板を除外し、フレーム対の間引きや外れ値除外はしていない。静止カードは0/0になるので速度比の対象外。第9話と同じ実画素差の考え方で、全動素材2.5以下。

v01で使った原寸座標の速度は、拡大すると画面上の速度と対応が変わる。診断値として別に残し、合格判定には使用していない。測定の詳細は [final_pixel_motion.json](research/wom_ショート作り直し_v02_20261102/final_pixel_motion.json)。

## Claude指摘への対応

- 全字幕行の可視字高を52pxで統一。自然な幅のArial Narrow Boldを使用し、縦横比を変える圧縮なし。2行以内・x80〜880。台本完全一致。全行の先頭語・末尾語・字高・座標は [caption_rows.csv](research/wom_ショート作り直し_v02_20261102/caption_rows.csv)。
- M1R見出しを `MEDUSA WAS BORN A GORGON` に変更。カードは「The beautiful young woman」から。カード下端y1017、案内上端y1030、間隔13px。全段を保持。
- A1R：本編の参照矩形 `[2000,1250,3020,2220]` を基に、開始 `[2000,1250,3020,2097]` → 終了 `[2200,1325,2830,1848]`。「Anubis weighs.」で天秤とアヌビスを中央に。
- P1R：甕のふたを語句に合わせて中央付近へ。刊本A12は全頁から本編矩形 `[65,1133,987,1287]`、さらに `[360,1133,990,1287]` へ寄り、横へゆっくり移る。原典に見える綴りは辞書形pyxisそのものではなく **Pixide / Pixidem**。本編と同じ箇所の屈折形として示し、文字を書き足していない。
- T1R：舒明9年条を含む `[3900,700,6100,5000]` → 僧旻の `[4400,1400,5020,3350]` → 是天狗也の `[4570,3024,4988,3987]`。「It is a tengu」で該当語へ寄り、その後は記事へ緩やかに引く。画面上の速度が急変しない補間に変更。

矩形・原寸倍率・切替時刻は [visual_manifest.json](research/wom_ショート作り直し_v02_20261102/visual_manifest.json)。全素材1.6倍以下。指定語句時点の `*_final_cue_*.jpg` は完成MP4から抽出。`*_design.jpg` は描画前の設計確認画像で区別する。

## 確認画像

'''
 for sid in ['A1R','M1R','P1R','T1R','A3R']:text+=f"- {sid}：[全字幕ページ](サムネ確認用/shorts_remake_v02/{sid}_all_captions.jpg)／[2秒おき](サムネ確認用/shorts_remake_v02/{sid}_every2s.jpg)／[案内](サムネ確認用/shorts_remake_v02/{sid}_CTA.jpg)\n"
 text+='''
全字幕ページと指定語句の構図を目視点検済み。人による通し試聴・発音・語との同期確認は未実施。

## 投稿時の申し送り

M1Rの英語タイトルは本人了承済み **In the Oldest Stories, Medusa Was Born a Gorgon**。旧案 `The Oldest Medusa Story Has No Curse` は使わない。

依頼の予定：A1R 11/8、P1R 11/9、T1R 11/10、M1R 11/11、A3R 11/12、各18:00 JST。予約はしていない。第10話本編は11/8 09:00予定。同日の本編・ショート合算を投稿作業時に照合する。

関連動画：A1R/A3R `AanbRJfeGxo`、P1R `iZl_31zW2sU`、T1R `poT3TlC7iWI`、M1R `uUMStOFL-68`。旧版は保持する。
'''
 (REPO/'new-channel/wom_ショート作り直し結果_v02_20261102.md').write_text(text)
 print('SHORTS REPOSITORY REPORT COMPLETE',flush=True)
if __name__=='__main__':main()
