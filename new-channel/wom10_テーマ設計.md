# Quiet Origins 第10話「クランプス」：テーマ設計と台本 v02（2026-11-02 Claude）

管理ID：`wom10`。状態：**台本v02を本人承認（2026-11-02「その他は大丈夫です」：台本v02・ショートK3の差し替え）。公開日は11/8（日）09:00（本人決定：第9話本編の2日後）。台本JSON `episodes/EP010_Krampus/records/content_en.json`・`content.json` と[制作依頼](wom10_制作依頼_20261102.md)を作成。** v01の確認4点は本人了承済み（2026-11-02「公開日はもっと早くにしますが大丈夫です」：題・扱い・素材探し依頼。公開日は11/21より早め、日付は本人が決める）。v02は、Codexの[原典照合](research/wom10_原典訳文_20261102.md)（13項目）と[素材候補](wom10_素材候補_20261102.md)（一次共有、CC0絵はがき4点）に合わせて、言い方を資料に合わせた版（変更点は末尾）。v01はGitの履歴（`2c2b08d`）。音声・映像は未制作。エピソードのフォルダは `episodes/EP010_Krampus/`（v02の本人承認後に台本JSONを作る）。

## 狙い

- 題（本人了承）：**Krampus: Is He Really Older Than Christmas?**／クランプスは本当にクリスマスより古いのか
- 冒頭の問い：12月5日の夜、アルプスの町を角と毛皮の怪物が鎖を鳴らして歩く。「キリスト教より古い、冬の異教の精霊だ」とよく言われる。では、いちばん古い記録には何が書かれているのか。
- 結論（照合後）：
  1. 聖ニコラウスは「4世紀のミュラの司教だったこと以外、歴史的に確かなことはほとんどない」（カトリック百科事典1911）。『黄金伝説』（13世紀、約1260年）の英訳では、ニコラウスは夜、貧しい男の**家の中へ**金を投げ入れ、三人の娘が嫁げるようにする（**3回**。英訳に「窓」はない。窓は絵画の図像）。
  2. ニコラウスの祝日はやがて子どもへの贈り物と結びつき、土地によっては訪問のときに子どもの行いを問うた。**最初期の年代・地域は未確認なので、年代を言わない。**
  3. 悪魔の供は、記録の上では**キリスト教のニコラウスの習わし**（劇・家回り）の中に現れ、聖人の権威の下に置かれる。**最初期の年代は未確定**（チロルのマトライで1736・1744年の司教側の苦情などが紹介されるが、初出とはしない）。
  4. 名前は地方ごとに違う（クネヒト・ループレヒト、クラウバウフ、クランプス）。「クランプス」の語源は**定まっていない**（かぎ・かぎ爪の語と結びつける説がある）。
  5. 1869年、オーストリア＝ハンガリーが世界初の公式はがきとよく言われるものを導入（オーストリア郵便・USPSの公式史）。その後、ニコラウスの季節のはがきが**多く**刷られた（部数は言わない）。Wien Museumの1909・1911年の多色石版の絵はがきに、長い舌・鎖・枝束・子どもを背負う姿。
  6. 異教起源の考え：19世紀のグリムは「異教の時代にも、季節の神が愉快な妖精や小人を従えていたと想像できる」と書いた（**推論であって記録ではない**）。ペルヒテン（本来1月6日前後）とニコラウスの習わしは、**少なくとも18世紀には地域によって混ざっていた**（インスブルック大学）。古い冬の習わしが仮面や毛皮に影響した可能性は否定しない。
  7. 20世紀には、クランプスで子どもを怖がらせる教育への**批判**があった（1929年の新聞など）。国による禁止は確認できないので言わない。今もアルプスでクランプスの行列が人を集め、ここ数十年でアルプスの外にも広まった。
- 尺の目標：**約6分**（v02で英語741語・日本語2,024字（P01〜P14）。第8話712語＝347.6秒から見て約6分）。
- 公開日：**11/8（日）09:00**（2026-11-02 本人決定。同日18:00に作り直しショートA1R。1日の上限内）。

## 注意して扱う点

