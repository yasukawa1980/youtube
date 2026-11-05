from wom12_scenes import *
from wom12_produce import REPO
import shutil
D=ROOT/'deliverables';P=REPO/'new-channel/サムネ確認用/wom12'
def put(im,k,rect,box):
 a=art(k);a=a.crop(tuple(round(v*a.size[i%2]) for i,v in enumerate(rect)));im.paste(ImageOps.fit(a,(box[2]-box[0],box[3]-box[1]),method=Image.Resampling.LANCZOS),(box[0],box[1]))
def main():
 arr=[]
 for opt in ['A','B']:
  im=Image.new('RGB',(1280,720),PAPER);dr=ImageDraw.Draw(im)
  if opt=='A':
   put(im,'N08_p1',(.14,.20,.85,.61),(24,140,630,569));put(im,'N03-B',(.12,.43,.86,.86),(650,140,1256,569));txt(im,'RED BEFORE 1931?',640,72,77,1190,FB);txt(im,'1821',328,620,79,550,FB);txt(im,'1904',953,620,79,550,FB)
  else:
   put(im,'N03-A',(.22,.13,.89,.77),(614,0,1280,665));txt(im,'RED',305,153,109,550,FB);txt(im,'BEFORE',305,319,124,560,FB);txt(im,'COCA-COLA?',305,490,76,570,FB)
  dr.rectangle((0,668,1280,720),fill=INK);txt(im,'QUIET ORIGINS',640,695,26,850,SANS,LIGHT);f=D/f'EP012_thumbnail_{opt}.jpg';im.save(f,quality=90,optimize=True);assert f.stat().st_size<1000000;shutil.copy2(f,P/f.name);arr.append(im.resize((168,94),Image.Resampling.LANCZOS))
 both=Image.new('RGB',(336,94),PAPER);both.paste(arr[0],(0,0));both.paste(arr[1],(168,0));both.save(P/'EP012_AB_168px.jpg',quality=96);shutil.copy2(P/'EP012_AB_168px.jpg',D/'EP012_AB_168px.jpg')
if __name__=='__main__':main()
