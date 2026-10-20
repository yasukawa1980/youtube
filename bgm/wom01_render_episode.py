"""Render a bounded two-image film unit at a time, then mix and caption the final."""
import json
import math
import re
import wave
import subprocess
import time
import hashlib
from pathlib import Path
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(os.environ['WOM_EPISODE_ROOT']).expanduser().resolve()
FPS=30
REC=json.loads((ROOT/'records/narration_timeline.json').read_text())
CONTENT=json.loads((ROOT/'records/content.json').read_text())
TOTAL=REC['duration_seconds']
RENDER=ROOT/'render';RENDER.mkdir(exist_ok=True)
DELIVER=ROOT/'deliverables'
def run(cmd,log=None):
    if log:
        with open(log,'w') as f: subprocess.run(cmd,check=True,stdout=f,stderr=subprocess.STDOUT)
    else:subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
def stamp(t,ass=False):
    scale=100 if ass else 1000
    n=round(t*scale);h=n//(3600*scale);n%=3600*scale;m=n//(60*scale);n%=60*scale;s=n//scale;part=n%scale
    return f'{h}:{m:02}:{s:02}.{part:02}' if ass else f'{h:02}:{m:02}:{s:02},{part:03}'
def wrap(t,n=30):
    lines=[]
    while len(t)>n:
        cut=n
        if t[cut] in '、。！？）」』':cut+=1
        lines.append(t[:cut]);t=t[cut:]
    if t:lines.append(t)
    return '\n'.join(lines)

cues=[c for seg in REC['segments'] for c in seg['cues']]
srt='\n\n'.join(f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{wrap(c["text"])}' for i,c in enumerate(cues,1))+'\n'
(DELIVER/'EP001_字幕_ja.srt').write_text(srt)
ass='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Narration,Hiragino Sans,44,&H00F8F6ED,&H00FFFFFF,&HCC140C07,&HCC140C07,0,0,0,0,100,100,0,0,3,10,0,2,100,100,56,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for c in cues:
    line=wrap(c['text']).replace('\n',r'\N').replace('{','').replace('}','')
    ass+=f'Dialogue: 0,{stamp(c["start"],True)},{stamp(c["end"],True)},Narration,,0,0,0,,{line}\n'
ap=DELIVER/'EP001_字幕_ja.ass';ap.write_text(ass)

clips=[];render_stats=[]
for i,seg in enumerate(REC['segments']):
    start=round(seg['start']*FPS)
    end=round((TOTAL if i==len(REC['segments'])-1 else seg['end'])*FPS)
    nf=end-start;dur=nf/FPS
    assets=[ROOT/'assets/composed'/f'{x}.png' for x in seg['visuals']]
    for p in assets:
        if not p.exists():raise FileNotFoundError(p)
    key=hashlib.sha256((str(nf)+';'.join(hashlib.sha256(p.read_bytes()).hexdigest() for p in assets)).encode()).hexdigest()[:10]
    out=RENDER/f'{seg["id"]}_{key}.mp4'
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','warning','-filter_complex_threads','1']
    for p in assets:cmd+=['-loop','1','-framerate',str(FPS),'-i',str(p)]
    filters=[]
    for j,p in enumerate(assets):
        # Gentle sub-pixel motion for imagery, stable diagrams remain fixed.
        moving=p.stem.startswith('met_') or p.stem in ['hero','nile','linen','archive']
        if moving:
            n=max(1,round((dur/len(assets)+.4)*FPS))
            z=f'(1.005+0.015*min(on/{n},1))' if j%2==0 else f'(1.02-0.015*min(on/{n},1))'
            x=f'(W-W/{z})/2';y=f'(H-H/{z})/2'
            motion=f",perspective=x0='{x}':y0='{y}':x1='{x}+W/{z}':y1='{y}':x2='{x}':y2='{y}+H/{z}':x3='{x}+W/{z}':y3='{y}+H/{z}':interpolation=cubic:sense=source:eval=frame"
        else:motion=''
        filters.append(f'[{j}:v]fps={FPS},setsar=1{motion},format=yuv420p,settb=AVTB,setpts=PTS-STARTPTS[v{j}]')
    if len(assets)==2:
        offset=dur/2-.4
        filters.append(f'[v0][v1]xfade=transition=fade:duration=0.8:offset={offset:.6f},trim=duration={dur:.6f}[v]')
    else:filters.append(f'[v0]trim=duration={dur:.6f}[v]')
    cmd+=['-filter_complex',';'.join(filters),'-map','[v]','-frames:v',str(nf),'-an',
          '-c:v','h264_videotoolbox','-q:v','82','-pix_fmt','yuv420p','-r',str(FPS),
          '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
          '-movflags','+faststart',str(out)]
    t=time.monotonic()
    if not out.exists() or out.stat().st_size<1024:run(cmd,RENDER/f'{seg["id"]}_render.log')
    # Validate duration before reuse/concatenation.
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(out)]))
    actual=float(probe['format']['duration'])
    if abs(actual-dur)>.08:raise ValueError((seg['id'],actual,dur))
    clips.append(out)
    render_stats.append({'segment_id':seg['id'],'frames':nf,'seconds':actual,'elapsed':time.monotonic()-t,'file':str(out.relative_to(ROOT))})
    print('RENDER',seg['id'],f'{actual:.2f}s in {time.monotonic()-t:.1f}s',flush=True)

