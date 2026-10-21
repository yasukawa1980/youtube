# Quiet Origins：アヌビス第1話 v05

2026-10-21。本人の「申し送り通りに進めて」の指示に基づき、[名称決定](../wom01_チャンネル名決定_20261021.md)と[Claudeの依頼A](../wom01_Claude確認_v04_20261021.md)を反映。

## 変更と維持した内容

- 全55画面とサムネの旧仮称を **QUIET ORIGINS** に変更。
- 図解13画面・クレジット1画面を上詰め。元画像の文字の最下端は実測 y=757px（1080px高）。41枚の写真・模写・再現画は名称以外の画素がv04と一致。
- 日本語の声を画面に **Japanese narration / VOICEVOX:冥鳴ひまり** と追加。英語のKokoro / Heart (af_heart) / synthetic speech表記を維持。
- 英語B、日本語C、BGMを含む**音声ストリームは両言語ともv04とハッシュ一致**。音声合成・音量調整を再実行していない。
- 英語150件・日本語136件の**SRTはv04とバイト一致**。字幕焼き込みなし。
- 共通尺 **682.700秒（11分22.7秒）**、1920×1080、30fps、**20,481フレーム**。55ショットの順序と時刻、CRF18、滑らかな拡大を維持。
- v01〜v04を上書きせず、新規フォルダに保存。

## 再生・Claudeの取得

Mac：`/Users/ryo/Desktop/新チャンネル/EP001_Anubis/Quiet_Origins_v05_20261021/deliverables/`

- 日本語：`EP001_Anubis_ja_v05_1080p30.mp4`
- 英語：`EP001_Anubis_en_v05_1080p30.mp4`
- 対応する同名SRTを同じフォルダに置き、外部字幕対応プレーヤーで読み込む。**動画に字幕を焼き込んだ版ではありません。**

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-41a8b2869bcd781d81b7)／Release ID **419118245**。全9添付をRESTで再取得しSHA-256一致を確認。

```sh
gh api repos/yasukawa1980/youtube/releases/419118245 --jq '.assets[] | "\(.id) \(.name) \(.digest)"'
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

| 添付 | Asset ID | bytes |
|---|---:|---:|
| EP001_Anubis_en_v05_1080p30.mp4 | 661243254 | 165,634,448 |
| EP001_Anubis_en_v05_1080p30.srt | 661243780 | 13,252 |
| EP001_Anubis_ja_v05_1080p30.mp4 | 661243844 | 165,104,416 |
| EP001_Anubis_ja_v05_1080p30.srt | 661244315 | 15,346 |
| EP001_audio_en.m4a | 661244354 | 16,143,257 |
| EP001_audio_ja.m4a | 661244427 | 15,613,221 |
| EP001_thumbnail_en.jpg | 661244525 | 407,649 |
| VOICE_CREDITS.txt | 661244564 | 129 |
| SHA256SUMS_shared.txt | 661244598 | 735 |

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
