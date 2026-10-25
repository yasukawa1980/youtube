# IRO20 生成プロンプト

内蔵image_genを使用。SunoとKlingの全文は同階層のJSONを正本とする。

- 音楽：[iro20_Sunoプロンプト.json](iro20_Sunoプロンプト.json)
- 動画：[iro20_Klingプロンプト.json](iro20_Klingプロンプト.json)

## 開始画像v01

```text
Use case: illustration-story. Create one polished 16:9 landscape starting-frame illustration for IRO Sounds IRO20, a quiet two-hour nighttime reading music video. Input image 1 is the FIRST character and rendering reference, NOT a composition to copy. Preserve the recognizable same adult woman around 30: slightly angular face, natural brown eyes, expressive eyebrows, chin-length wavy dark brown bob and small rectangular amber barrette at her left temple; muted teal overshirt over ivory T-shirt and navy trousers. NO bun or tied hair. Preserve the same LARGE adult golden retriever: broad light muzzle, heavy soft ears, honey coat, substantial paws, NOT a puppy.
New composition: a medium-wide seated-eye-level view diagonally along a deep upholstered window bench under an arched dark teal window, the woman at x=43%, dog at x=70%, close enough to feel companions. Woman sits comfortably on the bench with her legs tucked naturally below a plum throw, upper body visible, open book resting on her lap, hands resting simply on either edge. Eyes visibly OPEN looking softly toward the book, readable face in three-quarter view. Her body including head occupies about 48% of image height. Dog sleeps curled compactly on the SAME bench to her right; closed eyes, chin on forepaws, full body and full curled tail visibly inside the frame. Dog is large relative to her torso; its whole silhouette occupies roughly 23% of picture WIDTH, from x=59% to82%, leaving room to fit in a vertical 9:16 crop with margins. No furniture or objects obscure the dog. A deep PLUM muted purple upholstered cushion and throw distinguish this volume; teal is character clothing and window trim, warm honey lamp light contrasts indigo-blue hillside town outside. Autumn branches only outside. Scene is a modest lovingly used reading apartment, low record shelf below the window, a few books, one amber lamp toward far right; coherent perspective and generous lit shadows, quiet upper-left window area for later typography. No mug in her hands. No fine motor activity.
Match the reference's warm hand-drawn animated-feature illustration: expressive restrained contours, simplified painterly planes with selective fine gouache texture, sophisticated adult faces, appealing readable shapes, lived-in spatial depth. Keep faces gentle and mature, no large sparkling anime eyes, no glossy 3D or photography. Lift the darkest shadows enough to retain detail, avoid crushed blacks and blown lamp highlights. No lettering, logos, text, borders, watermarks or collage. Full bleed 16:9, high quality. This is a new scene of the SAME woman and SAME adult dog.
```

## 開始画像v02

```text
Use case: identity-preserve. Edit this IRO20 starting frame into a WIDER camera view of the SAME scene, same seated-eye-level angle, same woman, exact same face, dark brown bob and amber barrette, same large golden retriever, same plum window seat, same reading action, same hand-drawn movie style and lighting. The first version is too tightly framed for vertical video crops. Pull the camera back substantially: the entire dog including tail must fit within 23% of the landscape image width (not 38%), and woman-and-dog group within 48% width, staying at center-right. Make the room and window visible around them by expanding the field of view; do NOT shrink the dog relative to the woman. The large adult dog remains broad and heavy, sleeping curled beside her with complete tail and forepaws visible. Woman's face remains clearly recognizable and eyes visibly OPEN. Keep her hands simply resting on the open book. Add room depth at left and top, more window and a modest small bookshelf, not more people or animals. Maintain mature reference character, teal overshirt over ivory shirt, navy trousers under plum throw, calm adult taste. Lift deepest shadows slightly, no black foreground occluder. Main theme color is dusty PLUM purple rather than burgundy red. Full bleed 16:9, no text, no watermark.
```

## 開始画像v03

```text
Edit the provided starting frame ONLY for shadow exposure and tonal balance. Preserve the composition, geometry, exact woman face/bob/barrette/clothes, dog size and pose, hands, book, window, town and all objects. The image is too dark: deep shadows currently crush about 15.6 percent of pixels. Raise shadow and lower-midtones substantially, rendering the darkest shaded fabrics, corners and foliage in readable dark plum or warm blue-grey rather than near-black. Target fewer than 3 percent of pixels with luminance below 16/255. Keep nighttime mood and beautiful warm lamp/cool window contrast, preserve highlights below clipping, do not brighten sky into daytime. Treat this like a professional gentle lifted-black print grade with open luminous shadows, not added lamps, haze or a grey wash. Do not redraw or change camera framing. No text, 16:9.
```

## サムネ指示

開始画像v03を参照し、人物と犬を覆わない左上へ「読書BGM」「夜のページに、やさしい音」「室内楽チル｜2時間」。暗いPLUMの半透明地、主見出しは大きい生成り白、2行目は淡黄。絵・人物・犬・夜の照明を維持。16:9、追加ロゴなし。生成原本を1280×720へ縮小してJPG化。4回目の内蔵image_genで制作。


## 縦共通サムネ（内蔵image_gen・5回目）

参照：開始画像v03。編集原本を保存、開始画像は変更しない。

```text
Use case: identity-preserve. Create the shared vertical 9:16 Shorts cover for IRO20, based on this reference scene. Preserve exactly the adult woman with chin-length wavy dark brown bob, amber rectangular hair clip, teal overshirt, ivory tee; and the large adult golden retriever with broad pale muzzle and heavy ears. Same richly painted cinematic illustration and warm autumn reading nook, PLUM upholstery, teal arched window, blue night town lights. Recompose vertically to keep the woman reading on the left/center and the full large curled sleeping dog including tail on the right/lower center within safe margins. Woman's eyes naturally open looking down at book, not shut. Do not make dog a puppy. No bun hairstyle. Strong beautiful composition, not a stretched crop. Add exact bold cream Japanese headline in top safe area: 「読書BGM」. Below headline exact yellow subtitle 「音楽のショート試聴」. Below subtitle small cream text 「室内楽チル｜15秒」. Keep all text away from face and dog, on a naturally dark plum backdrop with enough contrast. Bottom safe area small unobtrusive title 「しおりを挟むには、まだ早い。」 and brand 「IRO SOUNDS」. Do not write 2時間. No timer, no extra logos or watermark. Portrait aspect ratio 9:16.
```

## 横サムネv02（内蔵image_gen・6回目）

参照：iro20_サムネ原本.png。追加は作品名の4行目。開始画像・動画用参照は変更しない。

```text
Use case: text-localization / precise text addition. Edit this existing IRO20 horizontal YouTube thumbnail, preserving the illustration and all three existing headline lines EXACTLY. Keep the adult bob-haired woman, amber hair clip, teal shirt, large full sleeping golden retriever, PLUM window bench, window night lights, lighting and composition unchanged. Keep existing text unchanged: 「読書BGM」, 「夜のページに、やさしい音」, 「室内楽チル｜2時間」. Add ONLY one small final line of cream Japanese sans-serif below the existing third line on the dark left background, left aligned with it: 「しおりを挟むには、まだ早い。」. This fourth line is much smaller than the genre line, approximately 30 pixels high at the supplied 1672-pixel width. Ensure exact punctuation and full text. Do not change font sizes, line breaks or colors of the existing three lines. No other additions. Preserve the 16:9 landscape shape, exposure and faces.
```
