"""Subtitle review revision with identical non-P05 encoded packets, too."""
import subprocess,shutil,re
import imageio_ffmpeg
from wom07_revision_v02 import ROOT,OLD,A,B,splice_file,ff,stream_hash

def main():
 for lang in ['en','ja']:
  src=ROOT/'_work/P05_G11-01.mp4';rep=ROOT/f'_work/P05_{lang}_subtitled.mp4';srt=ROOT/f'_work/{lang}_global.srt'
  original=OLD/f'deliverables/EP007_Thanksgiving_{lang}_v01_1080p30.srt'
  def ms(t):
   h,m,rest=t.split(':');sec,milli=rest.split(',');return int(h)*3600000+int(m)*60000+int(sec)*1000+int(milli)
  def stamp(t):
   h,t=divmod(t,3600000);m,t=divmod(t,60000);sec,milli=divmod(t,1000);return f'{h:02d}:{m:02d}:{sec:02d},{milli:03d}'
  blocks=[]
  for block in original.read_text().strip().split('\n\n'):
   lines=block.splitlines();a,b=[ms(x.strip()) for x in lines[1].split('-->')];a-=102600;b-=102600
   if b<=0 or a>=(B-A)*1000/30:continue
   blocks.append(str(len(blocks)+1)+'\n'+stamp(max(0,a))+' --> '+stamp(b)+'\n'+'\n'.join(lines[2:]))
  srt.write_text('\n\n'.join(blocks)+'\n')
  vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize=14,BorderStyle=3,MarginV=12'"
  subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-nostdin','-y','-v','error','-i',str(src),'-vf',vf,'-c:v','libx264','-threads','4','-preset','veryfast','-crf','18','-pix_fmt','yuv420p','-fps_mode','passthrough','-video_track_timescale','15360','-an','-movie_timescale','48000','-movflags','+faststart',str(rep)],check=True)
  old=OLD/f'deliverables/EP007_Thanksgiving_{lang}_v01_subtitled_review_1080p30.mp4';picture=ROOT/f'_work/review_{lang}_picture_master.mp4';dst=ROOT/f'deliverables/EP007_Thanksgiving_{lang}_v02_subtitled_review_1080p30.mp4'
  splice_file(old,rep,picture,'review_'+lang)
  ff(['-i',picture,'-i',old,'-map','0:v:0','-map','1:a:0','-map_metadata',1,'-metadata','comment=EP007 v02 subtitle review; P05 map facsimile; all other picture packets retained.','-c','copy','-movie_timescale',48000,'-movflags','+faststart',dst]);assert stream_hash(dst,'a')==stream_hash(old,'a')
  print('SUBTITLED V02',lang,flush=True)
if __name__=='__main__':main()
