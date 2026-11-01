# Quiet Origins 第9話「トロイの木馬」：テーマ設計と台本 v02（2026-11-01 Claude）

管理ID：`wom09`。状態：**台本v02を本人承認（2026-11-01「大丈夫です。進めて下さい」。AI映像なし、サムネA・Bの両方を作って確認版で選ぶことも了承）。台本JSON `episodes/EP009_TrojanHorse/records/content_en.json`・`content.json` と[制作依頼](wom09_制作依頼_20261101.md)を作成。** v01の確認4点は本人了承済み（2026-11-01「全て大丈夫です」）：題は問いの形、扱いの範囲、公開日11/6 09:00目標、素材探し依頼。v02は、Codexの[原典照合](research/wom09_原典訳文_20261101.md)（11項目）と[素材候補](wom09_素材候補_20261101.md)（25作品・カラー20）に合わせて、言い方を資料に合わせた版（変更点は末尾）。v01はGitの履歴（`976f3a0`）。音声・映像は未制作。エピソードのフォルダは `episodes/EP009_TrojanHorse/`（本人承認後に台本JSONを作る）。

## 狙い

- 題（本人了承、2026-11-01）：**The Trojan Horse: Is It in the Iliad?**／トロイの木馬は『イリアス』に出てくるのか
- 冒頭の問い：誰もが知る木馬の計略。多くの人はホメロス『イリアス』の場面だと思っている。けれど『イリアス』は木馬が作られる前に終わる。では、木馬の話はどこから来たのか。
- 結論（照合後）：
  1. 『イリアス』は戦争10年目の短い期間を描き、**ヘクトルの葬儀で終わる**（1883年訳の最終文「Thus held they funeral for Hector tamer of horses.」、刊本503頁を目視）。木馬による攻略・陥落・アキレウスの死は物語として描かれない（アキレウスの死は18巻・22巻で予告だけ）。
  2. 木馬が出てくる最古の文学は**『オデュッセイア』**。思い出として3か所、合わせて数十行（4巻：ヘレネが妻たちの声をまね、オデュッセウスがアンティクロスの口をふさぐ／8巻：盲目の歌い手デモドコス、エペイオスがアテナの助けで作り、トロイ人が三つの案で揉める／11巻：ネオプトレモスは青ざめなかった）。どこにも中の人数はない。
  3. 戦争の終わりを語った初期の叙事詩（『小イリアス』『イリオスの陥落』）は全文が残らず、主に後世の要約（プロクロス）と引用の断片で知られる。要約にはすでに、木馬・城壁を崩して引き入れる・ラオコーンと大蛇・シノンが出てくる。**ウェルギリウスの発明ではない。**
  4. 最古級の絵：ミコノス島の大甕（ミコノス考古学博物館2240、1961年発見、前7世紀第2四半期・前670年ごろとされる）。写真で7つの窓と顔、車輪が見える。「最古」と一つに決めない。
  5. 今の私たちが思い浮かべる詳しい筋が残るのは、**ウェルギリウス『アエネーイス』2巻**（前29〜前19年ごろ）。アエネアスがディドに語る。ラオコーンの警告（49行）と槍を投げつける（50〜53行）、シノンのうそ、大蛇、城壁を開く。
  6. パウサニアス（2世紀）はアテナイの「木の馬」と呼ばれる青銅像を見て、木馬は城壁を破る仕掛けだった、と別の説明を書いた。人数は『摘要』（アポロドーロス）が50人と記し、『小イリアス』の作者によれば3000人とも伝える。
- 尺の目標：**約6〜7分**（v02で英語827語、日本語約2,060字。第8話712語＝347.6秒から見て約6分40秒〜7分）。
- 公開日（本人了承）：**11/6（金）09:00**を目指す。間に合わなければ次の空いている日の09:00。

## 注意して扱う点

