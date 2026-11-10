"""Unchanged SRT/audio over v02 pictures, only after explicit review-encode consent."""
import os,sys,subprocess,shutil,json
from pathlib import Path
from wom14_v02 import ROOT,BASE,read,save,sha,probe,path_video
from wom14_v02_assemble import streamhash
import imageio_ffmpeg

def run(lang):
 assert read(ROOT/'records/user_clarifications.json').get('subtitled_review_recompression_approved') is True,'Await user answer about subtitled review pixel differences'
 src=path_video(ROOT,lang);dst=path_video(ROOT,lang,review=True);srt=ROOT/lang/'_work/subtitles_v02.srt';shutil.copy2(ROOT/lang/f'deliverables/EP014_Oni_{lang}_v02_1080p30.srt',srt)
 vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontName=Hiragino Sans,FontSize=14,BorderStyle=3,MarginV=10'"
 subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(src),'-vf',vf,'-filter_threads','1','-c:v','libx264','-threads','2','-preset','veryfast','-crf','18','-profile:v','high','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-c:a','copy','-movie_timescale','48000','-movflags','+faststart','-progress',str(ROOT/lang/'_work/subtitles_v02_progress.txt'),str(dst)],check=True)
 p=subprocess.run(['ffmpeg','-nostdin','-v','warning','-xerror','-threads','2','-i',str(dst),'-f','null','-'],capture_output=True,text=True);assert p.returncode==0 and not p.stderr.strip(),p.stderr
 a=streamhash(src,'a');assert a==streamhash(dst,'a')==streamhash(path_video(BASE,lang),'a');assert sha(srt)==sha(BASE/lang/f'deliverables/EP014_Oni_{lang}_v01_1080p30.srt')
 info=probe(dst);v=next(x for x in info['streams'] if x['codec_type']=='video');n=round(read(ROOT/lang/'records/master_timeline.json')['duration_seconds']*30);assert (v['width'],v['height'],v['profile'],v['pix_fmt'],v['avg_frame_rate'],int(v['nb_frames']))==(1920,1080,'High','yuv420p','30/1',n)
 pts=sorted(int(x) for x in subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_entries','packet=pts','-of','csv=p=0',str(dst)],text=True).splitlines());assert pts==list(range(0,n*512,512))
 save(ROOT/lang/'records/subtitled_v02.json',dict(passed=True,sha256=sha(dst),frames=n,audio_stream_identical_to_v01=True,audio_stream_sha256=a,srt_byte_identical_to_v01=True,srt_sha256=sha(srt),timing_unchanged=True,decode_warnings=0,profile=v['profile'],pix_fmt=v['pix_fmt'],exact_30fps_pts=True,pixel_identity_exception='User authorized subtitle-review re-encoding; normal English/Japanese and English4K preserve every unchanged decoded frame.'))
 shots=read(BASE/lang/'records/render_shots.json')
 for k in ['O02-A','O02-B','O03-23','O06-38','O08-31','R10-27','R11-30','R12-1447']:
  s=next(s for s in shots if s['key']==k);t=s['end']-.5;p=ROOT/lang/f'review/subtitle_sample_{lang}_{k}.jpg';subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-threads','1','-ss',str(t),'-i',str(dst),'-frames:v','1','-vf','scale=1280:720','-filter_threads','1','-q:v','2',str(p)],check=True)
 print('SUBTITLED VERIFIED',lang,flush=True)
if __name__=='__main__':run(sys.argv[1])
