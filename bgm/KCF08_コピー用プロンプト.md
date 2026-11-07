# KCF08「囲炉裏端」コピー用プロンプト（2026-11-07 / Claude）

設計は `bgm/KCF08_テーマ設計.md`。巻の設定は `bgm/volumes/kcf08.yaml`。

## Suno（ピアノ独奏・6種×8テイク）

- Style 欄にそのまま貼る。**各プロンプト4回生成（1回2曲）＝8テイク**。保存名は `kcf08_A-1` 〜 `kcf08_F-8`
- **長さはカスタム3:30**（スライダーに JS で `focus()` → 実キー ArrowRight）。Auto や 3:00 にしない
- 書き出し先は **`/Volumes/ESD-02/Suno書き出し/KCF08_48曲/`**（wav は `wav/`）
- JS 版は `bgm/KCF08_囲炉裏端/_suno_prompts.js`（中身は同じ。このファイルから生成）
- 禁句（`short` `brief` `staccato` `detached` `stop` `cut off` `wide silences` `walking` `Japanese` `pentatonic` `irori`）が無いことを生成時に機械で確かめた

### A — 間奏曲（G♭ major）（974字）

```
Classical solo piano in G flat major, 60 BPM, for solo acoustic grand piano alone — no strings, no bass, no drums, no guitar, no synth, no pad, no koto, no flute. A warm, quiet intermezzo: soft, rounded chords in the middle of the keyboard, with the melody sung gently in an inner voice and passed between the hands, unhurried, every phrase rounded and allowed to rest before the next. Deep, mellow and comforting, like sitting close to a low charcoal fire in an old wooden room on a cold, clear early-winter day. In the manner of a late nineteenth-century piano intermezzo, never jazz.
Recorded close in a small wooden room, a little natural room sound, no long reverb.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For working, reading and studying in a quiet cafe.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### B — サラバンド（D minor→F major）（963字）

```
Classical solo piano in D minor, 58 BPM, 3/4 time, for solo acoustic grand piano alone — no strings, no bass, no drums, no guitar, no synth, no pad, no koto, no flute. A slow, dignified sarabande: calm chords with a gentle weight on the second beat of each bar and a simple, noble melody above, moving now and then into the warmth of F major, never gloomy and never dramatic. Still and steady, like pale winter sunlight falling through a paper screen onto dark polished wooden boards. Like a baroque sarabande played softly and legato on a modern piano. Never jazz, no swing.
Recorded close in a small wooden room, a little natural room sound, no long reverb.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For working, reading and studying in a quiet cafe.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### C — 牧歌（F major）（925字）

```
Classical solo piano in F major, 56 BPM, 6/8 time, for solo acoustic grand piano alone — no strings, no bass, no drums, no guitar, no synth, no pad, no koto, no flute. A gentle pastorale: a soft, sustained open fifth held low in the bass like a quiet drone, and above it a plain, hymn-like tune in the right hand that wanders calmly and returns home, legato and tender. Fresh and peaceful, like a frosty garden on an early-winter morning turning bright in the first sun. In the manner of a nineteenth-century piano miniature, never jazz.
Recorded close in a small wooden room, a little natural room sound, no long reverb.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For working, reading and studying in a quiet cafe.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### D — 炉辺の歌（B♭ major）（964字）

```
Classical solo piano in B flat major, 69 BPM, for solo acoustic grand piano alone — no strings, no bass, no drums, no guitar, no synth, no pad, no koto, no flute. A tender fireside song: a warm, story-telling melody in the middle register over a slow, gently moving bass, like an old song remembered and told quietly to someone beside you, every phrase breathing and finishing before the next begins. Warm and content, like the glow of embers and steam rising from an iron kettle on a quiet early-winter afternoon. In the manner of a nineteenth-century piano song, never jazz.
Recorded close in a small wooden room, a little natural room sound, no long reverb.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For working, reading and studying in a quiet cafe.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### E — 初冬のうた（B minor→D major）（953字）

