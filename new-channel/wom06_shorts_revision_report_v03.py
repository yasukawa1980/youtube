"""Measured v03 revision report and lightweight Git evidence export."""
import sys, shutil
from pathlib import Path
from PIL import Image
import wom06_shorts_revision_v03 as rev
ROOT=rev.ROOT;read=rev.read;sha=rev.sha
GUIDE=rev.HERE/'wom_ショート_EP006_冒頭_v03_20261027'
REPORT=rev.HERE/'wom_ショート冒頭修正結果_EP006_v03_20261027.md'


def export():
    sharing=read(ROOT/'records/sharing_complete.json');assert sharing['draft'] and sharing['status']=='verified'
    for name in ['media_qc','subtitle_qc','motion_qc','preservation_qc','safe_crop_qc','headline_qc','visual_review']:assert read(ROOT/f'records/{name}.json')['passed']
    for folder in ['records','review','deliverables']:(GUIDE/folder).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').iterdir():
        if p.suffix in ['.json','.csv','.log']:shutil.copy2(p,GUIDE/'records'/p.name)
    for p in (ROOT/'review').rglob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        out=GUIDE/'review'/p.relative_to(ROOT/'review');out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.srt','.txt','.csv']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
    media=read(ROOT/'records/media_qc.json')['media'];shots=read(ROOT/'records/render_shots.json');motion=read(ROOT/'records/motion_qc.json')['checks'];diff=read(ROOT/'records/unchanged_frames_qc.json')['shorts'];hooks=read(ROOT/'records/headlines.json')
    guide=GUIDE.name
    headline_rows='\n'.join(f"| {h['id']} | {h['text']} | {len(h['lines'])} | {min(x['bbox'][1] for x in h['lines'])}–{max(x['bbox'][3] for x in h['lines'])} |" for h in hooks)
    metrics='\n'.join(f"| {m['id']} | {m['duration_seconds']:.6f}秒 | {m['lufs']:.2f} | {m['true_peak_dbtp']:.2f} | 同一 | 0 |" for m in media)
    framing='\n'.join(f"| {s['short_id']} | {s['foreground_height_pixels']}px／{s['foreground_height_fraction']*100:.2f}% | {s['source_crop_pixels']} | {s['source_to_output_scale_start'][1]:.6f}→{s['source_to_output_scale_end'][1]:.6f}倍 | {next(c['measurement']['p95_over_median'] for c in motion if c['short_id']==s['short_id'] and c['changed_first_shot']):.6f} |" for s in shots if s['changed_v03'])
    differences='\n'.join(f"| {r['id']} | {r['compared_frames']} | {r['identical_frames']} | {r['different_frames']} | {r['mean_abs_luma']:.9f} | {r['maximum_component_difference']} |" for r in diff)
    cuts='\n'.join(f"| {s['short_id']} | {s['asset_id']} | {s['start_frame']/30:.6f}–{s['end_frame']/30:.6f} | {'冒頭のみ修正' if s['changed_v03'] else '個別ショットファイル同一'} |" for s in shots)
    files='\n'.join(f"| {m['name']} | {m['bytes']:,} | `{m['sha256']}` |" for m in media)
    text=f'''# スフィンクスショート 冒頭v03 修正結果（2026-10-27）

[Claudeの本人承認済みv03依頼](wom_ショート冒頭修正_EP006_v03_20261027.md)を反映。**3本とも最初のショットだけを修正した。YouTubeへのアップロード・予約・公開は行っていない。** v01・v02は変更せず保全。本人のv03視聴・Claude確認はこれから。

## 再生と共有

- Mac：[v01・v02・v03を並べた比較ページ]({ROOT}/deliverables/preview.html)。
- [S1 v03（20秒）]({ROOT}/deliverables/QO_short_EP006_S1_v03.mp4)／[S2 v03（18秒）]({ROOT}/deliverables/QO_short_EP006_S2_v03.mp4)／[S3 v03（21.67秒）]({ROOT}/deliverables/QO_short_EP006_S3_v03.mp4)。
- Claude向け：[非公開Draft Release]({sharing['release_url']})、**Release ID {sharing['release_id']}**、タグ `qo-shorts-ep006-hook-v03-20261027`。
- 全{len(sharing['assets'])}添付をRelease ID指定RESTで再取得し、SHA-256とバイト数を照合済み。Draftを維持し、Releaseと全アセットの匿名GET 404を検証。[共有記録]({guide}/records/sharing_complete.json)／[非公開性の検査]({guide}/records/draft_access_verification.json)。
- 比較用v01・v02の6本も元とバイト同一で同梱した。`preview.html`と9本のMP4を同じフォルダに保存すれば、ダウンロード後も3版を並べて再生できる。旧Draftはv01 `425054637`、v02 `425093235`。

## 冒頭の見出し

| 本 | 見出し | 行数 | 文字のy範囲 |
|---|---|---:|---:|
{headline_rows}

Georgia Bold、生成り`#f4efdf`、実際の大文字の高さ100px。長い行のみ横方向にコンデンスし、x80〜880内、中央x480へ配置。文字の後ろだけ半透明の暗い帯。上の札・出典はv02の同じ画面位置・同じ描画を保持。

0フレーム目から表示し、60フレーム目（2.0秒）までは同じ不透明度。61〜68フレームでフェード、69フレーム目（2.3秒）には完全透明。本番と同じRGBA fadeフィルターで検証した。字幕は同時表示し、見出しと重ならない。[見出し記録]({guide}/records/headlines.json)／[フェード検査]({guide}/records/headline_qc.json)。

## 最初の絵・動きの実測

| 本 | 絵の高さ／画面高に対する比率 | 元画像の切り出しpx | 元画像1pxに対する表示倍率（開始→終了） | 動きp95÷中央値 |
|---|---|---|---:|---:|
{framing}

高さは札・文字を重ねる前の前景画像領域。S1は安全な元画像の高さ920pxから1600pxへ拡大（83.33%）。1920px全面へ伸ばすより拡大による粗さを抑え、二人の顔と翼の一部を残すため、依頼書の80%以上の選択肢を使用。下320pxは同じ安全範囲から作ったぼかし。S2は頭・前半身、S3は顔を中心に縦画面全体へ配置した。

3本とも0秒からショット末尾まで1.00→1.08倍の連続的な寄り。S1は画面下端を基準に寄せ、顔が下で欠けない構図。動きの測定は最終MP4の全連続フレームを使用し、札・字幕・フェードする見出しの領域を除いて画像の動きを測定した。時間方向の間引き・平滑化なし。後続6ショットも2.5以下。[測定記録]({guide}/records/motion_qc.json)。

S1の元画像は2072×4000px、安全範囲は正規化`[.12,.10,.95,.33]`の内側へ丸めた`[249,400,1968,1320]`px。前景・背景ともこの中だけから生成。73フレームすべてのカメラ窓がその内側にあることを検査。新しいAI画像・動画なし。[安全範囲検査]({guide}/records/safe_crop_qc.json)。

## 音声・字幕・再生検査

| 本 | 尺 | LUFS | dBTP | 元版との音声ストリーム | 連続デコード警告 |
|---|---:|---:|---:|---|---:|
{metrics}

1080×1920、30fps、H.264 High／yuv420p。音声は再エンコードせずコピーし、v02とのストリームハッシュ一致（S2はv01とも一致）。本編BGMの区間・音量も保全。字幕の全文・ページ分け・時刻・CTAを含むASSはv02とバイト一致。台本、素材順、切り替え時刻、尺を維持。[保全検査]({guide}/records/preservation_qc.json)／[メディア検査]({guide}/records/media_qc.json)。

個別ショットをそれぞれ独立デコードし、生フレームを1本の最終エンコーダーへ投入。v02完成MP4は比較検査にのみ使用し、制作の入力には使用していない。後続ショットはv02の既存個別ショットをハッシュ照合して再利用。[エンコード記録]({guide}/records/encoding_method.json)。

## 後続ショットの画素照合

| 本 | 比較フレーム数 | 画素一致 | 圧縮差あり | 全比較フレームの平均絶対輝度差／255 | 最大成分差／255 |
|---|---:|---:|---:|---:|---:|
{differences}

**S1・S3は後続の全フレームが画素一致。S2は395フレーム中166フレームに再圧縮差が残る。** S2の全YUV成分平均絶対差は0.169756613／255、フレーム単位の最大平均絶対差は0.737880337／255。単一画素成分の最大差は53／255。後続の個別ショット入力は元とSHA-256一致し、構成・画像・字幕・動きは変更していない。依頼書の「圧縮の差が出る場合はフレーム数と差の大きさを記録」に従い、再承認待ちにはしていない。[比較集計]({guide}/records/unchanged_frames_qc.json)／[全フレーム測定CSV]({guide}/records/unchanged_frames.csv)。

## 切り替え時刻（v02から変更なし）

| 本 | 素材 | 秒 | 状態 |
|---|---|---:|---|
{cuts}

## 画像での確認

連続デコードから0・0.5・1.0・1.5・2.0・2.5秒の18枚を抽出し、見出しの欠け、札・字幕との重なり、画面の占有率を確認した。長辺1280px以下、各JPG 1MB未満。18枚の個別画像はDraftの`opening_frames_18.zip`にも収録。

- [S1 冒頭6枚]({guide}/review/S1_opening_0_to_2_5s.jpg)
- [S2 冒頭6枚]({guide}/review/S2_opening_0_to_2_5s.jpg)
- [S3 冒頭6枚]({guide}/review/S3_opening_0_to_2_5s.jpg)

見出しを消した後も、S1は2.433333秒、S2は4.833333秒、S3は4.566667秒まで拡大構図のまま。その後は元の資料枠＋ぼかしへ戻る。本人のv03視聴は未実施。助手による新たな音声聴感判定も行っていない（音声は元版同一）。

## 完成v03ファイル

| ファイル | bytes | SHA-256 |
|---|---:|---|
{files}

再現用：[準備・制作](wom06_shorts_revision_v03.py)、[検査](wom06_shorts_revision_qc_v03.py)、[比較ページ・Draft](wom06_shorts_revision_delivery_v03.py)、[報告出力](wom06_shorts_revision_report_v03.py)。動画・音源・原寸素材・中間ファイルはGitに含めない。投稿依頼のファイル差し替えやYouTube操作は、v03の確認後の別依頼で行う。
'''
    REPORT.write_text(text)
    print('EXPORTED',REPORT,flush=True)


if __name__=='__main__':export()
