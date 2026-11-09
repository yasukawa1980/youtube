# Quiet Origins 絵画02「デラウェア川を渡るワシントン」：テーマ設計と台本 v02（2026-11-10 Claude）

管理ID：`pnt02`。エピソード名（案）：`PNT02_WashingtonCrossing`。
状態：**台本v02 本人了承（2026-11-10「推奨どおりで進める」）。[制作依頼](pnt02_制作依頼_20261110.md)をCodexへ渡す。** 台本JSONは `episodes/PNT02_WashingtonCrossing/records/`（英語は年を読みの形の言葉にしたため707語）。 v01の確認4点は本人了承済み（2026-11-10「推奨どおりで進める」）＝題A・公開11/28（土）09:00・台本の方向・依頼をCodexへ渡す。

v01の史実はClaudeの知識による下調べだった。v02はCodexの[原典照合](research/pnt02_原典訳文_20261110.md)・[素材候補](pnt02_素材候補_20261110.md)・[台帳](research/pnt02_素材台帳_20261110.json)（2026-11-10、コミット `88161c6`）で直した。照合で確かめられなかった点は、言い切らない形にするか削った。

シリーズの定義・作品を選ぶ条件・制作方針の例外（主役の絵の全体は本編で2回まで、別の細部は別素材、AIは静止画も使わない）は [`new-channel/wom13_テーマ設計.md`](../new-channel/wom13_テーマ設計.md) をそのまま引き継ぐ。

## この作品を選んだ理由（選ぶ条件の4つ）と照合の結果

| 条件 | この作品で | 照合の結果 |
|---|---|---|
| 1. 一文で言える「常識とのずれ」 | **アメリカ独立の象徴の絵は、約75年後のドイツで描かれた。兵士が掲げる星条旗は、渡河の時点ではまだ国旗として採用されていなかった** | 保てる。ただし「その旗はまだ無かった」とは言えない（決議の日付は図案の不存在の証明にならない） |
| 2. 絵の外の資料 | ワシントンの手紙（1776年12月27日）、旗の決議（1777年6月14日）、ホイットリッジの回想、1853年の版画、1848年の版画 | 本文は公的な翻刻で確認。**原稿・刊本の画像は未取得**（文字カードにする） |
| 3. PD・CC0の明記 | Met 97.34 は Public Domain、画像はCC0（APIで `isPublicDomain=true`） | 満たす |
| 4. 高解像度 | Metの公開画像 | **一部だけ満たす。** 全図の最大は4,000×2,335px（夜警は14,645px）。Met公式の細部写真5点（長辺3,847〜4,000px）で補う。下の「画像の大きさの扱い」 |

**狙い**：英語圏の視聴者に最も届く1本。夜警と同じ「変遷型」（年代ごとの章・年代の帯・サムネに年）で、**変えるのは主役の絵だけ**にして比べる。

## 狙い

- 題（本人了承 11/10）：**Did Washington Really Cross the Delaware Like This?**／「デラウェア川を渡るワシントン」は、本当にこうだったのか
- 冒頭の問い：アメリカの歴史で最も知られた絵の一つ。氷の川で、ワシントンが小舟に立ち、後ろで星条旗が掲げられる。けれど、この絵は1776年に描かれたものではない。
- 結論（照合後）：
  1. 渡河は1776年12月25日の夜から26日の未明。ワシントンは27日付のハンコック宛ての手紙で、暗くなりしだい渡り始める計画だったが、その夜にできた氷のために砲兵を渡し終えたのが3時、行軍を始めたのが4時近くだったと書いた。「非常に厳しい夜」、行軍は「雪と雹の激しい嵐」の中だった
  2. 絵の空には朝の光と、最後の星がある（Metの1968年と2011年の論文が、朝の光・夜明けと結びつけている）
  3. 星条旗を定めた大陸会議の決議は1777年6月14日で、渡河の約半年後。決議は星の並べ方を定めていない。史跡の解説によれば、渡河の夜にどの旗が掲げられたか、そもそも掲げられたかは分からない
  4. ロイツェは1816年ドイツ生まれ、1825年に家族とアメリカへ渡り、1841年にドイツへ戻ってデュッセルドルフで学んだ。最初の版は1849年に描き始めた。マウントバーノン（ワシントンの旧邸、いまは博物館）の解説では、1848年の革命を支持し、自由と民主主義への新たな闘いを励ますことを望んだ
  5. ホイットリッジの回想（Metの1968年の論文が引用）では、舵を取る人と、ワシントン自身のモデルを務めた。ワシントンの頭部はウードンの像を参考にしたとされる
  6. 最初の版は1850年11月のアトリエの火事で傷み、修復されて1863年にブレーメンへ。1942年の空襲で失われた。2枚目は1851年に描き始め、同年ニューヨークで展示され、多くの人が見に来た。1853年にニューヨークのグーピル社から版画が出た（LoCの目録）
  7. 1897年、ジョン・スチュアート・ケネディがMetへ寄贈。大きさは378.5×647.7cm
  8. 結び：**この絵はあの夜の記録ではない。75年後の画家が、自分の時代に向けて描いたあの夜の姿で、今の私たちが思い浮かべるのは、その姿のほう**
