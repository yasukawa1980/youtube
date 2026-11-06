import subprocess,json,hashlib,time,os,sys,math,datetime
OUT=sys.argv[1]
items=[('V01','PJEZO','SK-C-5'),('V02','pVyUn','SK-C-1453'),('V05','cciGN','RP-P-AO-25-25-1'),('V06','hjJLt','SK-C-1177'),('V07','jrmuj','KOG-AA-2-4-112'),('V08','hjCVy','RP-P-1896-A-19326')]
T=4000
JST=datetime.timezone(datetime.timedelta(hours=9))
log={'acquired_by':'Claude (owner-approved 2026-11-07, owner Mac, curl, official Rijksmuseum IIIF)','tile_max':T,'items':[]}
def get(url,dest):
    t0=datetime.datetime.now(JST).isoformat(timespec='seconds')
    r=subprocess.run(['curl','-s','-o',dest,'-w','%{http_code} %{size_download} %{content_type}',url],capture_output=True,text=True)
    code,size,ct=r.stdout.split(' ',2); time.sleep(1.1)
    return t0,int(code),int(size),ct
def dims(p):
    o=subprocess.run(['sips','-g','pixelWidth','-g','pixelHeight',p],capture_output=True,text=True).stdout.split()
    return int(o[o.index('pixelWidth:')+1]),int(o[o.index('pixelHeight:')+1])
sha=lambda p:hashlib.sha256(open(p,'rb').read()).hexdigest()
for vid,iid,obj in items:
    d=f'{OUT}/{vid}_{obj}'; os.makedirs(d,exist_ok=True)
    base=f'https://iiif.micr.io/{iid}'
    t0,code,size,ct=get(base+'/info.json',f'{d}/info.json')
    if code!=200: print(vid,'info',code); sys.exit(1)
    info=json.load(open(f'{d}/info.json')); W,H,MA=info['width'],info['height'],info.get('maxArea')
    rec={'id':vid,'object':obj,'iiif':base,'width':W,'height':H,'maxArea':MA,'info_fetched_jst':t0,'tiles':[]}
    if W*H<=MA: grid=[(0,0,W,H,'full')]
    else:
        nx,ny=math.ceil(W/T),math.ceil(H/T)
        grid=[(x*T,y*T,min(T,W-x*T),min(T,H-y*T),None) for y in range(ny) for x in range(nx)]
    for x,y,w,h,f in grid:
        reg='full' if f else f'{x},{y},{w},{h}'
        url=f'{base}/{reg}/max/0/default.jpg'
        name=f'{vid}_full.jpg' if f else f'{vid}_x{x:05d}_y{y:05d}_{w}x{h}.jpg'
        p=f'{d}/{name}'
        t0,code,size,ct=get(url,p)
        if code!=200: print(vid,reg,code); json.dump(log,open(f'{OUT}/取得記録_partial.json','w'),ensure_ascii=False,indent=1); sys.exit(1)
        gw,gh=dims(p)
        ok=(gw,gh)==(w,h)
        rec['tiles'].append({'file':name,'x':x,'y':y,'w':w,'h':h,'url':url,'fetched_jst':t0,'status':code,'bytes':size,'content_type':ct,'got_w':gw,'got_h':gh,'size_match':ok,'sha256':sha(p)})
        if not ok: print('SIZE MISMATCH',vid,name,gw,gh); sys.exit(1)
    log['items'].append(rec); print(vid,W,H,len(grid),'tiles ok',sum(t['bytes'] for t in rec['tiles']))
json.dump(log,open(f'{OUT}/取得記録.json','w'),ensure_ascii=False,indent=1)
