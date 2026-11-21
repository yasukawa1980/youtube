"""Render finite shot checkpoints and decode them individually into one master encoder."""
import sys, subprocess, json, hashlib, shutil, os
from pathlib import Path
from PIL import Image
from wom15_voice import ROOT,HERE,read,save,sha
from wom14_produce import OP,END
from wom15_art import art,ASSETS,BOXES,credits
from wom15_boards import board,diagram,WORDS,LEFT,RIGHT
def run(args,**kw):
 return subprocess.run([str(a) for a in args],check=True,**kw)
FF=['ffmpeg','-y','-nostdin','-v','error','-filter_threads','1','-filter_complex_threads','1','-threads','1']
def encoder(s):
 return ['-c:v','h264_videotoolbox','-profile:v','high','-b:v',('12M' if s==1 else '26M'),'-pix_fmt','yuv420p','-g','60','-bf','2','-video_track_timescale','15360']
def design(shot,events,s,folder):
 k=shot['key'];first=shot['start'];end=shot['end'];stages=[];motion=None
 folder.mkdir(parents=True,exist_ok=True)
 def put(frame,ident,draw):
  if frame>=end:return
  file=folder/(ident+'.jpg');meta=file.with_suffix('.json')
  if not (file.exists() and meta.exists()):
   result=draw();p,geo=result if isinstance(result,tuple) else (result,None)
   p.im.save(file,quality=97,subsampling=0)
   save(meta,dict(geometry=geo,text=p.metrics))
  stages.append(dict(frame=frame,file=str(file),meta=str(meta)))
 def ap(frame,u=0,idx=0,mark=False):
  put(frame,f'art_{idx}_{u:.4f}_{int(mark)}',lambda:art(k,s,u,idx,mark))
 if k in BOXES:
  ap(first)
  for f in range(1,19):
   u=f/18;ap(first+59+f,u*u*(3-2*u))
  if k=='D12-A':
   ap(max(first+78,events['conceived']),1,0,True)
   ap(events['born'],1,1,True)
  else:
   ap(first+78,1,0,True)
   if k=='D07-A':ap(events['latin'],1,1,True)
   if k=='D14-A':ap(max(first+80,end-48),1,1,True)
 elif k in ASSETS:
  ap(first,1 if k=='D01-A' else 0)
  geo=read(Path(stages[-1]['meta']))['geometry']
  if k=='D01-A':motion='opening'
  elif k=='D05-T':motion='drift'
  elif geo['scale']*1.025<=1:motion='art'
 elif k.startswith('D_board'):
  base={'D_board_empty':[], 'D_board_sun':['rome'],'D_board_sun_return':['rome',*LEFT[:-1]],
        'D_board_calc':['rome',*LEFT],'D_board_both':['rome',*LEFT,*RIGHT],
        'D_board_all':['rome',*LEFT,*RIGHT,'neither']}[k]
  additions={'D_board_empty':['rome'],'D_board_sun':['temple','margin','leo','before'],
    'D_board_sun_return':['saturnalia'],'D_board_calc':RIGHT,'D_board_both':['neither'],'D_board_all':['pliny']}[k]
  active=set(base)
  put(first,'start',lambda:board(s,active))
  for item in additions:
   frame=events[item];active.add(item)
   if item=='margin':active.add('unknown')
   if item in ('before','after','neither','saturnalia'):
    put(frame,item,lambda:board(s,active))
   else:
    for j in range(8):
     put(frame+j,item+str(j),lambda:board(s,active,item,round(-15*(1-j/7))))
 elif k=='D_count':
  put(first,'start',lambda:diagram(k,s))
  f=events['count'];n=end-f
  for j in range(1,10):put(f+round((j-1)*max(8,n-16)/9),'month'+str(j),lambda:diagram(k,s,j))
 elif k in ['D_map','D_markers']:put(first,'diagram',lambda:diagram(k,s))
 elif k=='credits':put(first,'credits',lambda:credits(s))
 else:raise ValueError(k)
 stages=list({e['frame']:e for e in sorted(stages,key=lambda e:e['frame'])}.values())
 assert stages[0]['frame']==first and all(first<=e['frame']<end for e in stages)
 return stages,motion
