"""Assemble v02 metadata, shot evidence, QA archives and the verified handoff."""
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw
from wom12_retime import NEW, OLD, read, save, sha
from wom11_delivery import mm

P=Path(__file__).resolve().parent
D=NEW/'deliverables'
R=NEW/'records'
SHARE=P/'wom12_確認版_v02_20261105'

def metadata():
    for dest in [D,R,SHARE]:dest.mkdir(parents=True,exist_ok=True)
    for p in (OLD/'deliverables').glob('*.jpg'):
        shutil.copy2(p,D/p.name)
        assert sha(p)==sha(D/p.name)
    shutil.copy2(OLD/'deliverables/EP012_source_credits.md',D)
    for lang in ['en','ja']:
        root=NEW/lang
        master=read(root/'records/master_timeline.json')
        content=read(root/'records'/('content_en.json' if lang=='en' else 'content.json'))
        chapters=[]
        for chapter in content['chapters']:
            seg=next(s for s in master['segments'] if s['chapter']==chapter['id'])
            chapters.append(mm(seg['start'] if chapters else 0)+' '+chapter['title'])
        name=f'EP012_upload_info_{lang}.md'
        text=(OLD/'deliverables'/name).read_text().split('\n\n')
        assert all(re.match(r'\d\d:\d\d ',c) for c in text[2].splitlines())
        text[2]='\n'.join(chapters)
        text='\n\n'.join(text)
        if lang=='en':
            fixes={'L. Prang & Co.（出版）, Christmas card':'L. Prang & Co. (publisher), Christmas card',
                   'Clement Clarke Moore（詩）／L. Prang & Co.（出版）、挿絵作者未確認, A Visit from St. Nicholas — PDFコマ10':'A Visit from St. Nicholas (Boston: L. Prang & Co., 1864), illustrator unknown'}
            for old,new in fixes.items():
                assert text.count(old)==1
                text=text.replace(old,new)
        (D/name).write_text(text)
        shutil.copy2(D/name,SHARE)
        # The listening sample itself contains the same utterances. Update its main-film index.
        name=f'EP012_pronunciation_{lang}'
        shutil.copy2(OLD/'deliverables'/(name+'.m4a'),D)
        cues={c['id']:c for s in master['segments'] for c in s['cues']}
        lines=[]
        for line in (OLD/'deliverables'/(name+'.txt')).read_text().splitlines():
            sample,cid,interval,body=line.split(' | ',3)
            c=cues[cid]
            lines.append(f"{sample} | {cid} | {c['start']:.3f}–{c['end']:.3f}s | {body}")
        (D/(name+'.txt')).write_text('\n'.join(lines)+'\n')
        rec=R/lang;rec.mkdir(exist_ok=True)
        for f in ['voice_gaps','rail_switches','render_shots']:
            src=root/'records'/(f+'.json')
            if src.exists():shutil.copy2(src,rec)
        save(rec/'timeline.json',dict(duration=master['duration_seconds'],brand_intervals=master['brand_intervals'],
             segments=[{k:s[k] for k in ['id','start','speech_end','end','source_sha256','audio_file']} for s in master['segments']]))
        save(rec/'chapters.json',chapters)

