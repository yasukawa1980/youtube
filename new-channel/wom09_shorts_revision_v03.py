"""EP009 v03: larger end CTA; preserve approved v02 source frames, audio and timing."""
import os,json,shutil,subprocess,argparse,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import imageio_ffmpeg
ROOT=Path('/Volumes/ESD-02/新チャンネル/ショート/EP009_v03_20261102')
OLD=ROOT.parent/'EP009_v02_20261102'
BIN=imageio_ffmpeg.get_ffmpeg_exe()
def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
def ff(args):subprocess.run([BIN,'-nostdin','-y','-v','warning',*map(str,args)],check=True)

def prepare():
 assert not ROOT.exists(),'Do not overwrite an existing revision'
 for d in ['assets','records','review','deliverables','_work']:(ROOT/d).mkdir(parents=True)
 for name in ['shorts.json','render_shots.json','caption_manifest.json','audio_qc.json','narration.json','revision_qc.json','scale_and_quote_qc.json']:
  shutil.copy2(OLD/'records'/name,ROOT/'records'/('v02_'+name))
 rows=read(OLD/'records/shorts.json')['shorts'];layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer)
 main=[80,1030,880,1256];sub=[80,1280,880,1376]
 d.rounded_rectangle(main,radius=16,fill=(232,217,183,235));d.rounded_rectangle(sub,radius=16,fill=(0,0,0,173))
 specs=[('SUBSCRIBE','Georgia Bold.ttf',84,1050,736,(59,44,33,255)),('FOR MORE ORIGINS','Georgia Bold.ttf',84,1152,736,(59,44,33,255)),('Full story: related video below','Arial Bold.ttf',56,1300,760,(244,240,223,255))]
 records=[]
 for index,(text,fn,height,y,width,color) in enumerate(specs):
  font=ImageFont.truetype('/System/Library/Fonts/Supplemental/'+fn,200);b=font.getbbox(text);mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),text,font=font,fill=255)
  natural=round(mask.width*height/mask.height);w=min(width,natural);mask=mask.resize((w,height),Image.Resampling.LANCZOS);x=480-w//2
  layer.paste(color,(x,y,x+w,y+height),mask)
  full=Image.new('L',(1080,1920));full.paste(mask,(x,y));full.save(ROOT/f'assets/cta_mask_{index}.png')
  records.append(dict(text=text,font=fn,glyph_height=height,glyph_bbox=[x,y,x+w,y+height],natural_width_at_height=natural,horizontal_scale=w/natural,plate_bbox=main if index<2 else sub,text_color=list(color[:3]),plate_opacity=(235 if index<2 else 173)/255))
 layer.save(ROOT/'assets/cta_v03.png')
 save(ROOT/'records/cta_design.json',dict(rows=records,group_bbox=[80,1030,880,1376],gap=24,main_horizontal_padding=32,vertical_padding=20,radius=16,appearance='instant; explicitly permitted by v03 request',font_height_interpretation='Actual raster glyph height, not nominal font size. Horizontal fitting keeps both requested lines inside x80–880.',png_sha256=sha(ROOT/'assets/cta_v03.png')))
 for s in rows:
  sid=s['id'];source=(OLD/f'_work/{sid}.ass').read_text();lines=[]
  def seconds(t):
   a,b,c=map(float,t.split(':'));return 3600*a+60*b+c
  for line in source.splitlines():
   if line.startswith('Dialogue:') and seconds(line.split(',')[1])>=s['cta_start']-.015:continue
   lines.append(line)
  (ROOT/f'_work/{sid}_narration.ass').write_text('\n'.join(lines)+'\n')
 print('PREPARED CTA',flush=True)

def render(mode,ids):
 rows=read(OLD/'records/shorts.json')['shorts'];shots=read(OLD/'records/render_shots.json');encodings=[]
 for s in rows:
  sid=s['id']
  if sid not in ids:
   encodings.append(next(e for e in read(ROOT/'records/encoding.json')['rows'] if e['id']==sid));continue
  out=ROOT/f'deliverables/QO_short_EP009_{sid}_v03.mp4';ass=ROOT/f'_work/{sid}_narration.ass'
  # Same original per-shot sources, headline, narration subtitles, encoder settings as v02.
  filt=f"[2:v]format=rgba,fade=t=out:st=2:d=0.3:alpha=1[h];[0:v][h]overlay=0:0:enable='lt(t,2.3)'[t];[t]split=2[captionin][clean];[captionin]ass='{ass}'[n];[n][clean]overlay=0:0:enable='gte(n,{s['cta_start_frame']})'[c];[c][3:v]overlay=0:0:enable='gte(n,{s['cta_start_frame']})'[v]"
  cmd=[BIN,'-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s','1080x1920','-r','30','-i','pipe:0','-i',str(OLD/f'audio/{sid}_final.m4a'),'-loop','1','-framerate','30','-i',str(OLD/f'assets/{sid}_headline.png'),'-loop','1','-framerate','30','-i',str(ROOT/'assets/cta_v03.png'),'-filter_complex_threads','2','-filter_complex',filt,'-map','[v]','-map','1:a:0','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high','-frames:v',str(s['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart',str(out)]
  with (ROOT/f'records/{sid}_encode.log').open('w') as log:
   proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
   try:
    for g in [g for g in shots if g['short_id']==sid]:
     subprocess.run(['ffmpeg','-nostdin','-v','warning','-threads','2','-i',g['encoded_file'],'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=proc.stdin,stderr=log,check=True)
    proc.stdin.close();assert proc.wait()==0
   except BaseException:proc.kill();proc.wait();raise
  encodings.append(dict(id=sid,mode=mode,command=cmd,sha256=sha(out),source_shots=[dict(path=g['encoded_file'],sha256=g['encoded_sha256']) for g in shots if g['short_id']==sid]))
  print('RENDERED',sid,mode,flush=True)
 save(ROOT/'records/encoding.json',dict(rows=encodings))

def preview():
 for s in read(OLD/'records/shorts.json')['shorts']:
  sid=s['id'];g=next(g for g in read(OLD/'records/render_shots.json') if g['short_id']==sid and g['end_frame']==s['frames']);n=s['cta_start_frame']-g['start_frame']
  ff(['-i',g['encoded_file'],'-i',ROOT/'assets/cta_v03.png','-filter_complex',f'[0:v]select=eq(n\\,{n})[f];[f][1:v]overlay=0:0,scale=720:1280[v]','-map','[v]','-frames:v',1,'-update',1,ROOT/f'review/{sid}_CTA_design.jpg'])
 print('CTA DESIGN PREVIEWS',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','preview','render']);p.add_argument('--mode',choices=['high'],default='high');p.add_argument('--ids',default='T1,T2,T3');a=p.parse_args()
 if a.stage=='render':render(a.mode,a.ids.split(','))
 else:globals()[a.stage]()
