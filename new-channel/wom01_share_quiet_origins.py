"""Share the verified v05 as a private draft; never publish a release."""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
from wom01_multilingual_render import read,save,sha

ROOT=Path(os.environ['WOM_EPISODE_ROOT'])
REPO_ROOT=Path(__file__).resolve().parent.parent
GUIDE=REPO_ROOT/'new-channel/wom01_Quiet_Origins_v05_20261021'
REPO='yasukawa1980/youtube'
TAG='wom01-quiet-origins-v05-20261021'

def api(args,data=None):
    return json.loads(subprocess.check_output(['gh','api',*args],input=json.dumps(data).encode() if data is not None else None))

def main():
    qc=read(ROOT/'records/qc_v05.json')
    layout=read(ROOT/'records/libass_validation.json')
    brand=read(ROOT/'records/brand_layout_validation.json')
    assert len(qc['files'])==2 and len(layout['checks'])==24 and len(brand['shots'])==55
    assert read(ROOT/'records/visual_review.json')['passed']
    names=[f'EP001_Anubis_{lang}_v05_1080p30.{ext}' for lang in ['en','ja'] for ext in ['mp4','srt']]
    names += ['EP001_audio_en.m4a','EP001_audio_ja.m4a','EP001_thumbnail_en.jpg','VOICE_CREDITS.txt']
    files=[ROOT/'deliverables'/n for n in names]
    manifest=ROOT/'deliverables/SHA256SUMS_shared.txt'
    manifest.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(manifest)
    body='''# Quiet Origins / EP001 — Anubis v05

Claudeの申し送りと本人の実行指示に基づく画面のみの更新。
全55ショットとサムネをQUIET ORIGINSへ変更し、図解・クレジット14画面を上詰め。
Japanese narration — VOICEVOX:冥鳴ひまり を画面に追加。英語Kokoro / Heart (af_heart)の表記も維持。
音声ストリームと外部SRTは英日ともv04と同一。尺682.7秒、20,481フレーム、1080p30。
字幕は焼き込みなし。同名SRTを外部字幕対応プレーヤーで読み込んでください。
実際のMP4へlibassで字幕を重ね、5種類の場面＋箱型図解×英日×2文字サイズを確認。
追加支出・YouTube投稿・チャンネル開設・Release公開なし。過去版は維持。
資料：new-channel/wom01_Quiet_Origins_v05_20261021/README.md
'''
    state=ROOT/'records/release_v05.json'
    if state.exists():release=api([f'repos/{REPO}/releases/{read(state)["id"]}'])
    else:
        release=next((x for x in api([f'repos/{REPO}/releases']) if x['tag_name']==TAG),None)
        if release is None:
            release=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins — アヌビス v05（名称・字幕余白・声クレジット）','body':body,'draft':True})
    assert release['draft'];save(state,release)
    for p in files:
        existing=next((x for x in release['assets'] if x['name']==p.name),None)
        if existing:assert existing['digest']=='sha256:'+sha(p)
        else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',REPO],check=True)
        print('UPLOADED',p.name,flush=True)
    release=api([f'repos/{REPO}/releases/{release["id"]}']);assert release['draft'];save(state,release)
    downloads=Path('/private/tmp/wom01-v05-download');downloads.mkdir(exist_ok=True);results=[]
    for p in files:
        asset=next(x for x in release['assets'] if x['name']==p.name);dest=downloads/p.name
        with dest.open('wb') as out:
            subprocess.run(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPO}/releases/assets/{asset["id"]}'],stdout=out,check=True)
        assert sha(dest)==sha(p)
        results.append({'name':p.name,'asset_id':asset['id'],'bytes':p.stat().st_size,'sha256':sha(p),'rest_download_match':True})
        print('VERIFIED',p.name,flush=True)
    save(ROOT/'records/sharing_verification_v05.json',{'release_id':release['id'],'draft':True,'assets':results})
    for folder in ['records','deliverables','frames']:(GUIDE/folder).mkdir(parents=True,exist_ok=True)
    for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,GUIDE/'records'/p.name)
    for lang in ['en','ja']:
        n=f'EP001_Anubis_{lang}_v05_1080p30.srt';shutil.copy2(ROOT/'deliverables'/n,GUIDE/'deliverables'/n)
    for size in [14,26]:shutil.copy2(ROOT/f'review/libass_{size}.jpg',GUIDE/f'frames/libass_{size}.jpg')
    shutil.copy2(ROOT/'review/wom01_サムネ.jpg',GUIDE/'frames/thumbnail.jpg')
    shutil.copy2(ROOT/'review/wom01_サムネ.jpg',REPO_ROOT/'new-channel/サムネ確認用/wom01_サムネ.jpg')
    shutil.copy2(manifest,GUIDE/manifest.name)
    table='\n'.join(f"| {x['name']} | {x['asset_id']} | {x['bytes']:,} |" for x in results)
    guide=f'''# Quiet Origins：アヌビス第1話 v05

2026-10-21。本人の「申し送り通りに進めて」の指示に基づき、[名称決定](../wom01_チャンネル名決定_20261021.md)と[Claudeの依頼A](../wom01_Claude確認_v04_20261021.md)を反映。

## 変更と維持した内容

- 全55画面とサムネの旧仮称を **QUIET ORIGINS** に変更。
- 図解13画面・クレジット1画面を上詰め。元画像の文字の最下端は実測 y={brand['card_text_bottom_max']}px（1080px高）。41枚の写真・模写・再現画は名称以外の画素がv04と一致。
- 日本語の声を画面に **Japanese narration / VOICEVOX:冥鳴ひまり** と追加。英語のKokoro / Heart (af_heart) / synthetic speech表記を維持。
- 英語B、日本語C、BGMを含む**音声ストリームは両言語ともv04とハッシュ一致**。音声合成・音量調整を再実行していない。
- 英語150件・日本語136件の**SRTはv04とバイト一致**。字幕焼き込みなし。
- 共通尺 **682.700秒（11分22.7秒）**、1920×1080、30fps、**20,481フレーム**。55ショットの順序と時刻、CRF18、滑らかな拡大を維持。
- v01〜v04を上書きせず、新規フォルダに保存。

## 再生・Claudeの取得

Mac：`{ROOT}/deliverables/`

- 日本語：`EP001_Anubis_ja_v05_1080p30.mp4`
- 英語：`EP001_Anubis_en_v05_1080p30.mp4`
- 対応する同名SRTを同じフォルダに置き、外部字幕対応プレーヤーで読み込む。**動画に字幕を焼き込んだ版ではありません。**

[非公開Draft Release]({release['html_url']})／Release ID **{release['id']}**。全{len(results)}添付をRESTで再取得しSHA-256一致を確認。

```sh
gh api repos/{REPO}/releases/{release['id']} --jq '.assets[] | "\\(.id) \\(.name) \\(.digest)"'
gh api -H 'Accept: application/octet-stream' repos/{REPO}/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}

## 検品

[全編・音声字幕照合](records/qc_v05.json)／[55画面検品](records/brand_layout_validation.json)／[libass検品](records/libass_validation.json)／[目視記録](records/visual_review.json)／[再取得照合](records/sharing_verification_v05.json)。

- 両動画の全編デコード成功。全20,481フレームのPTSが1/30秒の刻みで連続。英日で映像ストリームが一致。
- 実MP4 + 実SRTを **libass** で描画。史料写真・模写・図解・再現画・クレジットの5種類と箱型図解×英日×FontSize14/26（BorderStyle3、MarginV12）で画面文字との重なりを確認。
- [標準サイズの確認画像](frames/libass_14.jpg)／[拡大サイズの確認画像](frames/libass_26.jpg)。プレーヤーの画面撮影ではなく、実際の字幕描画エンジンを使った確認画像。実プレーヤーの設定により位置は変わる。
- [更新サムネ](frames/thumbnail.jpg)。確認用1280×720・1MB以下。

**本人の全編試聴は引き続き未確認**。v04の「はかり」・「オシリス」・間・BGMの聴感に関する試聴項目は維持。今回の音声はv04と同一であり、新たな聴感確認を行ったとは扱わない。
指定SSD ESD-EPBは未接続で未同期。ESD-02への代替保存はしていない。

## 再現

`../wom01_quiet_origins.py` を `prepare → visuals → pictures → package → layout` の順に実行。WOM_EPISODE_ROOTは新規フォルダ、WOM_PREVIOUS_ROOTはv04、WOM_SOURCE_ROOTは旧制作素材、WOM_BRANDは `Quiet Origins`。Python環境に既存のnumpy・Pillow・soundfileと、検品用imageio-ffmpeg 0.6.0（FFmpeg7.1/libass）を使用。制作は従来のFFmpeg8.1.1。
目視確認を記録後 `../wom01_share_quiet_origins.py` でDraft共有と再取得照合。公開処理は含まない。

追加契約・購入・YouTube投稿・チャンネル開設・ハンドル取得・Release公開は未実施。管理フォルダとIDは変更していない。
'''
    (GUIDE/'README.md').write_text(guide)
    addition='## 最新確認版 v05：Quiet Originsの名称反映（2026-10-21）\n\n全55画面・サムネを正式名へ変更し、図解とクレジットを上詰め、日本語音声のクレジットを追加。音声・外部字幕はv04と同一、共通尺11分22.7秒。[v05の再生・Claude取得入口](wom01_Quiet_Origins_v05_20261021/README.md)。\n\n'
    for name in ['README.md','wom01_テーマ設計.md']:
        p=REPO_ROOT/'new-channel'/name;s=p.read_text()
        if '## 最新確認版 v05' not in s:
            index=s.index('## 最新確認版 v04');s=s[:index]+addition+s[index:]
        s=s.replace('## 最新確認版 v04','## 以前の確認版 v04')
        p.write_text(s)
    p=REPO_ROOT/'new-channel/volumes/wom01.yaml';s=p.read_text()
    s=s.replace('status: bilingual_v04_ready_awaiting_owner_full_listening','status: bilingual_v05_ready_awaiting_owner_full_listening',1)
    s=s.replace('local_media_root: /Users/ryo/Desktop/新チャンネル/EP001_Anubis/C採用_はかり修正_v04_20261021',f'local_media_root: {ROOT}',1)
    s=s.replace('local_media_status: v04_delivered_2026-10-21','local_media_status: v05_delivered_2026-10-21',1)
    s=s.replace('# v04 英語・日本語の共通実尺','# v05 英語・日本語の共通実尺',1)
    s=s.replace('最新はfull_revision_v04','最新はfull_revision_v05',1)
    if '\nfull_revision_v05:' not in s:
        s+=f'''\nfull_revision_v05:
  status: owner_full_review_pending
  brand: Quiet Origins
  guide: new-channel/wom01_Quiet_Origins_v05_20261021/README.md
  local_media_root: {ROOT}
  duration_seconds: 682.7
  frames: 20481
  fps: 30
  shots: 55
  audio_streams_identical_to_v04: true
  srt_identical_to_v04: true
  subtitles_burned_in: false
  libass_checks: 24
  release_id: {release['id']}
  release_draft: true
  ssd_synced: false
'''
    p.write_text(s)
    (ROOT/'再生の案内.txt').write_text('Quiet Origins / アヌビス v05\n\n日本語：deliverables/EP001_Anubis_ja_v05_1080p30.mp4\n英語：deliverables/EP001_Anubis_en_v05_1080p30.mp4\n動画と同名のSRTを外部字幕対応プレーヤーで読み込んでください。焼き込み字幕ではありません。\n音声と字幕はv04と同一。11分22.7秒。日本語音声：VOICEVOX:冥鳴ひまり\n')
    print('COMPLETE',release['id'],release['html_url'],flush=True)

if __name__=='__main__':main()
