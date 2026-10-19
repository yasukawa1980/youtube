"""短い衝撃音（クリック・マイクへの接触・小石）を探す：0.5秒窓ごとにピークの-6dB幅と、前後100msのRMSに対する突出。
  python3 衝撃音.py ファイル 頭 長さ"""
import subprocess,sys,numpy as np
f,ss,t=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]); SR=48000
x=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-ss",str(ss),"-t",str(t),"-i",f,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,"<f4").reshape(-1,2)
a=np.abs(x).max(1); W=SR//2; hits=[]
for k in range(0,len(a)-W,W):
    seg=a[k:k+W]; i=seg.argmax(); p=seg[i]
    lo=max(0,k+i-4800); r=np.sqrt((x[lo:k+i+4800]**2).mean())
    pr=20*np.log10(p/(r+1e-12))
    if pr<16: continue
    j=k+i; above=np.where(a[max(0,j-4800):j+4800]>p/2)[0]; span=(above.max()-above.min())/SR*1000
    if span<30: hits.append((ss+k/SR, round(pr,1), round(span,1)))
print(f"{f} {ss}〜{ss+t}: 衝撃音 {len(hits)}件", hits[:20])
