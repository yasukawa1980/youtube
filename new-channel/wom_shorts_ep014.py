"""Generate the requested English narration and enforce the 24-second gate."""
import dataclasses
import hashlib
import json
import math
import os
import shutil
import zipfile
import re
from pathlib import Path

import numpy as np
import onnxruntime as ort
import soundfile as sf
from kokoro_onnx import Kokoro

REPO = Path(__file__).resolve().parent
ROOT = Path(os.environ.get('WOM_EP014_SHORTS_ROOT',
    '/Volumes/ESD-02/新チャンネル/ショート/EP014_v01_20261111'))
EPISODE = Path('/Volumes/ESD-02/新チャンネル/EP014_Oni')
MAIN = EPISODE / '確認版_v01_20261110' / 'records'
MODELS = Path('/Users/ryo/Desktop/BGM/_共通/音声モデル/Kokoro82M_v1')
REQUEST = REPO / 'wom_ショート制作依頼_EP014_20261110.md'
V02 = EPISODE / '確認版_v02_20261110'
PREVIOUS = Path('/Volumes/ESD-02/新チャンネル/ショート/EP013_v02_20261108')
PAGES = {
    'O1': "Oni are pictured | with horns and tiger skin. / But in Japan's oldest | official history, / the Nihon Shoki, / an oni appears | in six sixty-one, / on Mount Asakura. / It wore a large hat / and looked down | on a funeral. / The chronicle says nothing / about horns or tiger skin.",
    'O2': "In seven thirty-three, / a record | of the province of Izumo / explains the name | of one village, Ayo. / A one-eyed oni came / and ate a farmer's son. / As he was being eaten, / he cried out, ayo, ayo. / And so the place | was called Ayo.",
    'O3': "In seventeen seventy-nine, / Toriyama Sekien wrote / that the northeast, / the direction | of the ox and the tiger, / is called the demon gate. / Oni, he wrote, / wear an ox's horns | and a tiger's skin / to join the two. / But he presents it / as something people say.",
}
PAGE_LINES = {sid: [[line.strip() for line in page.split('|')] for page in text.split('/')]
              for sid, text in PAGES.items()}
HEADLINES = {'O1': ['IN 661, AN ONI', 'WORE A HAT'],
             'O2': ['THE ONE-EYED', 'ONI OF IZUMO'],
             'O3': ['WHY', 'TIGER SKIN?']}
