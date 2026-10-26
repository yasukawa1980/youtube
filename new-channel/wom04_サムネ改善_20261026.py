"""パンドラのサムネ3案。背景は組み込み生成、文字と比較は決定的に合成。"""
import importlib.util
import json
import shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('thumbnail_base',ROOT/'wom02_サムネ改善_20261026.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
OUT=ROOT/'サムネ確認用/wom04'
MEDIA=Path('/Users/ryo/Desktop/新チャンネル/EP004_Pandora/サムネ改善_20261026')
GENERATED=Path('/Users/ryo/.codex/generated_images/01a177ae-82d0-7bf2-9879-da3fbcc129b0')
SOURCES=[('exec-7cefa513-7932-446d-b1de-5fb6b8dbe477.png','案1_初回_未採用.png'),('exec-820cffae-cf28-48a8-8be9-e99890065a8e.png','案1案3_壺を開ける手_原寸.png'),('exec-0e7c0c88-ae2f-4bf1-9cc0-c2ec58b69930.png','案2_壺と小箱_原寸.png')]

def run():
    (MEDIA/'sources').mkdir(parents=True,exist_ok=True)
    (MEDIA/'deliverables').mkdir(exist_ok=True)
    originals=[]
    for src,name in SOURCES:
        target=MEDIA/'sources'/name
        if target.exists():assert v.sha(target)==v.sha(GENERATED/src)
        shutil.copy2(GENERATED/src,target);originals.append(v.record(target))
    bases=[v.gradient(ImageOps.fit(Image.open(MEDIA/'sources'/name).convert('RGB'),(1280,720)),.69,.63) for _,name in SOURCES[1:]]
    outputs=[];metrics=[];thumbs=[]
    specs=[(0,['NEVER A','BOX'],[530,290],"Pandora's Box"),(1,['NEVER A','BOX'],[530,290],"Pandora's Box"),(0,["PANDORA'S",'JAR'],[590,250],'It was never a box')]
    for i,(source,lines,widths,sub) in enumerate(specs,1):
        im=bases[source].copy()
        for y,line,width in zip([145,301],lines,widths):v.headline(im,line,(54,y),width)
        d=ImageDraw.Draw(im)
        d.text((58,476),sub,font=ImageFont.truetype(v.SERIF,33),fill=v.GOLD,stroke_width=1,stroke_fill='#141519')
        d.text((80,615),'QUIET ORIGINS',font=ImageFont.truetype(v.SANS,22),fill=v.GOLD)
        p=OUT/f'wom04_サムネ案{i}_20261026.jpg'
        im.save(p,quality=94,optimize=True,subsampling=0)
        assert p.stat().st_size<1000000
        shutil.copy2(p,MEDIA/'deliverables'/p.name)
        outputs.append(v.record(p));thumbs.append(im)
        # 下段と同じ高さにある壺本体の暖色境界。煙を含む上段とは分ける。
        a=np.array(bases[source]).astype(float)
        clay=(a[:,:,0]>=90)&(a[:,:,0]>a[:,:,2]*1.45)&(a[:,:,0]>a[:,:,1]*1.07)
        edges=[]
        for y in range(301,436):
            for x in range(700,1000):
                if clay[y,x:x+8].all():edges.append((x,y));break
        left,y=min(edges)
        # 上段の手・蓋・壺は、目視確認した保守的な主役保全領域x>=740内。
        guard=740
        upper_right=54+widths[0]+2;lower_right=54+widths[1]+2
        gap1=guard-upper_right;gap2=int(left)-lower_right
        assert min(gap1,gap2)>=16
        metrics.append({'candidate':i,'headline_widths':widths,'upper_title_shadow_right_exclusive_x':upper_right,'upper_subject_guard_left_x':guard,'upper_conservative_gap_px':gap1,'lower_title_shadow_right_exclusive_x':lower_right,'lower_clay_edge_x':int(left),'lower_clay_edge_y':int(y),'lower_gap_px':gap2,'minimum_conservative_gap_px':min(gap1,gap2)})
    comparison=Image.new('RGB',(936,150),'#15191e');d=ImageDraw.Draw(comparison)
    old=OUT/'wom04_サムネ_A01.jpg';ref=ROOT/'サムネ確認用/wom02/wom02_サムネ案1_v02_20261026.jpg'
    images=[Image.open(old),*thumbs,Image.open(ref)]
    for i,(im,label) in enumerate(zip(images,['現行 A01','案1：手と壺','案2：壺と小箱','案3：文言違い','参考：ハロウィン'])):
        x=16+i*184;d.text((x,8),label,font=ImageFont.truetype(v.JP,13),fill='white')
        comparison.paste(im.resize((168,94),Image.Resampling.LANCZOS),(x,35))
    p=OUT/'wom04_サムネ168px比較_20261026.jpg';comparison.save(p,quality=95,optimize=True,subsampling=0)
    shutil.copy2(p,MEDIA/'deliverables'/p.name);outputs.append(v.record(p))
    # 見出し枠と主役の保全領域を、各案を縮小した図に記録。
    sheet=Image.new('RGB',(1280,804),'#15191e');d=ImageDraw.Draw(sheet)
    for i,(im,m) in enumerate(zip(thumbs,metrics)):
        marked=im.copy();md=ImageDraw.Draw(marked)
        for y,width in zip([145,301],m['headline_widths']):md.rectangle((54,y,54+width+2,y+135),outline='#50e6ff',width=3)
        md.line((740,145,740,280),fill='#ff66bb',width=3)
        md.line((m['lower_clay_edge_x'],301,m['lower_clay_edge_x'],435),fill='#ff66bb',width=3)
        x=(i%2)*640;y=(i//2)*402
        sheet.paste(marked.resize((640,360),Image.Resampling.LANCZOS),(x,y+36))
        d.text((x+12,y+8),f"Option {i+1}: conservative min {m['minimum_conservative_gap_px']}px",font=ImageFont.truetype(v.SANS,19),fill='white')
    p=OUT/'wom04_サムネ余白検品_20261026.jpg';sheet.save(p,quality=90,optimize=True);assert p.stat().st_size<1000000;outputs.append(v.record(p))
    manifest={'date':'2026-10-26','service':'OpenAI built-in image_gen','generation_calls':3,'adopted_backgrounds':2,'originals':originals,'outputs':outputs,'measurements':metrics,'measurement_method':{'upper':'主役（手・蓋・壺）の外接保全領域を目視設定x>=740。実輪郭はこの領域の右。文字の影を含む外接枠からの保守値。煙は主役の硬い輪郭に含めない。','lower':'y301〜435、x700〜999を走査。R>=90,R>B*1.45,R>G*1.07が横8px連続する壺の暖色境界。文字枠の影を含む。'},'same_background_candidates':[1,3],'comparison_cell_px':[168,94],'youtube_modified':False,'previous_thumbnails':[v.record(old),v.record(ref)]}
    p=ROOT/'wom04_サムネ改善検品_20261026.json';p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');shutil.copy2(p,MEDIA/p.name)
    shutil.copy2(ROOT/'wom04_サムネ生成プロンプト_20261026.json',MEDIA/'wom04_サムネ生成プロンプト_20261026.json')
    print(json.dumps({'outputs':outputs,'measurements':metrics},ensure_ascii=False,indent=2))

if __name__=='__main__':run()
