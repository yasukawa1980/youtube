"""第13話ショート。指定音声を新規合成し、映像制作前に24秒上限を判定する。"""
import dataclasses
import hashlib
import json
import math
import re
import shutil
import sys
from importlib.metadata import version
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path('/Volumes/ESD-02/新チャンネル/ショート/EP013_v01_20261108')
MAIN = Path('/Volumes/ESD-02/新チャンネル/EP013_NightWatch/確認版_v01_20261107')
MODELS = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
REQUEST = Path(__file__).with_name('wom_ショート制作依頼_EP013_20261108.md')

def sha(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def guard():
    assert Path('/Volumes/ESD-02').is_mount(), 'STOP: 指定SSD未接続'
    assert shutil.disk_usage('/').free >= 350 * 1024**2, 'STOP: Mac空き容量の安全余裕不足'

def narration():
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    guard()
    queries = json.loads((MAIN/'records/queries_en.json').read_text())
    assert all(q['config']['voice'] == 'af_heart' and q['config']['speed'] == .82
               and q['config']['sentence_pause'] == .3 and q['config']['clause_pause'] == .12
               for q in queries)
    pronunciation = json.loads((MAIN/'records/pronunciation_review.json').read_text())
    assert all(not q['replacements'] for q in pronunciation['languages']['en'])
    scripts = re.findall(r'^### (V[123]) — (.+)\n\n見出し：\*\*(.+)\*\*\n\n> (.+)$', REQUEST.read_text(), re.M)
    assert len(scripts) == 3
    for d in ['audio', 'records']:
        (ROOT/d).mkdir(exist_ok=True)
    ort.disable_telemetry_events()
    opt = ort.SessionOptions()
    opt.intra_op_num_threads = 2
    opt.inter_op_num_threads = 1
    tts = Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'), opt,
                             providers=['CPUExecutionProvider']), str(MODELS/'voices-v1.0.bin'))
    provenance = dict(request_sha256=sha(REQUEST), main_queries_sha256=sha(MAIN/'records/queries_en.json'),
                      pronunciation_review_sha256=sha(MAIN/'records/pronunciation_review.json'),
                      model_sha256=sha(MODELS/'kokoro-v1.0.onnx'), voices_sha256=sha(MODELS/'voices-v1.0.bin'),
                      python_version=sys.version, python_executable=sys.executable,
                      versions={p: version(p) for p in ['kokoro-onnx', 'onnxruntime', 'numpy',
                                                       'phonemizer', 'espeakng-loader', 'soundfile']})
    rows = []
    for sid, title, headline, text in scripts:
        guard()
        phonemes = tts.tokenizer.phonemize(text, 'en-us')
        assert tts.tokenizer.known(phonemes) == phonemes
        cfg = dict(text=text, spoken_text=text, phonemes=phonemes, voice='af_heart', speed=.82,
                   sentence_pause=.3, clause_pause=.12, trim=True, applied_readings=[], **provenance)
        path = ROOT/f'audio/{sid}_native.wav'
        stamp = path.with_suffix('.json')
        timing = ROOT/f'records/{sid}_phoneme_timings.json'
        if path.exists():
            assert stamp.exists() and timing.exists() and json.loads(stamp.read_text()) == cfg, 'STOP: 既存音声と設定不一致'
            audio, sr = sf.read(path, dtype='float32')
        else:
            audio, sr, times = tts.create_timed(phonemes, voice='af_heart', speed=.82, lang='en-us',
                        is_phonemes=True, trim=True, sentence_pause=.3, clause_pause=.12)
            sf.write(path, audio, sr, subtype='PCM_16')
            save(stamp, cfg)
            save(timing, {'timings': [dataclasses.asdict(t) for t in times]})
        assert sr == 24000
        energy = np.array([np.sqrt(np.mean(audio[i:i+240]**2)) for i in range(0, len(audio), 240)])
        active = np.where(energy > 10**(-50/20))[0]
        frames = math.ceil(len(audio)/sr*30) + 75
        row = dict(id=sid, title=title, headline=headline, text=text, words=len(text.split()),
                   audio_file=str(path), audio_sha256=sha(path), samples=len(audio), sample_rate=sr,
                   native_audio_duration=len(audio)/sr, voice_onset_seconds=int(active[0])*.01,
                   last_voice_activity_seconds=min(len(audio), (int(active[-1])+1)*240)/sr,
                   cta_seconds=2.5, frames=frames, final_duration_seconds=frames/30,
                   within_24_seconds=frames <= 720)
        rows.append(row)
        result = dict(**provenance, scripts=rows, completed_count=len(rows), requested_count=3,
                      text_unchanged=True, speech_speed_modified_to_fit=False, human_full_listening=False,
                      all_within_24_seconds=len(rows) == 3 and all(r['within_24_seconds'] for r in rows),
                      gate='30fpsへ切り上げた音声尺＋案内2.5秒。24秒超で即停止。')
        save(ROOT/'records/narration.json', result)
        print(json.dumps(row, ensure_ascii=False), flush=True)
        if not row['within_24_seconds']:
            raise SystemExit('STOP: 24秒上限超過。後続の音声・映像制作は行わない。')
    guard()