- 尺の目安：**約5分半**（夜警と同じ話速。分量は末尾の「v02の実測」）。英日は別々の時間割。
- 公開日（本人了承 11/10）：**11/28（土）09:00**。投稿の予約は11/27中。11/28にQOの予約がないことはリポジトリの記録で確認した（Studioの画面では未確認。投稿の前に照合する）。

## 注意して扱う点

- **アメリカの象徴をからかわない。** 「間違いだらけの絵」という語り方をしない。ずれは「絵が描かれた時代と場所」から説明し、画家の選択として扱う。
- **「その旗は無かった」と言わない。** 言えるのは「国旗として採用されたのは渡河の約半年後」。グランド・ユニオン旗だったとも、旗が1本もなかったとも言わない（照合5）。
- **星の数と並びを、絵から数えたように言わない。** 旗は折れ重なっていて、13の星もすべての縞も画像から数えられない（照合4）。
- **「長く暗い夜」を手紙の言葉として言わない。** 手紙の言葉は「非常に厳しい夜」「雪と雹の激しい嵐」で、嵐は行軍に係る（照合3）。「みぞれ」と訳さない。
- **手紙は「ワシントンが書いた」でよいが、「自筆」とは言わない。** 送った原本の筆跡は副官ティルマン（照合3）。
- **1848年の動機は出典の主語を付ける。** 「マウントバーノンの解説では」と明示する。「Some historians」で済ませない（照合8）。画家の書簡で確かめたわけではない。
- **ホイットリッジの回想は「Metの論文が引用する回想」として扱う。** 自伝の刊本を直接読んだとは言わない（照合9）。顔のモデルと、体・ポーズのモデルを区別する。
- **最初の版が「焼けた」と言わない。** 火事で傷み、修復され、後にブレーメンで空襲により失われた（照合10）。
- **戦いの日は12月26日。** 12月25日と書いた解説（Metの販売用ページ）は採らない（照合11）。
- 来場者数（5万人超）・売値（1万ドル）は後世の館の解説の数字なので、台本には入れない。
- 「ワシントンは立っていられなかった」、旗を持つ人物（モンロー）、舟の種類（ダーラム・ボート）、ライン川がモデル、は扱わない（照合12。いずれも言い切れない）。
- 戦闘（トレントンの戦い）の死傷は語らない。トレントンは目的地として一言だけ。
- 実在人物の顔：絵の中のワシントンは絵の一部として扱ってよい。ロイツェの写真（V09）を使う場合は、顔の大写しにしない。

## 台本（英語・メイン）v02

章は6つ。P02のあとにオープニング（4秒）を入れる。P03以降、画面の下に年代の帯を出す。

### C01 A Famous Crossing

**P01** This is one of the best-known images of American history: Washington Crossing the Delaware. On a winter river, among floating ice, George Washington stands in a small boat and looks ahead. Behind him, a soldier raises the Stars and Stripes. But this painting was not made in 1776. It was made about seventy-five years later, in Germany. And on the night of the crossing, that flag had not yet been adopted as the nation's flag.

**P02** In this episode, we follow the image through time: from a winter night on the river, to a painter's studio in Düsseldorf, to the city where the painting became famous.

（ここでオープニング）

