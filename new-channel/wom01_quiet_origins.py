"""v05 picture-only revision. Requires a new WOM_EPISODE_ROOT and v04 previous root.

Stages: prepare, visuals, pictures, package, layout. Never regenerates audio/SRT.
Layout checks use imageio-ffmpeg's libass, independently of production FFmpeg.
"""
import argparse, json, os, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from wom01_multilingual_render import read, save, sha, ff, probe
from wom01_refine_av import pictures
import wom01_multilingual_visuals as visuals

def stream_hash(path, stream):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map',f'0:{stream}:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def prepare(root, previous):
    assert root != previous and not root.exists(), 'Use a new output folder'
    for d in ['records','deliverables','review','assets','_work/render']:
        (root/d).mkdir(parents=True,exist_ok=True)
    for n in ['content.json','content_en.json','master_timeline.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_cues_en.json','subtitle_cues_ja.json','audio_qc.json']:
        shutil.copy2(previous/'records'/n,root/'records'/n)
    for lang in ['en','ja']:
        for n in [f'EP001_audio_{lang}.m4a',f'EP001_字幕_{lang}.srt']:
            shutil.copy2(previous/'deliverables'/n,root/'deliverables'/n)
    save(root/'records/revision_request.json',{'version':'v05','brand':'Quiet Origins','source_root':str(previous),'audio_regenerated':False,'subtitles_regenerated':False,'subtitles_burned_in':False,'compact_cards':True,'japanese_screen_credit':'VOICEVOX:冥鳴ひまり','historical_v04_preserved':True})

