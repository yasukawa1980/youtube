# Vol.14 Moonlit Pine — コピー用プロンプト集

月夜の松／テーマ「巡る」。**尺は未定。30分でも60分でも成立するように素材を集める。**

## この巻の設計

**差別化の軸は「単一の対象を全方位から」。** 既存13本＋コンピ2本は、どれも「場所」を旅していた
（林・庭・塔・棚田・座敷）。この巻は**一本の松だけ**を撮る。松は最後まで一切動かず、
動くのはカメラだけ。遠景 → 幹 → 樹皮 → 松葉 → 球果 → 見上げ → 逆光 → また遠景、と
距離と角度が一巡して終わる。

**Vol.13の真逆になるのが狙い。** 冬木立＝裸・細い線・透ける。松＝常緑・黒く重い塊・透けない。
チャンネル一覧で並んだときに、同じ「木の巻」に見えない。

**季節は晩秋から初冬の、よく晴れた夜。** 地面は**苔と降り積もった落ち松葉**にする。
**霜は使わない**（Vol.13と被る）。雪も入れない（Vol.9）。

---

## 尺を決めていないことへの対応

| | 30分にする場合 | 60分にする場合 |
|---|---|---|
| 曲数 | 10曲 | 22曲 |
| 画像 | **22枚のうち10枚を使う** | 22枚すべて |
| 楽曲 | 44本から10本を選抜 | 44本から22本を選抜 |

**画像枚数は曲数の約数でないと、1枚あたりの表示時間が暴れる。**
22曲なら22枚、10曲なら10枚。だから**11場面 × A（引き）/ B（寄り）＝22枚**で撮っておき、
30分に決まったら下記の10枚を使う。

> 30分になった場合に使う10枚：
> **01・04・05・09・12・13・15・17・19・22**
> （遠景／樹皮／根方／葉叢／球果／枝越しの月／逆光シルエット／見上げ／遠景／夜明け前）
> A・Bが交互になりすぎず、距離のはしごが残るように選んである。

**楽曲は多いぶんには困らない。** 22曲選抜には「1種あたり上限4本」が要り、
そのためには種類が8つ必要（8×4＝32で、22ちょうどにならない）。10曲選抜にする場合も
同じ44本から選び直せばよく、**捨てる作業は発生しない。**

---

## A. 画像 22枚

### 保存のきまり

- **16:9 で出す**（手生成なので bgmkit の 3:2→16:9 切り出しとガンマ1.3は掛からない）
- 保存先は `Vol14_素材_松/画像/`
- ファイル名は **`vol14_01.png` 〜 `vol14_22.png`**（下の番号と一致させる）
- **1枚ずつ生成する**

### 毎回チェックすること

- **モミ・トウヒになっていないか。** 松は「円錐形のクリスマスツリー」ではない。
  幹が曲がり、太枝が**横に段々と広がる**形が出ているか
- **盆栽になっていないか**（鉢・台・室内）
- **海が入っていないか。** 松＝白砂青松でAIは浜辺を出したがる。
  **入ると波音を期待されて即離脱**になるので、1枚でも海が写ったら捨てる
- **枝がブレていないか。** 松風は日本語圏で最も強い「音の連想」。無風で通す
- **葉叢が真っ黒に潰れていないか。** 常緑は塊で暗くなる。針の1本1本が見えているか
  （逆光を狙う15・16だけは例外で、シルエットでよい）
- **霜・雪が入っていないか**（Vol.13・Vol.9と被る）
- **注連縄・柵・立札が付いていないか**（御神木としてAIが足したがる。紙垂と木札は崩れ字の元）
- **同じ画像を2回保存していないか**（名前も日時も違うので目では気づけない。MD5で見る）

---

### 場面1 — 丘の上の松

