"""採用背景を再生成せず、限定マスク内の煙の露出とU+2019だけを修正。"""
import importlib.util
import io
import json
import shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('base', ROOT/'wom02_サムネ改善_20261026.py')
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
OUT = ROOT/'サムネ確認用/wom04'
MEDIA = Path('/Users/ryo/Desktop/新チャンネル/EP004_Pandora/サムネ改善_20261026')
POLYGON = [(625,0),(927,0),(928,40),(919,63),(924,108),(941,134),(959,157),(965,166),(851,166),(824,163),(779,150),(780,126),(755,113),(701,120),(648,95),(628,65),(610,28)]

def compose(bg, title):
    im = v.gradient(bg,.69,.63)
    v.headline(im,title,(54,145),590)
    v.headline(im,'JAR',(54,301),250)
    d = ImageDraw.Draw(im)
    d.text((58,476),'It was never a box',font=ImageFont.truetype(v.SERIF,33),fill=v.GOLD,stroke_width=1,stroke_fill='#141519')
    d.text((80,615),'QUIET ORIGINS',font=ImageFont.truetype(v.SANS,22),fill=v.GOLD)
    return im

def run():
    src = MEDIA/'sources/案1案3_壺を開ける手_原寸.png'
    bg = ImageOps.fit(Image.open(src).convert('RGB'),(1280,720))
    support = Image.new('L',bg.size); ImageDraw.Draw(support).polygon(POLYGON,fill=255)
    # フェザーをマスク内部だけに閉じ込め、範囲外は厳密に0。
    m = np.array(support.filter(ImageFilter.MinFilter(31)).filter(ImageFilter.GaussianBlur(7)),dtype=float)/255
    allowed = np.array(support)>0; m *= allowed
    a = np.array(bg,dtype=float); yy = np.arange(720)[:,None]
    warmth = np.clip((yy-55)/130,0,1)
    gain = 1.85-.35*warmth
    tint = np.stack([18+10*warmth,18+2*warmth,20-12*warmth],axis=2)
    target = np.minimum(255,a*gain[:,:,None]+tint)
    b = np.rint(a+(target-a)*m[:,:,None]).astype('uint8')
    adjusted = Image.fromarray(b)
    old = compose(bg,"PANDORA'S"); new = compose(adjusted,'PANDORA’S')
    buf=io.BytesIO();old.save(buf,format='JPEG',quality=94,optimize=True,subsampling=0)
    prior=OUT/'wom04_サムネ案3_20261026.jpg'
    assert buf.getvalue()==prior.read_bytes(),'v01再現不一致'
    diff=np.any(b!=np.array(bg),axis=2)
    assert not diff[~allowed].any()
    final_allowed=allowed.copy();final_allowed[145:280,54:646]=True
    final_diff=np.any(np.array(new)!=np.array(old),axis=2)
    assert not final_diff[~final_allowed].any()
    p=OUT/'wom04_サムネ案3_v02_20261027.jpg';new.save(p,quality=94,optimize=True,subsampling=0)
    assert p.stat().st_size<1000000
    (MEDIA/'v02').mkdir(exist_ok=True)
    for im,name in [(bg,'背景_調整前.png'),(adjusted,'背景_煙調整後.png'),(support,'煙_変更許可マスク.png'),(new,'完成_圧縮前.png')]:im.save(MEDIA/'v02'/name)
    sheet=Image.new('RGB',(1040,440),'#15191e');d=ImageDraw.Draw(sheet)
    for x,im,label in [(10,old,'v01'),(530,new,'v02: U+2019 / smoke lighting')]:
        d.text((x,8),label,font=ImageFont.truetype(v.SANS,20),fill='white')
        sheet.paste(im.crop((590,0,1100,230)),(x,38))
        sheet.paste(im.resize((168,94),Image.Resampling.LANCZOS),(x,310))
    comparison=OUT/'wom04_サムネ案3_v01_v02比較_20261027.jpg';sheet.save(comparison,quality=94,optimize=True,subsampling=0)
    for f in [p,comparison]:shutil.copy2(f,MEDIA/'deliverables'/f.name)
    record={'date':'2026-10-27','image_generation_calls':0,'source':v.record(src),'previous':v.record(prior),'output':v.record(p),'comparison':v.record(comparison),'headline':{'text':'PANDORA’S','apostrophe':'U+2019','x':54,'y':145,'width':590,'height':132},'smoke':{'polygon_1280x720':POLYGON,'inward_erosion_px':15,'feather_sigma_px':7,'method':'gain 1.85→1.50; RGB lift upper(18,18,20)→lower(28,20,8); original texture retained; no added embers','changed_pixels':int(diff.sum()),'outside_mask_changed_pixels':int(diff[~allowed].sum()),'precompression_outside_smoke_and_headline_changed_pixels':int(final_diff[~final_allowed].sum()),'note':'0画素保証はJPEG圧縮前。JPEG再圧縮による差分は別。'},'v01_byte_identical_reproduction':True,'clearance':{'upper_guard_x':740,'upper_title_shadow_right_exclusive':646,'upper_conservative_gap_px':94,'lower_clay_edge_x':751,'lower_title_shadow_right_exclusive':306,'lower_gap_px':445,'minimum_conservative_gap_px':94}}
    f=ROOT/'wom04_サムネ案3_v02検品_20261027.json';f.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');shutil.copy2(f,MEDIA/f.name)
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=='__main__':run()
