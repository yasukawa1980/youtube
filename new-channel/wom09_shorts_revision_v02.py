"""EP009 v02: sentence captions, full-height Mykonos pan; retain original audio/art/CTA."""
import os,json,shutil,re,subprocess,math,argparse
from pathlib import Path
ROOT=Path('/Volumes/ESD-02/新チャンネル/ショート/EP009_v02_20261102')
OLD=ROOT.parent/'EP009_v01_20261102'
os.environ['QO_EP009_ROOT']=str(ROOT)
os.environ['QO_EP009_CONFIG']=str(ROOT/'records/revision_config.json')
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter,ImageEnhance

def read(p):return json.loads(p.read_text())
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def relocate(v):
 if isinstance(v,str):return v.replace(str(OLD),str(ROOT))
 if isinstance(v,list):return [relocate(x) for x in v]
 if isinstance(v,dict):return {k:relocate(x) for k,x in v.items()}
 return v

def prepare():
 assert not ROOT.exists(),'Never overwrite an existing revision'
 for d in ['audio','assets','records','_work','deliverables','review']:(ROOT/d).mkdir(parents=True)
 for p in (OLD/'audio').iterdir():
  if p.is_file():shutil.copy2(p,ROOT/'audio'/p.name)
 for p in (OLD/'assets').iterdir():shutil.copy2(p,ROOT/'assets'/p.name)
 for name in ['narration.json','shorts.json','visual_manifest.json','headlines.json','audio_qc.json','reading_replacements.json']:
  save(ROOT/'records'/name,relocate(read(OLD/'records'/name)))
 for p in (OLD/'records').glob('*_phoneme_timings.json'):shutil.copy2(p,ROOT/'records'/p.name)
 save(ROOT/'records/revision_config.json',dict(version='v02',minimum_line_words=3,request='wom_ショート修正依頼_EP009_v02_20261102.md',exception='T3の7語文と6語節では3語行が必要。文末の境界と原台本を優先。'))
 from wom09_shorts import sha
 rows=read(ROOT/'records/shorts.json');counts={'T1':[8,9,8,9,8],'T2':[8,4,8,4,4,5,4,5,4],'T3':[9,7,5,6,8,8]}
 for s in rows['shorts']:
  words=s['text'].split();groups=[];pos=0
  for n in counts[s['id']]:
   groups.append(dict(text=' '.join(words[pos:pos+n]),word_start=pos,word_end=pos+n));pos+=n
  assert pos==len(words)
  bounds=[0]+[round(s['words_timed'][g['word_start']]['start']*30) for g in groups[1:]]+[s['cta_start_frame']]
  # Give the 4-word "And in its side," page 1.4s, borrowing one frame from the preceding page.
  for i in range(len(groups)-1,0,-1):
   if bounds[i+1]-bounds[i]<42:bounds[i]=bounds[i+1]-42
  for i,g in enumerate(groups):
   g.update(start_frame=bounds[i],end_frame=bounds[i+1]);assert bounds[i+1]-bounds[i]>=42
   assert not any(re.search(r'[.!?]["”]?$',w) for w in g['text'].split()[:-1]),g
  s['caption_groups']=groups
 save(ROOT/'records/shorts.json',rows)
 manifest=read(ROOT/'records/visual_manifest.json')
 prior=read(OLD/'records/render_shots.json')
 for s in manifest['shots']:
  if s['short_id']!='T2':
   old=next(v for v in prior if v['short_id']==s['short_id'] and v['asset_id']==s['asset_id'])
   s.update(preencoded_file=old['encoded_file'],preencoded_sha256=old['encoded_sha256'])
  else:
   s.update(art_box=[0,390,1080,1806],foreground_height_fraction=1416/1920,source_crop_pixels=[315,0,990,885],viewport=[0,270,1080,1536],zoom_start=1.,zoom_end=1.,camera_phases='原寸1.6倍、全高885px。横の切り出しと上下配置を連続補間。11.533秒から車輪、15.067秒から胴の窓。')
   s['source'].update(native_initial_scale=1.6,native_max_scale=1.6)
   manifest['assets']['MYK01']=s['source']
 save(ROOT/'records/visual_manifest.json',manifest)
 # Headline remains Georgia/color/plate, reduced only for T2; clear of neck windows.
 layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer);f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia Bold.ttf',136);top=300;gh=64;gap=78;boxes=[]
 d.rounded_rectangle((80,top-20,700,top+gap+gh+20),radius=16,fill=(0,0,0,173))
 for j,text in enumerate(['WARRIORS IN','THE WINDOWS']):
  b=d.textbbox((0,0),text,font=f);mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),text,font=f,fill=255)
  mask=mask.resize((min(572,round(mask.width*gh/mask.height)),gh),Image.Resampling.LANCZOS);x=390-mask.width//2;y=top+j*gap;layer.paste((244,239,223,255),(x,y,x+mask.width,y+gh),mask);boxes.append(dict(text=text,bbox=[x,y,x+mask.width,y+gh],glyph_height=gh))
 hp=ROOT/'assets/T2_headline.png';layer.save(hp)
 hooks=read(ROOT/'records/headlines.json');h=next(h for h in hooks if h['id']=='T2');h.update(sha256=sha(hp),lines=boxes,overlay_bbox=[80,top-20,700,top+gap+gh+20]);save(ROOT/'records/headlines.json',hooks)
 print('PREPARED v02',flush=True)

