"""Measure final v03 format, every pre-CTA frame, audio identity and glyph contrast."""
import csv,json,subprocess,math,argparse
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from wom09_shorts_revision_v03 import ROOT,OLD,read,save,sha
from wom09_shorts_visual_qc import decode,lum
from wom01_quiet_origins import stream_hash
from wom_shorts_produce import levels

def frame_hashes(p,n):
 text=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(p),'-map','0:v:0','-frames:v',str(n),'-pix_fmt','yuv420p','-f','framemd5','-'],text=True)
 return [line.split(',')[-1].strip() for line in text.splitlines() if not line.startswith('#')]

def raw_selected(p,indices):
 expr='+'.join(f'eq(n\\,{n})' for n in indices)
 return subprocess.Popen(['ffmpeg','-nostdin','-v','error','-i',str(p),'-vf',f'select={expr}','-fps_mode','passthrough','-pix_fmt','yuv420p','-f','rawvideo','-'],stdout=subprocess.PIPE)

def compare(s,p):
 old=OLD/f'deliverables/QO_short_EP009_{s["id"]}_v02.mp4';n=s['cta_start_frame'];a=frame_hashes(old,n);b=frame_hashes(p,n);assert len(a)==len(b)==n
 changed=[i for i in range(n) if a[i]!=b[i]];diff=[]
 if changed:
  pa,pb=raw_selected(old,changed),raw_selected(p,changed)
  for i in changed:
   x=pa.stdout.read(1080*1920*3//2);y=pb.stdout.read(1080*1920*3//2);assert len(x)==len(y)==1080*1920*3//2
   delta=np.abs(np.frombuffer(x,np.uint8).astype(np.int16)-np.frombuffer(y,np.uint8).astype(np.int16));diff.append(dict(frame=i,seconds=i/30,mean_absolute_yuv_difference=float(delta.mean()),maximum_component_difference=int(delta.max()),changed_components=int(np.count_nonzero(delta))))
  assert pa.wait()==pb.wait()==0
 ah,bh=stream_hash(old,'a'),stream_hash(p,'a');assert ah==bh
 return dict(id=s['id'],compared_frames=n,pixel_identical_frames=n-len(changed),changed_frames=len(changed),first_changed_frame=changed[0] if changed else None,last_changed_frame=changed[-1] if changed else None,mean_absolute_difference_all_pre_cta_frames=sum(x['mean_absolute_yuv_difference'] for x in diff)/n,maximum_component_difference=max([x['maximum_component_difference'] for x in diff],default=0),changed_rows=diff,v02_audio_hash=ah,v03_audio_hash=bh,audio_identical=True,exact_pixel_equality=not changed,user_authorized_recompression=True)

def sheet(sid,kind,ns,frames):
 folder=ROOT/f'review/{sid}_{kind}';folder.mkdir(exist_ok=True);tiles=[]
 for n in ns:
  im=Image.fromarray(frames[n]);im.thumbnail((720,1280));p=folder/f'{n:04d}.jpg';im.save(p,quality=92,optimize=True);assert p.stat().st_size<1000000;tiles.append(im)
 cols=min(5,len(ns));out=Image.new('RGB',(cols*240,math.ceil(len(ns)/cols)*448),'#0c1820');d=ImageDraw.Draw(out);f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
 for i,(im,n) in enumerate(zip(tiles,ns)):
  x=i%cols*240;y=i//cols*448;out.paste(im.resize((240,427)),(x,y));d.text((x+5,y+427),f'{sid} {n/30:.2f}s',font=f,fill='white')
 out.thumbnail((1280,1280));out.save(ROOT/f'review/{sid}_{kind}.jpg',quality=92,optimize=True)

def main(ids):
 media=[];comparisons=[];narration=[];ctas=[];design=read(ROOT/'records/cta_design.json');layer=np.asarray(Image.open(ROOT/'assets/cta_v03.png'))
 masks=[np.asarray(Image.open(ROOT/f'assets/cta_mask_{i}.png')) for i in range(3)]
 for s in read(OLD/'records/shorts.json')['shorts']:
  sid=s['id']
  if sid not in ids:
   m=next(m for m in read(ROOT/'records/media_qc.json')['rows'] if m['id']==sid);assert sha(m['file'])==m['sha256'];media.append(m)
   comparisons.append(next(r for r in read(ROOT/'records/unchanged_frames_qc.json')['rows'] if r['id']==sid))
   previous=read(ROOT/'records/contrast_qc.json');narration.extend(r for r in previous['narration'] if r['id']==sid);ctas.extend(r for r in previous['cta'] if r['id']==sid);continue
  p=ROOT/f'deliverables/QO_short_EP009_{sid}_v03.mp4';cmp=compare(s,p);comparisons.append(cmp);print('COMPARE',sid,cmp['changed_frames'],'of',cmp['compared_frames'],'MAE',cmp['mean_absolute_difference_all_pre_cta_frames'],flush=True)
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(v for v in info['streams'] if v['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],v['pix_fmt'],v['profile'],int(v['nb_frames']))==(1080,1920,'30/1','yuv420p','High',s['frames'])
  dec=subprocess.run(['ffmpeg','-nostdin','-v','warning','-i',str(p),'-f','null','-'],capture_output=True,text=True,check=True);assert not dec.stderr.strip(),dec.stderr
  pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert pts==list(range(0,s['frames']*512,512))
  q=levels(p);assert abs(float(q['input_i'])+14)<.15 and float(q['input_tp'])<=-1
  media.append(dict(id=sid,file=str(p),sha256=sha(p),bytes=p.stat().st_size,frames=s['frames'],duration=s['frames']/30,width=1080,height=1920,fps=30,profile=v['profile'],pixel_format=v['pix_fmt'],continuous_decode_warnings=0,exact_pts=True,lufs=float(q['input_i']),true_peak=float(q['input_tp']),audio_identical_to_v02=True,cta_start=s['cta_start'],cta_end=s['frames']/30))
  group=[r for r in read(OLD/f'records/{sid}_backplates.json') if not r['brand']];ns=sorted(set([0,15,30,45,60,75]+list(range(0,s['frames'],60))+[s['cta_start_frame']-1,s['cta_start_frame'],s['cta_start_frame']+6,s['frames']-1]+[r['middle_frame'] for r in group]));frames=decode(p,ns);page_masks={}
  for r in group:
   m=np.load(OLD/r['mask']);page_masks.setdefault(r['page'],np.zeros((1920,1080),bool));page_masks[r['page']]|=m['ink']
  for r in group:
   m=np.load(OLD/r['mask']);ink=m['ink'];outer=np.asarray(Image.fromarray(ink.astype('uint8')*255).filter(ImageFilter.MaxFilter(19)))>0;excluded=np.asarray(Image.fromarray(page_masks[r['page']].astype('uint8')*255).filter(ImageFilter.MaxFilter(7)))>0;ring=outer & ~excluded & m['flat'];l=lum(frames[r['middle_frame']]);ratio=(float(l[m['core']].min())+.05)/(float(l[ring].max())+.05);assert ratio>=4.5,(sid,r['text'],ratio);narration.append(dict(id=sid,text=r['text'],frame=r['middle_frame'],ratio=ratio))
  for n in [s['cta_start_frame'],s['frames']-1]:
   l=lum(frames[n])
   for i,(mask,d) in enumerate(zip(masks,design['rows'])):
    ink=mask>10;core=np.asarray(Image.fromarray(np.uint8(mask>=252)*255).filter(ImageFilter.MinFilter(3)))>0
    outer=np.asarray(Image.fromarray(np.uint8(ink)*255).filter(ImageFilter.MaxFilter(19)))>0;exclude=np.asarray(Image.fromarray(np.uint8(ink)*255).filter(ImageFilter.MaxFilter(7)))>0
    flat=layer[:,:,3]==(235 if i<2 else 173);ring=outer & ~exclude & flat;assert ring.sum()>50
    if i<2:ratio=(float(l[ring].min())+.05)/(float(l[core].max())+.05)
    else:ratio=(float(l[core].min())+.05)/(float(l[ring].max())+.05)
    assert ratio>=4.5,(sid,n,d['text'],ratio)
    ctas.append(dict(id=sid,frame=n,text=d['text'],glyph_height=d['glyph_height'],glyph_bbox=d['glyph_bbox'],plate_bbox=d['plate_bbox'],ratio=ratio))
  for kind,indices in [('opening',[0,15,30,45,60,75]),('every2s',list(range(0,s['frames'],60))),('CTA',[s['cta_start_frame'],s['frames']-1]),('CTA_transition',[s['cta_start_frame']-1,s['cta_start_frame'],s['cta_start_frame']+6])]:sheet(sid,kind,indices,frames)
  print('QC',sid,'CTA minimum',min(x['ratio'] for x in ctas if x['id']==sid),flush=True)
 save(ROOT/'records/media_qc.json',dict(passed=True,rows=media))
 save(ROOT/'records/unchanged_frames_qc.json',dict(comparison_space='decoded 8-bit YUV420p; all pre-CTA frames',authorization='2026-11-02 本人：通常の投稿形式を優先し、再圧縮による微小な差は記録する',rows=comparisons))
 save(ROOT/'records/contrast_qc.json',dict(passed=True,narration=narration,cta=ctas,method='実動画の収縮した文字内部と隣接下地の保守的コントラスト。語り全字幕行は中央フレーム、案内全3行は開始/最終フレームで測定。'))
 with (ROOT/'deliverables/unchanged_frames.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['id','frame','seconds','mean_absolute_yuv_difference','maximum_component_difference','changed_components']);w.writeheader()
  for r in comparisons:
   for d in r['changed_rows']:w.writerow(dict(id=r['id'],**d))
 print('ALL QC PASSED',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ids',default='T1,T2,T3');main(p.parse_args().ids.split(','))