def picture(lang,s):
 dst=ROOT/lang;plan=read(dst/'records/shot_plan.json');events={x['key']:x['frame'] for x in read(dst/'records/phrase_events.json')}
 suffix='_4k' if s==2 else '';r=dst/('_work/render'+suffix);r.mkdir(parents=True,exist_ok=True)
 version=hashlib.sha256(''.join(sha(HERE/name) for name in ['wom15_render.py','wom15_art.py','wom15_boards.py']).encode()).hexdigest()[:12]
 size=f'{s*1920}x{s*1080}'
 for shot in plan:
  k=shot['key'];n=shot['end']-shot['start'];shot['frames']=n
  if k in ('opening','endcard'):shot['file']=str(OP if k=='opening' else END);continue
  stages,motion=design(shot,events,s,ROOT/'_work'/f'plates_{version}_{s}'/k)
  clip=r/(k+'.mp4');stamp=clip.with_suffix('.json')
  ident=dict(version=version,frames=n,stages=stages,motion=motion)
  if not (stamp.exists() and clip.exists() and read(stamp)==ident):
   if len(stages)>1:
    lst=r/(k+'.ffconcat');parts=['ffconcat version 1.0']
    for st,stop in zip(stages,[x['frame'] for x in stages[1:]]+[shot['end']]):
     parts.extend(["file '"+st['file']+"'","option framerate 30",f"duration {(stop-st['frame'])/30:.9f}"])
    parts.extend(["file '"+stages[-1]['file']+"'","option framerate 30"])
    lst.write_text('\n'.join(parts)+'\n');args=['-safe','0','-f','concat','-i',lst];vf='fps=30,format=yuv420p'
   else:
    args=['-loop','1','-framerate','30','-t',n/30,'-i',stages[0]['file']];vf='format=yuv420p'
   if motion:
    # Transform only the source panel. Overlay the unmodified type plate at its original position.
    left=0 if motion=='opening' else 690*s;w=s*1920-left;h=s*1080
    t=f'on/{max(1,n-1)}'
    z=f'(1.1-.1*{t})' if motion=='opening' else (f'(1+.025*{t})' if motion=='art' else '1')
    x=f'((W-W/{z})*.5)' if motion!='drift' else f'(24*{s}*{t})'
    y=f'(H-H/{z})' if motion=='opening' else f'((H-H/{z})*.5)'
    pan=f"perspective=x0='{x}':y0='{y}':x1='{x}+W/{z}':y1='{y}':x2='{x}':y2='{y}+H/{z}':x3='{x}+W/{z}':y3='{y}+H/{z}':sense=source:eval=frame:interpolation=cubic"
    if motion=='opening':
     # The corner plate is baked into the overview: mask it before the camera move.
     # Its entire transformed area stays behind the original opaque upper-left plate.
     vf=f"split[art][txt];[art]{pan}[v];[txt]crop={710*s}:{128*s}:0:0[tag];[v][tag]overlay=0:0,format=yuv420p"
    else:vf=f"split[base][im];[im]crop={w}:{h}:{left}:0,{pan}[cam];[base][cam]overlay={left}:0,format=yuv420p"
   tmp=clip.with_suffix('.part.mp4')
   run([*FF,*args,'-vf',vf,'-an','-frames:v',n,*encoder(s),tmp])
   count=int(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','csv=p=0',tmp]))
   assert count==n,(k,n,count)
   tmp.replace(clip);save(stamp,ident)
  shot.update(file=str(clip),stages=stages,motion=motion);print(lang,size,k,n,flush=True)
 save(dst/f'records/render_shots{suffix}.json',plan)
 out=dst/f'deliverables/EP015_December25_{lang}_v01_{1080*s}p30.mp4';aud=dst/f'deliverables/EP015_audio_{lang}.m4a'
 state=r/'assembly.json';sig=dict(shots=[sha(Path(x['file'])) for x in plan],audio=sha(aud))
 if out.exists() and state.exists() and read(state)==sig:return
 tmp=out.with_suffix('.part.mp4')
 enc=subprocess.Popen([str(a) for a in [*FF,'-f','rawvideo','-pix_fmt','yuv420p','-s',size,'-framerate','30','-i','pipe:0','-i',aud,'-map','0:v','-map','1:a','-c:a','copy',*encoder(s),'-metadata:s:a:0','language='+('eng' if lang=='en' else 'jpn'),'-movie_timescale','48000','-movflags','+faststart',tmp]],stdin=subprocess.PIPE)
 try:
  for sh in plan:
   scale=['-vf',f'scale={1920*s}:{1080*s}:flags=lanczos'] if s==2 and sh['key'] in ('opening','endcard') else []
   run([*FF,'-i',sh['file'],'-map','0:v','-an',*scale,'-frames:v',sh['frames'],'-threads:v','1','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin)
  enc.stdin.close();assert enc.wait()==0
 except BaseException:enc.kill();enc.wait();raise
 tmp.replace(out);save(state,sig)
if __name__=='__main__':picture(sys.argv[1],int(sys.argv[2]))
