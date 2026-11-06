"""EP012 Santa shorts: approved copy and native-voice duration gate before pictures."""
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
REQUEST=REPO/'wom_ショート制作依頼_EP012_20261106.md'
ROOT=Path('/Volumes/ESD-02/新チャンネル/ショート/EP012_v01_20261106')
MAIN=Path('/Volumes/ESD-02/新チャンネル/EP012_SantaClaus/確認版_v01_20261105')
MODELS=Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
FPS=30
FONTS=Path('/System/Library/Fonts/Supplemental')
JP=Path('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc')
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
    assert {q['spoken'] for q in readings if q['language']=='en'}=={'SAN-tee-claws'}
    scripts=re.findall(r'^### (N[123]) — (.+)\n\n見出し：\*\*(.+)\*\*\n\n> (.+)$',REQUEST.read_text(),re.M)
    assert len(scripts)==3
    for d in ['audio','records','assets','review','deliverables','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    ort.disable_telemetry_events();opt=ort.SessionOptions()
    opt.intra_op_num_threads=4;opt.inter_op_num_threads=1
    tts=Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'),opt,providers=['CPUExecutionProvider']),str(MODELS/'voices-v1.0.bin'))
    provenance=dict(request_sha256=sha(REQUEST),main_queries_sha256=sha(MAIN/'records/queries_en.json'),
                    model_sha256=sha(MODELS/'kokoro-v1.0.onnx'),voices_sha256=sha(MODELS/'voices-v1.0.bin'),
                    versions={p:version(p) for p in ['kokoro-onnx','onnxruntime','numpy']})
    rows=[]
    for sid,title,headline,text in scripts:
        spoken=text.replace('Santeclaus','SAN-tee-claws')
        phonemes=' '.join('sˈænti klˌɔːz' if p=='SAN-tee-claws' else tts.tokenizer.phonemize(p,'en-us') for p in re.split('(SAN-tee-claws)',spoken) if p.strip())
        replacements=[{'display':'Santeclaus','spoken':'SAN-tee-claws','phonemes':'sˈænti klˌɔːz'}] if 'Santeclaus' in text else []
        assert tts.tokenizer.known(phonemes)==phonemes
        cfg=dict(text=text,spoken_text=spoken,phonemes=phonemes,voice='af_heart',speed=.82,
                 sentence_pause=.3,clause_pause=.12,trim=True,applied_readings=replacements,**provenance)
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
                 frames=frames,final_duration_seconds=frames/FPS,within_24_seconds=frames<=720,readings_applied=replacements)
        rows.append(row)
        print(f'{sid}: {row["words"]} words; voice={row["native_audio_duration"]:.6f}s; CTA included={frames/FPS:.6f}s; onset={row["voice_onset_seconds"]:.2f}s',flush=True)
    result=dict(**provenance,scripts=rows,all_within_24_seconds=all(r['within_24_seconds'] for r in rows),
                text_unchanged=True,speech_speed_modified_to_fit=False,human_full_listening=False,
                gate='24 seconds including 2.5-second CTA; stop picture production and report on failure')
    save(ROOT/'records/narration.json',result)
    if not result['all_within_24_seconds']:
        raise SystemExit('STOP: duration gate failed. No picture production, rewriting or acceleration.')



LINES={
 'N1':"Many people believe | Coca-Cola made Santa red / in the nineteen thirties. / But look at The Children's Friend, / a little book printed | in New York / in eighteen twenty-one. / In one surviving copy, | now at Yale University, / Santeclaus is already | wearing a red coat.",
 'N2':"In January eighteen sixty-three, / during the American Civil War, / Thomas Nast drew Santa Claus | for Harper's Weekly. / His Santa visited | a Union army camp, / in a coat of stars | and striped trousers. / It was printed | in black and white.",
 'N3':"In eighteen twelve, / Washington Irving pictured | Saint Nicholas / riding over the tops | of the trees in a wagon. / In eighteen twenty-one, / a little book showed | his sleigh pulled / by a single reindeer. / Two years later, a poem gave him | eight tiny reindeer."
}
PAGE_LINES={sid:[[line.strip() for line in page.split('|')] for page in pages.split('/')] for sid,pages in LINES.items()}
HEADLINES={'N1':['SANTA WORE RED','IN 1821'],'N2':['SANTA ONCE WORE','THE FLAG'],'N3':['IN 1821, SANTA HAD','ONE REINDEER']}
MEDIA=MAIN.parent/'素材'
REGIONS={
 'N08_person':('N08_p1',[900,1120,1650,1780]),
 'N08_cover':('N08_cover',None),
 'N08_text':('N08_p1',[350,1940,1780,2490]),
 'N08_reindeer':('N08_p1',[270,1040,890,1770]),
 'N02_santa':('N02-A',[1760,1550,2310,2270]),
 'N02_camp':('N02-A',[660,910,1730,1530]),
 'N02_full':('N02-A',None)}
