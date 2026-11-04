"""Resume EP011 private-release verification through bounded REST byte ranges.

Usage: python wom11_rest_recovery.py <v02 ROOT>
Only the final 4K asset is recovered; seven earlier REST checks must already exist.
"""
import concurrent.futures
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO='yasukawa1980/youtube'
CHUNK=8*1024*1024

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    root=Path(sys.argv[1]);record=root/'records/sharing.json'
    state=json.loads(record.read_text())
    release=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/{state["release_id"]}']))
    assert release['draft'] and len(release['assets'])==8 and len(state['assets'])==7
    for c in state['assets']:
        a=next(x for x in release['assets'] if x['id']==c['asset_id'])
        assert c['rest_download_verified'] and a['size']==c['bytes'] and a['digest']=='sha256:'+c['sha256']
        assert digest(root/'deliverables'/c['name'])==c['sha256']
    asset=next(a for a in release['assets'] if a['name'].endswith('_v02_2160p30.mp4'))
    src=root/'deliverables_4k'/asset['name'];expected=digest(src);size=src.stat().st_size
    assert size==asset['size'] and asset['digest']=='sha256:'+expected
    cache=root/'_work/rest_recovery'/str(asset['id']);cache.mkdir(parents=True,exist_ok=True)
    endpoint=f'repos/{REPO}/releases/assets/{asset["id"]}'
    def fetch(start):
        end=min(start+CHUNK,size)-1;part=cache/f'{start:012d}.part';meta=part.with_suffix('.json')
        if part.exists() and meta.exists():
            m=json.loads(meta.read_text())
            if m['start']==start and m['end']==end and part.stat().st_size==end-start+1 and digest(part)==m['sha256']:
                return part
        response=part.with_suffix('.response');partial=part.with_suffix('.partial')
        prefix=partial.read_bytes() if partial.exists() else b''
        assert len(prefix)<=end-start+1
        def absorb(prefix):
            if not response.exists():return prefix
            data=response.read_bytes();split=re.search(rb'\r?\n\r?\n',data)
            if not split:return prefix
            header=data[:split.start()].decode('ascii',errors='replace');body=data[split.end():]
            match=re.search(r'(?im)^content-range: bytes (\d+)-(\d+)/(\d+)\r?$',header)
            if (' 206 ' not in header.splitlines()[0] or not match
                or tuple(map(int,match.groups()))!=(start+len(prefix),end,size)
                or len(body)>end-start+1-len(prefix)):return prefix
            prefix+=body;partial.write_bytes(prefix)
            return prefix
        prefix=absorb(prefix)
        for attempt in range(21):
            if len(prefix)==end-start+1:
                part.write_bytes(prefix)
                meta.write_text(json.dumps({'start':start,'end':end,'sha256':digest(part)})+'\n')
                print('RANGE VERIFIED',start,end,flush=True)
                return part
            before=len(prefix)
            try:
                with response.open('wb') as f:
                    subprocess.run(['gh','api','-i','-H','Accept: application/octet-stream','-H',f'Range: bytes={start+len(prefix)}-{end}',endpoint],stdout=f,stderr=subprocess.PIPE,timeout=60,check=True)
            except subprocess.SubprocessError as e:
                print('RANGE RETRY',start,attempt+1,type(e).__name__,flush=True)
            prefix=absorb(prefix)
            if len(prefix)>before:print('RANGE RECEIVED',start,len(prefix),'/',end-start+1,flush=True)
            else:time.sleep(3)
        raise RuntimeError(f'Range retrieval failed at {start}')
    starts=list(range(0,size,CHUNK))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:parts=list(pool.map(fetch,starts))
    h=hashlib.sha256();n=0
    for p in parts:
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1048576),b''):h.update(b);n+=len(b)
    assert n==size and h.hexdigest()==expected
    for ep in [f'repos/{REPO}/releases/{release["id"]}',endpoint]:
        accept='application/octet-stream' if '/assets/' in ep else 'application/vnd.github+json'
        for attempt in range(3):
            code=subprocess.check_output(['curl','-q','-sS','-o','/dev/null','-w','%{http_code}','-H','Accept: '+accept,'https://api.github.com/'+ep],text=True)
            if code=='404':break
            time.sleep(2)
        assert code=='404',f'Anonymous status {code}'
    latest=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/{release["id"]}']))
    assert latest['draft'] and len(latest['assets'])==8
    state['assets'].append({'name':asset['name'],'asset_id':asset['id'],'bytes':size,'sha256':expected,'rest_download_verified':True,'rest_method':'authenticated REST Range requests; contiguous full coverage and final whole-file SHA-256','range_count':len(parts),'anonymous_http_status':404,'browser_download_url':asset['browser_download_url']})
    state['status']='verified';record.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
    print('REST VERIFIED ALL EIGHT',release['id'],size,expected,flush=True)

if __name__=='__main__':main()
