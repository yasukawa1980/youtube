# Quiet Origins 第15話「クリスマスはなぜ12月25日なのか」：テーマ設計と台本 v02（2026-11-20 Claude）

管理ID：`wom15`（神話シリーズ第15話。第13話は欠番、「夜警」は絵画01）。状態：**台本v02（本人確認待ち）。** v01は本人了承（2026-11-20「推奨どおりでOK」：題材は12月25日・二説比較型、題は案A *Why Is Christmas on December 25?*、公開の目安12/2（火）09:00（遅れたら12/5（土））、素材探し・原典照合はCodexへ）。v02はCodexの[原典照合](research/wom15_原典訳文_20261120.md)（`932b319`）と[素材候補](wom15_素材候補_20261120.md)（26点、`418a6bd`、[Claudeの確認](wom15_Claude確認_素材_20261120.md)）に合わせて直した版（変更点は末尾）。v01はGitの履歴（`96a62fb`）。音声・映像は未制作。エピソードのフォルダは `episodes/EP015_December25/`（制作依頼のときに作る）。

## なぜこの題材か

- **年中行事の柱**：再生の多い本編は感謝祭（67回）・アヌビス（45回）・メドゥーサ（19回）・ハロウィン（17回）（11/20公開ページ）。行事の回が強い。12月は検索も関心も「クリスマス」に集まる。
- **第10話クランプス・第12話サンタの赤い服と重ならない**：両方とも「人物・姿」の話。第15話は「日付」の話で、資料もローマの暦・教父の文書と、まったく別。
- **QOの型そのもの**：「よく聞く説明（異教の祭りを置き換えた）を、いちばん古い記録で確かめる」。しかも答えが**一つに決まらない**ことを正直に見せられる。

## この回で試すこと：二つの説を比べる型

第14話は「通説の点検型」（4つの説に札を押す）だった。同じ型が続くとクリックされにくいという本人の懸念（11/4）に合わせ、第15話は**二つの説を並べて、証拠を左右に置いていく型**にする。コンセプト（最古の資料で確かめる・静かな語り・Kokoroの声・AI映像なし）は変えない。

| | 第14話（通説の点検型） | 第15話（二説比較型） |
|---|---|---|
| 章の立て方 | 説1〜4を順に | **最古の記録 → 説A（太陽の祭り）→ 説B（計算）→ 広がり → 結び** |
| 画面 | 点検カードに判定の札 | **証拠ボード**：左に `THE SUN FESTIVAL`、右に `THE CALCULATION`。資料が出るたびに、年つきの小さなカードを左右どちらかに置く。全部で5回（P05で空のボード、説Aの終わり、説Bの終わり、P13で「両方」、P14でそろった全体）。札は真偽にしない：`EARLIEST RECORD`／`WRITTEN CENTURIES LATER`／`NO ANCIENT SOURCE`／`AFTER THE DATE EXISTED` |
| サムネ・題 | 鬼の顔1点＋問い | **場面画1点＋日付の大文字**（下のサムネ案） |

効果は、本編の表示回数の出どころ（特に検索）とクリック率を第12話（サンタ）と比べて見る。題が検索語そのもの（*why is christmas on december 25*）なので、検索からの流入が増えるかを見る。

## 狙い

- 題の案（本人が決める）：
  - **案A（推奨）**：*Why Is Christmas on December 25?*／クリスマスはなぜ12月25日なのか
  - 案B：*Was Christmas Set on a Pagan Holiday?*／クリスマスは異教の祭りの日だったのか
  - 推奨の理由：①英語圏で毎年12月に多く調べられる問いそのもので、検索から届く。②案Bは「答えはどちらとも決めきれない」という結論に対して煽りが強く、信仰に関わる題材で「異教」を題に置くと、コメント欄が荒れやすい。案Bの切り口はショートの見出しに回す。
