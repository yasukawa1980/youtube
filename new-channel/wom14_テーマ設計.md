# Quiet Origins 第14話「鬼はなぜ虎の皮を着ているのか」：テーマ設計と台本 v02（2026-11-09 Claude）

管理ID：`wom14`（神話シリーズ第14話。第13話は欠番、「夜警」は絵画01）。状態：**台本v02を本人承認（2026-11-09「このまま進める」：尺は約8分40秒のまま、サムネはA・Bを168pxで比べる）。台本JSON `episodes/EP014_Oni/records/content_en.json`・`content.json` と[制作依頼](wom14_制作依頼_20261109.md)を作成。** v01は本人了承済み（2026-11-08「推奨どおりでOK」：題は案A *Why Do Japanese Oni Wear Tiger Skin?*、公開の目安11/18（水）09:00（間に合わなければ11/20）、説4は根拠が確かめられたときだけ、人を食う話は語りで短く絵は使わない）。v02はCodexの[原典照合](research/wom14_原典訳文_20261109.md)と[素材候補](wom14_素材候補_20261109.md)（映像候補22作品・原典照合用7頁、過去回との重複なし）に合わせて直した版（変更点は末尾）。v01はGitの履歴（`e6579ccd`）。音声・映像は未制作。エピソードのフォルダは `episodes/EP014_Oni/`（制作依頼のときに作る）。

## この回で試すこと：通説の点検型

第12話は本人決定の「変遷型」（年代の帯・並べ直しカード）だった。第14話は型を変え、**よく言われる説明を4つ挙げ、一つずつ古い資料で確かめる「通説の点検型」**にする。コンセプト（最古の資料で確かめる・静かな語り・Kokoroの声・AI映像なし）は変えない。変える要素は次の3つに絞る。

| | 第12話（変遷型） | 第14話（通説の点検型） |
|---|---|---|
| 章の立て方 | 年代ごと | **説ごと**（説1〜4。各章の中は年代順） |
| 画面 | 画面下の年代の帯、並べ直しカード3回 | **点検カード**：4つの説を左に並べ、確かめるたびに右へ判定の札を押す。全部で6回（P02で一覧、説1〜4の終わりで1枚ずつ、P14でそろった一覧）。札は真偽の二択にしない：`NOT IN THE OLDEST RECORDS`／`AN OLD GUESS`／`A LATER EXPLANATION`／`THE ROLES CHANGED` |
| サムネ・題 | 年つきの絵を2〜3点並べる | **鬼の顔1点を全面＋問いの短い大文字**。案A `WHY TIGER SKIN?`、案B `THE FIRST ONI WORE A HAT`（「著大笠」の原文の小さな切り出しを添える） |

効果は、本編の表示回数の出どころとクリック率を第9〜12話と比べて見る。日本の回は第5話以来なので、視聴者の地域（日本が約4割、10/27時点）の変化も見る。

## 第5話（天狗）との違い

| | 第5話 天狗 | 第14話 鬼 |
|---|---|---|
| 型 | 姿の移り変わりを一本の線でたどる | 4つの通説を一つずつ点検する |
| 『日本書紀』 | 巻23 舒明9年（637）の「天狗」＝音を立てる流れ星 | **巻26 斉明7年（661）の「鬼」**＝朝倉山の上の、大きな笠をかぶった者。北野本の複製（NDL）で、第5話と別の本・別の巻 |
| 新しい資料 | — | 『出雲国風土記』（733）、『和名類聚抄』（930年代）、『伊勢物語』、北野天神縁起絵巻（13世紀後半）、鳥山石燕（1779）、『続日本紀』（706）、『江家次第』、1447年の日記 |

## 狙い

