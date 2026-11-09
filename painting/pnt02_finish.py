"""Sequential low-memory rendering and QC; no upload or publication."""
import os
import subprocess
import sys
from datetime import datetime, timezone
from pnt02_produce import ROOT, REPO, save


def main():
    assert ROOT == __import__('pathlib').Path('/Volumes/ESD-02/新チャンネル/PNT02_WashingtonCrossing/確認版_v01_20261110')
    assert __import__('pathlib').Path('/Volumes/ESD-02').is_mount()
    jobs=[]
    for lang, scale in [('en',1),('ja',1),('en',2)]:
        jobs.append((['pnt02_picture.py',lang,str(scale)],dict(PNT02_SCALE=str(scale))))
    for lang in ['en','ja']:
        env=dict(PNT02_ROOT=str(ROOT/lang),PNT02_LANG=lang,PNT02_SCALE='1')
        for stage in ['package']+(['package4k'] if lang=='en' else [])+['reviews','precision','verify']:
            jobs.append((['pnt02_render.py',stage],env))
        for scale in ([1,2] if lang=='en' else [1]):
            for script in ['pnt02_qc.py','pnt02_final_layout.py','pnt02_motion.py']:
                jobs.append(([script],dict(env,PNT02_SCALE=str(scale))))
        jobs.append((['pnt02_subtitle_final.py'],env))
    done=[]
    state=ROOT/'records/finish_progress.json'
    for args, overrides in jobs:
        env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',VECLIB_MAXIMUM_THREADS='1',**overrides)
        label=' '.join(args)+' '+str(overrides)
        save(state,dict(completed=done,current=label,utc=datetime.now(timezone.utc).isoformat()))
        print('START',label,flush=True)
        subprocess.run([sys.executable,str(REPO/'painting'/args[0]),*args[1:]],env=env,check=True)
        done.append(label)
        print('DONE',label,flush=True)
    save(state,dict(completed=done,current=None,finished=True,utc=datetime.now(timezone.utc).isoformat()))


if __name__=='__main__':
    main()
