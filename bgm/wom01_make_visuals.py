"""Compose original diagrams and editorial frames without modifying asset originals."""
import json
import math
import numpy as np
from pathlib import Path
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

ROOT=Path(os.environ['WOM_EPISODE_ROOT']).expanduser().resolve()
W,H=1920,1080
OUT=ROOT/'assets/composed';OUT.mkdir(exist_ok=True)
FONT='/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
TITLE='/System/Library/Fonts/ヒラギノ明朝 ProN.ttc'
if not Path(FONT).exists(): FONT='/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc'
if not Path(TITLE).exists(): TITLE=FONT
GOLD=(215,179,110);IVORY=(244,239,222);MUTED=(161,168,180);BLUE=(89,137,158)
data=json.loads((ROOT/'records/content.json').read_text())
museum=json.loads((ROOT/'records/museum_assets.json').read_text())
byid={str(m['object_id']):m for m in museum}
font_cache={}
def font(n,title=False):
    key=(n,title)
    if key not in font_cache: font_cache[key]=ImageFont.truetype(TITLE if title else FONT,n)
    return font_cache[key]
def text(d,xy,t,n=42,color=IVORY,title=False):
    d.text(xy,t,font=font(n,title),fill=color)
def wrapped(d,xy,t,width,n=42,color=IVORY,line_height=None):
    lines=[];line=''
    for c in t:
        if c=='\n' or d.textlength(line+c,font=font(n))>width:
            lines.append(line);line='' if c=='\n' else c
        else:line+=c
    if line:lines.append(line)
    for i,line in enumerate(lines): text(d,(xy[0],xy[1]+i*(line_height or n*1.55)),line,n,color)
    return len(lines)
def bg():
    y,x=np.mgrid[0:H,0:W]
    glow=np.exp(-(((x-W*.73)/(W*.6))**2+((y-H*.5)/(H*.85))**2))
    rng=np.random.default_rng(15);grain=rng.normal(0,.8,(H,W))
    a=np.stack([9+10*glow+grain,17+10*glow+grain,27+12*glow+grain],axis=-1)
    return Image.fromarray(np.uint8(np.clip(a,0,255)))
def bars(im,heading,kind,source=''):
    d=ImageDraw.Draw(im)
    text(d,(86,37),'WORLDS OF MYSTERY  /  EP001',22,GOLD)
    text(d,(86,80),heading,49,IVORY,True)
    d.line((86,151,1834,151),fill=(61,73,85),width=2)
    boxw=int(d.textlength(kind,font=font(24)))+40
    d.rounded_rectangle((1834-boxw,42,1834,84),radius=12,fill=(32,42,50))
    text(d,(1814-boxw,46),kind,24,GOLD)
    if source: text(d,(86,826),source,25,MUTED)
    return im

names={
 '544075':('横たわるアヌビスの像','前343〜30年／石灰岩、当初は黒彩色'),
 '590939':('犬科の頭を持つ神の小像','前332〜30年／彩色木製／アヌビスと推定'),
 '557830':('ナクトアメンの墓の壁画模写','紙に描かれた模写／作品番号 33.8.21'),
 '548344':('ナウニの死者の書','前1050年頃／パピルス／作品番号 30.3.31'),
 '557657':('オシリスの前の裁き','前230〜150年頃／葬送パピルスの断片'),
 '544206':('アメンエムハト1世の浮き彫り','前1981〜1952年頃／石灰岩・彩色'),
 '547871':('アヌビスとされる金の小像','後2〜3世紀頃／同定は確実ではない'),
 '552247':('ローマ時代の棺材片','後100〜300年／布・化粧漆喰・彩色'),
 '570223':('小さなアヌビス像','前664〜30年／金属／高さ7.7cm'),
 '545547':('イミウトの祭具','前1919〜1885年頃／作品番号 14.3.19–.20')
}
for oid,m in byid.items():
    src=Image.open(ROOT/m['file']).convert('RGB')
    for detail in [False,True]:
        im=bg();title,date=names[oid]
        if detail:
            sw,sh=src.size
            box=(sw*.13,sh*.12,sw*.88,sh*.87)
            if oid=='544206':box=(sw*.34,sh*.05,sw*.93,sh*.96)
            if oid=='548344':box=(sw*.34,sh*.12,sw*.87,sh*.85)
            if oid=='557830':box=(sw*.08,sh*.25,sw*.91,sh*.91)
            src_use=src.crop(tuple(map(round,box)))
        else:src_use=src
        # Wider artifacts get a full-width frame; tall objects use an editorial two-column frame.
        wide=src_use.width/src_use.height>1.08
        area=(110,190,1810,784) if wide else (830,184,1790,791)
        art=ImageOps.contain(src_use,(area[2]-area[0],area[3]-area[1]),Image.Resampling.LANCZOS)
        px=area[0]+(area[2]-area[0]-art.width)//2
        py=area[1]+(area[3]-area[1]-art.height)//2
        im.paste(art,(px,py));d=ImageDraw.Draw(im)
        d.rectangle((px-3,py-3,px+art.width+3,py+art.height+3),outline=(114,96,64),width=2)
        if not wide:
            text(d,(115,245),'残された資料',28,GOLD)
            wrapped(d,(115,310),title,590,62,IVORY)
            wrapped(d,(115,535),date,600,33,MUTED)
            text(d,(115,688),'資料の写真から、姿と役割を読む',29,GOLD)
        bars(im,title+('｜拡大' if detail else ''),'史料画像',
             'The Metropolitan Museum of Art  /  '+m['object_number']+'  /  Open Access (CC0)')
        im.save(OUT/f'met_{oid}{"_detail" if detail else ""}.png')