- 題（本人了承 11/8）：**Why Do Japanese Oni Wear Tiger Skin?**／鬼はなぜ虎の皮を着ているのか
- 冒頭の問い：赤や青の肌、角、虎の皮の腰巻き、金棒。いまの鬼はこの姿で知られ、その理由もいくつか語られている。では、いちばん古い記録の鬼は、どんな姿だったのか。
- 結論（照合後）：
  1. **説1「鬼は昔からこの姿」**：最古級の二つの記録に、角・虎の皮・金棒は書かれていない。『日本書紀』斉明天皇7年（661）8月1日、皇太子が天皇の亡骸を奉じて磐瀬宮に戻ったその夕べ、朝倉山の上に**大きな笠をかぶった鬼**がいて、喪儀を見下ろしていた。1896年のアストンの英訳は「demon」とし、注に「Or spirit.」と添える。『出雲国風土記』（733年勘造）の阿用郷では、**一つ目の鬼**が田を耕す人の息子を食い、息子が「あよ、あよ」と言ったのが地名の由来とされる。
  2. **説2「おに＝隠（おん）」**：930年代の『和名類聚抄』（元和3年＝1617年の那波道円本で確認）は「或説云」（ある説では）として載せる。鬼は隠れて形を現したがらないから、と。同じ項は「人死魂神也」（人が死んだ魂）とも書く。**千年以上前からある説だが、当時から「ある説」**。10世紀ごろの『伊勢物語』第6段では、鬼が女を一口に食うが、姿は語られず、段の終わりの注は、その「鬼」は実は女を取り返した兄たちだったと明かす。
  3. **説3「角と虎の皮は鬼門＝丑寅だから」**：鳥山石燕『今昔画図続百鬼』（初刊1779年。1805年の本で確認）の「鬼」の解説に、世に丑寅の方を鬼門といい、いま鬼の形を描くには頭に牛の角、腰に虎の皮をまとわせ、丑と寅を合わせた形だと**言われている**（「といへり」）とある。角のある者は13世紀後半の北野天神縁起絵巻（Met）にすでに描かれている。石燕より古い文献（1756年の『牛馬問』など）は手掛かりだけで未照合なので言わない。**説明が先か絵が先かは、資料からは分からない**。
  4. **説4「鬼は追い払われる側」**（範囲を絞って残す）：疫病を払う宮中の大儺は『続日本紀』慶雲3年（706）に記録がある。平安後期の『江家次第』の追儺では、方相（ほうそう）が儺の声を上げ、戈で楯を三度たたき、群臣が声を合わせて追う。そして**殿上人が方相を射る**。追う役が、射られる側にもなっている。一方、豆で鬼を打つことは1425年の『看聞日記』に「近年」のこととして出て、1447年の『臥雲日件録』は「鬼は外、福は内」と唱えるのを「この国の儺を追うやり方だろう」と書く。**706年の儀式から今の家庭の豆まきまで一本の線で続いた、とは言わない。**
- 尺：本人指定で6分に合わせない。v02は英語1,042語・日本語2,367字で、話速が第12話と同じなら**約8分40秒**の見込み（第12話は835語で6分58.5秒からの比例）。照合で足した文（アストンの注・後注・江家次第・1447年）で長くなったので、背景の文（5月条・説文の字書・重複する言い換え）を削って1,141語から縮めた。それでも本人了承の目安（7〜8分）を超える。
- 公開日：**11/18（水）09:00**（本人了承の目安）。

### 公開日の照合（2026-11-09、リポジトリの記録だけ。Studioの画面では未確認）

| 日 | 本編 | ショート | 合計 | メモ |
|---|---|---|---|---|
| 11/14（土） | 第12話 09:00、または前倒し案なら絵画01 | 1〜2 | 2 | |
| 11/15（日）・11/16（月） | — | 1〜2 | 1〜2 | 前倒し案しだい |
| 11/17（火） | — | 0 | 0 | |
| **11/18（水）** | **第14話 09:00** | ショートO1は18:00の案 | 2 | O2・O3は11/19・20の12:00の案 |
| 11/21（土） | 絵画01（前倒しをしない場合） | | | |

制作の目安：v02の承認が11/9〜10なら、確認版v01は11/12〜13、Claude確認と本人試聴11/14〜15、予約11/16〜17。遅れたら11/20（金）09:00にずらす。予約の前にStudioで当日の本数を数え直す。

## 注意して扱う点

