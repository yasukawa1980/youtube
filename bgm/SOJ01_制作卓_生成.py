# -*- coding: utf-8 -*-
"""SOJ01_コピー用プロンプト.md から制作卓のHTMLを組む。プロンプトは打ち直さない。"""
import html
import json
import re

SRC = "/Users/ryo/youtube/bgm/SOJ01_コピー用プロンプト.md"
OUT = "/Users/ryo/youtube/bgm/Vol16_制作卓.html"

md = open(SRC).read()
blocks = re.findall(
    r"^## (\d{2})\. (.+?)\n\n(第[一二三]幕)／音＝(\S+?)(  ★人物)?\n\n```\n(.*?)\n```",
    md, re.S | re.M)
assert len(blocks) == 22, len(blocks)

ACT = {"第一幕": ("one", "通りを歩く", "雨は開けて広い。粒が立つ"),
       "第二幕": ("two", "軒下", "雨が近い。滴が一つずつ聞こえる"),
       "第三幕": ("three", "屋内", "雨が遠のき、高い方が落ちてこもる")}

scenes = []
for num, label, act, sound, fig, body in blocks:
    scenes.append(dict(n=int(num), label=label.replace("★", "").strip(),
                       act=act, sound=sound, fig=bool(fig), body=body.strip()))

SOUNDS = [
    ("①石畳と舗装", "場面 1–8", 4, "rain on pavement / rain on street", "広帯域・開けている"),
    ("②番傘", "場面 4・7", 2, "rain on umbrella", "粒が明確・近い"),
    ("③軒の雨だれ・雨樋", "場面 9–13", 4, "rain dripping / water dripping roof / rain gutter", "近接・滴が数えられる"),
    ("④屋内・障子/窓越し", "場面 14–20", 5, "rain on window / rain indoor / muffled rain", "低域寄り・高域が落ちている"),
    ("⑤細い雨", "場面 21–22", 2, "light rain / soft rain / quiet rain", "小さい・静か"),
    ("（ベース層 予備）", "当面は使わない", 1, "rain ambience / steady rain", "継ぎ目が気になったとき用"),
]
TOTAL_SOUNDS = sum(r[2] for r in SOUNDS)

CHECKS = [
    ("突発音", "0%", "雷・扉・話し声。睡眠用では一発で不可"),
    ("レベル変動", "≤ 2.5 dB", "雨脚が変わる素材は3時間ループで波打つ"),
    ("120Hz未満", "≤ 20%", "交通のゴロゴロ、マイクの吹かれ"),
    ("尺", "≥ 60秒", "ループの重ね幅の3倍が要る"),
    ("左右相関", "≤ 0.95", "モノラルを2chにしただけの素材"),
    ("無音区間", "無し", "途中で切れている素材"),
]

BANS = [
    ("文字", "提灯・のれん・看板・木札。この題材の最大の弱点。提灯は無地と明示してある"),
    ("雨の縦線", "AIの雨は引っかき傷になる。濡れた面・波紋・滴・霞で描かせる"),
    ("現代物", "電線・電柱・室外機・車・LED・白線・プラスチック"),
    ("顔と手", "後ろ姿のみ。手は袖に隠す。他の人物は1人も出さない"),
    ("月", "雨雲の下に月は無い。この巻だけ月を描かない"),
]

STEPS = [
    ("素材を検品する", 'python3 -m bgmkit vet "/Volumes/ESD-EPB/Whispers of Japan/SOJ01_素材_雨の石畳/環境音"',
     "「こもり」の大きい順に並んで出る。その順が第一幕→第三幕への割り振りになる"),
    ("画像の重複を見る", 'md5 "/Volumes/ESD-EPB/Whispers of Japan/SOJ01_素材_雨の石畳/画像/"*.png | awk \'{print $NF}\' | sort | uniq -d',
     "同じファイルが2回落ちても名前と日時では気づけない。何も出なければ重複なし"),
    ("音を組む", "python3 -m bgmkit audio soj01",
     "22本を497秒まで伸ばし、6秒重ねて連結。★ここで実際に聴いて target_lufs を決める"),
    ("通しで書き出す", "python3 -m bgmkit build soj01",
     "audio → video → mux → thumb。3時間は6GB前後・時間も約3倍かかる"),
]


