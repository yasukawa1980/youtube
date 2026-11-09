"""Collect measured delivery evidence and archive audio, metadata and small reviews."""
import shutil
import zipfile
from pathlib import Path
from PIL import Image
from pnt02_produce import ROOT, REPO, read, save, sha

OUT=REPO/'painting/pnt02_確認版_v01_20261110'


def main():
    summary=dict(video_completed=True,auditory_review_completed=False,languages={},technical_checks_passed=True)
    for lang in ['en','ja']:
        local=ROOT/lang
        dest=OUT/lang
        files=[]
        for path in sorted((local/'records').glob('*.json')):
            shutil.copy2(path,dest/path.name)
        review=dest/'final_video_review';review.mkdir(exist_ok=True)
        for path in sorted((local/'review').glob('*.jpg')):
            assert path.stat().st_size<1024*1024
            with Image.open(path) as im:assert max(im.size)<=1280
            shutil.copy2(path,review/path.name)
        for path in sorted((local/'deliverables').iterdir()):
            if path.suffix not in ['.mp4','.m4a','.wav','.srt']:continue
            files.append(dict(name=path.name,bytes=path.stat().st_size,sha256=sha(path)))
            if path.suffix=='.srt':shutil.copy2(path,dest/path.name)
        qc=read(local/'records/qc_v01.json')
        sub=read(local/'records/final_subtitle_qc.json')
        assert qc['passed'] and sub['passed']
        variants={}
        for suffix in (['','_4k'] if lang=='en' else ['']):
            checks={key:read(local/f'records/{filename}{suffix}.json') for key,filename in [
                ('continuous','continuous_qc'),('layout','final_layout'),('motion','final_video_motion')]}
            assert all(r['passed'] for r in checks.values()),(lang,suffix)
            variants[suffix or '1080p']=dict(decoded_frames=checks['continuous']['decoded_frames'],
                decode_warnings=checks['continuous']['decode_warnings'],
                motion_max_ratio=max(r['ratio'] for r in checks['motion']['checks']),
                native_scale_max=checks['layout']['native_scale_max'],
                contrast_min=checks['layout']['contrast_min'],
                plate_padding_min=checks['layout']['plate_padding_min'])
        summary['languages'][lang]=dict(duration_seconds=qc['duration_seconds'],frames=qc['frames'],
            loudness=qc['files'][0]['loudness'],subtitle_pages=sub['srt_pages'],
            subtitle_min_seconds=sub['min_srt_seconds'],subtitle_max_line=sub['max_line'],
            subtitle_min_clearance=sub['min_clearance_px'],variants=variants,files=files)
    overlap=read(ROOT/'records/final_moving_overlap.json');assert overlap['passed']
    shutil.copy2(ROOT/'records/final_moving_overlap.json',OUT/'final_moving_overlap.json')
    summary['maximum_actual_moving_overlap']=max(r['maximum_overlap'] for r in overlap['checks'])
    summary['pending']=['固有名・難読語の公式音声／辞書との実聴照合（聴取手段なし、本人試聴へ）',
        '本人の全編試聴：発音・年代帯と発話の厳密な同期・テンポ・縦置きの大きさ・文字カードの単調さ・サムネ選択']
    summary['chronology_timing_method']='Native sentence and subtitle-page timing plus character-offset interpolation, not forced word alignment; final pixels verified against this timing.'
    summary['image_policy']='Only the six approved museum source images. No generative images or corrections. Common approved 1080p brand clips alone are Lanczos-scaled in the 4K delivery.'
    save(OUT/'final_summary.json',summary)
    save(ROOT/'records/final_summary.json',summary)
    archive=ROOT/'deliverables'
    with zipfile.ZipFile(archive/'PNT02_audio_subtitles_final_v01.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for lang in ['en','ja']:
            for path in sorted((ROOT/lang/'deliverables').iterdir()):
                if path.suffix in ['.wav','.m4a','.srt']:z.write(path,f'{lang}/{path.name}')
        z.write(OUT/'reading_review.json','reading_review.json')
        z.writestr('README.txt','Final v01 audio/subtitle package for human review. Pronunciations have NOT been auditioned. Original unmodified speech, independent EN/JA timing. No publication.\n')
    with zipfile.ZipFile(archive/'PNT02_final_QC_metadata_thumbnails_v01.zip','w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for folder in [OUT,REPO/'painting/サムネ確認用/pnt02']:
            for path in sorted(folder.rglob('*')):
                if path.is_file() and path.name not in ['sharing.json','final_sharing.json','README.md','resume_status.json']:
                    z.write(path,path.relative_to(REPO/'painting'))
        z.writestr('README.txt','See final_summary.json and final_video_review for final delivery QC. card_*/design_* and preliminary records are historical design evidence, not final video frames. User listening and thumbnail choice are pending. Release remains private draft.\n')
    print('COLLECTED',sum(len(v['files']) for v in summary['languages'].values()),'deliverables',flush=True)


if __name__=='__main__':
    main()
