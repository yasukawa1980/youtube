# Quiet Origins 第12話「サンタクロースの赤い服」：テーマ設計と台本 v02（2026-11-05 Claude）

管理ID：`wom12`。状態：**台本v02を本人承認（2026-11-05「全ておまかせで大丈夫です」）。確認3点はClaudeの推奨どおり：N08はイェールの公開方針を確かめてから使う、N04は使う、公開は11/14（土）09:00。台本JSON `episodes/EP012_SantaClaus/records/content_en.json`・`content.json` と[制作依頼](wom12_制作依頼_20261105.md)を作成。** v01は本人了承済み（2026-11-04「概ね大丈夫です」：題は案A、公開11/14（土）09:00、台本の方向、LoCは1930年以前の米国出版物に限り可、Codexへの依頼）。尺は本人指定で6分に合わせない。v02はCodexの[原典照合](research/wom12_原典訳文_20261105.md)と[素材候補](wom12_素材候補_20261105.md)に合わせて直した版（変更点は末尾）。v01はGitの履歴（`47478fd`）。音声・映像は未制作。エピソードのフォルダは `episodes/EP012_SantaClaus/`（制作依頼のときに作る）。

## この回で試すこと：変遷型（本人決定 2026-11-04「Aでいきましょう」）

第1〜11話は「通説 → 原典で確かめる → 答え」を一つの時代の資料の中で進める形だった。第12話は**一つのイメージが時代でどう変わったかを、絵を年代順に並べて見せる「変遷型」**にする。コンセプト（最古の資料で確かめる・静かな語り・Kokoroの声・約6分・AI映像なし）は変えない。変える要素は次の3つに絞る（効果を測りやすくするため）。

| | これまで | 第12話（変遷型） |
|---|---|---|
| 章の立て方 | 話題ごと | **年代ごと**（4世紀 → 1087 → 1812 → 1821 → 1823 → 1858〜1881 → 1864〜1904 → 1931） |
| 画面 | 資料を1点ずつ寄りで見せる | 資料に加え、**画面の下に年代の帯**（細い線と年の目盛り。いまの年だけ大きく）を全編に出す。章の変わり目に、それまでのサンタを左から並べ直す「並べ直しカード」（3回） |
| サムネ・題 | 「AかBか？」型の題、絵1点 | **同じ人物の絵を2〜3点、年つきで横に並べる**。題は俗説を問う形 |

効果は、本編の表示回数の出どころ（ブラウジング・検索・関連動画）とクリック率を第9〜11話と比べて見る。1本では決めず、変遷型を2〜3本続けて判断する。

## 第10話（クランプス）との違い

| | 第10話 クランプス（`hqYSHCpQNLw`） | 第12話 サンタ |
|---|---|---|
| 主役 | ニコラウスの**供**（悪魔の姿） | ニコラウスが**アメリカでサンタになる**までと、その**服の色** |
| 聖ニコラウス | 黄金伝説（金を家に3回投げ入れる）、祝日と子ども | **P03〜P04の2区間だけ**。伝説の細部は繰り返さず、第10話へつなぐ |
| 新しい内容 | — | アーヴィング1812、『子どもの友』1821（赤い上着・トナカイ1頭）、「聖ニコラスの訪問の記」1823、ホーマー1858、ナスト1863・1881、色刷りの茶色（1864）と赤（1902・1904）、1931年の広告 |

## 狙い

