# IRO24「今年も、ツリーを出した。」コピー用プロンプト（2026-11-09 / Claude）

**★IRO Sounds（Whispers of Japan ではない）。** 設計は `iro/iro24_テーマ設計.md`。Suno は `iro/iro24_Sunoプロンプト.json`。

## 開始画像（Codex・内蔵の画像生成）

### 第1段：基準の部屋 S1 を2案（各1回）

参照画像1：`/Users/ryo/Desktop/BGM/IRO/Cafe/23_雨やどりのつもりだった/開始画像/iro23_S1_案2.png`（人物・犬・絵柄の第一参照。構図と店は真似しない）
保存先：`/Users/ryo/Desktop/BGM/IRO/Seasonal/24_今年もツリーを出した/開始画像/iro24_S1_案1.png`・`iro24_S1_案2.png`
検品：16未満の画素が3%以下、250以上が0.5%以下。犬は全身が見え、目を開けて伏せている。人物は目を開けて手元を見ている（こちらを見ない）。ツリーは飾り前で灯りなし。窓は四隅まで画面の中。題字を置く静かな面がある。

#### 共通（両案の先頭に付ける）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration for IRO Sounds IRO24, a three-hour Christmas jazz video in which the same cozy living room is shown from a winter afternoon into a snowy Christmas night. This first picture is the BASE scene: later pictures will be edits of it, so the room, the window, the tree, the sofa and the furniture must be clear, simple to keep consistent, and fully inside the frame. Input image 1 is the FIRST character and rendering reference, NOT a composition or a room to copy. Preserve the recognizable same adult woman around 30: slightly angular face, natural brown eyes, expressive eyebrows, chin-length wavy dark brown bob and small rectangular amber barrette at her left temple; muted teal overshirt over ivory T-shirt and navy trousers, with a soft oatmeal knitted cardigan worn open over the teal shirt so the teal stays clearly visible. NO bun or tied hair. Preserve the same LARGE adult golden retriever: broad light muzzle, heavy soft ears, honey coat, substantial paws, NOT a puppy.
Setting: a small, warm, lived-in apartment living room on a grey early-winter late afternoon in December. Cream plaster walls, light oak floor, a low cream sofa with a deep pine-green throw (#2F5D50), a small wooden side table, a low bookshelf, a floor lamp switched OFF, one large window with a plain wooden frame and soft cream curtains. Beside the window stands a real fir Christmas tree in a simple woven basket, about as tall as the window, still completely UNDECORATED: bare green branches, no lights, no ornaments, no star. On the floor in front of the tree sit two open cardboard boxes of ornaments and a coil of unlit string lights. The woman sits on the floor on a soft rug beside the boxes, taking a glass ornament out of tissue paper, looking down at it with her eyes visibly OPEN; readable face in soft three-quarter view, not looking at the viewer. The dog lies on the rug beside her, resting its head on its forepaws with eyes open and calm, full body and full tail visibly inside the frame, not hidden by any furniture; the dog's whole silhouette no wider than about 28% of the picture width. Outside the window: quiet rooftops and bare trees under a soft pale grey winter sky, no snow falling yet. The whole window, all four corners of the glass, must be inside the frame and not hidden by the tree. Soft diffuse daylight from the window, no golden backlight; cream, pine green and soft grey-blue tones; teal is only the character's clothing. No other people. No clock, no lettering, no sign text, no screens.
Leave one calm, plain surface in the UPPER part of the picture (the cream wall, painted as a real surface, not empty) where a title can be placed later; nothing important there.
Match the reference's warm hand-drawn animated-feature illustration: expressive restrained contours, simplified painterly planes with selective fine gouache texture, sophisticated adult faces, appealing readable shapes, lived-in spatial depth with coherent perspective. Keep faces gentle and mature, no large sparkling anime eyes, no glossy 3D or photography. Keep shadows detailed (no crushed blacks) and bright areas soft (no blown highlights). No lettering, logos, text, borders, watermarks or collage. Full bleed 16:9, high quality. This is a new scene of the SAME woman and SAME adult dog.
```

#### 案1：窓とツリーを右に

```text
Composition A — the living room seen from a low seated eye level, medium-wide, completely still camera. The window is in the RIGHT part of the picture (glass around x=58% to 88%, y=14% to 62%), and the bare fir tree stands just LEFT of the window (around x=44% to 60%), in front of the cream wall, not covering the glass. The woman sits on the rug in the lower middle (around x=34% to 52%), turned toward the tree; her head and upper body occupy about 35% of picture height. The dog lies on the rug to her LEFT, nearer to the camera (around x=10% to 36%), fully visible. The sofa is on the far left edge. The calm cream wall in the UPPER LEFT (around x=5% to 40%, y=6% to 26%) is the quiet area for the title.
```

#### 案2：窓とツリーを左に

```text
Composition B — the living room seen from a low seated eye level, medium-wide, completely still camera. The window is in the LEFT part of the picture (glass around x=10% to 40%, y=14% to 62%), and the bare fir tree stands just RIGHT of the window (around x=40% to 56%), in front of the cream wall, not covering the glass. The woman sits on the rug in the lower middle (around x=50% to 66%), turned toward the tree in a gentle three-quarter view; her head and upper body occupy about 35% of picture height. The dog lies on the rug to her RIGHT, nearer to the camera (around x=64% to 90%), fully visible. The sofa is on the far right edge. The calm cream wall in the UPPER RIGHT (around x=60% to 94%, y=6% to 26%) is the quiet area for the title.
```

### 第2段：編集3枚と別アングル2枚（第1段で選んだ案を基準に）

基準：第1段で選んだ `iro24_S1_案N.png`（以下 S1）
保存先：同じフォルダに `iro24_S2.png`・`iro24_S3.png`・`iro24_S4.png`・`iro24_S5.png`・`iro24_S6.png`
★雪・湯気・電球のまたたきは計算で重ねるので、**S2・S4・S6 の窓の外に降っている雪を描かない**（積もった雪はよい）。**どの絵にも湯気を描かない。**

#### 編集の共通（S2・S4・S6 の先頭に付ける）

```text
Edit input image 1 (the base living room scene). This is an EDIT, not a new picture: keep the camera, framing, perspective, the room, the window frame and its glass area, the curtains, the sofa, the side table, the bookshelf, the floor lamp, the rug, the fir tree's position, size and silhouette, and its basket at exactly the same pixel positions and the same sizes. Keep the same woman (wavy dark brown bob, amber barrette, teal overshirt, oatmeal cardigan, ivory T-shirt, navy trousers) and the same large adult golden retriever, the same painting style, the same rendering and the same level of detail. Change ONLY what is listed below. Do not add or remove any furniture or objects other than what is listed. Do not paint any falling snowflakes and do not paint any steam. No lettering, logos or text.
```

#### S2：雪が降り始める・飾りつけの途中

```text
Changes: It is a little later in the afternoon. The sky outside the window is a slightly darker soft blue-grey, and a thin first layer of snow lies on the rooftops and the window ledge outside (no falling flakes). The tree is now HALF decorated: a few simple glass ornaments in pine green, cream, muted red and soft gold hang on the lower and middle branches; the string lights are wound around the tree but switched OFF; no star yet. The woman now stands beside the tree in gentle profile, reaching up to hang one ornament on a branch, her eyes open and looking at the ornament. The ornament boxes stay on the floor. The dog now sleeps on the rug in the same position and size: eyes closed, chin on its forepaws. Soft grey daylight as before; the floor lamp is still off.
```

#### S4：夜・ツリーに灯り

```text
Changes: It is now night. Outside the window the sky is deep blue, the rooftops are covered in soft snow, and a few warm windows glow in the distance (no falling flakes). The tree is now FULLY decorated with the same simple ornaments and a small plain star on top, and its string lights are ON: many small warm-white bulbs, each a clearly separate small point of light, glowing softly — not a blurry glare. The floor lamp is now ON with a soft warm glow, so the room is cozy but NOT golden: the walls stay cream, the shadows stay soft blue-grey and pine green, faces and the dog remain clearly readable. The ornament boxes are gone. The woman now sits on the rug leaning back against the front of the sofa, reading an open book in her lap with her eyes open, one hand resting on the dog's head. The dog sleeps with its chin on her knee or close beside her on the rug, eyes closed, the same size as before and fully visible. A plain cream mug sits on the small side table.
```

#### S6：深夜・灯りだけ

```text
Changes: It is now late at night. Outside the window the sky is very deep navy, everything is covered in still white snow, the distant windows are dark (no falling flakes). The floor lamp is OFF. The ONLY light in the room is the fully decorated tree with its small warm-white bulbs ON, each a separate small point of light, plus a faint cool moonlight from the window, so the room is dim and calm but still readable: walls and floor softly visible in muted green-blue and cream, no crushed blacks. The woman now sits on the sofa wrapped in the pine-green throw blanket, a plain cream mug held in both hands, looking out of the window at the snow with her eyes open and a peaceful expression. The dog sleeps on the rug at the foot of the sofa, eyes closed, chin on its forepaws, fully visible, the same size as before.
```

#### S3：別アングル・手元の寄り（新しい絵）

参照画像1：S1、参照画像2：S4（部屋の色と飾りの色を合わせる）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration for IRO Sounds IRO24, matching the painting style, colors and objects of input images 1 and 2 exactly (they are the same living room). A close, calm view from above at a slight angle of the rug in front of the Christmas tree at dusk: a small round wooden tray with a plain cream ceramic mug of hot cocoa (no steam, no marshmallows piled up), an open cardboard box of simple glass ornaments in pine green, cream, muted red and soft gold nested in tissue paper, a loose coil of cream ribbon and a pair of small scissors. The woman's two hands only (no face), in the sleeves of the oatmeal knitted cardigan with a little teal cuff showing, gently holding one glass ornament by its loop. The lower branches of the tree enter the upper edge, with a few unlit bulbs. Soft cool window daylight with a little warm light from the room. Keep detail in the shadows and soft highlights. Leave the UPPER LEFT area calm (rug and soft shadow) for a title. Warm hand-drawn animated-feature illustration with selective fine gouache texture, no glossy 3D or photography. No lettering, logos, text, borders or watermarks. Full bleed 16:9.
```

#### S5：別アングル・外から窓越しの夜（新しい絵）

参照画像1：S4（窓・ツリー・人物と犬を合わせる）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration for IRO Sounds IRO24, matching the painting style, the woman, the golden retriever and the decorated Christmas tree of input image 1 exactly. Now seen from OUTSIDE at night: a quiet snowy residential street, looking at the same apartment window from across the street at a slightly low angle, completely still camera. The warm lit window is in the RIGHT half of the picture (around x=52% to 84%); through the glass we see the decorated tree with its small warm-white bulbs and, small and readable, the woman sitting on the rug reading with the large golden retriever sleeping beside her. Soft snow lies on the window ledge, the railings, a parked bicycle and the street; the sidewalk reflects the window light. The surrounding wall of the building is soft plaster in muted cream-grey; the night sky is deep blue with no stars painted (no falling snowflakes painted). Cool blue night tones with the warm window as the one gentle accent — not golden overall, shadows detailed, no crushed blacks. Leave the deep blue sky in the UPPER LEFT (around x=5% to 45%, y=6% to 28%) calm for a title. Warm hand-drawn animated-feature illustration with selective fine gouache texture, no glossy 3D or photography. No lettering, logos, signs, text, borders or watermarks. Full bleed 16:9.
```
