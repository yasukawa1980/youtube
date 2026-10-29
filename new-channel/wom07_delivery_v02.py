"""Package the verified single-shot revision and write its handoff."""
import argparse,shutil,zipfile
from pathlib import Path
from wom07_revision_v02 import ROOT,OLD,REPO,read,save,sha,A,B,TOTAL

def archive(name,entries):
 dst=ROOT/'deliverables'/name
 with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p,arc in entries:z.write(p,arc)
 with zipfile.ZipFile(dst) as z:assert z.testzip() is None
 return {'name':name,'path':str(dst),'bytes':dst.stat().st_size,'sha256':sha(dst),'entries':len(entries)}

def pack():
 assert read(ROOT/'records/qc_v02.json')['passed'] and read(ROOT/'records/map_motion_v02.json')['passed']
 d=ROOT/'deliverables';r=[]
 r.append(archive('EP007_v02_audio_and_subtitles.zip',[(p,p.name) for p in sorted(d.iterdir()) if p.suffix in ['.wav','.m4a','.srt','.txt']]))
 r.append(archive('EP007_v02_thumbnail_and_metadata.zip',[(p,p.name) for p in sorted(d.iterdir()) if p.suffix in ['.jpg','.md']]))
 evidence=[(p,str(p.relative_to(ROOT))) for folder in ['records','review'] for p in sorted((ROOT/folder).iterdir()) if p.suffix in ['.json','.jpg','.log']]
 evidence += [(p,'frame_hashes/'+p.name) for p in sorted((ROOT/'_work').glob('*.framemd5*')) if p.is_file()]
 r.append(archive('EP007_v02_QA_records.zip',evidence))
 source=Path(read(ROOT/'records/map_plan.json')['source']['local_original'])
 r.append(archive('EP007_v02_P05_map_review.zip',[(ROOT/'_work/P05_G11-01.mp4','P05_G11-01.mp4'),(source,'G11-01_original.jpg')]+[(p,p.name) for p in sorted((ROOT/'review').glob('P05_*.jpg'))]))
 save(ROOT/'records/release_archives_v02.json',r);print('PACKED',len(r),flush=True)

