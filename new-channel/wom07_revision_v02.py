"""EP007 v02: replace one closed-GOP interval, preserving all other picture packets."""
import argparse,copy,json,subprocess,shutil,math,hashlib
from pathlib import Path
from fractions import Fraction
import numpy as np
from PIL import Image,ImageOps,ImageFilter,ImageEnhance,ImageDraw,ImageFont
from wom07_produce import ROOT as OLD,REPO,read,save,sha,ff,probe
from wom01_quiet_origins import stream_hash
ROOT=OLD.parent/'確認版_v02_20261029'
A,B=3078,3776
TOTAL=10774
SOURCE='John Smith, New England, 1624 state — facsimile c. 1919 • Boston Public Library, Leventhal Map & Education Center'
LABEL='MAP (FACSIMILE)｜地図（複製）'
BG='#0c1820';GOLD='#d8b575';MUTED='#b0bfc3'
EN='/System/Library/Fonts/Supplemental/Arial.ttf';JA='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
def font(size,value):return ImageFont.truetype(JA if any(ord(c)>0x2fff for c in value) else EN,size)
def header_records():
 d=ImageDraw.Draw(Image.new('RGB',(1920,110)));size=23
 while d.textlength(SOURCE,font=font(size,SOURCE))>1730:size-=1
 items=[('QUIET ORIGINS  /  EP007',(92,18),28),(LABEL,(1820-d.textlength(LABEL,font=font(27,LABEL)),21),27),(SOURCE,(92,69),size)]
 return [{'text':value,'bbox':list(d.textbbox(xy,value,font=font(n,value)))} for value,xy,n in items]
def header(im):
 d=ImageDraw.Draw(im);d.rectangle((0,0,1920,109),fill=BG)
 d.text((92,18),'QUIET ORIGINS  /  EP007',font=font(28,'Q'),fill=GOLD)
 f=font(27,LABEL);d.text((1820-d.textlength(LABEL,font=f),21),LABEL,font=f,fill=GOLD)
 size=23
 while d.textlength(SOURCE,font=font(size,SOURCE))>1730:size-=1
 assert size>=17
 d.text((92,69),SOURCE,font=font(size,SOURCE),fill=MUTED)
 return im

