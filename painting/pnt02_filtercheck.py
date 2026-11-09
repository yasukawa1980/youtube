"""Two-frame filter/encoder checks in memory; no video files are saved."""
import io,os,sys,subprocess,threading,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import pnt02_scenes as v
from pnt02_picture import camera
from pathlib import Path
results=[]
for key in v.FILES:
 a=v.scene(key);b=v.art_overlay(key,'1849');streams=[]
 for im in [a,b]:
  buf=io.BytesIO();im.save(buf,format='PNG',compress_level=1);streams.append(buf.getvalue()*2)
 rd,wr=os.pipe();filt=camera(key,2,v.S)
 cmd=['ffmpeg','-nostdin','-v','error','-threads','1','-f','image2pipe','-framerate','30','-i','pipe:0','-threads','1','-f','image2pipe','-framerate','30','-i',f'pipe:{rd}','-filter_complex_threads','2','-filter_complex',filt,'-map','[v]','-frames:v','2','-c:v','libx264','-threads','2','-profile:v','high','-pix_fmt','yuv420p','-f','null','-']
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,pass_fds=(rd,));os.close(rd)
 errors=[]
 def write(stream,data):
  try:stream.write(data);stream.close()
  except BaseException as e:errors.append(str(e))
 ts=[threading.Thread(target=write,args=(p.stdin,streams[0])),threading.Thread(target=write,args=(os.fdopen(wr,'wb'),streams[1]))]
 for t in ts:t.start()
 stderr=p.stderr.read().decode();code=p.wait()
 for t in ts:t.join()
 assert code==0 and not stderr and not errors,(key,stderr,errors)
 results.append({'key':key,'scale':v.S,'frames_encoded_to_null':2,'errors':0,'saved_media':False});print(key,v.S,'OK',flush=True)
Path(f'painting/pnt02_確認版_v01_20261110/filter_smoke_scale{v.S}.json').write_text(json.dumps({'scope':'filter syntax and 2-frame encode only; not final video quality/motion verification','results':results},indent=2)+'\n')
