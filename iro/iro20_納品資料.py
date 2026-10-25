"""最終検品済みファイルから納品資料とMac側の写しをそろえる。"""
from pathlib import Path
import hashlib
import json
import shutil

import yaml

ROOT = Path(__file__).resolve().parents[1]
IRO = ROOT / 'iro'
YAML = IRO / 'volumes/iro20.yaml'


def main():
    cfg = yaml.safe_load(YAML.read_text()); base = Path(cfg['dir']); out = base / '投稿用'
    report = json.loads((IRO / 'iro20_完成検品.json').read_text())
    checks = report['checks']; main = checks['main']
    if set(checks) != set(['main', *'ABCD']) or not all(r['technical_pass'] for r in checks.values()):
        raise RuntimeError('完成5ファイルの技術検品が未合格')
    if not all(r['visual_review'] != 'pending' for r in checks.values()):
        raise RuntimeError('完成品の映像確認を記録してから資料を確定してください')
    selected = json.loads((IRO / 'iro20_選曲結果.json').read_text())
    cfg['status'] = 'files_delivered_technical_qc_pass_listening_pending'
    cfg['final'] = {'main': main['file'], 'duration_seconds': main['duration_seconds'],
        'lufs': main['lufs'], 'true_peak_dbtp': main['true_peak_dbtp'],
        'selected_tracks': 31, 'generated_candidates': 42, 'technical_pass': True,
        'direct_listening': 'not_performed', 'user_full_viewing': 'pending',
        'shorts': {tag: checks[tag]['file'] for tag in 'ABCD'}}
    YAML.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))
    metrics = f"映像尺2:00:17.625（コンテナ{main['duration_seconds']:.3f}秒）／{main['lufs']:.2f} LUFS／TP {main['true_peak_dbtp']:.2f} dBTP／映像{main['video_bitrate_bps']/1e6:.3f} Mbps"
    shortrows = '\n'.join(f"|{t}|{checks[t]['duration_seconds']:.3f}秒|{checks[t]['lufs']:.2f}|{checks[t]['true_peak_dbtp']:.2f}|" for t in 'ABCD')
    summary = f"""# IRO20 検品要約

作品：**しおりを挟むには、まだ早い。**／PLUM／夜の読書／室内楽チル。
新キャラ案1の成人ボブ女性＋大型ゴールデンを第一参照。窓ベンチは新規構図。

- 本編：{metrics}。1920×1080・24fps・{main['frames']}コマ。扉v5、最後15秒カード。
- 本編＋15秒ショート4本：最終AACを区切らず全体測定、映像・音声全編デコードすべて終了0・エラーログ0。aac_at使用。詳細は `iro20_完成検品.json`。
- 音楽：42候補を全編自動検査、31曲採用。Aハープ6／Bファゴット5／Cチェレスタ6／Dマンドリン5／Eトロンボーン6／Fハーモニウム3（楽器名は生成指示）。同じ種類の隣接・1曲おきなし、31曲のデコードPCM重複なし、4秒クロスフェード。同曲2巡なし。
- **直接聴取・音楽的評価・厳密な楽器同定は未実施。この接続は音声入力非対応。自動検査合格を聴感合格とは扱わない。本人の通し視聴待ち。**
- Kling：B1/B2土台、A窓を見る、B犬へ微笑む、C大きなあくび、D犬が目を開ける。6原本保存。B1は目元だけ長い閉眼を短縮し頭の時間は保全。背景固定・人物犬マスクで8部品を作成。全コマ検査、固定背景ずれ最大0.000367px、始終MAE約0.05/255。Cは静止待ち3秒を除き動作前から再構成。
- 犬ショート：608×1080切り抜き、端延長なし。動作範囲の左右余白80/90px、全身と尾を確認。完成品の4秒コマと土台顔8秒3fpsは見本JPGに収録。
- 画像：開始v03の暗部16未満2.7035%、250以上0.0128%。横サムネ1280×720・311912 bytes。新キャラは今回の試行採用のみ。
- 費用：Suno210/300（9760→9550、DL残8）、Kling384/512（本人補充後1404→1020）。Codex購入なし。
- 保存：Mac `{base}`。ESD-EPB未接続・未同期。YouTube投稿・予約・公開なし。Claude添削未実施。
"""
    (IRO / 'iro20_検品/Claude検品用_要約.md').write_text(summary)
    guide = f"""# IRO20 納品案内

「しおりを挟むには、まだ早い。」／Too Early for a Bookmark.
夜の読書向け室内楽チル。新しいボブの成人女性と大型ゴールデンを試行採用。

**完成ファイルの技術検品と映像確認済み。直接聴取は未実施、本人の通し視聴待ち。YouTube未投稿。**

## 視聴とファイル

- [通し視聴用・本編]({main['file']})：{metrics}。
- [構成確認用・110秒抜粋]({out / 'iro20_完成確認_抜粋110秒.mp4'})：導入、出来事4種、最後20秒。本編の通し視聴を代替しない。
- [本編サムネ]({out / 'iro20_サムネ.jpg'})／[ショート共通サムネ]({out / 'iro20_ショート共通サムネ.jpg'})。
"""
    guide += '\n'.join(f"- [ショート{tag}・15秒]({checks[tag]['file']})" for tag in 'ABCD')
    guide += f"""

A・Bはファイル名末尾が `_v02.mp4` のものを採用。番号なしA・Bは音量調整前の初稿保全用で、投稿対象外。

## 実測検品

本編は1920×1080、ショートは1080×1920、全て24fps。AAC 48kHzステレオ。
5ファイルとも最終AAC全体の連続測定、映像・音声の全編デコードを実施。デコードエラー0。

|ショート|コンテナ実尺|LUFS|dBTP|
|---|---:|---:|---:|
{shortrows}

各ショートの映像は360コマ＝15.000秒。コンテナの15.019秒はAAC末尾の余白を含む。

42候補から31曲を選定し、4秒クロスフェードで連結。全曲別・2巡なし。
自動検査では設定した閾値での人声・途中無音・末尾の警告なし。音色、自然さ、不要音の聴感確認は未実施。生成指示どおりの楽器であると断定していない。

## 投稿資料と保存

`iro20_アップロード情報.md` と `iro20_ショート_アップロード情報.md` に日英タイトル・説明・タグ・章・既存再生リスト案を記載。設定yaml、全プロンプト、クレジット台帳、選曲結果、生成曲一覧、検品JSON、制作記録とClaude用見本を同梱。

Mac保存先：`{base}`。原音42曲、Kling6原本、開始画像の全版を保全。既存作品の移動・削除なし。中間ファイルは `_work/` として保持し、Codexは削除していない。
指定ESD-EPBは未接続のため未同期。ESD-02へは代用コピーしていない。
GitHub `yasukawa1980/youtube` の `bgm/production` に資料と確認画像を共有。動画・音源・高解像度画像はGit対象外。

YouTubeへのアップロード・予約・公開、既存投稿設定の変更は行っていない。公開日は本人の通し視聴後に別途決める。各チャンネルは日本時間1日合計3本以内、ショート2本以内。
"""
    (IRO / 'iro20_納品案内.md').write_text(guide)
    record = f"""# IRO20 制作記録

2026-10-25企画開始、10-26制作。完成ファイルの技術検品・映像確認済み。直接聴取と本人通し視聴は未実施。YouTube未投稿。

## 企画・素材

引き継ぎ全文と適用AGENTS、検品基準、直近15〜19の設計・音楽・開始画像、IRO18修正、10/25分析・予約記録を調査。比較3案を画像で確認。案1をキャラと画風の第一参照にし、窓ベンチの新規構図を採用した。題は「しおりを挟むには、まだ早い。」、用途は夜の読書、PLUM、室内楽チル、約2時間、タイマーなし。

内蔵image_gen6回。開始v01は犬の幅、v02は暗部15.6107%のため修正し、v03を採用。原本1672×941、暗部2.7035%、明部0.0128%。横サムネv02は作品名を小さな4行目へ追加。用途を大きく表示し、168pxでも用途見出しを確認。全原本を保全。共通扉v5は短髪・白い服の背面人物で、お団子の旧主人公ではない。ブランド導入として保持し、全体の連続見本を確認した。

## 生成・選曲

本人承認Suno300／Kling512、Codex購入なし。Suno認証は本人対応で解消し、計42候補を生成・WAV保存。残高9760→9550で210消費、通常DL50→8、自動リロードOFFを確認。F初期は弦系の分類が続き保留。除外欄を補強しF04〜06を追加、オルガン系分類を含む3曲を採用。最終31曲の内訳A6/B5/C6/D5/E6/F3。自動分類は楽器同定の証明とはしない。

全42曲を最後まで10秒窓・5秒刻みAST、途中無音、末尾、LUFS/TP、高域で検査。31曲のPCMハッシュ重複なし。同じ種類を隣と1曲おきに置かず、4秒クロスフェード、曲別と連結後のラウドネスを調整。最終曲を音楽2時間到達前の10秒フェードで閉じる。同曲の2巡なし。選曲は自動衛生指標・尺・種類分散に基づき、音楽的な直接聴取は未実施。

この接続では15秒の音声入力試行も非対応だった。聴取済みとは記録せず、本人へ2分試作を提示し、最終本編・ショートも聴けるファイルで用意した。本人の通し視聴前に公開しない。

## 映像・修正

Kling3.0、1080p、8秒、音声OFF、開始=終了画像、各64で6本。本人補充後1404→1020、384消費。B1/B2は土台、A窓、B犬へ微笑む、C大きなあくび、D犬が目を開ける。公式DownloadがChromeで遮断されたA以降は、本人承認に基づき画面表示済みの公開mp4 URLを素材IDと照合して直接保存。内部API・認証情報の取得なし。

B1は長い閉眼を目元だけ追跡補正。頭・呼吸・手の時間を変えず、圧縮前の目元外の差0、追跡最大誤差0.1118px。6原本と補正素材をMacに保存。人物・犬の範囲だけを合成し、背景はB1開始画へ固定。マスクはぼかした後にも外側を制限。8種類各192コマを全コマ解析、固定背景ずれ最大0.000367px、始終MAE約0.05/255。先頭・末尾10コマを基準画へなじませた。Cは静止待ち3秒を除き動作直前から8秒単位を作り直した。

土台は不規則に並べ、同じ土台が3連続しない。出来事は重ねず10分周期で4種類を配置。扉と間543コマ、本体172680コマ、合計173223コマ。x264 CRF12の部品を連結し、最後15秒に専用背景の共通配置カードを表示。共通素材は上書きなし。

ショートは本編の出来事単位の頭から各15秒。608×1080で切り抜き、1080×1920へ拡大、端画素の延長なし。犬は尾を含む全身、動作範囲の左右余白80/90px。音源はA-01b/C-01a/D-01b/E-01bの各30秒地点から15秒で別種類。文字はA/Bが下、C/Dが上の帯に配置し顔や犬を避ける。A初稿はebur128で−14.8 LUFS、Bは−14.5だったため、初稿を残してA+0.8dB／B+0.5dBとリミッターの天井を調整したv02を採用。最終判定は別途loudnormの全体測定値で実施し、測定方式の異なる値を混同しない。

## 完成検品・納品

本編：{metrics}。ショート4本は全て15秒・360コマ。
最終AACはaac_atで書き出し、区切らず全体測定。完成5ファイルの映像・音声を全編デコードして終了0・エラー0。LUFSとTPは `iro20_完成検品.json` に記載。映像確認の範囲と未実施の直接聴取を分けて記録した。

Mac `{base}` に本編・110秒確認抜粋・横縦サムネ・4ショート・投稿情報と記録の写しを保存。Claude用1ページ要約と、開始画像・サムネ・168px・ショート4秒・女性顔8秒3fpsの見本を作成。Claude添削は未実施。本人から利用解除の連絡はなく、それを待たず制作を継続した。

指定ESD-EPBは未接続・未同期。既存ファイルの移動・削除なし。ローカルの分岐履歴をpushせず、remote最新起点の共有worktreeへ対象資料だけ適用。reset・force-pushなし。大容量素材・秘密情報はGit対象外。

中間のnorm WAV、music_bed、8秒部品、補助PNG、ブラウザ保存原本等は保全。再編集に使うため自動削除しない。YouTube投稿・予約・公開・設定変更なし。
"""
    old = IRO / 'iro20_制作記録.md'; archive = IRO / '_work/iro20/制作記録_制作途中.md'
    if old.exists() and not archive.exists(): shutil.copy2(old, archive)
    old.write_text(record)
    (IRO / 'iro20_再開メモ.md').write_text('# IRO20 再開メモ\n\n完成ファイルと技術検品を納品。直接聴取・本人の通し視聴・SSD同期は未完了。次回は iro20_納品案内.md と iro20_完成検品.json を先に読む。本人の指摘があれば元素材を保全して修正し、変更後のファイルだけ再検品する。YouTube投稿等は別依頼。\n')
    # 納品資料の写し。生成素材は元の場所のまま保持する。
    docs = sorted(p for p in IRO.glob('iro20_*') if p.suffix in ['.md', '.json'])
    docs += [YAML, *sorted((IRO / 'iro20_検品').glob('*'))]
    for p in docs:
        if p.is_file(): shutil.copy2(p, out / p.name)
    files = []
    for p in sorted(out.iterdir()):
        if not p.is_file() or p.name == 'iro20_納品一覧.json': continue
        h = hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda: f.read(4 * 1024 * 1024), b''): h.update(chunk)
        role = 'supporting_document_or_preview'
        if str(p) in [row['file'] for row in checks.values()]: role = 'final_video'
        if p.name in ['iro20_ショート_A.mp4', 'iro20_ショート_B.mp4']: role = 'superseded_preserved_do_not_upload'
        files.append({'path': str(p), 'role': role, 'bytes': p.stat().st_size, 'sha256': h.hexdigest()})
    manifest = {'delivery_status': cfg['status'], 'direct_listening': 'not_performed',
                'ssd_sync': 'not_synced', 'youtube_uploaded': False, 'files': files}
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    (IRO / 'iro20_納品一覧.json').write_text(text); (out / 'iro20_納品一覧.json').write_text(text)
    print('delivery files', len(files), flush=True)


if __name__ == '__main__':
    main()
