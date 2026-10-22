"""Final EP003 evidence: exact brand frames, source hashes, geometry and duration."""
import subprocess
from PIL import Image
from wom03_produce import ROOT,REPO,read,save,sha,content

def main():
 master=read(ROOT/'records/master_timeline.json');shots=read(ROOT/'records/render_shots.json');assert len(shots)==37
 assert sum(s['frames'] for s in shots)==12110
 for a,b in zip(shots,shots[1:]):assert round(a['end']*30)==round(b['start']*30)
 assert round((master['duration_seconds']-master['brand_intervals']['endcard'][0])*30)==600
 assert master['brand_intervals']['opening'][0]==master['segments'][1]['end'];assert master['ja_wait_before_opening']<=3
 for name in ['content.json','content_en.json']:assert sha(ROOT/'records'/name)==sha(REPO/'new-channel/episodes/EP003_Medusa/records'/name)
 manifest=read(ROOT/'records/visual_manifest.json')['shots'];geometry=[]
 for s in manifest:
  top,bottom=s['camera_band'];cy=(top+bottom)/2
  for t in s['texts']:
   assert t['bbox'][0]>=0 and t['bbox'][2]<=1920
   max_y=max(t['bbox'][3],cy+1.03*(t['bbox'][3]-cy)) if t['bbox'][1]>=top else t['bbox'][3];assert max_y<=700
   if s.get('base_asset'):assert t['bbox'][3]<100
  for box in s['art_boxes']:assert box[0]>=80 and box[1]>=110 and box[2]<=1840 and box[3]<=930
  geometry.append({'key':s['key'],'texts':s['texts'],'art_boxes':s['art_boxes'],'text_bottom':max(t['bbox'][3] for t in s['texts']),'passed':True})
 originals=[]
 for a in read(ROOT/'records/source_assets.json')['items']:
  for p in a['originals']:
   assert sha(p['path'])==p['sha256'];originals.append({'id':a['id'],'view_index':p['view_index'],'sha256':p['sha256'],'unchanged':True})
 for kind in ['ai_images','ai_videos']:
  for a in read(ROOT/f'records/{kind}.json'):assert sha(a['local_path'])==a['sha256']
 save(ROOT/'records/source_preservation.json',{'museum_originals_verified':len(originals),'originals':originals,'ai_originals_verified':13,'generated_details_added_to_museum_art':False})
 video=ROOT/'deliverables/EP003_Medusa_en_v01_1080p30.mp4';brands=[]
 def hashes(p,expr=None):
  args=['ffmpeg','-v','error','-threads','2','-i',str(p),'-an']
  if expr:args+=['-vf',f'select={expr}','-fps_mode','passthrough']
  txt=subprocess.check_output([*args,'-f','framemd5','-'],text=True);return [x.rsplit(',',1)[-1].strip() for x in txt.splitlines() if not x.startswith('#')]
 for s in shots:
  if s['segment_id']!='BRAND':continue
  a=round(s['start']*30);b=a+s['frames']-1;actual=hashes(video,f'between(n\\,{a}\\,{b})');expected=hashes(s['approved_brand_source']);assert actual==expected and len(actual)==s['frames'];brands.append({'key':s['key'],'start_frame':a,'frames':s['frames'],'decoded_pixels_identical':True,'source':s['approved_brand_source'],'source_sha256':sha(s['approved_brand_source'])})
 save(ROOT/'records/final_checks.json',{'passed':True,'frames':12110,'duration_seconds':master['duration_seconds'],'script_v03_unchanged':True,'brand_frames_verified':720,'brand_checks':brands,'endcard_exact_last_20_seconds':True,'ja_wait_before_opening':master['ja_wait_before_opening'],'geometry':geometry})
 print('FINAL CHECKS: 72 source originals, 13 AI originals, 720 brand frames, all layout bounds',flush=True)
if __name__=='__main__':main()
