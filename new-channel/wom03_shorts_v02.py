"""EP003 v02: picture cuts in M2 and the 450 BCE caption in M3 only."""
import argparse,copy,json,math,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
import wom03_shorts as previous
from wom03_shorts import read,save,sha,ff,font,FPS,camera
from wom01_quiet_origins import stream_hash
V1=previous.ROOT
ROOT=V1.parent/'EP003_確認版_v02_20261023'
REQUEST=Path(__file__).resolve().parent/'wom_ショート修正依頼_EP003_v02_20261023.md'

def prepare():
    for d in ['records','deliverables','review','_work']: (ROOT/d).mkdir(parents=True,exist_ok=True)
    shared=read(V1/'records/sharing.json')
    assert shared['status']=='verified' and shared['release_id']==421362774
    for a in shared['assets']:
        p=V1/'deliverables'/a['name']
        assert sha(p)==a['sha256']
    rows=copy.deepcopy(read(V1/'records/shorts.json'))
    m2=next(s for s in rows['shorts'] if s['id']=='M2')
    words=m2['words_timed']
    drinking=next(w['start'] for w in words if w['word']=='drinking')
    and_start=next(w['start'] for w in words if w['word']=='and')
    drinking_frame=round(drinking*FPS); and_frame=round(and_start*FPS)
    old_a26=next(s for s in read(V1/'records/visual_manifest.json')['shots'] if s['short_id']=='M2' and s['asset_id']=='A26')['start_frame']
    fallback=(and_frame-drinking_frame)/FPS<1.5
    a26_frame=old_a26 if fallback else and_frame
    visual=copy.deepcopy(read(V1/'records/visual_manifest.json'))
    bounds=[0,drinking_frame,a26_frame,m2['frames']]
    for i,s in enumerate(s for s in visual['shots'] if s['short_id']=='M2'):
        s.update(start_frame=bounds[i],end_frame=bounds[i+1],frames=bounds[i+1]-bounds[i])
    m3=next(s for s in rows['shorts'] if s['id']=='M3')
    g=m3['caption_groups']; assert g[3]['text']=='in Athens around 450' and g[4]['text']=='BCE, she sleeps with'
    boundary=round(m3['words_timed'][17]['start']*FPS)
    g[3].update(text='in Athens around 450 BCE,',word_end=17,end_frame=boundary)
    g[4].update(text='she sleeps with',word_start=17,start_frame=boundary)
    for s in rows['shorts']: assert ' '.join(g['text'] for g in s['caption_groups'])==s['text']
    save(ROOT/'records/shorts.json',rows)
    save(ROOT/'records/visual_manifest.json',visual)
    shutil.copy2(V1/'deliverables/QO_short_EP003_M1_v01.mp4',ROOT/'deliverables/QO_short_EP003_M1_v02.mp4')
    shutil.copy2(V1/'_work/M1.ass',ROOT/'_work/M1.ass')
    save(ROOT/'records/revision.json',dict(request_sha256=sha(REQUEST),request_commit='0acdc19',
        source_release_id=421362774,drinking_onset_native_seconds=drinking,drinking_start_frame=drinking_frame,
        drinking_start_seconds=drinking_frame/FPS,and_shields_onset_native_seconds=and_start,
        and_shields_candidate_frame=and_frame,and_shields_candidate_seconds=and_frame/FPS,
        candidate_eye_cup_seconds=(and_frame-drinking_frame)/FPS,minimum_eye_cup_seconds=1.5,
        shield_fallback_used=fallback,shield_start_frame=a26_frame,shield_start_seconds=a26_frame/FPS,
        actual_eye_cup_seconds=(a26_frame-drinking_frame)/FPS,
        M3_450_BCE_caption_start_frame=g[3]['start_frame'],M3_450_BCE_caption_end_frame=g[3]['end_frame'],
        audio_generation_or_processing_performed=False))
    print('PREPARED',drinking_frame,a26_frame,'fallback',fallback,flush=True)

