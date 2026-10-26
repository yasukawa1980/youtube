"""形状・文字は維持し、右側の石彫の夕日だけを非生成で調整。"""
import importlib.util
import io
import json
import shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',ROOT/'wom02_サムネ改善_20261026.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
OUT=ROOT/'サムネ確認用/wom03'
MEDIA=Path('/Users/ryo/Desktop/新チャンネル/EP003_Medusa/サムネ改善_20261027')

def compose(bg):
    im=v.gradient(bg,.69,.63)
    for y,text,w in [(145,'WHICH',410),(301,'MEDUSA?',540)]:v.headline(im,text,(54,y),w)
    d=ImageDraw.Draw(im)
    d.text((58,476),'Monster or Victim?',font=ImageFont.truetype(v.SERIF,33),fill=v.GOLD,stroke_width=1,stroke_fill='#141519')
    d.text((80,615),'QUIET ORIGINS',font=ImageFont.truetype(v.SANS,22),fill=v.GOLD)
    return im

def run():
    src=MEDIA/'sources/案1案3_左右の浮き彫り_原寸.png'
    bg=ImageOps.fit(Image.open(src).convert('RGB'),(1280,720));a=np.array(bg,dtype=float)
    y,x=np.mgrid[:720,:1280]
    mask=np.clip((x-630)/55,0,1)*np.clip((650-y)/30,0,1)
    direction=.72+.28*np.clip((x-630)/650,0,1)*(1-y/720)
    luma=a@np.array([.2126,.7152,.0722])
    light=np.clip((luma-40)/150,0,1)
    target=a+(255-a)*light[:,:,None]*np.array([.25,.13,.015])*direction[:,:,None]
    target[:,:,2]-=a[:,:,2]*light*.055
    target*=1-(1-light[:,:,None])*.035
    b=np.rint(a+(target-a)*mask[:,:,None]).astype('uint8')
    adjusted=Image.fromarray(b);old=compose(bg);new=compose(adjusted)
    prior=OUT/'wom03_サムネ案1_20261027.jpg'
    buf=io.BytesIO();old.save(buf,format='JPEG',quality=94,optimize=True,subsampling=0)
    assert buf.getvalue()==prior.read_bytes()
    allowed=mask>0;diff=np.any(b!=a,axis=2);finaldiff=np.any(np.array(old)!=np.array(new),axis=2)
    assert not diff[~allowed].any() and not finaldiff[~allowed].any()
    white_before=np.all(a>=250,axis=2);white_after=np.all(b>=250,axis=2)
    new_white=int(np.count_nonzero(white_after & ~white_before));assert new_white==0
    p=OUT/'wom03_サムネ案1_v02_20261027.jpg';new.save(p,quality=94,optimize=True,subsampling=0);assert p.stat().st_size<1000000
    (MEDIA/'v02').mkdir(exist_ok=True)
    for im,name in [(bg,'背景_調整前.png'),(adjusted,'背景_夕日調整後.png'),(Image.fromarray(np.rint(mask*255).astype('uint8')),'夕日_調整マスク.png'),(new,'完成_圧縮前.png')]:im.save(MEDIA/'v02'/name)
    # 上段は顔の560×560pxを等倍、下段は各168×94px。
    sheet=Image.new('RGB',(1160,760),'#15191e');d=ImageDraw.Draw(sheet)
    for xx,im,label in [(10,old,'v01'),(590,new,'v02: warmer evening light')]:
        d.text((xx,8),label,font=ImageFont.truetype(v.SANS,20),fill='white');sheet.paste(im.crop((700,40,1260,600)),(xx,38))
    refs=[OUT.parent/'wom02/wom02_サムネ案1_v02_20261026.jpg',OUT.parent/'wom04/wom04_サムネ案3_v02_20261027.jpg']
    for i,(im,label) in enumerate(zip([old,new,*[Image.open(p) for p in refs]],['v01','v02','Halloween','Pandora'])):
        xx=10+i*286;d.text((xx,620),label,font=ImageFont.truetype(v.SANS,17),fill='white');sheet.paste(im.resize((168,94),Image.Resampling.LANCZOS),(xx,650))
    comp=OUT/'wom03_サムネ案1_v01_v02比較_20261027.jpg';sheet.save(comp,quality=93,optimize=True,subsampling=0)
    for f in [p,comp]:shutil.copy2(f,MEDIA/'deliverables'/f.name)
    record={'date':'2026-10-27','image_generation_calls':0,'source':v.record(src),'previous':v.record(prior),'output':v.record(p),'comparison':v.record(comp),'lighting':{'support':'x>630, y<650 at 1280x720; left ramp55px, bottom ramp30px','method':'Existing luminance selects lit planes: light=clip((Y-40)/150). Add (255-RGB)*light*(.25,.13,.015)*upper-right direction; blue reduction .055*B*light; shadows up to3.5% deeper. All operations blended by mask.','changed_pixels':int(diff.sum()),'outside_mask_changed_pixels':int(diff[~allowed].sum()),'final_outside_mask_changed_pixels':int(finaldiff[~allowed].sum()),'new_near_white_pixels_RGB_ge250':new_white,'note':'画素差0はJPEG圧縮前。形状・構図・文字変更なし。'},'v01_byte_identical_reproduction':True,'clearance':{'subject_guard_x':630,'upper_shadow_right_exclusive':466,'lower_shadow_right_exclusive':596,'upper_gap_px':164,'lower_gap_px':34,'minimum_conservative_gap_px':34},'references':[v.record(p) for p in refs]}
    f=ROOT/'wom03_サムネ案1_v02検品_20261027.json';f.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');shutil.copy2(f,MEDIA/f.name)
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=='__main__':run()
