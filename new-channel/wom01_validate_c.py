"""Validate v04 text/timing/waveforms and generate explicitly simulated subtitle layouts.
Set WOM_EPISODE_ROOT to the v04 production root. No media is overwritten.
"""
from pathlib import Path
import json,re,subprocess,sys,os
import numpy as np
import soundfile as sf
from PIL import Image,ImageDraw,ImageFont
R=Path(os.environ['WOM_EPISODE_ROOT'])
SR=24000
read=lambda p:json.loads(p.read_text())
norm=lambda s:re.sub(r'\s+','',s)
def ms(t):
 h,m,s,f=map(int,re.split('[:,]',t));return (((h*60)+m)*60+s)*1000+f
report={'version':'v04','duration_seconds':682.7,'subtitle_languages':{},'waveform_checks':{},'layout_checks':[],'human_full_listening':False,'layout_method':'Pillow simulation: 56px Arial/Hiragino, 68px line height, 34px bottom margin. Not a player screenshot; local FFmpeg lacks libass. Actual player settings vary.'}
for lang in ['en','ja']:
 timeline=read(R/f'records/narration_timeline_{lang}.json');pages=read(R/f'records/subtitle_cues_{lang}.json')['cues']
 original=[c for s in timeline['segments'] for c in s['cues']];source={c['id']:c for c in original};grouped={k:[] for k in source}
 blocks=(R/f'deliverables/EP001_字幕_{lang}.srt').read_text().strip().split('\n\n');assert len(blocks)==len(pages)
 prev=0;dur=[];line_lengths=[]
 for i,(block,c) in enumerate(zip(blocks,pages),1):
  lines=block.splitlines();assert int(lines[0])==i
  a,b=map(ms,lines[1].split(' --> '));assert prev<=a<b<=682700
  assert a==round(c['start']*1000) and b==round(c['end']*1000)
  assert '\n'.join(lines[2:])==c['text'] and len(lines[2:])<=2
  prev=b;dur.append((b-a)/1000);line_lengths.extend(map(len,lines[2:]));grouped[c['sentence_id']].append(c)
 for cid,p in grouped.items():
  assert p and norm(''.join(c['text'] for c in p))==norm(source[cid]['text'])
  assert p[0]['start']==source[cid]['start'] and p[-1]['end']==source[cid]['end']
 assert max(line_lengths)<=(42 if lang=='en' else 23)
 subprocess.run(['ffmpeg','-v','error','-i',str(R/f'deliverables/EP001_字幕_{lang}.srt'),'-f','srt','-'],stdout=subprocess.DEVNULL,check=True)
 report['subtitle_languages'][lang]={'cue_count':len(pages),'sentence_count':len(original),'max_lines':2,'max_characters_per_line':max(line_lengths),'minimum_cue_seconds':min(dur),'source_text_preserved':True,'sentence_boundaries_match':True,'no_overlap_or_out_of_bounds':True,'srt_parse':'pass'}
 full,sr=sf.read(R/f'audio/{lang}/narration.wav',dtype='int16');assert sr==SR
 for seg in timeline['segments']:
  a,sr=sf.read(R/seg['audio_file'],dtype='int16');start=round(seg['start']*SR)
  assert np.array_equal(full[start:start+len(a)],a),seg['id']
 if lang=='ja':
  for c in original:
   a,sr=sf.read(R/c['audio_file'],dtype='int16');start=round(c['start']*SR)
   assert np.array_equal(full[start:start+len(a)],a),c['id']
 report['waveform_checks'][lang]={'all_28_segment_samples_match_master':True,'all_115_sentence_samples_match_master':True if lang=='ja' else None}
assert len(read(R/'records/reading_corrections.json'))==4
# Render external subtitles over representative stills at real new timeline timestamps.
manifest=read(R/'records/visual_manifest.json');master=read(R/'records/master_timeline.json');segments={s['id']:s for s in master['segments']}
shots=[]
for label in ['AI reconstruction','Museum object','Facsimile (copy on paper)','Concept diagram','Production credits']:
 shot=next(s for s in manifest['shots'] if s['label']==label);shots.append(shot)
folder=R/'review/subtitle_layout';folder.mkdir(exist_ok=True);contact=Image.new('RGB',(1280,len(shots)*390),'#ddd');draw=ImageDraw.Draw(contact)
for i,shot in enumerate(shots):
 src=R/shot['file'];a=np.array(Image.open(src));assert np.all(a[941:]==[12,24,32])
 for j,lang in enumerate(['en','ja']):
  tl=read(R/f'records/narration_timeline_{lang}.json');seg=next(s for s in tl['segments'] if s['id']==shot['segment_id'])
  ids={c['id'] for c in seg['cues']}
  page=max((c for c in read(R/f'records/subtitle_cues_{lang}.json')['cues'] if c['sentence_id'] in ids),key=lambda c:(len(c['text'].splitlines()),len(c['text'])))
  stamp=(page['start']+page['end'])/2;out=folder/f'{i:02}_{lang}.png';base=folder/f'{i:02}_base.png'
  # Layout simulation only: this local ffmpeg build has no libass subtitles filter.
  # Use a conventional 56 px font at 1080p, 68 px line spacing and 34 px bottom margin.
  fontpath=next(Path('/System/Library/Fonts').glob('* W3.ttc')) if lang=='ja' else Path('/System/Library/Fonts/Supplemental/Arial.ttf')
  font=ImageFont.truetype(str(fontpath),56);im=Image.open(src).convert('RGB');base_array=np.array(im)
  layer=Image.new('RGBA',im.size,(0,0,0,0));d=ImageDraw.Draw(layer);lines=page['text'].splitlines()
  top=1080-34-68*len(lines)
  for k,line in enumerate(lines):
   width=d.textlength(line,font=font);x=(1920-width)/2;y=top+68*k
   d.rectangle((x-14,y-3,x+width+14,y+65),fill=(0,0,0,180))
   d.text((x,y),line,font=font,fill='white',stroke_width=1,stroke_fill='black',anchor='lt')
  im=Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB');im.save(out)
  changed=np.any(np.array(im).astype(int)!=base_array.astype(int),axis=2)
  ys=np.where(changed)[0];assert len(ys)>0 and ys.min()>900,(shot['label'],lang,ys.min() if len(ys) else None)
  im=Image.open(out);im.thumbnail((640,360));contact.paste(im,(j*640,i*390));draw.text((j*640+8,i*390+363),f'{lang} {shot["label"]} {stamp:.2f}s',fill='black')
  report['layout_checks'].append({'label':shot['label'],'language':lang,'time_seconds':stamp,'subtitle_top_y':int(ys.min()),'subtitle_bottom_y':int(ys.max()),'header_and_source_uncovered':True})
contact.save(R/'review/subtitle_layout_contact.jpg',quality=86)
(R/'records/subtitle_and_layout_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report['subtitle_languages'],ensure_ascii=False));print('All waveform and ten subtitle overlay checks passed')