- **「異教の神ではなかった」と断定しない**。言うのは「残る記録はキリスト教のニコラウスの行事から始まる」「古代の文献にクランプスの名はない」「より古い根がある可能性は否定できない」まで。主語を保つ（「グリムは〜と想像した」）。
- **生きている行事として敬意を持つ**：今もアルプスの町で続く行事（クランプスラウフ）を、迷信や見世物として笑わない。地域の差を「ばらばら」ではなく「谷ごとに違う」と言う。
- **ズワルテ・ピート（オランダのニコラウスの供）は扱わない・映さない**。黒塗りの化粧の問題があるため。供の名を並べる区間でも挙げない。オランダのシンタクラースの版画は、供が写っていないものだけ。
- **絵はがきの選び方**：子どもをかごに入れる・枝で打つ場面は、怖さが強すぎないものを小さめに。**大人の女性を相手にした色っぽい絵はがき・政治風刺・民族を揶揄する絵はがきは使わない**。
- **20世紀の禁止の話**（1930年代や戦後に「禁止された」とよく言われる話）は、法令・指令が確認できないので台本に入れない。言うのは「子どもを怖がらせる教育への批判があった」まで。
- **ナチス期・現代映画（2015年の映画など）・ゲームの画像には触れない・使わない**。
- **引用は公有の英訳の原文どおり**（『黄金伝説』は William Caxton 訳を F. S. Ellis が編んだ版（1900））。v02では画面に引用文を出さない（Codexの確認は翻刻・OCRの段階で、刊本の頁の目視は未了のため）。
- **年代を言わない所**：子どもの習わしの始まり、悪魔の供の最初期、名前の初出。照合で確定していないため「やがて」「記録に現れるとき」と言う。
- **「ヘルの息子」の話は扱わない**（全古文献に無いとは言えず、触れると説明が長くなる）。
- **過去の場面の再現はAIで作らない**。クランプス・ニコラウス・子ども・行列はAIで作らない。
- **第8・9話の教訓**：最初からカラー素材を半分以上（絵はがきは多色石版でカラー、ニコラウスの祭壇画もカラー）。白黒の版画には暖かい単色の色調。文字カードは砂色の地に濃い茶色、**上下中央・主要行60px以上**、図の箱の内側の余白も測る。

## 出典（照合後。詳しくは[原典照合](research/wom10_原典訳文_20261102.md)）

| ID | 出典 | 台本 | 照合の結果と台本での扱い |
|---|---|---|---|
| K-S01 | Michael Ott, "St. Nicholas of Myra," *Catholic Encyclopedia* vol. 11（1911）（翻刻） | P03 | 「4世紀のミュラの司教だったこと以外、確かなことはほとんどない」。v01の言い方を維持 |
| K-S02 | 『黄金伝説』Caxton訳・Ellis編（Temple Classics 1900）巻2 聖ニコラウス（Fordham大学の翻刻） | P03 | 夜・家の中へ・3回・三人の娘。**「窓」を削る**。Metのビッチ・ディ・ロレンツォ（88.3.89）は窓から投げる図像（館の解説） |
| K-S03 | Wien Museum、Breuss「Der Krampus」（2020） | P04・P05 | 子どもの習わし・悪魔の供の最初期の年代は**未確認**。年代を外す |
| K-S04 | インスブルック大学「Klaubauf」 | P05・P06・P09 | マトライの1736・1744年の苦情、1816年の照会（原文書は未確認、初出としない）。クラウバウフの地域。ペルヒテン（1月6日前後）とニコラウスの習わしが少なくとも18世紀には混ざっていた |
| K-S05 | 米国議会図書館 Winick「Krampus」（2025-12-03） | P06・P11 | 語源は未確定（Krampe等の説）。20世紀の批判（1935年の新聞）。2000年代の米国での紹介、1962年の米国のKrampus Ball |
| K-S06 | オーストリア郵便の公式沿革、USPS公式史、聖ベネディクト大学図書館 | P07 | 1869年の官製はがき導入（10月1日）。「世界初の公式はがきとよく言われる」を支持 |
| K-S07 | Wien Museumの絵はがき（1909・1911、CC0、多色石版） | P07・P08 | 長い舌・鎖・枝束・子どもを背負う姿。印刷部数は未確認（`by the thousands` を削る）。*Gruß vom Krampus!* の文字の実物は未確保 |
| K-S08 | Grimm, *Teutonic Mythology*, tr. Stallybrass, vol. II（1883）（OCR） | P09 | 「異教の時代にも…愉快な妖精や小人を従者として…想像できる」。推論として紹介。初版1835年の同文は未確認なので年は言わず「19世紀」 |
| K-S09 | Breuss（1929年の *Die Frau*・*Arbeiter-Zeitung* の批判） | P11 | 教育上の批判。禁止は言わない |