- **ホメロスの言い方**：「ホメロスの『イリアス』」と慣例で呼ぶ。成立年代は一つの年に決めず、年表では「前8〜7世紀ごろ」。ウェルギリウスとの差は「何世紀も後」（「約700年」と言わない）。
- **史実かどうか**：「木馬はなかった」と断定しない。「攻城の仕掛けだった」も事実としては言わず、「パウサニアスはそう説明した」と主語を保つ。考古学（トロイの遺跡）には触れない。
- **ウェルギリウスを発明者にしない**：木馬・城壁・大蛇・シノンは先行の詩の要約にもある。言うのは「詳しい物語が残っている」「今の私たちが思い浮かべる場面の多くが鮮やかに描かれる」まで。「最も詳しい」「すべてを語った」は使わない。
- **ラオコーンの息子の人数**：『イリオスの陥落』の要約では二人のうち一人、『アエネーイス』では二人。台本では人数を言わない。
- **戦争の場面・裸体**：流血・殺戮の絵は使わない。後世の版画の小さな半裸の人物は全景で短く、拡大しない。サムネに裸体を入れない。
- **壺の人物名を断定しない**：館の同定どおりに札を付ける（例：「メネラオスとヘレネとされる場面」）。キタラ奏者の壺は「歌い手」の雰囲気として使い、デモドコスの肖像と書かない。
- **引用**：映像の文字カードに出す英文は、照合した公有の英訳の原文どおり（Lang, Leaf & Myers 1883、Mackail 1885）。ナレーションの他の部分は要約。Internet Archiveの刊本スキャン画像は映像に使わない（所蔵館のPD/CC0明記がない）。引用は文字カードで見せる。
- **パウサニアスの像の作者**（ストロンギュリオン）は未確認なので言わない。
- **AI映像は使わない**（v02の変更）。P14は本物の壺（キタラ奏者）で足りるため。Klingの残高315は使わない。P15のAIの一文も外す。
- **第8話の教訓（暗さ）**：画面のカラー素材は9点、白黒の版画は3点。白黒には暖かい単色の色調と明るさ。文字カードは砂色の地に濃い茶色の文字（コントラスト比4.5以上、金色の文字は使わない）。レンブラントの油彩は暗いので明るさを上げすぎず、胸像の部分だけを短く。

## 出典（v02、Codexの照合による）

確認の区分：A＝刊本画像で目視、B＝Web翻刻、C＝研究・館の解説。

| ID | 出典 | 台本 | 照合の結果 |
|---|---|---|---|
| T-S01 | Homer, *Iliad*、Lang, Leaf & Myers 訳（Macmillan, 1883） | P03・P04 | A：p503 24巻最終文「Thus held they funeral for Hector tamer of horses.」。1巻はアキレウスの怒り。アキレウスの死の予告は18.95–96、22.358–360（B） |
| T-S02 | Homer, *Odyssey*、Butcher & Lang 訳（1879）4巻271–289 | P06 | A：pp56–57。語り手メネラオス、ヘレネが三度回り将の名を呼び妻たちの声をまねる、オデュッセウスがアンティクロスの口をふさぐ |
| T-S03 | 同 8巻63–64・492–520 | P05 | A：p117 ムーサが視力を奪い歌を与えた。p131 エペイオスがアテナの助けで作った。三つの案（割る／高所から投げ落とす／神々への供物） |
| T-S04 | 同 11巻523–532 | P07 | A一部＋B：ネオプトレモスは青ざめず涙もぬぐわず、外へ出たがった。3か所の指定範囲で計58行（「数十行」は妥当）。人数の記述なし |
| T-S05 | プロクロス『クレストマティア』（Evelyn-White 訳 1914）の『小イリアス』『イリオスの陥落』要約 | P08 | B：エペイオスがアテナの指示で木馬を作る、城壁の一部を崩して引き入れる、大蛇がラオコーンと二人の息子のうち一人を殺す、シノンの火の合図。プロクロスの同定・年代には諸説 |
| T-S06 | ミコノスの浮彫大甕（ミコノス考古学博物館 2240） | P09 | C：前670年ごろ／前7世紀第2四半期、1961年発見。画像MYK01（撮影者のCC0）。「最古級の一つ」は可、単独の最古は不可（前700年ごろのボイオティアの留め金などの比較例） |
| T-S07 | Virgil, *Aeneid* 2巻、Mackail 訳（1885）、ラテン語本文 | P10・P11 | A：p25「Be it what it may, I fear the Grecians even when they offer gifts.」「he hurled his mighty spear」。B：2.49 *timeo Danaos et dona ferentes*、シノン57–198、大蛇199–227、城壁234前後。C：前29〜19年ごろ、死後刊行 |
| T-S08 | ホメロスの成立年代 | P11 | C：前8世紀〜前7世紀中頃と幅。差は「何世紀も」 |
| T-S09 | Pausanias 1.23.8、Jones 訳（1918） | P12 | B：「There is the horse called Wooden set up in bronze.」「a contrivance to make a breach in the Trojan wall」。像の作者名は本文になく未確認 |
| T-S10 | Apollodorus, *Epitome* 5.14、Frazer 訳（1921） | P12 | B：「fifty (or, according to the author of the Little Iliad, three thousand)」。同じ一節に二つの数 |
| T-S11 | Merriam-Webster「Trojan horse」 | P13 | C：有用に見せて害を与える命令を隠したプログラム。語の初出年は言わない |

