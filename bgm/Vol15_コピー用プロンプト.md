# Vol.15 Moonlit Silver Grass — コピー用プロンプト集

月夜のすすき野／テーマ「満ちる」。**22曲・60分。うち新しく作るのは9本だけ。**

## この巻の設計

**差別化の軸は「地平線」。** 既存14本＋コンピ2本＋Long Nights 3 は、見上げ（Vol.12）・
見下ろし（Vol.6）・囲まれた中（Vol.2/11/13/14）のどれかで、**一度も「平らに開けた場所」を
出していない。** 空が画面の半分を占め、遠くまで遮るものが無い画はこの巻が初めて。

**光は逆光。** 低い月を正面に置き、穂を透過光で銀色に光らせる。
Vol.8（石灯籠で下から暖色）ともVol.13（細い枝が透ける）とも当たり方が違う。

**そしてシリーズで初めて虫の音を敷く。** Vol.5「蛍の川」に続く2本目で、
純器楽の看板を降ろす判断ではない。テーマ「満ちる」は
**月が満ちる／穂が野を満たす／虫の音が沈黙を満たす**の三重で、
**この巻で音が加わること自体をテーマの側で引き受けている。**

---

## 作るのは9本だけ

| 種 | 在庫 | この巻 | 作る |
|---|---|---|---|
| ⑨琵琶 | **0本** | 5本 | **○ 14テイク** |
| ⑧龍笛 | **1本** | 4本 | **○ 10テイク** |
| ②尺八 | 33本（息0.05超えは4本） | 3本 | 在庫 |
| ①箏 | 10本 | 2〜3本 | 在庫 |
| ③ピアノ | 8本 | 1〜3本 | 在庫 |
| ④金属打 | 7本 | 1〜3本 | 在庫 |
| ⑥胡弓 | 12本 | 1〜3本 | 在庫 |
| ⑦笙 | 6本 | 1〜2本 | 在庫 |
| ⑩フル編成 | 14本 | 2〜3本 | 在庫 |

**24テイク。Vol.14は88本作って22本使った。** 在庫91本は既に
`Vol15_素材_すすき野/楽曲/` にコピー済みなので、生成したファイルを同じ場所に置き、
`volumes/vol15.yaml` の `kinds` に追記すれば `analyze` から通る。

⑤風鐸は入れない（軒の青銅鈴。野原には無い）。

---

## ★龍笛の作り方を変える

Vol.12で龍笛を新規枠にしたとき、音域（高い・澄んだ）と息の質まで書き分けたのに
**②尺八と分離しなかった**（②×⑧の平均一致度0.379は、②尺八の同種内平均0.368より高い）。
「吹く種は何本足しても割れない」という結論が出ている。

**この巻では音数で割る。** 発音の仕方が同じなら、残る手は音の密度しかない
（メモリ suno-prompt-design）。尺八は長く伸ばす持続音。**龍笛は逆に、短く切った音を
まばらに置き、あいだを長い沈黙にする。** さらに**下にドローンを敷かない**
（全曲がドローン支配で似るのは analyze でも出ている）。

---

# ★★ 長さを削る言葉を書かない（2026年8月17日 修正）

**初版は失敗している。** `Short detached notes` `stopped before it can bloom`
`Short ascending figures that stop` `Wide silences` と書いたため、30秒前後の曲しか出なかった。

**Sunoは「曲の長さの指示」と「音型の指示」を区別しない**（メモリ suno-prompt-design）。
`short` `stop` `brief` `staccato` `wide silences` `the silences are the main material` は
すべて曲全体を縮める。**疎であることは「短さ」ではなく「遅さ」で書く。**

| 書きたいこと | ✗ 書いてはいけない | ○ こう書く |
|---|---|---|
| 音がまばら | short notes / wide silences | each note allowed to ring out and fade completely before the next begins |
| 切って置く | detached, stopped, staccato | one note at a time, never overlapping |
| 間が長い | long silences between notes | a long, patient space around every phrase |
| 消える | stop, cut off | fade away naturally |

