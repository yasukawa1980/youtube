"""EP010 Krampus shorts: approved copy, native Heart voice, strict duration gate."""
import argparse
import dataclasses
import hashlib
import json
import math
import re
import subprocess
from importlib.metadata import version
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

REPO = Path(__file__).resolve().parent
REQUEST = REPO / 'wom_ショート制作依頼_EP010_20261103.md'
ROOT = Path('/Volumes/ESD-02/新チャンネル/ショート/EP010_v01_20261103')
MAIN = Path('/Volumes/ESD-02/新チャンネル/EP010_Krampus/確認版_v02_20261103')
MODELS = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
FPS = 30
FONTS = Path('/System/Library/Fonts/Supplemental')
LINES = {
    'K1': 'Krampus is often called | a pagan spirit of winter. / But when he appears | in historical accounts, / he belongs | to Christian Nicholas customs. / Nicholas arrives with figures | dressed as devils. / And in these settings, / even the frightening companion | works for the saint.',
    'K2': "The Krampus most people | picture today / owes a great deal | to the postcard. / In 1869, | Austria-Hungary introduced / what is often called | the world's first official postcard. / Within decades, / Krampus appeared | on many colorful cards: / dark fur, horns, / a long red tongue, | and chains.",
    'K3': "In this painting | from the 1430s, / Saint Nicholas throws gold | through a window. / But in an old English translation | of the Golden Legend, / he throws it | into a poor man's house / at night, three times, / so that the man's | three daughters can marry.",
}
PAGE_LINES = {sid:[[line.strip() for line in page.split('|')] for page in pages.split('/')]
              for sid,pages in LINES.items()}
SPECS = {
    'K1': [('K06a',None),('K09b','Nicholas arrives with figures'),('K07b','And in these settings')],
    'K2': [('K06b',None),('D_1869','In 1869'),('K01a','Within decades')],
    'K3': [('K04a',None),('D_house','But in an old English translation'),('K05b',"so that the man's three daughters")],
}
HEADLINES = {'K1':['KRAMPUS WORKS','FOR A SAINT'],
             'K2':['THE POSTCARD','THAT MADE KRAMPUS'],
             'K3':['GOLD THROUGH','THE WINDOW?']}


def sha(p):
    return hashlib.file_digest(Path(p).open('rb'), 'sha256').hexdigest()


