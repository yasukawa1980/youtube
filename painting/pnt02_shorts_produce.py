"""PNT02 approved shorts, using the EP013 v02 typography/audio/render helpers."""
import ast
import json
import math
import re
import shutil
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pnt02_shorts_preflight import ROOT, MAIN, MEDIA, REPO, REGIONS, guard, save, sha
sys.path.insert(0, str(REPO/'new-channel'))
REQUEST = ROOT/'records/request.md'
read = lambda p: json.loads(Path(p).read_text())
LINES = {
 'V1': "A soldier raises | the Stars and Stripes. / The crossing was in December | seventeen seventy-six. / Only in June | seventeen seventy-seven / did Congress resolve / that the flag would have / thirteen stripes | and thirteen stars. / Which flag, if any, | was carried is not known.",
 'V2': "This painting | of an American moment / was made in Germany. / Its painter, Emanuel Leutze, / studied in Düsseldorf. / He began the first version there / in eighteen forty-nine, / soon after revolutions / swept across Europe / in eighteen forty-eight.",
 'V3': "Who posed for Washington | in this painting? / Worthington Whittredge recalled / that he posed for the man | steering the boat, / and again for Washington himself. / For Washington's head, / Leutze is said to have looked / to a sculpture by Houdon."
}
PAGES = {sid:[[t.strip() for t in p.split('|')] for p in text.split('/')] for sid,text in LINES.items()}
HEADLINES = {'V1':["THIS FLAG WASN'T",'OFFICIAL YET?'], 'V2':['PAINTED IN','GERMANY?'], 'V3':['WHO POSED','AS WASHINGTON?']}
SPECS = {'V1':[('V1_flag',None),('D_resolution_s','Only in June')],
         'V2':[('V2_full',None),('D_leutze_s','Its painter'),('V10','soon after revolutions')],
         'V3':[('V3_steering',None),('V3_Washington','and again for Washington himself')]}
INK='#3b2c21'; PAPER='#e8d9b7'
JP='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
SANS='/System/Library/Fonts/Supplemental/Arial.ttf'
SERIF='/System/Library/Fonts/Supplemental/Georgia.ttf'

def helper():
    guard()
    import wom_shorts_remake as config
    config.ROOT=ROOT;config.REQUEST=REQUEST
    import wom_shorts_remake_produce as old
    old.ROOT=ROOT;old.REQUEST=REQUEST;old.BIN='/opt/homebrew/bin/ffmpeg'
    import wom_shorts_ep010 as layout
    layout.ROOT=ROOT
    return old,layout

def captions():
    guard()
    nar=read(ROOT/'records/narration.json')
    assert nar['all_within_24_seconds'] and nar['completed_count']==3
    for s in nar['scripts']:
        s['final_duration_seconds']=s['planned_duration_seconds'];s['frames']=s['planned_frames']
        assert ' '.join(' '.join(ls) for ls in PAGES[s['id']])==s['text']
    save(ROOT/'records/narration.json',nar)
    for d in ['assets','review','deliverables','_work']:(ROOT/d).mkdir(exist_ok=True)
    old,_=helper();old.CAPTIONS={sid:[' '.join(ls) for ls in pages] for sid,pages in PAGES.items()}
    old.EPISODES={sid:'PNT02' for sid in PAGES};old.captions()

def audio():
    old,_=helper()
    old.audio(bgm_sources={'PNT02':MAIN/'en/audio/common_selected_bgm.wav'},bgm_start_seconds=100)

def wrap(text,size,face,maxw=960):
    font=ImageFont.truetype(face,size);sep='' if face==JP else ' ';tokens=list(text) if face==JP else text.split(' ')
    lines=[];line=''
    for token in tokens:
        candidate=line+sep+token if line else token
        if font.getlength(candidate)>maxw and line:
            if line.endswith(('·','｜')):
                token=line[-1]+sep+token;line=line[:-1].rstrip()
            lines.append(line);line=token
        else:line=candidate
    if line:lines.append(line)
    assert sep.join(lines)==text
    return lines

def block(im,text,y,size,face,lineheight,rows,blocks):
    lines=wrap(text,size,face);font=ImageFont.truetype(face,size);d=ImageDraw.Draw(im)
    for line in lines:
        assert not line.endswith(('·','｜'))
        bb=font.getbbox(line);w=bb[2]-bb[0];h=bb[3]-bb[1];x=(1080-w)//2
        assert w<=980 and y+h<1030,(line,y+h)
        d.text((x-bb[0],y-bb[1]),line,font=font,fill=INK)
        rows.append(dict(text=line,bbox=[x,y,x+w,y+h],font_size=size,font=face,foreground=INK,background=PAPER))
        y+=lineheight
    blocks.append(dict(text=text,lines=lines,exact_text=True))
    return y

