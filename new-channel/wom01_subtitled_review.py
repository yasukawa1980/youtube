"""Create separate burned-subtitle review copies from an unchanged versioned master.

WOM_EPISODE_ROOT: source master; WOM_REVIEW_ROOT: new review folder.
Stages: render, verify. Requires imageio-ffmpeg (libass) in the local environment.
"""
import argparse, json, os, shutil, subprocess
from pathlib import Path
import imageio_ffmpeg
import numpy as np
from PIL import Image,ImageDraw
from wom01_multilingual_render import read,save,sha,probe

VERSION=os.environ.get("WOM_VERSION", "v05")
STYLE="FontSize=14,BorderStyle=3,MarginV=12"

def run(args):
    subprocess.run(args,check=True)

def stem(lang):return f'EP001_Anubis_{lang}_{VERSION}_subtitled_review_1080p30'

def stream_hash(path):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()

def cues(srt):
    def seconds(t):
        h,m,s=t.replace(',','.').split(':');return int(h)*3600+int(m)*60+float(s)
    result=[]
    for block in srt.read_text().strip().split('\n\n'):
        lines=block.splitlines();a,b=map(seconds,lines[1].split(' --> '))
        result.append({'id':int(lines[0]),'start':a,'end':b,'text':'\n'.join(lines[2:])})
    return result

def render(source,root):
    assert root!=source and not root.exists(), 'Use a new folder; never overwrite masters.'
    for folder in ['deliverables','records','review','_work']:(root/folder).mkdir(parents=True)
    binary=imageio_ffmpeg.get_ffmpeg_exe();inputs=[]
    for lang in ['ja','en']:
        src=source/f'deliverables/EP001_Anubis_{lang}_{VERSION}_1080p30.mp4'
        srt=source/f'deliverables/EP001_Anubis_{lang}_{VERSION}_1080p30.srt'
        inputs.append({'language':lang,'video_sha256':sha(src),'srt_sha256':sha(srt)})
        shutil.copy2(srt,root/f'_work/{lang}.srt')
        out=root/f'deliverables/{stem(lang)}.mp4'
        vf=f"subtitles='{root}/_work/{lang}.srt':original_size=1920x1080:force_style='{STYLE}'"
        cmd=[binary,'-nostdin','-y','-v','warning','-i',str(src),'-map','0:v:0','-map','0:a:0','-vf',vf,
             '-c:v','libx264','-preset','veryfast','-crf','18','-threads','4','-pix_fmt','yuv420p',
             '-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy',
             '-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709',
             '-metadata','title=Quiet Origins / EP001 — subtitle review ('+lang+')',
             '-metadata','comment=Burned subtitles for review. Japanese narration: VOICEVOX:冥鳴ひまり; English: Kokoro / Heart (af_heart). Audio unchanged from '+VERSION+'.',
             '-movflags','+faststart','-progress',str(root/f'_work/progress_{lang}.txt'),str(out)]
        print('RENDER',lang,flush=True);run(cmd);print('RENDERED',lang,flush=True)
    shutil.copy2(source/'deliverables/VOICE_CREDITS.txt',root/'deliverables/VOICE_CREDITS.txt')
    save(root/'records/render_request.json',{'source_root':str(source),'version':VERSION,'subtitles_burned_in':True,'purpose':f'owner review only; original {VERSION} unchanged','style':STYLE,'renderer':binary,'inputs':inputs})

def selected_bottom_frames(path,frames):
    terms=[f'eq(n\\,{n})' for n in frames]
    # Keep the expression parser depth bounded for hundreds of cue/gap samples.
    expression='+'.join('('+'+'.join(terms[i:i+20])+')' for i in range(0,len(terms),20))
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf',f'select={expression},crop=1920:180:0:900,scale=640:60',
       '-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'])
    return np.frombuffer(data,dtype=np.uint8).reshape(len(frames),60,640,3)

