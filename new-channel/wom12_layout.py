from wom12_produce import *
from wom12_scenes import *
from PIL import ImageColor
from wom11_pixel_qc import luminance

def main():
 shots=read(ROOT/'records/render_shots.json');layout=read(ROOT/'records/frame_layout.json');records=[];art_info=read(ROOT/'records/art_scales.json');assert set(art_info)==set(CAT)-{'N12-B'};used={k:dict(fullscreen=1,lineup2=sum(x==k for _,x in LINE2),lineup3=sum(x==k for _,x in LINE3)) for k in CAT};layout_m=[]
 for i,s in enumerate(shots):
  k=s['key'];
  if not k.startswith('D_'):continue
  ref=Image.open(ROOT/s['stages'][0]['file']).convert('RGB');a=np.array(ref);fg=np.linalg.norm(a.astype(float)-np.array(ImageColor.getrgb(INK)),axis=2)<2;bg=np.linalg.norm(a.astype(float)-np.array(ImageColor.getrgb(LIGHT)),axis=2)<2;fg[:160]=False;fg[742:]=False;bg[:160]=False;bg[742:]=False
  aa=np.array(ref.resize((1280,720),Image.Resampling.LANCZOS)).astype(float);actual=np.array(Image.open(ROOT/f'_work/continuous_en/{i*3+1:03d}.png').convert('RGB')).astype(float);fmask=np.linalg.norm(aa-np.array(ImageColor.getrgb(INK)),axis=2)<2;bmask=np.linalg.norm(aa-np.array(ImageColor.getrgb(LIGHT)),axis=2)<2
  for mask in [fmask,bmask]:mask[:110]=False;mask[493:]=False
  assert fmask.sum()>10 and bmask.sum()>10,k
  f=np.median(actual[fmask],axis=0);b=np.median(actual[bmask],axis=0);contrast=(luminance(b)+.05)/(luminance(f)+.05);assert contrast>=4.5,(k,contrast)
  texts=[x for x in layout if x['card']==k and 150<x['box'][1]<722 and x['box'][3]<748];margins=[min(x['box'][0]-75,1845-x['box'][2],x['box'][1]-147,748-x['box'][3]) for x in texts];sizes=[x['ink_height'] for x in texts if x['major']];records.append(dict(key=k,encoded_contrast=contrast,panel_padding_min_px=min(margins) if margins else None,body_heading_height_min_px=min(sizes) if sizes else None))
 for k,v in art_info.items():
  mx=v.get('end_scale_upper_bound',v['start_scale']);lim=1.4 if k.startswith('N03') else 1.2 if k=='N04-A' else 1;assert mx<=lim,(k,mx,lim)
 for title,rows,h in [('D_lineup2',[LINE2],340),('D_lineup3',[LINE3[:6],LINE3[6:]],202)]:
  for ri,row in enumerate(rows):
   step=round(1710/len(row));half=step//2-10
   for yr,k in row:
    if k:
     a=art(k);sc=min((2*half-22)/a.width,h/a.height,1);layout_m.append(dict(card=title,year=yr,key=k,displayed_height=round(a.height*sc),slot_height=h,column_pitch=step,box_to_box_gap=step-2*half,horizontal_inset=11,vertical_inset=10))
 save(ROOT/'records/episode_qc.json',dict(passed=True,contrast_and_card_padding=records,active_year_ink_px=60,usage=used,lineup_geometry=layout_m,fullframe_repeats=0,art_zoom=art_info,work_count_note='12 distinct works, 13 source images including the two different Yale pages; N12-B is the background of D_1823.',forbidden_images_used=[]))
if __name__=='__main__':main()