## 台本（英語・メイン）v02

章は5つ。P02のあとにオープニング（4秒）を入れる。

### C01 The Most Famous Trick

**P01** Outside the walls of Troy stands a giant wooden horse. The Greeks, it seems, have sailed away and left it behind as a gift. But inside, soldiers are waiting for the night. It is one of the most famous stories ever told, and many people remember it from Homer's Iliad. Yet the Iliad ends before the horse is ever built. So where does the story of the Trojan horse come from?

**P02** In this episode, we follow the horse from the last line of the Iliad, to a song in the Odyssey, to poems now mostly lost, and to a Roman poet who gave the story one of its most famous tellings.

（ここでオープニング）

### C02 Where the Iliad Ends

**P03** The Iliad is one of the oldest works of Greek literature. It tells of only a short time in the tenth year of the Trojan War, beginning with the anger of the hero Achilles. It ends not with the fall of Troy, but with a funeral. In one old translation, its final line reads: "Thus held they funeral for Hector tamer of horses."

**P04** The Iliad does not tell of a wooden horse, or of the city's fall. Even the death of Achilles is foretold, but never shown. The horse, the trick, the burning of Troy: all of that lies beyond the poem's last page.

### C03 A Song at a Feast

**P05** The horse does appear in Homer's other great poem, the Odyssey. Far from home, Odysseus sits at a feast and asks the blind singer Demodocus to sing of the wooden horse, which Epeius built with the help of the goddess Athena. In the song, the Trojans argue over what to do with it: break it open, throw it down onto the rocks, or keep it as an offering to the gods.

**P06** Earlier in the poem, King Menelaus remembers how Helen walked around the horse, calling out the names of the Greek leaders hidden inside, and imitating the voices of their wives. Odysseus held the men back, and covered one man's mouth with his hands, so that no one would answer.

**P07** And in the land of the dead, Odysseus tells the ghost of Achilles that his son was among the men inside, and never once turned pale. In Homer, the horse is a memory, told in a few dozen lines. None of these passages says how many men were inside.

### C04 Lost Poems, and a Roman Poet

**P08** Other early Greek poems told the end of the war, such as the Little Iliad and the Sack of Troy. They do not survive in full. We know them mainly through short summaries written centuries later. Yet those summaries already have the horse taken into the city through a broken wall, the Trojan priest Laocoön killed by serpents, and Sinon, a Greek who helps to deceive the Trojans.

**P09** Artists knew the story early, too. A large clay jar found on the Greek island of Mykonos, made around 670 BC, shows a horse on wheels, with the faces of warriors looking out of small windows in its side. It is one of the oldest known pictures of the Trojan horse.

**P10** The version most of us know comes from Rome. About two thousand years ago, the poet Virgil wrote the Aeneid. In its second book, the Trojan hero Aeneas tells a queen of his city's last night. The priest Laocoön warns, in one old translation, "I fear the Grecians even when they offer gifts," and hurls his spear at the horse. Sinon tells a convincing lie. Serpents come from the sea. And the Trojans open their own walls to pull the horse inside.

**P11** Virgil wrote many centuries after Homer's poems, and he told the story from the side of the defeated. He did not invent the horse, the serpents, or Sinon. But many of the scenes we picture today, the warning, the lie, the opened wall, come to us most vividly through his telling.

### C05 A Gift Remembered

**P12** At least one ancient writer offered another explanation. In the second century AD, the travel writer Pausanias saw a bronze statue in Athens, called the Wooden Horse. He wrote that anyone who did not think the Trojans utterly foolish knew the horse had really been a machine for breaking through the wall. And how many men were inside? One later handbook gives fifty, but adds that the author of the Little Iliad said three thousand.

**P13** So, is the Trojan horse in the Iliad? No. It appears briefly in the Odyssey, grew in poems now mostly lost and in pictures, and survives in rich detail in Virgil's Aeneid. Today, even computer programs that look useful but hide something harmful are called Trojan horses. The gift is still remembered, and still not trusted.

**P14** Every story has an origin. Sometimes, it begins with a song sung at a feast.

