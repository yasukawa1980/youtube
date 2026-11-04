"""Measure solid glyph/background contrast on frames decoded from the final video."""
import numpy as np
from PIL import Image,ImageColor
from wom11_produce import ROOT,read,save
from wom11_visuals import INK,BG

def luminance(rgb):
 x=np.array(rgb,dtype=float)/255;x=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4);return float(x@[.2126,.7152,.0722])
def main():
 shots=read(ROOT/'records/render_shots.json');rows=[]
 for i,s in enumerate(shots):
  if not s['key'].startswith('D_'):continue
  expected=np.array(Image.open(ROOT/s['file']).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)).astype(float)
  actual=np.array(Image.open(ROOT/f'_work/continuous_en/{i*3+3:03d}.png').convert('RGB')).astype(float)
  foreground=np.linalg.norm(expected-np.array(ImageColor.getrgb(INK)),axis=2)<4;bg=np.linalg.norm(expected-np.array(ImageColor.getrgb(BG)),axis=2)<2
  foreground[:100]=False;bg[:100]=False;foreground[600:]=False;bg[600:]=False
  assert foreground.sum()>100 and bg.sum()>100
  f=np.median(actual[foreground],axis=0);b=np.median(actual[bg],axis=0);lf,lb=luminance(f),luminance(b);ratio=(max(lf,lb)+.05)/(min(lf,lb)+.05);assert ratio>=4.5,(s['key'],ratio)
  rows.append({'key':s['key'],'final_frame':round(s['end']*30)-1,'foreground_rgb_median':f.tolist(),'background_rgb_median':b.tolist(),'contrast':ratio,'passed':True})
 save(ROOT/'records/encoded_card_contrast.json',{'passed':True,'method':'Final decoded last frame of each card, solid interior glyph and background masks from matched reference raster; 1280x720 inspection resolution','cards':rows});print('ENCODED CARD CONTRAST',min(x['contrast'] for x in rows),flush=True)
if __name__=='__main__':main()