def prepare():
 for d in ['records','assets','review','deliverables','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
 for name in ['content.json','content_en.json','master_timeline.json','source_assets.json','narration_timeline_en.json','narration_timeline_ja.json','subtitle_validation.json','subtitle_layout_validation.json','audio_qc.json','reading_replacements.json','pronunciation_locations.json','kling_generation.json']:
  shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
 for p in (OLD/'deliverables').iterdir():
  if p.suffix in ['.wav','.m4a','.srt','.txt']:
   dst=ROOT/'deliverables'/p.name.replace('_v01_','_v02_')
   if dst.exists():assert sha(dst)==sha(p)
   else:shutil.copy2(p,dst)
 thumb=OLD/'deliverables/wom07_サムネB_20261029.jpg';shutil.copy2(thumb,ROOT/'deliverables/EP007_thumbnail_B.jpg')
 approvals={'date_jst':'2026-10-29','direct_user_style_reply':'今回の写実的な画風で採用する','latest_instruction':'クロードからの申し送りを確認して進めて下さい','handoff':'new-channel/wom07_修正依頼_v02_20261029.md','handoff_sha256':sha(REPO/'new-channel/wom07_修正依頼_v02_20261029.md'),'scope':'P05 V02 replaced by G11-01. V01, V03 and V04 retained. Narration/BGM/full listening approved in handoff. Thumbnail B selected.','thumbnail':'B / NOT IN THE LETTER','human_listening':'approved: 大丈夫です (recorded in Claude handoff)','additional_generation':False,'additional_credits':0,'publication_authorized':False}
 save(ROOT/'records/approvals_v02.json',approvals)
 maprec=next(x for x in read(REPO/'new-channel/research/wom07_素材台帳_20261029.json')['assets'] if x['id']=='G11-01');assert sha(maprec['local_original'])==maprec['sha256']
 w,h=maprec['width'],maprec['height'];aspect=1760/820
 def rect(x,y,width):return [x,y,x+width,y+width*w/h/aspect]
 plan={'source':maprec,'start_crop_normalized':rect(.065,.49,.81),'end_crop_normalized':rect(.102,.786,.28),'plimouth_word_bbox_normalized':[.142,.835,.197,.855],'plimouth_label_center_normalized':[.17,.845],'frames':B-A,'interval_frames_half_open':[A,B],'seconds':[A/30,B/30],'viewport':[80,110,1760,820],'label':LABEL,'source_caption':SOURCE,'interpolation':'Geometric crop width, linearly interpolated center, floating-point bicubic source sampling.','portrait':'Excluded from both crops and the blurred background source.'}
 save(ROOT/'records/map_plan.json',plan)
 shots=copy.deepcopy(read(OLD/'records/render_shots.json'))
 for s in shots:
  if s['segment_id']=='P05':
   assert s['key']=='V02' and s['frames']==B-A
   s.update(key='G11-01',base_asset='G11-01',source=SOURCE,label=LABEL,changed_v02=True,file='assets/P05_G11-01_first.png',encoded_file='_work/P05_G11-01.mp4',art_boxes=[[80,110,1840,930]],camera_band=[110,930]);s.pop('render_config',None)
   s['texts']=header_records();s.pop('full_bleed',None);s['camera_direction']='coastline_to_plimouth'
   s.pop('sha256',None)
   if (ROOT/s['file']).exists():s['sha256']=sha(ROOT/s['file'])
  else:
   s['encoded_file']=str(OLD/s['encoded_file']);s['changed_v02']=False
   if s.get('file'):s['file']=str(OLD/s['file'])
 save(ROOT/'records/render_shots.json',shots)
 ids=[s['base_asset'] for s in shots if s.get('base_asset')];assert len(ids)==len(set(ids))==16 and 'V02' not in ids
 save(ROOT/'records/asset_usage_v02.json',{'assets':ids,'all_used_once':True,'originals':13,'ai_clips':3,'rejected_original_retained':str(OLD.parent/'素材/V02_Kling_v01.mp4')})
 for lang in ['en','ja']:
  p=OLD/f'deliverables/EP007_upload_info_{lang}.md';text=p.read_text()
  text=text.replace('V01–V04','V01, V03, V04').replace('V01-V04','V01, V03, V04')
  text=text.replace("Boston Public Library via Internet Archive — Mourt's Relation (1622), Good Newes (1624).", "Boston Public Library via Internet Archive — Mourt's Relation (1622), Good Newes (1624).\nBoston Public Library, Leventhal Map & Education Center — John Smith, New England, 1624 state, facsimile c. 1919.\n"+maprec['work_url'])
  text=text.replace('本人の試聴待ち。','本人の試聴OK（Claudeの修正依頼v02に記録）。').replace('AI映像の絵画的表現は未達のため確認事項。','V01・V03・V04は写実的な画風で採用。V02は地図へ差し替え。')
  text += '\n\n## v02 確定事項\n\nサムネ：B「NOT IN THE LETTER」（EP007_thumbnail_B.jpg）。\nP05はJohn Smithの地図G11-01に差し替え。AI動画はV01・V03・V04の3本。\n追加素材クレジット：Boston Public Library, Leventhal Map & Education Center（John Smith map, facsimile）。\nJohn Smith, New England, 1624 state — facsimile c. 1919.\n'
  (ROOT/'deliverables'/p.name).write_text(text)
 p=OLD/'deliverables/EP007_source_credits.md';text=p.read_text()+'\n\n## v02: G11-01 / P05\n\n'+SOURCE+'\n\n'+maprec['work_url']+'\n\n'+maprec['rights_statement']+'\n\nAI videos: V01, V03, V04 (Kling AI). V02 is not used in v02.\n';(ROOT/'deliverables'/p.name).write_text(text)
 print('V02 PREPARED',flush=True)

def render():
 plan=read(ROOT/'records/map_plan.json');im=Image.open(plan['source']['local_original']).convert('RGB');w,h=im.size
 start=np.array(plan['start_crop_normalized'])*[w,h,w,h];end=np.array(plan['end_crop_normalized'])*[w,h,w,h]
 bg=ImageEnhance.Brightness(ImageOps.fit(im.crop(tuple(start)),(1920,1080)).filter(ImageFilter.GaussianBlur(55))).enhance(.35)
 cmd=read(OLD/'records/encoding_method.json')['command'].copy();cmd[cmd.index('-pixel_format')+1]='rgb24';out=ROOT/'_work/P05_G11-01.mp4';cmd[-1:]=['-pix_fmt','yuv420p',str(out)]
 with (ROOT/'records/map_encode.log').open('w') as log:
  p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
  try:
   for n in range(B-A):
    t=n/(B-A-1);width=(start[2]-start[0])*((end[2]-end[0])/(start[2]-start[0]))**t;height=width*820/1760;c=(start[:2]+start[2:])/2*(1-t)+(end[:2]+end[2:])/2*t
    box=(c[0]-width/2,c[1]-height/2,c[0]+width/2,c[1]+height/2)
    art=im.transform((1760,820),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC);frame=bg.copy();frame.paste(art,(80,110));header(frame)
    if n in [0,(B-A-1)//2,B-A-1]:
     frame.resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/f'review/map_source_{n:03d}.jpg',quality=90,optimize=True)
     if n==0:frame.save(ROOT/'assets/P05_G11-01_first.png')
    p.stdin.write(frame.tobytes())
   p.stdin.close();assert p.wait()==0
  except BaseException:p.kill();p.wait();raise
 save(ROOT/'records/map_encoding.json',{'command':cmd,'sha256':sha(out),'frames':B-A})
 shots=read(ROOT/'records/render_shots.json');shot=next(s for s in shots if s['segment_id']=='P05');shot['sha256']=sha(ROOT/shot['file']);save(ROOT/'records/render_shots.json',shots)
 print('MAP RENDERED',flush=True)

def splice_file(old,replacement,out,record_name='splice'):
 import av
 a=av.open(str(old));b=av.open(str(replacement));sa=a.streams.video[0];sb=b.streams.video[0]
 assert sa.time_base==sb.time_base==Fraction(1,15360)
 ea,eb=sa.codec_context.extradata,sb.codec_context.extradata
 save(ROOT/f'records/{record_name}_codec_headers.json',{'v01_avcc_hex':ea.hex(),'replacement_avcc_hex':eb.hex(),'identical':ea==eb})
 assert ea==eb,'SPS/PPS differ; do not splice incompatible headers'
 def packets(c,s):return [p for p in c.demux(s) if p.dts is not None]
 aa=packets(a,sa);bb=packets(b,sb);assert len(aa)==TOTAL and len(bb)==B-A
 def naltypes(p):
  data=bytes(p);offset=0;types=[]
  while offset<len(data):size=int.from_bytes(data[offset:offset+4],'big');offset+=4;types.append(data[offset]&31);offset+=size
  assert offset==len(data);return types
 for frame in [A,B]:assert 5 in naltypes(next(p for p in aa if p.pts==frame*512)),('Boundary is not IDR',frame)
 assert 5 in naltypes(next(p for p in bb if p.pts==0))
 left=[p for p in aa if p.pts<A*512];right=[p for p in aa if p.pts>=B*512]
 for p in bb:p.pts+=A*512;p.dts+=A*512
 combined=left+bb+right;assert len(combined)==TOTAL and all(x.dts<y.dts for x,y in zip(combined,combined[1:]))
 with av.open(str(out),'w',options={'movflags':'+faststart','movie_timescale':'48000','video_track_timescale':'15360'}) as dest:
  stream=dest.add_stream_from_template(sa)
  for p in combined:p.stream=stream;dest.mux(p)
 a.close();b.close()
 save(ROOT/f'records/{record_name}_encoding_method.json',{'method':'Packet replacement at verified closed IDR boundaries; identical AVC SPS/PPS; all non-P05 encoded packets copied unchanged. No compressed shots with differing formats concatenated.','outside_packets_preserved':len(left)+len(right),'replacement_packets':len(bb),'total':TOTAL,'interval_frames_half_open':[A,B],'picture_master_sha256':sha(out)})

def splice():
 old=OLD/'deliverables/EP007_Thanksgiving_en_v01_1080p30.mp4';replacement=ROOT/'_work/P05_G11-01.mp4';out=ROOT/'_work/picture_master.mp4'
 splice_file(old,replacement,out)
 for lang in ['en','ja']:
  src=OLD/f'deliverables/EP007_Thanksgiving_{lang}_v01_1080p30.mp4';dst=ROOT/f'deliverables/EP007_Thanksgiving_{lang}_v02_1080p30.mp4'
  ff(['-i',out,'-i',src,'-map','0:v:0','-map','1:a:0','-map_metadata',1,'-metadata','comment=Quiet Origins EP007 v02; AI clips V01,V03,V04; P05 John Smith map facsimile.','-c','copy','-movie_timescale',48000,'-movflags','+faststart',dst]);assert stream_hash(src,'a')==stream_hash(dst,'a')
 print('V02 SPLICED AND PACKAGED',flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render','splice']);args=p.parse_args();globals()[args.stage]()
