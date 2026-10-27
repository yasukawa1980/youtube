"""Portable v01/v02/v03 comparison and private Draft sharing for EP006."""
import os, sys, html, shutil, zipfile
from pathlib import Path
import wom06_shorts_revision_v03 as rev
os.environ['QO_EP006_RELEASE_TAG']='qo-shorts-ep006-hook-v03-20261027'
os.environ['QO_EP006_RELEASE_NAME']='Quiet Origins：スフィンクス ショート冒頭 v03'
os.environ['QO_EP006_RELEASE_BODY']='本人承認済みのClaude v03依頼を反映。最初のショットだけを拡大し、0秒見出しと1.00→1.08倍の寄りを追加。音声ストリーム・字幕・尺・カット時刻を保全。後続画素差は記録済み。v01/v02/v03の比較動画を同梱。YouTube未投稿・未公開Draft。'
import wom06_shorts_delivery as delivery
ROOT=rev.ROOT


def docs():
    delivery.docs()
    records=[]
    for version,folder in [('v01',rev.V01),('v02',rev.OLD)]:
        for sid in rev.HEADLINES:
            src=folder/f'deliverables/QO_short_EP006_{sid}_{version}.mp4';dst=ROOT/'deliverables'/src.name
            if not dst.exists():shutil.copy2(src,dst)
            assert rev.sha(src)==rev.sha(dst)
            records.append(dict(id=sid,version=version,source=str(src),file=dst.name,sha256=rev.sha(dst),bytes=dst.stat().st_size))
    rev.save(ROOT/'records/comparison_versions.json',dict(original_versions_copied_without_changes=True,files=records))
    sections=[]
    for sid in rev.HEADLINES:
        cards=[]
        for version,label in [('v01','制作版 v01'),('v02','結論先行 v02'),('v03','大きな見出し・構図 v03')]:
            cards.append(f'<article><h3>{label}</h3><video controls preload="metadata" src="QO_short_EP006_{sid}_{version}.mp4"></video></article>')
        sections.append(f'<section><h2>{sid}</h2><div class="trio">'+''.join(cards)+'</div></section>')
    page='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>スフィンクス｜v01・v02・v03の比較</title><style>body{max-width:1350px;margin:28px auto;padding:0 24px;background:#101c22;color:#f4efdf;font:17px/1.65 system-ui}h1,h2,h3{color:#d8b575}h1{font-size:30px}h3{font-size:17px}.trio{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}video{width:100%;max-height:65vh;background:#000}section{border-top:1px solid #405052;margin-top:28px;padding:16px 0}p{max-width:85ch}@media(max-width:750px){.trio{grid-template-columns:1fr}}a{color:#d8b575}</style><h1>スフィンクスのショート：冒頭の比較</h1><p>各版を最初の3秒まで再生して、見出し・資料の大きさ・動きを比較できます。v03は最初のショットだけを修正し、v02の声・字幕・尺を維持しています。再生すると他の動画は一時停止します。</p><p>3本とも未投稿。S1は20秒、S2は18秒、S3は21.67秒。S2の後続映像には再圧縮による差があります（395フレーム中166フレーム、全比較フレームの平均輝度差0.222/255）。S1・S3の後続は画素一致です。</p>'''+''.join(sections)+'''<p>共有版はpreview.htmlと9本のMP4を同じフォルダへ保存して開いてください。v01・v02は元ファイルの同一コピーです。</p><script>document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(w=>{if(w!==v)w.pause()})));</script></html>'''
    (ROOT/'deliverables/preview.html').write_text(page)
    for sid in rev.HEADLINES:shutil.copy2(ROOT/f'review/{sid}_opening_0_to_2_5s.jpg',ROOT/f'deliverables/{sid}_opening_0_to_2_5s.jpg')
    with zipfile.ZipFile(ROOT/'deliverables/opening_frames_18.zip','w',zipfile.ZIP_DEFLATED) as z:
        for sid in rev.HEADLINES:
            for p in sorted((ROOT/f'review/opening_{sid}').glob('*.jpg')):z.write(p,f'{sid}/{p.name}')
    # Rebuild the record bundle after adding comparison provenance; no media intermediates.
    with zipfile.ZipFile(ROOT/'deliverables/production_records.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT/'records').iterdir()):
            if p.suffix in ['.json','.csv','.log'] and not p.name.startswith(('sharing','draft_access')):z.write(p,'records/'+p.name)
        for name in ['wom06_shorts_revision_v03.py','wom06_shorts_revision_qc_v03.py','wom06_shorts_revision_delivery_v03.py','wom06_shorts_revision_report_v03.py','wom06_shorts_v02_config.json','wom_ショート冒頭修正_EP006_v03_20261027.md']:
            p=rev.HERE/name
            if p.exists():z.write(p,'revision/'+name)
    print('PORTABLE 9-VIDEO COMPARISON READY',flush=True)


def selected_files():
    files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.suffix in ['.mp4','.srt','.jpg','.csv','.txt','.html','.zip'] and p.name!='SHA256SUMS_shared.txt')
    for version in ['v01','v02','v03']:assert sum(p.name.endswith(f'_{version}.mp4') for p in files)==3
    return files


if __name__=='__main__':
    if sys.argv[1]=='docs':docs()
    elif sys.argv[1]=='share':
        assert rev.read(ROOT/'records/preservation_qc.json')['passed']
        assert rev.read(ROOT/'records/headline_qc.json')['passed']
        assert rev.read(ROOT/'records/safe_crop_qc.json')['passed']
        delivery.selected_files=selected_files;delivery.share()
    else:raise SystemExit('docs|share')
