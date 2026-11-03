"""Revision scope, unchanged audio/timing, text content and subtitle clearance."""
import re
import os
os.environ.setdefault('WOM10_ROOT','/Volumes/ESD-02/新チャンネル/EP010_Krampus/確認版_v02_20261103')
from pathlib import Path
from wom10_produce import ROOT,read,save,sha
from wom01_quiet_origins import stream_hash
OLD=ROOT.parent/'確認版_v01_20261102'
def main():
 old=read(OLD/'records/visual_manifest.json');new=read(ROOT/'records/visual_manifest.json');changed={'K03a','D_names','D_summary','D_dec6','D_1869','D_grimm','D_noancient'};rows=[]
 for a,b in zip(old['shots'],new['shots']):
  assert a['key']==b['key'];key=a['key'];same=sha(OLD/a['file'])==sha(ROOT/b['file']);assert same==(key not in changed),(key,same)
  if key.startswith('D_') and key!='D_names':
   clean=lambda ts:re.sub(r'\s+','',''.join(t['text'] for t in ts))
   assert clean(a['text_boxes'])==clean(b['text_boxes']),key
  rows.append(dict(key=key,input_pixels_same=same))
 for name in ['master_timeline.json','content_en.json','content.json','subtitle_cues_en.json','subtitle_cues_ja.json']:assert sha(OLD/'records'/name)==sha(ROOT/'records'/name),name
 for lang in ['en','ja']:
  assert sha(OLD/f'deliverables/EP010_Krampus_{lang}_v01_1080p30.srt')==sha(ROOT/f'deliverables/EP010_Krampus_{lang}_v02_1080p30.srt')
  assert stream_hash(OLD/f'deliverables/EP010_Krampus_{lang}_v01_1080p30.mp4','a')==stream_hash(ROOT/f'deliverables/EP010_Krampus_{lang}_v02_1080p30.mp4','a')
  assert sha(OLD/f'deliverables/EP010_audio_{lang}.wav')==sha(ROOT/f'deliverables/EP010_audio_{lang}.wav')
 cards=read(ROOT/'records/layout_v02.json')['cards'];summary=next(c for c in cards if c['key']=='D_summary');assert min(b['min_padding_px'] for b in summary['boxes'])>=24
 assert all(t['cap_height']>=60 for t in summary['text_boxes'] if t.get('major') and t['bbox'][1]>110)
 names=next(c for c in cards if c['key']=='D_names');assert all(t['cap_height']>=60 for t in names['text_boxes'] if t['text'] in ['KNECHT RUPRECHT','KLAUBAUF','KRAMPUS'])
 # Existing review subtitles retain FontSize14. Larger optional FontSize26 may overlap these expanded diagrams.
 sub=read(OLD/'records/subtitle_layout_validation.json')['checks'];min_top=min(c['minimum_subtitle_top'] for c in sub if c['font_size']==14);maxbottom=max(t['bbox'][3] for c in cards for t in c['text_boxes']);assert maxbottom<min_top,(maxbottom,min_top)
 oldshots=read(OLD/'records/render_shots.json');newshots=read(ROOT/'records/render_shots.json');assert [(s['key'],s['start'],s['end']) for s in oldshots]==[(s['key'],s['start'],s['end']) for s in newshots]
 save(ROOT/'records/revision_qc_v02.json',dict(passed=True,changed_assets=sorted(changed),shot_checks=rows,script_audio_srt_timing_identical=True,subtitle_font_size=14,subtitle_minimum_top=min_top,card_maximum_text_bottom=maxbottom,clearance_px=min_top-maxbottom,summary_minimum_padding=min(b['min_padding_px'] for b in summary['boxes']),human_full_listening=False,K03a=read(ROOT/'records/v02_owner_approval.json')))
 print('REVISION QC PASS',maxbottom,min_top,flush=True)
if __name__=='__main__':main()