def verify(source,root):
    results=[];all_cues=[];request=read(root/'records/render_request.json')
    duration=float(read(source/'records/master_timeline.json')['duration_seconds']);expected_frames=round(duration*30)
    for lang in ['ja','en']:
        out=root/f'deliverables/{stem(lang)}.mp4';src=source/f'deliverables/EP001_Anubis_{lang}_{VERSION}_1080p30.mp4'
        srt=source/f'deliverables/EP001_Anubis_{lang}_{VERSION}_1080p30.srt'
        original=next(x for x in request['inputs'] if x['language']==lang)
        assert sha(src)==original['video_sha256'] and sha(srt)==original['srt_sha256']
        run(['ffmpeg','-v','error','-i',str(out),'-f','null','-']);p=probe(out)
        assert [x['codec_type'] for x in p['streams']]==['video','audio']
        v=p['streams'][0];assert v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='30/1'
        assert int(v['nb_frames'])==expected_frames and float(p['format']['duration'])==duration
        pts=sorted(map(int,subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts','-of','csv=p=0',str(out)],text=True).splitlines()))
        assert pts==list(range(0,expected_frames*512,512))
        ah=stream_hash(out);assert ah==stream_hash(src)
        cs=cues(srt);assert len(cs)==(150 if lang=='en' else 136)
        samples=[{'cue':x['id'],'frame':round((x['start']+x['end'])*15),'expected_subtitle':True} for x in cs]
        # Check silence gaps as well, to catch subtitles unintentionally held on screen.
        bounds=[(0,cs[0]['start'])]+[(a['end'],b['start']) for a,b in zip(cs,cs[1:])]+[(cs[-1]['end'],duration)]
        samples += [{'cue':None,'frame':round((a+b)*15),'expected_subtitle':False} for a,b in bounds if b-a>=.3]
        samples.sort(key=lambda x:x['frame']);frames=[x['frame'] for x in samples]
        a=selected_bottom_frames(src,frames);b=selected_bottom_frames(out,frames)
        for i,x in enumerate(samples):
            mask=(b[i].mean(axis=2)-a[i].mean(axis=2)>35)&(b[i].mean(axis=2)>140)
            count=int(mask.sum());x['new_bright_subtitle_pixels']=count
            if x['expected_subtitle']:assert count>80,(lang,x)
            else:assert count<80,(lang,x)
        all_cues.append({'language':lang,'subtitle_cues':len(cs),'samples':samples,'all_passed':True})
        results.append({'language':lang,'name':out.name,'bytes':out.stat().st_size,'sha256':sha(out),'probe':p,'audio_stream_hash':ah,'audio_identical_to_source':True,'full_decode':'pass','exact_30fps_pts':True,'subtitle_cues_checked':len(cs)})
        print('VERIFIED',lang,len(cs),'subtitle cues and',len(samples)-len(cs),'gaps',flush=True)
    save(root/'records/qc.json',{'duration_seconds':duration,'frames':expected_frames,'fps':30,'subtitles_burned_in':True,'human_full_listening':False,'files':results})
    save(root/'records/subtitle_presence_checks.json',all_cues)
    # Actual burned-video samples including all four large-subtitle edge cases.
    times={'ja':[10,52.2,204.7,310.3,439,670.0],'en':[10,52.2,204.7,310.3,439,669.3]}
    if VERSION=='v09':times={lang:[t+4 if t>=29.067 else t for t in values] for lang,values in times.items()}
    sheet=Image.new('RGB',(1280,2340),'#15242c')
    for col,lang in enumerate(['en','ja']):
        for row,t in enumerate(times[lang]):
            path=root/f'review/{lang}_{t:06.1f}.jpg'
            run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(root/f'deliverables/{stem(lang)}.mp4'),'-frames:v','1','-vf','scale=1280:720','-q:v','3',str(path)])
            im=Image.open(path);im.thumbnail((640,360));sheet.paste(im,(col*640,row*390+30))
            ImageDraw.Draw(sheet).text((col*640+8,row*390+8),f'{lang} / {t:.1f}s / burned subtitles',fill='white')
    sheet.save(root/'review/subtitled_review_contact.jpg',quality=88)

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['render','verify']);args=p.parse_args()
    source=Path(os.environ['WOM_EPISODE_ROOT']);root=Path(os.environ['WOM_REVIEW_ROOT'])
    if args.stage=='render':render(source,root)
    else:verify(source,root)
if __name__=='__main__':main()
