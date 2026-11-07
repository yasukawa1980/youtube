"""Quiet Origins EP013 provisional review: create a draft and verify every asset through REST."""
import argparse
import hashlib
import json
import shutil
import subprocess
import os
import time
from pathlib import Path

REPO='yasukawa1980/youtube'
VERSION=os.environ.get('WOM13_VERSION','v01')
assert VERSION in ['v01','v02']
TAG=f'quiet-origins-ep013-{VERSION}-20261107'

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
    files=sorted([*a.folder.glob(f'EP013_NightWatch_*_{VERSION}*.mp4'),*a.folder.glob(f'EP013_*_{VERSION}.zip')])
    assert len(files)==8, len(files)
    assert all(p.name.isascii() for p in files)
    releases=api([f'repos/{REPO}/releases?per_page=100'])
    r=next((r for r in releases if r['tag_name']==TAG),None)
    if r is None:
        r=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],{
            'tag_name':TAG,'target_commitish':'bgm/production',
            'name':f'Quiet Origins 第13話 確認版{VERSION}（英日・非公開）',
            'body':'Quiet Origins 第13話「夜警」。承認済み台本v02。英日1080p本編、英語原寸素材からの4K版、字幕入り英日確認版、音声・字幕・サムネ2案と検品記録。非公開・本人試聴とClaude確認待ち。',
            'draft':True})
    assert r['draft'] is True
    # Empty draft is checked before any media is uploaded. Never publish it.
    assert_anonymous_hidden(f'repos/{REPO}/releases/{r["id"]}')
    previous=json.loads(a.record.read_text()) if a.record.exists() else {}
    cached_checks=previous.get('assets',[]) if previous.get('release_id')==r['id'] else []
    state={'release_id':r['id'],'tag':TAG,'draft':True,'release_url':r['html_url'],'status':'uploading','assets':cached_checks}
    a.record.write_text(json.dumps(state,indent=2)+'\n')
    def upload(p):
        checksum = 'sha256:'+sha(p)
        old=next((v for v in r['assets'] if v['name']==p.name or v['digest']==checksum),None)
        if old:
            assert old['state']=='uploaded' and old['digest']==checksum
            if old['name']!=p.name:
                api(['--method','PATCH',f'repos/{REPO}/releases/assets/{old["id"]}','--input','-'],{'name':p.name})
        else:
            subprocess.run(['gh','release','upload',TAG,str(p),'--repo',REPO],check=True)
        print('UPLOADED',p.name,flush=True)
    if VERSION=='v02':
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as pool:
            list(pool.map(upload, sorted(files,key=lambda p:-p.stat().st_size)))
    else:
        for p in files:upload(p)
    r=api([f'repos/{REPO}/releases/{r["id"]}'])
    assert r['draft'] is True and len(r['assets'])==len(files)
    checks=[]
    for p in files:
        asset=next(v for v in r['assets'] if v['name']==p.name)
        expected_sha=sha(p)
        cached=next((c for c in cached_checks if c['asset_id']==asset['id'] and c['name']==p.name
                     and c['bytes']==p.stat().st_size and c['sha256']==expected_sha
                     and c.get('rest_download_verified') is True),None)
        assert asset['digest']=='sha256:'+expected_sha and asset['size']==p.stat().st_size
        if not cached:
            for attempt in range(3):
                h=hashlib.sha256();n=0;next_progress=64*1048576
                proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',
                                       f'repos/{REPO}/releases/assets/{asset["id"]}'],stdout=subprocess.PIPE)
                for b in iter(lambda:proc.stdout.read(1048576),b''):
                    h.update(b);n+=len(b)
                    if n>=next_progress:
                        print('REST PROGRESS',p.name,n,'/',p.stat().st_size,flush=True);next_progress+=64*1048576
                success=proc.wait()==0 and n==p.stat().st_size and h.hexdigest()==expected_sha
                if success:break
                print('REST RETRY',p.name,attempt+1,flush=True);time.sleep(2)
            assert success,f'REST verification failed after three attempts: {p.name}'
        assert_anonymous_hidden(f'repos/{REPO}/releases/assets/{asset["id"]}')
        checks.append({'name':p.name,'asset_id':asset['id'],'bytes':p.stat().st_size,'sha256':expected_sha,
                       'rest_download_verified':True,'anonymous_http_status':404,
                       'browser_download_url':asset['browser_download_url']})
        state.update(status='verifying',assets=checks)
        a.record.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
        print('REST CHECKPOINT VERIFIED' if cached else 'REST VERIFIED',p.name,flush=True)
    state.update(status='verified',assets=checks)
    a.record.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    print('SHARED',r['id'],len(checks),flush=True)

if __name__=='__main__':main()