def esc(s):
    return html.escape(s, quote=True)


def card(s):
    a = ACT[s["act"]][0]
    fig = '<span class="tag tag-fig">★人物</span>' if s["fig"] else ""
    return f"""<article class="scene act-{a}" data-n="{s['n']}">
<header class="scene-head">
<span class="num">{s['n']:02d}</span>
<div class="scene-id">
<h3>{esc(s['label'])}</h3>
<p class="meta"><span class="tag">音＝{esc(s['sound'])}</span>{fig}</p>
</div>
<label class="check"><input type="checkbox" data-key="img{s['n']}"><span>できた</span></label>
</header>
<pre class="prompt" id="p{s['n']}">{esc(s['body'])}</pre>
<button class="copy" data-target="p{s['n']}">プロンプトをコピー</button>
</article>"""


sound_rows = "\n".join(
    f"""<tr><th scope="row">{esc(a)}<span class="where">{esc(b)}</span></th>
<td class="n">{c}</td><td><code>{esc(d)}</code></td><td class="want">{esc(e)}</td></tr>"""
    for a, b, c, d, e in SOUNDS)

check_rows = "\n".join(
    f'<div class="crit"><span class="crit-k">{esc(k)}</span><span class="crit-v">{esc(v)}</span>'
    f'<span class="crit-w">{esc(w)}</span></div>' for k, v, w in CHECKS)

ban_rows = "\n".join(
    f'<li><strong>{esc(k)}</strong>{esc(v)}</li>' for k, v in BANS)

step_rows = "\n".join(
    f"""<li class="step">
<div class="step-t"><h3>{esc(t)}</h3><p>{esc(note)}</p></div>
<div class="cmdwrap"><pre class="cmd" id="c{i}">{esc(cmd)}</pre>
<button class="copy small" data-target="c{i}">コピー</button></div>
</li>""" for i, (t, cmd, note) in enumerate(STEPS))

acts_html = []
for act in ("第一幕", "第二幕", "第三幕"):
    key, where, sound = ACT[act]
    body = "\n".join(card(s) for s in scenes if s["act"] == act)
    ns = [s["n"] for s in scenes if s["act"] == act]
    acts_html.append(f"""<section class="act act-{key}">
<div class="act-head">
<span class="act-label">{act}</span>
<h2>{where}</h2>
<p>場面 {ns[0]}–{ns[-1]}　／　{sound}</p>
</div>
<div class="scenes">
{body}
</div>
</section>""")

