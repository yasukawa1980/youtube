"""Record explicit acceptance, preserve draft snapshots, and publish repository evidence only."""
import argparse,datetime,hashlib,json,shutil,subprocess,zipfile
from pathlib import Path
from PIL import Image
from wom06_revision_v02 import ROOT,OLD
from wom06_produce import REPO,read,save,sha
from wom06_share_v02 import api,GH,TAG
GUIDE=REPO/'new-channel/wom06_確認版_v02_20261027'
def acceptance():
 # This stage follows the user's explicit reply in this chat, not inferred consent.
 state=read(ROOT/'records/sharing.json');assert state['status']=='verified' and state['draft']
 record={'requirement_met':False,'status':'本人承認済み・圧縮差を許容してv02確定','user_exact_reply':'圧縮差を許容してv02を確定','recorded_at_jst':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).isoformat(),'outside_frames':8662,'pixel_identical_frames':8550,'compression_difference_frames':112,'mean_luma_difference_8bit':0.05935912440062831,'scope':'Only the exact pixel-identity criterion receives this exception. Original intermediate frames, audio, SRT and scripts remain identical. No publication authorized.'}
 dst=ROOT/'records/pixel_requirement_acceptance.json'
 if dst.exists() and read(dst).get('user_exact_reply')==record['user_exact_reply']:record=read(dst)
 save(dst,record);approval=ROOT/'deliverables/EP006_v02_approval.json';save(approval,record)
 finalzip=ROOT/'deliverables/EP006_records_v02_confirmed.zip'
 with zipfile.ZipFile(finalzip,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in sorted((ROOT/'records').glob('*.json')):
   if p.name=='sharing.json':continue
   info=zipfile.ZipInfo(p.name,date_time=(2026,10,27,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
 checksum=ROOT/'deliverables/SHA256SUMS_v02_confirmed.txt';names=[x['name'] for x in state['assets'] if x['name'] not in [approval.name,finalzip.name,checksum.name]]+[approval.name,finalzip.name]
 checksum.write_text(''.join(f'{sha(ROOT/"deliverables"/n)}  {n}\n' for n in sorted(names)))
 r=api([f'repos/{GH}/releases/{state["release_id"]}']);assert r['draft']
 for p in [approval,finalzip,checksum]:
  old=next((a for a in r['assets'] if a['name']==p.name),None)
  if old:assert old['digest']=='sha256:'+sha(p)
  else:subprocess.run(['gh','release','upload',TAG,str(p),'--repo',GH],check=True)
 r=api([f'repos/{GH}/releases/{state["release_id"]}'])
 for p in [approval,finalzip,checksum]:
  a=next(x for x in r['assets'] if x['name']==p.name);proc=subprocess.Popen(['gh','api','-H','Accept: application/octet-stream',f'repos/{GH}/releases/assets/{a["id"]}'],stdout=subprocess.PIPE);h=hashlib.sha256();n=0
  while True:
   b=proc.stdout.read(1048576)
   if not b:break
   h.update(b);n+=len(b)
  assert proc.wait()==0 and h.hexdigest()==sha(p) and n==p.stat().st_size and a['digest']=='sha256:'+h.hexdigest()
  state['assets']=[x for x in state['assets'] if x['name']!=p.name]+[{'name':p.name,'asset_id':a['id'],'bytes':n,'sha256':h.hexdigest(),'rest_download_verified':True}]
 body='第6話修正版v02確定（本人承認済み）。6区間修正・サムネ3案。英日共通365.166667秒／10955フレーム。音声・SRT・M4A・WAVはv01同一、4本の連続デコード警告0。変更外8662フレーム中8550が画素完全一致、直前112フレームの微小な圧縮差は本人が許容。承認文：圧縮差を許容してv02を確定。最新検査記録はEP006_records_v02_confirmed.zip、承認はEP006_v02_approval.json、全体チェックサムはSHA256SUMS_v02_confirmed.txt。最初のEP006_records_v02.zipとSHA256SUMS_shared.txtは承認前の保存履歴として保全。非公開Draftを維持、YouTube投稿・予約・公開なし。v01 Release 424086149を保全。'
 r=api(['--method','PATCH',f'repos/{GH}/releases/{state["release_id"]}','--input','-'],{'body':body,'draft':True});assert r['draft'] and len(r['assets'])==len(state['assets'])
 state.update(acceptance=record['status'],latest_records_archive=finalzip.name,latest_checksum=checksum.name);save(ROOT/'records/sharing.json',state);print('ACCEPTANCE SHARED',len(state['assets']),flush=True)

def report():
 shared=read(ROOT/'records/sharing.json');assert shared['status']=='verified' and shared['draft'];accept=read(ROOT/'records/pixel_requirement_acceptance.json');assert accept.get('user_exact_reply')=='圧縮差を許容してv02を確定'
 qc=read(ROOT/'records/qc_v02.json');motion=read(ROOT/'records/motion_v02.json');thumb=read(ROOT/'records/thumbnail_qc.json');diff=read(ROOT/'records/boundary_difference.json')
 GUIDE.mkdir(exist_ok=True)
 for name in ['records','frames']:(GUIDE/name).mkdir(exist_ok=True)
 for p in (ROOT/'records').glob('*.json'):shutil.copy2(p,GUIDE/'records'/p.name)
 for p in (ROOT/'review').iterdir():
  if p.suffix not in ['.jpg','.png']:continue
  assert max(Image.open(p).size)<=1280 and p.stat().st_size<1_000_000
  shutil.copy2(p,GUIDE/'frames'/p.name)
 for asset in shared['assets']:
  p=ROOT/'deliverables'/asset['name']
  if p.suffix in ['.md','.srt','.txt','.csv','.html'] or p.name=='EP006_v02_approval.json':shutil.copy2(p,GUIDE/p.name)
 total=sum(a['bytes'] for a in shared['assets']);ratio=max(c['ratio'] for c in motion['checks'] if not c['static_source'])
 thumbrows='\n'.join(f"| {x['option']} | {x['bytes']:,} | {x['minimum_conservative_clearance_px']:.0f}px |" for x in thumb['outputs'])
 text=f'''# 第6話 スフィンクス — 修正版v02（2026-10-27）

依頼書の6区間とサムネ3案を制作し、[非公開Draft Release]({shared['release_url']})に保存しました。**112フレームの再圧縮差は本人が「圧縮差を許容してv02を確定」と承認済み。v02を確定しました。** YouTube投稿・予約、Release公開は行っていません。

## 完成物

英日通常版MP4と字幕入り確認版MP4の4本、同一SRT・M4A・48kHz/24bit WAV、サムネ3案、168px比較、作品クレジット、検査記録。共通尺 **365.166667秒、10,955フレーム、1920×1080、30fps CFR、H.264 High／yuv420p**。

- [取得・再生案内](wom06_確認版_v02_20261027/README.md)。Release ID **{shared['release_id']}**、**{len(shared['assets'])}添付・{total:,} bytes**をRelease ID指定RESTから再取得し、SHA-256・bytes・GitHub digestを照合済み。
- SRTはv01と同じものを再添付。本編M4A・WAVとKling原本はv01 Release **424086149**を参照。v01のファイルとReleaseは保全。
- 最終記録ZIPは **EP006_records_v02_confirmed.zip**。先行確認用Draft **424414685**は別途保全し、最終Draftには移動方向まで検査した記録だけを収録しています。

## 6区間の修正

| 区間 | 修正 |
|---|---|
| P01 18.533333–27.933333秒 | ZangakiのInv27_001に差し替え。左の白い台紙を写真内側で除外。指定の撮影者・1870・出典札。 |
| P02 27.933333–40.300000秒 | 右だけを緑の青銅met_329999へ。左・文字・配置を維持、出典を更新。 |
| P07 136.900000–152.100000秒 | “the deadly Sphinx which destroyed the Cadmeans,”の1行。紙面の傾きに沿った四角形で切り出し、前後の行の断片を除外。文字の描き直しはなし。 |
| P09 172.200000–187.200000秒 | met_247343を450フレームの1ショットに統合、顔→翼のゆっくりした移動。met_255796は図像が小さく判別しにくいため不使用。 |
| P10 187.200000–204.800000秒 | CR. The riddling Sphinxからour doors.まで3行と行番号130全体。 |
| P10 204.800000–211.666667秒 | モローを[.12,.10,.95,.33]で切り出し。背景も同じ範囲だけから作り、全206フレームがこの範囲内。男性の乳首を除外。 |

[ヘシオドスの拡大原寸](wom06_確認版_v02_20261027/frames/hesiod_159_exact_detail.png)／[Jebbの拡大原寸](wom06_確認版_v02_20261027/frames/jebb1904_15_exact_detail.png)／[モロー先頭・中央・末尾](wom06_確認版_v02_20261027/frames/continuous_en_change_06.jpg)。

資料は**18点を各1回**。Frith/met_286141とmet_256761は予備、Zangaki/Inv27_001は1回。P01〜P03は茶色の浮彫→正面に近い古写真→灰色石像と緑の青銅→横からの遠景→顔の近景で、同じ構図や色の資料が連続しないことを[一覧画像](wom06_確認版_v02_20261027/frames/P01_P03_composition_comparison.jpg)で確認。

英日投稿情報は作品クレジットだけ更新。その他の本文・タイトル・チャプター・制作メモはv01のまま保存しています。制作メモの旧確認待ち文言は今回の承認状態を表すものではなく、この制作結果を最新状態とします。画面末尾はもともと所蔵館名のみで個別作品名・作者名がなく、所蔵館は変わらないため画面を維持。

## 検査と承認された例外

24ショット（本編22＋OP＋エンドカード）をそれぞれ独立にデコードし、非圧縮yuv420pを1つのエンコーダーへ渡しました。**v01完成MP4は生成入力に使っていません**。v01は画素・音声比較の読取専用参照だけです。

- 4本とも先頭から連続デコードし、警告・エラー0。通常版の英日全フレームで1920×1080/yuv420p、全SPS profile_idc=100。全PTSが正確な30fps、音声17,528,000サンプル。
- 英日通常版の映像ストリームは同一。4本の音声ストリーム、SRT・M4A・WAVのSHA-256は対応するv01と同一。台本・字幕本文・総尺は不変。エンドカードは最後の10秒。
- 変更6区間の先頭・中央・末尾を、両言語ともシークなしの連続デコードから抽出（18枚×2言語）。
- 動きのある5区間のp95÷中央値は最大 **{ratio:.6f} ≤ 2.5**。P02は静止画なので元の全371フレームの画素一致を確認し、最終圧縮の微小差を動きとして扱わず、生の測定値を保存。
- 変更区間2,293フレーム。変更外**8,662フレームの元の中間映像はすべて同一SHA-256**。
- 最終MP4の変更外は **8,550／8,662フレームが画素完全一致**。**112フレームは不一致**。単一エンコードの先読み圧縮による差と考えられ、区間は下記の修正カット直前のみです。完全一致を達成したとは扱っていません。

| フレーム（0始まり、終端含まず） | 秒 |
|---|---|
| 517–556 | 17.233333–18.533333 |
| 4072–4107 | 135.733333–136.900000 |
| 5128–5166 | 170.933333–172.200000 |

112フレーム全体の平均輝度差 **{diff['mean_luma_mae_over_112_frames']:.9f}/255**。最も平均差が大きいフレームは555（輝度平均差0.110495/255）。全サンプルの最大絶対差は**{diff['maximum_absolute_sample_difference']}**。[差分16倍の比較画像](wom06_確認版_v02_20261027/frames/boundary_compression_difference.jpg)と全測定値を保存しました。

この未達を伝え、本人から **「圧縮差を許容してv02を確定」** と回答を得ました。[承認記録](wom06_確認版_v02_20261027/records/pixel_requirement_acceptance.json)。音声・台本・字幕や公開に関する例外承認ではありません。

## サムネ3案

[168×94px・5枚比較](サムネ確認用/wom06/wom06_サムネ168px比較_20261027.jpg)。参考は第2話の差し替え後と、第4話の現行・案3 v02（2026-10-27 00:17 JST差し替え済み）。制作中に第4話が更新されたため、最終比較画像を最新の現行サムネに更新しました。大きい字はGeorgiaコンデンス・高さ132px、ブランド位置(80,615)・22px。3案とも1280×720 JPG、全面イラスト＋左側グラデーション。

| 案 | bytes | 文字と主役の保守的な最小間隔 |
|---|---:|---:|
{thumbrows}

間隔は文字ラスターと影の外接矩形、顔・頭巾・翼の影を余裕をもって囲んだ矩形の最短距離。主役の範囲を原寸で確認して最終値を確定。右下の時間表示位置に顔・目はありません。

**おすすめは案1「NO RIDDLE」**。168pxでも短い文字と大スフィンクスの顔を読み取りやすく、題名 *Egypt's Sphinx Never Asked a Riddle* と合わせれば、エジプトのスフィンクスと謎かけの誤解を扱う話だと伝わります。画像単体では説明が少ないので、小さなEgypt's Sphinxも残しています。案3は意味が明確ですが字が詰まり、案2は対比が見える一方で視線が分散します。

組み込みOpenAI画像生成を3回使用（案1用、案2初回、案2の影を修正）。案1と案3は同じ画像。プロンプト全文・各生成日時・原寸SHA-256はthumbnail_generation.json、原寸3枚はMacへ保全。追加契約・購入、追加Kling生成はありません。サムネの採用・差し替えはまだ行っていません。

Mac保存先：`{ROOT}`。
'''
 (REPO/'new-channel/wom06_制作結果_v02_20261027.md').write_text(text)
 guide=f'''# 第6話スフィンクス v02 — 取得・再生案内

[非公開Draft Release]({shared['release_url']})／Release ID **{shared['release_id']}**。全{len(shared['assets'])}添付（{total:,} bytes）をRESTで再取得し、SHA-256一致確認済み。YouTube投稿・予約、Release公開なし。

最初は `EP006_Sphinx_ja_v02_subtitled_review_1080p30.mp4`（日本語）または `EP006_Sphinx_en_v02_subtitled_review_1080p30.mp4`（英語）。通常版は字幕焼き込みなし。

Macでは `{ROOT}/deliverables/preview.html` から両言語・サムネ3案を確認できます。他の環境ではReleaseのpreview.html、MP4、JPGを同じフォルダへ取得して開いてください。

## Claudeからの取得

認証済みRESTでRelease IDを指定してください。Draftは通常URLや未認証アクセスでは取得できない場合があります。

```sh
gh api repos/yasukawa1980/youtube/releases/{shared['release_id']}
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

全asset ID・SHA・bytesは[sharing.json](records/sharing.json)。サムネの日本語ファイル名はGitHubで自動変換されています。`github_name`が実際の添付名、`name`が保存時の元ファイル名です。RESTで取得するときは`name`の名前で保存するとpreview.htmlから表示できます。Mac側のファイル名と内容は維持しています。

最終検査記録は **EP006_records_v02_confirmed.zip**、最終チェックサムは **SHA256SUMS_v02_confirmed.txt**、承認は **EP006_v02_approval.json**。先行確認用Draft 424414685は別途保全。最終Draftの抽出画像はEP006_review_frames_v02.zip。

変更外8,662フレーム中112フレームの圧縮差は本人が許容し、v02確定済み。画素完全一致の未達と測定値は隠さず記録。[制作結果](../wom06_制作結果_v02_20261027.md)／[承認記録](records/pixel_requirement_acceptance.json)。音声・字幕はv01同一。SRTを再添付し、本編M4A・WAVとKling原本はv01 Release 424086149参照。
'''
 (GUIDE/'README.md').write_text(guide);print('REPORT',shared['release_id'],len(shared['assets']),total,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['acceptance','report']);a=p.parse_args();globals()[a.stage]()