```
Classical solo piano in B minor, 62 BPM, for solo acoustic grand piano alone — no strings, no bass, no drums, no guitar, no synth, no pad, no koto, no flute. A slow, lyrical piece: the left hand sings the melody low in the tenor register, like a cello on the piano, while the right hand answers with soft, high, quiet chords; a little wistful, then opening warmly into D major and back, never sad or dramatic. Like the clear stillness of the first cold days of winter, cold outside and warm within. In the manner of a nineteenth-century piano miniature, never jazz.
Recorded close in a small wooden room, a little natural room sound, no long reverb.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For working, reading and studying in a quiet cafe.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

### F — 高音のきらめく小品（B major）（918字）

```
Classical solo piano in B major, 88 BPM, for solo acoustic grand piano alone — no strings, no bass, no drums, no guitar, no synth, no pad, no koto, no flute. A bright, delicate little piece in the upper register of the piano: a clear, sparkling melody of gently flowing notes over a light, even accompaniment in the middle, graceful and quietly cheerful, never loud, smooth and legato. Like winter sunlight glinting on frost in a garden on a clear, still morning. In the manner of a nineteenth-century piano miniature, never jazz.
Recorded close in a small wooden room, a little natural room sound, no long reverb.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For working, reading and studying in a quiet cafe.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

---

## 画像（4場面＋サムネ・合成済みの全文）

- 1枚ずつ、コードブロックの中身をそのまま貼る。共通の末尾（THE INTERIOR SIDE IS ALSO LIT を含む）は合成済み
- 保存名は `kcf08_01.png` 〜 `kcf08_05.png`。受け取りは `bgm/KCF08_囲炉裏端_画像/` → 作業先 `画像/`
- 届いたら：16未満の割合（潰れ）／9:16 に切った題字帯の明るさ／5枚の構図の相関（KCF04 は 01と04が0.945）／四隅の署名を等倍で

### 01 — 炉の間の全景

```
The irori room of a Japanese folk-house cafe in the late morning of a clear early-winter day, seen from a slightly raised viewpoint in one corner of the room, looking diagonally across the square sunken hearth in the centre of the polished wooden floor. A black iron kettle hangs over the glowing charcoal from the pot hook, a thin wisp of steam rising. Flat zabuton cushions sit on three sides of the hearth, and on the wide wooden hearth frame are two yunomi teacups and a white cup and saucer. Behind, a long row of paper shoji screens glows evenly with winter sunlight, and one is slid open to show a sliver of frosty garden and blue sky. Sunlight from a high window falls in a soft slanting shaft onto the floorboards. Honey-brown polished floor, cream shoji, ochre clay wall, deep brown smoke-darkened beams, and the one small warm orange of the charcoal. The brightest thing is the glowing row of shoji; the second brightest is the sunlit floor around the hearth.

Oil painting on canvas: thick impasto in the lit areas with visible brush and palette-knife marks, thin scumbled paint in the shadows, clear pale early-winter daylight from outside and the small warm glow of charcoal inside, calm and unhurried. Painterly, clearly not a photograph. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. No people, no figures, no animals. No text, no signature, no seal stamp, no lettering of any kind. Do not place any mark, monogram or initials in any corner of the image. Any noren curtain, signboard or paper lantern is completely plain, with no characters, no crest and no writing. No modern objects: no power lines, no electric appliances, no lamps, no plastic, no computers, no printed signs or labels. This is a small JAPANESE cafe inside an old wooden folk house (kominka) on a cold, clear, sunny day in early winter: a raised room with polished wooden floorboards and a square sunken irori hearth cut into the floor, a wide dark wooden hearth frame, fine grey ash with a low bed of glowing charcoal, a black cast-iron kettle (tetsubin) hanging over it from a bamboo-and-wood pot hook (jizai-kagi) with a wooden crossbar carved like a fish, heavy smoke-darkened beams and posts, paper shoji screens, earthen clay walls, flat zabuton cushions around the hearth, plain ceramic yunomi teacups or a white cup and saucer. The fire is ONLY a low bed of glowing charcoal in the ash: no tall flames, no blazing logs, no smoke filling the room. The early-winter colour comes ONLY from these: white frost on the moss and the garden, red senryo berries, white and yellow narcissus (suisen) in a plain vase, a few mandarin oranges (mikan) in a small basket, and a clear blue winter sky. No snow anywhere. NO persimmons and no dried persimmons. No sazanka camellia, no nanten, no yuzu. No autumn maples, no pampas grass. No wood stove, no hibachi brazier. Absolutely no Western cafe or cottage look: no fireplace with a mantelpiece, no log cabin or alpine chalet, no leather armchairs or sofas, no Persian rugs, no wrought-iron or wicker furniture, no brick, no stained glass, no lace curtains, no Christmas decoration. THE INTERIOR SIDE IS ALSO LIT: the room in front of and beside any window or screen is raised and open, never a dark silhouette against a bright opening; daylight bounces off the polished floorboards, the paper screens and the clay walls onto the hearth, the kettle and the objects in the foreground so they keep their colour and texture; the smoke-darkened beams still show their wood grain. Each picture in this set is seen from a clearly different viewpoint; do not repeat the composition of another scene. Wide 16:9 landscape. Exposed so that texture is clearly visible everywhere. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas.

Output exactly 1920 x 1080 pixels, landscape 16:9. Single full-frame image. UNSIGNED painting. Every corner must contain only natural scene paint strokes, absolutely no cursive signature-like strokes.
```