#### 01（A・遠景の全景）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. A single ancient Japanese black pine standing alone on a low grassy hill on a clear autumn night, seen from a distance at eye level, the whole tree in frame against a deep blue sky with a full moon high above it. The trunk leans and twists; the heavy branches spread outward in flat, layered tiers, wider than the tree is tall — the shape of an old pine that has stood a long time, gnarled and asymmetrical. Not a cone-shaped conifer, not a fir, not a spruce, not a Christmas tree silhouette, not a straight-trunked plantation tree, not a bonsai, no pot, no stand. The hill is dry grass and moss; there is no sea, no ocean, no beach, no sand, no waves, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. The tree stands in the right two thirds; the left third is open empty sky. The needle masses are exposed so that individual needles read — dark blue-green, not a solid black silhouette. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no ropes, no straw rope, no paper streamers, no fences, no posts, no power lines, no paved paths, no buildings, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 02（B・中景、枝の広がり）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. The same ancient Japanese black pine seen from closer on the hill at night, near enough that the spreading branches fill most of the frame and the top of the tree is cut off by the upper edge. The layered tiers of foliage run horizontally across the picture, one above another, with open moonlit sky visible between them. Gnarled, asymmetrical, leaning. Not a cone-shaped conifer, not a fir, not a spruce, not a Christmas tree silhouette, not a bonsai, no pot. There is no sea, no ocean, no beach, no sand, no waves, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. The needle masses are exposed so that individual needles read — dark blue-green, not a solid black silhouette. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no ropes, no straw rope, no paper streamers, no fences, no power lines, no buildings, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面2 — 幹

#### 03（A・幹の全体）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. The trunk of an old Japanese black pine at night, seen from a few steps away at eye level: a thick, leaning, twisting trunk that rises from the grass and splits into two heavy limbs near the top of the frame. Cold moonlight rakes across it from the right so the deep bark plates catch the light and the hollows stay open shadow. The hill behind falls away into blue darkness. Not a straight-trunked plantation conifer, not a fir, not a spruce, not a bonsai, no pot. There is no sea, no ocean, no beach, no sand, no waves, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no ropes, no straw rope, no paper streamers, no fences, no power lines, no buildings, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 04（B・樹皮のマクロ）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Extreme close view of the bark of an old Japanese black pine at night, the whole frame filled with thick irregular plates of bark divided by deep black fissures, like cracked armour. Fine grey lichen sits in the seams and a little dried resin has run and hardened on one plate. Cold moonlight grazes across from one side so every plate casts its own small shadow and the surface reads as relief. No leaves, no needles in frame. There is no sea, no sand, no water anywhere in the frame. The air is completely still. Exposed brighter than a typical night shot: shadows open and full of texture, nothing crushed to solid black. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no insects, no ropes, no nails, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面3 — 根方

#### 05（A・根が地面をつかむ）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. The foot of an old Japanese black pine at night, seen low and close: the trunk flares out into thick roots that grip the ground and run away over moss and bare earth, half buried, worn smooth on top. Between them the ground is covered in a deep brown mat of fallen pine needles. Cold moonlight comes from the left and picks out the tops of the roots while the earth between stays open shadow. No frost, no snow, no ice anywhere. There is no sea, no ocean, no beach, no sand, no waves, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Exposed brighter than a typical night shot: the shadows are open and full of visible texture, nothing crushed to solid black, the grain of the bark and the individual fallen needles readable. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no ropes, no straw rope, no fences, no posts, no paved paths, no buildings, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 06（B・落ち松葉と苔のマクロ）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Extreme close view of the ground under an old pine at night, filling the whole frame: a deep layer of fallen pine needles lying in every direction, dry and reddish-brown, with cushions of dark green moss pushing up between them and one small pine cone lying on its side. Almost abstract. No frost, no snow, no ice; there is no sea, no beach, no sand, no water anywhere in the frame. The air is completely still. Exposed brighter than a typical night shot: shadows open and full of texture, nothing crushed to solid black, every needle separately readable. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no insects, no footprints, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面4 — 太枝

#### 07（A・曲がった大枝の走り）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. A single heavy branch of an old Japanese black pine at night, running almost horizontally across the whole width of the frame, bending twice on its way out, thicker than a person's body at the base and thinning toward the right edge. Tufts of dark needles sit along its upper side. The sky behind is deep even blue, slightly out of focus. Not a fir, not a spruce, not a straight branch, not a bonsai. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. The needle tufts are exposed so individual needles read, not a solid black mass. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no ropes, no props, no supports, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 08（B・枝の分岐点）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Close view at night of the place where two limbs of an old pine divide, the crotch between them swollen and scarred, the bark torn into ridges by the strain and one old broken stub healed over below. Cold moonlight comes from above and behind so the rim of each limb glows and the crotch stays in open shadow. There is no sea, no sand, no water anywhere in the frame. The air is completely still. Exposed brighter than a typical night shot: shadows open and full of texture, nothing crushed to solid black. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no nests, no ropes, no nails, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面5 — 松葉