def cards():
    import pnt02_scenes as scene
    code=(REPO/'painting/pnt02_scenes.py').read_text()
    specs={
      'D_resolution_s':[
       ('TITLE CARD｜文字カード',140,22,JP,30),
       ('Resolution of the Continental Congress, 14 June 1777 — as quoted by the U.S. National Archives',185,27,SANS,36),
       ('大陸会議の決議（1777年6月14日）',300,25,JP,36),
       (scene.RESOLUTION[0],390,43,SERIF,60),
       (scene.RESOLUTION[1],820,30,JP,44)],
      'D_leutze_s':[
       ('TITLE CARD｜文字カード',140,22,JP,30),('Emanuel Leutze',190,40,SERIF,50),
       ('U.S. Department of State · Smithsonian American Art Museum',255,26,SANS,36),
       ('1816',360,64,SERIF,75),('Schwäbisch Gmünd, Württemberg',445,36,SERIF,48),
       ('1816年 ドイツ・シュヴェービッシュ・グミュント',500,26,JP,36),
       ('1825',590,64,SERIF,75),('United States',675,36,SERIF,48),('1825年 アメリカへ',730,26,JP,36),
       ('1841',820,64,SERIF,75),('Düsseldorf',905,36,SERIF,48),('1841年 デュッセルドルフ',960,26,JP,36)]}
    out={}
    for key,items in specs.items():
        im=Image.new('RGB',(1080,1920),PAPER);rows=[];blocks=[]
        for text,y,size,face,lh in items:
            assert text in code,text
            block(im,text,y,size,face,lh,rows,blocks)
        path=ROOT/f'assets/{key}_source.png';im.save(path)
        out[key]=dict(file=str(path),texts=rows,blocks=blocks,main_texts=[x[0] for x in items],exact_text_verified=True,
                      source='painting/pnt02_scenes.py',source_sha256=sha(REPO/'painting/pnt02_scenes.py'))
    save(ROOT/'records/card_texts.json',out);return out

