"""Pixel-check every subtitle at both requested sizes and extract every rendered shot."""
import os
os.environ.setdefault('WOM08_ROOT', '/Users/ryo/Desktop/新チャンネル/EP008_Tutankhamun/確認版_v02_20261030')
import argparse,math,re,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import imageio_ffmpeg
from wom08_produce import ROOT,REPO,read,save,sha,ff,content,SR
from wom01_subtitles import to_srt
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'

def layout():
 binary=imageio_ffmpeg.get_ffmpeg_exe();manifest=read(ROOT/'records/visual_manifest.json')['shots'];m=read(ROOT/'records/master_timeline.json')
 # Only text must clear subtitles; artwork may extend down to y930.
 maxbottom=max(max(t['bbox'][3],(sum(s['camera_band'])/2)+1.03*(t['bbox'][3]-sum(s['camera_band'])/2)) if t['bbox'][1]>=s['camera_band'][0] else t['bbox'][3] for s in manifest for t in s['texts'])
 assert maxbottom<=700
 checks=[]
 from wom01_subtitled_review import cues as parse_srt
 srt_checks={}
 for lang in ['en','ja']:
  cues=read(ROOT/f'records/subtitle_cues_{lang}.json')['cues']
  actual=parse_srt(ROOT/f'deliverables/EP008_Tutankhamun_{lang}_v02_1080p30.srt')
  normalize=lambda s:re.sub(r'\s+','',s)
  assert normalize(''.join(x['text'] for x in actual))==normalize(''.join(s['text'] for s in content(lang)['segments']))
  assert len(actual)==len(cues) and min(x['end']-x['start'] for x in actual)>=1.3999
  assert all(a['end']<=b['start'] for a,b in zip(actual,actual[1:]))
  srt_checks[lang]={'count':len(actual),'minimum_seconds':min(x['end']-x['start'] for x in actual),'matches_script':True,'max_lines':max(len(x['text'].splitlines()) for x in actual),'max_line_chars':max(len(y) for x in actual for y in x['text'].splitlines())}
  test=[{**c,'start':i+.1,'end':i+.9} for i,c in enumerate(cues)];srt=ROOT/f'_work/layout_{lang}.srt';srt.write_text(to_srt(test))
  for size in [14,26]:
   folder=ROOT/f'_work/layout_{lang}_{size}';folder.mkdir(exist_ok=True)
   vf=f"subtitles='{srt}':original_size=1920x1080:force_style='FontSize={size},BorderStyle=3,MarginV=12',select='mod(n,2)'"
   subprocess.run([binary,'-nostdin','-y','-v','error','-f','lavfi','-i',f'color=c=black:s=1920x1080:r=2:d={len(cues)}','-vf',vf,'-frames:v',str(len(cues)),'-fps_mode','passthrough',str(folder/'%04d.png')],check=True)
   boxes=[]
   for i,c in enumerate(cues,1):
    im=np.array(Image.open(folder/f'{i:04}.png').convert('RGB'));ys,xs=np.where(im.max(axis=2)>100);assert len(xs)>0,(lang,size,i)
    box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)];assert box[1]>700,(lang,size,i,box,c['text'])
    boxes.append({'cue':i,'sentence_id':c['sentence_id'],'bbox':box,'start':c['start'],'end':c['end']})
   checks.append({'language':lang,'font_size':size,'cue_count':len(cues),'minimum_subtitle_top':min(b['bbox'][1] for b in boxes),'max_content_bottom_with_zoom':maxbottom,'all_nonoverlapping':True,'boxes':boxes})
   print('LAYOUT',lang,size,len(cues),min(b['bbox'][1] for b in boxes),flush=True)
 save(ROOT/'records/subtitle_layout_validation.json',{'passed':True,'method':'All exact cue texts rasterized by libass at 1920x1080 on black; glyph bboxes compared with recorded composition bounds plus maximum zoom','checks':checks,'actual_srt_checks':srt_checks})
 # Recorded synthesis boundaries: check actual waveform contains pauses between sentences.
 import soundfile as sf
 boundary=[]
 for l in ['en','ja']:
  tl=read(ROOT/f'records/narration_timeline_{l}.json');a,sr=sf.read(ROOT.parent/'確認版_v01_20261029'/f'audio/{l}/narration.wav',dtype='float32')
  for s in tl['segments']:
   for c,nxt in zip(s['cues'],s['cues'][1:]):
    x=a[round(c['end']*sr):round(nxt['start']*sr)];assert len(x)>0 and float(np.max(abs(x)))==0
    boundary.append({'language':l,'after_sentence':c['id'],'start':c['end'],'end':nxt['start'],'gap_seconds':len(x)/sr,'digital_silence':True})
 save(ROOT/'records/sentence_boundary_validation.json',{'passed':True,'checks':boundary,'within_sentence_page_timing':'Proportional, not forced word alignment; sentence boundaries are sample measured.'})

if __name__=="__main__":layout()
