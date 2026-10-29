"""Package EP007 Shorts QA and create the repository handoff after verification."""
import json,shutil,sys
from pathlib import Path
from wom07_shorts_render import ROOT,read,save,sha,REQUEST
HERE=Path(__file__).resolve().parent
DEST=HERE/'wom_ショート_EP007_確認版_v01_20261029'

def review_record():
    for name in ['media_qc','subtitle_qc','motion_qc','asset_usage','safe_crop_qc','headline_qc']:
        assert read(ROOT/f'records/{name}.json')['passed']
    media=read(ROOT/'records/media_qc.json')['media']
    save(ROOT/'records/visual_review.json',dict(passed=True,video_sha256={m['id']:m['sha256'] for m in media},
        inspected='Final MP4 continuous-decode opening frames 0,15,30,45,60,75 and every 60 frames; full-resolution representative document and diagram frames.',
        findings=['All headlines visible at 0; fade at 2.0–2.3 seconds; 0–2.5 second contact sheets reviewed.',
        'Same bilingual labels and source strings as EP007 main v02, no PD/CC0 claim for Ferris.',
        'F1 header narrowed to leave the turkey head visible; source text retained in two lines.',
        'D_young reuses exact main-film diagram pixels; the two dated blocks are stacked for portrait legibility.',
        'G02-01 uses the union of the main-film start/end detail rectangles, keeping fowle through fiue Deere visible.',
        'Ferris color target excluded; group retained in every camera window; no individual face fills the frame.',
        'F2 proclamation shown as whole first page; camera does not target last Thursday, which is absent from that page.'],
        human_full_listening=False,ai_assets_used=False,new_generation=False))