LINES = {
 'V1': "This is Rembrandt's | The Night Watch, / painted in sixteen forty-two. / But the name | is not Rembrandt's. / According to the museum, / it is first found in writing / in seventeen ninety-seven. / An early description, / kept by the captain's family, / says nothing about the night.",
 'V2': "In seventeen fifteen, / The Night Watch was moved / to a room | in Amsterdam's town hall. / Around that time, / it was cut down at the edges / to fit its new place. / Most of the loss | was on the left, / where two men and a child | disappeared.",
 'V3': "Look closely at The Night Watch. / Behind the captain / is a small, bright figure: / a girl with a chicken / hanging from her belt. / The museum describes her / as a kind of mascot | for the company, / and links the chicken's claws / to the symbols | of the arquebusiers."
}
PAGE_LINES = {s: [[l.strip() for l in p.split('|')] for p in v.split('/')] for s,v in LINES.items()}
HEADLINES = {'V1': ['IS THE NIGHT WATCH', 'A NIGHT SCENE?'],
             'V2': ['WHO WAS', 'CUT OUT?'],
             'V3': ['WHY DOES SHE', 'CARRY A CHICKEN?']}
SPECS = {'V1': [('V01_full',None),('V01_D1','But the name'),('D_1797s','According to the museum')],
         'V2': [('V01_left',None),('D_cut_s','Around that time'),('V02_L','Most of the loss')],
         'V3': [('V01_girl',None),('V01_claws',"and links the chicken's claws")]}
REGIONS = {'V01_full': ('V01',[0,0,14645,12158]),
           'V01_D1': ('V01',[6004,5593,10252,7982]),
           'V01_left': ('V01',[0,3800,2400,8067]),
           'V01_girl': ('V01',[3600,6900,5500,10280]),
           'V01_claws': ('V01',[3800,7600,4880,9520]),
           'V02_L': ('V02',[0,3928,3866,6103])}
read = lambda p: json.loads(Path(p).read_text())

def helper():
    import wom_shorts_remake as config
    config.ROOT = ROOT
    config.REQUEST = REQUEST
    import wom_shorts_remake_produce as old
    old.ROOT = ROOT
    old.REQUEST = REQUEST
    old.BIN = '/opt/homebrew/bin/ffmpeg'
    import wom_shorts_ep010 as base
    base.ROOT = ROOT
    base.MAIN = MAIN
    return old, base

def captions():
    guard()
    old, _ = helper()
    old.CAPTIONS = {sid: [' '.join(ls) for ls in pages] for sid,pages in PAGE_LINES.items()}
    old.EPISODES = {sid: 'EP013' for sid in PAGE_LINES}
    for s in read(ROOT/'records/narration.json')['scripts']:
        assert ' '.join(old.CAPTIONS[s['id']]) == s['text']
    old.captions()

def audio():
    guard()
    old, _ = helper()
    old.audio(bgm_sources={'EP013': MAIN/'en/audio/common_selected_bgm.wav'}, bgm_start_seconds=100)

