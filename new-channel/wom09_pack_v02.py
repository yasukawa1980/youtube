"""Package only verified v02 media; preserve all v01 files."""
import os
os.environ.setdefault('WOM09_ROOT','/Users/ryo/Desktop/新チャンネル/EP009_TrojanHorse/確認版_v02_20261101')
from wom09_produce import ROOT,read,save,sha
from wom09_pack import archive

def main():
 for n in ['qc_v02','continuous_qc','final_video_motion','revision_qc_v02','subtitle_layout_validation']:assert read(ROOT/f'records/{n}.json')['passed']
 for q in read(ROOT/'records/qc_v02.json')['files']:assert sha(ROOT/'deliverables'/q['name'])==q['sha256']
 assert sha(ROOT/'deliverables/EP009_TrojanHorse_en_v02_1080p30.mp4')==read(ROOT/'records/final_video_motion.json')['video_sha256']
 d=ROOT/'deliverables';r=[]
 r.append(archive('EP009_audio_and_subtitles_v02.zip',[*d.glob('*.wav'),*d.glob('*.m4a'),*d.glob('*.srt'),*d.glob('*pronunciation*.txt')],d))
 r.append(archive('EP009_thumbnails_and_metadata_v02.zip',[*d.glob('*.jpg'),*d.glob('*.md'),*d.glob('*.csv')],d))
 r.append(archive('EP009_QA_records_v02.zip',[*ROOT.glob('records/*.json'),*ROOT.glob('records/*.txt'),*ROOT.glob('records/*.log'),*ROOT.glob('review/*.jpg')],ROOT))
 save(ROOT/'records/release_archives.json',r);print('V02 ARCHIVES',[(x['name'],x['bytes']) for x in r],flush=True)
if __name__=='__main__':main()