CSS = """
:root{
  color-scheme: light;
  --bg:#E7E9EE; --surface:#F3F4F7; --raise:#FBFBFD;
  --line:#CBD0DA; --line-soft:#DDE1E8;
  --ink:#141821; --ink-2:#434B5A; --ink-3:#5D6474;
  --amber:#88570D; --amber-line:#D2AE6B; --amber-wash:#F4EEE1;
  --indigo:#33406A; --indigo-wash:#E4E7F0;
  --done:#3F6147;
  --shadow:0 1px 2px rgba(20,24,33,.06), 0 8px 24px -16px rgba(20,24,33,.28);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme: dark;
    --bg:#0C0E12; --surface:#14171E; --raise:#1B1F28;
    --line:#272C37; --line-soft:#1F242D;
    --ink:#E9EAEE; --ink-2:#AAB1BF; --ink-3:#7E8697;
    --amber:#E3A754; --amber-line:#5A431F; --amber-wash:#1A160F;
    --indigo:#93A2CC; --indigo-wash:#12151F;
    --done:#82A98A;
    --shadow:0 1px 2px rgba(0,0,0,.5), 0 10px 30px -20px rgba(0,0,0,.9);
  }
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --bg:#0C0E12; --surface:#14171E; --raise:#1B1F28;
  --line:#272C37; --line-soft:#1F242D;
  --ink:#E9EAEE; --ink-2:#AAB1BF; --ink-3:#7E8697;
  --amber:#E3A754; --amber-line:#5A431F; --amber-wash:#1A160F;
  --indigo:#93A2CC; --indigo-wash:#12151F;
  --done:#82A98A;
  --shadow:0 1px 2px rgba(0,0,0,.5), 0 10px 30px -20px rgba(0,0,0,.9);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:"Zen Kaku Gothic New","Hiragino Sans","Yu Gothic",system-ui,sans-serif;
  font-size:15px; line-height:1.75; -webkit-font-smoothing:antialiased;
}
.wrap{max-width:1080px; margin:0 auto; padding:0 24px 96px}
h1,h2,h3{font-family:"Shippori Mincho","Hiragino Mincho ProN","Yu Mincho",serif;
  font-weight:600; text-wrap:balance; margin:0; line-height:1.35}

/* ── 見出し帯 ───────────────────────── */
.top{padding:64px 0 40px; border-bottom:1px solid var(--line)}
.eyebrow{font-size:11px; letter-spacing:.22em; text-transform:uppercase;
  color:var(--amber); font-weight:600; margin:0 0 14px}
.top h1{font-size:clamp(34px,6vw,54px); letter-spacing:.04em}
.romaji{font-family:"Shippori Mincho",serif; font-size:clamp(15px,2.2vw,19px);
  color:var(--ink-2); letter-spacing:.05em; margin:10px 0 0; font-style:italic}
.facts{display:flex; flex-wrap:wrap; gap:8px; margin-top:24px; padding:0; list-style:none}
.facts li{font-size:12px; letter-spacing:.04em; color:var(--ink-2);
  border:1px solid var(--line); border-radius:2px; padding:5px 11px; background:var(--surface)}
.facts li.hot{color:var(--amber); border-color:var(--amber-line); background:var(--amber-wash)}

/* ── 進捗 ───────────────────────── */
.gauges{display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr));
  gap:20px; margin-top:32px}
.gauge{background:var(--surface); border:1px solid var(--line); border-radius:3px; padding:16px 18px}
.gauge-top{display:flex; justify-content:space-between; align-items:baseline; gap:12px}
.gauge-k{font-size:12px; letter-spacing:.1em; color:var(--ink-2)}
.gauge-v{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:20px;
  font-variant-numeric:tabular-nums; color:var(--ink)}
.bar{height:3px; background:var(--line-soft); margin-top:12px; border-radius:2px; overflow:hidden}
.bar i{display:block; height:100%; width:0; background:var(--amber);
  transition:width .4s cubic-bezier(.2,.7,.3,1)}
.gauge-note{font-size:11px; color:var(--ink-3); margin:8px 0 0}

/* ── 節 ───────────────────────── */
section{margin-top:72px}
.sec-head{border-bottom:1px solid var(--line); padding-bottom:14px; margin-bottom:28px}
.sec-head h2{font-size:24px; letter-spacing:.06em}
.sec-head p{margin:8px 0 0; color:var(--ink-2); font-size:13.5px; max-width:62ch}

/* ── 素材表 ───────────────────────── */
.tablewrap{overflow-x:auto; border:1px solid var(--line); border-radius:3px; background:var(--surface)}
table{width:100%; border-collapse:collapse; min-width:640px}
th,td{text-align:left; padding:12px 16px; border-bottom:1px solid var(--line-soft);
  font-size:13px; vertical-align:top}
tbody tr:last-child th, tbody tr:last-child td{border-bottom:0}
thead th{font-size:11px; letter-spacing:.14em; color:var(--ink-3); font-weight:600;
  text-transform:uppercase; background:var(--raise); white-space:nowrap}
tbody th{font-weight:600; color:var(--ink); white-space:nowrap}
.where{display:block; font-weight:400; font-size:11px; color:var(--ink-3); letter-spacing:.03em}
td.n{font-family:"IBM Plex Mono",monospace; font-variant-numeric:tabular-nums;
  color:var(--amber); font-size:15px; width:1%}
td code{font-family:"IBM Plex Mono",monospace; font-size:12px; color:var(--ink-2)}
td.want{color:var(--ink-2)}

.warn{margin-top:18px; border-left:2px solid var(--amber); background:var(--amber-wash);
  padding:14px 18px; font-size:13.5px; color:var(--ink)}
.warn strong{color:var(--amber)}

.crits{display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr));
  gap:1px; background:var(--line); border:1px solid var(--line);
  border-radius:3px; margin-top:24px; overflow:hidden}
.crit{background:var(--surface); padding:14px 16px; display:grid;
  grid-template-columns:auto 1fr; gap:4px 12px; align-items:baseline}
.crit-k{font-size:12.5px; font-weight:600}
.crit-v{font-family:"IBM Plex Mono",monospace; font-size:12.5px; color:var(--amber);
  text-align:right; font-variant-numeric:tabular-nums}
.crit-w{grid-column:1/-1; font-size:11.5px; color:var(--ink-3); line-height:1.5}

.bans{list-style:none; padding:0; margin:24px 0 0;
  display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:10px}
.bans li{font-size:12.5px; color:var(--ink-2); line-height:1.6;
  border:1px solid var(--line); border-radius:3px; padding:12px 14px; background:var(--surface)}
.bans strong{display:block; color:var(--ink); font-size:13px; margin-bottom:2px}
.bans strong::before{content:"× "; color:var(--amber)}

/* ── 幕 ───────────────────────── */
.act{margin-top:56px}
.act-head{padding:18px 22px; border:1px solid var(--line); border-radius:3px 3px 0 0;
  border-bottom:0; background:var(--surface)}
.act-label{font-size:11px; letter-spacing:.2em; color:var(--amber); font-weight:600}
.act-head h2{font-size:20px; margin-top:4px; letter-spacing:.06em}
.act-head p{margin:6px 0 0; font-size:12.5px; color:var(--ink-3)}
/* 幕が進むほど地が沈む。この巻の弧そのもの */
.act-one .act-head{background:var(--amber-wash)}
.act-three .act-head{background:var(--indigo-wash)}
.act-three .act-label{color:var(--indigo)}

.scenes{display:grid; gap:1px; background:var(--line);
  border:1px solid var(--line); border-radius:0 0 3px 3px; overflow:hidden}
.scene{background:var(--surface); padding:20px 22px 22px}
.act-one .scene{background:linear-gradient(var(--amber-wash),var(--surface) 90px)}
.act-three .scene{background:linear-gradient(var(--indigo-wash),var(--surface) 90px)}
.scene.done{opacity:.55}
.scene-head{display:flex; gap:16px; align-items:flex-start}
.num{font-family:"IBM Plex Mono",monospace; font-size:13px; color:var(--ink-3);
  font-variant-numeric:tabular-nums; padding-top:3px; letter-spacing:.05em}
.scene-id{flex:1; min-width:0}
.scene-id h3{font-size:17px; letter-spacing:.04em}
.meta{margin:6px 0 0; display:flex; flex-wrap:wrap; gap:6px}
.tag{font-size:11px; letter-spacing:.05em; color:var(--ink-3);
  border:1px solid var(--line); border-radius:2px; padding:2px 8px; background:var(--raise)}
.tag-fig{color:var(--amber); border-color:var(--amber-line); background:var(--amber-wash)}

.check{display:flex; align-items:center; gap:7px; cursor:pointer; user-select:none;
  font-size:12px; color:var(--ink-3); white-space:nowrap; padding-top:2px}
.check input{width:15px; height:15px; accent-color:var(--done); cursor:pointer; margin:0}
.scene.done .check{color:var(--done)}

.prompt{margin:16px 0 0; max-height:190px; overflow:auto;
  font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11.5px; line-height:1.85;
  color:var(--ink-2); background:var(--raise); border:1px solid var(--line-soft);
  border-radius:3px; padding:14px 16px; white-space:pre-wrap; word-break:break-word}

button.copy{margin-top:12px; font:inherit; font-size:12.5px; letter-spacing:.05em;
  color:var(--ink); background:var(--raise); border:1px solid var(--line);
  border-radius:3px; padding:8px 16px; cursor:pointer;
  transition:border-color .15s, color .15s, background .15s}
button.copy:hover{border-color:var(--amber-line); color:var(--amber)}
button.copy:focus-visible{outline:2px solid var(--amber); outline-offset:2px}
button.copy.ok{color:var(--done); border-color:var(--done)}
button.copy.small{margin:0; padding:7px 14px; font-size:12px}

/* ── 手順 ───────────────────────── */
.steps{list-style:none; padding:0; margin:0; display:grid; gap:1px;
  background:var(--line); border:1px solid var(--line); border-radius:3px; overflow:hidden}
.step{background:var(--surface); padding:18px 22px; display:grid;
  grid-template-columns:minmax(210px,1fr) minmax(0,1.6fr); gap:10px 28px; align-items:start}
.step-t h3{font-size:15px; letter-spacing:.04em}
.step-t p{margin:5px 0 0; font-size:12px; color:var(--ink-3); line-height:1.6}
.cmdwrap{display:flex; flex-direction:column; gap:8px; align-items:flex-start; min-width:0}
.cmd{margin:0; width:100%; overflow-x:auto; font-family:"IBM Plex Mono",monospace;
  font-size:11.5px; line-height:1.7; color:var(--ink-2); background:var(--raise);
  border:1px solid var(--line-soft); border-radius:3px; padding:12px 14px; white-space:pre}
@media (max-width:720px){ .step{grid-template-columns:1fr} }

.foot{margin-top:72px; padding-top:22px; border-top:1px solid var(--line);
  font-size:11.5px; color:var(--ink-3); display:flex; flex-wrap:wrap; gap:6px 20px}
.foot code{font-family:"IBM Plex Mono",monospace}

@media (prefers-reduced-motion: reduce){ *{transition:none !important} }
"""

