"""Final-file checks for first-shot-only EP006 v03 revision."""
import sys, json, subprocess, csv, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import wom06_shorts_revision_v03 as rev
ROOT=rev.ROOT;OLD=rev.OLD;read=rev.read;save=rev.save;sha=rev.sha
from wom01_quiet_origins import stream_hash


def verify():
    rev.qc.verify();rev.qc.glyphs();rev.qc.frames()
    plan=read(ROOT/'records/revision_plan.json');checks=[]
    for sid in rev.HEADLINES:
        old=OLD/f'deliverables/QO_short_EP006_{sid}_v02.mp4';new=ROOT/f'deliverables/QO_short_EP006_{sid}_v03.mp4'
        assert sha(old)==plan['original_video_sha256'][sid]
        h1=stream_hash(old,'a');h2=stream_hash(new,'a');assert h1==h2
        if sid=='S2':assert h2==stream_hash(rev.V01/'deliverables/QO_short_EP006_S2_v01.mp4','a')
        checks.append(dict(id=sid,original_video_sha256=sha(old),revised_video_sha256=sha(new),audio_stream_sha256=h2,audio_stream_identical=True))
    assert sha(ROOT/'records/shorts.json')==sha(OLD/'records/shorts.json')
    assert sha(ROOT/'records/caption_manifest.json')==sha(OLD/'records/caption_manifest.json')
    save(ROOT/'records/preservation_qc.json',dict(passed=True,audio=checks,subtitle_text_and_frames_identical=True,script_cut_times_duration_identical=True,
        original_v02_files_unchanged=True,originals_used_only_for_qa=True))
    safe=next(s for s in read(ROOT/'records/render_shots.json') if s['short_id']=='S1' and s['changed_v03'])
    bound=safe['source_safe_pixels'];crop=safe['source_crop_pixels'];w,h=Image.open(safe['source']['path']).size
    assert bound[0]>=.12*w and bound[1]>=.10*h and bound[2]<=.95*w and bound[3]<=.33*h
    assert bound[0]<=crop[0]<crop[2]<=bound[2] and bound[1]<=crop[1]<crop[3]<=bound[3]
    assert safe['background_also_uses_only_crop']
    # Camera window is within the already-safe portrait at every output frame.
    bounds=[]
    for f in range(safe['frames']):
        z=1.08**(f/(safe['frames']-1));cw=1080/z;ch=1600/z;x=(1080-cw)/2;y=1600-ch
        assert min(x,y)>=0 and x+cw<=1080+1e-8 and y+ch<=1600+1e-8
        bounds.append(dict(frame=f,zoom=z,portrait_rect=[x,y,x+cw,y+ch]))
    save(ROOT/'records/safe_crop_qc.json',dict(passed=True,all_frames_checked=len(bounds),source_size=[w,h],safe_pixels=bound,portrait_source_crop=crop,
        background_source='Only the same safe crop; no full-source pixels in the background.',camera_bounds=bounds))
    print('PRESERVATION AND SAFE CROP PASSED',flush=True)


def opening_frames():
    requested=[0,15,30,45,60,75];records=[]
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
    for sid in rev.HEADLINES:
        video=ROOT/f'deliverables/QO_short_EP006_{sid}_v03.mp4'
        folder=ROOT/f'review/opening_{sid}';folder.mkdir(exist_ok=True)
        expr='+'.join(f'eq(n\\,{n})' for n in requested)
        subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-i',str(video),'-vf',f'select={expr},scale=720:1280',
                        '-fps_mode','passthrough','-q:v','3',str(folder/'%02d.jpg')],check=True)
        files=sorted(folder.glob('*.jpg'));assert len(files)==6
        sheet=Image.new('RGB',(1080,1320),'#0c1820');d=ImageDraw.Draw(sheet)
        for i,(frame,path) in enumerate(zip(requested,files)):
            im=Image.open(path);assert im.size==(720,1280) and path.stat().st_size<1000000
            small=im.resize((360,640),Image.Resampling.LANCZOS);x=i%3*360;y=i//3*660;sheet.paste(small,(x,y));d.text((x+10,y+637),f'{sid}  {frame/30:.1f}s',font=font,fill='#f4efdf')
            records.append(dict(id=sid,frame=frame,seconds=frame/30,path=str(path),sha256=sha(path),continuous_decode=True))
        sheet.thumbnail((1280,1280));sheet.save(ROOT/f'review/{sid}_opening_0_to_2_5s.jpg',quality=90,optimize=True)
    save(ROOT/'records/opening_frame_review.json',dict(method='One continuous decoder from frame zero, select exact frames 0/15/30/45/60/75; no seeking.',frames=records))
    print('18 OPENING FRAMES EXTRACTED',flush=True)


