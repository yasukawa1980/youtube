"""EP012 gate for review archive and final handoff; never publishes the release."""
from wom12_produce import *
import zipfile,sys,shutil
from wom12_scenes import CAT
D=ROOT/'deliverables';R=ROOT/'records';P=REPO/'new-channel';share=P/'wom12_確認版_v01_20261105'
def pack():
 for n in ['qc_v01','continuous_qc','final_video_motion','episode_qc','subtitle_layout_validation']:assert read(R/f'{n}.json')['passed'],n
 enc=read(ROOT/'deliverables_4k/encoding.json')['files'][0];assert enc['frames']==12555 and enc['audio_same'] and enc['decode_warnings']==0;save(R/'4k_encoding_v01.json',enc)
 groups={'EP012_audio_and_subtitles_v01.zip':([p for p in D.iterdir() if p.suffix in ['.wav','.m4a','.srt','.txt']],D),'EP012_thumbnails_and_metadata_v01.zip':([p for p in D.iterdir() if p.suffix in ['.jpg','.md']],D),'EP012_QA_records_v01.zip':([*[p for p in R.glob('*.json') if p.name not in ['release_archives.json','sharing.json','source_assets.json']],*(ROOT/'review').glob('*.jpg')],ROOT)};records=[]
 for name,(fs,base) in groups.items():
  out=D/name
  with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
   for f in sorted(fs):z.write(f,f.relative_to(base))
  with zipfile.ZipFile(out) as z:assert not z.testzip()
  records.append(dict(name=name,bytes=out.stat().st_size,sha256=sha(out)))
 save(R/'release_archives.json',records)
