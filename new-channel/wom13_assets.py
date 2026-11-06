"""Validate the owner-approved IIIF tiles and assemble lossless EP013 masters.

No image downloads, retouching, resampling, or AI reconstruction.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parent.parent
MEDIA = Path('/Volumes/ESD-02/新チャンネル/EP013_NightWatch/素材')
TILES = MEDIA / 'IIIF_原寸タイル_20261107'
RECORDS = REPO / 'new-channel/research'
PREVIEW = REPO / '_work/wom13-assets-preview'
Image.MAX_IMAGE_PIXELS = 200_000_000

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()

def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    assert Path('/Volumes/ESD-02').is_mount(), '指定SSD未接続'
    source = RECORDS / 'wom13_原寸取得記録_20261107.json'
    data = json.loads(source.read_text())
    assert json.loads((TILES/'取得記録.json').read_text()) == data
    checks = []
    # All inputs must pass before any assembled output is written.
    for item in data['items']:
        folder = TILES / (item['id'] + '_' + item['object'])
        info = json.loads((folder/'info.json').read_text())
        for key in ['width', 'height', 'maxArea']: assert info[key] == item[key]
        rectangles = []
        for tile in item['tiles']:
            p = folder / tile['file']
            assert sha(p) == tile['sha256'], f'SHA mismatch: {p}'
            assert p.stat().st_size == tile['bytes']
            with Image.open(p) as im:
                im.load()
                assert im.size == (tile['w'], tile['h']) and im.mode == 'RGB'
                profile = hashlib.sha256(im.info.get('icc_profile', b'')).hexdigest()
            x,y,w,h = [tile[k] for k in ['x','y','w','h']]
            assert 0 <= x < x+w <= item['width'] and 0 <= y < y+h <= item['height']
            for a,b,c,d in rectangles:
                assert min(x+w,c) <= max(x,a) or min(y+h,d) <= max(y,b), 'Overlap'
            rectangles.append((x,y,x+w,y+h))
            checks.append({'id':item['id'],'file':str(p),'sha256':tile['sha256'],'size':[w,h],'mode':'RGB','icc_sha256':profile,'ok':True})
        assert sum((c-a)*(d-b) for a,b,c,d in rectangles) == item['width']*item['height']
    save(RECORDS/'wom13_タイル照合_20261107.json', {'count':len(checks),'all_match':True,'tiles':checks})
    print('All',len(checks),'tile hashes, sizes, coverage verified', flush=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    assembled = []
    for item in data['items']:
        folder = TILES / (item['id']+'_'+item['object'])
        out = MEDIA / (item['id']+'_'+item['object']+'_原寸.png')
        canvas = Image.new('RGB', (item['width'],item['height']))
        profiles = set()
        for tile in item['tiles']:
            with Image.open(folder/tile['file']) as im:
                canvas.paste(im, (tile['x'],tile['y']))
                profiles.add(im.info.get('icc_profile',b''))
        assert len(profiles) == 1, 'ICC profile mismatch'
        kwargs = {'icc_profile':next(iter(profiles))} if next(iter(profiles)) else {}
        if out.exists():
            with Image.open(out) as previous:
                assert previous.size == canvas.size
                for tile in item['tiles']:
                    box=(tile['x'],tile['y'],tile['x']+tile['w'],tile['y']+tile['h'])
                    assert np.array_equal(np.asarray(previous.crop(box)),np.asarray(canvas.crop(box)))
        else: canvas.save(out, format='PNG', compress_level=6, **kwargs)
        # Absolute RGB sample differences across boundaries, 8-bit [0,255].
        seams = []
        for axis in ['x','y']:
            for k in sorted({t[axis] for t in item['tiles']} - {0}):
                if axis=='x':
                    a=np.asarray(canvas.crop((k-1,0,k,item['height'])),dtype=np.int16)
                    b=np.asarray(canvas.crop((k,0,k+1,item['height'])),dtype=np.int16)
                else:
                    a=np.asarray(canvas.crop((0,k-1,item['width'],k)),dtype=np.int16)
                    b=np.asarray(canvas.crop((0,k,item['width'],k+1)),dtype=np.int16)
                diff=np.abs(a-b)
                seams.append({'axis':axis,'boundary':k,'mean_abs_rgb':float(diff.mean()),'max_abs_rgb':int(diff.max()),'p95_abs_rgb':float(np.percentile(diff,95))})
        # Check the actual PNG preserves every decoded tile exactly.
        with Image.open(out) as reread:
            assert reread.size == canvas.size and reread.mode == 'RGB'
            for tile in item['tiles']:
                with Image.open(folder/tile['file']) as im:
                    box=(tile['x'],tile['y'],tile['x']+tile['w'],tile['y']+tile['h'])
                    assert np.array_equal(np.asarray(reread.crop(box)), np.asarray(im))
        preview = canvas.copy();preview.thumbnail((1600,1600));preview.save(PREVIEW/(item['id']+'.jpg'),quality=94)
        row={'id':item['id'],'file':str(out),'width':canvas.width,'height':canvas.height,'mode':'RGB','bit_depth_per_channel':8,'bytes':out.stat().st_size,'sha256':sha(out),'tile_pixel_equality':True,'seams':seams,'seam_note':'Adjacent pixels depict different source positions; nonzero differences alone do not establish a seam defect. Visual review is separate.'}
        assembled.append(row)
        save(RECORDS/'wom13_原寸結合検証_20261107.json',{'items':assembled,'complete':len(assembled)==len(data['items'])})
        print(item['id'],row['width'],row['height'],row['bytes'], 'seams',len(seams),flush=True)
        canvas.close()

if __name__ == '__main__': main()