- 冒頭の1文で題の問いをそのまま言う（11/20の運用提案「最初の1文で題名の問いを言う」を、この回から台本の決まりにする案）。
- 結論（v01時点の見込み。照合で弱めた点は台本v02と末尾の変更点のとおり）：
  1. **聖書に日付はない。** 2世紀末まで、誕生日を祝った記録も見当たらない。200年ごろ、アレクサンドリアのクレメンスは、誕生の日を計算した人々の説をいくつも挙げているが、12月25日はその中にない（要照合）。
  2. **12月25日の最古の記録は、354年にローマで作られた暦の本**（フィロカルスの暦、いわゆる「354年の年代記」）。殉教者の記念日の一覧の最初の行に「12月25日（1月の朔日の8日前）、キリスト、ユダヤのベツレヘムに生まれる」。この一覧は336年ごろのものと考えられている。**同じ本の暦の12月25日には「不敗者の誕生日、競走30回」**とある（どちらも要照合）。
  3. **説A：太陽の祭り。** 皇帝アウレリアヌスは274年、ローマに太陽神ソルの神殿を建てた。教会は、この日の祭りに重ねてキリストの誕生を置いた、という説。根拠：354年の暦、12世紀のシリア語写本の欄外の書き込み（異教徒がこの日に太陽の誕生を祝ったので、教会が祭日を移した、という趣旨）、5世紀のローマ司教レオが、サン・ピエトロの階段で太陽に頭を下げる信徒をいさめたこと。弱いところ：**太陽の祭りを12月25日に置く記録も、354年の暦より古いものは見つかっていない**と指摘されている。書き込みは800年後のもの。
  4. **よく聞く「サトゥルナリアを置き換えた」は日付が合わない**：サトゥルナリアは12月17日に始まり、長くても23日まで（要照合）。「ミトラス神の誕生日が12月25日」という話は、古代の資料に見当たらない（要照合。確かめられなければこの1文は削る）。
  5. **説B：計算。** キリストが亡くなった日を3月25日とする考えが、3世紀初めのテルトゥリアヌスに見える（要照合）。聖なる人は、身ごもられた日と亡くなった日が同じ、という考え方があり、3月25日に身ごもられたなら、9か月後は12月25日。400年ごろ、アウグスティヌスはそのとおりに書いている（『三位一体論』4巻、要照合）。東方では4月6日から数えて1月6日になり、今もアルメニア教会はこの日に祝う。弱いところ：**アウグスティヌスの説明は、12月25日の祭りがすでにあった後に書かれた。**
  6. **広がり**：386年ごろ、アンティオキアでヨアンネス・クリュソストモスは、この祭りを知ってから「まだ10年にならない」と説教し、西から伝わったと言っている（要照合）。
  7. **結び**：最古の記録はローマの336年〜354年。説明は二つあり、どちらにも根拠と弱いところがある。ローマの暦では12月25日が冬至の日とされていた（大プリニウス、要照合）ので、二つの説は同じ日を指していたのかもしれない。**どちらが正しいとは言わない。**
- 尺：本人指定で6分に合わせない。v01は英語942語・日本語2,467字。**v02は英語983語・日本語2,584字**（台本本文、11/20に数えた値）で、話速が第12話と同じなら**約8分10秒**の見込み（第12話は835語で6分58.5秒の記録）。
- 公開日の目安：**12/2（火）09:00**（下の表）。クリスマスの3週間前で、12月の検索の伸びに間に合う。遅れたら12/5（土）09:00。

### 公開日の照合（2026-11-20、リポジトリの記録だけ。Studioの画面では未確認）

| 日 | 本編 | ショート | 合計 | メモ |
|---|---|---|---|---|
| 11/28（土） | 絵画02 `FjWNAYSqly0` 09:00 | V1 18:00 | 2 | 予約済み |
| 11/29（日） | — | V2 12:00・V3 18:00 | 2 | 予約済み |
| 11/30（月）〜12/1（火） | — | 0 | 0 | 記録上は予約なし |
| **12/2（火）** | **第15話 09:00（案）** | S1 18:00の案 | 2 | S2・S3は12/3・12/4の12:00の案 |

- 第14話のショートO1〜O3は、v02（11/13、Release `443150622`）のあと**Claude確認・投稿の記録がない**。本編は11/18に公開済みなので、O1〜O3を11/21〜27に入れるなら、上の表の前に入る（別作業。本人に確認）。
- 制作の目安：v01の了承11/20〜21、Codexの照合11/21〜23、v02 11/24、確認版v01 11/26〜27、Claude確認と本人試聴11/28〜29、予約11/30〜12/1。