SHOTS = {
    'O1': [('O01-A', None), ('O03-23', "But in Japan's oldest"), ('O05-A', 'The chronicle says nothing')],
    'O2': [('O15-A', None), ('O06-38', 'A one-eyed oni')],
    'O3': [('O02-A', None), ('O11-12_text', 'Toriyama Sekien'), ('D_compass_s', 'Oni he wrote')],
}
VIEW = (0, 270, 1080, 950)
PAPER = '#e8d9b7'
INK = '#3b2c21'


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def narration():
    assert Path('/Volumes/ESD-02').is_mount()
    query_path = MAIN / 'queries_en.json'
    correction_path = MAIN / 'english_phoneme_corrections.json'
    settings = dict(voice='af_heart', speed=.82, sentence_pause=.3, clause_pause=.12)
    assert all(all(query['config'][k] == v for k, v in settings.items())
               for query in json.loads(query_path.read_text()))
    corrections = json.loads(correction_path.read_text())
    replacements = json.loads((MAIN/'approved_reading_corrections.json').read_text())['en']
    scripts = re.findall(r'^### (O[123]) — (.+)\n\n見出し：\*\*(.+)\*\*\n\n> (.+)$', REQUEST.read_text(), re.M)
    assert [sid for sid, *_ in scripts] == ['O1', 'O2', 'O3']
    ort.disable_telemetry_events()
    options = ort.SessionOptions()
    options.intra_op_num_threads = 4
    options.inter_op_num_threads = 1
    tts = Kokoro.from_session(ort.InferenceSession(str(MODELS/'kokoro-v1.0.onnx'), options,
        providers=['CPUExecutionProvider']), str(MODELS/'voices-v1.0.bin'))
    evidence = dict(settings=settings, request_sha256=sha(REQUEST), main_queries_sha256=sha(query_path),
        main_corrections_sha256=sha(correction_path), trim=True, scripts=[])
    for sid, title, headline, script in scripts:
        spoken = script
        for source, replacement in replacements.items():
            spoken = spoken.replace(source, replacement)
        applied = {key: value for key, value in corrections.items() if key in spoken}
        if applied:
            chunks = re.split('(' + '|'.join(map(re.escape, applied)) + ')', spoken)
            phonemes = ' '.join(applied[chunk] if chunk in applied else tts.tokenizer.phonemize(chunk, 'en-us')
                               for chunk in chunks if chunk.strip())
        else:
            phonemes = tts.tokenizer.phonemize(spoken, 'en-us')
        assert tts.tokenizer.known(phonemes) == phonemes
        audio, sr, times = tts.create_timed(phonemes, lang='en-us', is_phonemes=True, trim=True, **settings)
        assert sr == 24000
        path = ROOT/f'audio/{sid}_native.wav'
        sf.write(path, audio, sr, subtype='PCM_16')
        active = np.flatnonzero([np.sqrt(np.mean(audio[i:i+240]**2)) > 10**(-50/20)
                                for i in range(0, len(audio), 240)])
        frames = math.ceil(len(audio)/800) + 75
        row = dict(id=sid, title=title, headline=headline, text=script, spoken_text=spoken,
            phonemes=phonemes, applied_readings=applied, words=len(script.split()), audio_file=str(path),
            audio_sha256=sha(path), samples=len(audio), sample_rate=sr, native_audio_duration=len(audio)/sr,
            voice_onset_seconds=int(active[0])/100, last_voice_activity_seconds=min(len(audio), (int(active[-1])+1)*240)/sr,
            cta_seconds=2.5, frames=frames, final_duration_seconds=frames/30, within_24_seconds=frames <= 720)
        evidence['scripts'].append(row)
        save(ROOT/'records/narration.json', evidence)
        save(path.with_suffix('.json'), {'applied_readings': [
            {'display': key, 'spoken': key, 'phonemes': value} for key, value in applied.items()]})
        save(ROOT/f'records/{sid}_phoneme_timings.json', {'timings': [dataclasses.asdict(t) for t in times]})
        print(sid, len(audio)/sr, frames/30, applied, flush=True)
        if frames > 720:
            raise SystemExit('STOP: 案内2.5秒込みで24秒超過')

def read(path):
    return json.loads(Path(path).read_text())

def helpers():
    import wom_shorts_remake as config
    config.ROOT = ROOT
    config.REQUEST = REQUEST
    config.MODELS = MODELS
    import wom_shorts_remake_produce as old
    import wom_shorts_ep010 as design
    old.ROOT = design.ROOT = ROOT
    old.REQUEST = REQUEST
    old.BIN = '/opt/homebrew/bin/ffmpeg'
    return old, design

def captions():
    old, _ = helpers()
    old.CAPTIONS = {sid: [' '.join(lines) for lines in pages] for sid, pages in PAGE_LINES.items()}
    old.EPISODES = {sid: 'EP014' for sid in PAGES}
    old.captions()

def audio():
    old, _ = helpers()
    source = EPISODE/'確認版_v01_20261110/en/audio/common_selected_bgm.wav'
    old.audio(bgm_sources={'EP014': source}, bgm_start_seconds=100)

def bounds(size, fraction):
    return [round(v * size[i % 2]) for i, v in enumerate(fraction)]

def aspect_crop(size, center, height, width):
    x = min(max(center[0] - width/2, 0), size[0] - width)
    y = min(max(center[1] - height/2, 0), size[1] - height)
    return [x, y, x + width, y + height]

