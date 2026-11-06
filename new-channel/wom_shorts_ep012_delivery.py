"""Deliver approved EP012 short scripts as three private review videos."""
import hashlib
import json
import shutil
import subprocess
import time
import zipfile
from pathlib import Path

from PIL import Image
from wom_shorts_ep012 import ROOT,MAIN,REPO,REQUEST,read,save,sha
from wom_shorts_ep011_delivery import stamp
from wom12_share import api,assert_anonymous_hidden

TAG='quiet-origins-ep012-shorts-v01-20261106'
DEST=REPO/'wom_ショート確認版_EP012_v01_20261106'
TITLES={'N1':'Santa Wore Red in 1821','N2':'Santa Once Wore the Flag','N3':'In 1821, Santa Had One Reindeer'}
JAPANESE={'N1':'1821年、サンタはもう赤かった','N2':'星条旗の服を着たサンタ','N3':'1821年、トナカイは1頭だった'}
TIMES={'N1':'2026-11-14 18:00','N2':'2026-11-15 12:00','N3':'2026-11-16 12:00'}

def package():
    qc=read(ROOT/'records/final_qc.json')
    assert len(qc)==3 and read(ROOT/'records/final_pixel_motion.json')['passed']
    assert read(ROOT/'records/visual_review.json')['passed']
    shots=read(ROOT/'records/visual_manifest.json')['shots']
    caps=read(ROOT/'records/caption_manifest.json')
    nar=read(ROOT/'records/narration.json')
    for s in read(ROOT/'records/shorts.json')['shorts']:
        sid=s['id']
        cs=[c for c in caps if c['short_id']==sid]
        srt='\n\n'.join(f"{i+1}\n{stamp(c['start_frame'])} --> {stamp(c['end_frame'])}\n"+'\n'.join(c['lines']) for i,c in enumerate(cs))+'\n'
        (ROOT/f'deliverables/QO_short_EP012_{sid}_v01.srt').write_text(srt)
        refs=list(dict.fromkeys(g['source']['source'] for g in shots if g['short_id']==sid))
        if sid in ['N1','N3']:
            refs+=['Yale University Policy on Open Access to Digital Representations of Works in the Public Domain from Museum, Library, and Archive Collections (2011). https://collections.library.yale.edu/catalog/2014510']
        if sid=='N2':refs+=['The Metropolitan Museum of Art, 33.35.11, Public Domain. https://www.metmuseum.org/art/collection/search/427502']
        info=f"""# {sid} 投稿用情報

## Title

{TITLES[sid]}

## Description

{s['text']}

Full story: see the related video below.

Quiet Origins — Every story has an origin.

Sources and images:
"""+'\n'.join('- '+r for r in refs)+f"""

Narration: Kokoro / Heart (af_heart)
Music: QO_THEME_A02 / Suno

#QuietOrigins #SantaClaus #ChristmasHistory #Shorts

## 日本語タイトル

{JAPANESE[sid]}

## 制作メモ

公開案 {TIMES[sid]} JST。本人試聴・Claude確認後、別依頼で投稿する。関連動画は第12話の公開後に設定。
"""
        (ROOT/f'deliverables/{sid}_upload_info.md').write_text(info)
    save(ROOT/'records/approval.json',dict(request=str(REQUEST),request_sha256=sha(REQUEST),
        source_scripts_unchanged=True,actual_word_counts={s['id']:s['words'] for s in nar['scripts']},
        note='Request labels N1/N3 as 43 words; the exact supplied text contains 42 whitespace-delimited words each. Text retained.',
        human_listening=False,claude_review_pending=True,youtube_posted=False))
    shutil.copy2(REQUEST,ROOT/'records/request.md')
    source_files={g['source']['path'] for g in shots if not g['static']}
    save(ROOT/'records/source_hashes.json',[dict(path=p,sha256=sha(p)) for p in sorted(source_files)])
    for p in ROOT.glob('review/**/*.jpg'):
        assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
    files=[*ROOT.glob('records/*.json'),ROOT/'records/request.md',*ROOT.glob('review/**/*.jpg'),
           *ROOT.glob('deliverables/*.srt'),*ROOT.glob('deliverables/*.md')]
    files=[p for p in files if p.name not in ['sharing.json','delivery_files.json']]
    archive=ROOT/'deliverables/EP012_shorts_review_v01.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for p in sorted(files):z.write(p,p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    outputs=[*sorted(ROOT.glob('deliverables/QO_short_EP012_N*_v01.mp4')),archive]
    assert len(outputs)==4
    save(ROOT/'records/delivery_files.json',[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in outputs])

