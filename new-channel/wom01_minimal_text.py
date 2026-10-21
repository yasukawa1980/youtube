"""v06: existing imagery, bilingual type labels, word-free picture diagrams.

No generative-image calls or audio synthesis. Previous v05 remains untouched.
Stages: prepare, visuals, pictures, package, layout, review-render, review-verify.
"""
import argparse, json, os, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from wom01_multilingual_render import read, save, sha, ff, probe
from wom01_quiet_origins import stream_hash
from wom01_refine_av import camera_filter
from wom01_subtitled_review import cues

W,H=1920,1080
BG,IVORY,GOLD,MUTED='#0c1820','#f4efdf','#d8b575','#b0bfc3'
JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
EN='/System/Library/Fonts/Supplemental/Arial.ttf'
SERIF='/System/Library/Fonts/Supplemental/Georgia.ttf'
LABELS={'Museum object':'MUSEUM OBJECT｜博物館資料','AI reconstruction':'AI RECONSTRUCTION｜AIによる再現','Facsimile (copy on paper)':'FACSIMILE｜模写'}
ROOT=Path(os.environ['WOM_EPISODE_ROOT']); PREV=Path(os.environ['WOM_PREVIOUS_ROOT']); SOURCE=Path(os.environ['WOM_SOURCE_ROOT'])
VERSION=os.environ.get('WOM_VERSION','v06'); PREVIOUS_VERSION=os.environ.get('WOM_PREVIOUS_VERSION','v05')
TEXTS=[]; ASSETS=[]

def typeface(size,serif=False,japanese=False):
    return ImageFont.truetype(JA if japanese else SERIF if serif else EN,size)

def text(im,xy,value,size=30,color=IVORY,serif=False,center=False):
    d=ImageDraw.Draw(im);f=typeface(size,serif,any(ord(c)>0x3000 for c in value))
    if center:xy=(xy[0]-d.textlength(value,font=f)/2,xy[1])
    d.text(xy,value,font=f,fill=color)
    TEXTS.append({'text':value,'bbox':list(d.textbbox(xy,value,font=f))})

def label(im,xy,value,size=25,center=False):
    text(im,xy,LABELS[value],size,GOLD,center=center)

def header(im,source='',badge=None):
    text(im,(100,25),'QUIET ORIGINS  /  EP001',28,GOLD)
    if source:text(im,(100,166),source,30,MUTED)
    if badge:
        value=LABELS[badge];f=typeface(30,japanese=True);width=ImageDraw.Draw(im).textlength(value,font=f)+40
        ImageDraw.Draw(im).rounded_rectangle((1820-width,20,1820,70),10,fill='#243942')
        text(im,(1840-width,27),value,30,GOLD)
    return im

def minimal_bars(im,label_value,footer):
    im=im.copy();ImageDraw.Draw(im).rectangle((0,0,W,219),fill=BG)
    return header(im,footer if label_value!='AI reconstruction' else '',label_value if label_value in LABELS else None)

def catalog():
    return {s['key']:s for s in read(PREV/'records/visual_manifest.json')['shots'] if s.get('source')}

def asset(key):
    rec=dict(catalog()[key]);im=Image.open(SOURCE/rec['source']).convert('RGB')
    if rec.get('crop_pixels'):im=im.crop(tuple(rec['crop_pixels']))
    ASSETS.append({k:rec[k] for k in ['key','source','crop_pixels','label'] if k in rec})
    return im,rec

