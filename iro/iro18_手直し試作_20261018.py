"""IRO18 検品ゲート用。既存完成品は変更せず試作だけ出力する。"""
import argparse, hashlib, json
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
REPO=Path(__file__).resolve().parents[1]
OLD=REPO/'bgm/IRO/IRO18_毛糸の季節がやってきた'
OUT=Path('/Users/ryo/Desktop/BGM/IRO/Chill/18_毛糸の季節がやってきた/手直し_20261018')
POLYGON=[(783,585),(793,520),(821,470),(867,454),(893,404),(930,389),(1010,390),(1040,418),(1110,418),(1160,431),(1250,440),(1280,478),(1328,517),(1321,583),(1305,600),(1310,632),(1220,650),(1145,660),(1020,647),(960,620),(900,604)]
def sha(p):
 return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dog_mask():
 m=Image.new('L',(1920,1080));ImageDraw.Draw(m).ellipse((190,770,640,1030),fill=255)
 m=m.filter(ImageFilter.GaussianBlur(28))
 return m.resize((2688,1512),Image.Resampling.LANCZOS).crop((164,400,2084,1480))
def enlarge_dog(frame):
 im=Image.fromarray(frame) if isinstance(frame,np.ndarray) else frame
 assert im.size==(1920,1080)
 zoom=im.resize((2688,1512),Image.Resampling.LANCZOS).crop((164,400,2084,1480))
 return Image.composite(zoom,im,dog_mask())
def prepare(generated):
 OUT.mkdir(parents=True,exist_ok=True)
 original=Image.open(OLD/'開始画像/18_start.png').convert('RGB')
 candidate=Image.open(generated).convert('RGB')
 assert candidate.size==original.size==(1672,941),(candidate.size,original.size)
 candidate.save(OUT/'手元描き直し_生成原本.png')
 m=Image.new('L',original.size);d=ImageDraw.Draw(m);d.polygon(POLYGON,fill=255)
 # 手元から移した旧棒針の跡だけを含める。机全体は描き替えない。
 d.line([(1085,630),(1438,682)],fill=255,width=30)
 d.line([(1055,642),(1395,694)],fill=255,width=28)
 for x,y in [(1085,630),(1438,682),(1055,642),(1395,694)]:
  d.ellipse((x-21,y-21,x+21,y+21),fill=255)
 support=np.array(m)>0
 distance=cv2.distanceTransform(support.astype(np.uint8),cv2.DIST_L2,5)
 alpha=np.uint8(np.clip(distance/10,0,1)*255)
 alpha[~support]=0
 mask=Image.fromarray(alpha);merged=Image.composite(candidate,original,mask)
 changed=np.any(np.array(merged)!=np.array(original),axis=2)
 assert np.count_nonzero(changed&~support)==0
 merged.save(OUT/'18_start_編む手元_1672.png');mask.save(OUT/'手元変更マスク_1672.png')
 full=merged.resize((1920,1080),Image.Resampling.LANCZOS)
 full.save(OUT/'18_start_編む手元_Kling用.png')
 original.resize((1920,1080),Image.Resampling.LANCZOS).save(OUT/'18_start_旧_1920.png')
 enlarge_dog(full).save(OUT/'18_start_編む手元_犬1.4倍.png')
 dog_mask().save(OUT/'犬1.4倍_合成マスク.png')
 report={'original':str(OLD/'開始画像/18_start.png'),'original_sha256':sha(OLD/'開始画像/18_start.png'),'generated':str(generated),'generated_sha256':sha(generated),'polygon_original_1672':POLYGON,'needle_removal_lines_original_1672':[[1085,630,1438,682,30],[1055,642,1395,694,28]],'changed_pixels':int(changed.sum()),'outside_mask_changed_pixels':int(np.count_nonzero(changed&~support)),'dog_scale':1.4,'dog_anchor_1920':[410,1000],'dog_crop_offset':[164,400],'kling_input_dog':'旧サイズのまま。既存犬映像合成後に拡大するため','kling_input':str(OUT/'18_start_編む手元_Kling用.png')}
 (OUT/'開始画像_検証.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--generated',required=True);a=p.parse_args();prepare(a.generated)
