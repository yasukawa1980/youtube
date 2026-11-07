"""EP013 v02：承認された画角3点と家族アルバムカード。v01音声・字幕を再利用。"""
import ast
import copy
import math
import shutil
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import wom_shorts_ep013 as base

OLD = base.ROOT
ROOT = OLD.parent/'EP013_v02_20261108'
REPO = Path(__file__).resolve().parent
REQUEST = base.REQUEST
read, save, sha, guard = base.read, base.save, base.sha, base.guard
REQUESTED = {'V01_left':[0,4400,2400,6511], 'V01_girl':[3600,7000,5500,8671],
             'V01_claws':[3850,7720,4930,8670]}

def configure():
    base.ROOT = ROOT
    return base.helper()

def album():
    code=(REPO/'wom13_scenes.py').read_text()
    node=next(n for n in ast.parse(code).body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ALBUM' for t in n.targets))
    quotes=ast.literal_eval(node.value)
    header=['TITLE CARD｜文字カード',
        'Banninck Cocq family album — caption, as transcribed in Oud Holland, 1886, p.204',
        'バニング・コック家のアルバムの説明（1886年の翻刻）']
    assert all(t in code for t in header+quotes)
    im=Image.new('RGB',(1080,1920),'#e8d9b7');d=ImageDraw.Draw(im);rows=[];blocks=[]
    sans='/System/Library/Fonts/Supplemental/Arial.ttf'
    serif='/System/Library/Fonts/Supplemental/Georgia.ttf'
    jp='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
    def block(text,y,size,face,lineheight,japanese=False):
        f=ImageFont.truetype(face,size);tokens=list(text) if japanese else text.split(' ');sep='' if japanese else ' '
        lines=[];line=''
        for token in tokens:
            test=line+sep+token if line else token
            if f.getlength(test)>960 and line:lines.append(line);line=token
            else:line=test
        if line:lines.append(line)
        assert sep.join(lines)==text
        blocks.append(dict(text=text,lines=lines,exact_text=True))
        for line in lines:
            bb=f.getbbox(line);w=bb[2]-bb[0];h=bb[3]-bb[1];x=(1080-w)//2
            assert w<=980 and y+h<1140
            assert not line.endswith(('｜','·'))
            d.text((x-bb[0],y-bb[1]),line,font=f,fill='#3b2c21')
            rows.append(dict(text=line,bbox=[x,y,x+w,y+h],font_size=size,font=face));y+=lineheight
    block(header[0],140,22,jp,30,True)
    block(header[1],185,26,sans,35)
    block(header[2],285,24,jp,34,True)
    block(quotes[0],370,40,serif,52)
    block(quotes[1],710,34,serif,45)
    block(quotes[2],900,30,jp,42,True)
    assert max(r['bbox'][3] for r in rows)<1030, '登録案内の上端より上へ収める'
    path=ROOT/'assets/D_album_s_source.png';im.save(path)
    return dict(file=str(path),texts=rows,main_texts=header+quotes,blocks=blocks,
                exact_text_verified=True,main_source='wom13_scenes.py:ALBUM / D_album',
                source_sha256=sha(REPO/'wom13_scenes.py'))

def prepare():
    guard()
    for d in ['records','assets','audio','review','deliverables','_work/tmp']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    shutil.copy2(REQUEST,ROOT/'records/request.md')
    unchanged=[]
    for name in ['shorts.json','narration.json','audio_qc.json','caption_manifest.json','cta_design.json','headlines.json']:
        shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
        assert sha(OLD/'records'/name)==sha(ROOT/'records'/name)
    for sid in ['V1','V2','V3']:
        for suffix in ['native.wav','final.m4a']:
            src=OLD/f'audio/{sid}_{suffix}';dst=ROOT/f'audio/{sid}_{suffix}'
            shutil.copy2(src,dst);assert sha(src)==sha(dst)
            unchanged.append(dict(source=str(src),copy=str(dst),sha256=sha(src)))
        shutil.copy2(OLD/f'assets/{sid}_headline.png',ROOT/f'assets/{sid}_headline.png')
    shutil.copy2(OLD/'assets/common_cta.png',ROOT/'assets/common_cta.png')
    caps=read(ROOT/'records/caption_manifest.json')
    for c in caps:unchanged.append(dict(layer=c['file'],sha256=sha(Path(c['file'])),start_frame=c['start_frame'],end_frame=c['end_frame']))
    save(ROOT/'records/unchanged_inputs.json',dict(files=unchanged,caption_manifest_sha256=sha(OLD/'records/caption_manifest.json'),
         shorts_sha256=sha(OLD/'records/shorts.json'),no_voice_regeneration=True,no_caption_regeneration=True))
    manifest=read(OLD/'records/visual_manifest.json');layout=[]
    for g in manifest['shots']:
        key=g['asset_id']
        if key not in REQUESTED:continue
        box=REQUESTED[key];w=box[2]-box[0];cy=(box[1]+box[3])/2
        vp=g['viewport'];height=w*vp[3]/vp[2]
        adjusted=[box[0],cy-height/2,box[2],cy+height/2]
        base.REGIONS[key]=('V01',adjusted)
        im=base.prepared_art(key);path=ROOT/f'assets/{key}_source.png';im.save(path)
        z=g['zoom_end'];cx=(box[0]+box[2])/2
        end=[cx-w/z/2,cy-height/z/2,cx+w/z/2,cy+height/z/2]
        g.update(file=str(path),native_crop_start=adjusted,native_crop_end=end,display_size=vp[2:],
            prepared_size=list(im.size),native_max_scale=vp[2]/w*z,crop_start=[0,0,*im.size],crop_end=[0,0,*im.size],foreground_height_fraction=vp[3]/1920)
        g['source']['native_box']=adjusted
        assert g['native_max_scale']<=1
        layout.append(dict(asset=key,requested_box=box,adjusted_box=adjusted,viewport=vp,native_max_scale=g['native_max_scale'],
            note='実際の既存絵枠1000×900に合わせ、指定範囲の中心と幅を維持して上下だけ調整。'))
    girl=base.REGIONS['V01_girl'][1];claws=base.REGIONS['V01_claws'][1]
    assert girl[0]<=claws[0]<claws[2]<=girl[2] and girl[1]<=claws[1]<claws[3]<=girl[3]
    for a,b in [('V01_D1','V01_left'),('V01_D1','V01_girl'),('V01_left','V01_girl')]:
        p=base.REGIONS[a][1];q=base.REGIONS[b][1]
        assert max(0,min(p[2],q[2])-max(p[0],q[0]))*max(0,min(p[3],q[3])-max(p[1],q[1]))==0
    carddata=read(OLD/'records/card_texts.json');carddata['D_album_s']=album();save(ROOT/'records/card_texts.json',carddata)
    old,helper=configure();s=read(ROOT/'records/shorts.json')['shorts'][0]
    start=old.phrase_frame(s,'An early description')
    preceding=next(g for g in manifest['shots'] if g['asset_id']=='D_1797s')
    new=copy.deepcopy(preceding);preceding.update(end_frame=start,frames=start-preceding['start_frame'])
    new.update(asset_id='D_album_s',start_frame=start,frames=new['end_frame']-start,
               cut_phrase='An early description',file=carddata['D_album_s']['file'])
    manifest['shots'].insert(manifest['shots'].index(preceding)+1,new)
    save(ROOT/'records/visual_manifest.json',manifest);save(ROOT/'records/layout_v02.json',dict(crops=layout,album_start_frame=start,album_start_seconds=start/30))
    for s in read(ROOT/'records/shorts.json')['shorts']:
        for g in [g for g in manifest['shots'] if g['short_id']==s['id']]:
            for n in [g['start_frame'],g['end_frame']-1]:
                im=helper.design_frame(s,n,manifest['shots'],caps,base.frame_art);im.thumbnail((720,1280));im.save(ROOT/f'review/{s["id"]}_{n:04}_design.jpg',quality=90)
    print('準備完了',json_summary(layout,start),flush=True)

def json_summary(layout,start):
    return dict(crops=layout,album_start_seconds=start/30,mac_free_mib=shutil.disk_usage('/').free/1024**2)

def render():
    old,_=configure();old.frame_art=base.frame_art
    for sid in ['V1','V2','V3']:
        guard();old.render([sid],version='v02',prefix='QO_short_EP013')

def qc():
    configure()
    import wom_shorts_ep013_qc as check
    check.ROOT=ROOT
    check.audit(version='v02',expected_shots=9)
    comparisons=[]
    for sid in ['V1','V2','V3']:
        before=OLD/f'deliverables/QO_short_EP013_{sid}_v01.mp4';after=ROOT/f'deliverables/QO_short_EP013_{sid}_v02.mp4'
        hashes=[check.stream_hash(p) for p in [before,after]];assert hashes[0]==hashes[1]
        pcm=[]
        for p in [before,after]:
            pcm.append(subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(p),'-map','0:a:0','-c:a','pcm_s16le','-f','hash','-hash','sha256','-'],text=True).strip())
        assert pcm[0]==pcm[1]
        comparisons.append(dict(id=sid,aac_sha256=hashes[0],pcm_sha256=pcm[0],aac_identical=True,pcm_identical=True))
    save(ROOT/'records/audio_v01_v02_comparison.json',comparisons)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render','qc']);args=p.parse_args();globals()[args.stage]()
