"""Replace only the three EP014 short intervals identified in Claude's v02 review."""
import json
import os
import subprocess
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from PIL import Image, ImageDraw

import wom_shorts_ep014 as v01
from wom14_v02_assemble import concat, framehash

SSD = Path('/Volumes/ESD-02')
SHORTS = SSD/'新チャンネル/ショート'
BASE = SHORTS/'EP014_v01_20261111'
ROOT = Path(os.environ.get('WOM_EP014_SHORTS_V02_ROOT', SHORTS/'EP014_v02_20261113'))
REQUEST = Path(__file__).with_name('wom_ショートClaude確認_EP014_v01_20261112.md')
RUST = '#943a2c'
SOURCES = {
    'O1': '7f40d57868513fea9788b04458fb8ef288f6352e2b605e40b05652b328454f3d',
    'O2': '66e406f911b66d41da3ecc9290872a8b82240a265e16439f631ab873d228d6c0',
    'O3': '6cce54b528b429f4c33acddbacedb61c91aff36ad5be750c19e76a2ead8594c9',
}
COUNTS = {'O1': 694, 'O2': 584, 'O3': 634}
REPLACE = {'O1': (112,503), 'O2': (222,584), 'O3': (67,634)}
CAPTION_CHANGES = {'O1': [112,394,503], 'O2': [222,271], 'O3': [67,116,308,483]}
FMT = 'scale=flags=accurate_rnd+full_chroma_int:in_color_matrix=bt709:in_range=tv:out_range=pc,format=rgb24'
RAW_RGB = 1080*1920*3

def video(sid, version):
    root = BASE if version=='v01' else ROOT
    return root/f'deliverables/QO_short_EP014_{sid}_{version}.mp4'

def probe(path, *args):
    return json.loads(subprocess.check_output(['ffprobe','-v','error',*args,'-of','json',str(path)]))

def ff(log, *args):
    with log.open('wb') as error:
        subprocess.run(['ffmpeg','-nostdin','-y','-v','warning','-xerror',*map(str,args)],
                       stderr=error,check=True)
    assert log.stat().st_size==0,log.read_text()

def revised_shots(visual):
    by_key = {shot['asset_id']:shot for shot in visual}
    book = by_key['O03-23']
    izumo = by_key['O06-38']
    text = by_key['O11-12_text']
    compass = by_key['D_compass_s']
    # The end of the right column continues at the top of the left. Omit the
    # preceding right column text while keeping both strips in native positions.
    strips = [[816,351,1073,2215], [1073,2304,1282,2543]]
    shots = {
        'O1': [{**book, 'mode':'revised_page', 'clip_strips':strips,
                'camera_start_y':1447, 'camera_end_y':1447,
                'scale_start':.395, 'scale_end':.423, 'camera_lock_frame':394}],
        'O2': [{**izumo, 'mode':'revised_page',
                'camera_start_y':izumo['native_crops'][0][1]+950/(2*.395),
                'camera_end_y':790+950/(2*.395),
                'scale_start':.395, 'scale_end':.395, 'camera_lock_frame':271}],
        'O3': [
            {**text,'start_frame':67,'end_frame':116,'frames':49,'highlight_frames':[]},
            {**compass,'start_frame':116,'end_frame':308,'frames':192},
            {**text,'start_frame':308,'end_frame':634,'frames':326,'highlight_frames':[308,483]},
        ],
    }
    for sid in ('O1','O2'):
        shot = shots[sid][0]
        shot['native_crops'] = [camera(shot,n)[1] for n in
                                (shot['start_frame'],shot['camera_lock_frame'])]
        shot['native_max_scale'] = max(shot['scale_start'],shot['scale_end'])
    return shots

def prepare_page(shot):
    plate, art, (left,top) = v01.load_shot({**shot,'mode':'manuscript'})
    if 'clip_strips' in shot:
        clipped=Image.new('RGB',art.size,v01.PAPER)
        for l,t,r,b in shot['clip_strips']:
            box=(l-left,t-top,r-left,b-top)
            clipped.paste(art.crop(box),box[:2])
        art=clipped
    return plate,art,(left,top)

