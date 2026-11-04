"""EP011 Heart shorts: approved copy and native-voice duration gate before pictures."""
import argparse
import dataclasses
import hashlib
import json
import math
import re
from importlib.metadata import version
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont

REPO=Path(__file__).resolve().parent
REQUEST=REPO/'wom_ショート制作依頼_EP011_20261104.md'
ROOT=Path('/Volumes/ESD-02/新チャンネル/ショート/EP011_v01_20261104')
MAIN=Path('/Volumes/ESD-02/新チャンネル/EP011_WeighingOfTheHeart/確認版_v02_20261104')
MODELS=Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
FPS=30
FONTS=Path('/System/Library/Fonts/Supplemental')
JP=Path('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc')
LINES={
 'H1':'Spell 30B speaks directly | to the heart. / In an old translation, | it begins, My heart my mother. / Modern translators read it | as a plea / that the heart not speak | against its owner. / On this heart scarab, | the museum identifies / ten lines as Spell 30B.',
 'H2':'People often say the heart | had to be lighter than the feather. / Here, the heart is not shown | lighter than the feather. / The two sides hang in balance. / Museum descriptions speak | of the heart balancing with Maat, / truth and right order.',
 'H3':'In Spell 125, | the dead person lists / the wrongs they never did. / I have not stolen. / Then they greet forty-two gods, | each by name. / Could you fail? / Papyri made to help | the dead live on / are unlikely to show | their owner being devoured.'}
PAGE_LINES={sid:[[line.strip() for line in page.split('|')] for page in pages.split('/')] for sid,pages in LINES.items()}
SPECS={
 'H1':[('E07A_03',None),('E06A','Modern translators'),('E07A_01','On this heart scarab')],
 'H2':[('E01A_10_beam_to_scale',None),('D_balance','Museum descriptions')],
 'H3':[('R01',None),('D_stolen','I have not stolen'),('E01A_10_gods','Then they greet'),('E01A_10_ammit','Could you fail')]}
HEADLINES={'H1':['A SPELL SPOKEN','TO THE HEART'],'H2':['HEART AND FEATHER','IN BALANCE'],'H3':['42 GODS,','42 DENIALS']}

def read(p):return json.loads(Path(p).read_text())