## 台本（英語・メイン）v02

章は5つ。P02のあとにオープニング（4秒）を入れる。

### C01 The Dark Companion

**P01** On the night of December fifth, in towns across the Alps, a shaggy figure with horns, a long red tongue, and rattling chains comes through the streets. His name is Krampus. He walks beside Saint Nicholas, the kind bishop who brings gifts, and he has come for the children who misbehaved. People often say that Krampus is far older than Christmas, an ancient pagan spirit of winter. But what do the oldest records actually show?

**P02** In this episode, we follow Krampus from a bishop's legend, to the devils of old Nicholas customs, to a wave of colorful postcards, and finally to the question of how old he really is.

（ここでオープニング）

### C02 The Bishop Who Brought Gifts

**P03** Krampus begins with his companion. Saint Nicholas is said to have been a bishop of Myra, in what is now Turkey, in the fourth century. Almost nothing about his life is known for certain. But his legends spread across Europe. In one of the best known, told in the thirteenth-century Golden Legend, Nicholas secretly throws gold into a poor man's house at night, so that his three daughters can marry. He does it three times.

**P04** Over time, the saint's feast day, December sixth, became linked with gifts for children. In some places, his visit also came with a question: had the children been good? The giver of gifts had also become a judge. And a judge, it seems, needed someone to carry out the sentence.

### C03 Devils in the Saint's Service

**P05** When Nicholas's dark companions appear in historical accounts, they belong to these Christian customs: plays, and visits to homes. Nicholas arrives with figures dressed as devils, in masks, furs, and bells. In these Christian settings, the devil is brought under the saint's authority. Even the frightening companion works for the saint.

**P06** The companions had many names. In much of Germany, Knecht Ruprecht. In parts of Tyrol and Carinthia, Klaubauf. In Austria, Krampus. The origin of that name is uncertain, though it is often linked to an old word for a hook or a claw. The name, the costume, and the role changed from valley to valley. There was never just one Krampus.

### C04 A Devil on a Postcard

**P07** The Krampus most people picture today owes a great deal to the postcard. In 1869, Austria-Hungary introduced what is often called the world's first official postcard. In the decades that followed, many colorful cards for the Nicholas season were printed, and Krampus appeared on many of them.

**P08** On these cards, Krampus took a familiar shape: dark fur, horns, a long red tongue, chains, a bundle of twigs, and sometimes children carried off on his back. Some cards were meant to frighten. Others turned him into a striking piece of design. These cards, from a Vienna workshop around 1910, are now kept in a city museum.

### C05 Older Than Christmas?

**P09** So where does the idea of a pagan Krampus come from? In the nineteenth century, writers such as Jacob Grimm looked for traces of a pre-Christian past in later customs. Grimm wrote that he could well imagine that even in heathen times, a god whose coming heralded a happy time had a merry elf or dwarf at his side. He was imagining, not quoting a record. Masked winter processions, like the Perchten runs held around early January, seemed to fit such ideas. And in some places, these customs had already mixed with the Nicholas custom by the eighteenth century.

**P10** It is possible that older winter customs shaped the masks and furs. But no ancient text names Krampus, and the accounts we have place him inside the Christian Nicholas custom.

**P11** In the twentieth century, some critics questioned the use of Krampus to frighten children. Yet the custom lived on. Today, Krampus runs draw large crowds in the Alps, and in recent decades he has found new audiences far beyond them.

**P12** So, is Krampus older than Christmas? The records tell a different story. He appears as a devil in the service of a saint, goes by many names in the Alps, and gets his famous face from printed cards. His roots may run deeper. But as far as the sources can show, his story begins with a bishop who brought gifts.

**P13** Every story has an origin. Sometimes, it begins with a knock at the door on a winter night.

**P14** This video is based on historical texts and public museum collections. The narration uses synthetic speech. Sources and terms of use are listed in the description. If you enjoyed this story, please like the video and subscribe for more quiet origins. Thank you for watching.

## 台本（日本語）v02