- 題（本人了承 11/4）：**Did Coca-Cola Really Make Santa Red?**／サンタを赤くしたのは、本当にコカ・コーラなのか
- 冒頭の問い：「サンタの赤い服は、1930年代のコカ・コーラの広告から始まった」とよく言われる。では、それより古い版画・本・詩・雑誌を年の順に並べると、何が分かるか。
- 結論（照合後）：
  1. 始まりは4世紀のミュラの司教ニコラウス。生涯について歴史的に確かなことはほとんどない（1911年の百科事典）。1087年、バーリの船乗りたちが遺体（聖遺物）をミュラから持ち去り、バーリへ運んだ。祝日12月6日とその前夜に、ヨーロッパの一部で子どもに贈り物。オランダでは司教の姿のシンタクラース。
  2. **1812年**のアーヴィング『ニューヨーク史』改訂第2版（1809年の初版ではない）：オロフの夢に、毎年子どもへ贈り物を運ぶ「車（waggon）」に乗り、木々のてっぺんの上を来る聖ニコラス。そり・トナカイはまだない。
  3. 1821年『子どもの友』（ニューヨーク、ギリー刊）：「Old SANTECLAUS with much delight / His reindeer drives this frosty night」。挿絵はトナカイ1頭のそり。**イェール大学所蔵の一冊では、サンテクロースの上着は赤い**（Codexが原頁を目視）。
  4. 1823年12月23日『トロイ・センティネル』に無署名で「Account of a Visit from St. Nicholas」。編集者は寄稿者を知らないと前書き。のちにムーアの名で出版され、1844年に彼の自作詩集にも収録。詩は毛皮・8頭の小さなトナカイ・ばら色の頬・さくらんぼの鼻を言うが、**服の色は言わない**。
  5. 1858年、『ハーパーズ・ウィークリー』にウィンスロー・ホーマーの「Santa Claus and His Presents」。ナストは1863年1月3日号の「Santa Claus in Camp」（星柄の上着・縞のズボン、北軍の野営地）から1886年まで、同誌のクリスマスの絵を描いた（23年）。1881年1月1日号の「Merry Old Santa Claus」は白黒。
  6. 色刷り：1864年ボストンのプラング社の詩の刊本では**黄土色〜淡い茶色**の服。1902年12月3日号・1904年12月7日号の『パック』の表紙は赤い服。**緑・青は確認できていないので言わない**。
  7. サンドブロムがコカ・コーラのためにサンタを描いたのは1931年から1964年まで。会社の公式の歴史：「Santa appeared in a red coat before Sundblom painted him.」
  8. 結び（解釈。スミソニアン国立アメリカ歴史博物館の説明に寄せる）：広告は赤を発明していない。けれど、温かく人間らしい一人のサンタを繰り返し見せ、広く親しまれる姿にするのを後押しした。
- 尺：**6分に合わせない（2026-11-04 本人指定）**。話速は第11話と同じにし、速めない。間（区間の間・並べ直しカードで絵を見せる時間）も削らない。v02は英語835語で、約6分40秒〜7分の見込み（第11話797語・381秒から）。尺を縮めるために文を削ったり話速を上げたりしない。
- 公開日：本人了承は**11/14（土）09:00**。ただし11/5のショート前倒しで**11/12以降は予約がない**ので、早める案もある（下の表。本人が決める）。

### 公開日の照合（2026-11-05、`wom_ショート日程変更_自動実行修正依頼_20261105.md` の組み直し後の表で確認）

| 日 | 本編 | ショート | 合計 | メモ |
|---|---|---|---|---|
| 11/10（火） | 第11話 `Xa0bcKAfgJI` 09:00 | 2 | 3 | 上限ちょうど |
| 11/11（水） | — | 2（H2・H3） | 2 | 本編を入れると3本で上限内だが、第11話の翌日 |
| 11/12（木） | — | 0 | 0 | 早める案：本編09:00＋N1 18:00 |
| 11/13（金） | — | 0 | 0 | |
| 11/14（土） | 本人了承の案 | 0 | 0 | ショートN1〜N3は11/15〜17に各1本、または本編なしの日に3本まで |

制作の目安：v02の承認が11/5〜6なら、確認版v01は11/7〜8、Claude確認と本人試聴が11/8〜9。11/12公開なら予約は11/11中、11/14なら11/13中。

## 注意して扱う点

