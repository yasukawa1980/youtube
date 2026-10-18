"""境界修正した試作2本の検品資料のみ更新。完成品は変更しない。"""
from pathlib import Path
import json,hashlib,subprocess,shutil
import cv2
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent/'iro18_手直し_20261018'
MEDIA=Path('/Users/ryo/Desktop/BGM/IRO/Chill/18_毛糸の季節がやってきた/手直し_20261018')
FONT='/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def still(path,frame,box):
    c=cv2.VideoCapture(str(path));c.set(cv2.CAP_PROP_POS_FRAMES,frame);ok,bgr=c.read();c.release();assert ok
    return Image.fromarray(cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)).crop(box)
def main():
    q=[json.loads((R/f'試作{i}_境界修正_検証.json').read_text())for i in [1,2]]
    assert all(x['decode_ok'] and x['outside_composite_mask_changed_pixels_before_dog_and_encode']==0 for x in q)
    assert q[0]['same_polygon_for_both_takes']==q[1]['same_polygon_for_both_takes']
    board=Image.new('RGB',(1280,1240),'#24171e');d=ImageDraw.Draw(board);font=ImageFont.truetype(FONT,20)
    d.text((16,10),'IRO18：房・糸の境界修正／編む土台2本の検品（本編仕上げ前）',font=font,fill='white')
    for col,x in enumerate(q):
        left=col*640;d.text((left+12,45),f"試作{x['take']}・4秒／犬1.4倍",font=font,fill='#FFD75A')
        im=Image.open(R/f"試作{x['take']}_境界修正_全体4秒.jpg");board.paste(im.resize((640,360)),(left,76))
    for col,(file,title)in enumerate([('合成境界_旧赤と修正黄.jpg','境界：旧＝赤／修正＝黄、ぼかし18px'),('広域ROI_対象外変化の位置.jpg','従来の広域ROI：机上の変化は背景へ戻す')]):
        d.text((col*640+10,448),title,font=ImageFont.truetype(FONT,18),fill='white')
        im=Image.open(R/file);im.thumbnail((630,290));board.paste(im,(col*640+5,480))
    for row,x in enumerate(q):
        y=790+row*164;d.text((12,y),f"試作{x['take']} 房：0・2・4・6秒（48コマは要約の別紙リンク）",font=font,fill='white')
        for col,frame in enumerate([0,48,96,144]):
            im=still(x['output'],frame,(800,670,1330,865));im=im.resize((320,118));board.paste(im,(col*320,y+30))
    d.text((16,1138),'瞬き・目元の合成、頭の時間変更、ループのクロスフェードなし。',font=font,fill='white')
    d.text((16,1173),'手直しKling 128/192。検品資料を共有して停止。購入・投稿・予約なし。',font=font,fill='#FFD75A')
    board.save(R/'Claude検品用_見本.jpg',quality=90)
    # Keep all Git review JPGs compact, including the 48-frame thread contact sheet.
    files=[]
    for p in sorted(R.glob('*.jpg')):
        im=Image.open(p).convert('RGB')
        if max(im.size)>1280 or p.stat().st_size>=1_000_000:
            im.thumbnail((1280,1280),Image.Resampling.LANCZOS);im.save(p,quality=88)
        assert max(im.size)<=1280 and p.stat().st_size<1_000_000
        files.append({'file':p.name,'dimensions':list(im.size),'bytes':p.stat().st_size,'sha256':sha(p)})
    (R/'見本JPG_検証.json').write_text(json.dumps(files,ensure_ascii=False,indent=2)+'\n')
    print('検品用見本とJPG検証',len(files),flush=True)
if __name__=='__main__':main()