def save(p, value):
    Path(p).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def narration():
    import onnxruntime as ort
    from kokoro_onnx import Kokoro

    assert Path('/Volumes/ESD-02').is_mount(), 'Specified SSD is unavailable'
    for d in ['audio', 'records', 'assets', 'review', 'deliverables', '_work']:
        (ROOT / d).mkdir(parents=True, exist_ok=True)
    assert json.loads((MAIN/'records/reading_replacements.json').read_text()) == []
    scripts = re.findall(
        r'^### (K[123]) — (.+)\n\n見出し：\*\*(.+)\*\*\n\n> (.+)$',
        REQUEST.read_text(), re.M)
    assert len(scripts) == 3
    ort.disable_telemetry_events()
    opt = ort.SessionOptions()
    opt.intra_op_num_threads = 4
    opt.inter_op_num_threads = 1
    tts = Kokoro.from_session(ort.InferenceSession(
        str(MODELS/'kokoro-v1.0.onnx'), opt, providers=['CPUExecutionProvider']),
        str(MODELS/'voices-v1.0.bin'))
    rows = []
    for sid, title, headline, text in scripts:
        phonemes = tts.tokenizer.phonemize(text, 'en-us')
        assert tts.tokenizer.known(phonemes) == phonemes
        cfg = dict(text=text, spoken_text=text, phonemes=phonemes,
                   voice='af_heart', speed=.82, sentence_pause=.3,
                   clause_pause=.12, trim=True, applied_readings=[],
                   request_sha256=sha(REQUEST),
                   model_sha256=sha(MODELS/'kokoro-v1.0.onnx'),
                   voices_sha256=sha(MODELS/'voices-v1.0.bin'),
                   versions={p:version(p) for p in ['kokoro-onnx','onnxruntime','numpy']})
        path = ROOT/f'audio/{sid}_native.wav'
        stamp = path.with_suffix('.json')
        timing = ROOT/f'records/{sid}_phoneme_timings.json'
        if path.exists() and stamp.exists() and timing.exists() and json.loads(stamp.read_text()) == cfg:
            audio, sr = sf.read(path, dtype='float32')
        else:
            audio, sr, times = tts.create_timed(
                phonemes, voice='af_heart', speed=.82, lang='en-us',
                is_phonemes=True, trim=True, sentence_pause=.3, clause_pause=.12)
            sf.write(path, audio, sr, subtype='PCM_16')
            save(stamp, cfg)
            save(timing, {'timings':[dataclasses.asdict(t) for t in times]})
        assert sr == 24000
        energy = np.array([np.sqrt(np.mean(audio[i:i+240]**2)) for i in range(0,len(audio),240)])
        active = np.where(energy > 10**(-50/20))[0]
        frames = math.ceil(len(audio)/sr*FPS) + 75
        row = dict(id=sid, title=title, headline=headline, text=text,
                   words=len(text.split()), audio_file=str(path), audio_sha256=sha(path),
                   native_audio_duration=len(audio)/sr,
                   voice_onset_seconds=int(active[0])*.01,
                   last_voice_activity_seconds=min(len(audio),(int(active[-1])+1)*240)/sr,
                   frames=frames, final_duration_seconds=frames/FPS,
                   within_24_seconds=frames <= 720, readings_applied=[])
        rows.append(row)
        print(f'{sid}: {row["words"]} words; voice={row["native_audio_duration"]:.6f}s; CTA included={frames/FPS:.6f}s; onset={row["voice_onset_seconds"]:.2f}s', flush=True)
    result = dict(request_sha256=sha(REQUEST), scripts=rows,
                  all_within_24_seconds=all(r['within_24_seconds'] for r in rows),
                  text_unchanged=True, speech_speed_modified_to_fit=False,
                  human_full_listening=False,
                  gate='24 seconds including 2.5-second CTA; stop picture production and report on failure')
    save(ROOT/'records/narration.json',result)
    exception = ROOT/'records/duration_exception.json'
    approval = json.loads(exception.read_text()) if exception.exists() else {}
    permitted = all(r['within_24_seconds'] or (
        r['id']==approval.get('id') and r['frames']<=approval.get('approved_final_frames',0)) for r in rows)
    result['all_within_approved_limits'] = permitted
    result['duration_exception'] = approval
    save(ROOT/'records/narration.json',result)
    if not permitted:
        raise SystemExit('STOP: duration gate failed. No picture production, rewriting or acceleration.')


def helper():
    import wom_shorts_remake_produce as old
    old.ROOT = ROOT
    return old


def captions():
    old = helper()
    nar = json.loads((ROOT/'records/narration.json').read_text())
    assert nar['all_within_approved_limits']
    for s in nar['scripts']:
        assert ' '.join(' '.join(ls) for ls in PAGE_LINES[s['id']])==s['text']
    old.CAPTIONS={sid:[' '.join(ls) for ls in pages] for sid,pages in PAGE_LINES.items()}
    old.EPISODES={sid:'EP010' for sid in PAGE_LINES}
    old.REQUEST=REQUEST
    old.captions(duration_limits={'K2':24.533334})


def audio():
    old=helper()
    old.audio(bgm_sources={'EP010':MAIN/'audio/common_selected_bgm.wav'},bgm_start_seconds=100)


def put_text(layer,text,y,size=55,font='Arial Narrow Bold.ttf',color='#f4efdf',center=480):
    f=ImageFont.truetype(str(FONTS/font),size)
    b=f.getbbox(text);w=b[2]-b[0];h=b[3]-b[1];x=round(center-w/2)
    ImageDraw.Draw(layer).text((x-b[0],y-b[1]),text,font=f,fill=color)
    return dict(text=text,glyph_bbox=[x,y,x+w,y+h],glyph_height=h,
                cap_height=f.getbbox('H')[3]-f.getbbox('H')[1],font=f.path,
                font_size=size,horizontal_scale=1,resampling=False)