- **コカ・コーラの広告画像・ロゴ・商標の文字デザインは使わない**。1931年の広告は米国でまだ著作権が切れていない。画面は文字カード「1931 — Haddon Sundblom」だけ。会社を悪く言わない（「うそを広めた」と言わない）。
- **「コカ・コーラは何もしていない」とも言わない**。「赤を発明したのではない」と「広く定着させた（解釈）」を分けて言う。
- **宣伝にしない**：飲み物の名前は俗説を説明する所と結論の所だけ。説明欄に商品へのリンクを置かない。
- **聖ニコラウスの伝説は「伝えられる」と主語を保つ**。第10話の照合結果を引き継ぐ：黄金伝説では金を「家の中へ」3回投げ入れる（「窓」は絵の図像）。第12話では細部を言わない。
- **ズワルテ・ピートは扱わない・映さない**（第10話と同じ。シンタクラースの版画は供の写っていないものだけ）。
- **詩の作者**：「のちにムーアの名で出版され、1844年に自作詩集へ」と言い、ムーアの作と断定しない。ヘンリー・リヴィングストン説などの論争には立ち入らない。
- **オランダ移民がサンタを持ち込んだ、と断定しない**。ニューヨークでのオランダの習わしの影響の大きさは研究で見方が分かれる（アーヴィングらの創作が大きいとする説がある）。台本は「ニューヨークの作家たちがこの名を取り上げた」まで。
- **服の色の言い方**：照合で実物を確かめた色だけ（1821赤・1864茶・1902/1904赤）。緑・青は言わない。「赤が最も多かった」など割合は言わない。**1821年の赤は「イェールの一冊では」と限る**（手彩色で一冊ごとに違う可能性がある）。中世の司教の絵の赤い法衣を、サンタの赤い服の証拠にしない。
- **1087年**：「持ち去った」までで、盗みの是非は論じない。N06の絵を1087年の場面と言わない。
- **ナスト1863**：政治風刺（人形と首の縄）の部分は大写しにしない・説明しない。
- **人を描いた絵の中の子どもの顔を大写しにしない**。19世紀の挿絵の誇張された人種表現が写るものは使わない。
- **過去の場面の再現はAIで作らない**。サンタ・ニコラウス・子どもはAIで作らない。AI映像は使わない。
- **読み**：Myra、Bari、Sinterklaas、Washington Irving、Santeclaus、Troy、Clement Clarke Moore、Thomas Nast、Harper's Weekly、Puck、Haddon Sundblom。新しい語の読み替えは制作時に記録する。日本語はミュラ、バーリ、シンタクラース、ワシントン・アーヴィング、サンテクロース、トロイ、クレメント・クラーク・ムーア、トマス・ナスト、ハーパーズ・ウィークリー、パック、ハッドン・サンドブロム。

## 出典（照合後。詳しくは[原典照合](research/wom12_原典訳文_20261105.md)）

| ID | 出典 | 台本 | 照合の結果と台本での扱い |
|---|---|---|---|
| N-S01 | Michael Ott, "St. Nicholas of Myra," *Catholic Encyclopedia* vol.11（1911、Web翻刻） | P03・P04 | 「4世紀のミュラの司教だったこと以外、歴史的に確かなことはほとんどない」。1087年にイタリアの商人が遺体を盗みバーリへ。12月6日の贈り物。St. Nicholas Centerの解説で「バーリの船乗り」 |
| N-S02 | Washington Irving, *A History of New York*, 2nd ed., New-York 1812（NYPL所蔵、IA） | P05 | **1812年版** p.106を頁画像で確認。`riding over the tops of the trees, in that self same waggon wherein he brings his yearly presents to children`。1809年初版ではOCR検索で見つからない（全頁の目視はしていない）ので「1809年」とは言わない |
| N-S03 | *The Children's Friend*, New York: William B. Gilley, 1821（Yale Beinecke, Shirley 4065） | P06 | p.1を原頁で確認：`Old SANTECLAUS with much delight / His reindeer drives this frosty night`。挿絵は1頭のそり、**赤い上着・黒い帽子**。ギリーは出版者で、作者とは言わない |
| N-S04 | "Account of a Visit from St. Nicholas," *Troy Sentinel*, 1823-12-23, p.3（切抜きの再掲スキャン） | P07 | 4句を画像で照合。服の色の語なし。編集者は作者を知らないと前書き。1837年の詩集にムーアの名、1844年の自作詩集（The Strong、LoC。頁画像は未照合） |
| N-S05 | Homer 1858（Met 393182）、Nast 1863（Met 427502）、Nast 1881（Macculloch Hall TN2015.182）、ナストのクリスマスの絵は1886年まで（MMT Library、HarpWeek） | P08 | 日付・白黒・星柄と縞を確認。1863〜1886は23年 |
| N-S06 | Prang 1864 *A Visit from St. Nicholas*（LoC 73169323、コマ10）、*Puck* 1902-12-03（LoC 2010652186）、1904-12-07（LoC 2011645591） | P09 | 黄土色〜淡茶（1864）、赤（1902・1904）を実物で確認。緑・青は未確認なので言わない。「色刷りが安くなった」は根拠未確認なので言わない |
| N-S07 | The Coca-Cola Company, "Haddon Sundblom and the Coca-Cola Santas"（公式、文のみ） | P10 | 1931年に登場、最後の制作1964年。`Santa appeared in a red coat before Sundblom painted him.` 会社のサンタ広告全般は1920年代からあるので「会社が初めてサンタを使ったのが1931年」とは言わない |
| N-S08 | Smithsonian NMAH, "How Santa brought Coca-Cola in from the cold"（2015） | P11 | 既にあった赤白の姿を広告が広めた、という博物館の説明。「多くの歴史家」とは言わない |

