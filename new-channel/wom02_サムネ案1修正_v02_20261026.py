"""案1の見出し幅だけ修正。新規生成なし、v01保持。"""
import importlib.util
import json
import shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('thumb_v01',ROOT/'wom02_サムネ改善_20261026.py')
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
source=v.MEDIA/'sources/案1_手持ちカブ_原寸.png'
base=v.gradient(ImageOps.fit(Image.open(source).convert('RGB'),(1280,720)),.69,.63)
old=base.copy(); new=base.copy()
for im,w1,w2 in [(old,482,635),(new,448,590)]:
    v.headline(im,'BEFORE',(54,145),w1)
    v.headline(im,'PUMPKINS',(54,301),w2)
    v.caption(im,(58,476))
old_array=np.array(old); new_array=np.array(new)
changed=np.any(old_array!=new_array,axis=2)
allowed=np.zeros((720,1280),bool)
allowed[145:280,54:538]=True
allowed[301:436,54:691]=True
assert not (changed & ~allowed).any()
# 元のv01を同じエンコーダーで再現できることを確認。
import io
buf=io.BytesIO();old.save(buf,format='JPEG',quality=94,optimize=True,subsampling=0)
assert buf.getvalue()==(v.PREVIEW/'wom02_サムネ案1_20261026.jpg').read_bytes()
out=v.save(new,'wom02_サムネ案1_v02_20261026.jpg')
# 文字の外接枠と同じ高さの範囲で、照らされたカブの皮を計測。
# 彩色境界の定義：R>=80, R>B*1.4, R>G*1.05、横5px連続。
a=np.array(base).astype(float)
skin=(a[:,:,0]>=80)&(a[:,:,0]>a[:,:,2]*1.4)&(a[:,:,0]>a[:,:,1]*1.05)
edges=[]
for y in range(301,436):
    for x in range(650,850):
        if skin[y,x:x+5].all():
            edges.append((x,y));break
lantern_x,lantern_y=min(edges)
text_right=54+590+2 # 影を含む合成枠の排他的右端
gap=int(lantern_x-text_right)
assert gap>=16,(lantern_x,gap)
font=ImageFont.truetype(v.SANS,18)
sheet=Image.new('RGB',(1080,550),'#15191e');d=ImageDraw.Draw(sheet)
for col,(im,label) in enumerate([(old,'v01 / BEFORE 482, PUMPKINS 635'),(new,'v02 / BEFORE 448, PUMPKINS 590')]):
    x=20+col*540
    d.text((x,14),label,font=font,fill='white')
    crop=im.crop((580,290,830,450)).resize((500,320),Image.Resampling.NEAREST)
    sheet.paste(crop,(x,45))
    sheet.paste(im.resize((168,94),Image.Resampling.LANCZOS),(x,415))
    d.text((x,382),'168 x 94 px',font=font,fill='white')
d.text((570,520),f'Shadow box right: {text_right} / skin left: {lantern_x} / gap: {gap}px',font=ImageFont.truetype(v.SANS,15),fill=v.GOLD)
comparison=v.PREVIEW/'wom02_サムネ案1_v01_v02比較_20261026.jpg'
sheet.save(comparison,quality=94,optimize=True,subsampling=0)
shutil.copy2(comparison,v.MEDIA/'deliverables'/comparison.name)
record={'source':v.record(source),'output':v.record(out),'comparison':v.record(comparison),'widths_before':[482,635],'widths_after':[448,590],'height':132,'positions':[[54,145],[54,301]],'source_regenerated':False,'v01_byte_identical_reproduced':True,'changed_pixels_outside_title_boxes':0,'measurement':{'text_shadow_box_right_exclusive_x':text_right,'lantern_bright_skin_left_x':int(lantern_x),'lantern_edge_y':int(lantern_y),'horizontal_gap_px':gap,'rows_checked_inclusive':[301,435],'skin_definition':'R>=80 and R>B*1.4 and R>G*1.05, 5 consecutive horizontal pixels','note':'絵画の境界には幅があるため、明るい皮の色境界で測定。文字の影を含む外接枠を使った保守値。'}}
p=ROOT/'wom02_サムネ案1_v02検品_20261026.json'
p.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
shutil.copy2(p,v.MEDIA/p.name)
print(json.dumps(record,ensure_ascii=False,indent=2))