def text_asset(sid,kind,lines):
    old=helper();layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer);rows=[]
    if kind=='headline':
        d.rounded_rectangle((80,840,880,1066),16,fill=(0,0,0,173))
        for i,line in enumerate(lines):rows.append(old.puttext(layer,line,860+i*96,height=78,path='Georgia Bold.ttf'))
    elif kind=='cta':
        # Exact approved v03 CTA pixels, no text resampling.
        src=Path('/Volumes/ESD-02/新チャンネル/ショート/作り直し_v03_20261103/assets/common_cta.png')
        layer=Image.open(src).convert('RGBA')
        design=json.loads((src.parents[1]/'records/cta_design.json').read_text())
        rows=design['rows']
        save(ROOT/'records/cta_design.json',{**design,'source':str(src),'source_sha256':sha(src)})
    else:
        for line,y in zip(lines,[1240] if len(lines)==1 else [1198,1294]):
            f=ImageFont.truetype(str(FONTS/'Arial Narrow Bold.ttf'),55);b=f.getbbox(line)
            w=b[2]-b[0];x=round(480-w/2);plate=[x-18,y-20,x+w+18,y+80]
            assert 80<=plate[0] and plate[2]<=880 and 1150<=plate[1] and plate[3]<=1450,(sid,line,plate)
            d.rounded_rectangle(plate,16,fill=(0,0,0,173))
            # v03 uses the same baseline offset for every line, never rescales glyphs.
            d.text((x-b[0],y),line,font=f,fill=(244,239,223,255))
            rows.append(dict(text=line,glyph_bbox=list(d.textbbox((x-b[0],y),line,font=f)),
                             glyph_height=b[3]-b[1],cap_height=39,font=f.path,font_size=55,
                             horizontal_scale=1,resampling=False,plate_bbox=plate,opacity=173/255))
    p=ROOT/f'assets/{sid}_{kind}.png';layer.save(p)
    return p,rows


def cards(main):
    ink='#3b2c21';sand='#e8d9b7';allcards={}
    d1869=[t['text'] for t in main['D_1869']['text_boxes']][1:]
    specs={
        'D_1869':[
            ('1869',315,174,'Arial Bold.ttf'),
            ('THE FIRST OFFICIAL',540,86,'DIN Condensed Bold.ttf'),
            ('POSTCARD',640,86,'DIN Condensed Bold.ttf'),
            ('(AUSTRIA-HUNGARY)',740,86,'DIN Condensed Bold.ttf'),
            ('世界初の公式はがき',855,38,'JP'),
            ('（オーストリア＝ハンガリー）',908,32,'JP'),
            ('as it is often called',990,34,'Arial.ttf'),
            ('とよく言われる',1040,30,'JP')],
        'D_house':[
            ('The Golden Legend, trans. Caxton,',200,26,'Arial.ttf'),
            ('ed. Ellis (1900), vol. 2, p. 110',230,26,'Arial.ttf'),
            ('"...threw by night',470,90,'DIN Condensed Bold.ttf'),
            ('secretly into the house',580,90,'DIN Condensed Bold.ttf'),
            ('of the man',690,90,'DIN Condensed Bold.ttf'),
            ('a mass of gold..."',800,90,'DIN Condensed Bold.ttf'),
            ('夜、人知れず、その男の家の中へ',960,34,'JP'),
            ('金を投げ入れた',1015,34,'JP')],
    }
    for aid,lines in specs.items():
        im=Image.new('RGB',(1080,1920),sand);d=ImageDraw.Draw(im);texts=[]
        for text,y,size,name in lines:
            fontpath=Path('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc') if name=='JP' else FONTS/name
            f=ImageFont.truetype(str(fontpath),size);b=f.getbbox(text);w=b[2]-b[0];h=b[3]-b[1]
            assert w<=980,(aid,text,w)
            x=(1080-w)//2;d.text((x-b[0],y-b[1]),text,font=f,fill=ink)
            texts.append(dict(text=text,bbox=[x,y,x+w,y+h],glyph_height=h,font=str(fontpath),font_size=size))
        p=ROOT/f'assets/{aid}_card.png';im.save(p)
        if aid=='D_1869':
            actual=[' '.join(t['text'] for t in texts[1:3]),texts[0]['text']]
            assert actual[0]==d1869[1]
            assert texts[0]['text']==d1869[0] and texts[3]['text']==d1869[2]
            assert texts[4]['text']+texts[5]['text']==d1869[3]
            assert texts[6]['text']==d1869[4] and texts[7]['text']==d1869[5]
        else:
            quote=' '.join(t['text'] for t in texts[2:6])
            assert quote=='"...threw by night secretly into the house of the man a mass of gold..."'
            assert ''.join(t['text'] for t in texts[6:])=='夜、人知れず、その男の家の中へ金を投げ入れた'
            assert min(t['glyph_height'] for t in texts[2:6])>=60
        allcards[aid]=dict(file=str(p),texts=texts,exact_text_verified=True,source='Quiet Origins / approved production request')
    save(ROOT/'records/card_texts.json',allcards)
    return allcards


