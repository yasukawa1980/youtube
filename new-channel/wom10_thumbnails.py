"""Two source-only typography composites, no image generation."""
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
from wom10_produce import ROOT,read,save,sha
from wom10_visuals import BOLD,BG,INK
def main():
 assets={a['id']:a for a in read(ROOT/'records/source_assets.json')['assets']};checks=[]
 designs=[('A','K01a',[300,650,3300,2338],['OLDER THAN','CHRISTMAS?'],[55,380],99),('B','K06a',[0,750,3500,2719],["THE SAINT'S",'DEVIL'],[620,380],95)]
 for option,key,crop,lines,xy,size in designs:
  original=Image.open(assets[key]['original_path']).convert('RGB')
  if option=='A':
   crop=[1270,500,2010,1550];im=ImageOps.fit(original.crop((180,1200,1100,2500)),(1280,720),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(28));face=original.crop(crop);face=face.resize((round(face.width*720/face.height),720),Image.Resampling.LANCZOS);im.paste(face,(1280-face.width,0));xy=[45,230];size=90
  else:im=original.crop(crop).resize((1280,720),Image.Resampling.LANCZOS)
  d=ImageDraw.Draw(im);f=ImageFont.truetype(BOLD,size)
  for j,line in enumerate(lines):d.text((xy[0],xy[1]+j*(size+12)),line,font=f,fill='#fff9e8',stroke_width=5,stroke_fill='#161b16')
  d.rectangle((0,654,1280,720),fill=BG);d.text((38,670),'QUIET ORIGINS',font=ImageFont.truetype(BOLD,34),fill=INK)
  out=ROOT/f'deliverables/EP010_thumbnail_{option}.jpg';im.save(out,quality=93,optimize=True);assert out.stat().st_size<1000000
  im.resize((168,95),Image.Resampling.LANCZOS).save(ROOT/f'review/thumbnail_{option}_168.jpg',quality=95)
  checks.append(dict(option=option,asset_id=key,crop_pixels=crop,native_max_scale=720/(crop[3]-crop[1]) if option=='A' else max(1280/(crop[2]-crop[0]),720/(crop[3]-crop[1])),pixels=[1280,720],bytes=out.stat().st_size,sha256=sha(out),text=' '.join(lines),composition='Face detail on source-derived blurred green field' if option=='A' else 'Single source crop'))
 sheet=Image.new('RGB',(336,124),BG);d=ImageDraw.Draw(sheet)
 for i,k in enumerate(['A','B']):sheet.paste(Image.open(ROOT/f'review/thumbnail_{k}_168.jpg'),(168*i,29));d.text((168*i+6,5),k,font=ImageFont.truetype(BOLD,18),fill=INK)
 sheet.save(ROOT/'deliverables/EP010_thumbnails_168_comparison.jpg',quality=95);save(ROOT/'records/thumbnails.json',checks);print('THUMBNAILS COMPLETE',flush=True)
if __name__=='__main__':main()
