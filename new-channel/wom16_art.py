"""Source-native compositions, captions and line crops for EP016."""
import re
from functools import lru_cache
from PIL import Image,ImageDraw,ImageFilter
from wom16_voice import HERE,ROOT,read
from wom15_art import block
from wom15_boards import Plate,PAPER,INK,SOFT,RULE,VERMILION
from wom16_graphics import timeline,KEYS
SCRIPT=(HERE/'wom16_制作依頼_20261127.md').read_text()
used={v for seg in read(HERE/'episodes/EP016_Sirens/records/content_en.json')['segments'] for v in seg['visuals']}
ASSETS={a['id']:a for a in read(HERE/'research/wom16_素材台帳_20261127.json')['assets'] if a['id'] in used}
# Fractions of each ledger locator. The smaller bounds follow the typeset or manuscript lines.
ROWS={
 'SR09-A':[(.005,.433,.88,.582),(.01,.658,.902,.954)],
 'SR09-B':[(.02,.657,.80,.847)],
 'SR09-C':[(.031,.63,.735,.865)],
 'SR10-A':[(.035,.012,.814,.899)],'SR11-A':[(.025,.012,.99,.671)],
 'SR12-A':[(.008,.477,.856,.654),(.01,.742,.805,.978)],
 'SR05-A':[(.004,.335,.996,.666),(.01,.492,.993,.982)],
 'SR08-A':[(.035,.095,.966,.396)],
 'SR07-T':[(.024,.055,.888,.257),(.026,.566,.905,.771),(.026,.77,.91,.929)]}
BOXES={}
for k,rows in ROWS.items():
    l,t,r,b=[v/100 for v in ASSETS[k]['locator']['bbox_pct']]
    BOXES[k]=[(l+(r-l)*x,t+(b-t)*y,l+(r-l)*xx,t+(b-t)*yy) for x,y,xx,yy in rows]
LABELS={};NOTES={}
for line in SCRIPT.splitlines():
    m=re.match(r'^- \*\*(SR[0-9]+-[A-Z])\*\*',line)
    if not m:continue
    k=m[1];q=re.search(r'注[： ]+\x60([^\x60]+)\x60',line);tag=re.search(r'札 [*]*\x60([^\x60]+)\x60',line)
    if q:NOTES[k]=q[1]
    if tag:LABELS[k]=tag[1]
LABELS.update({'SR09-B':LABELS['SR09-A'],'SR09-C':LABELS['SR09-A'],'SR06-H':'MANUSCRIPT (C. 1480)｜写本（1480年ごろ）'})
NOTES['SR06-H']='A fish-tailed woman in a 15th-century book of arms. It is not labelled a siren.｜15世紀の紋章の本に描かれた、魚の尾をもつ女性。セイレーンとは書かれていない。'
for k in ASSETS:LABELS.setdefault(k,'PAINTING｜絵画' if k.startswith('SR17') else 'OBJECT｜器物')
assert all(k in NOTES for k in BOXES)
@lru_cache(maxsize=1)
def source(k):
    return Image.open(ASSETS[k]['original']).convert('RGB')
def face(t):
    return 'ja' if re.search(r'[ぁ-龯（）]',t) else 'header'
