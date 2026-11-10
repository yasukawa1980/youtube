"""EP014 v02: native-coordinate visual revisions and packet-preserving assembly.
No speech synthesis. v01 remains read-only. Unchanged normal/4K AVC packets are reused.
"""
import os,json,subprocess,shutil,hashlib,math,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
os.environ['WOM14_VERSION']='v02'
import wom14_scenes as v
from wom14_produce import REPO,sha,probe
BASE=Path('/Volumes/ESD-02/新チャンネル/EP014_Oni/確認版_v01_20261110')
ROOT=BASE.with_name('確認版_v02_20261110')
MODIFIED={'O02-A','O02-B','O03-23','O06-38','O08-31','R10-27','R11-30','R12-1447'}
TEXT=MODIFIED-{'O02-A','O02-B'}
# At 1080p, source glyph-cell pitch is >= 55 px. 4K respects the same native cap.
SCALES={'O03-23':.88,'O06-38':.43,'O08-31':.36,'R10-27':1.,'R11-30':.42,'R12-1447':.97}
CELL_NATIVE={'O03-23':74,'O06-38':165,'O08-31':218,'R10-27':57.3,'R11-30':148,'R12-1447':68}
# Tight horizontal spans retain the printed columns in their original positions.
SPAN={'O03-23':(.245,.385),'O06-38':(.599,.707),'O08-31':(.163,.292),'R10-27':(.160,.201),'R11-30':(.228,.410),'R12-1447':(.735,.802)}