def handoff():
 s=read(ROOT/'records/sharing_v02.json');assert s['status']=='verified' and s['draft'];q=read(ROOT/'records/qc_v02.json');motion=read(ROOT/'records/map_motion_v02.json')['measurement'];plan=read(ROOT/'records/map_plan.json');assert q['passed']
 out=REPO/'new-channel/wom07_確認版_v02_20261029';out.mkdir(exist_ok=True)
 for folder in ['records','review']:
  dest=out/folder;dest.mkdir(exist_ok=True)
  for p in (ROOT/folder).iterdir():
   if p.suffix not in ['.json','.jpg']:continue
   if p.suffix=='.jpg':assert p.stat().st_size<=1000000
   shutil.copy2(p,dest/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.md','.srt','.txt','.jpg']:
   if p.suffix=='.md':(out/p.name).write_text(p.read_text().rstrip()+'\n')
   else:shutil.copy2(p,out/p.name)
 report=f'''# 第7話「最初の感謝祭」修正版v02（2026-10-29）

状態：依頼されたP05差し替えとサムネB確定を完了し、検査・非公開共有済み。次はClaudeのv02確認と、本人による公開日の決定。YouTube投稿・Release公開は行っていない。

## 本人決定と修正範囲

[Claudeの修正依頼](../wom07_修正依頼_v02_20261029.md)（共有コミット5bfdd51）にある本人回答「画風A」「試聴は大丈夫です」「サムネはおすすめで」を反映。このチャットの「今回の写実的な画風で採用する」と最新申し送りを合わせ、V01・V03・V04を維持し、P05のV02だけ地図G11-01へ差し替えた。

- P05：102.600000〜125.866667秒、フレーム3078〜3775の698枚。
- G11-01：John Smith, New England, **1624 state — facsimile c. 1919**。Boston Public Library, Leventhal Map & Education Center。
- 札：`MAP (FACSIMILE)｜地図（複製）`。スミスの肖像は表示範囲から除外。
- 地図上のPlimouthの中心（原画像正規化座標）：`{plan['plimouth_label_center_normalized']}`。語の範囲：`{plan['plimouth_word_bbox_normalized']}`。海岸線の範囲から地名へ寄り、終点で読めることを画像確認。
- 開始切り出し：`{plan['start_crop_normalized']}`、終点：`{plan['end_crop_normalized']}`。小数座標による連続ズーム。
- V02原動画は素材フォルダに保全し、本編で不使用。
- サムネは**B「NOT IN THE LETTER」**。v01案BとSHA-256一致。英日投稿情報と素材クレジットも更新。
- 本人試聴はOK。音声、BGM（共通A2・アメリカ1）、字幕はv01のまま。Kling追加生成・追加消費0、累計296クレジット。

## 実測検査

- 英日通常版・字幕付き確認版の**全4本**を先頭から連続デコード。エラー・警告0。
- 全4本でP05以外の**{q['unchanged_frames']:,}フレームがv01と画素一致**。変更はP05の**{q['changed_frames']}フレームのみ**。
- 音声ストリームは各v01とハッシュ一致。英日SRT・M4A・WAVもファイルSHA-256一致。読み・音量の再生成なし。
- 共通尺{q['duration_seconds']:.6f}秒、{TOTAL:,}フレーム、1920×1080・30fps固定、H.264 High / yuv420p。英日通常版の映像ストリーム同一。
- 全ファイルのSPSはprofile_idc=100のみ。差し替え区間と元動画のSPS/PPSはバイト単位で一致。両端がIDRであることを確認し、P05以外の圧縮パケットを保持した。これにより、ほかの場面の再圧縮差分を発生させない。
- 地図の動き：全697組の隣接フレームを測定。中央値{motion['median_mad_8bit']:.6f}、p95 {motion['p95_mad_8bit']:.6f}、**p95/中央値 {motion['p95_over_median']:.6f}**（基準2.5以下）。差分の除外なし。完成MP4のP05全フレームが測定クリップと画素一致。
- 英日それぞれP05の先頭・中央・末尾を連続デコードから取得し、地名・札・出典を確認。`review/P05_{{en,ja}}_continuous.jpg`。
- 素材は原典13点＋AI3点、すべて1回。OP・エンドカード・クレジット画面を含むほか20ショットもv01と一致。

## 非公開ファイルの取得

[Draft Release]({s['release_url']}) — **Release ID `{s['release_id']}`**。現行8資産と訂正前検査ZIP1件（計9件）をRelease IDからのRESTで再取得し、サイズ・SHA-256一致、匿名アクセス404を確認。

- `EP007_Thanksgiving_{{en,ja}}_v02_1080p30.mp4`：字幕焼き込みなしの英日本編。
- `EP007_Thanksgiving_{{en,ja}}_v02_subtitled_review_1080p30.mp4`：英日字幕付き確認版。
- `EP007_v02_audio_and_subtitles.zip`：v01と同じ英日音声、字幕、発音確認用抜粋。
- `EP007_v02_thumbnail_and_metadata.zip`：確定サムネB、英日投稿情報、出典。
- `EP007_v02_QA_records.zip`：検査記録・承認記録・確認画像。
- `EP007_v02_P05_map_review.zip`：P05単独映像、地図原画像、確認画像。

`EP007_v02_QA_records_original_snapshot.zip` はP05の画像ハッシュ訂正前の台帳を保全した履歴。現行の検査記録は `EP007_v02_QA_records.zip`。動画・音声の変更はない。

RESTのasset ID・SHA-256は`records/sharing_v02.json`。v01 Release `427386290` は制作時点の記録として保持。v01内の画風未承認・試聴待ちという記載は本v02の本人決定で更新されている。

Mac保存先：`{ROOT}/deliverables/`。
'''
 (out/'README.md').write_text(report)
 (REPO/'new-channel/wom07_制作結果_v02_20261029.md').write_text(report.replace('(../wom07_修正依頼_v02_20261029.md)','(wom07_修正依頼_v02_20261029.md)'))
 (REPO/'new-channel/wom07_制作進捗_20261029.md').write_text('# 第7話 制作進捗（2026-10-29）\n\n修正版v02のP05地図差し替え・サムネB確定・検査・非公開Draft共有を完了。本人の試聴OK、V01・V03・V04の写実的画風を採用。\n\n[制作結果v02](wom07_制作結果_v02_20261029.md)／[取得案内](wom07_確認版_v02_20261029/README.md)。次はClaudeのv02確認と公開日の決定。\n')
 print('HANDOFF COMPLETE',out,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['pack','handoff']);a=p.parse_args();globals()[a.stage]()
