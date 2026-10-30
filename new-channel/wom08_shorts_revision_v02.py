"""第8話ショートv02。字幕の黒い下地とK2見出しの板だけを変更する。"""
import os,math,copy,json,re,shutil,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter
from wom01_multilingual_render import read,save,sha,ff
from wom01_quiet_origins import stream_hash
import imageio_ffmpeg
REPO=Path(__file__).resolve().parent.parent
ROOT=Path('/Users/ryo/Desktop/新チャンネル/ショート/EP008_v02_20261030')
OLD=ROOT.parent/'EP008_v01_20261030'
FPS=30;PADDING=20;RADIUS=16;PLATE_ALPHA_ASS='52';PLATE_OPACITY=173/255
BIN=imageio_ffmpeg.get_ffmpeg_exe()

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

def prepare():
 for d in ['records','assets','review','deliverables','_work/masks']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 for name in ['shorts.json','caption_manifest.json','narration.json','reading_replacements.json','script_approval.json','asset_usage.json','audio_qc.json','render_shots.json','headlines.json','safe_crop_qc.json']:
  shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
 for p in (OLD/'deliverables').iterdir():
  if p.suffix in ['.srt','.txt','.csv','.md'] and p.name!='SHA256SUMS_shared.txt':
   dest=ROOT/'deliverables'/p.name.replace('_v01.','_v02.');shutil.copy2(p,dest);assert sha(p)==sha(dest)
 rows=read(ROOT/'records/shorts.json')['shorts'];pages=read(ROOT/'records/caption_manifest.json');plate_records=[];heads=read(OLD/'records/headlines.json')
 for s in rows:
  sid=s['id'];source=(OLD/f'_work/{sid}.ass').read_text();events=[x for x in source.splitlines() if x.startswith('Dialogue:')];group=[x for x in pages if x['short_id']==sid];assert len(events)==len(group)
  style='Style: Plate,Arial,10,&H52000000,&H52000000,&H52000000,&H52000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1'
  modified=source.replace('[Events]',style+'\n[Events]');plate_events=[]
  for p,event in zip(group,events):
   stem=f'{sid}_{p["page"]:02d}';ass=ROOT/f'_work/masks/{stem}_text.ass';single_event_ass(source,event,ass);png=ass.with_suffix('.png');ass_frame(ass,png)
   masks=line_masks(Image.open(png),len(p['lines']));boxes=[[x0-PADDING,y0-PADDING,x1+PADDING,y1+PADDING] for x0,y0,x1,y1 in [m['bbox'] for m in masks]]
   assert all(0<=b[0]<b[2]<=1080 and 0<=b[1]<b[3]<=1920 for b in boxes)
   origin=[min(b[0] for b in boxes),min(b[1] for b in boxes)]
   vector=' '.join(rounded_path(b,origin) for b in boxes);fields=event.split(',',9)
   plate=f'Dialogue: 0,{fields[1]},{fields[2]},Plate,,0,0,0,,{{\\an7\\pos({origin[0]},{origin[1]})\\bord0\\shad0\\p1}}{vector}'
   plate_events.append(plate)
   white_ass=ROOT/f'_work/masks/{stem}_plate.ass';single_event_ass(modified,plate,white_ass);white=white_ass.with_suffix('.png');ass_frame(white_ass,white,'white');wrgb=np.asarray(Image.open(white).convert('RGB'));flat=wrgb.max(axis=2)<=86
   for mask in masks:assert np.all(flat[mask['core']]),(sid,p['page'],'板が文字を覆っていない')
   for j,(mask,box) in enumerate(zip(masks,boxes),1):
    q=ROOT/f'_work/masks/{stem}_line{j}.npz';np.savez_compressed(q,ink=mask['ink'],core=mask['core'],flat=flat)
    plate_records.append({'short_id':sid,'page':p['page'],'line':j,'text':p['lines'][j-1],'brand':p.get('brand',False),'start_frame':p['start_frame'],'end_frame':p['end_frame'],'middle_frame':(p['start_frame']+p['end_frame']-1)//2,'text_bbox':mask['bbox'],'plate_bbox':box,'padding':PADDING,'corner_radius':RADIUS,'opacity':PLATE_OPACITY,'mask':str(q.relative_to(ROOT))})
  # 同じレイヤーの先頭に描き、元の文字イベントより下へ板を置く。
  event_marker='Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'
  modified=modified.replace(event_marker,event_marker+'\n'.join(plate_events)+'\n')
  assert [x for x in modified.splitlines() if x.startswith('Dialogue:') and ',Main,' in x]==events
  (ROOT/f'_work/{sid}.ass').write_text(modified)
  hook=next(h for h in heads if h['id']==sid);im=Image.open(hook['file']).convert('RGBA');a=np.asarray(im).copy();original=a.copy()
  if sid=='K2':
   alpha=a[:,:,3].astype(float);present=alpha>=125;alpha[present]=217+(255-217)*(alpha[present]-125)/(255-125);a[:,:,3]=np.uint8(np.rint(alpha));assert np.array_equal(a[:,:,:3],original[:,:,:3]);assert np.array_equal(a[:,:,3][original[:,:,3]==255],original[:,:,3][original[:,:,3]==255])
  hp=ROOT/f'assets/{sid}_headline.png';Image.fromarray(a).save(hp);hook.update(file=str(hp),sha256=sha(hp),background_opacity=217/255 if sid=='K2' else 125/255,rgb_identical_to_v01=True,opaque_glyph_alpha_identical_to_v01=True)
 save(ROOT/'records/headlines.json',heads);save(ROOT/'records/subtitle_backplates.json',{'opacity':PLATE_OPACITY,'padding':PADDING,'radius':RADIUS,'rows':plate_records,'original_ASS_dialogues_byte_identical':True,'measurement_plan':'全字幕イベントの中央フレームを先頭から連続デコードし、各行の文字の内部画素とすぐ周囲の下地画素の相対輝度を比較する。'})
 save(ROOT/'records/revision_request_v02.json',{'request':'new-channel/wom_ショート修正依頼_EP008_v02_20261030.md','request_sha256':sha(REPO/'new-channel/wom_ショート修正依頼_EP008_v02_20261030.md'),'base_release_id':428689871,'scope':'字幕行の黒い半透明板とK2の見出し板の濃さのみ','audio_regenerated':False,'new_ai_visual_assets':False})
 print('BACKPLATES READY',len(plate_records),'lines',flush=True)

def render():
 rows=read(ROOT/'records/shorts.json')['shorts'];shots=read(ROOT/'records/render_shots.json');heads=read(ROOT/'records/headlines.json');records=[]
 for row in rows:
  sid=row['id'];group=[s for s in shots if s['short_id']==sid];hp=next(h['file'] for h in heads if h['id']==sid);ass=ROOT/f'_work/{sid}.ass';out=ROOT/f'deliverables/QO_short_EP008_{sid}_v02.mp4'
  cmd=[BIN,'-nostdin','-y','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s','1080x1920','-r','30','-i','pipe:0','-i',str(OLD/f'audio/{sid}_final.m4a'),'-loop','1','-framerate','30','-i',hp,'-filter_complex_threads','2','-filter_complex',f"[2:v]format=rgba,fade=t=out:st=2:d=0.3:alpha=1[h];[0:v][h]overlay=0:0:enable='lt(t,2.3)'[t];[t]ass='{ass}'[v]",'-map','[v]','-map','1:a:0','-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-profile:v','high','-frames:v',str(row['frames']),'-fps_mode','passthrough','-video_track_timescale','15360','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-c:a','copy','-movflags','+faststart',str(out)]
  with (ROOT/f'records/{sid}_encode.log').open('w') as log:
   enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
   try:
    for s in group:
     assert sha(Path(s['encoded_file']))==s['encoded_sha256'];subprocess.run(['ffmpeg','-nostdin','-v','warning','-threads','2','-i',s['encoded_file'],'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
    enc.stdin.close();assert enc.wait()==0
   except BaseException:enc.kill();enc.wait();raise
  assert stream_hash(out,'a')==stream_hash(OLD/f'deliverables/QO_short_EP008_{sid}_v01.mp4','a')
  records.append({'id':sid,'command':cmd,'video_sha256':sha(out),'shot_sources':[{'path':s['encoded_file'],'sha256':s['encoded_sha256']} for s in group]});print('V02 RENDERED',sid,flush=True)
 save(ROOT/'records/encoding_method.json',{'method':'v01の個別ショットを同じ順・時刻で独立デコードし、非圧縮フレームから各1エンコーダー。元のASS文字イベントを維持して黒い下地だけ追加。','shorts':records})

if __name__=='__main__':
 import sys
 globals()[sys.argv[1]]()
