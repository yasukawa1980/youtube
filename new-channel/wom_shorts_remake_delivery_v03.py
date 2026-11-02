import math,zipfile
from PIL import Image,ImageDraw
from wom_shorts_remake_v03 import ROOT,OLD,read,save,sha
from wom_shorts_remake_qc_v03 import decode

def main():
 caps=read(ROOT/'records/caption_manifest.json');checks=[]
 for s in read(ROOT/'records/shorts.json')['shorts']:
  sid=s['id'];cs=[c for c in caps if c['short_id']==sid];ns=sorted(set((c['start_frame']+c['end_frame'])//2 for c in cs));frames=decode(ROOT/f'deliverables/QO_short_remake_{sid}_v03.mp4',ns);sheet=Image.new('RGB',(960,math.ceil(len(cs)/4)*450),'#eee');d=ImageDraw.Draw(sheet)
  for i,c in enumerate(cs):
   im=Image.fromarray(frames[(c['start_frame']+c['end_frame'])//2]);im.thumbnail((240,427));x=i%4*240;y=i//4*450;sheet.paste(im,(x,y+23));d.text((x+5,y+4),f'{sid} page {i+1} / H 39px',fill='black')
   for r in c['rows']:assert r['cap_height']==39 and r['font_size']==55 and not r['resampling']
  sheet.thumbnail((1280,1280));sheet.save(ROOT/f'review/{sid}_all_captions_v03.jpg',quality=92)
 for p in (OLD/'assets').glob('*'):
  if '_caption' not in p.name:assert sha(p)==sha(ROOT/'assets'/p.name),p
 for n in ['shorts.json','visual_manifest.json']:
  old=(OLD/'records'/n).read_text();new=(ROOT/'records'/n).read_text().replace(str(ROOT),str(OLD));assert old==new,n
 save(ROOT/'records/v03_unchanged.json',dict(passed=True,all_nonsubtitle_assets_identical=True,timing_and_camera_identical=True,audio_streams_identical=True,cap_height=39,font_size=55))
 with zipfile.ZipFile(ROOT/'deliverables/remakes_review_v03.zip','w',zipfile.ZIP_DEFLATED) as z:
  for p in sorted([*ROOT.glob('review/*v03.jpg'),*ROOT.glob('records/*.json')]):
   if p.name!='github_draft_release.json':z.write(p,p.relative_to(ROOT))
 print('REVIEW READY',flush=True)
if __name__=='__main__':main()
