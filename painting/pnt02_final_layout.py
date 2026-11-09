"""Check decoded delivery images against the exact approved cards and overlays."""
import os
import numpy as np
from PIL import Image, ImageColor
from pnt02_produce import ROOT, REPO, read, save, sha
import pnt02_scenes as scene


def main():
    lang = os.environ['PNT02_LANG']
    scale = scene.S
    suffix = '_4k' if scale == 2 else ''
    shots = read(ROOT / f'records/render_shots{suffix}.json')
    qc = read(ROOT / f'records/continuous_qc{suffix}.json')
    indexes = {f: i+1 for i, f in enumerate(qc['selected_frames'])}
    checks = []
    for shot in shots:
        key = shot['key']
        for stage in shot['stages']:
            f = stage['start_frame'] + (stage['frames']-1)//2
            actual = Image.open(ROOT / f'_work/continuous{suffix}/{indexes[f]:03d}.png').convert('RGB')
            is_art = key in scene.FILES
            expected = scene.art_overlay(key, stage['year']) if is_art else scene.scene(key, stage['stage'], stage['year'])
            expected = expected.convert('RGB').resize((1280,720), Image.Resampling.LANCZOS)
            areas = [('header',(0,0,1280,68))] if is_art else [('card',(0,0,1280,720))]
            if is_art and stage['year'] is not None:
                areas.append(('chronology',(0,612,1280,720)))
            for area, box in areas:
                delta = np.abs(np.asarray(actual.crop(box)).astype(float)-np.asarray(expected.crop(box)).astype(float))
                mae, p99 = float(delta.mean()), float(np.percentile(delta,99))
                checks.append(dict(shot=key,frame=f,stage=stage['stage'],year=stage['year'],area=area,mae=mae,p99=p99,passed=mae<5 and p99<35))
    usage = {s['key']: sum(t['key']==s['key'] for t in shots) for s in shots}
    assert all(n==1 for n in usage.values()) and len(shots)==18
    assert {k for k in usage if k.startswith('V')} == set(scene.FILES)
    scales = read(ROOT / f'records/art_scales{suffix}.json')
    assert all(a['max_native_scale']<=1 for a in scales.values())
    assert all(e['year']=='—' for s in shots if s['segment_id'] in ['P07','P10'] for e in s['stages'])
    request = (REPO / 'painting/pnt02_制作依頼_20261110.md').read_text()
    for phrase in [scene.LETTER_HEAD]+[p for pair in scene.LETTER for p in pair]+scene.RESOLUTION+scene.WHITTREDGE:
        assert phrase in request, phrase
    rows = read(ROOT / f'records/frame_layout{suffix}.json')
    def luminance(color):
        a=np.array(ImageColor.getrgb(color))/255
        a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
        return float(a@np.array([.2126,.7152,.0722]))
    ratios=[]
    for row in rows:
        if not row['card'].startswith('D_') or row['card']=='D_timeline_intro':
            continue
        bg=scene.BAR if row['box'][1]>=915 else row['background']
        a,b=luminance(row['foreground']),luminance(bg)
        ratios.append((max(a,b)+.05)/(min(a,b)+.05))
        if row['major']:
            assert row['ink_height']>=60
    assert min(ratios)>=4.5
    padding=min(r['plate_padding'] for r in rows if 'plate_padding' in r)
    save(ROOT / f'records/final_layout{suffix}.json',dict(
        passed=all(c['passed'] for c in checks), video_sha256=qc['video_sha256'],
        method='Every card/chronology stage midpoint from uninterrupted final-video decode compared with exact source raster. Header/rail only for moving artwork.',
        usage=usage, quotation_text_exact=True, major_ink_min=60,
        contrast_min=min(ratios), plate_padding_min=padding,
        native_scale_max=max(a['max_native_scale'] for a in scales.values()),
        p07_p10_no_emphasis=True, checks=checks))
    print('LAYOUT',lang,scale,len(checks),'passed',all(c['passed'] for c in checks),flush=True)


if __name__=='__main__':
    main()
