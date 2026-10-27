"""EP006 v03: change only first-shot framing, camera and hook headline."""
import os, sys, json, copy, shutil, subprocess, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter, ImageEnhance
HERE=Path(__file__).resolve().parent
OLD=Path('/Users/ryo/Desktop/新チャンネル/ショート/EP006_冒頭比較_v02_20261027')
V01=OLD.with_name('EP006_確認版_v01_20261027')
ROOT=OLD.with_name('EP006_冒頭_v03_20261027')
REQUEST=HERE/'wom_ショート冒頭修正_EP006_v03_20261027.md'
os.environ['QO_EP006_ROOT']=str(ROOT)
os.environ['QO_EP006_REQUEST']=str(HERE/'wom_ショート冒頭修正_EP006_v02_20261027.md')
os.environ['QO_EP006_CONFIG']=str(HERE/'wom06_shorts_v02_config.json')
import wom06_shorts_render as base
import wom06_shorts_qc as qc
base.VERSION='v03';qc.VERSION='v03'
read=base.read;save=base.save;sha=base.sha;ff=base.ff
FONT='/System/Library/Fonts/Supplemental/Georgia Bold.ttf'
HEADLINES={'S1':['THE RIDDLE',"ISN\'T IN",'THE PLAY'],'S2':['NOT A','WOMAN'],'S3':['NOSE GONE','BEFORE','NAPOLEON']}


def headline(sid):
    layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer)
    f=ImageFont.truetype(FONT,136)
    top={'S1':365,'S2':820,'S3':755}[sid]
    # Exact uppercase glyph height, independently of the nominal font size.
    line_images=[];boxes=[]
    for text in HEADLINES[sid]:
        b=d.textbbox((0,0),text,font=f);mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),text,font=f,fill=255)
        mask=mask.resize((min(770,round(mask.width*100/mask.height)),100),Image.Resampling.LANCZOS)
        line_images.append(mask)
    bottom=top+len(line_images)*122-22
    shadow=Image.new('RGBA',layer.size)
    ImageDraw.Draw(shadow).rounded_rectangle((84,top-18,876,bottom+18),radius=16,fill=(5,12,16,125))
    layer=Image.alpha_composite(layer,shadow)
    for j,(text,mask) in enumerate(zip(HEADLINES[sid],line_images)):
        x=480-mask.width//2;y=top+j*122
        layer.paste((244,239,223,255),(x,y,x+mask.width,y+100),mask)
        boxes.append(dict(text=text,bbox=[x,y,x+mask.width,y+100],glyph_height=100))
    assert 330<=top<bottom<=1100 and all(80<=b['bbox'][0]<b['bbox'][2]<=880 for b in boxes)
    out=ROOT/f'assets/{sid}_headline.png';layer.save(out)
    return dict(text=' '.join(HEADLINES[sid]),font=FONT,color='#f4efdf',lines=boxes,
        overlay_bbox=[84,top-18,876,bottom+18],file=str(out),sha256=sha(out),start_frame=0,fade_start_seconds=2,fade_duration_seconds=.3,end_frame=69)