# Piecewise cubic Hermite interpolation: continuous position and speed at cue frames.
def camera(n):
 import numpy as np
 keys=[0,346,452,573,647];xs=[315,100,0,120,135];ys=[390,390,270,340,345]
 def spline(vals):
  i=min(len(keys)-2,max(0,int(np.searchsorted(keys,n,side='right'))-1));a,b=keys[i:i+2];u=(n-a)/(b-a)
  slopes=[(vals[1]-vals[0])/(keys[1]-keys[0])]+[(vals[j+1]-vals[j-1])/(keys[j+1]-keys[j-1]) for j in range(1,len(keys)-1)]+[(vals[-1]-vals[-2])/(keys[-1]-keys[-2])]
  # Hold vertical placement before wheels; no overshoot outside full visible height.
  if vals is ys:slopes[0]=slopes[1]=0
  return (2*u**3-3*u*u+1)*vals[i]+(u**3-2*u*u+u)*(b-a)*slopes[i]+(-2*u**3+3*u*u)*vals[i+1]+(u**3-u*u)*(b-a)*slopes[i+1]
 return max(0,min(315,spline(xs)))*1.6,max(270,min(390,spline(ys)))

def encode():
 from wom09_shorts import sha
 manifest=read(ROOT/'records/visual_manifest.json');s=next(s for s in manifest['shots'] if s['short_id']=='T2');im=Image.open(s['source']['path']).convert('RGB');photo=im.resize((1584,1416),Image.Resampling.LANCZOS).convert('RGBA')
 bg=ImageEnhance.Brightness(ImageOps.fit(im,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.4).convert('RGBA');header=Image.open(s['header_file']).convert('RGBA');out=ROOT/'_work/T2_MYK01_v02.mp4'
 cmd=['ffmpeg','-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-video_track_timescale','15360','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',str(out)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE);coords=[]
 for n in range(s['frames']):
  x,y=camera(n);art=photo.transform((1080,1920),Image.Transform.AFFINE,(1,0,x,0,1,-y),Image.Resampling.BICUBIC);frame=Image.alpha_composite(Image.alpha_composite(bg,art),header).convert('RGB');proc.stdin.write(frame.tobytes());coords.append(dict(frame=n,time=n/30,crop_x_native=x/1.6,photo_top=y,scale=1.6))
  if n%150==0:print('MYK FRAME',n,flush=True)
 proc.stdin.close();assert proc.wait()==0
 s.update(preencoded_file=str(out),preencoded_sha256=sha(out));save(ROOT/'records/visual_manifest.json',manifest);save(ROOT/'records/T2_camera_path.json',dict(full_source_height=885,display_height=1416,height_fraction=1416/1920,maximum_scale=1.6,rows=coords))
 print('MYK ENCODED',flush=True)

def audit():
 from wom09_shorts import sha
 from wom01_quiet_origins import stream_hash
 oldrows=read(OLD/'records/shorts.json')['shorts'];rows=read(ROOT/'records/shorts.json')['shorts'];caps=read(ROOT/'records/caption_manifest.json');oldcaps=read(OLD/'records/caption_manifest.json');checks=[]
 for s,o in zip(rows,oldrows):
  sid=s['id'];p=ROOT/f'deliverables/QO_short_EP009_{sid}_v02.mp4';op=OLD/f'deliverables/QO_short_EP009_{sid}_v01.mp4';a=stream_hash(p,'a');b=stream_hash(op,'a');assert a==b
  assert all(s[k]==o[k] for k in ['text','frames','cta_start_frame','cta_text','cta_subtext','native_audio_duration'])
  now=[p for p in caps if p['short_id']==sid and p.get('brand')];before=[p for p in oldcaps if p['short_id']==sid and p.get('brand')]
  assert [{k:v for k,v in p.items() if k!='page'} for p in now]==[{k:v for k,v in p.items() if k!='page'} for p in before]
  groups=s['caption_groups'];cross=sum(any(re.search(r'[.!?]["”]?$',w) for w in g['text'].split()[:-1]) for g in groups);assert cross==0
  exceptions=[dict(text=line,words=len(line.split())) for p in caps if p['short_id']==sid and not p.get('brand') for line in p['lines'] if len(line.split())<4]
  checks.append(dict(id=sid,v01_audio_stream_hash=b,v02_audio_stream_hash=a,audio_identical=True,script_frames_cta_identical=True,cross_sentence_caption_count=cross,minimum_caption_seconds=min((g['end_frame']-g['start_frame'])/30 for g in groups),three_word_line_exceptions=exceptions,caption_list=[dict(text=g['text'],start=g['start_frame']/30,end=g['end_frame']/30) for g in groups]))
 oldshots=read(OLD/'records/render_shots.json');newshots=read(ROOT/'records/render_shots.json');preserved=[]
 for shot in newshots:
  if shot['short_id']=='T2':continue
  prior=next(v for v in oldshots if v['short_id']==shot['short_id'] and v['asset_id']==shot['asset_id'])
  assert all(shot[k]==prior[k] for k in ['start_frame','end_frame','encoded_sha256'])
  assert sha(Path(shot['encoded_file']))==prior['encoded_sha256']
  preserved.append(dict(short=shot['short_id'],asset=shot['asset_id'],sha256=shot['encoded_sha256']))
 path=read(ROOT/'records/T2_camera_path.json');hb=next(h for h in read(ROOT/'records/headlines.json') if h['id']=='T2')['overlay_bbox']
 assert all(270<=r['photo_top'] and r['photo_top']+1416<=1920 and 0<=r['crop_x_native']<=315 for r in path['rows'])
 assert all(r['photo_top']+140*1.6>hb[3] for r in path['rows'][:70])
 save(ROOT/'records/preserved_visuals_qc.json',dict(passed=True,unchanged_shots=preserved,full_height_visible_all_frames=True,neck_windows_below_headline_all_first70_frames=True,neck_window_source_top=140,headline_bbox=hb))
 assert all(not r['three_word_line_exceptions'] for r in checks if r['id']!='T3')
 assert len(next(r for r in checks if r['id']=='T3')['three_word_line_exceptions'])==3
 save(ROOT/'records/revision_qc.json',dict(passed=True,rows=checks,exception_reason='文末分離・台本不変が優先。T3の7語文は3+4、6語節は3+3。その他は4〜5語/行。T1/T3の字幕なし中間動画はv01のSHA一致ファイルをそのまま使用。'))
 print('REVISION AUDIT passed',flush=True)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','encode','audit']);globals()[p.parse_args().stage]()
