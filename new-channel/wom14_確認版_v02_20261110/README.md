# 第14話「鬼」確認版v02（通常版3本を先行共有）

[非公開Draft Release](https://github.com/yasukawa1980/youtube/releases/tag/untagged-7fdea0a3651470accaea)（ID **439832736**）。v01 Release439388240を保全。

[制作結果・検品結果・残る2点](../wom14_制作結果_v02_20261110.md)。英日1080pと英語4Kは完成・検証済み。字幕入り確認版と最終ZIPは本人回答後。

|添付|asset ID|バイト|SHA-256|
|---|---:|---:|---|
|EP014_Oni_en_v02_1080p30.mp4|729632248|81548631|`b0dccdd21ed11855e76e1b8b8c3f886b414b31f4d5c62349196247d681428b68`|
|EP014_Oni_en_v02_2160p30.mp4|729632254|198576503|`981aa4b7a63bf2631014ec683a9d5a1bdb358d124ac37f6751a1e7af4ba380d0`|
|EP014_Oni_ja_v02_1080p30.mp4|729632243|83223190|`1167db3b3354ecf26e0c61b6c53fdfbc901c652df518262d603bd71fc359d7e7`|

取得：`gh api -H 'Accept: application/octet-stream' repos/yasukawa1980/youtube/releases/assets/ASSET_ID > OUTPUT`。全3本をRESTで全量再取得して照合済み。匿名アクセス404。

通常3本の未修正23ショットは全フレーム画素一致。音声・SRT・時間割不変。R10-27は原寸1.0倍で一部の筆画44pxのため55px未達。字幕入り確認版の再圧縮差とR10の優先順位が回答待ち。

画像の見方：`compare_*_pair.jpg` は左v01・右v02の実動画比較。`continuous_*` は最終動画の全31ショット一覧。`v02_*_sheet.jpg` は構図プレビュー。サムネ比較は `thumbnail_before_after_v02.jpg`。R10の比較用1.25倍案は `R10_native_limit_options.jpg`（未採用）。

SSD保存先：`/Volumes/ESD-02/新チャンネル/EP014_Oni/確認版_v02_20261110`。