def figure(k, size, main, geometry):
    _, _, w, h = VIEW
    ratio = w/h
    if k == 'O01-A':
        f = main[k]['stages'][0]['detail']['crop']
        l, t, r, b = bounds(size, f)
        center = ((l+r)/2, t+(b-t)*.58)
        heights = [(b-t)*1.20, (b-t)*1.26]
        return [aspect_crop(size, center, height, height*ratio) for height in heights]
    if k == 'O02-A':
        l, t, r, b = bounds(size, geometry[k]['oni_native_bounds_fraction'])
        center = ((l+r)/2, (t+b)/2)
        return [aspect_crop(size, center, height, height*ratio) for height in [h*1.045, h]]
    if k == 'O15-A':
        return [aspect_crop(size, (size[0]*.50, size[1]*.53), height, height*ratio)
                for height in [size[0]/ratio, size[0]/ratio/1.045]]
    return [aspect_crop(size, (size[0]*x, size[1]/2), size[1], size[1]*ratio) for x in [.43, .57]]

def text_layer(image, text, y, size, face, center=480, color=INK):
    from PIL import ImageDraw, ImageFont
    font = ImageFont.truetype(str(face), size)
    l,t,r,b = font.getbbox(text)
    x = round(center-(r-l)/2)
    assert x >= 40 and x+r-l <= 1040 and not text.endswith(('｜','·')), text
    ImageDraw.Draw(image).text((x-l, y-t), text, font=font, fill=color)
    return dict(text=text, bbox=[x,y,x+r-l,y+b-t], font_size=size, color=color)

def compass(scene, design):
    from PIL import Image, ImageDraw
    scene.METR.clear()
    scene.card('D_compass')
    reference = [row['text'] for row in scene.METR]
    scene.METR.clear()
    assert reference[:3] == ['DIAGRAM｜模式図','The twelve zodiac directions','Quiet Origins · Oni']
    assert reference[3:15] == list('子丑寅卯辰巳午未申酉戌亥')
    assert reference[15:] == ['N','北','ushitora','NE · “demon gate”','丑寅・北東・鬼門']
    image = Image.new('RGB', (1080,1920), PAPER)
    draw = ImageDraw.Draw(image)
    arial = design.FONTS/'Arial.ttf'
    rows = [text_layer(image, text, y, size, face) for text,y,size,face in
            zip(reference[:3], [140,176,219], [22,33,23], [scene.JA,arial,arial])]
    x,y,r = 480,610,232
    draw.ellipse((x-r,y-r,x+r,y+r), outline=scene.MUT, width=2)
    draw.arc((x-r-40,y-r-40,x+r+40,y+r+40), -63, -27, fill=scene.RUST, width=4)
    for i, char in enumerate(reference[3:15]):
        a = i*math.pi/6
        rows.append(text_layer(image, char, round(y-r*math.cos(a))-27, 53, scene.JA,
                               round(x+r*math.sin(a)), scene.RUST if char in '丑寅' else INK))
    for text,y,size,face in zip(reference[15:], [288,322,881,936,992], [35,23,48,37,32],
                               [scene.BOLD,scene.JA,scene.EN,scene.EN,scene.JA]):
        rows.append(text_layer(image, text, y, size, face))
    assert [row['text'] for row in rows] == reference
    return image, dict(main_texts=reference, texts=rows, exact_text_verified=True)