#### 09（A・枝先の葉叢）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Close view at night of the end of a pine branch, the needles growing in dense radiating tufts at the tips of the shoots, each tuft a starburst of long stiff needles. Deep blue sky behind, thrown out of focus. Cold moonlight comes from behind and above so the needles are edged with light and their arrangement reads clearly — a mass made of thousands of separate hard lines, not a soft blur, not a solid black shape. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no insects, no spider webs, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 10（B・針葉のマクロ）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Extreme macro view at night of a few pine needles, filling the whole frame: long paired needles held in a papery brown sheath at the base, the fine lengthwise grooves along each needle visible, one needle crossing another. Everything behind falls away into soft deep blue. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Exposed brighter than a typical night shot: shadows open and full of texture, nothing crushed to solid black. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no insects, no spider webs, no dew, no droplets, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面6 — 球果

#### 11（A・枝についた松ぼっくり）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Close view at night of three or four pine cones still attached to a branch, sitting among the needles, their scales open and stiff, the woody spiral arrangement clearly visible. Cold moonlight comes from the upper left so each scale casts a small shadow on the one below. Deep blue night behind, out of focus. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Exposed brighter than a typical night shot: shadows open and full of texture, nothing crushed to solid black. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no squirrels, no insects, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 12（B・松ぼっくり1つのマクロ）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Extreme macro view at night of one open pine cone filling most of the frame, seen slightly from below, the overlapping woody scales spiralling around it, each scale tip worn pale and edged with cold moonlight, the gaps between them deep black. Almost architectural. Everything behind is soft deep blue. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Exposed brighter than a typical night shot: shadows open and full of texture, nothing crushed to solid black. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no insects, no dew, no droplets, no hands, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面7 — 枝越しの月

#### 13（A・枝の隙間から月）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. The full moon seen at night through a gap between two heavy pine branches, the tufts of needles crowding in from the top and the right, the moon large and clear in the right half of the frame with the sky between the needles deep blue and full of stars. The left third is open sky with only a thin twig crossing it. The needle tufts nearest the moon are edged with light; the rest are exposed enough that individual needles still read. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no ropes, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 14（B・月と葉叢の寄り）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Close view at night of a single tuft of pine needles directly in front of the full moon, the needles crossing the bright disc as sharp black lines, the moon slightly out of focus behind them so its craters are soft while every needle is razor sharp. The moon sits in the right half; the left third is open dark sky. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no insects, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面8 — 回り込み（逆光）

#### 15（A・月を背にした松の全景 ★サムネ用）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. The same ancient Japanese black pine seen at night from the far side of the hill, now with the full moon directly behind it, so the whole tree reads as a black silhouette against a luminous sky — the leaning trunk, the flat layered tiers of branches and the ragged edge of the needle masses all drawn as one hard black shape. The moon shows through a gap in the branches in the right half of the frame; the left third is open sky, glowing faintly where the moonlight spreads. This is the strongest shape of the night. Not a cone-shaped conifer, not a fir, not a spruce, not a Christmas tree silhouette, not a bonsai. There is no sea, no ocean, no beach, no sand, no waves, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no ropes, no straw rope, no fences, no power lines, no buildings, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 16（B・シルエットの縁）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Close view at night of the outer edge of a pine's foliage lit from directly behind by the moon: the needle tips along the rim burn white against the dark, while the inside of the mass falls away into deep blue-black. The line between the two runs diagonally across the frame. Almost abstract — light caught on thousands of needle points. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no insects, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面9 — 見上げ

