"""Quiet Origins: local 4s ident / 20s end-card trials and bilingual connection previews.
Native procedural motion, approved Q texture, original locally synthesized audio.
No generation APIs, purchases, channel mutations, or edits to the v07 masters.
"""
import argparse, json, math, os, subprocess, hashlib
from pathlib import Path
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont
from wom01_multilingual_render import save,read,sha,probe,measure

ROOT=Path(os.environ['QO_MOTION_ROOT'])
BRAND=Path('/Users/ryo/Desktop/新チャンネル/ブランド素材/A案_登録用_v01_20261021')
EP=Path('/Users/ryo/Desktop/新チャンネル/EP001_Anubis/Quiet_Origins_v07_20261021')
W,H,FPS,SR=1920,1080,30,48000
BG=(12,24,32);GOLD=(216,181,117);IVORY=(244,239,223)
SERIF='/System/Library/Fonts/Supplemental/Georgia.ttf'

def ff(args):
    p=subprocess.run(['ffmpeg','-nostdin','-y','-v','error',*map(str,args)],capture_output=True)
    if p.returncode:raise RuntimeError(p.stderr.decode()[-6000:])

def smooth(t,a,b):
    u=np.clip((t-a)/(b-a),0,1);return u*u*(3-2*u)

def text_layer(value,y,size,color=IVORY):
    im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im);font=ImageFont.truetype(SERIF,size)
    x=(W-d.textlength(value,font=font))/2;d.text((x,y),value,font=font,fill=(*color,255))
    return im

