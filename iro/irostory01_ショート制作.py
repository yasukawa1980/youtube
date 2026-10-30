#!/usr/bin/env python3
"""絵物語01を36秒・縦1080pに再編集。新規生成APIは使わない。

bgm/.venv-audio-qc/bin/python iro/irostory01_ショート制作.py [preview|render|qc|all]
画像・動画・音声・中間物は指定SSDの作品フォルダに保存。
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.io import wavfile

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('story', REPO/'iro/irostory01_仕上げ.py')
story = importlib.util.module_from_spec(spec)
spec.loader.exec_module(story)
BASE = story.BASE
WORK = BASE/'_work/short_v1'
OUT = BASE/'投稿用'
MAIN = OUT/'irostory01_ショート_あと一ページのはずだった_v1.mp4'
W, H, FPS, SR, DURATION = 1080, 1920, 24, 48000, 36
# start/end, source, horizontal center, source audio interval start
SHOTS = [
    (0, 3, 'S1_reading.png', .705, 15),
    (3, 9, 'dog', .50, 24),
    (9, 15, 'woman', .705, 34),
    (15, 19, 'S3_waiting.png', .655, 41),
    (19, 22, 'S4_bookmark.png', .565, 55),
    (22, 26, 'S5_doorway.png', .49, 63),
    (26, 36, 'S6_walk.png', .47, 72),
]


def run(args, **kw):
    return subprocess.run(list(map(str, args)), check=True, **kw)


def typography(kind):
    layer = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(layer)
    if kind == 'open':
        for y in range(1150, 1660):
            alpha = int(155 * np.sin(np.pi*(y-1150)/510))
            d.line((0,y,W,y), fill=(10,27,28,alpha))
        d.text((90,1215), 'あと一ページ、', font=story.font(67,True), fill=(255,249,232))
        d.text((90,1310), 'のはずだった。', font=story.font(67,True), fill=(255,249,232))
        d.text((95,1440), 'IRO SOUNDS  /  小さな物語', font=story.font(28), fill=(240,228,204))
    else:
        for y in range(110, 440):
            alpha = int(160*np.sin(np.pi*(y-110)/330))
            d.line((0,y,W,y), fill=(10,27,28,alpha))
        d.text((95,205), 'つづきは、', font=story.font(67,True), fill=(255,249,232))
        d.text((95,300), '帰ってから。', font=story.font(67,True), fill=(255,249,232))
        d.text((100,1440), 'IRO SOUNDS  /  小さな物語', font=story.font(28), fill=(240,228,204), stroke_width=1, stroke_fill=(20,35,35))
    return np.array(layer)


class Editor:
    def __init__(self):
        self.images = {s[2]: cv2.cvtColor(cv2.imread(str(BASE/'開始画像'/s[2])), cv2.COLOR_BGR2RGB)
                       for s in SHOTS if s[2].endswith('.png')}
        self.motions = {key: story.Motion(BASE/'動作素材'/f'{key}_6s.mp4') for key in ('dog','woman')}
        self.layers = {key: typography(key) for key in ('open','end')}

    def shot(self, k, t):
        a,b,name,cx,_ = SHOTS[k]
        src = self.motions[name].frame(t-a) if name in self.motions else self.images[name]
        ih,iw = src.shape[:2]
        u = np.clip((t-a)/(b-a),0,1)
        # Close crops track the face; doorway and walk retain both characters.
        zoom = 1 if name in self.motions else 1+.018*u*u*(3-2*u)
        ch = ih/zoom
        # A slightly wider doorway view protects both full bodies. Soft image
        # extensions above/below keep a vertical canvas without cropping limbs.
        view_h = 1650 if name=='S5_doorway.png' else H
        cw = ch*W/view_h
        x = np.clip(cx*iw-cw/2,0,iw-cw)
        y = (ih-ch)/2
        matrix = np.array([[cw/W,0,x],[0,ch/view_h,y]],np.float32)
        view = cv2.warpAffine(src,matrix,(W,view_h),flags=cv2.INTER_LINEAR|cv2.WARP_INVERSE_MAP,
                             borderMode=cv2.BORDER_REPLICATE)
        if view_h==H:
            return view
        bg = cv2.resize(view,(W,H))
        bg = cv2.GaussianBlur(bg,(0,0),32)
        top = (H-view_h)//2
        bg[top:top+view_h] = view
        return bg

    def frame(self,t):
        k = next(k for k,s in enumerate(SHOTS) if s[0]<=t<s[1])
        im = self.shot(k,t)
        # Brief transitions keep the original quiet pacing without long holds.
        if k and t-SHOTS[k][0]<.25:
            alpha = (t-SHOTS[k][0])/.25
            prev = self.shot(k-1,SHOTS[k-1][1]-1/FPS)
            im = cv2.addWeighted(prev,1-alpha,im,alpha,0)
        if t<2.9:
            im = story.blend_layer(im,self.layers['open'],min(1,(2.9-t)/.4))
        if t>=30:
            im = story.blend_layer(im,self.layers['end'],min(1,(t-30)/.7))
        if t>35.4:
            im = (im*max(0,(36-t)/.6)).astype(np.uint8)
        return im


def preview():
    editor = Editor()
    times = [1,4,8,10,14,17,20,24,28,33]
    sheet = Image.new('RGB',(1350,1020),(22,29,28))
    d = ImageDraw.Draw(sheet)
    for k,t in enumerate(times):
        thumb = Image.fromarray(editor.frame(t)).resize((270,480),Image.Resampling.LANCZOS)
        x,y = k%5*270,k//5*510
        sheet.paste(thumb,(x,y))
        d.text((x+12,y+482),f'{t:02}s',font=story.font(20),fill='white')
    sheet.save(WORK/'縦構図確認.jpg',quality=90)
    print('縦構図プレビュー作成',flush=True)


def audio():
    sr,raw = wavfile.read(BASE/'音源/irostory01_生活音_仕上げv2.wav')
    assert sr==SR and raw.ndim==2
    raw = raw.astype(np.float32)/32768
    out = np.zeros((DURATION*SR,2),np.float32)
    for a,b,_,_,source_start in SHOTS:
        chunk = raw[source_start*SR:(source_start+b-a)*SR].copy()
        fade = int(.04*SR)
        chunk[:fade] *= np.linspace(0,1,fade)[:,None]
        chunk[-fade:] *= np.linspace(1,0,fade)[:,None]
        out[a*SR:b*SR] = chunk
    out[:int(.2*SR)] *= np.linspace(0,1,int(.2*SR))[:,None]
    out[-2*SR:] *= np.linspace(1,0,2*SR)[:,None]
    dest = BASE/'音源/irostory01_ショート_生活音_v1.wav'
    wavfile.write(dest,SR,(out*32767).astype(np.int16))
    return dest


def render():
    editor = Editor()
    raw = WORK/'映像のみ.mp4'
    with (WORK/'render.log').open('w') as log:
        enc = subprocess.Popen(['ffmpeg','-y','-v','warning','-f','rawvideo','-pix_fmt','rgb24',
             '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast',
             '-crf','18','-pix_fmt','yuv420p',str(raw)],stdin=subprocess.PIPE,stderr=log)
        try:
            for i in range(DURATION*FPS):
                enc.stdin.write(editor.frame(i/FPS).tobytes())
                if i%(FPS*6)==0: print(f'{i/FPS:.0f}/{DURATION}秒',flush=True)
        finally:
            enc.stdin.close()
        if enc.wait(): raise RuntimeError('映像出力失敗。render.log参照')
    sound = audio()
    af = 'loudnorm=I=-24:TP=-3:LRA=20'
    measured = run(['ffmpeg','-hide_banner','-i',sound,'-af',af+':print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    m = json.loads(measured[measured.rfind('{'):measured.rfind('}')+1])
    fixed = af+':linear=true:measured_I='+m['input_i']+':measured_TP='+m['input_tp']+':measured_LRA='+m['input_lra']+':measured_thresh='+m['input_thresh']+':offset='+m['target_offset']
    run(['ffmpeg','-y','-v','error','-i',raw,'-i',sound,'-map','0:v','-map','1:a','-c:v','copy',
         '-af',fixed,'-c:a','aac','-b:a','256k','-ar',SR,'-t',DURATION,'-movflags','+faststart',MAIN])
    print('36秒ショート出力完了',flush=True)


def qc():
    data = json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',MAIN],capture_output=True,text=True).stdout)
    dec = run(['ffmpeg','-v','error','-i',MAIN,'-f','null','-'],capture_output=True,text=True)
    loud = run(['ffmpeg','-hide_banner','-i',MAIN,'-vn','-af','loudnorm=I=-24:TP=-3:LRA=20:print_format=json','-f','null','-'],capture_output=True,text=True).stderr
    ld = json.loads(loud[loud.rfind('{'):loud.rfind('}')+1])
    vs = next(s for s in data['streams'] if s['codec_type']=='video')
    aus = next(s for s in data['streams'] if s['codec_type']=='audio')
    # Actual encoded output, including text, is inspected rather than only source crops.
    sheet = Image.new('RGB',(1350,1020),(22,29,28)); d = ImageDraw.Draw(sheet)
    for k,t in enumerate([1,4,8,10,14,17,20,24,28,33]):
        frame = WORK/f'qc_{t:02}.jpg'
        run(['ffmpeg','-y','-v','error','-ss',t,'-i',MAIN,'-frames:v','1','-q:v','2',frame])
        tile = Image.open(frame).resize((270,480),Image.Resampling.LANCZOS)
        x,y = k%5*270,k//5*510;sheet.paste(tile,(x,y))
        d.text((x+12,y+482),f'{t:02}s',font=story.font(20),fill='white')
        if t==1:
            cover = Image.open(frame).resize((720,1280),Image.Resampling.LANCZOS)
            cover.save(OUT/'irostory01_ショート_カバー候補.jpg',quality=90)
            cover.save(REPO/'サムネ確認用/IRO Sounds/irostory01_ショート_サムネ.jpg',quality=90)
    sheet.save(OUT/'irostory01_ショート_場面確認.jpg',quality=90)
    result = {'id':'irostory01','version':'short_v1','duration_seconds':float(data['format']['duration']),
              'width':vs['width'],'height':vs['height'],'fps':vs['avg_frame_rate'],'video_codec':vs['codec_name'],
              'audio_codec':aus['codec_name'],'sample_rate':aus['sample_rate'],'channels':aus['channels'],
              'size_bytes':MAIN.stat().st_size,'sha256':hashlib.sha256(MAIN.read_bytes()).hexdigest(),
              'integrated_lufs':float(ld['input_i']),'true_peak_dbtp':float(ld['input_tp']),
              'loudness_range':float(ld['input_lra']),'full_decode_errors':dec.stderr.strip(),
              'new_generation_credits':0,'music':False,'dialogue':False,
              'subjective_audio_review':'直接聴取は未実施。数値検品済み。',
              'shots':[{'start':a,'end':b,'source':s,'center_x':cx,'audio_source_start':at} for a,b,s,cx,at in SHOTS]}
    assert result['duration_seconds']==DURATION and (vs['width'],vs['height'])==(W,H)
    assert vs['avg_frame_rate']=='24/1' and not dec.stderr.strip() and result['true_peak_dbtp']<=-2.5
    (REPO/'iro/irostory01_ショート_完成検品.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('step',choices=['preview','render','qc','all'],nargs='?',default='all')
    args = parser.parse_args()
    for p in (WORK,OUT): p.mkdir(parents=True,exist_ok=True)
    for name,fn in [('preview',preview),('render',render),('qc',qc)]:
        if args.step in (name,'all'): fn()
