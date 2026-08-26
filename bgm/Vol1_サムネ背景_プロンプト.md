# Vol.1「月夜の鳥居」サムネ背景 —— 生成用プロンプト

> **★★2026年8月26日、この巻は作り直さないことに決まった（本人の判断）。**
> **Vol.1は最初の作品なので、当時のサムネのまま残す。**
> したがって以下は**使っていない**。気が変わったときのために置いてある。
>
> **★結果として、チャンネルでVol.1だけ見た目が違う。** 英語の題字・旧レイアウト
> （タグライン `SLEEP・RELAX・STUDY` と `Japanese Relaxing Music`）・尺バッジあり。
> 他の16本は日本語1行に統一されている。**これは承知のうえの例外。**
> 一覧で1本だけ浮くが、1本目にはそれだけの理由がある。
>
> `volumes/vol1.yaml` は削除した（背景が無いので実行すれば必ず失敗する設定だった）。
> 作るときは同じ内容で作り直すこと。


**★★これは再現であって、本編の一場面ではない。**
Vol.1だけ元画像も完成動画も手元に残っていない（`月夜の静寂.mov` は全フレーム真っ黒で、
53MBという容量もAAC音声だけでほぼ説明がつく＝黒い映像トラック付きの音源ファイル）。
他の15本は本編か元画像から作れたので、**この巻だけが例外**。

> **★先に試すべき手がある。** YouTube Studio から公開済みのVol.1をダウンロードできるなら、
> そこから1コマ抜くほうが確実（Vol.2はその方法で作った）。
> **生成すると、サムネにだけ本編に無い絵が出ることになる。**
> 睡眠用BGMでその齟齬が致命傷になるとは思わないが、避けられるなら避けたい。

## 何を再現するのか

公開済みのサムネ（`Moonlit Shrine_サムネ_16x9.png`）から読み取ったVol.1の世界：

- **鳥居**（題が「月夜の鳥居」なので、これが主役）
- 社殿・石灯籠・**暖色の灯り**が数点
- **濡れた石畳**の参道
- **石橋と渓流**
- 杉と竹の森、遠景の山
- **雲のかかった満月**（冷たい銀）

memo に「Vol.1は橋と渓流と竹で桜がない」とある（Vol.3の夜桜と分けるための区別）。
**桜を出さないこと。** 出すとVol.3と見分けがつかなくなる。

## 3つの禁止

1. **文字** … 鳥居の扁額（額束）に**必ず**書かせようとする。**無地と明示してある**。
   公開済みのサムネには実際に文字が入っており、現行の設計では不可
2. **桜** … Vol.3の差別化要素。この巻には無い
3. **人物** … Whispers は全巻とも無人

## 右に主役・左は静かに

題字のスクリムが左920pxを覆う（1920px中）。**鳥居は右半分に置き、月も右上**。
左三分の一は暗い杉と竹だけにする。

---

## 本命

```
Photorealistic cinematic still of a Japanese Shinto shrine approach at night under a full moon.

Composition in three clear depths. Nearest: a wet stone-flagged path entering from the lower left corner, each flagstone a black mirror holding long soft reflections, moss thick in the joints, wet ferns at the edge. Middle: a large weathered wooden torii gate standing across the path in the RIGHT half of the frame, its two uprights and curved lintel dark and rain-darkened, the grain of the wood clearly visible; the plaque on the gate is completely plain, blank and unmarked. Beyond and to the right of the torii, a small stone bridge arches over a shallow stream, and the tiled roof and warm lantern-lit interior of a shrine building show among the trees. Farthest: tall cedar and bamboo closing in on both sides, and forested hills dissolving into blue haze.

A few stone lanterns along the path carry small warm amber flames — the only warm light in the frame, deliberately sparse.

The full moon hangs in the UPPER RIGHT of the sky behind thin drifting cloud, cool and blue-silver, and lays a pale path of light down the wet stones.

The LEFT THIRD of the frame is deliberately quiet: dark cedar trunks and open night sky, almost no detail, nothing the eye catches. This area will be covered by a title.

The only light sources are the moon and the few lanterns: cool blue-silver overall, low key, with small warm accents. Exposed so that texture is clearly visible everywhere — wood grain, wet stone, moss, foliage, roof tiles. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas.

Calm and completely static. No people, no animals. No cherry blossoms anywhere. No text, no signage, no lettering, no calligraphy of any kind — the plaque on the torii is blank. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 控え（本命が窮屈になったとき）

鳥居を**くぐった先から見返す**構図。奥行きが出しやすく、左が空きやすい。

```
Photorealistic cinematic still of a Japanese Shinto shrine approach at night under a full moon, seen from just inside the gate looking back out.

Composition in three clear depths. Nearest: one massive weathered wooden upright of a torii gate rising up the RIGHT edge of the frame, cut off by the frame, its rain-darkened grain and iron banding in sharp detail; the plaque above is completely plain, blank and unmarked. Middle: the wet stone-flagged path running away from the camera and down a flight of mossy steps, every stone a black mirror, a pair of stone lanterns with small warm amber flames standing at the head of the steps. Farthest: a shallow stream crossed by a low stone bridge, and beyond it tall cedar and bamboo and forested hills fading into blue haze.

The full moon hangs in the UPPER RIGHT behind thin cloud, cool and blue-silver, laying a pale path of light down the wet stones toward the camera.

The LEFT THIRD of the frame is deliberately quiet: dark cedar and bamboo and open night sky, almost no detail. This area will be covered by a title.

The only light sources are the moon and two lanterns: cool blue-silver overall, low key, with small warm accents. Exposed so that texture is clearly visible everywhere — wood grain, wet stone, moss, foliage. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas.

Calm and completely static. No people, no animals. No cherry blossoms anywhere. No text, no signage, no lettering, no calligraphy of any kind — the plaque is blank. No modern objects. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

---

## 生成したあとに

1. **扁額に文字が入っていないか。** ここが最も高い確率で破られる
2. **桜が混じっていないか**（Vol.3との区別が消える）
3. **月が左三分の一に来ていないか**（題字と喧嘩する）
4. 保存して、下を実行する：

```bash
cp <生成した画像> "/Volumes/ESD-EPB/BGM/1_Whispers of Japan/Vol01_資料と楽曲/Vol1_背景_01.png"
python3 -m bgmkit thumb vol1
```

`volumes/vol1.yaml` は用意済み（題字は `[月夜の, 鳥居]`）。
出来上がりは `Vol1_サムネ_16x9_日本語.png`。**168pxに落として、他の15本と並べて確認すること。**
