"""Validate and share only completed preproduction work. Does not render or publish video."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,zipfile
import numpy as np
from PIL import ImageColor
from pnt02_produce import ROOT,REPO,read,save,sha
import pnt02_scenes as scenes

OUT=REPO/'painting/pnt02_確認版_v01_20261110'

def main():
 assert Path('/Volumes/ESD-02').is_mount()
 report={'status':'preproduction_only','video_completed':False,'auditory_review_completed':False,'languages':{}}
 for lang in ['en','ja']:
  r=ROOT/lang;dest=OUT/lang;dest.mkdir(exist_ok=True)
  names=['master_timeline.json','subtitle_validation.json','audio_qc.json','voice_gaps.json',f'subtitle_cues_{lang}.json']
  for name in names:shutil.copy2(r/'records'/name,dest/name)
  for p in (r/'deliverables').glob('*.srt'):shutil.copy2(p,dest/p.name)
  audio=r/f'deliverables/PNT02_audio_{lang}.m4a'
  result=subprocess.run(['ffmpeg','-nostdin','-hide_banner','-i',str(audio),'-af','silencedetect=noise=-60dB:d=1','-f','null','-'],capture_output=True,text=True,check=True)
  silence=[float(x) for x in re.findall(r'silence_duration: ([\d.]+)',result.stderr)]
  assert not silence,(lang,silence)
  levels=read(r/'records/audio_qc.json')['languages'][lang]['levels']
  assert abs(float(levels['input_i'])+16)<.3 and float(levels['input_tp'])<=-1
  m=read(r/'records/master_timeline.json');subs=read(r/'records/subtitle_validation.json')
  report['languages'][lang]=dict(duration_seconds=m['duration_seconds'],frames_at_30fps=round(m['duration_seconds']*30),levels=levels,subtitles=subs,opening=m['brand_intervals']['opening'],endcard=m['brand_intervals']['endcard'],silence_over_1s_at_minus60dB=silence,files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted((r/'deliverables').iterdir())])
 for name in ['request.json','first_pass_preserved.json','narration_segments_en.json','narration_segments_ja.json']:
  shutil.copy2(ROOT/'records'/name,OUT/name)
 request=(REPO/'painting/pnt02_制作依頼_20261110.md').read_text()
 quotes=[scenes.LETTER_HEAD,*[p for row in scenes.LETTER for p in row],*scenes.RESOLUTION,*scenes.WHITTREDGE]
 assert all(p in request for p in quotes)
 rows=read(OUT/'card_design_metrics.json')
 def lum(col):
  x=np.array(ImageColor.getrgb(col))/255;x=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4);return float(x@np.array([.2126,.7152,.0722]))
 checks=[]
 for r in rows:
  bg='#412f25' if r['box'][1]>=915 else '#f8f1dc' if 'plate_padding' in r else '#e9ddc4'
  a,b=lum(r['foreground']),lum(bg);ratio=(max(a,b)+.05)/(min(a,b)+.05)
  assert ratio>=4.5,(r,ratio)
  if r['major']:assert r['ink_height']>=60
  if 'plate_padding' in r:assert r['plate_padding']>=35,r
  checks.append(dict(r,contrast=ratio,actual_background=bg))
 report['card_design']=dict(exact_quote_strings=True,contrast_min=min(r['contrast'] for r in checks),major_ink_min=min(r['ink_height'] for r in rows if r['major']),label_ink_min=min(r['ink_height'] for r in rows),body_ink_min=min(r['ink_height'] for r in rows if 'plate_padding' in r),padding_min=min(r['plate_padding'] for r in rows if 'plate_padding' in r),note='Static design samples only; rail years are placeholders, not final episode frames. Subtitle/rail rendered overlap not yet checked.')
 report['pending']=['proper-name audio reference/listening and corrections if needed','shot layout and per-frame camera render','English/Japanese 1080p and English 4K MP4, subtitled review MP4','continuous decode and first/middle/last shot sheets','motion smoothness measurement','subtitle versus chronology-rail rendered clearance','final upload descriptions and chapters','full v01 media delivery']
 save(OUT/'preproduction_qc.json',report)
 save(OUT/'card_design_qc.json',checks)
 archive=ROOT/'deliverables';archive.mkdir(exist_ok=True)
 audiozip=archive/'PNT02_audio_subtitles_preliminary_v01.zip'
 with zipfile.ZipFile(audiozip,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for lang in ['en','ja']:
   for p in sorted((ROOT/lang/'deliverables').iterdir()):z.write(p,f'{lang}/{p.name}')
  z.writestr('README.txt','PRELIMINARY AUDIO ONLY. No finished video. Unmodified first-pass narration; pronunciations not auditioned. Both languages have independent timelines. See repository painting/pnt02_確認版_v01_20261110/README.md.\n')
 designzip=archive/'PNT02_design_records_preliminary_v01.zip'
 with zipfile.ZipFile(designzip,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
  for folder in [OUT,REPO/'painting/サムネ確認用/pnt02']:
   for p in sorted(folder.rglob('*')):
    if p.is_file() and p.name!='sharing.json':z.write(p,str(p.relative_to(REPO/'painting')))
 print(json.dumps({'audio':report['languages'],'cards':report['card_design'],'archives':[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)) for p in [audiozip,designzip]]},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