- **人を食う話（阿用郷・伊勢物語）は語りで短く**。食べる場面の絵は使わない。
- **661年の時点**：「葬列が出発した」ではなく「皇太子が亡骸を奉じて磐瀬宮に戻ったその夕べ」。日付は旧暦の月日で、西暦の月日に置き換えない。鬼の正体（後世の説）には触れない。
- **5月条（朝倉社の木・神の怒り・病死・鬼火）は尺のため語らない**。鬼火の細字は判読保留なので、今後も言わない。
- **「鬼」の字**：中国の古い字書（『説文解字』）の「人所帰為鬼」は、Web翻刻でしか確かめていないので、**書名も原文も出さず**、語りは「死者の霊と結びついていた」にとどめる。『和名類聚抄』の「人死魂神也」は原頁で確認済みなので、こちらを画面の根拠にする。
- **「目一鬼」**：縦書きの改行をまたぐので「一目」と読み違えない。「あよ」と言うのは食べられる息子で、鬼が竹を揺らしたとは言わない。
- **『伊勢物語』**：「誰も見なかった」とは言わない。「姿を語らない」と言う。後注の人名（二条の后・堀川のおとど・国経）は台本で言わない。
- **鬼門の説は「石燕が書き留めた、世に言われる説明」**。石燕の創作とも、誤りとも言わない。より古い文献の年（1445〜46年・1532年・1756年）は言わない。
- **北野天神縁起絵巻**：13世紀後半（Metの年代）。12世紀と言わない。地獄の責め苦の場面は使わない。角のある者を「最初の角のある鬼」と言わない。
- **方相氏の装い**：「黄金の四つ目」は1653年の刊本の裏書で確認したもの。台本の語りには入れず、画面の文字にも出さない（706年の装いの証拠ではないため）。
- **豆まき**：1425年が始まりとは言わない（日記に「近年」とある）。家庭の豆まきと宮中の追儺を同じ行事と言わない。
- **遊里・寺院の節分の絵**を家庭の実景と言わない（札は作品名と年だけ）。
- **AIで鬼・人物・場面を作らない**。AI映像は使わない。
- **読み**：Oni、Nihon Shoki、Empress Saimei、Kyushu、Ihase、Mount Asakura、W. G. Aston、Izumo Fudoki、Ayo、Minamoto no Shitagou、Wamyō Ruijushō、Tales of Ise、Kitano Tenjin、Toriyama Sekien、ushitora、Shoku Nihongi、Gōke Shidai、hōsō、Setsubun。新しい語の読み替えは制作時に記録する。日本語は、鬼、日本書紀、斉明天皇、九州、磐瀬宮（いわせのみや）、朝倉山、アストン、出雲国風土記、阿用（あよ）、源順（みなもとのしたごう）、和名類聚抄（わみょうるいじゅしょう）、伊勢物語、北野天神縁起絵巻、鳥山石燕（とりやませきえん）、丑寅（うしとら）、続日本紀（しょくにほんぎ）、江家次第（ごうけしだい）、方相（ほうそう）、臥雲日件録（がうんにっけんろく）、節分。

## 出典（照合後。詳しくは[原典照合](research/wom14_原典訳文_20261109.md)）

