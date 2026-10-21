"""Share burned-subtitle review copies in a new private draft, preserving v05."""
import json,os,shutil,subprocess
from pathlib import Path
from wom01_multilingual_render import read,save,sha
from wom01_subtitled_review import stem

REPO='yasukawa1980/youtube'
TAG='wom01-v05-subtitled-review-20261021'

def api(args,data=None):
    return json.loads(subprocess.check_output(['gh','api',*args],input=json.dumps(data).encode() if data is not None else None))

def main():
    root=Path(os.environ['WOM_REVIEW_ROOT']);w=Path(__file__).resolve().parent.parent
    dest=w/'new-channel/wom01_字幕入り確認用_v05_20261021'
    qc=read(root/'records/qc.json');assert len(qc['files'])==2
    assert read(root/'records/visual_review.json')['passed']
    files=[root/f'deliverables/{stem(lang)}.mp4' for lang in ['en','ja']]+[root/'deliverables/VOICE_CREDITS.txt']
    manifest=root/'deliverables/SHA256SUMS_shared.txt'
    manifest.write_text(''.join(f'{sha(p)}  {p.name}\n' for p in files));files.append(manifest)
    body='''# Quiet Origins / EP001 — v05 字幕入り確認用

本人の依頼により、確認用として英語・日本語それぞれの字幕を焼き込んだ全編MP4を追加。
動画を開くだけで字幕が表示されます。SRTの読み込みは不要。字幕はオフにできません。
通常のv05（字幕なし映像＋外部SRT）は変更せず、別フォルダ・別Draftとして保全。
Claudeのv05確認は不具合なし・再生成不要。拡大3行字幕の重なりを避け、確認済みの標準設定FontSize14 / BorderStyle3 / MarginV12で固定しました。
英語150件・日本語136件。音声・BGMのストリームはv05と同一。682.700秒・1080p30・20,481フレーム。
日本語音声：VOICEVOX:冥鳴ひまり。英語：Kokoro / Heart (af_heart)。
資料：new-channel/wom01_字幕入り確認用_v05_20261021/README.md
確認用の非公開Draftです。公開・投稿・チャンネル開設・追加購入なし。
'''
    state=root/'records/release.json'
    if state.exists():release=api([f'repos/{REPO}/releases/{read(state)["id"]}'])
    else:
        release=next((x for x in api([f'repos/{REPO}/releases']) if x['tag_name']==TAG),None)
        if release is None:
            release=api(['--method','POST',f'repos/{REPO}/releases','--input','-'],{'tag_name':TAG,'target_commitish':'bgm/production','name':'Quiet Origins アヌビス v05 — 英日字幕入り確認用','body':body,'draft':True})
    assert release['draft'];save(state,release)
    for p in files:
        item=next((x for x in release['assets'] if x['name']==p.name),None)
        if item:assert item['digest']=='sha256:'+sha(p)
        else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',REPO],check=True)
        print('UPLOADED',p.name,flush=True)
    release=api([f'repos/{REPO}/releases/{release["id"]}']);assert release['draft'];save(state,release)
    downloads=Path('/private/tmp/wom01-subtitled-download');downloads.mkdir(exist_ok=True);items=[]
    for p in files:
        asset=next(x for x in release['assets'] if x['name']==p.name);target=downloads/p.name
        with target.open('wb') as f:subprocess.run(['gh','api','-H','Accept: application/octet-stream',f'repos/{REPO}/releases/assets/{asset["id"]}'],stdout=f,check=True)
        assert sha(target)==sha(p)
        items.append({'name':p.name,'asset_id':asset['id'],'bytes':p.stat().st_size,'sha256':sha(p),'rest_download_match':True})
        print('VERIFIED',p.name,flush=True)
    save(root/'records/sharing_verification.json',{'draft':True,'release_id':release['id'],'assets':items})
    for folder in ['records','frames']:(dest/folder).mkdir(parents=True,exist_ok=True)
    for p in (root/'records').glob('*.json'):shutil.copy2(p,dest/'records'/p.name)
    shutil.copy2(root/'review/subtitled_review_contact.jpg',dest/'frames/subtitled_review_contact.jpg')
    shutil.copy2(manifest,dest/manifest.name)
    table='\n'.join(f"| {x['name']} | {x['asset_id']} | {x['bytes']:,} |" for x in items)
    doc=f'''# Quiet Origins アヌビス v05：字幕入り確認用

2026-10-21、本人の「Claudeの申し送り確認と、確認用の字幕入り動画作成」に対応。

## Claudeの申し送りと対応

[Claudeのv05確認](../wom01_Claude確認_v05_20261021.md)（`e62371d`）は、名称・音声クレジット・尺・フレーム・音声・SRTに問題なし、**v05の再生成は不要**という結論。
標準サイズの字幕は図解・クレジットに重なる80件すべてで重なりなし。極端な拡大で3行に折り返した場合だけ4件が重なるため、第2話以降の参考として記録されています。

通常のv05は変更せず、**標準サイズの字幕を焼き込んだ確認用コピー2本**を作成しました。英語音声には英語字幕、日本語音声には日本語字幕です。

## 開くだけで字幕が表示される動画

Mac保存先：`{root}/deliverables/`

- 日本語：`{stem('ja')}.mp4`
- 英語：`{stem('en')}.mp4`
- **SRTの読み込み不要。字幕は映像に固定されているためオフにできません。** 外部字幕を重ねる必要はありません。
- 字幕なしの通常版は [v05の案内](../wom01_Quiet_Origins_v05_20261021/README.md)にあります。

英語150件・日本語136件、本文・時刻は既存v05のSRTをそのまま使用。libassの設定は `original_size=1920x1080 / FontSize=14 / BorderStyle=3 / MarginV=12`。白字・黒背景の標準サイズです。
音声・BGMはコピーし再エンコードなし。映像のみ字幕を描画してH.264 CRF18で再エンコード。

## 検品

- 両言語とも **682.700秒、1920×1080、30fps、20,481フレーム**。全編デコード成功、全フレームのPTSが1/30秒刻みで連続。
- 音声ストリームのSHA-256はv05と一致。元のMP4・SRTのSHA-256も制作前後で一致。
- 英語150件・日本語136件の全字幕について、表示中のフレームで焼き込み文字の画素が増えていることを元動画との比較で確認。0.3秒以上の字幕の隙間では字幕が残っていないことも確認。
- [実際の字幕入り動画の確認画像](frames/subtitled_review_contact.jpg)。冒頭・箱型図解・天秤・クレジット等を画像で確認。Claudeが拡大字幕の重なりを指摘した4件も標準サイズで確認。
- [全編検品](records/qc.json)／[全字幕の表示検査](records/subtitle_presence_checks.json)／[画像確認](records/visual_review.json)。画素検査はOCRや人の通し視聴の代替ではありません。

本人の全編試聴は引き続き未確認。「はかり」4か所・07:18の「オシリス」・間・BGMの聴感は、元のv05と同じ確認項目です。

## Claudeの取得

[非公開Draft Release]({release['html_url']})／Release ID **{release['id']}**。全{len(items)}添付をRESTで再取得しSHA-256一致。

```sh
gh api repos/{REPO}/releases/{release['id']} --jq '.assets[] | "\\(.id) \\(.name) \\(.digest)"'
gh api -H 'Accept: application/octet-stream' repos/{REPO}/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
{table}

## 再現・条件

`../wom01_subtitled_review.py render` → `verify`。`WOM_EPISODE_ROOT` は通常版v05、`WOM_REVIEW_ROOT` は新規の確認用フォルダを指定。既存の一時Python環境とimageio-ffmpeg 0.6.0（FFmpeg7.1/libass）を使用。画像確認記録の作成後、`../wom01_share_subtitled_review.py` でDraft共有・再取得照合。
日本語音声：VOICEVOX:冥鳴ひまり／英語：Kokoro / Heart (af_heart)。追加契約・購入・YouTube投稿・チャンネル開設・Release公開なし。元のv05とそのDraft Releaseは変更なし。指定SSD ESD-EPBは未接続のため未同期。
'''
    (dest/'README.md').write_text(doc)
    addition='## 字幕入りの確認用動画（2026-10-21）\n\n本人の依頼で、v05に標準サイズの字幕を焼き込んだ英語・日本語の全編コピーを追加。動画を開くだけで字幕が表示されます。音声・BGM・尺は通常版v05と同じで、通常版は保全。[字幕入り確認用の再生・取得](wom01_字幕入り確認用_v05_20261021/README.md)。\n\n'
    for name in ['README.md','wom01_テーマ設計.md']:
        p=w/'new-channel'/name;s=p.read_text()
        if '## 字幕入りの確認用動画' not in s:
            pos=s.index('## 最新確認版 v05');s=s[:pos]+addition+s[pos:]
        p.write_text(s)
    p=w/'new-channel/volumes/wom01.yaml';s=p.read_text()
    if '\nsubtitled_review_v05:' not in s:
        s+=f'''\nsubtitled_review_v05:
  purpose: owner_review_copy
  guide: new-channel/wom01_字幕入り確認用_v05_20261021/README.md
  local_media_root: {root}
  subtitles_burned_in: true
  original_v05_unchanged: true
  audio_streams_identical_to_v05: true
  duration_seconds: 682.7
  frames: 20481
  subtitle_cues_en: 150
  subtitle_cues_ja: 136
  release_id: {release['id']}
  release_draft: true
  ssd_synced: false
'''
    p.write_text(s)
    (root/'再生の案内.txt').write_text(f'Quiet Origins アヌビス v05 字幕入り確認用\n\n日本語：deliverables/{stem("ja")}.mp4\n英語：deliverables/{stem("en")}.mp4\n\n動画を開くだけで字幕が表示されます。SRTの読み込み不要。字幕はオフにできません。\n音声・BGM・尺は通常版v05と同じです。日本語音声：VOICEVOX:冥鳴ひまり\n')
    print('COMPLETE',release['id'],release['html_url'],flush=True)

if __name__=='__main__':main()
