"""既存犬3素材を局所合成してから1.4倍。検品用のみ。"""
import importlib.util,json,subprocess
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
S=importlib.util.spec_from_file_location('prepare',Path(__file__).with_name('iro18_手直し試作_20261018.py'));m=importlib.util.module_from_spec(S);S.loader.exec_module(m)
OUT=m.OUT;FF='/opt/homebrew/bin/ffmpeg';W,H=1920,1080
FONT=ImageFont.truetype('/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',18)
def encoder(path,w,h):
 return subprocess.Popen([FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r','24','-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
def frames(path):
 cap=cv2.VideoCapture(str(path))
 for k in range(192):
  ok,frame=cap.read();assert ok,(path,k)
  yield cv2.cvtColor(cv2.resize(frame,(W,H),interpolation=cv2.INTER_LANCZOS4),cv2.COLOR_BGR2RGB)
 cap.release()
def main():
 still=np.array(Image.open(OUT/'18_start_編む手元_Kling用.png')).astype(np.float32)
 dm=np.zeros((H,W),np.float32);cv2.ellipse(dm,(409,862),(241,154),0,0,360,1,-1);dm=cv2.GaussianBlur(dm,(0,0),8)*(dm>0);dm=dm[:,:,None]
 baselist=list(frames(m.OLD/'Kling素材/B1.mp4'))
 enlarge_mask=np.array(m.dog_mask(),np.float32)[:,:,None]/255
 report={}
 for name,source in [('寝息','B1'),('C_あくび','C'),('D_走る夢','D_v2')]:
  full=encoder(OUT/f'犬1.4倍_{name}_8秒.mp4',W,H)
  short=encoder(OUT/f'犬1.4倍_{name}_縦切抜き検品.mp4',608,1080)
  sheet=Image.new('RGB',(1280,6*193),(24,24,24));draw=ImageDraw.Draw(sheet)
  union=np.zeros((H,W),bool);first=None;max_leg_diff=0;short_left=108 if source=='D_v2' else 94;outside_crop=[]
  for k,raw in enumerate(frames(m.OLD/f'Kling素材/{source}.mp4')):
   base=still*(1-dm)+baselist[k]*dm
   if source!='B1':
    a=min(1,(k+1)/12,(192-k)/12);base=base*(1-dm*a)+raw*dm*a
   before=np.uint8(np.clip(base+.5,0,255))
   zoom=Image.fromarray(before).resize((2688,1512),Image.Resampling.LANCZOS).crop((164,400,2084,1480))
   after=np.uint8(np.clip(np.array(zoom)*enlarge_mask+before*(1-enlarge_mask)+.5,0,255))
   if first is None:first=after.copy()
   motion=np.max(np.abs(after.astype(np.int16)-first.astype(np.int16)),axis=2)>16
   # Movement only in the dog neighborhood; static pixels elsewhere are irrelevant.
   motion[:620]=False;motion[:,820:]=False;union|=motion
   outside_crop.append(int(motion[:,:short_left].sum()+motion[:,short_left+608:].sum()))
   diff=np.max(np.abs(after.astype(np.int16)-before.astype(np.int16)),axis=2)
   max_leg_diff=max(max_leg_diff,int(diff[780:1080,740:850].max()))
   full.stdin.write(after.tobytes());short.stdin.write(after[:,short_left:short_left+608].copy().tobytes())
   if k%8==0:
    n=k//8;x=(n%4)*320;y=(n//4)*193
    tile=Image.fromarray(after).crop((0,620,820,1080)).resize((320,180),Image.Resampling.LANCZOS)
    sheet.paste(tile,(x,y));draw.text((x+4,y+172),f'{k/24:.2f}s',font=FONT,fill='white',stroke_width=1,stroke_fill='black')
  for enc in (full,short):enc.stdin.close();assert enc.wait()==0
  ys,xs=np.where(union)
  sheet.save(OUT/f'犬1.4倍_{name}_3fps.jpg',quality=90)
  report[name]={'source':str(m.OLD/f'Kling素材/{source}.mp4'),'source_sha256':m.sha(m.OLD/f'Kling素材/{source}.mp4'),'frames':192,'fps':24,'seconds':8,'enlargement_after_event_composite':True,'motion_bbox_threshold16':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'short_crop':[short_left,0,short_left+608,1080],'outside_short_motion_pixels_max':max(outside_crop),'table_leg_region_max_pixel_delta_due_to_scale':max_leg_diff}
  print(name,report[name],flush=True)
 (OUT/'犬拡大_検証.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
