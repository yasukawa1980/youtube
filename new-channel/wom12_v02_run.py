"""Build both language masters and quality records from the v02 timelines."""
import concurrent.futures
import os
import threading
import shutil
import subprocess
import sys
from pathlib import Path

from wom12_retime import BASE, NEW

SCRIPTS = Path(__file__).parent

audio_lock = threading.Lock()

def stage(script, env, *args):
    name = '_'.join([script,*args])
    log = Path(env['WOM12_ROOT'])/'_work'/(name+'.log')
    marker=log.with_suffix('.complete')
    if marker.exists():return
    print('START',env.get('WOM12_LANG'),name,flush=True)
    import contextlib
    lock=audio_lock if script=='wom12_music' else contextlib.nullcontext()
    with lock, log.open('w') as stream:
        subprocess.run([sys.executable, str(SCRIPTS/(script+'.py')), *args],env=env,stdout=stream,stderr=subprocess.STDOUT,check=True)
    marker.touch()
    print('DONE',env.get('WOM12_LANG'),name,flush=True)

def produce(lang):
    root = NEW/lang
    env=dict(os.environ,WOM12_VERSION='v02',WOM12_ROOT=str(root),WOM12_MEDIA=str(BASE/'素材'),WOM12_LANG=lang)
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        work=[pool.submit(stage,s,env) for s in ['wom12_picture','wom12_music']]
        for f in work:f.result()
    stage('wom12_render',env,'package')
    dst=NEW/'deliverables'
    dst.mkdir(exist_ok=True)
    if lang=='en':
        shutil.copy2(root/'deliverables/EP012_SantaClaus_en_v02_1080p30.mp4',dst)
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        u=None
        if lang=='en':
            (NEW/'_work').mkdir(exist_ok=True)
            u=pool.submit(stage,'wom12_4k',env,'v02','en')
        stage('wom12_render',env,'reviews')
        stage('wom12_render',env,'precision')
        stage('wom12_render',env,'verify')
        stage('wom12_continuous_qc',env)
        stage('wom12_subcheck',env)
        stage('wom12_motion',env)
        if u:u.result()
    for f in (root/'deliverables').iterdir():shutil.copy2(f,dst)
if __name__=='__main__':
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        tasks=[pool.submit(produce,lang) for lang in ['en','ja']]
        for task in tasks:task.result()