def render():
 import imageio_ffmpeg
 shots=read(ROOT/'records/visual_manifest.json')['shots'];rows=read(ROOT/'records/shorts.json')['shorts'];rendered=[s for s in read(V1/'records/render_shots.json') if s['short_id']!='M2'];captionrecords=[p for p in read(V1/'records/caption_manifest.json') if p['short_id']=='M1']
 for s in [s for s in shots if s['short_id']=='M2']:
  path=ROOT/f'_work/{s["short_id"]}_{s["asset_id"]}.mp4';stamp=path.with_suffix('.json');cfg={'image':s['sha256'],'frames':s['frames'],'camera':camera(s),'source_sha':s['source']['sha256']}
  if not(path.exists() and stamp.exists() and read(stamp)==cfg):
   if s['source']['kind']=='video':
    x,y,x1,y1=s['art_box'];factor=max(1,s['frames']/300)
    fc=f'[1:v]trim=end_frame=240,setpts=(PTS-STARTPTS)*{factor:.12f},scale={x1-x}:{y1-y}:flags=lanczos,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,tpad=stop_mode=clone:stop_duration=0.15[art];[0:v][art]overlay={x}:{y}:shortest=1,format=yuv420p[v]'
    args=['-loop',1,'-framerate',30,'-i',s['file'],'-i',s['source']['path'],'-filter_complex_threads',2,'-filter_complex',fc,'-map','[v]']
   else:args=['-loop',1,'-framerate',30,'-i',s['file'],'-filter_complex_threads',2,'-filter_complex',camera(s),'-map','[v]']
   ff([*args,'-frames:v',s['frames'],'-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',18,'-pix_fmt','yuv420p','-video_track_timescale',15360,'-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',path]);save(stamp,cfg)
  rendered.append({**s,'encoded_file':str(path),'encoded_sha256':sha(path)});print('SHOT',s['short_id'],s['asset_id'],flush=True)
 rendered.sort(key=lambda p:(p['short_id'],p['start_frame']));save(ROOT/'records/render_shots.json',rendered)
 for s in [s for s in rows if s['id']!='M1']:
  id=s['id'];group=[r for r in rendered if r['short_id']==id];listing=ROOT/f'_work/{id}_concat.txt';listing.write_text(''.join(f"file '{r['encoded_file']}'\nduration {r['frames']/FPS:.9f}\n" for r in group));picture=ROOT/f'_work/{id}_picture.mp4'
  ff(['-f','concat','-safe',0,'-i',listing,'-c','copy','-bsf:v','setts=pts=round(PTS/512)*512:dts=round(DTS/512)*512:duration=512',picture])
  pages=s['caption_groups']+[{'text':s['cta_text'],'start_frame':s['cta_start_frame'],'end_frame':s['frames'],'brand':True}];ass=['[Script Info]','ScriptType: v4.00+','PlayResX: 1080','PlayResY: 1920','[V4+ Styles]','Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding','Style: Main,Arial,68,&H00DFF0F4,&H00DFF0F4,&H0010180C,&HAA10180C,-1,0,0,0,100,100,0,0,1,4,1,5,80,200,0,1','[Events]','Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
  def tm(frame):
   ticks=round(frame/FPS*100);return f'{ticks//360000}:{ticks//6000%60:02}:{ticks//100%60:02}.{ticks%100:02}'
  for i,p in enumerate(pages):
   words=p['text'].split();d=ImageDraw.Draw(Image.new('RGB',(1,1)));lines=[]
   for size in ([44] if p.get('brand') else range(68,53,-2)):
    f=font(size,bold=True)
    if len(words)<=5 and d.textlength(p['text'],font=f)<=770:lines=[p['text']];break
    candidates=[[' '.join(words[:cut]),' '.join(words[cut:])] for cut in range(1,len(words)) if cut<=5 and len(words)-cut<=5]
    best=min(candidates,key=lambda lines:max(d.textlength(line,font=f) for line in lines))
    if max(d.textlength(line,font=f) for line in best)<=770:lines=best;break
   assert len(lines)<=2 and max(len(x.split()) for x in lines)<=5
   content='\\N'.join(lines);override=f'{{\\an5\\pos(480,1300)\\fs{size}}}';ass.append(f'Dialogue: 0,{tm(p["start_frame"])},{tm(p["end_frame"])},Main,,0,0,0,,{override}{content}')
   captionrecords.append({'short_id':id,'page':i+1,**p,'lines':lines,'font_size':size,'position':[480,1300]})
  ap=ROOT/f'_work/{id}.ass';ap.write_text('\n'.join(ass)+'\n');out=ROOT/f'deliverables/QO_short_{s["episode"]}_{id}_v02.mp4'
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(picture),'-i',str(V1/f'deliverables/QO_short_EP003_{id}_v01.mp4'),'-vf',f"ass='{ap}'",'-map','0:v:0','-map','1:a:0','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-frames:v',str(s['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(out)],check=True);print('RENDERED',id,flush=True)
 rendered.sort(key=lambda p:(p['short_id'],p['start_frame']));save(ROOT/'records/render_shots.json',rendered);save(ROOT/'records/caption_manifest.json',captionrecords)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render']);a=p.parse_args();globals()[a.stage]()