## 注意して扱う点

- **信仰をからかわない。** 「クリスマスは本当は異教の祭り」「教会が盗んだ」とは言わない。説Aも説Bも、学者の説明として同じ重さで並べる。**イエスが実際に生まれた日については何も言わない**（資料から分からない、とだけ）。
- **言い切るのは原文で確かめたことだけ。** 特に：354年の暦の2つの行の原文、殉教者一覧の成立年（336年ごろ）、アウレリアヌスの祭りの日付が354年より前に記録されていないこと、シリア語の書き込みの年代と書き手、レオの説教の箇所、テルトゥリアヌスの3月25日、アウグスティヌスの箇所、クリュソストモスの「10年」、プリニウスの冬至の日付。
- **ヒッポリュトスの『ダニエル書注解』の12月25日**は、後の書き加えの可能性が議論されている。台本には入れない（照合で記録だけ）。「教皇ユリウス1世が12月25日に決めた」という話も、後の伝えなので使わない。
- **サトゥルナリア・ミトラスの1文は、照合で確かめられた場合だけ残す。** 確かめられなければP07の該当文を削る。
- **現代の写真・映像は使わない**（今の教会・ミサ・クリスマスの飾り・人物）。降誕・受胎告知・東方三博士の絵は、美術館のPD・CC0の作品だけ。
- **ローマの太陽神の像・硬貨は「太陽神」として見せ、キリストの像と重ねない**（「キリスト＝太陽神」と画面で言わない）。ローマのネクロポリスの「太陽としてのキリスト」のモザイクは、写真の権利が不明なので使わない。
- **AIで人物・場面を作らない。** AI映像は使わない。
- **読み**：Chronograph of 354、Filocalus、Valentinus、kalends、Bethlehem、Sol Invictus、Aurelian、Saturnalia、Mithras、Dionysius bar Salibi、Leo the Great、Tertullian、Augustine、Epiphany、Armenian、John Chrysostom、Antioch、Pliny the Elder、Clement of Alexandria。日本語は、フィロカルス、ソル・インウィクトゥス（不敗の太陽）、アウレリアヌス、サトゥルナリア、ミトラス、レオ1世、テルトゥリアヌス、アウグスティヌス、公現祭（こうげんさい）、ヨアンネス・クリュソストモス、アンティオキア、大プリニウス、アレクサンドリアのクレメンス。

## 出典（照合済み。詳細は[原典照合](research/wom15_原典訳文_20261120.md)の番号）

