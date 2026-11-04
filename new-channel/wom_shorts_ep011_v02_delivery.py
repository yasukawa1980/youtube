"""Private review delivery for the two EP011 card corrections; no posting."""
import argparse
import hashlib
import shutil
import subprocess
import time
import zipfile
from pathlib import Path
from PIL import Image
from wom_shorts_ep011_v02 import ROOT,OLD,REPO,REQUEST,DEST,TAG,IDS,read,save,sha,video
from wom11_share import api,assert_anonymous_hidden


def package():
    qc=read(ROOT/'records/final_qc.json');assert len(qc)==2
    assert all(q['outside_card_all_frames_identical'] and q['audio_pcm_identical'] and q['warning_count']==0 for q in qc)
    assert read(ROOT/'records/visual_review.json')['passed']
    for name in ['caption_manifest.json','cta_design.json','shorts.json','headlines.json']:
        shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
    save(ROOT/'records/approval.json',dict(request_sha256=sha(REQUEST),user_instruction='クロードからの修正案を確認して進めて下さい',scope='Only H2/H3 card correction. H1 v01 retained.',youtube_posted=False,human_full_listening=False,claude_review_pending=True))
    members=sorted([*ROOT.glob('records/*.json'),ROOT/'records/request.md',*ROOT.glob('review/*.jpg'),*ROOT.glob('deliverables/*.srt'),*ROOT.glob('deliverables/*.md')])
    members=[p for p in members if p.name not in ['sharing.json','delivery_files.json']]
    for p in ROOT.glob('review/*.jpg'):assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
    archive=ROOT/'deliverables/EP011_shorts_review_v02.zip'
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
        r=api(['--method','POST',f'repos/{repo}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins 第11話ショート H2・H3 確認版v02（カード修正・未投稿）',body='H2・H3の文字カード3行の末尾区切りを削除。H2の文字全体を60px上へ移動し、案内との間隔103px。カード以外の全870フレームと音声PCMがv01に完全一致。H1はv01を継続。本人試聴・Claude確認待ち。YouTube未投稿・未予約。',draft=True))
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
    note=f"# 第11話ショート H2・H3 確認版v02\n\n**カード修正・検品・非公開共有済み。本人試聴とClaude確認待ち。YouTube未投稿・未予約。H1はv01を使用。**\n\n[Draft Release]({shared['release_url']}) — Release ID **{shared['release_id']}**。MP4 2本＋確認ZIPの全3添付をREST再取得し、サイズ・SHA-256一致、匿名404を確認。\n\n```sh\ngh api repos/yasukawa1980/youtube/releases/{shared['release_id']}\ngh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>\n```\n\n| ファイル | asset ID | bytes |\n|---|---:|---:|\n"
    for a in shared['assets']:note+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
    note+='\n[SHA-256一覧](SHA256SUMS_shared.txt)／[制作結果](../wom_ショート制作結果_EP011_v02_20261104.md)／[H1 v01取得先](../wom_ショート確認版_EP011_v01_20261104/README.md)。確認ZIPにはカード単体、完成動画の字幕・案内表示中の画像、文字・座標・全フレーム比較・PCM MD5等の記録を収録。\n'
    (DEST/'README.md').write_text(note)
    qc=read(ROOT/'records/final_qc.json');layout=read(ROOT/'records/layout.json');cards=read(ROOT/'records/card_texts.json')
    text='# Quiet Origins 第11話ショート H2・H3 v02 修正結果（2026-11-04）\n\n**指定3点の修正・検品・非公開共有を完了。** [Claude修正依頼](wom_ショート修正依頼_EP011_v02_20261104.md)を反映。[確認版の取得](wom_ショート確認版_EP011_v02_20261104/README.md)。H1は合格済みv01を継続。本人試聴・Claude確認待ち。YouTube未投稿・未予約。\n\n## 修正\n\nD_balanceの `THE HEART AND MAAT｜` と `Maat: truth and right order｜` の行末「｜」、D_stolenの `The Negative Confession ·` の行末「 ·」だけを除去し、文字幅で中央に再配置。他の文字・句読点・フォント・字の大きさを維持。D_balanceは各行の上端を一律60px上へ移動。D_stolenの縦位置は同一。\n\n'
    text+=f"H2カード最下段下端 y={layout['balance_bottom']}、SUBSCRIBE上端 y={layout['cta_glyph_top']}、差 **{layout['cta_gap_px']}px**（v01は43px、要求80px以上）。案内の背景板までは{layout['cta_plate_gap_px']}px。上部札下端 y={layout['header_bottom']}、カード上端 y={layout['balance_top']}、差 **{layout['header_gap_px']}px**（要求40px以上）。語り字幕の箱まで{layout['caption_gap_px']}px。\n\n| ID | 尺 | フレーム | LUFS | dBTP | カード以外で完全一致したフレーム |\n|---|---:|---:|---:|---:|---:|\n"
    for q in qc:text+=f"| {q['id']} | {q['duration_seconds']:.6f}秒 | {q['video_format']['nb_frames']} | {q['audio']['input_i']} | {q['audio']['input_tp']} | {q['outside_card_frame_count']} |\n"
    text+='\n1080×1920・30fps・H.264 High・yuv420p。全編の連続デコード警告0。音声は元MP4のAACをストリームコピーし、PCM s16leへデコードしたMD5とAAC SHA-256がv01と一致。SRTもSHA-256一致。焼き込み字幕・見出し・案内の画像とタイミングは既存データをそのまま使用。\n\n| ID | 映像が変わったフレーム（0起算、終端除外） | 時間（終端除外） | v01/v02共通のPCM MD5 |\n|---|---|---|---|\n'
    for q in qc:text+=f"| {q['id']} | {q['changed_start_frame']}–{q['changed_end_frame_exclusive']} | {q['changed_start_seconds']:.6f}–{q['changed_end_seconds']:.6f}秒 | `{q['audio_pcm_md5_v02']}` |\n"
    text+='\n変更区間はD_balance／D_stolenの表示区間と完全一致。v01のカード切替が閉じたIDRであるため、カード区間だけ再エンコードし、他のGOPをストリームコピーで接続。完成動画の全フレームを同一PTS・YUV420pにデコードしMD5比較、カード以外は全870フレーム完全一致。全フレーム比較記録を添付。素材範囲・動き・切替・尺を維持。\n\n## カード文字の実測\n\n| カード | 行 | bbox [左,上,右,下] | 大文字H高さ | フォントサイズ |\n|---|---|---|---:|---:|\n'
    for aid,c in cards.items():
        for r in c['texts']:text+=f"| {aid} | {r['text']} | {r['bbox']} | {r['cap_height']}px | {r['font_size']} |\n"
    text+='\n英語主要行の大文字高さは107／61／69pxで60px以上を維持。記号削除後の文字だけで横中央へ配置。文字の塊全体の各行上端間隔・フォント・サイズを維持。カード単体2枚と完成動画からの確認画像を目視検品し、文字切れ・重なり・行末記号残りなしを確認。本人による全編試聴は未実施。\n'
    text+=f"\n## 保存・共有\n\nSSD：`{ROOT}`。新規Draft Release **{shared['release_id']}**（非公開）。3添付すべてREST再取得・SHA-256・サイズ一致、匿名404。v01の動画・Draft Releaseは保全。Gitにはスクリプト・字幕・縮小確認JPG・検品記録だけを共有。公開案はH1 11/11、H2 11/12、H3 11/13の12:00 JSTのまま。投稿は本人試聴とClaude確認後の別依頼で行う。\n"
    (REPO/'wom_ショート制作結果_EP011_v02_20261104.md').write_text(text)
    print('HANDOFF READY',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['package','share','report']);a=p.parse_args();globals()[a.stage]()
