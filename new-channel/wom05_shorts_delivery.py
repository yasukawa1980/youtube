"""Private draft delivery of EP005 Shorts; Release-ID REST verification."""
import argparse,csv,hashlib,html,shutil,subprocess
from pathlib import Path
from PIL import Image
from wom05_shorts import ROOT,read,save,sha,FPS
from wom02_delivery import api
GH='yasukawa1980/youtube'
TAG='qo-shorts-ep005-complete-v01-20261024'

def docs():
 rows=[s for s in read(ROOT/'records/shorts.json')['shorts'] if s['id'] in {m['id'] for m in read(ROOT/'records/media_qc.json')['media']}];pages=read(ROOT/'records/caption_manifest.json');qc=read(ROOT/'records/media_qc.json');assert qc['passed']
 def stamp(frame):
  ms=round(frame/FPS*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 for s in rows:
  stem=f'QO_short_{s["episode"]}_{s["id"]}_v01';groups=[p for p in pages if p['short_id']==s['id']]
  (ROOT/f'deliverables/{stem}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(p["start_frame"])} --> {stamp(p["end_frame"])}\n'+ '\n'.join(p['lines']) for i,p in enumerate(groups))+'\n')
  for suffix in ['mid','every2s']:shutil.copy2(ROOT/f'review/{stem}_{suffix}.jpg',ROOT/f'deliverables/{stem}_{suffix}.jpg')
 (ROOT/'deliverables/scripts.txt').write_text('\n\n'.join(f'{s["episode"]} {s["id"]} — {s["title_ja"]}\n{s["text"]}' for s in rows)+'\n')
 fields=['id','name','duration_seconds','frames','lufs','true_peak_dbtp','voice_onset_normalized_stem_seconds','bgm_during_narration_dbfs','cta_seconds']
 with (ROOT/'deliverables/qc_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows({k:s[k] for k in fields} for s in qc['media'])
 cards=''.join(f'<section><h2>{s["episode"]} {s["id"]} — {html.escape(s["title_ja"])}</h2><video controls preload="metadata" src="QO_short_{s["episode"]}_{s["id"]}_v01.mp4"></video><p>{s["duration_seconds"]:.2f}秒・英語字幕入り</p></section>' for s in rows)
 (ROOT/'deliverables/preview.html').write_text('<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins Shorts v01</title><style>body{max-width:1100px;margin:28px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1,h2{color:#d8b575}h2{font-size:18px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px}video{width:100%;max-height:72vh;background:#000}a{color:#d8b575}</style><h1>Quiet Origins / Tengu Shorts v01</h1><p>第5話天狗 確認用。英語音声・英語字幕、縦1080×1920。確認用・未投稿。3本完成。T2は本人の方針に従い21.13秒、語りと鳶の動きのバランスを優先。</p><main>'+cards+'</main><script>document.querySelectorAll("video").forEach(v=>v.addEventListener("play",()=>document.querySelectorAll("video").forEach(w=>{if(w!==v)w.pause()})));</script></html>')
 with (ROOT/'deliverables/motion_qc.csv').open('w',newline='') as f:
  fields=['short_id','asset_id','frame_pairs','median','p95','p95_over_median','passed']
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for p in read(ROOT/'records/motion_qc.json')['checks']:
   w.writerow(dict(short_id=p['short_id'],asset_id=p['asset_id'],passed=p['passed'],**{k:p['measurement'][k] for k in fields[2:-1]}))
 print('DOCS COMPLETE',flush=True)


def selected_files():
    files=sorted(p for p in (ROOT/'deliverables').iterdir() if p.suffix in ['.mp4','.srt','.jpg','.csv','.txt','.html','.wav'] and p.name not in ['SHA256SUMS_shared.txt','T2_timing_pending.txt','EP005_T2_native_for_script_review.wav'])
    assert files and sum(p.suffix=='.mp4' for p in files)==len(read(ROOT/'records/media_qc.json')['media'])
    return files

def share():
    qc=read(ROOT/'records/media_qc.json')
    visual=read(ROOT/'records/visual_review.json')
    assert all(read(ROOT/'records'/n)['passed'] for n in ['media_qc.json','visual_review.json','motion_qc.json','subtitle_qc.json','asset_usage.json'])
    for m in qc['media']:
        assert sha(ROOT/'deliverables'/m['name'])==m['sha256']==visual['video_sha256'][m['id']]
    files=selected_files()
    check=ROOT/'deliverables/SHA256SUMS_shared.txt'
    check.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(check)
    state=ROOT/'records/sharing_complete.json'
    if state.exists(): r=api([f'repos/{GH}/releases/{read(state)["release_id"]}'])
    else:
        r=next((r for r in api([f'repos/{GH}/releases?per_page=100']) if r['tag_name']==TAG),None)
        if r is None:
            r=api(['--method','POST',f'repos/{GH}/releases','--input','-'],dict(tag_name=TAG,target_commitish='bgm/production',name='Quiet Origins：天狗 ショート確認版 v01',body='本人依頼・Claudeの台本を維持。英語Kokoro af_heart、縦1080×1920・30fps。検査合格済みの動画と記録。T1/T3 20秒、T2 21.13秒。本人の尺制限解除を反映し、台本と鳶の後半の速さを維持。YouTube未投稿、非公開Draftを維持。',draft=True))
    assert r['draft'] and r['published_at'] is None
    prior=read(state) if state.exists() else {}
    verified=prior.get('assets',prior.get('verified_assets',[]))
    save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='uploading',verified_assets=verified))
    for p in files:
        a=next((a for a in r['assets'] if a['name']==p.name),None)
        if a: assert a['state']=='uploaded' and a['size']==p.stat().st_size and a['digest']=='sha256:'+sha(p)
        else: subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
        print('UPLOADED',p.name,flush=True)
    r=api([f'repos/{GH}/releases/{r["id"]}'])
    assert r['draft'] and r['published_at'] is None and len(r['assets'])==len(files)
    checks=[]
    for p in files:
        a=next(a for a in r['assets'] if a['name']==p.name)
        cached=next((c for c in verified if c['asset_id']==a['id'] and c['sha256']==sha(p) and c['bytes']==p.stat().st_size and c['rest_download_verified']),None)
        if cached: checks.append(cached)
        else:
            for attempt in range(3):
                proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE)
                h=hashlib.sha256();count=0
                while True:
                    b=proc.stdout.read(1048576)
                    if not b: break
                    count+=len(b);h.update(b)
                ok=proc.wait()==0 and count==p.stat().st_size and h.hexdigest()==sha(p)==a['digest'].removeprefix('sha256:')
                if ok: break
            assert ok,p.name
            checks.append(dict(name=p.name,asset_id=a['id'],bytes=count,sha256=h.hexdigest(),rest_download_verified=True))
        save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='verifying',verified_assets=checks))
        print('REST VERIFIED',p.name,flush=True)
    save(state,dict(release_id=r['id'],release_url=r['html_url'],draft=True,status='verified',assets=checks))
    print('SHARED',r['id'],len(checks),flush=True)


if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['docs','share']);a=p.parse_args();globals()[a.stage]()
