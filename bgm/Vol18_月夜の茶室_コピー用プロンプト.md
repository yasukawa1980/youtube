# Vol.18 Moonlit Tea House — コピー用プロンプト集

月夜の茶室／テーマ「迎える」。**22曲・60分。新しく作るのは ①箏・③ピアノ・④金属打・⑥胡弓・⑩フル編成 の5種・36テイク。**
設定は `volumes/vol18.yaml`、画像の全文は `Vol18_月夜の茶室_画像プロンプト/`（22枚・合成済み）。

## 在庫（Vol.17の未採用・2026-11-25実数）

| 種 | 残り | この巻 | 作る |
|---|---|---|---|
| ①箏 | 4 | 2〜3 | ○ 8（A F major／B B minor） |
| ②尺八 | 35（息0.035以上は v12_尺八の独奏 の1本） | 1 | 作らない（本人「あまりいらない」） |
| ③ピアノ | **0**（在庫のフェルトピアノとVol.17の未採用は11/9の整理で削除済み） | 2〜3 | ○ 8（A A♭ major／B C minor） |
| ④金属打 | 4 | 2〜3 | ○ 8（A D／B G） |
| ⑥胡弓 | 3 | 2〜3 | ○ 8（A F minor／B B♭ minor） |
| ⑦笙 | 4（疑いの5本は除外） | 2 | 在庫 |
| ⑧龍笛 | 10 | 1〜2 | 在庫 |
| ⑨琵琶 | 18 | 3〜4 | 在庫 |
| ⑩フル編成 | 9（Em寄り） | 2〜3 | ○ 4（F major） |

## 守ること（Vol.17と同じ）

1. 長さを縮める語（short・stop・brief・staccato 等）を書かない
2. 人声の合図（mouth・breath・voice・sing）を書かない。胡弓は否定語を必ず残す
3. `chime`・`wind` を書かない
4. 末尾の定型句と否定語8つは削らない
5. 保存名は `v18_箏A-1.wav` の形（` (1)` を付けない）
6. 長さはカスタム 3:30（スライダーに focus→ArrowRight。KCFで尾切れゼロ）
7. 取得は Studio → Export → Multitrack（通常Downloadは使わない）。全本 volumedetect（無音検出）と vocalcheck

## 箏A（F major・陽音階・中高音）

```
Japanese ambient in F major, 50 BPM, for solo koto alone, in the bright yo pentatonic scale. Nothing is bowed or blown anywhere in the piece: no strings, no flute, no piano, no drone, no synth pad. Single plucked notes in the middle and upper register, each one allowed to ring out and fade completely before the next begins, with a long, patient space around every phrase. Clear, gentle and welcoming.
Recorded outdoors in a quiet garden at night, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 箏B（B minor・低い弦・押し手）

```
Japanese ambient in B minor, 44 BPM, for solo koto alone, played on the low, thick strings. Nothing is bowed or blown anywhere in the piece: no strings, no flute, no piano, no drone, no synth pad. Deep plucked notes with slow oshide pitch bends, the left hand pressing the string so that the pitch rises and sinks as the note fades. One note at a time, never overlapping, each allowed to ring out and fade away naturally.
Recorded outdoors in a quiet garden at night, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## ピアノA（A♭ major・中音域の和音）

```
Japanese ambient in A flat major, 50 BPM, for solo felt piano alone — no strings, no flute, no koto, no bells, no synth pad, no drone. Soft, warm chords of two or three notes in the middle register, struck gently, the felt softening every attack, each chord allowed to ring out and fade completely before the next one. A simple rising figure that returns again and again, a little differently each time.
Recorded close, in a quiet wooden room, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## ピアノB（C minor・高音の単音）

```
Japanese ambient in C minor, 44 BPM, for solo felt piano alone — no strings, no flute, no koto, no bells, no synth pad, no drone. Single notes high in the upper register, struck very softly, thin and clear, each one left alone to ring out and fade away completely, with a long, patient space around every phrase. Delicate, cool and still.
Recorded close, in a quiet wooden room, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 金属A（D・大小の鉢）

```
Japanese ambient built only from struck metal singing bowls tuned around D, small and large, struck softly with a padded mallet. No melody instruments at all — no piano, no koto, no flute, no strings, no drone. Each strike is left alone for a long time, the overtones slowly beating against each other as they fade to nothing, and then the next bowl is struck. Deep, round and calm.
Recorded outdoors in a quiet garden at night, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 金属B（G・小さな鈴）

```
Japanese ambient built only from small bright struck metal bowls and a small temple rin bowl tuned around G, struck lightly with a thin wooden striker. No melody instruments at all — no piano, no koto, no flute, no strings, no drone. High, clear, glassy tones, each strike allowed to ring out and fade away completely before the next, sometimes two bowls a fourth apart sounding together. Bright, pale and still.
Recorded outdoors in a quiet garden at night, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 胡弓A（F minor・低く長い弓）

```
Japanese ambient in F minor, 46 BPM, for a single bowed string instrument alone — a kokyu, small and reedy, bowed very slowly in its low register. Nothing is plucked or struck anywhere in the piece: no koto, no piano, no bells, no percussion, no drone. Long bow strokes, each note swelling and then fading away naturally, the hair of the bow audible on the string and the wooden body resonating. Plaintive, warm and patient.
Recorded outdoors in a quiet garden at night, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## 胡弓B（B♭ minor・高音・ゆるいポルタメント）

```
Japanese ambient in B flat minor, 50 BPM, for a single bowed string instrument alone — a kokyu, thin and nasal, bowed in its upper register. Nothing is plucked or struck anywhere in the piece: no koto, no piano, no bells, no percussion, no drone. Slow sliding portamento between notes, a slight wavering vibrato on the long held tones, each phrase allowed to fade away completely before the next. Pale, cool and lonely.
Recorded outdoors in a quiet garden at night, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```

## フル編成（F major）

```
Japanese ambient instrumental in F major, 60 BPM. Felt piano, koto, a low shakuhachi, warm sustained strings, and one deep struck bowl. A tiny thatched tea house in a frosted moss garden under the full moon, the path swept and the gate left open for a guest. Wide, generous, warm and quietly moving, the one moment the whole picture opens up. Calm and spacious mix.
Recorded outdoors in a quiet garden, very little reverberation.
A long, continuous, slowly unfolding piece with no clear sections and no ending.
It continues in this same way for many minutes.
For relaxation, reading, meditation and study.
Pure instrumental. No lyrics. No vocals. No vocalise. No choir. No humming. No wordless singing. No aahs. Instruments only.
```
