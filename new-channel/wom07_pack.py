"""Prepare ASCII-named review archives without deleting any originals."""
from pathlib import Path
import zipfile,json
from wom07_produce import ROOT,read,save,sha

def archive(name,files,base):
 out=ROOT/'deliverables'/name
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted(set(files)):
   if p.is_file():z.write(p,p.relative_to(base))
 with zipfile.ZipFile(out) as z:assert z.testzip() is None
 return {'name':name,'path':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'entries':len(files)}
def main():
 assert read(ROOT/'records/qc_v01.json')['passed']
 assert read(ROOT/'records/continuous_qc.json')['passed']
 assert read(ROOT/'records/final_video_motion.json')['passed']
 assert read(ROOT/'records/episode_specific_qc.json')['passed']
 d=ROOT/'deliverables';r=[]
 r.append(archive('EP007_audio_and_subtitles.zip',[*d.glob('*.wav'),*d.glob('*.m4a'),*d.glob('*.srt'),*d.glob('*pronunciation*.txt')],d))
 r.append(archive('EP007_thumbnails_and_metadata.zip',[*d.glob('*.jpg'),*d.glob('*.md'),*d.glob('*.csv')],d))
 r.append(archive('EP007_QA_records.zip',[*ROOT.glob('records/*.json'),*ROOT.glob('records/*.log'),*ROOT.glob('review/*.jpg')],ROOT))
 media=ROOT.parent/'素材';video_files=[media/'V01_Kling_v02.mp4',media/'V02_Kling_v01.mp4',media/'V03_Kling_v01.mp4',media/'V04_Kling_v01.mp4',media/'V01_rejected_Kling_v01.mp4']
 r.append(archive('EP007_AI_scene_review.zip',video_files,media))
 save(ROOT/'records/release_archives.json',r)
 print('ARCHIVES',[(x['name'],x['bytes']) for x in r],flush=True)
if __name__=='__main__':main()
