"""EP013 v02：検品済み3本をDraft限定で共有し、ID指定RESTで全量照合する。"""
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from PIL import Image
from wom_shorts_ep013_v02 import ROOT, OLD, REPO, REQUEST, read, save, sha, guard
from wom12_share import api, assert_anonymous_hidden

TAG='quiet-origins-ep013-shorts-v02-20261108'
DEST=REPO/'wom_ショート確認版_EP013_v02_20261108'

def package():
    guard()
    qc=read(ROOT/'records/final_qc.json')
    assert len(qc)==3 and all(q['continuous_decode_warning_count']==0 for q in qc)
    assert read(ROOT/'records/final_pixel_motion.json')['passed']
    assert read(ROOT/'records/visual_review.json')['passed']
    assert all(q['aac_identical'] and q['pcm_identical'] for q in read(ROOT/'records/audio_v01_v02_comparison.json'))
    # 字幕は既存caption_manifestのテキスト・フレーム時刻をそのまま外部SRTへ転記。
    caps=read(ROOT/'records/caption_manifest.json')
    def stamp(n):
        ms=round(n/30*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
        return f'{h:02}:{m:02}:{s:02},{ms:03}'
    for sid in ['V1','V2','V3']:
        cs=[c for c in caps if c['short_id']==sid]
        (ROOT/f'deliverables/QO_short_EP013_{sid}_v02.srt').write_text('\n\n'.join(
            f"{i+1}\n{stamp(c['start_frame'])} --> {stamp(c['end_frame'])}\n"+'\n'.join(c['lines']) for i,c in enumerate(cs))+'\n')
    members=sorted([*ROOT.glob('records/*.json'),ROOT/'records/request.md',*ROOT.glob('review/**/*.jpg'),*ROOT.glob('deliverables/*.srt')])
    members=[p for p in members if p.name not in ['sharing.json','delivery_files.json']]
    archive=ROOT/'deliverables/EP013_shorts_review_v02.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in members:
            if p.suffix=='.jpg':
                with Image.open(p) as im:assert max(im.size)<=1280
                assert p.stat().st_size<1000000
            z.write(p,p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    files=[ROOT/f'deliverables/QO_short_EP013_{sid}_v02.mp4' for sid in ['V1','V2','V3']]+[archive]
    save(ROOT/'records/delivery_files.json',[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files])
    print('確認ZIPとMP4 3本を梱包',flush=True)

def share():
    guard();repo='yasukawa1980/youtube';files=read(ROOT/'records/delivery_files.json')
    for f in files:assert sha(ROOT/'deliverables'/f['file'])==f['sha256']
    releases=api([f'repos/{repo}/releases?per_page=100']);r=next((r for r in releases if r['tag_name']==TAG),None)
    if r is None:
        r=api(['--method','POST',f'repos/{repo}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',
            name='Quiet Origins 第13話ショート V1〜V3 確認版v02（未投稿）',
            body='承認済みの画角修正と家族アルバムカード切り替え。音声AAC・PCMと字幕はv01一致。3本の全編検品済み。本人試聴・Claude確認待ち。YouTube未投稿・未予約。',draft=True))
    assert r['draft'];assert_anonymous_hidden(f'repos/{repo}/releases/{r["id"]}')
    state=dict(release_id=r['id'],release_url=r['html_url'],tag=TAG,draft=True,status='uploading',assets=[])
    save(ROOT/'records/sharing.json',state)
    for f in files:
        guard();asset=next((a for a in r['assets'] if a['name']==f['file']),None)
        if asset:assert asset['digest']=='sha256:'+f['sha256']
        else:subprocess.run(['gh','release','upload',TAG,str(ROOT/'deliverables'/f['file']),'--repo',repo],check=True)
        print('UPLOADED',f['file'],flush=True)
    r=api([f'repos/{repo}/releases/{r["id"]}']);assert r['draft'] and len(r['assets'])==len(files)
    for f in files:
        guard();a=next(a for a in r['assets'] if a['name']==f['file']);h=hashlib.sha256();n=0
        p=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{repo}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE)
        for b in iter(lambda:p.stdout.read(1048576),b''):h.update(b);n+=len(b)
        assert p.wait()==0 and n==f['bytes'] and h.hexdigest()==f['sha256']
        assert a['digest']=='sha256:'+f['sha256']
        assert_anonymous_hidden(f'repos/{repo}/releases/assets/{a["id"]}')
        state['assets'].append(dict(name=f['file'],asset_id=a['id'],bytes=n,sha256=f['sha256'],rest_download_verified=True,anonymous_http_status=404))
        save(ROOT/'records/sharing.json',state);print('REST VERIFIED',f['file'],flush=True)
    state['status']='verified';save(ROOT/'records/sharing.json',state)

def report():
    guard();shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified' and len(shared['assets'])==4
    qc=read(ROOT/'records/final_qc.json');layout=read(ROOT/'records/layout_v02.json')
    for d in ['records','確認画像','deliverables']:(DEST/d).mkdir(parents=True,exist_ok=True)
    for p in ROOT.glob('records/*.json'):shutil.copy2(p,DEST/'records'/p.name)
    for p in ROOT.glob('review/*.jpg'):
        if not p.name.endswith('_design.jpg'):shutil.copy2(p,DEST/'確認画像'/p.name)
    for rel in ['V1_frames/0412.jpg','V1_frames/0644.jpg','V2_frames/0000.jpg','V3_frames/0075.jpg','V3_frames/0412.jpg']:
        p=ROOT/'review'/rel;shutil.copy2(p,DEST/'確認画像'/rel.replace('/','_'))
    for p in ROOT.glob('deliverables/*.srt'):shutil.copy2(p,DEST/'deliverables'/p.name)
    (DEST/'SHA256SUMS_shared.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in shared['assets']))
    note=f'''# 第13話ショート V1〜V3 確認版v02

**2点の修正・全編検品・非公開共有を完了。本人試聴・Claude確認待ち。YouTube未投稿・未予約。**

[Draft Release]({shared['release_url']}) — Release ID **{shared['release_id']}**。3本のMP4＋確認ZIPをID指定RESTで全量再取得し、サイズ・SHA-256一致、匿名404を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/{shared['release_id']}
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT
```

| ファイル | asset ID | bytes |
|---|---:|---:|
'''
    for a in shared['assets']:note+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
    note+='\n[SHA-256一覧](SHA256SUMS_shared.txt)／[制作結果](../wom_ショート制作結果_EP013_20261108.md)。確認ZIPに冒頭0〜2.5秒、全字幕ページ、1秒・2秒おき、切り替え・末尾の画像と実測値を収録。\n'
    (DEST/'README.md').write_text(note)
    min_caption=min(q['minimum_contrast'] for q in qc)
    min_card=min(c['contrast_ratio'] for q in qc for g in q['card_contrast'] for c in g['checks'])
    text=f'''\n## v02：指定2点の修正・全編検品・非公開共有完了（2026-11-08）

本人のv02制作指示に基づき、fetchで **68eb4f819636c2e55cb4870cb372c568537ac6a8** を取得。既存専用worktreeをfast-forward更新して依頼書末尾を反映した。主作業ツリーの分岐履歴と未コミット作業は保全。[確認版・動画取得手順]({DEST.name}/README.md)。

### 変更内容と維持したもの

- V2今の左端、V3少女・鶏の爪の3範囲のみ変更。実際の既存絵枠は **1000×900px**（左40・上270）。依頼書の許可に従い、新指定座標の中心と幅を維持し、上下を枠の比率へ調整。
- V1は **{layout['album_start_frame']}フレーム＝{layout['album_start_seconds']:.6f}秒**、「An early description」からD_album_sへ切り替え。オランダ語原文・英日訳・札・出典は本編コードの文と文字列一致。日本語訳を登録案内の上に収めた。
- 音声を再合成せず、v01のnative WAV・最終AACをコピーしてSHA-256一致。完成v01/v02のAACストリームとデコードPCMも3本すべて一致。字幕26ページの画像・文・55ポイント・表示フレーム・見出し・CTAはv01を再利用。SRTは既存ページ・フレームを転記した補助ファイル。

| 素材 | 調整後の原寸座標（左・上・右・下） | 最大原寸倍率 |
|---|---|---:|
'''
    for g in layout['crops']:text+=f"| {g['asset']} | `{g['adjusted_box']}` | {g['native_max_scale']:.6f} |\n"
    text+='\n3本間の詳細範囲の交差は3組とも **0 px²**。V3鶏は少女範囲に包含。最大倍率は1倍以内。V1全体図・V2模式図は既承認の例外。AI補間・生成・色補正なし。\n\n'
    text+='素材一覧：V1＝V01_full → V01_D1 → D_1797s → **D_album_s**、V2＝V01_left → D_cut_s → V02_L、V3＝V01_girl → V01_claws。\n\n'
    text+='### 実測・検品\n\n| ショート | 尺 | フレーム | 音量 | True Peak | 声の開始 |\n|---|---:|---:|---:|---:|---:|\n'
    for q in qc:text+=f"| {q['id']} | {q['video_duration']:.6f}秒 | {q['video_format']['nb_frames']} | {q['audio']['input_i']} LUFS | {q['audio']['input_tp']} dBTP | {q['voice_onset']:.2f}秒 |\n"
    text+=f'''\n- 3本とも1080×1920・30fps・H.264 High・yuv420p、24秒以内。最後の案内は75フレーム＝2.5秒。V2はv01と同じ18.733秒（目安19秒より短いが変更していない）。
- 全 **{sum(int(q['video_format']['nb_frames']) for q in qc)}フレーム**を逐次デコード、警告0。各ショットの画素差で動きの連続性と静止カードを検査。
- 完成MP4を再測定し−14 LUFS±0.15以内、ピーク−1dBTP以下。v01のBGM開始10msの実測値と音声ストリーム一致により0秒からのBGMを維持。
- 字幕26ページは台本一致、文またぎ0、全行Arial Narrow Bold 55ポイント固定。完成動画の字幕最小コントラスト **{min_caption:.4f}:1**。
- 札の測定は元画像の指定文字色に一致する画素を**収縮なし**で抽出。完成MP4の同座標で最も明るい文字と最も暗い背景の比を測定（背景のみ3×3収縮）。文字候補が消える不具合を修正し、カード全行の最小値は **{min_card:.4f}:1**。
- 冒頭18枚、全字幕26ページ、1秒・2秒おきの全編一覧、全9ショットの切り替え、CTAと最終フレームを目視確認。詳細はvisual_review.json。人間による全編試聴は未実施。

### 保存と共有

SSD：`{ROOT}`。Pythonはv01の`_work/python`を再利用し、TMPDIR・中間物はSSD。新しいPython環境・Mac上のメディアは作成していない。報告作成直前のMac空き **{shutil.disk_usage('/').free/1024**2:.3f}MiB**。制作中は350MiB未満で停止するガードを使用。

新規非公開Draft Release **{shared['release_id']}**。MP4 3本と確認ZIPをRelease ID指定RESTで列挙し、4添付すべて全量再取得でサイズ・SHA-256一致。Release・添付は匿名404。Git共有はコード・記録・字幕・縮小JPGのみ。動画・音声・高解像度素材・中間物はGitに含めない。

投稿・予約・削除・reset・force-pushは実施していない。本人試聴とClaude確認を待つ。
'''
    reportfile=REPO/'wom_ショート制作結果_EP013_20261108.md';existing=reportfile.read_text()
    first=existing.index('> **最新状態');end=existing.index('\n',first)
    existing=existing[:first]+'> **最新状態：v02の指定2点修正・3本全編検品・非公開Draft ReleaseのREST照合を完了。本人試聴・Claude確認待ち。詳細は末尾。過去の停止記録は保全。**'+existing[end:]
    assert '\n## v02：指定2点' not in existing
    reportfile.write_text(existing+text)
    print('制作結果を追記',DEST,flush=True)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['package','share','report']);a=p.parse_args();globals()[a.stage]()
