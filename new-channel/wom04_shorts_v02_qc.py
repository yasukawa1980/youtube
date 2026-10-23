"""v02 revision checks: preserve audio and scope, validate glyphs/motion/media."""
import argparse,csv,json,subprocess,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import wom_shorts_qc as legacy
from wom04_shorts_v02 import ROOT,V1,REQUEST,read,save,sha,ff,FPS,stream_hash
from wom04_shorts import levels
legacy.ROOT=ROOT

def verify():
    rows=read(ROOT/'records/shorts.json')['shorts']; shots=read(ROOT/'records/render_shots.json'); media=[];usage=[]
    original=read(V1/'records/shorts.json')['shorts']
    assert len(shots)==7 and len({s['source']['sha256'] for s in shots})==7
    oldshots=read(V1/'records/render_shots.json')
    for s,o in zip(shots,oldshots):
        for key in ['asset_id','source','texts','start_frame','end_frame','frames','zoom_start','zoom_end']:
            assert s[key]==o[key],(s['asset_id'],key)
        assert s['frames']/FPS>=1.5
        if s['asset_id'] not in ['A02','A12']:assert s==o
        else:
            assert s['source_crop_normalized'][1]>=.38 if s['asset_id']=='A02' else True
        assert sha(Path(s['source']['path']))==s['source']['sha256']
        usage.append(dict(short_id=s['short_id'],asset_id=s['asset_id'],start_seconds=s['start_frame']/FPS,end_seconds=s['end_frame']/FPS,use_count=1,source_sha256=s['source']['sha256']))
    for id in ['P2','P3']:assert (ROOT/f'_work/{id}.ass').read_bytes()==(V1/f'_work/{id}.ass').read_bytes()
    assert stream_hash(ROOT/'_work/P1_picture.mp4','v')==stream_hash(V1/'_work/P1_picture.mp4','v')
    for s,o in zip(rows,original):
        id=s['id'];p=ROOT/f'deliverables/QO_short_EP004_{id}_v02.mp4';old=V1/f'deliverables/QO_short_EP004_{id}_v01.mp4'
        assert s['text']==o['text'] and s['frames']==o['frames'] and s['words_timed']==o['words_timed']
        if id!='P1':assert s==o
        else:
            assert s['caption_groups'][:-2]==o['caption_groups'][:-2]
            assert s['caption_groups'][-2]['text']=='made on Crete,'
            assert s['caption_groups'][-1]['text']=='about one and a half meters tall.'
            cap=next(c for c in read(ROOT/'records/caption_manifest.json') if c['text']=='about one and a half meters tall.')
            assert cap['lines']==['about one and a half','meters tall.']
        assert ' '.join(g['text'] for g in s['caption_groups'])==s['text']
        assert stream_hash(p,'a')==stream_hash(old,'a')
        ff(['-i',p,'-f','null','-'])
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
        v=next(t for t in info['streams'] if t['codec_type']=='video')
        assert (v['width'],v['height'],v['avg_frame_rate'],int(v['nb_frames']))==(1080,1920,'30/1',s['frames'])
        assert 15<=float(info['format']['duration'])<=20
        pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(p)],text=True).splitlines()))
        assert v['time_base']=='1/15360' and pts==list(range(0,s['frames']*512,512))
        q=levels(p);assert abs(float(q['input_i'])+14)<=.15 and float(q['input_tp'])<=-1
        oldqc=next(m for m in read(V1/'records/media_qc.json')['media'] if m['id']==id)
        media.append(dict(id=id,name=p.name,sha256=sha(p),bytes=p.stat().st_size,frames=s['frames'],duration_seconds=float(info['format']['duration']),video_duration_seconds=s['duration_seconds'],lufs=float(q['input_i']),true_peak_dbtp=float(q['input_tp']),voice_onset_normalized_stem_seconds=oldqc['voice_onset_normalized_stem_seconds'],bgm_during_narration_dbfs=oldqc['bgm_during_narration_dbfs'],cta_seconds=s['duration_seconds']-s['cta_start'],v01_audio_stream_sha256=stream_hash(old,'a'),v02_audio_stream_sha256=stream_hash(p,'a'),audio_identical_to_v01=True,full_decode=True,exact_pts_30fps=True))
        print('VERIFIED',id,'audio identical',q['input_i'],q['input_tp'],flush=True)
    save(ROOT/'records/media_qc.json',dict(passed=True,media=media,request_sha256=sha(REQUEST),render_shots_sha256=sha(ROOT/'records/render_shots.json'),cuts_sources_labels_unchanged=True,P2_P3_ASS_byte_identical=True,P1_underlying_picture_stream_identical=True,human_full_listening=False))
    save(ROOT/'records/asset_usage.json',dict(passed=True,unique_sources=7,rows=usage,same_source_not_repeated_within_episode=True))
    with (ROOT/'deliverables/asset_usage.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(usage[0]),lineterminator='\n');w.writeheader();w.writerows(usage)

def frames():
 rows=read(ROOT/'records/shorts.json')['shorts'];font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16);records=[]
 for s in rows:
  stem=f'QO_short_{s["episode"]}_{s["id"]}_v02';video=ROOT/f'deliverables/{stem}.mp4';times=list(np.arange(0,s['duration_seconds'],2));items=[]
  mid=ROOT/f'review/{stem}_mid.jpg';ff(['-ss',s['duration_seconds']/2,'-i',video,'-frames:v',1,'-vf','scale=720:1280','-q:v',3,mid])
  sheet=Image.new('RGB',(1280,math.ceil(len(times)/5)*480),'#0c1820');d=ImageDraw.Draw(sheet)
  for i,t in enumerate(times):
   frame=ROOT/f'_work/{stem}_{i:02}.jpg';ff(['-ss',float(t),'-i',video,'-frames:v',1,'-vf','scale=256:455','-q:v',3,frame]);x=i%5*256;y=i//5*480;sheet.paste(Image.open(frame),(x,y));d.text((x+8,y+456),f'{s["id"]} {t:.0f}s',font=font,fill='#f4efdf');items.append(float(t))
  out=ROOT/f'review/{stem}_every2s.jpg';sheet.save(out,quality=88,optimize=True);assert max(sheet.size)<=1280 and out.stat().st_size<1000000;records.append({'id':s['id'],'video_sha256':sha(video),'midpoint_seconds':s['duration_seconds']/2,'midpoint_jpg':mid.name,'every_2s_jpg':out.name,'sample_seconds':items});print('FRAMES',s['id'],len(times),flush=True)
 save(ROOT/'records/frame_review.json',{'shorts':records,'all_midpoints_and_every_2_seconds':True})


