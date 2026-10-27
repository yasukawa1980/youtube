"""Export EP006 Shorts records and measured delivery report to Git."""
import shutil
from pathlib import Path
from PIL import Image
from wom06_shorts_render import ROOT, REQUEST, read, save, sha

REPO=Path(__file__).resolve().parent.parent
GUIDE=REPO/'new-channel/wom_ショート_EP006_確認版_v01_20261027'
REPORT=REPO/'new-channel/wom_ショート制作結果_EP006_20261027.md'


def export():
    share=read(ROOT/'records/sharing_complete.json')
    assert share['status']=='verified' and share['draft']
    for name in ['media_qc','subtitle_qc','motion_qc','asset_usage','visual_review']:
        assert read(ROOT/f'records/{name}.json')['passed']
    access=read(ROOT/'records/draft_access_verification.json')
    assert access['draft'] and access['published_at'] is None
    assert all(c['anonymous_http_status']==404 for c in access['checks'])
    for d in ['records','review','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').iterdir():
        if p.suffix in ['.json','.log']:shutil.copy2(p,GUIDE/'records'/p.name)
    for p in (ROOT/'audio').glob('*_native.json'):shutil.copy2(p,GUIDE/'records'/p.name)
    for p in (ROOT/'review').glob('*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
        shutil.copy2(p,GUIDE/'review'/p.name)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.srt','.txt','.csv']:shutil.copy2(p,GUIDE/'deliverables'/p.name)
    nar=read(ROOT/'records/narration.json');media=read(ROOT/'records/media_qc.json')['media']
    shots=read(ROOT/'records/render_shots.json');motion=read(ROOT/'records/motion_qc.json')['checks']
    maxmotion=max(c['measurement']['p95_over_median'] for c in motion)
    measurements='\n'.join(f"| {m['id']} | {m['duration_seconds']:.6f} | {next(s['native_audio_duration'] for s in nar['scripts'] if s['id']==m['id']):.6f} | {m['lufs']:.2f} | {m['true_peak_dbtp']:.2f} | {m['voice_onset_normalized_stem_seconds']:.2f} | {m['frames']} |" for m in media)
    cuts='\n'.join(f"| {s['short_id']} | {s['asset_id']} | {s['start_frame']/30:.3f}–{s['end_frame']/30:.3f} | {s['cut_phrase'] or '先頭'} | {s['cut_word_seconds'] if s['cut_word_seconds'] is not None else '—'} |" for s in shots)
    hashes='\n'.join(f"| {m['name']} | {m['bytes']:,} | `{m['sha256']}` |" for m in media)
    credits='\n'.join(f"| {s['asset_id']} | {s['source']['label']} | {s['source']['source'] or '本編 D_riddle（出典欄なし）'} |" for s in shots)
    guides=GUIDE.name
    readings=nar['reading_replacements_sha256']
    report=f'''# 第6話「スフィンクス」英語ショート3本 制作結果（2026-10-27）

[Claude依頼書]({REQUEST.name})どおりS1〜S3の確認版v01を制作。台本は原文のまま、英語Kokoro af_heart／英語字幕入り。**YouTubeへのアップロード・予約・公開は実施していない。** 本人の通し試聴とClaudeの確認はこれから。

## 成果物と共有

- Mac：`{ROOT}`
- 再生ページ：`{ROOT}/deliverables/preview.html`
- [非公開Draft Release]({share['release_url']})、Release ID **{share['release_id']}**、タグ `qo-shorts-ep006-complete-v01-20261027`。
- Release IDを指定したRESTで全 **{len(share['assets'])}ファイル**を再ダウンロードし、SHA-256とバイト数を照合済み。`draft=true`、`published_at=null`。各ファイルの照合記録は[sharing_complete.json]({guides}/records/sharing_complete.json)。
- 公開リポジトリ内の未公開Draft。GitHub公式REST仕様でDraftはpush権限者に限定されることを確認し、当該Releaseと全アセットの未認証GETがすべて404になることも検証した。[アクセス検査]({guides}/records/draft_access_verification.json)、[公式仕様](https://docs.github.com/en/rest/releases/releases#list-releases)。
- 動画3本、SRT3本、2秒おき一覧3枚・中央フレーム3枚、台本、QC・動き・素材一覧CSV、再生ページ、制作記録ZIP、SHA一覧を同梱。

## 尺・音声の実測

| ID | 完成秒数 | 読み上げ原音秒数 | LUFS | dBTP | 最初の声（秒） | フレーム |
|---|---:|---:|---:|---:|---:|---:|
{measurements}

3本とも22秒以内。S3は台本・話速を維持して21.67秒とした。声の開始は正規化後ナレーション単体を10ms窓・−50 dBFS閾値で検出。本編BGMの静かな120／140／160秒開始の区間を使い、語りの下は−33.5 dBFS。完成MP4内の音声ストリームと検査済みAACが一致。

本編と同じaf_heart、speed 0.82、sentence_pause 0.3、clause_pause 0.12。Kokoro ONNX 0.6.1、ONNX Runtime 1.31.0、numpy 2.3.5を使用。速度・ピッチの後加工なし。本編v02の`reading_replacements.json`をバイト単位でコピーし、SHA-256は`{readings}`。

実際に使用した補正はSophocles、Hatshepsut、Fredericの音素と`1730s → seventeen thirties`。Oedipus・Giza・Nordenは本編と同じ標準トークナイザーの読み（本編に追加音素指定なし）。[設定と原音測定]({guides}/records/narration.json)、[補正原本]({guides}/records/reading_replacements.json)。今回生成した音声について本人の通し試聴は未実施。

## 構成・切り替え

| ID | 素材 | 表示時間（秒） | 切り替え語 | 音素由来の語開始秒 |
|---|---|---:|---|---:|
{cuts}

切り替えは最寄り30fpsフレームへ丸め、語開始との差は最大1/60秒以内。各素材は1.5秒以上、9素材は3本全体で重複なし。時刻はKokoroの音素長から台本単語へ対応付けたモデル由来の推定で、人による聴覚アラインメントではない。

モローは本編v02の`[.12,.10,.95,.33]`のみ。前景・ぼかし背景の両方を先にその範囲だけから作り、その合成画面内でカメラを動かすため、全フレームで範囲外の胸・犠牲者が入らない。Jebbは本編v02と同じ`[60,1400,1015,1524]`px、3行の本文を保全。D_riddleは本編の既存線画を使用し、朝・昼・晩の記号なし。新規AI素材なし。

## 札・出典

本編v02の札・出典の文をそのまま使用。XLVのみ今回の依頼書に指定された追加出典を使用。上部y140〜260に収まり、撮影者・刊年を保持。

| 素材 | 札 | 出典 |
|---|---|---|
{credits}

## 検査

- 1080×1920、30fps、H.264 High、yuv420p。全フレームのPTS間隔を照合。
- 個別ショットをそれぞれ独立デコードし、raw yuv420pを1本の完成動画につき1つのエンコーダーへ順に投入。字幕も同じ最終エンコードで焼き込み。MP4ビットストリーム連結なし。[エンコード記録]({guides}/records/encoding_method.json)。
- 完成3本を先頭から連続デコードし、**警告0件**。
- 字幕文字列は依頼書原文と完全一致。全ページを本番と同じlibass・フォントで描画し、輪郭・影を含めx80〜880／y1150〜1450内、2行以下・各行最大5語。`in the 1730s,`と`in 1798.`はそれぞれ同じ字幕ページに保持。
- 最後の2秒に`Full story on Quiet Origins`、追加の読み上げ・オープニング・エンドカードなし。
- 動きは**最終MP4の全フレーム**で、各ショットの資料内側70%の連続フレーム輝度差を測定。サンプリング間引き・平滑化なし。p95÷中央値は最大 **{maxmotion:.6f}**、全9ショットで2.5以下。[測定記録]({guides}/records/motion_qc.json)。
- 2秒おき一覧と各動画の中央フレームを目視点検。6枚のJPGはいずれも長辺1280px以下、1MB未満。[S1一覧]({guides}/review/QO_short_EP006_S1_v01_every2s.jpg)／[S2一覧]({guides}/review/QO_short_EP006_S2_v01_every2s.jpg)／[S3一覧]({guides}/review/QO_short_EP006_S3_v01_every2s.jpg)。

## 完成ファイル

| ファイル | bytes | SHA-256 |
|---|---:|---|
{hashes}

制作スクリプト：[原音・尺検査](wom06_shorts.py)、[字幕・音楽・映像](wom06_shorts_render.py)、[検査](wom06_shorts_qc.py)、[Draft共有](wom06_shorts_delivery.py)、[報告出力](wom06_shorts_report.py)。動画・音源・原寸素材・中間ファイルはGitに含めない。

投稿予定は依頼書の参考案のまま。今回の作業でYouTube予約や関連動画設定を変更していない。投稿は別依頼で行う。
'''
    REPORT.write_text(report)
    print('EXPORTED',GUIDE,REPORT,flush=True)


if __name__=='__main__':export()
