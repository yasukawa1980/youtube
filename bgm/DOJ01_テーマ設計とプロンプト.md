# Days of Old Japan / 01 —— 風鈴の縁側

**2026年8月26日 設計。** シリーズ1本目。在庫の器楽108本から20曲、そこに風鈴を重ねる。

| | |
|---|---|
| 音 | 器楽20曲（在庫・新規生成ゼロ）＋ **風鈴と遠くの蝉** |
| 尺 | 50〜60分（20曲） |
| 絵 | **水彩・不透明水彩で5枚**（4曲ごとに切り替え） |
| 題字 | 風鈴の縁側 |

英語の題名（Vol.5 の `蛍の川 with River Sounds` に倣う）：

```
The Verandah in Summer 🌙 Japanese Ambient Music with Wind Chimes | XX Min
```

---

## 1. ★風鈴は「敷く」素材ではない

**ここが雨・蝉と根本的に違う。** 風鈴は風が吹いたときだけ鳴る**間欠音**で、
実際の縁側では10〜60秒の沈黙をはさんで数回鳴る。

**したがって `vet` の合否がそのまま使えない。**

- 良い風鈴の録音は**必ず「レベル変動」で落ちる**（沈黙と打音の繰り返しなので当然）
- 逆に変動の小さい風鈴の録音は、鳴りっぱなし＝**現実には存在しない音**
- **落ちたことを不合格と読まないこと。** 蝉の巻で「音程あり」を外したのと同じ構図

## ★連続する地が別に要る

風鈴だけを重ねると、鳴っていない時間は純器楽に戻ってしまい、
題名に `with Wind Chimes` と書いた説明がつかない。**2層にする。**

| 層 | 役割 | 素材 |
|---|---|---|
| 地 | 通して薄く鳴り続ける | **遠くの蝉**（`SOJ02_素材_蝉/環境音/` が使える） |
| 点 | ときどき鳴る | **風鈴** |

**★蝉は「遠く」に置くこと。** 蝉の巻を出した直後なので、主役にすると重なる。
こもりの低い（＝遠い）素材を選び、地としてかなり下げる。

**★★道具が1つ足りない。** `ambient:` は1ファイルしか受け取らない。
2層にするには「複数ファイル＋それぞれの濃さ」に対応させる必要がある。
**素材が揃ってから実装する**（蝉の巻で学んだとおり、素材より先に道具を決めない）。

---

## 2. 落としてくる素材

**★日本の効果音サイトを当たること。** Pixabayの `風鈴` はほとんどが
**西洋のウィンドチャイム**（金属管の連なり）で、日本の風鈴（ガラスの一つ鈴）は
4秒のものが1本あっただけ。蝉のときと同じ構図で、日本のサイトのほうが確実。

欲しいもの：

1. **風鈴（ガラスまたは南部鉄）** … 5〜10本。**短くてよい**（数秒〜30秒）。
   間欠に並べ直すので、長さより**打音が澄んでいること**が大事
2. **できれば「縁側の夏」の一発録り** … 風鈴と遠くの蝉が一緒に入っているもの。
   1本で済むなら2層にする必要が無い。**まずこれを探す**

**★避けるもの** … 金属管が連なって鳴るウィンドチャイム（音階が違い、日本の縁側にならない）。
`chime` で検索すると大半がこれ。

置き場所：

```
/Volumes/ESD-EPB/Whispers of Japan/DOJ01_素材/環境音/
```

---

## 3. 絵 —— 5枚で「内から外へ」

SOJ01は雨が遠くこもっていく、SOJ02は一日の光が一周する。**この巻は視点が外へ出ていく。**
座敷の暗がりから始まり、縁側を通り、庭を抜けて、夏野の遠景で終わる。

**★人物は出さない。** 1枚が10分以上映る。代わりに**人の居た跡**を置く
（団扇・麦茶の硝子・脱いだ草履）。**サムネだけ人物を出す**（蝉の巻と同じ考え方）。

**★★短冊に文字を書かせないこと。** 風鈴の短冊には本来文字が入る。
この題材で最も高い確率で破られる禁止。**全枚に「無地」と明示してある。**

### 全枚に効く禁止

1. **文字** … 短冊・掛け軸・のれん。**短冊は無地**と明示
2. **現代物** … 電線・室外機・サッシ・プラスチック・LED
3. **人物** … 5枚とも出さない（跡だけ）
4. **写実に寄せない** … 筆致と紙の目を残す。写真のようになったら失敗


---

## 4. コピー用プロンプト —— 本編5枚

保存先は `/Volumes/ESD-EPB/Whispers of Japan/DOJ01_素材/画像/doj01_01.png` 〜 `_05.png`。

**★★2026年8月26日改訂。** ChatGPT が指摘した5つの取り違えを全枚に反映した。
どれも実際に起こる失敗で、指摘は妥当だった。

