"""試作1本の検品用JPGと記録だけを梱包。投稿用へは書き込まない。"""
import importlib.util,json,shutil
from pathlib import Path
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
S=importlib.util.spec_from_file_location('prepare',Path(__file__).with_name('iro18_手直し試作_20261018.py'));m=importlib.util.module_from_spec(S);S.loader.exec_module(m)
OUT=m.OUT;REVIEW=m.REPO/'iro/iro18_手直し_20261018';REVIEW.mkdir(parents=True,exist_ok=True)
JP='/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc';AV='/System/Library/Fonts/Avenir Next.ttc'
FONT=ImageFont.truetype(JP,20)
def thumbnail():
 im=Image.open(OUT/'18_start_編む手元_犬1.4倍.png').convert('RGBA').resize((1280,720),Image.Resampling.LANCZOS)
 yy,xx=np.mgrid[:720,:1280];alpha=np.clip((690-xx)/180,0,1)*np.clip(np.minimum(yy+50,490-yy)/95,0,1)*175
 shade=Image.new('RGBA',im.size,(31,12,21,0));shade.putalpha(Image.fromarray(alpha.astype('uint8')));im=Image.alpha_composite(im,shade)
 layer=Image.new('RGBA',im.size);d=ImageDraw.Draw(layer);x=48
 d.rounded_rectangle((x,65,550,118),radius=26,fill=(116,51,72,255));d.text((x+23,70),'BURGUNDY  |  Acoustic Chill',font=ImageFont.truetype(AV,28,index=2),fill='white')
 for y,t in [(151,'毛糸の季節が、'),(249,'やってきた。')]:d.text((x-2,y),t,font=ImageFont.truetype(JP,76),fill='white')
 d.text((x,363),'編み物BGM 2時間',font=ImageFont.truetype(JP,60),fill='#FFD75A')
 shadow=Image.new('RGBA',im.size,(15,7,10,0));shadow.putalpha(layer.getchannel('A').filter(ImageFilter.GaussianBlur(6)))
 out=Image.alpha_composite(Image.alpha_composite(im,shadow),layer).convert('RGB');out.save(OUT/'iro18_サムネ_試作.png');out.save(REVIEW/'iro18_サムネ_試作.jpg',quality=90)
 out.resize((168,94),Image.Resampling.LANCZOS).save(REVIEW/'iro18_サムネ_168px.jpg',quality=95)
 return out

def main():
 thumb=thumbnail()
 for name in ['開始画像_検証.json','犬拡大_検証.json']:
  shutil.copy2(OUT/name,REVIEW/name)
 for name in ['寝息','C_あくび','D_走る夢']:
  im=Image.open(OUT/f'犬1.4倍_{name}_3fps.jpg');im.save(REVIEW/f'犬1.4倍_{name}_3fps.jpg',quality=85)
 Image.open('/private/tmp/iro18_kling_completed.png').convert('RGB').resize((1280,678),Image.Resampling.LANCZOS).save(REVIEW/'Kling試作1_完成画面.jpg',quality=85)
 shutil.copy2(m.OLD/'手直し_20261018/手直し設計_Codexへ.md',REVIEW/'手直し設計_Codexへ.md')
 board=Image.new('RGB',(1280,1240),(24,24,24));d=ImageDraw.Draw(board)
 def tile(path,box,label):
  x,y,w,h=box;im=Image.open(path).convert('RGB');im.thumbnail((w,h-28),Image.Resampling.LANCZOS);board.paste(im,(x,y+28));d.text((x+6,y+3),label,font=FONT,fill='white')
 tile(m.OLD/'開始画像/18_start.png',(0,0,640,388),'旧：手を添える／犬は元サイズ')
 tile(OUT/'18_start_編む手元_犬1.4倍.png',(640,0,640,388),'試作：編む手元／犬1.4倍')
 tile(REVIEW/'iro18_サムネ_試作.jpg',(0,388,640,388),'サムネ試作：題・帯・小見出しは維持')
 small=Image.open(REVIEW/'iro18_サムネ_168px.jpg');board.paste(small,(680,430));d.text((680,398),'168px（実寸）',font=FONT,fill='white')
 hand=Image.open(OUT/'18_start_編む手元_Kling用.png').crop((900,450,1530,700));hand.thumbnail((590,240),Image.Resampling.LANCZOS);board.paste(hand,(665,530));d.text((875,490),'腕・手元だけを描き直し',font=FONT,fill='white')
 for i,(key,label) in enumerate([('C_あくび','あくび：4秒'),('D_走る夢','走る夢：4秒')]):
  cap=cv2.VideoCapture(str(OUT/f'犬1.4倍_{key}_8秒.mp4'));cap.set(cv2.CAP_PROP_POS_FRAMES,96);ok,bgr=cap.read();cap.release();assert ok
  im=Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).crop((0,620,850,1080));im.thumbnail((630,340),Image.Resampling.LANCZOS)
  board.paste(im,(i*640,820));d.text((i*640+6,787),label+'／敷物と脚の境界',font=FONT,fill='white')
 d.text((20,1190),'試作1本で停止・Claude検品待ち。手元48コマ／顔24コマは別紙。投稿用の差替えなし。',font=FONT,fill='#FFD75A')
 board.save(REVIEW/'Claude検品用_見本.jpg',quality=88)
 files=[]
 for p in sorted(REVIEW.glob('*.jpg')):
  with Image.open(p) as im:dim=list(im.size)
  assert max(dim)<=1280 and p.stat().st_size<1_000_000,(p,dim,p.stat().st_size)
  files.append({'file':p.name,'dimensions':dim,'bytes':p.stat().st_size,'sha256':m.sha(p)})
 (REVIEW/'見本JPG_検証.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n')
 print('JPG',len(files),'max bytes',max(r['bytes'] for r in files))
if __name__=='__main__':main()