**P15** This video is based on historical texts and public museum collections. The narration uses synthetic speech. Sources and terms of use are listed in the description. If you enjoyed this story, please like the video and subscribe for more quiet origins. Thank you for watching.

## 台本（日本語）v02

**P01** トロイの城壁の外に、巨大な木の馬が立っています。ギリシャ軍は船で去り、贈り物として馬を残していったように見えます。けれど馬の中では、兵士たちが夜を待っていました。世界で最も有名な物語の一つで、ホメロスの『イリアス』の場面として覚えている人も多いでしょう。ところが『イリアス』は、木馬が作られる前に終わっています。では、トロイの木馬の話はどこから来たのでしょう。

**P02** 今回は、『イリアス』の最後の一行から、『オデュッセイア』の中の歌へ、ほとんど失われた詩へ、そしてこの物語を後世に広く伝えたローマの詩人へと、木馬をたどります。

**P03** 『イリアス』は、ギリシャ文学で最も古い作品の一つです。描かれるのは、トロイ戦争の十年目の、短い期間。英雄アキレウスの怒りから始まります。そして物語は、トロイの陥落ではなく、葬儀で終わります。古い英訳では、最後の一行はこうです。「こうして彼らは、馬を馴らすヘクトルの葬儀を営んだ」。

**P04** 『イリアス』は、木の馬も、町の陥落も語りません。アキレウスの死でさえ、予告されるだけで、描かれはしないのです。木馬も、計略も、燃えるトロイも、すべては詩の最後のページの先にあります。

**P05** 木馬が登場するのは、ホメロスのもう一つの大きな詩、『オデュッセイア』です。故郷から遠く離れた宴の席で、オデュッセウスは盲目の歌い手デモドコスに、木の馬の歌を頼みます。女神アテナの助けを得て、エペイオスが作った馬です。歌の中で、トロイの人々はその扱いを言い争います。打ち割るか、岩の上へ投げ落とすか、それとも神々への捧げ物として残すか。

**P06** それより前の場面では、メネラオス王が思い出を語ります。ヘレネが木馬の周りを歩き、中に隠れたギリシャの将たちの名を呼んで、その妻たちの声をまねたこと。オデュッセウスは仲間を押しとどめ、一人の口を手でふさいで、誰も答えないようにしました。

**P07** さらに冥界では、オデュッセウスがアキレウスの霊に、あなたの息子も馬の中にいて、一度も青ざめなかったと語ります。ホメロスの中で、木馬は思い出として、合わせて数十行で語られるだけです。中に何人いたのかは、これらのどの箇所にも書かれていません。

**P08** 戦争の終わりを語った初期のギリシャの詩は、ほかにもありました。『小イリアス』や『イリオスの陥落』です。けれど、その全文は残っていません。主に、何世紀も後に書かれた短い要約で知られています。その要約にはすでに、城壁を崩して町に入れられる木馬や、大蛇に殺されるトロイの神官ラオコーン、トロイの人々をだます手助けをするギリシャ人シノンが登場します。

**P09** 画家や職人たちも、早くからこの話を知っていました。ギリシャのミコノス島で見つかった、紀元前670年ごろの大きな土の甕には、車輪のついた馬が描かれ、脇腹の小さな窓から戦士たちの顔がのぞいています。知られている中で最も古い、トロイの木馬の絵の一つです。

**P10** 私たちの多くが知っている筋書きは、ローマから来ました。およそ二千年前、詩人ウェルギリウスが『アエネーイス』を書きます。その第二巻で、トロイの英雄アエネアスが、ある女王に、町の最後の夜を語ります。神官ラオコーンは「私は、贈り物を携えたギリシャ人さえ恐れる」と警告し、馬に槍を投げつけます。シノンはもっともらしいうそをつき、海から大蛇が現れます。そしてトロイの人々は、自分たちの城壁を開き、馬を町に引き入れるのです。

**P11** ウェルギリウスが書いたのは、ホメロスの詩から何世紀も後のこと。しかも、敗れた側から物語を語りました。木馬も、大蛇も、シノンも、彼が考え出したものではありません。けれど、警告、うそ、開かれた城壁。今の私たちが思い浮かべる場面の多くは、彼の語りを通して、最も鮮やかに伝わっています。

**P12** 古代にも、別の説明を示した書き手がいました。2世紀の旅行作家パウサニアスは、アテナイで「木の馬」と呼ばれる青銅の像を見て、こう書いています。トロイの人々をまったくの愚か者だと思わない人なら、あの馬は本当は城壁を破るための仕掛けだったと知っている、と。では、中には何人いたのか。後の時代の手引き書は五十人と記し、『小イリアス』の作者によれば三千人だった、とも伝えています。

