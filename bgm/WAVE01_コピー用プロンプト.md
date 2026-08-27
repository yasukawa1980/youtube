# WAVE01「月の水鏡」コピー用プロンプト —— Suno 10本 ＋ 本編5枚 ＋ サムネ1枚

設計は `WAVE01_テーマ設計.md`。設定は `genres/waves.yaml` と `volumes/wave01.yaml`。

保存先は `/Volumes/ESD-EPB/BGM/4_Waves of Japan/WAVE01_素材_月の水鏡/`
（`曲/` `ビート/` `画像/`）。

---

# 第一部 —— Suno（床）

## ★★この巻だけ、いつもの設計原則が反転する

[[suno-prompt-design]] の中核は**「曲どうしを似せない」**（編成と音域で割る・
一致度を最小化する・同じ種は2本まで）。**この巻ではそれを全部やらない。**

理由は床の役目が違うから。Whispers の22曲は**1曲ずつが聴かれる**が、
この巻の床は **`mosaic` で3〜4本を同時に重ね、25〜55分ひとつの面として鳴らす**。
**重なる以上、調と音色が揃っていないと濁るだけ**で、似ていることが要件になる。

**したがって全20本を同じ枠で作る。** 分けるのは場面の5段階だけ。

| | Whispers | この巻 |
|---|---|---|
| 目的 | 曲どうしを似せない | **同じ場面の中は似せる** |
| 割り方 | 編成・音域・発音の仕方 | **明るさと音域だけ**（場面1→5で暗く低く） |
| 選抜 | `select` が一致度で選ぶ | **選抜しない。場面ごとに4本そのまま重ねる** |
| 尺 | 2〜3分 | **長いほどよい**（`mosaic` の片が長く取れる） |

## 全10プロンプトに効いている規則

**1. 長さを削る言葉を書かない**（[[suno-prompt-design]]）。
`short` `stop` `brief` `staccato` `detached` `wide silences` `cut off` は
**曲の長さの指示として読まれる**。全プロンプトの末尾に定型句を置いてある：

```
A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.
```

**2. ★人声の否定を8つ書く。** この巻は笙（フリーリードの管楽器）が主役なので
**特に危ない**——`mouth organ` `breath` `voice` `sing` はどれも人声の合図で、
Vol.9では笙2曲に言葉のないハミングが入った。**本文で `mouth` と `breath` を使わない**
書き方にしてある（`shō` `free-reed` `air` で言う）。末尾は必ず：

```
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

**3. ★調は全曲 G。** ビート層の中心が 196Hz（G3）に固定されているため
（`WAVE01_テーマ設計.md` §5）。**全プロンプトに `in the key of G` を書いてある。**
調が違う曲が1本混ざるとビートと擦れる。**`analyze` のキー判定で必ず検品すること。**

**4. ★アタックのある音を1つも入れない。** 撥く・叩く・弾く音は3時間で必ず起こす。
琵琶・箏・金属打・ピアノは**この巻では一切使わない**（在庫があっても使わない）。

**5. 残響は書いてよい。** 尺八を使う巻では残響を書かない規則があるが（息が埋まるため）、
この巻に尺八は入らないので当てはまらない。むしろ**長い残響が面をつなぐ**。

## テイク数

**1場面につき 2プロンプト（A/B）× 3テイク = 6本を出し、良い4本を採る。**
2テイクちょうどにしない（[[suno-prompt-design]]「生成本数も必要数ちょうどにしない」）。
**全10プロンプト × 3テイク = 30本を出して20本使う。**

**★デコード後のMD5で重複を確認すること。** Sunoは同じファイルを2つ落とすことがあり、
ファイル名では判別できない（[[ai-image-download-duplicates]]）。

ファイル名は `薄暮A1.mp3` `薄暮A2.mp3` `薄暮B1.mp3` `薄暮B2.mp3` の形で
`volumes/wave01.yaml` の `order_tracks` に書いてある。

---

## 01. 薄暮（30分／うなり 12.00 → 11.33Hz）—— 明るい。まだ光がある

### 薄暮 A

```
A slow Japanese ambient drone in the key of G. A shō — the Japanese free-reed instrument — holds a wide, still cluster chord high above the listener, unmoving, like light held in the air. Beneath it, a soft bowed string pad in the same key swells and recedes without ever arriving anywhere. Every tone begins so gradually that no beginning can be heard. There is no melody, no rhythm, no pulse and no percussion of any kind. The harmony does not change; it only breathes wider and narrower. Warm, luminous, the colour of the last light on water. Long natural reverb, as if heard across an open lake. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### 薄暮 B

