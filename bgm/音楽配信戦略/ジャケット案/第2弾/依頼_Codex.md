# 第2弾ジャケット絵の依頼（2026-10-10 Claude→Codex）

前回（`../生成/生成記録.md`）と同じ進め方で、**文字なしの正方形の絵を作品ごとに3案**、Codex内蔵 image_gen で個別に新規生成し、
`bgm/音楽配信戦略/ジャケット案/第2弾/生成/` に `Whispers2_1.png`〜`Whispers2_3.png`、`IRO2_1.png`〜`IRO2_3.png` で保存してください。
生成原寸のまま（拡大・補正なし）。終わったら同じフォルダに `生成記録.md`（寸法・前回と同じ方法の平均輝度・文字領域の輝度・Whispersは Y<16 の割合・目視検品・渡した参照画像）を書いてください。
文字入れと3000px化はClaudeが後でやります。既存ファイルの上書き・移動・削除はしないでください。

## Whispers of Japan 第2弾「Falling Leaves at Night ／ 落葉の夜」
曲：葉の灯り（箏）・夜の並木（フェルトピアノ）・鈴の夜（鈴と鉢）。初回「Moonlit Ginkgo」（山の上の大銀杏1本と満月）と**同じ絵に見えないこと**が大事。今回は「銀杏並木の夜道」。
文字領域：上3分の1（`[x:0,W) × [y:0,H/3)`）。

```text
Photorealistic cinematic still, traditional Japanese scenery at night, exact square 1:1 composition.
A quiet old stone-paved path running straight away from the viewer between two rows of tall ginkgo
trees, like a temple approach, seen from standing eye height in the middle of the path. The trees'
crowns are full of clear golden-yellow fan-shaped leaves, and the stone path is thickly carpeted with
fallen golden ginkgo leaves, a few leaves drifting in the air. Far down the path, small and dim, the
dark silhouette of a simple wooden temple gate. A small bright half moon in the upper part of the sky,
slightly left of centre.
The only light source is the moon: cool blue-silver, low key — except that the ginkgo leaves keep
their own clear golden-yellow colour, softened by the moonlight, the one warm colour in the picture.
There are no lamps, lanterns or fires anywhere.
Exposed so that texture is clearly visible everywhere — bark, stone, every single fan-shaped leaf on
the ground. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High
dynamic range, rich texture even in the darkest areas.
Calm and completely static, no people, no animals, no text, no signage, no lettering of any kind.
Muted blue palette apart from the ginkgo gold, fine film grain.
Keep the entire upper third of the frame as calm, open, deep-blue night sky with only faint stars and
the moon — the tree crowns stay below it, no branches or leaves reaching into it — as a clean space
for titles. Square 1:1.
```
参照画像：渡さない（新規生成）。

## IRO Sounds 第2弾「今日はもう、ゆるくていい。／ Take It Easy Today」
曲：Slow Afternoon・Soft Strings・Steel Pan Breeze・Warm Organ・Evening Sax（IRO07の曲）。YouTubeのIRO07（PINK・Chill）と見た目をそろえる。
文字領域：左50%×上40%（前回と同じ）。

渡す参照画像（この順）：
1. `bgm/IRO/IRO07_今日はもうゆるくていい/Codex案/サムネ.png` — 場面・配色・人物・画風の主参照
2. `bgm/IRO/IRO07_今日はもうゆるくていい/Codex案/本編_桜色.png` — 同じ部屋・画風の補助参照
3. `bgm/IRO/IRO02_コーヒーが冷める前に/Codex案/サムネ.png` — 同一人物・画風の補助参照（カフェ場面・ピーチ配色はコピーしない）

```text
Use case: illustration-story
Asset type: text-free square 1:1 album cover artwork for IRO Sounds "Take It Easy Today"
Primary request: Place the same recognizable illustrated young woman from the provided IRO references
in her own cozy pink room in the late afternoon, relaxing on the floor against a bed with soft cushions,
listening to music on headphones next to a small record player.
Input images: identity, room and art-style references. Preserve the same young woman: high dark-brown
messy bun with a few loose strands, cream oversized chunky knit sweater, dark loose trousers, natural
proportions, back or three-quarter-back view, no detailed face, light beige over-ear headphones. Match
the same high-quality editorial 2D digital illustration, soft gouache texture, clean shapes, subtle
grain, cozy animation-film atmosphere, illustrated-not-photorealistic finish.
Scene/backdrop: A small modern bedroom with a large window and sheer pink curtains on the right, warm
golden late-afternoon light, a trailing pothos plant on a low wooden cabinet with a record player,
a fluffy rug, a soft blush blanket and pink cushions. Through the window only soft glowing sky and
clouds, no readable signs.
Subject: The woman sits on the rug in the lower right, leaning back against the bed and cushions,
legs loosely stretched out, completely relaxed, looking toward the window.
Composition/framing: Exact square 1:1 composition. Reserve the upper-left area (roughly the left 50%
of the upper 40%) as a calm copy-safe field in medium dusty rose pink, created by a softly shaded
plain interior wall. It must not be a bright window or a white wall. No person, plant, curtain,
furniture, highlight or detailed texture may intrude into that area. Place the woman, window, plant
and record player in the right half and lower half. Strong readable silhouette even at 60px.
Make it clearly a different picture from the YouTube thumbnail reference (different angle and
arrangement), while keeping the same room mood.
Lighting/mood: Lazy, unhurried late afternoon. Warm golden light from the window on the right,
soft pink bounce light, gentle cream highlights.
Color palette: PINK — dusty rose, blush pink, cream, warm gold, a little sage green from the plant.
Constraints: One person only. No text, letters, numbers, symbols, logo, watermark, UI, clock,
record label marks, screen or signage. No Japanese motifs or traditional architecture. No
photorealism. Preserve the same person and art style as the references.
```
