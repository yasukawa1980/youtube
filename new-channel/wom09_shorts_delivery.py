"""EP009ショート確認用の字幕・台本・測定記録・Draft添付をまとめる。"""
import json,csv,zipfile
from pathlib import Path
from wom09_shorts import ROOT,REQUEST,sha,save
from wom_shorts_produce import read
from wom09_shorts_render import VERSION,CONFIG

def main():
 rows=read(ROOT/'records/shorts.json')['shorts'];shots=read(ROOT/'records/render_shots.json');media=read(ROOT/'records/media_qc.json');contrast=read(ROOT/'records/contrast_qc.json');motion=read(ROOT/'records/motion_qc.json')
 assert media['passed'] and contrast['passed'] and motion['passed']
 if VERSION=='v02':assert read(ROOT/'records/revision_qc.json')['passed'] and read(ROOT/'records/preserved_visuals_qc.json')['passed']
 assert all(q['sha256']==sha(ROOT/'deliverables'/q['name']) for q in media['media'])
 def time(f):
  ms=round(f/30*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 glyphs=[]
 for s in rows:
  sid=s['id'];pages=[p for p in read(ROOT/'records/caption_manifest.json') if p['short_id']==sid]
  assert ' '.join(p['text'] for p in pages if not p.get('brand'))==s['text']
  assert all(len(p['lines'])<=2 and all(CONFIG.get('minimum_line_words',4)<=len(line.split())<=5 for line in p['lines']) for p in pages)
  assert any('670 BC.' in p['text'] for p in pages) if sid=='T2' else True
  plates=read(ROOT/f'records/{sid}_backplates.json')
  assert all(80<=p['plate_bbox'][0]<p['plate_bbox'][2]<=880 and 1150<=p['plate_bbox'][1]<p['plate_bbox'][3]<=1450 for p in plates)
  glyphs.append(dict(id=sid,caption_pages=len([p for p in pages if not p.get('brand')]),lines=len(plates),exact_script=True,all_bounds_passed=True,cta_lines=[p['text'] for p in pages if p.get('brand')]))
  # Narration subtitles only; the silent CTA is burned into the video.
  cues=[]
  for i,p in enumerate([p for p in pages if not p.get('brand')],1):cues.append(f'{i}\n{time(p["start_frame"])} --> {time(p["end_frame"])}\n'+ '\n'.join(p['lines']))
  (ROOT/f'deliverables/QO_short_EP009_{sid}_{VERSION}.srt').write_text('\n\n'.join(cues)+'\n')
  (ROOT/f'deliverables/QO_short_EP009_{sid}_{VERSION}.txt').write_text(s['text']+'\n')
 save(ROOT/'records/subtitle_qc.json',dict(passed=True,rows=glyphs,method=('台本全文・語数・各行4〜5語（T3の7語文/6語節のみ3語行）・実ASSレンダーの文字/下地範囲を照合。' if VERSION=='v02' else '台本全文・語数・各行4〜5語・実ASSレンダーの文字/下地範囲を照合。')))
 cards=[];scales=[]
 for s in shots:
  a=s['source'];maximum=a['native_max_scale'];assert maximum<=1.6
  scales.append(dict(short=s['short_id'],asset=s['asset_id'],initial_scale=a['native_initial_scale'],maximum_scale=maximum,original_pixels=a['original_pixels'],opening_height_fraction=s['foreground_height_fraction']))
  if s['asset_id'].startswith('D_'):
   text=' '.join(t['text'] for t in s['card_texts']);expected={'D_lastline':'"Thus held they funeral for Hector tamer of horses."','D_gifts':'"I fear the Grecians even when they offer gifts." timeo Danaos et dona ferentes'}[s['asset_id']];assert text==expected;cards.append(dict(asset=s['asset_id'],exact_text=text,source=a['source'],passed=True))
 save(ROOT/'records/scale_and_quote_qc.json',dict(passed=True,scales=scales,cards=cards,T2_opening_note=('写真の全高885pxを1.6倍の1416px（73.75%）で表示。横を切り出し、車輪・窓へ移動。' if VERSION=='v02' else '990×885の原寸から首・胴・脚の全体と縦横比を守るため、最初の実画像高は912/1920=47.5%。80%は目安として扱い、原寸1.6倍上限と全体提示を優先。背景は同じ写真のぼかし。語に合わせた脚元・窓への移動でも最大1.54576倍。')))
 credits=f'Quiet Origins EP009 Shorts {VERSION}\n\nMain film: https://youtu.be/WSipndkxiiE (scheduled 2026-11-06 09:00 JST)\nNarration: Kokoro af_heart, speed 0.82; new reads of approved scripts; no reading replacements.\nMusic: QO_THEME_A02, original project music.\nNo AI images or AI video. Prints use the main-film warm monochrome treatment.\n\n'
 if VERSION=='v02':credits=credits.replace('new reads of approved scripts','identical v01 audio streams; no resynthesis')
 ledger={a['key']:a for a in read(Path('/Volumes/ESD-02/新チャンネル/EP009_TrojanHorse/確認版_v03_20261101/records/source_assets.json'))['assets']}
 for s in shots:
  a=s['source'];credits+=f'{s["short_id"]} / {s["asset_id"]}: {a["source"]}\n'
  if s['asset_id'] in ledger:credits+=ledger[s['asset_id']]['page']+'\n'
 credits+='\nThe Met: Open Access/CC0. Rijksmuseum historical prints: public domain/open collection. Mykonos photograph: AbelDionis, CC0. Iliad translation: Lang, Leaf & Myers (1883). Aeneid translation: J. W. Mackail (1885).\n'
 (ROOT/'deliverables/credits_and_sources.txt').write_text(credits)
 (ROOT/'deliverables/README_review.txt').write_text('第9話ショート3本・未投稿確認版。台本・音声・字幕・最後の登録案内を本人に試聴確認していただくための資料。\nT1 20.566667秒／T2 21.6秒／T3 20.833333秒。最後2.5秒に無音声の2行案内。\nT2は全体像を守るため、最初の実画像高は47.5%（80%目安より小さい）。原寸1.6倍上限を優先。\nカット時刻はrecords/render_shots.json、字幕と対比はrecords/shorts.json、検査は各qc.json、確認画像はreview/。\n人間による全文試聴は未実施。投稿せず、Claudeと本人の確認待ち。\n')
 if VERSION=='v02':
  p=ROOT/'deliverables/README_review.txt';p.write_text('EP009 Shorts v02 — v01音声・台本・尺・最後の案内を保持。T2写真を高さ1416px（73.75%）、最大1.6倍へ変更。字幕は全20ページで文をまたぐもの0、最短1.4秒。T3のみ7語文/6語節を3語行で処理。\n未投稿。revision_qc.jsonの字幕一覧、T2_camera_cues.jpg、全QCを確認してください。\n')

 archive=ROOT/f'deliverables/EP009_shorts_review_{VERSION}.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for folder in ['records','review']:
   for p in sorted((ROOT/folder).rglob('*')):
    if p.is_file() and p.suffix in ['.json','.jpg','.log']:z.write(p,str(p.relative_to(ROOT)))
  for p in sorted((ROOT/'deliverables').iterdir()):
   if p.suffix in ['.txt','.srt','.csv']:z.write(p,'deliverables/'+p.name)
  for p in sorted((ROOT/'audio').glob('*_native.wav')):z.write(p,'audio/'+p.name)
 save(ROOT/'records/delivery_manifest.json',dict(files=[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in sorted((ROOT/'deliverables').iterdir()) if p.suffix in ['.mp4','.zip']]))
 print('PACKAGED',archive.stat().st_size,flush=True)
if __name__=='__main__':main()