**P13** では、トロイの木馬は『イリアス』に出てくるのか。答えは、いいえ。『オデュッセイア』に短く現れ、ほとんど失われた詩や絵の中で育ち、ウェルギリウスの『アエネーイス』に、詳しい物語として残りました。今では、役に立つふりをして害になるものを隠したコンピュータのプログラムまで、トロイの木馬と呼ばれます。その贈り物は今も覚えられ、そして今も信用されていません。

**P14** どの物語にも由来がある。ときには、それは宴の席で歌われた一つの歌から始まります。

**P15** この動画は、歴史上の文献と公開された美術館のコレクションをもとに構成しました。ナレーションには音声合成を使っています。出典と利用条件は概要欄にまとめています。楽しんでいただけたら、高評価とチャンネル登録をお願いします。ご覧いただき、ありがとうございました。

## 画面の構成（v02案）

確定版のショット割りは制作依頼で決める。同じ素材は1本の中で1回だけ。札は館の同定どおり、後世の作品には年代を入れる（例「後世の想像図（16世紀）」）。

| 区間 | 見せたいもの | 素材（[素材候補](wom09_素材候補_20261101.md)のID） | 色 |
|---|---|---|---|
| P01 | 木馬（0秒から全面で動かす） | **met_202259** 木馬の彩色陶皿（16世紀中頃）。円形なので砂色の地に置き、皿の中の馬へゆっくり寄る | カラー |
| P02 | ホメロスの本 | **R06** フラクスマン構図集『オデュッセイア』の扉（1805） | 白黒 |
| P03 | ホメロス → 葬儀の前の場面 | **met_437394** レンブラント（1653）の胸像の部分だけ → **met_198621** ヘクトルの遺体の返還を願うプリアモスのカメオ（1815〜25ごろ） | カラー |
| P04 | 詩の最後の一行 | 文字カード：「Thus held they funeral for Hector tamer of horses.」（Lang, Leaf & Myers 1883）→「NO HORSE IN THE ILIAD｜『イリアス』に木馬はない」 | 砂色 |
| P05 | 歌い手 | **met_247952** キタラ奏者の壺（前500年ごろ）→ 文字カード（三つの案：割る／投げ落とす／捧げ物に） | カラー |
| P06 | ヘレネ | **met_254876** メネラオスとヘレネとされる場面の壺（前540年ごろ） | カラー |
| P07 | 3か所・人数なし | 文字カード（Odyssey 4・8・11、合わせて数十行、人数の記述なし） | 砂色 |
| P08 | 失われた詩 | 模式図（失われた詩 → 何世紀も後の要約。要約にある4つ：木馬・城壁・ラオコーン・シノン） | 砂色 |
| P09 | ミコノスの甕 | **MYK01**（撮影者のCC0、990×885pxなので大きく寄らない。窓と顔の部分を見せる） | カラー |
| P10 | アエネーイス2巻 | **R04** 木馬を引き入れる行列（版画）→ 文字カード（Mackail 1885「I fear the Grecians even when they offer gifts.」／ラテン語 *timeo Danaos et dona ferentes*）→ **R01** 馬に槍を向ける人物と城壁の開口（版画） | 白黒（暖色の単色） |
| P11 | 年表 | 模式図（ホメロス 前8〜7世紀ごろ ／ ミコノスの甕 前670年ごろ ／ アエネーイス 前29〜19年ごろ） | 砂色 |
| P12 | アテナイ・人数 | **met_341207** アクロポリスの水彩（1834。木馬の像は描かれていないと札に書く）→ 文字カード「50? 3,000?」 | カラー |
| P13 | まとめ | 模式図（イリアス：なし → オデュッセイア：数十行 → 失われた詩・絵 → アエネーイス：詳しい物語）→ **met_253376** 木馬を彫ったエトルリアの紅玉髄（前500〜475年、小さいので解像度の範囲で） | カラー |
| P14 | 歌の余韻 | **met_254896** キタラ奏者のアンフォラ（ベルリンの画家、前490年ごろ）にゆっくり寄る | カラー |
| P15 | エンドカード（共通版v02、10秒） | — | — |