def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def save(path,data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def narration():
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    assert Path('/Volumes/ESD-02').is_mount(),'Specified SSD is unavailable'
    queries=json.loads((MAIN/'records/queries_en.json').read_text())
    assert all(q['config']['voice']=='af_heart' and q['config']['speed']==.82
               and q['config']['sentence_pause']==.3 and q['config']['clause_pause']==.12 for q in queries)
    readings=json.loads((MAIN/'records/reading_replacements.json').read_text())
    assert not [q for q in readings if q['language']=='en']
    scripts=re.findall(r'^### (H[123]) — (.+)\n\n見出し：\*\*(.+)\*\*\n\n> (.+)$',REQUEST.read_text(),re.M)
    assert len(scripts)==3 and [len(x[3].split()) for x in scripts]==[44,41,43]
    for d in ['audio','records','assets','review','deliverables','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    ort.disable_telemetry_events();opt=ort.SessionOptions()
    opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
    tts=Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(MODELS/'voices-v1.0.bin'))
    provenance=dict(request_sha256=sha(REQUEST),main_queries_sha256=sha(MAIN/'records/queries_en.json'),
                    model_sha256=sha(MODELS/'kokoro-v1.0.onnx'),voices_sha256=sha(MODELS/'voices-v1.0.bin'),
                    versions={p:version(p) for p in ['kokoro-onnx','onnxruntime','numpy']})
    rows=[]
    for sid,title,headline,text in scripts:
        phonemes=tts.tokenizer.phonemize(text,'en-us')
        assert tts.tokenizer.known(phonemes)==phonemes
        cfg=dict(text=text,spoken_text=text,phonemes=phonemes,voice='af_heart',speed=.82,
                 sentence_pause=.3,clause_pause=.12,trim=True,applied_readings=[],**provenance)
        path=ROOT/f'audio/{sid}_native.wav';stamp=path.with_suffix('.json')
        timing=ROOT/f'records/{sid}_phoneme_timings.json'
        if path.exists() and stamp.exists() and timing.exists() and json.loads(stamp.read_text())==cfg:
            audio,sr=sf.read(path,dtype='float32')
        else:
            audio,sr,times=tts.create_timed(phonemes,voice='af_heart',speed=.82,lang='en-us',is_phonemes=True,trim=True,sentence_pause=.3,clause_pause=.12)
            sf.write(path,audio,sr,subtype='PCM_16');save(stamp,cfg)
            save(timing,{'timings':[dataclasses.asdict(t) for t in times]})
        assert sr==24000
        energy=np.array([np.sqrt(np.mean(audio[i:i+240]**2)) for i in range(0,len(audio),240)])
        active=np.where(energy>10**(-50/20))[0]
        frames=math.ceil(len(audio)/sr*FPS)+75
        row=dict(id=sid,title=title,headline=headline,text=text,words=len(text.split()),audio_file=str(path),audio_sha256=sha(path),
                 native_audio_duration=len(audio)/sr,voice_onset_seconds=int(active[0])*.01,
                 last_voice_activity_seconds=min(len(audio),(int(active[-1])+1)*240)/sr,
                 frames=frames,final_duration_seconds=frames/FPS,within_24_seconds=frames<=720,readings_applied=[])
        rows.append(row)
        print(f'{sid}: {row["words"]} words; voice={row["native_audio_duration"]:.6f}s; CTA included={frames/FPS:.6f}s; onset={row["voice_onset_seconds"]:.2f}s',flush=True)
    result=dict(**provenance,scripts=rows,all_within_24_seconds=all(r['within_24_seconds'] for r in rows),
                text_unchanged=True,speech_speed_modified_to_fit=False,human_full_listening=False,
                gate='24 seconds including 2.5-second CTA; stop picture production and report on failure')
    save(ROOT/'records/narration.json',result)
    if not result['all_within_24_seconds']:
        raise SystemExit('STOP: duration gate failed. No picture production, rewriting or acceleration.')

def helper():
    import wom_shorts_ep010 as base
    base.ROOT=ROOT;base.MAIN=MAIN;base.REQUEST=REQUEST
    return base

def captions():
    assert read(ROOT/'records/narration.json')['all_within_24_seconds']
    for s in read(ROOT/'records/narration.json')['scripts']:
        assert ' '.join(' '.join(ls) for ls in PAGE_LINES[s['id']])==s['text']
    old=helper().helper();old.REQUEST=REQUEST
    old.CAPTIONS={sid:[' '.join(ls) for ls in pages] for sid,pages in PAGE_LINES.items()}
    old.EPISODES={sid:'EP011' for sid in PAGE_LINES};old.captions()
    rows=read(ROOT/'records/shorts.json')
    for s in rows['shorts']:
        for text in ['Spell 30B','Spell 125','My heart my mother.','I have not stolen.']:
            if text in s['text']:assert any(text in g['text'] for g in s['caption_groups'])

def audio():
    helper().helper().audio(bgm_sources={'EP011':MAIN/'audio/common_selected_bgm.wav'},bgm_start_seconds=100)

def cards():
    specs={
      'D_balance':[
        ('IN BALANCE',470,150,'DIN Condensed Bold.ttf'),
        ('THE HEART AND MAAT｜',650,85,'Arial Narrow Bold.ttf'),
        ('心臓とマアトがつり合う',755,40,'JP'),
        ('Maat: truth and right order｜',910,42,'Arial Narrow.ttf'),
        ('マアト：真理と正しい秩序',975,32,'JP')],
      'D_stolen':[
        ('The Negative Confession ·',310,30,'Arial.ttf'),
        ('E. A. Wallis Budge, 1895',355,30,'Arial.ttf'),
        ('I have not stolen.',600,96,'Arial Narrow Bold.ttf'),
        ('盗まなかった',740,48,'JP')]}
    records={}
    for aid,lines in specs.items():
        im=Image.new('RGB',(1080,1920),'#e8d9b7');d=ImageDraw.Draw(im);rows=[]
        for text,y,size,name in lines:
            f=ImageFont.truetype(str(JP if name=='JP' else FONTS/name),size)
            # Render the full-width divider with the Japanese font, preserving the exact character.
            parts=[(text.rstrip('｜'),f)]
            if text.endswith('｜'):parts.append(('｜',ImageFont.truetype(str(JP),size)))
            boxes=[font.getbbox(t) for t,font in parts];width=sum(b[2]-b[0] for b in boxes)
            assert width<=980,(aid,text,width)
            x=round((1080-width)/2);x0=x
            for (t,font),b in zip(parts,boxes):
                d.text((x-b[0],y-b[1]),t,font=font,fill='#3b2c21');x+=b[2]-b[0]
            rows.append(dict(text=text,bbox=[x0,y,x,y+max(b[3]-b[1] for b in boxes)],
                             cap_height=f.getbbox('H')[3]-f.getbbox('H')[1],font_size=size,font=str(f.path)))
        if aid=='D_balance':
            assert ''.join(r['text'] for r in rows)=='IN BALANCETHE HEART AND MAAT｜心臓とマアトがつり合うMaat: truth and right order｜マアト：真理と正しい秩序'
            assert min(r['cap_height'] for r in rows[:2])>=60
        else:
            assert ' '.join(r['text'] for r in rows[:2])=='The Negative Confession · E. A. Wallis Budge, 1895'
            assert rows[2]['text']=='I have not stolen.' and rows[3]['text']=='盗まなかった'
            assert rows[2]['cap_height']>=60
        p=ROOT/f'assets/{aid}_card.png';im.save(p)
        records[aid]=dict(file=str(p),texts=rows,exact_text_verified=True,source='Quiet Origins / approved production request')
    save(ROOT/'records/card_texts.json',records);return records

def visuals():
    base=helper();old=base.helper()
    main={r['key']:r for r in read(MAIN/'records/render_shots.json')}
    carddata=cards();shorts=read(ROOT/'records/shorts.json')['shorts'];caps=[];shots=[];heads=[]
    base.text_asset('common','cta',[])
    for s in shorts:
        sid=s['id'];hp,hr=base.text_asset(sid,'headline',HEADLINES[sid])
        heads.append(dict(id=sid,file=str(hp),rows=hr,fade_start=2,fade_duration=.3))
        for j,(g,lines) in enumerate(zip(s['caption_groups'],PAGE_LINES[sid])):
            cp,cr=base.text_asset(sid,f'caption{j:02}',lines)
            caps.append(dict(short_id=sid,page=j,**g,lines=lines,file=str(cp),rows=cr,
                             line_end_exceptions=['the dead live on'] if 'the dead live on' in lines else []))
        starts=[0 if cue is None else old.phrase_frame(s,cue) for aid,cue in SPECS[sid]]
        for j,(aid,cue) in enumerate(SPECS[sid]):
            end=starts[j+1] if j+1<len(starts) else s['frames'];first=j==0
            if aid in carddata:
                p=Path(carddata[aid]['file']);im=Image.open(p).convert('RGB')
                rect=[0,0,1080,1920];last=rect.copy();vp=[0,0,1080,1920];zoom=1;limit=1
                texts=['TITLE CARD｜文字カード'];source=dict(id=aid,path=str(p),sha256=sha(p),label=texts[0],source=carddata[aid]['source'])
                note=None
            else:
                key={'E01A_10_beam_to_scale':'E01A_10_beam','E01A_10_gods':'E01A_10_beam'}.get(aid,aid)
                m=main[key];p=Path(m['original_source']);assert sha(p)==m['original_sha256']
                im=Image.open(p).convert('RGB');rect=m['crop_pixels'].copy();last=rect.copy()
                vp=[40,285,1000,1344] if first else [40,270,1000,860]
                zoom=1.08 if first else 1.04;limit=1.6;note=None;texts=m['source_text']
                if aid=='R01':
                    rect=[1600,570,2250,1470];last=rect.copy();vp=[59,285,962,1332]
                if aid=='E01A_10_beam_to_scale':
                    rect=[1450,1040,2090,1340] # Same beam/pan detail, with edge padding to retain both complete pans.
                    last=main['E01A_10_scale']['crop_pixels'].copy();vp=[40,270,1000,560];zoom=1;limit=3.4
                    note='Specific beam-to-scale zoom-out overrides generic first-shot zoom-in and approximate 70% height; both pans and the prescribed source range remain visible without distortion.'
                if aid=='E01A_10_gods':
                    rect=[1450,495,2290,1005];last=[1550,495,2390,1005];zoom=1
                if aid=='E01A_10_ammit':limit=2.5
                source=dict(id=aid,path=str(p),sha256=sha(p),label=texts[0],source=texts[1],original_dimensions=list(im.size),main_crop=m['crop_pixels'])
            prepared=ROOT/f'assets/{sid}_{aid}_source.png';im.save(prepared)
            bg=im.copy() if aid in carddata else Image.new('RGB',(1080,1920),'#e8d9b7')
            bgfile=ROOT/f'assets/{sid}_{aid}_bg.jpg';bg.save(bgfile,quality=94)
            header=Image.new('RGBA',(1080,1920));hd=ImageDraw.Draw(header);header_rows=[];wrapped=[]
            for k,text in enumerate(['QUIET ORIGINS / EP011',*texts]):
                fp=JP if '｜' in text else FONTS/'Arial.ttf';f=ImageFont.truetype(str(fp),20 if k<2 else 18)
                line=''
                for word in text.split():
                    t=(line+' '+word).strip()
                    if f.getlength(t)>920:wrapped.append((line,f));line=word
                    else:line=t
                if line:wrapped.append((line,f))
            for k,(text,f) in enumerate(wrapped):
                hd.text((80,140+24*k),text,font=f,fill='#3b2c21');bb=hd.textbbox((80,140+24*k),text,font=f)
                assert bb[3]<=260;header_rows.append(dict(text=text,bbox=list(bb)))
            hfile=ROOT/f'assets/{sid}_{aid}_header.png';header.save(hfile)
            native=max(min(vp[2]/(r[2]-r[0]),vp[3]/(r[3]-r[1])) for r in [rect,last])*zoom
            assert native<=limit+1e-8,(aid,native,limit)
            foreh=min(vp[2]/(rect[2]-rect[0]),vp[3]/(rect[3]-rect[1]))*(rect[3]-rect[1])
            shots.append(dict(short_id=sid,episode='EP011',asset_id=aid,source=source,start_frame=starts[j],end_frame=end,frames=end-starts[j],cut_phrase=cue,cut_seconds=starts[j]/30,file=str(prepared),background=str(bgfile),header=str(hfile),header_texts=header_rows,crop_start=rect,crop_end=last,viewport=vp,zoom_end=zoom,native_max_scale=native,native_scale_limit=limit,foreground_height_fraction=foreh/1920 if first else None,static=aid in carddata,note=note))
    assert len(shots)==len({s['asset_id'] for s in shots})==9
    # The three Imhotep source regions are disjoint; a single continuous beam-to-scale shot is one use.
    a=next(s for s in shots if s['asset_id']=='E01A_10_beam_to_scale');g=next(s for s in shots if s['asset_id']=='E01A_10_gods');m=next(s for s in shots if s['asset_id']=='E01A_10_ammit')
    assert max(g['crop_start'][3],g['crop_end'][3])<min(a['crop_start'][1],a['crop_end'][1],m['crop_start'][1])
    assert max(a['crop_start'][2],a['crop_end'][2])<m['crop_start'][0]
    save(ROOT/'records/visual_manifest.json',dict(shots=shots,unique_asset_regions=9,no_AI=True,imhotep_regions_disjoint=True))
    save(ROOT/'records/caption_manifest.json',caps);save(ROOT/'records/headlines.json',heads)
    for s in shorts:
        for n in sorted(set([0,15,30,45,60,75,s['cta_start_frame']]+[g['start_frame'] for g in shots if g['short_id']==s['id']])):
            im=base.design_frame(s,n,shots,caps,frame_art);im.thumbnail((720,1280));im.save(ROOT/f'review/{s["id"]}_{n:04}_design.jpg',quality=90)
    print('VISUALS READY: nine unique regions/cards; exact text and scale limits verified',flush=True)

def frame_art(g,frac,loaded):
    im,bg,head=loaded;x,y,w,h=g['viewport']
    a=np.array(g['crop_start'],float);b=np.array(g['crop_end'],float);c=a+(b-a)*frac
    z=math.exp(math.log(g['zoom_end'])*frac);cx=(c[0]+c[2])/2;cy=(c[1]+c[3])/2
    cw=(c[2]-c[0])/z;ch=(c[3]-c[1])/z;rect=(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2)
    scale=min(w/cw,h/ch);nw=round(cw*scale);nh=round(ch*scale)
    x+=round((w-nw)/2);y+=round((h-nh)/2)
    crop=im.resize((nw,nh),Image.Resampling.LANCZOS,box=rect)
    frame=bg.copy();frame.paste(crop,(x,y));return Image.alpha_composite(frame.convert('RGBA'),head)

def render():
    old=helper().helper();old.frame_art=frame_art
    old.render(['H1','H2','H3'],version='v01',prefix='QO_short_EP011')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['narration','captions','audio','visuals','render'])
    args=parser.parse_args();globals()[args.stage]()