def visuals():
    from PIL import Image, ImageDraw, ImageFont
    import wom14_scenes as scene
    old, design = helpers()
    main_zip = V02/'deliverables/EP014_QA_records_v02.zip'
    with zipfile.ZipFile(main_zip) as bundle:
        main = {row['key']:row for row in json.loads(bundle.read('records/en/render_shots.json'))}
        geometry = {row['shot']:row for row in json.loads(bundle.read('records/visual_geometry_v02.json'))
                    if row['language']=='en' and row['scale']==1}
    caps, heads, shots = [], [], []
    cta = PREVIOUS/'assets/common_cta.png'
    shutil.copyfile(cta, ROOT/'assets/common_cta.png')
    cta_record = read(PREVIOUS/'records/cta_design.json')
    save(ROOT/'records/cta_design.json', {**cta_record,'source':str(cta),'source_sha256':sha(cta)})
    card, card_record = compass(scene, design)
    card.save(ROOT/'assets/D_compass_s_source.png')
    save(ROOT/'records/card_texts.json', {'D_compass_s': card_record})
    for s in read(ROOT/'records/shorts.json')['shorts']:
        sid = s['id']
        assert ' '.join(HEADLINES[sid]) == s['headline']
        headline = Image.new('RGBA',(1080,1920))
        ImageDraw.Draw(headline).rounded_rectangle((80,980,880,1168),16,fill=(0,0,0,173))
        hr = [old.puttext(headline,line,990+i*82,height=70,path='Georgia Bold.ttf')
              for i,line in enumerate(HEADLINES[sid])]
        hp = ROOT/f'assets/{sid}_headline.png'
        headline.save(hp)
        heads.append(dict(id=sid,file=str(hp),rows=hr))
        for j,(group,lines) in enumerate(zip(s['caption_groups'],PAGE_LINES[sid],strict=True)):
            path, rows = design.text_asset(sid,f'caption{j:02}',lines)
            caps.append(dict(short_id=sid,page=j,**group,lines=lines,file=str(path),rows=rows))
        starts = [0 if cue is None else old.phrase_frame(s,cue.replace("-", "")) for k,cue in SHOTS[sid]]+[s['frames']]
        for j,(key,cue) in enumerate(SHOTS[sid]):
            k = key.removesuffix('_text')
            record = dict(short_id=sid,asset_id=key,start_frame=starts[j],end_frame=starts[j+1],
                          frames=starts[j+1]-starts[j],cut_phrase=cue,viewport=VIEW)
            assert record['frames'] > 0
            plate = Image.new('RGB',(1080,1920),PAPER)
            if k in scene.CAT:
                labels = scene.CAT[k]
                record['labels'] = list(labels)
                label_rows = []
                for label,y,face in zip(labels,[148,182,215],[scene.JA,*[design.FONTS/'Arial.ttf']*2]):
                    size = next(n for n in range(23,17,-1) if ImageFont.truetype(str(face),n).getlength(label)<=870)
                    label_rows.append(text_layer(plate,label,y,size,face))
                record['label_rows'] = label_rows
                size = scene.ASSETS[k]['original_dimensions']
                source = Path(scene.ASSETS[k]['original_path'])
                record.update(source=str(source), source_sha256=sha(source), source_size=size)
                if k in {'O03-23','O06-38'}:
                    g = geometry[k]
                    boxes = [[bounds(size, b) for b in stage] for stage in scene.BOXES[k]]
                    span = g['source_x_span']
                    fractions = [b for stage in scene.BOXES[k] for b in stage]
                    clip = bounds(size,[span[0],min(b[1] for b in fractions)-.015,
                                        span[1],max(b[3] for b in fractions)+.015])
                    scale = g['native_scale']
                    max_height = VIEW[3]/scale
                    centers = [g['camera'][0]['center_y_fraction'], .25 if k=='O03-23' else .24,
                               .68 if k=='O03-23' else .24]
                    crop = [[clip[0],c*size[1]-max_height/2,clip[2],c*size[1]+max_height/2] for c in centers]
                    cues = [old.phrase_frame(s,'It wore a large hat')] if k=='O03-23' else [starts[j]]
                    record.update(mode='manuscript', native_max_scale=scale, native_crops=crop,
                                  native_clip=clip, highlight_boxes=boxes, highlight_frames=cues,
                                  columns_reordered=False)
                elif k=='O11-12':
                    clip = bounds(size, scene.SAFE[k])
                    boxes = [[bounds(size, b) for b in stage] for stage in scene.BOXES[k]]
                    mask = [(.035,.17),(.395,.17),(.395,.385),(.30,.435),(.035,.435)]
                    mask = [bounds(size, point) for point in mask]
                    scale = min(1, VIEW[2]/(clip[2]-clip[0]), VIEW[3]/(clip[3]-clip[1]))
                    end = starts[j+1]
                    record.update(mode='text',native_max_scale=scale,native_crops=[clip],native_clip=clip,
                                  safe_polygon=mask, highlight_boxes=boxes,
                                  highlight_frames=[starts[j],end-min(42,record['frames']//3)])
                else:
                    crops = figure(k,size,main,geometry)
                    scale = max(max(VIEW[2]/(b[2]-b[0]),VIEW[3]/(b[3]-b[1])) for b in crops)
                    record.update(mode='figure',native_max_scale=round(scale,9),native_crops=crops)
                assert record['native_max_scale'] <= 1
                plate_path = ROOT/f'assets/{key}_plate.png'
                plate.save(plate_path)
                record['plate'] = str(plate_path)
            else:
                record.update(mode='card',native_max_scale=0,native_crops=[],plate=str(ROOT/'assets/D_compass_s_source.png'))
            shots.append(record)
    assert len({g['asset_id'] for g in shots}) == len(shots) == 8
    save(ROOT/'records/visual_manifest.json',dict(shots=shots))
    save(ROOT/'records/caption_manifest.json',caps)
    save(ROOT/'records/headlines.json',heads)

def load_shot(shot):
    from PIL import Image, ImageDraw
    plate = Image.open(shot['plate']).convert('RGB')
    if shot['mode']=='card':
        return plate,None,(0,0)
    crops = shot['native_crops']
    clip = shot.get('native_clip')
    if clip is None:
        clip = [math.floor(min(b[0] for b in crops)),math.floor(min(b[1] for b in crops)),
                math.ceil(max(b[2] for b in crops)),math.ceil(max(b[3] for b in crops))]
    with Image.open(shot['source']) as source:
        assert list(source.size)==shot['source_size']
        art=source.crop(clip).convert('RGB')
    if shot['mode']=='text':
        mask=Image.new('L',art.size)
        ImageDraw.Draw(mask).polygon([(x-clip[0],y-clip[1]) for x,y in shot['safe_polygon']],fill=255)
        clean=Image.new('RGB',art.size,PAPER)
        clean.paste(art,(0,0),mask)
        art=clean
    return plate,art,clip[:2]

def frame(shot, n, loaded, rust):
    from PIL import Image, ImageDraw
    plate,art,(left,top) = loaded
    mode = shot['mode']
    if mode=='card':
        return plate
    x,y,w,h=shot['viewport']
    crops=shot['native_crops']
    start,end=shot['start_frame'],shot['end_frame']
    fraction=(n-start)/max(1,end-start-1)
    if mode=='figure':
        l,t,r,b = [a+(z-a)*fraction for a,z in zip(*crops)]
        tile = art.resize((w,h),Image.Resampling.LANCZOS,box=(l-left,t-top,r-left,b-top))
    else:
        scale = shot['native_max_scale']
        if mode=='manuscript':
            switch=shot['highlight_frames'][0]
            if shot['asset_id']=='O03-23':
                # Keep the first visible group on screen at the start of the relevant phrase.
                u=max(0,(n-switch-12)/max(1,end-switch-13))
                pivot=.48
            else:
                u=max(0,(fraction-.08)/.72)
                pivot=1.
            u=min(1,u)
            i=0 if u<pivot else 1
            f=u/pivot if i==0 else (u-pivot)/(1-pivot) if pivot<1 else 1
            f=f*f*(3-2*f)
            l,t,r,b=[a+(z-a)*f for a,z in zip(crops[i],crops[i+1])]
        else:
            l,t,r,b=crops[0]
        tw,th=round((r-l)*scale),round((b-t)*scale)
        tile = art.transform((tw,th),Image.Transform.AFFINE,(1/scale,0,l-left,0,1/scale,t-top),
                             resample=Image.Resampling.BICUBIC,fillcolor=PAPER)
        active = [i for i, first in enumerate(shot['highlight_frames']) if n>=first]
        if active:
            draw=ImageDraw.Draw(tile)
            for x0,y0,x1,y1 in shot['highlight_boxes'][active[-1]]:
                draw.rectangle(((x0-l)*scale,(y0-t)*scale,(x1-l)*scale,(y1-t)*scale),
                               outline=rust,width=2)
        x+=(w-tw)//2
        y+=(h-th)//2
    out=plate.copy()
    out.paste(tile,(x,y))
    return out

def composite(base, n, short, captions, headline, cta):
    from PIL import Image
    image=base.convert('RGBA')
    headline_end=min(69,short['opening_end_frame'])
    if n<headline_end:
        overlay=headline
        if n>=headline_end-9:
            overlay=headline.copy()
            overlay.putalpha(headline.getchannel('A').point(lambda a:round(a*(headline_end-n)/9)))
        image=Image.alpha_composite(image,overlay)
    layer = cta if n>=short['cta_start_frame'] else next(
        layer for row,layer in captions if row['start_frame']<=n<row['end_frame'])
    return Image.alpha_composite(image,layer).convert('RGB')

def render(preview=False):
    import subprocess
    from PIL import Image
    import wom14_scenes as scene
    visual=read(ROOT/'records/visual_manifest.json')['shots']
    captions=read(ROOT/'records/caption_manifest.json')
    cta=Image.open(ROOT/'assets/common_cta.png').convert('RGBA')
    for short in read(ROOT/'records/shorts.json')['shorts']:
        sid=short['id']
        headline=Image.open(ROOT/f'assets/{sid}_headline.png').convert('RGBA')
        pages=[(row,Image.open(row['file']).convert('RGBA')) for row in captions if row['short_id']==sid]
        shots=[g for g in visual if g['short_id']==sid]
        short['opening_end_frame']=shots[0]['end_frame']
        path=ROOT/f'deliverables/QO_short_EP014_{sid}_v01.mp4'
        cmd=['ffmpeg','-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920',
             '-r','30','-i','pipe:0','-i',str(ROOT/f'audio/{sid}_final.m4a'),'-map','0:v','-map','1:a',
             '-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high',
             '-vf','scale=out_color_matrix=bt709:out_range=tv','-pix_fmt','yuv420p',
             '-frames:v',str(short['frames']),'-color_primaries','bt709','-color_trc','bt709',
             '-colorspace','bt709','-color_range','tv','-c:a','copy','-movflags','+faststart',str(path)]
        log=ROOT/f'records/{sid}_encode.log'
        with log.open('w') as err:
            process=None if preview else subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
            try:
                for shot in shots:
                    loaded=load_shot(shot)
                    start,end=shot['start_frame'],shot['end_frame']
                    indices={start,(start+end)//2,end-1,*shot.get('highlight_frames',[])}
                    for n in sorted(indices) if preview else range(start,end):
                        image=composite(frame(shot,n,loaded,scene.RUST),n,short,pages,headline,cta)
                        if preview:
                            image.thumbnail((540,960))
                            image.save(ROOT/f'review/{sid}_{n:04d}_design.jpg',quality=91)
                        else:
                            process.stdin.write(image.tobytes())
                if process:
                    process.stdin.close()
                    assert process.wait()==0 and log.stat().st_size==0,log.read_text()
            except BaseException:
                if process:
                    process.kill()
                    process.wait()
                raise
        print('PREVIEW' if preview else 'RENDER',sid,flush=True)

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('stage',choices=['narration','captions','audio','visuals','preview','render'])
    stage=parser.parse_args().stage
    assert Path('/Volumes/ESD-02').is_mount()
    for directory in ['records','audio','assets','review','deliverables']:
        (ROOT/directory).mkdir(parents=True,exist_ok=True)
    if stage=='preview':
        render(preview=True)
    else:
        globals()[stage]()
