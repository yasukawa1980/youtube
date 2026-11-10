"""Measure the three delivered MP4s and extract verification stills."""
import json
import math
import re
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image, ImageDraw, ImageColor

from wom_shorts_ep014 import ROOT, REQUEST, PAPER, bounds, read, save, sha, helpers
from wom_shorts_ep013_qc import contrast, stream_hash

OPENING = [0,15,30,45,60,75]
RAW = 1080*1920*3

def sheet(folder, indices, path, columns):
    columns=min(columns,len(indices))
    width=1280//columns
    height=round(width*16/9)
    image=Image.new('RGB',(columns*width,math.ceil(len(indices)/columns)*(height+22)),'#0c1820')
    draw=ImageDraw.Draw(image)
    for i,frame in enumerate(indices):
        x,y=(i%columns)*width,(i//columns)*(height+22)
        with Image.open(folder/f'{frame:04}.jpg') as still:
            image.paste(still.resize((width,height),Image.Resampling.LANCZOS),(x,y))
        draw.text((x+7,y+height+3),f'{frame/30:.3f}s',fill='white')
    image.save(path,quality=89,optimize=True)

def luminance(color):
    values = [c/255 for c in ImageColor.getrgb(color)]
    return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4)
               for w,v in zip((.2126,.7152,.0722),values))

def card_contrast(rows):
    return [dict(text=row['text'], contrast_ratio=(luminance(PAPER)+.05)/(luminance(row['color'])+.05),
                 method='WCAG ratio from specified foreground and paper RGB')
            for row in rows]

