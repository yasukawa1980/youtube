# youtube

YouTubeチャンネル用のメモ・素材管理リポジトリです。

## フォルダ構成

- `scripts/` — 動画の台本・構成メモ
- `ideas/` — 動画アイデアのメモ

## 動画制作の流れ

1. アイデアを `ideas/` にメモ
2. 台本を `scripts/` に作成
3. 編集
4. アップロード

## 童謡の単曲版を作る

生成コードは `bgm/bgmkit/single_songs.py`。設定は1曲ごとに `bgm/volumes/doyo03.yaml`〜`doyo06.yaml` に分けています。既存のdoyo01・doyo02は秋・冬の童謡集として維持します。

| 単曲ID | 公開順・曲名 | 設定 | 完成尺 | LUFS |
|---|---|---|---|---|
| doyo03 | 01 夕焼け小焼け | [設定](bgm/volumes/doyo03.yaml) | 270.800秒 | −14.02 |
| doyo04 | 02 赤とんぼ | [設定](bgm/volumes/doyo04.yaml) | 253.867秒 | −14.07 |
| doyo05 | 03 紅葉 | [設定](bgm/volumes/doyo05.yaml) | 279.367秒 | −13.99 |
| doyo06 | 04 七つの子 | [設定](bgm/volumes/doyo06.yaml) | 217.936秒 | −14.13 |

完成動画・サムネ原本・使用音源は `/Users/ryo/Desktop/BGM/1_Whispers of Japan/童謡単曲/` の各曲フォルダにあります。各設定の `artifacts` が現行ファイルの所在を示します。確認用サムネは `サムネ確認用/童謡単曲/doyo03_サムネ.jpg`〜`doyo06_サムネ.jpg`（手直し予定）。

里の秋は保留。紅葉の制作時True Peakは−0.92 dBTPで検証時の警告があります。4曲の測定値・素材・確認状況は [制作まとめ](bgm/DOYO01_テーマ設計.md)、移動前後の記録は [整理結果](bgm/DOYO01_整理結果_20261018.json) を参照してください。

### 準備と実行

Python 3.9以降、FFmpeg / ffprobe（libx264、AAC、loudnorm、acrossfade対応）、PyYAMLが必要です。

```bash
brew install ffmpeg
python3 -m venv .venv-single-songs
source .venv-single-songs/bin/activate
python3 -m pip install -r bgm/requirements-single-songs.txt
cd /Users/ryo/youtube
# 素材、切り出し時刻、出力先を確認するだけ（4曲）
for id in doyo03 doyo04 doyo05 doyo06; do
  python3 -m bgm.bgmkit.single_songs --config "bgm/volumes/$id.yaml" --version short --check
done
# 夕焼け小焼けの短い単曲版を生成（既定設定はdoyo03）
python3 -m bgm.bgmkit.single_songs --version short
# 赤とんぼの短い単曲版を生成
python3 -m bgm.bgmkit.single_songs --config bgm/volumes/doyo04.yaml --version short
```

既存の完成動画・投稿文・検証結果があれば停止します。作り直す場合だけ `--overwrite` を明示します。`--version short` は横型の短い単曲版、`10min` / `30min` は10分・30分版。省略すると3種類すべてを生成します。今回は整理のみで、動画を再生成していません。

出力先は各YAMLの `output_dir`。動画と同名の `.txt` に投稿文下書き、`.json` に測定値・使用素材・接続位置・検証結果を保存します。今回移行した既存動画の測定記録は `bgm/DOYO01_単曲版_測定記録.json` にも保存しています。既存の `output/yuuyake_10分.mp4`・`output/yuuyake_30分.mp4` は今回の移動一覧に含まれないため現位置に残しています。

### 設定と処理

相対パスは設定ファイルのあるフォルダを基準に解決します。現行の素材パス・出力先はMacの絶対パスです。別のMacで実行するときは設定内のパスを実在する場所へ変更してください。

- `songs[].audio.path` は音源全体。`short.audio` の `start` / `end` で短い版の使用範囲を指定し、`short.repeats` で1〜2回の演奏を指定します。
- `end` は長さではなく元音源の終了位置。時刻は秒数または引用符付きの `"02:45"` 形式で指定します。
- `alternates` があると30分版で基本音源と別テイクを順に繰り返します。10分版と短い版には影響しません。
- 接続は1〜2秒の線形クロスフェード。冒頭・末尾は3〜5秒のフェード。長尺版は最後が曲の途中でフェードする場合があります。
- 48 kHz・ステレオで整音し、完成AACを再測定。出力は1920×1080・30 fps・H.264＋AAC 192 kbpsです。
- 全編デコードと尺・コーデックを確認します。目標LUFSとの差が1 LUを超える場合やTrue Peakが−1 dBTPを超える場合は警告します。主観的な聴感確認は別途必要です。

既存の回帰テスト（FFmpeg実行を含む）：

```bash
python3 -m unittest discover -s bgm/tests -p 'test_single_songs.py' -v
```
