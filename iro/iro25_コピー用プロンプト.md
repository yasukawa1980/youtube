# IRO25「雪が積もるまで、集中する。」コピー用プロンプト（2026-11-20 / Claude）

**★IRO Sounds（Whispers of Japan ではない）。** 設計は `iro/iro25_テーマ設計.md`。Suno は `iro/iro25_Sunoプロンプト.json`。

## 開始画像（Codex・内蔵の画像生成）

### 第1段：基準の部屋 S1 を2案（各1回）

参照画像1：`/Users/ryo/Desktop/BGM/IRO/Seasonal/24_今年もツリーを出した/開始画像/iro24_S1_案1.png`（人物・犬・絵柄の第一参照。構図と部屋は真似しない）
保存先：`/Users/ryo/Desktop/BGM/IRO/Study/25_雪が積もるまで集中する/開始画像/iro25_S1_案1.png`・`iro25_S1_案2.png`
検品：16未満の画素が3%以下、250以上が0.5%以下。犬は全身が見え、目を開けて伏せている。人物は目を**開けて**手元を見ている（こちらを見ない）。窓は四隅まで画面の中。右上にタイマーを置く静かな面がある。窓の外に降る雪・湯気・文字がない。

#### 共通（両案の先頭に付ける）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration for IRO Sounds IRO25, a three-hour Pomodoro study video in which the same small study room is shown from a grey winter afternoon into a quiet snowy night. This first picture is the BASE scene: later pictures will be edits of it, so the room, the window, the desk and the furniture must be clear, simple to keep consistent, and fully inside the frame. Input image 1 is the FIRST character and rendering reference, NOT a composition or a room to copy. Preserve the recognizable same adult woman around 30: slightly angular face, natural brown eyes, expressive eyebrows, chin-length wavy dark brown bob and small rectangular amber barrette at her left temple; muted teal overshirt over ivory T-shirt and navy trousers, with a soft oatmeal knitted cardigan worn open over the teal shirt so the teal stays clearly visible. NO bun or tied hair. Preserve the same LARGE adult golden retriever: broad light muzzle, heavy soft ears, honey coat, substantial paws, NOT a puppy.
Time and weather: a grey early-winter afternoon in December, an overcast pale sky, no snow falling yet and no snow on the ground or rooftops yet. On the desk: an open notebook with faint unreadable pencil lines, a closed textbook, a small stack of plain index cards held by a ring, a pencil case, and a plain cream ceramic mug (no steam). A small desk lamp switched OFF. The woman is studying, holding a pencil over the notebook, looking down at the page with her eyes clearly OPEN (visible irises, not closed, not sleepy); readable face in soft three-quarter view, not looking at the viewer. The dog lies close beside her, within arm's reach, head resting on its forepaws with eyes open and calm, full body and full tail visibly inside the frame; the dog's whole silhouette no wider than about 28% of the picture width.
Soft diffuse daylight from the window, no golden backlight; frosty grey-blue (#8FAFC4), cream and warm wood tones; teal is only the character's clothing. No other people. No clock, no calendar, no lettering, no sign text, no book titles, no screens, no phone.
Leave one calm, plain surface in the UPPER RIGHT of the picture (a real painted wall or ceiling surface, not empty space) where a large timer will be placed later; nothing important there, no shelves or frames on it.
Match the reference's warm hand-drawn animated-feature illustration: expressive restrained contours, simplified painterly planes with selective fine gouache texture, sophisticated adult faces, appealing readable shapes, lived-in spatial depth with coherent perspective. Keep faces gentle and mature, no large sparkling anime eyes, no glossy 3D or photography. Keep shadows detailed (no crushed blacks) and bright areas soft (no blown highlights). No lettering, logos, text, borders, watermarks or collage. Full bleed 16:9, high quality. This is a new scene of the SAME woman and SAME adult dog.
```

#### 案1：こたつで勉強

```text
Composition A — a small Japanese-style room with tatami mats and cream plaster walls, a low kotatsu table covered with a soft quilt in frosty grey-blue and cream. The camera sits on the tatami across the kotatsu, slightly lower than seated eye level, at a gentle diagonal, medium-wide, completely still. The woman sits at the kotatsu in the RIGHT part of the picture (around x=55% to 75%), her legs under the quilt, turned toward the left in a three-quarter view, writing in the notebook on the kotatsu top. The dog lies on the tatami at her LEFT, in the lower middle of the picture (around x=30% to 55%), its body half tucked under the edge of the kotatsu quilt, head and forepaws and tail outside the quilt and clearly visible. A low waist-high window with a plain wooden frame and clear glass panes (no shoji paper) is in the LEFT back of the room (glass around x=6% to 34%, y=18% to 55%), showing quiet tiled rooftops and a bare tree under a pale grey winter sky. A small wooden shelf with a few books and a potted plant stands below the window. The upper right is a plain cream plaster wall for the timer.
```

#### 案2：屋根裏の天窓の机

```text
Composition B — a cozy attic study room with a steeply sloping white-painted wooden ceiling. A wide skylight is set into the sloping ceiling in the upper middle (glass around x=36% to 62%, y=4% to 30%), and a small vertical window is in the right wall (glass around x=78% to 92%, y=24% to 58%); both show a pale grey winter sky and, through the small window, quiet rooftops. A simple light-oak desk stands directly under the skylight. The camera stands at the back of the room at seated eye level, at a gentle diagonal, medium-wide, completely still. The woman sits on a wooden chair at the desk in the LEFT third of the picture (around x=18% to 36%), turned toward the right in a three-quarter view, writing in the notebook; her face is clearly visible and her eyes clearly open. The dog lies curled on a soft round rug on the floor right beside her chair, to her RIGHT (around x=38% to 62%), close enough that she could touch its head, not far away across the room. The upper right is a plain area of the sloping painted ceiling (between the skylight and the small window, above the window) for the timer.
```

### 第2段：編集3枚と別アングル2枚（第1段で選んだ案を基準に）

基準：第1段で選んだ `iro25_S1_案N.png`（以下 S1）
保存先：同じフォルダに `iro25_S2.png`・`iro25_S3.png`・`iro25_S4.png`・`iro25_S5.png`・`iro25_S6.png`
★雪・湯気・ランプのゆらぎは計算で重ねるので、**S2・S4・S6 の窓の外に降っている雪を描かない**（積もった雪はよい）。**どの絵にも湯気を描かない。**
検品：S2・S4・S6 は S1 と部屋の位置のずれが2画素以内（輪郭の位相相関で Claude が測る）。暗部16未満が S4・S6 で5%以下。

#### 編集の共通（S2・S4・S6 の先頭に付ける）

```text
Edit input image 1 (the base study room scene). This is an EDIT, not a new picture: keep the camera, framing, perspective, the room, the walls and ceiling, the window frames and their glass areas, the desk (or kotatsu) and its position, the shelf, the lamp, the rug or tatami, and every piece of furniture at exactly the same pixel positions and the same sizes. Keep the plain timer surface in the upper right empty. Keep the same woman (wavy dark brown bob, amber barrette, teal overshirt, oatmeal cardigan, ivory T-shirt, navy trousers) and the same large adult golden retriever, the same painting style, the same rendering and the same level of detail. Change ONLY what is listed below. Do not add or remove any furniture or objects other than what is listed. Do not paint any falling snowflakes and do not paint any steam. No lettering, logos or text.
```

#### S2：雪が降り始める

```text
Changes: It is a little later in the afternoon. The sky outside the window is a slightly darker soft blue-grey, and a very thin first dusting of snow lies on the rooftops and the window ledge outside (no falling flakes). The woman is now writing in the notebook, seen in the same position, eyes open and looking down at the page. The dog is now ASLEEP in the same place: eyes closed, chin resting on its forepaws, body relaxed. Everything else unchanged.
```

#### S4：夕暮れ・ランプが灯る

```text
Changes: It is now early evening, just after sunset. Outside the window the sky is deep twilight blue, the rooftops are clearly white with snow, and a few warm windows glow in the distance (no falling flakes). The small desk lamp is now ON, giving a soft warm pool of light on the desk and on the woman's face and hands; the rest of the room is in calm cool blue shadow, still readable, no crushed blacks. The woman is now reading the open textbook, eyes open, with her other hand resting gently on the sleeping dog's head beside her. The dog is asleep (eyes closed, chin on forepaws). Everything else unchanged.
```

#### S6：夜・雪が積もって静か

```text
Changes: It is now night. Outside the window the sky is very deep navy, everything is covered in thick still white snow, the distant windows are mostly dark (no falling flakes). The desk lamp is ON with the same warm pool of light; the rest of the room is dim and calm but every shape is still readable (no crushed blacks). The woman rests her cheek on one hand and looks down at an open workbook with her eyes open, calm and focused, not sleepy. A second plain cream mug sits beside the first. The dog is still asleep in the same place. Everything else unchanged.
```

#### S3：別アングル・手元の寄り（新しい絵）

参照画像1：S1、参照画像2：S4（部屋の色と机の物を合わせる）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration for IRO Sounds IRO25, matching the painting style, colors and desk objects of input images 1 and 2 exactly (they are the same study room). A close, calm view from slightly above of the desk surface in late afternoon: the open notebook with faint unreadable pencil lines, the ring of plain index cards, a pencil, the same plain cream ceramic mug (no steam), and the woman's two hands — one holding the index cards, one resting on the notebook — wearing the teal shirt cuffs under the oatmeal cardigan sleeves. Her face is NOT in the picture. In the soft-focus background, the window shows a grey-blue sky with a thin dusting of snow on the ledge (no falling flakes). Leave a calm plain area in the upper right (the soft out-of-focus wall) for a timer. Soft diffuse window light, frosty grey-blue, cream and warm wood tones. No steam, no lettering, no readable text, no logos, no screens. Keep shadows detailed and highlights soft. Full bleed 16:9, high quality.
```

#### S5：別アングル・犬の寄り（新しい絵）

参照画像1：S4（犬・部屋・灯りを合わせる）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration for IRO Sounds IRO25, matching the painting style, the large adult golden retriever and the study room of input image 1 exactly. A close, low view at floor level of the dog sleeping curled up beside the desk in the early evening: eyes closed, chin on its forepaws, honey coat softly lit by the warm desk lamp from above, broad light muzzle, heavy soft ears, substantial paws, the whole dog including the tail inside the frame and filling about half of the picture width, placed slightly right of center. In the soft-focus background on the left: the woman's knees in navy trousers and the edge of the desk (her face not shown), and a part of the window with snow-covered rooftops under a deep twilight blue sky (no falling flakes). Leave a calm plain area in the upper right (soft out-of-focus wall) for a timer. Warm lamp light and cool blue shadow, no crushed blacks. No steam, no lettering, no logos. Full bleed 16:9, high quality. NOT a puppy.
```
