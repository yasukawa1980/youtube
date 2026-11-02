"""Claude-approved visual revision. Reuse every v01 narration/music sample."""
import argparse,copy,json,math,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageOps
import wom_shorts_remake_produce as v1
OLD=v1.ROOT
ROOT=OLD.parent/'作り直し_v02_20261102'
read=v1.read;save=v1.save;sha=v1.sha
# Meaningful phrase groups. Vertical bar separates lines; slash separates pages.
LINES={
'A1R':'Who really judged | the dead? / Not Anubis alone. / On this Egyptian papyrus, | the heart is weighed / on a scale. / Anubis weighs. / Thoth, the ibis-headed god, | records the result. / And if the scale balanced, | Osiris received the dead. / Judgment was a scene | with many gods.',
'M1R':'In one of the oldest | accounts of Medusa, / there is no curse. / Around 700 BC, | the poet Hesiod says / she is simply born | a Gorgon, / the only mortal one | of three sisters. / The beautiful young woman | whose hair became snakes / comes later, | from the Roman poet Ovid.',
'P1R':"It was never a box. / In Hesiod's poem, | from around 700 BC, / Pandora lifts the great lid | of a pithos, / a storage jar | like this one. / The box came more than | two thousand years later. / In 1508, | the scholar Erasmus / wrote pyxis, a small box, / and the word stuck.",
'T1R':'Before the long nose, | the first tengu was a star. / In the Nihon Shoki, | finished in 720, / a great star crosses the sky | in 637, / with a sound like thunder. / A monk named Bin says | it is not a falling star. / It is a tengu, | a celestial dog.',
'A3R':'Why does Anubis have | the head of a canine? / One idea, | noted by the museum, / starts in the cemeteries. / Canines roamed | ancient burial grounds / and could disturb the dead. / But a watchful canine | could also be imagined / as their guardian. / It is an interpretation, | not proof.'}
CAPHEIGHT=52 # Exact visible glyph height, same on every line.
F=ImageFont.truetype(str(v1.FONTS/'Arial Narrow Bold.ttf'),192)
def text_size(line):
 b=F.getbbox(line);return round((b[2]-b[0])*CAPHEIGHT/(b[3]-b[1])),CAPHEIGHT

ORIGINAL_TEXT_LAYER=v1.text_layer

def configure():
 v1.ROOT=ROOT
 v1.HEADLINES['M1R']=['MEDUSA WAS BORN','A GORGON']
 v1.SPECS['M1R']=[('A24',None),('A07','Around 700 BC'),('D_timeline','The beautiful young woman')]
 v1.text_layer=text_layer
 v1.splitlines=lambda text:next(ls for pages in page_lines.values() for ls in pages if ' '.join(ls)==text)
 v1.frame_art=frame_art

page_lines={k:[[line.strip() for line in p.split('|')] for p in v.split('/')] for k,v in LINES.items()}

def prepare():
 for d in ['audio','records','assets','review','deliverables','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 for p in (OLD/'audio').glob('*'):
  if p.is_file() and p.suffix in ['.m4a','.wav','.json'] and not (ROOT/'audio'/p.name).exists():shutil.copy2(p,ROOT/'audio'/p.name)
 for p in (OLD/'records').glob('*.json'):
  if p.name not in ['github_draft_release.json','encoding.json','final_qc.json','review_status.json']:shutil.copy2(p,ROOT/'records'/p.name)
 rows=read(OLD/'records/shorts.json')
 for s in rows['shorts']:
  sid=s['id'];groups=[];pos=0
  assert ' '.join(' '.join(x) for x in page_lines[sid])==s['text']
  for lines in page_lines[sid]:
   for line in lines:assert text_size(line)[0]<=764,(sid,line,text_size(line))
   n=len(' '.join(lines).split());groups.append(dict(text=' '.join(lines),word_start=pos,word_end=pos+n));pos+=n
  for i,g in enumerate(groups):
   g['start_frame']=round(s['words_timed'][g['word_start']]['start']*30) if i else 0
   g['end_frame']=round(s['words_timed'][groups[i+1]['word_start']]['start']*30) if i+1<len(groups) else s['cta_start_frame']
  s['caption_groups']=groups
 save(ROOT/'records/shorts.json',rows)
 save(ROOT/'records/v02_approval.json',dict(P1R_seconds=24.733333333333334,P1R_words=49,voice_changed=False,script_changed=False,M1R_headline='MEDUSA WAS BORN A GORGON',M1R_upload_title='In the Oldest Stories, Medusa Was Born a Gorgon'))
 print('PREPARED',flush=True)

def text_layer(lines,kind,sid):
 if not kind.startswith('caption'):return ORIGINAL_TEXT_LAYER(lines,kind,sid)
 layer=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(layer);rows=[]
 for line,y in zip(lines,[1240] if len(lines)==1 else [1198,1294]):
  b=F.getbbox(line);w,h=text_size(line);x=round(480-w/2);box=[x-18,y-20,x+w+18,y+h+20]
  assert box[0]>=80 and box[2]<=880 and box[1]>=1150 and box[3]<=1450
  d.rounded_rectangle(box,16,fill=(0,0,0,173));mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),line,font=F,fill=255);mask=mask.resize((w,h),Image.Resampling.LANCZOS);layer.paste((244,239,223,255),(x,y,x+w,y+h),mask)
  rows.append(dict(text=line,glyph_bbox=[x,y,x+w,y+h],glyph_height=h,font='Arial Narrow Bold.ttf',font_size=192,target_glyph_height=CAPHEIGHT,horizontal_scale=1,scale_method='Uniform isotropic resampling to 52px glyph height; no width-only squeezing',plate_bbox=box,opacity=173/255,padding=18))
 p=ROOT/f'assets/{sid}_{kind}.png';layer.save(p);return p,rows

