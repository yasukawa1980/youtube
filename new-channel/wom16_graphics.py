"""Cumulative bilingual timeline. Coordinates use the 1920 × 1080 composition."""
from PIL import ImageDraw
from wom15_boards import Plate, PAPER, INK, RULE, SOFT
from wom15_art import lines

CARDS=[
 '8TH C. BC · HOMER: A VOICE, NO BODY｜紀元前8世紀ごろ・ホメロス：声だけ、姿はない',
 '7TH–3RD C. BC · GREEK ART AND POETS: BIRDS｜紀元前7〜3世紀・ギリシャの美術と詩：鳥',
 'C. AD 700 · BOOK OF MONSTERS: FISH TAILS｜西暦700年ごろ・『怪物の書』：魚の尾',
 '13TH–14TH C. · ONE TEXT: EAGLE CLAWS AND FISH TAILS｜13〜14世紀・ある書物：鷲の爪と魚の尾']
JAPANESE_LINES=[
    ['紀元前8世紀ごろ・','ホメロス：声だけ、','姿はない'],
    ['紀元前7〜3世紀・','ギリシャの','美術と詩：鳥'],
    ['西暦700年ごろ・','『怪物の書』：魚の尾'],
    ['13〜14世紀・','ある書物：','鷲の爪と魚の尾'],
]
KEYS=['D_tl_voice','D_tl_bird','D_tl_fish','D_tl_both','D_tl_all']
def symbol(p,n,cx,cy):
    s=p.s
    def pts(points):
        return [((cx+x)*s,(cy+y)*s) for x,y in points]
    def poly(points):p.d.polygon(pts(points),fill=INK)
    if n==0:
        import math
        for dy in [-22,0,22]:
            p.d.line(pts([(x,dy+8*math.sin(x/21)) for x in range(-64,65)]),fill=INK,width=5*s)
    if n in (1,3):
        p.d.ellipse(((cx+14)*s,(cy-47)*s,(cx+46)*s,(cy-15)*s),fill=INK)
        poly([(19,-20),(39,-20),(41,-9),(22,5),(9,1)])
        poly([(28,-4),(5,-22),(-49,-50),(-37,-22),(-59,-32),(-41,-9),(-64,-14),(-44,8),(-16,23),(3,24),(25,9)])
        if n==1:
            p.line([(cx-9,cy+19),(cx-14,cy+43),(cx-24,cy+46)],INK,4)
            p.line([(cx+2,cy+18),(cx+2,cy+40),(cx-5,cy+45)],INK,4)
    if n in (2,3):
        # A curved peduncle opens into one rounded fan, visible below the combined wing.
        off=14 if n==3 else 0
        drop=28 if n==3 else 0
        tail=[(-7,-29),(12,-31),(19,-21),(19,-6),(13,7),(0,17),(-12,21),(-17,27),(-23,40),(-34,49),(-48,53),(-58,52),(-55,39),(-48,27),(-36,18),(-22,14),(-12,8),(-5,-3),(-3,-15)]
        poly([(off+x,drop+y) for x,y in tail])
def timeline(s,stage,offset=0,summary=False):
    p=Plate(s);p.label('TIMELINE｜年表')
    p.line([(68,752),(1850,752)],RULE,3)
    for text,x,r in [('8TH C. BC｜紀元前8世紀',44,450),('13TH–14TH C.｜13〜14世紀',1380,1880)]:
        p.text(text,(x,770,r,822),28,'ja')
    for n in range(min(stage+1,4)):
        x=[52,485,966,1423][n];w=[411,455,435,447][n];y=150+(offset if n==stage else 0)
        bounds=(x,y,x+w,y+555);p.box(bounds,PAPER,RULE,2)
        symbol(p,n,x+w//2,y+(62 if n==3 else 86))
        a,b=CARDS[n].split('｜')
        prior=len(p.metrics)
        for phrase,size,face,base,step in [(a,48,'main',159,56),(b,41,'ja',383,49)]:
            rows=JAPANESE_LINES[n] if face=='ja' else lines(phrase,w-34,size,face,s)
            if face=='ja':assert ''.join(rows)==phrase
            for j,row in enumerate(rows):
                top=y+base+j*step;p.text(row,(x+10,top,x+w-10,top+step),size,face)
        p.padding(prior,bounds)
        if n:
            p.line([(x+w//2,y+555),(x+w//2,750)],RULE,2)
        if n==0:p.text('traditional dating｜通説の年代',(62,y+557,450,y+595),20,'ja',SOFT)
    if summary:p.text('ONE NAME, TWO SHAPES｜一つの名前、二つの姿',(520,817,1400,877),31,'ja')
    return p
