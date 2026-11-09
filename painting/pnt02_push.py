"""Share only pnt02 deliverable records atop current origin, preserving local HEAD/index."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

REPO=Path(__file__).resolve().parent.parent
BRANCH='bgm/production'
BASE='123845503f696780213f7f586fcd22c2e661a8f8'


def git(*args, env=None, data=None):
    return subprocess.check_output(['git',*args],cwd=REPO,env=env,input=data)


def blob(revision,path):
    proc=subprocess.run(['git','show',f'{revision}:{path}'],cwd=REPO,capture_output=True)
    if proc.returncode:
        assert not git('ls-tree',revision,'--',path).strip(),path
        return None
    return proc.stdout


def main():
    assert len(sys.argv)==2,'Pass a Japanese commit message with measured results'
    index=REPO/'.git/index'
    index_hash=hashlib.sha256(index.read_bytes()).hexdigest()
    head=git('rev-parse','HEAD').strip()
    git('fetch','origin',BRANCH)
    parent=git('rev-parse',f'origin/{BRANCH}').decode().strip()
    paths=set((REPO/'painting').glob('pnt02_*.py'))
    paths.update((REPO/'painting/pnt02_確認版_v01_20261110').rglob('*'))
    paths.update((REPO/'painting/サムネ確認用/pnt02').glob('*.jpg'))
    for name in ['pnt02_制作結果_v01_20261110.md','pnt02_制作再開結果_20261110.md']:
        paths.add(REPO/'painting'/name)
    changes=[]
    for path in sorted(paths):
        if not path.is_file() or '__pycache__' in path.parts:
            continue
        assert path.suffix in ['.py','.md','.json','.srt','.jpg'],path
        assert path.stat().st_size<1024*1024,path
        relative=path.relative_to(REPO).as_posix()
        current=path.read_bytes()
        upstream=blob(parent,relative)
        if upstream==current:
            continue
        initial=blob(BASE,relative)
        # Remote edits since the approved base must not be overwritten silently.
        if upstream!=initial:
            raise RuntimeError('Review concurrent remote change: '+relative)
        changes.append((relative,current))
    assert changes,'No changes to share'
    with tempfile.TemporaryDirectory(prefix='pnt02-index-') as folder:
        env=dict(os.environ,GIT_INDEX_FILE=str(Path(folder)/'index'))
        git('read-tree',parent,env=env)
        for path,data in changes:
            oid=git('hash-object','-w','--stdin',data=data).decode().strip()
            git('update-index','--add','--cacheinfo',f'100644,{oid},{path}',env=env)
        tree=git('write-tree',env=env).decode().strip()
        commit=git('commit-tree',tree,'-p',parent,data=(sys.argv[1]+'\n').encode()).decode().strip()
        # -z avoids quoted Unicode paths in the exact allowlist verification.
        actual=set(git('diff-tree','--no-commit-id','--name-only','-z','-r',commit).decode().strip('\0').split('\0'))
        assert actual=={p for p,_ in changes}
        git('push','origin',f'{commit}:refs/heads/{BRANCH}')
        remote=git('ls-remote','origin',f'refs/heads/{BRANCH}').decode().split()[0]
        assert remote==commit
    assert git('rev-parse','HEAD').strip()==head
    assert hashlib.sha256(index.read_bytes()).hexdigest()==index_hash
    print('PUSHED',commit,'parent',parent,'files',len(changes),'HEAD/index preserved')


if __name__=='__main__':
    main()
