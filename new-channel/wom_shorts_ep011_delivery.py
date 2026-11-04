"""Package, privately share, and document verified EP011 shorts without YouTube posting."""
import argparse
import hashlib
import json
import shutil
import subprocess
import time
import zipfile
from pathlib import Path
from PIL import Image
from wom_shorts_ep011 import ROOT,MAIN,REPO,REQUEST,sha,read,save

TAG='quiet-origins-ep011-shorts-v01-20261104'
DEST=REPO/'wom_ショート確認版_EP011_v01_20261104'
TITLES={'H1':'A Spell Spoken to the Heart','H2':'Heart and Feather in Balance','H3':'42 Gods, 42 Denials: Could You Fail?'}
JAPANESE={'H1':'心臓に語りかける呪文','H2':'心臓と羽根はつり合っていた','H3':'42柱の神々と42の否定'}

def stamp(frame):
    ms=round(frame/30*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def package():
    qc=read(ROOT/'records/final_qc.json');assert len(qc)==3
    assert read(ROOT/'records/final_pixel_motion.json')['passed'] and read(ROOT/'records/visual_review.json')['passed']
    shots=read(ROOT/'records/visual_manifest.json')['shots'];caps=read(ROOT/'records/caption_manifest.json')
    shorts=read(ROOT/'records/shorts.json')['shorts'];source=read(MAIN/'records/source_assets.json')
    originals={s['source']['path'] for s in shots if not s['static']};assert len(originals)==5
    assets=[]
    for a in source['assets']:
        images=[i for i in a['images'] if i['file'] in originals]
        if images:assets.append({k:a[k] for k in ['met_object_id','title','date','museum','accession','object_url','rights','rights_evidence','credit_line']}|{'images':images})
    assert len(assets)==4 and sum(len(a['images']) for a in assets)==5
    save(ROOT/'records/source_assets.json',dict(assets=assets,original_image_count=5,original_work_count=4,photographic_regions=7,cards=['D_balance','D_stolen'],unique_regions_and_cards=9,no_AI=True))
    save(ROOT/'records/approval.json',dict(request=str(REQUEST),request_sha256=sha(REQUEST),user_instruction='クロードの指示に従ってショートを制作して下さい',duration_exception=None,all_within_24_seconds=True,human_full_listening=False,claude_review_pending=True,youtube_posted=False))
    for s in shorts:
        sid=s['id'];cs=[c for c in caps if c['short_id']==sid]
        srt='\n\n'.join(f"{i+1}\n{stamp(c['start_frame'])} --> {stamp(c['end_frame'])}\n"+'\n'.join(c['lines']) for i,c in enumerate(cs))+'\n'
        (ROOT/f'deliverables/QO_short_EP011_{sid}_v01.srt').write_text(srt)
        credits=list(dict.fromkeys(g['source']['source'] for g in shots if g['short_id']==sid and not g['static']))
        info=f"# {sid} 投稿用情報（未投稿）\n\n## Title\n\n{TITLES[sid]}\n\n## Description\n\n{s['text']}\n\nFull story: see the related video below.\n\nQuiet Origins — Every story has an origin.\n\nSources and images:\n"+'\n'.join('- '+c for c in credits)+'\n\nNarration: Kokoro / Heart (af_heart)\nMusic: QO_THEME_A02 / Suno\n\n#QuietOrigins #AncientEgypt #BookOfTheDead #Shorts\n'
        info+=f"\n## 日本語タイトル\n\n{JAPANESE[sid]}\n\n## 制作・予約メモ（説明欄には貼らない）\n\n公開案：2026-11-{10+int(sid[-1]):02} 12:00 JST。未投稿・未予約。本人試聴とClaude確認後の別依頼で行う。関連動画は第11話の公開後に設定。予定を確定する前にチャンネル当日の本編＋ショート合計3本以下・ショート2本以下を再確認。\n"
        (ROOT/f'deliverables/{sid}_upload_info.md').write_text(info)
    (ROOT/'review/README.txt').write_text('Quiet Origins EP011 H1/H2/H3 v01\nEnglish burned-in captions; native af_heart voice; no YouTube upload.\nOpening at 0/0.5/1/1.5/2/2.5 seconds; every two seconds; all caption pages; cuts; CTA.\nHuman full listening and Claude review pending.\n')
    shutil.copy2(REQUEST,ROOT/'records/request.md')
    for p in (ROOT/'review').rglob('*.jpg'):assert max(Image.open(p).size)<=1280 and p.stat().st_size<1000000
    members=sorted([*ROOT.glob('records/*.json'),ROOT/'records/request.md',*ROOT.glob('review/**/*.jpg'),ROOT/'review/README.txt',*ROOT.glob('deliverables/*.srt'),*ROOT.glob('deliverables/*.md')])
    members=[p for p in members if p.name not in ['sharing.json','delivery_files.json']]
    archive=ROOT/'deliverables/EP011_shorts_review_v01.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in members:z.write(p,p.relative_to(ROOT))
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    files=[*sorted(ROOT.glob('deliverables/QO_short_EP011_H*_v01.mp4')),archive];assert len(files)==4
    save(ROOT/'records/delivery_files.json',[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files])
    print('PACKAGED',len(files),'assets',archive.stat().st_size,'ZIP bytes',flush=True)

def share():
    from wom11_share import api,assert_anonymous_hidden
    repo='yasukawa1980/youtube';files=read(ROOT/'records/delivery_files.json')
    for f in files:assert sha(ROOT/'deliverables'/f['file'])==f['sha256']
    releases=api([f'repos/{repo}/releases?per_page=100']);r=next((r for r in releases if r['tag_name']==TAG),None)
    if r is None:
        r=api(['--method','POST',f'repos/{repo}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins 第11話ショートH1〜H3 確認版v01（未投稿）',body='承認済み台本から英語3本を新規制作。H1 21.80秒、H2 18.17秒、H3 20.63秒。1080×1920・30fps、本編と同じaf_heart、QO_THEME_A02。字幕18ページ・素材9範囲を重複なく使用。Claude確認・本人試聴待ち。YouTube未投稿。',draft=True))
    assert r['draft'];assert_anonymous_hidden(f'repos/{repo}/releases/{r["id"]}')
    state=dict(release_id=r['id'],release_url=r['html_url'],tag=TAG,draft=True,status='uploading',assets=[])
    save(ROOT/'records/sharing.json',state)
    for f in files:
        asset=next((a for a in r['assets'] if a['name']==f['file']),None)
        if asset:assert asset['digest']=='sha256:'+f['sha256']
        else:subprocess.run(['gh','release','upload',TAG,str(ROOT/'deliverables'/f['file']),'--repo',repo],check=True)
        print('UPLOADED',f['file'],flush=True)
    r=api([f'repos/{repo}/releases/{r["id"]}']);assert r['draft'] and len(r['assets'])==4
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
    shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified' and len(shared['assets'])==4
    for d in ['records','確認画像','deliverables']:(DEST/d).mkdir(parents=True,exist_ok=True)
    for p in ROOT.glob('records/*.json'):shutil.copy2(p,DEST/'records'/p.name)
    for p in ROOT.glob('review/**/*.jpg'):
        if p.name.endswith('_design.jpg'):continue
        target=DEST/'確認画像'/p.relative_to(ROOT/'review');target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    for p in ROOT.glob('deliverables/*'):
        if p.suffix in ['.srt','.md']:shutil.copy2(p,DEST/'deliverables'/p.name)
    (DEST/'SHA256SUMS_shared.txt').write_text(''.join(f"{a['sha256']}  {a['name']}\n" for a in shared['assets']))
    note=f"# 第11話ショートH1〜H3 確認版v01\n\n**確認版3本を制作・検品し非公開共有済み。Claude確認・本人試聴待ち。YouTube未投稿・未予約。**\n\n[Draft Release]({shared['release_url']}) — Release ID **{shared['release_id']}**。4添付すべてREST再取得・サイズ・SHA-256一致、匿名404。\n\n```sh\ngh api repos/yasukawa1980/youtube/releases/{shared['release_id']}\ngh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/<asset_id> > <filename>\n```\n\n| ファイル | asset ID | bytes |\n|---|---:|---:|\n"
    for a in shared['assets']:note+=f"| {a['name']} | {a['asset_id']} | {a['bytes']} |\n"
    note+='\n[SHA-256一覧](SHA256SUMS_shared.txt)／[制作結果](../wom_ショート制作結果_EP011_20261104.md)。確認ZIPには字幕・投稿用文・全字幕ページ・冒頭0〜2.5秒・2秒おき・切替・最後の案内の画像と検品記録を収録。\n'
    (DEST/'README.md').write_text(note)
    qc=read(ROOT/'records/final_qc.json');motion=read(ROOT/'records/final_pixel_motion.json')['checks'];visual=read(ROOT/'records/visual_manifest.json')
    text='# Quiet Origins 第11話「心臓の計量」ショート3本 制作結果（2026-11-04）\n\n**確認版v01の3本が完成。** [Claude依頼](wom_ショート制作依頼_EP011_20261104.md)の指定台本・素材で制作。[確認動画の取得・全記録](wom_ショート確認版_EP011_v01_20261104/README.md)。Claude確認と本人試聴待ち。YouTube未投稿・未予約。\n\n| ID | 語数 | 尺 | 最初の声 | LUFS | dBTP | 字幕最低コントラスト |\n|---|---:|---:|---:|---:|---:|---:|\n'
    nar={s['id']:s for s in read(ROOT/'records/narration.json')['scripts']}
    for q in qc:text+=f"| {q['id']} | {nar[q['id']]['words']} | {q['video_duration']:.6f}秒 | {q['voice_onset']:.2f}秒 | {q['audio']['input_i']} | {q['audio']['input_tp']} | {q['minimum_contrast']:.3f} |\n"
    text+='\n尺は最後の案内2.5秒込み。全3本24秒以内。H2は目安19〜23秒より短いが、台本・話速・自然な間を維持し、尺合わせの追加や引き延ばしはしていない。\n\n## 制作・検証\n\n'
    text+='- Kokoro af_heart、speed 0.82／sentence_pause 0.3／clause_pause 0.12、読み替え0。本編設定と照合し、新規合成。台本の言い換え・追加なし。\n- QO_THEME_A02の本編選択音源100秒地点から。100Hzハイパス、2828Hzを3.5dB低減。語り中の音楽は声より15dB下、0秒からフェードインなし。\n- 縦1080×1920・30fps・H.264 High／yuv420p。各原資料を独立デコードし、各完成動画は単一エンコーダーで出力。先頭から全フレームを連続デコードし警告0。\n- 字幕18ページは台本と全文一致、文またぎ0、各2行以内。Arial Narrow Bold 55ポイント固定、大文字高さ39px、横伸縮なし。Spell 30B／Spell 125・引用2件は同一ページ内に保持。「the dead live on」のonは前置詞ではなく句動詞の副詞。\n- 0秒から見出し・主役・動き、見出しは2.0〜2.3秒で消える。最後の案内は承認済みv03の画像を同一ハッシュで使用。カード2枚の指定文字は改行以外すべて維持。英語主要行の大文字高さ60px以上。\n- 原画像5点（館作品4点）の7範囲と文字カード2枚、計9点を各1回。イムヘテプの下段天秤／上段2列／アメミトは座標上も重ならない。AIによる画像生成・補間なし。通常のLanczosで表示。\n'
    text+='\n## 画面の範囲と拡大\n\n| ショート | 素材 | 原画像上の開始範囲 → 終了範囲（x1,y1,x2,y2） | 最大倍率 |\n|---|---|---|---:|\n'
    for g in visual['shots']:
        if not g['static']:
            x1,y1,x2,y2=g['crop_end'];cx=(x1+x2)/2;cy=(y1+y2)/2;z=g['zoom_end']
            final_rect=[round(cx-(x2-x1)/z/2,3),round(cy-(y2-y1)/z/2,3),round(cx+(x2-x1)/z/2,3),round(cy+(y2-y1)/z/2,3)]
            text+=f"| {g['short_id']} | {g['asset_id']} | {g['crop_start']} → {final_rect} | {g['native_max_scale']:.6f} |\n"
    text+='\nH1とH3の最初の画像は画面高さの約70%。H2は個別指定の「梁・両皿から下段x30〜56%へ引く」を優先。両皿が欠けないようP10の近傍に余白を加え、横長の比率を保って画面幅に合わせた。汎用の「7割の高さ・寄り」と異なり、天秤は1つの連続した引きのショット。アメミトだけ承認済みの2.5倍以内を使用し、その他の資料は1.6倍以内。\n'
    text+=f"\n完成動画の全隣接フレーム差p95/中央値は最大{max(m['p95_over_median'] for m in motion if not m['static']):.3f}（上限2.5）。静止カードは絶対差p95<0.1。測定範囲と全フレーム差を記録。字幕・カードのコントラスト比はすべて4.5以上。\n\n## 保存・共有と次の確認\n\nSSD：`{ROOT}`。新しい非公開Draft Release **{shared['release_id']}**。完成MP4 3本＋確認ZIPの4添付をREST再取得・ハッシュ照合済み、匿名404。Gitにはコード・記録・字幕・投稿文・縮小確認JPGを共有。\n\n本人は3本の全編試聴（読み・BGM・字幕・動き）、Claudeは指定文と資料範囲・H2の引き・カード文字・字高・倍率を確認。公開案はH1 11/11・H2 11/12・H3 11/13の各12:00 JST。確認後の別依頼で投稿し、当日の本数を再照合する。\n"
    (REPO/'wom_ショート制作結果_EP011_20261104.md').write_text(text)
    print('HANDOFF READY',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['package','share','report']);a=p.parse_args();globals()[a.stage]()
