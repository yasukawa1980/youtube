# IRO20 再開メモ（10月26日継続）

**制作中・未納品**。本人承認はSuno300／Kling512、購入なし。再確認不要。Claude待ちは不要。投稿・予約・公開は本人の通し視聴後に別途。

## 現在

- 認証・Macロックは本人対応で解消。
- Suno：ワークスペース `8df2a704-452b-44ff-84a2-27028d4d33aa`。A〜Fの01〜03＝36曲にF04〜06を6曲追加し、42候補を受付。生成21回、想定210。最初の12曲後は9700／DL38で60消費を確認。最終残高の確認はまだ。通常WAVは1曲のアンロックで1枠消費。通常UIの以前のMultitrack経路は現行v6メニューに見当たらず、50枠から取得中。APIは使っていない。
- 試作36曲の保存・自動検品済み。全曲flagsなし、人声最大0.075422。F01〜03はASTで弦分類が続くため採用保留。F04はスタイルだけでなく除外欄にcello/violin等を追加。F04aはKeyboard/Organが上位へ出た。F04bは取得依頼済み、F05/06は生成済みで未取得。これらを検品し、6種類×5曲＋A1曲＝31曲で約2時間を組めるか確認する。音色は直接聴取未実施で、分類だけから同定合格とは言わない。
- 直接音声入力は非対応と確認。最終の技術検品と本人の通し視聴を明確に区別する。本人へ2分試聴版を提示済み。
- Kling：B1/B2/A/B/C/D全6本をMacへ保存。1404→1020、384消費確定。残り128は未使用。URL直接保存は本人が明示許可済み。`iro20_Kling表示URL.json`の公開mp4だけをcurlで取得可。ブラウザ内部APIやトークン取得は不可。
- B1の目元修正v01を確認。頭の時間を変えず、約3秒の閉眼を短縮。元素材は保全。
- 本編用8部品をMac `_work/映像_v01/parts` に書き出し済み。背景固定、人物と犬だけのマスク、端10コマを基準画へ。Cは静止待ち3秒を除き、動作開始直前から8秒単位へ再構成。6部品の全コマ実測済み、B2C/B1Dの残り2部品は追加確認が必要。
- 扉と間543コマ、最後15秒カードを作成済み。構成・連結リスト作成済み。本編・ショートは未完成。
- 横サムネv02は1280×720 311912 bytes。縦共通サムネ1080×1920 666874 bytes（Git確認用720×1280 341528 bytes）。

## 作業パス・コマンド

Mac：`/Users/ryo/Desktop/BGM/IRO/Reading/20_しおりを挟むにはまだ早い/`。
Pythonは **`bgm/.venv-audio-qc/bin/python`**。cv2/torch/transformers/yaml等あり。`bgm/.models/ast-audioset`が存在。sandbox内はMPS=False、通常権限へエスカレーションするとMPS=True。GPU検査はrequire_escalatedで起動。CPU検査を停止する場合は自分のプロセスだけを照合し、途中レポートを保全する。

- `PYTHONPATH=bgm bgm/.venv-audio-qc/bin/python -m bgmkit.music_qc --model bgm/.models/ast-audioset --report iro/iro20_音源検品.json <音源群>`：同じSHAの検査済み音源は再利用。
- `iro/iro20_映像制作.py parts|card|plan|video|audio|mux`。videoまで完了。audioはMac `_work/music_bed.wav` が必要。31曲の選曲後は既存bgmkit.audio.buildを絶対yamlパスで使う。新しい音楽組立用スクリプトはこれから。
- `iro/iro20_試聴を作る.py` は完了。ffmpegにdrawtextがないためPillowで動画字幕を生成。確認版 `投稿用/iro20_試作6種_2分.mp4`。
- `bgm/bgmkit/clip_qc.py` と `eye_patch.py` を今回追加。目元設定は `iro/iro20_B1目元設定.json`。

## 次

1. F04b/05/06をUIで取得してMacへコピー・検品。出所の対応は `iro20_Suno曲一覧.json`。検索欄で曲名を絞ると2曲だけDOMに出て取得が確実。全36曲一覧は仮想化され、一部の行はDOMに実体がない。firstをa、secondをbとして同名WAVと(1).wavを対応させる。aの到着前に同タイトルのbを送らない。
2. 31曲を決めてyamlへkinds/picked/order_tracksを設定。同じ曲の二巡なし。同一種隣接・1曲おき禁止。ABCDEF×5＋Aなら系統も3枠離せる。自動検品と音色の聴感未確認を記録。
3. 音楽を4秒クロスフェードして床を作る。必要尺7200以上か確認。本編音声は既存19の方式（aac_at、192k oversampling、limiter .56を2段）を実装済み。最終全体のLUFS/TP測定後に調整。
4. mux、4ショート、全編デコード、連結の変化、縦の全身・余白、字幕を実見。扉全編・カード位置も確認。
5. 日英投稿文を実成果へ合わせる。Claude用1枚見本はまだサムネ案だけなので、完成後に指定の開始画・サムネ・168px・ショート4秒・顔8秒3fpsへ更新する。
6. 完成品・資料をMacへ納品。ESD-EPBは未接続・未同期。ESD-02を勝手に代用しない。YouTubeには何も送らない。

## Git保全

元チェックアウトは古い分岐履歴と大量の未コミット作業がある。reset/force-push禁止。リモート基点の共有用worktreeは `/private/tmp/iro20-share-20261025`。今回の明示ファイルだけコピーしてcommit→push HEAD:bgm/production。直前共有82bf24b。動画・音源・高解像度素材・_workはGit対象外。
