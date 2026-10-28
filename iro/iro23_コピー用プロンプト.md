# IRO23「雨やどりの、つもりだった。」コピー用プロンプト（2026-10-28 / Claude）

**★IRO Sounds（Whispers of Japan ではない）。** 設計は `iro/iro23_テーマ設計.md`。Suno は `iro/iro23_Sunoプロンプト.json`。

## 開始画像（Codex・内蔵の画像生成）

### 第1段：基準の席 S1 を2案（各1回）

参照画像1：`/Users/ryo/Desktop/BGM/IRO/Study/22_日が暮れるまで集中する/開始画像/iro22_start_1920.png`（人物・犬・絵柄の第一参照。構図は真似しない）
保存先：`/Users/ryo/Desktop/BGM/IRO/Cafe/23_雨やどりのつもりだった/開始画像/iro23_S1_案1.png`・`iro23_S1_案2.png`
検品：16未満の画素が3%以下、250以上が0.5%以下。犬は全身が見え、目を開けて伏せている。人物は目を開けて手元を見ている（こちらを見ない）。マグはまだ無い。題字を置く静かな面がある。

#### 共通（両案の先頭に付ける）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration for IRO Sounds IRO23, a two-hour café music video in which the same café window seat is shown at different times from a rainy afternoon into the night. This first picture is the BASE scene: later pictures will be edits of it, so the room, window, table and furniture must be clear, simple to keep consistent, and fully inside the frame. Input image 1 is the FIRST character and rendering reference, NOT a composition to copy. Preserve the recognizable same adult woman around 30: slightly angular face, natural brown eyes, expressive eyebrows, chin-length wavy dark brown bob and small rectangular amber barrette at her left temple; muted teal overshirt over ivory T-shirt and navy trousers. NO bun or tied hair. Preserve the same LARGE adult golden retriever: broad light muzzle, heavy soft ears, honey coat, substantial paws, NOT a puppy.
Setting: a small, old, dog-friendly neighborhood café on a grey late-autumn afternoon, just as a light rain begins. Dark walnut wood, a few warm pendant lamps that are switched OFF, cream plaster walls, a shelf of cups and a few books, a small plant. She has just come in out of the rain and sits at a small two-person wooden table by a large window; her damp light raincoat hangs on the back of the other chair; a folded umbrella leans against the wall. She holds a small paper menu with no readable writing and looks down at it with her eyes visibly OPEN; readable face, not looking at the viewer. Nothing else on the table yet except a small glass of water — NO mug, NO cup, NO steam. The dog lies on the wooden floor beside her chair on a small MUTED MOCHA-BROWN mat (#7B5B45), resting its head on its forepaws with eyes open and calm, full body and full tail visibly inside the frame, not hidden by any furniture; the dog's whole silhouette no wider than about 28% of the picture width. Outside the window: a quiet wet street, soft grey sky, a few fine raindrops on the glass. Soft diffuse daylight from the window, no golden backlight; mocha-brown and cream tones with soft grey-blue shadows; teal is only the character's clothing. No other customers, no staff. No clock, no lettering, no sign text.
Leave one calm, plain surface in the UPPER part of the picture (a cream wall or the grey sky in the window, painted as a real surface, not empty) where a title can be placed later; nothing important there.
Match the reference's warm hand-drawn animated-feature illustration: expressive restrained contours, simplified painterly planes with selective fine gouache texture, sophisticated adult faces, appealing readable shapes, lived-in spatial depth with coherent perspective. Keep faces gentle and mature, no large sparkling anime eyes, no glossy 3D or photography. Keep shadows detailed (no crushed blacks) and bright areas soft (no blown highlights). No lettering, logos, text, borders, watermarks or collage. Full bleed 16:9, high quality. This is a new scene of the SAME woman and SAME adult dog.
```

#### 案1：窓を右に、斜め前から

```text
Composition A — the window seat seen from slightly in front, at seated eye level, medium-wide, completely still camera. The large window is on the RIGHT side of the picture; the small table stands against it. The woman sits on the LEFT side of the table (around x=38%), turned toward the window so her face is seen in a soft three-quarter view; her head and upper body occupy about 40% of picture height. The dog lies on the mocha mat on the floor in front of and slightly left of her chair (around x=12% to 38%), nearer to the camera, fully visible. The calm cream wall in the UPPER LEFT (around x=5% to 40%, y=6% to 28%) is the quiet area for the title.
```

#### 案2：窓を左に、真横から

```text
Composition B — the window seat seen exactly from the side at seated eye level, medium-wide, completely still camera. The large window fills the LEFT part of the picture; the small table stands against it. The woman sits on the RIGHT side of the table (around x=60%), seen in a gentle profile turned slightly toward the camera, facing left toward the window and the rainy street; her head and upper body occupy about 40% of picture height. The dog lies on the mocha mat on the floor at her feet, in the lower middle of the picture (around x=40% to 66%), nearer to the camera than the chair legs, fully visible. The soft grey sky in the UPPER part of the window (around x=6% to 40%, y=6% to 26%) is the quiet area for the title.
```

### 第2段：編集3枚と別アングル2枚（10/28 本人が**案2**を選択）

基準：`/Users/ryo/Desktop/BGM/IRO/Cafe/23_雨やどりのつもりだった/開始画像/iro23_S1_案2.png`（以下 S1）
保存先：同じフォルダに `iro23_S2.png`・`iro23_S3.png`・`iro23_S4.png`・`iro23_S5.png`・`iro23_S6.png`
★湯気は計算で重ねるので、**どの絵にも湯気を描かない**。

#### 編集の共通（S2・S4・S6 の先頭に付ける）

```text
Edit input image 1 (the base café scene). This is an EDIT, not a new picture: keep the camera, framing, perspective, the room, the window frames, the table, all chairs, the shelves, the lamps, the plants, the floor, the rug and the dog's mat at exactly the same pixel positions and the same sizes. Keep the same woman (wavy dark brown hair, amber barrette, teal overshirt, ivory T-shirt, navy trousers) and the same large adult golden retriever, the same painting style, the same rendering and the same level of detail. Change ONLY what is listed below. Do not add or remove any furniture, plants or objects other than what is listed. Do not paint any steam. No lettering, logos or text.
```

#### S2：雨が強まる

```text
Changes: The rain outside is now heavier: more raindrops and a few running streaks on the window glass, the street is wetter and greyer, the sky a slightly darker grey; the street lamps outside are still off or very faint. The menu is gone. The woman now sits a little more upright and holds a plain cream ceramic mug of coffee in both hands near her chest, resting her forearms on the table, looking out of the window at the rain with her eyes open and a soft, calm expression. The glass of water stays on the table. The dog now sleeps: eyes closed, chin on its forepaws, the same position and size on the mat. Inside light is the same soft grey daylight; the pendant lamps glow faintly as before.
```

#### S4：夕方・雨上がり、ランプが灯る

```text
Changes: The rain has stopped and it is early evening. Outside the window the clouds are breaking up and the low sky glows soft orange and pink behind the rooftops; the wet street reflects the sky; the street lamps outside are now on. Only a few raindrops remain on the glass. Inside, the pendant lamps and the table lamp on the right are now clearly lit with a warm amber glow, and the room is a little darker and warmer than before. The woman reads an open paperback book held in her left hand on the table, and her right hand hangs down beside her chair resting gently on the sleeping dog's head. The plain cream mug stands on the table near her. The dog sleeps with eyes closed, the same position and size on the mat.
```

#### S6：夜・閉店前

```text
Changes: It is night, close to closing time. Outside the window the sky is a deep blue-indigo, the street lamps glow warmly, the wet street holds long golden reflections, and a few fresh raindrops sit on the glass. Inside, the pendant lamps and the table lamp give a warm amber light and the corners of the room fall into soft, detailed shadow (no crushed blacks). The woman rests her cheek on one hand with her elbow on the table and looks out of the window at the night street with her eyes open, relaxed and content; the closed paperback lies on the table beside a second plain cream mug. The dog sleeps with eyes closed, the same position and size on the mat.
```

#### S3：手元の寄り（新しい絵・S1 を参照に）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration. Input image 1 is the reference for the café, the woman's clothing, the colours and the painting style; this is a NEW close-up of the same café table by the rainy window. Close view from just above the table at a gentle angle: the woman's hands only (no face), teal overshirt sleeves rolled to the forearm, an open paperback book on the dark walnut table with blank pale pages and no readable text, her left hand holding the book open and her right hand loosely around a plain cream ceramic mug of coffee. Beside it a small glass of water. Behind, slightly out of focus, the window glass with raindrops and the soft grey rainy street. Soft grey daylight from the window; mocha-brown and cream tones with soft grey-blue shadows. Do not paint any steam. Keep the mug fully visible with its top opening clear. Same warm hand-drawn animated-feature illustration style as the reference, simplified painterly planes with selective fine gouache texture, coherent perspective, detailed shadows, no blown highlights. No lettering, logos, text, borders, watermarks. Full bleed 16:9, high quality.
```

#### S5：店の外から窓越しの夜（新しい絵・S1 を参照に）

```text
Use case: illustration-story. Create one polished 16:9 landscape illustration. Input image 1 is the reference for the café interior, the woman, the dog, the colours and the painting style; this is a NEW view of the same small café from OUTSIDE at night after rain. The camera stands on the wet cobbled street at eye level, a little distance away, looking at the café's large window, completely still. Through the window: the warm amber-lit interior with the pendant lamps, the shelves and plants, and the woman at her small table in gentle profile, small in the picture, with the large golden retriever asleep on the floor beside her (visible through the lower window). The café front is dark walnut wood with an awning and a few potted plants; no sign, no lettering. The wet street in the foreground reflects the warm window light in long golden streaks; a street lamp glows; the night sky is deep blue-indigo with a few autumn leaves on the wet stones. Detailed shadows (no crushed blacks), soft highlights. Same warm hand-drawn animated-feature illustration style as the reference. No lettering, logos, text, signs, borders or watermarks. Full bleed 16:9, high quality.
```

## Suno

`iro/iro23_Sunoプロンプト.json` の `style` を Style 欄へ、`exclude` を除外欄へ。歌詞欄は空・Instrumental・長さはカスタムのスライダー240秒。