def prepare():
    for d in ['records','assets','audio','review','deliverables','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    names=['shorts.json','narration.json','reading_replacements.json','audio_qc.json','caption_manifest.json','subtitle_qc.json']+[f'{sid}_phoneme_timings.json' for sid in HEADLINES]
    for name in names:shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
    for sid in HEADLINES:
        for suffix in ['final.m4a','normalized.wav']:
            shutil.copy2(OLD/f'audio/{sid}_{suffix}',ROOT/f'audio/{sid}_{suffix}')
    aq=read(ROOT/'records/audio_qc.json')
    for r in aq['reports']:r['final_file']=str(ROOT/f'audio/{r["id"]}_final.m4a')
    save(ROOT/'records/audio_qc.json',aq)
    previous=read(OLD/'records/render_shots.json');shots=[];hooks=[]
    for original in previous:
        s=copy.deepcopy(original);s['changed_v03']=s['start_frame']==0
        if not s['changed_v03']:
            assert Path(s['encoded_file']).exists() and sha(s['encoded_file'])==s['encoded_sha256']
            shots.append(s);continue
        sid=s['short_id'];im=ImageOps.exif_transpose(Image.open(s['source']['path'])).convert('RGB')
        assert sha(s['source']['path'])==s['source']['sha256']
        if sid=='S1':
            safe=[math.ceil(.12*im.width),math.ceil(.10*im.height),math.floor(.95*im.width),math.floor(.33*im.height)]
            safe_image=im.crop(safe)
            h=safe_image.height;w=round(h*1080/1600);x=round(safe_image.width*.49-w/2)
            local=[x,0,x+w,h];crop=[safe[0]+x,safe[1],safe[0]+x+w,safe[3]]
            piece=safe_image.crop(local);height=1600
            bg=ImageEnhance.Brightness(ImageOps.fit(safe_image,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.30)
            fallback='1600px / 83.33% foreground height; safe source strip is 920px high, limiting enlargement and retaining both faces.'
        elif sid=='S2':
            crop=[3820,1500,5817,5050];piece=im.crop(crop);height=1920;bg=Image.new('RGB',(1080,1920));safe=None;fallback=None
        else:
            crop=[2470,0,5364,5144];piece=im.crop(crop);height=1920;bg=Image.new('RGB',(1080,1920));safe=None;fallback=None
        bg.paste(piece.resize((1080,height),Image.Resampling.LANCZOS),(0,0))
        # The stable header is copied exactly from the approved v02 composition.
        header=Image.new('RGBA',(1080,1920));old_image=Image.open(s['file']).convert('RGBA')
        header.paste(old_image.crop((0,120,1080,270)),(0,120))
        headerpath=ROOT/f'assets/{sid}_header.png';header.save(headerpath)
        raw=ROOT/f'assets/{sid}_portrait.png';bg.save(raw)
        s.update(file=str(raw),sha256=sha(raw),header_file=str(headerpath),
            encoded_file=str(ROOT/f'_work/{sid}_opening_v03.mp4'),art_box=[0,0,1080,height],viewport=[0,0,1080,height],
            zoom_start=1.,zoom_end=1.08,source_crop_pixels=crop,source_safe_pixels=safe,
            foreground_height_pixels=height,foreground_height_fraction=height/1920,
            source_to_output_scale_start=[1080/piece.width,height/piece.height],
            source_to_output_scale_end=[1080/piece.width*1.08,height/piece.height*1.08],
            foreground_fallback_reason=fallback,background_also_uses_only_crop=True)
        hook=headline(sid);hooks.append(hook|{'id':sid})
        shots.append(s)
        preview=Image.alpha_composite(bg.convert('RGBA'),header)
        preview=Image.alpha_composite(preview,Image.open(hook['file']).convert('RGBA'))
        preview.thumbnail((720,1280));preview.convert('RGB').save(ROOT/f'review/{sid}_opening_design.jpg',quality=88)
    save(ROOT/'records/render_shots.json',shots)
    save(ROOT/'records/visual_manifest.json',dict(shots=shots,assets=read(OLD/'records/visual_manifest.json')['assets'],same_source_not_repeated=True))
    save(ROOT/'records/headlines.json',hooks)
    save(ROOT/'records/revision_plan.json',dict(request=str(REQUEST),request_sha256=sha(REQUEST),reference_root=str(OLD),
        changed_first_shot_frames={s['short_id']:[s['start_frame'],s['end_frame']] for s in shots if s['changed_v03']},
        preserved_records={name:sha(OLD/'records'/name) for name in names},
        original_video_sha256={sid:sha(OLD/f'deliverables/QO_short_EP006_{sid}_v02.mp4') for sid in HEADLINES},
        audio_reencoded=False,script_changed=False,subtitles_changed=False,later_shot_inputs_unchanged=True))
    print('PREPARED V03',flush=True)


def first_camera(s):
    n=s['frames'];h=s['foreground_height_pixels'];z=f'exp(log(1.08)*on/{n-1})'
    x=f'(W-W/{z})/2';y=f'H-H/{z}' if s['short_id']=='S1' else f'(H-H/{z})/2'
    p=f"perspective=x0='{x}':y0='{y}':x1='{x}+W/{z}':y1='{y}':x2='{x}':y2='{y}+H/{z}':x3='{x}+W/{z}':y3='{y}+H/{z}':sense=source:eval=frame:interpolation=cubic"
    return f'[0:v]split=2[base][art];[art]crop=1080:{h}:0:0,format=yuv444p,{p}[moving];[base][moving]overlay=0:0:format=yuv444[portrait];[portrait][1:v]overlay=0:0:format=yuv444,format=yuv420p[v]'


def build():
    import imageio_ffmpeg
    shots=read(ROOT/'records/render_shots.json');hooks={h['id']:h for h in read(ROOT/'records/headlines.json')}
    for s in shots:
        if not s['changed_v03']:continue
        path=Path(s['encoded_file']);cfg=dict(image=s['sha256'],header=sha(s['header_file']),frames=s['frames'],camera=first_camera(s));stamp=path.with_suffix('.json')
        if not(path.exists() and stamp.exists() and read(stamp)==cfg):
            ff(['-loop',1,'-framerate',30,'-i',s['file'],'-loop',1,'-framerate',30,'-i',s['header_file'],
                '-filter_complex_threads',2,'-filter_complex',first_camera(s),'-map','[v]','-frames:v',s['frames'],'-an',
                '-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-profile:v','high','-pix_fmt','yuv420p',
                '-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',path])
            save(stamp,cfg)
        s['encoded_sha256']=sha(path);print('OPENING',s['short_id'],flush=True)
    save(ROOT/'records/render_shots.json',shots)
    manifest=read(ROOT/'records/visual_manifest.json');manifest['shots']=shots;save(ROOT/'records/visual_manifest.json',manifest)
    encodings=[]
    for row in read(ROOT/'records/shorts.json')['shorts']:
        sid=row['id'];ass,records=base.make_ass(row)
        assert records==[p for p in read(OLD/'records/caption_manifest.json') if p['short_id']==sid]
        assert ass.read_bytes()==(OLD/f'_work/{sid}.ass').read_bytes()
        out=ROOT/f'deliverables/QO_short_EP006_{sid}_v03.mp4'
        fc=f"[2:v]format=rgba,fade=t=out:st=2:d=0.3:alpha=1[hook];[0:v][hook]overlay=0:0:enable='lt(t,2.3)'[titled];[titled]ass='{ass}'[v]"
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s','1080x1920','-r','30','-i','pipe:0',
             '-i',str(ROOT/f'audio/{sid}_final.m4a'),'-loop','1','-framerate','30','-i',hooks[sid]['file'],
             '-filter_complex_threads','2','-filter_complex',fc,'-map','[v]','-map','1:a:0','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high',
             '-frames:v',str(row['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p',
             '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart',str(out)]
        group=[s for s in shots if s['short_id']==sid]
        with (ROOT/f'records/{sid}_encode.log').open('w') as log:
            enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
            try:
                for s in group:
                    assert '/deliverables/' not in s['encoded_file']
                    subprocess.run(['ffmpeg','-nostdin','-v','warning','-threads','2','-i',s['encoded_file'],'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
                enc.stdin.close();assert enc.wait()==0
            except BaseException:enc.kill();enc.wait();raise
        encodings.append(dict(id=sid,command=cmd,video_sha256=sha(out),shot_sources=[dict(path=s['encoded_file'],sha256=s['encoded_sha256']) for s in group]))
        print('RENDERED',sid,flush=True)
    save(ROOT/'records/encoding_method.json',dict(method='Independent shot decoders → raw frames → one final encoder. Only first-shot inputs changed; original subtitle ASS retained, headline overlay limited to frames 0–68. Final v02 MP4 used only for QA, never as render input.',shorts=encodings))


if __name__=='__main__':globals()[sys.argv[1]]()
