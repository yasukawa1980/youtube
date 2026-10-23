"""Pandora v02: replace A04 only; all other encoded shots/audio stay untouched."""
import argparse,copy,csv,hashlib,html,json,shutil,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageOps,ImageFilter,ImageEnhance,ImageDraw,ImageFont
from wom04_produce import read,save,sha,ff,probe,measure
from wom04_render import camera
from wom01_quiet_origins import stream_hash

V1=Path('/Users/ryo/Desktop/新チャンネル/EP004_Pandora/確認版_v01_20261023')
ROOT=V1.parent/'確認版_v02_20261023'
REPO=Path(__file__).resolve().parent.parent
REQUEST=REPO/'new-channel/wom04_Claude確認_v01_20261023.md'
CROP=[.77,.025,.968,.49]
FPS=30


def prepare():
    for d in ['records','assets','review','deliverables','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    sharing=read(V1/'records/sharing.json')
    assert sharing['release_id']==421509468 and sharing['status']=='verified'
    preserved={}
    for a in sharing['assets']:
        p=V1/'deliverables'/a['name'];assert sha(p)==a['sha256']
        preserved[a['name']]=a['sha256']
    save(ROOT/'records/v01_inputs.json',dict(source_release_id=421509468,files=preserved))
    oldmanifest=read(V1/'records/visual_manifest.json');manifest=copy.deepcopy(oldmanifest)
    source=next(a for a in read(V1/'records/source_assets.json')['assets'] if a['asset_id']=='A04')
    assert sha(source['local_path'])==source['sha256']
    original=ImageOps.exif_transpose(Image.open(source['local_path'])).convert('RGB')
    crop_px=[round(v*(original.width if i%2==0 else original.height)) for i,v in enumerate(CROP)]
    art=original.crop(crop_px)
    im=ImageEnhance.Brightness(ImageOps.fit(art,(1920,1080),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(55))).enhance(.35)
    fit=ImageOps.contain(art,(1760,820),Image.Resampling.LANCZOS)
    x=80+(1760-fit.width)//2;y=110+(820-fit.height)//2;im.paste(fit,(x,y))
    target=next(s for s in manifest['shots'] if s['key']=='A04')
    old=Image.open(V1/target['file']).convert('RGB')
    im.paste(old.crop((0,0,1920,110)),(0,0))
    path=ROOT/target['file'];path.parent.mkdir(exist_ok=True);im.save(path)
    for s in manifest['shots']:
        if s['key']=='A04':s.update(crop_normalized=CROP,art_boxes=[[x,y,x+fit.width,y+fit.height]],sha256=sha(path))
        else:s['file']=str(V1/s['file'])
    save(ROOT/'records/visual_manifest.json',manifest)
    save(ROOT/'records/revision.json',dict(request_sha256=sha(REQUEST),source_release_id=421509468,
        source_sha256=source['sha256'],source_path=source['local_path'],original_pixels=list(original.size),
        crop_normalized=CROP,crop_pixels=crop_px,art_box=[x,y,x+fit.width,y+fit.height],
        background_uses_same_safe_crop=True,header_pixels_copied_from_v01=True,
        modified_frame_start=1530,modified_frame_end_exclusive=1860,modified_seconds=[51,62],
        audio_synthesis_or_processing=False))
    for name in ['master_timeline.json','chapters.json','content.json','content_en.json','subtitle_validation.json','subtitle_layout_validation.json','audio_qc.json','wav_sample_validation.json']:
        shutil.copy2(V1/'records'/name,ROOT/'records'/name)
    for p in (V1/'deliverables').iterdir():
        if p.name in ['EP004_audio_ja.wav','EP004_thumbnail_A01.jpg','EP004_thumbnail_A21.jpg','EP004_upload_info_en.md','EP004_upload_info_ja.md','EP004_source_credits.md']:
            shutil.copy2(p,ROOT/'deliverables'/p.name)
    for lang in ['en','ja']:
        shutil.copy2(V1/f'deliverables/EP004_Pandora_{lang}_v01_1080p30.srt',ROOT/f'deliverables/EP004_Pandora_{lang}_v02_1080p30.srt')
    im.resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/'review/A04_v02_composition.jpg',quality=90,optimize=True)
    print('PREPARED',crop_px,[fit.width,fit.height],flush=True)


