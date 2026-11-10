// 給水装置工事データ（試作版）
// v が null の項目は「未確認」。必ず src（公式資料）で原文を確認すること。
window.JOREI_DATA = window.JOREI_DATA || {};
window.JOREI_DATA.water = {
  title: "給水装置工事",
  checkedOn: "2026-11-10",
  entries: [
    {
      id: "tokyo", name: "東京都水道局", pref: "東京都", region: "関東",
      law: "東京都給水条例",
      scope: "東京都水道局の給水区域。",
      floors: { directMax: null, boosterMin: null, boosterMax: null, note: "階数の基準は未確認です。増圧ポンプの設置を留保する「特例直圧直結給水」の制度があります。" },
      items: [
        { k: "直結直圧で給水できる階数", v: null, src: "https://www.waterworks.metro.tokyo.lg.jp/documents/d/waterworks/3_197" },
        { k: "特例の制度", v: "配水管の水圧で最上階まで給水できる場合、増圧ポンプの設置を留保する「特例直圧直結給水」あり。管理責任は所有者・使用者（条例第18条）。", src: "https://www.waterworks.metro.tokyo.lg.jp/documents/d/waterworks/3_197" }
      ],
      links: [
        { t: "東京都水道局 特例直圧直結給水の説明資料", u: "https://www.waterworks.metro.tokyo.lg.jp/documents/d/waterworks/3_197" }
      ]
    },
    {
      id: "yokohama", name: "横浜市水道局", pref: "神奈川県", region: "関東",
      law: "給水装置工事設計・施工指針",
      scope: "横浜市水道局の給水区域。",
      floors: { directMax: null, boosterMin: null, boosterMax: null, note: "3階建て以上で直結直圧を希望する場合は、事前の水圧調査が必要です。階数の上限は未確認です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "3階建て以上で直結直圧式を希望する場合は、事前に水圧調査が必要。", src: "https://www.city.yokohama.lg.jp/kurashi/sumai-kurashi/suido-gesui/suido/suishitsu/dekirumade/kyusui.html" },
        { k: "指針の関連項目", v: "「3階建以上への直結直圧式給水」「直結増圧式給水」「増圧給水設備設置の猶予」の項目あり。", src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/suido/kyuusui-souchi/202504kyusui-shishin.files/0175_20260401.pdf" },
        { k: "直結増圧の階数上限", v: null, src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/suido/kyuusui-souchi/202504kyusui-shishin.files/0175_20260401.pdf" }
      ],
      links: [
        { t: "横浜市 給水方式の説明", u: "https://www.city.yokohama.lg.jp/kurashi/sumai-kurashi/suido-gesui/suido/suishitsu/dekirumade/kyusui.html" },
        { t: "横浜市 設計・施工指針（2026年4月付）", u: "https://www.city.yokohama.lg.jp/business/bunyabetsu/suido/kyuusui-souchi/202504kyusui-shishin.files/0175_20260401.pdf" }
      ]
    },
    {
      id: "kawasaki", name: "川崎市上下水道局", pref: "神奈川県", region: "関東",
      law: "給水装置工事施行基準",
      scope: "川崎市上下水道局の給水区域。",
      floors: { directMax: 3, boosterMin: null, boosterMax: null, note: "直結直圧は2階まで／3階までの区分があります。3階直結直圧・直結増圧・特例直結直圧は「特別な直結給水方式」として設計審査の対象です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "2階直結直圧式と3階直結直圧式の区分あり。3階直結直圧の設計水圧は配水管の最小動水圧に応じて150〜250kPa。", src: "https://www.city.kawasaki.jp/800/cmsfiles/contents/0000083/83335/3_R8_sekoukijyun.pdf" },
        { k: "特別な直結給水方式", v: "3階直結直圧式・直結増圧式・特例直結直圧式は設計審査の要領が定められている。", src: "https://www.city.kawasaki.jp/templates/outline/cmsfiles/contents/0000003/3894/tyokketu.pdf" },
        { k: "直結増圧の階数上限", v: null, src: "https://www.city.kawasaki.jp/800/cmsfiles/contents/0000083/83335/3_R8_sekoukijyun.pdf" }
      ],
      links: [
        { t: "川崎市 給水装置工事施行基準", u: "https://www.city.kawasaki.jp/800/cmsfiles/contents/0000083/83335/3_R8_sekoukijyun.pdf" },
        { t: "川崎市 特別な直結給水方式の要領", u: "https://www.city.kawasaki.jp/templates/outline/cmsfiles/contents/0000003/3894/tyokketu.pdf" }
      ]
    },
    {
      id: "saitama", name: "さいたま市水道局", pref: "埼玉県", region: "関東",
      law: "給水装置工事設計施工基準",
      scope: "さいたま市水道局の給水区域。",
      floors: { directMax: 3, boosterMin: null, boosterMax: 15, note: "直圧式は3階まで、増圧式はおおむね15階までの建物が対象です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "配水管の水圧で直接、建物の3階まで給水。", src: "https://www.city.saitama.lg.jp/001/006/002/046/003/p009173.html" },
        { k: "直結増圧の階数上限", v: "おおむね15階までの建物。", src: "https://www.city.saitama.lg.jp/001/006/002/046/003/p009173.html" }
      ],
      links: [
        { t: "さいたま市 直結給水の案内", u: "https://www.city.saitama.lg.jp/001/006/002/046/003/p009173.html" },
        { t: "さいたま市 設計施工基準", u: "https://www.city.saitama.lg.jp/001/006/002/050/005/p012533_d/fil/sekkeisekoukijunn.pdf" }
      ]
    },
    {
      id: "kyoto", name: "京都市上下水道局", pref: "京都府", region: "近畿",
      law: "給水装置工事基準（上水道編）",
      scope: "京都市上下水道局の給水区域。",
      floors: { directMax: 5, boosterMin: 3, boosterMax: null, note: "手引きの図では直結直圧式は5階建て以下、直結増圧式は3階建て以上。3〜5階はどちらになるか局への確認が必要です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "5階建て以下（手引きの給水方式の図による）。", src: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000327/327572/tebiki(R7.4.1).pdf" },
        { k: "直結増圧の対象", v: "3階建て以上（手引きの給水方式の図による）。階数の上限は未確認。", src: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000327/327572/tebiki(R7.4.1).pdf" },
        { k: "関連する基準", v: "給水補助加圧装置設置基準（令和7年4月1日改正）、特定区間の標準配管図集（令和4年12月改訂）。", src: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000258/258521/kaatu-R7.pdf" }
      ],
      links: [
        { t: "京都市 給水装置工事基準（上水道編）", u: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000258/258521/koujikijyun-R7.pdf" },
        { t: "京都市 技術的基準", u: "https://www.city.kyoto.lg.jp/suido/cmsfiles/contents/0000322/322801/3gijyututekikijyun.pdf" }
      ]
    },
    {
      id: "osaka", name: "大阪市水道局", pref: "大阪府", region: "近畿",
      law: "給水装置の構造、工事材料及び工事費の算出方法等に関する規定の細目",
      scope: "大阪市水道局の給水区域。",
      floors: { directMax: null, boosterMin: null, boosterMax: null, note: "階数の基準は未確認です。直結増圧の対象は平成30年7月申込分から拡大されています。" },
      items: [
        { k: "直結直圧で給水できる階数", v: null, src: "https://www.city.osaka.lg.jp/suido/cmsfiles/contents/0000670/670760/32sonota.pdf" },
        { k: "直結増圧の扱い", v: "建物の高さなどの条件を緩和し、平成30年7月2日の工事申込分から直結増圧の対象を拡大。", src: "https://www.city.osaka.lg.jp/suido/cmsfiles/contents/0000670/670760/88sonota.pdf" },
        { k: "専用給水装置の数", v: "1戸・1事業につき1つが原則。直結増圧で単独対応できない大規模共同住宅などは条件付きで複数可。", src: "https://www.city.osaka.lg.jp/suido/cmsfiles/contents/0000621/621197/bessi.pdf" }
      ],
      links: [
        { t: "大阪市 規定の細目（2025年5月改訂）", u: "https://www.city.osaka.lg.jp/suido/cmsfiles/contents/0000670/670760/32sonota.pdf" }
      ]
    },
    {
      id: "hiroshima", name: "広島市水道局", pref: "広島県", region: "中国・四国",
      law: "直結給水に関する基準",
      scope: "広島市水道局の給水区域。",
      floors: { directMax: null, boosterMin: null, boosterMax: null, note: "4階以上へ配水管の水圧のみで給水する場合と、増圧装置を使う場合の基準があります。階数の上限は未確認です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "配水管の水圧のみで4階以上へ直接給水する場合の基準あり（上限階数は未確認）。", src: "https://www.water.city.hiroshima.lg.jp/uploaded/attachment/7796.pdf" },
        { k: "直結増圧の階数上限", v: null, src: "https://www.water.city.hiroshima.lg.jp/uploaded/attachment/7796.pdf" }
      ],
      links: [
        { t: "広島市 直結給水の基準", u: "https://www.water.city.hiroshima.lg.jp/uploaded/attachment/7796.pdf" }
      ]
    },
    {
      id: "sapporo", name: "札幌市水道局", pref: "北海道", region: "北海道・東北",
      law: "給水装置工事設計施工指針",
      scope: "札幌市水道局の給水区域。",
      floors: { directMax: null, boosterMin: null, boosterMax: null, note: "階数の基準は未確認です。対象地域でも直結できない場合があり、事前協議が必要です。" },
      items: [
        { k: "直結給水の対象地域", v: "直結直圧は配水管の水圧が所定の値を確保できる地域、直結加圧は一部を除く市街化区域内。事前協議が必要。", src: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/6.pdf" },
        { k: "3階以上の扱い", v: "直結給水で3階以上に給水する場合は、損失水頭の計算を水理計算書に記入。", src: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/0_sinkyutaisyouhyou.pdf" },
        { k: "直結直圧で給水できる階数", v: null, src: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/6.pdf" }
      ],
      links: [
        { t: "札幌市 設計施工指針（給水方式の章）", u: "https://www.city.sapporo.jp/suido/jigyosya/shitei/documents/6.pdf" }
      ]
    },
    {
      id: "fukuoka", name: "福岡市水道局", pref: "福岡県", region: "九州・沖縄",
      law: "給水装置工事施行基準（令和8年4月1日改訂）",
      scope: "福岡市水道局の給水区域。",
      floors: { directMax: 3, boosterMin: null, boosterMax: null, note: "直結直圧は3階建てまで（水理計算上給水できる建物）。病院・ホテル・飲食店・工場などは貯水槽が必要です。" },
      items: [
        { k: "直結直圧で給水できる階数", v: "3階建てまで（水理計算上給水可能な建物）。高低差のある土地は事前協議が必要。", src: "https://www.city.fukuoka.lg.jp/mizu/sessui/machi/002.html" },
        { k: "直結増圧の対象", v: "中高層のマンション・事務所ビルが主な対象。階数の上限は未確認。", src: "https://www.city.fukuoka.lg.jp/mizu/sessui/machi/002.html" },
        { k: "貯水槽が必要な建物", v: "病院、ホテル、飲食店、工場など、断水時にも業務用水が必要な施設。", src: "https://www.city.fukuoka.lg.jp/mizu/sessui/machi/002.html" },
        { k: "窓口", v: "直結給水の相談：水道局 節水推進課。事前協議・申請：水道サービス公社 給水審査課。", src: "https://www.city.fukuoka.lg.jp/mizu/sessui/machi/002.html" }
      ],
      links: [
        { t: "福岡市 直結給水の案内", u: "https://www.city.fukuoka.lg.jp/mizu/sessui/machi/002.html" },
        { t: "福岡市 給水装置工事施行基準", u: "https://www.city.fukuoka.lg.jp/mizu/sessui/0026.html" }
      ]
    }
  ]
};