#### 17（A・幹の真下から樹冠）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Standing at the foot of the old pine and looking up along the trunk at night: strong upward convergence, an extreme worm's-eye view, the trunk rushing away from the camera and the heavy limbs opening out overhead like a vault, patches of deep blue sky and a few stars showing between the needle masses. The moon is not in frame; the light comes from the upper right. Not a fir, not a spruce, not a straight plantation trunk, not a bonsai. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. The needle masses are exposed so that individual needles read, not a solid black ceiling. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no ropes, no supports, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 18（B・樹冠の中心）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Looking straight up into the centre of the old pine's crown at night: the limbs radiate outward from a point near the middle of the frame, needle masses layered over one another, a few gaps of deep blue sky and stars punched through the canopy. Strong convergence toward the centre. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Exposed brighter than a typical night shot: the canopy is open and full of visible texture, needles readable, nothing crushed to solid black. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no nests, no ropes, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面10 — 遠ざかる

#### 19（A・丘ごとの遠景）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. The hill seen from far off at night, the single old pine standing small on its crest against a wide deep blue sky, low rolling land around it fading into blue darkness, the moon high and to the left. The tree is no longer the whole picture — it is one dark shape on an empty ridge, and most of the frame is sky and open ground. There is no sea, no ocean, no beach, no sand, no waves, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. Not a fir, not a spruce, not a Christmas tree silhouette, no other trees around it. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no roads, no fences, no power lines, no poles, no buildings, no lights, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 20（B・丘の草地と松の影）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. The grassy crest of the hill at night with the shadow of the old pine thrown long across it, away from the camera: a single dark irregular shape lying over pale dry grass, the branches drawn out and stretched, the tree itself only partly in frame at the top right. The shadow is the subject. There is no sea, no ocean, no beach, no sand, no waves, no water anywhere in the frame. The air is completely still: no motion blur on any grass blade, nothing bending, nothing swaying. Exposed brighter than a typical night shot: shadows open and full of texture, individual grass blades readable, nothing crushed to solid black. Cold blue-grey moonlight, no warm tones, no orange, no amber, no yellow anywhere in the frame. No people, no animals, no birds, no paths, no fences, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

### 場面11 — 夜明け前

#### 21（A・薄明の松）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. The old pine on its hill just before dawn, the sky behind it turning a pale grey-blue from below while the top of the frame is still deep night blue, the moon gone and the shadows gone with it. The tree stands in flat, directionless light — no highlight, no cast shadow anywhere — and its needle masses read as soft dark grey-green rather than black. Still night, not yet daylight. Not a fir, not a spruce, not a Christmas tree silhouette, not a bonsai. There is no sea, no ocean, no beach, no sand, no waves, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. No warm tones, no orange, no amber, no yellow anywhere in the frame — the dawn is cold and blue, not golden. No people, no animals, no birds, no fences, no power lines, no buildings, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

#### 22（B・薄明の枝先）

```
16:9 aspect ratio, photorealistic, ultra high quality, highly detailed. Close view of the tip of a pine branch just before dawn, the needles soft dark green against a pale even grey-blue sky, lit from everywhere and nowhere so there are no shadows and no highlights at all, only shape. The quietest frame of the night. There is no sea, no sand, no water anywhere in the frame. The air is completely still: no motion blur, nothing bending, nothing swaying. No warm tones, no orange, no amber, no yellow anywhere in the frame — the dawn is cold and blue, not golden. No people, no animals, no birds, no insects, no dew, no droplets, no signage, no lettering of any kind. Photorealistic cinematic still, traditional Japanese scenery at night. The only light source is the moon: cool blue-silver, low key. Exposed so that texture is clearly visible everywhere — wood grain, stone, foliage, woven surfaces. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind. Muted palette, fine film grain, 16:9 composition with generous empty space on the left third for titles. Shot as a frame from a slow travel film, not a static postcard.
```

---

## B. Suno 8種（合計44テイク）

保存先は `Vol14_素材_松/楽曲/`。ワークスペースは Vol.14 用に新規作成する。

| 種 | 発音の仕方 | テイク数 | キー |
|---|---|---|---|
| ① 箏 | 撥く | 5 | D minor |
| ② 尺八 | 吹く | **10** | A minor |
| ③ フェルトピアノ | 打鍵 | 5 | F major |
| ④ 金属打 | 叩いて減衰 | 5 | C |
| ⑤ 胡弓 | 擦る | 5 | G minor |
| ⑥ 琵琶 | 撥く・ノイズ | 5 | B minor |
| ⑦ 木の打楽器 | 叩いて減衰 | 5 | （無調） |
| ⑧ フル編成 | 全部 | 4 | E minor |