def render():
    shots=copy.deepcopy(read(V1/'records/render_shots.json'))
    target=next(s for s in shots if s['key']=='A04')
    visual=next(s for s in read(ROOT/'records/visual_manifest.json')['shots'] if s['key']=='A04')
    out=ROOT/'_work/render/P03_01_A04.mp4';filt=camera(target['frames'],target['camera_band'],False,.03)
    cfg=dict(image_sha256=sha(ROOT/visual['file']),frames=target['frames'],filter=filt,crf=18)
    stamp=out.with_suffix('.json')
    if not(out.exists() and stamp.exists() and read(stamp)==cfg):
        ff(['-loop',1,'-framerate',30,'-i',ROOT/visual['file'],'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',target['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',out]);save(stamp,cfg)
    for s in shots:
        if s['key']=='A04':s.update(**visual,encoded_file=str(out),zoom_percent=3)
        else:s['encoded_file']=str(V1/s['encoded_file'])
    save(ROOT/'records/render_shots.json',shots)
    listing=ROOT/'_work/concat.txt';listing.write_text(''.join(f"file '{s['encoded_file']}'\nduration {s['frames']/30:.9f}\n" for s in shots))
    raw=ROOT/'_work/picture_concat.mp4';ff(['-f','concat','-safe',0,'-i',listing,'-c','copy',raw])
    picture=ROOT/'_work/picture_master.mp4'
    ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movie_timescale',48000,'-movflags','+faststart',picture])
    for lang in ['en','ja']:
        old=V1/f'deliverables/EP004_Pandora_{lang}_v01_1080p30.mp4'
        dest=ROOT/f'deliverables/EP004_Pandora_{lang}_v02_1080p30.mp4'
        ff(['-i',picture,'-i',old,'-map','0:v:0','-map','1:a:0','-map_metadata',1,'-c','copy','-movie_timescale',48000,'-movflags','+faststart',dest])
        print('PACKAGED',lang,flush=True)


def frame_hashes(path):
    dest=ROOT/'_work'/f'frame_hash_{sha(path)}.txt'
    if not dest.exists():
        with dest.open('wb') as out:
            subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(path),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','framemd5','-'],stdout=out,check=True)
    return [line.split(',')[-1].strip() for line in dest.read_text().splitlines() if line and not line.startswith('#')]


def verify():
    files=[];frames=12887;samples=20619200
    oldshots=read(V1/'records/render_shots.json');newshots=read(ROOT/'records/render_shots.json')
    assert len(oldshots)==len(newshots)==31
    for old,new in zip(oldshots,newshots):
        assert (old['key'],old['start'],old['end'],old['frames'],old.get('texts'))==(new['key'],new['start'],new['end'],new['frames'],new.get('texts'))
        if old['key']!='A04':assert sha(V1/old['encoded_file'])==sha(new['encoded_file'])
    for lang in ['en','ja']:
        old=V1/f'deliverables/EP004_Pandora_{lang}_v01_1080p30.mp4'
        new=ROOT/f'deliverables/EP004_Pandora_{lang}_v02_1080p30.mp4'
        assert stream_hash(old,'a')==stream_hash(new,'a')
        assert (V1/f'deliverables/EP004_Pandora_{lang}_v01_1080p30.srt').read_bytes()==new.with_suffix('.srt').read_bytes()
        assert sha(V1/f'deliverables/EP004_upload_info_{lang}.md')==sha(ROOT/f'deliverables/EP004_upload_info_{lang}.md')
        info=probe(new);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
        assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',frames)
        assert v['time_base']=='1/15360' and int(v['duration_ts'])==frames*512
        assert a['time_base']=='1/48000' and int(a['duration_ts'])==samples
        pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(new)],text=True).splitlines()))
        assert pts==list(range(0,frames*512,512))
        q=measure(new);assert abs(float(q['input_i'])+16)<.3 and float(q['input_tp'])<=-1
        if lang=='ja':ff(['-i',new,'-f','null','-'])
        files.append(dict(name=new.name,bytes=new.stat().st_size,sha256=sha(new),video_stream_sha256=stream_hash(new,'v'),audio_stream_sha256=stream_hash(new,'a'),audio_identical_to_v01=True,srt_byte_identical_to_v01=True,upload_information_byte_identical_to_v01=True,loudness=q,frames=frames,audio_samples=samples,exact_30fps_pts=True,full_decode=True))
        print('VERIFIED',lang,'audio/SRT unchanged',q['input_i'],q['input_tp'],flush=True)
    assert files[0]['video_stream_sha256']==files[1]['video_stream_sha256']
    original=frame_hashes(V1/'deliverables/EP004_Pandora_en_v01_1080p30.mp4')
    revised=frame_hashes(ROOT/'deliverables/EP004_Pandora_en_v02_1080p30.mp4')
    assert len(original)==len(revised)==frames
    changed=[i for i,(a,b) in enumerate(zip(original,revised)) if a!=b]
    assert changed==list(range(1530,1860)),(len(changed),changed[:5],changed[-5:])
    assert sha(ROOT/'deliverables/EP004_audio_ja.wav')==sha(V1/'deliverables/EP004_audio_ja.wav')
    save(ROOT/'records/qc_v02.json',dict(passed=True,files=files,duration_seconds=frames/30,frames=frames,shared_video_stream=True,
        decoded_pixel_comparison=dict(pixel_format='yuv420p',method='MD5 of every full decoded frame',total_frames=frames,
            changed_frames=len(changed),changed_frame_range_inclusive=[changed[0],changed[-1]],unchanged_frames=frames-len(changed),all_frames_outside_A04_identical=True),
        unchanged_encoded_shots=30,japanese_wav_byte_identical=True,human_full_listening_performed_this_revision=False))
    print('FRAME COMPARISON',frames-len(changed),'unchanged /',len(changed),'A04 frames changed',flush=True)


