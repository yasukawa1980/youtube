"""v07: tightly crop the three gods and enlarge nine picture diagrams.

Run with WOM_EPISODE_ROOT (new v07), WOM_PREVIOUS_ROOT (v06), and
WOM_SOURCE_ROOT (original materials). Keeps v06 media and audio untouched.
"""
import argparse, os, shutil
from pathlib import Path
os.environ['WOM_VERSION']='v07'
os.environ['WOM_PREVIOUS_VERSION']='v06'
os.environ['WOM_SUBTITLE_SAFE']='1'
import wom01_minimal_text as m
from PIL import Image, ImageDraw, ImageOps

TARGETS={'N03','N07','N08','N09','N10','N17','N18','N22','N27'}
CROPS={
 'anubis':('548344',[1530,1490,2450,2430],'Canid-headed figure kneeling by the scales'),
 'thoth':('552247',[1265,425,1550,970],'Ibis-headed figure before Osiris, holding palette and pen'),
 'osiris':('548344',[2810,1010,3625,2415],'Seated figure at right, white crown and crook'),
}
SETS={'evidence':['met_544075','met_557830','hero'],
      'timeline':['met_544206','met_548344','met_552247'],
      'journey':['linen','met_548344','met_548344_detail'],
      'human_work':['linen','met_590939'],
      'roles':['anubis','thoth','osiris'],
      'protect':['met_544075','linen','met_548344_detail']}

def panel(im,key,box):
    if key in CROPS:
        oid,crop,identification=CROPS[key]
        rec={'key':key,'source':f'assets/museum/met_{oid}.jpg','crop_pixels':crop,'label':'Museum object',
             'identification':identification,'reference':f'https://www.metmuseum.org/art/collection/search/{oid}',
             'original_size':list(Image.open(m.SOURCE/f'assets/museum/met_{oid}.jpg').size)}
        src=Image.open(m.SOURCE/rec['source']).convert('RGB').crop(crop)
    else:
        src,rec=m.asset(key);m.ASSETS.pop()
    x,y,w,h=box;art=ImageOps.contain(src,(w,h),Image.Resampling.LANCZOS)
    position=(x+(w-art.width)//2,y+(h-art.height)//2)
    im.paste(art,position)
    rec={k:rec[k] for k in ['key','source','crop_pixels','label','identification','reference','original_size'] if k in rec};rec['panel_box']=list(box);rec['display_bbox']=[*position,position[0]+art.width,position[1]+art.height]
    m.ASSETS.append(rec)
    return rec

def card(key):
    m.TEXTS=[];m.ASSETS=[]
    im=Image.new('RGB',(m.W,m.H),m.BG);d=ImageDraw.Draw(im);m.header(im,m.source_line())
    keys=SETS[key];n=len(keys);centers=[360,960,1560] if n==3 else [560,1360]
    # Keep the approved names at their original centers and vertical positions.
    if key=='roles':centers=[420,960,1500]
    height=340 if key=='roles' else 345 if key=='timeline' else 440
    width=470 if key=='roles' else 564 if n==3 else 768
    for i,(k,cx) in enumerate(zip(keys,centers)):
        rec=panel(im,k,(cx-width//2,220,width,height))
        label_y=565 if key=='roles' else 575 if key=='timeline' else 666
        m.label(im,(cx,label_y),rec['label'],28,True)
        if key=='timeline':m.text(im,(cx,614),['1981–1952','1050','100–300'][i],32,center=True)
        if key=='roles':
            m.text(im,(cx,607),['Anubis','Thoth','Osiris'][i],43,serif=True,center=True)
            m.text(im,(cx,660),['アヌビス','トト','オシリス'][i],26,m.MUTED,center=True)
    if key=='journey':
        for x in [660,1260]:
            d.line((x-14,435,x+14,435),fill=m.GOLD,width=5)
            d.line((x+14,435,x+4,425),fill=m.GOLD,width=5);d.line((x+14,435,x+4,445),fill=m.GOLD,width=5)
    if key=='human_work':
        d.line((950,435,970,435),fill=m.GOLD,width=5);d.line((960,425,960,445),fill=m.GOLD,width=5)
    if key=='timeline':
        d.line((100,666,1820,666),fill=m.GOLD,width=4);d.line((1260,656,1260,700),fill=m.GOLD,width=3)
        m.text(im,(700,674),'BCE｜紀元前',23,m.MUTED,center=True);m.text(im,(1560,674),'CE｜紀元後',23,m.MUTED,center=True)
    return im,m.TEXTS.copy(),m.ASSETS.copy()

def prepare():
    m.prepare()
    m.save(m.ROOT/'records/revision_request.json',{
      'version':'v07','source_root':str(m.PREV),'request':'new-channel/wom01_Claude確認_v06_20261021.md',
      'audio_regenerated':False,'srt_regenerated':False,'thumbnail_changed':False,'new_images_generated':False,
      'v06_preserved':True,'target_segments':sorted(TARGETS),
      'scaling':'General photo widths 1.2x, height bounded to 440px; labels 23 to 28px. Timeline/roles height bounded to preserve dates/names and y<=700. Tight role crops enlarge figures substantially.'})

def compose():
    old=m.read(m.PREV/'records/visual_manifest.json');shots=[];changed=[]
    for s in old['shots']:
        r=dict(s)
        target=s['segment_id'] in TARGETS and s['key'] in SETS
        if target:
            im,texts,assets=card(s['key']);im.save(m.ROOT/r['file'])
            r.update(screen_text=texts,components=assets,text_bottom_px=max(t['bbox'][3] for t in texts))
            r['picture_and_text_bottom_px']=max(r['text_bottom_px'],max(a['display_bbox'][3] for a in assets),700 if s['key']=='timeline' else 0)
            assert r['picture_and_text_bottom_px']<=700
            r['changed_in_v07']=True;changed.append(s['segment_id'])
        else:
            shutil.copy2(m.PREV/s['file'],m.ROOT/s['file'])
            if s.get('end_file'):shutil.copy2(m.PREV/s['end_file'],m.ROOT/s['end_file'])
            r['changed_in_v07']=False
        shots.append(r)
    assert sorted(changed)==sorted(TARGETS),changed
    m.save(m.ROOT/'records/visual_manifest.json',{**old,'version':'v07','shots':shots,'all_text_bottom_max':max(s['text_bottom_px'] for s in shots),'changed_shots':len(changed),'unchanged_shots':55-len(changed)})
    # Reuse the 46 unchanged encoded shots. Copies are independent, never overwritten in v06.
    encoded=m.read(m.PREV/'records/render_shots.json')
    for s,o in zip(shots,encoded):
        if not s['changed_in_v07']:
            path=m.PREV/o['encoded_file'];dest=m.ROOT/o['encoded_file']
            shutil.copy2(path,dest);shutil.copy2(path.with_suffix('.json'),dest.with_suffix('.json'))
    print('COMPOSED v07',len(changed),'changed /',55-len(changed),'reused',flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','visuals','pictures','package','layout','review-render','review-verify']);a=p.parse_args()
    if a.stage=='prepare':prepare()
    elif a.stage=='visuals':compose()
    elif a.stage=='pictures':m.pictures()
    elif a.stage=='package':m.package()
    elif a.stage=='layout':m.layout()
    else:m.review(a.stage)
if __name__=='__main__':main()