def prepared_art(key):
    """原寸タイルを順番に読み、Macのメモリ／swap負荷を抑えて縮小する。"""
    from PIL import Image
    from wom13_geometry import ITEMS, TILES
    aid, box = REGIONS[key]
    item = ITEMS[aid]
    l,t,r,b = box
    factor = min(1,2160/max(r-l,b-t))
    size = (round((r-l)*factor),round((b-t)*factor))
    im = Image.new('RGB', size)
    for tile in item['tiles']:
        x0,y0=max(l,tile['x']),max(t,tile['y'])
        x1,y1=min(r,tile['x']+tile['w']),min(b,tile['y']+tile['h'])
        if x0>=x1 or y0>=y1:
            continue
        dst=(round((x0-l)*size[0]/(r-l)),round((y0-t)*size[1]/(b-t)),
             round((x1-l)*size[0]/(r-l)),round((y1-t)*size[1]/(b-t)))
        with Image.open(TILES/(aid+'_'+item['object'])/tile['file']) as raw:
            patch=raw.crop((x0-tile['x'],y0-tile['y'],x1-tile['x'],y1-tile['y']))
            patch=patch.resize((dst[2]-dst[0],dst[3]-dst[1]),Image.Resampling.LANCZOS)
            im.paste(patch,dst[:2])
    return im

def cards():
    from PIL import Image,ImageDraw,ImageFont
    fonts=Path('/System/Library/Fonts/Supplemental')
    jp='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
    data={}
    im=Image.new('RGB',(1080,1920),'#e8d9b7')
    rows=[('TITLE CARD｜文字カード',140,22,'JP'),('A name appears in writing',185,32,'Arial.ttf'),
          ('Rijksmuseum · The Night Watch (SK-C-5)',228,23,'Arial.ttf'),
          ('1797',330,180,'Georgia Bold.ttf'),
          ('the name “the Night Watch”',570,65,'Arial Narrow Bold.ttf'),
          ('first found in writing',655,65,'Arial Narrow Bold.ttf'),
          ('— according to the Rijksmuseum',765,39,'Arial.ttf'),
          ('「夜警」の名が文献に初めて現れる',900,35,'JP'),
          ('（アムステルダム国立美術館の説明による）',960,29,'JP')]
    def put(im,rows):
        out=[];d=ImageDraw.Draw(im)
        for text,y,size,face in rows:
            f=ImageFont.truetype(jp if face=='JP' else str(fonts/face),size)
            b=f.getbbox(text);w=b[2]-b[0];h=b[3]-b[1];x=round((1080-w)/2)
            assert w<=1000,(text,w)
            assert not text.endswith(('｜','·'))
            d.text((x-b[0],y-b[1]),text,font=f,fill='#3b2c21')
            out.append(dict(text=text,bbox=[x,y,x+w,y+h],font_size=size,font=str(f.path)))
        return out
    records=put(im,rows)
    path=ROOT/'assets/D_1797s_card.png';im.save(path)
    source_texts=['TITLE CARD｜文字カード','A name appears in writing','Rijksmuseum · The Night Watch (SK-C-5)',
                  '1797','the name “the Night Watch” first found in writing','— according to the Rijksmuseum',
                  '「夜警」の名が文献に初めて現れる','（アムステルダム国立美術館の説明による）']
    assert ' '.join(r['text'] for r in records)==' '.join(source_texts)
    data['D_1797s']=dict(file=str(path),texts=records,main_texts=source_texts,exact_text_verified=True)
    # 模写の縮小全体図に、本編で実測した同じ四隅を重ねる。
    REGIONS['V02_full']=('V02',[0,0,10449,8183])
    art=prepared_art('V02_full');art.thumbnail((1040,815))
    im=Image.new('RGB',(1080,1920),'#e8d9b7');x=(1080-art.width)//2;y=330
    im.paste(art,(x,y))
    pts=read(REQUEST.parent/'research/wom13_模写対応点_20261107.json')['V01_corners_in_V02_fraction']
    poly=[(x+round(px*art.width),y+round(py*art.height)) for px,py in pts]
    mask=Image.new('L',im.size);d=ImageDraw.Draw(mask);d.rectangle((x,y,x+art.width,y+art.height),fill=89);d.polygon(poly,fill=0)
    im.paste('#000000',(0,0,1080,1920),mask)
    ImageDraw.Draw(im).line(poly+[poly[0]],fill='#e5d3ae',width=3)
    rows=[('SCHEMATIC｜模式図',140,23,'JP'),('Lundens (attributed) · Copy, c.1642–55',181,26,'Arial.ttf'),
          ('NG London · on loan to Rijksmuseum',222,23,'Arial.ttf'),
          ('SK-C-1453 · Public Domain',259,22,'Arial.ttf'),
          ('Frame: the part that survives today',285,25,'Arial.ttf'),('枠：いまも残る範囲',1148,25,'JP')]
    records=put(im,rows);path=ROOT/'assets/D_cut_s_card.png';im.save(path)
    main_texts=['SCHEMATIC','模式図','Lundens','(attributed)','Copy, c.1642–55','NG London','on loan to',
                'Rijksmuseum','SK-C-1453','Public Domain','Frame: the part that survives today｜枠：いまも残る範囲']
    norm=lambda s: re.sub(r'[\s｜·]','',s)
    assert norm(''.join(r['text'] for r in records))==norm(''.join(main_texts))
    data['D_cut_s']=dict(file=str(path),texts=records,main_texts=main_texts,exact_text_verified=True,
                          source_native_box=[0,0,10449,8183],native_max_scale=art.width/10449,
                          frame_corners_native_fraction=pts,schematic=True)
    save(ROOT/'records/card_texts.json',data)
    return data