| 照合 | 出典（確かめた箇所） | 台本 | 素材 |
|---|---|---|---|
| 1 | ルカ2:4–20・マタイ2:1–12に月日なし。1・2世紀に年ごとの降誕祝いの明瞭な記録なし（McGowanの判断） | P02 | D02-A |
| 2 | クレメンス『ストロマテイス』I.21.145–146：パコン月25日（5月20日）、ファルムティ月24・25日（4月19・20日）など。12月25日はない | P02 | D03-A |
| 3 | 354年の本：献辞の宛名Valentinus、Furius Dionysius Filocalus titulavit。原物は失われ写しで伝わる。殉教者一覧の冒頭「VIII kal. Ian. natus Christus in Betleem Iudeae.」（Mommsen 1892 p.71）。336年は関連する司教表からの**復元年代** | P03・P04 | D05-T・D05-A |
| 4 | 市民暦12月25日「N·INVICTI·CM·XXX」。solisもMithraeも書かれていない | P04・P07 | D06-A |
| 5 | アウレリウス・ウィクトル35.7：ローマにソルの壮麗な神域。274年。**354年以前に12月25日を祭日とする明示史料は特定できず** | P06・P07 | D04-A・B |
| 6 | Assemani 1721 p.164、Vat.sir.155 f.43v：無署名の欄外注。異教徒の太陽の誕生祝いにキリスト教徒も加わるのを見て、教父たちが1月6日から12月25日に移した、という趣旨。**筆者・記入年は不明** | P06・P07 | D07-A |
| 7 | レオ1世 説教27.4：階段を上がってから体を返し、昇る太陽に頭を下げる人々を戒める。5世紀中葉 | P06 | D08-A |
| 8 | マクロビウスI.10.18：七日間とする伝え。354年の暦で12月17日にSATVRNALIA→23日まで | P07 | D09-A |
| 9 | ミトラスを12月25日と結ぶ古代の証拠はないとする研究（Hijmans）。「全史料にない」は未確認→**暦の行に名がないことだけ言う** | P07 | （文字） |
| 10 | テルトゥリアヌス『ユダヤ人反駁』8：受難を3月25日。紀元200年前後 | P08 | D10-A |
| 11 | 『至点と分点について』（4世紀とされる匿名説教）：主は3月25日に身ごもられた。アウグスティヌス『三位一体論』IV.5.9：受胎は受難と同じ3月25日と**信じられ**、降誕は12月25日と**伝えられる**。5世紀初め | P08・P09 | D12-A |
| 12 | 東方の1月6日（エピファニオス51.24）。4月6日から数えたという因果は**復元説**。アルメニア使徒教会は1月6日に降誕と神現を祝う（エルサレムは旧暦で1月19日） | P10 | D13-A |
| 13 | クリュソストモス『降誕の説教』§1（PG 49 col.351）：まだ十年にならない。西の人々には古くから知られてきた。380年代後半 | P11 | D14-A |
| 14 | プリニウス『博物誌』XVIII §221：冬至はほぼ12月25日（fere）、§246：春分は3月25日に達するように見える（videtur）。1世紀の暦の目安 | P13 | D16-A |

## 台本（英語・メイン）v02

章は6つ。P02のあとにオープニング（4秒）を入れる。証拠ボードを出すときは、カードを置く音は入れず、0.9秒の間をとる。

### C01 A Date Without a Source

**P01** Why is Christmas on December twenty-fifth? Every year, on that day, people around the world celebrate the birth of Jesus. And every year, you may hear the same explanation. The early Christians, it is said, simply took over a Roman winter festival, a feast of the sun, or the Saturnalia. It is a tidy answer. But the oldest sources are still here, and they tell a more careful story.

**P02** The Gospels describe the birth in Bethlehem, the shepherds, and the star. They never give a day or a month. For about two centuries, we find no clear sign that Christians kept the birthday each year. Around the year two hundred, Clement of Alexandria noted that some people had tried to work out the day. He lists several answers. December twenty-fifth is not among them.

（ここでオープニング）

### C02 The Oldest Record

**P03** The date first appears in a book made in Rome in the year three fifty-four. It was an illustrated calendar, dedicated to a man named Valentinus, and lettered by the calligrapher Filocalus. The original is lost. We know it through later copies.

**P04** One section lists the days on which the church of Rome remembered its martyrs. The very first line reads: eight days before the kalends of January, Christ is born in Bethlehem of Judea. Counted the Roman way, that is December twenty-fifth. Many scholars think this list goes back to about three thirty-six. The same book also has the public Roman calendar. And on the same day, it reads: birthday of the Unconquered, thirty chariot races. The word sun is not written there.

**P05** So two celebrations share one date, in one book. Which came first? Scholars have offered two main answers. Let us place the evidence for each, one piece at a time.

### C03 Answer One: The Sun

**P06** The first answer begins with the sun. In two seventy-four, the emperor Aurelian built a magnificent temple in Rome to Sol, the sun god. Perhaps, the idea goes, the church placed the birth of Christ on the sun's own festival. There is support. A note in the margin of a Syriac manuscript says that the pagans celebrated the birthday of the sun on December twenty-fifth, that Christians joined in, and so church leaders moved the feast to that day from January sixth. And in the four hundreds, Pope Leo the Great scolded Christians who climbed the steps of Saint Peter's, then turned around and bowed to the rising sun.

**P07** But no one knows who wrote that margin note, or when. It was printed in seventeen twenty-one, and it is not an eyewitness to the choice. Leo, too, does not say why the date was chosen. And no clear source from before three fifty-four has been found that puts a festival of the sun on December twenty-fifth. What about the Saturnalia? The calendar of three fifty-four marks it on December seventeenth, and Macrobius says it lasted seven days. That ends on the twenty-third. You may also hear about the god Mithras. The calendar line does not name him.