# AI artwork is fitted to a video frame and explicitly identified, originals stay intact.
generated={'hero':'01_anubis_chamber.png','nile':'02_nile.png','linen':'03_linen.png','archive':'04_archive.png'}
for key,name in generated.items():
    p=ROOT/'assets/generated'/name
    if not p.exists():continue
    im=ImageOps.fit(Image.open(p).convert('RGB'),(W,H),method=Image.Resampling.LANCZOS)
    shade=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(shade)
    d.rectangle((0,0,W,164),fill=(4,10,18,170));d.rectangle((0,800,W,H),fill=(4,10,18,195))
    im=Image.alpha_composite(im.convert('RGBA'),shade).convert('RGB')
    bars(im,{'hero':'アヌビス','nile':'古代の世界を思い描く','linen':'身体を守るための準備','archive':'物語を、資料から読む'}[key],
         'AI再現イメージ','特定の遺跡・出土品を再現した記録画像ではありません')
    im.save(OUT/f'{key}.png')

def diagram(key,heading,draw_fn,source):
    im=bg();bars(im,heading,'概念図',source);draw_fn(ImageDraw.Draw(im));im.save(OUT/f'{key}.png')

def balance(d):
    d.line((960,297,960,688),fill=GOLD,width=8);d.line((558,398,1362,398),fill=GOLD,width=8)
    d.ellipse((946,278,974,306),fill=GOLD);d.line((895,689,1025,689),fill=GOLD,width=10)
    for x in (586,1334):
        d.line((x,399,x-95,600),fill=GOLD,width=3);d.line((x,399,x+95,600),fill=GOLD,width=3)
        d.arc((x-110,560,x+110,665),0,180,fill=GOLD,width=5)
    d.ellipse((537,520,586,569),fill=(163,81,78));d.ellipse((580,520,629,569),fill=(163,81,78))
    d.polygon([(537,548),(629,548),(583,610)],fill=(163,81,78))
    # Feather is a conventional symbol, not a reconstruction of Nauny's tiny Maat figure.
    d.line((1309,603,1364,507),fill=IVORY,width=4)
    for i in range(8):
        x=1321+i*5;y=585-i*9
        d.line((x-23,y-10,x+20,y-14),fill=IVORY,width=3)
    text(d,(468,706),'心臓',48);text(d,(1180,706),'マアトの象徴',48)
    text(d,(601,227),'秩序・倫理的なあり方との釣り合い',40,GOLD)
diagram('balance','心臓の秤量を読み解く',balance,'S04・S05に基づく概念図／羽根や女神像など、表現は資料により異なる')

def roles(d):
    labels=[('アヌビス','秤を読む','死者を守る',190),('トト','結果を記録する','知恵と筆記',720),('オシリス','死者を迎える','死後世界と再生',1250)]
    for name,job,sub,x in labels:
        d.rounded_rectangle((x,263,x+480,735),radius=28,fill=(22,38,51),outline=(94,109,117),width=2)
        text(d,(x+44,318),name,68,GOLD,True)
        d.line((x+44,434,x+430,434),fill=GOLD,width=2)
        text(d,(x+44,489),job,43);text(d,(x+44,581),sub,32,MUTED)
