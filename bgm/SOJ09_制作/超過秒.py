import subprocess,sys,numpy as np
f,ss,t,inI=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4])
SR=48000; g=-18-inI
x=np.frombuffer(subprocess.run(["ffmpeg","-v","error","-ss",str(ss),"-t",str(t),"-i",f,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout,"<f4").reshape(-1,2)
n=len(x)//SR; m=x[:n*SR].mean(1).reshape(n,SR)
pk=20*np.log10(np.abs(x[:n*SR]).max(1).reshape(n,SR).max(1)+1e-12)+g
fr=np.fft.rfftfreq(SR,1/SR)
def bands(sec):
    P=np.abs(np.fft.rfft(m[sec]*np.hanning(SR)))**2
    tot=P.sum(); return [100*P[(fr>=a)&(fr<b)].sum()/tot for a,b in [(0,150),(150,1000),(1000,4000),(4000,24000)]]
ref=np.mean([bands(i) for i in range(0,n,30)],0)
print(f"{f} 平常 <150:{ref[0]:.0f}% 150-1k:{ref[1]:.0f}% 1-4k:{ref[2]:.0f}% 4k+:{ref[3]:.0f}%")
for i in np.where(pk>-2.5)[0]:
    b=bands(i); lr=20*np.log10(np.abs(x[i*SR:(i+1)*SR,0]).max()/max(1e-9,np.abs(x[i*SR:(i+1)*SR,1]).max()))
    print(f"  {ss+i:6.0f}秒 {pk[i]:+5.1f}dBFS  <150:{b[0]:3.0f}% 150-1k:{b[1]:3.0f}% 1-4k:{b[2]:3.0f}% 4k+:{b[3]:3.0f}%  L/R差{lr:+.1f}dB")
