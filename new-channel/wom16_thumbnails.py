from PIL import Image, ImageDraw, ImageOps, ImageFont
from wom16_voice import ROOT,HERE
from wom15_thumbnails import centered,FONT

def run():
    dst=HERE/'サムネ確認用/wom16'
    source=Image.open(next((ROOT.parent/'素材').glob('SR01-A*'))).convert('RGB')
    base=Image.new('RGB',(1280,720),'#201a16')
    art=ImageOps.fit(source.crop((365,520,3660,3200)),(675,650),centering=(.56,.5))
    base.paste(art);panel=Image.new('RGB',(360,122),'#eee5cd')
    for i,(key,words,size) in enumerate([('A','BIRDS,\nNOT FISH',88),('B','WHEN DID SIRENS\nGET TAILS?',62)]):
        im=base.copy();d=ImageDraw.Draw(im)
        centered(d,words,(681,72,1273,565),size)
        centered(d,'QUIET ORIGINS',(0,652,1280,716),47)
        out=dst/f'wom16_サムネ{key}.jpg';im.save(out,quality=94,optimize=True)
        assert out.stat().st_size<1_000_000
        panel.paste(im.resize((168,95),Image.Resampling.LANCZOS),(5+181*i,24))
        ImageDraw.Draw(panel).text((6+181*i,3),key,font=ImageFont.truetype(FONT,16),fill='#201a16')
    panel.save(dst/'wom16_サムネAB_168px.jpg',quality=95)
if __name__=='__main__':run()