| ID | 出典 | 台本 | 照合の結果と台本での扱い |
|---|---|---|---|
| O-S01 | 『日本書紀』巻26 斉明7年5月・7月・8月条。貴重図書複製会『日本書紀：国宝北野本』（1940〜41年の複製、NDL 1142412、コマ22・23） | P04 | 8月1日「還至磐瀬宮。是夕於朝倉山上有鬼、著大笠、臨視喪儀。衆皆嗟怪」を画像で確認。5月条の鬼火の細字は判読保留 → 言わない |
| O-S02 | Aston *Nihongi* vol. II（1896、Smithsonian、271・272頁） | P04 | `a demon wearing a great hat, who looked down on the funeral proceedings`、脚注 `Or spirit.` |
| O-S03 | 『説文解字』巻9 鬼部「人所歸爲鬼」 | P03 | Web翻刻のみ。画面に出さず、語りは弱い言い方 |
| O-S04 | 『訂正出雲風土記』（千家俊信校、江戸後期の再版、NDL 2563532、コマ38・47） | P05 | 阿用郷の本文と「天平五年二月卅日勘造」を画像で確認。「目一鬼」「所食男云動動」 |
| O-S05 | 『倭名類聚抄』那波道円本（元和3年＝1617年、二十巻本、NDL 2544216、コマ31） | P07 | 「或説云隠字〔音於爾訛也〕鬼物隠而不欲顯形故俗呼曰隠也人死魂神也」。成立は承平年間931〜938（書誌の説明） |
| O-S06 | 『伊勢物語』佐佐木信綱校註（1892、NDL 877528、コマ18・19） | P08 | 「鬼はやひと口に喰ひてけり」、雷で声が聞こえない、後注「それをかく鬼といふなりけり」 |
| O-S07 | 北野天神縁起絵巻（Met 25.224a–e、late 13th century、PD） | P09 | 追加画像DP244660の門前に角のある者 |
| O-S08 | 鳥山石燕『今昔画図続百鬼』上（1805年の本、Smithsonian。初刊1779年はNDLイメージバンク） | P10・P11 | 「世に丑寅の方を鬼門といふ。今鬼の形を画くには、頭に牛角をいただき、腰に虎皮をまとふ。是丑と寅との二つを合せてこの形をなせりといへり」 |
| O-S09 | 『国史大系 第2巻 続日本紀』（1897、NDL 991092、コマ27） | P12 | 慶雲3年（706）是年「天下諸國疫疾。百姓多死。始作土牛大儺」 |
| O-S10 | 大江匡房『江家次第』十一（1653年跋の刊本、NDL 12865891、コマ29・30） | P12 | 「方相先作儺聲。以戈叩楯三箇度。群臣相共和呼追之」「殿上人於長橋内射方相」。研究の要旨はGRAS（2004）36〜43頁（引用しない） |
| O-S11 | 『看聞日記』応永32年（1425）正月8日（1931〜35年刊、NDL 2591323、コマ4）、『臥雲日件録抜尤』文安4年（1447）12月22日（『続史籍集覧』第3冊 1930、NDL 1920248、コマ170） | P12 | 「鬼大豆打事近年…」、「因唱鬼ハ外福内四字。蓋此方驅儺之樣也」 |

## 台本（英語・メイン）v02

章は6つ。P02のあとにオープニング（4秒）を入れる。説1〜4の章の終わりに点検カード（判定の札）を出し、札を押す音は入れず、0.9秒の間をとる。

### C01 The Oni We Know

**P01** Picture an oni, a demon from Japanese folklore. Red or blue skin, horns on its head, a loincloth of tiger skin, and an iron club in its hand. That is how oni appear today, in picture books, at festivals, and every February at Setsubun, when families throw roasted beans to drive them out of the house. But the oldest Japanese records are still here. So, why do oni wear tiger skin? And did they always?

**P02** In this episode, we check four things that are often said about oni. That oni always looked like this. That the word oni means hidden. That the horns and the tiger skin come from a direction on the compass. And that oni are the ones who get chased away. One by one, we will hold each of them up against the old sources.

（ここでオープニング）

### C02 Claim One: They Always Looked Like This

**P03** Japan's oldest official history, the Nihon Shoki, was completed in seven twenty. It is written in Chinese characters, and it uses the character that is read as oni today. In early Chinese writing, that character was tied to the spirits of the dead.

**P04** The chronicle tells of the year six sixty-one. Empress Saimei had moved her court to a temporary palace in Kyushu, in the west of Japan. That summer, she died there. Then, after the crown prince had brought her remains back to the Palace of Ihase, that evening, on the top of Mount Asakura, there was an oni. It wore a large hat, and it looked down on the funeral. Everyone who saw it cried out in wonder. When W. G. Aston translated this passage into English in eighteen ninety-six, he wrote demon, and added a note: or spirit. The chronicle says nothing about horns, tiger skin, or a club.

**P05** About seventy years after these events, in seven thirty-three, the province of Izumo completed a record of its land, the Izumo Fudoki. It explains the name of one village, Ayo, with a story. Long ago, a man was farming a mountain field. A one-eyed oni came and ate his son. The parents hid in a bamboo thicket, and the bamboo leaves stirred. As he was being eaten, the son cried out, ayo, ayo. And so the place was called Ayo.