### C02 1776: A Night on the River

**P03** On the evening of December 25th, 1776, Washington's army began to cross the Delaware River, from Pennsylvania into New Jersey, on its way to Trenton. Two days later, Washington described the crossing in a letter to John Hancock, the president of Congress.

**P04** The plan was to start as soon as it grew dark. But ice formed in the river that night, and slowed the boats so much that it was three o'clock before all the artillery was across, and nearly four before the troops began to march. He called it a very severe night, and wrote that they marched through a violent storm of snow and hail.

**P05** In the painting, a morning light is spreading across the sky, and a last star still shines above the boat. Studies of the painting connect this light with the coming dawn. The crossing that went on through the night is gathered here into a single view.

### C03 1777: A New Flag

**P06** The flag in the painting has red and white stripes, and white stars on a blue field. This is the Stars and Stripes. On June 14th, 1777, about six months after the crossing, the Continental Congress resolved that the flag of the United States would have thirteen stripes and thirteen stars. The resolution did not say how the stars should be arranged. Which flag was carried that night, if any, is not known.

### C04 1849: A Studio in Düsseldorf

**P07** The painter, Emanuel Leutze, was born in Germany in 1816. As a child, he moved with his family to the United States. In 1841, he went back to Germany to study painting, in Düsseldorf, a city known for its painters of history.

**P08** He began the first version of this picture there in 1849, soon after revolutions swept across Europe in 1848. Mount Vernon, Washington's home and now a museum, explains that Leutze supported those revolutions, and hoped his painting would inspire new struggles for liberty and democracy.

**P09** Americans in the city posed for the figures. One of them, the painter Worthington Whittredge, recalled that he posed for the man steering the boat, and again for Washington himself. For Washington's head, Leutze is said to have looked to a sculpture by Houdon.

**P10** In November 1850, a fire in the studio damaged the first version. The next year, Leutze began a second one. The first was repaired, went to the city of Bremen, and was lost in an air raid in 1942.

### C05 1851: New York

**P11** In 1851, the second version was shown in New York, and crowds came to see it. Two years later, an engraving after the painting was published, carrying the image far beyond the exhibition room.

**P12** In 1897, it was given to the Metropolitan Museum of Art, where it hangs today. It is more than six meters wide.

### C06 Then and Now

**P13** So, did Washington really cross the Delaware like this? The painting was made about seventy-five years after the night it shows, in another country. Its painter put the light of morning in the sky, and the later flag of a nation in a soldier's hands. It is not a record of that night. It is a picture of that night, made for the painter's own time. And today, it is the picture that many of us remember.

**P14** Every story has an origin. Sometimes, the image we remember was painted long after the moment itself.

**P15** This video is based on historical texts and public museum collections. The narration uses synthetic speech. Sources and terms of use are listed in the description. If you enjoyed this story, please like the video and subscribe for more quiet origins. Thank you for watching.

## 台本（日本語）v02

**P01** これは、アメリカの歴史で最もよく知られた絵の一つ、「デラウェア川を渡るワシントン」です。冬の川、流れる氷のあいだで、ジョージ・ワシントンが小舟に立ち、前を見つめています。その後ろでは、兵士が星条旗を掲げています。けれど、この絵が描かれたのは1776年ではありません。およそ75年後、ドイツで描かれました。そして渡河の夜、あの旗はまだ、国の旗として定められていませんでした。

**P02** 今回は、この絵の歩みをたどります。冬の夜の川から、デュッセルドルフの画家のアトリエ、そしてこの絵が有名になった街まで、時代の順に見ていきます。

**P03** 1776年12月25日の夕方、ワシントンの軍は、ペンシルベニアからニュージャージーへ、デラウェア川を渡り始めました。向かう先はトレントンです。2日後、ワシントンは大陸会議の議長ジョン・ハンコックへの手紙で、この渡河について書いています。

**P04** 暗くなりしだい渡り始める計画でした。けれどその夜、川には氷ができ、舟の進みをひどく遅らせました。砲兵をすべて渡し終えたのは3時、兵が行軍を始めたのは4時近くでした。ワシントンはそれを「非常に厳しい夜」と呼び、行軍は雪と雹の激しい嵐の中だったと書いています。

