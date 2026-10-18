"""承認済みの試作1・2の境界だけを修正。完成品や投稿用には触れない。"""
from pathlib import Path
import argparse, importlib.util, json, subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw

HERE=Path(__file__).resolve().parent
def load(name,file):
    s=importlib.util.spec_from_file_location(name,HERE/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('prep','iro18_手直し試作_20261018.py')
dog=load('dog','iro18_犬拡大検品_20261018.py')
qc=load('qc','iro18_編み物試作を検品_20261018.py')
PERSON=[(1102,37),(1372,37),(1440,201),(1420,392),(1556,433),(1635,585),
        (1560,599),(1520,623),(1503,659),(1511,704),(1511,730),(1390,735),
        (1320,750),(1220,850),(1050,850),(935,825),(810,797),(810,742),
        (887,663),(900,550),(943,493),(1075,408)]
# Object ROI is fixed from the reference image, independently of the composite mask.
SCARF=[(843,766),(980,705),(1070,645),(1287,630),(1310,700),(1285,746),
       (1199,831),(1090,826),(1015,813),(916,810),(841,788)]
THREAD=[(1312,551),(1330,594),(1360,645),(1396,680),(1443,696),(1502,700)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--take',type=int,choices=[1,2],required=True)
    ap.add_argument('--old-root',type=Path,default=m.OLD);a=ap.parse_args()
    out=m.OUT;review=HERE/'iro18_手直し_20261018';prefix=f'試作{a.take}_境界修正'
    raw=out/f'Kling_編み物試作{a.take}_原本.mp4';frames=list(dog.frames(raw))
    rawprobe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(raw)]))
    v=next(s for s in rawprobe['streams']if s['codec_type']=='video')
    assert (v['width'],v['height'],v['r_frame_rate'])==(1920,1080,'24/1')
    assert not any(s['codec_type']=='audio'for s in rawprobe['streams'])
    ref=np.array(Image.open(out/'18_start_編む手元_Kling用.png').convert('RGB'))
    mask=np.zeros((1080,1920),np.uint8);cv2.fillPoly(mask,[np.array(PERSON,np.int32)],255)
    support=mask>0;alpha=cv2.GaussianBlur(mask.astype(np.float32)/255,(0,0),18)*(support);alpha=alpha[:,:,None]
    roi=np.zeros_like(mask);cv2.fillPoly(roi,[np.array(SCARF,np.int32)],255)
    cv2.polylines(roi,[np.array(THREAD,np.int32)],False,255,12)
    old=np.zeros_like(mask);cv2.fillPoly(old,[np.array(qc.PERSON,np.int32)],255)
    img=Image.fromarray(ref);d=ImageDraw.Draw(img)
    d.line(qc.PERSON+[qc.PERSON[0]],fill='#ff6868',width=3)
    d.line(PERSON+[PERSON[0]],fill='#f8f46a',width=3)
    img.crop((740,430,1810,920)).resize((1280,586)).save(review/'合成境界_旧赤と修正黄.jpg',quality=91)
    Image.fromarray(mask).save(out/'女性映像_房と糸まで_マスク.png')
    Image.fromarray(roi).save(out/'マフラーと糸_検査ROI.png')
    dm=np.zeros((1080,1920),np.float32);cv2.ellipse(dm,(409,862),(241,154),0,0,360,1,-1)
    dm=(cv2.GaussianBlur(dm,(0,0),8)*(dm>0))[:,:,None]
    dest=out/f'{prefix}_犬1.4倍_8秒.mp4';enc=dog.encoder(dest,1920,1080)
    before=[];outside=[];alloutside=[];legacy_outside=[];bgdiff=0;adj=[];camera=[];encoded=[];first=frames[0].astype(np.int16)
    patch=cv2.cvtColor(frames[0],cv2.COLOR_RGB2GRAY)[80:650,80:760].astype(np.float32)
    for k,(frame,df) in enumerate(zip(frames,dog.frames(a.old_root/'Kling素材/B1.mp4'))):
        change=np.max(np.abs(frame.astype(np.int16)-first),axis=2)>12
        before.append(int(np.count_nonzero(change&(roi>0)&(old==0))))
        outside.append(int(np.count_nonzero(change&(roi>0)&~support)))
        alloutside.append(int(np.count_nonzero(change&~support)))
        legacy_outside.append(int(np.count_nonzero((change&~support)[550:850,950:1510])))
        fixed=np.uint8(np.clip(ref*(1-alpha)+frame*alpha+.5,0,255))
        bgdiff=max(bgdiff,int(np.count_nonzero(np.any(fixed!=ref,axis=2)&~support)))
        gray=cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)[80:650,80:760].astype(np.float32)
        xy,response=cv2.phaseCorrelate(patch,gray);camera.append(list(map(float,xy)))
        if k:adj.append(float(np.abs(frame.astype(np.float32)-frames[k-1]).mean(axis=2)[support].mean()))
        combined=np.uint8(np.clip(fixed*(1-dm)+df*dm+.5,0,255))
        final=np.array(m.enlarge_dog(combined));enc.stdin.write(final.tobytes());encoded.append(final)
    enc.stdin.close();assert enc.wait()==0
    seam=float(np.abs(frames[-1].astype(np.float32)-frames[0]).mean(axis=2)[support].mean());median=float(np.median(adj))
    for half,indices in [('前半',list(range(0,96,4))),('後半',list(range(96,192,4)))]:
        qc.sheet(frames,indices,(900,450,1530,700),4,320,review/f'{prefix}_手元6fps_{half}.jpg')
        qc.sheet(encoded,indices,(800,670,1330,865),4,320,review/f'{prefix}_房6fps_{half}.jpg')
    qc.sheet(encoded,list(range(0,192,4)),(1300,560,1520,745),6,200,review/f'{prefix}_糸6fps.jpg')
    qc.sheet(frames,list(range(0,192,8)),(1090,275,1350,460),6,200,review/f'{prefix}_顔3fps.jpg')
    qc.sheet(frames,list(range(0,192,8)),(1110,305,1260,355),6,200,review/f'{prefix}_目元3fps.jpg')
    for n in range(4):qc.sheet(frames,list(range(n*48,(n+1)*48)),(1110,305,1260,355),6,200,review/f'{prefix}_目元全コマ{n+1}.jpg')
    qc.sheet(frames,[0,1,190,191],(900,450,1530,700),2,600,review/f'{prefix}_頭尻.jpg')
    Image.fromarray(encoded[96]).resize((1280,720)).save(review/f'{prefix}_全体4秒.jpg',quality=91)
    lst=out/f'{prefix}_concat.txt';lst.write_text(''.join(f"file '{dest.name}'\n"for _ in range(3)))
    loop=out/f'{prefix}_3周24秒.mp4';subprocess.run([dog.FF,'-y','-v','error','-f','concat','-safe','0','-i',str(lst),'-c','copy',str(loop)],check=True)
    for p in [raw,dest,loop]:subprocess.run([dog.FF,'-v','error','-xerror','-i',str(p),'-f','null','-'],check=True)
    report={'take':a.take,'raw':str(raw),'raw_sha256':m.sha(raw),'output':str(dest),'loop24s':str(loop),
            'raw_video_parameters':{k:v.get(k)for k in ['codec_name','width','height','r_frame_rate','nb_frames','duration']},'raw_audio_streams':0,
            'frames':192,'fps':24,'seconds':8,'same_polygon_for_both_takes':PERSON,'blur_sigma_px':18,
            'roi_scarf':SCARF,'roi_thread':THREAD,'roi_thread_stroke_px':12,
            'raw_change_threshold_rgb_max':12,'object_roi_outside_old_mask_max':max(before),
            'object_roi_outside_new_mask_max':max(outside),'object_roi_outside_new_mask_per_frame':outside,
            'raw_whole_frame_outside_new_mask_max':max(alloutside),
            'legacy_rect_roi':[950,550,1510,850],'legacy_rect_outside_new_mask_max':max(legacy_outside),
            'measurement_scope':'0画素の判定はマフラー・房・接続糸の固定ROI。全画面の原素材変化は背景等を含むため別掲。',
            'outside_composite_mask_changed_pixels_before_dog_and_encode':bgdiff,
            'raw_adjacent_median_mad':median,'raw_seam_mad':seam,'seam_to_adjacent_ratio':seam/median,
            'background_phase_max_abs_xy':np.max(np.abs(camera),axis=0).tolist(),
            'crossfade':False,'eye_patch':False,'head_retiming':False,'dog_scale':1.4,'decode_ok':True}
    (review/f'{prefix}_検証.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    assert bgdiff==0
    print(json.dumps({k:v for k,v in report.items()if not isinstance(v,list)},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