```
A slow Japanese ambient drone in the key of G, built from bowed strings alone. A low sustained G in the cellos, a fifth above it in the violas, and a high thin sheen of violins that never moves. The bowing is so slow that the change of direction cannot be heard. Nothing is plucked and nothing is struck. There is no melody, no rhythm and no percussion. The chord widens and narrows very gradually and never resolves. Warm and open, the sound of a wide valley just after sunset. Long natural reverb. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 02. 宵（25分／11.33 → 10.78Hz）—— 色が抜ける。音数が減る

### 宵 A

```
A slow Japanese ambient drone in the key of G. The shō — the Japanese free-reed instrument — is almost alone now, holding one wide still cluster chord that never changes. Far beneath it, a single low sustained G from a bowed double bass, felt more than heard. Nothing else. There is no melody, no rhythm, no pulse and no percussion. Every tone enters and leaves without an edge. Cool, blue, weightless, the sound of colour draining out of the sky. Long natural reverb. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### 宵 B

```
A slow Japanese ambient drone in the key of G, quieter and emptier than before. A shō — the Japanese free-reed instrument — sustains a still chord in the middle register, and a soft synthesiser pad doubles it an octave below, blurring its edges. Fewer tones than before, each one lasting far longer. No melody, no rhythm, no percussion, no attack of any kind. The harmony stays exactly where it is. Cool and dim, with a faint silver ring high in the reverb. Long natural reverb. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 03. 月の道（30分／10.78 → 10.12Hz）—— 笙のみ。和音が動かない

### 月の道 A

```
A slow Japanese ambient drone in the key of G, for shō alone — the Japanese free-reed instrument. One wide still cluster chord, sustained without interruption, filling the whole space. The chord does not change and does not move; only its inner balance shifts, so slowly that no change can be pointed to. There is no melody, no rhythm, no pulse, no percussion and no other instrument. Silver, cold and completely steady. Very long natural reverb, as if heard over still water. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### 月の道 B

```
A slow Japanese ambient drone in the key of G. A shō — the Japanese free-reed instrument — holds a still cluster chord, and a second shō a fifth away holds another, the two overlapping into one wider chord that never resolves. Nothing else is present. No melody, no rhythm, no pulse, no percussion, no attack. The sound is perfectly level from beginning to end. Silver and glassy, with a long tail of reverb that never fully decays. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 04. 凪（40分／10.12 → 9.23Hz）—— 低いドローン

### 凪 A

```
A very low, very slow ambient drone in the key of G. A sustained G in the lowest register — bowed double bass and a deep synthesiser pad together — with almost nothing above it except a faint fifth far overhead. The sound sits completely still, like a held breath of the earth. No melody, no rhythm, no pulse, no percussion, no attack, no movement of any kind. Dark, deep, enormous and calm. Very long natural reverb. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### 凪 B

