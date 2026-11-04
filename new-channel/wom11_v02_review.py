"""Focused revision comparisons plus actual burned-subtitle review frames."""
import sys,subprocess
from PIL import Image,ImageDraw,ImageFont
from wom11_v02 import ROOT,V01,read,save,sha
SAMPLES=[('P06_heading',140),('P06_five_lines',159),('P10_Thoth',278),('P10_Ammit',282),('P12_summary',325)]
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
def frame(src,t,dst):
 subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=1280:720','-update','1',str(dst)],check=True)
def main():
 mode=sys.argv[1];rows=[]
 if mode=='normal':
  for key,t in SAMPLES:
   pair=[]
   for version,root in [('v01',V01),('v02',ROOT)]:
    src=root/f'deliverables/EP011_WeighingOfTheHeart_en_{version}_1080p30.mp4';dst=ROOT/f'review/{key}_{version}.jpg';frame(src,t,dst);pair.append(dst)
    rows.append({'key':key,'time_seconds':t,'version':version,'source_sha256':sha(src),'image':str(dst.relative_to(ROOT))})
   sheet=Image.new('RGB',(1280,390),'#0c1820');d=ImageDraw.Draw(sheet)
   for i,p in enumerate(pair):
    sheet.paste(Image.open(p).resize((640,360)),(i*640,30));d.text((i*640+10,5),f'{key} / {t}s / '+['v01','v02'][i],font=ImageFont.truetype(FONT,18),fill='white')
   sheet.save(ROOT/f'review/comparison_{key}.jpg',quality=90,optimize=True)
 else:
  assert mode=='subtitles'
  for lang in ['en','ja']:
   src=ROOT/f'deliverables/EP011_WeighingOfTheHeart_{lang}_v02_subtitled_review_1080p30.mp4'
   for key,t in SAMPLES:
    dst=ROOT/f'review/subtitled_{lang}_{key}.jpg';frame(src,t,dst);rows.append({'key':key,'time_seconds':t,'language':lang,'source_sha256':sha(src),'image':str(dst.relative_to(ROOT))})
 save(ROOT/f'records/review_samples_{mode}.json',{'method':'Focused time samples in addition to the separate full-stream first/middle/last audit','samples':rows});print('REVIEW SAMPLES',mode,len(rows),flush=True)
if __name__=='__main__':main()