**P05** 絵の中では、空に朝の光が広がり、舟の上には最後の星がまだ輝いています。この絵の研究は、この光を夜明けと結びつけています。夜通し続いた渡河が、ここでは一つの場面にまとめられているのです。

**P06** 絵の旗には、赤と白の縞と、青地に白い星があります。星条旗です。1777年6月14日、渡河のおよそ半年後に、大陸会議は、合衆国の旗を13本の縞と13の星とすることを決めました。決議は、星の並べ方を定めていません。あの夜にどの旗が掲げられたのか、そもそも旗があったのかは、分かっていません。

**P07** 画家のエマヌエル・ロイツェは、1816年にドイツで生まれました。子どものころ家族とともにアメリカへ渡り、1841年、絵を学ぶためにドイツへ戻ります。学んだのは、歴史画の画家が集まる街、デュッセルドルフでした。

**P08** 彼がこの街で最初の絵を描き始めたのは1849年。1848年にヨーロッパの各地で革命が起きた、すぐ後のことです。ワシントンの旧邸で、いまは博物館のマウントバーノンは、ロイツェがその革命を支持し、この絵が自由と民主主義への新たな闘いを励ますことを望んでいた、と説明しています。

**P09** 人物のモデルを務めたのは、この街にいたアメリカ人たちでした。その一人、画家のワージントン・ホイットリッジは、舟の舵を取る人と、そしてワシントンその人のモデルをしたと振り返っています。ワシントンの頭部は、ウードンの彫刻を参考にしたとされます。

**P10** 1850年11月、アトリエの火事で、最初の絵が傷みました。翌年、ロイツェは2枚目を描き始めます。最初の絵は修復され、ブレーメンの街へ渡りましたが、1942年の空襲で失われました。

**P11** 1851年、2枚目の絵はニューヨークで展示され、多くの人が見に訪れました。2年後にはこの絵をもとにした版画が出版され、その姿は展示室をはるかに越えて広まっていきました。

**P12** 1897年、絵はメトロポリタン美術館に寄贈され、今もそこに掛けられています。幅は6メートルを超えます。

**P13** では、ワシントンは本当にこうしてデラウェア川を渡ったのでしょうか。この絵は、描かれた夜からおよそ75年後に、別の国で描かれました。画家は空に朝の光を入れ、後の時代の国の旗を、兵士の手に持たせました。あの夜の記録ではありません。画家が自分の時代に向けて描いた、あの夜の姿です。そして今、多くの人が思い浮かべるのは、その姿なのです。

**P14** すべての物語には、始まりがあります。ときに、私たちが覚えている姿は、その出来事よりずっと後に描かれたものなのです。

**P15** この動画は、歴史資料と、美術館の公開コレクションにもとづいています。ナレーションには合成音声を使っています。出典と利用条件は説明欄に記載しています。楽しんでいただけたら、高評価とチャンネル登録で、これからも静かな起源の物語をお楽しみください。ご視聴ありがとうございました。

## 画像の大きさの扱い（照合で分かった制約）

- 全図の最大は `DP-14511-001.jpg`（4,000×2,335px）。4K（3,840×2,160）の横幅にほぼ等倍で収まるが、**全図からの切り出しで寄ると原寸を超える。** 全図はゆっくりした寄り・引き（1.05倍まで）だけにする。
- 寄りの画面は **Met公式の細部写真** から作る。縦長の3点（`DP245004` 空と左の舟／`DP245005` ワシントンと旗／`DP245006` 舵を取る人）は長辺3,847pxなので、**縦のまま画面の中に置く**（高さ2,160pxへ縮小。背景は暗い無地）。横長の `DP258218`（4,000×3,000）は画面いっぱいに使える。
- 細部写真どうしで同じ部分が重なるので、夜警と同じく **全ショットの切り出し範囲を記録し、重なりを数値で確かめる。**
- 額や展示室が写った写真（`DP249079`・`DP258191`・`DP258219`・`DP258220`）と白黒写真は使わない。

## 画面の案（素材は[素材候補](pnt02_素材候補_20261110.md)から）

