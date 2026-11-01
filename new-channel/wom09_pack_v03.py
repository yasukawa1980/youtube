"""Package v03 for review; retain the explicit final-pixel equality exception."""
import os
os.environ.setdefault('WOM09_ROOT','/Volumes/ESD-02/新チャンネル/EP009_TrojanHorse/確認版_v03_20261101')
from wom09_produce import ROOT,read,save,sha
from wom09_pack import archive

def main():
 for n in ['qc_v03','continuous_qc','final_video_motion','revision_qc_v03','subtitle_layout_validation']:assert read(ROOT/f'records/{n}.json')['passed']
 for q in read(ROOT/'records/qc_v03.json')['files']:assert sha(ROOT/'deliverables'/q['name'])==q['sha256']
 assert sha(ROOT/'deliverables/EP009_TrojanHorse_en_v03_1080p30.mp4')==read(ROOT/'records/final_video_motion.json')['video_sha256']
 # Draft review includes the measured 24-frame compression exception; do not
 # mislabel this exact-pixel comparison as passed. Layout/audio/format checks pass.
 assert read(ROOT/'records/final_pixel_comparison_v03.json')['comparison_complete']
 d=ROOT/'deliverables';r=[]
 r.append(archive('EP009_audio_and_subtitles_v03.zip',[*d.glob('*.wav'),*d.glob('*.m4a'),*d.glob('*.srt'),*d.glob('*pronunciation*.txt')],d))
 r.append(archive('EP009_thumbnails_and_metadata_v03.zip',[*d.glob('*.jpg'),*d.glob('*.md'),*d.glob('*.csv')],d))
 r.append(archive('EP009_QA_records_v03.zip',[*ROOT.glob('records/*.json'),*ROOT.glob('records/*.txt'),*ROOT.glob('records/*.log'),*ROOT.glob('review/*.jpg')],ROOT))
 save(ROOT/'records/release_archives.json',r);print('V03 ARCHIVES',[(x['name'],x['bytes']) for x in r],flush=True)
if __name__=='__main__':main()