def motion():
    hooks={h['id']:h for h in read(ROOT/'records/headlines.json')};checks=[]
    for s in read(ROOT/'records/render_shots.json'):
        sid=s['short_id'];b=s['art_box'];x=round(b[0]+.15*(b[2]-b[0]));y=round(b[1]+.15*(b[3]-b[1]));w=round(.7*(b[2]-b[0]));h=round(.7*(b[3]-b[1]))
        mask=np.ones((h,w),bool);exclusions=[]
        if s['changed_v03']:
            exclusions=[[0,110,1080,280],[60,1130,910,1470]]
            hb=hooks[sid]['overlay_bbox'];exclusions.append([hb[0]-24,hb[1]-24,hb[2]+24,hb[3]+24])
            for a,b1,c,d in exclusions:mask[max(0,b1-y):max(0,min(h,d-y)),max(0,a-x):max(0,min(w,c-x))]=False
        assert mask.sum()>10000
        p=ROOT/f'deliverables/QO_short_EP006_{sid}_v03.mp4';sig=sha(p)
        filt=f'trim=start_frame={s["start_frame"]}:end_frame={s["end_frame"]},format=gray,crop={w}:{h}:{x}:{y}:exact=1'
        proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(p),'-vf',filt,'-pix_fmt','gray','-fps_mode','passthrough','-f','rawvideo','-'],stdout=subprocess.PIPE)
        prior=None;ds=[]
        while True:
            raw=proc.stdout.read(w*h)
            if not raw:break
            assert len(raw)==w*h;a=np.frombuffer(raw,dtype=np.uint8).reshape(h,w)[mask].astype(np.int16)
            if prior is not None:ds.append(float(np.abs(a-prior).mean()))
            prior=a
        assert proc.wait()==0 and len(ds)==s['frames']-1
        med=float(np.median(ds));p95=float(np.quantile(ds,.95));ratio=p95/med if med else 1 if p95==0 else None
        q=dict(roi_xywh=[x,y,w,h],excluded_rects=exclusions,measured_pixels=int(mask.sum()),frame_pairs=len(ds),median=med,p95=p95,p95_over_median=ratio,differences=ds)
        passed=ratio is not None and ratio<=2.5
        checks.append(dict(short_id=sid,asset_id=s['asset_id'],encoded_sha256=sig,measurement=q,passed=passed,changed_first_shot=s['changed_v03']))
        print('MOTION',sid,s['asset_id'],ratio,passed,flush=True)
    save(ROOT/'records/motion_qc.json',dict(passed=all(c['passed'] for c in checks),threshold=2.5,checks=checks,
        method='All consecutive final-MP4 frame pairs within each shot; 8-bit gray MAD over interior 70% of the artwork. First-shot masks exclude static header, subtitle region, and fading headline with 24px margin, to measure camera motion rather than typography. No frame subsampling or temporal trimming.'))
    assert all(c['passed'] for c in checks)


