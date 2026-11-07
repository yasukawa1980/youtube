# KCF08 Suno 48本の検品：尾（最後の1秒）・高域（8kHz以上）・音量・頭・曲中の無音・音の終わる位置
# KCF07_小春日和/検品.py を元に、無音の検出（Suno が書き換えた指示から「終わりなし」が落ちたため）を足した
import subprocess, numpy as np, glob, os
D = "/Volumes/ESD-02/Suno書き出し/KCF08_48曲/wav"
SR = 48000
def load(p):
    b = subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","1","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(b, np.float32)
def db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-12)
print("名前          長さ   全体   頭     尾     高域   最長無音 音の終わり 判定")
for p in sorted(glob.glob(D+"/*.wav")):
    x = load(p); n = os.path.basename(p)[:-4]; dur = len(x)/SR
    body, head, tail = db(x), db(x[:SR]), db(x[-SR:])
    seg = x[:(len(x)//8192)*8192].reshape(-1,8192)
    S = (np.abs(np.fft.rfft(seg*np.hanning(8192),axis=1))**2).mean(0)
    f = np.fft.rfftfreq(8192,1/SR)
    hi = 10*np.log10(S[f>=8000].sum()/S.sum()+1e-20)
    # 0.1秒ごとの音量。本体より35dB以上低い区間を「無音」とみなす
    w = x[:(len(x)//4800)*4800].reshape(-1,4800)
    lv = 20*np.log10(np.sqrt((w**2).mean(1))+1e-12)
    quiet = lv < body-35
    run=best=0
    for q in quiet[:-10]:            # 最後の1秒は尾として別に見る
        run = run+1 if q else 0; best=max(best,run)
    loud = np.where(lv > body-25)[0]
    last = (loud[-1]+1)/10 if len(loud) else 0
    flag=[]
    if tail > -46: flag.append("尾切れ?")
    if hi > -40: flag.append("高域")
    if best/10 >= 3: flag.append("曲中無音")
    if dur-last > 15: flag.append("早く終わる")
    print("%-12s %6.1f %6.1f %6.1f %6.1f %6.1f %6.1fs %7.1fs  %s"%(n,dur,body,head,tail,hi,best/10,last," ".join(flag)))
