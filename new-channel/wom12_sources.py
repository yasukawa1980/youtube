from pathlib import Path
from collections import Counter
from wom12_produce import *
from wom12_scenes import CAT,LINE2,LINE3

def main():
 c=read(ROOT/'records/source_assets.json');ya=read(ROOT/'records/yale_n08.json');actual=read(ROOT/'records/render_shots.json');rows=[]
 for k in CAT:
  if k.startswith('N08_'):
   a=next(x for x in ya['files'] if x['id']==k);path=Path(a['path']);digest=a['sha256'];page='https://collections.library.yale.edu/catalog/2014510';rights=ya['policy'];name="The Children’s Friend, 1821 — "+k.split('_')[1]
  else:
   a=next(x for x in c['assets'] if x['id'].split('_')[0]==k);path=Path(a['local_path']);digest=a['sha256'];page=a['work_url'];rights=a['rights_label'];name=a['title']
  assert path.parent==MEDIA and sha(path)==digest and '原典照合用' not in str(path)
  full=sum(x['key']==k for x in actual)+(1 if k=='N12-B' and any(x['key']=='D_1823' for x in actual) else 0);assert full==1
  rows.append(dict(key=k,title=name,source=str(path),sha256=digest,rights=rights,work_url=page,fullscreen=full,comparison_2=sum(x==k for _,x in LINE2),comparison_3=sum(x==k for _,x in LINE3)))
 save(ROOT/'records/used_sources.json',dict(verified=True,checked_files=len(rows),rows=rows));print('Verified source files',len(rows))
if __name__=='__main__':main()
