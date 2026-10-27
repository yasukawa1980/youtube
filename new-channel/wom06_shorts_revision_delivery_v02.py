"""Comparison preview and private draft delivery for the Sphinx hook revision."""
import os,sys,html,json,shutil,zipfile
from pathlib import Path
import wom06_shorts_revision_v02 as rev
os.environ['QO_EP006_RELEASE_TAG']='qo-shorts-ep006-hook-v02-20261027'
os.environ['QO_EP006_RELEASE_NAME']='Quiet Origins：スフィンクス ショート冒頭比較 v02'
os.environ['QO_EP006_RELEASE_BODY']='本人依頼でS1・S3を結論先行の冒頭へ修正。S2はv01のバイト同一コピー。尺・話速・素材・末尾CTAを維持、字幕とカット時刻を再同期。YouTube未投稿。v01を保全した非公開Draft。旧版はRelease 425054637。'
import wom06_shorts_delivery as delivery
ROOT=rev.ROOT

def docs():
 delivery.docs()
 rows=rev.render.read(ROOT/'records/shorts.json')['shorts']
 sections=[]
 for s in rows:
  sid=s['id'];stem=f'QO_short_EP006_{sid}'
  old=f'../../{rev.OLD.name}/deliverables/{stem}_v01.mp4'
  label={'S1':'謎の言葉は劇で語られない','S2':'ギザのスフィンクス（変更なし）','S3':'鼻はナポレオン以前から欠けていた'}[sid]
  sections.append(f'<section><h2>{sid}｜{label}</h2><div class="pair"><article><h3>元の完成版 v01</h3><video controls preload="metadata" src="{html.escape(old)}"></video></article><article><h3>{"変更なし・同一ファイル" if sid=="S2" else "冒頭修正版 v02"}</h3><video controls preload="metadata" src="{stem}_v02.mp4"></video></article></div><p>{s["duration_seconds"]:.2f}秒。'+('S2は比較基準として元の完成版を維持。' if sid=='S2' else '英語・声・話速・素材順・末尾案内を維持し、冒頭の主張を先に。')+'</p><details><summary>修正版の英語台本</summary><p>'+html.escape(s['text'])+'</p></details></section>')
 page='''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>スフィンクス｜冒頭の比較</title><style>body{max-width:1000px;margin:32px auto;padding:0 22px;background:#101c22;color:#f5efdf;font:17px/1.7 system-ui}h1,h2,h3{color:#d4b87c}h1{font-size:30px}h2{font-size:23px}h3{font-size:16px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}section{border-top:1px solid #405052;margin-top:32px;padding:20px 0}video{width:100%;max-height:65vh;background:#050a0d}details{background:#1e3038;padding:12px 18px;border-radius:8px}a{color:#d4b87c}@media(max-width:600px){.pair{grid-template-columns:1fr}}p{max-width:75ch}</style><h1>スフィンクスのショート<br>冒頭の比較</h1><p>S1とS3は、意外な結論を最初に伝える形へ。S2はすでに結論から始まるため、そのまま残しています。YouTubeには投稿していません。</p><p>まず左右をそれぞれ最初の5秒まで再生し、話の面白さが伝わる早さを比較してください。その後、全編の読みと字幕をご確認ください。再生すると他の動画は一時停止します。</p>'''+''.join(sections)+'''<p>このMacでは旧版も再生できます。Draftをダウンロードした場合の旧版は、Release 425054637を参照してください。</p><script>document.querySelectorAll('video').forEach(v=>v.addEventListener('play',()=>document.querySelectorAll('video').forEach(w=>{if(w!==v)w.pause()})));</script></html>'''
 (ROOT/'deliverables/preview.html').write_text(page)
 # Bundle the exact revision configuration and reproducible runner alongside QC.
 with zipfile.ZipFile(ROOT/'deliverables/production_records.zip','a',zipfile.ZIP_DEFLATED) as z:
  for name in ['wom06_shorts_revision_v02.py','wom06_shorts_revision_delivery_v02.py','wom06_shorts_v02_config.json','wom_ショート冒頭修正_EP006_v02_20261027.md']:
   z.write(rev.HERE/name,'revision/'+name)
 print('COMPARISON PAGE READY',flush=True)

if __name__=='__main__':
 if sys.argv[1]=='docs':docs()
 elif sys.argv[1]=='share':delivery.share()
 else:raise SystemExit('docs|share')