**P01** 12月5日の夜、アルプスの町々を、角を生やし、長く赤い舌を垂らした毛むくじゃらの姿が、鎖を鳴らしながら通りを歩きます。その名はクランプス。贈り物を届けるやさしい司教、聖ニコラウスのそばを歩き、悪い子どもたちのもとへやって来ます。クランプスはクリスマスよりずっと古い、冬の異教の精霊だ、とよく言われます。では、いちばん古い記録には、何が書かれているのでしょう。

**P02** 今回は、一人の司教の伝説から、昔のニコラウスの行事に出てくる悪魔たちへ、色あざやかな絵はがきの流行へ、そして最後に、クランプスは本当はどれほど古いのかという問いへと、たどっていきます。

**P03** クランプスの話は、その連れから始まります。聖ニコラウスは、4世紀、今のトルコにあったミュラの町の司教だったと伝えられます。その生涯について確かなことは、ほとんど分かっていません。けれど彼の伝説は、ヨーロッパ中に広まりました。よく知られた話の一つが、13世紀の『黄金伝説』に語られています。ニコラウスは夜、人知れず貧しい男の家に金を投げ入れ、その三人の娘が嫁げるようにしたのです。それも、三度にわたって。

**P04** やがて、聖人の祝日である12月6日は、子どもへの贈り物と結びつきます。土地によっては、聖人の訪問に、ひとつの問いがついてきました。子どもたちは、良い子にしていたか。贈り物をくれる人は、裁く人にもなったのです。そして裁く人には、どうやら罰を下す役が必要でした。

**P05** ニコラウスの暗い連れが記録に現れるとき、彼らはこうしたキリスト教の行事の中にいます。劇や、家々を回る訪問です。ニコラウスは、仮面をつけ、毛皮をまとい、鈴を下げた悪魔の姿の者たちを連れてやって来ます。こうしたキリスト教の場では、悪魔は聖人の権威の下に置かれます。恐ろしい連れでさえ、聖人のために働いているのです。

**P06** 連れの名前は、さまざまでした。ドイツの多くの地域ではクネヒト・ループレヒト。チロルやケルンテンの一部ではクラウバウフ。オーストリアではクランプス。この名の由来ははっきりしませんが、かぎや、かぎ爪を表す古い言葉と結びつけて説明されることが多い名前です。名前も、衣装も、役目も、谷ごとに違っていました。クランプスは、一人ではなかったのです。

**P07** 今、多くの人が思い浮かべるクランプスの姿は、絵はがきに負うところが大きいのです。1869年、オーストリア＝ハンガリーは、世界初の公式のはがきとよく言われるものを導入しました。それから数十年のうちに、ニコラウスの季節の色あざやかなはがきが数多く刷られ、その多くにクランプスが登場しました。

**P08** はがきの上で、クランプスはおなじみの姿になっていきます。黒っぽい毛皮、角、長く赤い舌、鎖、小枝の束。ときには、子どもたちを背負って連れ去る姿も。怖がらせるためのはがきもありました。一方で、目を引くデザインの作品になったはがきもあります。ここに映る、1910年ごろにウィーンの工房で作られたはがきは、今、市の博物館に収められています。

**P09** では、異教のクランプスという考えは、どこから来たのでしょう。19世紀、ヤーコプ・グリムのような書き手たちは、後の時代の行事の中に、キリスト教以前の過去の名残を探しました。グリムは、異教の時代にも、幸せな時の訪れを告げる神が、愉快な妖精や小人をそばに従えていたことは十分想像できる、と書いています。それは想像であって、記録の引用ではありません。年明けごろに行われるペルヒテンのような、仮面をつけた冬の行列は、こうした考えにぴったり合うように見えました。そして土地によっては、こうした行事は、18世紀にはすでにニコラウスの行事と混ざり合っていたのです。

**P10** より古い冬の習わしが、仮面や毛皮の姿に影響した可能性はあります。けれど、クランプスの名を記した古代の文献はありません。そして残る記録は、彼をキリスト教のニコラウスの行事の中に置いています。

**P11** 20世紀には、クランプスで子どもを怖がらせることへの批判も出ました。それでも、行事は続きました。今では、アルプスでクランプスの行列が大勢の人を集め、ここ数十年で、アルプスの外でも新たな人々に知られるようになりました。