**P06** So the first claim does not hold. In two of the oldest records, one oni wears a hat and watches in silence. The other has a single eye. Neither record mentions horns or tiger skin.

### C03 Claim Two: The Hidden Ones

**P07** The second claim is about the word itself. In the nine thirties, the scholar Minamoto no Shitagou compiled a dictionary, the Wamyō Ruijushō. Under the character for oni, he gives the Japanese reading, oni. Then he adds a note. Some say that it comes from on, the sound of the character for hidden, because oni hide themselves and do not wish to show their form. The entry ends with a short definition: the soul of a person who has died.

**P08** So the idea is very old, more than a thousand years. But even then, it came with the words some say. It is an early guess, not a proven origin. In the Tales of Ise, a collection that took shape around the tenth century, a woman is carried off on a stormy night, and an oni swallows her in a single gulp. The tale never describes the oni. And a note at the end of the episode explains that the oni was really her own brothers, who had come to take her back.

### C04 Claim Three: The Ox and the Tiger

**P09** Faces began to appear in pictures. In the Illustrated Legends of the Kitano Tenjin Shrine, a scroll painted in the late thirteenth century, strange figures with horns and wild hair gather by a gate. Over the following centuries, artists kept giving oni horns, fangs and fierce faces.

**P10** The third claim explains the horns and the tiger skin. In seventeen seventy-nine, the artist Toriyama Sekien published a book of monsters. Beside his oni, he wrote a short note. People call the northeast, the direction of the ox and the tiger, the demon gate. When oni are painted today, they wear the horns of an ox on their heads and the skin of a tiger around their waists. This shape, he says, is said to join the ox and the tiger together.

**P11** It is a neat explanation, and Sekien himself presents it as something people say. He wrote it down more than a thousand years after the oldest records, and about five hundred years after the horned figures in the Kitano scroll. Whether the picture or the explanation came first, the sources do not tell us.

### C05 Claim Four: Who Was Chased?

**P12** The last claim brings us back to Setsubun. A court rite to drive away disease is recorded in seven oh six, in a year when many people died. In a later court manual, the Gōke Shidai, from about nine hundred years ago, an official called the hōsō leads the rite. He shouts, strikes his shield three times with his spear, and the courtiers join in the cry and chase. Then the manual adds one more line: the courtiers shoot arrows at the hōsō. Beans came later. In fourteen forty-seven, a Zen monk wrote down the cry, oni out, fortune in, and called it the way demons were driven out in this land.

**P13** So the roles changed. In that court manual, the figure who led the chase also became a target. And by the fifteenth century, beans were being thrown, and the oni was the one sent outside.

### C06 So, Why Tiger Skin?

**P14** So, why do oni wear tiger skin? One explanation links it to the ox and the tiger, the unlucky northeast. Sekien recorded it in seventeen seventy-nine, long after the first oni. The oldest records show something else: a figure in a large hat on a mountain, a one-eyed creature in a mountain field, and a word that may mean hidden. The horns, the tiger skin and the club came later, through pictures.

**P15** Every story has an origin. Sometimes, it begins with something no one could see.

**P16** This video is based on historical texts and public museum and library collections. The narration uses synthetic speech. Sources and terms of use are listed in the description. If you enjoyed this story, please like the video and subscribe for more quiet origins. Thank you for watching.

## 台本（日本語）v02

**P01** 鬼を思い浮かべてみてください。赤や青の肌、頭には角、虎の皮の腰巻き、そして手には金棒。いまの鬼は、こんな姿で知られています。絵本の中にも、祭りにも。そして毎年2月の節分には、家族が炒った豆をまいて、家の外へ追い払います。けれど、日本のいちばん古い記録は、今も残っています。では、鬼はなぜ虎の皮を着ているのでしょうか。そして、昔からそうだったのでしょうか。

**P02** 今回は、鬼についてよく言われる四つのことを確かめます。鬼は昔からこの姿だった。「おに」という言葉は「隠れる」という意味だ。角と虎の皮は、方角から来ている。そして、鬼は追い払われるものだ。一つずつ、古い資料と突き合わせていきます。

