"""Package audited EP009 v03 and record unchanged narration/art inputs."""
import zipfile,shutil
from pathlib import Path
from wom09_shorts_revision_v03 import ROOT,OLD,read,save,sha

def main():
 media=read(ROOT/'records/media_qc.json');contrast=read(ROOT/'records/contrast_qc.json');diff=read(ROOT/'records/unchanged_frames_qc.json');assert media['passed'] and contrast['passed']
 assert all(sha(r['file'])==r['sha256'] for r in media['rows'])
 rows=read(OLD/'records/shorts.json')['shorts'];enc=read(ROOT/'records/encoding.json')['rows'];checks=[]
 for s,e in zip(rows,enc):
  sid=s['id'];old=(OLD/f'_work/{sid}.ass').read_text().splitlines();new=(ROOT/f'_work/{sid}_narration.ass').read_text().splitlines();removed=[line for line in old if line not in new]
  assert len(removed)==4 and all(line.startswith('Dialogue:') for line in removed)
  for line in removed:
   t=line.split(',')[1];a,b,c=map(float,t.split(':'));assert abs(a*3600+b*60+c-s['cta_start'])<.011
  assert all(line in old for line in new)
  for source in e['source_shots']:assert sha(source['path'])==source['sha256']
  checks.append(dict(id=sid,narration_ass_unchanged=True,removed_only_old_cta_events=4,unchanged_source_shots=e['source_shots'],headline_sha256=sha(OLD/f'assets/{sid}_headline.png'),cta_start_frame=s['cta_start_frame'],cta_end_frame=s['frames'],cta_duration_frames=75,new_appearance='instant',source_file=str(OLD/f'deliverables/QO_short_EP009_{sid}_v02.mp4'),source_sha256=sha(OLD/f'deliverables/QO_short_EP009_{sid}_v02.mp4')))
  for ext in ['txt','srt']:shutil.copy2(OLD/f'deliverables/QO_short_EP009_{sid}_v02.{ext}',ROOT/f'deliverables/QO_short_EP009_{sid}_v03.{ext}')
 save(ROOT/'records/preserved_inputs_qc.json',dict(passed=True,rows=checks,script_subtitle_audio_picture_camera_timing_unchanged=True))
 credits=(OLD/'deliverables/credits_and_sources.txt').read_text().replace('Shorts v02','Shorts v03');(ROOT/'deliverables/credits_and_sources.txt').write_text(credits)
 (ROOT/'deliverables/README_review.txt').write_text('EP009ショートv03・未投稿。最後2.5秒の案内だけを拡大。登録案内は実字高84px×2行、砂色の板。本編案内は56px、黒の下地。横幅は指定範囲へ調整。グループx80–880/y1030–1376。開始はv02と同時、即時表示（依頼で許容）。\n本人は通常のH.264 Highを優先し、再圧縮差を記録する方式を指定。案内前の全フレームはrecords/unchanged_frames_qc.json・CSVで比較。音声ハッシュはv02と一致。v02_で始まる記録は変更していない元版の参照資料。\nreview/のCTA開始・最終フレーム、CTA_transition、冒頭、2秒おき画像を確認してください。2026-11-02に本人がv02の試聴OK。v03はClaude確認待ちでYouTubeへ投稿しない。\n')
 archive=ROOT/'deliverables/EP009_shorts_review_v03.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for folder in ['records','review']:
   for p in sorted((ROOT/folder).rglob('*')):
    if p.is_file() and p.suffix in ['.json','.jpg','.log']:z.write(p,str(p.relative_to(ROOT)))
  for p in (ROOT/'deliverables').iterdir():
   if p.suffix in ['.txt','.srt','.csv']:z.write(p,'deliverables/'+p.name)
  z.write(ROOT/'assets/cta_v03.png','assets/cta_v03.png')
 save(ROOT/'records/delivery_manifest.json',dict(files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted((ROOT/'deliverables').iterdir()) if p.suffix in ['.mp4','.zip']]))
 print('PACKAGED',archive.stat().st_size,flush=True)
if __name__=='__main__':main()