SPECS={
 'N1':[('N08_person',None),('N08_cover','But look at'),('N08_text','In one surviving copy')],
 'N2':[('N02_santa',None),('N02_camp','His Santa visited'),('N02_full','It was printed')],
 'N3':[('D_1812s',None),('N08_reindeer','In eighteen twenty-one'),('D_1823s','Two years later')]}

def helper():
    import wom_shorts_ep010 as base
    base.ROOT=ROOT
    base.MAIN=MAIN
    base.REQUEST=REQUEST
    return base

def captions():
    old=helper().helper()
    old.REQUEST=REQUEST
    old.CAPTIONS={sid:[' '.join(lines) for lines in pages] for sid,pages in PAGE_LINES.items()}
    old.EPISODES={sid:'EP012' for sid in PAGE_LINES}
    for s in read(ROOT/'records/narration.json')['scripts']:
        assert ' '.join(old.CAPTIONS[s['id']])==s['text']
    old.captions()

def audio():
    helper().helper().audio(bgm_sources={'EP012':MAIN/'audio/common_selected_bgm.wav'},bgm_start_seconds=100)

def cards():
    source={
     'D_1812s':[('Washington Irving,',300,30,'Arial.ttf'),('A History of New York, 2nd ed., 1812',345,30,'Arial.ttf'),
                 ('“…riding over the tops',455,85,'Arial Narrow Bold.ttf'),('of the trees,',565,85,'Arial Narrow Bold.ttf'),
                 ('in that self same waggon…”',675,85,'Arial Narrow Bold.ttf'),
                 ('木々のてっぺんの上を、',1080,37,'JP'),('あの同じ車に乗って',1125,37,'JP')],
     'D_1823s':[('Troy Sentinel, December 23, 1823',320,31,'Arial.ttf'),
                 ('But a miniature sleigh,',480,85,'Arial Narrow Bold.ttf'),
                 ('and eight tiny rein-deer,',590,85,'Arial Narrow Bold.ttf'),
                 ('小さなそりと、',800,42,'JP'),('8頭の小さなトナカイ',860,42,'JP')]
    }
    result={}
    for key,rows in source.items():
        im=Image.new('RGB',(1080,1920),'#e8d9b7')
        draw=ImageDraw.Draw(im)
        records=[]
        for text,y,size,font in rows:
            f=ImageFont.truetype(str(JP if font=='JP' else FONTS/font),size)
            b=f.getbbox(text)
            width=b[2]-b[0]
            assert width<=950,(key,text,width)
            x=round((1080-width)/2)
            draw.text((x-b[0],y-b[1]),text,font=f,fill='#3b2c21')
            records.append(dict(text=text,bbox=[x,y,x+width,y+b[3]-b[1]],font_size=size,
                                cap_height=f.getbbox('H')[3]-f.getbbox('H')[1],font=str(f.path)))
        expected='“…riding over the tops of the trees, in that self same waggon…”' if key=='D_1812s' else 'But a miniature sleigh, and eight tiny rein-deer,'
        english=[r['text'] for r in records if r['font_size']==85]
        assert ' '.join(english)==expected
        assert all(r['cap_height']>=60 for r in records if r['font_size']==85)
        assert all(not r['text'].endswith(('｜','·')) for r in records)
        path=ROOT/f'assets/{key}_card.png'
        im.save(path)
        result[key]=dict(file=str(path),texts=records,exact_text_verified=True,source=expected)
    save(ROOT/'records/card_texts.json',result)
    return result