concat=RENDER/'concat.txt';concat.write_text('\n'.join(f"file '{p}'" for p in clips))
video=RENDER/'picture_master.mp4'
run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(video)],RENDER/'concat.log')

# Original non-historical ambient score; no sampled or third-party music.
sr=24000;bed=ROOT/'audio/original_ambient.wav'
with wave.open(str(bed),'wb') as wav:
    wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(sr)
    for first in range(0,math.ceil(TOTAL*sr),sr*10):
        n=min(sr*10,math.ceil(TOTAL*sr)-first)
        t=(first+np.arange(n))/sr
        envelope=np.minimum(t/5,1)*np.minimum((TOTAL-t)/7,1)
        slow=.66+.34*np.sin(2*np.pi*t/53)**2
        base=.006*np.sin(2*np.pi*146.832384*t)*slow+.003*np.sin(2*np.pi*220*t+.5)
        notes=np.array([293.664768,349.228231,440.,391.995436,293.664768,523.251131])
        k=np.floor(t/14).astype(int);local=t%14
        pitch=notes[k%len(notes)]
        pluck=.018*np.sin(2*np.pi*pitch*local)*np.exp(-local/2.1)*(1-np.exp(-local/0.045))
        l=(base+pluck)*envelope
        r=(base+.92*pluck+.0017*np.sin(2*np.pi*293.664768*t+.45))*envelope
        block=np.stack([l,r],axis=1)
        wav.writeframesraw(np.int16(np.clip(block,-.99,.99)*32767).tobytes())

mix=ROOT/'audio/mix_before_master.wav'
run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-i',str(ROOT/'audio/narration.wav'),'-i',str(bed),
     '-filter_complex','[0:a]highpass=f=65,volume=1.4,pan=stereo|c0=c0|c1=c0[v];[1:a]volume=0.75[b];[v][b]amix=inputs=2:normalize=0:duration=longest[m]',
     '-map','[m]','-ar','48000','-c:a','pcm_s16le',str(mix)],ROOT/'records/mix.log')
measure=subprocess.run(['ffmpeg','-hide_banner','-i',str(mix),'-af','loudnorm=I=-16:TP=-2:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True)
stats=json.loads(re.search(r'\{\s*"input_i".*?\}',measure.stderr,re.S).group())
(ROOT/'records/audio_master_pass1.json').write_text(json.dumps(stats,indent=2))
ln=f'loudnorm=I=-16:TP=-2:LRA=11:measured_I={stats["input_i"]}:measured_TP={stats["input_tp"]}:measured_LRA={stats["input_lra"]}:measured_thresh={stats["input_thresh"]}:offset={stats["target_offset"]}:linear=true'
final=DELIVER/'EP001_アヌビス_完成試作_v01.mp4'
# This installed FFmpeg has no libass filter. Rasterize our own subtitle track
# with the system font, and overlay sparse PNG packets at sentence boundaries.
caption_dir=RENDER/'caption_track';caption_dir.mkdir(exist_ok=True)
ft=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',44)
blank=caption_dir/'blank.png';Image.new('RGBA',(1920,230),(0,0,0,0)).save(blank)
entries=[];cursor=0.0
for i,c in enumerate(cues):
    if c['start']>cursor:entries.append((blank,c['start']-cursor))
    im=Image.new('RGBA',(1920,230),(0,0,0,0));d=ImageDraw.Draw(im)
    lines=wrap(c['text']).split('\n');height=len(lines)*62
    y=1080-56-height-850
    for j,line in enumerate(lines):
        width=d.textlength(line,font=ft);x=(1920-width)/2;yy=y+j*62
        d.rounded_rectangle((x-16,yy-5,x+width+16,yy+57),radius=7,fill=(7,12,20,225))
        d.text((x,yy),line,font=ft,fill=(248,246,237,255))
    p=caption_dir/f'cue_{i:03}.png';im.save(p)
    entries.append((p,c['end']-c['start']));cursor=c['end']
if TOTAL>cursor:entries.append((blank,TOTAL-cursor))
track=caption_dir/'concat.txt'
track.write_text('\n'.join(f"file '{p}'\nduration {duration:.9f}" for p,duration in entries)+f"\nfile '{blank}'\n")
run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-filter_complex_threads','1','-i',str(video),'-i',str(mix),
     '-f','concat','-safe','0','-i',str(track),
     '-filter_complex','[0:v][2:v]overlay=x=0:y=850:eof_action=repeat:format=auto[v]',
     '-map','[v]','-map','1:a',
     '-af',ln,'-c:v','h264_videotoolbox','-q:v','82','-pix_fmt','yuv420p',
     '-c:a','aac','-b:a','192k','-ar','48000','-t',f'{TOTAL:.6f}',
     '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(final)],ROOT/'records/final_render.log')

(ROOT/'records/render_stats.json').write_text(json.dumps(render_stats,ensure_ascii=False,indent=2))
print('FINAL',final,'DURATION',TOTAL,flush=True)
