"""pnt02: native-image plates, individual shot decoders, one final AVC encoder.

Run with the existing local audio Python: python painting/pnt02_picture.py en 1
Then ja 1 and PNT02_SCALE=2 python painting/pnt02_picture.py en 2. Output is restricted to the specified ESD-02 directory.
This code never creates a Release, publishes a video, or edits source media.
"""
import json,os,subprocess,sys
from pathlib import Path
from PIL import Image
from pnt02_produce import ROOT,sha,read,save,probe,ff
from pnt02_shots import plan
import pnt02_scenes as v

def motion(key,frames,scale):
 box=v.BOXES[key];l,t,r,b=box;w,h=r-l,b-t
 amount=.02 if key in ['V01_room','V10'] else .04
 direction='out' if key=='V01_full_2' else 'down' if key=='V01_D1' else 'right' if key=='V01_D3' else 'in'
 def bounds(f):
  u=f/max(1,frames-1)
  z=1+amount*(1-u if direction=='out' else 1 if direction in ['down','right'] else u)
  ax=.25+.75*u if direction=='right' else .47 if 'full' in key else .5
  ay=u if direction=='down' else .48 if 'full' in key else .5
  x=l+(w-w/z)*ax;y=t+(h-h/z)*ay
  return [x,y,x+w/z,y+h/z]
 output_scale=min(1920*scale/w,1080*scale/h)
 for f in range(frames):
  x,y,xx,yy=bounds(f)
  assert l-1e-6<=x<xx<=r+1e-6 and t-1e-6<=y<yy<=b+1e-6
  assert output_scale*w/(xx-x)<=1+1e-9
 if 'full' in key:assert w/(1+amount)>=3846
 return dict(source_crop=box,max_zoom=1+amount,max_native_scale=output_scale*(1+amount),motion=direction,motion_start_native_box=bounds(0),motion_end_native_box=bounds(frames-1),minimum_native_crop_width=w/(1+amount),minimum_native_crop_height=h/(1+amount),all_frame_count=frames,all_frames_within_envelope=True,original_size=list(v.artwork(key).size),output_scale=output_scale)

def camera(key,count,scale):
 a=v.ARTMEAS[key];x,y,x1,y1=[round(q*scale) for q in a['pasted_box']];w=x1-x;h=y1-y
 info=motion(key,count,scale);amount=info['max_zoom']-1;direction=info['motion'];u=f'on/{max(1,count-1)}'
 z=f'(1+{amount}*'+(f'(1-{u})' if direction=='out' else '1' if direction in ['down','right'] else u)+')'
 xx=f'(W-W/{z})*'+(f'(.25+.75*{u})' if direction=='right' else '.47' if 'full' in key else '.5')
 yy=f'(H-H/{z})*'+(u if direction=='down' else '.48' if 'full' in key else '.5')
 p=f"perspective=x0='{xx}':y0='{yy}':x1='{xx}+W/{z}':y1='{yy}':x2='{xx}':y2='{yy}+H/{z}':x3='{xx}+W/{z}':y3='{yy}+H/{z}':sense=source:eval=frame:interpolation=cubic"
 a.update(info)
 return f'[0:v]fps=30,format=yuv444p,split[base][art];[art]crop={w}:{h}:{x}:{y}:exact=1,{p}[moving];[base][moving]overlay={x}:{y}:format=yuv444[pre];[pre][1:v]overlay=format=yuv444,format=yuv420p[v]'

def concat_entries(path,entries):
 lines=['ffconcat version 1.0']
 for e in entries:
  assert "'" not in str(e['path'])
  lines += [f"file '{e['path']}'",'option framerate 30',f"duration {e['frames']/30:.9f}"]
 lines += [f"file '{entries[-1]['path']}'",'option framerate 30']
 path.write_text('\n'.join(lines)+'\n')

