"""Compare seam gradients with neighbouring columns/rows and save native patches."""
import json
import numpy as np
from PIL import Image,ImageDraw
from wom13_geometry import crop_native,ITEMS,OUT
from wom13_assets import RECORDS,save

rows=[];patches=[]
for item in json.loads((RECORDS/'wom13_原寸結合検証_20261107.json').read_text())['items']:
    id=item['id'];W,H=item['width'],item['height']
    for seam in item['seams']:
        axis,k=seam['axis'],seam['boundary']
        box=(k-9,0,k+9,H) if axis=='x' else (0,k-9,W,k+9)
        a=np.asarray(crop_native(id,box),dtype=np.int16)
        diffs=np.abs(np.diff(a,axis=1 if axis=='x' else 0))
        means=diffs.mean(axis=(0,2) if axis=='x' else (1,2))
        centre=diffs[:,8,:] if axis=='x' else diffs[8,:,:]
        location=int(np.argmax(centre.max(axis=1)))
        baseline=float(np.median(np.delete(means,8)))
        row={'id':id,'axis':axis,'boundary':k,'mean_at_seam':float(means[8]),'median_mean_of_16_neighbour_differences':baseline,'ratio':float(means[8]/baseline),'max_abs_rgb':int(centre.max()),'native_patch_location':location}
        rows.append(row)
        if axis=='x':l=max(0,min(W-256,k-128));t=max(0,min(H-128,location-64))
        else:l=max(0,min(W-256,location-128));t=max(0,min(H-128,k-64))
        patches.append((row,crop_native(id,(l,t,l+256,t+128)),(k-l,None) if axis=='x' else (None,k-t)))
panel=Image.new('RGB',(1280,4*170),'#181818');d=ImageDraw.Draw(panel)
for i,(row,patch,marker) in enumerate(patches):
    x=(i%4)*320;y=(i//4)*170;panel.paste(patch,(x+32,y+35))
    d.text((x+5,y+4),f"{row['id']} {row['axis']}={row['boundary']} ratio={row['ratio']:.3f}",fill='white')
    if marker[0] is not None:d.line((x+32+marker[0],y+25,x+32+marker[0],y+33),fill='#f5c885',width=2)
    else:d.line((x+22,y+35+marker[1],x+30,y+35+marker[1]),fill='#f5c885',width=2)
panel.save(OUT/'接合16境界_原寸抜粋.jpg',quality=94)
save(RECORDS/'wom13_接合近傍比較_20261107.json',{'seams':rows,'ratio_range':[min(r['ratio'] for r in rows),max(r['ratio'] for r in rows)],'note':'8-bit decoded RGB; each seam compared to sixteen neighbouring row/column gradients. Patches show the maximum-difference location at1:1. Nonzero values include painting texture and JPEG encoding; metric alone cannot prove absence of every artifact.'})
print('seams',len(rows),'ratio range',min(r['ratio'] for r in rows),max(r['ratio'] for r in rows),flush=True)
