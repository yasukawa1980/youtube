"""Render all subtitle pages on a diagnostic solid field at native resolution; derive exact ink/box bounds."""
from wom12_produce import *
import imageio_ffmpeg,numpy as np
from PIL import Image
from wom01_subtitles import to_srt
STYLE='FontSize=14,BorderStyle=3,MarginV=49'
def main():
 rows=[]
 for l in ['en','ja']:
  q=read(ROOT/f'records/subtitle_cues_{l}.json')['cues'];srt=ROOT/f'_work/sub_bounds_{l}.srt';test=[dict(text=c['text'],start=i,end=i+.99) for i,c in enumerate(q)];srt.write_text(to_srt(test));vf=f"subtitles='{srt}':original_size=1920x1080:force_style='{STYLE}'";p=subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-f','lavfi','-i',f'color=c=0x00fa50:s=1920x1080:r=1:d={len(q)}','-vf',vf,'-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE)
  for i,c in enumerate(q):
   b=p.stdout.read(1920*1080*3);a=np.frombuffer(b,np.uint8).reshape(1080,1920,3);mask=(np.abs(a.astype(np.int16)-a[0,0].astype(np.int16)).max(axis=2)>16);y,x=np.where(mask);assert len(y)>0;rows.append(dict(lang=l,cue=i+1,start=c['start'],end=c['end'],bbox=[int(x.min()),int(y.min()),int(x.max()+1),int(y.max()+1)],lower_gap_to_rail=915-int(y.max()+1)))
  assert p.wait()==0
 edge=min(r['lower_gap_to_rail'] for r in rows);top=min(r['bbox'][1] for r in rows);print('subtitle rects:',len(rows),'top',top,'rail gap',edge);assert edge>0 and top>748;save(ROOT/'records/subtitle_layout_validation.json',dict(passed=True,style=STYLE,all_pages=len(rows),rail_top=915,min_gap=edge,minimum_top=top,measurement='Same libass binary and style as review. Each exact SRT page rendered at 1920x1080 on solid green diagnostic canvas; bounding box includes backing.',rows=rows))
if __name__=='__main__':main()