def art(k,s,u=0,idx=0,mark=False):
    p=Plate(s);a=ASSETS[k];im=source(k);iw,ih=im.size
    wide=k=='SR01-A';exception=k=='SR12-A' and s==2
    x=(0 if wide or exception else 690)*s;w=1920*s-x;h=1080*s
    rect=None
    if wide:
        scale=.565 if s==1 else 1/1.1
        cx,cy=iw*(.5 if s==2 else .565),ih*.471
    elif k=='SR06-H':
        l,t,r,b=a['locator']['bbox_pct'];im=im.crop((round(l*iw/100),round(t*ih/100),round(r*iw/100),round(b*ih/100)));iw,ih=im.size
        # Clip the incidental neighboring ink at the corners, outside the complete crest.
        mask=Image.new('L',im.size);outline=[(.025,.14),(.27,.10),(.44,.035),(.67,.035),(.69,.14),(.90,.135),(.967,.25),(.976,.66),(.91,.81),(.74,.887),(.57,.908),(.28,.89),(.105,.79),(.03,.70)]
        ImageDraw.Draw(mask).polygon([(round(x*iw),round(y*ih)) for x,y in outline],fill=255)
        paper=Image.new('RGB',im.size,PAPER);paper.paste(im,mask=mask.filter(ImageFilter.GaussianBlur(max(2,iw*.016))));im=paper
        scale=min(w/iw,h*.67/ih,1);cx,cy=iw*.5,ih*.5
    else:
        scale=min(w/iw,h/ih,1);cx,cy=iw*.5,ih*.5
    if k in BOXES:
        l,t,r,b=BOXES[k][idx]
        if exception and mark:
            # Native excerpt pasted on the same paper, eliminating the surrounding lines.
            le,te,ri,bo=round(l*iw)-18,round(t*ih)-28,round(r*iw)+18,round(b*ih)+28
            im=im.crop((le,te,ri,bo));x0=(1920*s-im.width)//2;y0=(h-im.height)//2
            p.im.paste(im,(x0,y0));rect=[x0+round(l*iw)-le,y0+round(t*ih)-te,x0+round(r*iw)-le,y0+round(b*ih)-te]
        else:
            dest=min(1,w/((r-l)*iw*1.18),h/((b-t)*ih*1.25))
            scale+=(dest-scale)*u;cx+=(iw*(r+l)/2-cx)*u;cy+=(ih*(b+t)/2-cy)*u
    if exception and not mark:
        p.im.paste(im,((1920*s-iw)//2,(1080*s-ih)//2))
    elif rect is None:
        left=cx-w/(2*scale);top=cy-h/(2*scale)
        if not wide and not exception:
            def origin(offset,span,dim):
                return min(max(offset,0),dim-span) if span<dim else (dim-span)/2
            left=origin(left,w/scale,iw);top=origin(top,h/scale,ih)
            if k=='SR06-H':top=ih/2-383*s/scale
        tile=im.transform((w,h),Image.Transform.AFFINE,(1/scale,0,left,0,1/scale,top),Image.Resampling.BICUBIC,fillcolor=PAPER)
        if wide and s==2:
            # Continue the photographed studio background across the narrow overscan.
            # Only the outermost background column is repeated, outside the original.
            lo=max(0,round(-left*scale)+2);hi=min(w,round((iw-left)*scale)-2)
            if lo:
                tile.paste(tile.crop((lo,0,lo+1,h)).resize((lo,h)),(0,0))
            if hi<w:
                tile.paste(tile.crop((hi-1,0,hi,h)).resize((w-hi,h)),(hi,0))
        p.im.paste(tile,(x,0))
        if mark:rect=[round(x+(l*iw-left)*scale),round((t*ih-top)*scale),round(x+(r*iw-left)*scale),round((b*ih-top)*scale)]
    if rect:p.d.rectangle(rect,outline=VERMILION,width=2 if exception else 2*s)
    if wide:
        p.box((0,0,710,128),INK)
        block(p,LABELS[k],22,8,670,20,'ja',PAPER)
        block(p,a['title'],22,35,677,33,'header',PAPER)
        block(p,'East Greek (Rhodian) · '+a['date']+' · The Met 06.1021.34 (CC0)',22,91,680,19,'small',PAPER)
    else:
        p.box((0,0,677,1080),PAPER)
        en,ja=LABELS[k].split('｜');y=block(p,en,38,40,605,28,'main');y=block(p,ja,38,y+4,604,22,'ja',SOFT)+20
        p.line([(38,y),(640,y)])
        if k in NOTES and k!='SR06-H':
            en,ja=NOTES[k].split('｜');y=block(p,en,38,y+26,600,35,'header')
            y=block(p,ja,38,y+12,600,26,'ja')
        y=max(y+38,455 if k in BOXES else 237)
        titles=a['title'].split(' — ') if k=='SR06-H' else [a['title']]
        for title in titles:
            y=block(p,title,38,y,603,31 if k in BOXES else 39,face(title))
        y=block(p,a['artist'],38,y+13,604,21,'ja' if face(a['artist'])=='ja' else 'small',SOFT)
        y=block(p,a['date'],38,y+8,604,23,'ja')
        if not k.startswith('SR17'):
            y=block(p,a['museum']+' · '+a['accession'],38,y+8,604,19,'ja' if face(a['museum'])=='ja' else 'small',SOFT)
        if k=='SR06-H':
            p.box((32,737,1885,893),PAPER,RULE,1)
            en,ja=NOTES[k].split('｜');block(p,en,57,757,1802,31,'header');block(p,ja,57,823,1802,27,'ja')
        assert y<910,(k,y)
    return p,dict(key=k,scale=scale,source_size=[iw,ih],source_box=BOXES[k][idx] if k in BOXES else None,output_box=rect)
def credits(s):
    p=Plate(s);p.pair('QUIET ORIGINS｜クワイエット・オリジンズ',(130,80,1790,239),70,36,None)
    rows=['English voice: Kokoro / Heart (af_heart)     ·     日本語の声　VOICEVOX:冥鳴ひまり','The Metropolitan Museum of Art     ·     The Cleveland Museum of Art','Universitätsbibliothek Basel     ·     ETH-Bibliothek Zürich     ·     Zentralbibliothek Zürich','Stiftung der Werke von C.G. Jung     ·     Wellcome Collection','Bayerische Staatsbibliothek München','Music: QO_THEME_A02 / Suno']
    for i,row in enumerate(rows):p.text(row,(78,280+i*89,1842,347+i*89),34,'ja' if i==0 else 'small')
    return p
