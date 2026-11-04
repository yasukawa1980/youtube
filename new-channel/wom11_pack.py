"""Bundle only verified EP011 deliverables; retain all originals and intermediate files."""
import zipfile
from wom11_produce import ROOT,read,save,sha,VERSION

def main():
 for n in [f'qc_{VERSION}','continuous_qc','final_video_motion','episode_qc','subtitle_layout_validation','encoded_card_contrast','visual_review']:assert read(ROOT/f'records/{n}.json')['passed']
 if VERSION=='v02':
  revision=read(ROOT/'records/revision_v02.json');assert revision['passed'] and len(revision['audio_stream_identity'])==2
 enc=read(ROOT/'deliverables_4k/encoding.json')['files'][0];assert enc['frames']==11441 and enc['audio_same'] and enc['decode_warnings']==0
 assert sha(ROOT/'deliverables_4k'/enc['output'])==enc['output_sha256'];save(ROOT/f'records/4k_encoding_{VERSION}.json',enc)
 records=[p for p in ROOT.glob('records/*.json') if p.name not in ['sharing.json','release_archives.json']]
 final_review=[p for p in ROOT.glob('review/*.jpg') if not p.name.startswith(('early_','storyboard_'))]
 groups=[(f'EP011_audio_and_subtitles_{VERSION}.zip',[p for p in ROOT.glob('deliverables/*') if p.suffix in ['.wav','.m4a','.srt','.txt']],ROOT/'deliverables'),(f'EP011_thumbnails_and_metadata_{VERSION}.zip',[p for p in ROOT.glob('deliverables/*') if p.suffix in ['.jpg','.md','.csv']],ROOT/'deliverables'),(f'EP011_QA_records_{VERSION}.zip',[*records,*final_review],ROOT)]
 result=[]
 for name,files,base in groups:
  out=ROOT/'deliverables'/name
  with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
   for p in sorted(files):z.write(p,p.relative_to(base))
  with zipfile.ZipFile(out) as z:assert z.testzip() is None
  result.append(dict(name=name,bytes=out.stat().st_size,sha256=sha(out)))
 save(ROOT/'records/release_archives.json',result);print('PACKAGED',len(result),flush=True)
if __name__=='__main__':main()