def motion():
    import wom04_motion as prior
    prior.ROOT=ROOT
    shot=next(s for s in read(ROOT/'records/render_shots.json') if s['key']=='A04')
    m=prior.motion_stats(Path(shot['encoded_file']),prior.roi(shot))
    assert m['frame_pairs']==329 and m['p95_over_median']<=2.5
    save(ROOT/'records/motion_A04_v02.json',dict(passed=True,key='A04',start=51,end=62,frames=330,encoded_sha256=sha(shot['encoded_file']),measurement=m,
        method='All 30fps frames; gray mean absolute difference in inner 70% of cropped art. No temporal smoothing or dropped samples.'))
    print('MOTION A04',m['p95_over_median'],flush=True)


def preview():
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
    sheet=Image.new('RGB',(1280,768),'#0c1820');d=ImageDraw.Draw(sheet)
    for i,t in enumerate([51,53,55,57,59,61.966667]):
        path=ROOT/f'_work/A04_frame_{i}.jpg'
        ff(['-ss',t,'-i',ROOT/'deliverables/EP004_Pandora_en_v02_1080p30.mp4','-frames:v',1,'-vf','scale=640:360','-q:v',3,path])
        # Preserve the 16:9 proportions on the exported proof sheet.
        im=Image.open(path).resize((426,240),Image.Resampling.LANCZOS)
        x=i%3*426;y=i//3*384;sheet.paste(im,(x,y));d.text((x+8,y+246),f'A04 / {t:.3f}s',font=font,fill='white')
    sheet=sheet.crop((0,0,1280,660));sheet.save(ROOT/'review/A04_v02_six_frames.jpg',quality=90,optimize=True)
    old=ROOT/'_work/A04_before.jpg';after=ROOT/'_work/A04_after.jpg'
    for src,dest in [(V1/'deliverables/EP004_Pandora_en_v01_1080p30.mp4',old),(ROOT/'deliverables/EP004_Pandora_en_v02_1080p30.mp4',after)]:
        ff(['-ss',56.5,'-i',src,'-frames:v',1,'-vf','scale=1280:720','-q:v',3,dest])
    im=Image.new('RGB',(1280,770),'#0c1820');d=ImageDraw.Draw(im)
    for i,p in enumerate([old,after]):
        im.paste(Image.open(p).resize((640,360),Image.Resampling.LANCZOS),(i*640,30));d.text((i*640+12,4),'v01 / before' if i==0 else 'v02 / revised',font=font,fill='white')
    im=im.crop((0,0,1280,390));im.save(ROOT/'review/A04_before_after.jpg',quality=90,optimize=True)
    ff(['-i',ROOT/'deliverables/EP004_Pandora_en_v02_1080p30.mp4','-ss',51,'-t',11,'-c:v','libx264','-threads',2,'-preset','veryfast','-crf',18,'-c:a','copy','-movflags','+faststart',ROOT/'deliverables/EP004_A04_v02_preview.mp4'])
    print('PREVIEW READY',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render','verify','motion','preview']);a=p.parse_args();globals()[a.stage]()
