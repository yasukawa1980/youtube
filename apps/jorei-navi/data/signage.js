// 屋外広告物データ（試作版）
// 2026-11-10〜11 に公式資料の原文と照合済み（照合表：../照合表_大阪市_看板.md、../照合表_6都市_看板.md）。
// v が null の項目は「未確認」。文中の「（未確認：…）」は、原文で確かめられなかった部分。
// selfUse.mode："total"＝看板の合計面積で判断／"each"＝1つずつの面積で判断
window.JOREI_DATA = window.JOREI_DATA || {};
window.JOREI_DATA.signage = {
  title: "屋外広告物（看板）",
  checkedOn: "2026-11-11（公式資料の原文と照合）",
  entries: [
    {
      id: "tokyo", name: "東京都", pref: "東京都", region: "関東",
      law: "東京都屋外広告物条例",
      scope: "都内の区市町村。八王子市は市独自の条例。町田市は令和6年10月1日から市の条例に移行しました。",
      selfUse: { mode: "total", limit: 5, limitCommercial: 10, note: "自家用広告物は合計5㎡を超えると許可対象。ただし第一種・第二種住居地域、準住居地域、近隣商業地域、商業地域、準工業地域、工業地域などでは合計10㎡まで（施行規則 別表第二）。低層・中高層住居専用地域、田園住居地域、風致地区、第一種文教地区などは5㎡。" },
      items: [
        { k: "許可期間", v: "広告板等は原則2年。引き続き表示する場合は継続申請が必要。", src: "https://www.toshiseibi.metro.tokyo.lg.jp/tamakenchikushidou/shigoto/okugaikoukoku" },
        { k: "自家用広告物の扱い", v: "表示面積の合計が5㎡（商業地域等では10㎡）を超えると許可対象。10㎡になるのは、第二種文教地区、第一種・第二種住居地域、準住居地域、近隣商業地域、商業地域、準工業地域、工業地域、工業専用地域、用途地域の指定のない地域など。5㎡は低層・中高層住居専用地域、田園住居地域、風致地区、特別緑地保全地区、自然公園の特別地域、第一種文教地区など。屋上に付けない・ネオン管を使わないなど、地域ごとの禁止事項もある。", src: "https://www.reiki.metro.tokyo.lg.jp/reiki/reiki_honbun/g101RG00001184.html" },
        { k: "手数料（多摩地域・都の許可分）", v: "広告塔・広告板：5㎡までごとに3,220円。小型広告板：1枚400円。はり紙等：50枚までごとに2,250円。広告旗・立看板等：1本（枚）450円。広告幕：1張990円。アドバルーン：1個2,850円。", src: "https://www.toshiseibi.metro.tokyo.lg.jp/tamakenchikushidou/shigoto/okugaikoukoku" },
        { k: "手数料（23区）", v: "区ごとの手数料条例で決まる。練馬区・千代田区は都と同じ額（広告塔・広告板は5㎡までごとに3,220円、小型広告板1枚400円、はり紙等50枚までごとに2,250円）。千代田区は広告塔・広告板の許可期間を2年以内としている。（未確認：残り21区の額）", src: "https://www1.g-reiki.net/nerima/reiki_honbun/a100RG00000674.html" },
        { k: "窓口", v: "区部は各区、多摩地域は市町または都の多摩建築指導事務所（場所・広告物の種類で異なる）。", src: "https://www.toshiseibi.metro.tokyo.lg.jp/ryokuchi_keikan/kekan_kese/koukoku/madoguchi-ichiran" }
      ],
      links: [
        { t: "東京都 屋外広告物のしおり等", u: "https://www.toshiseibi.metro.tokyo.lg.jp/ryokuchi_keikan/kekan_kese/koukoku/siori" },
        { t: "東京都 屋外広告物（トップ）", u: "https://www.toshiseibi.metro.tokyo.lg.jp/ryokuchi_keikan/kekan_kese/koukoku/" }
      ]
    },
    {
      id: "yokohama", name: "横浜市", pref: "神奈川県", region: "関東",
      law: "横浜市屋外広告物条例",
      scope: "横浜市内（市独自の条例）。",
      selfUse: { mode: "total", limit: 10, note: "1敷地あたりの表示面積の合計が10㎡以下で、蛍光塗料を使わないことなどが条件（条例第12条）。景観計画区域内では10㎡以下でも許可が必要な場合あり。" },
      items: [
        { k: "自家用広告物の扱い", v: "1敷地あたりの表示面積の合計が10㎡以下で、蛍光塗料を使わないなどの基準をすべて満たせば許可不要。景観計画区域内では10㎡以下でも許可が必要な場合あり。", src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugai-tekiyoujogai.html" },
        { k: "許可期間", v: "壁面・突出・広告塔・広告板などの看板類は3年以下。はり札等は1年以下、広告幕は3月以下、はり紙・広告旗・立看板等・アドバルーンは1月以下（施行規則第7条）。", src: "https://cgi.city.yokohama.lg.jp/somu/reiki/reiki_honbun/g202RG00001705.html" },
        { k: "手数料", v: "看板類：1基（5㎡を超えるものは5㎡までごと）照明あり2,400円／照明なし1,500円。電柱等：1枚150円。はり紙：100枚までごとに500円。広告旗：1張200円。アドバルーン：1個1,000円。", src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugaitebiki.files/tebiki_butsu_20260401.pdf" },
        { k: "継続と除却", v: "継続の許可は、許可期間満了日の30日前までに申請。期間満了後10日以内に除却。", src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugaitebiki.files/tebiki_butsu_20260401.pdf" },
        { k: "窓口", v: "都市整備局 景観調整課", src: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugaitebiki.files/tebiki_butsu_20260401.pdf" }
      ],
      links: [
        { t: "横浜市 屋外広告物の手引き（2026年4月）", u: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugaitebiki.files/tebiki_butsu_20260401.pdf" },
        { t: "横浜市 適用除外の一覧", u: "https://www.city.yokohama.lg.jp/business/bunyabetsu/toshiseibi/koukokubutsu/okugaitetsuzuki/okugai-tekiyoujogai.html" }
      ]
    },
    {
      id: "nagoya", name: "名古屋市", pref: "愛知県", region: "中部",
      law: "名古屋市屋外広告物条例",
      scope: "名古屋市内（市独自の条例）。",
      selfUse: { mode: "total", limit: 10, note: "表示面積の合計10㎡以下。ただし禁止地域等では合計5㎡以下で、赤色ネオン・点滅照明・回転灯を使わないこと（条例第7条、施行細則第7条）。" },
      items: [
        { k: "自家用広告物の扱い", v: "表示面積の合計が10㎡以下なら許可不要。禁止地域等（条例第6条第1項の地域）では合計5㎡以下で、赤色ネオンサイン・点滅する電気照明・回転灯を使わないこと。", src: "https://www.city.nagoya.jp/_res/projects/default_project/_page_/001/017/988/20241001_okugaikoukokubutsujyoureisekousaisoku.pdf" },
        { k: "許可期間", v: "広告板・広告塔・建物への直接表示は3年以内、電柱広告は3年以内、立看板・広告旗・広告幕・アドバルーン・はり紙は3か月以内（施行細則第4条）。広告板・広告塔などは、許可期間を1年以下にすると手数料が安くなる（例：面積5㎡ごとに1,300円→600円、電光表示ありは1,900円→1,200円。施行細則 別表第2の備考）。", src: "https://www.city.nagoya.jp/_res/projects/default_project/_page_/001/017/988/20241001_okugaikoukokubutsujyoureisekousaisoku.pdf" },
        { k: "手数料", v: "広告板・広告塔：面積5㎡ごとに1,300円（電光表示装置等は1,900円）。立看板・広告旗：1個150円。広告幕：1個500円。アドバルーン：1個700円。電柱広告：1個300円。はり紙等：100枚400円。", src: "https://www.city.nagoya.jp/jigyou/toshikeikaku/1017988/1017996/1018006.html" },
        { k: "安全点検", v: "1年以内に除却するものを除くすべての屋外広告物に、毎年1回の安全点検が義務。条件に当てはまる看板は3年に1度、有資格者による点検も必要。継続許可の申請時に点検結果を報告。", src: "https://www.city.nagoya.jp/jigyou/toshikeikaku/1017988/1018003.html" },
        { k: "許可シール", v: "許可を受けた看板にはる許可証（許可シール）と証印は廃止。令和6年4月以降は交付されない。", src: "https://www.city.nagoya.jp/jigyou/toshikeikaku/1017988/1011699/1011700.html" }
      ],
      links: [
        { t: "名古屋市 屋外広告物のページ", u: "https://www.city.nagoya.jp/jigyou/toshikeikaku/1017988/index.html" },
        { t: "名古屋市 屋外広告物条例", u: "https://www.city.nagoya.jp/_res/projects/default_project/_page_/001/017/988/20241001_okugaikoukokubutsujourei.pdf" }
      ]
    },
    {
      id: "kyoto", name: "京都市", pref: "京都府", region: "近畿",
      law: "京都市屋外広告物等に関する条例",
      scope: "京都市内全域（禁止地域、21種類の規制区域、先斗町などの特別規制地区）。",
      selfUse: { mode: "total", limit: 2, note: "区画内の合計面積が2㎡以下なら許可不要。区画内に複数の店舗がある場合は全店舗の合計。許可不要でも高さ・色彩などの基準には合わせる必要あり。" },
      items: [
        { k: "許可期間", v: "3年（種別により短い場合あり。アドバルーンは7日など）。有効期間は許可の日から3年となる前月の月末まで。継続する場合は更新の手続きが必要。", src: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000102/102522/sinnseinotebikir8.pdf" },
        { k: "手数料", v: "1個につき面積5㎡までごと。ひさし看板等：照明なし4,200円／照明あり6,300円。その他の建築物に定着するもの・土地に定着するもの：照明なし2,600円／照明あり3,900円。広告スタンド：800円／1,200円。", src: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000102/102522/sinnseinotebikir8.pdf" },
        { k: "自家用広告物の扱い", v: "区画内の合計面積が2㎡以下なら許可不要。区画内に複数の店舗がある場合は全店舗の合計。許可不要でも高さ・色彩などの基準には合わせる必要あり。", src: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000102/102522/sinnseinotebikir8.pdf" },
        { k: "禁止されるもの", v: "屋上広告物は市内全域で設置禁止。点滅する照明・動く照明（回転灯など）も、看板に使うことが市内全域で禁止（緊急・警告・交通規制など公衆の安全のためのものは除く。施行規則 別表第3）。", src: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000056/56450/05_20701.pdf" }
      ],
      links: [
        { t: "京都市 許可申請の手引き（令和8年10月改訂）", u: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000102/102522/sinnseinotebikir8.pdf" },
        { t: "京都市 景観ガイドライン 屋外広告物制度の解説", u: "https://www.city.kyoto.lg.jp/tokei/cmsfiles/contents/0000056/56450/04_040604.pdf" }
      ]
    },
    {
      id: "osaka", name: "大阪市", pref: "大阪府", region: "近畿",
      law: "大阪市屋外広告物条例",
      scope: "大阪市内（市独自の条例）。",
      selfUse: { mode: "each", limit: 7, note: "合計ではなく1つあたりの表示面積で判断。7㎡を超える看板だけ申請が必要（条例第7条、施行規則第7条）。自家用でない看板は大きさに関係なく申請が必要。" },
      items: [
        { k: "自家用広告物の扱い", v: "1つあたりの表示面積が7㎡以下なら許可不要。合計ではなく1つずつで判断する（例：5㎡・6㎡・9㎡の看板なら、9㎡の1つだけ申請が必要）。自家用でない看板は大きさに関係なく申請が必要。", src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/QA.pdf" },
        { k: "許可期間", v: "許可の期限は3年以内。簡易広告物等・アドバルーン・広告幕は30日以内（施行規則第4条）。しおりの表では、広告塔・広告板は資格のある管理者を置く場合3年以内、それ以外は2年以内。条例第2条第2項で、市長は許可に期限を付けられる。（未確認：2年以内とする規定そのもの。条例・規則には書かれていない）", src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/R7.okugaikoukokubutunosiori.pdf" },
        { k: "手数料", v: "広告塔・広告板：5㎡までごとに950円。電柱利用・車体利用・小型看板：1個200円。広告幕：1張300円。アドバルーン：1個500円。広告旗・立看板等：1本（枚）150円。はり紙・はり札等：100枚につき200円（条例 別表）。", src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/(R5)s31.10.1.okugaijyourei.pdf" },
        { k: "審査にかかる期間", v: "申請から許可まで、一般広告物は3週間程度、簡易広告物等は2週間程度。", src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/R7.okugaikoukokubutunosiori.pdf" },
        { k: "継続申請の期限", v: "許可期限が切れる日の7日前までに許可を受ける（条例第3条第2項）。", src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/(R5)s31.10.1.okugaijyourei.pdf" },
        { k: "窓口", v: "建設局総務部管理課（ATCビル ITM棟6階、06-6615-6687）。オンライン申請もあり。", src: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/R7.okugaikoukokubutunosiori.pdf" }
      ],
      links: [
        { t: "大阪市 屋外広告物の許可について（資料一覧）", u: "https://www.city.osaka.lg.jp/kensetsu/page/0000372127.html" },
        { t: "大阪市 屋外広告物のしおり（令和8年1月発行）", u: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/R7.okugaikoukokubutunosiori.pdf" },
        { t: "大阪市 屋外広告物よくある質問", u: "https://www.city.osaka.lg.jp/kensetsu/cmsfiles/contents/0000372/372127/QA.pdf" }
      ]
    },
    {
      id: "sapporo", name: "札幌市", pref: "北海道", region: "北海道・東北",
      law: "札幌市屋外広告物条例",
      scope: "札幌市内（北海道の条例は適用されません）。",
      selfUse: { mode: "total", limit: 10, note: "自家用広告物の表示面積の合計が10㎡以下で、かつ高さが20mを超えないもの。" },
      items: [
        { k: "自家用広告物の扱い", v: "表示面積の合計が10㎡以下で、かつ高さが20mを超えないものは許可不要。", src: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/documents/jourei_keihatu.pdf" },
        { k: "許可期間", v: "看板類は3年以内。はり紙・アドバルーン等は15日以内、立看板・宣伝車・広告旗等は1月以内、柱状広告物・車体利用広告・広告幕・内容を定期的に変えるもの等は1年以内（施行規則第6条）。", src: "https://www.city.sapporo.jp/ncms/reiki/d1w_reiki_nonframe/H411902100021/H411902100021_j.html" },
        { k: "手数料", v: "広告板・広告塔など：表示面積5㎡までごとに照明なし1,300円／照明あり1,900円。電光板：1,900円。立看板：1枚850円。宣伝車：1台1,800円。自家用広告は合計面積から10㎡分を差し引いて計算（条例第12条・別表1、施行規則第12条の2）。", src: "https://www.city.sapporo.jp/ncms/reiki/d1w_reiki_nonframe/H410901010043/H410901010043_j.html" },
        { k: "窓口", v: "看板がある区の土木センター。", src: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/documents/jourei_keihatu.pdf" },
        { k: "規制区域の調べ方", v: "札幌市地図情報サービスのテーマ「屋外広告物許可規制区域」で調べられる。ただし誤差があり、許可地域であることの証明には使えない。正確に知るには各区土木センターか建設局道路管理課に問い合わせる。大通地区（令和6年3月指定）は地図への反映が遅れるため別ページで確認。", src: "https://www.city.sapporo.jp/kensetsu/dokan/kokoku/kiseizu.html" }
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
      selfUse: { mode: "total", limit: 10, note: "合計10㎡以内なら許可不要。ただし発光可変表示式・ネオンサイン、都市高速道路・西九州自動車道から一定範囲のものは面積にかかわらず許可が必要。" },
      items: [
        { k: "自家用広告物の扱い", v: "合計10㎡以内なら許可不要。発光可変表示式広告物・ネオンサイン、都市高速道路・西九州自動車道から一定範囲のものは面積にかかわらず許可が必要。", src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/documents/leafletkoukoku.pdf" },
        { k: "許可期間", v: "広告板・広告塔など：1年以内。はり紙・はり札・立看板・広告幕・アドバルーン：1月以内。", src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/documents/tebiki300409.pdf" },
        { k: "手数料", v: "広告板・広告塔など1個につき面積で段階制：1㎡未満200円、1〜2㎡未満400円、2〜5㎡未満800円、5〜10㎡未満1,600円、10〜20㎡未満3,200円、20〜30㎡未満5,000円、30〜50㎡未満8,000円、50㎡以上は8,000円に1㎡ごと200円を加算。照明付きは2倍。非営利の広告物は不要。", src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/documents/tebiki300409.pdf" },
        { k: "更新と除却", v: "更新は許可期間満了日の7日前までに申請。満了後10日以内に除却。", src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/documents/tebiki300409.pdf" },
        { k: "窓口", v: "住宅都市みどり局 地域まちづくり推進部 都市景観室（092-711-4395）", src: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/adver_2.html" }
      ],
      links: [
        { t: "福岡市 屋外広告物のページ", u: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/adver_2.html" },
        { t: "福岡市 屋外広告物の手びき（令和8年10月）", u: "https://www.city.fukuoka.lg.jp/jutaku-toshi/toshikeikan/okugaikoukokubutsu/documents/tebiki300409.pdf" }
      ]
    }
  ]
};