def proof_frames():
    ff(['-ss',15.5,'-i',ROOT/'deliverables/QO_short_EP004_P1_v02.mp4','-frames:v',1,'-vf','scale=540:960','-q:v',3,ROOT/'review/QO_short_EP004_P1_v02_about.jpg'])
    shots=read(ROOT/'records/render_shots.json')
    for aid in ['A12','A02']:
        s=next(s for s in shots if s['asset_id']==aid);ns=[0,s['frames']//2,s['frames']-1];sheet=Image.new('RGB',(1080,680),'#0c1820');d=ImageDraw.Draw(sheet)
        for i,n in enumerate(ns):
            f=ROOT/f'_work/{aid}_{n}.jpg';ff(['-ss',n/FPS,'-i',s['encoded_file'],'-frames:v',1,'-vf','scale=360:640','-q:v',2,f]);sheet.paste(Image.open(f),(i*360,0));d.text((i*360+8,644),f'{aid} frame {n}',fill='white')
        sheet.save(ROOT/f'review/QO_short_EP004_{s["short_id"]}_v02_{aid}_motion.jpg',quality=88,optimize=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['verify','motion','glyphs','frames']);a=p.parse_args()
    (getattr(legacy,a.stage) if a.stage in ['motion','glyphs'] else globals()[a.stage])()
    if a.stage=='frames':proof_frames()
