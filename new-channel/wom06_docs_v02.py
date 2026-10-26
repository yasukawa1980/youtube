"""Only requested artwork credits change; v01 documents are preserved."""
import csv,json,re,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from wom06_revision_v02 import ROOT,OLD
from wom06_produce import read,save,sha

def main():
 shots=read(ROOT/'records/render_shots.json');used=read(ROOT/'records/visual_manifest.json')['unique_originals'];assets=read(ROOT/'records/source_assets.json')['assets'];z=next(a for a in assets if a['id']=='museo_Inv27_001')
 credits='# EP006 — Source image credits\n\n'
 for a in assets:
  if a['id'] not in used:continue
  credits+=f"## {a['id']} — {a['title']}\n\n{a['artist']}; {a['date']}; {a['museum']}; {a['accession']}.\n\n{a['object_url']}\n\nRights: {a['rights']}.\n{a.get('rights_url','')}\n\n"
 (ROOT/'deliverables/EP006_source_credits.md').write_text(credits.rstrip()+'\n')
 docs=[]
 for l in ['en','ja']:
  src=OLD/f'deliverables/EP006_upload_info_{l}.md';old=src.read_text();s=old.replace('Francis Frith (1858); ','')
  s='\n'.join(line for line in s.split('\n') if not any('/search/'+i in line for i in ['256761','286141']))
  s=s.replace('Archivio Museo Egizio — CC0\n','Archivio Museo Egizio — CC0\nC. & G. Zangaki, Inv27_001 (1870).\n'+z['object_url']+'\n')
  assert s.split('Image credits\n')[0]==old.split('Image credits\n')[0]
  assert s.split('Wellcome Collection via')[1]==old.split('Wellcome Collection via')[1]
  dst=ROOT/f'deliverables/EP006_upload_info_{l}.md';dst.write_text(s);docs.append({'name':dst.name,'sha256':sha(dst),'only_artwork_credit_changes':True,'production_memo_preserved_verbatim_from_v01':True})
 usage=[]
 for a in assets:
  matches=[s for s in shots if s.get('base_asset')==a['id'] or a['id'] in s.get('base_assets',[])]
  assert len(matches)<=1
  usage.append({'id':a['id'],'uses':len(matches),'segments':','.join(s['segment_id'] for s in matches),'status':'used' if matches else 'reserve','sha256':a.get('sha256','not downloaded')})
 with (ROOT/'deliverables/EP006_asset_usage_v02.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(usage[0]));w.writeheader();w.writerows(usage)
 save(ROOT/'records/asset_usage_v02.json',{'passed':True,'unique_originals':18,'assets':usage,'optional_met_255796_used':False,'reason':'Figure too small and low contrast; met_247343 alone fills P09.'})
 save(ROOT/'records/credit_revision.json',{'passed':True,'documents':docs,'removed':['met_286141','met_256761'],'added':['museo_Inv27_001'],'end_screen':'v01 only lists collections, not individual artworks/artists/accessions. Those collections remain correct, so the screen is unchanged.'})
 early=[s for s in shots if s['segment_id'] in ['P01','P02','P03']];sheet=Image.new('RGB',(1280,760),'#0c1820');d=ImageDraw.Draw(sheet)
 for i,s in enumerate(early):
  x=(i%3)*426;y=(i//3)*370;im=Image.open(s['file']).convert('RGB');sheet.paste(im.resize((426,240)),(x,y));d.text((x+8,y+250),s['segment_id']+' '+s['key'],font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',14),fill='white')
 sheet.save(ROOT/'review/P01_P03_composition_comparison.jpg',quality=88,optimize=True)
 sections=[]
 for l,title in [('en','English'),('ja','日本語')]:
  sections.append(f'<h2>{title}・字幕入り確認版</h2><video controls preload="metadata" src="EP006_Sphinx_{l}_v02_subtitled_review_1080p30.mp4"></video><p><a href="EP006_Sphinx_{l}_v02_1080p30.mp4">字幕なし本編</a> · <a href="EP006_Sphinx_{l}_v02_1080p30.srt">SRT</a></p>')
 html='<!doctype html><html lang="ja"><meta charset="utf-8"><title>EP006 Sphinx v02</title><style>body{max-width:1100px;margin:40px auto;padding:0 24px;background:#0c1820;color:#eee8dc;font:17px/1.7 system-ui}a{color:#b9d4e5}video,img{width:100%}h1,h2{color:#d8b575}</style><h1>Quiet Origins · Sphinx v02</h1><p>英日共通 365.166667秒。投稿・公開はしていません。6区間を修正、音声・字幕はv01と同一です。</p>'+''.join(sections)+'<h2>サムネ3案・168px比較</h2><img src="wom06_サムネ168px比較_20261027.jpg">'+''.join(f'<h3>案{i}</h3><img src="wom06_サムネ案{i}_20261027.jpg">' for i in [1,2,3])+'</html>'
 (ROOT/'deliverables/preview.html').write_text(html)
 print('CREDITS AND PREVIEW READY',flush=True)
if __name__=='__main__':main()
