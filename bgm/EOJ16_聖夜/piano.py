# -*- coding: utf-8 -*-
"""ECJ07：シューベルトの即興曲・ブラームスの間奏曲・ラフマニノフの前奏曲を和楽器で鳴らす。

★EOJ05 の debussy.py をそのまま持ってきて、**変えたのは1行だけ** ——
  右手／左手を固定のトラック1・2ではなく `rh_tr` / `lh_tr` で指定できるようにした。
  **即興曲 D.899-3 はトラックが5本ある**（右手＝旋律1＋細かい音型2／左手＝3・4・5）ので、
  1と2の決め打ちでは組めなかった。ほかは触っていない。

以下は元の説明（ドビュッシーの巻のもの。割り振りの規則は同じ）：

ドビュッシーのアラベスク2曲と月の光を和楽器で鳴らす。

★懸念だった「\change Staff で声部が譜表をまたぐ」は外れた（_調査_構造.py）。
  両手が同時に鳴る打点で音域が逆転するのは アラベスク 0.0% / 月の光 1.9%。
  MIDIのトラック1＝右手・2＝左手として素直に扱える。

★左手の作りは3曲で違う（実測）：
  アラベスク1 … 633打点の91%が単音。1.5拍以上が93音。分散和音が主
  アラベスク2 … 394打点の52%が単音、4拍のバスが35音。バス＋和音のグノシエンヌ型
  月の光      … 537打点の79%が単音だが1.5拍以上が221音（41%）。伸ばした音が最も多い
  → 窓ごとに最低音を拾う ECJ04 の規則をそのまま当てる。窓は小節（\time）に合わせて
     アラベスク 4.0拍 / 月の光 4.5拍（9/8）。

★尺八は3曲とも間引きが要る。打点間隔の中央が アラベスク1 0.33拍（100bpmで0.20秒）・
  アラベスク2 0.50拍（0.29秒）・月の光 0.25拍（54bpmで0.28秒）で、
  mel_hold 0.54秒に届かない。月光第3楽章・ノクターンに続く3例目。

割り振りは ECJ04 と同じ：
  左手 窓ごとの最低音 → 笙 ／ 左手 残り → 箏（分散和音の揺れ）
  右手 単音の打点・和音の頂点が MEL_GAP 半音以上高い → 尺八（詰まっていれば箏へ）
  右手 それ以外 → 箏
"""
import numpy as np, midiparse, synth, wafu

SR = synth.SR
MEL_GAP = 7
MEL_MIN = 55
GRACE = 0.2


