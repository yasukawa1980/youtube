import os
os.environ.setdefault('WOM10_ROOT','/Volumes/ESD-02/新チャンネル/EP010_Krampus/確認版_v02_20261103')
from pathlib import Path
import zipfile
from wom10_produce import ROOT,read,save,sha

def main():
 for n in ['qc_v02','continuous_qc','final_video_motion','revision_qc_v02']:assert read(ROOT/f'records/{n}.json')['passed']
 enc=read(ROOT/'deliverables_4k/encoding.json')['files'][0];assert enc['frames']==11018 and enc['audio_same'] and enc['decode_warnings']==0
 assert sha(ROOT/'deliverables_4k'/enc['output'])==enc['output_sha256']
 save(ROOT/'records/4k_encoding_v02.json',enc)
 # Curate current records; v01 records copied for reference are not presented as v02 tests.
 excluded={'qc_v01.json','episode_specific_qc.json','subtitle_layout_validation.json','contrast.json','encoded_card_contrast.json','sharing.json','container_precision.json','visual_review.json','K03a_pending.json','release_archives.json','final_pixel_comparison_v03.json'}
 records=[p for p in ROOT.glob('records/*.json') if p.name not in excluded]
 groups=[('EP010_audio_and_subtitles_v02.zip',[p for p in ROOT.glob('deliverables/*') if p.suffix in ['.wav','.m4a','.srt','.txt']],ROOT/'deliverables'),('EP010_thumbnails_and_metadata_v02.zip',[p for p in ROOT.glob('deliverables/*') if p.suffix in ['.jpg','.md','.csv']],ROOT/'deliverables'),('EP010_QA_records_v02.zip',[*records,*ROOT.glob('review/*.jpg')],ROOT)]
 result=[]
 for name,files,base in groups:
  out=ROOT/'deliverables'/name
  with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for p in sorted(files):z.write(p,p.relative_to(base))
  with zipfile.ZipFile(out) as z:assert z.testzip() is None
  result.append(dict(name=name,bytes=out.stat().st_size,sha256=sha(out)))
 save(ROOT/'records/release_archives_v02.json',result);print('PACKAGED V02',flush=True)
if __name__=='__main__':main()
