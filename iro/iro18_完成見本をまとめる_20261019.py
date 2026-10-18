"""完成本編から画面・章・編む手元を抜き、共有用の比較JPGを作る。"""
from pathlib import Path
import importlib.util,json,shutil,re
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
s=importlib.util.spec_from_file_location('finish',Path(__file__).with_name('iro18_完成品を仕上げる_20261019.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
R=m.REVIEW;FONT='/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
def read(path,frame):
 c=cv2.VideoCapture(str(path));c.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,a=c.read();c.release();assert ok,(str(path),frame);return cv2.cvtColor(a,cv2.COLOR_BGR2RGB)
def jpg(im,name):
 im=im.convert('RGB');im.thumbnail((1280,1280),Image.Resampling.LANCZOS);p=R/name;im.save(p,quality=90);assert p.stat().st_size<1000000;return p

def main():
 data=json.loads((m.WORK/'構成.json').read_text());pack=m.WORK/'parts'
 sample=[]
 for sec,label in [(30,'00分30秒'),(1800,'30分00秒'),(5400,'90分00秒')]:
  frame=sec*24;im=read(m.MAIN,frame);row=data['segments'][(frame-m.PREFIX)//192];rel=(frame-m.PREFIX)%192;part=read(pack/(row['key']+'.mp4'),rel)
  diff=int(np.abs(im.astype(np.int16)-part).max());assert diff==0
  p=jpg(Image.fromarray(im),f'完成本編_{label}.jpg');sample.append({'seconds':sec,'frame':frame,'take':row['take'],'file':p.name,'max_pixel_difference_to_part':diff})
 # 犬の章18か所は出来事の開始フレームと、4秒後を完成本編から比較。
 chapters=[];sheet=Image.new('RGB',(1280,6*180),'#251b22');draw=ImageDraw.Draw(sheet)
 for i,ev in enumerate(data['events']):
  checks=[]
  for delta in [0,96]:
   absolute=ev['final_frame']+delta;row=data['segments'][(absolute-m.PREFIX)//192];rel=(absolute-m.PREFIX)%192
   final=read(m.MAIN,absolute);source=read(pack/(row['key']+'.mp4'),rel);diff=int(np.abs(final.astype(np.int16)-source).max());assert diff==0;checks.append({'offset_frames':delta,'max_pixel_difference':diff})
  x=(i%3)*426;y=(i//3)*180;tile=Image.fromarray(final).crop((0,620,820,1080));tile.thumbnail((320,160));sheet.paste(tile,(x+90,y+20))
  sec=int(ev['final_seconds']);label=f"{sec//3600}:{sec%3600//60:02d}:{sec%60:02d} {ev['tag']}"
  draw.text((x+4,y+2),label,font=ImageFont.truetype(FONT,16),fill='white')
  chapters.append({**ev,'comparisons':checks})
 jpg(sheet,'完成本編_犬の章18か所.jpg')
 # 章ファイルは従来と同一、丸めた表示秒と実フレーム開始も一致。
 chapterfile=m.KIT/'11_チャプター_犬の動き.txt';assert chapterfile.read_bytes()==(m.OLD/'投稿用'/chapterfile.name).read_bytes()
 displayed=re.findall(r'^(\d+:\d+(?::\d+)?) 🐕',chapterfile.read_text(),re.M)[:18]
 def sec(t):
  v=0
  for x in t.split(':'):v=v*60+int(x)
  return v
 assert [sec(x)for x in displayed]==[int(x['final_seconds'])for x in chapters]
 for n in[1,2]:
  row=next(r for r in data['segments']if r['take']==n and not r['event']);start=m.PREFIX+row['start_body_frame']
  c=cv2.VideoCapture(str(m.MAIN));c.set(cv2.CAP_PROP_POS_FRAMES,start);frames=[]
  for k in range(192):
   ok,b=c.read();assert ok;frames.append(cv2.cvtColor(b,cv2.COLOR_BGR2RGB))
  c.release()
  for half,ids in [('前半',range(0,96,4)),('後半',range(96,192,4))]:m.fix.qc.sheet(frames,list(ids),(900,450,1530,700),4,320,R/f'完成本編_試作{n}_手元6fps_{half}.jpg')
  m.fix.qc.sheet(frames,list(range(0,192,8)),(1090,275,1350,460),6,200,R/f'完成本編_試作{n}_顔3fps.jpg')
 # 不規則配置で新しく生じる1→2、2→1も、針と顔をコマ見本へ。
 seamboard=Image.new('RGB',(1280,760),'#251b22');d=ImageDraw.Draw(seamboard);seams=[]
 for row,(a,b)in enumerate([(1,1),(1,2),(2,1),(2,2)]):
  aa=read(pack/f'take{a}_rgb.mp4',191);bb=read(pack/f'take{b}_rgb.mp4',0);seams.append({'from':a,'to':b,'whole_frame_mad':float(np.abs(aa.astype(np.float32)-bb).mean())})
  for col,(n,k)in enumerate([(a,190),(a,191),(b,0),(b,1)]):
   im=Image.fromarray(read(pack/f'take{n}_rgb.mp4',k)).crop((900,260,1530,700));im.thumbnail((280,160));seamboard.paste(im,(col*320,row*190+28));d.text((col*320+4,row*190+3),f'{a}→{b} : 試作{n} #{k}',font=ImageFont.truetype(FONT,16),fill='white')
 jpg(seamboard,'試作1と2_全4通りのつなぎ目.jpg')
 # 扉・導入と終了カードも完成本編から確認。
 edge=Image.new('RGB',(1280,768),'#251b22');d=ImageDraw.Draw(edge)
 for i,frame in enumerate([0,19*24,21*24,542,543,(m.TOTAL-360),m.TOTAL-240,m.TOTAL-1]):
  im=Image.fromarray(read(m.MAIN,frame));im.thumbnail((320,180));x=i%4*320;y=i//4*384;edge.paste(im,(x,y+30));d.text((x+3,y+4),f'{frame/24:.3f}s / #{frame}',font=ImageFont.truetype(FONT,14),fill='white')
 jpg(edge.crop((0,0,1280,600)),'完成本編_扉と終了カード.jpg')
 # 主見本は指定の3時刻、サムネ原寸/168px、ショート4本の4秒目。
 board=Image.new('RGB',(1280,1240),'#251b22');d=ImageDraw.Draw(board);font=ImageFont.truetype(FONT,20)
 d.text((12,8),'IRO18 完成検品：本編2時間・ショート4本・サムネ（未投稿）',font=font,fill='white')
 for i,item in enumerate(sample):
  im=Image.open(R/item['file']);im.thumbnail((426,240));board.paste(im,(i*426,70));d.text((i*426+8,43),['本編 0:30','本編 30:00','本編 1:30:00'][i],font=font,fill='#FFD75A')
 thumb=Image.open(m.OUT/'iro18_サムネ.jpg');board.paste(thumb.resize((640,360)),(0,350));d.text((12,319),'サムネ原寸は別添（1280×720）',font=font,fill='white')
 small=Image.open(m.OUT/'サムネ_168px.png');board.paste(small.resize((336,188),Image.Resampling.NEAREST),(720,360));d.text((720,565),'168px表示を2倍で掲載',font=font,fill='#FFD75A')
 d.text((720,605),'題・用途・尺を維持',font=font,fill='white');d.text((720,640),'編む手元＋犬1.4倍',font=font,fill='white')
 for i,tag in enumerate('ABCD'):
  im=Image.open(m.WORK/f'short_{tag}_4秒.jpg');im.thumbnail((270,480));board.paste(im,(i*320+25,755));d.text((i*320+12,723),f'ショート{tag}・4秒目',font=font,fill='white')
 jpg(board,'Claude検品用_見本.jpg');shutil.copy2(m.OUT/'iro18_サムネ.jpg',R/'iro18_サムネ.jpg');jpg(small,'iro18_サムネ_168px.jpg')
 # 旧/新開始絵と犬境界。別紙なので主見本の文字を小さくしない。
 compare=Image.new('RGB',(1280,1060),'#251b22');d=ImageDraw.Draw(compare)
 for i,(name,title)in enumerate([('18_start_旧_1920.png','旧開始画像'),('18_start_編む手元_犬1.4倍.png','新開始画像・犬1.4倍')]):
  im=Image.open(m.TRIAL/name);compare.paste(im.resize((640,360)),(i*640,35));d.text((i*640+8,6),title,font=font,fill='white')
 im=Image.open(R/'完成本編_00分30秒.jpg').resize((1920,1080));crop=im.crop((0,600,920,1080));crop.thumbnail((1280,620));compare.paste(crop,(0,430));d.text((12,400),'完成本編：敷物と机の脚の境界',font=font,fill='white');jpg(compare,'開始画像新旧と犬の境界.jpg')
 verification={'samples':sample,'chapters':chapters,'chapter_text_unchanged':True,'cross_take_seams':seams,'source':'代表画面・章・手元・顔は完成本編MP4から抽出。章は開始・4秒後を連結元と画素照合。切替4パターンは本編に使った部品で比較。'}
 (R/'完成画面と章_検証.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
 sizes=[]
 for p in R.glob('*.jpg'):
  im=Image.open(p)
  if max(im.size)>1280:jpg(im,p.name)
  im=Image.open(p);assert max(im.size)<=1280 and p.stat().st_size<1000000;sizes.append({'file':p.name,'dimensions':list(im.size),'bytes':p.stat().st_size,'sha256':m.sha(p)})
 (R/'見本JPG_検証.json').write_text(json.dumps(sizes,ensure_ascii=False,indent=2)+'\n');print('完成見本・章18か所・代表3時刻の照合完了',flush=True)
if __name__=='__main__':main()