### 02 — 炉縁の手元

```
A close, low view at the height of the hearth frame of the irori in a Japanese folk-house cafe, on a clear early-winter afternoon. In the foreground, the wide dark wooden hearth frame holds a white cup and saucer with steam rising, a small plate with a plain baked sweet, and a little basket of mikan oranges. In the middle, the round black iron kettle hangs from the bamboo pot hook over a low bed of glowing charcoal in soft grey ash, its curved side catching the window light, steam curling from its spout. In the softly blurred background, a paper shoji screen glows bright and a plain ceramic vase of white and yellow narcissus stands on a low wooden shelf. Daylight from the shoji on the left falls across the kettle, the cup and the oranges. Warm, close and intimate. The brightest thing is the glowing shoji behind; the cup, the oranges and the kettle in front are clearly lit and keep their colour.

Oil painting on canvas: thick impasto in the lit areas with visible brush and palette-knife marks, thin scumbled paint in the shadows, clear pale early-winter daylight from outside and the small warm glow of charcoal inside, calm and unhurried. Painterly, clearly not a photograph. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. No people, no figures, no animals. No text, no signature, no seal stamp, no lettering of any kind. Do not place any mark, monogram or initials in any corner of the image. Any noren curtain, signboard or paper lantern is completely plain, with no characters, no crest and no writing. No modern objects: no power lines, no electric appliances, no lamps, no plastic, no computers, no printed signs or labels. This is a small JAPANESE cafe inside an old wooden folk house (kominka) on a cold, clear, sunny day in early winter: a raised room with polished wooden floorboards and a square sunken irori hearth cut into the floor, a wide dark wooden hearth frame, fine grey ash with a low bed of glowing charcoal, a black cast-iron kettle (tetsubin) hanging over it from a bamboo-and-wood pot hook (jizai-kagi) with a wooden crossbar carved like a fish, heavy smoke-darkened beams and posts, paper shoji screens, earthen clay walls, flat zabuton cushions around the hearth, plain ceramic yunomi teacups or a white cup and saucer. The fire is ONLY a low bed of glowing charcoal in the ash: no tall flames, no blazing logs, no smoke filling the room. The early-winter colour comes ONLY from these: white frost on the moss and the garden, red senryo berries, white and yellow narcissus (suisen) in a plain vase, a few mandarin oranges (mikan) in a small basket, and a clear blue winter sky. No snow anywhere. NO persimmons and no dried persimmons. No sazanka camellia, no nanten, no yuzu. No autumn maples, no pampas grass. No wood stove, no hibachi brazier. Absolutely no Western cafe or cottage look: no fireplace with a mantelpiece, no log cabin or alpine chalet, no leather armchairs or sofas, no Persian rugs, no wrought-iron or wicker furniture, no brick, no stained glass, no lace curtains, no Christmas decoration. THE INTERIOR SIDE IS ALSO LIT: the room in front of and beside any window or screen is raised and open, never a dark silhouette against a bright opening; daylight bounces off the polished floorboards, the paper screens and the clay walls onto the hearth, the kettle and the objects in the foreground so they keep their colour and texture; the smoke-darkened beams still show their wood grain. Each picture in this set is seen from a clearly different viewpoint; do not repeat the composition of another scene. Wide 16:9 landscape. Exposed so that texture is clearly visible everywhere. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas.

Output exactly 1920 x 1080 pixels, landscape 16:9. Single full-frame image. UNSIGNED painting. Every corner must contain only natural scene paint strokes, absolutely no cursive signature-like strokes.
```

