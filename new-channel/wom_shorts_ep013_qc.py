"""第13話ショート。完成動画を順次デコードし、低メモリで検品する。"""
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from wom_shorts_ep013 import ROOT, MAIN, REQUEST, guard, read, save, sha, helper

def lum(a):
    a=a.astype(np.float32)/255
    a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
    return a@np.array([.2126,.7152,.0722],np.float32)

def contrast(frame,layer):
    with Image.open(layer) as im:
        im=im.convert('RGBA');box=im.getbbox();a=np.array(im.crop(box))
    rgb=frame[box[1]:box[3],box[0]:box[2]]
    core=(a[:,:,3]>=253)&(np.max(abs(a[:,:,:3].astype(int)-[244,239,223]),axis=2)<3)
    core=np.asarray(Image.fromarray(core.astype('uint8')*255).filter(ImageFilter.MinFilter(3)))>0
    ink=a[:,:,3]>174
    ring=(np.asarray(Image.fromarray(ink.astype('uint8')*255).filter(ImageFilter.MaxFilter(19)))>0)&~(np.asarray(Image.fromarray(ink.astype('uint8')*255).filter(ImageFilter.MaxFilter(7)))>0)&(a[:,:,3]==173)
    assert core.sum()>40 and ring.sum()>40
    L=lum(rgb);ratio=(float(L[core].min())+.05)/(float(L[ring].max())+.05)
    assert ratio>=4.5,ratio
    return dict(contrast_ratio=ratio,core_pixels=int(core.sum()),background_pixels=int(ring.sum()))

def card_contrast(frame,g):
    source=read(ROOT/'records/card_texts.json')[g['asset_id']]
    out=[]
    with Image.open(g['file']) as im:
        for row in source['texts']:
            x,y,r,b=row['bbox'];box=(max(0,x-5),max(0,y-5),min(1080,r+5),min(1920,b+5))
            a=np.array(im.crop(box).convert('RGB')).astype(int)
            core=np.max(abs(a-[59,44,33]),axis=2)<3
            bg=np.max(abs(a-[232,217,183]),axis=2)<3
            # 細い札を消さない。元画像の指定文字色に一致する画素を収縮せず使い、
            # 完成MP4の同じ座標の最悪値（最も明るい文字／暗い背景）を測る。
            bg=np.asarray(Image.fromarray(bg.astype('uint8')*255).filter(ImageFilter.MinFilter(3)))>0
            assert core.sum()>0 and bg.sum()>0,row
            L=lum(frame[box[1]:box[3],box[0]:box[2]])
            ratio=(float(L[bg].min())+.05)/(float(L[core].max())+.05)
            assert ratio>=4.5,(row['text'],ratio)
            out.append(dict(text=row['text'],contrast_ratio=ratio,core_pixels=int(core.sum()),
                            background_pixels=int(bg.sum()),method='指定文字色の画素を収縮なしで抽出し、完成MP4の最悪値を測定。背景のみ3x3収縮。'))
    return out

def sheet(sid,kind,indices,cols):
    cols=min(cols,len(indices));canvas=Image.new('RGB',(cols*240,math.ceil(len(indices)/cols)*450),'#0c1820')
    d=ImageDraw.Draw(canvas)
    for i,n in enumerate(indices):
        with Image.open(ROOT/f'review/{sid}_frames/{n:04}.jpg') as im:
            im.thumbnail((240,427));x=i%cols*240;y=i//cols*450;canvas.paste(im,(x,y))
            d.text((x+5,y+430),f'{sid} {n/30:.3f}s',fill='white')
    canvas.thumbnail((1280,1280));canvas.save(ROOT/f'review/{sid}_{kind}.jpg',quality=91,optimize=True)