**P03** 日本で最も古い正史、『日本書紀』は720年に完成しました。漢字で書かれていて、いま「おに」と読む字も使われています。古い中国の書物では、この字は死者の霊と結びついていました。

**P04** その記録は、661年のことを伝えています。斉明天皇は、都を西の九州にある仮の宮に移していました。その夏、天皇はそこで亡くなりました。そして、皇太子が天皇の亡骸を奉じて磐瀬宮に戻ったその夕べ、朝倉山の上に、鬼がいました。鬼は大きな笠をかぶり、葬儀を見下ろしていました。見た人々はみな、あやしんで声を上げました。1896年にこの箇所を英語に訳したアストンは、「デーモン」と書き、注に「あるいは霊」と添えています。角のことも、虎の皮のことも、金棒のことも、記録は何も言っていません。

**P05** この出来事からおよそ70年後の733年、出雲の国は、その土地の記録『出雲国風土記』をまとめました。そこには、阿用という村の名の由来が、ある話で説明されています。昔、ある人が山の田を耕していました。そこへ一つ目の鬼が来て、その人の息子を食べてしまいます。父と母は竹やぶに隠れ、竹の葉が揺れました。食べられながら、息子は「あよ、あよ」と叫びました。それで、この地は阿用と呼ばれるようになった、というのです。

**P06** ですから、一つ目の説は当てはまりません。最も古い記録の二つでは、一方の鬼は笠をかぶり、黙って見ています。もう一方は、目が一つ。どちらの記録も、角や虎の皮には触れていません。

**P07** 二つ目の説は、言葉そのものについてです。930年代、学者の源順は、辞書『和名類聚抄』をまとめました。「鬼」の字のところに、彼は和名「おに」を記します。そして、こう書き添えています。ある説では、「隠」の字の音「おん」がなまったものだという。鬼は身を隠し、形を現そうとしないからだ、と。この項は、短い説明で終わります。人が死んだあとの魂、と。

**P08** この考えは、とても古く、千年以上前からあります。けれど、そのころからすでに「ある説では」という言葉付きでした。確かめられた語源ではなく、早い時代の推測です。10世紀ごろに形づくられた『伊勢物語』では、嵐の夜に連れ出された女が、鬼に一口で食べられてしまいます。物語は、鬼の姿を一度も描きません。そして段の終わりの注は、その鬼とは、実は彼女を取り返しに来た兄たちのことだった、と明かしています。

**P09** 姿は、絵の中に現れ始めます。13世紀後半に描かれた『北野天神縁起絵巻』では、門のそばに、角を生やし、髪を振り乱した異形の者たちが集まっています。それからの何百年、絵師たちは鬼に、角や牙や恐ろしい顔を与え続けました。

**P10** 三つ目の説は、角と虎の皮を説明します。1779年、絵師の鳥山石燕は、妖怪の絵の本を出しました。鬼の絵の横に、彼は短い解説を書いています。世の人は、丑寅、つまり牛と虎の方角である北東を、鬼門と呼ぶ。いま鬼を描くときは、頭に牛の角をいただき、腰に虎の皮をまとわせる。この形は、丑と寅の二つを合わせたものだと言われている、と。

**P11** よくできた説明です。そして石燕自身も、それを「言われている」こととして書いています。彼がこれを書き留めたのは、最も古い記録から千年以上も後、北野の絵巻の角のある者たちからも、およそ500年後のことでした。絵が先か、説明が先か。資料は、それを教えてくれません。

**P12** 最後の説は、節分に話を戻します。病を追い払う宮中の儀式は、706年、多くの人が亡くなった年に記録されています。およそ900年前の宮中の手引き書『江家次第』では、方相と呼ばれる役人がこの儀式を率います。声を上げ、戈で楯を三度たたくと、群臣も声を合わせて追い立てます。そして手引き書は、もう一行を書き加えています。殿上人が、方相を射る、と。豆は、もっと後のことです。1447年、ある禅僧は「鬼は外、福は内」という唱え言葉を書き留め、これがこの国の鬼の追い払い方なのだろう、と記しました。

**P13** つまり、役が入れかわったのです。その手引き書では、追い立てを率いる者が、射られる的にもなっていました。そして15世紀には、豆がまかれ、外へ出されるのは鬼のほうになっていました。