def publish_report():
 s=read(R/'sharing.json');assert s['status']=='verified' and s['draft'] and len(s['assets'])==8;t=read(R/'master_timeline.json');subs=read(R/'subtitle_validation.json');l=read(R/'subtitle_layout_validation.json');motion=read(R/'final_video_motion.json');cq=read(R/'episode_qc.json');streams=read(R/'qc_v01.json')['files'];folder=share/'records';folder.mkdir(exist_ok=True,parents=True)
 for name in ['yale_n08','used_sources','master_timeline','encoding_method','render_shots','subtitle_validation','reading_replacements','pronunciation_locations','rail_switches','art_scales','subtitle_layout_validation','episode_qc','final_video_motion','qc_v01','continuous_qc','4k_encoding_v01','release_archives','sharing']:
  shutil.copy2(R/f'{name}.json',folder/f'{name}.json')
 for f in D.glob('EP012*.md'):shutil.copy2(f,share/f.name)
 for f in (ROOT/'review').glob('*'):
  if f.name.startswith(('continuous_en_sheet','continuous_ja_sheet','opening_')):shutil.copy2(f,share/f.name)
 title='Quiet Origins EP012「サンタクロースの赤い服」確認版v01';base=f'https://api.github.com/repos/yasukawa1980/youtube/releases/{s["release_id"]}';links=['# '+title,'',f'非公開Draft Release **{s["release_id"]}**（[権限のあるアカウントで開く]({s["release_url"]})）。公開・投稿予約は未実施。','','| ファイル | バイト | REST再取得 SHA-256 |','|---|---:|---|'];
 for a in s['assets']:links.append(f"| {a['name']} | {a['bytes']:,} | `{a['sha256']}` |")
 links+=['','`gh api repos/yasukawa1980/youtube/releases/'+str(s['release_id'])+'` でasset IDを確認。`gh api -H "Accept: application/octet-stream" repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT` で取得。','',f'SSD: `{ROOT}`','', '[英語投稿情報](EP012_upload_info_en.md)・[日本語投稿情報](EP012_upload_info_ja.md)・[素材クレジット](EP012_source_credits.md)。音声ZIPに発音試聴抜粋と対応時刻。','', 'Claude・本人の確認：0秒から英日の連続再生、固有名詞の読み、字幕と年代帯、比較カードとテンポ、サムネA/Bの選択。ショート制作・予約は別工程。'];(share/'README.md').write_text('\n'.join(links)+'\n')
 f=P/'wom12_制作結果_v01_20261105.md';old=f.read_text().split('**制作中。**')[0].split('## 制作・共有結果')[0];body=['## 制作・共有結果','',f'確認版v01を非公開Draft Release **{s["release_id"]}** へ共有。8ファイルすべてをRelease ID→asset ID指定のRESTで再取得し、バイト数とSHA-256の一致・匿名アクセス404を確認。[取得案内](wom12_確認版_v01_20261105/README.md)。','', '実測 **418.500秒（6:58.5）・12,555フレーム・23ショット**。共通OPは63.5–67.5秒、共通エンドカードは408.5–418.5秒。目安7分との差は−1.5秒。4Kは1080pからLanczos通常拡大で、画像復元ではない。英語音声は1080pと一致。','', '各ショットと共通OP・EDをそれぞれ個別デコードし、rawvideoで1個のエンコーダーへ入力。英日1080p通常版の映像ストリーム一致、通常2本・字幕入り2本・英語4Kの全編連続デコード警告0。両言語の23ショットすべて先頭・中央・末尾画像を取得。','',f"最終音量：英語 {streams[0]['loudness']['input_i']} LUFS / {streams[0]['loudness']['input_tp']} dBTP、日本語 {streams[2]['loudness']['input_i']} LUFS / {streams[2]['loudness']['input_tp']} dBTP。−60dB基準1秒以上の無音0件。曲はQO_THEME_A02、エンドカード等の共通音は保持。",'',f"字幕：英語88件、日本語101件、台本本文一致（レイアウト空白除外）、各2行以内、最短1.4秒。字幕上端最小{l['minimum_top']}px、年代帯上端915pxとの間隔最小{l['min_gap']}px。[全字幕の測定表](wom12_確認版_v01_20261105/records/subtitle_layout_validation.json)。",'',f"動きのある作品ショットの全隣接フレーム差 p95/中央値は最大 {max(x['ratio'] for x in motion['checks']):.3f}（上限2.5）。[全ショット測定](wom12_確認版_v01_20261105/records/final_video_motion.json)。",'', '[年の切替時刻と対応語](wom12_確認版_v01_20261105/records/rail_switches.json)は正台本の英語音声を基準にした共通映像。文中は字幕ページ内の文字位置による補間で、音素単位の強制アラインメントではない。日本語の語順・発話時刻には差がある。','', '[実測：カード・作品使用回数・拡大率](wom12_確認版_v01_20261105/records/episode_qc.json)。暗い茶色の帯・現在年の字高60px。N08は同じ冊子の異なる2頁を使用。N12-BはD_1823の背景のみ、N12-AはP12からP13で1ショットを保持。並べ直し内の再登場を別計上。N04の権利表記は依頼書のLoC原文どおり。','', '### カードの実測','','| カード | コントラスト | 内側の最小余白(px) | 主要文字の字高(px) |','|---|---:|---:|---:|'];
 for r in cq['contrast_and_card_padding']:body.append(f"| {r['key']} | {r['encoded_contrast']:.2f}:1 | {r['panel_padding_min_px']} | {r['body_heading_height_min_px'] or '比較図の年は31'} |")
 body+=['','比較図：4枚並べは画像枠高340px、2段並べは202px、列間の箱の隙間20px前後。実画像の高さは原画の縦横比により異なる。[個別寸法](wom12_確認版_v01_20261105/records/episode_qc.json)。P09のVedderカードは「But red kept coming back」から次の語りの頭まで約2.2秒（目安4秒より短い）。','','### 発音と本人確認','','初回の無置換音声を保存後、英語Santeclaus、日本語の「刷られ」「北軍」「星の柄」を発音入力だけ変更。[変更箇所と時刻](wom12_確認版_v01_20261105/records/reading_replacements.json)・[全試聴語の時刻](wom12_確認版_v01_20261105/records/pronunciation_locations.json)。本人による全編試聴・サムネ選択は未実施。YouTubeへの投稿・予約、Release公開、追加課金なし。'];f.write_text(old+'\n'.join(body)+'\n')
if __name__=='__main__':{'pack':pack,'report':publish_report}[sys.argv[1]]()
