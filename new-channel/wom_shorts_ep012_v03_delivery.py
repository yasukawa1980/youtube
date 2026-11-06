"""EP012 N1 v03を新規非公開Draftへ共有し、取得照合と申し送りを行う。"""
import argparse
import shutil
import zipfile
from PIL import Image
from wom_shorts_ep012_v03 import ROOT,OLD,REPO,REQUEST,DEST,TAG,read,save,sha,video
import wom_shorts_ep012_v02_delivery as delivery

def package():
    qc=read(ROOT/'records/final_qc.json');assert len(qc)==1
    q=qc[0];assert q['outside_patch_all_frames_identical'] and q['audio_pcm_identical'] and q['warning_count']==0
    assert read(ROOT/'records/visual_review.json')['passed']
    save(ROOT/'records/approval.json',dict(request_sha256=sha(REQUEST),user_instruction='クロードの修正依頼を確認して進めて下さい',scope='N1の冒頭の絵を73px下げる。N2 v01・N3 v02は合格済み版を継続。',youtube_posted=False,human_full_listening=False,claude_review_pending=True))
    for p in ROOT.glob('review/*.jpg'):assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
    members=sorted([*ROOT.glob('records/*.json'),ROOT/'records/request.md',*ROOT.glob('review/*.jpg'),*ROOT.glob('deliverables/*.srt'),*ROOT.glob('deliverables/*.md')])
    members=[p for p in members if p.name not in ['sharing.json','delivery_files.json']]
    archive=ROOT/'deliverables/EP012_N1_review_v03.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in members:z.write(p,p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    save(ROOT/'records/delivery_files.json',[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in [video('N1','v02'),archive]])
    print('共有用2添付を作成',flush=True)

def share():
    delivery.ROOT=ROOT;delivery.TAG=TAG
    delivery.RELEASE_NAME='Quiet Origins 第12話ショート N1 確認版v03（出典との間隔修正・未投稿）'
    delivery.RELEASE_BODY='N1の冒頭の絵を73px下げ、出典最下行の下端y=233と絵上端y=253の間を20px確保。大きさ・寄り・音声・字幕・尺はv02と同一。変更区間外466フレームが完全一致。N2 v01・N3 v02は合格済み版を継続。本人試聴・Claude確認待ち。YouTube未投稿・未予約。'
    delivery.share()

def report():
    shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified' and len(shared['assets'])==2
    for d in ['records','確認画像','deliverables']:(DEST/d).mkdir(parents=True,exist_ok=True)
    for p in ROOT.glob('records/*.json'):shutil.copy2(p,DEST/'records'/p.name)
    for p in ROOT.glob('review/*.jpg'):shutil.copy2(p,DEST/'確認画像'/p.name)
    for p in ROOT.glob('deliverables/*'):
        if p.suffix in ['.srt','.md']:shutil.copy2(p,DEST/'deliverables'/p.name)
    (DEST/'SHA256SUMS_shared.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in shared['assets']))
    note=f"""# 第12話ショート N1 確認版v03

**出典と絵の重なり修正・検品・非公開共有済み。本人試聴・Claude確認待ち。YouTube未投稿・未予約。N2 v01・N3 v02を継続。**

[Draft Release]({shared['release_url']}) — Release ID **{shared['release_id']}**。MP4 1本と確認ZIPの2添付をRelease ID指定RESTで列挙・再取得し、SHA-256・サイズ一致、匿名404を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/{shared['release_id']}
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
"""
    for a in shared['assets']:note+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
    note+='\n[SHA-256一覧](SHA256SUMS_shared.txt)／[修正結果](../wom_ショート制作結果_EP012_v03_20261107.md)／[N2 v01](../wom_ショート確認版_EP012_v01_20261106/README.md)／[N3 v02](../wom_ショート確認版_EP012_v02_20261107/README.md)。ZIPには指定時刻の画像・出典部分の拡大画像・座標・倍率・全フレーム比較・音声一致記録を収録。\n'
    (DEST/'README.md').write_text(note)
    q=read(ROOT/'records/final_qc.json')[0]
    text=f"""# Quiet Origins 第12話ショート N1 v03 修正結果（2026-11-07）

**[Claudeの修正依頼](wom_ショートClaude確認_EP012_v02_20261107.md)を反映し、検品と新規非公開共有を完了。** [動画・確認ZIPの取得](wom_ショート確認版_EP012_v03_20261107/README.md)。本人試聴・Claude確認待ち。YouTube未投稿・未予約。

## 修正と実測

N1冒頭のN08_personを **73px下**へ移動。出典最下行の下端は **y=233**、絵の上端は **y=253**、間隔は **20px**。幅1080px・高さ950px、最大倍率1.5264倍、寄り1.00→1.06倍、元の切り出し範囲はv02と同じ。変更した描画パラメータは絵のy座標だけ。

0・0.5・1.0・2.5秒と寄り終点の完成画像を確認。出典が絵から離れ、人物の顔と赤い上着は見出しの板に重ならない。絵下端はy=1203となり、最上部の字幕板（y=1178）に背景の余白部分が25px重なる。人物や上着はその範囲に入らず、字幕レイヤー・位置は維持。字幕のコントラストも4.5以上を確認。

## v02との一致検証

| 項目 | 結果 |
|---|---|
| 形式 | 1080×1920、30fps、H.264 High、yuv420p |
| 尺・フレーム数 | **20.900秒・627フレーム**、v02と同一 |
| 変更区間 | 0〜161フレーム（終端除外、0〜5.366667秒） |
| 変更区間外 | **466フレームすべて、PTSとデコード画像MD5が一致** |
| 音声 | 元AACをコピー。AAC SHA-256・デコードPCM MD5ともv02と一致 |
| 字幕 | SRTのSHA-256一致。焼き込み字幕・見出し・案内の画像と時刻も維持 |
| 音量 | {q['audio']['input_i']} LUFS / {q['audio']['input_tp']} dBTP |
| 連続デコード | 警告0 |

共通AAC SHA-256：`{q['aac_sha256']}`。共通PCM MD5：`{q['audio_pcm_md5_v03']}`。対象ショットのみ再描画し、以降の映像と音声はストリームコピー。N2 v01・N3 v02のMP4もハッシュ不変を確認し、合格済み版を継続。

## 確認画像

- [指定時刻の一覧](wom_ショート確認版_EP012_v03_20261107/確認画像/N1_requested_times.jpg)：0・0.5・1.0・2.5秒に加えて1.5・2.0秒も収録。
- [0.5秒の出典周辺](wom_ショート確認版_EP012_v03_20261107/確認画像/N1_0015_header_detail.jpg)：完成MP4から原寸の横1000×縦300pxを切り出し。
- 全字幕ページ・案内表示中の画像と検品JSONを同梱。本人による全編試聴は未実施。声とテンポはv01・v02でも確認可能。

## 保存・共有

SSD：`{ROOT}`。新規非公開Draft Release **{shared['release_id']}**。MP4＋確認ZIPの2添付をRESTで再取得し、サイズとSHA-256一致、匿名404を確認。v01・v02の動画と既存Releaseは保全。Gitには制作スクリプト・字幕・縮小JPG・検品記録を共有。

公開案はN1 11/14 18:00、N2 11/15 12:00、N3 11/16 12:00 JSTを維持。投稿・予約は行っていない。本編の日本語音声を追加しない方針（2026-11-07本人了承）も確認済み。
"""
    (REPO/'wom_ショート制作結果_EP012_v03_20261107.md').write_text(text)
    print('共有報告を作成',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['package','share','report']);a=p.parse_args();globals()[a.stage]()