diagram('roles','神々の仕事を分けて見る',roles,'S04・S05／秤量場面を理解するための整理。神の全役割を網羅するものではありません')

def journey(d):
    labels=[('身体を整える','保存と儀礼'),('旅を助ける','呪文と図像'),('試練を越える','心臓の秤量'),('次の存在へ','死後世界への願い')]
    for i,(a,b) in enumerate(labels):
        x=115+i*448
        d.rounded_rectangle((x,342,x+350,648),radius=25,fill=(21,40,52),outline=GOLD,width=2)
        text(d,(x+25,407),a,40,GOLD);text(d,(x+25,514),b,31)
        if i<3:d.polygon([(x+380,471),(x+416,495),(x+380,519)],fill=BLUE)
    text(d,(380,717),'古代の信仰を整理した図です。実在の死後世界を示すものではありません。',28,MUTED)
diagram('journey','死者の旅を支える考え方',journey,'S03・S04・S05／工程や信仰の内容は、時代・資料によって異なります')

def timeline(d):
    d.line((205,448,1700,448),fill=(123,140,154),width=4)
    events=[(260,'中王国','前1981〜1952年頃','王の浮き彫り'),(775,'第3中間期','前1050年頃','ナウニの死者の書'),(1230,'末期〜プトレマイオス期','前343〜30年','犬科の像'),(1650,'ローマ時代','後100〜300年','棺材片')]
    for x,a,b,c in events:
        d.ellipse((x-9,439,x+9,457),fill=GOLD)
        text(d,(x-135,300),a,29,GOLD);text(d,(x-135,511),b,28);text(d,(x-135,574),c,27,MUTED)
    text(d,(465,710),'今回使用する資料の年代比較／間隔は等縮尺ではありません',32,MUTED)
diagram('timeline','古代エジプトには、長い時間がある',timeline,'S01・S04・S07・S09／個別資料の年代。信仰全体の成立・消滅年を表すものではありません')

def evidence(d):
    items=[('01','残された資料','像・パピルス・浮き彫り'),('02','資料の読み取り','博物館の解説・解釈・留保'),('03','再現イメージ','理解を助けるための映像')]
    for i,(num,a,b) in enumerate(items):
        y=230+i*185
        d.rounded_rectangle((130,y,1790,y+142),radius=22,fill=(21,36,49),outline=(65,82,94),width=2)
        text(d,(174,y+34),num,54,GOLD)
        text(d,(300,y+35),a,45);text(d,(1010,y+42),b,34,MUTED)
diagram('evidence','史料・解釈・再現を分ける',evidence,'本動画の制作方針／写真の鮮明さと、歴史解釈の確実さは別です')

im=bg();d=ImageDraw.Draw(im)
text(d,(115,85),'WORLDS OF MYSTERY',31,GOLD)
text(d,(115,203),'アヌビス',120,IVORY,True)
text(d,(115,385),'死者を裁く神か、守る神か',56,GOLD,True)
text(d,(115,539),'史料画像：The Metropolitan Museum of Art / Open Access',33)
text(d,(115,602),'ナレーション：VOICEVOX:雀松朱司',33)
text(d,(115,665),'再現画：AI画像生成　音楽：本試作用のオリジナル音響',33)
text(d,(115,756),'出典・素材の利用条件は付属資料へ',32,MUTED)
im.save(OUT/'credits.png')

# Thumbnail is a native typographic layout over the unchanged AI key art.
im=ImageOps.fit(Image.open(ROOT/'assets/generated/01_anubis_chamber.png').convert('RGB'),(W,H),method=Image.Resampling.LANCZOS)
overlay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(overlay)
d.rectangle((0,0,1020,H),fill=(5,13,23,145))
im=Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(im)
text(d,(110,175),'アヌビス',175,IVORY,True)
text(d,(117,405),'死者を守る神',104,GOLD,True)
text(d,(120,617),'心臓の天秤に込められた意味',46,IVORY)
text(d,(121,917),'WORLDS OF MYSTERY  /  EP001',28,GOLD)
im.save(ROOT/'deliverables/EP001_サムネイル.jpg',quality=94)
small=im.copy();small.thumbnail((336,189));small.save(ROOT/'records/thumbnail_336px.jpg')
print('Visuals ready',len(list(OUT.glob('*.png'))),flush=True)