def view(rect,first=False,top=270,height=830):
 w=rect[2]-rect[0];h=rect[3]-rect[1];scale=min(1000/w,height/h,1.6)
 return [(1080-round(w*scale))//2,top+(height-round(h*scale))//2,round(w*scale),round(h*scale)]

def visuals():
 configure();v1.visuals();m=read(ROOT/'records/visual_manifest.json');rows={s['id']:s for s in read(ROOT/'records/shorts.json')['shorts']};details=[]
 for g in m['shots']:
  sid=g['short_id'];aid=g['asset_id'];s=rows[sid]
  if aid=='met_557657':
   g.update(crop_start=[2000,1250,3020,2097],crop_end=[2200,1325,2830,1848],viewport=[40,285,1000,830],zoom_end=1,native_max_scale=830/523)
   details.append(dict(id=sid,asset=aid,main_crop=[2000,1250,3020,2220],revised_start=g['crop_start'],revised_end=g['crop_end'],cue='Anubis weighs.',note='Balance beam, both pans and kneeling Anubis centered.'))
  elif aid=='D_timeline':
   g['viewport']=[90,270,900,747];g['zoom_end']=1;g['native_max_scale']=.9
   assert g['viewport'][1]+g['viewport'][3]<1030
  elif aid=='A01':
   im=Image.open(g['file']);w,h=im.size;start=[0,0,w,h];end=[350,0,1150,600]
   # Reframe upward so the lid is central when mentioned, retaining a single source.
   key=round(v1.phrase_frame(s,'lifts the great lid'))
   g['keyframes']=[dict(frame=g['start_frame'],rect=start,viewport=g['viewport']),dict(frame=key,rect=end,viewport=[40,600,1000,750]),dict(frame=g['end_frame']-1,rect=[360,0,1160,600],viewport=[40,600,1000,750])];g['zoom_end']=1
  elif aid=='A12':
   im=Image.open(g['source']['path']).convert('RGB');im=ImageOps.colorize(ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=.2),black='#443422',white='#f1e4c7');im.save(g['file']);w,h=im.size
   full=[0,0,w,h];band=[round(v*d) for v,d in zip(g['source']['main']['detail_crop_normalized'],[w,h,w,h])]
   close=[360,1133,990,1287];when=v1.phrase_frame(s,'In 1508')
   g['keyframes']=[dict(frame=g['start_frame'],rect=full,viewport=view(full)),dict(frame=max(g['start_frame']+30,when-30),rect=band,viewport=view(band)),dict(frame=when+15,rect=close,viewport=view(close)),dict(frame=g['end_frame']-1,rect=[560,1133,1190,1287],viewport=view(close))];g['zoom_end']=1
   details.append(dict(id=sid,asset=aid,main_crop=band,keyframes=g['keyframes'],note='Original shows inflected Pixide / Pixidem, not the dictionary form pyxis. Both lie in the main-film detail rectangle.'))
  elif aid=='ndl_1182143_010':
   full=[3900,700,6100,5000];monk=[4400,1400,5020,3350];tengu=[round(v*d) for v,d in zip([.60,.565,.655,.745],[7616,5352,7616,5352])]
   a=v1.phrase_frame(s,'A monk named Bin');b=v1.phrase_frame(s,'It is a tengu')
   g['keyframes']=[dict(frame=g['start_frame'],rect=full,viewport=view(full)),dict(frame=a,rect=monk,viewport=view(monk)),dict(frame=b,rect=tengu,viewport=view(tengu)),dict(frame=g['end_frame']-1,rect=full,viewport=view(full))];g['zoom_end']=1
   details.append(dict(id=sid,asset=aid,main_crop=tengu,keyframes=g['keyframes'],note='九年春二月…大星從東流西 / 時人曰…僧旻曰非流星是天狗也. Original page read visually.'))
  if 'keyframes' in g:
   g['native_max_scale']=max(max(k['viewport'][2]/(k['rect'][2]-k['rect'][0]),k['viewport'][3]/(k['rect'][3]-k['rect'][1])) for k in g['keyframes']);assert g['native_max_scale']<=1.601
 save(ROOT/'records/visual_manifest.json',m);save(ROOT/'records/v02_detail_crops.json',details)
 # Inspect actual frame combinations before encoding.
 preview=[];caps=read(ROOT/'records/caption_manifest.json')
 for s in rows.values():
  sid=s['id'];ns=sorted(set([0,60,s['cta_start_frame']]+[v1.phrase_frame(s,x) for x in {'A1R':['Anubis weighs'],'M1R':['The beautiful young woman'],'P1R':['In 1508','lifts the great lid'],'T1R':['A monk named Bin','It is a tengu'],'A3R':['Canines roamed']}[sid]]))
  for n in ns:
   g=next(x for x in m['shots'] if x['short_id']==sid and x['start_frame']<=n<x['end_frame']);loaded=[Image.open(g[k]).convert(mode) for k,mode in [('file','RGB'),('background','RGB'),('header','RGBA')]];im=frame_art(g,(n-g['start_frame'])/max(1,g['frames']-1),loaded)
   if n<60:im=Image.alpha_composite(im,Image.open(ROOT/f'assets/{sid}_headline.png').convert('RGBA'))
   layer=ROOT/'assets/common_cta.png' if n>=s['cta_start_frame'] else Path(next(c['file'] for c in caps if c['short_id']==sid and c['start_frame']<=n<c['end_frame']))
   im=Image.alpha_composite(im,Image.open(layer).convert('RGBA')).convert('RGB');im.thumbnail((720,1280));p=ROOT/f'review/{sid}_{n:04}_design.jpg';im.save(p,quality=90);preview.append((sid,n,p))
 print('VISUALS V02',len(preview),'design frames',flush=True)