**そのうえで長さの定型句を必ず末尾に置く**（初版にもあったが、上の語に押し負けていた）。
今回はさらに `It continues in this same way for many minutes.` を足して補強してある。

**それでも短ければ Suno の `Extend` で伸ばす。** 音色が気に入ったテイクは
作り直すより Extend のほうが早い。

---

# A. ⑨琵琶 — 14テイク

撥で弾く減衰系。この巻で唯一の「撥弦の低音」。在庫ゼロなのでどのみち作るしかない。
琵琶は**Vol.11で①箏と分離できている**ので、種としては安全。
**4種 × 3〜4テイク。キーを散らす。**

### 琵琶-1（D minor・低音域・語るように）

```
Solo Japanese biwa, played with a large wooden plectrum, low register, deep and woody.
Each stroke has a distinct percussive attack and the characteristic buzzing sawari
resonance that is allowed to ring out and fade away completely before the next stroke
begins. D minor. Extremely slow and unhurried, as if telling a story to no one.
Close, dry recording with almost no reverb, so the decay of each string is heard all the
way down. No drone, no sustained background pad, no strings section.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No chanting. No humming.
```

### 琵琶-2（A minor・中音域・粒を細かく）

```
Solo Japanese biwa in the middle register, A minor. Simple repeated plucked figures that
gather and thin out again over a long time, each phrase given room to breathe before the
next one arrives. Bright plectrum attack, woody body resonance, strings left to ring and
fade naturally. Slow, steady, unhurried. Dry, intimate recording.
No drone, no pad, no bowed instruments, no percussion.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No chanting. No humming.
```

### 琵琶-3（E minor・単音を置いていく）

```
Solo Japanese biwa, E minor, one note at a time and never overlapping. A single low note
is struck and its buzzing resonance is allowed to fill the room and fade away completely
on its own before the next note arrives. Occasional slow bend of the pitch by pressing the
string behind the fret. Extremely slow, patient and spacious.
Dry close recording, no room reverb. No drone, no accompaniment of any kind.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No chanting. No humming.
```

### 琵琶-4（G minor・高音域・銀色に）

```
Solo Japanese biwa in the upper register, G minor. Thin, silvery plucked tone, phrases
rising and falling like a line drawn slowly and then released, each one fading away
naturally before the next begins. The sawari buzz is present but light. Unhurried and
generous with space. Dry, close, no reverb tail.
No drone, no low sustained notes, no other instruments.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No chanting. No humming.
```

---

# B. ⑧龍笛 — 10テイク

雅楽の横笛。**3種。1と2を各4テイク、3を2テイク。**

**★尺八と完全には割れない前提で使う。** Vol.12で音域も息の質も書き分けたが
分離しなかった（②×⑧の平均一致度0.379は、②尺八の同種内平均0.368より高い）。
初版はこれを「音数」で割ろうとして長さを壊した。**この巻では割り切って、
音域（高い・澄んだ・揺れない）とドローン無しだけで分ける。**
この巻の尺八は3本しか入らないので、`order` が両者を離して置けば実害は出ない
（Vol.12は同じ状態で公開して問題になっていない）。

### 龍笛-1（C minor・高く澄んだ単音）

```
Solo Japanese ryuteki flute, high register, C minor. Single clear notes, each one allowed
to sound fully and then fade away naturally before the next one begins. Pure, steady tone
with no breathiness and no vibrato. Extremely slow and patient, with a great deal of air
around every phrase. Nothing underneath: no drone, no pad, no strings, no percussion.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No chanting. No humming.
```

### 龍笛-2（F# minor・二音の問答）

```
Solo Japanese ryuteki flute, F sharp minor, very high and clear. A simple two-note or
three-note shape is stated, allowed to fade completely, and then answered a step higher
after a long, patient pause. Crisp, glassy articulation with no breath noise, no growl and
no bending. Unhurried throughout. Absolutely no drone, no sustained background,
no accompaniment.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No chanting. No humming.
```

