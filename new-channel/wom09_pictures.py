"""EP009: 22 content shots plus unchanged brand clips; independent decoders, one encoder."""
import subprocess,json
import numpy as np
from wom09_produce import ROOT,OP,END,read,save,sha,ff,probe
from wom09_render import camera
CUTS={'P03':['It ends not with'], 'P04':['all of that lies beyond'], 'P05':['In the song, the Trojans argue'], 'P10':['The priest Laocoön warns','and hurls his spear'], 'P12':['And how many men'], 'P13':['Today, even computer programs']}
REVEALS={'D_options':['break it open','throw it down','or keep it'], 'D_lostpoems':['the horse taken','a broken wall','the Trojan priest','and Sinon'], 'D_passages':['In Homer, the horse']}
def phrase_frame(cues,phrase):
 cue=next(c for c in cues if phrase in c['text']);fraction=len(cue['text'].split(phrase)[0])/len(cue['text'])
 return round((cue['start']+(cue['end']-cue['start'])*fraction)*30)
def main():
 master=read(ROOT/'records/master_timeline.json');manifest=read(ROOT/'records/visual_manifest.json')['shots'];narr=read(ROOT/'records/narration_timeline_en.json')['segments'];shots=[]
 def brand(key,path):
  a,b=master['brand_intervals'][key];n=round((b-a)*30);v=next(s for s in probe(path)['streams'] if s['codec_type']=='video')
  assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'30/1',n)
  shots.append({'key':key,'segment_id':'BRAND','start':a,'end':b,'frames':n,'encoded_file':str(path),'original_source':str(path),'original_sha256':sha(path)})
 for i,seg in enumerate(master['segments']):
  group=[s for s in manifest if s['segment_id']==seg['id']];a=0 if i==0 else round(seg['start']*30);b=round(seg['end']*30);bounds=[a,*[phrase_frame(narr[i]['cues'],p) for p in CUTS.get(seg['id'],[])],b];assert len(bounds)==len(group)+1
  for j,s in enumerate(group):
   key=s['key'];n=int(bounds[j+1]-bounds[j]);assert n>0;out=ROOT/f'_work/render/{seg["id"]}_{j+1:02}_{key}.mp4';stamp=out.with_suffix('.json');static=key.startswith('D_') or key=='credits';stages=s.get('stages',[])
   args=['-loop',1,'-framerate',30,'-i',ROOT/(stages[0]['file'] if key in REVEALS else s['file'])]
   finish=phrase_frame(narr[i]['cues'],'Yet the Iliad ends')-bounds[j] if key=='met_202259' else None
   filt='[0:v]format=yuv420p[v]' if static else camera(n,s['camera_band'],amount=s['zoom_amount'],direction={'R06':'r06_title','R01':'r01_wall'}.get(key),finish_frame=finish)
   changeframes=[]
   if key in REVEALS:
    changes=[min(n-1,max(1,phrase_frame(narr[i]['cues'],p)-bounds[j])) for p in REVEALS[key]]
    assert changes==sorted(set(changes))
    filters=[];prev='0:v'
    for k,(stage,at) in enumerate(zip(stages[1:],changes),1):
     args+=['-loop',1,'-framerate',30,'-i',ROOT/stage['file']];outlabel=f's{k}';filters.append(f"[{prev}][{k}:v]overlay=0:0:enable='gte(n,{at})':format=yuv444[{outlabel}]");prev=outlabel
    filt=';'.join(filters)+f';[{prev}]format=yuv420p[v]';changeframes=changes
   cfg={'image_sha256':sha(ROOT/s['file']),'stages':[{'sha256':sha(ROOT/x['file']),'stage':x['stage']} for x in stages],'frames':n,'filter':filt,'lossless_static_intermediate':static,'stage_change_frames':changeframes}
   if not(out.exists() and stamp.exists() and read(stamp)==cfg):
    quality=['-qp',0,'-profile:v','high444'] if static else ['-crf',18,'-profile:v','high']
    ff([*args,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-frames:v',n,'-an','-c:v','libx264','-threads',2,'-preset','veryfast',*quality,'-pix_fmt','yuv420p','-video_track_timescale',15360,out]);save(stamp,cfg)
   assert int(next(v for v in probe(out)['streams'] if v['codec_type']=='video')['nb_frames'])==n
   shots.append({**s,'start':bounds[j]/30,'end':bounds[j+1]/30,'frames':n,'encoded_file':str(out.relative_to(ROOT)),'render_config':cfg,'stage_change_frames':changeframes})
   print('RENDERED',seg['id'],key,n,flush=True)
  if i==1:brand('opening',OP)
 brand('endcard',END)
 assert len(shots)==24 and sum(s['frames'] for s in shots)==round(master['duration_seconds']*30)
 save(ROOT/'records/render_shots.json',shots)
 out=ROOT/'_work/picture_master.mp4';records=[]
 cmd=['ffmpeg','-nostdin','-y','-v','warning','-f','rawvideo','-pixel_format','yuv420p','-video_size','1920x1080','-framerate','30','-i','pipe:0','-an','-c:v','libx264','-threads','3','-preset','medium','-crf','16','-profile:v','high','-level:v','4.1','-pix_fmt','yuv420p','-g','60','-bf','2','-maxrate','20M','-bufsize','30M','-fps_mode','passthrough','-video_track_timescale','15360','-movie_timescale','48000','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(out)]
 with (ROOT/'records/encode.log').open('w') as log:
  enc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for s in shots:
    src=ROOT/s['encoded_file'];v=next(x for x in probe(src)['streams'] if x['codec_type']=='video');assert int(v['nb_frames'])==s['frames']
    subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(src),'-map','0:v:0','-an','-pix_fmt','yuv420p','-fps_mode','passthrough','-f','rawvideo','pipe:1'],stdout=enc.stdin,stderr=log,check=True)
    records.append({'key':s['key'],'frames':s['frames'],'input_profile':v['profile']});print('ASSEMBLED',s['key'],flush=True)
   enc.stdin.close();assert enc.wait()==0
  except BaseException:
   enc.kill();enc.wait();raise
 save(ROOT/'records/encoding_method.json',{'method':'Independent shot decoders feeding one raw-video encoder','shots':records,'command':cmd,'cut_timing':'Synthesized sentence boundaries; phrase offset estimated by character proportion within each sentence','diagram_reveals':'Explicit whole-frame row reveals; stage frame numbers recorded'})
 print('PICTURES COMPLETE',len(shots),flush=True)
if __name__=='__main__':main()