def package(root, previous):
    shots=read(root/'records/render_shots.json');oldshots=read(previous/'records/render_shots.json')
    assert len(shots)==len(oldshots)==55
    for shot,oldshot in zip(shots,oldshots):
        assert all(shot[k]==oldshot[k] for k in ['segment_id','key','start','end','frames'])
        stamp=read((root/shot['encoded_file']).with_suffix('.json'))
        assert stamp['image_sha256']==sha(root/shot['file'])
        assert stamp['frames']==shot['frames'] and stamp['crf']==18
    raw=root/'_work/picture_master.mp4';picture=root/'_work/picture_cfr.mp4'
    # MP4 format durations are rounded to milliseconds. Supplying the exact
    # frame duration prevents those rounding errors accumulating across 55 cuts.
    concat=root/'_work/concat_exact_v05.txt'
    concat.write_text(''.join(f"file '{root/s['encoded_file']}'\nduration {s['frames']/30:.9f}\n" for s in shots))
    ff(['-f','concat','-safe',0,'-i',concat,'-c','copy','-movflags','+faststart',raw])
    assert probe(raw)['streams'][0]['time_base']=='1/15360'
    ff(['-i',raw,'-map','0:v:0','-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movflags','+faststart',picture])
    files=[]
    for lang in ['en','ja']:
        stem=f'EP001_Anubis_{lang}_v05_1080p30';out=root/f'deliverables/{stem}.mp4'
        old=previous/f'deliverables/EP001_Anubis_{lang}_v04_1080p30.mp4'
        srt=root/f'deliverables/{stem}.srt';shutil.copy2(root/f'deliverables/EP001_字幕_{lang}.srt',srt)
        assert sha(srt)==sha(previous/f'deliverables/EP001_Anubis_{lang}_v04_1080p30.srt')
        ff(['-i',picture,'-i',root/f'deliverables/EP001_audio_{lang}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn'),'-metadata','title=Quiet Origins / EP001 — Anubis','-metadata','comment=Japanese narration: VOICEVOX:冥鳴ひまり; English narration: Kokoro / Heart (af_heart); external subtitles','-movflags','+faststart',out])
        ff(['-i',out,'-f','null','-']);info=probe(out)
        assert [s['codec_type'] for s in info['streams']]==['video','audio']
        assert info['streams'][0]['avg_frame_rate']=='30/1' and int(info['streams'][0]['nb_frames'])==20481
        assert float(info['format']['duration'])==682.7
        ah=stream_hash(out,'a');assert ah==stream_hash(old,'a')
        pts=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(out)],text=True)
        assert sorted(int(x) for x in pts.splitlines())==list(range(0,20481*512,512))
        files.append({'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'video_stream_hash':stream_hash(out,'v'),'audio_stream_hash':ah,'audio_matches_v04':True,'srt_sha256':sha(srt),'srt_matches_v04':True,'full_decode':'pass','exact_30fps_pts':True,'probe':info})
        print('PACKAGED',lang,flush=True)
    assert files[0]['video_stream_hash']==files[1]['video_stream_hash']
    save(root/'records/qc_v05.json',{'version':'v05','brand':'Quiet Origins','duration_seconds':682.7,'frames':20481,'fps':30,'subtitles_burned_in':False,'human_full_listening':False,'files':files})
    shutil.copy2(previous/'deliverables/VOICE_CREDITS.txt',root/'deliverables/VOICE_CREDITS.txt')

def validate_brand(root, previous):
    manifest=read(root/'records/visual_manifest.json');checks=[];header=None;maximum=0
    for s in manifest['shots']:
        a=np.array(Image.open(root/s['file']));b=np.array(Image.open(previous/s['file']))
        h=a[20:65,90:670]
        if header is None:header=h
        assert np.array_equal(h,header)
        card=s['label'] in ['Concept diagram','Production credits']
        bottom=None
        if not card:assert np.array_equal(a[75:],b[75:])
        else:
            mask=(a[220:940,:,0]>140)&(a[220:940,:,1]>140)&(a[220:940,:,2]>80)
            bottom=int(np.where(mask)[0].max())+220;maximum=max(maximum,bottom)
            assert bottom<=760,(s['key'],bottom)
        checks.append({'file':s['file'],'brand_header_matches':True,'unchanged_below_brand':not card,'card_text_bottom_px':bottom})
    assert len(checks)==55 and sum(x['unchanged_below_brand'] for x in checks)==41
    save(root/'records/brand_layout_validation.json',{'brand':'QUIET ORIGINS','all_55_header_pixels_identical':True,'photo_facsimile_reconstruction_41_unchanged_below_y75':True,'card_text_bottom_max':maximum,'shots':checks})
    print('BRAND',len(checks),'shots, card text y <=',maximum,flush=True)

def layout(root):
    import imageio_ffmpeg
    binary=imageio_ffmpeg.get_ffmpeg_exe();shots=read(root/'records/render_shots.json')
    folder=root/'review/libass';folder.mkdir(exist_ok=True)
    checks=[];tiles={14:[],26:[]}
    for label in ['AI reconstruction','Museum object','Facsimile (copy on paper)','Concept diagram','Production credits','Concept diagram (boxes)']:
        shot=next(s for s in shots if s['key']=='evidence') if label=='Concept diagram (boxes)' else next(s for s in shots if s['label']==label)
        for lang in ['en','ja']:
            # Choose a two-line cue when one exists, within this exact shot.
            srt=root/f'deliverables/EP001_Anubis_{lang}_v05_1080p30.srt'
            cues=[]
            for block in srt.read_text().strip().split('\n\n'):
                lines=block.splitlines()
                def sec(s):
                    h,m,x=s.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(x)
                a,b=map(sec,lines[1].split(' --> '))
                t=max(a,shot['start'])+.15
                if t<min(b,shot['end'])-.05:cues.append((len(lines[2:]),t,int(lines[0])))
            _,t,cue=max(cues)
            video=root/f'deliverables/EP001_Anubis_{lang}_v05_1080p30.mp4'
            prefix=f'{shot["key"]}_{lang}'
            base=folder/f'{prefix}_base.png'
            cmd=[binary,'-v','warning','-y','-ss',str(t),'-copyts','-i',str(video)]
            subprocess.run(cmd+['-frames:v','1',str(base)],check=True,capture_output=True)
            a=np.array(Image.open(base).convert('RGB'))
            for size in [14,26]:
                dest=folder/f'{prefix}_{size}.png'
                filt=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize={size},BorderStyle=3,MarginV=12'"
                result=subprocess.run(cmd+['-vf',filt,'-frames:v','1',str(dest)],check=True,capture_output=True,text=True)
                b=np.array(Image.open(dest).convert('RGB'));mask=np.max(np.abs(a.astype(int)-b.astype(int)),axis=2)>8
                yy,xx=np.where(mask);assert len(yy)>0
                bbox=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]
                assert bbox[1]>760,(prefix,size,bbox)
                checks.append({'label':label,'language':lang,'time_seconds':t,'cue':cue,'font_size':size,'subtitle_bbox':bbox,'actual_libass_render':True,'image':str(dest.relative_to(root)),'warnings':result.stderr})
                tile=Image.open(dest).convert('RGB');tile.thumbnail((640,360))
                canvas=Image.new('RGB',(640,390),'#15242c');canvas.paste(tile,(0,30))
                ImageDraw.Draw(canvas).text((10,8),f'{label} / {lang} / FontSize={size}',fill='white')
                tiles[size].append(canvas)
    for size,items in tiles.items():
        sheet=Image.new('RGB',(1280,2340))
        for i,im in enumerate(items):sheet.paste(im,((i%2)*640,(i//2)*390))
        sheet.save(root/f'review/libass_{size}.jpg',quality=88)
    save(root/'records/libass_validation.json',{'binary':binary,'checks':checks,'note':'Actual MP4 + SRT rendered with libass, not player screenshots. Visual review of these images is separate.'})
    print('LIBASS',len(checks),'checks',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','visuals','pictures','package','layout']);args=p.parse_args()
    root=Path(os.environ['WOM_EPISODE_ROOT']);previous=Path(os.environ['WOM_PREVIOUS_ROOT'])
    os.environ.update(WOM_SUBTITLE_SAFE='1',WOM_COMPACT_CARDS='1',WOM_VIDEO_CRF='18')
    assert os.environ['WOM_BRAND']=='Quiet Origins'
    if args.stage=='prepare':prepare(root,previous)
    elif args.stage=='visuals':
        visuals.main()
        validate_brand(root,previous)
    elif args.stage=='pictures':pictures(root)
    elif args.stage=='package':package(root,previous)
    elif args.stage=='layout':layout(root)
if __name__=='__main__':main()
