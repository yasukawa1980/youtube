"""Source-image typography composites for two requested thumbnails; no image generation."""
from PIL import Image,ImageDraw,ImageFont
from wom09_produce import ROOT,read,save,sha
from wom09_visuals import BG,INK,BOLD

def main():
 assets={a['key']:a for a in read(ROOT/'records/source_assets.json')['assets']};checks=[]
 for option,key,lines in [('A','met_202259',['NOT IN','THE ILIAD']),('B','MYK01',['THE OLDEST','TROJAN','HORSE?'])]:
  im=Image.new('RGB',(1280,720),BG);a=Image.open(assets[key]['path']).convert('RGB');scale=min(720/a.height,1);a=a.resize((round(a.width*scale),round(a.height*scale)),Image.Resampling.LANCZOS);x=1280-a.width;im.paste(a,(x,0));d=ImageDraw.Draw(im)
  size=88 if option=='A' else 76;f=ImageFont.truetype(BOLD,size);y=200 if option=='A' else 150
  for line in lines:
   d.text((36,y),line,font=f,fill=INK,stroke_width=4,stroke_fill=BG);y+=size+19
  d.rectangle((0,654,1280,720),fill=BG);d.text((38,671),'QUIET ORIGINS',font=ImageFont.truetype(BOLD,33),fill=INK)
  out=ROOT/f'deliverables/EP009_thumbnail_{option}.jpg';im.save(out,quality=93,optimize=True);assert out.stat().st_size<1000000
  small=im.resize((168,95),Image.Resampling.LANCZOS);small.save(ROOT/f'review/thumbnail_{option}_168.jpg',quality=95)
  checks.append({'option':option,'asset_id':key,'native_source_scale':scale,'pixels':[1280,720],'bytes':out.stat().st_size,'sha256':sha(out),'text':' '.join(lines)})
 sheet=Image.new('RGB',(336,124),BG);d=ImageDraw.Draw(sheet)
 for i,k in enumerate(['A','B']):sheet.paste(Image.open(ROOT/f'review/thumbnail_{k}_168.jpg'),(168*i,29));d.text((168*i+6,5),k,font=ImageFont.truetype(BOLD,18),fill=INK)
 sheet.save(ROOT/'deliverables/EP009_thumbnails_168_comparison.jpg',quality=95)
 save(ROOT/'records/thumbnails.json',checks)
 print('THUMBNAILS COMPLETE',flush=True)
if __name__=='__main__':main()