def share():
    repo='yasukawa1980/youtube'
    files=read(ROOT/'records/delivery_files.json')
    for f in files:assert sha(ROOT/'deliverables'/f['file'])==f['sha256']
    releases=api([f'repos/{repo}/releases?per_page=100'])
    r=next((r for r in releases if r['tag_name']==TAG),None)
    if r is None:
        r=api(['--method','POST',f'repos/{repo}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',
            name='Quiet Origins 第12話ショートN1〜N3 確認版v01',
            body='英語3本。N1 20.90秒、N2 19.53秒、N3 20.60秒。N1の冒頭は原寸上限内で人物を表示。確認ZIPに字幕・素材の座標・全字幕ページと検品記録を収録。Claude確認と本人試聴待ち。',draft=True))
    assert r['draft']
    assert_anonymous_hidden(f'repos/{repo}/releases/{r["id"]}')
    state=dict(release_id=r['id'],release_url=r['html_url'],tag=TAG,draft=True,status='uploading',assets=[])
    save(ROOT/'records/sharing.json',state)
    for f in files:
        asset=next((a for a in r['assets'] if a['name']==f['file']),None)
        if asset:assert asset['digest']=='sha256:'+f['sha256']
        else:subprocess.run(['gh','release','upload',TAG,str(ROOT/'deliverables'/f['file']),'--repo',repo],check=True)
        print('UPLOADED',f['file'],flush=True)
    r=api([f'repos/{repo}/releases/{r["id"]}'])
    assert r['draft'] and len(r['assets'])==4
    for f in files:
        a=next(a for a in r['assets'] if a['name']==f['file'])
        endpoint=f'repos/{repo}/releases/assets/{a["id"]}'
        data=subprocess.check_output(['gh','api','-H','Accept: application/octet-stream',endpoint])
        assert len(data)==f['bytes'] and hashlib.sha256(data).hexdigest()==f['sha256']
        assert_anonymous_hidden(endpoint)
        state['assets'].append(dict(name=f['file'],asset_id=a['id'],bytes=len(data),sha256=f['sha256'],rest_download_verified=True,anonymous_http_status=404))
        save(ROOT/'records/sharing.json',state)
        print('VERIFIED',f['file'],flush=True)
    state['status']='verified'
    save(ROOT/'records/sharing.json',state)