def read(p):return json.loads(Path(p).read_text())
def save(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def run(args):subprocess.run([str(x) for x in args],check=True)
def ff(args):run(['ffmpeg','-nostdin','-y','-v','warning',*args])
def path_video(base,lang,scale=1,review=False):return base/lang/f'deliverables/EP014_Oni_{lang}_{"v01" if base==BASE else "v02"}_{"subtitled_review_" if review else ""}{2160 if scale==2 else 1080}p30.mp4'
def prepare():
 for lang in ['en','ja']:
  for d in ['records','deliverables','review','_work']:(ROOT/lang/d).mkdir(parents=True,exist_ok=True)
  for name in ['master_timeline.json',f'subtitle_cues_{lang}.json','render_shots.json','render_shots_4k.json','phrase_events.json','phrase_events_4k.json']:
   p=BASE/lang/'records'/name
   if p.exists():shutil.copy2(p,ROOT/lang/'records'/name)
  for p in (BASE/lang/'deliverables').iterdir():
   if p.suffix in ['.wav','.m4a','.srt']:
    q=ROOT/lang/'deliverables'/p.name.replace('_v01_','_v02_');shutil.copy2(p,q);assert sha(p)==sha(q)
 (ROOT/'deliverables').mkdir(exist_ok=True);(ROOT/'records').mkdir(exist_ok=True)
 save(ROOT/'records/request.json',dict(source_release=439388240,request='wom14_Claude確認_v01_20261110.md',modified=sorted(MODIFIED),speech_regenerated=False,timeline_changed=False,v01_read_only=True))

def setup(scale):
 v.S=scale;v.W=1920*scale;v.H=1080*scale

def interpolate(points,t):
 for (a,x),(b,y) in zip(points,points[1:]):
  if t<=b:
   u=max(0,min(1,(t-a)/(b-a)));u=u*u*(3-2*u);return x+(y-x)*u
 return points[-1][1]

def text_camera(k,s,frame,scale):
 stages=s['stages'];focus=[e for e in stages if e['kind']=='source_focus'];z=next(e['start_frame'] for e in stages if e['kind']=='source_zoom') if any(e['kind']=='source_zoom' for e in stages) else focus[0]['start_frame']
 f=focus[0]['start_frame'];end=round(s['end']*30);q=focus[1]['start_frame'] if len(focus)>1 else end
 u=max(0,min(1,(frame-f)/max(1,q-f-1)));w=max(0,min(1,(frame-q)/max(1,end-q-1)))
 curves={
 'O03-23':[(0,.855),(.12,.855),(.38,.25),(1,.68)],
 'O06-38':[(0,.738),(.18,.738),(.64,.24),(1,.24)],
 'O08-31':[(0,.725),(.12,.725),(.34,.40),(.60,.65),(.82,.41),(1,.63)],
 'R10-27':[(0,.656),(1,.656)],
 'R11-30':[(0,.59),(.20,.77),(.55,.35),(.80,.35),(1,.47)],
 'R12-1447':[(0,.705),(.7,.705),(1,.79)]}
 cy=interpolate(curves[k],u)
 if frame>=q and len(focus)>1:
  cy={'O08-31':.63,'R11-30':.483,'R12-1447':interpolate([(0,.79),(.15,.82),(.75,.27),(1,.27)],w)}.get(k,cy)
 sc=min(1.,SCALES[k]*scale)
 return round(s['start']*30)+60,round(s['start']*30)+78,cy,sc,(-1 if frame<f else 1 if frame>=q and len(focus)>1 else 0)

def base_plate(k,scale):
 setup(scale);im=v.art_scene(k,v.SAFE.get(k,(0,0,1,1)));top=(205 if len(v.wrap(v.NOTES[k][0],23,v.EN,1800))==1 else 235) if k in v.NOTES else 130
 ImageDraw.Draw(im).rectangle((0,top*scale,v.W,v.H),fill=v.PAPER)
 return im,top,905

def affine_art(base,src,scale_native,cx,cy,top,bottom,xspan=None,boxes=None,clip=None):
 S=v.S;im=base.copy();bandh=(bottom-top)*S
 if xspan is None:xspan=(0,src.width)
 # Render only original source pixels in the crop; no foreign photography background.
 width=min(1840*S,round((xspan[1]-xspan[0])*scale_native));width=max(2,width)
 left=(v.W-width)//2;originx=cx-width/(2*scale_native);originy=cy-bandh/(2*scale_native)
 sample=src.crop(clip) if clip else src
 ox=originx-(clip[0] if clip else 0);oy=originy-(clip[1] if clip else 0)
 tile=sample.transform((width,bandh),Image.Transform.AFFINE,(1/scale_native,0,ox,0,1/scale_native,oy),resample=Image.Resampling.BICUBIC,fillcolor=v.PAPER)
 if boxes:
  d=ImageDraw.Draw(tile)
  for x0,y0,x1,y1 in boxes:d.rectangle(((x0-originx)*scale_native,(y0-originy)*scale_native,(x1-originx)*scale_native,(y1-originy)*scale_native),outline=v.RUST,width=2*S)
 im.paste(tile,(left,top*S));return im

def make_frame(s,j,scale,cache):
 k=s['key'];start=round(s['start']*30);frame=start+j;setup(scale)
 if 'src' not in cache:
  cache['src']=v.original(k).copy();cache['base'],cache['top'],cache['bottom']=base_plate(k,scale)
 src=cache['src'];base=cache['base'];top=cache['top'];bottom=cache['bottom']
 if k=='O02-A':
  # Hold full work for two seconds, then interpolate native scale and source centre.
  u=max(0,min(1,(j-60)/max(1,s['frames']-61)));initial=min(1,(bottom-top)*scale/src.height)
  limit=float(os.getenv('WOM14_ONI_MAX_SCALE','1'));sc=initial+(limit-initial)*u
  weight=initial/sc*(1-u);cx=src.width*(.5*weight+.455*(1-weight));cy=src.height*(.5*weight+.801*(1-weight))
  span=(src.width*.20*u,src.width*(1-.29*u))
  return affine_art(base,src,sc,cx,cy,top,bottom,span)
 if k=='O02-B':
  # Entire sampling window lies strictly inside honshi, without black surround/ruler.
  b=v.boxpx(k,(.405,.245,.665,.435));art=src.crop(b);sc=min(1,(bottom-top)*scale/art.height)
  return affine_art(base,art,sc,art.width/2,art.height/2,top,bottom)
 z,f,cy,sc,highlight=text_camera(k,s,frame,scale)
 if frame<z:return Image.open(BASE/('en' if s.get('_lang','en')=='en' else 'ja')/s['stages'][0]['file']).convert('RGB')
 xspan=tuple(x*src.width for x in SPAN[k]);cx=sum(xspan)/2
 if frame<f:
  u=(frame-z+1)/(f-z);u=u*u*(3-2*u)
  safe=v.SAFE.get(k,(0,0,1,1));initial=min(1,1840*scale/((safe[2]-safe[0])*src.width),(bottom-top)*scale/((safe[3]-safe[1])*src.height))
  sc=initial+(sc-initial)*u;cx=src.width*(safe[0]+safe[2])/2*(1-u)+cx*u;cy=(safe[1]+safe[3])/2*(1-u)+cy*u
  xspan=(src.width*safe[0]*(1-u)+xspan[0]*u,src.width*safe[2]*(1-u)+xspan[1]*u)
 boxes=[v.boxpx(k,b) for b in v.BOXES[k][highlight]] if frame>=f and highlight>=0 else []
 bounds=[b for stage in v.BOXES[k] for b in stage];clip=None
 if frame>=f:clip=v.boxpx(k,(SPAN[k][0],max(0,min(b[1] for b in bounds)-.015),SPAN[k][1],min(1,max(b[3] for b in bounds)+.015)))
 return affine_art(base,src,sc,cx,cy*src.height,top,bottom,xspan,boxes,clip)

def preview(lang='en',scale=1):
 setup(scale);suffix='_4k' if scale==2 else '';shots=read(BASE/lang/f'records/render_shots{suffix}.json');out=ROOT/lang/'review';out.mkdir(parents=True,exist_ok=True);metrics=[]
 for s in shots:
  if s['key'] not in MODIFIED:continue
  s['_lang']=lang;cache={};positions=[0,min(61,s['frames']-1),s['frames']//2,s['frames']-1]
  if s['key'] in TEXT:positions+= [e['start_frame']-round(s['start']*30) for e in s['stages'] if e['kind']=='source_focus']
  positions=sorted(set(positions));sheet=Image.new('RGB',(1280,math.ceil(len(positions)/2)*385),'#201b17');d=ImageDraw.Draw(sheet)
  for i,j in enumerate(positions):
   im=make_frame(s,j,scale,cache);im.resize((1280,720)).save(out/f'v02_{lang}{suffix}_{s["key"]}_{j}.jpg',quality=91);thumb=im.resize((640,360));sheet.paste(thumb,(i%2*640,i//2*385+25));d.text((i%2*640+6,i//2*385+5),f'{s["key"]} frame {j} (absolute {round(s["start"]*30)+j})',fill='white')
  sheet.thumbnail((1280,1280));sheet.save(out/f'v02_{lang}{suffix}_{s["key"]}_sheet.jpg',quality=88)
  metrics.append(dict(shot=s['key'],scale_native=min(1,SCALES[s['key']]*scale) if s['key'] in TEXT else None,character_cell_height=CELL_NATIVE[s['key']]*min(1,SCALES[s['key']]*scale) if s['key'] in TEXT else None,annotation_gap=(14 if s['key'] in v.NOTES else 9)*scale,art_bottom=905*scale,subtitle_top=932*scale,subtitle_gap=27*scale))
  v.original.cache_clear()
 save(ROOT/lang/f'records/v02_layout{suffix}.json',dict(measurement='Source character cell height (not every irregular brush-stroke ink bounding box)',checks=metrics));print('PREVIEW',lang,scale,flush=True)

def render(lang,scale):
 setup(scale);suffix='_4k' if scale==2 else '';shots=read(BASE/lang/f'records/render_shots{suffix}.json');folder=ROOT/lang/('_work/replacements'+suffix);folder.mkdir(parents=True,exist_ok=True)
 for s in shots:
  if s['key'] not in MODIFIED:continue
  s['_lang']=lang;out=folder/(s['key']+'.mp4');stamp=out.with_suffix('.json');cfg=dict(script=sha(Path(__file__)),scale=scale,lang=lang,frames=s['frames'],oni_max_scale=os.getenv('WOM14_ONI_MAX_SCALE','1'))
  if out.exists() and stamp.exists() and read(stamp)==cfg:continue
  cache={};log=folder/(s['key']+'.log');cmd=['ffmpeg','-y','-nostdin','-v','warning','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{v.W}x{v.H}','-framerate','30','-i','pipe:0','-an','-filter_threads','1','-c:v','libx264','-preset','veryfast','-threads','2','-x264-params','rc-lookahead=5:sync-lookahead=0','-crf','17','-profile:v','high','-pix_fmt','yuv420p','-g','60','-bf','2','-video_track_timescale','15360','-movie_timescale','48000','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709',str(out)]
  with log.open('w') as err:
   p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=err)
   try:
    for j in range(s['frames']):p.stdin.write(make_frame(s,j,scale,cache).tobytes())
    p.stdin.close();assert p.wait()==0
   except BaseException:p.kill();p.wait();raise
  assert not log.read_text().strip(),log.read_text();save(stamp,cfg);v.original.cache_clear();print('RENDERED',lang,scale,s['key'],s['frames'],flush=True)

if __name__=='__main__':
 task=sys.argv[1]
 if task=='prepare':prepare()
 elif task=='preview':preview(sys.argv[2],int(sys.argv[3]))
 elif task=='render':render(sys.argv[2],int(sys.argv[3]))
