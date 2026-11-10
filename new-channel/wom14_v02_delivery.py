"""Bundle verified v02 results without regenerating v01 audio or subtitles."""
import json,shutil,zipfile,os,sys
from pathlib import Path
from PIL import Image
from wom14_v02 import ROOT,BASE,REPO,read,save,sha
SHARE=REPO/'new-channel/wom14_確認版_v02_20261110';D=ROOT/'deliverables'

def archive():
 assert read(ROOT/'records/visual_review_v02.json')['reviewed']
 for lang,scale in [('en',1),('ja',1),('en',2)]:
  suffix='_4k' if scale==2 else ''
  for name in [f'pixel_identity_v02{suffix}.json',f'continuous_qc{suffix}.json',f'motion_v02{suffix}.json']:assert read(ROOT/lang/'records'/name)['passed']
 for lang in ['en','ja']:assert read(ROOT/lang/'records/subtitled_v02.json')['passed']
 for lang in ['en','ja']:
  for p in (ROOT/lang/'deliverables').iterdir():
   if p.suffix in ['.mp4','.srt','.m4a','.wav']:shutil.copy2(p,D/p.name)
  dest=SHARE/'records'/lang;dest.mkdir(parents=True,exist_ok=True)
  for p in (ROOT/lang/'records').glob('*.json'):shutil.copy2(p,dest/p.name)
  for pattern in ['*sheet*.jpg','*pair.jpg','opening_*.jpg','stage_*.jpg','subtitle_sample_*.jpg']:
   for p in (ROOT/lang/'review').glob(pattern):
    with Image.open(p) as im:assert max(im.size)<=1280 and p.stat().st_size<1_000_000
    shutil.copy2(p,SHARE/p.name)
 for p in (ROOT/'records').glob('*.json'):
  if p.name not in ['sharing.json','deliverable_manifest.json','pipeline_v02.json']:shutil.copy2(p,SHARE/'records'/p.name)
 for p in (BASE/'deliverables').glob('*.md'):shutil.copy2(p,D/p.name);shutil.copy2(p,SHARE/p.name)
 for p in (BASE/'deliverables').glob('*pronunciation*.txt'):shutil.copy2(p,D/p.name);shutil.copy2(p,SHARE/p.name)
 for p in D.glob('*.srt'):shutil.copy2(p,SHARE/p.name)
 audiozip=BASE/'deliverables/EP014_audio_and_subtitles_v01.zip';newaudio=D/'EP014_audio_and_subtitles_v02.zip';shutil.copy2(audiozip,newaudio);assert sha(audiozip)==sha(newaudio)
 save(ROOT/'records/audio_subtitle_bundle_identity.json',dict(v01_sha256=sha(audiozip),v02_sha256=sha(newaudio),byte_identical=True,note='Archive filenames inside remain v01 because the audio/SRT bundle is an exact copy. Individual v02 SRT files are also identical to v01.'))
 shutil.copy2(ROOT/'records/audio_subtitle_bundle_identity.json',SHARE/'records/audio_subtitle_bundle_identity.json')
 groups={'thumbnails_and_metadata':list(D.glob('*.jpg'))+list(D.glob('*.md')),'QA_records':[p for p in (SHARE/'records').rglob('*.json') if p.name not in ['sharing.json','deliverable_manifest.json','pipeline_v02.json']]+list(SHARE.glob('*.jpg'))+[p for lang in ['en','ja'] for p in (ROOT/lang/'records').glob('*.framemd5')]}
 for name,files in groups.items():
  p=D/f'EP014_{name}_v02.zip'
  with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
   for f in sorted(files):
    arc=f.relative_to(SHARE) if f.is_relative_to(SHARE) else Path('frame_hashes')/f.parent.parent.name/f.name if f.suffix=='.framemd5' else f.name
    z.write(f,arc)
  with zipfile.ZipFile(p) as z:assert z.testzip() is None
 files=sorted([*D.glob('*v02*.mp4'),*D.glob('*v02.zip')]);assert len(files)==8
 save(ROOT/'records/deliverable_manifest.json',[dict(name=p.name,bytes=p.stat().st_size,sha256=sha(p)) for p in files]);shutil.copy2(ROOT/'records/deliverable_manifest.json',SHARE/'records/deliverable_manifest.json');print('ARCHIVES READY',flush=True)

