"""EP012：人物・トナカイの拡大。対象ショット以外の映像と音声を保存する。"""
import argparse
import copy
import json
import math
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import wom_shorts_ep012 as base
from wom_shorts_ep011_v02 import run, ff, frame_hashes

REPO=Path(__file__).resolve().parent
OLD=base.ROOT
ROOT=OLD.parent/'EP012_v02_20261107'
REQUEST=REPO/'wom_ショートClaude確認_EP012_v01_20261106.md'
DEST=REPO/'wom_ショート確認版_EP012_v02_20261107'
TAG='quiet-origins-ep012-shorts-v02-20261107'
OUTPUT_VERSION='v02'
IDS=['N1','N3']
TARGETS={'N1':'N08_person','N3':'N08_reindeer'}
read,save,sha=base.read,base.save,base.sha

def video(sid,version):
    return (OLD if version=='v01' else ROOT)/f'deliverables/QO_short_EP012_{sid}_{version}.mp4'

def prepare():
    assert Path('/Volumes/ESD-02').is_mount()
    for d in ['records','review','deliverables','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    shutil.copy2(REQUEST,ROOT/'records/request.md')
    before=read(OLD/'records/visual_manifest.json');after=copy.deepcopy(before)
    caps=read(OLD/'records/caption_manifest.json');layout=[]
    for g in after['shots']:
        sid=g['short_id']
        if TARGETS.get(sid)!=g['asset_id']:continue
        prev=copy.deepcopy(g)
        if sid=='N1':
            g.update(viewport=[0,180,1080,951],zoom_end=1.06)
            note='原画750×660の範囲を維持。表示幅1080px、0秒から1.06倍までLanczosで寄る。'
        else:
            # 角・足先を残し、上下の背景だけを詰めて字幕より上へ収める。
            g.update(crop_start=[270,1105,890,1695],crop_end=[270,1105,890,1695],viewport=[54,240,972,925],zoom_end=1.6/(972/620))
            note='原画620×730の上下背景65px・75pxを省き620×590。角・足先を保持。字幕との間隔13pxを確保。'
        rect=g['crop_start'];x,y,w,h=g['viewport'];cw=rect[2]-rect[0];ch=rect[3]-rect[1]
        scale=min(w/cw,h/ch);nw=round(cw*scale);nh=round(ch*scale)
        bounds=[x+round((w-nw)/2),y+round((h-nh)/2),x+round((w-nw)/2)+nw,y+round((h-nh)/2)+nh]
        g.update(native_max_scale=scale*g['zoom_end'],native_scale_limit=1.6,note=note,
                 foreground_height_fraction=nh/1920 if sid=='N1' else None)
        assert g['native_max_scale']<=1.6+1e-10
        cap_top=min(r['plate_bbox'][1] for c in caps if c['short_id']==sid and c['start_frame']<g['end_frame'] and c['end_frame']>g['start_frame'] for r in c['rows'])
        assert bounds[3]<cap_top
        row=dict(id=sid,asset_id=g['asset_id'],before={k:prev[k] for k in ['crop_start','viewport','zoom_end','native_max_scale']},
                 crop=g['crop_start'],viewport=g['viewport'],display_bounds=bounds,zoom_end=g['zoom_end'],native_max_scale=g['native_max_scale'],
                 caption_top=cap_top,caption_gap_px=cap_top-bounds[3],resampling='Pillow Lanczos',ai_interpolation=False,note=note)
        if sid=='N3':
            row['header_bottom']=max(r['bbox'][3] for r in g['header_texts'])
            row['header_gap_px']=bounds[1]-row['header_bottom'];assert row['header_gap_px']>0
            z=g['zoom_end'];row['last_frame_crop']=[580-cw/z/2,1400-ch/z/2,580+cw/z/2,1400+ch/z/2]
        layout.append(row)
    save(ROOT/'records/visual_manifest.json',after);save(ROOT/'records/layout.json',layout)
    unchanged=[]
    for sid in IDS:
        src=OLD/f'deliverables/QO_short_EP012_{sid}_v01.srt';dst=ROOT/f'deliverables/QO_short_EP012_{sid}_v02.srt'
        shutil.copy2(src,dst);assert sha(src)==sha(dst)
        unchanged.append(dict(id=sid,srt_sha256=sha(src),v02_srt_sha256=sha(dst)))
        shutil.copy2(OLD/f'deliverables/{sid}_upload_info.md',ROOT/f'deliverables/{sid}_upload_info.md')
    names=['caption_manifest.json','cta_design.json','shorts.json','headlines.json']
    for name in names:shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
    layers=sorted({c['file'] for c in caps}|{str(OLD/f'assets/{sid}_headline.png') for sid in IDS}|{str(OLD/'assets/common_cta.png')})
    save(ROOT/'records/unchanged_inputs.json',dict(subtitles=unchanged,records={n:sha(OLD/'records'/n) for n in names},
         layers=[dict(file=p,sha256=sha(p)) for p in layers],n2_original_sha256=sha(video('N2','v01'))))
    helper=base.helper();shorts=read(OLD/'records/shorts.json')['shorts']
    for sid in IDS:
        s=next(s for s in shorts if s['id']==sid);g=next(g for g in after['shots'] if g['asset_id']==TARGETS[sid])
        for n in [g['start_frame'],g['end_frame']-1]:
            im=helper.design_frame(s,n,after['shots'],caps,base.frame_art);im.thumbnail((720,1280));im.save(ROOT/f'review/{sid}_{n:04}_design.jpg',quality=92)
    print('準備完了',layout,flush=True)

def render():
    import imageio_ffmpeg
    helper=base.helper();shorts=read(OLD/'records/shorts.json')['shorts'];caps=read(OLD/'records/caption_manifest.json');shots=read(ROOT/'records/visual_manifest.json')['shots']
    records=[]
    for sid in IDS:
        s=next(s for s in shorts if s['id']==sid);gs=[g for g in shots if g['short_id']==sid];target=next(g for g in gs if g['asset_id']==TARGETS[sid])
        a,b=target['start_frame'],target['end_frame'];pattern=ROOT/f'_work/{sid}_original_%02d.mp4'
        split=ff(['-i',video(sid,'v01'),'-map','0:v:0','-c','copy','-f','segment','-segment_times',','.join(f'{g["start_frame"]/30:.9f}' for g in gs[1:]),'-segment_time_delta','0.00001','-reset_timestamps','1','-segment_format_options','avoid_negative_ts=disabled',pattern]);assert not split.stderr,split.stderr
        patch=ROOT/f'_work/{sid}_art_patch.mp4'
        cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-frames:v',str(b-a),'-fps_mode','passthrough','-video_track_timescale','15360','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(patch)]
        with (ROOT/f'records/{sid}_patch_encode.log').open('wb') as log:
            p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
            try:
                for n in range(a,b):p.stdin.write(helper.design_frame(s,n,shots,caps,base.frame_art).tobytes())
                p.stdin.close();assert p.wait()==0
            except BaseException:p.kill();p.wait();raise
        parts=[(patch if g['asset_id']==TARGETS[sid] else ROOT/f'_work/{sid}_original_{i:02}.mp4',g['frames']) for i,g in enumerate(gs)]
        playlist=ROOT/f'_work/{sid}_concat.txt';playlist.write_text('ffconcat version 1.0\n'+''.join(f"file '{p}'\nduration {n/30:.9f}\n" for p,n in parts))
        out=video(sid,'v02');r=ff(['-f','concat','-safe','0','-i',playlist,'-i',video(sid,'v01'),'-map','0:v:0','-map','1:a:0','-c','copy','-video_track_timescale','15360','-movflags','+faststart',out])
        (ROOT/f'records/{sid}_remux.log').write_text(r.stderr);assert not r.stderr,r.stderr
        records.append(dict(id=sid,start_frame=a,end_frame_exclusive=b,encoder=cmd,method='対象ショットのみ再描画。他の閉じたIDR区間と元AACはストリームコピー。',output=str(out),sha256=sha(out)))
        print('書き出し完了',sid,flush=True)
    save(ROOT/'records/encoding.json',records)

