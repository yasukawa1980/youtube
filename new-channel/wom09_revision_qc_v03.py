"""Box/arrow clearances, exact unaffected source pixels, and v02 invariants."""
from wom09_revision_v03 import BASE
from wom09_produce import ROOT,read,save,sha
from wom01_quiet_origins import stream_hash
from PIL import Image,ImageDraw,ImageFont
import numpy as np
import subprocess,csv,re,hashlib

def main():
 shots=read(ROOT/'records/render_shots.json');oldshots=read(BASE/'records/render_shots.json');manifest=read(ROOT/'records/visual_manifest.json');oldmanifest=read(BASE/'records/visual_manifest.json')
 keys=['key','segment_id','start','end','frames','stage_change_frames']
 assert [{k:s.get(k) for k in keys} for s in shots]==[{k:s.get(k) for k in keys} for s in oldshots]
 assert read(ROOT/'records/master_timeline.json')==read(BASE/'records/master_timeline.json')
 base=read(ROOT/'records/v02_baseline.json');assert all(sha(BASE/'deliverables'/n)==h for n,h in base['immutable_deliverables'].items())
 same=[]
 for lang in ['en','ja']:
  for ext in ['wav','m4a']:
   n=f'EP009_audio_{lang}.{ext}';assert sha(ROOT/'deliverables'/n)==sha(BASE/'deliverables'/n);same.append({'file':n,'sha256':sha(ROOT/'deliverables'/n)})
  n=f'EP009_TrojanHorse_{lang}_v03_1080p30.srt';assert sha(ROOT/'deliverables'/n)==sha(BASE/'deliverables'/n.replace('_v03_','_v02_'));same.append({'file':n,'sha256':sha(ROOT/'deliverables'/n)})
  for suffix in ['', '_subtitled_review']:
   n=f'EP009_TrojanHorse_{lang}_v03{suffix}_1080p30.mp4';h=stream_hash(ROOT/'deliverables'/n,'a');assert h==stream_hash(BASE/'deliverables'/n.replace('_v03_','_v02_'),'a');same.append({'file':n,'audio_stream_sha256':h})
 changed=[]
 for a,b in zip(manifest['shots'],oldmanifest['shots']):
  assert a['key']==b['key'];aa=np.array(Image.open(ROOT/a['file']));bb=np.array(Image.open(BASE/b['file']));assert np.array_equal(aa[:110],bb[:110])
  if not np.array_equal(aa,bb):changed.append(a['key'])
  if a['key']!='D_summary':assert a==b
 assert changed==['D_summary']
 unchanged=[]
 # Each unchanged encoded shot input is byte-identical. Decode that identical
 # input to frame hashes, proving all pixels sent into the common encoder match.
 for a,b in zip(shots,oldshots):
  if a['key']=='D_summary':continue
  p,q=ROOT/a['encoded_file'],BASE/b['encoded_file'];h=sha(p);assert h==sha(q),a['key']
  cmd=['ffmpeg','-nostdin','-v','error','-i',str(p),'-map','0:v:0','-an','-pix_fmt','yuv420p','-f','framemd5','-']
  out=subprocess.check_output(cmd);lines=[x for x in out.decode().splitlines() if x and not x.startswith('#')];assert len(lines)==a['frames']
  unchanged.append({'key':a['key'],'frames':len(lines),'v02_v03_identical_input_sha256':h,'decoded_frame_manifest_sha256':hashlib.sha256(out).hexdigest(),'all_source_pixels_identical':True})
  print('UNCHANGED SOURCE PIXELS',a['key'],len(lines),flush=True)
 layout=read(ROOT/'records/summary_layout_v03.json');assert layout['passed']
 for b in layout['boxes']:assert min(b['gaps_px'].values())>=24
 for a in layout['arrows']:assert a['length_px']>=40 and min(a['left_gap_px'],a['right_gap_px'])>=16
 assert layout['overall_center_y']==404 and min(layout['body_contrast'],layout['accent_contrast'])>=4.5
 # Same absolute frame 9454, 315.133333 seconds; never seek.
 frame=9454;images=[]
 for ver,folder in [('v02',BASE),('v03',ROOT)]:
  dst=ROOT/f'_work/summary_{ver}.png';cmd=['ffmpeg','-nostdin','-y','-v','warning','-i',str(folder/f'deliverables/EP009_TrojanHorse_en_{ver}_1080p30.mp4'),'-vf',f'select=eq(n\\,{frame}),scale=1280:720','-frames:v','1','-fps_mode','passthrough','-update','1',str(dst)]
  p=subprocess.run(cmd,capture_output=True,text=True,check=True);assert not p.stderr.strip(),p.stderr;images.append(Image.open(dst).copy())
 pair=Image.new('RGB',(1280,400),'#e8d9b7');d=ImageDraw.Draw(pair);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
 for i,(ver,im) in enumerate(zip(['v02','v03'],images)):
  d.text((i*640+12,9),f'{ver}  D_summary  315.133s',font=font,fill='#3b2c21');pair.paste(im.resize((640,360),Image.Resampling.LANCZOS),(i*640,40))
 pair.save(ROOT/'review/compare_D_summary_v02_v03.jpg',quality=94,optimize=True)
 images[1].save(ROOT/'review/D_summary_v03_final.jpg',quality=94,optimize=True)
 with (ROOT/'deliverables/EP009_summary_clearance_v03.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['box','left','top','right','bottom'],lineterminator='\n');w.writeheader()
  for b in layout['boxes']:w.writerow({'box':b['index'],**b['gaps_px']})
 save(ROOT/'records/revision_qc_v03.json',{'passed':True,'changed_visuals':changed,'unchanged_shot_count':len(unchanged),'unchanged_source_pixel_checks':unchanged,'pixel_comparison_scope':'Every pixel of all 23 unchanged shot inputs, before the required common lossy H.264 encode. No claim that final compressed files are byte-identical.','v02_deliverables_preserved':True,'timing_and_reveal_frames_unchanged':True,'same_audio_and_srt':same,'comparison':{'frame':frame,'seconds':frame/30,'file':'review/compare_D_summary_v02_v03.jpg'},'human_full_listening':False})
 print('V03 REVISION QC PASSED',flush=True)
if __name__=='__main__':main()
