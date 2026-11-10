"""Preserve unchanged AVC packets and prove decoded per-frame pixel equality."""
from pathlib import Path
import subprocess,json,hashlib,os,sys,shutil
from wom14_v02 import BASE,ROOT,MODIFIED,read,save,sha,probe,ff,path_video

def blocks(shots):
 out=[]
 for s in shots:
  changed=s['key'] in MODIFIED;a=round(s['start']*30);b=round(s['end']*30)
  if out and out[-1]['changed']==changed:out[-1]['end']=b;out[-1]['shots'].append(s['key'])
  else:out.append(dict(start=a,end=b,changed=changed,shots=[s['key']]))
 return out

def concat(path,parts,counts):
 path.write_text('ffconcat version 1.0\n'+''.join(f"file '{p}'\nduration {n/30:.9f}\n" for p,n in zip(parts,counts)))

def assemble(lang,scale):
 suffix='_4k' if scale==2 else '';shots=read(BASE/lang/f'records/render_shots{suffix}.json');groups=blocks(shots);src=path_video(BASE,lang,scale);out=path_video(ROOT,lang,scale);folder=ROOT/lang/('_work/splice'+suffix);folder.mkdir(exist_ok=True)
 cuts=[g['start'] for g in groups[1:]];keys=json.loads(subprocess.check_output(['ffprobe','-v','error','-skip_frame','nokey','-select_streams','v','-show_frames','-show_entries','frame=pts_time','-of','json',str(src)]))['frames'];keys={round(float(f['pts_time'])*30) for f in keys};assert set(cuts)<=keys
 ff(['-threads',1,'-i',src,'-map','0:v:0','-an','-c','copy','-f','segment','-segment_times',','.join(f'{n/30:.9f}' for n in cuts),'-segment_time_delta','0.016666667','-reset_timestamps',1,'-segment_format_options','video_track_timescale=15360',folder/'original_%02d.mp4'])
 parts=[];counts=[]
 for i,g in enumerate(groups):
  if g['changed']:
   for key in g['shots']:
    s=next(s for s in shots if s['key']==key);p=ROOT/lang/('_work/replacements'+suffix)/(key+'.mp4');parts.append(p);counts.append(s['frames'])
  else:
   p=folder/f'original_{i:02d}.mp4';assert int(next(x for x in probe(p)['streams'] if x['codec_type']=='video')['nb_frames'])==g['end']-g['start'];parts.append(p);counts.append(g['end']-g['start'])
 lst=folder/'final.ffconcat';concat(lst,parts,counts)
 ff(['-f','concat','-safe',0,'-i',lst,'-i',BASE/lang/f'deliverables/EP014_audio_{lang}.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-bsf:v','setts=pts=PTS:dts=DTS:duration=512','-video_track_timescale',15360,'-movie_timescale',48000,'-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn'),'-movflags','+faststart',out])
 save(ROOT/lang/f'records/assembly_v02{suffix}.json',dict(method='Smart replacement at IDR-aligned group boundaries; unchanged v01 AVC packets preserved; new finite-shot encodes only for eight revised shots',source_sha256=sha(src),output_sha256=sha(out),groups=groups,frames=sum(counts),v01_read_only=True))
 print('ASSEMBLED',lang,scale,flush=True)

def framehash(src,dest):
 stamp=dest.with_suffix('.json');digest=sha(src)
 if not(dest.exists() and stamp.exists() and read(stamp)['video_sha256']==digest):
  p=subprocess.run(['ffmpeg','-y','-nostdin','-v','warning','-xerror','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','framemd5',str(dest)],capture_output=True,text=True);assert p.returncode==0 and not p.stderr.strip(),p.stderr
  save(stamp,dict(video_sha256=digest,decode_warnings=0,hash_method='MD5 of decoded raw yuv420p pixels per frame'))
 rows=[line.split(',') for line in dest.read_text().splitlines() if not line.startswith('#') and line.strip()]
 return [r[-1].strip() for r in rows]

def streamhash(p,stream):
 return subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(p),'-map',f'0:{stream}:0','-c','copy','-f','streamhash','-hash','sha256','-'],text=True).strip()

def verify(lang,scale):
 suffix='_4k' if scale==2 else '';shots=read(BASE/lang/f'records/render_shots{suffix}.json');src=path_video(BASE,lang,scale);out=path_video(ROOT,lang,scale);folder=ROOT/lang/'records';a=framehash(src,folder/f'v01_pixels{suffix}.framemd5');b=framehash(out,folder/f'v02_pixels{suffix}.framemd5');assert len(a)==len(b)==sum(s['frames'] for s in shots);checks=[]
 for s in shots:
  start=round(s['start']*30);end=start+s['frames'];n=sum(x!=y for x,y in zip(a[start:end],b[start:end]));changed=s['key'] in MODIFIED
  if not changed:assert n==0,(lang,scale,s['key'],n)
  checks.append(dict(shot=s['key'],modified=changed,frames=s['frames'],different_frames=n,pixels_identical=n==0,v01_pixel_sequence_sha256=hashlib.sha256(''.join(a[start:end]).encode()).hexdigest(),v02_pixel_sequence_sha256=hashlib.sha256(''.join(b[start:end]).encode()).hexdigest()))
 info=probe(out);v=next(s for s in info['streams'] if s['codec_type']=='video');assert (v['width'],v['height'],v['profile'],v['pix_fmt'],v['avg_frame_rate'])==(1920*scale,1080*scale,'High','yuv420p','30/1');assert v['time_base']=='1/15360'
 pts=sorted(int(x) for x in subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_entries','packet=pts','-of','csv=p=0',str(out)],text=True).splitlines());assert pts==list(range(0,len(a)*512,512))
 ah=streamhash(src,'a');bh=streamhash(out,'a');assert ah==bh
 st=BASE/lang/f'deliverables/EP014_Oni_{lang}_v01_1080p30.srt';dt=ROOT/lang/f'deliverables/EP014_Oni_{lang}_v02_1080p30.srt';assert sha(st)==sha(dt)
 assert sha(BASE/lang/'records/master_timeline.json')==sha(ROOT/lang/'records/master_timeline.json')
 save(folder/f'pixel_identity_v02{suffix}.json',dict(passed=True,source_sha256=sha(src),output_sha256=sha(out),frames=len(a),unchanged_shots=sum(not x['modified'] for x in checks),unchanged_frames=sum(x['frames'] for x in checks if not x['modified']),all_unchanged_pixels_identical=True,audio_stream_identical=True,audio_stream_sha256=ah,srt_byte_identical=True,srt_sha256=sha(st),timeline_byte_identical=True,decode_warnings=0,profile=v['profile'],pix_fmt=v['pix_fmt'],width=v['width'],height=v['height'],exact_30fps_pts=True,duration=float(info['format']['duration']),checks=checks))
 print('PIXELS VERIFIED',lang,scale,len(a),flush=True)
if __name__=='__main__':globals()[sys.argv[1]](sys.argv[2],int(sys.argv[3]))
