"""Prepare ASCII-named review archives without deleting any originals."""
from pathlib import Path
import zipfile,json
from wom10_produce import ROOT,read,save,sha

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
 for q in read(ROOT/'records/qc_v01.json')['files']:assert sha(ROOT/'deliverables'/q['name'])==q['sha256']
 assert sha(ROOT/'deliverables/EP010_Krampus_en_v01_1080p30.mp4')==read(ROOT/'records/final_video_motion.json')['video_sha256']
 for q in read(ROOT/'records/continuous_qc.json')['checks']:assert sha(ROOT/f"deliverables/EP010_Krampus_{q['language']}_v01_1080p30.mp4")==q['video_sha256']
 d=ROOT/'deliverables';r=[]
 r.append(archive('EP010_audio_and_subtitles.zip',[*d.glob('*.wav'),*d.glob('*.m4a'),*d.glob('*.srt'),*d.glob('*pronunciation*.txt')],d))
 r.append(archive('EP010_thumbnails_and_metadata.zip',[*d.glob('*.jpg'),*d.glob('*.md'),*d.glob('*.csv')],d))
 r.append(archive('EP010_QA_records.zip',[*ROOT.glob('records/*.json'),*ROOT.glob('records/*.log'),*ROOT.glob('records/*.txt'),*ROOT.glob('review/*.jpg')],ROOT))
 save(ROOT/'records/release_archives.json',r)
 print('ARCHIVES',[(x['name'],x['bytes']) for x in r],flush=True)
if __name__=='__main__':main()