| 指摘 | 直し方 |
|---|---|
| `glass of barley tea` が現代のタンブラーやプラコップになる | **厚手の古い型ガラス・漆の盆に載せて**と具体化 |
| `open sliding screens` がアルミサッシになる | **木枠の障子・紙と木目が見える**と積極的に書いた（禁止も追加） |
| `almost dissolved` が絵ではなく**写真のボケ**になる | **3〜4筆で置いて滲ませる**と*描き方*で言う。`NOT photographic blur` を明記 |
| 室内の指定が薄いと**家具や飾りを勝手に足す** | **他には何も無い**と各枚に明記（家具・掛け軸・置物・鉢） |
| 左三分の一に物が入る | 「静か」ではなく**「何も置かない」という禁止**に変えた |

**★1枚が10分以上映る。** 等倍で隅まで見ること。
**★★水彩は168pxで写実より不利。** 淡い washes は縮小すると中間色に潰れる。
生成後に必ず168pxで確認し、潰れていたら明暗を強くして作り直す。

### 01. 座敷の奥から縁側を見る

内 ／ 暗がりから明るい庭へ

```
The interior of a traditional old Japanese room in midsummer, viewed from deep inside the room looking out toward the verandah and the garden. Three clear spatial depths. Nearest: the cool shaded tatami floor filling most of the foreground, its woven texture caught in a few dry strokes, with a round paper fan lying flat where someone set it down and, beside it, a heavy old pressed-glass tumbler of cold barley tea beaded with condensation, standing on a small lacquered wooden tray. Middle: the dark wooden posts and lintels of the open wood-framed shoji screens, their paper panels and timber grain plainly visible, and past them the sunlit boards of the verandah. Farthest: the summer garden flooded with intense afternoon light, pale and hazy, laid in as a few loose wet washes. The room is otherwise completely bare — no furniture, no cabinets, no cushions, no ornaments and nothing hanging on the walls. The subject is the contrast between the cool blue interior shade and the burning bright garden.

A painted illustration in traditional transparent watercolour and gouache, traditional Japanese scenery in high summer. Transparent watercolour washes for the sky, the distance and the deep shade, laid wet-into-wet so they bloom and bleed softly; more opaque gouache for the foreground, laid in confident flat shapes with visible brush edges. Visible cold-pressed paper tooth throughout. A few places where the wash has pooled and dried with a hard edge. In the distance the brushwork is loose and economical — far shapes are reduced to three or four wet strokes and left to bloom. This is painterly simplification, NOT photographic blur and NOT a soft-focus lens effect: edges stay as brush edges. Small areas of bare paper left unpainted as the brightest highlights. No ink outlines. Keep the main subject structured and readable: the drawing underneath is sound, simplified but never distorted. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. Warm limited palette — raw sienna, olive, pale ochre, soft indigo in the shadows. Nothing at all is placed in the LEFT THIRD of the frame: no objects, no figures, no bright accents, no lettering — it stays quiet flat wash. No people anywhere. No text, no signage, no lettering, no calligraphy, no hanging scrolls, no patterned paper of any kind. No modern objects whatsoever: no power lines, no utility poles, no electric lamps or light fittings, no vehicles, no air conditioners, no plastic, no aluminium or metal window frames, no glazed glass windows, no modern cups, bottles or tableware. 16:9 composition with generous quiet empty space in the left third for titles.
```

### 02. 縁側と簾、風鈴

中 ／ 風鈴が初めて出る

```
The wooden verandah of a traditional old Japanese house on a summer afternoon, seen along its length. Three clear spatial depths. Nearest: the worn verandah boards running away from the viewer, their grain and old polish caught in long confident strokes. Middle: a rolled reed blind of split bamboo hanging from the eaves, throwing striped shadow across the boards, and a small Japanese glass wind chime hanging from the wooden eave beam — below the chime hangs a narrow paper tag which is completely plain, blank and unmarked, with no writing or pattern of any kind. Farthest: the garden in soft washed light, reduced to loose wet strokes. The verandah is otherwise completely bare — nothing else is placed on the boards. A faint suggestion of movement in the paper tag, as if a breeze has just passed.

A painted illustration in traditional transparent watercolour and gouache, traditional Japanese scenery in high summer. Transparent watercolour washes for the sky, the distance and the deep shade, laid wet-into-wet so they bloom and bleed softly; more opaque gouache for the foreground, laid in confident flat shapes with visible brush edges. Visible cold-pressed paper tooth throughout. A few places where the wash has pooled and dried with a hard edge. In the distance the brushwork is loose and economical — far shapes are reduced to three or four wet strokes and left to bloom. This is painterly simplification, NOT photographic blur and NOT a soft-focus lens effect: edges stay as brush edges. Small areas of bare paper left unpainted as the brightest highlights. No ink outlines. Keep the main subject structured and readable: the drawing underneath is sound, simplified but never distorted. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. Warm limited palette — raw sienna, olive, pale ochre, soft indigo in the shadows. Nothing at all is placed in the LEFT THIRD of the frame: no objects, no figures, no bright accents, no lettering — it stays quiet flat wash. No people anywhere. No text, no signage, no lettering, no calligraphy, no hanging scrolls, no patterned paper of any kind. No modern objects whatsoever: no power lines, no utility poles, no electric lamps or light fittings, no vehicles, no air conditioners, no plastic, no aluminium or metal window frames, no glazed glass windows, no modern cups, bottles or tableware. 16:9 composition with generous quiet empty space in the left third for titles.
```