JS = """
const KEY = 'vol16-rain-console';
let state = {};
try { state = JSON.parse(localStorage.getItem(KEY) || '{}'); } catch (e) { state = {}; }

function save(){ try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {} }

function paint(){
  let img = 0;
  document.querySelectorAll('input[type=checkbox]').forEach(function(b){
    const on = !!state[b.dataset.key];
    b.checked = on;
    const card = b.closest('.scene');
    if (card) card.classList.toggle('done', on);
    if (on && b.dataset.key.startsWith('img')) img++;
  });
  const g = document.getElementById('g-img');
  g.querySelector('.gauge-v').textContent = img + ' / 22';
  g.querySelector('.bar i').style.width = (img / 22 * 100) + '%';
}

document.addEventListener('change', function(e){
  const b = e.target;
  if (b.type !== 'checkbox' || !b.dataset.key) return;
  state[b.dataset.key] = b.checked;
  save(); paint();
});

document.addEventListener('click', function(e){
  const btn = e.target.closest('button.copy');
  if (!btn) return;
  const text = document.getElementById(btn.dataset.target).textContent;
  const done = function(){
    const was = btn.textContent;
    btn.textContent = 'コピーしました';
    btn.classList.add('ok');
    setTimeout(function(){ btn.textContent = was; btn.classList.remove('ok'); }, 1600);
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(done, fallback);
  } else { fallback(); }
  function fallback(){
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select();
    try { document.execCommand('copy'); done(); } catch (err) {
      btn.textContent = '選択してコピーしてください';
    }
    document.body.removeChild(ta);
  }
});

paint();
"""

