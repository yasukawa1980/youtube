"""SOJ09：各素材で、区間ごと −18 LUFS に揃えたとき標本ピークが −2.5dBFS を超えない最長・最良の区間を探す。
  python3 区間を探す.py ファイル 欲しい秒数
1秒ごとの最大値と、400ms単位の音量（簡易K特性なし・RMSで近似）から区間ラウドネスを見積もり、
候補区間を ffmpeg loudnorm で実測し直す。"""
import subprocess, sys, json, re, numpy as np
f, want = sys.argv[1], float(sys.argv[2])
SR = 48000
x = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,"<f4").reshape(-1,2)
n = len(x)//SR
pk = np.abs(x[:n*SR]).max(1).reshape(n,SR).max(1)
ms = (x[:n*SR]**2).mean(1).reshape(n,SR).mean(1)
def meas(ss,t):
    e=subprocess.run(["ffmpeg","-hide_banner","-nostats","-ss",str(ss),"-t",str(t),"-i",f,"-af","loudnorm=print_format=json","-f","null","-"],capture_output=True,text=True).stderr
    return json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}",e,re.S).group(0))
w=int(want); best=[]
if w>n: print(f"短い: {n}秒しかない"); w=n
for s in range(0,n-w+1,5):
    rms=10*np.log10(ms[s:s+w].mean()+1e-15)
    g=-18-(rms-0.7)   # LUFS≒RMS-0.7 の粗い見積もり（実測で直す）
    over=int((20*np.log10(pk[s:s+w]+1e-12)+g>-2.5).sum())
    best.append((over,-rms,s))
best.sort()
seen=[]
for over,_,s in best:
    if any(abs(s-q)<120 for q in seen): continue
    seen.append(s)
    m=meas(s,w); g=-18-float(m["input_i"])
    over=int((20*np.log10(pk[s:s+w]+1e-12)+g>-2.5).sum()); mx=20*np.log10(pk[s:s+w].max())+g
    print(f"{f}  {s}〜{s+w}秒  in {m['input_i']} LUFS  −18で最大{mx:+.1f}dBFS  超{over}秒")
    if len(seen)>=4: break