def visuals():
    old=helper();main={r['key']:r for r in json.loads((MAIN/'records/render_shots.json').read_text())}
    carddata=cards(main);shorts=json.loads((ROOT/'records/shorts.json').read_text())['shorts']
    captions_out=[];shots=[];heads=[];used=[]
    text_asset('common','cta',[])
    for s in shorts:
        sid=s['id'];hp,hr=text_asset(sid,'headline',HEADLINES[sid]);heads.append(dict(id=sid,file=str(hp),rows=hr,fade_start=2,fade_duration=.3))
        for j,(g,lines) in enumerate(zip(s['caption_groups'],PAGE_LINES[sid])):
            cp,cr=text_asset(sid,f'caption{j:02}',lines)
            captions_out.append(dict(short_id=sid,page=j,**g,lines=lines,file=str(cp),rows=cr,word_count_exceptions=[]))
        starts=[0 if cue is None else old.phrase_frame(s,cue) for aid,cue in SPECS[sid]]
        for j,(aid,cue) in enumerate(SPECS[sid]):
            end=starts[j+1] if j+1<len(starts) else s['frames'];first=j==0
            if aid in carddata:
                p=Path(carddata[aid]['file']);im=Image.open(p).convert('RGB');rect=[0,0,1080,1920];vp=[0,0,1080,1920];zoom=1
                source=dict(id=aid,path=str(p),sha256=sha(p),label='TITLE CARD｜文字カード',source=carddata[aid]['source'])
                texts=['TITLE CARD｜文字カード'];crop_end=rect
            else:
                m=main[aid];p=Path(m['original_source']);assert sha(p)==m['original_sha256']
                im=Image.open(p).convert('RGB');w,h=im.size
                rect=m['crop_pixels'].copy()
                if aid=='K06b':rect=[0,0,w,h] # Approved entire postcard, including blank lower portion.
                if aid=='K04a':rect=[380,80,1840,2101] # Saint, hand, gold, and adjacent window.
                if aid=='K01a':rect=[0,0,w,h]
                if aid in ['K09b','K07b']:
                    # Same crop safety limits and warm monochrome treatment as the main film.
                    im=ImageOps.colorize(ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=.5),black='#443422',white='#f1e4c7')
                vp=[40,285,1000,1344] if first else [40,270,1000,860]
                zoom=1.08 if first else 1.04
                crop_end=rect.copy()
                if aid=='K09b':
                    # Keep the leftmost weapon out of the focus; drift across the actors.
                    rect=[1400,1300,5090,4700];crop_end=[1550,1300,5190,4700]
                if aid=='K07b':
                    rect=[300,180,3000,2300];crop_end=[420,190,2980,2200]
                if aid=='K01a':
                    # Full width keeps basket occupants small; drift from fur/tongue to chains.
                    rect=[0,0,w,4000];crop_end=[0,650,w,4650];zoom=1.02
                if aid=='K05b':
                    rect=[0,0,w,h];crop_end=[150,130,1200,1500];zoom=1.04
                if aid=='K06b':
                    # Entire card enters at frame 0; 8% enlargement uses clamped edges, no initial crop.
                    pass
                source=dict(id=aid,path=str(p),sha256=sha(p),label=m['source_text'][0],source=m['source_text'][1],original_dimensions=[w,h],main_crop=m['crop_pixels'])
                texts=m['source_text']
            prepared=ROOT/f'assets/{sid}_{aid}_source.png';im.save(prepared)
            if aid in carddata:bg=im.copy()
            else:
                # Sand backdrop keeps evidence clear without adding fictitious image content.
                bg=Image.new('RGB',(1080,1920),'#e8d9b7')
            bgfile=ROOT/f'assets/{sid}_{aid}_bg.jpg';bg.save(bgfile,quality=94)
            header=Image.new('RGBA',(1080,1920));hd=ImageDraw.Draw(header);header_records=[]
            if texts:
                values=['QUIET ORIGINS / EP010',*texts];wrapped=[]
                for k,text in enumerate(values):
                    fp=Path('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc') if '｜' in text else FONTS/'Arial.ttf'
                    f=ImageFont.truetype(str(fp),20 if k<2 else 18)
                    lines=[text] if f.getlength(text)<=920 else []
                    if not lines:
                        line=''
                        for word in text.split():
                            t=(line+' '+word).strip()
                            if f.getlength(t)>920:lines.append(line);line=word
                            else:line=t
                        if line:lines.append(line)
                    for line in lines:wrapped.append((line,f))
                for k,(text,f) in enumerate(wrapped):
                    y=140+24*k;hd.text((80,y),text,font=f,fill='#3b2c21')
                    bb=hd.textbbox((80,y),text,font=f);assert bb[3]<=260
                    header_records.append(dict(text=text,bbox=list(bb)))
            hfile=ROOT/f'assets/{sid}_{aid}_header.png';header.save(hfile)
            # frame_art fits each aspect ratio into its viewport before the final composite.
            native=max(min(vp[2]/(r[2]-r[0]),vp[3]/(r[3]-r[1])) for r in [rect,crop_end])*zoom
            assert native<=1.6,(aid,native)
            if first:foreh=min(vp[2]/(rect[2]-rect[0]),vp[3]/(rect[3]-rect[1]))*(rect[3]-rect[1])
            else:foreh=None
            shots.append(dict(short_id=sid,episode='EP010',asset_id=aid,source=source,
                start_frame=starts[j],end_frame=end,frames=end-starts[j],cut_phrase=cue,
                cut_seconds=starts[j]/30,file=str(prepared),background=str(bgfile),header=str(hfile),
                header_texts=header_records,crop_start=rect,crop_end=crop_end,viewport=vp,
                zoom_end=zoom,native_max_scale=native,foreground_height_fraction=foreh/1920 if first else None,
                static=aid in carddata,note='K06b full original postcard takes precedence over art-only enlargement' if aid=='K06b' else None))
            used.append(aid)
    assert len(used)==len(set(used))==9
    save(ROOT/'records/visual_manifest.json',dict(shots=shots,unique_originals=9,no_AI=True))
    save(ROOT/'records/caption_manifest.json',captions_out);save(ROOT/'records/headlines.json',heads)
    # Inspect starts and all cuts before encoding.
    import wom_shorts_remake_v02 as camera
    for s in shorts:
        for n in sorted(set([0,15,30,45,60,75,s['cta_start_frame']]+[g['start_frame'] for g in shots if g['short_id']==s['id']])):
            im=design_frame(s,n,shots,captions_out,camera.frame_art)
            im.thumbnail((720,1280));im.save(ROOT/f'review/{s["id"]}_{n:04}_design.jpg',quality=90)
    print('VISUALS: 9 unique assets, fixed 55pt captions, exact cards',flush=True)


