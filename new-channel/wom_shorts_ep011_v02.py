"""EP011 v02: replace only two card GOPs; retain all other encoded pictures and audio."""
import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import wom_shorts_ep011 as base

REPO=Path(__file__).resolve().parent
OLD=base.ROOT
ROOT=OLD.parent/'EP011_v02_20261104'
REQUEST=REPO/'wom_ショート修正依頼_EP011_v02_20261104.md'
DEST=REPO/'wom_ショート確認版_EP011_v02_20261104'
TAG='quiet-origins-ep011-shorts-v02-20261104'
read,save,sha=base.read,base.save,base.sha
IDS=['H2','H3']

def run(args):
    r=subprocess.run([str(x) for x in args],capture_output=True,text=True)
    assert r.returncode==0,(args,r.stderr)
    return r

def ff(args):return run(['ffmpeg','-nostdin','-y','-v','warning',*args])

def video(sid,version):return (OLD if version=='v01' else ROOT)/f'deliverables/QO_short_EP011_{sid}_{version}.mp4'

def prepare():
    assert Path('/Volumes/ESD-02').is_mount(),'Specified SSD unavailable'
    for d in ['assets','records','review','deliverables','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    shutil.copy2(REQUEST,ROOT/'records/request.md')
    before=read(OLD/'records/card_texts.json');after=copy.deepcopy(before)
    changes={'THE HEART AND MAAT｜':'THE HEART AND MAAT','Maat: truth and right order｜':'Maat: truth and right order','The Negative Confession ·':'The Negative Confession'}
    for aid,card in after.items():
        im=Image.new('RGB',(1080,1920),'#e8d9b7');d=ImageDraw.Draw(im)
        for old,row in zip(before[aid]['texts'],card['texts']):
            text=changes.get(old['text'],old['text']);f=ImageFont.truetype(old['font'],old['font_size'])
            b=f.getbbox(text);w=b[2]-b[0];h=b[3]-b[1];x=round((1080-w)/2);y=old['bbox'][1]-(60 if aid=='D_balance' else 0)
            d.text((x-b[0],y-b[1]),text,font=f,fill='#3b2c21')
            row.update(text=text,bbox=[x,y,x+w,y+h])
            assert not text.endswith(('｜','·'))
            assert row['cap_height']==old['cap_height'] and row['font_size']==old['font_size']
            assert text==changes.get(old['text'],old['text'])
        p=ROOT/f'assets/{aid}_card.png';im.save(p);card.update(file=str(p),sha256=sha(p),source='Claude approved v02 card-only correction')
        thumb=im.copy();thumb.thumbnail((720,1280));thumb.save(ROOT/f'review/{aid}_card.jpg',quality=93,optimize=True)
    save(ROOT/'records/card_texts.json',after)
    manifest=read(OLD/'records/visual_manifest.json')
    for g in manifest['shots']:
        if g['asset_id'] not in after:continue
        p=after[g['asset_id']]['file'];g.update(file=p,background=p)
        g['source'].update(path=p,sha256=sha(p))
    save(ROOT/'records/visual_manifest.json',manifest)
    bal=next(g for g in manifest['shots'] if g['asset_id']=='D_balance')
    header_bottom=max(r['bbox'][3] for r in bal['header_texts'])
    cta_top=min(r['glyph_bbox'][1] for r in read(OLD/'records/cta_design.json')['rows'])
    rows=after['D_balance']['texts'];bottom=max(r['bbox'][3] for r in rows);top=min(r['bbox'][1] for r in rows)
    assert cta_top-bottom>=80 and top-header_bottom>=40
    caps=read(OLD/'records/caption_manifest.json')
    cap_top=min(r['plate_bbox'][1] for c in caps if c['short_id']=='H2' and c['end_frame']>bal['start_frame'] for r in c['rows'])
    assert bottom<cap_top
    save(ROOT/'records/layout.json',dict(balance_shift_y=-60,balance_bottom=bottom,cta_glyph_top=cta_top,cta_gap_px=cta_top-bottom,cta_plate_gap_px=1030-bottom,header_bottom=header_bottom,balance_top=top,header_gap_px=top-header_bottom,caption_top=cap_top,caption_gap_px=cap_top-bottom))
    hashes=[]
    for sid in IDS:
        src=OLD/f'deliverables/QO_short_EP011_{sid}_v01.srt';dst=ROOT/f'deliverables/QO_short_EP011_{sid}_v02.srt';shutil.copy2(src,dst)
        hashes.append(dict(id=sid,srt_sha256=sha(src),srt_v02_sha256=sha(dst)))
        shutil.copy2(OLD/f'deliverables/{sid}_upload_info.md',ROOT/f'deliverables/{sid}_upload_info.md')
    save(ROOT/'records/unchanged_inputs.json',dict(subtitles=hashes,caption_manifest_sha256=sha(OLD/'records/caption_manifest.json'),shorts_sha256=sha(OLD/'records/shorts.json'),cta_sha256=sha(OLD/'assets/common_cta.png'),h1_original_sha256=sha(video('H1','v01'))))
    print('PREPARED',read(ROOT/'records/layout.json'),flush=True)

def render():
    import imageio_ffmpeg
    helper=base.helper();shorts=read(OLD/'records/shorts.json')['shorts'];caps=read(OLD/'records/caption_manifest.json');shots=read(ROOT/'records/visual_manifest.json')['shots']
    records=[]
    for sid in IDS:
        s=next(s for s in shorts if s['id']==sid);g=next(g for g in shots if g['short_id']==sid and g['static']);a,b=g['start_frame'],g['end_frame']
        # Original cuts are closed IDRs. Segment at those cuts without decoding unchanged GOPs.
        boundaries=[a]+([b] if b<s['frames'] else [])
        pattern=ROOT/f'_work/{sid}_original_%02d.mp4'
        cmd=['-i',video(sid,'v01'),'-map','0:v:0','-c','copy','-f','segment','-segment_times',','.join(f'{n/30:.9f}' for n in boundaries),'-segment_time_delta','0.00001','-reset_timestamps','1','-segment_format_options','avoid_negative_ts=disabled',pattern]
        split=ff(cmd);assert not split.stderr,split.stderr
        patch=ROOT/f'_work/{sid}_card_patch.mp4'
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-frames:v',str(b-a),'-fps_mode','passthrough','-video_track_timescale','15360','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(patch)]
        with (ROOT/f'records/{sid}_patch_encode.log').open('wb') as log:
            p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
            try:
                for n in range(a,b):
                    im=helper.design_frame(s,n,shots,caps,base.frame_art);p.stdin.write(im.tobytes())
                p.stdin.close();assert p.wait()==0
            except BaseException:p.kill();p.wait();raise
        parts=[(ROOT/f'_work/{sid}_original_00.mp4',a),(patch,b-a)]
        if b<s['frames']:parts.append((ROOT/f'_work/{sid}_original_02.mp4',s['frames']-b))
        playlist=ROOT/f'_work/{sid}_concat.txt'
        playlist.write_text('ffconcat version 1.0\n'+''.join(f"file '{p}'\nduration {n/30:.9f}\n" for p,n in parts))
        out=video(sid,'v02')
        result=ff(['-f','concat','-safe','0','-i',playlist,'-i',video(sid,'v01'),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','15360','-movflags','+faststart',out])
        (ROOT/f'records/{sid}_remux.log').write_text(result.stderr)
        records.append(dict(id=sid,card_start_frame=a,card_end_frame_exclusive=b,patch_encoder=cmd,method='Original closed-IDR video segments retained with stream copy; only card segment re-encoded. Original AAC stream copied.',output=str(out),sha256=sha(out)))
        print('RENDERED',sid,flush=True)
    save(ROOT/'records/encoding.json',records)

def frame_hashes(path):
    r=run(['ffmpeg','-nostdin','-v','error','-i',path,'-map','0:v:0','-pix_fmt','yuv420p','-f','framemd5','-'])
    rows=[line.split(',') for line in r.stdout.splitlines() if line and not line.startswith('#')]
    return [dict(dts=int(r[1]),pts=int(r[2]),duration=int(r[3]),bytes=int(r[4]),md5=r[5].strip()) for r in rows]

def qc():
    from wom_shorts_remake_produce import levels
    from wom_shorts_ep011_qc import card_contrast
    from wom_shorts_remake_qc_v03 import contrast
    shorts=read(OLD/'records/shorts.json')['shorts'];caps=read(OLD/'records/caption_manifest.json');shots=read(ROOT/'records/visual_manifest.json')['shots']
    results=[]
    for sid in IDS:
        src=video(sid,'v01');out=video(sid,'v02');s=next(s for s in shorts if s['id']==sid);g=next(g for g in shots if g['short_id']==sid and g['static'])
        probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',out]).stdout)
        v=next(x for x in probe['streams'] if x['codec_type']=='video')
        assert (v['codec_name'],v['profile'],v['pix_fmt'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==('h264','High','yuv420p',1080,1920,'30/1',s['frames']),v
        assert abs(float(v['duration'])-s['frames']/30)<.000001 and float(v['start_time'])==0,v
        dec=run(['ffmpeg','-nostdin','-v','warning','-i',out,'-f','null','-'])
        (ROOT/f'records/{sid}_continuous_decode.log').write_text(dec.stderr)
        assert not dec.stderr,dec.stderr
        oldhash=frame_hashes(src);newhash=frame_hashes(out)
        assert len(oldhash)==len(newhash)==s['frames'],(len(oldhash),len(newhash))
        changes=[i for i,(a,b) in enumerate(zip(oldhash,newhash)) if a['md5']!=b['md5']]
        assert changes==list(range(g['start_frame'],g['end_frame'])),(sid,changes[:10],changes[-10:])
        assert all(a['pts']==b['pts']==i and a['duration']==b['duration']==1 for i,(a,b) in enumerate(zip(oldhash,newhash)))
        save(ROOT/f'records/{sid}_frame_comparison.json',dict(v01=oldhash,v02=newhash,changed_frames=changes,outside_card_identical=True))
        def audio_hash(path,pcm=True):
            return run(['ffmpeg','-nostdin','-v','error','-i',path,'-map','0:a:0','-c:a','pcm_s16le' if pcm else 'copy','-f','hash','-hash','md5' if pcm else 'sha256','-']).stdout.strip().split('=')[1]
        md5=[audio_hash(p) for p in [src,out]];aac=[audio_hash(p,False) for p in [src,out]]
        assert md5[0]==md5[1] and aac[0]==aac[1]
        aud=levels(out);assert abs(float(aud['input_i'])+14)<=.15 and float(aud['input_tp'])<=-1
        indices=sorted(set([g['start_frame'],g['end_frame']-1,s['cta_start_frame'],s['frames']-1]+[(c['start_frame']+c['end_frame'])//2 for c in caps if c['short_id']==sid and c['end_frame']>g['start_frame'] and c['start_frame']<g['end_frame']]))
        cr=[];cc=[];pictures=[]
        for n in indices:
            args=['ffmpeg','-nostdin','-v','error','-i',str(out),'-vf',f'select=eq(n\\,{n})','-frames:v','1','-pix_fmt','rgb24','-f','rawvideo','-']
            r=subprocess.run(args,capture_output=True);assert r.returncode==0 and len(r.stdout)==1080*1920*3,r.stderr
            arr=np.frombuffer(r.stdout,np.uint8).reshape(1920,1080,3);im=Image.fromarray(arr)
            im.save(ROOT/f'_work/{sid}_{n:04}.png')
            im.thumbnail((720,1280));p=ROOT/f'review/{sid}_{n:04}.jpg';im.save(p,quality=93,optimize=True);pictures.append(dict(frame=n,file=p.name,sha256=sha(p)))
            if g['start_frame']<=n<g['end_frame']:
                if n<s['cta_start_frame']:
                    cc.append(dict(frame=n,**card_contrast(arr,g['file'])))
                if n<s['cta_start_frame']:
                    c=next(c for c in caps if c['short_id']==sid and c['start_frame']<=n<c['end_frame'])
                    cr.append(dict(frame=n,page=c['page'],**contrast(arr,c['file'])))
        results.append(dict(id=sid,path=str(out),sha256=sha(out),bytes=out.stat().st_size,duration_seconds=s['frames']/30,container_duration=float(probe['format']['duration']),video_format={k:v[k] for k in ['codec_name','profile','pix_fmt','width','height','r_frame_rate','nb_frames']},warning_count=0,audio=aud,audio_pcm_md5_v01=md5[0],audio_pcm_md5_v02=md5[1],aac_sha256=aac[0],audio_pcm_identical=True,outside_card_frame_count=s['frames']-len(changes),outside_card_all_frames_identical=True,changed_start_frame=min(changes),changed_end_frame_exclusive=max(changes)+1,changed_start_seconds=min(changes)/30,changed_end_seconds=(max(changes)+1)/30,subtitle_layers_unchanged=True,card_contrast=cc,subtitle_contrast=cr,pictures=pictures,human_full_listening=False,youtube_posted=False))
        print('QC PASS',sid,'identical outside',s['frames']-len(changes),'audio PCM',md5[0],flush=True)
    assert read(ROOT/'records/unchanged_inputs.json')['h1_original_sha256']==sha(video('H1','v01'))
    save(ROOT/'records/final_qc.json',results)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render','qc']);a=p.parse_args();globals()[a.stage]()