**P12** では、クランプスはクリスマスより古いのか。記録が語るのは、別の物語です。聖人に仕える悪魔として現れ、アルプスでさまざまな名で呼ばれ、刷られたはがきでおなじみの顔になった。その根は、もっと深いところにあるのかもしれません。けれど資料でたどれるかぎり、彼の物語は、贈り物を届けた一人の司教から始まっています。

**P13** どの物語にも由来がある。ときには、それは冬の夜に戸をたたく音から始まります。

**P14** この動画は、歴史上の文献と公開された美術館のコレクションをもとに構成しました。ナレーションには音声合成を使っています。出典と利用条件は概要欄にまとめています。楽しんでいただけたら、高評価とチャンネル登録をお願いします。ご覧いただき、ありがとうございました。

## 画面の構成（v02案）

確定版のショット割りは制作依頼で決める。同じ素材は1本の中で1回だけ。第1〜9話で使った作品は使わない。素材は[素材候補](wom10_素材候補_20261102.md)の14点（カラー10・白黒4、所蔵館のCC0／Public Domain Mark）。**絵はがき・祭壇画は縦長なので、横の画面では左右をぼかし背景で埋めるか、絵の一部へ寄る。**

| 区間 | 見せたいもの | 素材 |
|---|---|---|
| P01 | クランプス（0秒から全面で動かす） | **K01a**（Divéky 1909、黒い毛皮・長い舌・鎖）。顔から全身へゆっくり引く。かごの人物は年齢を断定しない |
| P02 | 道すじの予告 | **K06a**（1911、司教と緑の悪魔） |
| P03 | 聖ニコラウス・持参金 | **K05b**（14世紀のステンドグラスの聖ニコラウス）→「Golden Legend」から **K04a**（ビッチ・ディ・ロレンツォ《Saint Nicholas Providing Dowries》1433–35）。絵は窓から投げる図だが、語りは英訳どおり「家の中へ」。札は作品名だけ |
| P04 | 祝日・子ども | **K05c**（祝福する司教・聖ニコラウスの彩色木彫）→ 文字カード D_dec6「DECEMBER 6」 |
| P05 | 悪魔の供（キリスト教の場） | **K09b**（エンス谷のニコラウス劇の演者15人の写真、Volkskundemuseum PDM。**19世紀の写真で16世紀の資料ではない**と札に年代）。左端の武器に寄らない |
| P06 | 名前の違い | 地図の模式図（Knecht Ruprecht／Klaubauf／Krampus。札「DIAGRAM｜模式図」） |
| P07 | 1869年のはがき | 文字カード「1869 · FIRST OFFICIAL POSTCARD」（実物の画像は未確保）→ **K06b**（Divéky 1909、ニコラウスとクランプス） |
| P08 | おなじみの姿・デザイン | **K03a**（1911、赤い悪魔と枝束）。**子どもと舌の部分を大きく映さず**、枝束・角の上半分へ寄る |
| P09 | グリム・ペルヒテン | 文字カード（グリムの一文の要約、`IMAGINED, NOT RECORDED`）→「Perchten」から **K09a**（ザンクト・ヨハン・イム・ポンガウのJagdpercht、写真。**クランプスではない**、撮影日を1月と書かない） |
| P10 | 古代の文献にない | 文字カード「NO ANCIENT TEXT NAMES KRAMPUS」（上下中央・大きめ） |
| P11 | 今も続く行事 | **K07b**（ウィーンのナッシュマルクトのクランプスとニコラウスの人形の店、1915、Wien Museum CC0、色票は外す） |
| P12 | まとめ | 模式図（4世紀 ニコラウス → 13世紀 黄金伝説 → 記録の中の悪魔の供 → 1869〜 絵はがき → 19世紀 グリムの想像）。**悪魔の供の箱には年を書かない**。箱の内側の余白を測る |
| P13 | 冬の夜の余韻 | **K10a**（《Winter Scene in Moonlight》、Met。アルプスの景色とは言わない） |
| P14 | エンドカード（共通版v02、10秒） | — |

使わない素材：K05a・K05d（三少年の別の伝説で、裸体の少年が写る）、K07a（デューラーの騎士・死・悪魔。クランプスと関係がない）。グリム英訳・黄金伝説の頁画像（Internet Archiveの表記が所蔵館の明示PD/CC0でない）。AI映像は使わない。BGMは既存の `QO_THEME_A02`（新規生成・課金なし）。

