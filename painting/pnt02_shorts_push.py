"""Push only this resume's records atop current remote, preserving local HEAD/index."""
import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

REPO=Path(__file__).resolve().parent.parent
BASE='7ede2457acce8736cab572fd561ac801c84d5484'
BRANCH='bgm/production'
REVIEW=REPO/'painting/pnt02_ショート確認版_v01_20261110/records/corrected_7ede2457'

def git(*args,env=None,data=None):
    return subprocess.check_output(['git',*args],cwd=REPO,env=env,input=data)

def blob(rev,path):
    result=subprocess.run(['git','show',f'{rev}:{path}'],cwd=REPO,capture_output=True)
    if result.returncode:
        assert not git('ls-tree',rev,'--',path).strip(),path
        return None
    return result.stdout

def main():
    index=REPO/'.git/index';indexhash=hashlib.sha256(index.read_bytes()).hexdigest();head=git('rev-parse','HEAD')
    git('fetch','origin',BRANCH);parent=git('rev-parse',f'origin/{BRANCH}').decode().strip()
    git('merge-base','--is-ancestor',BASE,parent)
    paths=[REPO/'painting'/n for n in ['pnt02_shorts_preflight.py','pnt02_shorts_produce.py','pnt02_shorts_resume.py','pnt02_shorts_qc.py','pnt02_shorts_share.py','pnt02_shorts_push.py','pnt02_ショート制作結果_20261110.md']]
    paths += sorted(p for p in REVIEW.rglob('*') if p.is_file())
    changes=[]
    for p in paths:
        assert p.suffix in ['.py','.json','.md','.jpg','.log'] and p.stat().st_size<1024*1024,p
        relative=p.relative_to(REPO).as_posix();current=p.read_bytes();upstream=blob(parent,relative)
        if upstream==current:continue
        assert upstream==blob(BASE,relative),'Concurrent remote change: '+relative
        changes.append((relative,current))
    assert changes
    with tempfile.TemporaryDirectory(prefix='pnt02-shorts-index-') as folder:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(folder)/'index'))
        git('read-tree',parent,env=env)
        for path,data in changes:
            oid=git('hash-object','-w','--stdin',data=data).decode().strip()
            git('update-index','--add','--cacheinfo',f'100644,{oid},{path}',env=env)
        tree=git('write-tree',env=env).decode().strip()
        message='絵画02ショート3本を修正範囲で完成・非公開共有（22.367／20.067／18.400秒、重なり0px²、デコード警告0）\n\n承認済み音声3本を再利用。V3は上寄せ1.04倍・字幕70px下移動。Draft Release 439916775 の5資産をRESTダウンロードSHA-256一致で照合。指定SSD ESD-02へ保存。共有対象のみをリモート最新に積み、ローカルHEAD/indexは維持。投稿・予約なし。\n'
        commit=git('commit-tree',tree,'-p',parent,data=message.encode()).decode().strip()
        actual=set(git('diff-tree','--no-commit-id','--name-only','-z','-r',commit).decode().strip('\0').split('\0'))
        assert actual=={p for p,_ in changes}
        git('push','origin',f'{commit}:refs/heads/{BRANCH}')
        assert git('ls-remote','origin',f'refs/heads/{BRANCH}').decode().split()[0]==commit
    assert git('rev-parse','HEAD')==head and hashlib.sha256(index.read_bytes()).hexdigest()==indexhash
    print('PUSHED',commit,'parent',parent,'files',len(changes),'HEAD/index preserved')

if __name__=='__main__':main()