### 龍笛-3（B minor・上へ抜ける）

```
Solo Japanese ryuteki flute, B minor. Slow ascending figures that rise and then hang in
the air, fading away naturally, returning again after a long and irregular pause. Bright,
thin, glassy tone, played straight with no vibrato and no breath texture.
No drone, no pad, no reverb wash, nothing sounding between the phrases.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No chanting. No humming.
```

---

## 生成したあとにやること

1. ファイルを `Vol15_素材_すすき野/楽曲/` に置く
2. `volumes/vol15.yaml` の `kinds` に `"ファイル名（拡張子なし）": ⑨琵琶` の形で追記
3. `python3 -m bgmkit analyze vol15` … 重複（同じファイルが2回DLされる件）と一致度を見る
4. `python3 -m bgmkit select vol15` … 琵琶5・龍笛4が下限で固定してある
5. `python3 -m bgmkit order vol15`
6. `python3 -m bgmkit audio vol15` … 最後に**虫の音の効きが実測で出る**。
   3〜5kHzが +6dB 以上上がっていれば敷けている

**`--write` は使わないこと。** yaml.safe_dump がYAMLを丸ごと書き直してコメントが全部消える
（Vol.14で一度消している）。出力を手で貼る。

---

## C. 画像 22枚

11場面 × A（引き）/ B（寄り）＝22。**曲順と1対1に対応する**（場面名は `volumes/vol15.yaml` の `scenes`）。

### 保存のきまり

- **16:9 で出す**（手生成なので bgmkit の切り出しとガンマ1.3は掛からない）
- 保存先は `/Volumes/ESD-EPB/Whispers of Japan/Vol15_素材_すすき野/画像/`
- ファイル名は **`vol15_01.png` 〜 `vol15_22.png`**（下の番号と一致させる）
- **1枚ずつ生成する**

### ★露出だけは毎回見ること

**Long Nights 3 では手生成の画像が暗すぎて、60枚中28枚に暗部の持ち上げを掛けた**
（真っ黒に潰れた画素が中央値32.5%・最大72.0%）。全プロンプトに露出の一文を入れてあるが、
それでも潰れることがある。**暗部にディテールが残っているかを1枚ずつ見ること。**

### 毎回チェックすること

- **穂がブレていないか。** すすきは「なびく草」なので、ブレた瞬間に音の期待が生まれる。
  **無風の証明は露**（07・08・21・22に入れてある）。**虫の音そのものも証明になる**
  （虫は風の夜に鳴かない）。プロンプトに風の語は1語も書いていない。**書き足さないこと**
  （否定形で書いても引っぱられる。Vol.13・Vol.14と同じ扱い）
- **円錐形の高い山が入っていないか。** すすき＋満月でAIは富士山を出したがる。遠景は低い稜線だけ
- **水が入っていないか**（池・川・濡れた路面）。水音を期待され、Vol.5とも紛らわしい
- **穂が金色になっていないか。** 黄金の穂はVol.7の棚田や麦畑に見える。**銀白色・羽毛状**で通す
- **月見の道具が入っていないか**（三方・団子・活けたすすき）。器物と崩れ字を呼び、Vol.10とも被る
- **鳥居・石灯籠・竹・松・雪・霜が入っていないか**
  （順に Vol.1・Long Nights 3・Vol.2・Vol.14・Vol.9・Vol.13 と被る）
- **人・道具・文字が写っていないか**
- **★月の位置が番号の順と合っているか。** 03で昇り、11で中天、19で西、21で薄明。
  **ここが崩れると「一夜を旅する」構成そのものが壊れる。** 生成し直すときも位置を必ず引き継ぐ
- **同じ画像を2回保存していないか**（名前も日時も違うので目では気づけない。MD5で見る）

### サムネイルの元画

**まだ決めない。** 22枚が揃ってから168pxで実測して選ぶ（Long Nights 3 と同じ手順）。
候補は **13（逆光の銀・引き）** — この巻で最も明るく、既存14枚のどれとも似ない。
ただし14枚の中で一番白いので、題字が乗るかは実測しないと分からない。

