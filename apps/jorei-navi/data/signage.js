// 屋外広告物データ（試作版）
// v が null の項目は「未確認」。必ず src（公式資料）で原文を確認すること。
window.JOREI_DATA = window.JOREI_DATA || {};
window.JOREI_DATA.signage = {
  title: "屋外広告物（看板）",
  checkedOn: "2026-11-10",
  entries: [
    {
      id: "tokyo", name: "東京都", pref: "東京都", region: "関東",
      law: "東京都屋外広告物条例",
      scope: "都内の区市町村。八王子市は市独自の条例、町田市は設置許可のみ市条例が適用されます。",
      selfUse: { limit: 5, limitCommercial: 10, note: "自家用広告物は合計5㎡（商業地域等は10㎡）を超えると許可対象（区の案内資料による）。" },
      items: [
        { k: "許可期間", v: "広告板等は原則2年。引き続き表示する場合は継続申請が必要。", src: "https://www.toshiseibi.metro.tokyo.lg.jp/tamakenchikushidou/shigoto/okugaikoukoku" },
        { k: "自家用広告物の扱い", v: "合計5㎡（商業地域等は10㎡）を超えると許可対象。", src: "https://www.city.setagaya.lg.jp/documents/3783/okugairule.pdf" },
        { k: "手数料", v: null, src: "https://www.toshiseibi.metro.tokyo.lg.jp/ryokuchi_keikan/kekan_kese/koukoku/siori" },
        { k: "窓口", v: "区部は各区、多摩地域は市町村または都の担当課（場所・広告物の種類で異なる）。", src: "https://www.toshiseibi.metro.tokyo.lg.jp/kenchiku/koukoku/index.html" }
      ],
      links: [
        { t: "東京都 屋外広告物のしおり", u: "https://www.toshiseibi.metro.tokyo.lg.jp/ryokuchi_keikan/kekan_kese/koukoku/siori" },
        { t: "東京都 屋外広告物条例の概要", u: "https://www.toshiseibi.metro.tokyo.lg.jp/kenchiku/koukoku/kou_jourei.htm" }
      ]
    },
    {
      id: "yokohama", name: "横浜市", pref: "神奈川県", region: "関東",
      law: "横浜市屋外広告物条例",
      scope: "横浜市内（市独自の条例）。",
      selfUse: { limit: 10, note: "自家用広告物で表示面積の合計が10㎡以内のものなどは許可不要の場合あり（条例第12条）。細かい条件は手引きで確認。" },
      items: [
        { k: "自家用広告物の扱い", v: "表示面積の合計が10㎡以内のものなどは許可不要の場合あり（条例第12条）。", src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugai-qa.html" },
        { k: "許可期間", v: null, src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugaitebiki.files/tebiki_butsu_20260401.pdf" },
        { k: "手数料", v: null, src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugaitebiki.files/tebiki_butsu_20260401.pdf" },
        { k: "窓口", v: "都市整備局 景観調整課", src: "https://www.city.yokohama.lg.jp/faq/kukyoku/toshi/keikan-chosei/20211015130617086.html" }
      ],
      links: [
        { t: "横浜市 屋外広告物の手引き（2026年4月）", u: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugaitebiki.files/tebiki_butsu_20260401.pdf" },
        { t: "横浜市 適用除外の一覧", u: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugai-tekiyoujogai.html" }
      ]
    },
    {
      id: "nagoya", name: "名古屋市", pref: "愛知県", region: "中部",
      law: "名古屋市屋外広告物条例",
      scope: "名古屋市内（市独自の条例）。愛知県内では豊橋・岡崎・一宮・豊田・小牧の各市も独自条例です。",
      selfUse: { limit: null, note: "自家用広告物の適用除外の面積は未確認です。" },
      items: [
        { k: "許可期間", v: "広告板・広告塔は3年以内、立看板・広告旗・広告幕は3か月以内、電柱広告は3年以内。", src: "https://www.city.nagoya.jp/jutakutoshi/cmsfiles/contents/0000173/173420/kyokakikan_tesuuryou1.pdf" },
        { k: "手数料", v: "広告板・広告塔：面積5㎡あたり1,300円（電光表示装置等は1,900円）。立看板・広告旗：1個150円。広告幕：1個500円。電柱広告：1個300円。（許可の始期が令和6年10月以降のもの）", src: "https://www.city.nagoya.jp/jutakutoshi/cmsfiles/contents/0000173/173420/kyokakikan_tesuuryou1.pdf" },
        { k: "自家用広告物の扱い", v: null, src: "https://www.city.nagoya.jp/jutakutoshi/cmsfiles/contents/0000010/10566/R6.4tebiki.pdf" },
        { k: "その他", v: "継続許可の際は安全点検が義務。許可証（許可シール）は2024年4月以降交付されません。", src: "https://www.city.nagoya.jp/jutakutoshi/cmsfiles/contents/0000070/70762/202408_keizokukyokashinsei-anzentenkennoonegai.pdf" }
      ],
      links: [
        { t: "名古屋市 屋外広告物のページ", u: "https://www.city.nagoya.jp/jigyou/toshikeikaku/1017988/index.html" },
        { t: "名古屋市 屋外広告物の手引き", u: "https://www.city.nagoya.jp/jutakutoshi/cmsfiles/contents/0000010/10566/R6.4tebiki.pdf" }
      ]
    },
    {
      id: "kyoto", name: "京都市", pref: "京都府", region: "近畿",
      law: "京都市屋外広告物等に関する条例",
      scope: "京都市内全域（21種類の規制区域。先斗町などの特別規制地区もあり）。",
      selfUse: { limit: 2, note: "自家用で合計面積が2㎡以下のものは許可不要。" },
      items: [
        { k: "許可期間", v: "3年。自動更新ではなく、更新（継続）の手続きが必要。", src: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000102/102522/sinnseinotebikir8.pdf" },
        { k: "手数料", v: "建築物等定着型（袖看板・壁面看板など）：5㎡までごとに照明なし4,200円／照明あり6,300円。その他・土地に定着するもの：照明なし2,600円／照明あり3,900円。", src: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000102/102522/sinnseinotebikir8.pdf" },
        { k: "自家用広告物の扱い", v: "合計面積2㎡以下は許可不要。", src: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000283/283884/syuutipanhu.pdf" },
        { k: "禁止されるもの", v: "屋上広告物、可動式・点滅式の広告物は市内全域で禁止。", src: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000283/283884/syuutipanhu.pdf" }
      ],
      links: [
        { t: "京都市 許可申請の手引き", u: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000102/102522/sinnseinotebikir8.pdf" },
        { t: "京都市 規制区域の基準概要", u: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000056/56450/04_040604.pdf" }
      ]
    },
    {
      id: "osaka", name: "大阪市", pref: "大阪府", region: "近畿",
      law: "大阪市屋外広告物条例",
      scope: "大阪市内（市独自の条例）。",
      selfUse: { limit: null, note: "自家用広告物の適用除外の面積は未確認です。" },
      items: [
        { k: "手数料（簡易広告物）", v: "広告幕：1張300円。アドバルーン：1個500円。広告旗・立看板等：1本（枚）150円。はり紙・はり札等：100枚につき200円。", src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000018/18630/hou-1.pdf" },
        { k: "審査にかかる期間", v: "申請から許可まで、一般広告物は3週間程度、簡易広告物等は2週間程度。", src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/QA.pdf" },
        { k: "許可期間", v: null, src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/R4.siori.pdf" },
        { k: "自家用広告物の扱い", v: null, src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/R4.siori.pdf" }
      ],
      links: [
        { t: "大阪市 屋外広告物のしおり", u: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/R4.siori.pdf" },
        { t: "大阪市 屋外広告物Q&A", u: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/QA.pdf" }
      ]
    },
    {
      id: "sapporo", name: "札幌市", pref: "北海道", region: "北海道・東北",
      law: "札幌市屋外広告物条例",
      scope: "札幌市内（北海道の条例は適用されません）。",
      selfUse: { limit: 10, note: "自家用広告物のみで合計10㎡以下、かつ高さが20mを超えないものなどは許可申請が不要の場合あり。" },
      items: [
        { k: "自家用広告物の扱い", v: "自家用のみの掲出で総面積10㎡以下（高さ20m以下）などは許可申請が不要の場合あり。", src: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/documents/jourei_keihatu.pdf" },
        { k: "許可期間・手数料（宣伝車）", v: "宣伝車は1か月以内、1台につき1,800円。", src: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/kyoka.html" },
        { k: "許可期間・手数料（看板類）", v: null, src: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/kyoka.html" },
        { k: "規制区域の調べ方", v: "札幌市地図情報サービスの「屋外広告物許可規制区域」で確認可（誤差があり証明には使えません）。", src: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/kiseizu.html" }
      ],
      links: [
        { t: "札幌市 屋外広告物の許可と手続き", u: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/kyoka.html" },
        { t: "札幌市 規制区域図", u: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/kiseizu.html" }
      ]
    },
    {
      id: "fukuoka", name: "福岡市", pref: "福岡県", region: "九州・沖縄",
      law: "福岡市屋外広告物条例",
      scope: "福岡市内（市独自の条例）。",
      selfUse: { limit: 10, note: "自家用広告物は合計10㎡以内なら許可申請不要。ただし発光可変表示式・ネオンサイン、都市高速道路等の沿道は面積にかかわらず許可が必要。" },
      items: [
        { k: "自家用広告物の扱い", v: "敷地内の自家用広告物は合計10㎡以内なら許可申請不要。発光可変表示式広告物・ネオンサイン、都市高速道路・西九州自動車道から一定範囲のものは面積にかかわらず許可が必要。", src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/documents/leafletkoukoku.pdf" },
        { k: "許可期間", v: null, src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/adver_2.html" },
        { k: "手数料", v: null, src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/adver_2.html" },
        { k: "窓口", v: "住宅都市局 都市景観室", src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/adver_2.html" }
      ],
      links: [
        { t: "福岡市 屋外広告物のページ（手びき）", u: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/adver_2.html" },
        { t: "福岡市 屋外広告物条例（例規集）", u: "https://www.city.fukuoka.lg.jp/d1w_reiki/reiki_honbun/q003RG00000720.html" }
      ]
    }
  ]
};