### C04 Answer Two: The Calculation

**P08** The second answer begins not with a birth, but with a death. Early Christian writers tried to work out the day on which Jesus died. Around the year two hundred, Tertullian placed it on March twenty-fifth. Later writers linked that day to the day his life began, the day he was conceived.

**P09** A sermon thought to come from the three hundreds says it plainly: our Lord was conceived on March twenty-fifth. Nine months later is December twenty-fifth. Early in the four hundreds, Augustine writes it too. He is believed, Augustine says, to have been conceived on March twenty-fifth, the day on which he also suffered. And he was born, by tradition, on December twenty-fifth.

**P10** In the east, many churches kept January sixth as the feast of his birth and baptism. Some scholars think a similar count, from April sixth, lies behind that date, but that is a reconstruction. The Armenian Church still celebrates the birth of Christ on January sixth. And here, too, there is a gap. These writers were working after the feast of December twenty-fifth already existed. Their reasoning may explain how the date was chosen. Or it may be a reason given afterwards.

### C05 How the Date Spread

**P11** The Roman date travelled east. In the late three eighties, in the city of Antioch, John Chrysostom told his listeners that they had known this feast for less than ten years. In the west, he said, people had known it from long ago.

**P12** So the oldest record is Roman, from the three hundreds. And the two answers are not quite the same kind of evidence. The sun gives us a festival on the same day. The calculation gives us a reason, written by Christians themselves. Neither gives us a record of the choice being made.

### C06 So, Why December Twenty-Fifth?

**P13** There is one more piece. In the first century, Pliny the Elder wrote that the winter solstice falls at about December twenty-fifth, and that the spring equinox seems to fall on March twenty-fifth. These were calendar markers, not exact measurements. But a feast of the sun would fit at the solstice. So would a birth counted nine months from March twenty-fifth. Perhaps the two answers were never really rivals. They may point to the same turning of the year.

**P14** So, why is Christmas on December twenty-fifth? The oldest record we have comes from Rome, in the three hundreds. One answer says the date was set beside a festival of the sun. The other says it was counted from March twenty-fifth. Each has evidence, and each has a gap. The sources do not let us choose with certainty.

**P15** Every story has an origin. Sometimes, two stories point to the same day.

**P16** This video is based on historical texts and public museum and library collections. The narration uses synthetic speech. Sources and terms of use are listed in the description. If you enjoyed this story, please like the video and subscribe for more quiet origins. Thank you for watching.

## 台本（日本語）v02

**P01** クリスマスは、なぜ12月25日なのでしょうか。毎年この日、世界中の人々がイエスの誕生を祝います。そして毎年のように、同じ説明を耳にします。初期のキリスト教徒は、ローマの冬の祭り、太陽の祭りやサトゥルナリアを、そのまま引き継いだのだ、と。すっきりした答えです。けれど、いちばん古い資料は今も残っていて、もっと慎重な話を伝えています。

**P02** 福音書は、ベツレヘムでの誕生、羊飼いたち、そして星を語ります。けれど、その日付は、日も月も書いていません。およそ200年のあいだ、キリスト教徒が毎年誕生日を祝っていたという、はっきりした記録は見当たりません。200年ごろ、アレクサンドリアのクレメンスは、その日を割り出そうとした人々がいたと記しています。挙げられた答えはいくつかあります。12月25日は、その中にありません。

**P03** この日付が初めて現れるのは、354年にローマで作られた一冊の本です。絵の入った暦の本で、ウァレンティヌスという人物に献じられ、書家フィロカルスが文字を記しました。元の本は失われ、後の時代の写しで伝わっています。

**P04** その中に、ローマの教会が殉教者たちを記念した日を並べた一覧があります。その最初の行には、こうあります。「1月の朔日の8日前、キリスト、ユダヤのベツレヘムに生まれる」。ローマの数え方で、これは12月25日です。この一覧は、336年ごろまでさかのぼると考える学者が多くいます。同じ本には、ローマの公の暦も収められています。そして、同じ日に、こう書かれています。「不敗者の誕生日。戦車競走30回」。太陽という言葉は、そこには書かれていません。

