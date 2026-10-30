"""第8話ショートv02の差分・全編・字幕コントラスト・比較画像を検証する。"""
import csv,json,subprocess,math,inspect
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from wom08_shorts_revision_v02 import ROOT,OLD,read,save,sha,stream_hash
from wom_shorts_produce import levels
FONT=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
def video(root,sid,v):return root/f'deliverables/QO_short_EP008_{sid}_{v}.mp4'
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

def pair(a,b,label,path,crop=None):
 ims=[Image.fromarray(x).crop(crop) if crop else Image.fromarray(x) for x in [a,b]]
 w=640;h=round(ims[0].height*w/ims[0].width);canvas=Image.new('RGB',(1280,h+65),'#0c1820');d=ImageDraw.Draw(canvas)
 for i,im in enumerate(ims):canvas.paste(im.resize((w,h),Image.Resampling.LANCZOS),(i*w,65));d.text((i*w+15,12),f'{label}   '+['v01','v02'][i],font=FONT,fill='#f4efdf')
 canvas.save(path,quality=88,optimize=True);assert path.stat().st_size<1000000
 return canvas

def main():
 rows=read(ROOT/'records/shorts.json')['shorts'];plates=read(ROOT/'records/subtitle_backplates.json')['rows'];media=[];contrasts=[];comparisons=[]
 for name in ['shorts.json','caption_manifest.json','narration.json','reading_replacements.json','script_approval.json','render_shots.json','audio_qc.json']:
  assert sha(ROOT/'records'/name)==sha(OLD/'records'/name),name
 for s in read(ROOT/'records/render_shots.json'):assert sha(Path(s['encoded_file']))==s['encoded_sha256']
 for s in rows:
  sid=s['id'];p=video(ROOT,sid,'v02');before=video(OLD,sid,'v01')
  r=subprocess.run(['ffmpeg','-nostdin','-v','warning','-i',str(p),'-f','null','-'],capture_output=True,check=True);assert not r.stderr.strip(),r.stderr
  info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(x for x in info['streams'] if x['codec_type']=='video')
  assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']),v['profile'],v['pix_fmt'])==(1080,1920,'30/1',s['frames'],'High','yuv420p')
  fi=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=width,height,pix_fmt','-of','json',str(p)]))['frames'];assert len(fi)==s['frames'] and {(f['width'],f['height'],f['pix_fmt']) for f in fi}=={(1080,1920,'yuv420p')}
  pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert v['time_base']=='1/15360' and pts==list(range(0,s['frames']*512,512))
  ah=stream_hash(p,'a');assert ah==stream_hash(before,'a');q=levels(p);assert abs(float(q['input_i'])+14)<.15 and float(q['input_tp'])<=-1
  media.append({'id':sid,'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'frames':s['frames'],'duration_seconds':float(info['format']['duration']),'video_duration_seconds':s['frames']/30,'lufs':float(q['input_i']),'true_peak_dbtp':float(q['input_tp']),'continuous_decode_warnings':0,'single_frame_format':True,'exact_pts_30fps':True,'audio_stream_identical_to_v01':True,'audio_stream_sha256':ah})
  group=[r for r in plates if r['short_id']==sid];opening=[0,15,30,45,60,75];every=list(range(0,s['frames'],60));indices=sorted(set(opening+every+[r['middle_frame'] for r in group]));old=decode(before,indices);new=decode(p,indices)
  outdir=ROOT/f'review/{sid}';outdir.mkdir(exist_ok=True)
  for kind,ns in [('opening',opening),('every2s',every)]:
   tiles=[]
   for n in ns:
    dest=outdir/f'{kind}_{n:04d}.jpg';im=pair(old[n],new[n],f'{sid} {n/30:.2f}s',dest);tiles.append(im);comparisons.append({'id':sid,'kind':kind,'frame':n,'seconds':n/30,'file':str(dest.relative_to(ROOT)),'sha256':sha(dest)})
   # 各セルは左右がv01/v02。個別比較画像を別途保存する。
   cols=3;tw=426;th=round(tiles[0].height*tw/1280);sheet=Image.new('RGB',(1278,math.ceil(len(tiles)/cols)*th),'#0c1820')
   for i,im in enumerate(tiles):sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(i%cols*tw,i//cols*th))
   sheet.thumbnail((1280,1280));sheet.save(ROOT/f'review/{sid}_{kind}_comparison.jpg',quality=90,optimize=True)
  page_masks={}
  for r in group:
   k=r['page'];m=np.load(ROOT/r['mask']);page_masks.setdefault(k,np.zeros((1920,1080),bool));page_masks[k]|=m['ink']
  for r in group:
   m=np.load(ROOT/r['mask']);ink=m['ink'];allink=page_masks[r['page']];outer=np.asarray(Image.fromarray(ink.astype('uint8')*255).filter(ImageFilter.MaxFilter(19)))>0;excluded=np.asarray(Image.fromarray(allink.astype('uint8')*255).filter(ImageFilter.MaxFilter(7)))>0;ring=outer & ~excluded & m['flat'];assert ring.sum()>50
   frame=new[r['middle_frame']];l=lum(frame);mintext=float(l[m['core']].min());maxbg=float(l[ring].max());ratio=(mintext+.05)/(maxbg+.05)
   result={k:r[k] for k in ['short_id','page','line','text','brand','middle_frame','text_bbox','plate_bbox','padding','opacity']};result.update(seconds=r['middle_frame']/30,text_core_pixels=int(m['core'].sum()),adjacent_background_pixels=int(ring.sum()),minimum_text_luminance=mintext,maximum_adjacent_background_luminance=maxbg,contrast_ratio=ratio,passed=ratio>=4.5);contrasts.append(result)
   assert result['passed'],result
  for page in sorted(page_masks):
   r=next(r for r in group if r['page']==page);n=r['middle_frame'];pair(old[n],new[n],f'{sid} caption {page} {n/30:.2f}s',outdir/f'caption_{page:02d}.jpg',crop=(40,1120,920,1470))
  print('QC',sid,q['input_i'],q['input_tp'],'contrast min',min(r['contrast_ratio'] for r in contrasts if r['short_id']==sid),flush=True)
 save(ROOT/'records/media_qc.json',{'passed':True,'media':media,'human_full_listening':False,'unchanged_source_shots':9,'unchanged_script_audio_cuts_camera':True})
 save(ROOT/'records/contrast_qc.json',{'passed':True,'threshold':4.5,'rows':contrasts,'minimum':min(r['contrast_ratio'] for r in contrasts),'method':'全19字幕イベントの中央フレーム、34行を先頭から連続デコード。元の文字を黒背景に単独描画しRGB244/240/223±3の領域を3×3収縮した内部画素を取得。最も暗い文字内部と、文字輪郭から3〜9px離れた直近の板（別行を含む文字輪郭は除外）の最も明るい画素で保守的な比を測定。sRGBを線形化し相対輝度(L+.05)の比を使用。分位数への置換やフレーム除外はしない。'})
 with (ROOT/'deliverables/subtitle_contrast_v02.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(contrasts[0]));w.writeheader();w.writerows(contrasts)
 save(ROOT/'records/frame_comparison.json',{'continuous_decode_from_zero':True,'no_seek':True,'opening_seconds':[0,.5,1,1.5,2,2.5],'comparisons':comparisons})
 print('ALL PASSED',len(contrasts),'lines',flush=True)

def motion():
 import wom08_shorts_qc as base
 source=inspect.getsource(base.motion).replace('_v01.mp4','_v02.mp4');scope=dict(globals());exec(source,scope);scope['motion']()
if __name__=='__main__':
 import sys
 globals()[sys.argv[1] if len(sys.argv)>1 else 'main']()
