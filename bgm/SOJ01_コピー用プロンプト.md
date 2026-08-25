# Vol.16 コピー用プロンプト —— 画像22枚

**そのまま貼れる完結版。** 1枚ずつ生成する。16:9でそのまま出す（切り出しもガンマも掛けない）。
設計の根拠は `SOJ01_テーマ設計.md`。

保存先は `/Volumes/ESD-EPB/Whispers of Japan/SOJ01_素材_雨の石畳/画像/soj01_01.png` 〜 `_22.png`。

**★DLの重複はMD5で見ること。** 同じファイルが2回落ちても名前と日時では気づけない
（メモリ `ai-image-download-duplicates`）。22枚そろったら次で照合する：

```bash
md5 /Volumes/ESD-EPB/Whispers\ of\ Japan/SOJ01_素材_雨の石畳/画像/*.png | awk '{print $NF}' | sort | uniq -d
```

## 全枚に効いている禁止

1. **文字** — 提灯・のれん・看板・木札。この題材の最大の弱点。提灯は無地と明示してある
2. **雨の縦線** — AIの雨は引っかき傷になる。濡れた面・波紋・滴・霞で描かせる
3. **現代物** — 電線・電柱・室外機・車・LED・白線・プラスチック
4. **顔と手** — 後ろ姿のみ。手は袖に隠す。他の人物は1人も出さない
5. **月** — 雨雲の下に月は無い

## 人物が写るのは8枚だけ

場面 **1・4・7・9・12・13・16・20**。服の3点（**濃紺の着物・鴇鼠の帯・低い束ね髪**）を
毎回書いてあるので、顔を出さなくても同じ人物に見える。

---

## 01. ★通りの入口・引き

第一幕／音＝石畳  ★人物

```
Wide establishing shot looking down a narrow old Japanese merchant street of machiya townhouses, seen from its entrance. The street runs away from the camera and dissolves into soft haze. Rows of plain paper lanterns hang under the eaves on both sides, their amber light smeared into long vertical reflections on the black wet flagstones. Far down the street, small and distant, a woman under a traditional oiled-paper umbrella walks away from the camera. The left third of the frame is a quiet dark wall of wooden lattice with little detail.

A single woman in traditional Japanese dress, seen strictly from behind. Her face is never visible and never turns toward the camera. Her hands are covered by her kimono sleeves and are not rendered in detail. She wears a deep indigo kimono with a soft ash-rose obi tied in a flat drum knot at the back, and her hair is gathered in a low simple bun. She is completely still and quiet. No other people anywhere in the image.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 02. 濡れた石畳・寄り

第一幕／音＝石畳

```
Low close view of wet flagstone paving at night, the camera near the ground. Each stone is a black mirror; the amber lanterns overhead are reflected in long soft vertical streaks that stretch toward the camera. Thin films of water fill the joints between the stones. The stone is worn smooth and its grain and chipped edges are clearly visible. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 03. 格子戸の連なり・引き

第一幕／音＝石畳

```
A run of wooden lattice doors and windows along a machiya facade, viewed at a shallow angle along the street so the lattice repeats away into the distance. Warm light glows from behind the lattice and from the paper screens beyond it, throwing a grid of soft amber bars onto the wet stone below. Rain beads on the dark timber. A plain paper lantern hangs at the near eave. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 04. ★番傘の後ろ姿・中景 ←サムネ第一候補

第一幕／音＝番傘  ★人物

```
Medium shot from behind of a woman walking away down the wet lantern-lit street, holding a traditional oiled-paper umbrella with bamboo ribs above her. She is placed to the right of centre; the left third of the frame is quiet dark wall and empty wet stone. The umbrella's ribs catch the lantern light from below, and water runs off its rim in fine threads. Her dark shape is set against the warm reflections lying in the flagstones ahead of her. Her raised arm and the umbrella shaft are seen from behind and her hand is hidden by the falling sleeve of her kimono.

A single woman in traditional Japanese dress, seen strictly from behind. Her face is never visible and never turns toward the camera. Her hands are covered by her kimono sleeves and are not rendered in detail. She wears a deep indigo kimono with a soft ash-rose obi tied in a flat drum knot at the back, and her hair is gathered in a low simple bun. She is completely still and quiet. No other people anywhere in the image.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 05. 水たまりの波紋・寄り

第一幕／音＝水面

```
Close view, angled down, of a shallow puddle in a hollow of the paving, filled with the reflection of a paper lantern. Concentric ripples cross the reflection continuously and break the amber light into moving rings. The wet stone around the puddle is dark and glossy, its texture clearly visible. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 06. 辻の常夜灯・引き

第一幕／音＝石畳

```
A stone lantern standing where two narrow stone streets meet. Its inner flame glows warm behind soot-darkened stone; rain runs off its roof-stone in thin threads and pools at its base. The two streets recede into haze on either side, each lined with faint hanging lanterns. Moss and rain-darkened stone at its foot. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 07. ★傘の下から・見上げ

