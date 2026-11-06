"""EP012の拡大修正2本を非公開共有し、RESTで再取得照合する。"""
import argparse
import hashlib
import shutil
import subprocess
import time
import zipfile
from pathlib import Path
from PIL import Image
from wom_shorts_ep012_v02 import ROOT,OLD,REPO,REQUEST,DEST,TAG,IDS,read,save,sha,video
from wom12_share import api,assert_anonymous_hidden


def package():
    qc=read(ROOT/'records/final_qc.json');assert len(qc)==2
    assert all(q['outside_patch_all_frames_identical'] and q['audio_pcm_identical'] and q['warning_count']==0 for q in qc)
    assert read(ROOT/'records/visual_review.json')['passed']
    for name in ['caption_manifest.json','cta_design.json','shorts.json','headlines.json']:
        shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
    save(ROOT/'records/approval.json',dict(request_sha256=sha(REQUEST),user_instruction='クロードからの修正依頼を確認して進めて下さい',scope='N1人物・N3トナカイの拡大のみ。N2はv01を継続。',youtube_posted=False,human_full_listening=False,claude_review_pending=True))
    members=sorted([*ROOT.glob('records/*.json'),ROOT/'records/request.md',*ROOT.glob('review/*.jpg'),*ROOT.glob('deliverables/*.srt'),*ROOT.glob('deliverables/*.md')])
    members=[p for p in members if p.name not in ['sharing.json','delivery_files.json']]
    for p in ROOT.glob('review/*.jpg'):assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
    archive=ROOT/'deliverables/EP012_shorts_review_v02.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in members:z.write(p,p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    files=[*[video(sid,'v02') for sid in IDS],archive]
    save(ROOT/'records/delivery_files.json',[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files])
    print('PACKAGED',len(files),'assets',flush=True)


def share():
    repo='yasukawa1980/youtube';files=read(ROOT/'records/delivery_files.json')
    for f in files:assert sha(ROOT/'deliverables'/f['file'])==f['sha256']
    releases=api([f'repos/{repo}/releases?per_page=100']);r=next((r for r in releases if r['tag_name']==TAG),None)
    if r is None:
        r=api(['--method','POST',f'repos/{repo}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins 第12話ショート N1・N3 確認版v02（絵の拡大・未投稿）',body='N1の人物は表示幅1080px・最大1.5264倍、N3のトナカイは最大1.6倍・字幕との間隔13px。対象以外の全907フレーム・音声・字幕がv01と一致。N2は合格済みv01を継続。本人試聴・Claude確認待ち。YouTube未投稿・未予約。',draft=True))
    assert r['draft'];assert_anonymous_hidden(f'repos/{repo}/releases/{r["id"]}')
    state=dict(release_id=r['id'],release_url=r['html_url'],tag=TAG,draft=True,status='uploading',assets=[]);save(ROOT/'records/sharing.json',state)
    for f in files:
        asset=next((a for a in r['assets'] if a['name']==f['file']),None)
        if asset:assert asset['digest']=='sha256:'+f['sha256']
        else:subprocess.run(['gh','release','upload',TAG,str(ROOT/'deliverables'/f['file']),'--repo',repo],check=True)
        print('UPLOADED',f['file'],flush=True)
    r=api([f'repos/{repo}/releases/{r["id"]}']);assert r['draft'] and len(r['assets'])==3
    for f in files:
        a=next(a for a in r['assets'] if a['name']==f['file'])
        for attempt in range(3):
            h=hashlib.sha256();n=0
            p=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{repo}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE)
            for b in iter(lambda:p.stdout.read(1048576),b''):h.update(b);n+=len(b)
            ok=p.wait()==0 and n==f['bytes'] and h.hexdigest()==f['sha256']
            if ok:break
            time.sleep(2)
        assert ok and a['digest']=='sha256:'+f['sha256']
        assert_anonymous_hidden(f'repos/{repo}/releases/assets/{a["id"]}')
        state['assets'].append(dict(name=f['file'],asset_id=a['id'],bytes=n,sha256=f['sha256'],rest_download_verified=True,anonymous_http_status=404))
        state['status']='verifying';save(ROOT/'records/sharing.json',state)
        print('REST VERIFIED',f['file'],flush=True)
    state['status']='verified';save(ROOT/'records/sharing.json',state)