def inspect_4k(src, total_frames):
    shots=read(NEW/'en/records/render_shots.json')
    assert total_frames==sum(s['frames'] for s in shots)
    frames=[]
    for s in shots:
        start=round(s['start']*30)
        frames.extend([start,start+(s['frames']-1)//2,start+s['frames']-1])
    folder=NEW/'_work/4k_checks'
    folder.mkdir(exist_ok=True)
    # showinfo sees every decoded frame before selection. Disable the expensive plane checksums.
    expr='+'.join(f'eq(n\\,{f})' for f in frames)
    cmd=['ffmpeg','-y','-nostdin','-v','level+info','-xerror','-threads','4','-i',str(src),'-an','-vf',
         'showinfo=checksum=0,select='+expr+',scale=426:240','-fps_mode','passthrough',str(folder/'%03d.png')]
    out=subprocess.run(cmd,check=True,capture_output=True,text=True).stderr
    assert not re.search(r'\[(?:warning|error|fatal)\]',out),out[-2000:]
    rows=re.findall(r'\bn:\s*(\d+)\s+pts:\s*(-?\d+).*?\bfmt:(\w+).*?\bs:(\d+x\d+)',out)
    assert len(rows)==total_frames and {r[2:] for r in rows}=={('yuv420p','3840x2160')}
    assert all(int(r[0])==i and int(r[1])==i*512 for i,r in enumerate(rows))
    assert len(list(folder.glob('*.png')))==len(frames)
    for b in range(6):
        sheet=Image.new('RGB',(1280,4*272),'#112029')
        pen=ImageDraw.Draw(sheet)
        for j,s in enumerate(shots[b*4:b*4+4]):
            i=b*4+j
            pen.text((10,j*272+6),f"4K {i+1:02d}  {s['key']}  |  FIRST, MIDDLE, LAST",fill='white')
            for k in range(3):
                with Image.open(folder/f'{i*3+k+1:03d}.png') as im:sheet.paste(im,(k*426,j*272+27))
        sheet.save(SHARE/f'continuous_en_4k_sheet_{b+1:02d}.jpg',quality=86)
    return dict(formats=['3840x2160 yuv420p H.264 High'],exact_30fps_pts=True,selected_frames=frames)

def sheets4k():
    info=read(NEW/'deliverables_4k/encoding.json')['files'][0]
    assert info['audio_same'] and info['decode_warnings']==0
    assert sha(D/info['source'])==info['source_sha256']
    assert len(info['selected_frames'])==69 and len(list(SHARE.glob('continuous_en_4k_sheet_*.jpg')))==6
    save(R/'4k.json',info)

def archive():
    metadata()
    for lang in ['en','ja']:
        root=NEW/lang
        for f in ['continuous_qc','subtitle_layout_validation','final_video_motion','qc_v02']:
            data=read(root/'records'/(f+'.json'))
            assert data['passed']
            shutil.copy2(root/'records'/(f+'.json'),R/lang)
        for f in (root/'review').glob('continuous_*_sheet*.jpg'):shutil.copy2(f,SHARE)
        srt=next(root.glob('deliverables/*.srt'))
        blocks=srt.read_text().strip().split('\n\n')
        body=''.join(''.join(b.splitlines()[2:]) for b in blocks)
        content=read(root/'records'/('content_en.json' if lang=='en' else 'content.json'))
        clean=lambda t:re.sub(r'\s+','',t)
        assert clean(body)==clean(''.join(c['text'] for c in content['segments']))
        for b in blocks:
            lines=b.splitlines()[2:]
            assert len(lines)<=2 and max(map(len,lines))<=(42 if lang=='en' else 23)
        assert [(round(c['end']-c['start'],3)>=1.4) for c in read(root/f'records/subtitle_cues_{lang}.json')['cues']].count(False)==0
        save(R/lang/'subtitles.json',dict(count=len(blocks),srt_sha256=sha(srt),script_matches=True))
    sheets4k()
    shutil.copytree(R,SHARE/'records',dirs_exist_ok=True)
    groups={'audio_and_subtitles':[p for p in D.iterdir() if p.suffix in ['.m4a','.wav','.srt','.txt']],
            'thumbnails_and_metadata':[p for p in D.iterdir() if p.suffix in ['.jpg','.md']],
            'QA_records':[*R.rglob('*.json'),*SHARE.glob('*.jpg')]}
    for group,files in groups.items():
        p=D/f'EP012_{group}_v02.zip'
        with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
            for f in sorted(files):z.write(f,Path('records')/f.relative_to(R) if f.is_relative_to(R) else f.name)
        with zipfile.ZipFile(p) as z:assert z.testzip() is None

def report():
    share=read(R/'sharing.json')
    assert share['draft'] and share['status']=='verified' and len(share['assets'])==8
    shutil.copy2(R/'sharing.json',SHARE/'records')
    lines=['# Quiet Origins 第12話 確認版v02 制作結果','','英語P01のナレーションは33.478秒で終わり、P02は34.400秒で始まる。区間末の空きはv01の約7.1秒から0.922秒になった。v01から英日各14区間の語りを取り出し、配置前に全PCMサンプルを元のナレーショントラックと照合した。','',
           '| 言語 | 総尺 | フレーム | OP | ED | ヴェダー | 音量 | ピーク | 字幕と帯の最小間隔 |','|---|---:|---:|---|---|---:|---:|---:|---:|']
    for l in ['en','ja']:
        r=R/l;m=read(r/'timeline.json');q=read(r/'qc_v02.json')['files'][0];v=next(x for x in read(r/'render_shots.json') if x['key']=='N11-B')
        op,ed=(m['brand_intervals'][k] for k in ['opening','endcard'])
        lines.append(f"| {l} | {m['duration']:.3f}秒 | {q['frames']:,} | {op[0]:.3f}–{op[1]:.3f}秒 | {ed[0]:.3f}–{ed[1]:.3f}秒 | {v['frames']/30:.3f}秒 | {q['loudness']['input_i']} LUFS | {q['loudness']['input_tp']} dBTP | {read(r/'subtitle_layout_validation.json')['min_gap']}px |")
    lines+=['','英日各23ショット。通常版・字幕入り版・英語4Kの全5本を最後までデコードし、警告0件。英1080p・日1080p・英4Kは全フレームで形式各1種類、ショットごとの先頭・中央・末尾を各69枚採取。英語4Kは修正版の英語1080pをLanczosで拡大し、音声ストリーム一致。','',
           '字幕と映像の切替は各言語の字幕ページに従う。同じページに複数の年がある場合は文字位置で補間。英語概要欄はチャプターと指示されたクレジット2行を変更、日本語はチャプターを更新。サムネはv01の3枚をハッシュ照合して再利用。','',
           '## 区間末の間（秒）','','語りファイルの終端から次の語りファイルの先頭までを測定。P02は表の間に4秒のOPが加わる。P14は次の語りに代わりEDの先頭まで。冒頭は英日とも1.8秒。','','|区間|英語の間|日本語の間|備考|','|---|---:|---:|---|']
    gs=[read(R/l/'voice_gaps.json')['gaps'] for l in ['en','ja']]
    for a,b in zip(*gs):
        id=a['id'];note='OP込み '+f"{a['to_next_voice']:.3f} / {b['to_next_voice']:.3f} 秒" if id=='P02' else '比較カード1.5秒を含む' if a['card_hold'] else 'EDの先頭まで' if id=='P14' else ''
        lines.append(f"| {id} | {a['gap']:.3f} | {b['gap']:.3f} | {note} |")
    lines+=['','## 語り単体の測定','','−45 dB以下が2秒以上続いた全区間。音声ファイル内の語頭・語尾の余白を含むため、上の配置上の間隔と差がある。','','|言語|開始（秒）|終了（秒）|長さ（秒）|画面|','|---|---:|---:|---:|---|']
    for l in ['en','ja']:
        for x in read(R/l/'voice_gaps.json')['silence']:lines.append(f"| {l} | {x['start']:.3f} | {x['end']:.3f} | {x['duration']:.3f} | {x['reason']} |")
    lines+=['','OP・ED・比較カード以外の検出は英日とも0件。','',
            f"非公開Draft Release {share['release_id']}。8添付をRelease ID経由のRESTで全量再取得し、バイト数とSHA-256の一致、匿名404を確認。[取得案内と試写資料](wom12_確認版_v02_20261105/README.md)。"]
    (P/'wom12_制作結果_v02_20261105.md').write_text('\n'.join(lines)+'\n')
    links=['# 第12話「サンタクロースの赤い服」確認版v02','',f"[非公開Draft Releaseを開く]({share['release_url']})。Release ID は {share['release_id']}。英語版は33秒ごろに続く次の語りを確認してください。",'','[英語投稿情報](EP012_upload_info_en.md)・[日本語投稿情報](EP012_upload_info_ja.md)・[区間の間と語り単体の検品表](../wom12_制作結果_v02_20261105.md)。','']
    for l in ['en','ja']:
        links.append(f"- {l} [字幕に対応する年代と切替時刻](records/{l}/rail_switches.json)・[ショットと素材・表示時間](records/{l}/render_shots.json)・[音声検査](records/{l}/voice_gaps.json)。")
    links+=['','|添付|asset ID|バイト|SHA-256|','|---|---:|---:|---|']
    for a in share['assets']:links.append(f"| {a['name']} | {a['asset_id']} | {a['bytes']} | `{a['sha256']}` |")
    links+=['',f"`gh api repos/yasukawa1980/youtube/releases/{share['release_id']}` で一覧を取得。各ファイルは `gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT` で取得。",'',f'SSD保存先 `{NEW}`。']
    (SHARE/'README.md').write_text('\n'.join(links)+'\n')

if __name__=='__main__':
    {'metadata':metadata,'archive':archive,'report':report}[sys.argv[1]]()
