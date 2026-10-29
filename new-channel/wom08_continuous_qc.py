"""EP008 full-stream verification; frame selection never uses seeking."""
import json,re,subprocess,math
import numpy as np
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from wom08_produce import ROOT,REPO,read,save,sha,probe
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def main():
 shots=read(ROOT/'records/render_shots.json');m=read(ROOT/'records/master_timeline.json');total=round(m['duration_seconds']*30)
 assert len(shots)==25 and sum(s['frames'] for s in shots)==total
 assert all(round(a['end']*30)==round(b['start']*30) for a,b in zip(shots,shots[1:]))
 selected=[];triples=[]
 for s in shots:
  a=round(s['start']*30);ns=[a,a+(s['frames']-1)//2,a+s['frames']-1];selected.extend(ns);triples.append(ns)
 expr='+'.join(f'eq(n\\,{n})' for n in selected);checks=[];font=ImageFont.truetype(FONT,17)
 for lang in ['en','ja']:
  src=ROOT/f'deliverables/EP008_Tutankhamun_{lang}_v01_1080p30.mp4';folder=ROOT/f'_work/continuous_{lang}';folder.mkdir(exist_ok=True)
  cmd=['ffmpeg','-nostdin','-y','-v','warning','-threads','2','-i',str(src),'-vf',f'select={expr},scale=1280:720','-fps_mode','passthrough','-c:v','png','-pix_fmt','rgb24',str(folder/'%03d.png')]
  q=subprocess.run(cmd,capture_output=True,text=True,check=True);assert not q.stderr.strip(),q.stderr
  ims=sorted(folder.glob('*.png'));assert len(ims)==len(selected)
  p=probe(src);v=next(x for x in p['streams'] if x['codec_type']=='video');assert v['profile']=='High' and v['pix_fmt']=='yuv420p' and int(v['nb_frames'])==total
  frameinfo=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=width,height,pix_fmt','-of','json',str(src)],text=True))['frames']
  formats={(f['width'],f['height'],f['pix_fmt']) for f in frameinfo};assert formats=={(1920,1080,'yuv420p')} and len(frameinfo)==total
  tr=subprocess.run(['ffmpeg','-v','info','-i',str(src),'-map','0:v:0','-c','copy','-bsf:v','trace_headers','-f','null','-'],capture_output=True,text=True,check=True)
  profiles=set(re.findall(r'profile_idc\s+[01]+\s+=\s+(\d+)',tr.stderr));assert profiles=={'100'},profiles
  records=[]
  for i,s in enumerate(shots):
   header_checks=[]
   if s['segment_id']!='BRAND':
    expected=Image.open(ROOT/s['file']).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
    ref=np.asarray(expected)[:68].astype(np.int16)
    for j in range(3):
     actual=np.asarray(Image.open(ims[i*3+j]).convert('RGB'))[:68].astype(np.int16)
     error=float(np.abs(actual-ref).mean())
     a=actual.max(axis=2)>100;b=ref.max(axis=2)>100
     overlap=float(np.logical_and(a,b).sum()/np.logical_or(a,b).sum())
     # Caption glyphs must match; RGB MAE is retained separately because RGB
     # artwork and the final tagged YUV video have different color conversion.
     assert overlap>=.90,(lang,s['key'],'source header glyph mismatch',overlap)
     header_checks.append({'rgb_mean_absolute_error':error,'glyph_intersection_over_union':overlap})
   trip=Image.new('RGB',(1280,280),'#0c1820');d=ImageDraw.Draw(trip)
   for j,label in enumerate(['FIRST','MIDDLE','LAST']):
    im=Image.open(ims[i*3+j]);trip.paste(im.resize((426,240)),(j*426,0));d.text((j*426+8,244),f'{label}  frame {triples[i][j]}',font=font,fill='#f4efdf')
   dst=ROOT/f'review/continuous_{lang}_shot_{i+1:02d}.jpg';trip.save(dst,quality=88,optimize=True)
   center=ROOT/f'review/center_{lang}_{i+1:02d}.jpg';Image.open(ims[i*3+1]).save(center,quality=89,optimize=True)
   records.append({'key':s['key'],'frames':triples[i],'triptych':str(dst.relative_to(ROOT)),'center':str(center.relative_to(ROOT)),'source':s.get('source'),'label':s.get('label'),'source_header_checks':header_checks})
  for batch in range(math.ceil(len(shots)/4)):
   sheet=Image.new('RGB',(1280,1240),'#0c1820');d=ImageDraw.Draw(sheet)
   for j,s in enumerate(shots[batch*4:batch*4+4]):
    i=batch*4+j;d.text((10,j*310+4),f'{lang} {i+1:02d} {s["key"]}',font=font,fill='#d8b575');sheet.paste(Image.open(ROOT/records[i]['triptych']),(0,j*310+30))
   sheet.save(ROOT/f'review/continuous_{lang}_sheet_{batch+1:02d}.jpg',quality=85,optimize=True)
  checks.append({'language':lang,'video_sha256':sha(src),'decoded_frames':total,'decoded_pixel_formats':[list(x) for x in formats],'sps_profile_idc':sorted(profiles),'decode_warnings':0,'no_seeking':True,'records':records})
  print('CONTINUOUS QC',lang,total,len(ims),flush=True)
 assert abs(m['brand_intervals']['endcard'][1]-m['brand_intervals']['endcard'][0]-10)<1e-8
 for name in ['content.json','content_en.json']:assert sha(ROOT/'records'/name)==sha(REPO/'new-channel/episodes/EP008_Tutankhamun/records'/name)
 used=read(ROOT/'records/visual_manifest.json')['unique_originals'];assert len(used)==len(set(used))==16
 opening_frames=[]
 for lang in ['en','ja']:
  src=ROOT/f'deliverables/EP008_Tutankhamun_{lang}_v01_1080p30.mp4'
  cmd=['ffmpeg','-nostdin','-y','-v','warning','-i',str(src),'-vf',r'select=eq(n\,0)+eq(n\,30)+eq(n\,60)+eq(n\,90),scale=1280:720','-frames:v','4','-fps_mode','passthrough',str(ROOT/f'review/opening_{lang}_%02d.jpg')]
  q=subprocess.run(cmd,capture_output=True,text=True,check=True);assert not q.stderr.strip()
  opening_frames.append({'language':lang,'source_frames':[0,30,60,90],'files':[f'review/opening_{lang}_{i:02d}.jpg' for i in range(1,5)]})
 save(ROOT/'records/continuous_qc.json',{'passed':True,'checks':checks,'script_unchanged':True,'unique_originals':used,'endcard_exact_last_10_seconds':True,'opening_frames':opening_frames})
if __name__=='__main__':main()