**★8種にする理由。** 22曲を選ぶには「1種あたり上限4本」が要る。上限が小さいと同じ音色が
偏り、`種類数 × 上限` が22ちょうどだと配分が1通りに固定されて選抜が選抜にならない。
8種 × 4 = 32本ぶんの枠から22本を選ぶ形が、余地の残る最小構成。

**★⑥琵琶と⑦木の打楽器が新規枠。どちらも減衰系（撥く・叩く）。**
Vol.12で「吹く種は何本足しても割れない」（笙・龍笛・尺八が一致度0.37〜0.38の団子）が確定
しているので、新しい枠は必ず減衰系にする。Vol.12の風鐸は同種内0.275で全種中もっとも似ず、
選抜が自動的に上限まで積んだ。琵琶はVol.11で①箏と分離できている。

**★②尺八は10テイク取る。** Vol.13は12本中2本しか息の足切り（0.05）を通らなかった。
22曲なら尺八が最大4本要るので、歩留まりが同じなら10本でも足りない可能性がある。
**生成後に平坦度を測って、2本を切ったら追加生成する。**

**★残響ゼロを継続する。** 丘の上の一本松なので、設計上も壁がない。
Vol.12で尺八の息が 0.0537 → 0.0799 に増え、「長い残響の指示が息のノイズを埋める」が確定済み。

**★`wind` を1語も書かない。** 松風はこのシリーズで最も強い「音の連想」を持つ言葉。
場の描写は `on an open hill`（開けた丘）と `completely still`（完全な静止）だけで書く。

---

### ① 箏の独奏 — D minor・撥く（5テイク）

```
Japanese ambient in D minor, 50 BPM, for solo koto alone. Nothing is bowed or blown anywhere in the piece: no strings, no flute, no piano, no drone, no synth pad. Only plucked notes, very few of them, with long empty silence between them.
Recorded outdoors on an open hill beside one old pine tree — no room, no walls, almost no reverberation at all. The night air is cold and completely still; each sound carries a little way across the grass and then simply stops, and the silence after it is long.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### ② 尺八の独奏 — A minor・吹く（**10テイク**）

```
Japanese ambient in A minor, 56 BPM, for solo shakuhachi bamboo flute with almost nothing behind it — only a single low sustained drone, very far back. No piano, no koto, no strings, no percussion. Heavy muraiki: strong audible air turbulence across the blowing edge at the start of every note, the rush of air louder than the tone itself on some notes. Raw, rough, wooden. Long phrases with silence between them.
Recorded outdoors on an open hill beside one old pine tree — no room, no walls, almost no reverberation at all. The night air is cold and completely still; each sound carries a little way across the grass and then simply stops, and the silence after it is long.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

**生成後に1-5kHz平坦度で足切りする**（目安0.05〜0.2、0.02未満は落とす）。
Vol.13は12本中2本、Vol.12は12本中5本。**通った本数が4本に届かなければ追加生成する。**

### ③ フェルトピアノ独奏 — F major・打鍵（5テイク）

```
Japanese ambient in F major, 54 BPM, for solo felt piano alone — no strings, no flute, no koto, no bells, no synth pad, no drone. Single notes in the middle and upper register, struck softly and left completely alone, thin and clear, the felt taking the edge off every attack. A simple figure of four notes that returns unchanged after long pauses. Very few notes.
Recorded outdoors on an open hill beside one old pine tree — no room, no walls, almost no reverberation at all. The night air is cold and completely still; each sound carries a little way across the grass and then simply stops, and the silence after it is long.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### ④ 金属打（鈴と鉢）のみ — C・叩いて減衰（5テイク）

```
Japanese ambient built only from small struck metal bowls and singing bowls tuned around C, with one much larger bowl struck twice in the whole piece. No melody instruments at all — no piano, no koto, no flute, no strings, no drone. Each strike is left completely alone for a very long time, the overtones beating against each other as they fade to nothing. Extremely sparse — long stretches where nothing is struck at all.
Recorded outdoors on an open hill beside one old pine tree — no room, no walls, almost no reverberation at all. The night air is cold and completely still; each sound carries a little way across the grass and then simply stops, and the silence after it is long.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

