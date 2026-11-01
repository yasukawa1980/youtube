"""EP009 Shorts verification with the established full-frame/glyph checks."""
import argparse,csv,json,subprocess,math
from pathlib import Path
import numpy as np
import soundfile as sf
from wom09_shorts_render import ROOT,REQUEST,SR,FPS,VERSION,read,save,sha,ff,levels
from wom01_quiet_origins import stream_hash

def verify():
 rows=[s for s in read(ROOT/'records/shorts.json')['shorts'] if s['id'] in ['T1','T2','T3']];shots=read(ROOT/'records/render_shots.json');usage=[];media=[];audio=read(ROOT/'records/audio_qc.json');assert audio['passed'];assert read(ROOT/'records/narration.json')['request_sha256']==sha(REQUEST)
 for episode in ['EP009']:
  members={s['id'] for s in rows if s['episode']==episode};sources=[s['source']['sha256'] for s in shots if s['short_id'] in members];assert len(sources)==len(set(sources))
 for s in rows:
  for phrase in ['670 BC.']:
   if phrase in s['text']:assert any(phrase in g['text'] for g in s['caption_groups'])
  id=s['id'];groups=[g for g in shots if g['short_id']==id];assert sum(g['frames'] for g in groups)==s['frames']
  for a,b in zip(groups,groups[1:]):assert a['end_frame']==b['start_frame']
  for g in groups:
   assert g['frames']/FPS>=1.5
   if g['cut_phrase'] is not None:assert abs(g['start_frame']/FPS-g['cut_word_seconds'])<=1/60
   if g['asset_id']=='met_437153':assert g['source_crop_normalized']==[.12,.10,.95,.33] and g['background_also_uses_only_crop']
   if g['asset_id']=='jebb1904_15':assert g['source_crop_pixels']==[60,1400,1015,1524]
   assert sha(Path(g['source']['path']))==g['source']['sha256'];assert sha(Path(g['encoded_file']))==g['encoded_sha256'];usage.append({'short_id':id,'episode':s['episode'],'asset_id':g['asset_id'],'start_seconds':g['start_frame']/FPS,'end_seconds':g['end_frame']/FPS,'use_count':1,'source_sha256':g['source']['sha256']})
   assert all(140<=t['bbox'][1]<t['bbox'][3]<=260 for t in g['texts'])
  p=ROOT/f'deliverables/QO_short_{s["episode"]}_{id}_{VERSION}.mp4';decode=subprocess.run(['ffmpeg','-nostdin','-v','warning','-i',str(p),'-f','null','-'],capture_output=True,text=True,check=True);assert not decode.stderr.strip(),decode.stderr;info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]));v=next(t for t in info['streams'] if t['codec_type']=='video');assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',s['frames']);assert abs(float(info['format']['duration'])-s['frames']/FPS)<.04;assert 15<=float(info['format']['duration'])<=24;assert v['codec_name']=='h264' and v['profile']=='High' and v['pix_fmt']=='yuv420p'
  pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()));assert v['time_base']=='1/15360' and pts==list(range(0,s['frames']*512,512))
  raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(p),'-t','0.01','-ar','24000','-ac','2','-f','f32le','-']);initial=np.frombuffer(raw,np.float32);initial_dbfs=20*math.log10(max(1e-12,float(np.sqrt(np.mean(initial**2)))));assert initial_dbfs>-70
  frameinfo=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=width,height,pix_fmt','-of','json',str(p)]))['frames'];assert len(frameinfo)==s['frames'] and {(f['width'],f['height'],f['pix_fmt']) for f in frameinfo}=={(1080,1920,'yuv420p')}
  q=levels(p);assert abs(float(q['input_i'])+14)<=.15 and float(q['input_tp'])<=-1;assert stream_hash(p,'a')==stream_hash(ROOT/f'audio/{id}_final.m4a','a')
  voice,sr=sf.read(ROOT/f'audio/{id}_normalized.wav',dtype='float32');step=round(.01*sr);power=np.array([np.sqrt(np.mean(voice[i:i+step]**2)) for i in range(0,len(voice),step)]);onset=float(np.where(power>10**(-50/20))[0][0]*.01);assert onset<=.3
  aq=next(a for a in audio['reports'] if a['id']==id);assert abs(aq['bgm_during_narration_dbfs']-aq['voice_during_narration_dbfs']+15)<.001;assert aq['bgm_first_10ms_dbfs']>-70 and not aq['bgm_fade_in']
  media.append({'id':id,'name':p.name,'sha256':sha(p),'bytes':p.stat().st_size,'frames':s['frames'],'duration_seconds':float(info['format']['duration']),'video_duration_seconds':s['duration_seconds'],'lufs':float(q['input_i']),'true_peak_dbtp':float(q['input_tp']),'voice_onset_normalized_stem_seconds':onset,'voice_onset_threshold_dbfs':-50,'voice_onset_window_seconds':.01,'bgm_during_narration_dbfs':aq['bgm_during_narration_dbfs'],'full_decode':True,'continuous_decode_warnings':0,'video_profile':v['profile'],'pixel_format':v['pix_fmt'],'exact_pts_30fps':True,'audio_stream_matches_measured_m4a':True,'final_mix_first_10ms_dbfs':initial_dbfs,'cta_seconds':s['duration_seconds']-s['cta_start']});print('VERIFIED',id,q['input_i'],q['input_tp'],onset,flush=True)
 assert len(usage)==7
 with (ROOT/'deliverables/asset_usage.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(usage[0]));w.writeheader();w.writerows(usage)
 save(ROOT/'records/asset_usage.json',{'passed':True,'unique_sources':7,'rows':usage,'same_source_not_repeated_within_episode':True})
 save(ROOT/'records/media_qc.json',{'passed':True,'media':media,'request_sha256':sha(REQUEST),'render_shots_sha256':sha(ROOT/'records/render_shots.json'),'audio_qc_sha256':sha(ROOT/'records/audio_qc.json'),'human_full_listening':False})



def motion():
    hooks={h['id']:h for h in read(ROOT/'records/headlines.json')};checks=[]
    for s in read(ROOT/'records/render_shots.json'):
        sid=s['short_id'];b=s['art_box'];x=round(b[0]+.15*(b[2]-b[0]));y=round(b[1]+.15*(b[3]-b[1]));w=round(.7*(b[2]-b[0]));h=round(.7*(b[3]-b[1]))
        mask=np.ones((h,w),bool);exclusions=[]
        if s['start_frame']==0:
            exclusions=[[0,110,1080,280],[60,1130,910,1470]]
            hb=hooks[sid]['overlay_bbox'];exclusions.append([hb[0]-24,hb[1]-24,hb[2]+24,hb[3]+24])
            for a,b1,c,d in exclusions:mask[max(0,b1-y):max(0,min(h,d-y)),max(0,a-x):max(0,min(w,c-x))]=False
        assert mask.sum()>10000
        p=ROOT/f'deliverables/QO_short_EP009_{sid}_v01.mp4';sig=sha(p)
        filt=f'trim=start_frame={s["start_frame"]}:end_frame={s["end_frame"]},format=gray,crop={w}:{h}:{x}:{y}:exact=1'
        proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(p),'-vf',filt,'-pix_fmt','gray','-fps_mode','passthrough','-f','rawvideo','-'],stdout=subprocess.PIPE)
        prior=None;ds=[]
        while True:
            raw=proc.stdout.read(w*h)
            if not raw:break
            assert len(raw)==w*h;a=np.frombuffer(raw,dtype=np.uint8).reshape(h,w)[mask].astype(np.int16)
            if prior is not None:ds.append(float(np.abs(a-prior).mean()))
            prior=a
        assert proc.wait()==0 and len(ds)==s['frames']-1
        med=float(np.median(ds));p95=float(np.quantile(ds,.95));ratio=p95/med if med else 1 if p95==0 else None
        q=dict(roi_xywh=[x,y,w,h],excluded_rects=exclusions,measured_pixels=int(mask.sum()),frame_pairs=len(ds),median=med,p95=p95,p95_over_median=ratio,differences=ds)
        passed=ratio is not None and ratio<=2.5
        checks.append(dict(short_id=sid,asset_id=s['asset_id'],encoded_sha256=sig,measurement=q,passed=passed,changed_first_shot=s['start_frame']==0))
        print('MOTION',sid,s['asset_id'],ratio,passed,flush=True)
    save(ROOT/'records/motion_qc.json',dict(passed=all(c['passed'] for c in checks),threshold=2.5,checks=checks,
        method='All consecutive final-MP4 frame pairs within each shot; 8-bit gray MAD over interior 70% of the artwork. First-shot masks exclude static header, subtitle region, and fading headline with 24px margin, to measure camera motion rather than typography. No frame subsampling or temporal trimming.'))
    assert all(c['passed'] for c in checks)


