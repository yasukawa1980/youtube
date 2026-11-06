"""EP012 N1：v02冒頭の絵を73px下げ、出典との間隔20pxを確保。"""
import argparse
import copy
import shutil
from pathlib import Path

from PIL import Image
import wom_shorts_ep012_v02 as shared

REPO=Path(__file__).resolve().parent
V01=shared.OLD
OLD=shared.ROOT
ROOT=OLD.parent/'EP012_v03_20261107'
REQUEST=REPO/'wom_ショートClaude確認_EP012_v02_20261107.md'
DEST=REPO/'wom_ショート確認版_EP012_v03_20261107'
TAG='quiet-origins-ep012-shorts-v03-20261107'
read,save,sha=shared.read,shared.save,shared.sha

def video(sid,version):
    # 共有処理内のv01/v02は、それぞれ比較元・出力という役割を表す。
    if sid=='N2':return V01/'deliverables/QO_short_EP012_N2_v01.mp4'
    folder,actual=(OLD,'v02') if version=='v01' else (ROOT,'v03')
    return folder/f'deliverables/QO_short_EP012_{sid}_{actual}.mp4'

def configure():
    shared.OLD=OLD;shared.ROOT=ROOT;shared.IDS=['N1'];shared.video=video;shared.OUTPUT_VERSION='v03'

def prepare():
    assert Path('/Volumes/ESD-02').is_mount()
    for d in ['records','review','deliverables','_work']:(ROOT/d).mkdir(parents=True,exist_ok=True)
    shutil.copy2(REQUEST,ROOT/'records/request.md')
    before=read(OLD/'records/visual_manifest.json');after=copy.deepcopy(before)
    g=next(g for g in after['shots'] if g['asset_id']=='N08_person')
    previous=copy.deepcopy(g);header_bottom=max(r['bbox'][3] for r in g['header_texts'])
    g['viewport'][1]=header_bottom+20
    # 機能変更はこのy座標のみ。倍率・原画・各レイヤー・切替時刻は固定。
    assert {k:v for k,v in g.items() if k!='viewport'}=={k:v for k,v in previous.items() if k!='viewport'}
    assert g['viewport'][0::2]==previous['viewport'][0::2] and g['viewport'][3]==previous['viewport'][3]
    oldlay=next(r for r in read(OLD/'records/layout.json') if r['id']=='N1');layout=copy.deepcopy(oldlay)
    delta=g['viewport'][1]-previous['viewport'][1]
    bounds=layout['display_bounds'];bounds[1]+=delta;bounds[3]+=delta
    layout.update(viewport=g['viewport'],before=previous['viewport'],shift_y_px=delta,header_bottom=header_bottom,header_gap_px=bounds[1]-header_bottom,caption_gap_px=layout['caption_top']-bounds[3],note='v02の大きさ・倍率・寄りを維持し、絵だけ73px下へ。絵下端の背景は字幕板に25px重なるが、人物・上着には重ならない。')
    assert layout['header_gap_px']>=20 and delta==73
    save(ROOT/'records/layout.json',layout);save(ROOT/'records/visual_manifest.json',after)
    names=['caption_manifest.json','cta_design.json','shorts.json','headlines.json','source_hashes.json']
    for name in names:shutil.copy2(OLD/'records'/name,ROOT/'records'/name)
    src=OLD/'deliverables/QO_short_EP012_N1_v02.srt';dst=ROOT/'deliverables/QO_short_EP012_N1_v03.srt';shutil.copy2(src,dst)
    shutil.copy2(OLD/'deliverables/N1_upload_info.md',ROOT/'deliverables/N1_upload_info.md')
    unchanged=read(OLD/'records/unchanged_inputs.json')
    unchanged.update(subtitles=[dict(id='N1',srt_sha256=sha(src),v03_srt_sha256=sha(dst))],records={n:sha(OLD/'records'/n) for n in names},baseline_version='v02',output_version='v03',n3_v02_sha256=sha(video('N3','v01')))
    save(ROOT/'records/unchanged_inputs.json',unchanged)
    s=next(s for s in read(OLD/'records/shorts.json')['shorts'] if s['id']=='N1');caps=read(OLD/'records/caption_manifest.json');helper=shared.base.helper()
    for n in [0,15,30,68,75,160]:
        im=helper.design_frame(s,n,after['shots'],caps,shared.base.frame_art);im.thumbnail((720,1280));im.save(ROOT/f'review/N1_{n:04}_design.jpg',quality=92,optimize=True)
    print('配置完了：',layout,flush=True)

def render():
    configure();shared.render()

def qc():
    configure();shared.qc()
    data=read(ROOT/'records/final_qc.json')
    for q in data:
        q['baseline_version']='v02';q['output_version']='v03'
        q['audio_pcm_md5_v03']=q.pop('audio_pcm_md5_v02');q['audio_pcm_md5_v02']=q.pop('audio_pcm_md5_v01')
    save(ROOT/'records/final_qc.json',data)
    p=ROOT/'records/N1_frame_comparison.json';frames=read(p)
    frames['revised_v03']=frames.pop('v02');frames['baseline_v02']=frames.pop('v01');save(p,frames)
    assert read(ROOT/'records/unchanged_inputs.json')['n3_v02_sha256']==sha(video('N3','v01'))
    # 0.5秒の出典と絵の境界を、原寸に近い倍率でも確認できるよう収録。
    from wom_shorts_remake_qc_v03 import decode
    arr=decode(video('N1','v02'),[15])[15];im=Image.fromarray(arr)
    im.crop((40,100,1040,400)).save(ROOT/'review/N1_0015_header_detail.jpg',quality=95,optimize=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','render','qc']);a=p.parse_args();globals()[a.stage]()