## 台本（英語・メイン）v02

章は5つ。P02のあとにオープニング（4秒）を入れる。章の見出しに年を入れ、画面の下の年代の帯と合わせる。

### C01 The Red Suit

**P01** Every December, the same story comes back. Santa Claus wears red because of Coca-Cola. In the nineteen thirties, the company's advertisements showed a warm, round Santa in a red suit, and many people believe that is where the red suit began. It is a good story. But the older pictures are still here: prints, books, poems and magazine covers. We can put them in order. So, did Coca-Cola really make Santa red?

**P02** In this episode, we follow Santa through time: a bishop in the fourth century, a dream in a New York history book, a little book with a single reindeer, a poem with eight, a drawing made in wartime, and the color of his coat, long before nineteen thirty-one.

（ここでオープニング）

### C02 Fourth Century: A Bishop of Myra

**P03** The story begins with a real name. Nicholas was a bishop of Myra, a town in what is now southern Turkey, in the fourth century. Beyond that, almost nothing about his life is historically certain. The stories of his kindness came later, and they made him a saint of gift-giving.

**P04** In ten eighty-seven, sailors from Bari, in southern Italy, took his remains from Myra and carried them home to their own city. In parts of Europe, children came to receive gifts on his feast day, December the sixth, and on the evening before. In the Netherlands, he became Sinterklaas, and he is still dressed as a bishop.

### C03 1812 to 1823: New York

**P05** Across the ocean, New York writers took up the name. In eighteen twelve, in the expanded second edition of his comic History of New York, Washington Irving described a dream. In it, the good Saint Nicholas came riding over the tops of the trees, in the same wagon in which he brings his yearly presents to children. There is no sleigh here yet, and no reindeer.

**P06** Nine years later, in eighteen twenty-one, a small illustrated book printed in New York, The Children's Friend, changed that. Its first page begins: Old Santeclaus with much delight, his reindeer drives this frosty night. The picture shows his sleigh, pulled by a single reindeer. And in one surviving copy, now at Yale University, Santeclaus is already wearing a red coat.

**P07** Two years later, in eighteen twenty-three, a newspaper in Troy, New York, printed an unsigned poem, Account of a Visit from St. Nicholas. The editor wrote that he did not know who had sent it. It was later published under Clement Clarke Moore's name, and in eighteen forty-four it appeared in his own book of poems. Its Saint Nicholas is chubby and plump, a right jolly old elf. He is dressed all in fur, from his head to his foot. He drives a miniature sleigh with eight tiny reindeer. His cheeks are like roses, his nose like a cherry. But the poem never gives his clothes a color.

### C04 1858 to 1904: Ink and Color

**P08** Magazines carried Santa to many more readers. In eighteen fifty-eight, Harper's Weekly printed Santa Claus and His Presents, drawn by a young Winslow Homer. Soon after, Thomas Nast began drawing Santa for the same magazine, and he kept drawing him for more than twenty years. In January eighteen sixty-three, during the American Civil War, his Santa visited a Union army camp, in a coat of stars and striped trousers. In eighteen eighty-one came his Merry Old Santa Claus: round, bearded, with a pipe and an armful of toys. These pictures were printed in black and white.

**P09** Color prints tell us more. In a book of the poem published in Boston in eighteen sixty-four, Santa's suit is a pale, earthy brown. So his coat was not fixed. But red kept coming back. In December nineteen oh two, and again in nineteen oh four, the magazine Puck put a red-suited Santa on its Christmas covers, decades before the famous soft-drink paintings.

### C05 1931: Could a Company Make Santa Red?

**P10** The illustrator Haddon Sundblom began painting Santa for Coca-Cola in nineteen thirty-one, and he painted his last one for the company in nineteen sixty-four. The company's own history says it plainly. Santa appeared in a red coat before Sundblom painted him.

