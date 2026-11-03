"""Quiet Origins EP010 provisional review: create a draft and verify every asset through REST."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

REPO='yasukawa1980/youtube'
TAG='quiet-origins-ep010-v02-20261103'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()

def api(args,data=None):
    r=subprocess.run(['gh','api',*args],input=json.dumps(data) if data is not None else None,
                     capture_output=True,text=True,check=True)
    return json.loads(r.stdout)

def assert_anonymous_hidden(endpoint):
    accept='application/octet-stream' if '/assets/' in endpoint else 'application/vnd.github+json'
    code=subprocess.check_output(['curl','-q','-sS','-o','/dev/null','-w','%{http_code}',
                                  '-H','Accept: '+accept,
                                  'https://api.github.com/'+endpoint],text=True)
    assert code=='404',f'Anonymous access must be denied: {endpoint} ({code})'

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--folder',type=Path,required=True)
    ap.add_argument('--record',type=Path,required=True)
    a=ap.parse_args()
    files=sorted([*a.folder.glob('EP010_Krampus_*.mp4'),*a.folder.glob('EP010_*.zip'),*a.folder.parent.glob('deliverables_4k/*_v02_2160p30.mp4')])
    assert len(files)==8, len(files)
    assert all(p.name.isascii() for p in files)
    releases=api([f'repos/{REPO}/releases?per_page=100'])
    r=next((r for r in releases if r['tag_name']==TAG),None)
    if r is None:
        r=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],{
            'tag_name':TAG,'target_commitish':'bgm/production',
            'name':'Quiet Origins 第10話 確認版v02（英日・非公開）',
            'body':'Quiet Origins 第10話クランプスの英日確認版v02。承認済み台本v02、既存音声モデルとQO_THEME_A02、原典11点・カード6枚を使用。367.266667秒、H.264 High 1080p30。K03aは本人了承の上半身構図。カード6枚を中央配置へ修正。v02英語4K拡大版を添付。v01の4K版は投稿に使用しない。固有名詞の本人試聴・サムネA/B選択・Claude確認待ち。非公開Draftを維持し、公開・YouTube投稿はしません。',
            'draft':True})
    assert r['draft'] is True
    # Empty draft is checked before any media is uploaded. Never publish it.
    assert_anonymous_hidden(f'repos/{REPO}/releases/{r["id"]}')
    state={'release_id':r['id'],'tag':TAG,'draft':True,'release_url':r['html_url'],'status':'uploading'}
    a.record.write_text(json.dumps(state,indent=2)+'\n')
    for p in files:
        old=next((v for v in r['assets'] if v['name']==p.name or v['digest']=='sha256:'+sha(p)),None)
        if old:
            assert old['state']=='uploaded' and old['digest']=='sha256:'+sha(p)
            if old['name']!=p.name:
                api(['--method','PATCH',f'repos/{REPO}/releases/assets/{old["id"]}','--input','-'],{'name':p.name})
        else:
            subprocess.run(['gh','release','upload',TAG,str(p),'--repo',REPO],check=True)
        print('UPLOADED',p.name,flush=True)
    r=api([f'repos/{REPO}/releases/{r["id"]}'])
    assert r['draft'] is True and len(r['assets'])==len(files)
    checks=[]
    for p in files:
        asset=next(v for v in r['assets'] if v['name']==p.name)
        h=hashlib.sha256();n=0
        proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',
                               f'repos/{REPO}/releases/assets/{asset["id"]}'],stdout=subprocess.PIPE)
        for b in iter(lambda:proc.stdout.read(1048576),b''):h.update(b);n+=len(b)
        assert proc.wait()==0
        assert n==p.stat().st_size and h.hexdigest()==sha(p)
        assert asset['digest']=='sha256:'+h.hexdigest()
        assert_anonymous_hidden(f'repos/{REPO}/releases/assets/{asset["id"]}')
        checks.append({'name':p.name,'asset_id':asset['id'],'bytes':n,'sha256':h.hexdigest(),
                       'rest_download_verified':True,'anonymous_http_status':404,
                       'browser_download_url':asset['browser_download_url']})
        print('REST VERIFIED',p.name,flush=True)
    state.update(status='verified',assets=checks)
    a.record.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    print('SHARED',r['id'],len(checks),flush=True)

if __name__=='__main__':main()
