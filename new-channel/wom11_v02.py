"""EP011 approved visual-only revision; v01 media and speech are read-only.

Run with the existing production Python: wom11_v02.py prepare|visuals|pictures|
package|reviews|precision|verify|continuous|motion|pixel|episode|revision|4k.
"""
import os,sys,shutil,subprocess,importlib,json
from pathlib import Path
os.environ['WOM11_VERSION']='v02'
os.environ['WOM11_ROOT']='/Volumes/ESD-02/新チャンネル/EP011_WeighingOfTheHeart/確認版_v02_20261104'
from wom11_produce import ROOT,REPO,read,save,sha
V01=ROOT.parent/'確認版_v01_20261104'

def copy_checked(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True)
 if not dst.exists():shutil.copy2(src,dst)
 assert sha(src)==sha(dst),(src,dst)

def prepare():
 assert Path('/Volumes/ESD-02').is_mount() and V01.exists()
 for d in ['records','assets','review','deliverables','_work/render','_work/motion_cache']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 names=['content','content_en','master_timeline','narration_segments_en','narration_segments_ja','narration_timeline_en','narration_timeline_ja','queries_en','queries_ja','first_pass_preserved','reading_replacements','subtitle_cues_en','subtitle_cues_ja','subtitle_validation','audio_qc','request','pronunciation_locations']
 for name in names:copy_checked(V01/f'records/{name}.json',ROOT/f'records/{name}.json')
 for p in (V01/'audio').rglob('*'):
  if p.is_file():copy_checked(p,ROOT/p.relative_to(V01))
 for p in (V01/'deliverables').glob('*'):
  if p.suffix in ['.wav','.m4a','.srt','.txt'] or p.name=='EP011_thumbnail_A.jpg':
   copy_checked(p,ROOT/'deliverables'/p.name.replace('_v01_','_v02_'))
 for p in (V01/'assets').glob('*'):
  if not p.name.startswith('E10B'):copy_checked(p,ROOT/'assets'/p.name)
 for p in (V01/'_work/render').glob('*'):
  if 'E10B' not in p.name:copy_checked(p,ROOT/'_work/render'/p.name)
 for p in (V01/'_work/motion_cache').glob('*.json'):copy_checked(p,ROOT/'_work/motion_cache'/p.name)
 catalog=read(V01/'records/source_assets.json');allowed={551786,557657,243713,551381,550986,558378,545802,420448}
 assets={'episode':'EP011','date':'2026-11-04','scope':'確認版v02の採用作品のみ。元の調査台帳はv01とresearchに保全。','original_directory':catalog['original_directory'],'source_catalog_sha256':sha(V01/'records/source_assets.json'),'summary':{'active_unique_works':8},'assets':[a for a in catalog['assets'] if a['met_object_id'] in allowed]};save(ROOT/'records/source_assets.json',assets)
 save(ROOT/'records/thumbnails.json',{'selected':'A','owner_approved':True,'image':next(a for a in read(V01/'records/thumbnails.json') if a['option']=='A')})
 save(ROOT/'records/v02_request.json',{'request_file':'new-channel/wom11_Claude確認_v01_20261104.md','request_sha256':sha(REPO/'new-channel/wom11_Claude確認_v01_20261104.md'),'baseline':str(V01),'unchanged_audio_scripts_subtitles':True,'thumbnail_selected':'A','approved_ammit_scale':[2.3,2.7],'no_new_speech':True})
 print('V02 INPUTS PRESERVED',flush=True)