```
A very low, very slow ambient drone in the key of G. One deep sustained G, doubled at the octave, played by bowed strings so quietly that the sound seems to come from underneath the floor. A single distant shō — the Japanese free-reed instrument — holds one thin tone far above it, barely audible. Nothing else. No melody, no rhythm, no pulse, no percussion, no attack. The whole piece stays at exactly one level. Dark, still, vast. Very long natural reverb. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 05. 靄（55分／9.23 → 8.00Hz）—— 動かない。この巻の底

### 靄 A

```
An extremely slow, extremely still ambient drone in the key of G. One low sustained G and its fifth, held by a deep synthesiser pad and bowed strings, with all high frequencies rolled away so that only the warm body of the sound remains. Nothing enters and nothing leaves. No melody, no rhythm, no pulse, no percussion, no attack, no change. It is a single unchanging field of sound. Dark, soft-edged, endless. Very long natural reverb, blurred until the source cannot be located. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### 靄 B

```
An extremely slow, extremely still ambient drone in the key of G, quieter than anything before it. A single low sustained G from a deep synthesiser pad, with a very faint shō — the Japanese free-reed instrument — somewhere far behind it, so distant that it reads as part of the reverb rather than as an instrument. No melody, no rhythm, no pulse, no percussion, no attack and no development whatsoever. The level never changes. Dark, warm, dissolved, with no edges anywhere. Very long natural reverb. A long, continuous, slowly unfolding piece with no clear sections and no ending. It continues in this same way for many minutes.

Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

---

# 第二部 —— 画像（本編5枚 ＋ サムネ1枚）

## ★★このシリーズは写実。水彩にしない

[[days-of-old-japan-series]] が水彩を担っている。**絵で分けるのがこの2ラインの
唯一の分かれ目**なので、こちらは写実を守ること。

## ★★1枚が25〜55分映り続ける

ごまかしが効かない。生成したら等倍で隅まで見て、崩れがあれば必ず作り直すこと。
**特に場面5は55分**（本編で最長）。

## 人物を固定する3点

- **淡い縹色(はなだいろ)の麻の着物**
- **肩に掛けた薄物（生成りの羽織り）**
- **襟足で低くひとつに結んだ髪**

SOJ01（濃紺の着物）SOJ02（麦わら帽子）と被らせない3点。
**本編5枚は顔を見せない**（後ろ姿のみ）。**サムネだけ顔を出す。**

## ★★全枚に効いている禁止 —— 最初の3つは「鏡」から出てくる

1. **★水面を乱すものを一切出さない** —— 鳥・魚・虫・落ち葉・雨・水の輪・波紋。
   **場面4と5で「完全な鏡」が要る以上、鳥が一羽居るだけで画が嘘になる。**
   人物も水際まで。水に触れさせない
2. **★月以外の光源を出さない** —— 灯籠・提灯・家の灯り・星の主張。二つ目の光があると対称が壊れる
3. **★月に光条（十字のレンズフレア）を付けない** —— 肉眼にも静止画にも出ない嘘
4. **文字** —— 木札・石碑・灯籠の刻字・舟の船名。灯籠は無地と明示してある
5. **現代物** —— 電線・電柱・ガードレール・コンクリート護岸・アルミの手すり・ボート小屋
6. **★★手前を陸にしない**（2026年8月27日、場面03とサムネの作り直しで判明）

## ★★★反射を描かせる絵は、カメラを水の上に出す

**初版の場面03とサムネは失敗した。** 女性の反転した顔と肩が、乾いた砂利の一粒一粒の
上に描かれた。原因はプロンプトの守り方ではなく**幾何**で、
**反射は必ず「対象の足元からカメラの側へ」伸びる**。
`in the near foreground, wet dark pebbles at the waterline` と手前を陸に指定した以上、
反射の行き場は砂利しかなかった。**モデルは正しく描いている。**

**★「陸に反射を描くな」と否定で足しても直らない。** 反射そのものが消えて、
この巻の主題（鏡）が消える。

**★直し方はカメラを水の上に出すこと。** 視点を水面のすぐ上に置いて岸を振り返る形にし、
**画面の下半分から三分の二を、途切れない水にする。** そうすれば反射の落ちる先が水になる。
**うまくいった場面05は手前が全部水だったので破綻していない。** そこに合わせる。

- 人物は向こう岸の水際に立つ（**水には触れないまま**でよい）
- 手前は「水そのもの」を実体として与える（[[days-of-old-japan-series]] の
  「何も無いと書くと靄で埋める」と同じ理屈で、空けずに面を与える）
- 石・砂利・地面を手前に**1つも置かない**

## ★★月と人物は必ず画面の右

サムネの題字が乗るスクリム（x=40〜920）を暗いまま保つため。
**この巻は特に落ちやすい**——月柱が水面を縦に走るので、構図を間違えると題字の真下に
光の筋が入る。**全枚の英文に `on the right side of the frame` と書き込んである。**

## ★★「何も無い」と書かない

DOJ01 で左三分の一を `Nothing at all is placed in the LEFT THIRD` と書いたら
**モデルが靄で埋めた**。描くものが無いので埋めたのであって、
**禁止ではなく実体を与える**のが効く。この巻の左には毎枚
「暗い対岸の稜線」「静かな水の面」など**実在の面**を与えてある。

## 3つの奥行きを毎枚に書いてある

手前（細部が鋭い）／中景（主題）／遠景（霞んで溶ける）。
**手前の細部を省かせないこと。** ここが平坦だと壁紙に見えてくる。

---

## 01. 薄暮・桟橋の突端（30分）★人物

```
A still mountain lake in Japan at late dusk, photorealistic, seen from the shore. The last band of sunset colour lies low along the far ridge; the sky above it has already gone deep blue. Three clear depths: in the near foreground, the weathered planks of an old wooden pier running away from the camera, every grain and nail head sharp, wet at the edges; in the middle, the end of the pier and the woman standing at its tip, small, facing the water, on the right side of the frame; far behind, the dark ridgeline of the opposite shore dissolving into evening haze. The water still carries a fine breeze-ripple, so the reflected light is broken into countless small pieces and no clear mirror image forms — her figure casts no readable reflection at this stage, and no reflection of any kind falls on the planks of the pier. The left side of the frame is the quiet dark ridge and the flat unlit surface of the water — real surfaces, softly lit, with little detail. Cool blue overall with one warm band of remaining light low on the right. Natural light only. Early twentieth century Japan, no modern objects anywhere.

