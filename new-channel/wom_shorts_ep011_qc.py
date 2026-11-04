"""Full sequential decoding, final-pixel contrast and motion, all-page review sheets."""
import json
import math
import re
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image,ImageDraw,ImageFilter

from wom_shorts_ep011 import ROOT,MAIN,PAGE_LINES,sha,save
from wom_shorts_remake_produce import levels
from wom_shorts_remake_qc_v03 import contrast,lum


def card_contrast(frame,path):
    src=np.asarray(Image.open(path).convert('RGB'));ink=np.array([59,44,33]);sand=np.array([232,217,183])
    text=np.max(abs(src.astype(int)-ink),axis=2)<2
    bg=np.max(abs(src.astype(int)-sand),axis=2)<2
    text=np.asarray(Image.fromarray(text.astype('uint8')*255).filter(ImageFilter.MinFilter(3)))>0
    bg=np.asarray(Image.fromarray(bg.astype('uint8')*255).filter(ImageFilter.MinFilter(11)))>0
    text[:270]=False;text[1100:]=False;bg[:270]=False;bg[1100:]=False
    L=lum(frame);ratio=(float(L[bg].min())+.05)/(float(L[text].max())+.05)
    assert ratio>=4.5,ratio
    return dict(contrast_ratio=ratio,text_core_pixels=int(text.sum()),background_pixels=int(bg.sum()))


def sheet(sid,kind,indices,frames,cols=5):
    folder=ROOT/f'review/{sid}_{kind}';folder.mkdir(exist_ok=True)
    cols=min(cols,len(indices));canvas=Image.new('RGB',(cols*240,math.ceil(len(indices)/cols)*450),'#0c1820');d=ImageDraw.Draw(canvas)
    for i,n in enumerate(indices):
        im=Image.fromarray(frames[n]);im.thumbnail((720,1280));im.save(folder/f'{n:04}.jpg',quality=89,optimize=True)
        thumb=im.copy();thumb.thumbnail((240,427));x=i%cols*240;y=i//cols*450
        canvas.paste(thumb,(x,y));d.text((x+5,y+430),f'{sid} {n/30:.3f}s',fill='white')
    canvas.thumbnail((1280,1280));canvas.save(ROOT/f'review/{sid}_{kind}.jpg',quality=91,optimize=True)