| 区間 | 画面 | 確認点 |
|---|---|---|
| P01 | **全体（1回目）** `DP-14511-001`。ゆっくり寄る（1.05倍まで） | 全体が1回目 |
| P02 | 年の並べ直し（夜警・第12話と同じ D_timeline_intro）：1776 → 1777 → 1849 → 1851 | 細部をほかの区間と重ねない |
| P03 | **文字カード**：手紙の見出し `Head Quarters Newtown 27th Decemr 1776` と宛先 | 地図（V08）は権利文言が未確認なので使わない |
| P04 | **文字カード**：氷と時刻の一文、天気の一文（原文＋英日訳） | 出典「Founders Online の翻刻」。原稿画像は使わない |
| P05 | 細部：空と星 `DP245004`（縦置き） | 左の漕ぎ手も写るので、P09と同じ部分を使わない |
| P06 | 細部：旗とワシントン `DP245005`（縦置き） → **文字カード**：決議の原文＋英日訳 | 決議はNARAの再掲に従う。別の再掲と継ぎ合わせない |
| P07 | **文字カード**：1816 Schwäbisch Gmünd → 1825 → 1841 Düsseldorf | ロイツェの写真（V09）は原寸未取得。取れれば候補 |
| P08 | 1848年の版画「Des Deutschen Vaterland」（V10、SMB、PDM 1.0） | 顔の大写しにしない。画家の動機の証拠としては見せない（時代の資料） |
| P09 | 細部：舵を取る人 `DP258218`（横、画面いっぱい） → **文字カード**：回想の一文（Met 1968年論文の引用として） | 自伝の頁画像は使わない |
| P10 | **文字カード**：1850 → 1863 Bremen → 1942 | 最初の版の写真は権利明記がないので使わない。Metの白黒写真で代用しない |
| P11 | 1853年の版画（V05、LoC）。**取れなければ** 細部 `DP245006`（縦置き） | V05は原寸の取得が403で未了 |
| P12 | 細部：右側の人物群（`DP245006` または `DP258218` の未使用部分） | 原寸を超えない |
| P13 | **全体（2回目）**。ゆっくり引く | 全体はここまで |
| P14〜P15 | 共通のエンドカード（10秒） | |

札は既存の形（`MUSEUM OBJECT｜博物館資料`、`DETAIL｜部分`、`DOCUMENT｜文書` など）。

**★画面の素材が夜警より少ない。** 絵の外の画像はV10の1点（V05・V09は取得待ち）で、文字カードが5区間になる。静止画中心の弱点（中盤の離脱）が出やすいので、公開後に夜警と比べる数字の一つにする。

**サムネの案：**
- A（推奨）：ワシントンと旗の細部（`DP245005`）を大きく、見出し **NOT IN 1776?**、年 **1851**。夜警の **NOT AT NIGHT? / 1642** と同じ形
- B：全体図と **1776 → 1851** の年

## 出典（照合後。詳しくは[原典照合](research/pnt02_原典訳文_20261110.md)の出典索引）

| ID | 出典 | 台本 | 台本での扱い |
|---|---|---|---|
| S01・S02 | Met 97.34 作品記録・公式API・画像利用方針 | P01・P12 | 1851年、378.5×647.7cm、Gift of John Stewart Kennedy, 1897。画像CC0 |
| S03 | Founders Online：Washington to Hancock, 27 Dec. 1776 | P03・P04 | 計画（暗くなりしだい）、3時・4時近く、very severe Night、Storm of Snow and Hail |
| S05 | NARA：1777年6月14日の決議の再掲 | P06 | 13本の縞・13の星。並べ方の指定なし |
| S06 | Washington Crossing Historic Park：Myths and Legends | P06 | 当夜の旗は不明（if any were flown at all） |
| S08 | Mount Vernon：Crossing the Delaware in Art | P08 | 1848年の革命の支持と、自由と民主主義への闘いを励ます意図（館の解説として） |
| S09・S10 | 米国務省・スミソニアン米国美術館の経歴 | P07・P08 | 1816年生まれ、1825年渡米、1841年ドイツへ、1849年着手 |
| S11 | Howat 1968, Met Bulletin 26(7) | P05・P09・P10・P11 | 朝の光、ホイットリッジの回想の引用、火事、1851年の展示 |
| S12 | Met Bulletin 2011（修復） | P05・P10 | 金星と夜明け、1850年11月の火事、1851年1月に2枚目着手 |
| S17 | LoC：Girardet の版画（1853、Goupil） | P11 | 1853年に版画。最初の複製とは言わない |
| S22 | SMB：Des Deutschen Vaterland（1848） | P08 | 時代の資料 |

