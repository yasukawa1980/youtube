"""天狗の生成背景2点へ文字を合成し、3案と比較・検品記録を作る。"""
import importlib.util
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('base',ROOT/'wom02_サムネ改善_20261026.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
OUT=ROOT/'サムネ確認用/wom05'
MEDIA=Path('/Users/ryo/Desktop/新チャンネル/EP005_Tengu/サムネ改善_20261027')
GENERATED=Path('/Users/ryo/.codex/generated_images/01a177ae-82d0-7bf2-9879-da3fbcc129b0')
SOURCES=[('exec-fb48c912-6023-48e6-95d7-7a00e5105d98.png','案1案3_夜空の星_原寸.png'),('exec-de2d1c56-5221-41fa-88d8-c1759973b7e4.png','案2_面と星_原寸.png')]

def run():
    OUT.mkdir(parents=True,exist_ok=True)
    (MEDIA/'sources').mkdir(parents=True,exist_ok=True)
    (MEDIA/'deliverables').mkdir(exist_ok=True)
    originals=[];bases=[]
    for src,name in SOURCES:
        target=MEDIA/'sources'/name
        if not target.exists():shutil.copy2(GENERATED/src,target)
        else:assert v.sha(target)==v.sha(GENERATED/src)
        originals.append(v.record(target))
        bases.append(v.gradient(ImageOps.fit(Image.open(target).convert('RGB'),(1280,720)),.69,.63))
    outputs=[];metrics=[];thumbs=[]
    for i,(source,lines,widths) in enumerate([(0,['STAR','TENGU'],[410,500]),(1,['STAR','TENGU'],[410,500]),(0,['SKY','DOG?'],[330,430])],1):
        im=bases[source].copy()
        for y,line,w in zip([145,301],lines,widths):v.headline(im,line,(54,y),w)
        d=ImageDraw.Draw(im)
        d.text((58,476),('The first tengu was a star' if i==3 else 'Before the long nose'),font=ImageFont.truetype(v.SERIF,33),fill=v.GOLD,stroke_width=1,stroke_fill='#141519')
        d.text((80,615),'QUIET ORIGINS',font=ImageFont.truetype(v.SANS,22),fill=v.GOLD)
        p=OUT/f'wom05_サムネ案{i}_20261027.jpg';im.save(p,quality=94,optimize=True,subsampling=0)
        assert p.stat().st_size<1000000
        outputs.append(v.record(p));thumbs.append(im);shutil.copy2(p,MEDIA/'deliverables'/p.name)
        gaps=[740-(54+w+2) for w in widths]
        assert min(gaps)>=16
        metrics.append({'candidate':i,'widths':widths,'subject_guard_left_x':740,'title_shadow_right_exclusive_x':[54+w+2 for w in widths],'conservative_gaps_px':gaps,'minimum_conservative_gap_px':min(gaps)})
    old=OUT/'wom05_サムネ_met_24145.jpg'
    refs=[ROOT/'サムネ確認用/wom02/wom02_サムネ案1_v02_20261026.jpg',ROOT/'サムネ確認用/wom03/wom03_サムネ案1_v02_20261027.jpg',ROOT/'サムネ確認用/wom04/wom04_サムネ案3_v02_20261027.jpg']
    sheet=Image.new('RGB',(1272,150),'#15191e');d=ImageDraw.Draw(sheet)
    for i,(im,label) in enumerate(zip([Image.open(old),*thumbs,*[Image.open(p) for p in refs]],['現行 met_24145','案1：星','案2：面と星','案3：SKY DOG?','参考：ハロウィン','参考：メドゥーサ','参考：パンドラ'])):
        x=12+i*180;d.text((x,8),label,font=ImageFont.truetype(v.JP,13),fill='white');sheet.paste(im.resize((168,94),Image.Resampling.LANCZOS),(x,35))
    p=OUT/'wom05_サムネ168px比較_20261027.jpg';sheet.save(p,quality=95,optimize=True,subsampling=0);outputs.append(v.record(p));shutil.copy2(p,MEDIA/'deliverables'/p.name)
    sheet=Image.new('RGB',(1280,804),'#15191e');d=ImageDraw.Draw(sheet)
    for i,(im,m) in enumerate(zip(thumbs,metrics)):
        mark=im.copy();md=ImageDraw.Draw(mark)
        for y,w in zip([145,301],m['widths']):md.rectangle((54,y,54+w+2,y+135),outline='#50e6ff',width=3)
        md.line((740,145,740,436),fill='#ff66bb',width=3)
        x=i%2*640;y=i//2*402
        d.text((x+12,y+8),f"Option {i+1}: conservative gap {m['minimum_conservative_gap_px']}px",font=ImageFont.truetype(v.SANS,19),fill='white')
        sheet.paste(mark.resize((640,360),Image.Resampling.LANCZOS),(x,y+36))
    p=OUT/'wom05_サムネ余白検品_20261027.jpg';sheet.save(p,quality=90,optimize=True);outputs.append(v.record(p));shutil.copy2(p,MEDIA/'deliverables'/p.name)
    record={'date':'2026-10-27','service':'OpenAI built-in image_gen','generation_calls':2,'originals':originals,'outputs':outputs,'measurements':metrics,'measurement_method':'y145〜436の見出し帯で、星の頭・明るい尾とハロー・面の鼻先もx740より右にあることを目視確認。文字の影を含む外接枠から保全領域x740への距離。実輪郭の自動抽出値ではなく保守値。','title_height_px':132,'comparison_cell_px':[168,94],'same_background_candidates':[1,3],'youtube_modified':False,'previous_thumbnails':[v.record(p) for p in [old,*refs]]}
    p=ROOT/'wom05_サムネ改善検品_20261027.json';p.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');shutil.copy2(p,MEDIA/p.name)
    p=ROOT/'wom05_サムネ生成プロンプト_20261027.json';shutil.copy2(p,MEDIA/p.name)
    print(json.dumps({'outputs':outputs,'measurements':metrics},ensure_ascii=False,indent=2))

if __name__=='__main__':run()
