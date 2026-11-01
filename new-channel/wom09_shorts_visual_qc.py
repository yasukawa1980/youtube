"""EP009の全字幕・見出し・最後の案内を実動画の画素で検証する。"""
import json,csv,subprocess,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from wom09_shorts import ROOT,save,sha
from wom_shorts_produce import read
def lum(a):
 a=a.astype(float)/255;a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);return a@np.array([.2126,.7152,.0722])
def decode(p,indices):
 expr='+'.join(f'eq(n\\,{n})' for n in indices)
 proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-i',str(p),'-vf',f'select={expr}','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 out={}
 for n in indices:
  b=proc.stdout.read(1080*1920*3);assert len(b)==1080*1920*3;out[n]=np.frombuffer(b,np.uint8).reshape(1920,1080,3).copy()
 assert proc.stdout.read()==b'';err=proc.stderr.read();assert proc.wait()==0 and not err,err
 return out

def main():
 contrasts=[];heads=[];cta=[];pictures=[]
 for s in read(ROOT/'records/shorts.json')['shorts']:
  sid=s['id'];group=read(ROOT/f'records/{sid}_backplates.json');indices=sorted(set([0,15,30,45,60,75]+list(range(0,s['frames'],60))+[r['middle_frame'] for r in group]+[s['cta_start_frame'],s['frames']-1]));frames=decode(ROOT/f'deliverables/QO_short_EP009_{sid}_v01.mp4',indices)
  page_masks={}
  for r in group:
   m=np.load(ROOT/r['mask']);page_masks.setdefault(r['page'],np.zeros((1920,1080),bool));page_masks[r['page']]|=m['ink']
  for r in group:
   m=np.load(ROOT/r['mask']);ink=m['ink'];outer=np.asarray(Image.fromarray(ink.astype('uint8')*255).filter(ImageFilter.MaxFilter(19)))>0;excluded=np.asarray(Image.fromarray(page_masks[r['page']].astype('uint8')*255).filter(ImageFilter.MaxFilter(7)))>0;ring=outer & ~excluded & m['flat'];assert ring.sum()>50
   l=lum(frames[r['middle_frame']]);low=float(l[m['core']].min());high=float(l[ring].max());ratio=(low+.05)/(high+.05)
   contrasts.append({k:v for k,v in r.items() if k!='mask'}|dict(contrast_ratio=ratio,minimum_text_luminance=low,maximum_adjacent_background_luminance=high,passed=ratio>=4.5));assert ratio>=4.5,(sid,r['text'],ratio)
  hook=next(h for h in read(ROOT/'records/headlines.json') if h['id']==sid);arr=np.array(Image.open(hook['file']).convert('RGBA'));ink=arr[:,:,3]>174;solid=(np.abs(arr[:,:,:3].astype(int)-np.array([244,239,223])).max(axis=2)<=3)&(arr[:,:,3]>=252);core=np.asarray(Image.fromarray(np.uint8(solid)*255).filter(ImageFilter.MinFilter(3)))>0;ring=(np.asarray(Image.fromarray(np.uint8(ink)*255).filter(ImageFilter.MaxFilter(19)))>0)&~(np.asarray(Image.fromarray(np.uint8(ink)*255).filter(ImageFilter.MaxFilter(7)))>0)&(arr[:,:,3]==173)
  l=lum(frames[0]);ratio=(float(l[core].min())+.05)/(float(l[ring].max())+.05);heads.append(dict(id=sid,text=hook['text'],contrast_ratio=ratio,passed=ratio>=4.5));assert ratio>=4.5,(sid,'headline',ratio)
  assert s['cta_start']>=s['native_audio_duration']>=s['last_voice_activity_seconds'];assert abs(s['duration_seconds']-s['cta_start']-2.5)<1e-8
  cta.append(dict(id=sid,last_voice_activity=s['last_voice_activity_seconds'],native_end=s['native_audio_duration'],cta_start=s['cta_start'],cta_end=s['duration_seconds'],cta_duration=2.5,no_voice_overlap=True))
  shots=[x for x in read(ROOT/'records/render_shots.json') if x['short_id']==sid];assert not shots[-1]['asset_id'].startswith('D_');tail=sum(max(0,g['end_frame']-max(g['start_frame'],s['frames']-300)) for g in shots if not g['asset_id'].startswith('D_'));assert tail>=45
  pictures.append(dict(id=sid,art_seconds_in_last10=tail/30,last_asset=shots[-1]['asset_id'],through_end=True))
  for kind,ns in [('opening',[0,15,30,45,60,75]),('every2s',list(range(0,s['frames'],60))),('CTA',[s['cta_start_frame'],s['frames']-1])]:
   tiles=[];folder=ROOT/f'review/{sid}_{kind}';folder.mkdir(exist_ok=True)
   for n in ns:
    im=Image.fromarray(frames[n]);im.thumbnail((720,1280));dest=folder/f'{n:04d}.jpg';im.save(dest,quality=90,optimize=True);assert dest.stat().st_size<1000000;tiles.append(im)
   tw=240;th=448;cols=min(5,len(tiles));sheet=Image.new('RGB',(cols*tw,math.ceil(len(tiles)/cols)*th),'#0c1820');d=ImageDraw.Draw(sheet);f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
   for i,(im,n) in enumerate(zip(tiles,ns)):
    x=i%cols*tw;y=i//cols*th;sheet.paste(im.resize((240,427)),(x,y));d.text((x+5,y+427),f'{sid} {n/30:.2f}s',font=f,fill='white')
   sheet.thumbnail((1280,1280));sheet.save(ROOT/f'review/{sid}_{kind}.jpg',quality=92,optimize=True)
  print('VISUAL QC',sid,'caption contrast',min(r['contrast_ratio'] for r in contrasts if r['short_id']==sid),'headline',ratio,flush=True)
 save(ROOT/'records/contrast_qc.json',dict(passed=True,minimum=min(r['contrast_ratio'] for r in contrasts),rows=contrasts,headline=heads,method='全字幕行（CTA含む）の中央フレームを先頭から連続デコード。収縮した字の内部の最小輝度と、直近下地の最大輝度の比。見出しは0フレームで同様に実測。'))
 save(ROOT/'records/cta_qc.json',dict(passed=True,rows=cta,picture_tails=pictures))
 with (ROOT/'deliverables/subtitle_contrast.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(contrasts[0]));w.writeheader();w.writerows(contrasts)
if __name__=='__main__':main()