def report():
    shared=read(ROOT/'records/sharing.json')
    assert shared['status']=='verified' and len(shared['assets'])==4
    for folder in ['records','確認画像','deliverables']:(DEST/folder).mkdir(exist_ok=True,parents=True)
    for p in ROOT.glob('records/*.json'):shutil.copy2(p,DEST/'records'/p.name)
    for p in ROOT.glob('review/**/*.jpg'):
        if p.name.endswith('_design.jpg'):continue
        d=DEST/'確認画像'/p.relative_to(ROOT/'review')
        d.parent.mkdir(exist_ok=True,parents=True)
        shutil.copy2(p,d)
    for p in ROOT.glob('deliverables/*'):
        if p.suffix in ['.srt','.md']:shutil.copy2(p,DEST/'deliverables'/p.name)
    note=['# 第12話 ショートN1〜N3 確認版v01','',
          f"[非公開Draft Release]({shared['release_url']})。Release ID **{shared['release_id']}**。4添付をRESTで全量再取得し、バイト数とSHA-256一致、匿名404を確認。",'',
          '[制作結果と確認点](../wom_ショート制作結果_EP012_20261106.md)。動画の試聴後、N1の人物サイズ・N2の範囲・N3の引用カードを確認してください。','',
          '|ファイル|asset ID|バイト|SHA-256|','|---|---:|---:|---|']
    for a in shared['assets']:note.append(f"|{a['name']}|{a['asset_id']}|{a['bytes']}|`{a['sha256']}`|")
    note+=['',f"`gh api repos/yasukawa1980/youtube/releases/{shared['release_id']}` で一覧を取得し、`gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT` で保存。"]
    (DEST/'README.md').write_text('\n'.join(note)+'\n')
    qc=read(ROOT/'records/final_qc.json')
    visual=read(ROOT/'records/visual_manifest.json')
    text=['# 第12話「サンタクロースの赤い服」ショート3本 制作結果（2026-11-06）','',
          '[依頼書](wom_ショート制作依頼_EP012_20261106.md)の本文でN1〜N3を制作し、非公開共有済み。[確認版の取得](wom_ショート確認版_EP012_v01_20261106/README.md)。本人試聴・Claude確認待ち。','',
          '|ID|尺（案内込み）|最初の声|LUFS|dBTP|字幕の最低コントラスト|','|---|---:|---:|---:|---:|---:|']
    for q in qc:text.append(f"|{q['id']}|{q['video_duration']:.3f}秒|{q['voice_onset']:.2f}秒|{q['audio']['input_i']}|{q['audio']['input_tp']}|{q['minimum_contrast']:.3f}|")
    text+=['','全3本24秒以内。1080×1920・30fps・H.264 High・yuv420p、全編連続デコード警告0件。0秒から音楽と見出しを表示。Kokoro af_heart、speed 0.82、sentence_pause 0.3、clause_pause 0.12で新規合成。Santeclausの読みを本編と同じ音素に指定。本文と字幕は一致、文をまたぐ字幕0、Arial Narrow Bold 55ポイント固定。最後の登録案内は2.5秒。','',
           'N1/N3の語数は依頼書に43語とあるが、渡された本文を空白で数えた実測は各42語。本文を採用した。N2は39語。','',
           '## 確認が必要な画面','',
           'N1の冒頭は、原寸上限と見出しとの重なり回避を優先し、人物とそりの範囲を画面高さの約28%で表示した。「高さ7割前後」の目安より小さい。原画の当該範囲は750×660pxで、最終最大倍率は1倍以下。確認画像で主役の大きさを判断してほしい。','',
           'N3の最初の引用カードでは文字を固定し、下線が左から伸びる動きを0秒から付けた。英語原文は指定どおり。日本語訳は見出しの下・字幕の上に配置。最後のカードは登録案内の上に収めた。','',
           'N02-Aの人物と首の縄の部分は、サンタと野営地の2つの寄りの範囲から除外。最後の全体ショットでは画面幅内に作品全体を収める。','',
           '## 素材範囲と拡大率','',
           '原寸画像の座標を [左,上,右,下] で記す。終端側は範囲内へゆっくり寄るため、始端範囲の部分集合。N08_p1の人物・本文・トナカイの範囲は互いに重ならないことを座標で確認。','',
           '|ショート|範囲|原画の座標|最大倍率|','|---|---|---|---:|']
    for g in visual['shots']:text.append(f"|{g['short_id']}|{g['asset_id']}|{g['crop_start']}|{g['native_max_scale']:.4f}|")
    motion=read(ROOT/'records/final_pixel_motion.json')['checks']
    ratios=[m['p95_over_median'] for m in motion if not m['static']]
    text+=['',f'完成動画の動く原画の隣接フレーム差p95/中央値は最大{max(ratios):.3f}。素材・字幕・引用カードのコントラストと倍率の検品値、冒頭0〜2.5秒・全字幕ページ・2秒おき・登録案内の画像を確認ZIPに同梱。','',
           f'SSD保存先 `{ROOT}`。非公開Draft Release **{shared["release_id"]}**。公開案はN1が11/14 18:00、N2が11/15 12:00、N3が11/16 12:00 JST。投稿は試聴・確認後の別依頼で行う。']
    (REPO/'wom_ショート制作結果_EP012_20261106.md').write_text('\n'.join(text)+'\n')

if __name__=='__main__':
    import sys
    {'package':package,'share':share,'report':report}[sys.argv[1]]()
