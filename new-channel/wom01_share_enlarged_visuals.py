"""Share v07 regular and subtitled-review masters in one non-public Draft Release."""
import json,os,shutil,subprocess,hashlib
from pathlib import Path
from wom01_multilingual_render import read,save,sha
ROOT=Path(os.environ['WOM_EPISODE_ROOT']);REPO_ROOT=Path(__file__).resolve().parent.parent
REPO='yasukawa1980/youtube';TAG='wom01-enlarged-diagrams-v07-20261021'
GUIDE=REPO_ROOT/'new-channel/wom01_図解拡大_v07_20261021'
def api(args,data=None):
    return json.loads(subprocess.check_output(['gh','api',*args],input=json.dumps(data).encode() if data is not None else None))
def main():
    qc=read(ROOT/'records/qc_v07.json');layout=read(ROOT/'records/subtitle_layout_all.json');review=read(ROOT/'subtitled_review/records/qc.json')
    assert len(qc['files'])==2 and layout['all_passed'] and len(review['files'])==2
    assert read(ROOT/'records/visual_review.json')['passed']
    files=[ROOT/f'deliverables/EP001_Anubis_{lang}_v07_1080p30.{ext}' for lang in ['en','ja'] for ext in ['mp4','srt']]
    files += [ROOT/'deliverables'/n for n in ['EP001_audio_en.m4a','EP001_audio_ja.m4a','EP001_thumbnail_en.jpg','VOICE_CREDITS.txt']]
    files += [ROOT/f'subtitled_review/deliverables/EP001_Anubis_{lang}_v07_subtitled_review_1080p30.mp4' for lang in ['en','ja']]
    manifest=ROOT/'deliverables/SHA256SUMS_shared.txt';manifest.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(manifest)
    body='''# Quiet Origins / EP001 — Anubis v07

本人承認のClaude案を反映。神々の姿を個別に切り出し、指定の図解9ショットの写真と札を拡大。ほか46ショットはv06から再利用。
英日音声・SRT・サムネはv06と同一。682.700秒、20,481フレーム、1920x1080・30fps。
通常版MP4は字幕焼き込みなし。同名SRTを外部字幕として使用。
_subtitled_review_ の2本は字幕焼き込み確認用コピー（FontSize14）。動画を開くだけで字幕が表示される。
YouTubeへの動画投稿・追加購入・Releaseの公開なし。
資料：new-channel/wom01_図解拡大_v07_20261021/README.md
'''
    state=ROOT/'records/release_v07.json'
    if state.exists():release=api([f'repos/{REPO}/releases/{read(state)["id"]}'])
    else:
        release=next((r for r in api([f'repos/{REPO}/releases']) if r['tag_name']==TAG),None)
        if release is None:release=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins — アヌビス v07（神々の切り出し・図解拡大・字幕入り確認版）','body':body,'draft':True})
    assert release['draft'];save(state,release)
    for p in files:
        existing=next((a for a in release['assets'] if a['name']==p.name),None)
        if existing:assert existing['digest']=='sha256:'+sha(p)
        else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',REPO],check=True)
        print('UPLOADED',p.name,flush=True)
    release=api([f'repos/{REPO}/releases/{release["id"]}']);assert release['draft'];save(state,release)
    checks=[]
    for p in files:
        a=next(a for a in release['assets'] if a['name']==p.name)
        # Stream REST download into a digest, avoiding a second large disk copy.
        proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPO}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE)
        digest=hashlib.sha256();size=0
        while True:
            block=proc.stdout.read(1024*1024)
            if not block:break
            digest.update(block);size+=len(block)
        assert proc.wait()==0 and digest.hexdigest()==sha(p) and size==p.stat().st_size
        checks.append({'name':p.name,'asset_id':a['id'],'bytes':size,'sha256':digest.hexdigest(),'rest_download_verified':True})
        print('VERIFIED',p.name,flush=True)
    save(ROOT/'records/sharing_verification_v07.json',{'release_id':release['id'],'release_url':release['html_url'],'draft':True,'assets':checks})
    for d in ['records','frames','deliverables']:(GUIDE/d).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,GUIDE/'records'/p.name)
    for p in (ROOT/'review').glob('midpoints_*.jpg'):shutil.copy2(p,GUIDE/'frames'/p.name)
    for p in (ROOT/'review').glob('v07_*.jpg'):shutil.copy2(p,GUIDE/'frames'/p.name)
    for p in (ROOT/'review/layout').glob('*.jpg'):shutil.copy2(p,GUIDE/'frames'/p.name)
    shutil.copy2(ROOT/'subtitled_review/review/subtitled_review_contact.jpg',GUIDE/'frames/subtitled_review_contact.jpg')
    for n in ['qc.json','subtitle_presence_checks.json']:shutil.copy2(ROOT/'subtitled_review/records'/n,GUIDE/'records'/('review_'+n))
    for lang in ['en','ja']:shutil.copy2(ROOT/f'deliverables/EP001_Anubis_{lang}_v07_1080p30.srt',GUIDE/f'deliverables/EP001_Anubis_{lang}_v07_1080p30.srt')
    shutil.copy2(manifest,GUIDE/manifest.name)
    table='\n'.join(f"| {a['name']} | {a['asset_id']} | {a['bytes']:,} |" for a in checks)
    (GUIDE/'README.md').write_text(f'''# Quiet Origins：アヌビス第1話 v07（神々の切り出し・図解拡大）

2026-10-21。本人の実行依頼により、[Claudeの本人承認済み案](../wom01_Claude確認_v06_20261021.md)を反映。

## 完成動画

Mac保存先：`{ROOT}`。

- 字幕入り日本語確認用：`subtitled_review/deliverables/EP001_Anubis_ja_v07_subtitled_review_1080p30.mp4`
- 字幕入り英語確認用：`subtitled_review/deliverables/EP001_Anubis_en_v07_subtitled_review_1080p30.mp4`
- 通常版（字幕焼き込みなし）：`deliverables/EP001_Anubis_ja_v07_1080p30.mp4` / `EP001_Anubis_en_v07_1080p30.mp4`
- 英日SRT・音声M4A・サムネ・声のクレジット：`deliverables/`。

通常版の英日MP4は同一映像と言語別音声。字幕入り確認版はFontSize14の表示を焼き込んだ別コピー。

## 変更と維持

- N17・N18：アヌビス（548344の天秤の横）、トト（552247のトキの頭で筆記具を持つ神）、オシリス（548344の右端の玉座）を個別に切り出した。原寸の画像とMetの公式解説を照合。元画像・原寸サイズ・切り出し座標・表示位置・参照URLを[画像台帳](records/visual_manifest.json)に記録。名前と配置はv06を維持。
- N03・N07・N08・N09・N10・N17・N18・N22・N27の計9ショットを修正。一般の写真枠の横幅は1.2倍、縦は字幕領域に合わせ最大440px。札は23→28px。年表と神々の図は年代・名前の場所を確保するため縦の拡大を抑えた。残り46ショットは画像・エンコード済み映像をv06から再利用しハッシュ一致を確認。
- 年表・神名・クレジットを含め、文字と写真・図の箱の下端はy≤700px。全字幕を2サイズ（14／26）で実描画し、{layout['total']}条件で重なりなし。保守的な最小余白は{layout['min_clearance']}px。
- 英日音声ストリーム・SRT・サムネはv06と同一。尺682.700秒、20,481フレーム、55ショットの順序・開始・終了時刻を維持。英日映像ストリームも同一。
- 通常版と字幕入り確認版の計4本で全編デコード・PTSを検査。確認版では英150・日136字幕と空白区間を検査。
- v06は保全。YouTube動画投稿・追加支出なし。指定SSDへの同期は未実施。全編の聴感は未確認（音声は変更していない）。

## Claudeからの取得

[非公開Draft Release]({release['html_url']})／Release ID **{release['id']}**。全{len(checks)}添付をRelease IDからRESTで再取得してSHA-256一致を確認。

```sh
gh api repos/{REPO}/releases/{release['id']} --jq '.assets[] | "\\(.id) \\(.name)"'
gh api -H 'Accept: application/octet-stream' repos/{REPO}/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}

[検品](records/qc_v07.json)／[全字幕の重なり検査](records/subtitle_layout_all.json)／[画面の確認記録](records/visual_review.json)／[字幕入り版検品](records/review_qc.json)／[共有照合](records/sharing_verification_v07.json)。

全55ショットの中央フレームは `frames/midpoints_01.jpg`〜`midpoints_05.jpg`。全字幕表示例は `frames/font14_*.jpg` / `font26_*.jpg`。語りの自然さ・はかり4か所・オシリスの抑揚など以前からの本人試聴項目は継続。
''')
    print('SHARED',release['id'],len(checks),flush=True)
if __name__=='__main__':main()
