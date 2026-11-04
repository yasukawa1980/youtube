"""Git-visible v02 handoff, gated on technical/visual QA and verified draft sharing."""
import shutil,json
from pathlib import Path
from PIL import Image
from wom11_v02 import ROOT,REPO,read,sha,V01

def main():
 share=read(ROOT/'records/sharing.json');assert share['status']=='verified' and share['draft'] and len(share['assets'])==8
 for name in ['qc_v02','revision_v02','continuous_qc','final_video_motion','episode_qc','subtitle_layout_validation','encoded_card_contrast','visual_review']:assert read(ROOT/f'records/{name}.json')['passed']
 qc=read(ROOT/'records/qc_v02.json');rev=read(ROOT/'records/revision_v02.json');enc=read(ROOT/'records/4k_encoding_v02.json');p6=rev['P06'];p10=rev['P10'];summary=rev['D_summary'];motion=read(ROOT/'records/final_video_motion.json')
 out=REPO/'new-channel/wom11_確認版_v02_20261104';out.mkdir(exist_ok=True)
 for name in ['records','確認画像']:(out/name).mkdir(exist_ok=True)
 for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,out/'records'/p.name)
 for p in (ROOT/'deliverables').glob('*'):
  if p.suffix in ['.srt','.md','.txt','.csv'] or p.name=='EP011_thumbnail_A.jpg':shutil.copy2(p,out/p.name)
 for p in (ROOT/'review').glob('*.jpg'):
  if p.name.startswith(('early_','storyboard_')):continue
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000,p
  shutil.copy2(p,out/'確認画像'/p.name)
 (out/'SHA256SUMS_shared.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in share['assets']))
 note=f'''# 第11話「心臓の計量」確認版v02 取得案内

Claudeの[確認メモ](../wom11_Claude確認_v01_20261104.md)にある映像4か所を修正。**音声・字幕・台本はv01とハッシュ一致。サムネは本人承認のA。** v01は保全。本人試聴・Claudeの最終確認待ち。YouTube未投稿、Release未公開。

[非公開Draft Release]({share['release_url']})、Release ID **{share['release_id']}**。

```sh
gh api repos/yasukawa1980/youtube/releases/{share['release_id']}
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

英日1080p通常版、英日字幕入り確認版、英語4K通常拡大版と資料ZIP3本。全8添付をRESTで再取得し、サイズ・SHA-256一致、匿名404を確認。

| ファイル | asset ID | bytes |
|---|---:|---:|
'''
 for a in share['assets']:note+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
 note+='\n[SHA-256一覧](SHA256SUMS_shared.txt)／[修正結果](../wom11_制作結果_v02_20261104.md)／[採用サムネA](EP011_thumbnail_A.jpg)。音声・字幕ZIP内の発音抜粋はv01と同一なので、試聴はどちらの版でもよい。\n'
 (out/'README.md').write_text(note)
 ratio=max(x['ratio'] for x in motion['checks'] if not x['static_source'])
 report=f'''# 第11話「心臓の計量」制作結果v02（2026-11-04）

**映像4か所の修正・検品・非公開共有を完了。本人試聴とClaudeの最終確認待ち。** [取得案内](wom11_確認版_v02_20261104/README.md)。Release ID `{share['release_id']}`。v01 Release `433561970` とSSD上のv01を保全。YouTube投稿・予約・公開、追加課金なし。

## 修正と実測

| 箇所 | v02の内容・実測 |
|---|---|
| P06 | 1行目まで中央にTHE NEGATIVE CONFESSION／否定告白、字高{p6['central_heading_glyph_heights'][0]}／{p6['central_heading_glyph_heights'][1]}px。1行目と同時に中央見出しを消す。D_denialsを{p6['end']:.6f}秒まで延長。5行がそろう{p6['all_five_lines_from']:.6f}秒から{p6['all_five_lines_hold_seconds']:.6f}秒保持。E10Bを映像・採用素材台帳・クレジット・概要欄から除外 |
| トトE08A | {p10['thoth_start']:.6f}–{p10['thoth_end']:.6f}秒、{p10['thoth_seconds']:.6f}秒。アメミト画面は英語「One old description calls her」の開始に合わせた |
| アメミト | 元画像の専用範囲をLanczosで通常拡大。{p10['ammit_native_initial_scale']:.6f}→{p10['ammit_native_max_scale']:.3f}倍、表示画像{p10['ammit_image_initial_size'][0]}×{p10['ammit_image_initial_size'][1]}→約{p10['ammit_max_image_size'][0]}×{p10['ammit_max_image_size'][1]}px。AI補間・復元なし |
| D_summary | 上3・下2の2段。画面左右の余白最小{summary['edge_margin_px']}px、箱の内側最小{summary['minimum_inner_padding_px']}px。英語主要行字高{summary['major_glyph_height']}px、コントラスト{summary['contrast']:.3f}。SPELL 30B — WORDS FOR THE HEARTは2行 |

素材は8作品、内容21＋ブランド2＝23ショット。サムネAを採用し、画像はv01と同一。台本JSON内の旧visuals指定も含めてファイルを保全し、実際の映像構成は `render_shots.json` と `visual_manifest.json` に記録。

## 維持したもの

英日台本JSON、WAV・M4A（発音抜粋を含む）、英日SRTはv01とSHA-256一致。英日通常MP4の音声ストリームもv01と一致。初回合成・読み替え・音声設定は変更していない。D_denialsの引用段階1〜5と、修正対象外の全入力画像はv01と同一。新しい中央見出しは段階0だけ。引用5文とTodtenbuchの綴りは維持。

## P10の英日発話と映像の差

映像は英日共通で、切替は英語基準。トト画面は{p10['thoth_start']:.3f}〜{p10['thoth_end']:.3f}秒、アメミト画面は{p10['ammit_start']:.3f}秒から。

| 言語 | 文 | 開始–終了（秒） |
|---|---|---|
'''
 for lang,key in [('en','english_sentences'),('ja','japanese_sentences')]:
  for c in p10[key]:report+=f"| {lang} | {c['text']} | {c['start']:.3f}–{c['end']:.3f} |\n"
 report+=f'''
日本語のアメミト文開始より、アメミト画面への切替が{-p10['japanese_Ammit_sentence_start_minus_visual_start']:.3f}秒遅い。英日共通映像を保った上での指定どおりの差で、本人試聴時の確認項目。

## 完成版の検品

尺{qc['duration_seconds']:.6f}秒・{qc['frames']:,}フレーム、1080p H.264 High／yuv420p／30fps CFR。全ショット個別デコードから単一エンコーダーへ渡して書き出した。通常英日の映像ストリーム一致。通常2本・字幕入り2本・英語4Kすべて連続デコード警告0。エンドカードは371.366667–381.366667秒の最後10秒。英日とも全23ショットの先頭・中央・末尾を抽出し、最終画面を確認。

音量は英語{qc['files'][0]['loudness']['input_i']} LUFS／{qc['files'][0]['loudness']['input_tp']} dBTP、日本語{qc['files'][2]['loudness']['input_i']} LUFS／{qc['files'][2]['loudness']['input_tp']} dBTP。字幕86／98件は本文不変、2行以内、最短1.4秒以上。焼き込み字幕とカード文字の重なりなし。動素材の全隣接フレーム差p95/中央値は最大{ratio:.3f}（上限2.5）。カードは指定の段階表示以外、全画素が静止。

英語4Kは修正版1080pからLanczosで作り直し。{enc['frames']:,}フレーム、{enc['duration']:.6f}秒、{enc['bytes']:,} bytes。通常拡大であり細部の復元はしていない。音声は修正版1080pと同一。

全8添付をRelease ID指定RESTで再取得し、サイズ・SHA-256一致、匿名404を確認。保存先 `{ROOT}`。

本人の確認事項は、固有名詞と否定告白の聞き取り、日本語の語りと画面の差、P08のガラス護符の長さ、通し再生。音声はv01でも試聴可能。サムネ選択はAで確定済み。公開予定11/10 09:00 JST、予約は11/9まで（本作業では未実施）。
'''
 (REPO/'new-channel/wom11_制作結果_v02_20261104.md').write_text(report)
 print('V02 GIT HANDOFF READY',flush=True)
if __name__=='__main__':main()