**`chime` と書かない**（wind chime を連想させる）。`struck metal bowls` `singing bowls` に留める。

### ⑤ 胡弓 — G minor・擦る（5テイク）

```
Japanese ambient in G minor, 48 BPM, for a single bowed string instrument alone — a kokyu, small and nasal, bowed very slowly. Nothing is plucked or struck anywhere in the piece: no koto, no piano, no bells, no percussion. You can hear the hair of the bow dragging on the string, and the wood of the body resonating. Thin, reedy, plaintive, cold.
Recorded outdoors on an open hill beside one old pine tree — no room, no walls, almost no reverberation at all. The night air is cold and completely still; each sound carries a little way across the grass and then simply stops, and the silence after it is long.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### ⑥ 琵琶の独奏 — B minor・撥く（5テイク／**新規枠**）

```
Japanese ambient in B minor, 46 BPM, for solo biwa alone — a large plucked lute struck with a heavy wooden plectrum. Nothing is bowed or blown anywhere in the piece: no flute, no strings, no piano, no drone, no synth pad. Prominent sawari: a hard buzzing rattle where the string touches the neck, so every note begins as noise before it becomes a tone. The plectrum scrapes across the face of the instrument on some strokes. Very few notes, struck hard, then left to die away completely before the next one.
Recorded outdoors on an open hill beside one old pine tree — no room, no walls, almost no reverberation at all. The night air is cold and completely still; each sound carries a little way across the grass and then simply stops, and the silence after it is long.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

**琵琶は語りの伴奏楽器なので、人声が最も出やすい種。** 否定語8つに加えて、
**生成物は必ず全テイク聴いてから使う**（Vol.9の笙と同じ事故が起きうる）。

### ⑦ 木の打楽器のみ — 無調・叩いて減衰（5テイク／**新規枠**）

```
Japanese ambient built only from struck wood: two hard wooden clappers knocked together, and one large hollow wooden block struck with a padded stick. No pitched instruments at all — no piano, no koto, no flute, no strings, no bells, no metal, no drone. Every sound is dry, hard and short, with no ring and no sustain, and the space between strikes is very long. Extremely sparse — a single knock, then nothing for a long time. The grain of the wood is audible in each strike.
Recorded outdoors on an open hill beside one old pine tree — no room, no walls, almost no reverberation at all. The night air is cold and completely still; each sound carries a little way across the grass and then simply stops, and the silence after it is long.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

**この種は曲が短く出やすい**（音数を減らす指定は尺を縮める。Vol.9で確認済み）。
2分に届かないテイクが続くようなら `Extend` で伸ばす。**30秒未満のテイクは必ず捨てる**
（一致度が測れず0.000になり、選抜で必ず勝ってしまう。Vol.13で実際に起きた）。

### ⑧ Brand Standard — E minor・全編成（4テイク／**MD5で重複確認**）

```
Japanese ambient instrumental in E minor, 62 BPM. Felt piano, low shakuhachi long tones, koto, warm sustained strings, and one deep struck bowl. One ancient pine alone on a hill at night, the moon behind it, the whole tree drawn as a single black shape against the light. Wide, generous, quietly moving, the one moment the whole picture opens up. Calm and spacious mix.
Recorded outdoors on an open hill — no room, no walls, almost no reverberation at all.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

---

## C. 素材が揃ったあとの手順

```bash
cd /Users/ryo/youtube/bgm
python3 -m bgmkit analyze vol14
```

`analyze` の前に**必ず**やること（Vol.13で全部踏んだ）：

1. **ファイル名をNFCに揃える。** Sunoの日本語ファイル名は分解された形（ヒ+゚）で落ちてくる
   ことがあり、`kinds` の照合が静かに全滅する
2. **30秒未満のテイクを `exclude` に入れる。** 一致度が0.000になり選抜で必ず勝つ
3. **ディスクの空きを見る。** 60分なら5GB、30分なら3GBは要る

尺は `analyze` の結果（何本が使いものになるか）を見てから決めても間に合う。
**22曲ぶんの候補が揃わなければ30分にすればよい。**