### 03 — 霜晴れの庭から見た母屋

★屋外。いちばん明るい絵＝ショートの安全牌。

```
Outdoors, in the frosty garden of an old Japanese folk house that is now a quiet cafe, late in the morning on a clear, cold early-winter day, looking at the front of the house from the garden. A deep thatched roof with a thin wisp of smoke rising from the smoke vent at its gable, a long wooden engawa veranda in full sun, and glass-paned wooden sliding doors along it, two of them slid open so that the warm irori room inside can be glimpsed, lit by the sunlight, with the black kettle hanging over the hearth. In the foreground, moss and stepping stones silvered with white frost, a low clump of red senryo berries beside a weathered stone, and bare winter branches against a deep blue sky. Crisp, bright and still. This is the brightest picture of the set: sunlit thatch, sunlit veranda boards, white frost and blue sky; the open room inside is lit too, never a black hole.

Oil painting on canvas: thick impasto in the lit areas with visible brush and palette-knife marks, thin scumbled paint in the shadows, clear pale early-winter daylight from outside and the small warm glow of charcoal inside, calm and unhurried. Painterly, clearly not a photograph. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. No people, no figures, no animals. No text, no signature, no seal stamp, no lettering of any kind. Do not place any mark, monogram or initials in any corner of the image. Any noren curtain, signboard or paper lantern is completely plain, with no characters, no crest and no writing. No modern objects: no power lines, no electric appliances, no lamps, no plastic, no computers, no printed signs or labels. This is a small JAPANESE cafe inside an old wooden folk house (kominka) on a cold, clear, sunny day in early winter: a raised room with polished wooden floorboards and a square sunken irori hearth cut into the floor, a wide dark wooden hearth frame, fine grey ash with a low bed of glowing charcoal, a black cast-iron kettle (tetsubin) hanging over it from a bamboo-and-wood pot hook (jizai-kagi) with a wooden crossbar carved like a fish, heavy smoke-darkened beams and posts, paper shoji screens, earthen clay walls, flat zabuton cushions around the hearth, plain ceramic yunomi teacups or a white cup and saucer. The fire is ONLY a low bed of glowing charcoal in the ash: no tall flames, no blazing logs, no smoke filling the room. The early-winter colour comes ONLY from these: white frost on the moss and the garden, red senryo berries, white and yellow narcissus (suisen) in a plain vase, a few mandarin oranges (mikan) in a small basket, and a clear blue winter sky. No snow anywhere. NO persimmons and no dried persimmons. No sazanka camellia, no nanten, no yuzu. No autumn maples, no pampas grass. No wood stove, no hibachi brazier. Absolutely no Western cafe or cottage look: no fireplace with a mantelpiece, no log cabin or alpine chalet, no leather armchairs or sofas, no Persian rugs, no wrought-iron or wicker furniture, no brick, no stained glass, no lace curtains, no Christmas decoration. THE INTERIOR SIDE IS ALSO LIT: the room in front of and beside any window or screen is raised and open, never a dark silhouette against a bright opening; daylight bounces off the polished floorboards, the paper screens and the clay walls onto the hearth, the kettle and the objects in the foreground so they keep their colour and texture; the smoke-darkened beams still show their wood grain. Each picture in this set is seen from a clearly different viewpoint; do not repeat the composition of another scene. Wide 16:9 landscape. Exposed so that texture is clearly visible everywhere. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas.

Output exactly 1920 x 1080 pixels, landscape 16:9. Single full-frame image. UNSIGNED painting. Every corner must contain only natural scene paint strokes, absolutely no cursive signature-like strokes.
```

