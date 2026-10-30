# IRO小さな物語01 画像生成プロンプト

内蔵image_genを使用。6回で6場面を制作。API CLIは使用していない。

参照の流れ：S1はIRO共通キャラクター刷新の案1、S2はS1、S3はS2、S4はS1、S5はS1とS3、S6はS5。各原画像はMac/SSDの本作「開始画像」フォルダに保存。

## S1

```text
Use case: illustration-story. Asset: first shot of a quiet 90-second IRO SOUNDS illustrated film, 16:9 landscape. Reference image is ONLY the character identities and hand-painted cinematic illustration style. Create a NEW scene in the SAME cozy home during a softly rainy autumn AFTERNOON (not night). Adult woman around 30, chin-length wavy dark-brown bob, small rectangular amber hairclip, natural brown eyes, teal overshirt over cream tee, navy trousers, oatmeal socks. Large mature golden retriever with pale broad muzzle and large paws, never a puppy. Wide cinematic room view: tall teal arched window left with raindrops and gray-blue autumn garden outside; rust armchair right, woman seated comfortably in it reading a dark green hardcover book; dog asleep curled on cream rug at her feet, whole dog visible. Small wooden table and cream ceramic mug, bookcase. Soft cool daylight with warm wood and restrained amber lamp. Calm grown-up expressions, rich brush texture, sophisticated film still, readable medium exposure. No text, no borders, no watermark, no collage. Keep room uncluttered, physically plausible anatomy. Render a single full-bleed 16:9 frame at high resolution.
```

## S2

```text
Use case: identity-preserve / illustration-story. Edit the supplied film frame into the next moment of the SAME scene. Keep the woman identity, her teal overshirt, cream tee, navy trousers, amber hairclip, rust armchair, all furniture and arched window positions, mature golden retriever size and coat, painting style and frame unchanged. Change only: the dog is now awake, lifting its head slightly and looking toward the woman with calm expectant eyes. The woman has paused her reading, finger keeping her place in the open dark green book, looking down toward the dog with a small affectionate smile. Outside the rain has stopped: keep beads on window but brighter soft gray daylight and a little clearing blue sky. No dramatic sunset. Single full bleed 16:9 landscape frame, no text. Natural anatomically correct hands and dog.
```

## S3

```text
Use case: illustration-story. Next shot of the same IRO film. The input is a visual reference for exact dog identity, home design, painterly style and lighting, not a layout to copy. New low eye-level medium-wide shot inside the entrance hall of that same cozy house. The SAME very large mature golden retriever, broad pale muzzle, honey coat, large paws, sits patiently on warm wood floor beside a teal painted front door. Full dog visible in right half, looking up toward a simple tan leather walking leash hanging from a brass hook LEFT of the door. Leash has clearly visible loop handle and a small metal clip at bottom, hangs loose, NOT attached to dog yet. A small bench with a pair of brown ankle boots and folded umbrella, cream wall, small edge of rust living-room armchair distant through doorway. Soft post-rain afternoon daylight through door glass, restrained warm lamp. No person in frame. Quiet expectant mood, natural anatomy, hand-painted cinematic realism, match reference quality. 16:9 landscape, no words, no logo, no border.
```

## S4

```text
Use case: illustration-story. New insert shot for the same quiet IRO SOUNDS film. Use supplied reference for exact style, color, wardrobe and objects. Close view of the small wooden side table beside the rust armchair. The dark green cloth hardcover book is now CLOSED and resting on the table, a narrow muted ochre ribbon bookmark clearly protrudes 5 cm from the bottom edge. The woman's single relaxed anatomically correct hand with FIVE natural fingers rests gently flat on the closed cover; teal shirt cuff on forearm enters from right, no other hands. Cream mug with understated green leaf decoration sits behind book at right. Softly blurred teal window and wet autumn leaves at left; warm rust chair at right background. Soft afternoon light after rain, rich hand-painted cinematic illustration, quiet tactile detail, no readable words on book, no title, no border, no watermark. Landscape 16:9 full bleed. The book and ribbon tell us she saved her place and decided to go outside.
```

## S5

```text
Use case: illustration-story. Create the transition shot of this quiet film, exactly same characters as reference 1 and same entrance hall as reference 2. Full 16:9 frame from inside home looking toward OPEN teal front door. Adult woman with chin-length wavy dark brown bob and small rectangular amber hairclip, teal overshirt over cream tee, navy trousers, now brown ankle boots, stands at doorway seen in three-quarter rear view. She holds a simple tan leather leash in lowered right hand; leash runs visibly in a loose curve to a plain tan collar on the SAME large mature golden retriever standing to her right, both facing outdoors. Whole figures and all feet/paws visible. Brass wall hook now EMPTY. Wet gray flagstone path outside with autumn leaves, clearing pale blue afternoon sky, softly bright natural light, no heavy golden sunset. Rust chair faintly visible on right inside. Beautiful painterly cinematic illustration, consistent tactile detail and anatomy, no words, no borders, no watermark. Still moment just before they step outside.
```

## S6

```text
Use case: illustration-story. Final shot of a quiet IRO SOUNDS short film. Input reference is exact identity, wardrobe and hand-painted cinematic style. New outdoor scene after the rain: wide shot from behind of this same adult woman (chin-length wavy dark brown bob, amber rectangular hairclip, teal overshirt, cream tee, navy wide trousers, brown ankle boots) and same large mature golden retriever with pale broad muzzle and honey coat, taking a gentle walk AWAY from camera along a wet stone path. Woman near center-left, dog at her right, both full bodies occupy only 40 percent of image height. Her right hand holds tan leash loosely and continuously attached to dog's plain tan collar. Quiet residential garden lane, low stone wall, autumn orange and copper leaves, a foreground shallow puddle reflecting pale sky and leaf branches. Soft blue-gray clearing sky with diffuse afternoon light, only gentle warm accents, NOT an overpowering golden sunset. Small cozy house with teal doorway far behind to side. Calm understated conclusion, no people other than them, no words, no logo, no border, no collage. Landscape 16:9. Natural walking poses, four dog legs, two human legs.
```


## 完成v2の追加生成
中間画像「女性は読書中、犬だけ顔を上げた状態」と、Kling 3.0による犬・女性各6秒のプロンプト全文は `irostory01_動作プロンプト.json` を参照。生成済み2本で完成v2を制作。再生成は不要。