---

### 01 — 場面「野の入口」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view of the edge of an open plain of Japanese silver grass (susuki, Miscanthus
sinensis) in late autumn. The horizon sits low and the sky fills the upper two thirds.
A full moon has just cleared the horizon on the left, low and large, and its light comes
toward the camera so the plumes at the field's edge are lit from behind and glow pale silver
against the darker mass of grass. Beyond the field, only a very low, soft ridgeline.
Ground-level camera, slightly below the tops of the plumes.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 02 — 場面「野の入口」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A close photograph of three or four stems of Japanese silver grass at the edge of the field,
shot from below against the sky. The low full moon is behind them and out of focus, a soft
bright disc, so each plume is rimmed with silver light and the seed filaments catch the glow
one by one. Shallow depth of field, the field behind dissolving into dark blue.
No horizon visible.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 03 — 場面「月の出」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view across the open silver grass plain, the full moon low above the far horizon and
slightly right of centre, large and clear. A broad path of pale light runs from the moon
across the tops of the plumes toward the camera. The plain is completely flat and stretches
to the horizon on every side; a faint low ridgeline sits far in the distance.
Camera at chest height.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 04 — 場面「月の出」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A telephoto shot compressing the plain, the full moon large and low, filling much of the
frame, with the tops of the silver grass plumes crossing the lower edge of the moon's disc as
dark and silver silhouettes. The moon's surface detail is clearly visible. Everything is
still. Long lens, strong compression.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 05 — 場面「穂の海」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A very wide view of an endless sea of Japanese silver grass seen from slightly above, the
plumes filling the lower half of the frame from edge to edge like a pale silver swell.
The moon is higher now, behind and to the left of the camera, so the plumes are lit across
their tops. Deep blue sky above with faint stars. The horizon line is almost perfectly flat
and unbroken.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 06 — 場面「穂の海」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
Looking straight down into the mass of silver grass from just above the plumes, filling the
entire frame with layer upon layer of feathery silver-white heads and the dark stems below
them. No sky, no horizon. Moonlight rakes across from the upper left, picking out the topmost
plumes and letting the deeper layers fall into soft blue shadow that still holds detail.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 07 — 場面「露」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view low among the silver grass, the camera down near the base of the stems looking
out across the plain. Heavy dew has settled: countless tiny water beads cling along the stems
and the lower leaves, each one catching a point of moonlight so the base of the field is
scattered with small cold sparks. The plumes above are pale against a deep blue sky.
The full moon is high and off to the right.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 08 — 場面「露」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
An extreme close macro of dew beads on a single silver grass stem and its narrow leaf blade,
each bead holding a tiny inverted reflection of the moon. The beads are perfectly round and
perfectly still. Behind, the field is completely out of focus, a wash of dark blue and faint
silver. Very shallow depth of field.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 09 — 場面「細道」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view of a narrow earthen footpath running away from the camera into the plain of
silver grass, the grass standing higher than head height on both sides so the path becomes a
corridor. The path is dry, packed bare earth. Far ahead the corridor opens and the moonlit
sky shows through the gap. The moon is high and slightly left, lighting the tops of the walls
of grass.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 10 — 場面「細道」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
From inside the narrow path, camera turned to look at the wall of silver grass beside it from
an arm's length away. Stems rise vertically out of frame; the plumes above catch moonlight
while the lower stems stay in deep blue shadow with detail intact. A sliver of moonlit sky at
the very top of the frame.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 11 — 場面「中天」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view of the open plain with the full moon high overhead near the top of the frame,
small and brilliant. The light now falls almost straight down, so the plumes are lit on their
crowns and the field reads as a soft silver plane with dark vertical stems beneath.
The horizon is low and far. The sky is at its deepest blue and the stars are faint against
the moon's brightness.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 12 — 場面「中天」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
Looking up through a stand of silver grass toward the high moon, the stems and plumes
converging upward around the bright disc. The plumes nearest the moon are translucent and
glowing where the light passes through them. Strong upward perspective. Everything perfectly
still and sharp.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 13 — 場面「逆光の銀」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view straight into the moonlight, the moon now lower again and directly ahead, so the
entire field of silver grass is fully backlit. Every plume in the frame is a glowing filament
of silver-white light against a dark blue field and sky, and the whole plain seems to be lit
from within. The horizon is a thin dark band. This is the brightest and most silver image of
the set.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 14 — 場面「逆光の銀」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A close-up of a single silver grass plume fully backlit by the moon, filling most of the
frame, every seed filament separately lit and glowing so the plume looks like spun glass.
The moon itself is just outside the frame. The background is dark blue and completely out of
focus. Nothing else in the picture.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 15 — 場面「影の帯」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view of the plain where long parallel bands of shadow and moonlight lie across the
silver grass, cast by a distant low line of leafless trees far off to one side. The bands run
diagonally across the frame from lower left to upper right. The lit bands are pale silver,
the shadowed bands deep blue with detail still visible. The moon is low behind the trees.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 16 — 場面「影の帯」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
At the boundary between a shadow band and a lit band, the camera close to the grass so the
transition crosses the middle of the frame. On one side the plumes glow silver; on the other
the same plumes are deep blue but still fully legible. The edge of the shadow is soft.
Shallow depth of field behind.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 17 — 場面「枯れ色」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view of a part of the plain where the season has turned further: among the silver
plumes stand many dried russet and tawny brown stems and curled leaves from earlier in the
autumn. The warm dry browns read clearly but stay muted under the blue moonlight, so the
picture is still a cold night scene with warmth only in the detail. The moon is past its
highest and beginning to descend on the right.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 18 — 場面「枯れ色」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A close-up of a cluster of dried, curled silver grass leaves and old russet stems, their
papery texture and split edges clearly resolved, with two or three fresh silver plumes rising
behind them slightly out of focus. Warm brown against cold silver. Moonlight comes from
behind and to the right.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 19 — 場面「西へ傾く」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view with the moon low in the west, large again and sinking toward the far horizon on
the right, its light now warmer and more golden-white than earlier. The silver grass takes a
faint warm cast on the lit side while the sky above stays deep blue. Long shadows stretch
away from the camera across the plain.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 20 — 場面「西へ傾く」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A telephoto shot of the setting moon partly cut by the tops of the silver grass on the
horizon, the plumes in front reading as a dark and silver fringe across the lower part of the
moon's disc. The moon is large and slightly warm. Strong long-lens compression,
everything still.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 21 — 場面「薄明」（A・引き）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A wide view of the plain at the very beginning of dawn, the moon gone or a pale ghost near
the horizon, the sky graded from deep blue at the top to a cold pale grey and the faintest
cool rose at the horizon. The silver grass is now lit softly and evenly from the whole sky
rather than from a point, so the plumes look matte and pale. Dew still lies on the stems.
The horizon is low and the sky dominates.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```

### 22 — 場面「薄明」（B・寄り）

```
Photorealistic 16:9 night photograph, ultra high quality, sharp throughout,
no people, no animals, no text and no signage.
A dawn close-up of silver grass plumes against the pale graded sky, the light soft and
directionless, the plumes matte silver-grey with dew still beaded along the stems below.
Quiet, cool and even. Shallow depth of field. This is the calmest and palest image of the
set, and it closes the night.
The silver grass plumes are completely motionless and razor sharp, with no motion blur;
the individual filaments of each feathery plume are resolved.
Exposed properly for a moonlit night: the sky holds a deep luminous blue, and the shadowed
areas keep visible detail instead of being crushed to pure black.
Do not include any tall iconic conical mountain, any water of any kind, any shrine gate,
stone lantern, bamboo, pine tree, snow, frost, offering stand or arranged flowers.
The plumes are silver-white and feathery, never golden grain and never rice.
```