### 04 — 土間から見上げた炉の間

```
Standing low on the packed earth floor (doma) by the entrance of a Japanese folk-house cafe, on a clear early-winter afternoon, looking sideways and slightly up over the wide polished wooden step (agarikamachi) into the raised irori room. From this low angle the hearth is seen side-on at floor level: the black kettle on its pot hook, the glowing charcoal, zabuton cushions on the floorboards, and beyond them paper shoji screens glowing with sunlight. Sunlight pours in from the open entrance door behind the viewer and lies in a long warm patch across the earth floor and the edge of the wooden step. On the earth floor in the foreground stands a large plain ceramic water jar with a wooden lid and a wooden ladle. Pale earth floor, honey-coloured step, cream shoji, dark beams overhead. The brightest things are the sunlit patch on the earth floor and the glowing shoji; the hearth area between them is clearly lit by bounced light.

Oil painting on canvas: thick impasto in the lit areas with visible brush and palette-knife marks, thin scumbled paint in the shadows, clear pale early-winter daylight from outside and the small warm glow of charcoal inside, calm and unhurried. Painterly, clearly not a photograph. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. No people, no figures, no animals. No text, no signature, no seal stamp, no lettering of any kind. Do not place any mark, monogram or initials in any corner of the image. Any noren curtain, signboard or paper lantern is completely plain, with no characters, no crest and no writing. No modern objects: no power lines, no electric appliances, no lamps, no plastic, no computers, no printed signs or labels. This is a small JAPANESE cafe inside an old wooden folk house (kominka) on a cold, clear, sunny day in early winter: a raised room with polished wooden floorboards and a square sunken irori hearth cut into the floor, a wide dark wooden hearth frame, fine grey ash with a low bed of glowing charcoal, a black cast-iron kettle (tetsubin) hanging over it from a bamboo-and-wood pot hook (jizai-kagi) with a wooden crossbar carved like a fish, heavy smoke-darkened beams and posts, paper shoji screens, earthen clay walls, flat zabuton cushions around the hearth, plain ceramic yunomi teacups or a white cup and saucer. The fire is ONLY a low bed of glowing charcoal in the ash: no tall flames, no blazing logs, no smoke filling the room. The early-winter colour comes ONLY from these: white frost on the moss and the garden, red senryo berries, white and yellow narcissus (suisen) in a plain vase, a few mandarin oranges (mikan) in a small basket, and a clear blue winter sky. No snow anywhere. NO persimmons and no dried persimmons. No sazanka camellia, no nanten, no yuzu. No autumn maples, no pampas grass. No wood stove, no hibachi brazier. Absolutely no Western cafe or cottage look: no fireplace with a mantelpiece, no log cabin or alpine chalet, no leather armchairs or sofas, no Persian rugs, no wrought-iron or wicker furniture, no brick, no stained glass, no lace curtains, no Christmas decoration. THE INTERIOR SIDE IS ALSO LIT: the room in front of and beside any window or screen is raised and open, never a dark silhouette against a bright opening; daylight bounces off the polished floorboards, the paper screens and the clay walls onto the hearth, the kettle and the objects in the foreground so they keep their colour and texture; the smoke-darkened beams still show their wood grain. Each picture in this set is seen from a clearly different viewpoint; do not repeat the composition of another scene. Wide 16:9 landscape. Exposed so that texture is clearly visible everywhere. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas.

Output exactly 1920 x 1080 pixels, landscape 16:9. Single full-frame image. UNSIGNED painting. Every corner must contain only natural scene paint strokes, absolutely no cursive signature-like strokes.
```

### 05 — サムネ専用