**P05** 一冊の本の中で、二つの祝いが同じ日に並んでいるのです。どちらが先だったのか。学者たちは、主に二つの答えを出してきました。それぞれの証拠を、一つずつ置いていきましょう。

**P06** 一つ目の答えは、太陽から始まります。274年、皇帝アウレリアヌスは、ローマに太陽神ソルの壮麗な神殿を建てました。教会は、太陽の祭りの日にキリストの誕生を置いたのではないか、という考えです。これを支える資料もあります。シリア語の写本の欄外に書かれた書き込みは、こう言っています。異教徒は12月25日に太陽の誕生日を祝っていて、キリスト教徒もそれに加わった。そこで教会の指導者たちは、祭日を1月6日からこの日に移したのだ、と。そして400年代、ローマの司教レオは、サン・ピエトロ聖堂の階段を上ってから振り返り、昇る太陽に頭を下げる信徒たちをいさめました。

**P07** けれど、その欄外の書き込みを、誰がいつ書いたのかは分かっていません。印刷されたのは1721年で、日付が選ばれたときを見ていた人の証言ではありません。レオも、なぜその日が選ばれたのかは語っていません。そして、354年より前に、太陽の祭りを12月25日に置く、はっきりした資料は見つかっていません。では、サトゥルナリアはどうでしょう。354年の暦は、この祭りを12月17日に記し、マクロビウスは7日間続いたと伝えています。それなら終わりは23日です。ミトラスという神の話も耳にします。けれど、暦のその行に、ミトラスの名はありません。

**P08** 二つ目の答えは、誕生ではなく、死から始まります。初期のキリスト教の書き手たちは、イエスが亡くなった日を割り出そうとしました。200年ごろ、テルトゥリアヌスは、それを3月25日としています。後の書き手たちは、その日を、イエスの命が始まった日、つまり身ごもられた日と結びつけました。

**P09** 300年代のものと考えられている説教は、はっきりとこう言います。主は3月25日に身ごもられた、と。その9か月後は、12月25日です。400年代の初め、アウグスティヌスもそう書いています。主は3月25日に身ごもられたと信じられている。その日は、主が苦しみを受けた日でもある。そして、言い伝えによれば、12月25日に生まれた、と。

**P10** 東方では、多くの教会が、1月6日をイエスの誕生と洗礼の祝日としていました。その日付の背後にも、4月6日から数える同じような計算があったと考える学者もいますが、それは復元された説です。アルメニア教会は、今も1月6日にキリストの誕生を祝っています。そして、ここにも空白があります。これらの書き手が書いたのは、12月25日の祭りがすでにあった後でした。その考えが日付を決めたのかもしれません。あるいは、後から添えられた理由なのかもしれません。

**P11** ローマの日付は、東へ伝わりました。380年代の後半、アンティオキアの町で、ヨアンネス・クリュソストモスは聞き手たちに、この祭りを知ってから、まだ10年にならない、と語っています。西の人々は、ずっと前から知っていた、と。

**P12** つまり、最も古い記録はローマのもので、300年代です。そして、二つの答えは、同じ種類の証拠ではありません。太陽の説が示すのは、同じ日にあった祭りです。計算の説が示すのは、キリスト教徒自身が書いた理由です。どちらも、その日が選ばれたときの記録ではありません。

**P13** もう一つ、置いておきたいものがあります。1世紀、大プリニウスは、冬至はおよそ12月25日、春分は3月25日にあたるように見える、と書きました。これは暦の上の目安で、正確な観測ではありません。けれど、太陽の祭りは冬至に来ます。3月25日から9か月を数えた誕生も、そこに来ます。二つの答えは、もともと争い合うものではなかったのかもしれません。同じ年の変わり目を指していたのかもしれないのです。

**P14** では、クリスマスはなぜ12月25日なのか。私たちが持つ最も古い記録は、300年代のローマのものです。一つの答えは、太陽の祭りの隣に日付が置かれたと言います。もう一つの答えは、3月25日から数えられたと言います。どちらにも証拠があり、どちらにも空白があります。資料は、どちらかを確かに選ばせてはくれません。

