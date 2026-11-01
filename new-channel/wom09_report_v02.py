"""Save the verified revision report and compact review evidence for Claude."""
import os
os.environ.setdefault('WOM09_ROOT','/Users/ryo/Desktop/新チャンネル/EP009_TrojanHorse/確認版_v02_20261101')
import shutil
from pathlib import Path
from wom09_produce import ROOT,REPO,read,sha

def table(head,rows):return '|'+ '|'.join(head)+'|\n|'+'|'.join(['---']*len(head))+'|\n'+''.join('|'+ '|'.join(map(str,r))+'|\n' for r in rows)
def main():
 q=read(ROOT/'records/qc_v02.json');c=read(ROOT/'records/continuous_qc.json');mo=read(ROOT/'records/final_video_motion.json');r=read(ROOT/'records/revision_qc_v02.json');b=read(ROOT/'records/bust_luminance_v02.json');eb=read(ROOT/'records/encoded_bust_comparison.json');share=read(ROOT/'records/sharing.json');layout=read(ROOT/'records/subtitle_layout_validation.json')
 assert all(x['passed'] for x in [q,c,mo,r,layout]) and share['draft'] and share['status']=='verified'
 folder=REPO/'new-channel/wom09_確認版_v02_20261101'
 for name in ['records','確認画像']:(folder/name).mkdir(parents=True,exist_ok=True)
 for p in (ROOT/'records').iterdir():
  if p.suffix in ['.json','.txt','.log']:shutil.copy2(p,folder/'records'/p.name)
 for p in (ROOT/'deliverables').iterdir():
  if p.suffix in ['.srt','.md','.csv','.txt']:shutil.copy2(p,folder/p.name)
 for pattern in ['compare_*.jpg','comparison_sheet_*.jpg','continuous_*_sheet_*.jpg','opening_*.jpg']:
  for p in (ROOT/'review').glob(pattern):shutil.copy2(p,folder/'確認画像'/p.name)
 (folder/'SHA256SUMS_shared.txt').write_text(''.join(a['sha256']+'  '+a['name']+'\n' for a in share['assets']))
 maxratio=max(x['ratio'] for x in mo['checks'] if x['motion_ratio_applicable'])
 text=f'''# Quiet Origins 第9話 確認版v02（2026-11-01）

**Claudeの修正依頼2点を反映し、技術検査と新しい非公開Draft共有を完了。本人の全編試聴・サムネ選択待ち。**

対象はv01 Release `430493346`。指示：[修正依頼v02](../wom09_修正依頼_v02_20261101.md)。変更は文字カード9枚の拡大・中央配置と、P03のレンブラント胸像の明るさだけ。v01はそのまま保全。

## 確認動画・取得

[非公開Draft Release]({share['release_url']})、Release ID **{share['release_id']}**。7資産をRESTで再取得し、サイズ・SHA-256が全件一致。Draft維持、Releaseと各資産の匿名アクセス404。

- `EP009_TrojanHorse_ja_v02_subtitled_review_1080p30.mp4`：日本語字幕付き。
- `EP009_TrojanHorse_en_v02_subtitled_review_1080p30.mp4`：英語字幕付き。
- `EP009_TrojanHorse_{{en,ja}}_v02_1080p30.mp4`：字幕なし本編2本。
- `EP009_audio_and_subtitles_v02.zip`：英日音声WAV/M4A、SRT、既存の発音確認抜粋。
- `EP009_thumbnails_and_metadata_v02.zip`：変更していないサムネA/B、投稿情報、文字配置・動きの検査表。
- `EP009_QA_records_v02.zip`：v01/v02比較10組、英日連続デコード画像、検査記録。

取得IDとハッシュ：[sharing.json](records/sharing.json)。ブラウザーで取得できない場合は `gh api repos/yasukawa1980/youtube/releases/{share['release_id']}` でasset IDを確認し、`gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE` で取得する。公開リポジトリ上の未公開Draftとして共有し、公開操作はしていない。

Mac保存先：`{ROOT}/`（動画・音声は `deliverables/`）。

## 修正した配置

- 本文の最上端・最下端の中点を **y=403.5〜404** に統一。安全範囲y=110〜700、左右48px以上。札・出典の上部110pxはv01と画素一致。
- 本文は約1.3倍を基本に拡大。主要な英語の行は60px以上を目安とし、D_summaryは37→60px、D_timelineの見出しは40→60px。日本語の補助行も35〜62pxへ拡大。文面は空白・改行を除き同一。
- D_passagesの結論は英語60px・太字、日本語44px・太字。上の英語3行も60pxで、結論が小さくならない。
- D_optionsは見出しと3行を左右中央に配置。段階表示のフレーム番号をv01と照合して完全一致。行が増えるときに既存行が飛ばないよう、最終ブロックを中央に置き、各行の位置は固定。
- D_timelineの線と3点は **y=404**。背景 #e8d9b7、本文 #3b2c21、強調 #5a3a1a は維持。

'''
 text+=table(['カード','v01 上端–下端 y','v02 上端–下端 y','v02 中点 y','v01 本文px','v02 本文px','本文/強調コントラスト'],[[x['key'],f"{x['v01_top_y']}–{x['v01_bottom_y']}",f"{x['v02_top_y']}–{x['v02_bottom_y']}",x['v02_center_y'],f"{x['v01_font_min']}–{x['v01_font_max']}",f"{x['v02_font_min']}–{x['v02_font_max']}",f"{x['body_contrast']:.3f} / {x['accent_contrast']:.3f}"] for x in r['layout_rows']])
 text+='\n全9枚、コントラスト比4.5以上。詳細な文字ごとの座標・サイズは [card_layout_v02.json](records/card_layout_v02.json)、表は [CSV](EP009_layout_comparison_v02.csv)。\n\n'
 text+=f'''## 胸像の明るさ

- 同じ表示領域の8bit輝度平均 **{b['v01_mean_luma_8bit']:.6f} → {b['v02_mean_luma_8bit']:.6f}**、**+{b['increase_percent']:.4f}%**。
- 黒端に達したチャンネル数 {b['v01_black_channels']}→{b['v02_black_channels']}、白端に達したチャンネル数 {b['v01_white_channels']}→{b['v02_white_channels']}。白飛び・黒つぶれの増加なし。
- RGB各チャンネルへ同じ係数を掛け、中間調を持ち上げ、ハイライトへ向けて係数を弱めた。色相比は8bit丸め前に維持。胸像領域の外側・札・切り出し・カメラの動きは維持。
- 書き出したv01/v02の同じフレームの内側70%領域でも、平均輝度 **+{eb['increase_percent']:.3f}%** を確認。元PNGと動画の色変換・圧縮があるため、こちらは別測定として記録。

## 維持・技術検査

- **英日のWAV/M4A・SRTはv01とファイルSHA-256一致**。英日本編・字幕付き確認版4本の音声ストリームもv01と同一。音声の再生成・再ミックスなし。
- 共通尺376.433333秒、11,293フレーム、24ショット。全ショットの開始・終了・フレーム数と文字の段階表示時刻がv01と一致。
- 素材・札・文面・出典・サムネ・共通OP/ENDは維持。画像が変わったのは指定の10枚だけ。v01の配布ファイル全件も変更前ハッシュと一致。
- 各ショットを別々にデコードし、非圧縮フレームを1つのエンコーダーへ入力。H.264 High / yuv420p / 1920×1080 / 30fps CFR。
- 英日4動画を先頭から末尾まで連続デコードし、エラー・警告0。英日本編は全11,293フレームで形式1種類、SPS profile_idc=100のみ。各24ショットの先頭・中央・末尾を連続デコードから抽出。
- 英日本編の映像ストリーム同一。動く12ショットのp95÷中央値は最大 **{maxratio:.6f}**（上限2.5）。文字カードは指定表示フレーム以外の可逆中間動画の差分0を確認。
- 英日とも−16.00 LUFS、ピークは英−3.96 / 日−5.16 dBTP。字幕全ページを標準・拡大で描画し、本文との非重複を確認（字幕最上端y=851以上、本文最大y=649）。
- 引用2つは画面用文字と指定文面の完全一致を確認：`"Thus held they funeral for Hector tamer of horses."`／`"I fear the Grecians even when they offer gifts."`。

## 同じ時刻の比較

左v01、右v02。字幕なし本編から、同じ絶対フレームを連続デコードして抽出。段階表示のあるカードは最後の行が出た後を選んだ。

'''
 for x in r['comparisons']:text+=f"- [{x['key']} — {x['seconds']:.3f}秒／frame {x['frame']}](確認画像/{Path(x['file']).name})\n"
 text+='\n本人の音声試聴は未実施。v01と音声が同じなので、既存の発音確認抜粋をそのまま使える。サムネはClaudeがAを推奨しているが、本人の最終選択は未了。YouTube投稿・予約・Release公開は行っていない。\n'
 (folder/'README.md').write_text(text)
 result=text.replace('(../wom09_','(wom09_').replace('(records/','(wom09_確認版_v02_20261101/records/').replace('(確認画像/','(wom09_確認版_v02_20261101/確認画像/').replace('(EP009_','(wom09_確認版_v02_20261101/EP009_')
 (REPO/'new-channel/wom09_制作結果_v02_20261101.md').write_text(result)
 hand=REPO/'new-channel/Claude引き継ぎ_次のセッション.md';s=hand.read_text();mark='## 2026-11-01 Codex追記（第9話の修正版v02完成）';note=f'''{mark}

- [制作結果v02](wom09_制作結果_v02_20261101.md)／[取得案内・同時刻比較](wom09_確認版_v02_20261101/README.md)。文字カード9枚を中央配置・拡大、D_passages結論を太字60px、年表線y=404。胸像の平均輝度+{b['increase_percent']:.4f}%。
- [新しい非公開Draft]({share['release_url']})、Release ID `{share['release_id']}`。7資産をREST再取得して全件照合、匿名404・Draft維持。v01も保全。
- 英日WAV/M4A/SRTのファイルハッシュと4動画の音声ストリームはv01と同一。376.433333秒・24ショット・切り替え／行表示時刻も維持。連続デコード警告・エラー0。
- 次はClaudeの比較画像確認、本人の全編試聴とサムネA/B選択。ClaudeはA推奨、本人の選択は未了。公開・YouTube投稿は未実施。

'''
 if mark not in s:
  first,rest=s.split('\n',1);hand.write_text(first+'\n\n'+note+rest.lstrip())
 print('V02 REPORT',folder,flush=True)
if __name__=='__main__':
 from pathlib import Path
 main()