予備：R03（木馬と城門、半裸の人物が多いので短く）、met_241228・met_254795（キタラ）、met_341205（淡いアクロポリス）、met_254509・met_667511・met_247955・met_247931（ヘレネの解釈に留保）。使わない：R02・R05・met_354833（裸体・殺害）、met_10482（第4話で使用済み）、met_248179・met_248714、met_337384・met_336983（場面違い）。

**AI映像なし。** BGMは既存の `QO_THEME_A02`（新規生成・課金なし）。

## サムネ（案）

- **A**：met_202259 の彩色陶皿を全面（砂色の地）、文字「NOT IN THE ILIAD」。色が明るく、木馬だと一目で分かる。
- **B**：MYK01 の窓から顔がのぞく木馬、文字「THE OLDEST TROJAN HORSE?」。珍しさが強いが、解像度が低く土色。
- 制作時に両方作り、本人が選ぶ。Claudeのおすすめは **A**（題の答えと文字が合う）。

## ショート（本編の合格後に別依頼、案）

| 案 | 内容 | 素材 |
|---|---|---|
| T1 | 『イリアス』の最後の一行に木馬はない | met_198621 → 文字カード |
| T2 | 窓から顔がのぞく、2,700年前の木馬 | MYK01 |
| T3 | 「贈り物を携えたギリシャ人さえ恐れる」 | R04・R01 |

字幕には最初から黒の半透明の下地（不透明度0.68前後）。後半10秒にも絵。

## 人気チャンネルの調査と第8話の反省の反映

| 項目 | 第9話での扱い |
|---|---|
| 本編の冒頭 | 0秒から主役（木馬の彩色陶皿）を全面で動かす |
| 色 | カラー素材9点・白黒3点。白黒には暖かい単色の色調。文字カードは砂色の地に濃い茶色 |
| BGM | Suno（語りより約18dB小さく、切れ目で+6dB、100Hz以下を削る） |
| サムネ | 木馬の絵を全面に、短い英語の言葉を一つ |

## v01からの変更点（Codexの照合による）

| 区間 | v01 | v02 | 理由 |
|---|---|---|---|
| P02 | 物語のすべてを語った | 後世に広く伝えた（one of its most famous tellings） | 先行の詩も全体を扱っていた |
| P03 | 数週間／So held they funeral for Hector, tamer of horses. | 短い期間／**Thus held they funeral for Hector tamer of horses.** | 一般の数え方で約50日。1883年刊本p503の印字どおり |
| P04 | no fall of the city | does not tell of … the city's fall | 予感・予言まで「ない」と言わない |
| P05 | throw it from the rocks | throw it down onto the rocks | 8巻の訳（高所から岩へ）に合わせる |
| P06 | covered one man's mouth | covered one man's mouth with his hands | 刊本の言い方に寄せる |
| P07 | Homer never says how many | None of these passages says how many | 確かめた範囲に合わせる |
| P08 | 失われた | 全文は残らず。要約に**すでに木馬・城壁・ラオコーン・シノン** | 断片も残る。ウェルギリウスの発明と誤解させない |
| P10 | 「贈り物を持ってくるときでも、ギリシャ人は恐ろしい」／strikes／槍を突き立て | Mackail訳「I fear the Grecians even when they offer gifts」／「私は、贈り物を携えたギリシャ人さえ恐れる」／hurls／投げつけ | 公有訳の原文どおり。timeoは一人称。50〜53行は投げる動作 |
| P11 | 約700年後 | 何世紀も後。「彼が考え出したものではない」を追加 | ホメロスの年代に幅。先行詩との関係 |
| P12 | 古代の読者もいぶかしんだ／意見が分かれた | 別の説明を示した書き手がいた／一つの手引き書が二つの数を伝える | パウサニアス一人から一般化しない |
| P13 | 最も詳しく語った | 詳しい物語として残った。「役に立つふりをして」を追加 | 最上級を避ける。辞書の定義に合わせる |
| P15 | AI映像の一文 | 削除 | AI映像を使わない |
| 画面 | ミコノスは模式図の可能性、AIの灯火 | MYK01の写真、P14はキタラの壺。AIなし | 素材がそろった |

## 本人に確認したいこと（v02）→ 2026-11-01 すべて了承

1. **台本v02**（上の英日）でよいか。特にP08・P11で「ウェルギリウスが考え出したのではない」と入れた点。
2. **AI映像を使わない**（P14は本物の壺）でよいか。
3. よければ、Claudeが台本JSONと**制作依頼**を作り、Codexへ確認版v01の制作を頼む（公開目標11/6 09:00）。サムネはA・Bの両方を作ってもらい、確認版で選ぶ。