**P11** So Coca-Cola did not invent the red suit. But year after year, its advertisements showed the same warm, very human Santa, and helped make him familiar to a very wide audience. The color was older. What the advertisements helped spread was one friendly face.

**P12** So, did Coca-Cola really make Santa red? No. A red coat appears more than a century earlier. What changed over time was almost everything else. A bishop became a visitor in the night. The visitor rode a wagon, then a sleigh with one reindeer, then eight. A poem dressed him in fur. And printers spread many versions of him, until one became the face most of us know.

**P13** Every story has an origin. Sometimes, it begins with a bishop, and printers finish it.

**P14** This video is based on historical texts and public museum and library collections. The narration uses synthetic speech. Sources and terms of use are listed in the description. If you enjoyed this story, please like the video and subscribe for more quiet origins. Thank you for watching.

## 台本（日本語）v02

**P01** 毎年12月になると、同じ話が戻ってきます。サンタクロースが赤い服を着ているのは、コカ・コーラのおかげだ、と。1930年代、この会社の広告には、赤い服を着た、温かく丸みのあるサンタが描かれました。赤い服はそこから始まった、と信じる人は少なくありません。よくできた話です。けれど、もっと古い絵は今も残っています。版画、本、詩、雑誌の表紙。それらを年の順に並べることができます。では、サンタを赤くしたのは、本当にコカ・コーラなのでしょうか。

**P02** 今回は、時代を追ってサンタをたどります。4世紀の司教、ニューヨークの歴史の本に書かれた夢、トナカイが1頭だけの小さな本、8頭が登場する詩、戦争のさなかに描かれた一枚の絵。そして、1931年よりずっと前の、彼の上着の色へ。

**P03** 物語は、実在の名前から始まります。ニコラウスは4世紀、いまのトルコ南部にあった町、ミュラの司教でした。それ以外、彼の生涯について歴史的に確かなことは、ほとんどありません。その優しさを伝える物語はのちに生まれ、彼を贈り物の聖人にしました。

**P04** 1087年、南イタリアのバーリの船乗りたちが、彼の遺骸をミュラから持ち去り、自分たちの町へ運びました。ヨーロッパの一部では、彼の祝日、12月6日と、その前の晩に、子どもたちが贈り物を受け取るようになります。オランダでは、彼はシンタクラースになりました。今も、司教の姿のままです。

**P05** 海の向こうでは、ニューヨークの作家たちがこの名を取り上げました。1812年、ワシントン・アーヴィングは、滑稽な『ニューヨーク史』の改訂第2版で、ある夢を描きました。その夢の中で、善き聖ニコラスは、毎年子どもたちに贈り物を運ぶあの同じ車に乗り、木々のてっぺんの上をやって来ます。ここにはまだ、そりもトナカイもありません。

**P06** その9年後、1821年。ニューヨークで刷られた絵入りの小さな本『子どもの友』が、それを変えました。最初の頁は、こう始まります。サンテクロースじいさんは大喜びで、霜の降りる今夜、トナカイを駆る。挿絵には、1頭のトナカイが引くそりが描かれています。そして、今イェール大学にある一冊では、サンテクロースは、もう赤い上着を着ているのです。

**P07** その2年後、1823年。ニューヨーク州トロイの新聞が、作者の名のない一編の詩を載せました。「聖ニコラスの訪問の記」です。編集者は、誰が送ってきたのか知らない、と書いています。この詩はのちにクレメント・クラーク・ムーアの名で出版され、1844年には彼自身の詩集にも収められました。詩の聖ニコラスは、丸々と太った、まことに陽気な年寄りの妖精。頭から足まで、毛皮をまとっています。8頭の小さなトナカイが引く、小さなそりを走らせます。頬はばらのよう、鼻はさくらんぼのよう。けれど詩は、彼の服の色を、一度も言っていません。

**P08** 雑誌が、サンタをもっと多くの読者に届けました。1858年、『ハーパーズ・ウィークリー』は、若きウィンスロー・ホーマーが描いた「サンタクロースと贈り物」を載せています。まもなく、トマス・ナストが同じ雑誌でサンタを描き始め、20年以上描き続けました。1863年1月、南北戦争のさなか、彼のサンタは北軍の野営地を訪れます。星の柄の上着と、縞のズボンで。1881年には「陽気なサンタじいさん」。丸くて、ひげをたくわえ、パイプをくわえ、おもちゃを腕いっぱいに抱えています。これらの絵は、白黒で刷られました。

