"""Publish no video: share approved-brand full v09 in a non-public Draft Release."""
import html,os,shutil
from pathlib import Path
import wom01_share_opening_revision as shared
from wom01_integrate_brand import ROOT,REPO,read

def preview(root,files):
 cards=[]
 for p in files:
  if p.suffix!='.mp4':continue
  label=('日本語' if '_ja_' in p.name else 'English')+(' / 字幕入り確認用' if 'subtitled_review' in p.name else ' / 通常版・字幕焼き込みなし')
  src=html.escape(os.path.relpath(p,root/'deliverables'))
  cards.append(f'<section><h2>{label}</h2><video controls preload="metadata" src="{src}" data-fallback="{p.name}"></video></section>')
 out=root/'deliverables/preview.html';out.write_text('''<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Quiet Origins v09</title><style>body{max-width:1120px;margin:32px auto;padding:0 20px;background:#0c1820;color:#f4efdf;font:17px/1.6 system-ui}h1{color:#d8b575}h2{font-size:20px;font-weight:500}section{margin:30px 0}video{width:100%;max-height:75vh;background:#000}</style><h1>Quiet Origins / Anubis v09</h1><p>オープニングとエンドカードを組み込んだ全編・11分42秒です。ロゴは00:29〜00:33、エンドカードは11:22〜11:42。通常版と字幕入り確認用を選べます。</p>'''+''.join(cards)+'''<script>document.querySelectorAll('video').forEach(v=>{v.addEventListener('error',()=>{if(!v.dataset.tried){v.dataset.tried='1';v.src=v.dataset.fallback;}});v.addEventListener('play',()=>document.querySelectorAll('video').forEach(w=>{if(w!==v)w.pause()}));});</script></html>''');return out

def main():
 assert read(ROOT/'records/metadata_validation.json')['passed']
 assert read(ROOT/'records/source_preservation.json')['passed']
 assert read(ROOT/'records/brand_subtitle_absence.json')['passed'] and read(ROOT/'records/chapter_frame_checks.json')['passed']
 assert len(read(ROOT/'subtitled_review/records/qc.json')['files'])==2
 shared.ROOT=ROOT;shared.preview=preview
 for lang in ['en','ja']:shutil.copy2(ROOT/f'deliverables/EP001_投稿用情報_{lang}.md',ROOT/f'deliverables/EP001_upload_info_{lang}.md')
 files=[ROOT/f'deliverables/EP001_Anubis_{lang}_v09_1080p30.{ext}' for lang in ['en','ja'] for ext in ['mp4','srt']]
 files += [ROOT/f'subtitled_review/deliverables/EP001_Anubis_{lang}_v09_subtitled_review_1080p30.mp4' for lang in ['en','ja']]
 files += [ROOT/'deliverables'/n for n in ['EP001_audio_en.m4a','EP001_audio_ja.m4a','EP001_thumbnail_en.jpg','VOICE_CREDITS.txt','EP001_upload_info_en.md','EP001_upload_info_ja.md']]
 body='''本人が試聴承認したv08＋オープニングv02（4秒）＋エンドカードv01（20秒）を全編へ組み込み。702.000秒、21,060フレーム、1080p30。英日で映像ストリームは同一。ロゴ29.066667〜33.066667秒、エンドカード682〜702秒、先頭0.7秒ディゾルブ。

通常版は字幕焼き込みなし。英150・日136件のSRTは本文と改行を保ち、N02以降+4秒。最後の日本語お礼は681.691秒まで残し、682秒以降は字幕なし。字幕入り確認用コピーも添付。

本編音声を全体再正規化せず、接続部以外は元の音量を維持。動画は共通映像をCRF18で一度書き出し、英日音声をAAC192kで別々に結合。チャプターと女性声クレジットを更新した英日投稿情報を添付。

本人の公開指示待ち。YouTube投稿・Release公開・追加支出は行っていない。'''
 shared.share(ROOT,'wom01-integrated-v09-20261021','Quiet Origins：アヌビス v09（オープニング・エンドカード組み込み全編）',body,files,REPO/'new-channel/wom01_全編組み込み_v09_20261021','qc_v09.json')
if __name__=='__main__':main()