def frame_art(g,frac,loaded):
    guard();im,bg,head=loaded;x,y,w,h=g['viewport'];z=math.exp(math.log(g['zoom_end'])*frac)
    cw,ch=im.width/z,im.height/z
    rect=((im.width-cw)/2,(im.height-ch)/2,(im.width+cw)/2,(im.height+ch)/2)
    size=g['display_size'];crop=im.resize(tuple(size),Image.Resampling.LANCZOS,box=rect)
    frame=bg.copy();frame.paste(crop,(x+(w-size[0])//2,y+(h-size[1])//2))
    return Image.alpha_composite(frame.convert('RGBA'),head)

def visuals():
    old,layout=helper();carddata=cards();shorts=read(ROOT/'records/shorts.json')['shorts'];caps=[];heads=[];shots=[]
    layout.text_asset('common','cta',[])
    maincode=(REPO/'painting/pnt02_scenes.py').read_text()
    for s in shorts:
        sid=s['id'];hp,hr=layout.text_asset(sid,'headline',HEADLINES[sid]);heads.append(dict(id=sid,file=str(hp),rows=hr))
        for j,(g,lines) in enumerate(zip(s['caption_groups'],PAGES[sid])):
            p,rows=layout.text_asset(sid,f'caption{j:02}',lines)
            caps.append(dict(short_id=sid,page=j,**g,lines=lines,file=str(p),rows=rows))
        starts=[0 if cue is None else old.phrase_frame(s,cue) for key,cue in SPECS[sid]]
        for j,(key,cue) in enumerate(SPECS[sid]):
            end=starts[j+1] if j+1<len(starts) else s['frames'];static=key in carddata
            box=None;source={};texts=[];z=1;scale=0
            if static:
                im=Image.open(carddata[key]['file']).convert('RGB');viewport=[0,0,1080,1920];size=[1080,1920]
            else:
                if key in REGIONS:
                    aid,filename,box=REGIONS[key];path=MEDIA/'Met_97.34'/filename
                elif key=='V2_full':
                    path=MEDIA/'Met_97.34/DP-14511-001.jpg';box=[650,130,3150,2329]
                else:path=MEDIA/'SMB_3964830/smb3964830.jpg'
                with Image.open(path) as raw:
                    if box is None:box=[0,0,*raw.size]
                    assert 0<=box[0]<box[2]<=raw.width and 0<=box[1]<box[3]<=raw.height
                    im=raw.convert('RGB').crop(box)
                viewport=[0,270,1080,950];z=1.04
                factor=min(viewport[2]/im.width,viewport[3]/im.height)
                size=[round(im.width*factor),round(im.height*factor)]
                scale=max(size[0]/im.width,size[1]/im.height)*z;assert scale<=1,'STOP: 原寸超過'
                if key=='V10':texts=['PRINT｜版画','Des Deutschen Vaterland von Moritz Arndt · 1848','Staatliche Museen zu Berlin, Kunstbibliothek · 1900,682 · PDM 1.0 · Photo: Dietmar Katz']
                else:texts=['PAINTING｜絵画' if key=='V2_full' else 'DETAIL｜部分',
                  'Emanuel Leutze · Washington Crossing the Delaware · 1851' if key=='V2_full' else 'Washington Crossing the Delaware · 1851',
                  'The Metropolitan Museum of Art · 97.34 · Public Domain / Open Access, CC0']
                assert all(t in maincode for t in texts)
                source=dict(original_file=str(path),sha256=sha(path),native_box=box,label=texts[0],texts=texts)
            path=ROOT/f'assets/{key}_source.png';im.save(path)
            bgpath=ROOT/f'assets/{key}_bg.jpg';Image.new('RGB',(1080,1920),PAPER).save(bgpath,quality=95)
            header=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(header);hr=[];y=130
            for k,text in enumerate([] if static else ['QUIET ORIGINS',*texts]):
                face=JP if '｜' in text else SANS;f=ImageFont.truetype(face,20 if k<2 else 19)
                for line in wrap(text,f.size,face,940):
                    d.text((65,y),line,font=f,fill=INK);bb=list(d.textbbox((65,y),line,font=f));assert bb[3]<270
                    hr.append(dict(text=line,bbox=bb,font_size=f.size,font=face,foreground=INK,background=PAPER));y+=24
            hpath=ROOT/f'assets/{key}_header.png';header.save(hpath)
            final=None
            if box:
                l,t,r,b=box;cx=(l+r)/2;cy=(t+b)/2;final=[cx-(r-l)/z/2,cy-(b-t)/z/2,cx+(r-l)/z/2,cy+(b-t)/z/2]
            shots.append(dict(short_id=sid,asset_id=key,source=source,start_frame=starts[j],end_frame=end,frames=end-starts[j],
               cut_phrase=cue,file=str(path),background=str(bgpath),header=str(hpath),header_texts=hr,viewport=viewport,
               display_size=size,prepared_size=list(im.size),native_crop_start=box,native_crop_end=final,
               zoom_end=z,native_max_scale=scale,static=static))
    save(ROOT/'records/visual_manifest.json',dict(shots=shots,no_AI=True,no_color_correction=True,overlap_record='crop_preflight.json',
         crop_adjustments='None. Aspect-preserving fit to 1080x950; <=1px letterbox for approved details. V2 full view centrally cropped around boat.'))
    save(ROOT/'records/caption_manifest.json',caps);save(ROOT/'records/headlines.json',heads)
    for s in shorts:
        for n in sorted(set([0,15,30,45,60,75,s['cta_start_frame']]+[g['start_frame'] for g in shots if g['short_id']==s['id']]+[g['end_frame']-1 for g in shots if g['short_id']==s['id']])):
            im=layout.design_frame(s,n,shots,caps,frame_art);im.thumbnail((540,960));im.save(ROOT/f'review/{s["id"]}_{n:04}_design.jpg',quality=90)
    print('VISUALS',len(shots),'shots',len(caps),'caption pages',flush=True)

def render():
    review=read(ROOT/'records/visual_review.json')
    assert review['passed'], 'STOP: 指定範囲の目視確認が不合格。範囲修正前に書き出さない。'
    assert review['visual_manifest_sha256']==sha(ROOT/'records/visual_manifest.json')
    old,_=helper();old.frame_art=frame_art
    old.render(['V1','V2','V3'],version='v01',prefix='QO_short_PNT02')

if __name__=='__main__':globals()[sys.argv[1]]()