**P09** 色刷りの絵は、さらに多くを教えてくれます。1864年にボストンで出版された、この詩の本では、サンタの服は淡い土のような茶色です。上着の色は、決まっていなかったのです。けれど赤は、何度も戻ってきました。1902年12月と、1904年にもふたたび、雑誌『パック』はクリスマスの表紙に、赤い服のサンタを載せています。有名な清涼飲料の絵より、何十年も前のことです。

**P10** 画家ハッドン・サンドブロムがコカ・コーラのためにサンタを描き始めたのは、1931年。会社のための最後の一枚は、1964年でした。その会社自身の歴史の解説は、はっきりこう書いています。サンドブロムが描く前から、サンタは赤い上着で登場していた。

**P11** つまり、コカ・コーラが赤い服を発明したわけではありません。けれど、広告は毎年、同じ温かく、とても人間らしいサンタを見せ、その姿をとても多くの人に親しまれるものにするのを後押ししました。色は、もっと古いものでした。広告が広めたのは、一つの親しみやすい顔だったのです。

**P12** では、サンタを赤くしたのは、本当にコカ・コーラだったのか。答えは、いいえ。赤い上着は、100年以上前にもう現れています。時代とともに変わったのは、それ以外のほとんどすべてです。司教は、夜の訪問者になりました。訪問者は車に乗り、やがて1頭のトナカイのそりに、そして8頭のそりに乗りました。詩が彼に毛皮を着せました。そして印刷が、さまざまな姿の彼を広め、その中の一つが、私たちの多くが知る顔になったのです。

**P13** すべての物語には、始まりがあります。ときにそれは一人の司教から始まり、印刷の職人たちが仕上げるのです。

**P14** この動画は、歴史資料と、美術館・図書館の公開コレクションにもとづいています。ナレーションには合成音声を使っています。出典と利用条件は説明欄に記載しています。楽しんでいただけたら、高評価とチャンネル登録で、これからも静かな起源の物語をお楽しみください。ご視聴ありがとうございました。

## 画面の案（素材は[素材候補](wom12_素材候補_20261105.md)から）

| 区間 | 年代の帯 | 画面 | 素材 |
|---|---|---|---|
| P01 | 帯なし | 1902年『パック』の赤いサンタ → 文字カード「1931?」 | N03-A |
| P02 | 帯が左から現れる | 並べ直しカード①（これから出る年の目盛りだけを並べる） | — |
| P03 | 4世紀 | ヘラルト・ダヴィトの聖ニコラウス（c.1500/1520、縦長を上から下へ） | N05-A |
| P04 | 1087 | ヤコポ・ダ・エンポリの聖ニコラウス（c.1610）。**1087年の場面の絵とは言わない**（札は作品名と年だけ） | N06-A |
| P05 | 1812 | 文字カード：1812年版の原文1行（`riding over the tops of the trees, in that self same waggon`）と書名・版 | 文字 |
| P06 | 1821 | **確認1の答えしだい**：可なら『子どもの友』の表紙・p.1の絵（N08）。不可なら文字カード（4行の原文） | N08または文字 |
| P07 | 1823 | 文字カード：原文の4句を1句ずつ（初出の綴り `dress'd`・`rein-deer`）。背景は雪景色を暗く | N12-B（背景） |
| P08 | 1858・1863・1881 | ホーマー1858（寄りは贈り物の部分、子どもの顔に寄らない）→ ナスト1863（人形と首の縄の部分は大写しにしない）→ 文字カード「1881 Merry Old Santa Claus — black and white」 | N11-C・N02-A |
| P09 | 1864・1902・1904 | **確認2の答えしだい**：1864年の茶色のサンタ（N04）→ プラングのカード2点で「色刷りの時代」→ 1904年『パック』の赤。並べ直しカード②（1821赤・1864茶・1902赤・1904赤を横に） | N04-A・N11-A・N11-B・N03-B |
| P10 | 1931・1964 | 文字カード「1931–1964 Haddon Sundblom」と会社の一文の引用（広告画像なし） | 文字 |
| P11 | 帯全体 | 並べ直しカード③（4世紀〜1931を全部並べる。1931は文字だけの枠） | 既出素材の縮小 |
| P12〜P13 | 帯全体 | シスレー「ヴヌー＝ナドンの初雪」（1878）。昼の絵なので「夜」とは札に書かない | N12-A |