A single young woman seen from behind, her face never visible to the camera. She wears a pale hanada-blue linen kimono with an unbleached light wrap over her shoulders, and her hair is tied low at the nape. Her hands are not rendered in detail. She stands quietly, not posed. She occupies only a small part of the frame; the place holds her. She does not touch the water. No other people anywhere in the image.

No birds, no fish, no insects, no falling leaves, no rain, no ripples spreading in rings. No lanterns, no lamps, no house lights, no second light source of any kind. No star pattern or cross-shaped flare on any light. No writing, letters or characters anywhere. No power lines, poles, guard rails, concrete embankments, metal railings or boat sheds.
```

## 02. 宵・岸辺に座る（25分）★人物

```
A still mountain lake in Japan in the blue hour after sunset, photorealistic, seen from the shore. All colour has drained from the sky, which is now a single even indigo; the moon has just cleared the eastern ridge on the right side of the frame and sits low and small above the mountains. Three clear depths: in the near foreground, dark reeds and a low flat rock at the water's edge, each stem and grain sharp; in the middle, the woman seated on the rock, seen from behind, facing the water and the moon, on the right side of the frame; far behind, the eastern ridge with the low moon above it, softened by haze. The water is far calmer than before — the ripple is fine and even, and the moon's reflection has begun to gather into a narrow unsteady column. The reeds are completely still; there is no wind. The left side of the frame is the dark opposite shore and the flat unlit water — real surfaces, dimly lit, with little detail. Indigo and silver only. Natural light only. Early twentieth century Japan, no modern objects anywhere.

A single young woman seen from behind, her face never visible to the camera. She wears a pale hanada-blue linen kimono with an unbleached light wrap over her shoulders, and her hair is tied low at the nape. Her hands are not rendered in detail. She sits quietly and still. She does not touch the water. No other people anywhere in the image.