def build(out, src, bpm, scale='ritsu', tonic_pc=0, transpose=0, rh_tr=(1,), lh_tr=(2,),
          pedal_beats=6.0, bass_floor=36, limit=None, melody='shakuhachi',
          koto_gain=0.40, sho_gain=0.26, mel_gain=0.80, air=0.45, muraiki=0.15,
          mel_floor=0.40, mel_gap=0.14, mel_hold=0.54, rt=3.8, mix=0.30,
          lh_mel=(), prep=None, ret_audio=False, quiet=False):
    """★ECJ09で足したのは `prep` だけ（MIDIを読んだ直後、音階へ写す前の音符列に掛ける関数。
      熱情の繰り返しの展開と、終わりの減七を主和音へ差し替えるのに使う。既定は None で ECJ08 と同じ動き）。

    ★ECJ08で足したのは `lh_mel` だけ（拍で指定する区間のリスト。既定は空で、ECJ07と同じ動き）。

    「雨だれ」の中間部（第28〜75小節）は**旋律が左手のいちばん低い線**にあり、右手は同音の連打。
    元の規則のままだと、**尺八が連打（G#）を吹き、本当の旋律は笙と箏に回る**
    （試作1回目の実測：中間部の尺八43音のうち88%が同じ高さの繰り返し）。
    → 区間の中だけ、左手の打点ごとの最低音を旋律として尺八へ回し（48未満は1オクターブ上げてから、
      置くときにさらに上げるので2オクターブ上）、右手は連打も和音も全部箏へ回す。
      笙は左手の残り（主に5度）から窓ごとの最低音を取る。
    """
    spb = 60.0 / bpm
    notes = midiparse.notes(src)[0]
    if prep:
        notes = prep(notes)
    if scale:
        notes = wafu.transform(notes, tonic_pc, scale, 'up')
    if transpose:
        notes = [(t, d, n + transpose, v, tr) for t, d, n, v, tr in notes]
    if limit:
        notes = [n for n in notes if n[0] * spb < limit + 6]

    lh = [n for n in notes if n[4] in lh_tr]
    rh = [n for n in notes if n[4] in rh_tr]

    # ── 左手が旋律を持つ区間（lh_mel）
    inwin = lambda t: any(a <= t < b for a, b in lh_mel)
    lh_line, rh_all = [], []
    if lh_mel:
        rh_all = [(t, d, n, v) for t, d, n, v, tr in rh if inwin(t)]
        rh = [x for x in rh if not inwin(x[0])]
        on = {}
        for x in lh:
            if inwin(x[0]) and x[1] >= GRACE:
                on.setdefault(round(x[0], 3), []).append(x)
        take = {id(min(g, key=lambda x: x[2])) for g in on.values()}
        # ★48以上になるまでオクターブを上げる（1回だけだと第40小節の E1 が尺八で E3 まで下がった）
        up = lambda n: n if n >= 48 else up(n + 12)
        lh_line = [(x[0], x[1], up(x[2]), x[3]) for x in lh if id(x) in take]
        lh = [x for x in lh if id(x) not in take]

    # ── 右手：旋律を抜く
    onsets = {}
    for t, d, n, v, tr in rh:
        onsets.setdefault(round(t, 3), []).append((d, n, v))
    keys = sorted(onsets)
    mel, inner = [], []
    for i, t in enumerate(keys):
        grp = sorted(onsets[t], key=lambda x: x[1])
        long_ = [g for g in grp if g[0] >= GRACE]
        take = bool(long_) and (len(long_) == 1 or (long_[-1][1] - long_[-2][1] >= MEL_GAP))
        if take and long_[-1][1] >= MEL_MIN:
            d, n, v = long_[-1]
            mel.append((t, d, n, v))
            grp = [g for g in grp if g is not long_[-1]]
        inner += [(t, d, n, v) for d, n, v in grp]
    mel = sorted(mel + lh_line)   # lh_mel の区間の旋律（左手の最低音）を合流させる
    inner += rh_all               # 同じ区間の右手（連打と和音）は全部箏

    # ★切るのは「次の旋律の打点」の手前。長い音の打点で数えると、
    #   そこで旋律を採らなかった場合に前の音が次の音を跨いで残り単音が崩れる
    #   （Op.9-1・3 で実測 最大4本）。
    #   さらに★ノクターンは旋律そのものが速い（実測：打点間隔の78%が0.54秒未満・
    #   最小0.034秒。ジムノペディは1音2.1〜2.5秒）。尺八では吹けないので
    #   **次の打点まで mel_hold 秒に届かない音は箏へ落とす**（月光第3楽章と同じ規則。
    #   音符は1つも捨てない）。
    cut, runs = [], []
    for i, (t, d, n, v) in enumerate(mel):
        nxt = mel[i + 1][0] if i + 1 < len(mel) else t + d
        span = (nxt - t) * spb
        if span < mel_hold:
            runs.append((t, d, n, v))
        else:
            cut.append((t, float(np.clip(min(span, d * spb) - mel_gap, mel_floor, 9.0)), n, v))
    mel_total = len(mel)          # 旋律として抜いた総数（うち速いものは箏へ落ちる）
    mel = cut
    inner += runs

    total = max(t + d for t, d, *_ in notes) * spb + 12.0
    N = int(SR * total); L = np.zeros(N, np.float32); R = np.zeros(N, np.float32)

    def place(sig, at, pan):
        p = int(SR * at); e = min(N, p + len(sig))
        if e > p:
            s = sig[:e - p]
            L[p:e] += s * np.sqrt(.5 * (1 - pan)); R[p:e] += s * np.sqrt(.5 * (1 + pan))

    for t, dur, n, v in mel:
        p = n + 12 if n < 60 else n
        if melody == 'shakuhachi':
            place(synth.shakuhachi(p, dur, mel_gain, air=air,
                                   muraiki=muraiki + 0.15 * (dur >= 1.8)), t * spb, 0.05)
        elif melody == 'koto':
            for i in range(max(1, int(dur / 1.4))):
                place(synth.koto(p, 3.4, mel_gain * (0.9 if i == 0 else 0.45), bright=0.68),
                      t * spb + i * 1.4, 0.05)
        elif melody == 'sho':
            place(synth.sho([p], dur, mel_gain * 0.8, breath=0.03), t * spb, 0.05)

    for t, d, n, v in inner:
        place(synth.koto(n if n >= 52 else n + 12, min(3.6, max(1.2, d * spb * 1.4)),
                         koto_gain * (0.62 if d < GRACE else 1.0), bright=0.58),
              t * spb, float(np.clip((n - 62) / 40.0, -.45, .45)))

    # ── 左手：窓ごとの最低音を笙、残りを箏
    end = max(t + d for t, d, *_ in lh)
    pedal, swing = [], 0
    w = 0.0
    used = set()
    while w < end:
        seg = [x for x in lh if w <= x[0] < w + pedal_beats]
        if seg:
            lo = min(seg, key=lambda x: x[2])
            pedal.append((w, pedal_beats, lo[2]))
            used.add((round(lo[0], 3), lo[2]))
        w += pedal_beats
    for t, d, n, v, tr in lh:
        if (round(t, 3), n) in used:
            continue
        p = n + 12 if n < 40 else n
        place(synth.koto(p, min(4.4, max(1.4, d * spb * 1.6)), koto_gain * 0.9,
                         bright=0.42 if p < 52 else 0.55, damp=0.9968),
              t * spb, float(np.clip((p - 58) / 44.0, -.40, .40)))
        swing += 1
    for t, d, n in pedal:
        p = n + 12 if n < bass_floor else n
        place(synth.sho([p], d * spb * 1.05, sho_gain, breath=0.02), t * spb, -0.10)

    x = np.vstack([synth.reverb(L, rt=rt, mix=mix), synth.reverb(R, rt=rt + .2, mix=mix)])
    if not quiet:
        print('%-26s %5.2f分  尺八%4d  箏(伴奏＋速い旋律)%4d  箏(分散)%4d  笙%3d'
              % (out, total / 60, len(mel), len(inner), swing, len(pedal)))
    if ret_audio:
        return x, dict(sec=total, mel=len(mel), inner=len(inner), swing=swing,
                       sho=len(pedal), mel_total=mel_total,
                       mel_iv=[(t * spb, dur) for t, dur, _, _ in mel])
    synth.write_wav(out, x)
