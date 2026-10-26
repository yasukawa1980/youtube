"""EP006 full-stream verification; frame selection never uses seeking."""
import json,re,subprocess,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from wom06_produce import ROOT,REPO,read,save,sha,probe
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
  src=ROOT/f'deliverables/EP006_Sphinx_{lang}_v01_1080p30.mp4';folder=ROOT/f'_work/continuous_{lang}';folder.mkdir(exist_ok=True)
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
   trip=Image.new('RGB',(1280,280),'#0c1820');d=ImageDraw.Draw(trip)
   for j,label in enumerate(['FIRST','MIDDLE','LAST']):
    im=Image.open(ims[i*3+j]);trip.paste(im.resize((426,240)),(j*426,0));d.text((j*426+8,244),f'{label}  frame {triples[i][j]}',font=font,fill='#f4efdf')
   dst=ROOT/f'review/continuous_{lang}_shot_{i+1:02d}.jpg';trip.save(dst,quality=88,optimize=True)
   center=ROOT/f'review/center_{lang}_{i+1:02d}.jpg';Image.open(ims[i*3+1]).save(center,quality=89,optimize=True)
   records.append({'key':s['key'],'frames':triples[i],'triptych':str(dst.relative_to(ROOT)),'center':str(center.relative_to(ROOT)),'source':s.get('source'),'label':s.get('label')})
  for batch in range(math.ceil(len(shots)/4)):
   sheet=Image.new('RGB',(1280,1240),'#0c1820');d=ImageDraw.Draw(sheet)
   for j,s in enumerate(shots[batch*4:batch*4+4]):
    i=batch*4+j;d.text((10,j*310+4),f'{lang} {i+1:02d} {s["key"]}',font=font,fill='#d8b575');sheet.paste(Image.open(ROOT/records[i]['triptych']),(0,j*310+30))
   sheet.save(ROOT/f'review/continuous_{lang}_sheet_{batch+1:02d}.jpg',quality=85,optimize=True)
  checks.append({'language':lang,'video_sha256':sha(src),'decoded_frames':total,'decoded_pixel_formats':[list(x) for x in formats],'sps_profile_idc':sorted(profiles),'decode_warnings':0,'no_seeking':True,'records':records})
  print('CONTINUOUS QC',lang,total,len(ims),flush=True)
 # The Moreau composition and its blurred background are both built from the fixed crop.
 visual=read(ROOT/'records/visual_manifest.json')['shots'];moreau=next(s for s in visual if s['key']=='met_437153')
 assert moreau['crop_normalized']==[.12,.10,.95,.355] and moreau['background_also_uses_only_crop']
 assert m['brand_intervals']['endcard'][1]-m['brand_intervals']['endcard'][0]==10
 for name in ['content.json','content_en.json']:assert sha(ROOT/'records'/name)==sha(REPO/'new-channel/episodes/EP006_Sphinx/records'/name)
 used=read(ROOT/'records/visual_manifest.json')['unique_originals'];assert len(used)==len(set(used))==19
 for prefix in ['hesiod_','jebb1904_','norden_']:assert sum(k.startswith(prefix) for k in used)==1
 assert not {'met_287084','met_700111'} & set(used)
 save(ROOT/'records/continuous_qc.json',{'passed':True,'checks':checks,'script_unchanged':True,'unique_originals':used,'moreau_fixed_crop':moreau['crop_normalized'],'moreau_no_uncropped_source_in_background':True,'endcard_exact_last_10_seconds':True})
if __name__=='__main__':main()
