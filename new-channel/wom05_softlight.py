import sys
sys.path.insert(0,'new-channel')
from wom05_produce import ROOT,MEDIA,ff,save,sha
src=MEDIA/'V02_Kling_v02.mp4';dst=ROOT/'assets/V02_softlight_v02.mp4'
# Blur only the apparition region; soft edges avoid a visible rectangular patch.
alpha="255*max(0,min(1,(1-sqrt(pow((X-400)/415,2)+pow((Y-400)/430,2)))*5))"
f=f"[0:v]split[base][patch];[patch]crop=800:800:560:70,gblur=sigma=23:steps=3,format=yuva420p,geq=lum='lum(X,Y)':cb='cb(X,Y)':cr='cr(X,Y)':a='{alpha}',fade=t=out:st=4.0:d=1.6:alpha=1[soft];[base][soft]overlay=560:70:enable='lt(t,5.6)',format=yuv420p[v]"
ff(['-i',src,'-filter_complex_threads',2,'-filter_complex',f,'-map','[v]','-an','-c:v','libx264','-threads',4,'-preset','veryfast','-crf',16,dst])
save(ROOT/'records/V02_softlight_processing.json',{'source':str(src),'source_sha256':sha(src),'derived':str(dst),'derived_sha256':sha(dst),'filter':f,'reason':'Remove generated facial, hand and costume detail while retaining a soft seated outline; blur fades before bird descent. Original preserved.'})
ff(['-ss',2,'-i',dst,'-frames:v',1,'-vf','scale=1280:720',ROOT/'review/V02_softlight_detail.jpg'])