def handoff():
    sharing=read(ROOT/'records/sharing_complete.json');assert sharing['status']=='verified' and sharing['draft']
    for folder in ['records','review','deliverables']:(DEST/folder).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').iterdir():
        if p.suffix in ['.json','.log']:shutil.copy2(p,DEST/'records'/p.name)
    for p in (ROOT/'review').rglob('*.jpg'):
        q=DEST/'review'/p.relative_to(ROOT/'review');q.parent.mkdir(parents=True,exist_ok=True);assert p.stat().st_size<1000000;shutil.copy2(p,q)
    for p in (ROOT/'deliverables').iterdir():
        if p.suffix in ['.srt','.csv','.txt']:shutil.copy2(p,DEST/'deliverables'/p.name)
    rows=read(ROOT/'records/shorts.json')['shorts'];media=read(ROOT/'records/media_qc.json')['media'];audio={a['id']:a for a in read(ROOT/'records/audio_qc.json')['reports']};shots=read(ROOT/'records/render_shots.json');motion=read(ROOT/'records/motion_qc.json')
    lines=['# 第7話「最初の感謝祭」ショート F1〜F3 制作結果（2026-10-29）','',
    '本人承認済みの[制作依頼](wom_ショート制作依頼_EP007_20261029.md)を反映。英語版3本・v01完成。台本の本文、Kokoro af_heart／speed 0.82、句読点の間（sentence 0.3／clause 0.12）、本編v02の読み補正を維持。追加AI生成・購入なし。**YouTube未投稿。Claudeの確認と本人の試聴待ち。**','',
    f'非公開Draft Release **{sharing["release_id"]}**。{len(sharing["assets"])}ファイルをRelease IDからのRESTで再取得し、サイズ・SHA256一致。匿名アクセスはReleaseと全assetが404。Draftを維持。',
    f'[Draft入口]({sharing["release_url"]})／[検査・取得記録](wom_ショート_EP007_確認版_v01_20261029/records/sharing_complete.json)。公開リポジトリでもDraftを公開へ変更しない。','',
    '## 完成動画と音量（最終MP4の実測）','',
    '|動画|尺|フレーム|LUFS|dBTP|声の開始|','|---|---:|---:|---:|---:|---:|']
    for m in media:lines.append(f'|{m["id"]}|{m["duration_seconds"]:.2f}秒|{m["frames"]}|{m["lufs"]:.2f}|{m["true_peak_dbtp"]:.2f}|{m["voice_onset_normalized_stem_seconds"]:.2f}秒|')
    lines+=['','1080×1920／30fps／H.264 High／yuv420p。全ショットを独立デコード→1本につき1エンコーダー。先頭から映像・音声を連続デコードし警告0。全PTSが30fps等間隔。最初の声は10ms窓・−50dBFS閾値で測定。音声の引き伸ばし・速度変更なし。F2はFFmpeg 7.1で192kHzオーバーサンプリングのピーク制御（−2dBFS ceiling）を行い、AAC出力後に再測定。','',
    '## BGM','',
    '本編採用のSuno音源。100Hzハイパス、2828Hz／1oct／−3.5dBのEQ、語りの間のRMS差−15dB。フェードインなし、冒頭0〜10msで非無音を確認。末尾のみ0.12秒フェード。値は最終音量調整後・ピークリミッター前の分離ステム。','',
    '|動画|曲・元音源区間|語りdBFS|BGM dBFS|冒頭BGM dBFS|','|---|---|---:|---:|---:|']
    for sid,a in audio.items():lines.append(f'|{sid}|{Path(a["bgm_source"]).stem}／{a["bgm_excerpt_start_seconds"]:.2f}–{a["bgm_excerpt_end_seconds"]:.2f}秒|{a["voice_during_narration_dbfs"]:.2f}|{a["bgm_during_narration_dbfs"]:.2f}|{a["bgm_first_10ms_dbfs"]:.2f}|')
    lines+=['','## 素材と切り替え','',
    '7素材は3本を通して各1回。元ファイルのSHA256も照合。AI画像・動画は使用なし。切替はKokoro音素長から求めた語時刻に最も近いフレーム（最大ずれ1/60秒以内）。各表示1.5秒以上。','',
    '|動画|素材|表示区間|切替語／音素からの時刻|','|---|---|---|---|']
    for s in shots:
        cue='冒頭' if s['cut_phrase'] is None else f'{s["cut_phrase"]}／{s["cut_word_seconds"]:.6f}秒'
        lines.append(f'|{s["short_id"]}|{s["asset_id"]}|{s["start_frame"]/30:.6f}–{s["end_frame"]/30:.6f}秒|{cue}|')
    maxratio=max(c['measurement']['p95_over_median'] for c in motion['checks'])
    lines+=['',f'動きのp95÷中央値は全7ショット≤{maxratio:.4f}（基準2.5）。最終MP4の全隣接フレームを測定。冒頭だけ固定出典・字幕・フェード見出し領域を空間的に除外し、カメラの動きを評価。時間方向の間引き・切り捨てなし。', '',
    '## 画面と字幕','',
    '- 見出しはスフィンクスv03のGeorgia Bold／生成り #f4efdf／字高100px、x80–880・y330–1100内。0フレームから表示、2.0秒から0.3秒で消える。実フィルターのアルファ値をフレーム0–69で検査。',
    '- 冒頭は3本とも資料画像を1080×1920全面に配置、1.00→1.08倍。F3は色票を外した上下範囲（原画像y0.10–0.79）で絵の全高を残す。純粋な絵画部分（y0.185–0.763）は画面高の約83.8%。人物群のROIが全400フレームのカメラ範囲内にあることを検査。',
    '- 札・出典の本文は本編v02と同一。F1冒頭の欄のみ左側650px内にして鳥の顔を隠さない。F3はLoCのNo known restrictions on publication表記で、PD/CC0とは書かない。',
    '- F1のp61は本編の移動する拡大矩形の和集合（x0.065–0.795、y0.058–0.39）。原文を修正せずfowle〜fiue Deereの段落を同時に表示。D_youngは本編模式図の画素を切り出し、2つの年代のブロックを上下に並べ替えた。文章の追加・書き換えなし。',
    '- F2の宣言は第1頁全体からゆっくり寄る。last Thursdayへの拡大なし。F3の手紙見出しは本編と同じ矩形。',
    '- 台本と英語字幕は完全一致。各11字幕＋最後2秒のCTA、1行最大5語・最大2行。すべての字幕を実際のlibassで描画し、輪郭・影込みでx80–880、y1150–1450内。1621／1841／1863を数字だけで分離していない。',
    '- 0・0.5・1・1.5・2・2.5秒の計18枚、2秒おきの一覧を最終MP4の先頭からの連続デコードで作成・画面確認。顔の大写し・色票なし。', '',
    '## Claudeへの確認依頼と投稿予定','',
    '映像・台本・切替・字幕・出典を確認し、本人には3本の声とBGMの聴きやすさを確認してもらう。機械測定・静止画検査済みであり、人間による全編試聴済みとは扱っていない。', '',
    '承認済み予定：F1 11/2 18:00、F2 11/3 12:00、F3 11/3 18:00（JST）。関連動画は本編 HZsl96AigLY、11/2公開後に設定。**投稿は別依頼**。投稿前に当日の本編＋ショート合計≤3本、ショート≤2本を再照合。', '',
    f'Mac保存先：`{ROOT}`。再生入口：`deliverables/preview.html`。動画・音源・原寸素材はGitに含めず、縮小画像・台本・検査記録・スクリプトのみ共有。']
    (HERE/'wom_ショート制作結果_EP007_20261029.md').write_text('\n'.join(lines)+'\n')
    (DEST/'README.md').write_text(f'# Quiet Origins EP007 Shorts F1–F3 v01\n\n[制作結果](../wom_ショート制作結果_EP007_20261029.md)\n\n非公開Draft Release ID **{sharing["release_id"]}**。REST `GET /repos/yasukawa1980/youtube/releases/{sharing["release_id"]}` でasset一覧を取得し、asset ID指定で取得。Draft維持・YouTube未投稿。\n\nMac：`{ROOT}/deliverables/preview.html`\n\n[共有SHA256](deliverables/SHA256SUMS_shared.txt)／[REST照合](records/sharing_complete.json)\n')
    print('HANDOFF',DEST,flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