### 03. 風鈴の寄り

中 ／ この巻の顔

```
Close view of one single small Japanese glass wind chime hanging from a wooden eave beam against a summer garden. The chime is painted with care: the thin clear glass bowl with its faint colour at the rim, the small clapper hanging inside, the fine cord above, and below it the narrow paper tag — the tag is completely plain, blank and unmarked, with no writing, no characters and no pattern of any kind. Light passes through the glass and lays one small bright mark on it, left as bare unpainted paper. Behind, the garden is reduced to loose wet washes of green and gold laid wet-into-wet — painterly simplification, not photographic blur. Only one chime is in the picture; there are no other chimes and no other objects.

A painted illustration in traditional transparent watercolour and gouache, traditional Japanese scenery in high summer. Transparent watercolour washes for the sky, the distance and the deep shade, laid wet-into-wet so they bloom and bleed softly; more opaque gouache for the foreground, laid in confident flat shapes with visible brush edges. Visible cold-pressed paper tooth throughout. A few places where the wash has pooled and dried with a hard edge. In the distance the brushwork is loose and economical — far shapes are reduced to three or four wet strokes and left to bloom. This is painterly simplification, NOT photographic blur and NOT a soft-focus lens effect: edges stay as brush edges. Small areas of bare paper left unpainted as the brightest highlights. No ink outlines. Keep the main subject structured and readable: the drawing underneath is sound, simplified but never distorted. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. Warm limited palette — raw sienna, olive, pale ochre, soft indigo in the shadows. Nothing at all is placed in the LEFT THIRD of the frame: no objects, no figures, no bright accents, no lettering — it stays quiet flat wash. No people anywhere. No text, no signage, no lettering, no calligraphy, no hanging scrolls, no patterned paper of any kind. No modern objects whatsoever: no power lines, no utility poles, no electric lamps or light fittings, no vehicles, no air conditioners, no plastic, no aluminium or metal window frames, no glazed glass windows, no modern cups, bottles or tableware. 16:9 composition with generous quiet empty space in the left third for titles.
```

### 04. 庭

外 ／ 視点が出る

```
A small enclosed traditional Japanese garden at the height of summer, seen from the verandah. Three clear spatial depths. Nearest: stepping stones set into thick moss, each stone laid in as a single confident stroke, the moss stippled and damp. Middle: a low stone water basin with still water standing in it and a bamboo ladle resting across the rim, and a clipped shrub heavy with leaf. Farthest: an earthen garden wall capped with weathered tiles, and a maple in full green leaf reduced to a few loose wet strokes. Dappled light falls across the moss in soft-edged patches left as bare paper. The garden holds nothing else — no lanterns, no ornaments, no pots, no fencing.

A painted illustration in traditional transparent watercolour and gouache, traditional Japanese scenery in high summer. Transparent watercolour washes for the sky, the distance and the deep shade, laid wet-into-wet so they bloom and bleed softly; more opaque gouache for the foreground, laid in confident flat shapes with visible brush edges. Visible cold-pressed paper tooth throughout. A few places where the wash has pooled and dried with a hard edge. In the distance the brushwork is loose and economical — far shapes are reduced to three or four wet strokes and left to bloom. This is painterly simplification, NOT photographic blur and NOT a soft-focus lens effect: edges stay as brush edges. Small areas of bare paper left unpainted as the brightest highlights. No ink outlines. Keep the main subject structured and readable: the drawing underneath is sound, simplified but never distorted. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. Warm limited palette — raw sienna, olive, pale ochre, soft indigo in the shadows. Nothing at all is placed in the LEFT THIRD of the frame: no objects, no figures, no bright accents, no lettering — it stays quiet flat wash. No people anywhere. No text, no signage, no lettering, no calligraphy, no hanging scrolls, no patterned paper of any kind. No modern objects whatsoever: no power lines, no utility poles, no electric lamps or light fittings, no vehicles, no air conditioners, no plastic, no aluminium or metal window frames, no glazed glass windows, no modern cups, bottles or tableware. 16:9 composition with generous quiet empty space in the left third for titles.
```

### 05. 生垣の向こうの夏野

遠 ／ いちばん外

