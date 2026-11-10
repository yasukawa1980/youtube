"""Package checked shorts in a new nonpublic Draft Release and verify every download."""
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path
from pnt02_shorts_preflight import ROOT, REPO, guard, save, sha

REPOSITORY='yasukawa1980/youtube'
TAG='qo-pnt02-shorts-v01-20261110'

def api(endpoint,method='GET',data=None):
    args=['gh','api','--method',method,endpoint]
    if data is not None:args+=['--input','-']
    return json.loads(subprocess.check_output(args,input=json.dumps(data).encode() if data is not None else None))

def package():
    guard()
    qc=json.loads((ROOT/'records/final_qc.json').read_text());assert len(qc)==3
    assert all(q['video_duration']<=24 and q['container_duration']<=24 and q['continuous_decode_warning_count']==0 for q in qc)
    assert json.loads((ROOT/'records/final_pixel_motion.json').read_text())['passed']
    assert json.loads((ROOT/'records/final_visual_review.json').read_text())['passed']
    # Exact rendered caption frames at native 1080x1920; smaller review JPEGs remain separate.
    import numpy as np
    from PIL import Image
    from pnt02_shorts_produce import helper
    helper()
    from wom_shorts_remake_qc_v03 import decode
    caps=json.loads((ROOT/'records/caption_manifest.json').read_text())
    out=ROOT/'review_native';out.mkdir(exist_ok=True)
    for sid in ['V1','V2','V3']:
        ns=sorted({(c['start_frame']+c['end_frame'])//2 for c in caps if c['short_id']==sid})
        frames=decode(ROOT/f'deliverables/QO_short_PNT02_{sid}_v01.mp4',ns)
        for n,arr in frames.items():Image.fromarray(arr).save(out/f'{sid}_{n:04}_caption.png')
    sets={
      'PNT02_shorts_review_records_v01.zip':[p for folder in ['records','review','review_native'] for p in (ROOT/folder).rglob('*') if p.is_file()],
      'PNT02_shorts_audio_comparisons_v01.zip':[p for p in (ROOT/'audio').rglob('*') if p.is_file()]}
    for name,files in sets.items():
        with zipfile.ZipFile(ROOT/'deliverables'/name,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('README.txt','PNT02 shorts v01. No YouTube upload. Main/short pronunciation WAVs: actual main sentence, one second silence, actual short sentence excerpt. Native caption PNGs are in review_native/. Human listening remains pending.\n')
            for p in sorted(files):z.write(p,p.relative_to(ROOT))
        print('PACKAGED',name,flush=True)

def share():
    guard()
    files=sorted((ROOT/'deliverables').glob('QO_short_PNT02_V?_v01.mp4'))
    files += [ROOT/'deliverables'/n for n in ['PNT02_shorts_review_records_v01.zip','PNT02_shorts_audio_comparisons_v01.zip']]
    assert len(files)==5 and all(p.is_file() for p in files)
    releases=api(f'repos/{REPOSITORY}/releases?per_page=100')
    r=next((r for r in releases if r['tag_name']==TAG),None)
    if r is None:
        r=api(f'repos/{REPOSITORY}/releases','POST',dict(tag_name=TAG,target_commitish='bgm/production',draft=True,
            name='Quiet Origins 絵画02 ショートV1〜V3 v01（非公開・試聴待ち）',
            body='停止30f49cbbから再開し、範囲修正7ede2457を反映。既存音声を再利用。完成MP4は22.367・20.067・18.400秒、全編デコード警告0、全3組の範囲重なり0px²。字幕・画像・音量の検品記録と固有名詞4語の本編比較音声を添付。Claude確認・本人試聴待ち。YouTube投稿・予約なし。結果: bgm/production の painting/pnt02_ショート制作結果_20261110.md。'))
    rid=r['id'];assert r['draft'] is True
    state=dict(release_id=rid,tag=TAG,url=r['html_url'],draft=True,status='uploading',assets=[])
    record=ROOT/'records/sharing.json';save(record,state)
    for p in files:
        expected=sha(p)
        r=api(f'repos/{REPOSITORY}/releases/{rid}');assert r['draft'] is True
        old=next((a for a in r['assets'] if a['name']==p.name),None)
        if old:assert old['digest']=='sha256:'+expected,'Different existing asset: preserve and stop'
        else:
            subprocess.run(['gh','api','--method','POST',f'https://uploads.github.com/repos/{REPOSITORY}/releases/{rid}/assets?name={p.name}',
                            '-H','Content-Type: application/octet-stream','--input',str(p),'--silent'],check=True)
        r=api(f'repos/{REPOSITORY}/releases/{rid}');assert r['draft'] is True
        a=next(a for a in r['assets'] if a['name']==p.name)
        assert a['digest']=='sha256:'+expected and a['size']==p.stat().st_size
        proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPOSITORY}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE)
        h=hashlib.sha256();size=0
        for chunk in iter(lambda:proc.stdout.read(1024*1024),b''):h.update(chunk);size+=len(chunk)
        assert proc.wait()==0 and h.hexdigest()==expected and size==p.stat().st_size
        state['assets'].append(dict(name=p.name,asset_id=a['id'],bytes=size,sha256=expected,rest_download_verified=True));save(record,state)
        print('REST VERIFIED',p.name,flush=True)
    status=subprocess.check_output(['curl','-q','-sS','-o','/dev/null','-w','%{http_code}',f'https://api.github.com/repos/{REPOSITORY}/releases/{rid}'],text=True)
    assert status=='404'
    state.update(status='shared_pending_Claude_and_user_listening',anonymous_http_status=status,youtube_posted=False)
    save(record,state);print('PRIVATE DRAFT VERIFIED',rid,flush=True)

if __name__=='__main__':globals()[sys.argv[1]]()
