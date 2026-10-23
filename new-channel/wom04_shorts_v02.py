"""EP004 v02: two artwork crops and one caption boundary; original AAC retained."""
import argparse,copy,math,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFilter,ImageEnhance
import wom04_shorts as previous
from wom04_shorts import read,save,sha,ff,font,FPS
from wom01_quiet_origins import stream_hash
V1=previous.ROOT
ROOT=V1.parent/'EP004_確認版_v02_20261024'
REQUEST=Path(__file__).resolve().parent/'wom_ショート修正依頼_EP004_v02_20261024.md'
CHANGED={'A02':(.08,.40,.92,.86),'A12':(.04,.375,.74,.70)}

def prepare():
    for d in ['records','deliverables','review','_work','assets']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    shared=read(V1/'records/sharing.json');assert shared['status']=='verified' and shared['release_id']==422102895
    for a in shared['assets']:
        assert sha(V1/'deliverables'/a['name'])==a['sha256']
    rows=copy.deepcopy(read(V1/'records/shorts.json'))
    p1=next(s for s in rows['shorts'] if s['id']=='P1');g=p1['caption_groups']
    assert g[-2]['text']=='made on Crete, about' and g[-1]['text']=='one and a half meters tall.'
    index=next(i for i,w in enumerate(p1['words_timed']) if w['word']=='about')
    frame=round(p1['words_timed'][index]['start']*FPS)
    g[-2].update(text='made on Crete,',word_end=index,end_frame=frame)
    g[-1].update(text='about one and a half meters tall.',word_start=index,start_frame=frame)
    assert ' '.join(x['text'] for x in g)==p1['text']
    visual=copy.deepcopy(read(V1/'records/visual_manifest.json'))
    for s in visual['shots']:
        aid=s['asset_id']
        if aid not in CHANGED:continue
        a=s['source'];im=ImageOps.exif_transpose(Image.open(a['path'])).convert('RGB')
        box=[round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(CHANGED[aid])]
        piece=im.crop(box)
        bg=ImageEnhance.Brightness(ImageOps.fit(piece,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.30)
        old=Image.open(s['file']);bg.paste(old.crop((0,120,1080,270)),(0,120))
        fit=ImageOps.contain(piece,(1080,860),Image.Resampling.LANCZOS);x=(1080-fit.width)//2;y=270+(860-fit.height)//2
        bg.paste(fit,(x,y));path=ROOT/f'assets/{s["short_id"]}_{aid}.png';bg.save(path)
        shift=0 if aid!='A12' else y-270+(.60-CHANGED[aid][1])/(CHANGED[aid][3]-CHANGED[aid][1])*fit.height-430
        s.update(file=str(path),sha256=sha(path),source_crop_pixels=box,source_crop_normalized=CHANGED[aid],art_box=[x,y,x+fit.width,y+fit.height],camera_pan_y_end=shift)
    visual.pop('A02_rim_only_no_figural_neck',None)
    visual.update(A02_body_animal_bands_only=True,A12_paragraph_heading_and_Pixide=True)
    save(ROOT/'records/shorts.json',rows);save(ROOT/'records/visual_manifest.json',visual)
    save(ROOT/'records/revision.json',dict(request_sha256=sha(REQUEST),request_commit='694574b',source_release_id=422102895,changed_crops=CHANGED,P1_about_start_frame=frame,P1_about_start_seconds=frame/FPS,audio_generation_or_processing_performed=False,all_cut_times_unchanged=True,A12_target_source_y_normalized=.60,A12_top_note='x0=0.04 preserves leftmost letters; y0=0.375 includes the complete heading.'))
    print('PREPARED',frame,flush=True)

def camera(s):
    if s['asset_id']!='A12':return previous.camera(s)
    n=max(1,s['frames']-1);z=f'(.97*exp(log(1/.97)*on/{n}))'
    x=f'(W/2-W/(2*{z}))';y=f'(H/2-H/(2*{z})+{s["camera_pan_y_end"]:.9f}*on/{n})'
    p=f"perspective=x0='{x}':y0='{y}':x1='{x}+W/{z}':y1='{y}':x2='{x}':y2='{y}+H/{z}':x3='{x}+W/{z}':y3='{y}+H/{z}':sense=source:eval=frame:interpolation=cubic"
    return f'[0:v]split=2[base][art];[art]crop=1080:860:0:270,format=yuv444p,{p}[moving];[base][moving]overlay=0:270:format=yuv444,format=yuv420p[v]'

def render():
 import imageio_ffmpeg
 shots=read(ROOT/'records/visual_manifest.json')['shots'];rows=read(ROOT/'records/shorts.json')['shorts'];rendered=[];captionrecords=[]
 for s in shots:
  if s['asset_id'] not in CHANGED:
   rendered.append(next(o for o in read(V1/'records/render_shots.json') if o['short_id']==s['short_id'] and o['asset_id']==s['asset_id']));continue
  path=ROOT/f'_work/{s["short_id"]}_{s["asset_id"]}.mp4';stamp=path.with_suffix('.json');cfg={'image':s['sha256'],'frames':s['frames'],'camera':camera(s),'source_sha':s['source']['sha256']}
  if not(path.exists() and stamp.exists() and read(stamp)==cfg):
   if s['source']['kind']=='video':
    x,y,x1,y1=s['art_box'];factor=max(1,s['frames']/300)
    fc=f'[1:v]trim=end_frame=240,setpts=(PTS-STARTPTS)*{factor:.12f},scale={x1-x}:{y1-y}:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.15[art];[0:v][art]overlay={x}:{y}:shortest=1,format=yuv420p[v]'
    args=['-loop',1,'-framerate',30,'-i',s['file'],'-i',s['source']['path'],'-filter_complex_threads',2,'-filter_complex',fc,'-map','[v]']
   else:args=['-loop',1,'-framerate',30,'-i',s['file'],'-filter_complex_threads',2,'-filter_complex',camera(s),'-map','[v]']
   ff([*args,'-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-pix_fmt','yuv420p','-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',path]);save(stamp,cfg)
  rendered.append({**s,'encoded_file':str(path),'encoded_sha256':sha(path)});print('SHOT',s['short_id'],s['asset_id'],flush=True)
 save(ROOT/'records/render_shots.json',rendered)
 for s in rows:
  id=s['id'];group=[r for r in rendered if r['short_id']==id];listing=ROOT/f'_work/{id}_concat.txt';listing.write_text(''.join(f"file '{r['encoded_file']}'\nduration {r['frames']/FPS:.9f}\n" for r in group));picture=ROOT/f'_work/{id}_picture.mp4'
  ff(['-f','concat','-safe',0,'-i',listing,'-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512',picture])
  pages=s['caption_groups']+[{'text':s['cta_text'],'start_frame':s['cta_start_frame'],'end_frame':s['frames'],'brand':True}];ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding','Style: Main,Arial,68,&H00DFF0F4,&H00DFF0F4,&H0010180C,&HAA10180C,-1,0,0,0,100,100,0,0,1,4,1,5,80,200,0,1','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
  def tm(frame):
   ticks=round(frame/FPS*100);return f'{ticks//360000}:{ticks//6000%60:02}:{ticks//100%60:02}.{ticks%100:02}'
  for i,p in enumerate(pages):
   words=p['text'].split();d=ImageDraw.Draw(Image.new('RGB',(1,1)));lines=[]
   for size in ([44] if p.get('brand') else range(68,53,-2)):
    f=font(size,bold=True)
    if p['text']=='about one and a half meters tall.':
     lines=['about one and a half','meters tall.']
     if max(d.textlength(line,font=f) for line in lines)<=770:break
    if len(words)<=5 and d.textlength(p['text'],font=f)<=770:lines=[p['text']];break
    candidates=[[' '.join(words[:cut]),' '.join(words[cut:])] for cut in range(1,len(words)) if cut<=5 and len(words)-cut<=5]
    best=min(candidates,key=lambda lines:max(d.textlength(line,font=f) for line in lines))
    if max(d.textlength(line,font=f) for line in best)<=770:lines=best;break
   assert len(lines)<=2 and max(len(x.split()) for x in lines)<=5
   content='\\N'.join(lines);override=f'{{\\an5\\pos(480,1300)\\fs{size}}}';ass.append(f'Dialogue: 0,{tm(p["start_frame"])},{tm(p["end_frame"])},Main,,0,0,0,,{override}{content}')
   captionrecords.append({'short_id':id,'page':i+1,**p,'lines':lines,'font_size':size,'position':[480,1300]})
  ap=ROOT/f'_work/{id}.ass';ap.write_text('\n'.join(ass)+'\n');out=ROOT/f'deliverables/QO_short_{s["episode"]}_{id}_v02.mp4'
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(picture),'-i',str(V1/f'deliverables/QO_short_EP004_{id}_v01.mp4'),'-vf',f"ass='{ap}'",'-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-frames:v',str(s['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True);print('RENDERED',id,flush=True)
 save(ROOT/'records/render_shots.json',rendered);save(ROOT/'records/caption_manifest.json',captionrecords)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render']);a=p.parse_args();globals()[a.stage]()
