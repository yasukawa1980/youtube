"""EP013 measured comparison and review-only crop proposal; no video rendering."""
import csv, itertools, json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from wom13_assets import REPO, MEDIA, TILES, RECORDS, sha, save

OUT=REPO/'new-channel/wom13_素材検証_20261107'
DATA=json.loads((TILES/'取得記録.json').read_text())
ITEMS={i['id']:i for i in DATA['items']}

def crop_native(id, box):
    """Crop decoded verified tiles without loading a 179MB PNG repeatedly."""
    l,t,r,b=map(int,box);out=Image.new('RGB',(r-l,b-t));item=ITEMS[id]
    for tile in item['tiles']:
        x0,y0=max(l,tile['x']),max(t,tile['y'])
        x1,y1=min(r,tile['x']+tile['w']),min(b,tile['y']+tile['h'])
        if x0>=x1 or y0>=y1: continue
        with Image.open(TILES/(id+'_'+item['object'])/tile['file']) as im:
            out.paste(im.crop((x0-tile['x'],y0-tile['y'],x1-tile['x'],y1-tile['y'])),(x0-l,y0-t))
    return out

def pairs(boxes):
    out=[]
    for a,b in itertools.combinations(boxes,2):
        p,q=boxes[a],boxes[b]
        overlap=max(0,min(p[2],q[2])-max(p[0],q[0]))*max(0,min(p[3],q[3])-max(p[1],q[1]))
        smaller=min((p[2]-p[0])*(p[3]-p[1]),(q[2]-q[0])*(q[3]-q[1]))
        out.append({'a':a,'b':b,'overlap_over_smaller':overlap/smaller,'pass_25_percent':overlap/smaller<=.25})
    return out