def frame_art(g,frac,loaded):
 im,bg,head=loaded
 if 'keyframes' in g:
  n=g['start_frame']+frac*(g['frames']-1);ks=g['keyframes'];i=min(len(ks)-2,max(0,next((j-1 for j,k in enumerate(ks) if k['frame']>n),len(ks)-2)))
  a,b=ks[i],ks[i+1];t=np.clip((n-a['frame'])/max(1,b['frame']-a['frame']),0,1)
  if g['asset_id']=='ndl_1182143_010':
   ah=a['rect'][3]-a['rect'][1];bh=b['rect'][3]-b['rect'][1];t=ah*t/(bh+(ah-bh)*t)
  rect=np.array(a['rect'])+(np.array(b['rect'])-a['rect'])*t;vp=np.array(a['viewport'])+(np.array(b['viewport'])-a['viewport'])*t;x,y,w,h=map(lambda v:round(float(v)),vp)
 else:
  x,y,w,h=g['viewport'];a=np.array(g['crop_start'],float);b=np.array(g['crop_end'],float);c=a+(b-a)*frac;z=math.exp(math.log(g['zoom_end'])*frac);cx=(c[0]+c[2])/2;cy=(c[1]+c[3])/2;cw=(c[2]-c[0])/z;ch=(c[3]-c[1])/z;rect=[cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2]
 cw=rect[2]-rect[0];ch=rect[3]-rect[1];scale=min(w/cw,h/ch);nw=round(cw*scale);nh=round(ch*scale);x+=round((w-nw)/2);y+=round((h-nh)/2);w,h=nw,nh
 crop=im.transform((w,h),Image.Transform.EXTENT,tuple(rect),Image.Resampling.BICUBIC);frame=bg.copy();frame.paste(crop,(x,y));return Image.alpha_composite(frame.convert('RGBA'),head)

def render(ids):
 configure();v1.render(ids,version='v02')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','visuals','render']);p.add_argument('--ids',default='A1R,M1R,P1R,T1R,A3R');a=p.parse_args()
 if a.stage=='render':render(a.ids.split(','))
 else:globals()[a.stage]()
