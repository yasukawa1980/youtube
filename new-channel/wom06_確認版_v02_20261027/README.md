# 第6話スフィンクス v02 — 取得・再生案内

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-bd546a38eb9dc4bd003c)／Release ID **424433823**。全19添付（463,235,483 bytes）をRESTで再取得し、SHA-256一致確認済み。YouTube投稿・予約、Release公開なし。

最初は `EP006_Sphinx_ja_v02_subtitled_review_1080p30.mp4`（日本語）または `EP006_Sphinx_en_v02_subtitled_review_1080p30.mp4`（英語）。通常版は字幕焼き込みなし。

Macでは `/Users/ryo/Desktop/新チャンネル/EP006_Sphinx/確認版_v02_20261027/deliverables/preview.html` から両言語・サムネ3案を確認できます。他の環境ではReleaseのpreview.html、MP4、JPGを同じフォルダへ取得して開いてください。

## Claudeからの取得

認証済みRESTでRelease IDを指定してください。Draftは通常URLや未認証アクセスでは取得できない場合があります。

```sh
gh api repos/yasukawa1980/youtube/releases/424433823
gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > FILE_NAME
```

全asset ID・SHA・bytesは[sharing.json](records/sharing.json)。サムネの日本語ファイル名はGitHubで自動変換されています。`github_name`が実際の添付名、`name`が保存時の元ファイル名です。RESTで取得するときは`name`の名前で保存するとpreview.htmlから表示できます。Mac側のファイル名と内容は維持しています。

最終検査記録は **EP006_records_v02_confirmed.zip**、最終チェックサムは **SHA256SUMS_v02_confirmed.txt**、承認は **EP006_v02_approval.json**。先行確認用Draft 424414685は別途保全。最終Draftの抽出画像はEP006_review_frames_v02.zip。

変更外8,662フレーム中112フレームの圧縮差は本人が許容し、v02確定済み。画素完全一致の未達と測定値は隠さず記録。[制作結果](../wom06_制作結果_v02_20261027.md)／[承認記録](records/pixel_requirement_acceptance.json)。音声・字幕はv01同一。SRTを再添付し、本編M4A・WAVとKling原本はv01 Release 424086149参照。
