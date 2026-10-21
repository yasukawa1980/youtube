"""Verify v07's scope/preservation and create before/after review sheets.

Run after the layout stage. Human/model visual inspection is recorded separately.
"""
import os, json
from pathlib import Path
from PIL import Image,ImageDraw
from wom01_multilingual_render import read,save,sha
ROOT=Path(os.environ['WOM_EPISODE_ROOT']);PREV=Path(os.environ['WOM_PREVIOUS_ROOT']);SOURCE=Path(os.environ['WOM_SOURCE_ROOT'])

def main():
    old=read(PREV/'records/render_shots.json');new=read(ROOT/'records/render_shots.json');results=[];changed=[]
    for i,(a,b) in enumerate(zip(old,new)):
        assert all(a[k]==b[k] for k in ['key','segment_id','frames','start','end'])
        identical_image=sha(PREV/a['file'])==sha(ROOT/b['file'])
        identical_encoded=sha(PREV/a['encoded_file'])==sha(ROOT/b['encoded_file'])
        assert identical_image==identical_encoded==(not b['changed_in_v07'])
        if b['changed_in_v07']:
            changed.append((i,b));assert b['picture_and_text_bottom_px']<=700
            for component in b['components']:
                x,y,x2,y2=component['display_bbox'];assert 0<=x<x2<=1920 and 220<=y<y2<=700
            if b['key']=='roles':
                names=['Anubis','アヌビス','Thoth','トト','Osiris','オシリス']
                assert [t for t in a['screen_text'] if t['text'] in names]==[t for t in b['screen_text'] if t['text'] in names]
        results.append({'shot':i+1,'segment':b['segment_id'],'key':b['key'],'unchanged_image':identical_image,'unchanged_encoded_video':identical_encoded})
    assert len(changed)==9 and len(results)==55
    preserved=[]
    for line in (PREV/'deliverables/SHA256SUMS_shared.txt').read_text().splitlines():
        expected,name=line.split('  ',1);matches=list((PREV/'deliverables').glob(name))+list((PREV/'subtitled_review/deliverables').glob(name));assert matches
        assert all(sha(p)==expected for p in matches);preserved.append(name)
    for name in ['EP001_thumbnail_en.jpg','EP001_audio_en.m4a','EP001_audio_ja.m4a','VOICE_CREDITS.txt']:
        assert sha(ROOT/'deliverables'/name)==sha(PREV/'deliverables'/name)
    layout=read(ROOT/'records/subtitle_layout_all.json')
    for check in layout['checks']:
        check['diagram_band_clearance']=check['subtitle_top']-710
        assert check['diagram_band_clearance']>0
    layout['text_min_clearance']=min(c['conservative_clearance'] for c in layout['checks'])
    layout['min_clearance']=min(c['diagram_band_clearance'] for c in layout['checks'])
    layout['diagram_bottom_bound_including_camera_px']=710
    layout['method']='Actual MP4/SRT at all cue overlaps, FontSize14/26; additionally require subtitles below full diagram band y700 plus ten-pixel camera margin.'
    save(ROOT/'records/subtitle_layout_all.json',layout)
    # Actual encoded midpoints side by side, v06 left / v07 right.
    for offset in range(0,len(changed),3):
        sheet=Image.new('RGB',(1280,1170),'#0c1820');d=ImageDraw.Draw(sheet)
        for j,(i,s) in enumerate(changed[offset:offset+3]):
            for col,root in enumerate([PREV,ROOT]):
                im=Image.open(root/f'review/mid_{i:02}.jpg');im.thumbnail((640,360));sheet.paste(im,(col*640,j*390+30))
                d.text((col*640+10,j*390+8),f'v0{6+col} | Shot {i+1:02} | {s["segment_id"]} {s["key"]}',fill='white')
        sheet.save(ROOT/f'review/v07_before_after_{offset//3+1:02}.jpg',quality=90)
    # The exact rectangles on scaled original museum images.
    sheet=Image.new('RGB',(1280,700),'#0c1820');d=ImageDraw.Draw(sheet)
    role=next(s for s in new if s['key']=='roles');colors={'anubis':'#ffad47','thoth':'#ffad47','osiris':'#79e9ff'}
    for col,oid in enumerate(['548344','552247']):
        src=Image.open(SOURCE/f'assets/museum/met_{oid}.jpg').convert('RGB');scale=min(620/src.width,620/src.height)
        src=src.resize((round(src.width*scale),round(src.height*scale)));origin=(col*640+10,50);sheet.paste(src,origin)
        d.text((col*640+10,12),f'Met {oid} | crop rectangles on source',fill='white')
        for c in role['components']:
            if oid not in c['source']:continue
            box=[round(c['crop_pixels'][j]*scale)+(origin[0] if j%2==0 else origin[1]) for j in range(4)]
            d.rectangle(box,outline=colors[c['key']],width=3);d.text((box[0]+5,box[1]+5),c['key'],fill=colors[c['key']])
    sheet.save(ROOT/'review/v07_crop_sources.jpg',quality=90)
    save(ROOT/'records/scope_verification_v07.json',{'passed':True,'changed_shots':9,'unchanged_shots':46,'shots':results,'v06_shared_files_preserved':preserved,'role_name_positions_unchanged':True,'thumbnail_audio_files_identical':True})
    print('SCOPE PASS: 9 changed, 46 bit-identical shots; v06 shared files preserved',flush=True)
if __name__=='__main__':main()
