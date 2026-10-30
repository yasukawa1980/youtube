"""EP008の9資料を縦へ配置。本編の色調・札・出典を継承し、新聞は許可した記事内だけを使う。"""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageOps,ImageFilter,ImageEnhance,ImageFont

def build(ctx):
 ROOT,MAIN,read,save,sha,font,FPS=[ctx[k] for k in ['ROOT','MAIN','read','save','sha','font','FPS']]
 shots_main={s['key']:s for s in read(MAIN/'records/render_shots.json')};raw={a['id']:a for a in read(MAIN/'records/source_assets.json')['assets']};colors={a['id']:a for a in read(MAIN/'records/color_assets_v02.json')['assets'] if a['selected']}
 v02=MAIN.parent/'確認版_v02_20261030';v01=MAIN.parent/'確認版_v01_20261029';(ROOT/'assets').mkdir(exist_ok=True)
 specs={'K1':[('B286',None),('B313','What the tomb does hold'),('B312','One alabaster cup wishes')],'K2':[('N03',None),('N02','They quoted Arthur Conan Doyle'),('N01','The curse story grew')],'K3':[('C01',None),('D_novels_1869','In 1869'),('B157','That was more than fifty years before')]}
 BG='#0c1820';GOLD='#d8b575';IVORY='#f4efdf';hooks=[];shots=[];assets={}
 # Every newspaper foreground and background comes from these exact main-film approved columns.
 approved={'N01':[.309,.144,.438,.716],'N02':[.278,.160,.414,.754],'N03':[.598,.098,.723,.985]}
 used_news={'N03':[.598,.098,.723,.264],'N02':[.278,.594,.414,.754],'N01':[.309,.144,.438,.221]}
 def rect(im,b):return [round(v*dim) for v,dim in zip(b,[im.width,im.height,im.width,im.height])]
 def wrap(d,text,size,width):
  f=font(size,text);result=[];line=''
  for word in text.split():
   val=(line+' '+word).strip()
   if d.textlength(val,font=f)>width and line:result.append(line);line=word
   else:line=val
  if line:result.append(line)
  return result
 def oldpath(m):return MAIN/Path(m['file'])
 for row in read(ROOT/'records/shorts.json')['shorts']:
  sid=row['id'];hooks.append(ctx['headline'](sid));starts=[0 if phrase is None else ctx['phrase_frame'](row,phrase) for aid,phrase in specs[sid]]
  for i,(aid,phrase) in enumerate(specs[sid]):
   m=shots_main[aid];crop=None;norm=None;diagram=None;first_height=1.0;source_meta=None
   if aid.startswith('N'):
    source=Path(raw[aid]['path']);assert sha(source)==raw[aid]['sha256'];im=Image.open(source).convert('RGB');norm=used_news[aid];crop=rect(im,norm);piece=im.crop(crop)
    a=np.asarray(piece,dtype=float)/255.;piece=Image.fromarray(np.uint8(np.rint(a**.95*255)))
    if aid=='N03':first_height=1590/1920
    if aid=='N02':
     # Two excerpts of one article: Doyle's claim and Budge's rebuttal, no adjacent columns.
     fullrect=rect(im,approved[aid]);col=im.crop(fullrect);piece=Image.new('RGB',(720,820),'#eeeeee');diagram=[]
     for b,y,maxh in [([0,2435,col.width,2800],10,445),([0,1950,col.width,2225],475,335)]:
      patch=col.crop(b);arr=np.asarray(patch,dtype=float)/255.;patch=Image.fromarray(np.uint8(np.rint(arr**.95*255)));patch=ImageOps.contain(patch,(680,maxh),Image.Resampling.LANCZOS);x=(720-patch.width)//2;piece.paste(patch,(x,y));diagram.append({'source':[b[0]+fullrect[0],b[1]+fullrect[1],b[2]+fullrect[0],b[3]+fullrect[1]],'destination':[x,y,x+patch.width,y+patch.height]})
     crop=[fullrect[0],fullrect[1]+1950,fullrect[2],fullrect[1]+2800];norm=[crop[0]/im.width,crop[1]/im.height,crop[2]/im.width,crop[3]/im.height]
    bounds=approved[aid];assert bounds[0]<=norm[0]<norm[2]<=bounds[2] and bounds[1]<=norm[1]<norm[3]<=bounds[3]
    source_meta=raw[aid]
   elif aid=='C01':
    source=Path(colors[aid]['original_path']);assert sha(source)==colors[aid]['sha256'];im=Image.open(source).convert('RGB');first_height=.84
    h=im.height;w=round(h*1080/(1920*first_height));crop=[im.width-w,0,im.width,h];piece=im.crop(crop);source_meta=colors[aid]
   elif aid=='D_novels_1869':
    source=oldpath(m);assert sha(source)==m['sha256'];im=Image.open(source).convert('RGB');piece=Image.new('RGB',(1020,820),'#e8d9b7');diagram=[]
    texts=m['body_texts'];assert len(texts)==4
    def patch(b,y,maxw=940,maxh=100):
     q=im.crop(b);q=ImageOps.contain(q,(maxw,maxh),Image.Resampling.LANCZOS);x=(1020-q.width)//2;piece.paste(q,(x,y));diagram.append({'source':b,'destination':[x,y,x+q.width,y+q.height]})
    def padded(b):return [math.floor(b[0])-5,math.floor(b[1])-5,math.ceil(b[2])+5,math.ceil(b[3])+5]
    patch(padded(texts[0]['bbox']),35,900,70)
    b=padded(texts[1]['bbox']);f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia.ttf',69);split=round(texts[1]['bbox'][0]+f.getlength('Lost in a Pyramid; or,')+f.getlength(' ')/2)
    patch([b[0],b[1],split,b[3]],165,940,105);patch([split,b[1],b[2],b[3]],300,940,105)
    patch(padded(texts[2]['bbox']),455,900,70);patch(padded(texts[3]['bbox']),565,940,80)
    assert max(p['source'][3] for p in diagram)<475
   else:
    source=v02/f'assets/{aid}_toned.png';im=Image.open(source).convert('RGB');piece=im
    if aid=='B286':
     h=im.height;w=round(h*1080/1920);x=im.width-w;crop=[x,0,x+w,h];piece=im.crop(crop)
    source_meta=raw[aid]
   blur=ImageEnhance.Brightness(ImageOps.fit(piece,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.355)
   if i==0:
    if first_height==1:
     base=ImageOps.fit(piece,(1080,1920),Image.Resampling.LANCZOS);box=[0,0,1080,1920]
    else:
     fit=ImageOps.contain(piece,(1080,round(1920*first_height)),Image.Resampling.LANCZOS);x=(1080-fit.width)//2;y=330 if aid=='N03' else (1920-fit.height)//2;base=blur;base.paste(fit,(x,y));box=[x,y,x+fit.width,y+fit.height]
    viewport=[0,0,1080,1920]
   else:
    base=blur;fit=ImageOps.contain(piece,(1020,820),Image.Resampling.LANCZOS);x=(1080-fit.width)//2;y=270+(860-fit.height)//2;base.paste(fit,(x,y));box=[x,y,x+fit.width,y+fit.height];viewport=[0,270,1080,860]
   header=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(header);d.rectangle((0,120,1079,269),fill=BG);texts=[]
   label=m['label'];source_text=m['source'] or m['texts'][2]['text'];note=[t['text'] for t in m.get('texts',[]) if aid=='C01' and t['bbox'][1]>=110]
   lines=[(140,'QUIET ORIGINS / EP008',21,GOLD),(169,label,22,GOLD)]
   sources=wrap(d,source_text,17,920);assert len(sources)<=2,(aid,sources)
   lines.extend((198+j*22,t,17,IVORY) for j,t in enumerate(sources));y=198+len(sources)*22
   for val in note:
    size=17
    while d.textlength(val,font=font(size,val))>920:size-=1
    assert size>=14
    lines.append((y,val,size,IVORY));y+=size+4
   for y,val,size,color in lines:
    while d.textlength(val,font=font(size,val))>920:size-=1
    f=font(size,val);b=d.textbbox((80,y),val,font=f);assert 140<=b[1]<b[3]<=260 and b[2]<=1000,(aid,val,b)
    d.text((80,y),val,font=f,fill=color);texts.append({'text':val,'bbox':list(b),'font_size':size})
   hp=ROOT/f'assets/{sid}_{aid}_header.png';header.save(hp);out=ROOT/f'assets/{sid}_{aid}.png';base.save(out)
   source_rec={'id':aid,'path':str(source),'sha256':sha(source),'kind':'image','label':label,'source':source_text,'main_source_file':str(oldpath(m)),'main_source_sha256':m['sha256']}
   if source_meta:source_rec['original_record']=source_meta
   assets[aid]=source_rec
   stop=starts[i+1] if i+1<len(starts) else row['frames'];assert stop-starts[i]>=45,(sid,aid,starts,stop)
   wordtime=None if phrase is None else next(w['start'] for w in row['words_timed'] if round(w['start']*FPS)==starts[i])
   shots.append({'short_id':sid,'asset_id':aid,'start_frame':starts[i],'end_frame':stop,'frames':stop-starts[i],'file':str(out),'sha256':sha(out),'header_file':str(hp),'source':source_rec,'texts':texts,'art_box':box,'source_crop_pixels':crop,'source_crop_normalized':norm,'approved_main_newspaper_crop':approved.get(aid),'background_also_uses_only_crop':True,'zoom_start':1.,'zoom_end':1.08 if i==0 else 1.03,'viewport':viewport,'cut_phrase':phrase,'cut_word_seconds':wordtime,'foreground_height_fraction':(box[3]-box[1])/1920 if i==0 else None,'diagram_layout':diagram,'no_1892_row':aid=='D_novels_1869'})
 assert len(shots)==9 and len(assets)==9 and len({s['source']['sha256'] for s in shots})==9
 save(ROOT/'records/visual_manifest.json',{'shots':shots,'assets':assets,'same_source_not_repeated':True});save(ROOT/'records/headlines.json',hooks)
 print('EP008 VISUALS',len(shots),flush=True)
