"""Validate approved pnt02 inputs and measure detail registration, without modifying art."""
from pathlib import Path
import hashlib,itertools,json,subprocess,sys
import cv2
import numpy as np
from PIL import Image,ImageDraw
REPO=Path(__file__).resolve().parent.parent
OUT=REPO/'painting/pnt02_確認版_v01_20261110'
MEDIA=Path('/Volumes/ESD-02/新チャンネル/PNT02_WashingtonCrossing/素材')
FILES={'V01_full':'Met_97.34/DP-14511-001.jpg','D1':'Met_97.34/DP245004.jpg','D2':'Met_97.34/DP245005.jpg','D3':'Met_97.34/DP258218.jpg','V01_room':'Met_97.34/DP258191.jpg','V10':'SMB_3964830/smb3964830.jpg'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 assert Path('/Volumes/ESD-02').is_mount(), 'Specified SSD is not mounted'
 OUT.mkdir(exist_ok=True)
 catalog=json.loads((REPO/'painting/research/pnt02_素材台帳_20261110.json').read_text())
 assets=[]
 for k,name in FILES.items():
  p=MEDIA/name
  with Image.open(p) as im:w,h=im.size
  digest=sha(p)
  assert digest in json.dumps(catalog), (k,'SHA missing from verified catalog')
  assets.append(dict(id=k,path=str(p),width=w,height=h,bytes=p.stat().st_size,sha256=digest,catalog_sha_match=True))
 scripts=[]
 for name in ['content.json','content_en.json']:
  rel='painting/episodes/PNT02_WashingtonCrossing/records/'+name;p=REPO/rel
  remote=subprocess.check_output(['git','show','origin/bgm/production:'+rel],cwd=REPO)
  assert remote==p.read_bytes(),rel
  c=json.loads(remote);scripts.append(dict(path=rel,sha256=sha(p),segments=len(c['segments']),chapters=len(c['chapters']),characters=sum(len(s['text']) for s in c['segments']),whitespace_words=sum(len(s['text'].split()) for s in c['segments'])))
 save(OUT/'input_verification.json',dict(remote_base=subprocess.check_output(['git','rev-parse','origin/bgm/production'],cwd=REPO,text=True).strip(),assets=assets,scripts=scripts,source_images_modified=False))
 # SIFT at half-resolution; fit homography in original-pixel coordinates. Only
 # coordinates are transformed. Rendering will use unwarped original JPEG pixels.
 cv2.setRNGSeed(0);sift=cv2.SIFT_create(nfeatures=16000)
 def features(key):
  im=cv2.imread(str(MEDIA/FILES[key]));g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);g=cv2.resize(g,None,fx=.5,fy=.5)
  return sift.detectAndCompute(g,None)
 fk,fd=features('V01_full');rows=[]
 for key in ['D1','D2','D3']:
  kp,desc=features(key);matches=cv2.BFMatcher().knnMatch(desc,fd,k=2);good=[a for a,b in matches if a.distance<.70*b.distance]
  src=np.float32([kp[m.queryIdx].pt for m in good])*2;dst=np.float32([fk[m.trainIdx].pt for m in good])*2
  H,mask=cv2.findHomography(src,dst,cv2.RANSAC,4.0,maxIters=10000,confidence=.999)
  assert H is not None and mask.sum()>=20,(key,len(good))
  keep=mask.ravel().astype(bool);pred=cv2.perspectiveTransform(src[:,None,:],H)[:,0,:];err=np.linalg.norm(pred-dst,axis=1)
  im=Image.open(MEDIA/FILES[key]);w,h=im.size;corners=np.float32([[0,0],[w,0],[w,h],[0,h]])
  poly=cv2.perspectiveTransform(corners[:,None,:],H)[:,0,:]
  rows.append(dict(id=key,native_size=[w,h],homography=H.tolist(),polygon_in_full_px=poly.tolist(),matches=len(good),inliers=int(keep.sum()),residual_rms_px=float(np.sqrt(np.mean(err[keep]**2))),residual_max_px=float(err[keep].max()),correspondences=[dict(detail_xy=s.tolist(),full_xy=t.tolist(),residual_px=float(e),inlier=bool(i)) for s,t,e,i in zip(src,dst,err,keep)]))
 pairs=[]
 for a,b in itertools.combinations(rows,2):
  p=np.float32(a['polygon_in_full_px']);q=np.float32(b['polygon_in_full_px']);area,_=cv2.intersectConvexConvex(p,q);ratio=area/min(cv2.contourArea(p),cv2.contourArea(q))
  pairs.append(dict(a=a['id'],b=b['id'],overlap_over_smaller=ratio,pass_25_percent=ratio<=.25))
 save(OUT/'detail_registration.json',dict(method='SIFT (half resolution), Lowe ratio <0.70, original-coordinate homography / RANSAC threshold4px, seed0; measurement only, no pixel warping',registration=rows,uncropped_overlap=pairs,final_crops_verified=False))
 # Final viewports: D2 keeps the complete flag and Washington's face/upper body;
 # D3 keeps the steering figure and hand. Cropping is authorized in request §3.
 boxes={'D1':[0,0,1589,3847],'D2':[0,0,2611,2750],'D3':[0,450,4000,2700]}
 final=[]
 for r in rows:
  x,y,xx,yy=boxes[r['id']];poly=cv2.perspectiveTransform(np.float32([[[x,y]],[[xx,y]],[[xx,yy]],[[x,yy]]]),np.array(r['homography']))[:,0,:]
  scale=2160/(yy-y) if r['id']!='D3' else 3840/(xx-x)
  final.append(dict(id=r['id'],crop_native_px=boxes[r['id']],polygon_in_full_px=poly.tolist(),native_scale_4k=scale,max_zoom=1.04,max_native_scale_4k=scale*1.04,minimum_crop_size_at_max_zoom=[(xx-x)/1.04,(yy-y)/1.04],display_height_4k=2160,display_width_4k=(xx-x)*scale))
 finalpairs=[]
 for a,b in itertools.combinations(final,2):
  p=np.float32(a['polygon_in_full_px']);q=np.float32(b['polygon_in_full_px']);area,_=cv2.intersectConvexConvex(p,q);ratio=area/min(cv2.contourArea(p),cv2.contourArea(q))
  finalpairs.append(dict(a=a['id'],b=b['id'],overlap_over_smaller=ratio,pass_25_percent=ratio<=.25))
 assert all(p['pass_25_percent'] for p in finalpairs)
 assert all(r['max_native_scale_4k']<=1 for r in final)
 save(OUT/'final_crop_geometry.json',dict(status='geometry_verified_not_final_video_QA',crops=final,overlap_pairs=finalpairs,maximum_overlap=max(p['overlap_over_smaller'] for p in finalpairs),motion_bound='Every frame must crop INSIDE these viewports; overlap is conservatively computed from their full envelopes.',visual_review='D2 flag and Washington head/upper body retained; D3 steering figure head and right hand retained. Native JPEG pixels are not warped.',full_view=dict(crop_native_px=[0,42.5,4000,2292.5],max_zoom=1.04,minimum_crop_width=4000/1.04,max_native_scale_4k=3840/4000*1.04,note='16:9 cover crops 42.5px from top and bottom; not yet rendered.')))
 review=Image.new('RGB',(1280,720),'#151515');dr=ImageDraw.Draw(review)
 for i,r in enumerate(final):
  a=Image.open(MEDIA/FILES[r['id']]).crop(boxes[r['id']]);a.thumbnail((420,660));x=i*426+(426-a.width)//2;review.paste(a,(x,40));dr.text((i*426+5,10),r['id']+' '+str(boxes[r['id']]),fill='white')
 review.save(OUT/'final_detail_crops.jpg',quality=92)
 im=Image.open(MEDIA/FILES['V01_full']).convert('RGB');im.thumbnail((1280,1280));d=ImageDraw.Draw(im)
 for row,color in zip(rows,['#ff4b40','#40ff80','#50b0ff']):
  pts=[(x*im.width/4000,y*im.width/4000) for x,y in row['polygon_in_full_px']];d.line(pts+[pts[0]],fill=color,width=3);d.text(pts[0],row['id'],fill=color,stroke_width=1)
 im.save(OUT/'detail_registration_overview.jpg',quality=91)
 sheet=Image.new('RGB',(1280,720),'#161616');d=ImageDraw.Draw(sheet)
 for i,(k,name) in enumerate(FILES.items()):
  im=Image.open(MEDIA/name);im.thumbnail((410,310));x=i%3*426;y=i//3*360;sheet.paste(im,(x+(426-im.width)//2,y+30));d.text((x+12,y+8),k,fill='white')
 sheet.save(OUT/'source_contact.jpg',quality=90)
 print(json.dumps(dict(assets=len(assets),scripts=scripts,overlap=pairs,residuals=[{k:r[k] for k in ['id','inliers','residual_rms_px','residual_max_px']} for r in rows]),ensure_ascii=False,indent=2))
if __name__=='__main__':main()