- 使わない：N12-C（題がSpring）、N07（Rijksmuseumのログインが必要。新規登録しない）、N09・N10の画像（文字カードで足りる）。N01は条件を満たす画像がないので文字カード。
- N03-A・N03-BはLoCの縮小JPEG（約780×1024）。4Kでの全面表示は粗くなるので、**画面の高さの7割程度までにとどめ、横は余白（紙の色）にする**。サムネも左右に並べる大きさにとどめる。
- サムネ案：左にN04（1864・茶）またはN08（1821・赤）、右にN03-B（1904・赤）、それぞれに年。上に `RED BEFORE 1931?`。

## ショート案（本編合格後に別依頼）

| ID | 見出し | 中身 |
|---|---|---|
| N1 | `SANTA WORE RED IN 1821`（N08が使えないなら `SANTA WAS RED BEFORE 1931`） | 俗説 → 1821年の赤い上着（または1902・1904年の『パック』）→ 答え |
| N2 | `SANTA ONCE WORE THE FLAG` | ナスト1863、北軍の野営地、星柄の上着と縞のズボン |
| N3 | `IN 1821, SANTA HAD ONE REINDEER` | 1812年の車 → 1821年の1頭 → 1823年の8頭 |

公開日は本編の日が決まってから決める（本編のない日は3本まで、本編の日は2本まで）。

## v01からの主な変更（照合による）

- P03：「同時代の記録で確かめられない」→「歴史的に確かなことはほとんどない」（1911年の百科事典の文に合わせた）。
- P04：「運んだ」→「持ち去り、運んだ」（盗み出したとする記録がある）。祝日に「その前の晩」を加えた。司教冠の描写を外した（画像がないため）。
- P05：**1809年 → 1812年の改訂第2版**。原文の「waggon（車）」を入れ、「まだそりもトナカイもない」を加えた。
- P06（新しい区間）：『子どもの友』を独立させ、原文2行と**赤い上着（イェールの一冊）**を加えた。
- P07：「ムーアが名乗り出た」→「ムーアの名で出版され、1844年に自作詩集へ」。編集者の前書きを加えた。引用は初出に合わせた。
- P08：ホーマー1858を加えた。ナストの「20年以上」は1863〜1886で確認。
- P09：「色刷りが安くなった」を削除（根拠未確認）。緑・青を外し、確認できた1864年の茶色だけを言う。
- P10：「会社のサンタの絵は1931年から」→「サンドブロムが1931年から1964年まで」（会社のサンタ広告自体は1920年代からある）。公式の一文を引用。
- P11：「多くの歴史家は考える」を削除。スミソニアンの説明に合わせた。
- P12：「印刷が最後に色を与えた」→「印刷がさまざまな姿を広めた」（中世の絵にもすでに色がある）。「100年以上前に赤」は1821年の一冊による。
- 英語688語 → 835語。

## 本人確認（3点）

1. **N08『子どもの友』（1821、イェール大学）の挿絵を映像に使うか**。1821年の出版で米国では明らかに保護期間が終わっているが、イェールの画面の権利欄は一般的な免責の文で、「パブリックドメイン」とは明記していない。いまの基準（所蔵館の明記、またはLoCの1930年以前の米国出版物）には当てはまらない。**推奨：Codexにイェール大学図書館の公開方針（パブリックドメインの所蔵品の画像を自由に使ってよいと書いているか）を確かめてもらい、書いてあれば使う**。だめなら文字カードで、事実（赤い上着）は台本で言う。
2. **N04（1864年プラング社の本、LoC）を使うか**。LoCの文言が「既知の制限なし（No known restrictions on publication）」ではなく「この資料群に米国の著作権その他の制限があるとは把握していない」。意味はほぼ同じで、1864年の米国出版物。**推奨：了承済みの基準と同じ扱いで使う**（クレジットは表示どおり）。
3. **公開日**：了承済みの11/14（土）09:00のままにするか、空いた11/12（木）09:00に早めるか。**推奨は11/14のまま**（試聴の余裕を残す）。
