"""EP009の字幕と最後の案内へ、実レンダー寸法に基づく黒い下地を付ける。"""
import numpy as np
from PIL import Image,ImageFilter
import subprocess
import imageio_ffmpeg
from wom09_shorts import ROOT,save
BIN=imageio_ffmpeg.get_ffmpeg_exe()
RADIUS=16
def ass_frame(ass,out,color='black'):
 subprocess.run([BIN,'-nostdin','-y','-v','error','-f','lavfi','-i',f'color=c={color}:s=1080x1920:r=30:d=0.1','-vf',f"ass='{ass}'",'-frames:v','1','-pix_fmt','rgb24',str(out)],check=True)

def single_event_ass(source,dialogue,path):
 prefix=source.split('[Events]')[0]
 fields=dialogue.split(',',9);fields[1]='0:00:00.00';fields[2]='0:00:01.00'
 path.write_text(prefix+'[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'+','.join(fields)+'\n')

def line_masks(image,count):
 rgb=np.asarray(image.convert('RGB'));ink=rgb.max(axis=2)>10;ys=np.where(ink.any(axis=1))[0];assert len(ys)
 if count==1:ranges=[(ys.min(),ys.max()+1)]
 else:
  assert count==2;cy=np.where((np.abs(rgb.astype(np.int16)-np.array([244,240,223])).max(axis=2)<=3).any(axis=1))[0];gaps=np.diff(cy);k=int(np.argmax(gaps));assert gaps[k]>=3
  split=(int(cy[k])+int(cy[k+1]))//2;ranges=[(int(ys.min()),split+1),(split+1,int(ys.max()+1))]
 core=(np.abs(rgb.astype(np.int16)-np.array([244,240,223])).max(axis=2)<=3)
 core=np.asarray(Image.fromarray(np.uint8(core)*255).filter(ImageFilter.MinFilter(3)))>0
 result=[]
 for ya,yb in ranges:
  m=np.zeros_like(ink);m[ya:yb]=ink[ya:yb];yy,xx=np.where(m);assert len(xx)
  c=np.zeros_like(core);c[ya:yb]=core[ya:yb];assert c.sum()>20
  result.append({'bbox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],'ink':m,'core':c})
 return result

def rounded_path(box,origin):
 x0,y0,x1,y1=box;x0-=origin[0];x1-=origin[0];y0-=origin[1];y1-=origin[1];r=RADIUS;k=r*.55228475
 vals=[('m',[x0+r,y0]),('l',[x1-r,y0]),('b',[x1-r+k,y0,x1,y0+r-k,x1,y0+r]),('l',[x1,y1-r]),('b',[x1,y1-r+k,x1-r+k,y1,x1-r,y1]),('l',[x0+r,y1]),('b',[x0+r-k,y1,x0,y1-r+k,x0,y1-r]),('l',[x0,y0+r]),('b',[x0,y0+r-k,x0+r-k,y0,x0+r,y0])]
 return ' '.join(cmd+' '+' '.join(str(round(v)) for v in points) for cmd,points in vals)+' c'

def add_backplates(path,pages):
 source=path.read_text();events=[x for x in source.splitlines() if x.startswith('Dialogue:')];assert len(events)==len(pages)
 style='Style: Plate,Arial,10,&H52000000,&H52000000,&H52000000,&H52000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1'
 modified=source.replace('[Events]',style+'\n[Events]');plates=[];records=[]
 (ROOT/'_work/masks').mkdir(parents=True,exist_ok=True)
 for p,event in zip(pages,events):
  stem=f'{p["short_id"]}_{p["page"]:02d}';ass=ROOT/f'_work/masks/{stem}_text.ass';single_event_ass(source,event,ass);png=ass.with_suffix('.png');ass_frame(ass,png)
  masks=line_masks(Image.open(png),len(p['lines']));boxes=[[x0-20,y0-20,x1+20,y1+20] for x0,y0,x1,y1 in [m['bbox'] for m in masks]]
  assert all(80<=b[0]<b[2]<=880 and 1150<=b[1]<b[3]<=1450 for b in boxes),(p,boxes)
  origin=[min(b[0] for b in boxes),min(b[1] for b in boxes)];vector=' '.join(rounded_path(b,origin) for b in boxes);fields=event.split(',',9)
  plate=f'Dialogue: 0,{fields[1]},{fields[2]},Plate,,0,0,0,,{{\\an7\\pos({origin[0]},{origin[1]})\\bord0\\shad0\\p1}}{vector}'
  plates.append(plate);pa=ROOT/f'_work/masks/{stem}_plate.ass';single_event_ass(modified,plate,pa);pp=pa.with_suffix('.png');ass_frame(pa,pp,'white');flat=np.asarray(Image.open(pp).convert('RGB')).max(axis=2)<=86
  for j,(m,box) in enumerate(zip(masks,boxes),1):
   assert np.all(flat[m['core']]);dest=ROOT/f'_work/masks/{stem}_line{j}.npz';np.savez_compressed(dest,ink=m['ink'],core=m['core'],flat=flat)
   records.append(dict(short_id=p['short_id'],page=p['page'],line=j,text=p['lines'][j-1],brand=p.get('brand',False),start_frame=p['start_frame'],end_frame=p['end_frame'],middle_frame=(p['start_frame']+p['end_frame']-1)//2,text_bbox=m['bbox'],plate_bbox=box,padding=20,corner_radius=16,opacity=173/255,mask=str(dest.relative_to(ROOT))))
 marker='Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n';modified=modified.replace(marker,marker+'\n'.join(plates)+'\n');path.write_text(modified)
 save(ROOT/f'records/{pages[0]["short_id"]}_backplates.json',records)