def report():
 s=read(ROOT/'records/sharing.json');assert s['draft'] and s['status']=='verified' and len(s['assets'])==8 and s['release_id']!=439388240
 shutil.copy2(ROOT/'records/sharing.json',SHARE/'records/sharing.json')
 lines=['# Quiet Origins 第14話「鬼」確認版v02 制作結果（2026-11-10）','','Claude確認v01の映像4点を修正。音声・SRT・時間割・ショット境界を維持。v01 Release 439388240は保全。公開・予約はしていない。','',f"[確認版v02の非公開Draft Release]({s['release_url']})（ID `{s['release_id']}`）。動画5本・ZIP3件をRESTで全量再取得し、サイズとSHA-256一致、匿名404を確認。",'', '## 修正内容','','1. O02-A：全体を2秒保持したあと、鬼2体へ原寸1.0倍まで連続して寄る。取得原寸の鬼の範囲は約359px（1080pの約33.3%）。40%に届かないため、本人回答で原寸上限を優先。4Kも原寸以上に拡大しない。','2. O02-B：本紙内の人物部分だけを切り出し、黒い撮影背景・白い棒を除外。長さは維持。','3. 原典6頁：列の順序を変えず、囲みと前後の文字へ寄る。長い引用は上下に移動して見せる。最初の全体表示は2秒。囲みの出現フレームはv01と同一。O06-38は目／一鬼の2列を一つの囲みとして維持し、下端の目から上端の一鬼へ移動する。','4. サムネA/B：絵の大きさを維持して80px上へ移し、牙の下端を帯の上へ出した。Bの文字欄は絵の右端から30px離した。','', '## 不変の映像・音声・字幕','','通常英日1080pと英語4Kは変更対象だけを再描画し、変更しない区間のv01 AVCパケットを保持。境界はIDRと一致する区間を使う。v01の「全編一つのエンコーダー」方式で再圧縮すると画素が変わるため、今回の明示指定である画素一致を優先した。','', '|出力|総フレーム|未修正ショット|未修正フレーム|画素差|尺|','|---|---:|---:|---:|---:|---:|']
 for lang,scale in [('en',1),('ja',1),('en',2)]:
  suffix='_4k' if scale==2 else '';p=read(ROOT/lang/f'records/pixel_identity_v02{suffix}.json');lines.append(f"|{lang} {2160 if scale==2 else 1080}p|{p['frames']}|{p['unchanged_shots']}|{p['unchanged_frames']}|全フレーム0|{p['duration']:.3f}秒|")
 lines+=['','全未修正フレームのデコード済みyuv420p画素を比較。各ショットの結果は `pixel_identity_v02*.json`、フレームごとのMD5はQA ZIPの `frame_hashes/`。音声は圧縮ストリームSHA-256一致、SRT・時間割JSONはバイト一致。音声・字幕ZIPもv01とバイト一致（ZIP内部のファイル名はv01のまま）。','', '字幕入り確認版のみ、本人回答により再圧縮差を許容。未修正ショットの画素一致は通常3本について保証する。字幕入り英日版も字幕内容・時刻と音声の一致を検証済み。方針は `user_clarifications.json`、結果は各言語の `subtitled_v02.json` に記録。','', '## 検品と文字寸法','','全5動画はH.264 High／yuv420p／30fps、連続PTS、連続デコード警告0。通常3本は全フレームの形式1種類も検証。通常3本の全31ショットの先頭・中央・末尾、修正箇所のv01/v02比較を添付。字幕入り版は英日各8修正ショットを画面確認。原典の注との間隔14px（注のない頁は見出し線から9px）、字幕上端との最小間隔27px。4Kは座標間隔2倍。','', '文字寸法は原画像の字枠・行送りと、黒い筆画の実寸を区別。1080pの字枠高は57.3px以上だが、R10-27の「土」「大」などの筆画高は原寸で約44pxであり、55px条件は未達。本人回答により、この頁も原寸1.0倍を優先する。4Kも原寸上限を守る。測定は `R10_native_letter_measurement.json`、倍率・囲み時刻は `visual_geometry_v02.json`。比較画像の1.25倍案は未採用。','', '|出力|O02-A 動きp95/中央値|','|---|---:|']
 for lang,scale in [('en',1),('ja',1),('en',2)]:
  p=read(ROOT/lang/f'records/motion_v02{"_4k" if scale==2 else ""}.json');lines.append(f"|{lang} {2160 if scale==2 else 1080}p|{p['ratio']:.3f}|")
 lines+=['', '本人の試聴は同一音声のv01でも継続可能。公開予定は11/18 09:00 JST。本人の試聴・Claude確認・サムネ選択の後に別の投稿依頼で進める。','',f'原寸・出力保存先：`{ROOT}`。']
 (REPO/'new-channel/wom14_制作結果_v02_20261110.md').write_text('\n'.join(lines)+'\n')
 r=['# 第14話「鬼」確認版v02','',f"[非公開Draft Release]({s['release_url']})（ID `{s['release_id']}`）。v01（439388240）は保全。",'', '[制作結果](../wom14_制作結果_v02_20261110.md)。英日1080p、英語4K、字幕入り英日、音声・字幕ZIP、サムネ・投稿情報ZIP、QA ZIP。','', '|添付|asset ID|バイト|SHA-256|','|---|---:|---:|---|']
 for a in s['assets']:r.append(f"|{a['name']}|{a['asset_id']}|{a['bytes']}|`{a['sha256']}`|")
 r+=['',f"取得：`gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT`。Release ID一覧：`gh api repos/yasukawa1980/youtube/releases/{s['release_id']}`。",'', '音声・字幕ZIPはv01と完全に同じバイト列。通常3本の未修正全フレーム画素一致の台帳はQA ZIPの `frame_hashes/`。比較画像は左v01、右v02。','',f'SSD：`{ROOT}`。公開・予約はしていない。']
 (SHARE/'README.md').write_text('\n'.join(r)+'\n');print('REPORT READY',flush=True)
if __name__=='__main__':globals()[sys.argv[1]]()