def audit():
    shorts=json.loads((ROOT/'records/shorts.json').read_text())['shorts']
    shots=json.loads((ROOT/'records/visual_manifest.json').read_text())['shots']
    caps=json.loads((ROOT/'records/caption_manifest.json').read_text())
    assert len(shots)==len({g['asset_id'] for g in shots})==9
    assert all(g['native_max_scale']<=g['native_scale_limit']+1e-8 for g in shots)
    assert json.loads((ROOT/'records/visual_manifest.json').read_text())['imhotep_regions_disjoint']
    results=[];motion=[]
    for s in shorts:
        sid=s['id'];p=ROOT/f'deliverables/QO_short_EP011_{sid}_v01.mp4'
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
        v=next(x for x in probe['streams'] if x['codec_type']=='video')
        assert (v['codec_name'],v['profile'],v['pix_fmt'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==('h264','High','yuv420p',1080,1920,'30/1',s['frames'])
        assert s['frames']<=720
        cs=[c for c in caps if c['short_id']==sid];gs=[g for g in shots if g['short_id']==sid]
        assert ' '.join(c['text'] for c in cs)==s['text']
        assert not any(re.search(r'[.!?]["”]?\s',c['text']) for c in cs)
        assert all(len(c['lines'])<=2 and len(c['text'].split())>1 for c in cs)
        for c in cs:
            for r in c['rows']:
                assert r['cap_height']==39 and r['font_size']==55 and not r['resampling']
                assert r['text']=='the dead live on' or not re.search(r'\b(a|an|the|of|to|for|with|in|on|through|into|from|at)$',r['text'],re.I),r['text'] # 'on' is the adverb in 'live on'.
                b=r['plate_bbox'];assert b[0]>=80 and b[2]<=880 and b[1]>=1150 and b[3]<=1450
        assert s['voice_onset_seconds']<=.3
        assert s['cta_start']>=s['native_audio_duration'] and s['frames']-s['cta_start_frame']==75
        ns=set([0,15,30,45,60,75,s['cta_start_frame'],s['frames']-1])
        ns.update(range(0,s['frames'],60));ns.update((c['start_frame']+c['end_frame'])//2 for c in cs)
        ns.update(g['start_frame'] for g in gs)
        continuous=subprocess.run(['ffmpeg','-nostdin','-v','warning','-i',str(p),'-f','null','-'],capture_output=True,text=True)
        (ROOT/f'records/{sid}_continuous_decode.log').write_text(continuous.stderr)
        assert continuous.returncode==0 and continuous.stderr=='',continuous.stderr
        # RGB extraction is a separate analysis pass; native decode above supplies warning count.
        frames={};errfile=ROOT/f'records/{sid}_RGB_extraction.log'
        with errfile.open('wb') as err:
            proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(p),'-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=err)
            for g in gs:
                x,y,w,h=g['viewport'];x0=max(x+10,20);x1=min(x+w-10,1060);y0=max(y+10,300);y1=min(y+h-10,1010)
                mask=np.ones((y1-y0,x1-x0),bool)
                if g['start_frame']==0:
                    ha=np.asarray(Image.open(ROOT/f'assets/{sid}_headline.png').convert('RGBA'))[:,:,3]
                    mask&=ha[y0:y1,x0:x1]==0
                assert mask.sum()>1000
                last=None;ds=[]
                for n in range(g['start_frame'],g['end_frame']):
                    data=proc.stdout.read(1080*1920*3);assert len(data)==1080*1920*3,(sid,n,len(data))
                    arr=np.frombuffer(data,np.uint8).reshape(1920,1080,3)
                    if n in ns:frames[n]=arr.copy()
                    roi=arr[y0:y1,x0:x1].mean(axis=2).astype(np.float32)
                    if last is not None:ds.append(float(np.abs(roi-last)[mask].mean()))
                    last=roi
                med=float(np.median(ds));q95=float(np.percentile(ds,95));ratio=q95/med if med else None
                static=g['static'];ok=q95<.1 if static else ratio is not None and ratio<=2.5
                motion.append(dict(id=sid,asset=g['asset_id'],roi_xyxy=[x0,y0,x1,y1],frame_pairs=len(ds),median=med,p95=q95,p95_over_median=ratio,static=static,passed=ok,frame_differences=ds))
                print('MOTION',sid,g['asset_id'],ratio,ok,flush=True)
            assert not proc.stdout.read(1) and proc.wait()==0
        assert errfile.read_text()=='',errfile.read_text()
        cr=[dict(page=c['page'],text=c['text'],frame=(c['start_frame']+c['end_frame'])//2,**contrast(frames[(c['start_frame']+c['end_frame'])//2],c['file'])) for c in cs]
        cardchecks=[dict(asset=g['asset_id'],**card_contrast(frames[g['start_frame']],g['file'])) for g in gs if g['static']]
        headline=contrast(frames[0],ROOT/f'assets/{sid}_headline.png')
        aud=levels(p);assert abs(float(aud['input_i'])+14)<=.15 and float(aud['input_tp'])<=-1
        for kind,inds,cols in [('opening',[0,15,30,45,60,75],3),('every2s',list(range(0,s['frames'],60)),5),('all_captions',[(c['start_frame']+c['end_frame'])//2 for c in cs],4),('CTA',[s['cta_start_frame'],s['frames']-1],2),('cuts',[g['start_frame'] for g in gs],3)]:
            sheet(sid,kind,inds,frames,cols)
        # The final encoder copies the already measured AAC without re-encoding.
        def stream_hash(src):
            out=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(src),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'])
            return out.decode().strip()
        assert stream_hash(p)==stream_hash(ROOT/f'audio/{sid}_final.m4a')
        results.append(dict(id=sid,path=str(p),sha256=sha(p),bytes=p.stat().st_size,video_duration=s['frames']/30,container_duration=float(probe['format']['duration']),video_format={k:v[k] for k in ['codec_name','profile','pix_fmt','width','height','r_frame_rate','nb_frames']},continuous_decode_warning_count=0,audio=aud,voice_onset=s['voice_onset_seconds'],cta_start=s['cta_start'],cta_duration=2.5,native_voice_end=s['native_audio_duration'],caption_text_exact=True,cross_sentence_caption_count=0,caption_font_size=55,caption_cap_height=39,subtitle_contrast=cr,minimum_contrast=min(r['contrast_ratio'] for r in cr),headline_contrast=headline,card_contrast=cardchecks,cut_frames=[g['start_frame'] for g in gs],maximum_native_scale=max(g['native_max_scale'] for g in gs),first_frame_foreground_height=gs[0]['foreground_height_fraction'],human_full_listening=False,youtube_posted=False))
        print('QC',sid,'PASS',results[-1]['minimum_contrast'],aud['input_i'],aud['input_tp'],flush=True)
    save(ROOT/'records/final_qc.json',results)
    save(ROOT/'records/final_pixel_motion.json',dict(passed=all(m['passed'] for m in motion),method='Every adjacent completed-video RGB frame, arithmetic mean channel luminance; fixed foreground ROI above captions and CTA; first-shot headline pixels masked; no seeking or discarded zero pairs. Static card requires p95 absolute mean difference <0.1.',checks=motion))
    assert all(m['passed'] for m in motion),'Review motion diagnostics before delivery'
    print('ALL THREE PASS',flush=True)


if __name__=='__main__':audit()