**P14** では、鬼はなぜ虎の皮を着ているのか。一つの説明は、それを牛と虎、不吉な北東に結びつけます。石燕がそれを書き留めたのは1779年。最初の鬼より、ずっと後のことでした。最も古い記録が見せてくれるのは、別のものです。山の上で大きな笠をかぶった者。山の田に現れた、目が一つのもの。そして、「隠れる」を意味するのかもしれない言葉。角も、虎の皮も、金棒も、後から、絵を通してやって来たのです。

**P15** すべての物語には、始まりがあります。ときにそれは、誰にも見えなかったものから始まるのです。

**P16** この動画は、歴史資料と、美術館・図書館の公開コレクションにもとづいています。ナレーションには合成音声を使っています。出典と利用条件は説明欄に記載しています。楽しんでいただけたら、高評価とチャンネル登録で、これからも静かな起源の物語をお楽しみください。ご視聴ありがとうございました。

## 画面の案（素材は[素材候補](wom14_素材候補_20261109.md)のID。1本の動画で同じ作品は1回だけ）

| 区間 | 点検カード | 画面 | 素材 |
|---|---|---|---|
| P01 | — | 0秒から大津絵の赤鬼の**顔**に寄る（角・牙）→ 文字カード「horns · tiger skin · iron club」→ 島原の鬼やらいの小さな赤鬼に寄る | O01-A・文字・O02-A |
| P02 | **一覧**（4つの説、札はまだ空） | 点検カード | 文字 |
| P03 | — | 文字カード「鬼」1字（中国の字書の原文は出さない） | 文字 |
| P04 | — | 北野本巻26 コマ23（「著大笠 臨視喪儀」に寄る）→ アストン272頁（8月条の行と脚注2）→ 月の山の風景画（実景とは言わない） | O03-23・O04-272・O05-A |
| P05 | — | 『訂正出雲風土記』コマ38（「目／一鬼」に寄る。改行をまたぐ2列を一緒に）→ 竹と岩の墨画 | O06-38・O15-A |
| P06 | 説1に `NOT IN THE OLDEST RECORDS` | 点検カード | 文字 |
| P07 | — | 『倭名類聚抄』コマ31の「鬼」の項（「或説云」→「人死魂神也」の順に寄る） | O08-31 |
| P08 | 説2に `AN OLD GUESS` | 点検カード（「It is an early guess」で札）→ 芥川の見立て絵（鬼は描かれていない） | 文字・O09-A |
| P09 | — | 北野天神縁起絵巻 DP244660 の門前の角のある者（x=.64〜.80、y=.50〜.81）→ 暁斎の蝸牛と鬼（長い角） | O10-A・O14-B |
| P10 | — | 石燕「鬼」の**解説の文字だけ**の切り出し（絵の下部は出さない）→ 十二支の方位の模式図（北東に丑・寅） | O11-12・模式図 |
| P11 | 説3に `A LATER EXPLANATION` | 点検カード | 文字 |
| P12 | — | 『続日本紀』コマ27（「始作土牛大儺」）→ 『江家次第』コマ30（「射方相」）→ 浅草寺の節分 → 『臥雲日件録抜尤』コマ170（「鬼ハ外福内」） | R10-27・R11-30・O02-B・R12-1447 |
| P13 | 説4に `THE ROLES CHANGED` | 鍾馗が豆をまき小鬼が逃げる図 → 点検カード | O02-D・文字 |
| P14 | 4つの札がそろった一覧 | 点検カード → 念仏鬼（暁斎系の淡彩、O01-C）の顔 | 文字・O01-C |
| P15 | — | 多摩川の秋の月 | O16-A |
| P16 | — | 終わりのカード（第12話と同じ型） | — |