第一幕／音＝番傘  ★人物

```
Looking upward from just behind a woman's shoulder into the underside of her traditional oiled-paper umbrella, which fills most of the frame. The bamboo ribs radiate from the hub; the oiled paper glows faintly amber where the street lanterns shine through it from outside, and darker patches show where the paper is soaked. Beyond the umbrella's rim, out-of-focus lantern light and dark eaves. The back of her head and the nape of her neck are at the bottom edge of the frame, her hair in a low simple bun.

A single woman in traditional Japanese dress, seen strictly from behind. Her face is never visible and never turns toward the camera. Her hands are covered by her kimono sleeves and are not rendered in detail. She wears a deep indigo kimono with a soft ash-rose obi tied in a flat drum knot at the back, and her hair is gathered in a low simple bun. She is completely still and quiet. No other people anywhere in the image.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 08. 石橋と堀・引き

第一幕／音＝水面

```
A small arched stone bridge over a narrow canal running beside the street. The canal's black water is dimpled all over by rain, and a single paper lantern on the far bank lays a long broken amber reflection across it. The bridge's worn stone rail is wet and gleaming. Low mossy stone embankments on both sides. Haze closes the view beyond the bridge. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 09. ★軒下に入る・中景

第二幕／音＝軒  ★人物

```
A woman seen from behind stepping in under the deep eaves of a machiya, out of the rain. She is medium-sized in the frame and stands at the right; the wet street she has left runs off to the left third of the frame, empty and dark. Her oiled-paper umbrella is still open and tilted back as she passes the eave line. A curtain of fine water falls from the tiled eave just in front of her. Warm lantern light from inside the lattice falls across her shoulders.

A single woman in traditional Japanese dress, seen strictly from behind. Her face is never visible and never turns toward the camera. Her hands are covered by her kimono sleeves and are not rendered in detail. She wears a deep indigo kimono with a soft ash-rose obi tied in a flat drum knot at the back, and her hair is gathered in a low simple bun. She is completely still and quiet. No other people anywhere in the image.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 10. 軒の雨だれ・寄り

第二幕／音＝雨だれ

```
Close view of the edge of a tiled roof at night. Water gathers along the lip of each curved tile and falls in a broken line of separate drops, caught and lit warm from below by a lantern. The clay tiles are dark and slick, their curves and the moss in their joints clearly visible. Behind the falling water, the dark timber of the eave bracket. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 11. 立てかけた番傘・寄り

第二幕／音＝雨だれ

```
A traditional oiled-paper umbrella, closed and tied, leaning against a wooden lattice wall under the eaves. It is soaked; water runs down its bamboo shaft and beads along its folded paper, and a small pool has spread on the stone at its tip. Warm light from behind the lattice rakes across the wet paper and the grain of the timber. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 12. ★軒下から見る通り・引き

第二幕／音＝軒  ★人物

```
Shot from inside the shelter of the eaves, looking out at the rainy street. The back of a woman's head and shoulders fills the lower right of the frame, close to the camera and dark, as she stands watching the street. Beyond her the street is a soft amber blur of hanging lanterns doubled in the wet flagstones and veiled by haze. A line of falling water hangs from the eave across the top of the frame. The left third is dark eave timber, quiet and empty.

A single woman in traditional Japanese dress, seen strictly from behind. Her face is never visible and never turns toward the camera. Her hands are covered by her kimono sleeves and are not rendered in detail. She wears a deep indigo kimono with a soft ash-rose obi tied in a flat drum knot at the back, and her hair is gathered in a low simple bun. She is completely still and quiet. No other people anywhere in the image.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 13. ★格子戸が半分開く・後ろ姿

第二幕／音＝軒  ★人物

```
A wooden lattice sliding door standing half open, seen from outside under the eaves. Warm light pours from the opening onto the wet stone. A woman seen from behind is stepping through the gap; only her back and the flat drum knot of her obi are lit by the light from within, the rest of her in silhouette. Rain still beads on the dark timber of the door frame. The left third of the frame is dark wet stone, quiet and empty.

A single woman in traditional Japanese dress, seen strictly from behind. Her face is never visible and never turns toward the camera. Her hands are covered by her kimono sleeves and are not rendered in detail. She wears a deep indigo kimono with a soft ash-rose obi tied in a flat drum knot at the back, and her hair is gathered in a low simple bun. She is completely still and quiet. No other people anywhere in the image.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 14. 土間・引き

第三幕／音＝屋内

```
The earthen-floored entrance room of an old Japanese townhouse, seen from just inside. The packed earth floor is dark and slightly damp; a step up to a polished wooden edge runs across the middle of the frame. Warm light from a standing paper lamp fills the room. Through the half-open lattice door at the right, the blue-grey rainy street shows as a cool slot of light. The left third is plain dark plaster wall. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 15. 廊下の奥・引き