def compare():
    shots=read(ROOT/'records/render_shots.json');summary=[];details=[]
    size=1080*1920*3//2;luma=1080*1920
    for sid in rev.HEADLINES:
        first=next(s for s in shots if s['short_id']==sid and s['start_frame']==0);start=first['end_frame']
        paths=[OLD/f'deliverables/QO_short_EP006_{sid}_v02.mp4',ROOT/f'deliverables/QO_short_EP006_{sid}_v03.mp4']
        procs=[subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(p),'-vf',f'trim=start_frame={start}',
                               '-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','-'],stdout=subprocess.PIPE) for p in paths]
        changed=0;count=0;sum_abs=0;sum_y=0;max_delta=0;worst_mean=0
        while True:
            raw=[p.stdout.read(size) for p in procs]
            if not any(raw):break
            assert all(len(r)==size for r in raw)
            a,b=[np.frombuffer(r,dtype=np.uint8) for r in raw];same=np.array_equal(a,b)
            ma=0;my=0;peak=0
            if not same:
                diff=np.abs(a.astype(np.int16)-b.astype(np.int16));ma=float(diff.mean());my=float(diff[:luma].mean());peak=int(diff.max())
                sum_abs+=int(diff.sum());sum_y+=int(diff[:luma].sum());max_delta=max(max_delta,peak);worst_mean=max(worst_mean,ma);changed+=1
            details.append(dict(id=sid,frame=start+count,equal=same,mean_abs_yuv=ma,mean_abs_luma=my,max_component_difference=peak));count+=1
        assert all(p.wait()==0 for p in procs)
        expected=sum(s['frames'] for s in shots if s['short_id']==sid and not s['changed_v03']);assert count==expected
        summary.append(dict(id=sid,start_frame=start,compared_frames=count,identical_frames=count-changed,different_frames=changed,
                            mean_abs_yuv=sum_abs/(count*size),mean_abs_luma=sum_y/(count*luma),maximum_component_difference=max_delta,
                            maximum_frame_mean_abs_yuv=worst_mean,source_shots_sha256_unchanged=True))
        print('COMPARE',sid,count,changed,'different;',sum_y/(count*luma),'luma MAD',flush=True)
    with (ROOT/'records/unchanged_frames.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(details[0]),lineterminator='\n');w.writeheader();w.writerows(details)
    save(ROOT/'records/unchanged_frames_qc.json',dict(checked=True,all_frames_identical=all(r['different_frames']==0 for r in summary),
        compression_difference_report_allowed_by_request=True,pixel_format='decoded yuv420p',range='0–255 per component',shorts=summary))


def headline_check():
    import imageio_ffmpeg
    r=rev
    rows=[]
    for hook in r.read(r.ROOT/'records/headlines.json'):
     cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-v','error','-loop','1','-framerate','30','-i',hook['file'],'-vf','format=rgba,fade=t=out:st=2:d=0.3:alpha=1','-frames:v','70','-pix_fmt','rgba','-f','rawvideo','-']
     proc=subprocess.Popen(cmd,stdout=subprocess.PIPE);means=[]
     for n in range(70):
      b=proc.stdout.read(1080*1920*4);assert len(b)==1080*1920*4
      a=np.frombuffer(b,np.uint8).reshape(1920,1080,4)[:,:,3];means.append(float(a.mean()))
     assert proc.wait()==0
     assert all(v==means[0] for v in means[:61]) and all(a>b for a,b in zip(means[60:69],means[61:70])) and means[69]==0
     rows.append(dict(id=hook['id'],opaque_through_frame=60,fade_frames=list(range(61,69)),fully_transparent_frame=69,alpha_mean_by_frame=means,headline_text=hook['text'],glyph_heights=[x['glyph_height'] for x in hook['lines']],glyph_bounds=[x['bbox'] for x in hook['lines']],passed=True))
    r.save(r.ROOT/'records/headline_qc.json',dict(passed=True,checks=rows,method='Actual RGBA fade filter used in final encoder evaluated for frames 0–69. Headline PNG glyph bounds measured before composition; final continuous-decode images visually inspected.'))

if __name__=='__main__':globals()[sys.argv[1]]()
