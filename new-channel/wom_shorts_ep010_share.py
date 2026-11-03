"""Upload the four EP010 review artifacts to a new nonpublic GitHub Draft Release."""
import argparse
import hashlib
import json
import subprocess

from wom_shorts_ep010 import ROOT,save,sha
from wom_shorts_remake_share_v03 import api,assert_anonymous_hidden

REPO='yasukawa1980/youtube'
TAG='quiet-origins-ep010-shorts-v01-20261103'


def main():
    files=sorted([*ROOT.glob('deliverables/QO_short_EP010_K*_v01.mp4'),
                  *ROOT.glob('deliverables/EP010_shorts_review_v01.zip')])
    assert len(files)==4
    qc=json.loads((ROOT/'records/final_qc.json').read_text())
    assert len(qc)==3 and all(r['continuous_decode_warning_count']==0 for r in qc)
    assert json.loads((ROOT/'records/final_pixel_motion.json').read_text())['passed']
    releases=api([f'repos/{REPO}/releases?per_page=100'])
    release=next((r for r in releases if r['tag_name']==TAG),None)
    if release is None:
        release=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],{
            'tag_name':TAG,'target_commitish':'bgm/production',
            'name':'Quiet Origins 第10話クランプス ショート3本 確認版v01（未投稿）',
            'body':'本人承認済みのK1・K2・K3台本。K2のみ24.533333秒を本人が例外承認。素材9点・重複なし・AI映像なし。字幕はArial Narrow Bold 55pt固定。最後2.5秒に登録案内。Claude確認・本人試聴待ち。YouTubeには投稿しない。',
            'draft':True})
    assert release['draft']
    rid=release['id'];assert_anonymous_hidden(f'repos/{REPO}/releases/{rid}')
    state=dict(release_id=rid,tag=TAG,draft=True,release_url=release['html_url'],status='uploading')
    save(ROOT/'records/github_draft_release.json',state)
    for path in files:
        old=next((a for a in release['assets'] if a['name']==path.name),None)
        if old:assert old['state']=='uploaded' and old['digest']=='sha256:'+sha(path)
        else:subprocess.run(['gh','release','upload',TAG,str(path),'--repo',REPO],check=True)
        print('UPLOADED',path.name,flush=True)
    release=api([f'repos/{REPO}/releases/{rid}'])
    assert release['draft'] and len(release['assets'])==4
    checks=[]
    for path in files:
        asset=next(a for a in release['assets'] if a['name']==path.name)
        h=hashlib.sha256();size=0
        proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPO}/releases/assets/{asset["id"]}'],stdout=subprocess.PIPE)
        for chunk in iter(lambda:proc.stdout.read(1048576),b''):h.update(chunk);size+=len(chunk)
        assert proc.wait()==0 and size==path.stat().st_size and h.hexdigest()==sha(path)
        assert asset['digest']=='sha256:'+h.hexdigest()
        assert_anonymous_hidden(f'repos/{REPO}/releases/assets/{asset["id"]}')
        checks.append(dict(name=path.name,asset_id=asset['id'],bytes=size,sha256=h.hexdigest(),rest_download_verified=True,anonymous_http_status=404,browser_download_url=asset['browser_download_url']))
        print('REST VERIFIED',path.name,flush=True)
    state.update(status='verified',assets=checks)
    save(ROOT/'records/github_draft_release.json',state)
    print('SHARED',rid,len(checks),flush=True)


if __name__=='__main__':main()