def stream_hash(path):
    return subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def audit(version='v01',expected_shots=8):
    old,_=helper()
    shorts=read(ROOT/'records/shorts.json')['shorts'];visual=read(ROOT/'records/visual_manifest.json')
    shots=visual['shots'];caps=read(ROOT/'records/caption_manifest.json');results=[];motions=[]
    assert len(shots)==expected_shots and all(x['overlap_px2']==0 for x in visual['overlaps'])
    assert all(g['native_max_scale']<=1 for g in shots)
    # 本編のカード文字と出典が、改行・組版の区切り以外は同じかを照合。
    maincode=(REQUEST.parent/'wom13_scenes.py').read_text()
    cards=read(ROOT/'records/card_texts.json')
    for key,card in cards.items():
        for text in card['main_texts']:
            assert text in maincode,(key,text)
    for s in shorts:
        guard();sid=s['id'];path=ROOT/f'deliverables/QO_short_EP013_{sid}_{version}.mp4'
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))
        v=next(x for x in probe['streams'] if x['codec_type']=='video')
        assert (v['codec_name'],v['profile'],v['pix_fmt'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==('h264','High','yuv420p',1080,1920,'30/1',s['frames'])
        assert s['frames']<=720 and s['frames']-s['cta_start_frame']==75
        cs=[c for c in caps if c['short_id']==sid];gs=[g for g in shots if g['short_id']==sid]
        assert ' '.join(c['text'] for c in cs)==s['text']
        assert not any(re.search(r'[.!?]["”]?\s',c['text']) for c in cs)
        assert all(len(c['lines'])<=2 for c in cs)
        for c in cs:
            for row in c['rows']:
                assert row['font_size']==55 and row['cap_height']==39 and not row['resampling']
                assert not re.search(r'\b(a|an|the|of|to|for|with|in|on|through|into|from|at)$',row['text'],re.I),row['text']
        assert s['voice_onset_seconds']<=.3
        indices=set([0,15,30,45,60,75,s['cta_start_frame'],s['frames']-1])
        indices.update(range(0,s['frames'],30));indices.update((c['start_frame']+c['end_frame'])//2 for c in cs)
        indices.update(g['start_frame'] for g in gs)
        folder=ROOT/f'review/{sid}_frames';folder.mkdir(exist_ok=True)
        checks=[];cardchecks=[];headline=None
        log=ROOT/f'records/{sid}_continuous_decode.log'
        # 1回の全編デコードで警告・画素差・確認画像・コントラストを測定。
        with log.open('wb') as err:
            proc=subprocess.Popen(['ffmpeg','-nostdin','-v','warning','-threads','2','-i',str(path),'-threads','2','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=err)
            try:
                for g in gs:
                    x,y,w,h=g['viewport'];dw,dh=g['display_size'];x+=(w-dw)//2;y+=(h-dh)//2
                    box=[max(20,x+10),max(300,y+10),min(1060,x+dw-10),min(820,y+dh-10)]
                    x0,y0,x1,y1=box;assert x1>x0 and y1>y0
                    mask=np.ones((y1-y0,x1-x0),bool)
                    if g['start_frame']==0:
                        with Image.open(ROOT/f'assets/{sid}_headline.png') as im:mask&=np.array(im)[:,:,3][y0:y1,x0:x1]==0
                    assert mask.sum()>1000
                    previous=None;diffs=[]
                    for n in range(g['start_frame'],g['end_frame']):
                        if n%150==0:guard();print('DECODE',sid,n,flush=True)
                        data=proc.stdout.read(1080*1920*3);assert len(data)==1080*1920*3,(sid,n)
                        arr=np.frombuffer(data,np.uint8).reshape(1920,1080,3)
                        roi=arr[y0:y1,x0:x1].mean(axis=2).astype(np.float32)
                        if previous is not None:diffs.append(float(np.abs(roi-previous)[mask].mean()))
                        previous=roi
                        if n in indices:
                            im=Image.fromarray(arr);im.thumbnail((720,1280));im.save(folder/f'{n:04}.jpg',quality=90,optimize=True)
                        if n==0:headline=contrast(arr,ROOT/f'assets/{sid}_headline.png')
                        for c in cs:
                            if n==(c['start_frame']+c['end_frame'])//2:
                                checks.append(dict(page=c['page'],text=c['text'],frame=n,**contrast(arr,c['file'])))
                        if g['static'] and n==g['start_frame']:
                            cardchecks.append(dict(asset=g['asset_id'],checks=card_contrast(arr,g)))
                    median=float(np.median(diffs));p95=float(np.percentile(diffs,95));ratio=p95/median if median else None
                    passed=p95<.1 if g['static'] else ratio is not None and ratio<=2.5 and median>0
                    motions.append(dict(id=sid,asset=g['asset_id'],roi_xyxy=box,frame_pairs=len(diffs),median=median,p95=p95,p95_over_median=ratio,
                                        static=g['static'],passed=passed,frame_differences=diffs))
                assert not proc.stdout.read(1) and proc.wait()==0
            except BaseException:
                proc.kill();proc.wait();raise
        assert log.read_text()=='',log.read_text()
        aud=old.levels(path);assert abs(float(aud['input_i'])+14)<=.15 and float(aud['input_tp'])<=-1
        assert stream_hash(path)==stream_hash(ROOT/f'audio/{sid}_final.m4a')
        for kind,inds,cols in [('opening',[0,15,30,45,60,75],3),('every2s',list(range(0,s['frames'],60)),5),
              ('every1s_a',list(range(0,min(330,s['frames']),30)),4),('every1s_b',list(range(330,s['frames'],30)),4),
              ('all_captions',[(c['start_frame']+c['end_frame'])//2 for c in cs],4),
              ('CTA',[s['cta_start_frame'],s['frames']-1],2),('cuts',[g['start_frame'] for g in gs],3)]:sheet(sid,kind,inds,cols)
        results.append(dict(id=sid,path=str(path),sha256=sha(path),bytes=path.stat().st_size,
                  video_duration=s['frames']/30,container_duration=float(probe['format']['duration']),
                  video_format={k:v[k] for k in ['codec_name','profile','pix_fmt','width','height','r_frame_rate','nb_frames']},
                  continuous_decode_warning_count=0,audio=aud,voice_onset=s['voice_onset_seconds'],cta_duration=2.5,
                  subtitle_contrast=checks,minimum_contrast=min(c['contrast_ratio'] for c in checks),headline_contrast=headline,
                  card_contrast=cardchecks,caption_text_exact=True,cross_sentence_caption_count=0,caption_font_size=55,
                  maximum_native_scale=max(g['native_max_scale'] for g in gs),human_full_listening=False,youtube_posted=False))
        save(ROOT/'records/final_qc.json',results)
        save(ROOT/'records/final_pixel_motion.json',dict(passed=all(m['passed'] for m in motions),checks=motions))
        assert all(m['passed'] for m in motions), 'STOP: 完成動画の動き検証不合格'
        print('QC PASS',sid,aud['input_i'],results[-1]['minimum_contrast'],flush=True)
    for path in (ROOT/'review').rglob('*.jpg'):
        with Image.open(path) as im:assert max(im.size)<=1280
        assert path.stat().st_size<1000000
    guard()

if __name__=='__main__':audit()