def revision():
 manifest=read(ROOT/'records/visual_manifest.json');old={s['key']:s for s in read(V01/'records/visual_manifest.json')['shots']};shots=read(ROOT/'records/render_shots.json');by={s['key']:s for s in shots};checks=[]
 for name in ['content.json','content_en.json']:
  a=V01/'records'/name;b=ROOT/'records'/name;assert sha(a)==sha(b);checks.append({'file':str(b.relative_to(ROOT)),'sha256':sha(b),'matches_v01':True})
 for a in (V01/'deliverables').glob('*'):
  if a.suffix in ['.wav','.m4a','.srt']:
   b=ROOT/'deliverables'/a.name.replace('_v01_','_v02_');assert sha(a)==sha(b);checks.append({'file':str(b.relative_to(ROOT)),'sha256':sha(b),'matches_v01':True})
 images=[]
 for s in manifest['shots']:
  same=sha(ROOT/s['file'])==sha(V01/old[s['key']]['file']);assert same or s['key'] in ['D_summary','E01A_10_ammit']
  images.append({'key':s['key'],'sha256':sha(ROOT/s['file']),'matches_v01':same})
 assert len(shots)==23 and 'E10B' not in by and len(manifest['unique_originals'])==8
 for p in (ROOT/'deliverables').glob('*.md'):
  assert not any(s in p.read_text() for s in ['12074','50.130.16','Sargent','Egyptians Raising Water']),p
 d=by['D_denials'];p06=next(s for s in read(ROOT/'records/master_timeline.json')['segments'] if s['id']=='P06');assert d['end']==p06['end']
 stage=d['stages'][0];heads=[t for t in stage['text_boxes'] if t['major']];assert [t['text'] for t in heads]==['THE NEGATIVE CONFESSION','否定告白'] and min(t['glyph_height'] for t in heads)>=60
 for variant in d['stages'][1:]:assert sha(ROOT/variant['file'])==sha(V01/variant['file'])
 full=d['start']+d['stage_change_frames'][-1]/30;hold=d['end']-full;assert hold>=5.9
 cues={l:next(s for s in read(ROOT/f'records/narration_timeline_{l}.json')['segments'] if s['id']=='P10')['cues'] for l in ['en','ja']}
 thoth=by['E08A'];ammit=by['E01A_10_ammit'];assert 5<thoth['end']-thoth['start']<6
 assert abs(ammit['start']-cues['en'][6]['start'])<=1/60
 box=ammit['art_boxes'][0];size=[box[2]-box[0],box[3]-box[1]];assert 600<=size[1]<=700 and 2.3<=ammit['native_initial_scale']<=ammit['native_max_scale']<=2.7
 summary=next(c for c in read(ROOT/'records/contrast.json')['cards'] if c['key']=='D_summary');boxes=summary['boxes'];margin=min(min(b['box'][0],1920-b['box'][2]) for b in boxes);padding=min(b['min_padding_px'] for b in boxes);assert margin>=96 and padding>=32
 third=boxes[2]['box'];lines=[t['text'] for t in by['D_summary']['text_boxes'] if t['major'] and third[0]<=t['bbox'][0]<third[2] and third[1]<=t['bbox'][1]<third[3]]
 assert len(lines)==2 and ' '.join(lines)=='SPELL 30B — WORDS FOR THE HEART'
 from wom01_quiet_origins import stream_hash
 av=[]
 for l in ['en','ja']:
  oldmp=V01/f'deliverables/EP011_WeighingOfTheHeart_{l}_v01_1080p30.mp4';newmp=ROOT/f'deliverables/EP011_WeighingOfTheHeart_{l}_v02_1080p30.mp4'
  if newmp.exists():
   a,b=stream_hash(oldmp,'a'),stream_hash(newmp,'a');assert a==b;av.append({'language':l,'audio_stream_sha256':b,'matches_v01':True})
 result={'passed':True,'immutable_files':checks,'input_images':images,'thumbnail_A_sha256':sha(ROOT/'deliverables/EP011_thumbnail_A.jpg'),'thumbnail_selected':'A','audio_stream_identity':av,'P06':{'start':d['start'],'end':d['end'],'central_heading_glyph_heights':[t['glyph_height'] for t in heads],'all_five_lines_from':full,'all_five_lines_hold_seconds':hold,'E10B_removed':True},'P10':{'thoth_start':thoth['start'],'thoth_end':thoth['end'],'thoth_seconds':thoth['end']-thoth['start'],'ammit_start':ammit['start'],'ammit_image_initial_size':size,'ammit_native_initial_scale':ammit['native_initial_scale'],'ammit_native_max_scale':ammit['native_max_scale'],'ammit_max_image_size':[round((ammit['crop_pixels'][2]-ammit['crop_pixels'][0])*ammit['native_max_scale']),round((ammit['crop_pixels'][3]-ammit['crop_pixels'][1])*ammit['native_max_scale'])],'english_sentences':cues['en'][4:],'japanese_sentences':cues['ja'][4:],'japanese_Ammit_sentence_start_minus_visual_start':cues['ja'][5]['start']-ammit['start']},'D_summary':{'rows':[3,2],'edge_margin_px':margin,'minimum_inner_padding_px':padding,'major_glyph_height':summary['minimum_major_glyph_height'],'contrast':summary['foreground_contrast'],'boxes':boxes}}
 save(ROOT/'records/revision_v02.json',result);print('V02 REVISION VERIFIED',len(checks),'immutable files; P06',hold,'s; Thoth',result['P10']['thoth_seconds'],'s',flush=True)

def main():
 stage=sys.argv[1]
 if stage=='prepare':prepare();return
 if stage=='revision':revision();return
 if stage=='4k':subprocess.run([sys.executable,str(REPO/'new-channel/wom11_4k.py'),'v02','en'],check=True);return
 modules={'visuals':'visuals','pictures':'pictures','continuous':'continuous_qc','motion':'final_motion','pixel':'pixel_qc','episode':'episode_qc','metadata':'delivery','layout':'validate'}
 if stage in ['package','reviews','precision','verify']:getattr(importlib.import_module('wom11_render'),stage)()
 else:
  m=importlib.import_module('wom11_'+modules[stage]);getattr(m,'layout' if stage=='layout' else 'main')()
if __name__=='__main__':main()
