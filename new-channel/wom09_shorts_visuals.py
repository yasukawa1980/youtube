"""EP009承認済み7資料を縦へ配置。原寸倍率・出典・カメラを記録する。"""
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageFilter,ImageEnhance,ImageFont

def build(ctx):
 ROOT,MAIN,read,save,sha,font,FPS=[ctx[k] for k in ['ROOT','MAIN','read','save','sha','font','FPS']]
 (ROOT/'assets').mkdir(exist_ok=True)
 main={s['key']:s for s in read(MAIN/'records/render_shots.json')};raw={a['key']:a for a in read(MAIN/'records/source_assets.json')['assets']}
 specs={'T1':[('met_202259',None),('D_lastline','In one old translation'),('met_247952','The wooden horse appears later')],'T2':[('MYK01',None)],'T3':[('R04',None),('D_gifts','This famous warning is not from Homer'),('R01','There the Trojan priest')]}
 shots=[];assets={};hooks=[]
 BG='#e8d9b7';INK='#3b2c21';ACCENT='#5a3a1a'
 def wrap(text,size,width,serif=False):
  f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia.ttf',size) if serif else font(size,text)
  out=[];line=''
  for w in text.split():
   test=(line+' '+w).strip()
   if f.getlength(test)>width and line:out.append(line);line=w
   else:line=test
  if line:out.append(line)
  return out,f
 for row in read(ROOT/'records/shorts.json')['shorts']:
  sid=row['id'];hooks.append(ctx['headline'](sid));starts=[0 if phrase is None else ctx['phrase_frame'](row,phrase) for aid,phrase in specs[sid]]
  for i,(aid,phrase) in enumerate(specs[sid]):
   m=main[aid];crop=None;cardtexts=[]
   if aid.startswith('D_'):
    source=MAIN/m['file'];im=Image.open(source);piece=Image.new('RGB',(1020,860),BG);d=ImageDraw.Draw(piece)
    quote=' '.join(t['text'] for t in m['text_boxes'] if t.get('font_style')=='serif' and t['font_size']>70)
    expected={'D_lastline':'"Thus held they funeral for Hector tamer of horses."','D_gifts':'"I fear the Grecians even when they offer gifts."'}[aid];assert quote==expected
    lines,f=wrap(quote,72,900,True);y=145
    for line in lines:
     x=(1020-f.getlength(line))/2;d.text((x,y),line,font=f,fill=INK);cardtexts.append(dict(text=line,bbox=list(d.textbbox((x,y),line,font=f))));y+=100
    if aid=='D_gifts':
     val='timeo Danaos et dona ferentes';f=ImageFont.truetype('/System/Library/Fonts/Supplemental/Georgia.ttf',38);x=(1020-f.getlength(val))/2;d.text((x,y+65),val,font=f,fill=INK);cardtexts.append(dict(text=val,bbox=list(d.textbbox((x,y+65),val,font=f))))
    label=m['text_boxes'][0]['text'];source_text=m['text_boxes'][1]['text'];note=None;scale=1;original_size=im.size
   else:
    source=Path(raw[aid]['path']);im=Image.open(source).convert('RGB');assert sha(source)==m['original_sha256'];original_size=im.size
    if aid.startswith('R'):im=ImageOps.colorize(ImageOps.autocontrast(ImageOps.grayscale(im),cutoff=.5),black='#443422',white='#f1e4c7')
    # First prints focus on the wooden horse, not the nearby people.
    norm={'met_202259':(.22,.08,.75,.99),'R04':(.48,.17,.84,.97)}.get(aid,(0,0,1,1))
    crop=[round(v*d) for v,d in zip(norm,[im.width,im.height]*2)];piece=im.crop(crop)
    label,source_text,note=m['source_text'];scale=1
   blur=ImageEnhance.Brightness(ImageOps.fit(piece,(1080,1920)).filter(ImageFilter.GaussianBlur(45))).enhance(.4)
   zoom=1.08 if i==0 else 1.03
   if aid=='MYK01':
    # Preserve the complete horse at the start; 990x885 cannot fill 80% portrait height without cropping it.
    fit=ImageOps.contain(piece,(1020,1300),Image.Resampling.LANCZOS);x=(1080-fit.width)//2;y=295;scale=max(fit.width/piece.width,fit.height/piece.height);base=blur;base.paste(fit,(x,y));viewport=[0,270,1080,1200]
   elif i==0:
    scale=min(1080/piece.width,1760/piece.height,1.6/zoom)
    fit=piece.resize((round(piece.width*scale),round(piece.height*scale)),Image.Resampling.LANCZOS);x=(1080-fit.width)//2;y=(1920-fit.height)//2;base=blur;base.paste(fit,(x,y));viewport=[0,0,1080,1920]
   else:
    fit=ImageOps.contain(piece,(1020,830),Image.Resampling.LANCZOS);x=(1080-fit.width)//2;y=270+(860-fit.height)//2;scale=max(fit.width/piece.width,fit.height/piece.height);base=blur;base.paste(fit,(x,y));viewport=[0,270,1080,860]
   box=[x,y,x+fit.width,y+fit.height];assert scale*zoom<=1.601,(aid,scale)
   header=Image.new('RGBA',(1080,1920));d=ImageDraw.Draw(header);d.rectangle((0,120,1079,269),fill=BG);texts=[]
   lines=[(140,'QUIET ORIGINS / EP009',21),(167,label,22)]
   wrapped,_=wrap(source_text,17,920);assert len(wrapped)<=2
   lines.extend((197+21*j,t,17) for j,t in enumerate(wrapped))
   if note:lines.append((197+21*len(wrapped),note,17))
   for yy,val,size in lines:
    f=font(size,val);b=d.textbbox((80,yy),val,font=f);assert 140<=b[1]<b[3]<=260 and b[2]<=1000,(aid,b)
    d.text((80,yy),val,font=f,fill=INK);texts.append(dict(text=val,bbox=list(b),font_size=size))
   hp=ROOT/f'assets/{sid}_{aid}_header.png';header.save(hp);out=ROOT/f'assets/{sid}_{aid}.png';base.save(out)
   stop=starts[i+1] if i+1<len(starts) else row['frames'];assert stop-starts[i]>=45
   meta=dict(id=aid,path=str(source),sha256=sha(source),kind='card' if aid.startswith('D_') else 'image',label=label,source=source_text,original_pixels=list(original_size),native_initial_scale=scale,native_max_scale=scale*zoom)
   assets[aid]=meta
   shot=dict(short_id=sid,asset_id=aid,start_frame=starts[i],end_frame=stop,frames=stop-starts[i],file=str(out),sha256=sha(out),header_file=str(hp),source=meta,texts=texts,art_box=box,source_crop_pixels=crop,zoom_start=1.,zoom_end=zoom,viewport=viewport,cut_phrase=phrase,cut_word_seconds=None if phrase is None else next(w['start'] for w in row['words_timed'] if round(w['start']*FPS)==starts[i]),foreground_height_fraction=fit.height/1920 if i==0 else None,card_texts=cardtexts)
   if aid=='MYK01':
    shot['camera_cues']=[dict(phrase=p,frame=ctx['phrase_frame'](row,p)) for p in ['The horse stands on wheels','small windows show the faces']]
    shot['source']['native_max_scale']=scale*1.5
    shot['camera_phases']='冒頭0–2.3秒で1.00→1.08。その後は同一ショット内で1.50まで継続し、語の開始から脚元、窓へ緩やかに移動。原寸最大1.546倍。'
   shots.append(shot)
 assert len(shots)==7 and len(assets)==7 and len({s['source']['sha256'] for s in shots})==7
 save(ROOT/'records/visual_manifest.json',dict(shots=shots,assets=assets,same_source_not_repeated=True));save(ROOT/'records/headlines.json',hooks)
 print('EP009 VISUALS',len(shots),flush=True)