**P15** すべての物語には、始まりがあります。ときには、二つの物語が、同じ一日を指しているのです。

**P16** この動画は、歴史資料と、美術館・図書館の公開コレクションにもとづいています。ナレーションには合成音声を使っています。出典と利用条件は説明欄に記載しています。楽しんでいただけたら、高評価とチャンネル登録で、これからも静かな起源の物語をお楽しみください。ご視聴ありがとうございました。

## 画面の案（素材IDは[素材候補](wom15_素材候補_20261120.md)）

| 区間 | 証拠ボード | 画面 | 素材 |
|---|---|---|---|
| P01 | — | 0秒からサヴォルドの夜の降誕（暖かい光）を全面 → アウレリアヌスの硬貨（ソル） | D01-A → D04-A |
| P02 | — | 福音書の刊本のルカ2章 → クレメンスの刊本（日付の行に寄る） | D02-A → D03-A |
| P03 | — | 1888年刊本の354年の本の装飾扉（写しの複製） | D05-T |
| P04 | — | Mommsen 1892 p.71「VIII kal. Ian. natus Christus in Betleem Iudeae.」に寄って囲む → 12月表の「N. Invicti. CM. XXX.」の行に寄って囲む | D05-A → D06-A |
| P05 | **空のボード** | 証拠ボード（左右に354年のカードを1枚ずつ置く） | 文字 |
| P06 | — | 別の硬貨（ソル）→ Assemaniの刊本の欄外注の頁 → 旧サン・ピエトロの前庭の版画（人物は小さく） | D04-B → D07-A → D08-A |
| P07 | 説Aの側に `AUTHOR AND DATE UNKNOWN`・`NO CLEAR SOURCE BEFORE 354` | マクロビウスの刊本（七日間の行）→ 証拠ボード | D09-A・文字 |
| P08 | — | テルトゥリアヌスの刊本（VIII Kalendas Aprilis の行）→ 受胎告知の絵 | D10-A → D11-A |
| P09 | — | アウグスティヌスの刊本（3月25日・12月25日の行）→ 「3月25日＋9か月＝12月25日」の暦の模式図 | D12-A・文字 |
| P10 | 説Bの側に `AFTER THE DATE EXISTED` | 東方三博士の礼拝の絵（1月6日）→ 証拠ボード | D13-A・文字 |
| P11 | — | クリュソストモスの説教のラテン語引用頁（「まだ十年にならない」）→ ローマとアンティオキアの位置だけの模式図（経路の線は引かない） | D14-A・文字 |
| P12 | **両方の側に並んだボード** | 証拠ボード | 文字 |
| P13 | — | 冬の日の出の風景画 → プリニウスの刊本（§221）→ 暦の模式図（12月25日に冬至・3月25日に春分、「目安」と表記） | D15-A → D16-A・文字 |
| P14 | そろった全体 | 証拠ボード → メングスの降誕（冒頭とは別の作品） | D01-C |
| P15 | — | 冬の夜明けの風景（P13と別の絵） | D17-A |
| P16 | — | 終わりのカード（第14話と同じ型） | — |

- 札はv01から3枚を差し替えた：`WRITTEN CENTURIES LATER` → `AUTHOR AND DATE UNKNOWN`、`NO ANCIENT SOURCE` → `NO CLEAR SOURCE BEFORE 354`（照合5・6のとおり言い切らない）。`EARLIEST RECORD` は使わない（P04の行そのものが見えるので不要）。
- 硬貨D04-A・Bは撮影者（Sandir）のCC0。クレジットに撮影者名を入れる。写本そのものの画像は使わない（保留）。
- 未使用の候補：D05-B（1850年刊本）、D06-I（1888年刊本の12月の挿絵）、D11-B、D13-B、D17-B・C。D06-IはP03の差し替え候補。

## サムネの案（168pxで比べる）

