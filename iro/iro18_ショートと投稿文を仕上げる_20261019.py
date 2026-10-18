"""IRO18の承認済み素材からショート4本と投稿文を仕上げる。音声はコピー。"""
from pathlib import Path
import importlib.util,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
P=Path(__file__).with_name('iro18_完成品を仕上げる_20261019.py');s=importlib.util.spec_from_file_location('finish',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
JP='/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc';AV='/System/Library/Fonts/Avenir Next.ttc'
SCENES=[('A',918,['ひと目ずつ、','ゆっくりと。'],'試作1_境界修正_犬1.4倍_8秒.mp4'),('B',918,['もうひと段、','編んだら休憩。'],'試作2_境界修正_犬1.4倍_8秒.mp4'),('C',94,['毛糸の前で、','ふぁーっと一息。'],'犬1.4倍_C_あくび_8秒.mp4'),('D',108,['どこまで走る、','夢のなか。'],'犬1.4倍_D_走る夢_8秒.mp4')]
def main():
 info=[]
 for tag,left,lines,source in SCENES:
  top=1430 if tag in 'AB' else 170
  y=np.arange(1920);a=np.clip(np.minimum(y-(top-140),(top+470)-y)/140,0,1)*165
  band=Image.new('RGBA',(1080,1920),(38,14,25,0));band.putalpha(Image.fromarray(np.repeat(a[:,None],1080,axis=1).astype('uint8')))
  lay=Image.new('RGBA',band.size);d=ImageDraw.Draw(lay)
  d.rounded_rectangle((66,top,700,top+56),28,fill=(116,51,72,255));d.text((90,top+6),'BURGUNDY  |  Acoustic Chill',font=ImageFont.truetype(AV,34,index=2),fill='white')
  for i,t in enumerate(lines):d.text((65,top+85+i*105),t,font=ImageFont.truetype(JP,84),fill='white')
  d.text((70,top+328),'編み物BGM 2時間・本編はチャンネルから',font=ImageFont.truetype(JP,34),fill=(255,215,90,255))
  shade=Image.new('RGBA',band.size,(0,8,8,0));shade.putalpha(lay.getchannel('A').filter(ImageFilter.GaussianBlur(7)))
  overlay=m.WORK/f'short_{tag}_文字.png';Image.alpha_composite(Image.alpha_composite(band,shade),lay).save(overlay)
  follow=source if tag in 'AB'else'犬1.4倍_寝息_8秒.mp4'
  listing=m.WORK/f'short_{tag}_連結.txt';listing.write_text(''.join(f"file '{m.TRIAL/n}'\n"for n in[source,follow]))
  final=m.KIT/f'iro18_ショート_{tag}.mp4';oldaudio=m.OUT/'旧投稿用_保全'/final.name
  vonly=m.WORK/f'short_{tag}_映像.mp4'
  m.run(['-f','concat','-safe','0','-i',listing,'-i',overlay,'-filter_complex',f'[0:v]crop=608:1080:{left}:0,scale=1080:1920:flags=lanczos[b];[b][1:v]overlay=0:0,format=yuv420p[v]','-map','[v]','-an',*m.encopts(),'-frames:v',360,'-movflags','+faststart',vonly])
  m.run(['-i',vonly,'-i',oldaudio,'-map','0:v:0','-map','1:a:0','-c','copy','-movflags','+faststart',final])
  v=m.video(final);assert int(v['nb_frames'])==360 and(v['width'],v['height'])==(1080,1920)
  m.run(['-ss',4,'-i',final,'-frames:v',1,m.WORK/f'short_{tag}_4秒.jpg'])
  info.append({'tag':tag,'file':str(final),'source':str(m.TRIAL/source),'follow':str(m.TRIAL/follow),'source_start':0,'crop':[left,0,608,1080],'edge_extension_y':0,'frames':360,'title':''.join(lines),'audio_copied_from':str(oldaudio),'audio_reencoded':False})
  print('short complete',tag,flush=True)
 (m.WORK/'ショート設定.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n')
 # 既存の章・タグ・既定文を保持し、動作とA/B題だけを更新。
 for p in (m.OLD/'投稿用').glob('*.txt'):shutil.copy2(p,m.KIT/p.name)
 replacements={'マフラーにそっと手を添える女性':'ゆっくり編み物を続ける女性','A woman rests her hands on a knitted scarf while a golden retriever sleeps curled up on the rug.':'A woman knits slowly, stitch by stitch, while a golden retriever sleeps curled up on the rug.'}
 for name in ['00_説明文_これを貼る.txt','05_説明文_日本語.txt','06_説明文_英語.txt','10_英語ローカライズ_説明文.txt']:
  p=m.KIT/name;text=p.read_text()
  for a,b in replacements.items():text=text.replace(a,b)
  p.write_text(text)
 for name,title,body,en in [('13_ショートA.txt','ひと目ずつ、ゆっくりと。','毛糸を広げて、ひと目ずつ。静かな部屋で、ゆっくり編み物を続ける時間。','One stitch at a time, slowly and gently.'),('14_ショートB.txt','もうひと段、編んだら休憩。','小さく針を動かして、もうひと段。編み物のおともに、暖かな音楽を。','One more row, then a little break.')]:
  (m.KIT/name).write_text(title+'\n\n'+body+'\n'+en+'\n\n#編み物BGM #作業用BGM #shorts\n')
 (m.KIT/'本編の保存先.txt').write_text(str(m.MAIN)+'\n')
 (m.KIT/'00_使い方.txt').write_text('手直し完成・未投稿。本人の通し視聴とClaude完成検品待ち。\n本編・ショート4本・サムネはこのフォルダ内。\nIRO Soundsの既定説明文を残し、その上に00の本文を挿入（日本語→英語）。\n既存の🛋️ Chill｜チルBGMを使用。章・タグ・ハッシュタグは従来どおり。\nこの依頼ではYouTubeへの投稿・予約は行っていません。\n')
 print('posting text complete',flush=True)
if __name__=='__main__':main()