def qc():
    old,_=helpers()
    import wom14_scenes as scene
    audio=read(ROOT/'records/audio_qc.json')['reports']
    scripts=read(ROOT/'records/shorts.json')['shorts']
    caps=read(ROOT/'records/caption_manifest.json')
    cards=read(ROOT/'records/card_texts.json')
    shots=read(ROOT/'records/visual_manifest.json')['shots']
    output=[]
    for short,mix in zip(scripts,audio,strict=True):
        sid=short['id']
        path=ROOT/f'deliverables/QO_short_EP014_{sid}_v01.mp4'
        qc_path=ROOT/f'records/{sid}_continuous_decode.log'
        ff=['ffmpeg','-nostdin','-v','warning','-i',str(path)]
        with qc_path.open('wb') as err:
            subprocess.run([*ff,'-map','0:v:0','-map','0:a:0','-f','null','-'],
                           stderr=err,check=True)
        assert not qc_path.stat().st_size,qc_path.read_text()
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams',
                                                 '-of','json',str(path)]))
        video,track=probe['streams']
        frames=short['frames']
        assert (video['codec_name'],video['profile'],video['width'],video['height'],video['pix_fmt'],
                video['r_frame_rate'],int(video['nb_frames']),video['color_space'])==(
                'h264','High',1080,1920,'yuv420p','30/1',frames,'bt709')
        assert (track['codec_name'],track['sample_rate'],track['channels'])==('aac','48000',2)
        assert frames<=720 and frames-short['cta_start_frame']==75
        assert float(probe['format']['duration'])<=24
        assert short['voice_onset_seconds']<=.3 and mix['bgm_first_10ms_dbfs']>-70
        loudness=old.levels(path)
        assert abs(float(loudness['input_i'])+14)<=.15 and float(loudness['input_tp'])<=-1
        assert stream_hash(path)==stream_hash(ROOT/f'audio/{sid}_final.m4a')
        chapters=[g for g in shots if g['short_id']==sid]
        assert chapters[0]['start_frame']==0 and chapters[-1]['end_frame']==frames
        assert all(a['end_frame']==b['start_frame'] for a,b in zip(chapters,chapters[1:]))
        pages=[p for p in caps if p['short_id']==sid]
        assert ' '.join(p['text'] for p in pages)==short['text']
        assert all(not re.search(r'[.!?][”"]?\s',p['text']) for p in pages)
        for page in pages:
            assert ' '.join(page['lines'])==page['text']
            assert all(row['font_size']==55 and row['cap_height']==39 and not row['resampling']
                       for row in page['rows'])
            assert all(not re.search(r"\b(a|an|the|of|to|for|with|in|on|through|into|from|at)$",line,re.I)
                       for line in page['lines'])
        text_checks=[]
        for shot in chapters:
            key=shot['asset_id'].removesuffix('_text')
            if key in scene.CAT:
                assert shot['labels']==list(scene.CAT[key])
                assert [r['text'] for r in shot['label_rows']]==shot['labels']
                text_checks.extend(card_contrast(shot['label_rows']))
            if key in scene.BOXES:
                assert shot['highlight_boxes']==[[bounds(shot['source_size'],b) for b in stage]
                                                 for stage in scene.BOXES[key]]
            if key=='D_compass_s':
                assert cards[key]['exact_text_verified']
                text_checks.extend(card_contrast(cards[key]['texts']))
        assert min(row['contrast_ratio'] for row in text_checks)>=4.5
        evidence={kind:indices for kind,indices in [
            ('opening',OPENING),('every2s',list(range(0,frames,60))),
            ('all_captions',[(p['start_frame']+p['end_frame'])//2 for p in pages]),
            ('CTA',[short['cta_start_frame'],frames-1]),
            ('source_cues',sorted({n for g in chapters for n in
                                   [g['start_frame'],(g['start_frame']+g['end_frame'])//2,g['end_frame']-1,
                                    *g.get('highlight_frames',[])]}))]}
        expected=sorted(set().union(*evidence.values(),{1,2,3,4,5}))
        folder=ROOT/f'review/{sid}_frames'
        folder.mkdir(exist_ok=True)
        filt="select='"+'+'.join(f'eq(n,{n})' for n in expected)+"',scale=flags=accurate_rnd+full_chroma_int:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24"
        images={}
        checks=[]
        rgb_log=ROOT/f'records/{sid}_rgb_extract.log'
        with rgb_log.open('wb') as err:
            cmd=[*ff,'-an','-vf',filt,'-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-']
            with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=err) as process:
                for n in expected:
                    data=process.stdout.read(RAW)
                    assert len(data)==RAW,(sid,n,len(data))
                    arr=np.frombuffer(data,np.uint8).reshape(1920,1080,3)
                    still=Image.fromarray(arr)
                    for p,at in zip(pages,evidence['all_captions']):
                        if n==at:
                            checks.append(dict(text=p['text'],frame=n,**contrast(arr,p['file'])))
                    if n==0:
                        headline=contrast(arr,ROOT/f'assets/{sid}_headline.png')
                    if n==short['cta_start_frame']:
                        cta_contrast=contrast(arr,ROOT/'assets/common_cta.png')
                    if n<=5:
                        # Exclude fixed labels, headline and captions to sample only the moving opening artwork.
                        images[n]=np.asarray(still.crop((100,300,880,810)).convert('L'),dtype=np.int16)
                    if any(n in selection for selection in evidence.values()):
                        still.thumbnail((720,1280))
                        still.save(folder/f'{n:04}.jpg',quality=92,optimize=True)
                assert not process.stdout.read(1) and process.wait()==0
        assert not rgb_log.stat().st_size,rgb_log.read_text()
        motion=[float(np.mean(np.abs(images[n]-images[n-1]))) for n in range(1,6)]
        assert all(delta>0 for delta in motion)
        for kind,indices in evidence.items():
            sheet(folder,indices,ROOT/f'review/{sid}_{kind}.jpg',2 if kind=='CTA' else 4)
        output.append(dict(id=sid,filename=path.name,bytes=path.stat().st_size,sha256=sha(path),
            video_duration=frames/30,container_duration=float(probe['format']['duration']),
            frame_count=frames,video='H.264 High, 1080x1920, 30 fps, yuv420p, BT.709',
            audio='AAC, 48000 Hz, stereo',loudness_lufs=float(loudness['input_i']),
            true_peak_dbtp=float(loudness['input_tp']),decode_warnings=0,
            rgb_extract_warnings=0,
            voice_onset_seconds=short['voice_onset_seconds'],bgm_first_10ms_dbfs=mix['bgm_first_10ms_dbfs'],
            cta_start_frame=short['cta_start_frame'],cta_seconds=2.5,caption_pages=len(pages),
            cross_sentence_captions=0,caption_minimum_contrast=min(c['contrast_ratio'] for c in checks),
            caption_contrast=checks,headline_contrast=headline,cta_contrast=cta_contrast,
            source_text_contrast=text_checks,opening_frame_luma_deltas=motion,
            evidence_frames=evidence))
        print('QC',sid,output[-1]['loudness_lufs'],output[-1]['caption_minimum_contrast'],flush=True)
    save(ROOT/'records/final_qc.json',output)

def bundle():
    assert len(read(ROOT/'records/final_qc.json'))==3
    path=ROOT/'deliverables/EP014_shorts_QA_v01.zip'
    with ZipFile(path,'w',compression=ZIP_DEFLATED) as archive:
        archive.write(REQUEST,'request.md')
        for directory in ['records','review']:
            for item in sorted((ROOT/directory).rglob('*')):
                if item.is_file() and not item.name.endswith('_design.jpg'):
                    archive.write(item,item.relative_to(ROOT))
    with ZipFile(path) as archive:
        assert archive.testzip() is None

if __name__=='__main__':
    qc()
    bundle()