def visuals():
    # Reuse the accepted typography, brand panels and original-art renderer.
    import wom12_scenes as main
    base=helper()
    old=base.helper()
    carddata=cards()
    shorts=read(ROOT/'records/shorts.json')['shorts']
    caps,shots,heads=[],[],[]
    base.text_asset('common','cta',[])
    for s in shorts:
        sid=s['id']
        hp,hr=base.text_asset(sid,'headline',HEADLINES[sid])
        heads.append(dict(id=sid,file=str(hp),rows=hr,fade_start=2,fade_duration=.3))
        for j,(g,lines) in enumerate(zip(s['caption_groups'],PAGE_LINES[sid])):
            path,rows=base.text_asset(sid,f'caption{j:02}',lines)
            caps.append(dict(short_id=sid,page=j,**g,lines=lines,file=str(path),rows=rows))
        starts=[0 if cue is None else old.phrase_frame(s,re.sub(r"[^a-zA-Z0-9' ]",'',cue)) for key,cue in SPECS[sid]]
        for j,(key,cue) in enumerate(SPECS[sid]):
            end=starts[j+1] if j+1<len(starts) else s['frames']
            note=None
            is_card=key in carddata
            if is_card:
                path=Path(carddata[key]['file'])
                im=Image.open(path).convert('RGB')
                rect=[0,0,1080,1920]
                viewport=[0,0,1080,1920]
                zoom,limit=1,1
                texts=['TITLE CARD｜文字カード']
                source=dict(id=key,path=str(path),sha256=sha(path),source=carddata[key]['source'],label=texts[0])
            else:
                original,rect=REGIONS[key]
                path=next(MEDIA.glob(original+'_*.jpg'))
                im=Image.open(path).convert('RGB')
                rect=rect or [0,0,im.width,im.height]
                texts=list(main.CAT[original])
                source=dict(id=key,path=str(path),sha256=sha(path),source=' · '.join(texts[1:]),label=texts[0],original_dimensions=list(im.size))
                zoom=1.04
                limit=1 if original.startswith('N08') else 1.6
                viewport=[40,275,1000,840]
                if key=='N08_person':
                    viewport=[40,280,1000,530]
                    note='Native-resolution cap takes precedence over approximate 70% height. The original subject crop is 750×660 pixels; visual review required for the smaller first subject.'
                if key=='N02_santa':
                    viewport=[40,275,1000,1344]
                scale=min(viewport[2]/(rect[2]-rect[0]),viewport[3]/(rect[3]-rect[1]))
                if scale*zoom>limit:
                    factor=limit/(scale*zoom)
                    w,h=round(viewport[2]*factor-.5),round(viewport[3]*factor-.5)
                    viewport=[viewport[0]+(viewport[2]-w)//2,viewport[1]+(viewport[3]-h)//2,w,h]
            prepared=ROOT/f'assets/{sid}_{key}_source.png'
            im.save(prepared)
            bg=im.copy() if is_card else Image.new('RGB',(1080,1920),'#e8d9b7')
            bgfile=ROOT/f'assets/{sid}_{key}_bg.jpg'
            bg.save(bgfile,quality=94)
            header=Image.new('RGBA',(1080,1920))
            draw=ImageDraw.Draw(header)
            header_rows=[]
            y=140
            for k,text in enumerate(['QUIET ORIGINS / EP012',*texts]):
                f=ImageFont.truetype(str(JP if '｜' in text else FONTS/'Arial.ttf'),20 if k<2 else 18)
                line=''
                for word in text.split()+['']:
                    candidate=(line+' '+word).strip()
                    if not word or f.getlength(candidate)>920:
                        draw.text((80,y),line,font=f,fill='#3b2c21')
                        box=list(draw.textbbox((80,y),line,font=f))
                        assert box[3]<=260,(key,box)
                        header_rows.append(dict(text=line,bbox=box))
                        y+=24
                        line=word
                    else:line=candidate
            hfile=ROOT/f'assets/{sid}_{key}_header.png'
            header.save(hfile)
            scale=min(viewport[2]/(rect[2]-rect[0]),viewport[3]/(rect[3]-rect[1]))
            assert scale*zoom<=limit+1e-8,(key,scale*zoom,limit)
            shots.append(dict(short_id=sid,episode='EP012',asset_id=key,source=source,
                 start_frame=starts[j],end_frame=end,frames=end-starts[j],cut_phrase=cue,cut_seconds=starts[j]/30,
                 file=str(prepared),background=str(bgfile),header=str(hfile),header_texts=header_rows,
                 crop_start=rect,crop_end=rect,viewport=viewport,zoom_end=zoom,native_max_scale=scale*zoom,native_scale_limit=limit,
                 foreground_height_fraction=scale*(rect[3]-rect[1])/1920 if j==0 else None,
                 static=is_card,animated_underline=key=='D_1812s',note=note))
    from itertools import combinations
    boxes=[REGIONS[k][1] for k in ['N08_person','N08_text','N08_reindeer']]
    for a,b in combinations(boxes,2):
        assert min(a[2],b[2])<=max(a[0],b[0]) or min(a[3],b[3])<=max(a[1],b[1])
    save(ROOT/'records/visual_manifest.json',dict(shots=shots,unique_asset_regions=9,no_AI=True,yale_regions_disjoint=True))
    save(ROOT/'records/caption_manifest.json',caps)
    save(ROOT/'records/headlines.json',heads)
    for s in shorts:
        indices=sorted(set([0,15,30,45,60,75,s['cta_start_frame']]+[g['start_frame'] for g in shots if g['short_id']==s['id']]))
        for n in indices:
            im=base.design_frame(s,n,shots,caps,frame_art)
            im.thumbnail((720,1280))
            im.save(ROOT/f'review/{s["id"]}_{n:04}_design.jpg',quality=89)

def frame_art(g,frac,loaded):
    from wom_shorts_ep011 import frame_art as existing
    frame=existing(g,frac,loaded)
    if g.get('animated_underline'):
        draw=ImageDraw.Draw(frame)
        draw.line((210,780,210+max(1,round(650*frac)),780),fill='#81643c',width=4)
    return frame

def render():
    old=helper().helper()
    old.frame_art=frame_art
    old.render(['N1','N2','N3'],version='v01',prefix='QO_short_EP012')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['narration','captions','audio','visuals','render'])
    args=parser.parse_args()
    globals()[args.stage]()