def main():
    OUT.mkdir(exist_ok=True)
    # Manually identified features, refined in original-size 256px patches.
    landmarks=[
        ('captain_nose',[7199,6201],[5752,4413]),
        ('lieutenant_nose',[8645,6783],[6699,4742]),
        ('girl_nose',[4698,7565],[4174,5230]),
        ('drum_sound_hole_center',[14011,8824],[10089,5993]),
        ('flag_cloth_upper_attachment',[2181,339],[2383,537]),
        ('right_spear_tip',[13910,3679],[10134,2372]),
    ]
    src=np.array([x[1] for x in landmarks],float);dst=np.array([x[2] for x in landmarks],float)
    A=np.zeros((len(src)*2,4));A[::2,0]=src[:,0];A[::2,1]=-src[:,1];A[::2,2]=1
    A[1::2,0]=src[:,1];A[1::2,1]=src[:,0];A[1::2,3]=1
    a,b,tx,ty=np.linalg.lstsq(A,dst.ravel(),rcond=None)[0]
    M=np.array([[a,-b],[b,a]]);pred=src@M.T+[tx,ty];res=np.linalg.norm(pred-dst,axis=1)
    corners=np.array([[0,0],[14645,0],[14645,12158],[0,12158]])@M.T+[tx,ty]
    rows=[{'name':k,'V01_xy':s,'V02_xy':t,'predicted_V02_xy':p.tolist(),'residual_px':float(e),'residual_fraction_of_V02_width':float(e/10449)} for (k,s,t),p,e in zip(landmarks,pred,res)]
    # Difference relative to Claude's approximate left9–10%, right100%, top/bottomfew%.
    # Report actual corners; do not pretend the hand-painted copy is a perfect registration.
    save(RECORDS/'wom13_模写対応点_20261107.json',{
        'method':'unweighted least-squares similarity; no shear, anisotropic scale, or outlier removal',
        'coordinate_basis':'original pixel coordinates; manual landmark selection reviewed at 1:1',
        'landmarks':rows,'matrix_2x3':[[a,-b,tx],[b,a,ty]],'scale':float(math.hypot(a,b)),
        'rotation_degrees':float(math.degrees(math.atan2(b,a))),
        'residual_max_px':float(res.max()),'residual_rms_px':float(np.sqrt((res**2).mean())),
        'residual_max_percent_width':float(res.max()/10449*100),'pass_max_2_percent':bool(res.max()/10449<=.02),
        'V01_corners_in_V02_pixels':corners.tolist(),'V01_corners_in_V02_fraction':(corners/[10449,8183]).tolist(),
        'note':'Manual correspondences and a hand-painted copy imply uncertainty; this is a schematic frame, not an exact reconstruction. No points discarded.'})
    small=crop_native('V02',(0,0,10449,8183));small.thumbnail((1280,1280))
    dr=ImageDraw.Draw(small);factor=small.width/10449
    outline=[tuple(p*factor) for p in corners];dr.line(outline+[outline[0]],fill='#eed4a5',width=2)
    for i,p in enumerate(dst*factor,1):dr.ellipse((p[0]-4,p[1]-4,p[0]+4,p[1]+4),outline='#ffb64d',width=2);dr.text((p[0]+7,p[1]),str(i),fill='#ffffff')
    dr.rectangle((0,0,650,32),fill='#1d1815');dr.text((10,9),'REVIEW ONLY / similarity fit, 6 points / not a restored painting',fill='white')
    small.save(OUT/'D_cut_対応点と枠.jpg',quality=91)
    native=Image.new('RGB',(600,1800),'#181818');dr=ImageDraw.Draw(native)
    for i,(name,*xy) in enumerate(landmarks):
        for j,(x,y) in enumerate(xy):
            patch=crop_native('V01' if j==0 else 'V02',(x-128,y-128,x+128,y+128));xx=j*300+22;yy=i*300+40
            native.paste(patch,(xx,yy));dr.text((j*300+5,i*300+5),name,fill='white');dr.text((j*300+5,i*300+20),f'{x},{y} / original pixel crop',fill='white')
            dr.line((xx+122,yy+128,xx+134,yy+128),fill='#ff5050');dr.line((xx+128,yy+122,xx+128,yy+134),fill='#ff5050')
    # Two review pages preserve 1:1 pixels while keeping each side <=1280.
    native.crop((0,0,600,900)).save(OUT/'対応点_原寸1.jpg',quality=94)
    native.crop((0,900,600,1800)).save(OUT/'対応点_原寸2.jpg',quality=94)
    original={'D1':[.41,.46,.70,.656],'D2':[.03,.40,.30,.583],'D3':[.13,.25,.40,.433],'D4':[.73,.60,1,.783],'D5':[.20,.57,.47,.753],'D6':[.45,.05,.72,.233],'D7':[.53,.66,.795,.84]}
    proposed={k:list(v) for k,v in original.items()}
    # Preserve 16:9 in native pixels. D6 is the sole requested exception, not approved.
    proposed['D2'][1]=.43;proposed['D3'][1]=.27;proposed['D5'][1]=.59
    proposed['D6']=[.42,.075,.78,0]
    for k,v in proposed.items():v[3]=v[1]+(v[2]-v[0])*14645/12158*9/16
    crop_rows=[]
    for k,v in proposed.items():
        delta=[v[i]-original[k][i] for i in range(4)]
        crop_rows.append({'id':k,'requested':original[k],'proposed':v,'edge_deltas':delta,'within_003':max(map(abs,delta))<=.03+1e-9,'source_crop_width_px':(v[2]-v[0])*14645,'source_crop_height_px':(v[3]-v[1])*12158,'max_4k_scale':3840/((v[2]-v[0])*14645)})
    overlap=pairs(proposed)
    save(RECORDS/'wom13_切り出し検証_20261107.json',{'status':'proposal_only_pending_D6_exception','requested_boxes':original,'proposed_boxes':crop_rows,'all_21_overlap_pairs':overlap,'maximum_overlap_fraction':max(x['overlap_over_smaller'] for x in overlap),'all_overlap_pass':all(x['pass_25_percent'] for x in overlap),'D6_issue':'With y1 capped at .263, lower shield/frame remains cut. Proposed wider region exceeds allowed edge adjustments. Do not use without approval.','V02_L_requested':[0,.48,.37,.746],'V02_L_source_width':10449*.37})
    with (OUT/'細部重なり_修正案.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(overlap[0]),lineterminator='\n');w.writeheader();w.writerows(overlap)
    # Concrete before/after card, no colour or brightness changes.
    comparison=Image.new('RGB',(1280,400),'#191919');d=ImageDraw.Draw(comparison)
    for i,(caption,box) in enumerate([('D6 requested',original['D6']),('D6 proposed - approval required',proposed['D6'])]):
        px=[round(v*(14645 if j%2==0 else 12158)) for j,v in enumerate(box)];im=crop_native('V01',px);im.thumbnail((640,360));comparison.paste(im,(i*640,40));d.text((i*640+10,10),caption,fill='white')
    comparison.save(OUT/'D6_現指定と修正案.jpg',quality=94)
    # Pair chart for all requested crops, to let Claude inspect content and omissions.
    contact=Image.new('RGB',(1280,4*395),'#151515');d=ImageDraw.Draw(contact)
    for i,(k,v) in enumerate(proposed.items()):
        px=[round(c*(14645 if j%2==0 else 12158)) for j,c in enumerate(v)];im=crop_native('V01',px);im.thumbnail((640,360));x=(i%2)*640;y=(i//2)*395
        contact.paste(im,(x,y+30));d.text((x+10,y+8),k+(' / proposed exception' if k=='D6' else ' / candidate'),fill='white')
    contact.thumbnail((1280,1280));contact.save(OUT/'細部7枠_修正案.jpg',quality=93)
    print('fit max%',res.max()/10449*100,'proposed overlap max',max(x['overlap_over_smaller'] for x in overlap),'D6 approval needed',flush=True)

if __name__=='__main__':main()