def qc():
    from wom_shorts_remake_produce import levels
    from wom_shorts_remake_qc_v03 import contrast,decode
    shorts=read(OLD/'records/shorts.json')['shorts'];caps=read(OLD/'records/caption_manifest.json');shots=read(ROOT/'records/visual_manifest.json')['shots'];results=[]
    for sid in IDS:
        src,out=video(sid,'v01'),video(sid,'v02');s=next(s for s in shorts if s['id']==sid);g=next(g for g in shots if g['asset_id']==TARGETS[sid]);a,b=g['start_frame'],g['end_frame']
        probe=json.loads(run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',out]).stdout);v=next(x for x in probe['streams'] if x['codec_type']=='video')
        assert (v['codec_name'],v['profile'],v['pix_fmt'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==('h264','High','yuv420p',1080,1920,'30/1',s['frames'])
        assert abs(float(v['duration'])-s['frames']/30)<.000001 and float(v['start_time'])==0
        dec=run(['ffmpeg','-nostdin','-v','warning','-i',out,'-f','null','-']);assert not dec.stderr,dec.stderr
        (ROOT/f'records/{sid}_continuous_decode.log').write_text(dec.stderr)
        oldhash,newhash=frame_hashes(src),frame_hashes(out);assert len(oldhash)==len(newhash)==s['frames']
        changes=[i for i,(x,y) in enumerate(zip(oldhash,newhash)) if x['md5']!=y['md5']];assert changes==list(range(a,b)),(sid,changes[:10],changes[-10:])
        assert all(x['pts']==y['pts']==i and x['duration']==y['duration']==1 for i,(x,y) in enumerate(zip(oldhash,newhash)))
        save(ROOT/f'records/{sid}_frame_comparison.json',dict(v01=oldhash,v02=newhash,changed_frames=changes,outside_patch_identical=True))
        def audio_hash(path,pcm):return run(['ffmpeg','-nostdin','-v','error','-i',path,'-map','0:a:0','-c:a','pcm_s16le' if pcm else 'copy','-f','hash','-hash','md5' if pcm else 'sha256','-']).stdout.strip().split('=')[1]
        pcm=[audio_hash(p,True) for p in [src,out]];aac=[audio_hash(p,False) for p in [src,out]];assert pcm[0]==pcm[1] and aac[0]==aac[1]
        aud=levels(out);assert abs(float(aud['input_i'])+14)<=.15 and float(aud['input_tp'])<=-1
        required=[0,15,30,45,60,75] if sid=='N1' else list(range(a,b,60))
        ns=sorted(set(required+[b-1,s['cta_start_frame'],s['frames']-1]+[(c['start_frame']+c['end_frame'])//2 for c in caps if c['short_id']==sid]))
        frames=decode(out,ns);pictures=[];cr=[]
        for n,arr in frames.items():
            im=Image.fromarray(arr);im.thumbnail((720,1280));p=ROOT/f'review/{sid}_{n:04}.jpg';im.save(p,quality=93,optimize=True)
            assert p.stat().st_size<1000000;pictures.append(dict(frame=n,seconds=n/30,file=p.name,sha256=sha(p)))
            if n<s['cta_start_frame']:
                c=next(c for c in caps if c['short_id']==sid and c['start_frame']<=n<c['end_frame']);cr.append(dict(frame=n,page=c['page'],**contrast(arr,c['file'])))
        hc=contrast(frames[0],next(h['file'] for h in read(OLD/'records/headlines.json') if h['id']==sid)) if sid=='N1' else None
        sheet=Image.new('RGB',(240*len(required),448),'#0c1820');d=ImageDraw.Draw(sheet)
        for j,n in enumerate(required):
            sheet.paste(Image.fromarray(frames[n]).resize((240,427)),(240*j,0));d.text((240*j+4,430),f'{sid} {n/30:.3f}s',fill='white')
        sheet.thumbnail((1280,1280));sheet.save(ROOT/f'review/{sid}_requested_times.jpg',quality=92,optimize=True)
        zs=np.exp(np.log(g['zoom_end'])*np.arange(g['frames'])/(g['frames']-1));c=np.array(g['crop_start']);sizes=np.column_stack(((c[2]-c[0])/zs,(c[3]-c[1])/zs));speed=np.linalg.norm(np.diff(sizes,axis=0),axis=1);ratio=float(np.percentile(speed,95)/np.median(speed));assert ratio<=2.5
        results.append(dict(id=sid,path=str(out),sha256=sha(out),bytes=out.stat().st_size,duration_seconds=s['frames']/30,container_duration=float(probe['format']['duration']),video_format={k:v[k] for k in ['codec_name','profile','pix_fmt','width','height','r_frame_rate','nb_frames']},warning_count=0,audio=aud,audio_pcm_md5_v01=pcm[0],audio_pcm_md5_v02=pcm[1],aac_sha256=aac[0],audio_pcm_identical=True,aac_identical=True,outside_patch_frame_count=s['frames']-len(changes),outside_patch_all_frames_identical=True,changed_start_frame=a,changed_end_frame_exclusive=b,subtitle_contrast=cr,headline_contrast=hc,pictures=pictures,native_max_scale=g['native_max_scale'],motion_p95_over_median=ratio,motion_method='全フレームの原画内カメラ座標変化量。光学フローではない。',human_full_listening=False,youtube_posted=False))
        print('検品合格',sid,'変更外一致',s['frames']-len(changes),'音声一致',flush=True)
    unchanged=read(ROOT/'records/unchanged_inputs.json');assert unchanged['n2_original_sha256']==sha(video('N2','v01'))
    assert all(sha(p['file'])==p['sha256'] for p in unchanged['layers'])
    assert all(sha(OLD/'records'/name)==value==sha(ROOT/'records'/name) for name,value in unchanged['records'].items())
    assert all(sha(ROOT/f'deliverables/QO_short_EP012_{r["id"]}_{OUTPUT_VERSION}.srt')==r['srt_sha256'] for r in unchanged['subtitles'])
    save(ROOT/'records/final_qc.json',results)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render','qc']);a=p.parse_args();globals()[a.stage]()
