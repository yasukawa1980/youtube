"""Kling 1本目だけを検品。追加生成・完成品差替えは行わない。"""
import importlib.util,json,subprocess
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
S=importlib.util.spec_from_file_location('prepare',Path(__file__).with_name('iro18_手直し試作_20261018.py'));m=importlib.util.module_from_spec(S);S.loader.exec_module(m)
S2=importlib.util.spec_from_file_location('dogs',Path(__file__).with_name('iro18_犬拡大検品_20261018.py'));dog=importlib.util.module_from_spec(S2);S2.loader.exec_module(dog)
OUT=m.OUT;REVIEW=m.REPO/'iro/iro18_手直し_20261018';REVIEW.mkdir(parents=True,exist_ok=True)
PERSON=[(1102,37),(1372,37),(1440,201),(1420,392),(1556,433),(1650,640),(1582,740),(1456,763),(1315,722),(1110,730),(947,752),(887,663),(900,550),(943,493),(1075,408)]
FONT=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',16)
def sheet(frames,indices,box,cols,tilew,path):
 w,h=box[2]-box[0],box[3]-box[1];th=round(h*tilew/w);cellh=th+22
 im=Image.new('RGB',(cols*tilew,((len(indices)+cols-1)//cols)*cellh),(24,24,24));d=ImageDraw.Draw(im)
 for n,k in enumerate(indices):
  x=n%cols*tilew;y=n//cols*cellh
  im.paste(Image.fromarray(frames[k]).crop(box).resize((tilew,th),Image.Resampling.LANCZOS),(x,y));d.text((x+5,y+th+1),f'{k/24:.3f}s / #{k}',font=FONT,fill='white')
 im.save(path,quality=92)
def main():
 raw=OUT/'Kling_編み物試作1_原本.mp4';frames=list(dog.frames(raw));ref=np.array(Image.open(OUT/'18_start_編む手元_Kling用.png'))
 mask=np.zeros((1080,1920),np.uint8);cv2.fillPoly(mask,[np.array(PERSON,np.int32)],255)
 alpha=cv2.GaussianBlur(mask.astype(np.float32)/255,(0,0),7)*(mask>0);alpha=alpha[:,:,None];support=mask>0
 Image.fromarray(mask).save(OUT/'女性映像_合成範囲.png')
 # 既存の犬の寝息を局所合成した後、設計どおり犬を拡大。
 dm=np.zeros((1080,1920),np.float32);cv2.ellipse(dm,(409,862),(241,154),0,0,360,1,-1);dm=cv2.GaussianBlur(dm,(0,0),8)*(dm>0);dm=dm[:,:,None]
 base_dog=dog.frames(m.OLD/'Kling素材/B1.mp4')
 enc=dog.encoder(OUT/'編み物試作1_背景固定_犬1.4倍_8秒.mp4',1920,1080)
 encoded=[];adj=[];shift=[];raw_out=[];outside=0;first=frames[0].astype(np.int16)
 # Camera estimate uses a fixed cabinet/wall patch, excluding woman and dog.
 patch0=cv2.cvtColor(frames[0],cv2.COLOR_RGB2GRAY)[80:650,80:760].astype(np.float32)
 for k,(frame,df) in enumerate(zip(frames,base_dog)):
  fixed=np.uint8(np.clip(ref*(1-alpha)+frame*alpha+.5,0,255))
  outside=max(outside,int(np.count_nonzero(np.any(fixed!=ref,axis=2)&~support)))
  raw_out.append(int(np.count_nonzero((np.max(np.abs(frame.astype(np.int16)-first),axis=2)>12)&~support)))
  gray=cv2.cvtColor(frame,cv2.COLOR_RGB2GRAY)[80:650,80:760].astype(np.float32)
  xy,response=cv2.phaseCorrelate(patch0,gray);shift.append([float(xy[0]),float(xy[1]),float(response)])
  if k:adj.append(float(np.abs(frame.astype(np.float32)-frames[k-1]).mean(axis=2)[support].mean()))
  combined=np.uint8(np.clip(fixed*(1-dm)+df*dm+.5,0,255));final=np.array(m.enlarge_dog(combined));enc.stdin.write(final.tobytes());encoded.append(final)
 enc.stdin.close();assert enc.wait()==0
 seam=float(np.abs(frames[-1].astype(np.float32)-frames[0]).mean(axis=2)[support].mean())
 median=float(np.median(adj));ratio=seam/median if median else None
 sheet(frames,list(range(0,96,4)),(900,450,1530,700),4,320,REVIEW/'手元_6fps_前半.jpg')
 sheet(frames,list(range(96,192,4)),(900,450,1530,700),4,320,REVIEW/'手元_6fps_後半.jpg')
 sheet(frames,list(range(0,192,8)),(1090,275,1350,460),6,200,REVIEW/'顔_3fps.jpg')
 sheet(frames,list(range(0,192,8)),(1110,305,1260,355),6,200,REVIEW/'目元_3fps.jpg')
 for n in range(4):
  sheet(frames,list(range(n*48,(n+1)*48)),(1110,305,1260,355),6,200,REVIEW/f'目元_全コマ_{n+1}.jpg')
 sheet(frames,[0,1,190,191],(900,450,1530,700),2,600,REVIEW/'手元_頭尻比較.jpg')
 Image.fromarray(encoded[96]).resize((1280,720),Image.Resampling.LANCZOS).save(REVIEW/'編み物_犬1.4倍_4秒.jpg',quality=90)
 for path in (raw,OUT/'編み物試作1_背景固定_犬1.4倍_8秒.mp4'):
  subprocess.run([dog.FF,'-v','error','-i',str(path),'-f','null','-'],check=True)
 (OUT/'ループ検品用_concat.txt').write_text(''.join("file '編み物試作1_背景固定_犬1.4倍_8秒.mp4'\n" for _ in range(3)))
 subprocess.run([dog.FF,'-y','-v','error','-f','concat','-safe','0','-i',str(OUT/'ループ検品用_concat.txt'),'-c','copy',str(OUT/'編み物試作1_3周つなぎ確認_24秒.mp4')],check=True)
 probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(raw)]))
 report={'raw_video':str(raw),'raw_sha256':m.sha(raw),'raw_probe':probe,'sample_frames':192,'sample_seconds':8,'sample_fps':24,'person_polygon':PERSON,'background_restored_outside_mask_changed_pixels_before_encode':outside,'raw_outside_person_changed_pixels_max_threshold12':max(raw_out),'raw_person_mad_adjacent_median':median,'raw_person_mad_seam':seam,'raw_seam_to_adjacent_ratio':ratio,'raw_background_phase_shift_max_abs_xy':np.max(np.abs(np.array(shift)[:,:2]),axis=0).tolist(),'raw_background_phase_response_min':min(x[2] for x in shift),'camera_estimate_note':'原素材のキャビネット・壁領域で位相相関。出力背景は静止画へ復元。','frame_sheets':{'hands_fps':6,'hands_frames':48,'face_fps':3,'face_frames':24,'eyes_fps':3,'eyes_frames':24},'decode_ok':True,'decision':'Claude検品待ち。追加生成なし。長時間本編・投稿用差替えなし。'}
 (REVIEW/'Kling試作1_検証.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in report.items() if k not in ('raw_probe','person_polygon')},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()
