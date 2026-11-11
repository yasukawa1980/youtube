// 給水装置工事データ（試作版）
// v が null の項目は「未確認」。必ず src（公式資料）で原文を確認すること。
// floors：かんたん判定に使う階数の目安
//   sure       … 特別な条件なしで直結直圧（ポンプなし）の対象になる階数の上限
//   cond       … 水圧の条件や事前協議などを満たせば直結直圧にできる階数の上限
//   boosterMax … 直結増圧（ポンプあり）の階数の上限。基準に上限の数字がないときは null
window.JOREI_DATA = window.JOREI_DATA || {};
window.JOREI_DATA.water = {
  title: "給水装置工事",
  checkedOn: "2026-11-11（公式資料の原文と照合）",
  entries: [
    {
      id: "tokyo", name: "東京都水道局", pref: "東京都", region: "関東",
      law: "東京都給水条例・給水装置設計・施工基準（給水装置編）",
      scope: "東京都水道局の給水区域。",
      floors: { sure: 3, cond: null, boosterMax: null, note: "直圧は原則3階まで。4階以上は増圧か貯水槽。水圧の高い地域では、増圧ポンプの設置を留保して直圧で給水する「特例直圧給水」があり、階数は水理計算で決まります（決まった上限の数字はありません）。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "原則として最大3階まで。3階建ての屋上に散水用などの単独水栓を付ける場合は、水理計算で支障がなければ可。", src: "https://www.waterworks.metro.tokyo.lg.jp/documents/d/waterworks/106023027007-07_r0804" },
        { k: "4階以上", v: "受水タンクか増圧給水設備が必要。ただし一定の条件に合えば「特例直圧給水」で4階以上へ直圧給水できる（増圧ポンプの設置スペースの確保が条件、メータ口径20〜75ミリ）。", src: "https://www.waterworks.metro.tokyo.lg.jp/kurashi/chokketsu/houshiki" },
        { k: "直結増圧の階数上限", v: "階高の制限なし（水理計算上可能な範囲）。", src: "https://www.waterworks.metro.tokyo.lg.jp/kurashi/chokketsu/houshiki" }
      ],
      links: [
        { t: "東京都水道局 給水装置設計・施工基準（給水装置編）令和8年4月版", u: "https://www.waterworks.metro.tokyo.lg.jp/documents/d/waterworks/106023027007-07_r0804" },
        { t: "東京都水道局 給水方式について", u: "https://www.waterworks.metro.tokyo.lg.jp/kurashi/chokketsu/houshiki" }
      ]
    },
    {
      id: "yokohama", name: "横浜市水道局", pref: "神奈川県", region: "関東",
      law: "給水装置工事設計・施工指針（令和8年4月1日適用）",
      scope: "横浜市水道局の給水区域。",
      floors: { sure: 2, cond: 6, boosterMax: null, note: "3階建て以上で直結直圧にするには、事前の給水水圧調査と水理計算が必要です。決まった階数ではなく、回答された水圧で給水できる階まで。増圧ポンプの設置を猶予する制度は6階建てまでです。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "3階建て以上を直結直圧にする場合は、事前に給水水圧調査を依頼する。給水水圧0.25MPa（または回答された水圧）で給水できる階層・規模まで。", src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/suido/kyuusui-souchi/202504kyusui-shishin.files/0178_20260401.pdf" },
        { k: "増圧給水設備設置の猶予", v: "6階建て以下で、回答された水圧が0.25MPaを超える場合、増圧ポンプを置かずに直結直圧にできる。口径50ミリの引込管で給水できる規模まで。", src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/suido/kyuusui-souchi/202504kyusui-shishin.files/0178_20260401.pdf" },
        { k: "直結増圧の上限", v: "階数ではなく水量で制限。計画同時使用水量は1時間あたり40㎥（毎分666L）まで、引込管口径75ミリ以下。", src: "https://www.city.yokohama.lg.jp/kurashi/sumai-kurashi/suido-gesui/suido/suishitsu/dekirumade/kyusui.html" }
      ],
      links: [
        { t: "横浜市 給水方式の説明", u: "https://www.city.yokohama.lg.jp/kurashi/sumai-kurashi/suido-gesui/suido/suishitsu/dekirumade/kyusui.html" },
        { t: "横浜市 設計・施工指針 第3章 給水装置の基本計画", u: "https://www.city.yokohama.lg.jp/business/bunyabetsu/suido/kyuusui-souchi/202504kyusui-shishin.files/0178_20260401.pdf" }
      ]
    },
    {
      id: "kawasaki", name: "川崎市上下水道局", pref: "神奈川県", region: "関東",
      law: "給水装置工事施行基準（令和8年版）",
      scope: "川崎市上下水道局の給水区域。",
      floors: { sure: 2, cond: 6, boosterMax: null, note: "直結直圧は地上2階までが原則。配水管の水圧が足りる地域では3階直結直圧、さらに水圧の高い地域では「特例直結直圧」で4〜6階程度まで。直結増圧の階数の上限は、施行基準の該当の節に書かれていません。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "地上2階までが原則。3階直結直圧は、配水管の最小動水圧0.20MPa以上（専用住宅は0.15MPa以上）の地域。", src: "https://www.city.kawasaki.jp/800/cmsfiles/contents/0000083/83335/3_R8_sekoukijyun.pdf" },
        { k: "特例直結直圧", v: "直結増圧の対象でも増圧ポンプの設置を猶予する方式。最小動水圧0.30MPa以上で4階程度、0.35MPa以上で5階程度、0.40MPa以上で6階程度まで（目安）。", src: "https://www.city.kawasaki.jp/800/cmsfiles/contents/0000083/83335/3_R8_sekoukijyun.pdf" },
        { k: "直結増圧", v: "最小動水圧0.20MPa以上の地域。階数の上限は施行基準の該当の節に記載なし（未確認）。", src: "https://www.city.kawasaki.jp/800/cmsfiles/contents/0000083/83335/3_R8_sekoukijyun.pdf" }
      ],
      links: [
        { t: "川崎市 給水装置工事施行基準", u: "https://www.city.kawasaki.jp/800/cmsfiles/contents/0000083/83335/3_R8_sekoukijyun.pdf" },
        { t: "川崎市 特別な直結給水方式の要領", u: "https://www.city.kawasaki.jp/templates/outline/cmsfiles/contents/0000003/3894/tyokketu.pdf" }
      ]
    },
    {
      id: "saitama", name: "さいたま市水道局", pref: "埼玉県", region: "関東",
      law: "直結給水システム設計施工基準（令和3年4月1日施行）",
      scope: "さいたま市水道局の給水区域。",
      floors: { sure: 3, cond: null, boosterMax: 15, note: "直圧式は3階まで（水栓の最高位は配水管から10m以下、最小動水圧0.196MPa以上の地域）。増圧式はおおむね15階以下の建物です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "住宅・共同住宅・事務所ビル等の3階まで（水理計算上可能な範囲）。水栓の最高位は配水管の管芯から10m以下。", src: "https://www.city.saitama.lg.jp/001/006/002/050/005/p012533_d/fil/sekkeisekoukijunn.pdf" },
        { k: "直結増圧の階数上限", v: "おおむね15階以下。共同住宅はファミリー149世帯・ワンルーム283世帯以下、事務所ビル等は1日最大使用水量おおむね149㎥以下。", src: "https://www.city.saitama.lg.jp/001/006/002/050/005/p012533_d/fil/sekkeisekoukijunn.pdf" },
        { k: "併用", v: "直圧式と増圧式は併用できない（2階までの直結直圧は併用可）。", src: "https://www.city.saitama.lg.jp/001/006/002/050/005/p012533_d/fil/sekkeisekoukijunn.pdf" }
      ],
      links: [
        { t: "さいたま市 直結給水の案内", u: "https://www.city.saitama.lg.jp/001/006/002/046/003/p009173.html" },
        { t: "さいたま市 直結給水システム設計施工基準", u: "https://www.city.saitama.lg.jp/001/006/002/050/005/p012533_d/fil/sekkeisekoukijunn.pdf" }
      ]
    },
    {
      id: "kyoto", name: "京都市上下水道局", pref: "京都府", region: "近畿",
      law: "給水装置工事基準（上水道編）令和7年版",
      scope: "京都市上下水道局の給水区域。",
      floors: { sure: 2, cond: 5, boosterMax: null, note: "3階以上に給水する建物は受水槽式が原則ですが、条件を満たせば直結にできます。直結直圧は配水管の年間最小動水圧が3階0.245MPa・4階0.294MPa・5階0.343MPa以上で5階まで（3階建ての個人住宅は0.196MPa以上）。直結増圧は3階以上が対象で、上限の階数は未確認です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "2階以下が基本。3階建ての個人住宅は最小動水圧0.196MPa以上、それ以外は3階0.245MPa・4階0.294MPa・5階0.343MPa以上で5階まで。", src: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000258/258521/koujikijyun-R7.pdf" },
        { k: "受水槽式が原則になる場合", v: "地上3階建て以上で3階以上に給水設備があるとき（局が認める建物は直結可）、断減水時も給水が必要なとき、一時に多量の水を使うときなど。", src: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000258/258521/koujikijyun-R7.pdf" },
        { k: "直結増圧", v: "3階以上の建物で最小動水圧0.196MPa以上。階数の上限は「直結式給水施行要領」によるとされ、未確認。", src: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000258/258521/koujikijyun-R7.pdf" }
      ],
      links: [
        { t: "京都市 給水装置工事基準（上水道編）", u: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000258/258521/koujikijyun-R7.pdf" },
        { t: "京都市 給水補助加圧装置設置基準", u: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000258/258521/kaatu-R7.pdf" }
      ]
    },
    {
      id: "osaka", name: "大阪市水道局", pref: "大阪府", region: "近畿",
      law: "大阪市水道事業給水条例・同施行規程",
      scope: "大阪市水道局の給水区域。",
      floors: { sure: 3, cond: 5, boosterMax: null, note: "直結直圧は3階建てまで。配水管の水圧が高い地域では、条件付きの特例で4・5階建てまで。直結増圧は階数の制限なし・200戸程度までで、水理計算での確認が必要です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "3階建てまでの建物が対象。配水管水圧の高い地域では、特例として一定の条件で4・5階建てまで（条件の細目は未確認）。", src: "https://www.city.osaka.lg.jp/suido/page/0000161205.html" },
        { k: "直結増圧の階数上限", v: "階数の制限なし、200戸までの建物が対象。", src: "https://www.city.osaka.lg.jp/suido/page/0000391113.html" },
        { k: "専用給水装置の数", v: "1戸・1事業につき1つが原則。直結増圧の1装置では水量の上限を超える大規模共同住宅などは、誤接合のおそれがない配管なら複数可。", src: "https://www.city.osaka.lg.jp/suido/cmsfiles/contents/0000670/670760/88sonota.pdf" }
      ],
      links: [
        { t: "大阪市 本市における給水方式について", u: "https://www.city.osaka.lg.jp/suido/page/0000391113.html" },
        { t: "大阪市 よくある質問と回答【給水方式】", u: "https://www.city.osaka.lg.jp/suido/page/0000161205.html" }
      ]
    },
    {
      id: "hiroshima", name: "広島市水道局", pref: "広島県", region: "中国・四国",
      law: "給水装置等の設計施工事務取扱要綱 第2編 中高層建物直結給水施行基準",
      scope: "広島市水道局の給水区域。",
      floors: { sure: null, cond: 5, boosterMax: null, note: "4階以上へ直結直圧で給水できるのは、配水管の最小動水圧が0.30MPa以上の区域（案内資料の図では5階程度まで）。3階までの扱いは原文で未確認です。直結増圧は案内資料の図で10階程度、基準に上限の数字はありません。" },
      items: [
        { k: "直結直圧（4階以上）", v: "配水管の最小動水圧0.30MPa以上の区域。満たさない場合も、水理計算で残存水圧を確保できれば可。", src: "https://www.water.city.hiroshima.lg.jp/uploaded/attachment/7796.pdf" },
        { k: "直結増圧", v: "配水管の最小動水圧0.20MPa以上の区域。案内資料では「10階程度の建物なら」。", src: "https://www.water.city.hiroshima.lg.jp/uploaded/attachment/7201.pdf" },
        { k: "受水槽式になる建物", v: "入院・手術設備のある病院、ホテル・旅館、大規模レストラン、公衆浴場、有毒薬品を扱う工場など。", src: "https://www.water.city.hiroshima.lg.jp/uploaded/attachment/7796.pdf" },
        { k: "3階までの直結直圧", v: null, src: "https://www.water.city.hiroshima.lg.jp/soshiki/12/60.html" }
      ],
      links: [
        { t: "広島市 中高層建物直結給水施行基準", u: "https://www.water.city.hiroshima.lg.jp/uploaded/attachment/7796.pdf" },
        { t: "広島市 直結給水への切替工事（案内）", u: "https://www.water.city.hiroshima.lg.jp/uploaded/attachment/7201.pdf" }
      ]
    },
    {
      id: "sapporo", name: "札幌市水道局", pref: "北海道", region: "北海道・東北",
      law: "給水装置工事設計施工指針（令和8年4月改訂版）",
      scope: "札幌市水道局の給水区域。",
      floors: { sure: null, cond: 5, boosterMax: null, note: "直結直圧は5階程度、直結加圧（増圧）は10階程度が標準です。4階以上の直結は中高層建物直結給水技術基準により、事前協議が必要（必要な配水管水圧は4階0.25MPa、5階0.30MPa）。3階までの扱いは原文で未確認です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "5階程度が標準。4階は配水管水圧0.25MPa、5階は0.30MPaが標準。", src: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/6-r8.pdf" },
        { k: "直結加圧（増圧）", v: "10階程度が標準。直列多段加圧方式ではさらに高層も可。", src: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/6-r8.pdf" },
        { k: "直結給水の対象外", v: "病院、ホテル、飲食店中心の雑居ビル、理美容院など。", src: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/6-r8.pdf" },
        { k: "3階までの直結直圧", v: null, src: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/4-r8.pdf" }
      ],
      links: [
        { t: "札幌市 直結給水方式", u: "https://www.city.sapporo.jp/suido/overview/apartment/chokketsu.html" },
        { t: "札幌市 中高層建物直結給水技術基準", u: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/6-r8.pdf" }
      ]
    },
    {
      id: "fukuoka", name: "福岡市水道局", pref: "福岡県", region: "九州・沖縄",
      law: "福岡市水道給水条例・給水装置工事施行基準",
      scope: "福岡市水道局の給水区域。",
      floors: { sure: 2, cond: 3, boosterMax: null, note: "3階以上に給水栓がある建物は、増圧装置か貯水槽が必要（条例第28条）。3階直結直圧は配水管の最小動水圧0.196MPa以上の地域で、事前協議が必要です。直結増圧はおおむね10階程度までの建物を勧めていますが、基準に階数の上限はありません。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "2階までは最小動水圧0.147MPa以上の地域。3階は0.196MPa以上の地域で、3階建てまでの建物（屋上の太陽熱温水器なども条件付きで可）。", src: "https://www.city.fukuoka.lg.jp/mizu/sessui/machi/documents/05_kyuusuisoutinokeikaku.pdf" },
        { k: "直結増圧", v: "最小動水圧0.147MPa以上の地域で、使用圧力0.75MPa以下の増圧装置で給水できる建物。案内ではおおむね10階程度までの共同住宅・事務所など。", src: "https://www.city.fukuoka.lg.jp/mizu/sessui/0026.html" },
        { k: "貯水槽が必要な場合", v: "一時に多量の水を使用する箇所など（条例第28条第2項）。", src: "https://www.city.fukuoka.lg.jp/d1w_reiki/reiki_honbun/q003RG00000874.html" }
      ],
      links: [
        { t: "福岡市 直結増圧式給水", u: "https://www.city.fukuoka.lg.jp/mizu/sessui/0026.html" },
        { t: "福岡市 給水装置工事施行基準 第5章 給水装置の計画", u: "https://www.city.fukuoka.lg.jp/mizu/sessui/machi/documents/05_kyuusuisoutinokeikaku.pdf" }
      ]
    }
  ]
};