## ショート（v02案。本編の承認後に制作依頼）

第9話の型（0秒の大見出し・全面の絵・0秒から動き・0秒からBGM・字幕は文の切れ目・最後の2.5秒に大きな登録の案内）。

| # | 見出し（案） | 中身 |
|---|---|---|
| K1 | **KRAMPUS WORKS FOR A SAINT** | 記録の上では、クランプスはキリスト教のニコラウスの行事の中に現れ、聖人の権威の下にいる |
| K2 | **THE POSTCARD THAT MADE KRAMPUS** | 1869年の公式はがき→1910年ごろのウィーンの絵はがき（K01aなど） |
| K3 | **GOLD THROUGH THE WINDOW?** | 『黄金伝説』の英訳では「家の中へ」、窓は絵の中の伝え方（ビッチ・ディ・ロレンツォの絵）。v01のK3「ヘルの息子」は本編から外したのでやめる |

ショートの公開は、本編の公開日と翌日（1日の本数の上限：本編とショートで3本、ショートは2本まで）。

## 第9話で学んだことの反映

| 項目 | 第10話での扱い |
|---|---|
| 本編の冒頭 | 0秒から主役（クランプスの絵はがき）を全面で動かす |
| 色 | カラー素材を半分以上。文字カードは砂色の地に濃い茶色、上下中央・主要行60px以上 |
| 図 | 箱の内側の余白を測る（第9話v02の箱からはみ出しの再発防止） |
| ショート | 案内は横に縮めず字高で収める。字幕は文の切れ目。小さな原寸素材は原寸1.6倍まで、画面の高さの7割程度 |
| AI | なしで作るのが第一案（Kling残高315のまま） |
| 保存 | 原寸素材と完成品は本人指定のSSD **ESD-02**（`/Volumes/ESD-02/新チャンネル/EP010_Krampus/`） |

## v01からの変更点（原典照合の反映）

| 区間 | v01 | v02 | 理由 |
|---|---|---|---|
| P03 | throws gold through a window | into a poor man's house、3回 | 英訳に「窓」はない（照合2） |
| P04 | By the end of the Middle Ages … gifts were left the evening before | Over time … linked with gifts for children | 年代・地域が未確認（照合3） |
| P05 | appear clearly in records from the 16th and 17th centuries／not pagan gods … defeated | When … appear in historical accounts, they belong to these Christian customs／brought under the saint's authority | 最初期の年代は未確定。「異教ではない」の断定を避ける（照合4） |
| P06 | In Tyrol, Klaubauf／In Austria and Bavaria／often linked to a claw | parts of Tyrol and Carinthia／In Austria／origin is uncertain | クラウバウフの地域、語源は未確定（照合5） |
| P07 | printed by the thousands／many carried "Greetings from Krampus" | many colorful cards … Krampus appeared on a great number of them | 部数は未確認。文字入りの実物も未確保（照合7） |
| P08 | birch twigs／basket／chased away by the children | twigs／children carried off on his back／design・Vienna workshop・city museum | 植物を断定しない。冗談の実物が未確保。選んだ絵はがきに合わせた（照合8） |
| P09 | scholars … went searching／Krampus and the Perchten spoken of together | Grimmの「想像できる」を推論として紹介／18世紀には地域によって混ざっていた | 照合9・10 |
| P10 | 「ヘルの息子」の2文 | 削除 | 全称否定が強すぎる（照合11） |
| P11 | at times discouraged, and at times revived／known around the world | critics questioned … frighten children／new audiences far beyond the Alps | 禁止は未確認、復興の年代も未特定（照合12・13） |
| P12 | takes his name in the Alps | goes by many names in the Alps | 名前の初出が未確定 |

## 本人に確認したいこと（v02）

1. **台本v02**（上）でよいか。照合で確かめられなかった年代（子どもの習わしの始まり、悪魔の供の最初期）は言わない形にした。
2. **ショートK3の差し替え**：v01の「ヘルの息子」をやめ、**GOLD THROUGH THE WINDOW?**（英訳では家の中へ、窓は絵の伝え方）にしてよいか。
3. **公開日**：何日の09:00にするか（11/21より前。作り直しショートは11/8〜11/12の18:00）。制作の目安は、素材がそろってから確認版まで約2〜3日。