No birds, no fish, no insects, no falling leaves, no rain, no ripples spreading in rings. No lanterns, no lamps, no house lights, no second light source of any kind. No star pattern or cross-shaped flare on the moon. No writing, letters or characters anywhere. No power lines, poles, guard rails, concrete embankments, metal railings or boat sheds.
```

## 03. 月の道・水際に立つ（30分）★人物 ★この巻の主題

**★2026年8月27日 改訂。** 初版は手前を砂利にしていたため、反射が石の上に落ちた。
**カメラを水の上に出して、手前を全部水にしてある。**

```
A still mountain lake in Japan at night, photorealistic. The camera is low, just above the surface of the water and out on the lake itself, looking back toward the shore. THE ENTIRE LOWER TWO THIRDS OF THE FRAME IS UNBROKEN OPEN WATER — there are no stones, no gravel, no sand and no ground of any kind in the foreground. The moon is high on the right side of the frame, and a bright column of moonlight runs across the water from behind the woman toward the camera. Three clear depths: in the near foreground, the black glass surface of the still water itself, with the faintest grain of light on it; in the middle, the woman standing on the far waterline, seen from behind, on the right side of the frame; far behind her, the low dark ridge of the opposite shore dissolving into haze. THE WATER IS PERFECTLY STILL — her reflection extends from her feet down toward the camera, complete and sharply readable, lying entirely on open water, and it is the single most important element of the picture. Every reflection in this image falls on water and on nothing else. The left side of the frame is the dark far shore and the flat black water — real surfaces, faintly lit, with little detail. Silver, indigo and black only. Natural light only. Early twentieth century Japan, no modern objects anywhere.

A single young woman seen from behind, her face never visible to the camera. She wears a pale hanada-blue linen kimono with an unbleached light wrap over her shoulders, and her hair is tied low at the nape. Her whole figure is visible down to her feet, standing on the ground at the far edge of the water. Her hands are not rendered in detail. She stands at the very edge of the water but does not step into it and does not touch it. No other people anywhere in the image.

No stones, gravel, sand, shingle, beach or dry ground anywhere in the near foreground — the foreground is water. No reflection of any kind falling on land. No birds, no fish, no insects, no falling leaves, no rain, no ripples spreading in rings. No lanterns, no lamps, no house lights, no second light source of any kind. No star pattern or cross-shaped flare on the moon. No writing, letters or characters anywhere. No power lines, poles, guard rails, concrete embankments, metal railings or boat sheds.
```

## 04. 凪・無人の湖（40分）

```
A still mountain lake in Japan late at night, photorealistic, seen from a low viewpoint just above the water. There is no one in the picture. The moon is high on the right side of the frame. THE WATER IS A PERFECT MIRROR — the opposite mountains, the moon and the sky are reproduced in it exactly, upside down, with no distortion at all, so that the picture reads as almost symmetrical top to bottom. The waterline where the two halves meet is still just findable, but only barely. Three clear depths: in the near foreground, the dark still surface of the water itself, glass-smooth, with one small moored wooden boat at the right, empty, its hull and its reflection equally sharp; in the middle, the mirrored line of the far shore; far behind, the ridge and its inverted twin fading into thin haze. The left side of the frame is the dark mirrored ridge and the still black water — real surfaces, faintly lit, with little detail. Silver, indigo and black only. Natural light only. Early twentieth century Japan, no modern objects anywhere. No people anywhere in the image.

