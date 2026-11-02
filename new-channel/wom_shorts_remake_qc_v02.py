"""Decode final remakes, measure text contrast, geometry, timing, and audio."""
import argparse,json,math,re,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from wom_shorts_remake_v02 import ROOT,read,save,sha
from wom_shorts_remake_produce import levels

def lum(a):
 a=a.astype(float)/255;a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4);return a@np.array([.2126,.7152,.0722])

def decode(path,indices):
 expr='+'.join(f'eq(n\\,{n})' for n in indices);p=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-i',str(path),'-vf',f'select={expr}','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);out={}
 for n in indices:
  b=p.stdout.read(1080*1920*3);assert len(b)==1080*1920*3,(n,len(b));out[n]=np.frombuffer(b,np.uint8).reshape(1920,1080,3).copy()
 assert p.stdout.read()==b'';err=p.stderr.read().decode();assert p.wait()==0 and not err,err
 return out

def contrast(frame,layer):
 a=np.array(Image.open(layer).convert('RGBA'));core=(a[:,:,3]>=253)&(np.max(abs(a[:,:,:3].astype(int)-np.array([244,239,223])),axis=2)<3);core=np.asarray(Image.fromarray(core.astype('uint8')*255).filter(ImageFilter.MinFilter(3)))>0
 ink=a[:,:,3]>174;ring=(np.asarray(Image.fromarray(ink.astype('uint8')*255).filter(ImageFilter.MaxFilter(19)))>0)&~(np.asarray(Image.fromarray(ink.astype('uint8')*255).filter(ImageFilter.MaxFilter(7)))>0)&(a[:,:,3]==173)
 assert core.sum()>40 and ring.sum()>40
 L=lum(frame);lo=float(L[core].min());hi=float(L[ring].max());ratio=(lo+.05)/(hi+.05);assert ratio>=4.5,ratio
 return dict(contrast_ratio=ratio,minimum_text_luminance=lo,maximum_background_luminance=hi)

