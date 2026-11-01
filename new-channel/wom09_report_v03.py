"""Publish compact v03 evidence and handoff after verified Draft storage."""
from wom09_revision_v03 import BASE
from wom09_produce import ROOT,REPO,read
from pathlib import Path
import shutil

def main():
 q=read(ROOT/'records/qc_v03.json');r=read(ROOT/'records/revision_qc_v03.json');c=read(ROOT/'records/continuous_qc.json');l=read(ROOT/'records/summary_layout_v03.json');s=read(ROOT/'records/sharing.json');fp=read(ROOT/'records/final_pixel_comparison_v03.json')
 assert all(x['passed'] for x in [q,r,c,l,read(ROOT/'records/final_video_motion.json'),read(ROOT/'records/subtitle_layout_validation.json')])
 assert fp['comparison_complete']
 assert s['draft'] and s['status']=='verified' and len(s['assets'])==7
 folder=REPO/'new-channel/wom09_確認版_v03_20261101'
 for name in ['records','確認画像']:(folder/name).mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'records').iterdir():
  if p.suffix in ['.json','.txt','.log']:shutil.copy2(p,folder/'records'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.csv','.txt']:shutil.copy2(p,folder/p.name)
 for pattern in ['D_summary_v03*.jpg','compare_*.jpg','continuous_*_sheet_*.jpg','opening_*.jpg']:
  for p in (ROOT/'review').glob(pattern):shutil.copy2(p,folder/'確認画像'/p.name)
 (folder/'SHA256SUMS_shared.txt').write_text(''.join(a['sha256']+'  '+a['name']+'\n' for a in s['assets']))
 text=f'''# Quiet Origins 第9話 確認版v03（2026-11-01）

**D_summary（P13前半）1枚の修正を完了。全4箱の文字が枠内に収まり、余白は最小27px。新しい未公開Draftの7資産をREST再取得して照合済み。最終再圧縮の画素差24フレームは下記のとおり。本人の試聴・サムネ選択待ち。**

指示：[Claude修正依頼v03](../wom09_修正依頼_v03_20261101.md)、[Claudeのv02確認](../wom09_Claude確認_v02_20261101.md)。元はv02 Release `430613430`。前回の検査に箱内の余白測定が欠けていたため、今回は文字の外接矩形から線の内側までの距離を全4箱で検査した。

## 変更した画面と実測値

- D_summaryだけを変更。英語60→**48px**、日本語**35px**。単語の途中で切らず、文字内容は空白・改行を除いて一致。
- 4箱は各396px幅、全体x=48〜1872、y=184〜624。全体の中点 **y=404**。線幅3pxを除いた内側の矩形から文字の外接矩形までの距離を測定。
- 地 #e8d9b7、本文 #3b2c21、強調 #5a3a1aを維持。コントラスト比は本文 **{l['body_contrast']:.3f}**、強調 **{l['accent_contrast']:.3f}**（どちらも4.5以上）。

| 箱 | 文字の外接矩形 x0,y0,x1,y1 | 左余白 | 上余白 | 右余白 | 下余白 |
|---|---|---:|---:|---:|---:|
'''
 for b in l['boxes']:
  g=b['gaps_px'];text+=f"|{b['index']}|{', '.join(map(str,b['text_bbox']))}|{g['left']}px|{g['top']}px|{g['right']}px|{g['bottom']}px|\n"
 text+='\n全方向24px以上。各行の文字矩形と線の座標は [summary_layout_v03.json](records/summary_layout_v03.json)、表は [CSV](EP009_summary_clearance_v03.csv)。\n\n| 矢印 | 長さ | 左の箱とのすき間 | 右の箱とのすき間 |\n|---|---:|---:|---:|\n'
 for a in l['arrows']:text+=f"|{a['index']}|{a['length_px']}px|{a['left_gap_px']}px|{a['right_gap_px']}px|\n"
 text+=f'''
[同時刻のv02／v03比較（315.133秒・frame9454）](確認画像/compare_D_summary_v02_v03.jpg)／[v03完成動画からの拡大確認](確認画像/D_summary_v03_final.jpg)。両方とも先頭から連続デコードして同じ絶対フレームを抽出した。

## 維持した内容と検査

- その他**23ショットのエンコーダー入力がv02とバイト単位で一致**。同じ入力を全フレームデコードしてフレームハッシュを記録し、共通エンコーダーへ渡す画素がすべて同じであることを確認。素材画像21枚、段階表示画像、共通OP/ENDも同一。D_summaryの上部110pxの札も画素一致。
- 最終MP4同士も全11,293フレームをフル解像度yuv420pでデコードして比較。**22ショットは完成動画でも全画素一致**。D_countの末尾24フレーム（306.800〜307.600秒）だけ圧縮由来の微差が残る。D_countの入力画素は全一致で、素材や配置は変えていない。変更前からある307.467秒のキーフレームがD_summaryへの切り替え4フレーム前にあり、この切り替え付近で圧縮の先読みが影響したと考えられる。
- **完成MP4でD_summary以外の全画素が完全一致する条件は未達**。元依頼の「非圧縮フレームを1つのエンコーダーへ渡す」「H.264 High」の工程を維持した。差は8bit輝度の平均 **{fp['compression_difference']['luma_mean_absolute_difference_8bit']:.8f}**、最大 **{fp['compression_difference']['luma_max_absolute_difference_8bit']}**、変更画素比 **{fp['compression_difference']['luma_changed_sample_fraction']*100:.6f}%**。英日本編の映像ストリームは同じ。Claudeの再確認項目として残す。詳細：[最終動画の画素比較](records/final_pixel_comparison_v03.json)／[D_count 307.500秒の比較画像](確認画像/compare_compression_D_count.jpg)（この補足画像のみ正確な時刻へのシークで抽出、全画素検査と主比較は連続デコード）。
- **英日WAV・M4A・SRTはv02とSHA-256一致**。4動画に入っている音声ストリームもv02と一致。再合成・再ミックスなし。
- 376.433333秒、11,293フレーム、24ショット。全ショットの開始・終了・フレーム数、段階表示の時刻はv02と一致。文面・字幕内容・色・サムネA/Bは維持。
- 全ショットを個別にデコードし、非圧縮フレームを1つのエンコーダーへ入力。全編 **H.264 High / yuv420p / 1920×1080 / 30fps CFR**。
- 英日本編の全11,293フレームで形式1種類、SPS profile_idc=100のみ。4動画すべてを先頭から末尾までデコードし、エラー・警告0。英日それぞれ全24ショットの先頭・中央・末尾72枚を連続デコードから抽出し、一覧画像に保存。
- 英日本編の映像ストリーム一致。動く12ショットのp95÷中央値は2.5以下。静止カードは指定の段階表示時刻以外の入力画素差分0。
- 字幕全ページを標準・拡大の2サイズで描画して非重複を確認。音声は英日とも−16.00 LUFS、英−3.96 / 日−5.16 dBTP。
- v02の配布ファイル全件を開始前のSHA-256と照合し、変更なし。v01も書き換えていない。

詳細：[revision_qc_v03.json](records/revision_qc_v03.json)、[動画検査](records/qc_v03.json)、[連続デコード検査](records/continuous_qc.json)、[目視確認記録](records/visual_review_v03.json)。

## 保存・共有

本人指定の **SSD ESD-02** に新規保存：`{ROOT}/`。Macの空き容量不足のため保存先を確認し、本人がESD-02を選択した。既存v01・v02は移動していない。

[未公開Draft Release]({s['release_url']})、ID **{s['release_id']}**。公開リポジトリ上の未公開Draftで、Release・全資産の匿名アクセス404を確認。7資産のサイズ・SHA-256がREST再取得で全件一致。

- `EP009_TrojanHorse_{{en,ja}}_v03_1080p30.mp4`：英日字幕なし本編。
- `EP009_TrojanHorse_{{en,ja}}_v03_subtitled_review_1080p30.mp4`：英日字幕付き確認版。
- `EP009_audio_and_subtitles_v03.zip`：英日音声・SRT・既存の発音確認抜粋。
- `EP009_thumbnails_and_metadata_v03.zip`：既存サムネA/B・投稿情報・検査CSV。
- `EP009_QA_records_v03.zip`：比較・一覧画像・検査記録。

取得ID・ハッシュ：[sharing.json](records/sharing.json)。必要なら `gh api repos/yasukawa1980/youtube/releases/{s['release_id']}` からasset IDを確認し、`gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE` で取得できる。

本人による全編試聴は未了。音声はv01/v02と同一。サムネはClaudeがAを推奨、本人の最終選択待ち。公開・YouTube投稿・予約はしていない。
'''
 (folder/'README.md').write_text(text)
 result=text.replace('(../wom09_','(wom09_').replace('(records/','(wom09_確認版_v03_20261101/records/').replace('(確認画像/','(wom09_確認版_v03_20261101/確認画像/').replace('(EP009_','(wom09_確認版_v03_20261101/EP009_')
 (REPO/'new-channel/wom09_制作結果_v03_20261101.md').write_text(result)
 h=REPO/'new-channel/Claude引き継ぎ_次のセッション.md';t=h.read_text();mark='## 2026-11-01 Codex追記（第9話D_summary修正版v03作成・圧縮差の確認待ち）'
 if mark not in t:
  first,rest=t.split('\n',1);h.write_text(first+'\n\n'+f'''{mark}

- [制作結果v03](wom09_制作結果_v03_20261101.md)／[同時刻比較・取得案内](wom09_確認版_v03_20261101/README.md)。D_summaryだけ修正、英語48px、箱内最小余白27px、矢印40px・両側20px、全体中心y=404。その他23ショットは入力画素一致。最終MP4では22ショットが全画素一致、D_count末尾24フレームだけ圧縮由来の微差あり（完成MP4の全画素一致条件は未達・要Claude確認）。音声・SRT・時刻もv02と同一。
- [未公開Draft]({s['release_url']})、Release `{s['release_id']}`。7資産をREST再取得照合、匿名404・Draft維持。英日形式1種類、4動画の連続デコード警告0、各24ショットの一覧画像あり。
- 本人指定のESD-02へv03新規保存。v01/v02は移動・変更なし。次はClaudeの箱内余白確認、本人の全編試聴とサムネ選択（ClaudeはA推奨）。公開・投稿なし。

'''+rest.lstrip())
 print('V03 REPORT',folder,flush=True)
if __name__=='__main__':main()
