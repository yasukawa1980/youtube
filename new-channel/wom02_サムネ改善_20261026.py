"""依頼書指定の切り出し・グラデーション・文字合成。原画像は非破壊で保存。"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

REPO = Path(__file__).resolve().parents[1]
PREVIEW = REPO / 'new-channel/サムネ確認用/wom02'
MEDIA = Path('/Users/ryo/Desktop/新チャンネル/EP002_Halloween/サムネ改善_20261026')
SERIF = '/System/Library/Fonts/Supplemental/Georgia.ttf'
SANS = '/System/Library/Fonts/Supplemental/Arial.ttf'
JP = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
IVORY, GOLD = '#f4efdf', '#d8b575'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def record(p):
    im = Image.open(p)
    return {'path': str(p), 'size': list(im.size), 'bytes': p.stat().st_size, 'sha256': sha(p)}

def gradient(im, amount=.65, stop=.64):
    mask = Image.new('L', (1280, 720))
    row = [int(255 * amount * max(0, 1-x/(1280*stop))**.7) for x in range(1280)]
    mask.putdata(row*720)
    return Image.composite(Image.new('RGB', im.size, '#050d17'), im, mask)

def headline(im, text, xy, width, height=132):
    # 同じGeorgiaの字形を保持し、縦の可読寸法を優先したコンデンス組み。
    font = ImageFont.truetype(SERIF, 190)
    box = font.getbbox(text)
    tile = Image.new('RGBA', (box[2]-box[0]+8, box[3]-box[1]+8))
    ImageDraw.Draw(tile).text((4-box[0],4-box[1]), text, font=font, fill=IVORY)
    tile = tile.resize((width, height), Image.Resampling.LANCZOS)
    shadow = Image.new('RGBA', tile.size, (0,0,0,0))
    shadow.putalpha(tile.getchannel('A').point(lambda a: int(a*.75)))
    im.paste(shadow, (xy[0]+2,xy[1]+3), shadow)
    im.paste(tile, xy, tile)

def caption(im, pos):
    d=ImageDraw.Draw(im)
    d.text(pos, 'Halloween: Celtic or Not?', font=ImageFont.truetype(SERIF, 33), fill=GOLD, stroke_width=1, stroke_fill='#141519')
    d.text((80,615), 'QUIET ORIGINS', font=ImageFont.truetype(SANS,22), fill=GOLD)

def save(im, name):
    p=PREVIEW/name
    im.save(p, quality=94, optimize=True, subsampling=0)
    assert im.size==(1280,720) and p.stat().st_size < 1_000_000
    shutil.copy2(p, MEDIA/'deliverables'/name)
    return p

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--scene1', type=Path, required=True)
    ap.add_argument('--scene3', type=Path, required=True)
    args=ap.parse_args()
    PREVIEW.mkdir(parents=True,exist_ok=True)
    (MEDIA/'sources').mkdir(parents=True,exist_ok=True)
    (MEDIA/'deliverables').mkdir(exist_ok=True)
    originals=[]
    for source,name in [(args.scene1,'案1_手持ちカブ_原寸.png'),(args.scene3,'案3_カブとかぼちゃ_原寸.png'),(Path('/Users/ryo/Desktop/新チャンネル/EP002_Halloween/素材/R02_reconstruction_v01.png'),'案2_R02_元画像.png')]:
        target=MEDIA/'sources'/name
        if target.exists() and sha(target)!=sha(source):
            raise RuntimeError(f'異なる既存画像を上書きしません: {target}')
        shutil.copy2(source,target)
        originals.append(record(target))
    im1=ImageOps.fit(Image.open(args.scene1).convert('RGB'),(1280,720))
    im1=gradient(im1,.69,.63)
    headline(im1,'BEFORE',(54,145),482)
    headline(im1,'PUMPKINS',(54,301),635)
    caption(im1,(58,476))
    p1=save(im1,'wom02_サムネ案1_20261026.jpg')
    r02=Image.open(MEDIA/'sources/案2_R02_元画像.png').convert('RGB')
    crop=(220,150,1210,707)
    im2=r02.crop(crop).resize((1280,720),Image.Resampling.LANCZOS)
    im2=gradient(im2,.92,.71)
    headline(im2,'BEFORE',(54,90),482)
    headline(im2,'PUMPKINS',(54,246),635)
    caption(im2,(58,420))
    p2=save(im2,'wom02_サムネ案2_20261026.jpg')
    im3=ImageOps.fit(Image.open(args.scene3).convert('RGB'),(1280,720))
    im3=gradient(im3,.2,.7)
    headline(im3,'TURNIPS FIRST?',(54,46),1172)
    caption(im3,(60,202))
    d=ImageDraw.Draw(im3)
    d.line((605,421,680,421),fill=GOLD,width=4)
    d.line((664,407,680,421,664,435),fill=GOLD,width=4)
    p3=save(im3,'wom02_サムネ案3_20261026.jpg')
    current=PREVIEW/'wom02_サムネ.jpg'
    anubis=REPO/'new-channel/サムネ確認用/wom01_サムネ.jpg'
    labels=['現行','案1：手持ち','案2：既存R02','案3：対比','参考：アヌビス']
    sheet=Image.new('RGB',(936,150),'#15191e')
    d=ImageDraw.Draw(sheet)
    for i,(p,label) in enumerate(zip([current,p1,p2,p3,anubis],labels)):
        x=16+i*184
        d.text((x,8),label,font=ImageFont.truetype(JP,13),fill='white')
        sheet.paste(Image.open(p).convert('RGB').resize((168,94),Image.Resampling.LANCZOS),(x,35))
    comparison=PREVIEW/'wom02_サムネ168px比較_20261026.jpg'
    sheet.save(comparison,quality=95,optimize=True,subsampling=0)
    shutil.copy2(comparison,MEDIA/'deliverables'/comparison.name)
    manifest={'date':'2026-10-26','service':'OpenAI built-in image_gen','originals':originals,'outputs':[record(p) for p in [p1,p2,p3,comparison]],'r02_crop_box':list(crop),'text_font':SERIF,'title_raster_height_px':132,'title_height_ratio':132/720,'comparison_cell_px':[168,94],'existing_thumbnails':[record(current),record(anubis)],'youtube_modified':False}
    out=REPO/'new-channel/wom02_サムネ改善検品_20261026.json'
    out.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    shutil.copy2(out,MEDIA/out.name)
    print(json.dumps(manifest,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