第三幕／音＝屋内

```
A narrow wooden corridor running deep into an old Japanese house. On the right, a run of paper screen doors glows faintly from the rooms behind them; on the left, dark plaster and a low window. The polished floorboards reflect the warm light in long soft bands. At the far end of the corridor stands a single small paper lamp, and beside it a window shows cool grey rainy light. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 16. ★座敷に座る後ろ姿・引き

第三幕／音＝屋内  ★人物

```
A tatami room seen from the back of the room. A woman sits on the tatami, seen from behind, small and placed slightly right of centre, facing an open paper screen door. Beyond the opening lies a small dark garden in the rain: wet stones, a low shrub, and a grey veil of falling water. A standing paper lamp at the right casts warm light across the tatami and up her back. The left third of the frame is quiet empty tatami and shadow.

A single woman in traditional Japanese dress, seen strictly from behind. Her face is never visible and never turns toward the camera. Her hands are covered by her kimono sleeves and are not rendered in detail. She wears a deep indigo kimono with a soft ash-rose obi tied in a flat drum knot at the back, and her hair is gathered in a low simple bun. She is completely still and quiet. No other people anywhere in the image.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 17. 障子紙に映る雨・寄り

第三幕／音＝屋内

```
Close view of a paper screen door lit from behind. The paper is a soft warm rectangle divided by its wooden grid; across it fall the blurred moving shadows of water running off the eave beyond, and the dark shape of a wet branch. The paper's fibres and the grain of the wooden grid are clearly visible. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 18. 開いた障子越しの庭・引き

第三幕／音＝屋内

```
Looking out from inside a dim tatami room through a fully opened paper screen at a small enclosed garden at night in the rain. The garden is a shallow, quiet arrangement of wet stepping stones, moss and one low pine, all glossy with water and lit faintly amber by a lamp behind the camera. The far wall of the garden fades into haze. The dark frame of the opening forms a quiet border down the left third. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 19. 手水鉢に降る雨・寄り

第三幕／音＝屋内

```
Close view of a stone water basin in the garden, brimming and overflowing. Rain strikes the surface continuously and fills it with small overlapping rings; a thin sheet of water slips over the basin's worn lip and darkens the stone below. Moss grows thick in the basin's hollows and a bamboo ladle rests across it. Warm lamplight from one side, cool blue-grey from the rainy garden on the other. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 20. ★行灯のそば・中景

第三幕／音＝細い雨  ★人物

```
A dim tatami room at night with a standing paper lamp as the clear subject, close to the camera at the right, its paper glowing warm and its wooden frame throwing a soft shadow. Deeper into the room and small in the frame, a woman sits on the tatami with her back to the camera, near the open screen through which the dark rainy garden shows as a cool grey slot. The lamp dominates; she is a quiet dark shape. The left third is empty tatami and shadow.

A single woman in traditional Japanese dress, seen strictly from behind. Her face is never visible and never turns toward the camera. Her hands are covered by her kimono sleeves and are not rendered in detail. She wears a deep indigo kimono with a soft ash-rose obi tied in a flat drum knot at the back, and her hair is gathered in a low simple bun. She is completely still and quiet. No other people anywhere in the image.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 21. 誰もいない座敷・引き

第三幕／音＝細い雨

```
The same tatami room, now empty. A flat floor cushion sits where someone had been; the standing paper lamp still burns at the right, and the paper screen is still open onto the dark rainy garden. Nothing moves. The woven texture of the tatami and the worn cloth edging of the mats are clearly visible in the low warm light. The left third of the frame is quiet empty tatami and shadow. No people anywhere.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```

## 22. 雨の庭・引き

第三幕／音＝細い雨

```
The small enclosed garden at the deepest part of the night, seen from the dark opening of the room. Only one small lamp still glows, far to the right, its light barely reaching the wet stones. The rain has thinned to a fine quiet fall and the stepping stones and moss hold a low sheen. Everything else is deep blue-grey — open, dim, and still full of visible detail. The left third is dark and empty. No people.

Photorealistic cinematic still, an old Japanese townhouse street at night in the rain. The only light comes from plain paper lanterns and the warm glow leaking through wooden lattice windows — amber, low and soft, fading to deep blue-grey in the distance. Exposed so that texture is clearly visible everywhere: wet stone, wood grain, roof tiles, paper, cloth. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas. The rain is shown only through its effects — mirror-wet stone, ripples in shallow puddles, water beading and running off edges, a soft veil of haze in the distance. No visible rain streaks or rain lines anywhere in the frame. No moon and no moonlight; the sky is overcast. No text, no signage, no lettering, no calligraphy of any kind — the paper lanterns are plain and unmarked. No modern objects: no power lines, no utility poles, no electric lamps, no vehicles, no air conditioners, no plastic, no road markings. Muted palette, fine film grain, 16:9 composition with generous quiet empty space in the left third for titles.
```