def camera(shot, n):
    start, stop = shot['start_frame'], shot['camera_lock_frame']
    u = min(1,max(0,(n-start)/(stop-start)))
    progress = u*u*(3-2*u)
    scale = shot['scale_start'] + progress*(shot['scale_end']-shot['scale_start'])
    y = shot['camera_start_y'] + progress*(shot['camera_end_y']-shot['camera_start_y'])
    l,_,r,_ = shot['native_clip']
    _,_,_,height = shot['viewport']
    return scale,(l,y-height/(2*scale),r,y+height/(2*scale))

def page_frame(shot, n, loaded):
    plate, art, (left,top) = loaded
    scale, (l,t,r,b) = camera(shot,n)
    x,y,w,h = shot['viewport']
    tile_w = round((r-l)*scale)
    tile = art.transform((tile_w,h),Image.Transform.AFFINE,(1/scale,0,l-left,0,1/scale,t-top),
                         resample=Image.Resampling.BICUBIC,fillcolor=v01.PAPER)
    if n >= shot['highlight_frames'][0]:
        draw = ImageDraw.Draw(tile)
        for x0,y0,x1,y1 in shot['highlight_boxes'][0]:
            draw.rectangle(((x0-l)*scale,(y0-t)*scale,(x1-l)*scale,(y1-t)*scale),
                           outline=RUST,width=2)
    output=plate.copy()
    output.paste(tile,(x+(w-tile_w)//2,y))
    return output

def write_segment(short, shots, pages, path, log):
    sid=short['id']
    headline=Image.open(BASE/f'assets/{sid}_headline.png').convert('RGBA')
    cta=Image.open(BASE/'assets/common_cta.png').convert('RGBA')
    short={**short,'opening_end_frame':REPLACE[sid][0]}
    layers=[(p,Image.open(p['file']).convert('RGBA')) for p in pages]
    cmd=['ffmpeg','-nostdin','-y','-v','warning','-xerror','-f','rawvideo','-pix_fmt','rgb24',
         '-s','1080x1920','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','4',
         '-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p',
         '-vf','scale=out_color_matrix=bt709:out_range=tv','-video_track_timescale','15360',
         '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv',
         '-x264-params','open-gop=0',str(path)]
    with log.open('wb') as err, subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err) as process:
        try:
            for shot in shots:
                revised = shot['mode']=='revised_page'
                loaded = prepare_page(shot) if revised else v01.load_shot(shot)
                for n in range(shot['start_frame'],shot['end_frame']):
                    base = page_frame(shot,n,loaded) if revised else v01.frame(shot,n,loaded,RUST)
                    image = v01.composite(base,n,short,layers,headline,cta)
                    process.stdin.write(image.tobytes())
            process.stdin.close()
            assert process.wait()==0 and log.stat().st_size==0,log.read_text()
        except BaseException:
            process.kill()
            process.wait()
            raise

def assemble(sid, replacement):
    source = video(sid,'v01')
    start,end = REPLACE[sid]
    edges = sorted({0,start,end,COUNTS[sid]})
    cuts = edges[1:-1]
    keys = probe(source,'-select_streams','v:0','-skip_frame','nokey',
                 '-show_frames','-show_entries','frame=pts_time')['frames']
    assert set(cuts) <= {round(float(f['pts_time'])*30) for f in keys}
    work=ROOT/f'_work/{sid}'
    ff(ROOT/f'records/{sid}_split.log','-i',source,'-map','0:v:0','-an','-c','copy','-f','segment',
       '-segment_times',','.join(f'{n/30:.9f}' for n in cuts),'-segment_time_delta','0.016666667',
       '-reset_timestamps',1,'-segment_format_options','video_track_timescale=15360',work/'original_%02d.mp4')
    paths,counts = [],[]
    for i,(first,last) in enumerate(zip(edges,edges[1:])):
        p=replacement if (first,last)==(start,end) else work/f'original_{i:02d}.mp4'
        stream=probe(p,'-select_streams','v:0','-show_streams')['streams'][0]
        assert int(stream['nb_frames'])==last-first,(sid,first,last,stream['nb_frames'])
        paths.append(p)
        counts.append(last-first)
    listing=work/'splice.ffconcat'
    concat(listing,paths,counts)
    ff(ROOT/f'records/{sid}_assemble.log','-f','concat','-safe','0','-i',listing,'-i',source,
       '-map','0:v:0','-map','1:a:0','-c','copy','-bsf:v','setts=pts=PTS:dts=DTS:duration=512',
       '-video_track_timescale','15360','-movflags','+faststart',video(sid,'v02'))

def render():
    captions=v01.read(BASE/'records/caption_manifest.json')
    shorts=v01.read(BASE/'records/shorts.json')['shorts']
    shots=revised_shots(v01.read(BASE/'records/visual_manifest.json')['shots'])
    overlay_files = {Path(page['file']) for page in captions}
    overlay_files.update(BASE/f'assets/{sid}_headline.png' for sid in COUNTS)
    overlay_files.add(BASE/'assets/common_cta.png')
    v01.save(ROOT/'records/overlay_identity.json',dict(
        v01_caption_manifest_sha256=v01.sha(BASE/'records/caption_manifest.json'),
        v02_caption_manifest_sha256=v01.sha(ROOT/'records/caption_manifest.json'),
        caption_pages=len(captions), all_layers_read_directly_from_v01=True,
        overlay_sha256={p.name:v01.sha(p) for p in sorted(overlay_files)}))
    v01.save(ROOT/'records/revised_shots.json',shots)
    for short in shorts:
        sid=short['id']
        assert short['frames']==COUNTS[sid] and short['cta_start_frame']==COUNTS[sid]-75
        assert v01.sha(video(sid,'v01'))==SOURCES[sid]
        pages=[p for p in captions if p['short_id']==sid]
        assert set(CAPTION_CHANGES[sid])<={p['start_frame'] for p in pages}
        work=ROOT/f'_work/{sid}'
        work.mkdir(parents=True,exist_ok=True)
        part=work/'replacement.mp4'
        write_segment(short,shots[sid],pages,part,ROOT/f'records/{sid}_encode.log')
        assemble(sid,part)
        print('RENDERED',sid,flush=True)

def comparison_indices(sid):
    if sid=='O1':
        return [112,*range(120,481,30),394,502,503]
    if sid=='O2':
        return [222,*range(240,571,30),271,509,583]
    return [0,66,67,115,116,159,307,308,482,483,559,633]

def extract(path, frames):
    test='+'.join(f'eq(n,{n})' for n in frames)
    cmd=['ffmpeg','-nostdin','-v','warning','-xerror','-i',str(path),'-an',
         '-vf',f"select='{test}',{FMT}",'-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-']
    # Decode the full stream but return RGB only for the selected frames.
    result={}
    with subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as process:
        for frame in frames:
            data=process.stdout.read(RAW_RGB)
            assert len(data)==RAW_RGB,(path,frame,process.stderr.read())
            image=Image.frombytes('RGB',(1080,1920),data)
            image.thumbnail((600,1067),Image.Resampling.LANCZOS)
            result[frame]=image
        assert not process.stdout.read(1)
        assert process.wait()==0 and not process.stderr.read()
    return result

def compare(sid):
    frames=sorted(set(comparison_indices(sid)))
    a=extract(video(sid,'v01'),frames)
    b=extract(video(sid,'v02'),frames)
    folder=ROOT/f'review/{sid}'
    folder.mkdir(exist_ok=True)
    for frame in frames:
        sheet=Image.new('RGB',(1200,a[frame].height+27),'#0c1820')
        sheet.paste(a[frame],(0,27))
        sheet.paste(b[frame],(600,27))
        draw=ImageDraw.Draw(sheet)
        for x,version in [(7,'v01'),(607,'v02')]:
            draw.text((x,7),f'{sid}  {version}  {frame/30:.3f}s  frame {frame}',fill='white')
        sheet.save(folder/f'{frame:04}.jpg',quality=91,optimize=True)
    return frames

def audio_packets(path):
    return probe(path,'-select_streams','a:0','-show_packets','-show_data_hash','sha256',
                 '-show_entries','packet=pts,dts,duration,size,data_hash')['packets']

def verify():
    results=[]
    for sid,frames in COUNTS.items():
        source,target=video(sid,'v01'),video(sid,'v02')
        assert v01.sha(source)==SOURCES[sid]
        hashes=[framehash(p,ROOT/f'records/{sid}_{version}.framemd5')
                for p,version in [(source,'v01'),(target,'v02')]]
        before,after=hashes
        assert len(before)==len(after)==frames
        start,end=REPLACE[sid]
        assert before[:start]==after[:start] and before[end:]==after[end:]
        assert all(a!=b for a,b in zip(before[start:end],after[start:end]))
        old_audio,new_audio=audio_packets(source),audio_packets(target)
        assert old_audio==new_audio,(sid,len(old_audio),len(new_audio))
        audio_sha=[subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(path),
                    '-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
                   for path in (source,target)]
        assert audio_sha[0]==audio_sha[1]
        ff(ROOT/f'records/{sid}_continuous_decode.log','-i',target,'-map','0:v:0','-map','0:a:0',
           '-f','null','-')
        old=probe(source,'-show_streams','-show_format')
        new=probe(target,'-show_streams','-show_format')
        duration = float(new['format']['duration'])
        assert duration == float(old['format']['duration']) <= 24
        v,a=new['streams']
        assert (v['codec_name'],v['profile'],v['width'],v['height'],v['pix_fmt'],
                v['avg_frame_rate'],v['time_base'],int(v['nb_frames']),v['color_space'])==(
                'h264','High',1080,1920,'yuv420p','30/1','1/15360',frames,'bt709')
        assert (a['codec_name'],a['sample_rate'],a['channels'])==('aac','48000',2)
        pts=probe(target,'-select_streams','v:0','-show_packets','-show_entries','packet=pts,duration')['packets']
        assert sorted(p['pts'] for p in pts)==list(range(0,frames*512,512))
        assert all(p['duration']==512 for p in pts)
        stills=compare(sid)
        results.append(dict(id=sid,filename=target.name,sha256=v01.sha(target),size=target.stat().st_size,
            duration_seconds=frames/30,container_duration_seconds=duration,frames=frames,
            video='H.264 High / 1080x1920 / yuv420p / BT.709 / 30 fps',audio='AAC 48 kHz stereo',
            replaced_interval=[start,end],replaced_frames=end-start,unchanged_frames=frames-(end-start),
            frame_md5_equal_outside_replacement=True,continuous_decode_warnings=0,
            audio_sha256=audio_sha[0],aac_packets_with_timestamps_equal=len(new_audio),comparison_frames=stills))
        print('VERIFIED',sid,results[-1]['unchanged_frames'],'unchanged frames',flush=True)
    v01.save(ROOT/'records/final_qc.json',results)

def package():
    assert len(v01.read(ROOT/'records/final_qc.json'))==3
    path=ROOT/'deliverables/EP014_shorts_QA_v02.zip'
    with ZipFile(path,'w',compression=ZIP_DEFLATED) as archive:
        archive.write(REQUEST,'request.md')
        for directory in ('records','review'):
            for item in sorted((ROOT/directory).rglob('*')):
                if item.is_file():
                    archive.write(item,item.relative_to(ROOT))
    with ZipFile(path) as archive:
        assert archive.testzip() is None

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['render','verify','package'])
    stage=parser.parse_args().stage
    assert SSD.is_mount()
    for directory in ('records','review','deliverables'):
        (ROOT/directory).mkdir(parents=True,exist_ok=True)
    for name in ('caption_manifest.json','cta_design.json','headlines.json','shorts.json','card_texts.json'):
        data=(BASE/'records'/name).read_bytes()
        destination=ROOT/'records'/name
        if destination.exists():
            assert destination.read_bytes()==data
        else:
            destination.write_bytes(data)
    globals()[stage]()

if __name__=='__main__':
    main()