```
A view out past a garden hedge to open summer country. Three clear spatial depths. Nearest: the clipped top of the hedge running across the lower frame, painted in flat gouache shapes. Middle: terraced rice fields stepping away, the young rice a wash of soft green with the standing water between the rows left as pale bare paper. Farthest: low wooded hills and a wide pale sky, laid in as three or four wet strokes and left to bloom — painterly simplification, not photographic blur. Utterly still and very quiet. There are no buildings, no poles, no wires and no figures anywhere in the view.

A painted illustration in traditional transparent watercolour and gouache, traditional Japanese scenery in high summer. Transparent watercolour washes for the sky, the distance and the deep shade, laid wet-into-wet so they bloom and bleed softly; more opaque gouache for the foreground, laid in confident flat shapes with visible brush edges. Visible cold-pressed paper tooth throughout. A few places where the wash has pooled and dried with a hard edge. In the distance the brushwork is loose and economical — far shapes are reduced to three or four wet strokes and left to bloom. This is painterly simplification, NOT photographic blur and NOT a soft-focus lens effect: edges stay as brush edges. Small areas of bare paper left unpainted as the brightest highlights. No ink outlines. Keep the main subject structured and readable: the drawing underneath is sound, simplified but never distorted. Strong clear difference between the light and dark masses so the image still reads when reduced to a thumbnail. Warm limited palette — raw sienna, olive, pale ochre, soft indigo in the shadows. Nothing at all is placed in the LEFT THIRD of the frame: no objects, no figures, no bright accents, no lettering — it stays quiet flat wash. No people anywhere. No text, no signage, no lettering, no calligraphy, no hanging scrolls, no patterned paper of any kind. No modern objects whatsoever: no power lines, no utility poles, no electric lamps or light fittings, no vehicles, no air conditioners, no plastic, no aluminium or metal window frames, no glazed glass windows, no modern cups, bottles or tableware. 16:9 composition with generous quiet empty space in the left third for titles.
```

### サムネ用（`doj01_thumb.png`）★人物あり

**★本編5枚は無人、サムネだけ人物を出す**（蝉の巻と同じ考え方）。
**★女性は右半分に置く**（題字のスクリムが左920pxを覆う）。

```
A painted illustration in traditional transparent watercolour and gouache: a young Japanese woman sitting on the wooden verandah of a traditional old Japanese house on a summer afternoon, framed from the waist up, placed in the RIGHT half of the frame and turned three-quarters toward the viewer. She wears a simple unbleached cotton summer kimono, her hair tied low at the nape. Her expression is bright and unforced — a small natural smile, eyes open and alive. Beside her, hanging from the wooden eave beam, is one small Japanese glass wind chime; the narrow paper tag below it is completely plain, blank and unmarked, with no writing or pattern of any kind.

Painting technique: transparent watercolour washes for the garden and the distance, laid wet-into-wet so they bloom and bleed; more opaque gouache for the figure, laid in confident flat shapes with visible brush edges. Visible cold-pressed paper tooth. Small areas of bare paper left unpainted as the brightest highlights. No ink outlines. The distant garden is reduced to a few loose wet strokes — painterly simplification, NOT photographic blur and NOT a soft-focus lens effect.

Keep the FACE structured and readable: the drawing underneath is sound, the features placed correctly and simply, the eyes and mouth described with a few sure strokes rather than blended into mush. Simplified but never distorted. An ordinary, believable face — NOT a glamour render, no glossy skin, no enlarged eyes, no idealised symmetry. Hands are not rendered in detail.

Nothing at all is placed in the LEFT HALF of the frame: no objects, no figures, no bright accents, no lettering — it stays quiet flat wash. This area will be covered by a title.

Warm limited palette: raw sienna, olive, pale ochre, soft indigo in the shadows. Strong clear difference between the light and dark masses so the image still reads at thumbnail size. No text, no signage, no lettering, no calligraphy of any kind. No modern objects whatsoever: no electric lamps, no aluminium or metal window frames, no glazed glass windows, no modern cups or tableware. Absolutely no other people. 16:9 composition.
```

---

## 5. 生成したあとに

```bash
cd /Volumes/ESD-EPB/Whispers\ of\ Japan/DOJ01_素材/画像
md5 *.png | awk '{print $NF}' | sort | uniq -d      # 重複
```

- [ ] **短冊に文字が入っていないか**（この題材で最も破られやすい）
- [ ] **アルミサッシ・現代の器が混じっていないか**
- [ ] **写真のボケになっていないか**（筆致と紙の目が残っているか）
- [ ] **左三分の一に物が入っていないか**
- [ ] **6枚を並べて場面と1枚ずつ照合**（SOJ01は抜き取りで通して19と20が入れ替わった）
- [ ] **168pxに落として、明暗が潰れていないか**（水彩の最大の弱点）