- **原典照合用（R）の頁も、NDLの保護期間満了（PDM）なので映像に使ってよい**。Codexの「映像の本候補」外の扱いは、数に入れていないだけと読む（制作依頼で明記する）。
- **使わない候補**：O01-B・O01-D・O02-C・O14-C・O15-B・O15-C（予備）、O03-22・O04-271・O06-47・O06-48（照合用）。
- **サムネ**：A `WHY TIGER SKIN?`＝大津絵の赤鬼（O01-A）の顔を全面。足の虎の皮の脚絆が見えるよう縦に寄せる案も。B `THE FIRST ONI WORE A HAT`＝同じ顔＋北野本の「著大笠」の小さな切り出し。**角・虎の皮の腰巻き・金棒の3点がそろったカラーの絵は見つかっていない**（Codex）。サムネはA・Bの2案を作り、168pxで比べる。

## ショートの案（本編合格後に別依頼）

| | 見出し | 中身 | 役割 |
|---|---|---|---|
| O1 | `THE FIRST ONI WORE A HAT` | 661年の朝倉山。笠と、角がないこと。アストンの「or spirit」 | 新しい人に届く |
| O2 | `THE ONE-EYED ONI OF IZUMO` | 阿用郷の地名の由来（食べる場面は語りで一言） | 資料の細部 |
| O3 | `WHY TIGER SKIN?` | 石燕の丑寅の説明と「言われている」。「では、なぜ絵の鬼に角が生えたのか」を残して本編へ | 本編へ |

節分（2027年2月3日）の前に、O3か説4の切り口のショートを再活用できる。

## v01からの変更点（照合による）

1. **P04**：「葬列が出発したその夕べ」→「皇太子が亡骸を奉じて磐瀬宮に戻ったその夕べ」（原文「還至磐瀬宮。是夕」）。5月条（神社の木・あやしい火）は尺のため削った。アストンの訳語と脚注「or spirit」を加えた。
2. **P03**：「中国では死者の霊、幽霊に近いもの」→「古い中国の書物では死者の霊と結びついていた」（説文はWeb翻刻のみのため弱め、字書の文は削った）。
3. **P05**：「約70年後」の起点を「この出来事から」と明示。
4. **P06**：「描かれていない」→「触れていない」。
5. **P07**：同じ項の「人死魂神也」を加えた（P03とつながる）。
6. **P08**：「この書き手にとって鬼は見えないもの」を削った（P07の「形を現そうとしない」と重なり、「見えない」は言いすぎ）。『伊勢物語』は「誰も見なかった」を削り「姿を描かない」、後注（鬼は実は兄たち）を加えた。成立は「10世紀ごろに形づくられた」。
7. **P09**：「中世までに地獄の絵巻に」→「13世紀後半の北野天神縁起絵巻」に具体化。「金棒も持たせた」を削った（根拠となる図がないため）。
8. **P10・P11**：石燕の解説を原頁の文（「今鬼の形を画くには」「といへり」）に合わせ、石燕自身が「言われている」と書いていることを加えた。「考えは石燕より古いかもしれない」を削った（先行文献は未照合）。「絵の姿を方角に結びつける」の一文は尺のため削った。
9. **P12・P13（説4）**：「豆まきは追儺から生まれた」「方相氏が鬼とみなされた」を削り、確かめた記録だけで組み直した：706年の大儺 →『江家次第』で方相が射られる → 1447年の日記の「鬼は外、福は内」（1425年の『看聞日記』は尺のため語らず、照合の根拠としてだけ残す）。「毎年2月に家族が追い払う相手になった」（現代への直結）を削った。黄金四目は語らない。
10. **P14**：「その説明は古い」→「石燕が1779年に書き留めた」。

## 本人に確認したこと（2026-11-09 すべて推奨どおりで承認）

1. **台本v02でよいか**（特に説4を記録の紹介に絞った形）。
2. **尺**：約8分40秒の見込み（了承の目安7〜8分を超える）。このままでよいか、さらに削るか。さらに削るなら、P04のアストンの注（約10秒）とP08の後注（兄たち、約12秒）を外して約8分20秒（推奨：このまま。どちらもショートや「意外な答え」に効く細部で、話速を上げたり間を削ったりはしない）。
3. **サムネ**：大津絵の赤鬼の顔でA・Bの2案を作り、168pxで比べてから選ぶ、でよいか。
4. 了承後、台本JSONと制作依頼を作ってCodexへ渡してよいか（確認版v01は11/13中を目標、公開11/18（水）09:00）。