def background():
    # Code-native atlas contours; not a map of a named place.
    rng=np.random.default_rng(318);noise=rng.normal(0,1.25,(H,W,1));yy,xx=np.mgrid[:H,:W]
    vignette=1-.19*((xx-W/2)/(W/2))**2-.14*((yy-H/2)/(H/2))**2
    arr=np.clip(np.array(BG)[None,None,:]*vignette[:,:,None]+noise,0,255).astype('uint8')
    im=Image.fromarray(arr);d=ImageDraw.Draw(im)
    for side in [0,1]:
      for k in range(29):
        points=[]
        for y in range(-20,H+21,5):
          x=-100+k*12+64*math.sin(y/210+k*.095)+24*math.sin(y/61+k*.13)
          points.append((x if side==0 else W-x,y))
        d.line(points,fill=(58+k//5,57+k//6,48),width=1)
      for radius in [350,550,760]:
        cx=-160 if side==0 else W+160;cy=220 if side==0 else 790
        for degree in np.arange(0,360,1.6):
          a=math.radians(degree);b=math.radians(degree+.55)
          d.line((cx+radius*math.cos(a),cy+radius*math.sin(a),cx+radius*math.cos(b),cy+radius*math.sin(b)),fill=(84,76,56),width=1)
    for cx,cy in [(155,700),(1760,410)]:
      for angle in range(0,360,45):
        r=58 if angle%90==0 else 28;a=math.radians(angle)
        d.line((cx,cy,cx+r*math.cos(a),cy+r*math.sin(a)),fill=(106,91,63),width=1)
      d.ellipse((cx-8,cy-8,cx+8,cy+8),outline=(106,91,63),width=1)
    return im

def logo_layer(size,xy):
    # Video compositor alpha matte: retain the approved gold pixels, no redrawing of Q.
    im=Image.open(BRAND/'Quiet_Origins_icon_A_1024.png').convert('RGB')
    a=np.array(im,dtype=np.float32);warm=np.minimum(a[:,:,0]-a[:,:,2],a[:,:,1]-a[:,:,2])
    alpha=np.clip((warm-12)/34,0,1)*255
    rgba=Image.fromarray(np.dstack([a.astype('uint8'),alpha.astype('uint8')]),'RGBA').resize((size,size),Image.Resampling.LANCZOS)
    layer=Image.new('RGBA',(W,H));layer.alpha_composite(rgba,xy);return layer

def composite(base,layer,opacity):
    if opacity<=0:return base
    if opacity>=1:return Image.alpha_composite(base,layer)
    copy=layer.copy();copy.putalpha(layer.getchannel('A').point(lambda a:round(a*opacity)))
    return Image.alpha_composite(base,copy)

def render_picture(kind):
    duration=4 if kind=='opening' else 20;count=duration*FPS
    base=background();logo=logo_layer(660,(630,95)) if kind=='opening' else logo_layer(330,(1275,410))
    title=text_layer('Quiet Origins',714,100) if kind=='opening' else text_layer('Quiet Origins',142,96)
    tagline=text_layer('Every story has an origin.',886,44)
    guide=Image.new('RGBA',(W,H));d=ImageDraw.Draw(guide)
    d.rectangle((238,367,958,772),outline=(*GOLD,135),width=2);d.ellipse((1274,410,1606,742),outline=(*GOLD,135),width=2)
    # Encode the clean end-card; a separate still documents element positions.
    yy,xx=np.mgrid[:H,:W];base_arr=np.asarray(base).astype('float32')
    out=ROOT/f'_work/{kind}_picture.mp4'
    cmd=['ffmpeg','-nostdin','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p','-video_track_timescale','15360','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    for n in range(count):
      t=n/FPS
      if kind=='opening':
        cx=-250+2500*smooth(t,.25,2.8)
        light=np.exp(-((xx-cx)/330)**2-((yy-430)/610)**2)*5.5*math.sin(math.pi*min(t/3.2,1))**2
      else:
        cx=600+300*math.sin(t*.16);light=np.exp(-((xx-cx)/760)**2-((yy-420)/720)**2)*(1.5+1.1*math.sin(t*.24))
      frame=Image.fromarray(np.clip(base_arr+light[:,:,None]*np.array([1,.80,.46]),0,255).astype('uint8')).convert('RGBA')
      frame=composite(frame,logo,float(smooth(t,.18,1.15)) if kind=='opening' else 1)
      frame=composite(frame,title,float(smooth(t,1.05,2.05)) if kind=='opening' else 1)
      if kind=='endcard':frame=composite(frame,tagline,1)
      if n in ([0,15,30,60,90,119] if kind=='opening' else [0,150,300,450,599]):
        frame.convert('RGB').save(ROOT/f'review/{kind}_{n:03}.jpg',quality=88)
      if kind=='endcard' and n==300:
        Image.alpha_composite(frame,guide).convert('RGB').save(ROOT/'review/endcard_layout_guide.jpg',quality=90)
      proc.stdin.write(frame.convert('RGB').tobytes())
    proc.stdin.close();err=proc.stderr.read();assert proc.wait()==0,err.decode()
    print('PICTURE',kind,count,flush=True)

def sound(kind):
    duration=4 if kind=='opening' else 20;t=np.arange(duration*SR)/SR
    # Original synthesized motif: D / A, matching the episode's tonal center.
    bed=(np.sin(2*np.pi*146.832384*t)+.48*np.sin(2*np.pi*220*t+.4)+.18*np.sin(2*np.pi*293.664768*t+.7))
    bed*=.55+.10*np.sin(2*np.pi*t/13)
    stereo=np.stack([bed,bed+.045*np.sin(2*np.pi*220.35*t)],axis=1)
    if kind=='opening':
      local=np.maximum(t-.85,0);tone=(np.sin(2*np.pi*440*local)+.10*np.sin(2*np.pi*880*local))*np.exp(-local/1.1)*(1-np.exp(-local/.10))*(t>=.85)
      stereo+=np.stack([tone*.38,tone*.35],axis=1)
      env=np.minimum(smooth(t,0,.55),1-smooth(t,3.1,4))
    else:
      for onset,pitch in [(1,293.664768),(7,349.228231),(13,440.)]:
        local=np.maximum(t-onset,0);tone=np.sin(2*np.pi*pitch*local)*np.exp(-local/2.5)*(1-np.exp(-local/.12))*(t>=onset)
        stereo+=np.stack([tone*.24,tone*.22],axis=1)
      env=np.minimum(smooth(t,0,.7),1-smooth(t,15,20))
    stereo*=env[:,None]
    stereo*=10**(-29/20)/np.sqrt(np.mean(stereo**2))
    raw=ROOT/f'_work/{kind}_raw.wav';sf.write(raw,stereo,SR,subtype='FLOAT')
    q=measure(raw);target=-29 if kind=='opening' else -30;gain=target-float(q['input_i'])
    stereo*=10**(gain/20);assert np.max(np.abs(stereo))<.25
    out=ROOT/f'deliverables/Quiet_Origins_{kind}_trial_v01.wav';sf.write(out,stereo,SR,subtype='PCM_24')
    q=measure(out);q.update(duration_seconds=duration,target_lufs=target,method='Original local sine synthesis, D/A tonal center; no third-party audio or API')
    save(ROOT/f'records/{kind}_audio.json',q)
    ff(['-i',ROOT/f'_work/{kind}_picture.mp4','-i',out,'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-ar',SR,'-t',duration,'-movflags','+faststart',ROOT/f'deliverables/Quiet_Origins_{kind}_trial_v01.mp4'])
    print('AUDIO',kind,q['input_i'],q['input_tp'],flush=True)

def connections():
    # Insert between paragraph N01 and N02, never mid-sentence. Preview only.
    cut=872/30;end=1555/30
    for lang in ['en','ja']:
      src=EP/f'subtitled_review/deliverables/EP001_Anubis_{lang}_v07_subtitled_review_1080p30.mp4'
      opening=ROOT/'deliverables/Quiet_Origins_opening_trial_v01.mp4'
      # Tiny audio envelopes at the splice prevent clicks without moving any speech.
      filt=f"[0:v]trim=0:{cut},setpts=PTS-STARTPTS[v0];[0:a]atrim=0:{cut},asetpts=PTS-STARTPTS,aresample=48000,afade=t=out:st={cut-.12}:d=0.12[a0];[1:v]setpts=PTS-STARTPTS[v1];[1:a]aresample=48000,asetpts=PTS-STARTPTS[a1];[0:v]trim=start={cut}:end={end},setpts=PTS-STARTPTS[v2];[0:a]atrim=start={cut}:end={end},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.015[a2];[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]"
      out=ROOT/f'deliverables/EP001_{lang}_opening_connection_trial_v01.mp4'
      ff(['-i',src,'-i',opening,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf',18,'-threads',4,'-c:a','aac','-b:a','192k','-ar',SR,'-r',FPS,'-video_track_timescale',15360,'-movflags','+faststart',out])
      # Credits + thanks, then 0.7s dissolve to the end-card. Last spoken word ends at 677.691.
      endcard=ROOT/'deliverables/Quiet_Origins_endcard_trial_v01.mp4'
      filt="[0:v]trim=start=658:end=678.7,setpts=PTS-STARTPTS,format=yuv420p,settb=AVTB[v0];[0:a]atrim=start=658:end=678.7,asetpts=PTS-STARTPTS,aresample=48000[a0];[1:v]setpts=PTS-STARTPTS,format=yuv420p,settb=AVTB[v1];[1:a]aresample=48000,asetpts=PTS-STARTPTS[a1];[v0][v1]xfade=transition=fade:duration=0.7:offset=20[v];[a0][a1]acrossfade=d=0.7:c1=tri:c2=tri[a]"
      out=ROOT/f'deliverables/EP001_{lang}_endcard_connection_trial_v01.mp4'
      ff(['-i',src,'-i',endcard,'-filter_complex_threads',2,'-filter_complex',filt,'-map','[v]','-map','[a]','-c:v','libx264','-preset','veryfast','-crf',18,'-threads',4,'-c:a','aac','-b:a','192k','-ar',SR,'-r',FPS,'-video_track_timescale',15360,'-t',40,'-movflags','+faststart',out])
      print('CONNECTION',lang,flush=True)
    save(ROOT/'records/connection_plan.json',{'opening':{'source_range':[0,end],'insert_at':cut,'ident_seconds':4,'output_seconds':end+4,'reason':'Common paragraph boundary N01/N02; no voice or caption bisected'},'ending':{'source_range':[658,678.7],'endcard_seconds':20,'overlap_seconds':.7,'dissolve_source_start':678,'last_spoken_word_ja':677.6906666666666,'output_seconds':40,'note':'Review excerpt omits four seconds of the old post-credit music; full v07 unchanged'},'source_subtitles':'Existing burned review copies; captions move with their source frames','languages':['en','ja']})

def verify():
    files=[]
    for p in sorted((ROOT/'deliverables').glob('*.mp4')):
      q=probe(p);v=next(x for x in q['streams'] if x['codec_type']=='video');expected=1675 if 'opening_connection' in p.name else 1200 if 'endcard_connection' in p.name else 120 if 'opening_trial' in p.name else 600
      assert v['width']==W and v['height']==H and v['avg_frame_rate']=='30/1' and int(v['nb_frames'])==expected,(p.name,v['nb_frames'])
      pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()))
      assert pts==list(range(0,expected*512,512)),p.name
      ff(['-i',p,'-f','null','-'])
      levels=measure(p);assert float(levels['input_tp'])<-1
      files.append({'name':p.name,'bytes':p.stat().st_size,'sha256':sha(p),'duration_seconds':float(q['format']['duration']),'frames':expected,'fps':30,'full_decode':'pass','exact_pts':True,'audio':levels})
      print('VERIFIED',p.name,expected,flush=True)
    preserved=[]
    for line in (EP/'deliverables/SHA256SUMS_shared.txt').read_text().splitlines():
      digest,name=line.split('  ',1);matches=list((EP/'deliverables').glob(name))+list((EP/'subtitled_review/deliverables').glob(name));assert matches and all(sha(p)==digest for p in matches);preserved.append(name)
    save(ROOT/'records/qc.json',{'passed':True,'files':files,'v07_files_preserved':preserved,'human_listening':False,'method':'Frame count, exact packet PTS, full decode, audio loudness/true peak; original v07 SHA-256 checked'})

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','pictures','sound','connections','verify']);a=p.parse_args()
    if a.stage=='prepare':
      assert not ROOT.exists()
      for d in ['_work','deliverables','records','review']:(ROOT/d).mkdir(parents=True)
      save(ROOT/'records/request.json',{'owner_request':'4秒オープニング・20秒エンドカードと本編接続確認版の試作を進める','status':'trial','source_episode':str(EP),'approved_icon':str(BRAND/'Quiet_Origins_icon_A_1024.png'),'approved_icon_sha256':sha(BRAND/'Quiet_Origins_icon_A_1024.png'),'paid_services':False,'youtube_changed':False,'full_episode_changed':False,'ssd_sync':False,'motion':'Independent logo/title fades; fixed typography; subtle code-generated atlas lighting','endcard':'Clean left space for future next-video element, Q on right; layout guide is a separate still'})
    elif a.stage=='pictures':
      for k in ['opening','endcard']:render_picture(k)
    elif a.stage=='sound':
      for k in ['opening','endcard']:sound(k)
    elif a.stage=='connections':connections()
    else:verify()
if __name__=='__main__':main()
