"""Prepare source records, review images and a compact review ZIP for Claude."""
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image
from wom_shorts_ep010 import ROOT,REPO,REQUEST,MAIN,sha,save


def main():
    qc=json.loads((ROOT/'records/final_qc.json').read_text())
    motion=json.loads((ROOT/'records/final_pixel_motion.json').read_text())
    assert len(qc)==3 and motion['passed']
    source=json.loads((MAIN/'records/source_assets.json').read_text())
    ids={'K06a','K09b','K07b','K06b','K01a','K04a','K05b'}
    selected=[a for a in source['assets'] if a['id'] in ids]
    assert len(selected)==7
    save(ROOT/'records/source_assets.json',dict(assets=selected,count=7,cards=['D_1869','D_house'],no_AI=True))
    save(ROOT/'records/approval.json',dict(request=str(REQUEST),request_sha256=sha(REQUEST),duration_exception=json.loads((ROOT/'records/duration_exception.json').read_text()),human_full_listening=False,claude_review_pending=True,youtube_posted=False))
    (ROOT/'review/README.txt').write_text('Quiet Origins EP010 shorts v01\nK1 21.533333s / K2 24.533333s (explicitly approved exception) / K3 20.933333s\nBurned-in English captions. No YouTube upload. Human listening and Claude review pending.\nOpening: 0, 0.5, 1, 1.5, 2, 2.5 seconds. All caption pages, every 2 seconds, cuts, CTA.\n')
    for p in (ROOT/'review').rglob('*.jpg'):
        im=Image.open(p);assert max(im.size)<=1280 and p.stat().st_size<1_000_000,(p,im.size,p.stat().st_size)
    members=sorted([*ROOT.glob('records/*.json'),*ROOT.glob('review/**/*.jpg'),ROOT/'review/README.txt'])
    members=[p for p in members if p.name!='github_draft_release.json']
    archive=ROOT/'deliverables/EP010_shorts_review_v01.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in members:z.write(p,p.relative_to(ROOT))
    files=[*sorted(ROOT.glob('deliverables/QO_short_EP010_K*_v01.mp4')),archive]
    assert len(files)==4
    save(ROOT/'records/delivery_files.json',[dict(file=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files])
    dest=REPO/'wom_ショート確認版_EP010_v01_20261103'
    (dest/'records').mkdir(parents=True,exist_ok=True)
    (dest/'確認画像').mkdir(exist_ok=True)
    for p in ROOT.glob('records/*.json'):shutil.copy2(p,dest/'records'/p.name)
    for p in ROOT.glob('review/*.jpg'):shutil.copy2(p,dest/'確認画像'/p.name)
    for kind in ['opening','all_captions']:
        for folder in ROOT.glob(f'review/K*_{kind}'):
            out=dest/'確認画像'/folder.name;out.mkdir(exist_ok=True)
            for p in folder.glob('*.jpg'):shutil.copy2(p,out/p.name)
    print('REVIEW READY',archive.stat().st_size,'bytes',len(members),'ZIP members',flush=True)


if __name__=='__main__':main()