def frame_art(g,frac,loaded):
    from PIL import Image
    guard()
    im,bg,head=loaded
    x,y,w,h=g['viewport'];z=math.exp(math.log(g['zoom_end'])*frac)
    cw,ch=im.width/z,im.height/z
    rect=((im.width-cw)/2,(im.height-ch)/2,(im.width+cw)/2,(im.height+ch)/2)
    size=g['display_size']
    crop=im.resize(tuple(size),Image.Resampling.LANCZOS,box=rect)
    frame=bg.copy();frame.paste(crop,(x+(w-size[0])//2,y+(h-size[1])//2))
    return Image.alpha_composite(frame.convert('RGBA'),head)

def visuals():
    from PIL import Image,ImageDraw,ImageFont
    guard()
    for d in ['assets','review','deliverables']:(ROOT/d).mkdir(exist_ok=True)
    old,base=helper();carddata=cards()
    shorts=read(ROOT/'records/shorts.json')['shorts'];caps=[];shots=[];heads=[]
    base.text_asset('common','cta',[])
    for s in shorts:
        sid=s['id'];hp,hr=base.text_asset(sid,'headline',HEADLINES[sid]);heads.append(dict(id=sid,file=str(hp),rows=hr))
        for j,(g,lines) in enumerate(zip(s['caption_groups'],PAGE_LINES[sid])):
            path,rows=base.text_asset(sid,f'caption{j:02}',lines)
            caps.append(dict(short_id=sid,page=j,**g,lines=lines,file=str(path),rows=rows))
        starts=[0 if cue is None else old.phrase_frame(s,re.sub(r"[^a-zA-Z0-9' ]",'',cue)) for key,cue in SPECS[sid]]
        for j,(key,cue) in enumerate(SPECS[sid]):
            guard();end=starts[j+1] if j+1<len(starts) else s['frames'];static=key in carddata
            texts=[];source={};nativebox=None
            if static:
                im=Image.open(carddata[key]['file']).convert('RGB');viewport=[0,0,1080,1920];zoom=1
                size=[1080,1920];scale=carddata[key].get('native_max_scale',0)
            else:
                aid,nativebox=REGIONS[key];im=prepared_art(key)
                viewport=[40,270,1000,900];zoom=1.04
                if key=='V01_full':viewport=[0,270,1080,897]
                scale=min(viewport[2]/(nativebox[2]-nativebox[0]),viewport[3]/(nativebox[3]-nativebox[1]))
                size=[round((nativebox[2]-nativebox[0])*scale),round((nativebox[3]-nativebox[1])*scale)]
                scale=max(size[0]/(nativebox[2]-nativebox[0]),size[1]/(nativebox[3]-nativebox[1]))*zoom
                assert scale<=1
                if key=='V01_full':texts=['PAINTING｜絵画','Rembrandt · The Night Watch · 1642','Rijksmuseum · SK-C-5 · Public Domain']
                elif key.startswith('V01'):texts=['DETAIL｜部分','The Night Watch · 1642','Rijksmuseum, Amsterdam · SK-C-5 · Public Domain']
                else:texts=['COPY｜模写','Attributed to Gerrit Lundens · Copy after The Night Watch · c.1642–55',
                            'National Gallery, London, on loan to Rijksmuseum · SK-C-1453 · Public Domain']
                source=dict(id=aid,original_file=str(MAIN.parent/'素材'/('V01_SK-C-5_原寸.png' if aid=='V01' else 'V02_SK-C-1453_原寸.png')),
                            native_box=nativebox,label=texts[0],source=' · '.join(texts[1:]))
            path=ROOT/f'assets/{key}_source.png';im.save(path)
            bg=Image.new('RGB',(1080,1920),'#e8d9b7');bgpath=ROOT/f'assets/{key}_bg.jpg';bg.save(bgpath,quality=95)
            header=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(header);hr=[];y=130
            for k,text in enumerate([] if static else ['QUIET ORIGINS',*texts]):
                f=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc' if '｜' in text else '/System/Library/Fonts/Supplemental/Arial.ttf',20 if k<2 else 19)
                words=text.split();lines=[];line=''
                for word in words:
                    candidate=(line+' '+word).strip()
                    if f.getlength(candidate)>940 and line:
                        if line.endswith('·'):
                            line=line[:-1].rstrip();word='· '+word
                        lines.append(line);line=word
                    else:line=candidate
                if line:lines.append(line)
                for line in lines:
                    d.text((65,y),line,font=f,fill='#3b2c21');bbox=list(d.textbbox((65,y),line,font=f))
                    assert bbox[3]<270
                    hr.append(dict(text=line,bbox=bbox));y+=24
            hpath=ROOT/f'assets/{key}_header.png';header.save(hpath)
            finalbox=None
            if nativebox:
                l,t,r,b=nativebox;cx=(l+r)/2;cy=(t+b)/2
                finalbox=[cx-(r-l)/zoom/2,cy-(b-t)/zoom/2,cx+(r-l)/zoom/2,cy+(b-t)/zoom/2]
            shots.append(dict(short_id=sid,asset_id=key,source=source,start_frame=starts[j],end_frame=end,frames=end-starts[j],
                 cut_phrase=cue,file=str(path),background=str(bgpath),header=str(hpath),header_texts=hr,
                 viewport=viewport,display_size=size,crop_start=[0,0,*im.size],crop_end=[0,0,*im.size],
                 native_crop_start=nativebox,native_crop_end=finalbox,zoom_end=zoom,native_max_scale=scale,native_scale_limit=1,
                 static=static,foreground_height_fraction=size[1]/1920,prepared_size=list(im.size)))
            im.close()
    from itertools import combinations
    overlaps=[]
    for a,b in combinations(['V01_D1','V01_left','V01_girl'],2):
        p=REGIONS[a][1];q=REGIONS[b][1];area=max(0,min(p[2],q[2])-max(p[0],q[0]))*max(0,min(p[3],q[3])-max(p[1],q[1]))
        assert area==0;overlaps.append(dict(a=a,b=b,overlap_px2=area))
    save(ROOT/'records/visual_manifest.json',dict(shots=shots,overlaps=overlaps,no_AI=True,no_color_correction=True,
         method='原寸タイルから領域内のみを通常のLanczosで縮小。寄りは承認枠の内側。V1全体図とV2模式図は例外。'))
    save(ROOT/'records/caption_manifest.json',caps);save(ROOT/'records/headlines.json',heads)
    for s in shorts:
        inds=sorted(set([0,15,30,45,60,75,s['cta_start_frame']]+[g['start_frame'] for g in shots if g['short_id']==s['id']]))
        for n in inds:
            im=base.design_frame(s,n,shots,caps,frame_art);im.thumbnail((720,1280));im.save(ROOT/f'review/{s["id"]}_{n:04}_design.jpg',quality=89)
    print('VISUALS READY',len(shots),len(caps),flush=True)

def render():
    guard()
    old,_=helper();old.frame_art=frame_art
    for sid in ['V1','V2','V3']:
        guard();old.render([sid],version='v01',prefix='QO_short_EP013')

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['narration','captions','audio','visuals','render']);args=parser.parse_args()
    globals()[args.stage]()
