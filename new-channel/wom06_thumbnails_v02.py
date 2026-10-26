"""Requested full-bleed thumbnails. Original generated images remain untouched."""
import importlib.util,json,shutil,math,datetime
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
from wom06_revision_v02 import ROOT
from wom06_produce import REPO,save,sha
spec=importlib.util.spec_from_file_location('style',Path(__file__).with_name('wom02_サムネ改善_20261026.py'));style=importlib.util.module_from_spec(spec);spec.loader.exec_module(style)
DEST=REPO/'new-channel/サムネ確認用/wom06'
def main():
 DEST.mkdir(parents=True,exist_ok=True);(ROOT/'thumbnail_sources').mkdir(exist_ok=True)
 prompts=json.loads((REPO/'new-channel/wom06_サムネ生成プロンプト_v02_20261026.json').read_text());sources={}
 for r in prompts['prompts']:
  src=Path(r['file']);dst=ROOT/'thumbnail_sources'/f'{r["id"]}.png';shutil.copy2(src,dst);sources[r['id']]=dst
  r.update(saved_original=str(dst),sha256=sha(dst),generation_date_jst=datetime.datetime.fromtimestamp(src.stat().st_mtime,datetime.timezone(datetime.timedelta(hours=9))).isoformat())
 save(ROOT/'records/thumbnail_generation.json',prompts)
 # Subject rectangles are conservative bounds inspected on resized images, including spare margins.
 specs=[('scene1',[('NO',54,145,250),('RIDDLE',54,301,565)],"Egypt's Sphinx",476,{'face_and_headdress':[770,25,1255,440]}),('scene2',[('TWO',54,90,330),('SPHINXES',54,246,650)],'Only one asked a riddle',540,{'face_and_headdress':[725,40,1280,525],'greek_winged_silhouette':[174,407,345,501]}),('scene1',[('NEVER ASKED',54,145,650),('A RIDDLE',54,301,560)],"Egypt's Sphinx",476,{'face_and_headdress':[770,25,1255,440]})]
 files=[];checks=[]
 for i,(key,lines,caption,cy,guards) in enumerate(specs,1):
  im=style.gradient(ImageOps.fit(Image.open(sources[key]).convert('RGB'),(1280,720),Image.Resampling.LANCZOS),.69,.63)
  mask=Image.new('RGB',(1280,720),'black')
  boxes=[]
  for text,x,y,w in lines:
   style.headline(im,text,(x,y),w);style.headline(mask,text,(x,y),w)
   # Raster layer bounds include its anti-aliased edges and offset shadow.
   boxes.append([x,y,x+w+2,y+135])
  d=ImageDraw.Draw(im);d.text((58,cy),caption,font=ImageFont.truetype(style.SERIF,33),fill=style.GOLD,stroke_width=1,stroke_fill='#141519');d.text((80,615),'QUIET ORIGINS',font=ImageFont.truetype(style.SANS,22),fill=style.GOLD)
  gaps=[]
  for box in boxes:
   for name,g in guards.items():
    dx=max(g[0]-box[2],box[0]-g[2],0);dy=max(g[1]-box[3],box[1]-g[3],0);gaps.append({'text_bounds':box,'subject':name,'subject_bounds':g,'minimum_clearance_px':math.hypot(dx,dy)})
  minimum=min(x['minimum_clearance_px'] for x in gaps);assert minimum>=16
  name=f'wom06_サムネ案{i}_20261027.jpg';path=DEST/name;im.save(path,quality=94,optimize=True,subsampling=0);assert path.stat().st_size<1_000_000;shutil.copy2(path,ROOT/'deliverables'/name);files.append(path)
  proof=im.copy();d=ImageDraw.Draw(proof)
  for b in boxes:d.rectangle(b,outline='cyan',width=2)
  for b in guards.values():d.rectangle(b,outline='yellow',width=2)
  proof.save(ROOT/f'review/thumbnail_{i}_clearance.jpg',quality=90,optimize=True)
  checks.append({'option':i,'path':str(path),'size':[1280,720],'bytes':path.stat().st_size,'sha256':sha(path),'minimum_conservative_clearance_px':minimum,'clearance_measurements':gaps,'measurement_method':'Distance between complete headline raster+shadow rectangles and manually inspected conservative subject rectangles; actual visible glyph clearance is at least this value.','face_eyes_outside_duration_badge_rectangle':[1110,650,1280,720],'font':style.SERIF,'headline_raster_height':132,'brand_xy':[80,615],'brand_font_px':22})
 refs=[REPO/'new-channel/サムネ確認用/wom02/wom02_サムネ案1_v02_20261026.jpg',REPO/'new-channel/サムネ確認用/wom04/wom04_サムネ案3_v02_20261027.jpg']
 sheet=Image.new('RGB',(936,150),'#15191e');d=ImageDraw.Draw(sheet)
 for i,(f,label) in enumerate(zip(files+refs,['案1：NO RIDDLE','案2：TWO SPHINXES','案3：NEVER ASKED','参考：第2話 現行','参考：第4話 現行'])):
  x=16+i*184;d.text((x,8),label,font=ImageFont.truetype(style.JP,12),fill='white');sheet.paste(Image.open(f).convert('RGB').resize((168,94),Image.Resampling.LANCZOS),(x,35))
 comp=DEST/'wom06_サムネ168px比較_20261027.jpg';sheet.save(comp,quality=95,optimize=True,subsampling=0);shutil.copy2(comp,ROOT/'deliverables'/comp.name)
 save(ROOT/'records/thumbnail_qc.json',{'passed':True,'date':'2026-10-27','outputs':checks,'comparison':str(comp),'comparison_cell_px':[168,94],'references':[{'path':str(p),'sha256':sha(p)} for p in refs],'no_youtube_changes':True,'recommendation':'案1。NO RIDDLEと大スフィンクスの顔が168pxでも明瞭。題名と組み合わせれば、エジプトのスフィンクスと謎かけの誤解を扱う話と伝わる。単体では背景説明が少なく、案3は明確だが文字が詰まる。案2は対比が見えるが視線が分散する。'})
 print('THUMBNAILS',[(r['option'],r['bytes'],r['minimum_conservative_clearance_px']) for r in checks],flush=True)
if __name__=='__main__':main()