def run(lang,scale):
 assert lang in ['en','ja'] and scale in [1,2] and (lang=='en' or scale==1)
 assert Path('/Volumes/ESD-02').is_mount()
 assert ROOT==Path('/Volumes/ESD-02/新チャンネル/PNT02_WashingtonCrossing/確認版_v01_20261110'), 'No alternate output disk'
 assert v.S==scale, 'Set PNT02_SCALE before importing scene module'
 dst=ROOT/lang;suffix='_4k' if scale==2 else '';work=dst/f'_work/render{suffix}';work.mkdir(parents=True,exist_ok=True)
 data=plan(lang);shots=data['shots']
 for shot in shots:
  key=shot['key']
  if shot['segment_id']=='BRAND':continue
  art=key in v.FILES;entries=[]
  if art:
   source=work/f'{key}_source.png';v.scene(key).save(source,compress_level=2)
  for i,e in enumerate(shot['stages']):
   im=v.art_overlay(key,e['year']) if art else v.scene(key,e['stage'],e['year'])
   p=work/f'{key}_{i:02}.png';im.save(p,compress_level=2)
   entries.append(dict(path=p,frames=e['frames']))
  playlist=work/f'{key}.ffconcat';concat_entries(playlist,entries)
  if art:
   args=['-loop',1,'-framerate',30,'-threads',1,'-t',shot['frames']/30,'-i',source,'-threads',1,'-f','concat','-safe',0,'-i',playlist]
   filt=camera(key,shot['frames'],scale)
  else:
   args=['-threads',1,'-f','concat','-safe',0,'-i',playlist];filt='[0:v]fps=30,format=yuv420p[v]'
  out=work/f'{key}.mp4';stamp=out.with_suffix('.json')
  cfg=dict(images=[(sha(e['path']),e['frames']) for e in entries],source=sha(source) if art else None,filter=filt,frames=shot['frames'],scale=scale,encoder='libx264/veryfast/crf15/threads2/high/yuv420p')
  if not(out.exists() and stamp.exists() and read(stamp)==json.loads(json.dumps(cfg))):
   ff([*args,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-an','-frames:v',shot['frames'],'-c:v','libx264','-preset','veryfast','-threads',2,'-x264-params','rc-lookahead=5:sync-lookahead=0','-crf',15,'-profile:v','high','-pix_fmt','yuv420p','-video_track_timescale',15360,out]);save(stamp,cfg)
  video=next(s for s in probe(out)['streams'] if s['codec_type']=='video');assert int(video['nb_frames'])==shot['frames']
  shot.update(encoded_file=str(out),moving=art);print('SHOT',lang,scale,key,shot['frames'],flush=True)
 save(dst/f'records/render_shots{suffix}.json',shots);save(dst/f'records/art_scales{suffix}.json',v.ARTMEAS);save(dst/f'records/frame_layout{suffix}.json',v.METR);save(dst/f'records/rail_switches{suffix}.json',data)
 v.artwork.cache_clear()
 master=dst/f'_work/picture_master{suffix}.mp4';record=dst/f'records/encoding_method{suffix}.json'
 inputs=[dict(key=s['key'],sha256=sha(Path(s['encoded_file'])),frames=s['frames']) for s in shots]
 previous=read(record) if record.exists() else {}
 if master.exists() and previous.get('inputs')==inputs and previous.get('master_sha256')==sha(master):return
 cmd=['ffmpeg','-y','-nostdin','-v','warning','-f','rawvideo','-pix_fmt','yuv420p','-s',f'{1920*scale}x{1080*scale}','-r','30','-i','pipe:0','-an','-c:v','libx264','-threads','2','-preset','veryfast','-x264-params','rc-lookahead=5:sync-lookahead=0','-crf','16','-profile:v','high','-pix_fmt','yuv420p','-g','60','-bf','2','-video_track_timescale','15360','-movie_timescale','48000','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709','-movflags','+faststart',str(master)]
 with (dst/f'records/encode{suffix}.log').open('w') as log:
  encoder=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for shot in shots:
    dec=['ffmpeg','-nostdin','-v','error','-threads','1','-i',shot['encoded_file'],'-map','0:v:0','-an']
    if shot['segment_id']=='BRAND' and scale==2:dec+=['-vf','scale=3840:2160:flags=lanczos','-filter_threads','1']
    subprocess.run([*dec,'-frames:v',str(shot['frames']),'-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=encoder.stdin,stderr=log,check=True)
   encoder.stdin.close();assert encoder.wait()==0
  except BaseException:encoder.kill();encoder.wait();raise
 save(record,dict(inputs=inputs,master_sha256=sha(master),method='Each logical shot and common brand clip is independently decoded to raw yuv420p; one H.264 encoder writes the entire movie.',common_brand_4k='Existing approved 1080p OP/ED scaled with Lanczos' if scale==2 else None))

if __name__=='__main__':
 run(sys.argv[1],int(sys.argv[2]))
