"""Check subtitle text and the chronology region in actual final review videos."""
import os
import re
import subprocess
import numpy as np
from PIL import Image
from pnt02_produce import ROOT, REPO, read, save, sha


def main():
    lang=os.environ['PNT02_LANG']
    base=ROOT/f'deliverables/PNT02_WashingtonCrossing_{lang}_v01_1080p30.mp4'
    review=base.with_name(base.stem.replace('_1080p30','_subtitled_review_1080p30')+'.mp4')
    srt=base.with_suffix('.srt').read_text()
    blocks=srt.strip().split('\n\n')
    text=''.join(''.join(b.splitlines()[2:]) for b in blocks)
    content=read(ROOT/'records'/('content_en.json' if lang=='en' else 'content.json'))
    clean=lambda t:re.sub(r'\s+','',t)
    assert clean(text)==clean(''.join(s['text'] for s in content['segments']))
    assert all(len(b.splitlines()[2:])<=2 and all(len(t)<=(42 if lang=='en' else 23) for t in b.splitlines()[2:]) for b in blocks)
    def seconds(t):
        h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
    times=[tuple(seconds(x.strip()) for x in b.splitlines()[1].split('-->')) for b in blocks]
    assert min(b-a for a,b in times)>=1.3999
    frames=[round((a+b)/2*30) for a,b in times]
    def expression(values):
        if len(values)==1:return f'eq(n\\,{values[0]})'
        m=len(values)//2;return '('+expression(values[:m])+'+'+expression(values[m:])+')'
    folder=ROOT/'_work/final_subtitle_pages';folder.mkdir(exist_ok=True)
    for label,src in [('plain',base),('subtitled',review)]:
        subprocess.run(['ffmpeg','-nostdin','-y','-v','warning','-xerror','-threads','1','-i',str(src),
            '-an','-filter_threads','1','-vf','select='+expression(frames),'-fps_mode','passthrough',
            '-threads','1',str(folder/(label+'_%03d.png'))],check=True)
    rows=[]
    bounds=read(REPO/f'painting/pnt02_確認版_v01_20261110/{lang}/subtitle_layout_validation.json')
    for i,frame in enumerate(frames,1):
        a=Image.open(folder/f'plain_{i:03}.png').convert('RGB')
        b=Image.open(folder/f'subtitled_{i:03}.png').convert('RGB')
        delta=np.abs(np.asarray(a).astype(float)-np.asarray(b).astype(float))
        rail=delta[915:];mae=float(rail.mean());p99=float(np.percentile(rail,99))
        # A subtitle must actually be present in its expected backing/text area.
        x,y,right,bottom=bounds['rows'][i-1]['bbox']
        changed=int((delta[y:bottom,x:right].max(axis=2)>40).sum())
        rows.append(dict(cue=i,frame=frame,rail_mae=mae,rail_p99=p99,changed_subtitle_pixels=changed,
                         passed=mae<3 and p99<20 and changed>100))
        if i in [1,10,20,30,40,50,60,len(frames)]:
            b.resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/f'review/subtitle_final_{lang}_{i:03}.jpg',quality=91,optimize=True)
    save(ROOT/'records/final_subtitle_qc.json',dict(passed=all(r['passed'] for r in rows),
        script_exact_ignoring_whitespace=True,srt_pages=len(blocks),min_srt_seconds=min(b-a for a,b in times),
        max_lines=max(len(b.splitlines()[2:]) for b in blocks),max_line=max(len(t) for b in blocks for t in b.splitlines()[2:]),
        min_clearance_px=bounds['min_gap'],review_sha256=sha(review),
        method='All subtitle midpoint frames from continuous final delivery/review decode. Check unchanged rail, present subtitle pixels, and exact SRT text. Exact subtitle bounds from same libass/style diagnostic.',checks=rows))
    print('FINAL SUBTITLES',lang,len(rows),all(r['passed'] for r in rows),flush=True)


if __name__=='__main__':
    main()