def design_frame(s,n,shots,captions_out,frame_art):
    sid=s['id'];g=next(g for g in shots if g['short_id']==sid and g['start_frame']<=n<g['end_frame'])
    loaded=(Image.open(g['file']).convert('RGB'),Image.open(g['background']).convert('RGB'),Image.open(g['header']).convert('RGBA'))
    im=frame_art(g,(n-g['start_frame'])/max(1,g['frames']-1),loaded)
    if n<69:
        hh=Image.open(ROOT/f'assets/{sid}_headline.png').convert('RGBA')
        if n>=60:hh.putalpha(hh.getchannel('A').point(lambda a:round(a*(69-n)/9)))
        im=Image.alpha_composite(im,hh)
    layer=ROOT/'assets/common_cta.png' if n>=s['cta_start_frame'] else Path(next(c['file'] for c in captions_out if c['short_id']==sid and c['start_frame']<=n<c['end_frame']))
    return Image.alpha_composite(im,Image.open(layer).convert('RGBA')).convert('RGB')


def render(ids=None):
    import wom_shorts_remake_v02 as camera
    old=helper();old.frame_art=camera.frame_art
    old.render(ids or ['K1','K2','K3'],version='v01',prefix='QO_short_EP010')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['narration','captions','audio','visuals','render'])
    parser.add_argument('--ids', default='K1,K2,K3')
    args = parser.parse_args()
    if args.stage=='render':render(args.ids.split(','))
    else:globals()[args.stage]()
