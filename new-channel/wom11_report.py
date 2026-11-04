"""Publish Git-visible review records only after private release verification."""
import shutil,json
from pathlib import Path
from PIL import Image
from wom11_produce import ROOT,REPO,read,sha

def main():
 share=read(ROOT/'records/sharing.json');assert share['status']=='verified' and len(share['assets'])==8
 qc=read(ROOT/'records/qc_v01.json');ep=read(ROOT/'records/episode_qc.json');motion=read(ROOT/'records/final_video_motion.json');enc=read(ROOT/'records/4k_encoding_v01.json');layout=read(ROOT/'records/subtitle_layout_validation.json');cards=read(ROOT/'records/contrast.json')['cards'];assert qc['passed'] and ep['passed'] and motion['passed'] and read(ROOT/'records/visual_review.json')['passed']
 out=REPO/'new-channel/wom11_確認版_v01_20261104';out.mkdir(parents=True,exist_ok=True)
 for n in ['records','確認画像']:(out/n).mkdir(exist_ok=True)
 for p in ROOT.glob('records/*.json'):shutil.copy2(p,out/'records'/p.name)
 for p in ROOT.glob('deliverables/*'):
  if p.suffix in ['.srt','.md','.txt','.csv']:shutil.copy2(p,out/p.name)
 for p in ROOT.glob('review/*.jpg'):
  if p.name.startswith(('early_','storyboard_')):continue
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000,(p,Image.open(p).size,p.stat().st_size)
  shutil.copy2(p,out/'確認画像'/p.name)
 td=REPO/'new-channel/サムネ確認用/wom11';td.mkdir(exist_ok=True)
 for p in ROOT.glob('deliverables/EP011_thumb*.jpg'):shutil.copy2(p,td/p.name)
 (out/'SHA256SUMS_shared.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in share['assets']))
 readme=f'''# 第11話「心臓の計量」確認版v01 取得案内

本人承認済み台本v02と、天秤の表示B案を反映。**Claude確認・本人試聴待ち。YouTube未投稿、Release未公開。**

[非公開Draft Release]({share['release_url']})、Release ID **{share['release_id']}**。英日1080p通常版、英日字幕入り確認版、英語4K拡大版、資料ZIP3本。計8ファイルをRelease ID指定RESTで再取得し、バイト数・SHA-256一致、匿名404を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/{share['release_id']}
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
'''
 for a in share['assets']:readme+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
 readme+='\n[SHA-256一覧](SHA256SUMS_shared.txt)／[制作結果](../wom11_制作結果_v01_20261104.md)。\n\n英語4Kは1080p完成版の通常拡大。固有名詞の試聴抜粋は音声・字幕ZIP内。サムネはA/Bから本人が選択する。日本語は同尺の別音声として使用可能。\n'
 (out/'README.md').write_text(readme)
 minimum=min(c['foreground_contrast'] for c in cards);gap=min(b['min_padding_px'] for c in cards for b in c['boxes']);ratio=max(c['ratio'] for c in motion['checks'] if not c['static_source']);metrics=read(ROOT/'records/subtitle_validation.json')
 report=f'''# 第11話「心臓の計量」制作結果v01（2026-11-04）

**確認版完成、非公開Draft Releaseへの共有・REST再取得照合済み。Claude確認・本人試聴待ち。** [取得案内](wom11_確認版_v01_20261104/README.md)。Release ID `{share['release_id']}`。公開・予約・追加課金なし。ショートは未制作。

## 内容と承認

- 承認済み台本v02（英日14区間）を本文変更なしで使用。第1話の再使用はMet 557657だけ。
- 素材9作品、内容22ショット＋オープニング4秒・エンドカード10秒。原寸は指定SSD ESD-02、Gitはコード・記録・小さいJPGのみ。
- 天秤B案を本人が選択。P01最大1.7倍、P10最大3.4倍の通常拡大。この2ショットだけ原寸1倍の例外。他は1倍以下。AI生成・着色・復元なし。
- Section10のオシリス・天秤・アメミトは非重複矩形。意図した再登場はP10の梁・皿だけ。Section05・13は異なる区画。
- P06の最後の引用は英語の該当文開始から2秒表示してから、同じ文の途中で水辺の絵へ切り替え。引用5文をすべて表示するためのタイミング調整。台本は不変。
- 英日共通映像のため、行表示とカットは英語の発話時刻を基準にしている。日本語は区間全体を同尺に収め、区間内の各文と画面の切り替えには差がある。試聴時に確認する。

## 映像・音声

英日共通 **{qc['duration_seconds']:.6f}秒（6分21.367秒）・{qc['frames']:,}フレーム**、1920×1080・30fps CFR・H.264 High・yuv420p。全ショットを個別デコードし、非圧縮フレームを単一エンコーダーへ渡した。共通映像も同じ経路。全4本の連続デコード警告0、通常英日映像ストリーム一致。英日の各ショット先頭・中央・末尾を抽出して画面を確認。エンドカード開始371.366667秒、終了381.366667秒。

| 言語 | LUFS | dBTP | 字幕数 | 最短字幕秒 | 最大1行字数 |
|---|---:|---:|---:|---:|---:|
'''
 for l,idx in [('en',0),('ja',2)]:
  q=qc['files'][idx]['loudness'];s=metrics[l];report+=f"| {l} | {q['input_i']} | {q['input_tp']} | {s['count']} | {s['min_seconds']:.3f} | {s['max_line_chars']} |\n"
 report+=f'''
BGMはQO_THEME_A02のみ。1秒以上・−60dB以下の全体無音なし。英語Kokoro/Heart speed0.82、日本語VOICEVOX:冥鳴ひまりC設定。声の速度・ピッチを尺合わせで変更していない。字幕本文は改行・空白を除いて台本と一致、2行以内。標準FontSize14の焼き込み確認版で、全字幕の最上端はy{min(c['minimum_subtitle_top'] for c in layout['checks'])}、カード文字との重なりなし。

無置換の初回音声153文を保全。英語は初回を採用。日本語6種類（二つの真理の間／真理の主／秤を守る者／現代の訳／甲虫／声正しき者）を音声クエリ上の誤読に基づいて修正。字幕は元の表記。修正前後のクエリ、文の時刻、音声SHA-256、試聴抜粋を保存。人の聴感による発音・通し再生確認は未実施。

## 画面検品

文字カード6枚の主要行は字高60px以上。通常幅・改行による構成を基本とし、長い引用と5段図にはDIN Condensedを使用。最低コントラスト **{minimum:.3f}**、5段図の箱内最小余白 **{gap}px**。各カードと各素材の表は確認版フォルダのCSVに保存。否定告白5行（角かっこ含む）・Todtenbuch綴りを機械照合。イムヘテプにSpell 125札なし。30B章の刻文はMet 550986。

完成動画の動素材について、連続フレーム差のp95/中央値は最大 **{ratio:.3f}**、すべて2.5以下。文字カードは指定の行表示切替以外、中間素材の画素変化なし。共通ブランド映像は動き比の対象外。原寸にない細部の復元はしていない。

サムネは[案A](サムネ確認用/wom11/EP011_thumbnail_A.jpg)／[案B](サムネ確認用/wom11/EP011_thumbnail_B.jpg)。[168px比較](サムネ確認用/wom11/EP011_thumbnails_168_comparison.jpg)。どちらも1280×720・1MB未満。

## 英語4Kと共有

1080p完成版からLanczosで3840×2160へ拡大（第10話と同じx264 veryfast・40Mbps指定、上限45Mbps・GOP15）。**元画像の情報量が増える処理ではない**。実測{enc['frames']:,}フレーム、{enc['duration']:.6f}秒、{enc['bytes']:,} bytes、平均{enc['bit_rate']/1e6:.3f}Mbps。H.264 High・yuv420p・30fps、全編デコード警告0、音声ストリームは1080pと同一。

8添付すべてRESTで再取得、SHA-256・バイト数一致。匿名は404、Draftのまま維持。保存先 `{ROOT}`。

## 本人の確認事項

1. 試聴抜粋のMaat・Ammit・Thoth・Lepsius・Annu・Heliopolis・scarab・Spell 30B・springtideと、日本語の指定語の読み。
2. 古い英語の否定告白5文が聞き取れるか。
3. 最初の数秒、天秤の拡大、通し再生の見え方。
4. サムネA/Bの選択。

公開予定11/10 09:00 JST、予約目標11/9。投稿は別の指示後に、その日のチャンネル本数を再照合する。本依頼で投稿・公開は行っていない。
'''
 (REPO/'new-channel/wom11_制作結果_v01_20261104.md').write_text(report);print('GIT HANDOFF READY',flush=True)
if __name__=='__main__':main()