def audit(ids):
 caps=read(ROOT/'records/caption_manifest.json');shots=read(ROOT/'records/visual_manifest.json')['shots'];result=[]
 for s in read(ROOT/'records/shorts.json')['shorts']:
  sid=s['id']
  if sid not in ids:continue
  p=ROOT/f'deliverables/QO_short_remake_{sid}_v02.mp4';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]));v=next(x for x in probe['streams'] if x['codec_type']=='video');assert (v['codec_name'],v['profile'],v['pix_fmt'],v['width'],v['height'],v['r_frame_rate'],int(v['nb_frames']))==('h264','High','yuv420p',1080,1920,'30/1',s['frames'])
  continuous=subprocess.run(['ffmpeg','-nostdin','-v','warning','-i',str(p),'-f','null','-'],capture_output=True,text=True);assert continuous.returncode==0 and continuous.stderr=='',continuous.stderr
  cs=[x for x in caps if x['short_id']==sid];gs=[x for x in shots if x['short_id']==sid]
  assert ' '.join(c['text'] for c in cs)==s['text'];cross=sum(bool(re.search(r'[.!?]["”]?\s',c['text'])) for c in cs);assert cross==0
  ns=sorted(set([0,15,30,45,60,75,s['cta_start_frame'],s['frames']-1]+list(range(0,s['frames'],60))+[(c['start_frame']+c['end_frame'])//2 for c in cs]+[g['start_frame'] for g in gs]))
  frames=decode(p,ns);cr=[]
  for c in cs:
   n=(c['start_frame']+c['end_frame'])//2;cr.append(dict(page=c['page'],text=c['text'],frame=n,**contrast(frames[n],c['file'])))
  hc=contrast(frames[0],ROOT/f'assets/{sid}_headline.png');audio=levels(p);assert abs(float(audio['input_i'])+14)<=.15 and float(audio['input_tp'])<=-1
  motion=[]
  for g in gs:
   samples=[]
   for n in range(g['frames']):
    f=n/max(1,g['frames']-1)
    if 'keyframes' in g:
     at=g['start_frame']+n;ks=g['keyframes'];i=min(len(ks)-2,max(0,next((j-1 for j,k in enumerate(ks) if k['frame']>at),len(ks)-2)));a,b=ks[i],ks[i+1];t=np.clip((at-a['frame'])/max(1,b['frame']-a['frame']),0,1);c=np.array(a['rect'])+(np.array(b['rect'])-a['rect'])*t;z=1
    else:
     a=np.array(g['crop_start'],float);b=np.array(g['crop_end'],float);c=a+(b-a)*f;z=math.exp(math.log(g['zoom_end'])*f)
    samples.append([(c[0]+c[2])/2,(c[1]+c[3])/2,(c[2]-c[0])/z,(c[3]-c[1])/z])
   speed=np.linalg.norm(np.diff(samples,axis=0),axis=1);ratio=float(np.percentile(speed,95)/np.median(speed)) if np.median(speed)>1e-9 else 1.0
   motion.append(dict(asset_id=g['asset_id'],p95_over_median=ratio,method='Rendered camera source-coordinate trajectory, per-frame Euclidean displacement; shot boundaries excluded. Not optical flow.',native_max_scale=g['native_max_scale'],passed=ratio<=2.5))
  for kind,inds in [('opening',[0,15,30,45,60,75]),('every2s',list(range(0,s['frames'],60))),('CTA',[s['cta_start_frame'],s['frames']-1])]:
   folder=ROOT/f'review/{sid}_{kind}';folder.mkdir(exist_ok=True);cols=min(5,len(inds));sheet=Image.new('RGB',(cols*240,math.ceil(len(inds)/cols)*448),'#0c1820');d=ImageDraw.Draw(sheet)
   for j,n in enumerate(inds):
    im=Image.fromarray(frames[n]);im.thumbnail((720,1280));im.save(folder/f'{n:04}.jpg',quality=88,optimize=True);thumb=im.resize((240,427));x=j%cols*240;y=j//cols*448;sheet.paste(thumb,(x,y));d.text((x+5,y+430),f'{sid} {n/30:.2f}s',fill='white')
   sheet.thumbnail((1280,1280));sheet.save(ROOT/f'review/{sid}_{kind}.jpg',quality=90,optimize=True)
  assert s['cta_start']>=s['native_audio_duration'];assert abs(s['duration_seconds']-s['cta_start']-2.5)<1e-7
  result.append(dict(id=sid,path=str(p),sha256=sha(p),bytes=p.stat().st_size,video_duration=s['frames']/30,container_duration=float(probe['format']['duration']),video_format={k:v[k] for k in ['codec_name','profile','pix_fmt','width','height','r_frame_rate','nb_frames']},continuous_decode_warning_count=0,audio=audio,voice_onset=s['voice_onset_seconds'],native_voice_end=s['native_audio_duration'],last_voice_activity=s['last_voice_activity_seconds'],cta_start=s['cta_start'],cta_end=s['duration_seconds'],cta_duration=2.5,cta_horizontal_scale=1,caption_text_exact=True,cross_sentence_caption_count=0,subtitle_contrast=cr,minimum_contrast=min(c['contrast_ratio'] for c in cr),headline_contrast=hc,word_count_exceptions=[dict(text=c['text'],lines=c['word_count_exceptions'],reason='Exact sentence boundary takes precedence for short sentences / remainders.') for c in cs if c['word_count_exceptions']],foreground_height_fraction=gs[0]['foreground_height_fraction'],first_evidence_cut=gs[1]['cut_seconds'],cut_timing_note='The individual approved phrase cues take precedence over the generic approximately-1.5-second guidance.',cuts=[dict(asset=g['asset_id'],start=g['start_frame']/30,end=g['end_frame']/30,cue=g['cut_phrase']) for g in gs],motion=motion,human_full_listening=False,youtube_posted=False))
  from wom01_quiet_origins import stream_hash
  old=ROOT.parent/'作り直し_v01_20261102'/f'deliverables/QO_short_remake_{sid}_v01.mp4'
  assert stream_hash(old,'a')==stream_hash(p,'a')
  result[-1]['audio_stream_identical_to_v01']=True
  assert all(r['glyph_height']==52 for c in cs for r in c['rows'])
  result[-1]['caption_glyph_height']=52
  result[-1]['caption_rows']=[dict(text=r['text'],first_word=r['text'].split()[0],last_word=r['text'].split()[-1],glyph_height=r['glyph_height'],bbox=r['glyph_bbox']) for c in cs for r in c['rows']]
  print('QC',sid,'PASS',min(c['contrast_ratio'] for c in cr),audio['input_i'],audio['input_tp'],flush=True)
 prior=read(ROOT/'records/final_qc.json') if (ROOT/'records/final_qc.json').exists() else []
 save(ROOT/'records/final_qc.json',[r for r in prior if r['id'] not in ids]+result)

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ids',default='A1R,M1R,P1R,T1R,A3R');a=p.parse_args();audit(a.ids.split(','))
