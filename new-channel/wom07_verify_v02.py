"""Full continuous decoding, exact frame preservation, and unchanged-audio proof."""
import subprocess,json,re,concurrent.futures
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom07_revision_v02 import ROOT,OLD,A,B,TOTAL,read,save,sha,probe,stream_hash,ff

def hashes(path,name):
 dst=ROOT/'_work'/f'{name}.framemd5';stamp=dst.with_suffix('.json');signature=sha(path)
 if not(dst.exists() and stamp.exists() and read(stamp)['sha256']==signature):
  cmd=['ffmpeg','-nostdin','-y','-v','warning','-threads','2','-i',str(path),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','framemd5',str(dst),'-map','0:a:0?','-vn','-f','null','-']
  q=subprocess.run(cmd,capture_output=True,text=True,check=True);assert not q.stderr.strip(),q.stderr
  save(stamp,{'sha256':signature,'continuous_decode_warnings':0,'command':cmd})
 rows=[x.split(',') for x in dst.read_text().splitlines() if x and not x.startswith('#')]
 assert all(int(x[4])==1920*1080*3//2 for x in rows)
 return [x[-1].strip() for x in rows]

def main():
 jobs={};files=[]
 for lang in ['en','ja']:
  for review in [False,True]:
   suffix='_subtitled_review' if review else ''
   old=OLD/f'deliverables/EP007_Thanksgiving_{lang}_v01{suffix}_1080p30.mp4';new=ROOT/f'deliverables/EP007_Thanksgiving_{lang}_v02{suffix}_1080p30.mp4'
   key=f'{lang}{suffix}';oldkey='old_'+key if review else 'old_clean'
   jobs[oldkey]=old if review else OLD/'deliverables/EP007_Thanksgiving_en_v01_1080p30.mp4';jobs['new_'+key]=new
   files.append((lang,review,old,new,oldkey,'new_'+key))
 decoded={}
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  future={pool.submit(hashes,p,k):k for k,p in jobs.items()}
  for f in concurrent.futures.as_completed(future):k=future[f];decoded[k]=f.result();print('CONTINUOUS DECODE',k,len(decoded[k]),flush=True)
 checks=[]
 for lang,review,old,new,oldkey,newkey in files:
  a,b=decoded[oldkey],decoded[newkey];assert len(a)==len(b)==TOTAL
  changes=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y];assert changes==list(range(A,B)),(lang,review,len(changes),[i for i in changes if not A<=i<B][:10])
  info=probe(new);v=next(x for x in info['streams'] if x['codec_type']=='video');au=next(x for x in info['streams'] if x['codec_type']=='audio')
  assert (v['profile'],v['pix_fmt'],v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==('High','yuv420p',1920,1080,'30/1',TOTAL)
  assert v['time_base']=='1/15360' and int(v['duration_ts'])==TOTAL*512 and int(au['duration_ts'])==TOTAL*1600
  pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(new)],text=True).splitlines()));assert pts==list(range(0,TOTAL*512,512))
  ah=stream_hash(old,'a');assert ah==stream_hash(new,'a');vh=stream_hash(new,'v')
  trace=subprocess.run(['ffmpeg','-v','info','-i',str(new),'-map','0:v:0','-c','copy','-bsf:v','trace_headers','-f','null','-'],capture_output=True,text=True,check=True);profiles=set(re.findall(r'profile_idc\s+[01]+\s+=\s+(\d+)',trace.stderr));assert profiles=={'100'}
  checks.append({'name':new.name,'sha256':sha(new),'bytes':new.stat().st_size,'decode_warnings':0,'decoded_frames':TOTAL,'profile':'High','pix_fmt':'yuv420p','sps_profile_idc':[100],'exact_30fps_pts':True,'duration_seconds':TOTAL/30,'outside_P05_pixel_identical':True,'unchanged_frames':TOTAL-(B-A),'changed_frames':len(changes),'changed_interval_half_open':[A,B],'v01_audio_stream_sha256':ah,'audio_stream_unchanged':True,'video_stream_sha256':vh})
  print('EXACT PRESERVATION',new.name,TOTAL-len(changes),'unchanged',flush=True)
 assert checks[0]['video_stream_sha256']==checks[2]['video_stream_sha256']
 # Prove the delivered P05 pixels are the exact individually rendered map clip.
 mapfile=ROOT/'_work/P05_G11-01.mp4';dst=ROOT/'_work/map.framemd5';q=subprocess.run(['ffmpeg','-nostdin','-y','-v','warning','-i',str(mapfile),'-pix_fmt','yuv420p','-fps_mode','passthrough','-f','framemd5',str(dst)],capture_output=True,text=True,check=True);assert not q.stderr.strip()
 map_hashes=[x.split(',')[-1].strip() for x in dst.read_text().splitlines() if x and not x.startswith('#')];assert map_hashes==decoded['new_en'][A:B]
 import wom07_motion as motion
 motion.ROOT=ROOT;stats=motion.motion_stats(mapfile,[344,233,1232,574]);assert stats['frame_pairs']==B-A-1 and stats['p95_over_median']<=2.5
 save(ROOT/'records/map_motion_v02.json',{'passed':True,'method':'Every consecutive decoded P05 frame, 8-bit gray ROI [344,233,1232,574], no discarded differences. Delivered P05 all 698 frame MD5 values equal the measured map clip.','measurement':stats})
 for lang in ['en','ja']:
  old=OLD/f'deliverables/EP007_Thanksgiving_{lang}_v01_1080p30.srt';new=ROOT/f'deliverables/EP007_Thanksgiving_{lang}_v02_1080p30.srt';assert sha(old)==sha(new)
  for ext in ['m4a','wav']:assert sha(OLD/f'deliverables/EP007_audio_{lang}.{ext}')==sha(ROOT/f'deliverables/EP007_audio_{lang}.{ext}')
 assert sha(OLD/'deliverables/wom07_サムネB_20261029.jpg')==sha(ROOT/'deliverables/EP007_thumbnail_B.jpg')
 save(ROOT/'records/qc_v02.json',{'passed':True,'duration_seconds':TOTAL/30,'frames':TOTAL,'changed_frames':B-A,'unchanged_frames':TOTAL-(B-A),'srt_wav_m4a_unchanged':True,'thumbnail_B_original_unchanged':True,'same_video_en_ja':True,'checks':checks})
 # Continuous decoding from the beginning, no seeking, for the requested visual proof.
 for lang in ['en','ja']:
  src=ROOT/f'deliverables/EP007_Thanksgiving_{lang}_v02_1080p30.mp4';expr='+'.join(f'eq(n\\,{n})' for n in [A,A+(B-A-1)//2,B-1]);folder=ROOT/f'_work/continuous_{lang}';folder.mkdir(exist_ok=True)
  q=subprocess.run(['ffmpeg','-nostdin','-y','-v','warning','-threads','2','-i',str(src),'-vf',f'select={expr},scale=1280:720','-fps_mode','passthrough','-pix_fmt','rgb24',str(folder/'%02d.png')],capture_output=True,text=True,check=True);assert not q.stderr.strip()
  sheet=Image.new('RGB',(1280,780),'#0c1820');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
  for i,label in enumerate(['FIRST / 102.600 s','MIDDLE / 114.200 s','LAST / 125.833 s']):
   im=Image.open(folder/f'{i+1:02d}.png');im.save(ROOT/f'review/P05_{lang}_{i+1:02d}.jpg',quality=90,optimize=True);sheet.paste(im.resize((640,360)),((i%2)*640,(i//2)*390));d.text(((i%2)*640+8,(i//2)*390+364),label,font=font,fill='white')
  sheet.save(ROOT/f'review/P05_{lang}_continuous.jpg',quality=89,optimize=True)
 print('V02 ALL CHECKS PASSED',stats['p95_over_median'],flush=True)
if __name__=='__main__':main()
