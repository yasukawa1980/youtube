"""Exhaustive pairwise overlap of actual moving crops, not just crop envelopes.
Run with PYTHONPATH=_work/pnt02-deps and _work/qo-production-python/bin/python.
"""
import itertools
import cv2
import numpy as np
from pnt02_produce import ROOT, REPO, read, save
from pnt02_shots import plan
from pnt02_picture import motion


def main():
    registration=read(REPO/'painting/pnt02_確認版_v01_20261110/detail_registration.json')
    transforms={r['id']:np.asarray(r['homography']) for r in registration['registration']}
    checks=[]
    for lang in ['en','ja']:
        polygons={}
        for shot in plan(lang)['shots']:
            key=shot['key']
            if key not in ['V01_D1','V01_D2','V01_D3']:
                continue
            config=motion(key,shot['frames'],2)
            left,top,right,bottom=config['source_crop'];w,h=right-left,bottom-top
            rows=[]
            for f in range(shot['frames']):
                u=f/max(1,shot['frames']-1)
                z=1.04 if key in ['V01_D1','V01_D3'] else 1+.04*u
                ax=.25+.75*u if key=='V01_D3' else .5
                ay=u if key=='V01_D1' else .5
                x,y=left+(w-w/z)*ax,top+(h-h/z)*ay
                rectangle=np.array([[x,y],[x+w/z,y],[x+w/z,y+h/z],[x,y+h/z]],np.float32)
                polygon=cv2.perspectiveTransform(rectangle[None,:,:],transforms[key[-2:]])[0]
                rows.append((polygon,abs(cv2.contourArea(polygon))))
            polygons[key]=rows
        for a,b in itertools.combinations(polygons,2):
            maximum=0;frames=None
            for i,(p,area_p) in enumerate(polygons[a]):
                for j,(q,area_q) in enumerate(polygons[b]):
                    intersection,_=cv2.intersectConvexConvex(p,q)
                    ratio=intersection/min(area_p,area_q)
                    if ratio>maximum:
                        maximum=ratio;frames=[i,j]
            checks.append(dict(language=lang,a=a,b=b,frame_pairs=len(polygons[a])*len(polygons[b]),
                               maximum_overlap=maximum,maximum_at_local_frames=frames,passed=maximum<=.25))
            print('GEOMETRY',lang,a,b,maximum,flush=True)
    save(ROOT/'records/final_moving_overlap.json',dict(passed=all(r['passed'] for r in checks),
         method='All pairs of actual per-frame crop quadrilaterals transformed into the full painting using the recorded SIFT homographies. Overlap divided by the smaller actual crop area.',
         registration_source='detail_registration.json',checks=checks))


if __name__=='__main__':
    main()