HTML = f"""<title>雨の石畳</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@500;600&family=Zen+Kaku+Gothic+New:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>

<div class="wrap">

<header class="top">
  <p class="eyebrow">Whispers of Japan ／ Vol.16</p>
  <h1>雨の石畳</h1>
  <p class="romaji">Rain on the Lantern Street 🌙 Japanese Rain Sounds for Sleep | 3 Hours</p>
  <ul class="facts">
    <li class="hot">楽器はゼロ。雨だけ</li>
    <li class="hot">雷は入れない</li>
    <li>22トラック × 497秒 ＝ 3時間00分08秒</li>
    <li>曲間 6秒</li>
    <li class="hot">初めて人物を出す巻（後ろ姿・顔なし）</li>
    <li>この巻だけ月を描かない</li>
  </ul>

  <div class="gauges">
    <div class="gauge" id="g-img">
      <div class="gauge-top"><span class="gauge-k">画像</span><span class="gauge-v">0 / 22</span></div>
      <div class="bar"><i></i></div>
      <p class="gauge-note">1枚ずつ生成する。16:9でそのまま出す（切り出しもガンマも掛けない）</p>
    </div>
    <div class="gauge">
      <div class="gauge-top"><span class="gauge-k">雨の素材</span><span class="gauge-v">{TOTAL_SOUNDS} 本</span></div>
      <div class="bar"><i style="width:100%;background:var(--line)"></i></div>
      <p class="gauge-note">Pixabay Content License。落としたら <code>vet</code> に掛ける</p>
    </div>
  </div>
</header>

<section>
  <div class="sec-head">
    <h2>まず雨を仕入れる</h2>
    <p>ここが唯一の外部依存。1本60秒以上あれば足ります（場面の8分17秒までは自動で伸ばします）。</p>
  </div>

  <div class="tablewrap">
    <table>
      <thead><tr><th scope="col">用途</th><th scope="col">本数</th><th scope="col">探す語</th><th scope="col">求める性質</th></tr></thead>
      <tbody>
{sound_rows}
      </tbody>
    </table>
  </div>

  <p class="warn"><strong>全素材の絶対条件は、雷が1回も入っていないこと。</strong>
  睡眠用で最悪の突発音で、3時間のあいだ何度もその瞬間が来ます。
  <code>rain</code> で検索すると <code>rain and thunder</code> が大量に混ざります。</p>

  <div class="crits">
{check_rows}
  </div>
  <p class="warn"><strong>この閾値は雨でまだ実測していません。</strong>
  虫の音（Vol.15）とピンクノイズでしか当たっていないので、最初の一山を測ったら見直します。</p>
</section>

<section>
  <div class="sec-head">
    <h2>画像 22枚</h2>
    <p>三幕を通して音が遠ざかっていきます。人物が写るのは8枚だけ。
    服の3点（濃紺の着物・鴇鼠の帯・低い束ね髪）を毎回書いてあるので、顔を出さなくても同じ人物に見えます。</p>
  </div>

  <ul class="bans">
{ban_rows}
  </ul>

{"".join(acts_html)}
</section>

<section>
  <div class="sec-head">
    <h2>揃ったら</h2>
    <p><code>cd /Users/ryo/youtube/bgm</code> してから。</p>
  </div>
  <ol class="steps">
{step_rows}
  </ol>
</section>

<p class="foot">
  <span>設計 <code>bgm/SOJ01_テーマ設計.md</code></span>
  <span>設定 <code>bgm/volumes/soj01.yaml</code></span>
  <span>作業先 <code>/Volumes/ESD-EPB/Whispers of Japan/SOJ01_素材_雨の石畳/</code></span>
  <span>進捗はこの端末に保存されます</span>
</p>

</div>
<script>{JS}</script>
"""

open(OUT, "w").write(HTML)
print(f"{OUT}  {len(HTML)/1024:.0f}KB  場面{len(scenes)}  素材{TOTAL_SOUNDS}本")
