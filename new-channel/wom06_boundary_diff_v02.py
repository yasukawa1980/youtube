"""Quantify boundary compression changes; v01 only serves as read-only reference."""
import subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from wom06_revision_v02 import ROOT,OLD
from wom06_produce import read,save,sha

def main():
 r=read(ROOT/'records/pixel_comparison.json');intervals=r['outside_nonidentical_intervals_half_open'];indices=[i for a,b in intervals for i in range(a,b)]
 expr='+'.join(f'between(n\\,{a}\\,{b-1})' for a,b in intervals)
 files=[]
 for version,root in [('v01',OLD),('v02',ROOT)]:
  dst=ROOT/f'_work/{version}_boundary.yuv';src=root/f'deliverables/EP006_Sphinx_en_{version}_1080p30.mp4'
  subprocess.run(['ffmpeg','-nostdin','-y','-v','warning','-threads','2','-i',str(src),'-vf','select='+expr,'-fps_mode','passthrough','-an','-pix_fmt','yuv420p','-f','rawvideo',str(dst)],capture_output=True,check=True);files.append(dst)
 n=1920*1080*3//2;a=np.memmap(files[0],dtype=np.uint8,mode='r',shape=(len(indices),n));b=np.memmap(files[1],dtype=np.uint8,mode='r',shape=(len(indices),n));stats=[]
 for j,i in enumerate(indices):
  diff=np.abs(a[j].astype(np.int16)-b[j].astype(np.int16));y=diff[:1920*1080]
  stats.append({'frame':i,'mae_all_yuv_samples':float(diff.mean()),'mae_luma':float(y.mean()),'max_absolute_sample_difference':int(diff.max()),'different_sample_ratio':float(np.count_nonzero(diff)/n)})
 worst=max(stats,key=lambda s:s['mae_all_yuv_samples']);j=indices.index(worst['frame'])
 sheet=Image.new('RGB',(1280,770),'#0c1820');d=ImageDraw.Draw(sheet);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',17)
 for k,(data,label) in enumerate([(a[j],'v01 luma'),(b[j],'v02 luma'),(np.clip(np.abs(a[j].astype(np.int16)-b[j].astype(np.int16))*16,0,255).astype(np.uint8),'absolute difference x16')]):
  im=Image.fromarray(data[:1920*1080].reshape(1080,1920)).convert('RGB').resize((640,360));x=(k%2)*640;y0=(k//2)*390;sheet.paste(im,(x,y0));d.text((x+8,y0+363),label+' | frame '+str(worst['frame']),font=font,fill='white')
 sheet.save(ROOT/'review/boundary_compression_difference.jpg',quality=93,optimize=True)
 save(ROOT/'records/boundary_difference.json',{'same_original_intermediates':True,'reason_inferred':'Encoder lookahead/MB-tree changes quantization before an altered scene; all differences are confined to three pre-cut intervals.','frames':len(indices),'worst_frame':worst,'mean_luma_mae_over_112_frames':float(np.mean([s['mae_luma'] for s in stats])),'maximum_absolute_sample_difference':max(s['max_absolute_sample_difference'] for s in stats),'measurements':stats})
 print('BOUNDARY DIFFERENCE',worst,flush=True)
if __name__=='__main__':main()