def panel(im,key,box):
    src,rec=asset(key);x,y,w,h=box;art=ImageOps.contain(src,(w,h),Image.Resampling.LANCZOS)
    im.paste(art,(x+(w-art.width)//2,y+(h-art.height)//2))
    return rec

def source_line():return 'The Metropolitan Museum of Art / Open Access (CC0)'

def arrow(d,x,y):
    d.line((x-35,y,x+35,y),fill=GOLD,width=7);d.line((x+35,y,x+14,y-18),fill=GOLD,width=7);d.line((x+35,y,x+14,y+18),fill=GOLD,width=7)

def card_image(seg,key):
    global TEXTS,ASSETS
    TEXTS=[];ASSETS=[]
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im);second=None
    if key=='balance':
        # Keep the approved v05 scale drawing exactly; erase only its two labels.
        old=next(s for s in read(PREV/'records/visual_manifest.json')['shots'] if s['segment_id']==seg['id'] and s['key']==key)
        im=Image.open(PREV/old['file']).convert('RGB');d=ImageDraw.Draw(im)
        d.rectangle((0,0,W,219),fill=BG);d.rectangle((0,700,W,H),fill=BG)
        header(im)
    elif key=='credits':
        header(im)
        rows=[('Museum images',source_line()),('English narration','Kokoro / Heart (af_heart) / synthetic speech'),('Japanese narration','VOICEVOX:冥鳴ひまり'),('Reconstructions and music','AI-generated images / original ambient score')]
        for i,(a,b) in enumerate(rows):
            y=230+i*112
            d.rounded_rectangle((130,y,1790,y+102),18,fill='#1a303a',outline='#42535b',width=2)
            text(im,(175,y+20),f'{i+1:02}',42,GOLD)
            text(im,(320,y+8),a,36,serif=True);text(im,(320,y+58),b,30,MUTED)
    elif key in ['maat','passage']:
        keys=['met_548344_maat'] if key=='maat' else ['met_557657_scale','met_548344_detail']
        frames=[];texts=[];allassets=[]
        for k in keys:
            frame=Image.new('RGB',(W,H),BG);TEXTS=[];ASSETS=[]
            # Maat uses the existing crop, presented higher and larger than the next shot.
            panel(frame,k,(180,215,1560,480));header(frame,source_line(),'Museum object')
            frames.append(frame);texts.append(TEXTS.copy());allassets.extend(ASSETS)
        im=frames[0];second=frames[1] if len(frames)>1 else None;TEXTS=texts[0];ASSETS=allassets
    else:
        sets={'evidence':['met_544075','met_557830','hero'],'timeline':['met_544206','met_548344','met_552247'],
              'journey':['linen','met_548344','met_548344_detail'],'human_work':['linen','met_590939'],
              'roles':['met_548344_detail','met_552247_detail','met_557657_osiris'],'protect':['met_544075','linen','met_548344_detail']}
        keys=sets[key];header(im,source_line());n=len(keys)
        centers=[420,960,1500] if n==3 else [560,1360]
        for i,(k,cx) in enumerate(zip(keys,centers)):
            rec=panel(im,k,(cx-(235 if n==3 else 320),225,470 if n==3 else 640,325 if key in ['timeline','roles'] else 375))
            label(im,(cx,565 if key in ['timeline','roles'] else 620),rec['label'],23,True)
            if key=='timeline':text(im,(cx,610),['1981–1952','1050','100–300'][i],32,center=True)
            if key=='roles':
                text(im,(cx,607),['Anubis','Thoth','Osiris'][i],43,serif=True,center=True)
                text(im,(cx,660),['アヌビス','トト','オシリス'][i],26,MUTED,center=True)
        if key=='journey':
            for x in [690,1230]:arrow(d,x,420)
        if key=='human_work':
            d.line((930,425,990,425),fill=GOLD,width=7);d.line((960,395,960,455),fill=GOLD,width=7)
        if key=='timeline':
            d.line((185,660,1735,660),fill=GOLD,width=4);d.line((1230,645,1230,700),fill=GOLD,width=3)
            text(im,(700,674),'BCE｜紀元前',23,MUTED,center=True);text(im,(1480,674),'CE｜紀元後',23,MUTED,center=True)
    return im,second,TEXTS.copy(),ASSETS.copy()

def prepare():
    assert not ROOT.exists() and ROOT!=PREV
    for d in ['records','deliverables','review','assets/composed_en','_work/render']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    for n in ['content.json','content_en.json','master_timeline.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_cues_en.json','subtitle_cues_ja.json','audio_qc.json']:
        shutil.copy2(PREV/'records'/n,ROOT/'records'/n)
    for lang in ['en','ja']:
        for n in [f'EP001_audio_{lang}.m4a',f'EP001_字幕_{lang}.srt']:shutil.copy2(PREV/'deliverables'/n,ROOT/'deliverables'/n)
    for n in ['VOICE_CREDITS.txt','EP001_thumbnail_en.jpg']:shutil.copy2(PREV/'deliverables'/n,ROOT/'deliverables'/n)
    save(ROOT/'records/revision_request.json',{'version':'v06','source_root':str(PREV),'request':'new-channel/wom01_画面文字削減案_20261021.md','audio_regenerated':False,'srt_regenerated':False,'new_images_generated':False,'thumbnail_changed':False,'credits_layout':'v05 wording retained, four rows compacted to y<=668 for enlarged three-line subtitles','v05_preserved':True})

def compose():
    global TEXTS,ASSETS
    old=read(PREV/'records/visual_manifest.json');segments={s['id']:s for s in read(ROOT/'records/content_en.json')['segments']};shots=[]
    for s in old['shots']:
        r=dict(s);TEXTS=[];ASSETS=[];second=None
        if s.get('source'):
            im=Image.open(PREV/s['file']).convert('RGB')
            oid=s['key'].split('_')[1] if s['key'].startswith('met_') else None
            museum={str(a['object_id']):a for a in read(SOURCE/'records/museum_assets.json')}
            source=f'The Metropolitan Museum of Art / {museum[oid]["object_number"]} / Open Access (CC0)' if oid else ''
            im=minimal_bars(im,s['label'],source)
            assert np.array_equal(np.array(im)[220:],np.array(Image.open(PREV/s['file']))[220:])
            texts=TEXTS.copy();assets=[{k:s[k] for k in ['key','source','crop_pixels','label'] if k in s}]
            r['artwork_below_y220_identical_to_v05']=True
        else:
            im,second,texts,assets=card_image(segments[s['segment_id']],s['key'])
        r['screen_text']=texts;r['components']=assets
        r['text_bottom_px']=max(t['bbox'][3] for t in texts)
        assert r['text_bottom_px']<=700,(s['key'],r['text_bottom_px'])
        im.save(ROOT/r['file'])
        if second:
            alternate=str(Path(r['file']).with_name(Path(r['file']).stem+'_end.png'));second.save(ROOT/alternate);r['end_file']=alternate;r['internal_dissolve_seconds']=2.0
        thumb=im.copy();thumb.thumbnail((960,540));thumb.save(ROOT/'review'/f"{Path(r['file']).stem}.jpg",quality=86)
        shots.append(r)
    assert len(shots)==55 and sum(bool(s.get('source')) for s in shots)==41
    assert sha(ROOT/'deliverables/EP001_thumbnail_en.jpg')==sha(PREV/'deliverables/EP001_thumbnail_en.jpg')
    save(ROOT/'records/visual_manifest.json',{'version':'v06','language':'en+ja short type labels','subtitles_burned_in':False,'shots':shots,'label_dictionary':LABELS,'all_text_bottom_max':max(s['text_bottom_px'] for s in shots)})
    print('COMPOSED',len(shots),'max text bottom',max(s['text_bottom_px'] for s in shots),flush=True)

def pictures():
    old=read(PREV/'records/render_shots.json');manifest=read(ROOT/'records/visual_manifest.json')['shots'];shots=[]
    for i,(s,o) in enumerate(zip(manifest,old)):
        assert (s['segment_id'],s['key'])==(o['segment_id'],o['key']);count=o['frames'];path=ROOT/f'_work/render/{i:02}_{s["segment_id"]}_{s["key"]}.mp4'
        filt=camera_filter(count);inputs=['-loop',1,'-framerate',30,'-i',ROOT/s['file']]
        expected={'image_sha256':sha(ROOT/s['file']),'frames':count,'filter':filt,'crf':18}
        if s.get('end_file'):
            inputs+=['-loop',1,'-framerate',30,'-i',ROOT/s['end_file']]
            start=(count/30-2)/2
            dissolve=f"[0:v][1:v]blend=all_expr='A*(1-clip((T-{start})/2,0,1))+B*clip((T-{start})/2,0,1)'[blend];"
            filt=dissolve+filt.replace('[0:v]','[blend]',1);expected.update(filter=filt,end_image_sha256=sha(ROOT/s['end_file']))
        stamp=path.with_suffix('.json')
        if not path.exists() or not stamp.exists() or read(stamp)!=expected:
            ff(inputs+['-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',count,'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',path]);save(stamp,expected)
        shots.append({**s,**{k:o[k] for k in ['start','end','frames']},'encoded_file':str(path.relative_to(ROOT))})
        print('PICTURE',i+1,s['key'],count,flush=True)
    save(ROOT/'records/render_shots.json',shots)

def package():
    shots=read(ROOT/'records/render_shots.json');old=read(PREV/'records/render_shots.json');assert len(shots)==55
    for a,b in zip(shots,old):
        assert all(a[k]==b[k] for k in ['segment_id','key','start','end','frames'])
        stamp=read((ROOT/a['encoded_file']).with_suffix('.json'));assert stamp['image_sha256']==sha(ROOT/a['file'])
    concat=ROOT/'_work/concat_exact.txt';concat.write_text(''.join(f"file '{ROOT/s['encoded_file']}'\nduration {s['frames']/30:.9f}\n" for s in shots))
    picture=ROOT/'_work/picture_cfr.mp4'
    ff(['-f','concat','-safe',0,'-i',concat,'-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512','-movflags','+faststart',picture])
    results=[]
    for lang in ['en','ja']:
        stem=f'EP001_Anubis_{lang}_{VERSION}_1080p30';out=ROOT/f'deliverables/{stem}.mp4';srt=ROOT/f'deliverables/{stem}.srt';shutil.copy2(ROOT/f'deliverables/EP001_字幕_{lang}.srt',srt)
        ff(['-i',picture,'-i',ROOT/f'deliverables/EP001_audio_{lang}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn'),'-metadata',f'title=Quiet Origins / EP001 — Anubis {VERSION}','-metadata','comment=Japanese narration: VOICEVOX:冥鳴ひまり; English narration: Kokoro / Heart (af_heart); external subtitles','-movflags','+faststart',out])
        ff(['-i',out,'-f','null','-']);p=probe(out);v=p['streams'][0]
        assert [x['codec_type'] for x in p['streams']]==['video','audio']
        assert v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==20481 and float(p['format']['duration'])==682.7
        pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(out)],text=True).splitlines()));assert pts==list(range(0,20481*512,512))
        ah=stream_hash(out,'a');assert ah==stream_hash(PREV/f'deliverables/EP001_Anubis_{lang}_{PREVIOUS_VERSION}_1080p30.mp4','a')
        assert sha(srt)==sha(PREV/f'deliverables/EP001_Anubis_{lang}_{PREVIOUS_VERSION}_1080p30.srt')
        results.append({'language':lang,'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'audio_matches_previous':True,'srt_matches_previous':True,'full_decode':'pass','exact_30fps_pts':True,'probe':p,'video_stream_hash':stream_hash(out,'v')})
        print('PACKAGED',lang,flush=True)
    assert results[0]['video_stream_hash']==results[1]['video_stream_hash']
    save(ROOT/f'records/qc_{VERSION}.json',{'duration_seconds':682.7,'frames':20481,'shots':55,'subtitles_burned_in':False,'human_full_listening':False,'previous_version':PREVIOUS_VERSION,'shot_intervals_match_previous':True,'thumbnail_matches_previous':True,'files':results})

def layout():
    import imageio_ffmpeg
    binary=imageio_ffmpeg.get_ffmpeg_exe();shots=read(ROOT/'records/render_shots.json');folder=ROOT/'review/layout';folder.mkdir(exist_ok=True)
    checks=[];thumbs={14:[],26:[]}
    for lang in ['en','ja']:
        video=ROOT/f'deliverables/EP001_Anubis_{lang}_{VERSION}_1080p30.mp4';srt=video.with_suffix('.srt')
        for shot in [s for s in shots if not s.get('source')]:
            for cue in cues(srt):
                a=max(cue['start'],shot['start']);b=min(cue['end'],shot['end'])
                if b-a<.05:continue
                t=(a+b)/2
                base=[binary,'-v','error','-ss',str(t),'-copyts','-i',str(video)]
                end=['-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','-']
                original=np.frombuffer(subprocess.check_output(base+end),np.uint8).reshape(H,W,3)
                for size in [14,26]:
                    filt=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize={size},BorderStyle=3,MarginV=12'"
                    data=subprocess.check_output(base+['-vf',filt]+end);burned=np.frombuffer(data,np.uint8).reshape(H,W,3)
                    mask=np.max(np.abs(burned.astype(np.int16)-original.astype(np.int16)),axis=2)>12
                    yy,xx=np.where(mask);assert len(yy)>0
                    top=int(yy.min());bottom=shot['text_bottom_px']
                    # Camera zoom is restricted to y220..940; bound maximum downward displacement.
                    conservative_bottom=bottom+10 if bottom>=220 else bottom
                    assert top>conservative_bottom,(lang,cue['id'],shot['key'],size,top,bottom)
                    checks.append({'language':lang,'cue':cue['id'],'shot':shot['file'],'time':t,'font_size':size,'subtitle_top':top,'text_bottom':bottom,'conservative_clearance':top-conservative_bottom})
                    im=Image.fromarray(burned);im.thumbnail((384,216));tile=Image.new('RGB',(384,242),BG);tile.paste(im,(0,26));ImageDraw.Draw(tile).text((6,6),f'{lang} cue{cue["id"]} {shot["key"]} font{size}',fill='white');thumbs[size].append(tile)
        print('LAYOUT',lang,'done',flush=True)
    for size,tiles in thumbs.items():
        # Smaller paged sheets make every rendered case inspectable.
        for offset in range(0,len(tiles),20):
            chunk=tiles[offset:offset+20];sheet=Image.new('RGB',(1536,242*((len(chunk)+3)//4)),BG)
            for i,im in enumerate(chunk):sheet.paste(im,((i%4)*384,(i//4)*242))
            sheet.save(folder/f'font{size}_{offset//20+1:02}.jpg',quality=88)
    save(ROOT/'records/subtitle_layout_all.json',{'checks':checks,'total':len(checks),'min_clearance':min(c['conservative_clearance'] for c in checks),'all_passed':True,'method':'Actual MP4 and SRT rendered with libass at every cue/diagram overlap midpoint; conservative ten-pixel camera margin'})
    # All 55 actual midpoint frames, grouped into readable pages.
    for offset in range(0,len(shots),12):
        part=shots[offset:offset+12];sheet=Image.new('RGB',(1280,390*((len(part)+1)//2)),BG)
        for i,s in enumerate(part):
            path=ROOT/f'review/mid_{offset+i:02}.jpg';ff(['-ss',(s['start']+s['end'])/2,'-i',ROOT/f'deliverables/EP001_Anubis_en_{VERSION}_1080p30.mp4','-frames:v',1,'-vf','scale=1280:720','-q:v',3,path])
            im=Image.open(path);im.thumbnail((640,360));sheet.paste(im,((i%2)*640,(i//2)*390+30));ImageDraw.Draw(sheet).text(((i%2)*640+8,(i//2)*390+8),f'{offset+i+1:02} {s["segment_id"]} {s["key"]}',fill='white')
        sheet.save(ROOT/f'review/midpoints_{offset//12+1:02}.jpg',quality=88)
    print('LAYOUT CHECKS',len(checks),flush=True)

def review(stage):
    import wom01_subtitled_review as sr
    sr.VERSION=VERSION;review_root=ROOT/'subtitled_review'
    if stage=='review-render':sr.render(ROOT,review_root)
    else:sr.verify(ROOT,review_root)

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','visuals','pictures','package','layout','review-render','review-verify']);args=p.parse_args()
    os.environ.update(WOM_SUBTITLE_SAFE='1',WOM_MINIMAL_TEXT='1',WOM_BRAND='Quiet Origins')
    if args.stage=='prepare':prepare()
    elif args.stage=='visuals':
        import wom01_multilingual_visuals as v
        v.main()
    elif args.stage=='pictures':pictures()
    elif args.stage=='package':package()
    elif args.stage=='layout':layout()
    else:review(args.stage)
if __name__=='__main__':main()