def headline_check():
    import imageio_ffmpeg
    import wom09_shorts_render as r
    rows=[]
    for hook in r.read(r.ROOT/'records/headlines.json'):
     cmd=[imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-v','error','-loop','1','-framerate','30','-i',hook['file'],'-vf','format=rgba,fade=t=out:st=2:d=0.3:alpha=1','-frames:v','70','-pix_fmt','rgba','-f','rawvideo','-']
     proc=subprocess.Popen(cmd,stdout=subprocess.PIPE);means=[]
     for n in range(70):
      b=proc.stdout.read(1080*1920*4);assert len(b)==1080*1920*4
      a=np.frombuffer(b,np.uint8).reshape(1920,1080,4)[:,:,3];means.append(float(a.mean()))
     assert proc.wait()==0
     assert all(v==means[0] for v in means[:61]) and all(a>b for a,b in zip(means[60:69],means[61:70])) and means[69]==0
     rows.append(dict(id=hook['id'],opaque_through_frame=60,fade_frames=list(range(61,69)),fully_transparent_frame=69,alpha_mean_by_frame=means,headline_text=hook['text'],glyph_heights=[x['glyph_height'] for x in hook['lines']],glyph_bounds=[x['bbox'] for x in hook['lines']],passed=True))
    r.save(r.ROOT/'records/headline_qc.json',dict(passed=True,checks=rows,method='Actual RGBA fade filter used in final encoder evaluated for frames 0–69. Headline PNG glyph bounds measured before composition; final continuous-decode images visually inspected.'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['verify','motion','headline_check']);a=p.parse_args();globals()[a.stage]()