## v01からの主な変更（照合による）

- P01：「that flag had not yet been adopted」→「…adopted as the nation's flag」。国旗として未採用、までに限る。
- P03：「12月25日の夜」→「夕方に渡り始めた」（手紙の The Evening of the 25th）。
- P04：手紙の計画（暗くなりしだい）を加え、天気を手紙の言葉（very severe Night／雪と雹の嵐、嵐は行軍に係る）に直した。
- P05：「ワシントン自身の言葉では長く暗い夜」を削除（手紙にない）。朝の光と最後の星、「研究は夜明けと結びつける」に変えた。
- P06：「円く並んだ13の星」を削除（決議に指定がなく、絵からも数えられない）。「そもそも旗があったのか」を史跡の解説に合わせた。
- P07：年（1816・1841）を加えた。
- P08：「1850年ごろ」→「最初の版を1849年に描き始めた」。「Some historians」→「マウントバーノンの解説では」。
- P09：「自伝で書いた」→「振り返っている」（Metの論文が引用する回想）。ウードンの彫刻を加え、顔とポーズのモデルを区別した。
- P10：火事の年月（1850年11月）、2枚目の着手（翌年）、空襲の年（1942）を加えた。「美術館（Kunsthalle）」→「ブレーメンの街」（館名の発音が未確認のため）。
- P11：「本や家庭へ」を削除（具体例が未確認）。「2年後に版画」（1853）に限った。
- P13：「後の世代があの夜をどう覚えておきたかったか」→「画家が自分の時代に向けて描いたあの夜の姿で、今多くの人が思い浮かべるのはその姿」（照合の指摘：後の世代の総意とするのは広すぎる）。
- 章C04の年を1850→1849に。

## v02の本人確認（3点・2026-11-10 了承済み）

**2026-11-10 本人了承「推奨どおりで進める」：3点とも下の推奨どおり。** 3のV05・V09は、本人のChromeで所蔵館のページを開いたところ、LoC・NPGともボット確認（Cloudflareのチェック）で止まった（11/10）。本人がチェックを通せば取得できる。取れるまではP11を文字カードで作る（制作依頼）。

1. **台本v02でよいか**（とくにP13の結び：「あの夜の記録ではなく、画家が自分の時代に向けて描いた姿。今多くの人が思い浮かべるのはその姿」）。**推奨：このまま。**
2. **画像の大きさの扱い**：全図は4,000pxが最大で、夜警のように全図から自由に寄れない。寄りはMet公式の細部写真を縦のまま画面に置く形にする。**推奨：この形で。** 条件4は「一部だけ満たす」と記録し、絵画03（北斎）は細部を自由に寄れる画像があるかを先に確かめる。
3. **取得待ちの素材**（V05 1853年の版画・V09 ロイツェを含む1864年の写真）：Codexの環境では403だった。**推奨：取得だけ本人のMacのブラウザで行う**（夜警と同じ相談）。取れなければP11は細部写真で代える。

## ショート案（本編合格後に別依頼）

| | 見出し（仮） | 使う細部 | 内容 |
|---|---|---|---|
| V1 | **THIS FLAG WASN'T OFFICIAL YET?** | 旗 `DP245005` | 1777年の決議。問いの形で。「存在しなかった」と言わない |
| V2 | **PAINTED IN GERMANY?** | 全体 → 1848年の版画 | デュッセルドルフと1848年 |
| V3 | **WHO POSED AS WASHINGTON?** | 舵を取る人 `DP258218` | ホイットリッジの回想（Metの論文の引用として） |

## v02の実測

実測（2026-11-10、台本の本文だけを数えた）：英語696語・日本語1,679字（全15区間）。夜警の確認版v01（台本687語・英語301.200秒）と同じ話速なら英語の語りは約305秒（推定。音声はまだ作っていない）。オープニング4秒・エンドカード10秒・区間の間を足して約5分半の見込み。
