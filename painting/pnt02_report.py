"""Write the current delivery report from measured QC and verified private release state."""
from pathlib import Path
from pnt02_produce import ROOT, REPO, read, save

OUT=REPO/'painting/pnt02_確認版_v01_20261110'


def main():
    summary=read(OUT/'final_summary.json')
    shared=read(OUT/'final_sharing.json')
    assert summary['technical_checks_passed'] and shared['status']=='v01_shared_pending_user_listening'
    visual=read(OUT/'final_visual_review.json')
    assert visual['reviewed']
    en,ja=[summary['languages'][l] for l in ['en','ja']]
    minimum_contrast=min(v['contrast_min'] for l in [en,ja] for v in l['variants'].values())
    minimum_padding=min(v['plate_padding_min'] for l in [en,ja] for v in l['variants'].values())
    maximum_motion=max(v['motion_max_ratio'] for l in [en,ja] for v in l['variants'].values())
    text=f'''# 絵画02 pnt02 確認版v01 制作結果（2026-11-10）

**動画5本を制作し、非公開Draft Release `{shared['release_id']}` へ追加。追加7資産すべてを数値Asset IDで再取得し、サイズとSHA-256一致を確認。本人の試聴待ち。**

取得は [確認版README](pnt02_確認版_v01_20261110/README.md)。旧 preliminary ZIP 2件は削除せず保全。Releaseはdraftのまま、匿名RESTは404。投稿・予約・Release公開・購入・アカウント作成なし。

保存先：`{ROOT}`。指定ESD-02のみ使用。既存台本v02・初回無置換音声・BGM・ブランド素材を維持。年代帯の訂正 `1238455` を反映し、再承認は求めていない。

## 完成した出力

- 英語1080p30、英語2160p30、日本語1080p30、英日1080p30字幕入り版：計5本。
- 英日WAV・M4A・SRT、サムネ2案と168px比較、英日投稿情報（各6章・12出典）。
- 最終動画からの18ショット×先頭・中央・末尾、冒頭0/1/2/3秒、各カード・年代帯状態、字幕サンプル。設計画像とは別の `final_video_review/`。

## §7の確認結果

|項目|英語|日本語|
|---|---:|---:|
|総尺|{en['duration_seconds']:.6f}秒|{ja['duration_seconds']:.6f}秒|
|30fpsフレーム数|{en['frames']:,}|{ja['frames']:,}|
|LUFS|{en['loudness']['input_i']}|{ja['loudness']['input_i']}|
|True Peak dBTP|{en['loudness']['input_tp']}|{ja['loudness']['input_tp']}|
|SRTページ数|{en['subtitle_pages']}|{ja['subtitle_pages']}|
|SRT最短秒|{en['subtitle_min_seconds']:.3f}|{ja['subtitle_min_seconds']:.3f}|
|1行最大文字数|{en['subtitle_max_line']}|{ja['subtitle_max_line']}|
|字幕と帯の最小間隔|{en['subtitle_min_clearance']}px|{ja['subtitle_min_clearance']}px|

- 全編H.264 High / yuv420p / 30fps CFR、映像形式1種類。英日1080pと英語4Kを先頭から連続デコード、警告0。字幕入り2本も全編デコード警告0。PTS・フレーム数・音声サンプル数を検証。
- 全ショット・共通OP/EDを個別デコードし、非圧縮フレームを単一エンコーダーへ渡した。エンコード2スレッド・小さいlookahead、書き出しは順番に実行。
- 全図2回、D1/D2/D3/room/V10各1回。禁止素材なし。P13〜P14は単一ショット。V10にLeutze表記なし、細部に人物名なし。最終動画の札・出典・カード・帯を元の正確な描画と数値照合し、一覧画像を目視確認。
- 最大原寸倍率0.9984。全図/D3の最小切り出し幅3846.154px・高さ2163.462px。縦素材は高さ2160px（1080p版1080px）、暗い無地背景。詳細は各 `art_scales*.json`。4Kの共通OP/EDだけは承認済み1080p素材のLanczos拡大。
- 細部登録は既存SIFTホモグラフィを再利用（画素の変形ではなく範囲測定）。D1/D2/D3のRMS残差1.019/0.898/0.904px。静的外周では24.145%だったD2/D3が動く画角で25.416%となったため、D3のパン開始を可動範囲の25%位置へ修正。英日すべてのフレーム組み合わせを測定し、D1/D2最大9.574%、D1/D3 0%、D2/D3最大{summary['maximum_actual_moving_overlap']*100:.3f}%で25%以内。`final_moving_overlap.json` に全組み合わせ数と最大時点。
- 字幕本文は空白・改行を除いて承認済み台本と完全一致。英語の年は読みの形のまま。2行以内。全144ページで最終字幕入り動画の表示と帯領域の非重複を検証。
- 文字カードの原文は指定と文字列一致。主要字高60px以上、コントラスト最小{minimum_contrast:.3f}、箱内最小余白{minimum_padding:g}px（1080p基準）。最終動画の全状態を描画と比較。
- 年代帯：P07全体/P10は強調なし。P08の1849は英170.200秒／日159.333秒、P12 todayは英246.866667秒／日234.866667秒。各 `rail_switches*.json` に全時刻。時刻は文音声・字幕ページ内の文字位置による補間で、語単位の強制アラインメントではない。
- 動く7ショットの全隣接フレームを測定。英日1080p・英語4Kの p95/中央値 最大{maximum_motion:.4f}（上限2.5）。静止カード・表示切替・共通OP/EDはこの指標の対象外。EDは総尺のちょうど10秒前から。
- 言語ごとに通常版と字幕入り版の音声ストリーム一致。英語4Kも英語1080pの音声と一致。−60dB以下で1秒以上の全ミックス無音0。

## 満たせなかった確認・本人への引き継ぎ

公式音声・辞書との実聴照合、固有名・難読語の試聴は未実施。この環境に音声を聴いて評価するツールがなく、聞いた資料は0件。本人の今回の指定に従って無置換音声のまま試聴へ回す。読み替え一覧は英日とも0件。`reading_review.json` に理由・対象語を記録。

本人はLeutze/Whittredge/Houdon/Düsseldorf/Bremenと年、日本語の渡河・砲兵・行軍・雹・大陸会議・決議・舵・旧邸など、年代帯と発話の厳密な同期、テンポ、縦置きの大きさ、文字カードの単調さ、P12展示室、サムネA/B、全編の連続再生を確認する。

Git共有は通常HEAD/インデックスを保持し、最新originを親に対象ファイルだけを別インデックスでコミットする。reset・force-push・worktreeなし。最終pushのコミットIDは実行後の報告を参照。
'''
    (REPO/'painting/pnt02_制作結果_v01_20261110.md').write_text(text)
    lines=['# pnt02 確認版v01 取得案内','',f'非公開Draft Release ID：`{shared["release_id"]}`。動画5本完成、本人試聴待ち。旧 preliminary ZIP は制作途中の履歴資料。公開しない。','',
        '[制作結果と未確認項目](../pnt02_制作結果_v01_20261110.md) · [最終数値](final_summary.json) · [再取得照合](final_sharing.json)','',
        '## 数値IDで取得','', '認証済みGitHub CLIで確認する。Releaseを公開する必要はない。','',
        '```sh',f'gh api repos/yasukawa1980/youtube/releases/{shared["release_id"]}',
        'gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/<Asset ID> > <保存名>','```','',
        '|ファイル|Asset ID|バイト数|','|---|---:|---:|']
    for asset in shared['assets']:lines.append(f'|{asset["name"]}|{asset["asset_id"]}|{asset["bytes"]:,}|')
    lines+=['','7資産すべて数値IDで再取得済み。サイズ・SHA-256一致。SHA-256全値は `final_sharing.json`。',
        '', '## レビュー画像・記録','',
        '- `en/final_video_review/`：英1080p・4Kの先頭/中央/末尾の一覧、カード状態、冒頭・字幕。',
        '- `ja/final_video_review/`：日本語1080pの同じ確認資料。',
        '- `continuous_*_sheet_*.jpg` は最終MP4から連続デコードした一覧。`design_*`・`card_*` は以前の設計画像。',
        '- 音声と字幕は `PNT02_audio_subtitles_final_v01.zip`。資料・サムネ・投稿情報は `PNT02_final_QC_metadata_thumbnails_v01.zip`。',
        '- 発音は未聴取。固有名、難読語、発話と帯の厳密な同期、テンポ、縦置き・文字カード、サムネA/Bは本人確認。','']
    (OUT/'README.md').write_text('\n'.join(lines))
    save(OUT/'resume_status.json',dict(status='v01_shared_pending_user_listening',chronology_resolved=True,
        owner_confirmation_required=False,script_changed=False,video_completed=True,release_updated=True,
        release_id=shared['release_id'],technical_checks_passed=True,pending=summary['pending']))
    path=REPO/'painting/pnt02_制作再開結果_20261110.md'
    old=path.read_text()
    marker='## 前回の環境停止記録（履歴）'
    if marker in old:old=old.split(marker,1)[1].lstrip()
    path.write_text(f'# pnt02 再開完了（2026-11-10）\n\n今回の通常実行ではESD-02への書き込み、.git更新、GitHub接続を確認。動画5本と検品を完了し、Draft Release {shared["release_id"]} に7資産を追加・再取得照合した。発音の実聴と本人試聴は未完了。詳細は [制作結果](pnt02_制作結果_v01_20261110.md)。\n\n{marker}\n\n'+old)
    print('REPORT WRITTEN',flush=True)


if __name__=='__main__':
    main()
