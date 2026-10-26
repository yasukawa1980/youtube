# IRO21「遠回りして、帰ろうか。」コピー用プロンプト

設計は `iro/iro21_テーマ設計.md`。ここには生成サービスへ貼る全文だけを置く。

## 開始画像（Codex・内蔵の画像生成・2案を各1回）

参照画像1：`/Users/ryo/Desktop/BGM/IRO/Reading/20_しおりを挟むにはまだ早い/開始画像/iro20_start_1920.png`（人物・犬・絵柄の第一参照。構図は真似しない）
保存先：`/Users/ryo/Desktop/BGM/IRO/Drive/21_遠回りして帰ろうか/開始画像/iro21_start_案1.png`・`iro21_start_案2.png`
検品：16未満の画素が3%以下、250以上が0.5%以下。犬は頭からしっぽの先まで1920基準で幅500px以内。

### 共通（両案の先頭に付ける）

```text
Use case: illustration-story. Create one polished 16:9 landscape starting-frame illustration for IRO Sounds IRO21, a two-hour late-autumn night-drive music video. Input image 1 is the FIRST character and rendering reference, NOT a composition to copy. Preserve the recognizable same adult woman around 30: slightly angular face, natural brown eyes, expressive eyebrows, chin-length wavy dark brown bob and small rectangular amber barrette at her left temple; muted teal overshirt over ivory T-shirt and navy trousers. NO bun or tied hair. Preserve the same LARGE adult golden retriever: broad light muzzle, heavy soft ears, honey coat, substantial paws, NOT a puppy.
Setting: inside a small, modest, slightly old hatchback at night, Japanese right-hand-drive car, the woman is driving calmly along an elevated bayside expressway. Both of her hands rest simply on the steering wheel at the same place; the wheel is straight. The dog sleeps on the front passenger seat inside a low-sided RUST colored pet car-seat bed (#9C4A2E, muted rusty orange-brown), curled compactly: closed eyes, chin on forepaws, full body and full curled tail visibly inside the frame and above the bed rim. The dog's whole silhouette is no wider than about 26% of the picture width. Soft amber glow from analog dashboard gauges; rust and teal fabric accents in the cabin. No logos, no brand marks, no readable text on gauges or signs, no license plates, no phone, no other people.
Outside: only the DISTANT view is visible, so the scene would look the same for a few seconds while driving: an indigo night sky, a calm dark bay, a far hillside city of small warm lights and one long distant bridge with a line of lights. Keep the road surface hidden below the dashboard line; no nearby cars, no lane markings, no nearby lamp posts in view. Interior lit by warm sodium-orange light from above and the soft dashboard glow, readable faces.
Match the reference's warm hand-drawn animated-feature illustration: expressive restrained contours, simplified painterly planes with selective fine gouache texture, sophisticated adult faces, appealing readable shapes, believable car-interior perspective. Keep faces gentle and mature, no large sparkling anime eyes, no glossy 3D or photography. Lift the darkest shadows enough to retain detail, avoid crushed blacks and blown highlights. No lettering, logos, text, borders, watermarks or collage. Full bleed 16:9, high quality. This is a new scene of the SAME woman and SAME adult dog.
```

### 案1：後部座席から斜め前を見る

```text
Composition A — from the back seat: the camera sits on the LEFT rear seat at seated eye level, looking diagonally forward-right through the cabin, completely still. The woman in the right-hand driver's seat is on the RIGHT side of the picture (around x=70%), seen from behind at a three-quarter angle so her left cheek line, eyelashes, the amber barrette and her calm expression toward the road are visible; her head and shoulders occupy about 40% of picture height. The sleeping dog in the passenger seat bed is on the LEFT (around x=25%), facing toward the camera, fully visible from head to tail tip. Between them, the CENTER of the windshield shows the distant bay, city lights and the long lit bridge; the top-left area of the windshield and roof lining stays quiet and darker for later typography. Front seat backs and headrests frame the view but must not hide the dog's face or the woman's profile.
```

### 案2：ダッシュボードから車内を見る

```text
Composition B — from the dashboard: the camera is mounted just inside the windshield, slightly toward the passenger side, looking back into the cabin, completely still. The woman driving is on the LEFT of the picture (around x=35%), her face clearly visible in a soft three-quarter view, eyes OPEN and looking calmly at the road ahead so her gaze passes just to the right of the camera, never staring into the lens. The sleeping dog in the passenger seat bed is on the RIGHT (around x=72%), fully visible from head to tail tip. Behind them, the rear and side windows show the distant indigo bay and small warm city lights. The upper-left area above the woman's head (roof lining and rear window) stays quiet and darker for later typography. The bottom edge is the soft dark top of the dashboard, not cutting the dog.
```