- **案A（推奨）**：夜の降誕の絵（暗い場面に暖かい光、主役1つ）を全面＋大きな字 `WHY DEC 25?`（2行まで）。チャンネルの型（第1話アヌビス以来の「暗い場面＋暖かい光」）どおり。
- 案B：ローマの太陽神の硬貨を大きく＋`THE SUN'S BIRTHDAY?`。資料の小窓は168pxで読めないので入れない。
- どちらも題名をそのまま繰り返さない。人物の顔（聖母子）は絵の中のもので、写実のAI画ではない。

## ショートの案（本編合格後に別依頼）

| | 見出し（照合後に決める） | 中身 | 役割 |
|---|---|---|---|
| S1 | `THE OLDEST CHRISTMAS DATE` | 354年の暦の最初の行と、同じ日の「不敗者の誕生日」 | 新しい人に届く |
| S2 | `SATURNALIA ENDED ON DEC 23` | 354年の暦の12月17日とマクロビウスの七日間（照合8で確認） | よく聞く話の点検 |
| S3 | `WHY DEC 25? TWO ANSWERS` | 3月25日から9か月。「では、太陽の説は？」を残して本編へ | 本編へ |

12/2（火）が本編のある日なのでショートは2本まで（S1は12/2 18:00、S2・S3は12/3・12/4の12:00の案）。

## v01からの変更点（照合による）

| 段落 | v01 | v02 | 根拠（照合） |
|---|---|---|---|
| P01 | a slightly different story | a more careful story | 結論を「異教説はまちがい」と読ませないため |
| P02 | no sign that Christians marked the birthday at all／answers, in the spring | no clear sign that Christians kept the birthday each year／「春」を削除 | 1・2（全地域の不存在は未確認、クレメンスの日付は春だけではない） |
| P03 | a wealthy Christian named Valentinus, by the calligrapher Filocalus | dedicated to a man named Valentinus, and lettered by the calligrapher Filocalus | 3（裕福なキリスト教徒は推定、titulavit＝標題を記した） |
| P04 | Scholars think this list was put together around 336 | Many scholars think this list goes back to about 336。「The word sun is not written there.」を追加 | 3・4（336年は復元年代、行にsolisがない） |
| P06 | the Unconquered Sun／Centuries later, a note…／bowed to the rising sun on the steps | the sun god／欄外注の趣旨に「Christians joined in」「from January sixth」を足す／階段を上って振り返る、の順 | 5・6・7 |
| P07 | written some 800 years after the fact／no source older than 354／even at its longest／Mithras: No ancient source says so | 筆者・年代は不明、1721年刊、目撃証言ではない／no clear source…has been found／暦の12月17日＋マクロビウスの7日→23日／ミトラスは「暦の行に名がない」だけ | 5・6・8・9 |
| P08 | some believed that a holy life was complete, measured in whole years | Later writers linked that day to the day…he was conceived | 11（聖人一般の規則は二例から導けない） |
| P09 | Around the year 400, Augustine | 4世紀の匿名説教を先に置き、Augustineは「Early in the four hundreds」。believed／by traditionの区別を保つ | 11 |
| P10 | some counted from a different spring date, and arrived at January sixth | 1月6日は誕生と洗礼の祝日、4月6日からの計算は「復元説」と明示 | 12 |
| P11 | In about 386…It had come, he said, from the west. Within a few generations…most of the Christian world | In the late 380s／西の人々は古くから知っていた／普及の一文を削除 | 13 |
| P12 | Neither has a source from before the date appeared | Neither gives us a record of the choice being made | 5・11 |
| P13 | In the Roman calendar of the time, Dec 25 was counted as the winter solstice | 1世紀のプリニウスの目安（fere・videtur）として言い、正確な観測ではないと添える | 14 |

## 本人に確認すること

1. **台本v02**（上の変更点）でよいか。結論は変えず、言い切りを照合で確かめた範囲に弱めた。
2. **尺**：約8分10秒の見込みでよいか。
3. **サムネ**：案A（サヴォルドの夜の降誕＋`WHY DEC 25?`）と案B（アウレリアヌスの硬貨＋`THE SUN'S BIRTHDAY?`）を168pxで比べてよいか。
4. よければ、台本JSONと制作依頼を作る（公開の目安12/2（火）09:00は維持）。
