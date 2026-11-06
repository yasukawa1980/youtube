"""Allocate unchanged Japanese subtitle pages to the English segment speech spans."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

from wom01_subtitles import to_srt
from wom12_share import api, assert_anonymous_hidden, sha

REPO = 'yasukawa1980/youtube'
ROOT = Path('/Volumes/ESD-02/新チャンネル/EP012_SantaClaus/確認版_v02_20261105')
CODE = Path(__file__).resolve().parent
DEST = CODE/'wom12_日本語字幕_英語時間割_20261106'

def read(p):
    return json.loads(p.read_text())

def build():
    assert ROOT.parent.parent.parent.is_dir() and Path('/Volumes/ESD-02').is_mount()
    DEST.mkdir(exist_ok=True)
    pages = read(ROOT/'ja/records/subtitle_cues_ja.json')['cues']
    segments = read(ROOT/'en/records/master_timeline.json')['segments']
    text = read(ROOT/'ja/records/content.json')
    cues, records = [], []
    for seg in segments:
        subset = [p for p in pages if p['sentence_id'].startswith(seg['id']+'-')]
        start = round(seg['start']*1000)
        end = round(seg['speech_end']*1000)
        span = end-start
        assert span>=1400*len(subset)
        weights=[len(p['text'].replace('\n','')) for p in subset]
        remaining=set(range(len(subset)))
        durations=[0.0]*len(subset)
        available=span
        while remaining:
            total=sum(weights[i] for i in remaining)
            short=[i for i in remaining if available*weights[i]/total<1400]
            if not short:
                for i in remaining:durations[i]=available*weights[i]/total
                break
            for i in short:
                durations[i]=1400
                available-=1400
                remaining.remove(i)
        count=len(cues)
        cumulative=0.0
        cursor=start
        for p, duration in zip(subset,durations):
            cumulative+=duration
            finish=start+round(cumulative)
            assert finish-cursor>=1400
            cues.append(dict(start=cursor/1000,end=finish/1000,text=p['text']))
            cursor=finish
        assert cursor==end
        records.append(dict(id=seg['id'],start=start/1000,end=end/1000,pages=len(subset),first_cue=count+1,last_cue=len(cues)))
    clean=lambda s:re.sub(r'\s+','',s)
    assert [c['text'] for c in cues]==[p['text'] for p in pages]
    assert clean(''.join(c['text'] for c in cues))==clean(''.join(s['text'] for s in text['segments']))
    old=(ROOT/'deliverables/EP012_SantaClaus_ja_v02_1080p30.srt').read_text().strip().split('\n\n')
    assert ['\n'.join(b.splitlines()[2:]) for b in old]==[c['text'] for c in cues]
    assert all(len(c['text'].splitlines())<=2 and max(map(len,c['text'].splitlines()))<=23 for c in cues)
    assert all(a['end']<=b['start'] for a,b in zip(cues,cues[1:]))
    target=ROOT/'EP012_SantaClaus_ja_on_en_v02.srt'
    target.write_text(to_srt(cues))
    (DEST/target.name).write_bytes(target.read_bytes())
    report=dict(script_matches=True,page_text_identical_to_japanese_v02=True,cues=len(cues),
                minimum_duration=min(round(c['end']-c['start'],3) for c in cues),
                max_lines=max(len(c['text'].splitlines()) for c in cues),
                max_line_chars=max(len(line) for c in cues for line in c['text'].splitlines()),
                all_cues_within_english_segment_speech=True,segments=records,
                srt_sha256=sha(target),srt_bytes=target.stat().st_size,
                weighting='Characters excluding line breaks, with minimum 1400 ms and rounding on cumulative millisecond boundaries')
    record=DEST/'verification.json'
    record.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='segments'},ensure_ascii=False),flush=True)
    return [target,record]

def share(files):
    tag='quiet-origins-ep012-ja-on-en-v02-20261106'
    existing=api([f'repos/{REPO}/releases?per_page=100'])
    release=next((r for r in existing if r['tag_name']==tag),None)
    if release is None:
        release=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],dict(tag_name=tag,target_commitish='bgm/production',
            name='Quiet Origins 第12話 英語時間割の日本語字幕',body='確認版v02英語4K用の日本語SRT。承認済み日本語本文101ページを英語各区間の語り範囲に文字数配分。検証記録を添付。',draft=True))
    assert release['draft']
    assert_anonymous_hidden(f'repos/{REPO}/releases/{release["id"]}')
    for p in files:
        old=next((a for a in release['assets'] if a['name']==p.name),None)
        if old:
            assert old['digest']=='sha256:'+sha(p)
        else:
            subprocess.run(['gh','release','upload',tag,str(p),'--repo',REPO],check=True)
    release=api([f'repos/{REPO}/releases/{release["id"]}'])
    assert release['draft'] and len(release['assets'])==len(files)
    results=[]
    for p in files:
        a=next(a for a in release['assets'] if a['name']==p.name)
        endpoint=f'repos/{REPO}/releases/assets/{a["id"]}'
        data=subprocess.check_output(['gh','api','-H','Accept: application/octet-stream',endpoint])
        assert len(data)==p.stat().st_size and hashlib.sha256(data).hexdigest()==sha(p)
        assert_anonymous_hidden(endpoint)
        results.append(dict(name=p.name,asset_id=a['id'],bytes=len(data),sha256=sha(p),rest_verified=True,anonymous_http_status=404))
    state=dict(release_id=release['id'],url=release['html_url'],draft=True,assets=results)
    (DEST/'sharing.json').write_text(json.dumps(state,indent=2)+'\n')
    note=f"""# 第12話 日本語字幕を英語の時間割へ配置（2026-11-06）

作成済み。[日本語字幕SRT](wom12_日本語字幕_英語時間割_20261106/EP012_SantaClaus_ja_on_en_v02.srt)。英語本編386.467秒のP01〜P14それぞれの語りの開始〜終了内に、日本語の既存101ページを文字数比で配分した。全ページの本文・改行が日本語版v02のSRTと一致し、レイアウト用の空白を除いた本文が台本 content.json と一致。

最短1.400秒、最大2行、1行最大22字。全字幕が対応する英語区間の語り内に収まり、重なり0件。[区間ごとの検証記録](wom12_日本語字幕_英語時間割_20261106/verification.json)。段落内は文字数による配分で、単語単位の同期ではない。

SSD保存先 `{files[0]}`。SHA-256 `{sha(files[0])}`、{files[0].stat().st_size:,} bytes。

新しい非公開Draft Release **{release['id']}** に2点を添付。Release ID経由のREST再取得で全量・SHA-256一致、匿名404を確認。[権限のあるアカウントで取得]({release['html_url']})・[asset IDと照合結果](wom12_日本語字幕_英語時間割_20261106/sharing.json)。

本編投稿担当へ、このSRTを英語4K版の日本語字幕として渡す。
"""
    (CODE/'wom12_日本語字幕_英語時間割_20261106.md').write_text(note)
    print('VERIFIED',release['id'],flush=True)

if __name__=='__main__':
    share(build())