def report():
    shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified' and len(shared['assets'])==3
    for d in ['records','確認画像','deliverables']:(DEST/d).mkdir(parents=True,exist_ok=True)
    for p in ROOT.glob('records/*.json'):shutil.copy2(p,DEST/'records'/p.name)
    for p in ROOT.glob('review/*.jpg'):shutil.copy2(p,DEST/'確認画像'/p.name)
    for p in ROOT.glob('deliverables/*'):
        if p.suffix in ['.srt','.md']:shutil.copy2(p,DEST/'deliverables'/p.name)
    (DEST/'SHA256SUMS_shared.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in shared['assets']))
    note=f"""# 第12話ショート N1・N3 確認版v02

**絵の拡大修正・検品・非公開共有済み。本人試聴・Claude確認待ち。YouTube未投稿・未予約。N2は合格済みv01を継続。**

[Draft Release]({shared['release_url']}) — Release ID **{shared['release_id']}**。MP4 2本と確認ZIPの全3添付を、Release ID指定RESTで列挙・再取得し、SHA-256とサイズ一致、匿名404を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/{shared['release_id']}
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>
```

| ファイル | asset ID | bytes |
|---|---:|---:|
"""
    for a in shared['assets']:note+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
    note+='\n[SHA-256一覧](SHA256SUMS_shared.txt)／[修正結果](../wom_ショート制作結果_EP012_v02_20261107.md)／[N2 v01取得先](../wom_ショート確認版_EP012_v01_20261106/README.md)。確認ZIPには指定時刻の画像・全字幕ページ・座標・倍率・全フレーム比較・音声一致記録を収録。\n'
    (DEST/'README.md').write_text(note)
    qc=read(ROOT/'records/final_qc.json');layout=read(ROOT/'records/layout.json')
    text='''# Quiet Origins 第12話ショート N1・N3 v02 修正結果（2026-11-07）

**Claude指定の拡大修正・検品・新規非公開共有を完了。** [修正依頼](wom_ショートClaude確認_EP012_v01_20261106.md)を反映。[動画・確認ZIPの取得](wom_ショート確認版_EP012_v02_20261107/README.md)。本人試聴・Claude確認待ち。YouTube未投稿・未予約。

## 修正内容

- **N1：N08_person** の原画750×660pxの切り出し範囲を維持し、表示幅1080px・y=180〜1130へ拡大。0秒から1.00→1.06倍でゆっくり寄り、原画に対する最大倍率は **1.5264倍**。見出しは既存の板つきのまま。顔と赤い上着に見出しが重ならないことを指定時刻の完成画像で確認。
- **N3：N08_reindeer** は最大 **1.6000倍**。角と足先を残して上下の背景を65px・75px詰め、原画の620×730pxから620×590pxを使用。表示は幅972px（画面幅90%）・高さ925px、y=240〜1165。緩い寄り1.00→1.020576倍で最大倍率に到達。上部クレジット下端から7px、字幕板上端から最短 **13px** を確保。人物の範囲は含めていない。
- 拡大は通常の **Lanczos**。AI補間・画像生成なし。原画像はv01と同一。

N1の「But look at」以降の表紙・本文、N3の最初と最後の文字カードはそのまま。N2は合格済みv01を継続。日本語字幕（英語の時間割）は合格済みRelease **436614416**／SHA-256先頭 `910fca54` を継続する。

## 実測と一致確認

| ID | 尺 | フレーム数 | 最大倍率 | LUFS | dBTP | 修正区間以外の一致フレーム数 |
|---|---:|---:|---:|---:|---:|---:|
'''
    for q in qc:text+=f"| {q['id']} | {q['duration_seconds']:.3f}秒 | {q['video_format']['nb_frames']} | {q['native_max_scale']:.4f} | {q['audio']['input_i']} | {q['audio']['input_tp']} | {q['outside_patch_frame_count']} |\n"
    text+='''
1080×1920・30fps・H.264 High・yuv420p。全編の連続デコード警告0。全フレームのPTS・枚数・尺がv01と同一。対象ショットのみを再描画し、他の閉じたIDR区間をストリームコピー。完成映像をYUV420pへデコードして比較し、修正区間外の合計 **907フレームが完全一致**。

元MP4のAACをストリームコピーし、AAC SHA-256とデコード後PCM MD5の両方がv01と一致。SRTもSHA-256一致。台本・音声・字幕・見出し・案内の文字、画像レイヤー、表示時間は既存データをそのまま使用。N2のMP4ハッシュも不変。字幕・見出しのコントラストは完成フレームで4.5以上を確認。カメラ移動は全フレームの原画座標変化を測定（光学フロー検査ではない）。

| ID | 変更区間（0起算、終端除外） | 共通AAC SHA-256 |
|---|---|---|
'''
    for q in qc:text+=f"| {q['id']} | {q['changed_start_frame']}〜{q['changed_end_frame_exclusive']}フレーム（{q['changed_start_frame']/30:.6f}〜{q['changed_end_frame_exclusive']/30:.6f}秒） | `{q['aac_sha256']}` |\n"
    text+='''
## 確認画像

- [N1：0・0.5・1.0・1.5・2.0・2.5秒](wom_ショート確認版_EP012_v02_20261107/確認画像/N1_requested_times.jpg)。各時刻の個別JPGも同梱。
- [N3：「In eighteen twenty-one」開始から2秒おき](wom_ショート確認版_EP012_v02_20261107/確認画像/N3_requested_times.jpg)。開始8.033333秒、10.033333秒、12.033333秒。寄り終点13.900秒の画像も同梱。
- 全字幕ページの中間と案内開始・末尾の完成画像も収録。長辺1280px以下、1枚1MB未満。顔と上着の見出し回避、トナカイの角・足先、字幕板との間隔を目視確認。本人による全編試聴は未実施。声とテンポはv01で試聴可能。

'''
    text+=f"## 保存・共有\n\nSSD：`{ROOT}`。新規非公開Draft Release **{shared['release_id']}**。MP4 2本＋確認ZIPの3添付をREST再取得し、サイズ・SHA-256一致、匿名404を確認。v01動画と既存Releaseは保全。Gitには制作スクリプト・字幕・縮小確認画像・検品記録を共有。公開案はN1 11/14 18:00、N2 11/15 12:00、N3 11/16 12:00 JSTのまま。投稿・予約は行っていない。\n"
    (REPO/'wom_ショート制作結果_EP012_v02_20261107.md').write_text(text)
    print('共有報告を作成',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['package','share','report']);a=p.parse_args();globals()[a.stage]()