★構図の指定がほかの4枚と違う。題字が左に乗る（幕は左端から1300pxに向けて薄れる）。
★★左3分の1を明るい障子・白い壁にしない。題字の地が明るくなりすぎる（KCF05は左22.1で地16/15＝最良）。本編には使わない。

```
The irori room of a Japanese folk-house cafe on a clear early-winter day, arranged so that the LEFT THIRD of the frame is simple and quiet and DARK, and the subject sits on the RIGHT. On the right two-thirds: the square sunken hearth with its wide wooden frame, a black iron kettle hanging from the bamboo pot hook with white steam rising, a low bed of glowing charcoal, flat zabuton cushions, and on the hearth frame a white cup and saucer and a small basket of mikan oranges; behind them a row of paper shoji screens glowing with winter sunlight, so that the picture is immediately readable as a warm, quiet Japanese cafe around an irori, even at thumbnail size. The LEFT THIRD is ONLY a broad smoke-darkened timber post and the dark earthen clay wall beside it, deep in shade, even and low in detail: no shoji, no window, no cup, no vase, no scroll, nothing to read, a calm DARK ground for title characters. Strong contrast between the lit hearth and shoji on the right and the dark timber and clay on the left.

Oil painting on canvas: thick impasto in the lit areas with visible brush and palette-knife marks, thin scumbled paint in the shadows, clear pale early-winter daylight from outside and the small warm glow of charcoal inside, calm and unhurried. Painterly, clearly not a photograph. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. No people, no figures, no animals. No text, no signature, no seal stamp, no lettering of any kind. Do not place any mark, monogram or initials in any corner of the image. Any noren curtain, signboard or paper lantern is completely plain, with no characters, no crest and no writing. No modern objects: no power lines, no electric appliances, no lamps, no plastic, no computers, no printed signs or labels. This is a small JAPANESE cafe inside an old wooden folk house (kominka) on a cold, clear, sunny day in early winter: a raised room with polished wooden floorboards and a square sunken irori hearth cut into the floor, a wide dark wooden hearth frame, fine grey ash with a low bed of glowing charcoal, a black cast-iron kettle (tetsubin) hanging over it from a bamboo-and-wood pot hook (jizai-kagi) with a wooden crossbar carved like a fish, heavy smoke-darkened beams and posts, paper shoji screens, earthen clay walls, flat zabuton cushions around the hearth, plain ceramic yunomi teacups or a white cup and saucer. The fire is ONLY a low bed of glowing charcoal in the ash: no tall flames, no blazing logs, no smoke filling the room. The early-winter colour comes ONLY from these: white frost on the moss and the garden, red senryo berries, white and yellow narcissus (suisen) in a plain vase, a few mandarin oranges (mikan) in a small basket, and a clear blue winter sky. No snow anywhere. NO persimmons and no dried persimmons. No sazanka camellia, no nanten, no yuzu. No autumn maples, no pampas grass. No wood stove, no hibachi brazier. Absolutely no Western cafe or cottage look: no fireplace with a mantelpiece, no log cabin or alpine chalet, no leather armchairs or sofas, no Persian rugs, no wrought-iron or wicker furniture, no brick, no stained glass, no lace curtains, no Christmas decoration. THE INTERIOR SIDE IS ALSO LIT: the room in front of and beside any window or screen is raised and open, never a dark silhouette against a bright opening; daylight bounces off the polished floorboards, the paper screens and the clay walls onto the hearth, the kettle and the objects in the foreground so they keep their colour and texture; the smoke-darkened beams still show their wood grain. Each picture in this set is seen from a clearly different viewpoint; do not repeat the composition of another scene. Wide 16:9 landscape. Exposed so that texture is clearly visible everywhere. Shadows are lifted and open, full of visible detail, nothing crushed to pure black. High dynamic range, rich texture even in the darkest areas.

Output exactly 1920 x 1080 pixels, landscape 16:9. Single full-frame image. UNSIGNED painting. Every corner must contain only natural scene paint strokes, absolutely no cursive signature-like strokes.
```