No birds, no fish, no insects, no falling leaves, no rain, no ripples spreading in rings, no wake behind the boat — the surface is completely undisturbed. No lanterns, no lamps, no house lights, no second light source of any kind. No star pattern or cross-shaped flare on the moon. No writing, letters or characters anywhere, including on the boat. No power lines, poles, guard rails, concrete embankments, metal railings or boat sheds.
```

## 05. 靄・上下が消える（55分）★最長・この巻の底

```
A still mountain lake in Japan in the deep of the night, photorealistic, seen from just above the water. There is no one in the picture and no shore is visible. A low mist stands on the surface and has swallowed the far bank entirely. THE HORIZON HAS DISAPPEARED — the water is a flawless mirror and the mist blurs the join, so that the moon above and the moon below are equally clear and it is genuinely impossible to tell which half of the picture is sky and which is water. The moon sits on the right side of the frame, with its twin directly below it. Three clear depths: in the near foreground, the black glass surface of the water with the faintest grain of light on it; in the middle, the two moons and the soft standing mist between them; far behind, nothing but graduated haze. The left side of the frame is quiet luminous mist over still black water — a real surface, softly lit, almost without detail. Silver, indigo and black only, very dark overall but never crushed. Natural light only. No modern objects anywhere. No people anywhere in the image.

No birds, no fish, no insects, no falling leaves, no rain, no ripples spreading in rings — the surface is completely undisturbed. No lanterns, no lamps, no house lights, no second light source of any kind. No star pattern or cross-shaped flare on either moon. No writing, letters or characters anywhere. No power lines, poles, guard rails, concrete embankments, metal railings or boat sheds. No land, no buildings, no boats.
```

## 06. サムネ（★顔あり・別画像）—— ★2026年8月27日、**使わないことにした**

**本編の場面02をそのまま使う**（本人の指定。実測で通っている。設計書 §7）。
作り直しが要るときのために残してある。

**★2026年8月27日 改訂。** 初版は反転した顔と肩が乾いた砂利の上に描かれた。
**カメラを水の上に出し、下半分を全部水にしてある。**

**★構図の要件は3つ、どれも絶対。**
①月と女性を画面の右に置く（左のスクリムを暗く保つ）
②水面に映り込みを必ず入れる（168pxで顔は消えるが**「上下に同じものが並ぶ」形は残る**）
③**手前に石・砂利・地面を1つも置かない**（②が破綻する）

```
A young Japanese woman at the edge of a perfectly still mountain lake at night, photorealistic. The camera is low, just above the surface of the water and only a few paces out from the shore, looking back at her, so that she stands large in the frame. THE ENTIRE LOWER HALF OF THE FRAME IS UNBROKEN OPEN WATER — there are no stones, no gravel, no sand and no ground of any kind anywhere in the picture except the narrow dark line of the far bank. She is on the right side of the frame, standing at the waterline in three-quarter view, her face clearly visible and calm, lit softly from the side by a low moon behind her to the right. THE WATER IS A FLAWLESS MIRROR — her whole figure and the moon are each reproduced in it directly below themselves, complete and sharp, lying entirely on open water. Every reflection in this image falls on water and on nothing else. Three depths: the still black water in the near foreground with the faintest grain of light on it, the woman and her reflection in the middle, and the far ridge dissolving into haze behind. The left third of the frame is the dark opposite ridge and flat black water — real surfaces, dimly lit, with almost no detail, dark enough for text to sit over it. Silver, indigo and black, with the warm skin tone as the only other colour. Natural light only. Early twentieth century Japan.

She wears a pale hanada-blue linen kimono with an unbleached light wrap over her shoulders, and her hair is tied low at the nape. Her expression is quiet and unforced, eyes open, not smiling. Her whole figure is visible down to her feet, standing on the ground at the edge of the water. Her hands are not rendered in detail. She does not step into the water and does not touch it.

No stones, gravel, sand, shingle, beach or dry ground anywhere in the near foreground — the foreground is water. No reflection of any kind falling on land. No other people anywhere in the image. No birds, no fish, no ripples spreading in rings — the surface is completely undisturbed. No lanterns, no lamps, no house lights, no second light source. No star pattern or cross-shaped flare on the moon. No writing, letters or characters anywhere. No power lines, poles, guard rails, concrete embankments, metal railings or boat sheds.
```

**★出来たら168pxで実測してから確定する。** [[whispers-thumbnail-design]] の手順で、
題字が乗る帯の**最大輝度とばらつき**を測る。
