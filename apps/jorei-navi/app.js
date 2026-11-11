// 条例ナビ：画面の描画と、かんたん判定
(function () {
  "use strict";
  var DATA = window.JOREI_DATA || {};
  var state = { tab: "signage", q: "", region: "" };
  var $ = function (id) { return document.getElementById(id); };

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function link(url, text) {
    return '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(text) + "</a>";
  }
  function pill(kind, text) { return '<span class="pill ' + kind + '">' + esc(text) + "</span>"; }

  // 看板：自家用広告物の面積から、許可が要りそうかの目安を返す
  // mode が "each" の自治体は、合計ではなく「いちばん大きい看板」の面積で判断する
  function judgeSignage(entry, area, maxOne, zone) {
    var s = entry.selfUse || {};
    if (s.limit == null) return { kind: "warn", label: "未確認", note: s.note };
    var each = s.mode === "each";
    var limit = zone === "commercial" && s.limitCommercial ? s.limitCommercial : s.limit;
    var value = each ? maxOne : area;
    var what = each ? "いちばん大きい看板が" : "合計が";
    if (value > limit) return { kind: "ng", label: "許可が必要", note: what + "目安の" + limit + "㎡を超えています。" + s.note };
    return { kind: "ok", label: "許可不要の可能性", note: what + "目安の" + limit + "㎡以下。" + s.note };
  }

  // 給水：建物の階数から、選べそうな給水方式の目安を返す
  function judgeWater(entry, floors) {
    var f = entry.floors || {};
    if (f.directMax == null) return { kind: "warn", label: "未確認", note: f.note };
    if (floors <= f.directMax) return { kind: "ok", label: "直結直圧の対象になり得る", note: f.note };
    if (f.boosterMax != null && floors > f.boosterMax) return { kind: "ng", label: "受水槽式などを検討", note: f.note };
    return { kind: "warn", label: "直結増圧などを検討", note: f.note };
  }

  function renderCheck() {
    var d = DATA[state.tab];
    var isSign = state.tab === "signage";
    $("check-title").textContent = isSign ? "かんたん判定：自分の店の看板に許可は要る？" : "かんたん判定：何階建てまで直結で給水できる？";
    $("check-hint").textContent = isSign
      ? "自分の店や事務所に出す看板（自家用広告物）の合計面積と、いちばん大きい看板の面積を入れると、自治体ごとの目安を表示します。合計で判断する自治体と、1つずつで判断する自治体があります。"
      : "建物の階数を入れると、受水槽なしで給水できそうかを水道局ごとに表示します。";
    $("lbl-area").hidden = !isSign;
    $("lbl-max").hidden = !isSign;
    $("lbl-zone").hidden = !isSign;
    $("lbl-floors").hidden = isSign;

    var area = parseFloat($("in-area").value);
    var maxOne = parseFloat($("in-max").value);
    var floors = parseInt($("in-floors").value, 10);
    var zone = $("in-zone").value;
    var bad = isSign ? !(area >= 0 && maxOne >= 0) : !(floors >= 1);
    var mismatch = isSign && !bad && maxOne > area;
    var rows = d.entries.map(function (e) {
      var r = bad ? { kind: "warn", label: "数値を入力", note: "" }
        : mismatch ? { kind: "warn", label: "入力を確認", note: "いちばん大きい看板の面積が、合計面積より大きくなっています。" }
        : isSign ? judgeSignage(e, area, maxOne, zone) : judgeWater(e, floors);
      return "<tr><td>" + esc(e.name) + "</td><td>" + pill(r.kind, r.label) + "</td><td>" + esc(r.note || "") + "</td></tr>";
    });
    $("check-table").innerHTML =
      "<thead><tr><th>" + (isSign ? "自治体" : "水道局") + "</th><th>目安</th><th>理由・注意</th></tr></thead><tbody>" + rows.join("") + "</tbody>";
  }

  function renderRegions() {
    var seen = [];
    DATA[state.tab].entries.forEach(function (e) { if (seen.indexOf(e.region) < 0) seen.push(e.region); });
    $("region").innerHTML = '<option value="">すべて</option>' + seen.map(function (r) {
      return '<option value="' + esc(r) + '"' + (r === state.region ? " selected" : "") + ">" + esc(r) + "</option>";
    }).join("");
    if (seen.indexOf(state.region) < 0) state.region = "";
  }

  function renderCards() {
    var d = DATA[state.tab];
    var q = state.q.trim();
    var list = d.entries.filter(function (e) {
      if (state.region && e.region !== state.region) return false;
      if (!q) return true;
      return (e.name + e.pref + e.law).indexOf(q) >= 0;
    });
    $("count").textContent = list.length + " 件 / 全 " + d.entries.length + " 件";
    $("cards").innerHTML = list.length ? list.map(function (e) {
      var items = e.items.map(function (it) {
        var unknown = it.v == null;
        return "<div><dt>" + esc(it.k) + (unknown ? pill("warn", "未確認") : "") + "</dt>" +
          '<dd class="' + (unknown ? "unknown" : "") + '">' + (unknown ? "公式資料で確認してください。" : esc(it.v)) +
          ' <span class="src">' + link(it.src, "出典") + "</span></dd></div>";
      }).join("");
      var links = e.links.map(function (l) { return "<li>" + link(l.u, l.t) + "</li>"; }).join("");
      return '<article class="card"><div><h3>' + esc(e.name) + '</h3><p class="sub">' + esc(e.pref) + "・" + esc(e.region) + "</p></div>" +
        '<p class="law">' + esc(e.law) + '</p><p class="sub">' + esc(e.scope) + "</p><dl>" + items + '</dl><ul class="links">' + links + "</ul></article>";
    }).join("") : '<p class="empty">条件に合う自治体がありません。検索の言葉を変えてみてください。</p>';
    $("checked").textContent = "データの確認日：" + d.checkedOn;
  }

  function renderAll() {
    Array.prototype.forEach.call(document.querySelectorAll(".tabs button"), function (b) {
      b.setAttribute("aria-selected", String(b.dataset.tab === state.tab));
    });
    renderRegions(); renderCheck(); renderCards();
  }

  document.querySelector(".tabs").addEventListener("click", function (ev) {
    var b = ev.target.closest("button[data-tab]");
    if (!b) return;
    state.tab = b.dataset.tab;
    renderAll();
  });
  $("check-form").addEventListener("input", renderCheck);
  $("check-form").addEventListener("submit", function (ev) { ev.preventDefault(); });
  $("q").addEventListener("input", function () { state.q = this.value; renderCards(); });
  $("region").addEventListener("change", function () { state.region = this.value; renderCards(); });

  renderAll();
})();
